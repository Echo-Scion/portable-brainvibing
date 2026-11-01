"""
Kernel Spoke Mesh
Discovers, harvests, and monitors sibling repositories ("Stars") in the developer workspace
for the Orion Constellation supervisory multi-project knowledge mesh.
Pure Python standard library implementation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Base imports
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.paths import get_workspace_dir, atomic_write_text, DEFAULT_IGNORE_DIRS

try:
    from core.db import log_telemetry as _kernel_log_telemetry
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


CANONICAL_CONTEXT_FILES: Tuple[str, ...] = (
    "VISION.md",
    "README.md",
    "00_Strategy/MEMORY.md",
    "00_Strategy/BLUEPRINT.md",
    "01_Product/ROADMAP.md",
    "02_Creative/STYLE_GUIDE.md",
    "03_Tech/ARCHITECTURE.md",
)


class SpokeStar:
    """Represents a discovered spoke repository ('Star') within the constellation."""

    def __init__(
        self,
        name: str,
        root_path: str,
        stack: str = "Generic",
        archetype: str = "Software Repository",
        dna_state: str = "UNKNOWN",
        dna_score: int = 0,
        context_dir: Optional[str] = None,
        context_files: Optional[Dict[str, str]] = None,
        latest_mtime: float = 0.0,
    ):
        self.name = name
        self.root_path = os.path.abspath(root_path)
        self.stack = stack
        self.archetype = archetype
        self.dna_state = dna_state
        self.dna_score = dna_score
        self.context_dir = context_dir
        self.context_files: Dict[str, str] = context_files or {}
        self.latest_mtime = latest_mtime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root_path": self.root_path,
            "stack": self.stack,
            "archetype": self.archetype,
            "dna_state": self.dna_state,
            "dna_score": self.dna_score,
            "context_dir": self.context_dir,
            "context_files": self.context_files,
            "latest_mtime": self.latest_mtime,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpokeStar":
        return cls(
            name=data.get("name", ""),
            root_path=data.get("root_path", ""),
            stack=data.get("stack", "Generic"),
            archetype=data.get("archetype", "Software Repository"),
            dna_state=data.get("dna_state", "UNKNOWN"),
            dna_score=int(data.get("dna_score", 0)),
            context_dir=data.get("context_dir"),
            context_files=data.get("context_files", {}),
            latest_mtime=float(data.get("latest_mtime", 0.0)),
        )


def _detect_stack(repo_dir: str) -> Tuple[str, str]:
    """Detects programming stack and archetype from repository root indicators."""
    r_path = Path(repo_dir)

    # Check .agents/.project_manifest.json
    manifest_file = r_path / ".agents" / ".project_manifest.json"
    if manifest_file.is_file():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                s = data.get("stack") or data.get("ecosystem")
                arch = data.get("archetype")
                if s:
                    if isinstance(s, dict):
                        fw = s.get("framework") or s.get("ecosystem") or ""
                        lang = s.get("language") or ""
                        stack_str = f"{fw.title()} / {lang.title()}" if fw and lang else (fw.title() or lang.title() or "Generic")
                    else:
                        stack_str = str(s)
                    return stack_str, str(arch or "Software Repository")
        except Exception as _e:
            _log_telemetry(_e, "spoke_mesh:manifest_read")

    # Check indicators
    if (r_path / "pubspec.yaml").is_file():
        return "Flutter / Dart", "Mobile / Cross-Platform App"
    if (r_path / "package.json").is_file():
        try:
            with open(r_path / "package.json", "r", encoding="utf-8") as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "@modelcontextprotocol/sdk" in deps:
                    return "Node / TypeScript (MCP)", "MCP Server / Service"
                if "react" in deps or "next" in deps:
                    return "React / Web", "Frontend Web Application"
                return "Node / TypeScript", "Node.js Application"
        except Exception:
            return "Node / JavaScript", "Node Application"
    if (r_path / "pyproject.toml").is_file() or (r_path / "setup.py").is_file():
        return "Python", "Python Application / Library"
    if (r_path / "Cargo.toml").is_file():
        return "Rust", "Systems / Native Tool"
    if (r_path / "build.gradle").is_file() or (r_path / "build.gradle.kts").is_file():
        return "Android / Kotlin", "Android Application"

    return "Generic", "Software Repository"


def _read_dna_metadata(repo_dir: str) -> Tuple[str, int, str]:
    """Reads DNA compliance score and state from .agents/.dna.json if present."""
    dna_file = Path(repo_dir) / ".agents" / ".dna.json"
    if dna_file.is_file():
        try:
            with open(dna_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                state = data.get("dna_state", "BORN")
                score = int(data.get("dna_compliance_score", 0))
                arch = data.get("archetype", "Software Repository")
                return state, score, arch
        except Exception as _e:
            _log_telemetry(_e, "spoke_mesh:dna_read")
    return "UNKNOWN", 0, "Software Repository"


def _harvest_context(repo_dir: str) -> Tuple[Optional[str], Dict[str, str], float]:
    """Harvests domain context markdown files and determines latest modification time."""
    context_dir = os.path.join(repo_dir, "context")
    if not os.path.isdir(context_dir):
        return None, {}, 0.0

    files_map: Dict[str, str] = {}
    latest_mtime = 0.0

    for rel_file in CANONICAL_CONTEXT_FILES:
        full_path = os.path.join(context_dir, rel_file.replace("/", os.sep))
        if os.path.isfile(full_path):
            files_map[rel_file] = os.path.abspath(full_path)
            try:
                mtime = os.path.getmtime(full_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime
            except OSError:
                pass

    return os.path.abspath(context_dir), files_map, latest_mtime


def discover_spokes(
    search_root: Optional[str] = None,
    current_project_dir: Optional[str] = None,
    include_self: bool = False,
) -> List[SpokeStar]:
    """
    Discovers sibling spoke repositories ('Stars') around current_project_dir.
    Searches search_root (defaulting to parent of current project).
    """
    cur_ws = os.path.abspath(str(current_project_dir or get_workspace_dir()))
    root = os.path.abspath(str(search_root or Path(cur_ws).parent))

    spokes: List[SpokeStar] = []

    if not os.path.isdir(root):
        return spokes

    for entry in sorted(os.listdir(root)):
        full_entry_path = os.path.join(root, entry)
        if not os.path.isdir(full_entry_path):
            continue

        # Skip self unless explicitly requested
        if not include_self and os.path.abspath(full_entry_path) == cur_ws:
            continue

        # Ignore hidden and blacklisted directories
        if entry.startswith(".") or entry in DEFAULT_IGNORE_DIRS or entry.lower() in DEFAULT_IGNORE_DIRS:
            continue

        # Check if directory resembles a project
        has_agents = os.path.isdir(os.path.join(full_entry_path, ".agents"))
        has_context = os.path.isdir(os.path.join(full_entry_path, "context"))
        has_manifest = any(
            os.path.isfile(os.path.join(full_entry_path, f))
            for f in ("pubspec.yaml", "package.json", "pyproject.toml", "Cargo.toml", "build.gradle", "build.gradle.kts")
        )

        if not (has_agents or has_context or has_manifest):
            continue

        # Extract project name
        p_name = entry
        manifest_path = os.path.join(full_entry_path, ".agents", ".project_manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    p_name = json.load(mf).get("project_name") or entry
            except Exception:
                pass

        stack, detected_arch = _detect_stack(full_entry_path)
        dna_state, dna_score, dna_arch = _read_dna_metadata(full_entry_path)
        archetype = dna_arch if dna_arch != "Software Repository" else detected_arch
        ctx_dir, ctx_files, latest_mtime = _harvest_context(full_entry_path)

        star = SpokeStar(
            name=p_name,
            root_path=full_entry_path,
            stack=stack,
            archetype=archetype,
            dna_state=dna_state,
            dna_score=dna_score,
            context_dir=ctx_dir,
            context_files=ctx_files,
            latest_mtime=latest_mtime,
        )
        spokes.append(star)

    return sorted(spokes, key=lambda s: s.name.lower())


def get_constellation_cache_path(workspace_root: Optional[str] = None) -> str:
    """Returns the persistent cache path for constellation sync states."""
    root = workspace_root or str(get_workspace_dir())
    cache_dir = os.path.join(root, ".orion", "working")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "constellation_cache.json")


def load_constellation_cache(workspace_root: Optional[str] = None) -> Dict[str, Any]:
    """Loads constellation sync cache from disk."""
    p = get_constellation_cache_path(workspace_root)
    if os.path.isfile(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as _e:
            _log_telemetry(_e, "spoke_mesh:load_cache")
    return {"stars": {}, "last_full_sync": 0.0}


def save_constellation_cache(cache_data: Dict[str, Any], workspace_root: Optional[str] = None) -> None:
    """Saves constellation sync cache atomically to disk."""
    p = get_constellation_cache_path(workspace_root)
    atomic_write_text(p, json.dumps(cache_data, indent=2))


def is_star_dirty(star: SpokeStar, cache_data: Dict[str, Any]) -> bool:
    """Checks whether a spoke star's context has changed since its last recorded sync."""
    stars_cache = cache_data.get("stars", {})
    star_entry = stars_cache.get(star.name)
    if not star_entry:
        return True
    cached_mtime = float(star_entry.get("latest_mtime", 0.0))
    return star.latest_mtime > cached_mtime
