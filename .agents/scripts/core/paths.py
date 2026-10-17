"""
Kernel Paths
Provides canonical path discovery and normalization across the workspace, .agents, .orion, context, and scratch.
"""

import os
from pathlib import Path
from typing import Union


def normalize_path(path: Union[str, Path]) -> str:
    """Return path with forward slashes for cross-platform deterministic comparison."""
    return str(path).replace('\\', '/')


def get_workspace_dir() -> Path:
    """Locate the workspace root directory by walking up from cwd or this file."""
    for start in (Path(os.getcwd()).resolve(), Path(__file__).resolve().parent):
        cur = start
        while cur.name in (".agents", ".orion", "scripts", "core", "kernel", "commands", "hooks"):
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
