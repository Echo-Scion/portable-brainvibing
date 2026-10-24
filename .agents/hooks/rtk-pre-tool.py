#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rtk-pre-tool.py - Resilient, CWD-Agnostic PreToolUse Hook Launcher.

Guarantees:
1. Works whether executed from workspace root or inside .agents/ or .agents/hooks/.
2. Always fails open (Exit Code 0) if orion.py, Python dependencies, or RTK are missing/errored,
   preventing Antigravity / Claude Code circuit breakers (Exit Code 2 lockout) from bricking the IDE.
"""
import sys
import os
import subprocess

def main() -> int:
    try:
        # Determine paths relative to this script file
        this_dir = os.path.dirname(os.path.abspath(__file__))
        agents_dir = os.path.dirname(this_dir) # .agents
        workspace_root = os.path.dirname(agents_dir)

        # Candidates for orion.py
        candidate_paths = [
            os.path.join(agents_dir, "scripts", "orion.py"),
            os.path.join(workspace_root, ".agents", "scripts", "orion.py"),
            os.path.join(os.getcwd(), ".agents", "scripts", "orion.py"),
            os.path.join(os.getcwd(), "scripts", "orion.py"),
        ]

        orion_path = None
        for p in candidate_paths:
            if os.path.isfile(p):
                orion_path = p
                break

        if not orion_path:
            # Fail open gracefully
            return 0

        # Execute orion.py rtk hook antigravity directly using same python interpreter
        cmd = [sys.executable, orion_path, "rtk", "hook", "antigravity"]
        
        # Read standard input if available (Antigravity passes tool invocation payload via stdin)
        stdin_data = None
        try:
            if not sys.stdin.isatty():
                stdin_data = sys.stdin.buffer.read()
        except Exception:
            stdin_data = None

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if stdin_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace_root if os.path.isdir(workspace_root) else os.getcwd()
        )
        stdout_bytes, stderr_bytes = proc.communicate(input=stdin_data)

        # Emit output back to host IDE
        if stdout_bytes:
            sys.stdout.buffer.write(stdout_bytes)
            sys.stdout.flush()

        # If child exited with an error, do NOT fail closed with 2 unless intended;
        # For pre-tool hooks, non-zero return codes block all IDE tools.
        # RTK rewrite emits code 0 on success or harmless bypass.
        return proc.returncode if proc.returncode == 0 else 0

    except Exception:
        # Fail-open guarantee: Never block the agent due to unhandled exceptions in hook launcher
        return 0

if __name__ == "__main__":
    sys.exit(main())
