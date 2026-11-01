"""
ORION CONSTELLATION MODULE (commands/constellation.py)
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

    print("\n🌌 ORION CONSTELLATION — MULTI-PROJECT KNOWLEDGE MESH")
    print("=" * 82)
    print(f"Hub Location : {ws}")
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


def cmd_export(out_dir: Optional[str] = None, search_root: Optional[str] = None) -> int:
    """Exports the Constellation multi-project Obsidian Vault."""
    spokes = discover_spokes(search_root=search_root)
    ws = get_workspace_dir()
    target_out = out_dir or os.path.join(str(ws), "constellation")

    print(f"\n🌌 Exporting Orion Constellation Vault to: {os.path.abspath(target_out)}")
    exporter = ConstellationVaultExporter(output_dir=target_out)
    res = exporter.export_constellation(spokes)

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
        print(f"  - Vault Path  : {res['vault_dir']}")
        return 0
    else:
        print(f"[ERROR] Failed to export Constellation Vault.")
        return 1


def cmd_sync(search_root: Optional[str] = None) -> int:
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
    cmd_export(search_root=search_root)
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

    p_sync = subparsers.add_parser("sync", help="Synchronize cross-project graph and refresh vault")
    p_sync.add_argument("--search-root", default=None, help="Custom search directory for sibling projects")

    parsed = parser.parse_args(args)

    if parsed.subcommand == "status":
        return cmd_status(search_root=parsed.search_root)
    elif parsed.subcommand == "export":
        return cmd_export(out_dir=parsed.out, search_root=parsed.search_root)
    elif parsed.subcommand == "sync":
        return cmd_sync(search_root=parsed.search_root)
    else:
        # Default action: status
        return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
