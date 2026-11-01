#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
commands/worktree.py
--------------------
CLI interface for worktree management & declarative whitelist seeder.
Commands:
  python .agents/scripts/orion.py worktree seed <target_path>
  python .agents/scripts/orion.py worktree add <branch> [path]
  python .agents/scripts/orion.py worktree list
"""

import os
import sys
import argparse
import subprocess
from typing import List

_WINDOWLESS_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0


def cmd_worktree_seed(args: argparse.Namespace) -> int:
    from core.worktree import WorktreeSeeder
    source_root = os.path.abspath(args.source or ".")
    target_path = os.path.abspath(args.target)

    print(f"\n🌱 WORKTREE SEEDER: {os.path.basename(target_path)}")
    print("------------------------------------------------------------")
    print(f"  • Source Root       : {source_root}")
    print(f"  • Target Worktree   : {target_path}")
    print(f"  • Dry Run           : {args.dry_run}")

    report = WorktreeSeeder.seed_worktree(
        source_root=source_root,
        target_worktree=target_path,
        dry_run=args.dry_run,
        allow_hardlink=not args.copy_only,
    )

    if report.errors:
        print("\n❌ Seed Errors Encountered:")
        for err in report.errors:
            print(f"  - {err}")
        return 1

    print(f"\n✅ Seeded {len(report.files_seeded)} asset(s) ({report.total_bytes / 1024:.1f} KB):")
    for f in report.files_seeded:
        print(f"  • {f}")

    if not args.dry_run:
        methods = []
        if report.reflink_count:
            methods.append(f"{report.reflink_count} reflink")
        if report.hardlink_count:
            methods.append(f"{report.hardlink_count} hardlink")
        if report.copy_count:
            methods.append(f"{report.copy_count} copy")
        method_summary = ", ".join(methods) if methods else "zero copies"
        print(f"\n🚀 Worktree Warmed Successfully ({method_summary}). Ready for sub-agent execution.\n")
    else:
        print("\n[DRY RUN] Zero files written to disk.\n")

    return 0


def cmd_worktree_add(args: argparse.Namespace) -> int:
    from core.worktree import WorktreeSeeder
    source_root = os.path.abspath(args.source or ".")
    branch = args.branch
    target_path = args.path or os.path.join(source_root, ".worktrees", branch)
    abs_target = os.path.abspath(target_path)

    print(f"\n🌿 SPAWNING ISOLATED WORKTREE: {branch}")
    print("------------------------------------------------------------")
    print(f"  • Branch Target     : {branch}")
    print(f"  • Destination Path  : {abs_target}")

    # 1. Run git worktree add
    os.makedirs(os.path.dirname(abs_target), exist_ok=True)
    git_cmd = ["git", "worktree", "add", "-b", branch, abs_target]
    if args.base:
        git_cmd.append(args.base)

    try:
        proc = subprocess.run(
            git_cmd,
            cwd=source_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=_WINDOWLESS_FLAGS,
        )
        if proc.returncode != 0:
            # Maybe branch exists, try without -b
            git_cmd_existing = ["git", "worktree", "add", abs_target, branch]
            proc = subprocess.run(
                git_cmd_existing,
                cwd=source_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=_WINDOWLESS_FLAGS,
            )
            if proc.returncode != 0:
                print(f"\n❌ Git worktree add failed:\n{proc.stderr.strip()}")
                return 1
    except Exception as e:
        print(f"\n❌ Failed to invoke git worktree: {e}")
        return 1

    print("  • Git Worktree Created: Exit Code 0")

    # 2. Seed worktree with .worktreeinclude
    report = WorktreeSeeder.seed_worktree(
        source_root=source_root,
        target_worktree=abs_target,
        dry_run=False,
        allow_hardlink=not args.copy_only,
    )

    if report.files_seeded:
        print(f"  • Seeded {len(report.files_seeded)} ignored environment asset(s):")
        for f in report.files_seeded:
            print(f"    - {f}")

    print(f"\n✅ Isolated workspace ready at: {abs_target}\n")
    return 0


def cmd_worktree_list(args: argparse.Namespace) -> int:
    from core.worktree import WorktreeSeeder
    workspace_root = os.path.abspath(args.source or ".")
    wts = WorktreeSeeder.list_worktrees(workspace_root)

    print(f"\n🌲 ACTIVE GIT WORKTREES: {os.path.basename(workspace_root)}")
    print("------------------------------------------------------------")
    if not wts:
        print("  • No active worktrees found (or not a git repository).\n")
        return 0

    for idx, wt in enumerate(wts, 1):
        main_label = " [MAIN WORKSPACE]" if wt["is_main"] else ""
        warm_icon = "🔥 WARM" if wt["is_warm"] else "❄️  COLD"
        print(f"  {idx}. {wt['branch'] or 'detached'}{main_label}")
        print(f"     Path   : {wt['path']}")
        print(f"     Status : {warm_icon}")
        print(f"     HEAD   : {wt['head'][:8] if wt['head'] else 'unknown'}")
        print()

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Declarative Worktree Seeder & Workspace Manager")
    subparsers = parser.add_subparsers(dest="subaction")

    # seed
    p_seed = subparsers.add_parser("seed", help="Seed an existing worktree from .worktreeinclude")
    p_seed.add_argument("target", help="Path to target worktree directory")
    p_seed.add_argument("--source", default=".", help="Source root directory (default: current directory)")
    p_seed.add_argument("--dry-run", action="store_true", help="Simulate seeding without copying files")
    p_seed.add_argument("--copy-only", action="store_true", help="Disallow hardlinks and force standard file copies")

    # add
    p_add = subparsers.add_parser("add", help="Create a new git worktree and atomically seed environment assets")
    p_add.add_argument("branch", help="New branch name for the worktree")
    p_add.add_argument("path", nargs="?", default=None, help="Destination directory path (default: .worktrees/<branch>)")
    p_add.add_argument("--base", default=None, help="Base commit / branch to branch off of")
    p_add.add_argument("--source", default=".", help="Source root directory (default: current directory)")
    p_add.add_argument("--copy-only", action="store_true", help="Disallow hardlinks and force standard file copies")

    # list
    p_list = subparsers.add_parser("list", help="List active git worktrees and their warm/cold seed status")
    p_list.add_argument("--source", default=".", help="Workspace root directory (default: current directory)")

    parsed_args = parser.parse_args(argv)

    if parsed_args.subaction == "seed":
        return cmd_worktree_seed(parsed_args)
    elif parsed_args.subaction == "add":
        return cmd_worktree_add(parsed_args)
    elif parsed_args.subaction == "list":
        return cmd_worktree_list(parsed_args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
