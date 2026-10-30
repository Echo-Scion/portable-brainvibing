"""
Kernel DB & Foundation Data Layer
Provides hardened, WAL-enabled SQLite connections, FTS5 sanitation, token budgeting,
and safe console stream output.
"""

import os
import sys
import re
import math
import time
import json
import uuid
import sqlite3
import struct
import argparse
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, asdict, field
from typing import Union, List, Any, Optional, Dict, Tuple, Set, Generator

import copy
import functools
import concurrent.futures

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


class MechanicalInvariantError(RuntimeError):
    """Raised when a function completes without throwing an exception but violates a mechanical post-condition or SLA timeout."""
    pass


def log_telemetry(
    err: Optional[Exception] = None,
    context: str = "",
    severity: str = "WARN",
    state_snapshot: Optional[Dict[str, Any]] = None,
) -> None:
    """Centralized non-fatal telemetry logger & Self-Evolve Auto-Catch Sink."""
    if os.environ.get("ORION_DEBUG"):
        msg = f": {err}" if err else ""
        try:
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
        except Exception:
            pass

    if err is None and not context:
        return

    try:
        from core.paths import get_orion_dir
        orion_dir = str(get_orion_dir())
    except Exception:
        orion_dir = os.path.join(os.getcwd(), ".orion")

    working_dir = os.path.join(orion_dir, "working")
    if not os.path.isdir(orion_dir):
        return

    try:
        os.makedirs(working_dir, exist_ok=True)
        err_msg = str(err) if err else "unclassified_anomaly"
        err_type = type(err).__name__ if err else "MechanicalAnomaly"

        try:
            from core.security import redact_secrets
            err_msg = redact_secrets(err_msg)[:600]
        except Exception:
            err_msg = err_msg[:600]

        module_name = context.split(":")[0] if ":" in context else "core"
        record: Dict[str, Any] = {
            "timestamp": time.time(),
            "module": module_name,
            "context": context or "unspecified",
            "exception_type": err_type,
            "error": err_msg,
            "severity": severity,
        }
        if state_snapshot:
            try:
                raw_snap = json.dumps(state_snapshot, default=str)[:500]
                record["state_snapshot"] = json.loads(raw_snap)
            except Exception:
                record["state_snapshot"] = {"raw": str(state_snapshot)[:300]}

        catches_jsonl_path = os.path.join(working_dir, "mechanical_catches.jsonl")
        with open(catches_jsonl_path, "a", encoding="utf-8") as jf:
            jf.write(json.dumps(record) + "\n")

        if severity in ("INVARIANT_BREACH", "ERROR"):
            try:
                is_testing = "unittest" in sys.modules or "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))
                from commands.reflexion import ObservationLedger, BASE_DIR as _REFLEXION_BASE
                norm_orion = os.path.abspath(orion_dir)
                ws_root = os.path.abspath(os.path.dirname(_REFLEXION_BASE))
                is_in_workspace = norm_orion.startswith(ws_root)
                if is_testing and is_in_workspace:
                    pass  # Prevent test suites from polluting production observation ledger
                elif not is_in_workspace:
                    ledger = ObservationLedger(
                        active_path=os.path.join(working_dir, "OBSERVATIONS.md"),
                        archive_path=os.path.join(working_dir, "OBSERVATIONS.archive.md"),
                    )
                    ledger.add_observation(
                        title=f"Mechanical catch in {context}: {err_type}",
                        kind="violation",
                        target=context,
                        rule_id="MECHANICAL_INVARIANT_BREACH",
                        evidence=err_msg[:200]
                    )
                else:
                    ledger = ObservationLedger()
                    ledger.add_observation(
                        title=f"Mechanical catch in {context}: {err_type}",
                        kind="violation",
                        target=context,
                        rule_id="MECHANICAL_INVARIANT_BREACH",
                        evidence=err_msg[:200]
                    )
            except Exception:
                pass
    except Exception:
        pass


def drain_mechanical_catches(clear: bool = False) -> List[Dict[str, Any]]:
    """Reads structured mechanical catch events from .orion/working/mechanical_catches.jsonl."""
    try:
        from core.paths import get_orion_dir
        working_dir = os.path.join(str(get_orion_dir()), "working")
    except Exception:
        working_dir = os.path.join(os.getcwd(), ".orion", "working")

    jsonl_path = os.path.join(working_dir, "mechanical_catches.jsonl")
    if not os.path.exists(jsonl_path):
        return []
    records = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass
        if clear:
            atomic_write_text(jsonl_path, "")
            legacy_json = os.path.join(working_dir, "mechanical_catches.json")
            if os.path.exists(legacy_json):
                try:
                    os.remove(legacy_json)
                except OSError:
                    pass
        return records
    except Exception as _e:
        log_telemetry(_e, "db.py:drain_mechanical_catches")
        return []


def sovereign_catch(
    context: str,
    fallback_value: Any = None,
    *,
    post_condition: Optional[Any] = None,
    timeout_sec: Optional[float] = None,
    fallback_fn: Optional[Any] = None,
    enforce_hard_timeout: bool = False,
):
    """
    Universal Mechanical Catch Decorator for .agents functions.
    Traps standard exceptions, execution timeouts, and silent semantic post-condition violations,
    routing structured telemetry into Seam 1 (.orion/working/mechanical_catches.json).
    Preserves 100% backward compatibility with @sovereign_catch(context, fallback_value).
    """
    def _resolve_fallback(*args: Any, **kwargs: Any) -> Any:
        if callable(fallback_fn):
            try:
                return fallback_fn(*args, **kwargs)
            except TypeError:
                return fallback_fn()
        try:
            return copy.deepcopy(fallback_value)
        except Exception:
            return fallback_value

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            t0 = time.perf_counter()
            try:
                if timeout_sec is not None and timeout_sec > 0 and enforce_hard_timeout:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(func, *args, **kwargs)
                        try:
                            result = future.result(timeout=timeout_sec)
                        except concurrent.futures.TimeoutError as te:
                            raise MechanicalInvariantError(
                                f"Hard timeout exceeded ({timeout_sec:.2f}s) in {context}"
                            ) from te
                else:
                    result = func(*args, **kwargs)

                elapsed = time.perf_counter() - t0
                if timeout_sec is not None and timeout_sec > 0 and elapsed > timeout_sec:
                    raise MechanicalInvariantError(
                        f"SLA timeout violated ({elapsed:.2f}s > {timeout_sec:.2f}s) in {context}"
                    )

                if callable(post_condition):
                    verdict = post_condition(result)
                    if isinstance(verdict, tuple):
                        ok, reason = bool(verdict[0]), str(verdict[1])
                    else:
                        ok, reason = bool(verdict), "Post-condition predicate returned False"
                    if not ok:
                        raise MechanicalInvariantError(
                            f"Semantic post-condition failed in {context}: {reason}"
                        )
                return result
            except Exception as exc:
                sev = "INVARIANT_BREACH" if isinstance(exc, MechanicalInvariantError) else "ERROR"
                snap = {"args_count": len(args), "kwargs_keys": list(kwargs.keys())[:5]}
                log_telemetry(exc, context=context, severity=sev, state_snapshot=snap)
                return _resolve_fallback(*args, **kwargs)

        return wrapper
    return decorator


mechanical_catch = sovereign_catch


EMOJI_ASCII_MAP: Dict[str, str] = {
    "🟢": "[OK]",
    "🟡": "[WARN]",
    "🔴": "[FAIL]",
    "⚡": "[!]",
    "🚦": "[CHECKPOINT]",
    "📋": "[EVIDENCE]",
    "🔮": "[NEXT]",
    "🧠": "[BRAIN]",
    "👁️": "[OBS]",
    "⚠️": "[WARN]",
    "📦": "[MAP]",
    "📄": "[FILE]",
    "🎨": "[UI]",
    "🛡️": "[SEC]",
    "🗺️": "[INDEX]",
    "🛠️": "[SKILL]",
    "📚": "[RULE]",
    "🚀": "[PLAYBOOK]",
    "🧰": "[SCRIPT]",
    "🧪": "[TEST]",
    "•": "*",
    "│": "|",
    "─": "-",
    "└": "`--",
    "├": "|--",
}


def transliterate_emojis(text: str) -> str:
    """Translates common emojis and Unicode markers to human-readable ASCII tags."""
    if not text:
        return text
    result = text
    for glyph, ascii_tag in EMOJI_ASCII_MAP.items():
        if glyph in result:
            result = result.replace(glyph, ascii_tag)
    return result


def configure_utf8() -> None:
    """Safely configure stdout and stderr to UTF-8 with replace error handler, propagating env."""
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8:replace")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception as _e:
                log_telemetry(_e, "configure_utf8:reconfigure")


# Auto-configure streams and environment when core.db is loaded
configure_utf8()


def safe_print(*args: Any, **kwargs: Any) -> None:
    """Print that safely handles broken pipes, NO_EMOJI / ORION_ASCII_ONLY, or unencodable characters."""
    force_ascii = (
        os.environ.get("NO_EMOJI") == "1"
        or os.environ.get("ORION_ASCII_ONLY") == "1"
    )
    if force_ascii:
        text = " ".join(str(a) for a in args)
        clean_text = transliterate_emojis(text)
        try:
            print(clean_text, **kwargs)
            return
        except UnicodeEncodeError:
            print(clean_text.encode('ascii', errors='replace').decode('ascii'), **kwargs)
            return
        except BrokenPipeError:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            return

    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            text = " ".join(str(a) for a in args)
            clean_text = transliterate_emojis(text)
            clean_text = clean_text.encode('ascii', errors='replace').decode('ascii')
            print(clean_text, **kwargs)
        except Exception as _e:
            log_telemetry(_e, "safe_print:fallback")
    except BrokenPipeError:
        try:
            sys.stdout.flush()
        except Exception as _e:
            log_telemetry(_e, "safe_print:broken_pipe_flush")


try:
    from core.paths import atomic_write_text
except ImportError:
    def atomic_write_text(filepath: Union[str, Path], content: str) -> None:
        """Atomically write text content to a destination file via temporary file and atomic replace."""
        abs_path = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        tmp_path = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, abs_path)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


def read_omni_buffer(context_path: Union[str, Path], max_age_sec: float = 300.0) -> Dict[str, Any]:
    """Reads context.json omni-buffer with stale-data guard (TTL validation)."""
    p = str(context_path)
    if not os.path.exists(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        ts_ms = data.get("timestamp_ms", 0)
        now_ms = time.time() * 1000
        if (now_ms - ts_ms) > (max_age_sec * 1000):
            data["stale"] = True
        else:
            data["stale"] = False
        return data
    except Exception as e:
        log_telemetry(e, "read_omni_buffer")
        return {}


def connect_sqlite(
    db_path: Union[str, Path],
    wal: bool = True,
    timeout_sec: float = 5.0,
    mmap_size: int = 67108864,
    cache_size: int = -16000,
    read_only: bool = False
) -> sqlite3.Connection:
    """Open or create an SQLite database with production PRAGMAs.
    - WAL journal mode for concurrent reading/writing
    - busy_timeout for lock evasion
    - temp_store in memory
    - mmap_size for fast zero-copy OS paging
    - read_only URI mode (mode=ro) for lock-free concurrent reads on Windows
    """
    path_obj = Path(db_path)

    if read_only:
        if not path_obj.exists():
            # If database does not exist yet, cannot open in read-only mode
            raise FileNotFoundError(f"Cannot open non-existent SQLite database in read-only mode: {db_path}")
        abs_posix = path_obj.resolve().as_posix()
        conn = sqlite3.connect(f"file:{abs_posix}?mode=ro", uri=True, timeout=timeout_sec)
        try:
            conn.execute(f"PRAGMA busy_timeout={int(timeout_sec * 1000)};")
            conn.execute("PRAGMA query_only=ON;")
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute(f"PRAGMA mmap_size={int(mmap_size)};")
            conn.execute(f"PRAGMA cache_size={int(cache_size)};")
        except Exception as _e:
            log_telemetry(_e, f"connect_sqlite:ro_pragmas:{db_path}")
        return conn

    path_obj.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path_obj), timeout=timeout_sec)
    try:
        conn.execute(f"PRAGMA busy_timeout={int(timeout_sec * 1000)};")
        conn.execute("PRAGMA foreign_keys=ON;")

        if wal:
            try:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("PRAGMA temp_store=MEMORY;")
                conn.execute(f"PRAGMA mmap_size={int(mmap_size)};")
                conn.execute(f"PRAGMA cache_size={int(cache_size)};")
            except Exception as _e:
                log_telemetry(_e, f"connect_sqlite:pragmas:{db_path}")
    except Exception as _init_e:
        try:
            conn.close()
        except Exception as _ce:
            log_telemetry(_ce, "connect_sqlite:close")
        raise _init_e

    return conn


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if a table exists in the connected database."""
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (table_name,)
    )
    return cur.fetchone() is not None


def sanitize_fts_query(query: str) -> str:
    """Sanitize query string for SQLite FTS5 MATCH clause, stripping dangerous syntax tokens."""
    if not query:
        return ""
    cleaned = re.sub(r'[*"\'^:()\-+~{}]', ' ', query)
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) >= 2]
    if not tokens:
        return ""
    return " ".join(f'"{t}"' for t in tokens)


def build_fts_query_or(terms: Any) -> str:
    """Build an OR-joined FTS5 query string for broad lexical matching."""
    if not terms:
        return ""
    if isinstance(terms, str):
        cleaned = re.sub(r'[*"\'^:()\-+~{}]', ' ', terms)
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) >= 2]
    else:
        tokens = []
        for t in terms:
            cleaned = re.sub(r'[*"\'^:()\-+~{}]', ' ', str(t))
            for sub in cleaned.split():
                if len(sub.strip()) >= 2:
                    tokens.append(sub.strip())
    if not tokens:
        return ""
    return " OR ".join(f'"{t}"' for t in tokens)


def pack_vector(vector: List[float]) -> bytes:
    """Serializes a float vector to compact bytes using struct pack."""
    if not vector:
        return b""
    return struct.pack(f"{len(vector)}f", *vector)


def unpack_vector(blob: bytes) -> List[float]:
    """Deserializes compact binary blob back to float list."""
    if not blob or len(blob) % 4 != 0:
        return []
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))


def cosine_similarity(v1: Any, v2: Any) -> float:
    """Computes cosine similarity between two vectors or binary blobs."""
    vec1 = unpack_vector(v1) if isinstance(v1, (bytes, bytearray)) else v1
    vec2 = unpack_vector(v2) if isinstance(v2, (bytes, bytearray)) else v2
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    res = dot / (norm_a * norm_b)
    return 0.0 if (math.isnan(res) or math.isinf(res)) else res


def estimate_tokens(text: str) -> int:
    """Deterministic BPE token counter (uses Tier 2 HF tokenizers if installed, else len/3.8 fallback)."""
    if not text:
        return 0
    try:
        from core.accelerators import HAS_TOKENIZERS, count_bpe_tokens
        if HAS_TOKENIZERS:
            return count_bpe_tokens(text)
    except Exception:
        pass
    return max(1, int(math.ceil(len(text) / 3.8)))


def compute_structural_fingerprint(signatures: List[str], imports: Optional[List[str]] = None) -> str:
    """
    Computes an 8-byte (16-hex) structural AST interface digest over exported signatures & imports.
    Immune to internal function-body edits, whitespace formatting, or comment changes.
    """
    import hashlib
    canonical = "\n".join(sorted(s.strip() for s in (signatures or []) if s.strip()))
    if imports:
        canonical += "\n--IMPORTS--\n" + "\n".join(sorted(i.strip() for i in imports if i.strip()))
    return hashlib.blake2b(canonical.encode("utf-8", errors="replace"), digest_size=8).hexdigest()


def truncate_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximate token budget, appending an omission marker."""
    current_tokens = estimate_tokens(text)
    if current_tokens <= max_tokens:
        return text

    ratio = max_tokens / float(current_tokens)
    cutoff = int(len(text) * ratio)
    truncated = text[:cutoff]
    
    last_nl = truncated.rfind('\n')
    if last_nl > cutoff * 0.8:
        truncated = truncated[:last_nl]

    return truncated + f"\n\n... [Truncated: {current_tokens - max_tokens} tokens omitted] ...\n"


# ==============================================================================
# ACTION-OBSERVATION TRAJECTORY STREAM
# ==============================================================================

@dataclass(slots=True)
class Event:
    event_id: str
    kind: str  # 'action' | 'observation' | 'system'
    source: str
    payload: Dict[str, Any]
    action_type: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class ActionObservationStream:
    """
    Pillar 1: Action-Observation Trajectory Stream & Cycle Detector.
    Maintains append-only JSON-L trajectory records, event replay,
    and stuck-loop / cyclical execution detection.
    """

    def __init__(self, log_path: Union[str, Path] = ".orion/working/trajectory.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        kind: str,
        source: str,
        payload: Dict[str, Any],
        action_type: Optional[str] = None
    ) -> Event:
        evt = Event(
            event_id=f"evt_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}",
            kind=kind,
            source=source,
            payload=payload,
            action_type=action_type,
            timestamp=time.time()
        )
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(evt), default=str) + "\n")
        except Exception as e:
            log_telemetry(e, f"ActionObservationStream:record:{kind}")
        return evt

    def record_action(self, source: str, action_type: str, payload: Dict[str, Any]) -> Event:
        return self.record(kind="action", source=source, payload=payload, action_type=action_type)

    def record_observation(self, source: str, payload: Dict[str, Any]) -> Event:
        return self.record(kind="observation", source=source, payload=payload)

    def read_trajectory(self) -> List[Event]:
        if not self.log_path.is_file():
            return []

        events: List[Event] = []
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        data = json.loads(stripped)
                        events.append(Event(
                            event_id=data.get("event_id", ""),
                            kind=data.get("kind", ""),
                            source=data.get("source", ""),
                            payload=data.get("payload", {}),
                            action_type=data.get("action_type"),
                            timestamp=data.get("timestamp", 0.0)
                        ))
        except Exception as e:
            log_telemetry(e, "ActionObservationStream:read_trajectory")
        return events

    def get_last_action(self) -> Optional[Event]:
        traj = self.read_trajectory()
        for evt in reversed(traj):
            if evt.kind == "action":
                return evt
        return None

    def get_last_observation(self) -> Optional[Event]:
        traj = self.read_trajectory()
        for evt in reversed(traj):
            if evt.kind == "observation":
                return evt
        return None

    def detect_stuck_loop(self, window_size: int = 3, session_id: Optional[str] = None) -> bool:
        traj = self.read_trajectory()
        actions = [
            evt for evt in traj
            if evt.kind == "action"
            and (not session_id or not isinstance(evt.payload, dict) or evt.payload.get("session_id", session_id) == session_id)
        ]
        if len(actions) < window_size:
            return False

        recent = actions[-window_size:]
        # Passing CLI commands (exit_code == 0) are legitimate verification gates, not stuck failure loops
        if all(
            isinstance(a.payload, dict)
            and isinstance(a.payload.get("args"), dict)
            and a.payload["args"].get("exit_code") == 0
            for a in recent
        ):
            return False

        first_sig = (recent[0].action_type, json.dumps(recent[0].payload, sort_keys=True))
        all_identical = all(
            (a.action_type, json.dumps(a.payload, sort_keys=True)) == first_sig
            for a in recent
        )
        if all_identical:
            return True

        if len(actions) >= 4 and window_size >= 4:
            r4 = actions[-4:]
            sig0 = (r4[0].action_type, json.dumps(r4[0].payload, sort_keys=True))
            sig1 = (r4[1].action_type, json.dumps(r4[1].payload, sort_keys=True))
            sig2 = (r4[2].action_type, json.dumps(r4[2].payload, sort_keys=True))
            sig3 = (r4[3].action_type, json.dumps(r4[3].payload, sort_keys=True))
            if sig0 == sig2 and sig1 == sig3 and sig0 != sig1:
                return True

        return False

    def detect_sequential_paging(self, consecutive_threshold: int = 3, session_id: Optional[str] = None) -> Optional[str]:
        traj = self.read_trajectory()
        actions = [
            evt for evt in traj
            if evt.kind == "action"
            and (not session_id or not isinstance(evt.payload, dict) or evt.payload.get("session_id", session_id) == session_id)
        ]
        if len(actions) < consecutive_threshold:
            return None

        read_tools = {"view_file", "Read", "read_file", "view_file_outline"}
        target_file = None
        consecutive_count = 0
        spans: List[Tuple[int, int]] = []

        for a in reversed(actions):
            t_name = a.action_type or (a.payload.get("tool_name") if isinstance(a.payload, dict) else "")
            if t_name not in read_tools:
                break

            args = a.payload.get("args", {}) if isinstance(a.payload, dict) else {}
            curr_path = args.get("AbsolutePath") or args.get("file_path") or args.get("path") or args.get("TargetFile")
            if not curr_path:
                break

            try:
                start_l = int(args.get("StartLine") or args.get("offset") or 0)
                end_l = int(args.get("EndLine") or (start_l + int(args.get("limit", 0))) or 0)
            except (ValueError, TypeError):
                start_l, end_l = 0, 0

            if target_file is None:
                target_file = curr_path
                consecutive_count = 1
                spans.append((start_l, end_l))
            elif target_file == curr_path:
                consecutive_count += 1
                spans.append((start_l, end_l))
            else:
                break

            if consecutive_count >= consecutive_threshold:
                ordered = list(reversed(spans))
                min_chunks = max(2, consecutive_threshold)
                is_contiguous_chunking = len(ordered) >= min_chunks and all(
                    ordered[i][1] > 0 and ordered[i + 1][0] > 0 and abs(ordered[i + 1][0] - ordered[i][1]) <= 5
                    for i in range(len(ordered) - 1)
                )
                if is_contiguous_chunking or consecutive_count >= 5:
                    return target_file

        return None

    def replay_trajectory(self, filter_kind: Optional[str] = None) -> List[Dict[str, Any]]:
        traj = self.read_trajectory()
        if filter_kind:
            traj = [e for e in traj if e.kind == filter_kind]
        return [asdict(e) for e in traj]


# ==============================================================================
# SOVEREIGN TRACER & SPAN OBSERVABILITY
# ==============================================================================

class SovereignTracer:
    """
    Pillar 1: Hierarchical Trace & Span Observability Engine.
    Captures nested execution graphs, latency attribution, and token costs
    into SQLite WAL database without cloud telemetry leakage.
    """

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            from core.paths import get_persistence_db_path
            self.db_path = str(get_persistence_db_path())
        else:
            self.db_path = db_path

        self.conn = connect_sqlite(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._active_trace_id: Optional[str] = None
        self._span_stack: List[str] = []
        self._span_counter: int = 0
        self._init_db()

    def _init_db(self) -> None:
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS spans (
                        span_id TEXT PRIMARY KEY,
                        trace_id TEXT NOT NULL,
                        parent_id TEXT,
                        name TEXT NOT NULL,
                        start_time REAL NOT NULL,
                        end_time REAL NOT NULL,
                        latency_ms REAL NOT NULL,
                        prompt_tokens INTEGER DEFAULT 0,
                        completion_tokens INTEGER DEFAULT 0,
                        metadata_json TEXT
                    );
                """)
                self.conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);
                """)
                cur = self.conn.cursor()
                cur.execute("PRAGMA table_info(spans);")
                cols = {row[1] for row in cur.fetchall()}
                if "latency_ms" not in cols:
                    self.conn.execute("ALTER TABLE spans ADD COLUMN latency_ms REAL NOT NULL DEFAULT 0.0;")
                if "metadata_json" not in cols:
                    self.conn.execute("ALTER TABLE spans ADD COLUMN metadata_json TEXT;")
        except Exception as e:
            log_telemetry(e, "telemetry.py:_init_db")

    def start_trace(self, trace_id: Optional[str] = None) -> str:
        self._active_trace_id = trace_id or f"trace_{uuid.uuid4().hex[:12]}"
        self._span_stack.clear()
        return self._active_trace_id

    def record_span(
        self,
        span_id: str,
        trace_id: str,
        parent_id: Optional[str],
        name: str,
        start_t: float,
        end_t: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        latency_ms = max(0.0, (end_t - start_t) * 1000.0)
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT OR REPLACE INTO spans (
                        span_id, trace_id, parent_id, name,
                        start_time, end_time, latency_ms,
                        prompt_tokens, completion_tokens, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    span_id,
                    trace_id,
                    parent_id,
                    name,
                    start_t,
                    end_t,
                    latency_ms,
                    prompt_tokens,
                    completion_tokens,
                    json.dumps(metadata or {}, default=str)
                ))
        except Exception as e:
            log_telemetry(e, f"telemetry.py:record_span:{span_id}")

    @contextmanager
    def span(
        self,
        name: str,
        parent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        active_trace = trace_id or self._active_trace_id or self.start_trace()
        active_parent = parent_id or (self._span_stack[-1] if self._span_stack else None)
        span_id = f"span_{uuid.uuid4().hex[:10]}"

        self._span_counter += 1
        meta_dict = dict(metadata) if metadata else {}
        meta_dict["_seq"] = self._span_counter

        span_ctx: Dict[str, Any] = {
            "span_id": span_id,
            "trace_id": active_trace,
            "parent_id": active_parent,
            "name": name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "metadata": meta_dict
        }

        self._span_stack.append(span_id)
        start_t = time.time()
        try:
            yield span_ctx
        finally:
            end_t = time.time()
            while self._span_stack and self._span_stack[-1] != span_id and span_id in self._span_stack:
                self._span_stack.pop()
            if self._span_stack and self._span_stack[-1] == span_id:
                self._span_stack.pop()

            self.record_span(
                span_id=span_id,
                trace_id=active_trace,
                parent_id=active_parent,
                name=name,
                start_t=start_t,
                end_t=end_t,
                prompt_tokens=span_ctx.get("prompt_tokens", 0),
                completion_tokens=span_ctx.get("completion_tokens", 0),
                metadata=span_ctx.get("metadata", {})
            )

    def get_trace_spans(self, trace_id: str) -> List[Dict[str, Any]]:
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT span_id, trace_id, parent_id, name,
                       start_time, end_time, latency_ms,
                       prompt_tokens, completion_tokens, metadata_json
                FROM spans
                WHERE trace_id = ?
            """, (trace_id,))
            rows = cur.fetchall()

            def _sort_key(r):
                seq = 0
                if r[9]:
                    try:
                        seq = json.loads(r[9]).get("_seq", 0)
                    except Exception as _e:
                        log_telemetry(_e, "telemetry:sort_key")
                return (r[4], seq)

            sorted_rows = sorted(rows, key=_sort_key)
            result = []
            for r in sorted_rows:
                meta = json.loads(r[9]) if r[9] else {}
                meta.pop("_seq", None)
                result.append({
                    "span_id": r[0],
                    "trace_id": r[1],
                    "parent_id": r[2],
                    "name": r[3],
                    "start_time": r[4],
                    "end_time": r[5],
                    "latency_ms": r[6],
                    "prompt_tokens": r[7],
                    "completion_tokens": r[8],
                    "metadata": meta
                })
            return result
        except Exception as e:
            log_telemetry(e, f"telemetry.py:get_trace_spans:{trace_id}")
            return []

    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT COUNT(*),
                       COALESCE(SUM(latency_ms), 0.0),
                       COALESCE(SUM(prompt_tokens), 0),
                       COALESCE(SUM(completion_tokens), 0)
                FROM spans
                WHERE trace_id = ?
            """, (trace_id,))
            row = cur.fetchone()
            if not row or row[0] == 0:
                return {"trace_id": trace_id, "span_count": 0, "total_latency_ms": 0.0, "total_tokens": 0}

            count, total_ms, p_tok, c_tok = row
            return {
                "trace_id": trace_id,
                "span_count": count,
                "total_latency_ms": round(total_ms, 2),
                "prompt_tokens": p_tok,
                "completion_tokens": c_tok,
                "total_tokens": p_tok + c_tok
            }
        except Exception as e:
            log_telemetry(e, f"telemetry.py:get_trace_summary:{trace_id}")
            return {"trace_id": trace_id, "error": str(e)}

    def list_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT trace_id, COUNT(*) as span_count, MIN(start_time) as first_seen,
                       COALESCE(SUM(latency_ms), 0.0) as total_latency,
                       COALESCE(SUM(prompt_tokens + completion_tokens), 0) as total_tokens
                FROM spans
                GROUP BY trace_id
                ORDER BY first_seen DESC
                LIMIT ?
            """, (limit,))
            return [
                {
                    "trace_id": row[0],
                    "span_count": row[1],
                    "first_seen": row[2],
                    "total_latency_ms": round(row[3] or 0.0, 2),
                    "total_tokens": row[4] or 0
                }
                for row in cur.fetchall()
            ]
        except Exception as e:
            log_telemetry(e, "telemetry.py:list_traces")
            return []

    def close(self) -> None:
        if getattr(self, "conn", None):
            try:
                self.conn.close()
            except Exception as _e:
                log_telemetry(_e, "SovereignTracer:close")
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ==============================================================================
# MAIN CLI DISPATCHER
# ==============================================================================

def main():
    raw_args = sys.argv[1:]
    if raw_args and raw_args[0] in ["events", "event_stream"]:
        e_args = raw_args[1:]
        parser = argparse.ArgumentParser(description="Pillar 1: Action-Observation Event Stream")
        parser.add_argument("action", choices=["view", "replay", "stuck"], default="view", nargs="?", help="Action to perform")
        parser.add_argument("--log", type=str, default=".orion/working/trajectory.jsonl", help="Path to trajectory JSON-L file")
        parser.add_argument("--window", type=int, default=3, help="Window size for stuck loop detection")
        args = parser.parse_args(e_args)

        stream = ActionObservationStream(args.log)
        if args.action in ["view", "replay"]:
            events = stream.read_trajectory()
            print(f"[EVENT STREAM: {args.log}] Total events: {len(events)}")
            for idx, evt in enumerate(events, start=1):
                act_tag = f"({evt.action_type})" if evt.action_type else ""
                print(f"  {idx:3d}. [{evt.kind.upper()}] from {evt.source} {act_tag}: {json.dumps(evt.payload)}")
        elif args.action == "stuck":
            stuck = stream.detect_stuck_loop(window_size=args.window)
            if stuck:
                print(f"⚠️ [STUCK LOOP DETECTED] Agent trajectory exhibits repeating/cyclical actions.")
                sys.exit(1)
            else:
                print(f"[PROGRESS NORMAL] No stuck loop detected in the last {args.window} actions.")
                sys.exit(0)
        return

    if raw_args and raw_args[0] in ["telemetry", "trace"]:
        t_args = raw_args[1:]
        parser = argparse.ArgumentParser(description="Pillar 1: Hierarchical Trace Telemetry")
        parser.add_argument("action", choices=["view", "summary", "list"], default="summary", nargs="?", help="Action to perform")
        parser.add_argument("--trace-id", type=str, help="Specific trace ID to inspect")
        parser.add_argument("--db", type=str, help="Path to orion.db")
        args = parser.parse_args(t_args)

        tracer = SovereignTracer(args.db)
        if args.action == "summary" and args.trace_id:
            summary = tracer.get_trace_summary(args.trace_id)
            print(json.dumps(summary, indent=2))
        elif args.action == "view" and args.trace_id:
            spans = tracer.get_trace_spans(args.trace_id)
            print(f"[TRACE SPANS: {args.trace_id}] Total spans: {len(spans)}")
            for s in spans:
                print(f"  • {s['name']} (Latency: {s['latency_ms']}ms, Tokens: {s['prompt_tokens']}+{s['completion_tokens']})")
        elif args.action == "list":
            traces = tracer.list_traces()
            print(f"[RECORDED TRACES] Total: {len(traces)}")
            for t in traces:
                print(f"  • {t['trace_id']} ({t['span_count']} spans, Latency: {t['total_latency_ms']}ms, Tokens: {t['total_tokens']})")
        else:
            print("Usage: orion.py telemetry [summary|view|list] [--trace-id <id>]")
        return

    print("Kernel DB & Foundation Data Layer active.")


if __name__ == "__main__":
    main()
