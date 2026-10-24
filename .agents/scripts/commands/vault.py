"""
ORION VAULT MODULE (commands/vault.py)
Encapsulates Obsidian Vault Export, Second Brain brief generation,
and vault mirror maintenance for the Orion knowledge graph.
"""

import argparse
import os
import sys
from typing import Any, Dict, Optional

# Base directory anchoring
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.paths import get_orion_dir, get_workspace_dir, get_persistence_db_path
from core.memory import ObsidianVaultExporter, SecondBrainManager

try:
    from core.db import log_telemetry as _kernel_log_telemetry
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


def export_vault(out_dir: Optional[str] = None, db_path: Optional[str] = None) -> int:
    """Exports the entire Orion knowledge graph into an Obsidian vault."""
    try:
        db = db_path or str(get_persistence_db_path())
        exporter = ObsidianVaultExporter(db_path=db)
        result = exporter.export_vault(out_dir)
        if result.get("status") != "SUCCESS":
            print(f"[ERROR] Obsidian vault export failed: {result.get('message', 'unknown error')}")
            return 1

        print(f"[SUCCESS] Obsidian vault exported to {result['vault_dir']}")
        print(
            f"[STATUS] notes={result['total_notes']} "
            f"nodes={result['nodes_exported']} "
            f"communities={result['communities_exported']}"
        )
        return 0
    except Exception as e:
        _log_telemetry(e, "vault.py:export_vault")
        print(f"[ERROR] Failed to export vault: {e}")
        return 1


def build_second_brain(out_dir: Optional[str] = None) -> Dict[str, str]:
    """Generates the 4-note Second Brain briefing structure."""
    try:
        sb = SecondBrainManager(out_dir)
        notes = sb.build_second_brain()
        print(f"\n🧠 Second Brain Protocol Generated (4 High-Density Briefing Notes):")
        for k, v in notes.items():
            print(f"  - [{k.upper()}]: {v}")
        return notes
    except Exception as e:
        _log_telemetry(e, "vault.py:build_second_brain")
        return {}


import shutil


def clean_vault_mirrors(orion_dir: Optional[str] = None) -> int:
    """Prunes stale vault mirrors and temporary export artifacts."""
    target_orion = orion_dir or str(get_orion_dir())
    stale_dirs = [
        os.path.join(target_orion, "vault", "nodes"),
        os.path.join(target_orion, "vault", "communities"),
        os.path.join(target_orion, "export", "vault", "nodes"),
        os.path.join(target_orion, "export", "vault", "communities"),
        os.path.join(target_orion, "export", "vault"),
    ]
    cleaned = 0
    for d in stale_dirs:
        if os.path.isdir(d):
            try:
                for root, dirs, files in os.walk(d, topdown=False):
                    for f in files:
                        try:
                            os.remove(os.path.join(root, f))
                            cleaned += 1
                        except OSError:
                            pass
                    for sub_d in dirs:
                        try:
                            os.rmdir(os.path.join(root, sub_d))
                        except OSError:
                            pass
                try:
                    os.rmdir(d)
                except OSError:
                    pass
            except OSError as e:
                _log_telemetry(e, "vault.py:clean_vault_mirrors")
    return cleaned


def vault_main(argv=None) -> int:
    """CLI Entrypoint for vault commands."""
    parser = argparse.ArgumentParser(
        prog="orion.py vault",
        description="Obsidian Vault and Second Brain Manager for Orion",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Vault subcommands")

    export_p = subparsers.add_parser("export", help="Export Orion graph to Obsidian vault")
    export_p.add_argument("--out", default=None, help="Target directory (default: .orion/vault)")

    brain_p = subparsers.add_parser("second-brain", help="Generate 4-note Second Brain briefing")
    brain_p.add_argument("--out", default=None, help="Target directory (default: .orion/working/brain)")

    clean_p = subparsers.add_parser("clean", help="Clean stale vault export caches")

    args = parser.parse_args(argv)
    if not args.subcommand or args.subcommand == "export":
        out = getattr(args, "out", None)
        return export_vault(out)
    elif args.subcommand == "second-brain":
        build_second_brain(args.out)
        return 0
    elif args.subcommand == "clean":
        n = clean_vault_mirrors()
        print(f"Cleaned {n} vault cache items.")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(vault_main(sys.argv[1:]))
