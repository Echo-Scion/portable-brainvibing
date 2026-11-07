#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
core/worktree.py
----------------
Native, Zero-Pip Worktree Seeder Engine & Declarative Whitelist Synchronizer.
Ports gitignored and untracked environment assets (.env, .orion context, credentials)
into newly created Git worktrees or isolated subagent workspaces with sub-millisecond
reflink (Copy-on-Write), hardlinks, and safe cross-device fallbacks.
"""

import os
import sys
import fnmatch
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Dict, Any, Optional

_WINDOWLESS_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0

DEFAULT_WORKTREE_PATTERNS = [
    ".env",
    ".env.local",
    ".env.*.local",
    ".orion/working/context.json",
    ".agents/.project_manifest.json",
    ".agents/.foundation_path",
    "local/",
]


@dataclass
class WorktreeSeedReport:
    """Report detailing seeded files and mechanism applied."""
    source_root: str
    target_worktree: str
    files_seeded: List[str] = field(default_factory=list)
    dirs_created: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    clone_strategy: str = "auto"
    reflink_count: int = 0
    hardlink_count: int = 0
    copy_count: int = 0
    total_bytes: int = 0
    errors: List[str] = field(default_factory=list)


class WorktreeSeeder:
    """
    Zero-Pip Declarative Worktree Seeder Engine (Pillar 1 Native Floor).
    Supports:
      1. APFS clonefile / Btrfs reflink via os.copy_file_range (Copy-on-Write)
      2. NTFS / POSIX hardlinks via os.link (instant zero-disk duplication)
      3. Cross-volume defensive fallback via shutil.copy2
    """

    INCLUDE_FILENAME = ".worktreeinclude"

    @classmethod
    def load_include_patterns(cls, source_root: str) -> List[str]:
        """Loads whitelist patterns from .worktreeinclude, or falls back to standard templates."""
        patterns: List[str] = []
        inc_file = os.path.join(source_root, cls.INCLUDE_FILENAME)
        template_file = os.path.join(source_root, ".agents", "templates", "worktreeinclude.template")

        target_file = inc_file if os.path.isfile(inc_file) else (template_file if os.path.isfile(template_file) else None)

        if target_file and os.path.isfile(target_file):
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except OSError:
                pass

        if not patterns:
            patterns = list(DEFAULT_WORKTREE_PATTERNS)

        return patterns

    @classmethod
    def match_path(cls, rel_path: str, patterns: List[str]) -> bool:
        """Evaluates whether a relative path matches gitignore-style wildcard patterns."""
        norm = rel_path.replace("\\", "/")
        for pat in patterns:
            pat_norm = pat.replace("\\", "/").rstrip("/")
            if pat.endswith("/"):
                # Directory wildcard
                if norm == pat_norm or norm.startswith(pat_norm + "/"):
                    return True
            else:
                if fnmatch.fnmatch(norm, pat_norm) or fnmatch.fnmatch(os.path.basename(norm), pat_norm):
                    return True
                if norm.startswith(pat_norm + "/"):
                    return True
        return False

    @classmethod
    def fast_clone_file(cls, src: str, dst: str, allow_hardlink: bool = True) -> str:
        """
        Transfers file using the fastest available OS mechanism:
        Reflink -> Hardlink -> Safe Copy.
        """
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        is_dotenv = os.path.basename(src).lower().startswith(".env")
        if is_dotenv:
            allow_hardlink = False

        if os.path.exists(dst):
            try:
                os.remove(dst)
            except OSError:
                pass

        # 1. Reflink (Linux / macOS / APFS via os.copy_file_range where available)
        if not is_dotenv and hasattr(os, "copy_file_range") and sys.platform != "win32":
            try:
                with open(src, "rb") as f_in, open(dst, "wb") as f_out:
                    size = os.path.getsize(src)
                    offset = 0
                    while offset < size:
                        chunk = min(1024 * 1024 * 16, size - offset)
                        copied = os.copy_file_range(f_in.fileno(), f_out.fileno(), chunk)
                        if copied == 0:
                            break
                        offset += copied
                shutil.copystat(src, dst)
                return "reflink"
            except (OSError, AttributeError):
                if os.path.exists(dst):
                    try:
                        os.remove(dst)
                    except OSError:
                        pass

        # 2. Hardlink (Same volume on Windows NTFS / Linux / macOS)
        if allow_hardlink and hasattr(os, "link"):
            try:
                os.link(src, dst)
                return "hardlink"
            except (OSError, AttributeError):
                # Cross-device link (EXDEV) or privilege restriction
                if os.path.exists(dst):
                    try:
                        os.remove(dst)
                    except OSError:
                        pass

        # 3. Defensive Copy Fallback
        shutil.copy2(src, dst)
        if is_dotenv and sys.platform != "win32":
            try:
                os.chmod(dst, 0o600)
            except OSError:
                pass
        return "copy"

    @classmethod
    def seed_worktree(
        cls,
        source_root: str,
        target_worktree: str,
        dry_run: bool = False,
        allow_hardlink: bool = True
    ) -> WorktreeSeedReport:
        """
        Surgically copies whitelisted ignored / untracked environment files
        from source_root into target_worktree.
        """
        abs_src = os.path.abspath(source_root)
        abs_target = os.path.abspath(target_worktree)

        report = WorktreeSeedReport(source_root=abs_src, target_worktree=abs_target)

        if not os.path.isdir(abs_src):
            report.errors.append(f"Source root does not exist: {abs_src}")
            return report

        if abs_src == abs_target:
            report.errors.append("Source root and target worktree cannot be identical.")
            return report

        patterns = cls.load_include_patterns(abs_src)

        # Candidates collection
        candidates: List[str] = []
        for pat in patterns:
            pat_clean = pat.rstrip("/")
            candidate_path = os.path.join(abs_src, pat_clean)
            if os.path.isfile(candidate_path):
                candidates.append(pat_clean)
            elif os.path.isdir(candidate_path):
                # Walk entire subfolder
                for w_root, _, w_files in os.walk(candidate_path):
                    for wf in w_files:
                        full_f = os.path.join(w_root, wf)
                        rel_f = os.path.relpath(full_f, abs_src)
                        candidates.append(rel_f)
            else:
                # Glob search
                base_dir = abs_src
                first_wild = min(
                    (pat_clean.find(c) for c in ("*", "?", "[") if pat_clean.find(c) != -1),
                    default=-1
                )
                if first_wild != -1:
                    prefix_dir = os.path.dirname(pat_clean[:first_wild])
                    search_dir = os.path.join(abs_src, prefix_dir)
                    if os.path.isdir(search_dir):
                        for g_root, _, g_files in os.walk(search_dir):
                            for gf in g_files:
                                full_gf = os.path.join(g_root, gf)
                                rel_gf = os.path.relpath(full_gf, abs_src)
                                if cls.match_path(rel_gf, [pat]):
                                    candidates.append(rel_gf)

        candidates = sorted(list(set(candidates)))

        for rel in candidates:
            src_file = os.path.join(abs_src, rel)
            dst_file = os.path.join(abs_target, rel)

            if not os.path.isfile(src_file):
                continue

            try:
                sz = os.path.getsize(src_file)
            except OSError:
                sz = 0

            if dry_run:
                report.files_seeded.append(rel)
                report.total_bytes += sz
                continue

            try:
                strategy = cls.fast_clone_file(src_file, dst_file, allow_hardlink=allow_hardlink)
                report.files_seeded.append(rel)
                report.total_bytes += sz
                if strategy == "reflink":
                    report.reflink_count += 1
                elif strategy == "hardlink":
                    report.hardlink_count += 1
                else:
                    report.copy_count += 1
            except Exception as e:
                report.errors.append(f"Failed to seed {rel}: {e}")

        return report

    @classmethod
    def list_worktrees(cls, workspace_root: str) -> List[Dict[str, Any]]:
        """Queries git for active worktrees and verifies their warm/seeded status."""
        abs_root = os.path.abspath(workspace_root)
        worktrees = []

        try:
            proc = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=abs_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=_WINDOWLESS_FLAGS,
            )
            if proc.returncode == 0:
                current_entry: Dict[str, str] = {}
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        if current_entry and "worktree" in current_entry:
                            wt_path = current_entry["worktree"]
                            is_main = (os.path.abspath(wt_path) == abs_root)
                            has_env = os.path.isfile(os.path.join(wt_path, ".env"))
                            has_orion = os.path.isfile(os.path.join(wt_path, ".orion", "working", "context.json"))
                            worktrees.append({
                                "path": wt_path,
                                "branch": current_entry.get("branch", "").replace("refs/heads/", ""),
                                "head": current_entry.get("HEAD", ""),
                                "is_main": is_main,
                                "is_warm": has_env or has_orion or is_main,
                            })
                            current_entry = {}
                        continue
                    if " " in line:
                        k, v = line.split(" ", 1)
                        current_entry[k] = v
                    elif line.startswith("bare"):
                        current_entry["bare"] = "true"

                if current_entry and "worktree" in current_entry:
                    wt_path = current_entry["worktree"]
                    is_main = (os.path.abspath(wt_path) == abs_root)
                    has_env = os.path.isfile(os.path.join(wt_path, ".env"))
                    has_orion = os.path.isfile(os.path.join(wt_path, ".orion", "working", "context.json"))
                    worktrees.append({
                        "path": wt_path,
                        "branch": current_entry.get("branch", "").replace("refs/heads/", ""),
                        "head": current_entry.get("HEAD", ""),
                        "is_main": is_main,
                        "is_warm": has_env or has_orion or is_main,
                    })
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return worktrees
