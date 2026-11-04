#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commands/polluter_finder.py
---------------------------
Deterministic Test Pollution Bisector in Python 3 stdlib.
Sequentially executes test files and checks after each file whether unwanted
filesystem/state pollution (e.g., stray .git, lockfiles, leaked DBs) appeared.

Usage:
  python .agents/scripts/orion.py polluter <leak_target> [test_pattern] [--runner <cmd>]
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

_WINDOWLESS_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0


def find_test_files(pattern: str) -> List[str]:
    """Discover matching test files cross-platform."""
    # Support glob patterns like test_*.py or tests/**/*.py
    matched = glob.glob(pattern, recursive=True)
    if not matched:
        # Fallback to search in tests/ or test/ if pattern was relative
        if not pattern.startswith("tests") and not pattern.startswith("test"):
            matched = glob.glob(os.path.join("tests", pattern), recursive=True)
            if not matched:
                matched = glob.glob(os.path.join("test", pattern), recursive=True)
    return sorted(list(set(f for f in matched if os.path.isfile(f))))


def detect_test_runner(test_file: str, custom_runner: Optional[str] = None) -> List[str]:
    """Resolve the test command for a specific file."""
    if custom_runner:
        return [custom_runner, test_file]
    
    ext = os.path.splitext(test_file)[1].lower()
    if ext == ".py":
        return [sys.executable, "-m", "unittest", test_file]
    elif ext in [".ts", ".js", ".tsx", ".jsx"]:
        if os.path.exists("pnpm-lock.yaml"):
            return ["pnpm", "test", test_file]
        return ["npm", "test", "--", test_file]
    elif ext == ".dart":
        return ["flutter", "test", test_file]
    elif ext == ".rs":
        return ["cargo", "test", "--test", Path(test_file).stem]
    
    # Generic fallback
    return [sys.executable, test_file]


def run_bisect(leak_target: str, test_pattern: str, custom_runner: Optional[str] = None) -> int:
    target_path = Path(leak_target)
    print(f"\n🔍 TEST POLLUTION BISECTOR")
    print(f"------------------------------------------------------------")
    print(f"  • Pollution Target : {leak_target}")
    print(f"  • Test Pattern     : {test_pattern}")
    print(f"  • Custom Runner    : {custom_runner or '(auto-detect)'}")

    test_files = find_test_files(test_pattern)
    if not test_files:
        print(f"\n⚠️  Zero test files matched pattern '{test_pattern}'.")
        return 0

    total = len(test_files)
    print(f"  • Found Tests      : {total} file(s)\n")

    for idx, test_file in enumerate(test_files, 1):
        if target_path.exists():
            print(f"⚠️  Pollution target already exists prior to test {idx}/{total}: {test_file}")
            print(f"   Skipping run to prevent false identification.")
            continue

        print(f"[{idx}/{total}] Running: {test_file} ...", end=" ", flush=True)
        cmd = detect_test_runner(test_file, custom_runner)
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=_WINDOWLESS_FLAGS,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            print("OK" if res.returncode == 0 else f"FAIL({res.returncode})")
        except subprocess.TimeoutExpired:
            print("TIMEOUT (120s)")
        except Exception as e:
            print(f"ERROR ({e})")

        # Check if pollution target appeared
        if target_path.exists():
            print(f"\n" + "=" * 60)
            print(f"🎯 FOUND POLLUTER TEST!")
            print(f"   Test File: {test_file}")
            print(f"   Created  : {leak_target}")
            print(f"=" * 60)
            print(f"Remediation:")
            print(f"  1. Run isolated test: {' '.join(cmd)}")
            print(f"  2. Inspect test cleanup teardown / mock restore logic.")
            return 1

    print(f"\n✅ No polluter found — all {total} test file(s) executed without creating {leak_target}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic Test Pollution Bisector")
    parser.add_argument("target", help="File or directory path that should not be created")
    parser.add_argument("pattern", nargs="?", default="tests/**/*.py", help="Glob pattern for test files")
    parser.add_argument("--runner", default=None, help="Custom runner executable (e.g. pytest)")
    args = parser.parse_args()

    return run_bisect(args.target, args.pattern, args.runner)


if __name__ == "__main__":
    sys.exit(main())
