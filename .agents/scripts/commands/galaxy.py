"""
ORION CONSTELLATION MODULE (commands/galaxy.py)
Encapsulates Multi-Project Spoke Discovery, Knowledge Mesh Synchronization,
and Foundation-Level Obsidian Vault Export for Orion.
Pure Python standard library implementation.
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Base directory anchoring
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

try:
    from core.db import configure_utf8
    configure_utf8()
except ImportError:
    pass

from core.paths import get_workspace_dir
from core.spoke_mesh import (
    discover_spokes,
    load_constellation_cache,
    save_constellation_cache,
    is_star_dirty,
    SpokeStar,
    inspect_spoke_dir,
    load_constellation_registry,
    save_constellation_registry,
)
from core.memory import ConstellationVaultExporter

try:
    from core.db import log_telemetry as _kernel_log_telemetry
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


def cmd_status(search_root: Optional[str] = None) -> int:
    """Displays the Constellation status table of all discovered stars."""
    spokes = discover_spokes(search_root=search_root)
    ws = get_workspace_dir()
    cache = load_constellation_cache(str(ws))
    reg = load_constellation_registry(str(ws))

    print("\n🌌 ORION CONSTELLATION — MULTI-PROJECT KNOWLEDGE MESH")
    print("=" * 82)
    print(f"Hub Location : {ws}")
    if reg.get("search_roots"):
        print(f"Custom Roots : {', '.join(reg['search_roots'])}")
    if reg.get("spokes"):
        print(f"Custom Spokes: {', '.join(reg['spokes'])}")
    print(f"Total Stars  : {len(spokes)} discovered project(s)")
    print("-" * 82)

    if not spokes:
        print("[INFO] No sibling projects discovered.")
        return 0

    print(f"{'STAR':<16} {'STACK':<26} {'DNA SCORE':<12} {'CONTEXT':<12} {'SYNC STATUS'}")
    print("-" * 82)

    for star in spokes:
        dirty = is_star_dirty(star, cache)
        sync_str = "[MODIFIED]" if dirty else "[SYNCED]"
        score_str = f"{star.dna_score}/100" if star.dna_score > 0 else "N/A"
        ctx_cnt = f"{len(star.context_files)} file(s)"
        stk = star.stack[:24] + ".." if len(star.stack) > 26 else star.stack
        print(f"{star.name:<16} {stk:<26} {score_str:<12} {ctx_cnt:<12} {sync_str}")

    print("=" * 82)
    return 0


def cmd_add(path_str: str, as_root: bool = False) -> int:
    """Registers an arbitrary directory as a constellation search root or explicit spoke."""
    abs_path = os.path.abspath(os.path.expanduser(path_str))
    if not os.path.isdir(abs_path):
        print(f"[ERROR] Directory not found: {abs_path}")
        return 1

    ws = get_workspace_dir()
    reg = load_constellation_registry(str(ws))

    if as_root:
        if abs_path in reg.get("search_roots", []):
            print(f"[INFO] Search root already registered: {abs_path}")
            return 0
        reg.setdefault("search_roots", []).append(abs_path)
        save_constellation_registry(reg, str(ws))
        print(f"[SUCCESS] Registered search root: {abs_path}")
    else:
        star = inspect_spoke_dir(abs_path)
        if not star:
            print(f"[WARNING] Directory does not currently match standard project indicators (.agents, context, manifest, or AGENTS.md): {abs_path}")
            print(f"[INFO] Adding anyway as explicit spoke.")
        if abs_path in reg.get("spokes", []):
            print(f"[INFO] Spoke already registered: {abs_path}")
            return 0
        reg.setdefault("spokes", []).append(abs_path)
        save_constellation_registry(reg, str(ws))
        star_name = star.name if star else os.path.basename(abs_path)
        print(f"[SUCCESS] Registered spoke: {star_name} ({abs_path})")

    return 0


def cmd_remove(path_str: str) -> int:
    """Removes a path from constellation search roots or explicit spokes."""
    abs_path = os.path.abspath(os.path.expanduser(path_str))
    ws = get_workspace_dir()
    reg = load_constellation_registry(str(ws))

    removed_root = False
    removed_spoke = False

    roots = reg.get("search_roots", [])
    if abs_path in roots:
        roots.remove(abs_path)
        removed_root = True

    spokes = reg.get("spokes", [])
    target_spokes = [s for s in spokes if os.path.abspath(s) == abs_path or os.path.basename(s).lower() == path_str.lower()]
    for s in target_spokes:
        spokes.remove(s)
        removed_spoke = True

    if removed_root or removed_spoke:
        save_constellation_registry(reg, str(ws))
        msg = []
        if removed_root:
            msg.append(f"search root ({abs_path})")
        if removed_spoke:
            msg.append(f"spoke ({path_str})")
        print(f"[SUCCESS] Removed from registry: {', '.join(msg)}")
        return 0
    else:
        print(f"[WARNING] Not found in constellation registry: {path_str}")
        return 1


def cmd_export(out_dir: Optional[str] = None, search_root: Optional[str] = None, include_graph: bool = True) -> int:
    """Exports the Constellation multi-project Obsidian Vault."""
    spokes = discover_spokes(search_root=search_root)
    ws = get_workspace_dir()
    target_out = out_dir or os.path.join(str(ws), "constellation")

    print(f"\n🌌 Exporting Orion Constellation Vault to: {os.path.abspath(target_out)}")
    exporter = ConstellationVaultExporter(output_dir=target_out)
    res = exporter.export_constellation(spokes, include_graph=include_graph)

    if res.get("status") == "SUCCESS":
        # Update cache
        cache = load_constellation_cache(str(ws))
        for star in spokes:
            cache.setdefault("stars", {})[star.name] = {
                "latest_mtime": star.latest_mtime,
                "synced_at": time.time(),
            }
        cache["last_full_sync"] = time.time()
        save_constellation_cache(cache, str(ws))

        print(f"[SUCCESS] Orion Constellation Vault exported successfully.")
        print(f"  - Total Stars : {res['total_stars']}")
        print(f"  - Total Notes : {res['total_notes']}")
        if res.get("graph_exported"):
            print(f"  - Graph Notes : {res.get('graph_notes', 0)} (in 01_Knowledge_Graph/)")
        print(f"  - Vault Path  : {res['vault_dir']}")
        return 0
    else:
        print(f"[ERROR] Failed to export Constellation Vault.")
        return 1


def cmd_sync(search_root: Optional[str] = None, include_graph: bool = True) -> int:
    """Syncs all star context notes and ingests cross-project graph triplets into orion.db."""
    spokes = discover_spokes(search_root=search_root)
    ws = get_workspace_dir()
    cache = load_constellation_cache(str(ws))

    print(f"\n🌌 Synchronizing Orion Constellation Knowledge Mesh...")
    dirty_stars = [s for s in spokes if is_star_dirty(s, cache)]
    print(f"Discovered {len(spokes)} star(s) ({len(dirty_stars)} modified or new).")

    # Ingest graph triplets into orion.db
    triplets = []
    for s in spokes:
        triplets.append({
            "subject": s.name,
            "predicate": "inherits_from",
            "object": "_foundation",
            "source_path": s.root_path,
            "description": f"Star project inheriting Foundation standards (Stack: {s.stack}, DNA: {s.dna_score}/100)"
        })
        primary_tech = s.stack.split("/")[0].strip() if "/" in s.stack else s.stack
        if primary_tech and primary_tech != "Generic":
            triplets.append({
                "subject": s.name,
                "predicate": "implements_tech",
                "object": primary_tech,
                "source_path": s.root_path,
                "description": f"{s.name} utilizes {primary_tech}"
            })

    try:
        from commands.brain import inject_triplets
        inject_triplets(json.dumps(triplets), exit_on_error=False)
        print(f"[SUCCESS] Ingested {len(triplets)} cross-project relations into Orion Graph.")
    except Exception as _ge:
        _log_telemetry(_ge, "constellation:sync_triplets")

    # Also refresh vault export
    cmd_export(search_root=search_root, include_graph=include_graph)
    return 0


def main(args: Optional[List[str]] = None) -> int:
    if args is None:
        args = sys.argv[1:]

    # Strip command name if invoked via orion.py
    if args and args[0].lower() == "constellation":
        args = args[1:]

    parser = argparse.ArgumentParser(description="Orion Constellation Multi-Project Knowledge Mesh & Vault Manager")
    subparsers = parser.add_subparsers(dest="subcommand")

    p_status = subparsers.add_parser("status", help="Display portfolio scorecard of all discovered stars")
    p_status.add_argument("--search-root", default=None, help="Custom search directory for sibling projects")

    p_export = subparsers.add_parser("export", help="Export unified Obsidian vault spanning all stars")
    p_export.add_argument("--out", default=None, help="Target directory for constellation vault")
    p_export.add_argument("--search-root", default=None, help="Custom search directory for sibling projects")
    p_export.add_argument("--no-graph", action="store_true", help="Skip deep SQLite knowledge graph export")

    p_sync = subparsers.add_parser("sync", help="Synchronize cross-project graph and refresh vault")
    p_sync.add_argument("--search-root", default=None, help="Custom search directory for sibling projects")
    p_sync.add_argument("--no-graph", action="store_true", help="Skip deep SQLite knowledge graph export")

    p_add = subparsers.add_parser("add", help="Register an arbitrary directory or search root into Constellation")
    p_add.add_argument("path", help="Directory path to spoke project or search root")
    p_add.add_argument("--root", action="store_true", help="Register as a multi-project search root instead of a single spoke")

    p_remove = subparsers.add_parser("remove", help="Remove a directory or spoke from Constellation registry")
    p_remove.add_argument("path", help="Directory path or spoke name to remove")

    parsed = parser.parse_args(args)

    if parsed.subcommand == "status":
        return cmd_status(search_root=parsed.search_root)
    elif parsed.subcommand == "export":
        return cmd_export(out_dir=parsed.out, search_root=parsed.search_root, include_graph=not getattr(parsed, "no_graph", False))
    elif parsed.subcommand == "sync":
        return cmd_sync(search_root=parsed.search_root, include_graph=not getattr(parsed, "no_graph", False))
    elif parsed.subcommand == "add":
        return cmd_add(path_str=parsed.path, as_root=getattr(parsed, "root", False))
    elif parsed.subcommand == "remove":
        return cmd_remove(path_str=parsed.path)
    else:
        # Default action: status
        return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
