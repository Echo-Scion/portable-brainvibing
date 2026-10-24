"""
Tool-Call Quantum Counter & Secret Egress Redactor.
Pure Python 3 standard library implementation.
Tracks tool calls and ensures egress transcript slices contain zero secrets.
"""
import os
import sys
import re
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from core.db import ActionObservationStream, log_telemetry as _log_telemetry
from core.security import redact_secrets


class SecretRedactor:
    """Deterministic regex sanitizer for session transcripts and evidence slices."""

    @classmethod
    def redact_text(cls, text: str) -> str:
        if not text:
            return ""
        return redact_secrets(text)

    @classmethod
    def redact_data(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls.redact_text(data)
        elif isinstance(data, dict):
            return {k: cls.redact_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.redact_data(v) for v in data]
        return data


@dataclass
class SessionTelemetryState:
    session_id: str
    tool_call_count: int = 0
    last_reflection_call: int = 0
    total_turns: int = 0
    created_at: str = ""
    active: bool = True


class ToolQuantumCapture:
    """
    Counts tool calls in an active session without resident daemons.
    Determines when an episode reaches quantum maturity (N tool calls).
    """

    def __init__(self, state_dir: str, quantum_threshold: int = 50):
        self.state_dir = state_dir
        self.quantum_threshold = quantum_threshold
        self.sessions_dir = os.path.join(self.state_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        working_dir = os.path.normpath(os.path.join(self.state_dir, "..", "working"))
        os.makedirs(working_dir, exist_ok=True)
        self.event_stream = ActionObservationStream(
            os.path.join(working_dir, "trajectory.jsonl")
        )

    def _get_session_path(self, session_id: str) -> str:
        safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "_", session_id)
        return os.path.join(self.sessions_dir, f"{safe_id}.json")

    def load_session(self, session_id: str) -> SessionTelemetryState:
        p = self._get_session_path(session_id)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    valid_keys = set(SessionTelemetryState.__dataclass_fields__.keys())
                    filtered = {k: v for k, v in data.items() if k in valid_keys}
                    return SessionTelemetryState(**filtered)
            except Exception as _e:
                _log_telemetry(_e, "capture.py:load_session")
        return SessionTelemetryState(session_id=session_id)

    def save_session(self, state: SessionTelemetryState) -> None:
        p = self._get_session_path(state.session_id)
        tmp = f"{p}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state.__dict__, f, indent=2)
            os.replace(tmp, p)
        except Exception:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass
            raise

    def record_tool_call(self, session_id: str, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, int]:
        """
        Increments tool call count.
        Returns:
            (should_reflect: bool, current_quantum_calls: int)
        """
        state = self.load_session(session_id)
        if not state.active:
            raise RuntimeError(
                "[CIRCUIT BREAKER ACTIVE]: Session is locked due to a prior circuit breaker trip. "
                "Run reflexion or reset-circuit-breaker before calling tools."
            )
        state.tool_call_count += 1
        state.total_turns += 1
        is_post_success = isinstance(args, dict) and args.get("exit_code") == 0
        if isinstance(args, dict):
            ec = args.get("exit_code") if "exit_code" in args else args.get("exitCode")
            if ec is not None and isinstance(ec, int) and ec > 0:
                try:
                    from commands.reflexion import ObservationLedger, BASE_DIR as _REFLEXION_BASE
                    norm_state = os.path.abspath(self.state_dir)
                    ws_root = os.path.abspath(os.path.dirname(_REFLEXION_BASE))
                    if norm_state.startswith(ws_root):
                        ledger = ObservationLedger()
                    else:
                        ledger = ObservationLedger(
                            active_path=os.path.join(self.state_dir, "OBSERVATIONS.md"),
                            archive_path=os.path.join(self.state_dir, "OBSERVATIONS.archive.md"),
                        )
                    ledger.add_observation(
                        title=f"Tool failure in {tool_name} (Exit Code {ec})",
                        kind="violation",
                        target=tool_name,
                        rule_id="TOOL_EXIT_NONZERO",
                        evidence=f"Args: {str(args)[:200]}"
                    )
                except Exception:
                    pass

        self.event_stream.record(
            kind="observation" if is_post_success else "action",
            source="tool",
            payload={"session_id": session_id, "tool_name": tool_name, "args": args},
            action_type=tool_name,
        )
        is_stuck = False if is_post_success else self.event_stream.detect_stuck_loop(window_size=3, session_id=session_id)
        if is_stuck:
            state.active = False
            self.save_session(state)
            raise RuntimeError(
                "[CIRCUIT BREAKER TRIPPED]: 3 identical/cyclical tool actions detected in trajectory. "
                "Execution halted mechanically. Output root-cause analysis to user."
            )

        paging_file = self.event_stream.detect_sequential_paging(consecutive_threshold=3, session_id=session_id)
        if paging_file:
            state.active = False
            self.save_session(state)
            raise RuntimeError(
                f"[CIRCUIT BREAKER TRIPPED]: Sequential paging detected on file '{paging_file}'. "
                "Do not read files sequentially. Use 'python .agents/scripts/orion.py scan map <file>' "
                "to get spans, then call view_file once with exact StartLine and EndLine."
            )
        
        calls_since_reflect = state.tool_call_count - state.last_reflection_call
        should_reflect = calls_since_reflect >= self.quantum_threshold

        if should_reflect:
            state.last_reflection_call = state.tool_call_count

        self.save_session(state)
        return should_reflect, calls_since_reflect

    def reset_reflection_watermark(self, session_id: str) -> None:
        state = self.load_session(session_id)
        state.last_reflection_call = state.tool_call_count
        self.save_session(state)
        # Flush observations on watermark boundary
        try:
            from commands.reflexion import ObservationLedger
            ObservationLedger().get_digest()
        except Exception as _e:
            _log_telemetry(_e, "capture.py:reset_reflection_watermark:flush_obs")

    def reset_circuit_breaker(self, session_id: str) -> None:
        state = self.load_session(session_id)
        state.active = True
        self.save_session(state)
        # 1. Append circuit breaker reset marker to trajectory
        try:
            self.event_stream.record(
                kind="action",
                source="harness",
                payload={"session_id": session_id, "action": "darwinian_reset"},
                action_type="circuit_breaker_reset",
            )
        except Exception as _e1:
            _log_telemetry(_e1, "capture.py:reset_circuit_breaker:trajectory")
        # 2. Append recovery marker to failures.log to clear pre-agent-wake lockout
        try:
            working_dir = os.path.normpath(os.path.join(self.state_dir, "..", "working"))
            failures_log = os.path.join(working_dir, "failures.log")
            with open(failures_log, "a", encoding="utf-8") as f:
                f.write(f"\n## [Darwinian Hook] Reflexion Reset: Session {session_id} unlocked at {time.time()}\n")
        except Exception as _e2:
            _log_telemetry(_e2, "capture.py:reset_circuit_breaker:failures_log")
