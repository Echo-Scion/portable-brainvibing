"""
Kernel Paths
Provides canonical path discovery and normalization across the workspace, .agents, .orion, context, and scratch.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Union, List, Set, Tuple, Optional, Callable, Dict

WINDOWLESS_FLAGS: int = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0


DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git", ".orion", ".scratch", "scratch", "node_modules", "vendor",
    "build", "dist", "target", ".cache", "__pycache__", ".dart_tool",
    ".gradle", ".idea", ".vscode", ".gemini", ".cursor", ".claude",
    ".clinerules", ".hermes", "coverage", ".worktrees", "temp", "tmp",
    ".turbo", ".next", ".pytest_cache", ".mypy_cache", ".svelte-kit",
    ".nuxt", "out", "Pods", "DerivedData", "CMakeFiles", "obj", ".bundle",
    "bower_components", "venv", ".venv", "env", "installs", "backups",
    "cache", "audio_cache", "image_cache", "state-snapshots", "logs",
    "hermes-agent"
}

DEFAULT_IGNORE_FILENAMES: Set[str] = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "pubspec.lock",
    "cargo.lock", "poetry.lock", "composer.lock", "gemfile.lock", "pipfile.lock",
    "bun.lockb", "bun.lock", "uv.lock", "gradle.lockfile", "podfile.lock",
    ".ds_store", "thumbs.db", "desktop.ini"
}

AGENT_TOOLING_DIRS: Set[str] = {
    ".agents", ".orion", ".gemini", ".claude", ".cursor", ".opencode", ".hermes",
    ".antigravity-plugin", ".claude-plugin", ".cursor-plugin", ".codex-plugin",
    ".devin-plugin", ".copilot-plugin", ".kimi-plugin", ".hermes-plugin",
    ".muse-plugin", ".droid-plugin", ".grok-plugin", ".pi-plugin",
    ".qwen-plugin", ".minimax-plugin", ".mimo-plugin"
}

AGENT_ROOT_FILES: Set[str] = {
    "agents.md", "gemini.md", "claude.md", "minimax.md", "mimo.md",
    "learnings.md", "gemini-extension.json", "deploy_me.md", "agent_identity.md"
}


def is_agent_tooling_path(rel_path: str, root_dir: str = "") -> bool:
    norm = rel_path.replace("\\", "/").strip("/")
    if not norm:
        return False
    parts = norm.split("/")
    first_seg = parts[0]
    if first_seg in AGENT_TOOLING_DIRS or first_seg.endswith("-plugin"):
        return True
    if len(parts) == 1:
        f_low = first_seg.lower()
        if f_low == "agents.md":
            return False
        if f_low == "gemini.md":
            if root_dir and os.path.isfile(os.path.join(root_dir, "AGENTS.md")):
                return True
            return False
        if f_low in AGENT_ROOT_FILES:
            return True
    if parts[-1].lower() in AGENT_ROOT_FILES:
        return True
    if norm.startswith(".github/copilot"):
        return True
    return False


class GitIgnoreFilter:
    """Hierarchical gitignore matcher supporting nested monorepo .gitignore & .agentsignore files."""

    def __init__(
        self,
        root_dir: Union[str, Path],
        exclude_agent_tooling: bool = False,
        custom_ignore_dirs: Optional[Set[str]] = None,
        custom_ignore_filenames: Optional[Set[str]] = None,
        asset_filter_fn: Optional[Callable[[str], bool]] = None,
    ):
        self.root_dir = os.path.abspath(str(root_dir))
        self.exclude_agent_tooling = exclude_agent_tooling
        self.ignore_dirs = set(DEFAULT_IGNORE_DIRS)
        if custom_ignore_dirs:
            self.ignore_dirs.update(custom_ignore_dirs)
        self.ignore_filenames = set(DEFAULT_IGNORE_FILENAMES)
        if custom_ignore_filenames:
            self.ignore_filenames.update(custom_ignore_filenames)
        self.asset_filter_fn = asset_filter_fn
        self.rules: List[Tuple[str, re.Pattern, bool, bool]] = []
        self._loaded_dirs: Set[str] = set()
        self._load_ignore_files_for_dir("")

    def _load_ignore_files_for_dir(self, rel_dir: str) -> None:
        if rel_dir in self._loaded_dirs:
            return
        self._loaded_dirs.add(rel_dir)
        target_dir = os.path.join(self.root_dir, rel_dir) if rel_dir else self.root_dir
        for fname in (".gitignore", ".agentsignore"):
            gi_path = os.path.join(target_dir, fname)
            if not os.path.isfile(gi_path):
                continue
            try:
                with open(gi_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f.read().splitlines():
                        self.add_rule(line, base_rel_dir=rel_dir)
            except Exception:
                pass

    def add_rule(self, line: str, base_rel_dir: str = "") -> None:
        raw = line.strip()
        if not raw or raw.startswith("#"):
            return
        is_neg = raw.startswith("!")
        if is_neg:
            raw = raw[1:].strip()
        is_dir_only = raw.endswith("/")
        if is_dir_only:
            raw = raw.rstrip("/")
        is_anchored = raw.startswith("/") or ("/" in raw)
        clean_pat = raw.lstrip("/")
        if clean_pat:
            compiled = self._git_glob_to_regex(clean_pat, is_anchored)
            self.rules.append((base_rel_dir.replace("\\", "/").strip("/"), compiled, is_neg, is_dir_only))

    @staticmethod
    def _git_glob_to_regex(pat: str, is_anchored: bool) -> re.Pattern:
        out = ["^" if is_anchored else "(?:^|/)"]
        i, n = 0, len(pat)
        while i < n:
            if pat[i] == "\\" and i + 1 < n:
                out.append(re.escape(pat[i + 1]))
                i += 2
            elif pat[i:i + 3] == "**/":
                out.append("(?:.+/)?")
                i += 3
            elif pat[i:i + 2] == "**":
                out.append(".*")
                i += 2
            elif pat[i] == "*":
                out.append("[^/]*")
                i += 1
            elif pat[i] == "?":
                out.append("[^/]")
                i += 1
            elif pat[i] == "[":
                j = pat.find("]", i + 1)
                if j != -1:
                    inner = pat[i + 1:j]
                    if inner.startswith("!"):
                        inner = "^" + inner[1:]
                    out.append(f"[{inner}]")
                    i = j + 1
                else:
                    out.append(r"\[")
                    i += 1
            else:
                out.append(re.escape(pat[i]))
                i += 1
        out.append("(?:$|/)")
        return re.compile("".join(out))

    def is_ignored(self, rel_path: str, is_dir: bool = False) -> bool:
        norm = rel_path.replace("\\", "/").strip("/")
        if not norm or norm == ".":
            return False
        if self.exclude_agent_tooling and is_agent_tooling_path(norm, self.root_dir):
            return True

        parts = norm.split("/")
        check_parts = parts if is_dir else parts[:-1]
        if any(p in self.ignore_dirs for p in check_parts):
            return True
        if not is_dir:
            if parts[-1].lower() in self.ignore_filenames:
                return True
            if self.asset_filter_fn and self.asset_filter_fn(norm):
                return True

        accum = ""
        for part in parts[:-1]:
            accum = f"{accum}/{part}" if accum else part
            self._load_ignore_files_for_dir(accum)

        ignored = False
        for base_dir, regex, is_neg, dir_only in self.rules:
            if base_dir:
                if not (norm == base_dir or norm.startswith(base_dir + "/")):
                    continue
                sub_path = norm[len(base_dir):].lstrip("/")
            else:
                sub_path = norm
            if not sub_path:
                continue
            m = regex.search(sub_path)
            if m:
                if dir_only and not is_dir:
                    if m.end() == len(sub_path) and "/" not in sub_path[m.start():]:
                        continue
                ignored = not is_neg
        return ignored


def should_traverse_dir(
    dir_name: str,
    ignore_filter: Optional[GitIgnoreFilter] = None,
    rel_path: str = "",
    allow_agents: bool = False,
) -> bool:
    """Unified in-place dirs[:] pruner across all workspace scans."""
    if dir_name in DEFAULT_IGNORE_DIRS or dir_name.lower() in DEFAULT_IGNORE_DIRS:
        return False
    if dir_name.startswith("."):
        if dir_name == ".agents" and allow_agents:
            return True
        if dir_name in {".github", ".storybook"}:
            return True
        return False
    if ignore_filter:
        check_path = f"{rel_path}/{dir_name}".strip("/") if rel_path else dir_name
        if ignore_filter.is_ignored(check_path, is_dir=True):
            return False
    return True


def get_workspace_files(
    workspace_dir: Optional[Union[str, Path]] = None,
    extensions: Optional[Tuple[str, ...]] = None,
    tracked_only: bool = True,
    include_agents: bool = True,
) -> List[str]:
    """
    Returns relative paths (normalized with forward slashes) of workspace files.
    Prefers git ls-files for sub-50ms execution and automatic virtualenv/build exclusion.
    Falls back to os.walk with GitIgnoreFilter when outside Git.
    """
    ws = Path(workspace_dir).resolve() if workspace_dir else get_workspace_dir()
    ws_str = str(ws)

    # 1. Fast Git-native query
    if tracked_only:
        try:
            cmd = ["git", "ls-files"]
            flags = WINDOWLESS_FLAGS
            proc = subprocess.run(
                cmd,
                cwd=ws_str,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5.0,
                shell=False,
                creationflags=flags,
            )
            if proc.returncode == 0:
                files = []
                for line in proc.stdout.splitlines():
                    f = line.strip().replace("\\", "/")
                    if not f:
                        continue
                    if not include_agents and f.startswith(".agents/"):
                        continue
                    if extensions is None or any(f.endswith(ext) for ext in extensions):
                        files.append(f)
                return sorted(files)
        except Exception:
            pass

    # 2. Dynamic GitIgnoreFilter fallback
    gif = GitIgnoreFilter(ws_str, exclude_agent_tooling=not include_agents)
    collected = []
    for root, dirs, filenames in os.walk(ws_str):
        rel_root = os.path.relpath(root, ws_str).replace("\\", "/")
        if rel_root == ".":
            rel_root = ""
        dirs[:] = [
            d for d in dirs
            if should_traverse_dir(d, gif, rel_path=f"{rel_root}/{d}".strip("/"), allow_agents=include_agents)
        ]
        for fn in filenames:
            rel_file = f"{rel_root}/{fn}".strip("/")
            if extensions is not None and not any(fn.endswith(ext) for ext in extensions):
                continue
            if not gif.is_ignored(rel_file, is_dir=False):
                collected.append(rel_file)

    return sorted(collected)


def normalize_path(path: Union[str, Path]) -> str:
    """Return path with forward slashes for cross-platform deterministic comparison."""
    return str(path).replace('\\', '/')


def get_workspace_dir() -> Path:
    """Locate the workspace root directory by walking up from cwd or this file."""
    for start in (Path(os.getcwd()).resolve(), Path(__file__).resolve().parent):
        cur = start
        while ".agents" in cur.parts or ".orion" in cur.parts:
            cur = cur.parent

        while True:
            if (cur / ".agents").exists() or (cur / ".orion").exists():
                return cur
            parent = cur.parent
            if parent == cur:
                break
            cur = parent

    return Path(os.getcwd()).resolve()


def get_agents_dir() -> Path:
    """Return canonical path to .agents directory."""
    return get_workspace_dir() / ".agents"


def get_orion_dir() -> Path:
    """Return canonical path to .orion directory."""
    return get_workspace_dir() / ".orion"


def get_persistence_db_path(workspace_root: Union[str, Path, None] = None) -> Path:
    """Return canonical SQLite persistence path for shared runtime state."""
    root = Path(workspace_root).expanduser().resolve() if workspace_root else get_workspace_dir()
    return root / ".orion" / "orion.db"


def get_context_dir() -> Path:
    """Return canonical path to context directory."""
    return get_workspace_dir() / "context"


def get_scratch_dir() -> Path:
    """Return canonical path to scratch directory."""
    return get_workspace_dir() / "scratch"


def atomic_write_text(filepath: Union[str, Path], content: str) -> None:
    """Thread-safe and process-safe atomic file writer with guaranteed temp cleanup."""
    import uuid
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
