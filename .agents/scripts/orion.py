#!/usr/bin/env python
import sys
import os
import subprocess
import time

# Ensure .agents/scripts is in sys.path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# Prevent Python from writing .pyc and __pycache__ inside .agents ecosystem
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Force utf-8 encoding for standard output to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()

load_env()

CMD_MAP = {
    "brain": ["commands", "brain.py"],
    "context": ["commands", "brain.py"],
    "ingest": ["commands", "brain.py"],
    "gc": ["commands", "brain.py"],
    "clean": ["commands", "brain.py"],
    "verify": ["commands", "verify_agents.py"],
    "verify_agents": ["commands", "verify_agents.py"],
    "orion_ops": ["commands", "brain.py"],
    "orion": ["commands", "brain.py"],
    "deploy": ["commands", "foundation.py"],
    "push-upstream": ["commands", "foundation.py"],
    "sync-ai": ["commands", "foundation.py"],
    "foundation": ["commands", "foundation.py"],
    "scan": ["core", "scanner.py"],
    "scanner": ["core", "scanner.py"],
    "compress": ["commands", "brain.py"],
    "compress_memory": ["commands", "brain.py"],
    "amnesia": ["commands", "state_machine.py"],
    "rule_eviction": ["commands", "state_machine.py"],
    "preflight": ["commands", "verify_agents.py"],
    "preflight_check": ["commands", "verify_agents.py"],

    "budget": ["commands", "state_machine.py"],
    "track_budget": ["commands", "state_machine.py"],
    "compile": ["commands", "brain.py"],
    "compile_rules": ["commands", "brain.py"],
    "context-lint": ["commands", "verify_agents.py"],
    "context_naming_lint": ["commands", "verify_agents.py"],
    "instruction-lint": ["commands", "verify_agents.py"],
    "instruction_language_lint": ["commands", "verify_agents.py"],
    "linkify": ["commands", "reflexion.py"],
    "matrix": ["commands", "brain.py"],
    "matrix-query": ["commands", "brain.py"],
    "matrix_query": ["commands", "brain.py"],
    "rtk": ["core", "capabilities.py"],
    "rtk_proxy": ["core", "capabilities.py"],
    "adversarial": ["commands", "verify_agents.py"],
    "security": ["core", "security.py"],
    "memory": ["commands", "brain.py"],
    "reflexion": ["commands", "reflexion.py"],
    "reflect": ["commands", "reflexion.py"],
    "record": ["commands", "reflexion.py"],

    "raw_ingest": ["commands", "brain.py"],
    "consolidate": ["commands", "reflexion.py"],
    "contradict": ["commands", "brain.py"],
    "fsm": ["commands", "state_machine.py"],
    "shrink": ["commands", "brain.py"],
    "distill": ["commands", "brain.py"],
    "eval": ["..", "evals", "audit_aesthetics.py"],
    "contrast": ["..", "evals", "audit_aesthetics.py"],
    "pack": ["utils", "packer.py"],
    "packer": ["utils", "packer.py"],
    "digest": ["utils", "packer.py"],
    "assert": ["..", "evals", "assertion_engine.py"],
    "validate-response": ["..", "evals", "assertion_engine.py"],
    "response-validator": ["..", "evals", "assertion_engine.py"],
    "consequence": ["..", "evals", "consequence_verifier.py"],
    "consequence-verify": ["..", "evals", "consequence_verifier.py"],
    "false-green": ["..", "evals", "consequence_verifier.py"],
    "bun": ["core", "capabilities.py"],
    "bun_runtime": ["core", "capabilities.py"],
    "compact": ["commands", "brain.py"],
    "compactor": ["commands", "brain.py"],
    "state_graph": ["commands", "state_machine.py"],
    "telemetry": ["core", "db.py"],
    "trace": ["core", "db.py"],
    "sandbox": ["core", "sandbox.py"],
    "event_stream": ["core", "db.py"],
    "events": ["core", "db.py"],
    "harness": ["core", "harness", "engine.py"],
    "sovereign_harness": ["core", "harness", "engine.py"],
    "compile_ast": ["core", "security.py"],
    "ast_rules": ["core", "security.py"],
    "diagnostics": ["commands", "brain.py"],
    "repomap": ["core", "scanner.py"],
    "graph": ["core", "orion_graph.py"],
    "orion_graph": ["core", "orion_graph.py"]
}

_ALIAS_NAMES = {
    "verify_agents", "orion", "push-upstream", "sync-ai", "scanner",
    "compress_memory", "amnesia", "rule_eviction", "preflight_check",
    "track_budget", "compile_rules", "context_naming_lint",
    "instruction_language_lint", "matrix-query", "matrix_query",
    "rtk_proxy", "reflect", "trace", "response-validator",
    "bun_runtime", "compactor", "events", "consequence-verify", "false-green",
    "sovereign_harness", "compile_ast", "ast_rules", "repomap", "orion_graph",
    "packer", "digest", "contrast", "event_stream", "clean"
}
CANONICAL_CMD_MAP = {name: path for name, path in CMD_MAP.items() if name not in _ALIAS_NAMES}
ALIAS_CMD_MAP = {name: CMD_MAP[name] for name in _ALIAS_NAMES}

DEPRECATED_ALIASES = {
    "deploy": "foundation deploy",
    "push-upstream": "foundation push-upstream",
    "sync-ai": "foundation sync-ai",
}

# Phase 3 — Compression Suite group dispatch
# Usage: orion.py compact <level|engine> [args...]
COMPACT_GROUP = {
    # 5 Tingkat Kompresi Native .agents
    "lite":       ["commands", "brain.py", "compact", "--level", "lite"],
    "stream":     ["commands", "brain.py", "compact", "--level", "stream"],
    "full":       ["commands", "brain.py", "compact", "--level", "full"],
    "aggressive": ["commands", "brain.py", "compact", "--level", "aggressive"],
    "ultra":      ["commands", "brain.py", "compact", "--level", "ultra"],
    "pipeline":   ["commands", "brain.py", "compact", "--level", "pipeline"],
    # Sub-mesin spesifik & kompatibilitas mundur
    "stopword":   ["commands", "brain.py", "compress"],
    "compress":   ["commands", "brain.py", "compress"],
    "shrink":     ["commands", "brain.py", "shrink"],
    "fts5":       ["commands", "brain.py", "compact", "--level", "ultra"],
    "compactor":  ["commands", "brain.py", "compact", "--level", "pipeline"],
    "distill":    ["commands", "brain.py", "distill"],
}

# Grouped help sections — order matters for display
_HELP_GROUPS = {
    "Brain / Knowledge":   ["brain", "context", "ingest", "orion_ops", "raw_ingest", "consolidate",
                            "contradict", "linkify", "memory", "graph", "gc"],
    "Scan / Audit":        ["scan", "verify", "security", "eval", "preflight",
                            "adversarial", "context-lint", "instruction-lint",
                            "matrix", "compile", "consequence"],
    "Compression Suite":   ["compact", "compress", "shrink", "distill"],
    "Foundation / Deploy": ["foundation", "bun"],
    "Runtime / Misc":      ["fsm", "reflexion", "harness", "rtk", "telemetry",
                            "sandbox", "events", "pack", "budget",
                            "compile_ast", "diagnostics", "validate-response",
                            "assert", "state_graph"],
}


def print_help():
    print("========================================")
    print(" ORION: The Unified Brain Engine CLI")
    print("========================================\n")
    print("Usage: python .agents/scripts/orion.py <command> [args...]\n")
    shown = set()
    for group, cmds in _HELP_GROUPS.items():
        visible = [c for c in cmds if c in CANONICAL_CMD_MAP or c in COMPACT_GROUP]
        if not visible:
            continue
        print(f"  [{group}]")
        for cmd in visible:
            print(f"    {cmd:<20}")
            shown.add(cmd)
        print()
    ungrouped = [c for c in sorted(CANONICAL_CMD_MAP) if c not in shown]
    if ungrouped:
        print("  [Other]")
        for cmd in ungrouped:
            print(f"    {cmd:<20}")
        print()
    print("  Compression levels & sub-engines:")
    print("    orion.py compact <lite|stream|full|aggressive|ultra|pipeline|shrink|distill> [args...]")
    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print_help()
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    cmd = sys.argv[1]

    # High-frequency in-process fast path (Pillar 2 RTK proxy)
    if cmd in ("rtk", "rtk_proxy"):
        from core.capabilities import run_rtk_proxy
        sys.exit(run_rtk_proxy(sys.argv[2:]))

    # Phase 3: compact group dispatch — orion.py compact <engine> [args...]
    if cmd == "compact" and len(sys.argv) >= 3 and sys.argv[2] in COMPACT_GROUP:
        engine = sys.argv[2]
        entry = COMPACT_GROUP[engine]
        rel_path = entry[:2]
        extra_args = entry[2:]
        target_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), *rel_path)
        args = extra_args + sys.argv[3:]
        python_exec = sys.executable or "python"
        t0 = time.time()
        try:
            result = subprocess.run([python_exec, "-B", target_script] + args)
            t1 = time.time()
            try:
                from core.db import SovereignTracer
                with SovereignTracer() as tracer:
                    tracer.record_span(
                        span_id=f"cli_{int(t0 * 1000)}",
                        trace_id=os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session"),
                        parent_id=None,
                        name=f"orion:compact:{engine}",
                        start_t=t0,
                        end_t=t1,
                        metadata={"exit_code": result.returncode, "args": args[:3]}
                    )
            except Exception as _te:
                try:
                    from core.db import log_telemetry
                    log_telemetry(_te, "orion:record_span")
                except Exception as _fallback_err:
                    if os.environ.get("ORION_DEBUG"):
                        sys.stderr.write(f"[ORION_FALLBACK_ERR] {_fallback_err}\n")
            try:
                from core.harness.capture import ToolQuantumCapture
                workspace_dir = os.path.dirname(os.path.dirname(SCRIPTS_DIR))
                harness_state_dir = os.path.join(workspace_dir, '.orion', 'harness')
                capture = ToolQuantumCapture(state_dir=harness_state_dir)
                session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
                capture.record_tool_call(session_id, f"orion:compact:{engine}", {"args": args[:3], "exit_code": result.returncode})
            except Exception as _ce:
                try:
                    from core.db import log_telemetry
                    log_telemetry(_ce, "orion:compact:record_tool_quantum")
                except Exception as _fallback_err:
                    if os.environ.get("ORION_DEBUG"):
                        sys.stderr.write(f"[ORION_FALLBACK_ERR] {_fallback_err}\n")
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(130)

    if cmd in CANONICAL_CMD_MAP:
        rel_path = CANONICAL_CMD_MAP[cmd]
    elif cmd in ALIAS_CMD_MAP:
        rel_path = ALIAS_CMD_MAP[cmd]
        target_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), *rel_path)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
    target_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), *rel_path)

    if cmd in DEPRECATED_ALIASES:
        sys.stderr.write(
            f"[DEPRECATION] '{cmd}' is deprecated; "
            f"use '{DEPRECATED_ALIASES[cmd]}'.\n"
        )

    # Foundation, state machine, verify_agents, evals, brain, db, and reflexion subcommands are passed explicitly
    if cmd in {
        "deploy", "push-upstream", "sync-ai", "budget", "track_budget", "amnesia", "rule_eviction",
        "consolidate", "linkify", "record", "reflect", "reflexion", "state_graph",
        "preflight", "preflight_check", "context-lint", "context_naming_lint",
        "instruction-lint", "instruction_language_lint", "adversarial",
        "validate-response", "response-validator",
        "orion_ops", "orion", "compress", "compress_memory", "compile", "compile_rules",
        "matrix", "matrix-query", "matrix_query", "memory", "raw_ingest", "contradict",
        "shrink", "distill", "compact", "compactor", "diagnostics", "context", "ingest",
        "gc", "clean", "rtk", "rtk_proxy", "bun", "bun_runtime",
        "repomap", "telemetry", "trace", "events", "event_stream"
    }:
        args = [cmd] + sys.argv[2:]
    else:
        args = sys.argv[2:]

    python_exec = sys.executable or "python"

    t0 = time.time()
    exit_code = 0
    in_process_success = False
    orig_argv = list(sys.argv)

    try:
        import runpy
        sys.argv = [target_script] + args
        try:
            runpy.run_path(target_script, run_name="__main__")
            exit_code = 0
            in_process_success = True
        except SystemExit as se:
            if se.code is None:
                exit_code = 0
            elif isinstance(se.code, int):
                exit_code = se.code
            else:
                sys.stderr.write(f"{se.code}\n")
                exit_code = 1
            in_process_success = True
        finally:
            sys.argv = orig_argv
    except KeyboardInterrupt:
        sys.argv = orig_argv
        sys.exit(130)
    except Exception as _runpy_err:
        sys.argv = orig_argv
        if os.environ.get("ORION_DEBUG"):
            sys.stderr.write(f"[ORION_RUNPY_FALLBACK] In-process execution fell back: {_runpy_err}\n")
        in_process_success = False

    if not in_process_success:
        try:
            result = subprocess.run([python_exec, "-B", target_script] + args)
            exit_code = result.returncode
        except KeyboardInterrupt:
            sys.exit(130)

    t1 = time.time()
    try:
        from core.db import SovereignTracer
        with SovereignTracer() as tracer:
            tracer.record_span(
                span_id=f"cli_{int(t0 * 1000)}",
                trace_id=os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session"),
                parent_id=None,
                name=f"orion:{cmd}",
                start_t=t0,
                end_t=t1,
                metadata={"exit_code": exit_code, "args": args[:3]}
            )
    except Exception as _te:
        try:
            from core.db import log_telemetry
            log_telemetry(_te, "orion:record_span")
        except Exception as _fallback_err:
            if os.environ.get("ORION_DEBUG"):
                sys.stderr.write(f"[ORION_FALLBACK_ERR] {_fallback_err}\n")
    try:
        from core.harness.capture import ToolQuantumCapture
        workspace_dir = os.path.dirname(os.path.dirname(SCRIPTS_DIR))
        harness_state_dir = os.path.join(workspace_dir, '.orion', 'harness')
        capture = ToolQuantumCapture(state_dir=harness_state_dir)
        session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
        capture.record_tool_call(session_id, f"orion:{cmd}", {"args": args[:3], "exit_code": exit_code})
    except Exception as _ce:
        try:
            from core.db import log_telemetry
            log_telemetry(_ce, "orion:record_tool_quantum")
        except Exception as _fallback_err:
            if os.environ.get("ORION_DEBUG"):
                sys.stderr.write(f"[ORION_FALLBACK_ERR] {_fallback_err}\n")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
