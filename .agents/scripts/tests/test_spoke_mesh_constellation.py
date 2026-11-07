"""
Unit Tests for Orion Constellation Spoke Mesh and Multi-Project Discovery.
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.spoke_mesh import (
    SpokeStar,
    discover_spokes,
    load_constellation_cache,
    save_constellation_cache,
    is_star_dirty,
    inspect_spoke_dir,
    load_constellation_registry,
    save_constellation_registry,
)
from commands.galaxy import cmd_add, cmd_remove
from core.memory import ConstellationVaultExporter


class TestSpokeMeshConstellation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_spoke_star_serialization(self):
        star = SpokeStar(
            name="test-star",
            root_path="/fake/path",
            stack="Flutter / Dart",
            archetype="Mobile Application",
            dna_state="LIVING",
            dna_score=95,
            context_dir="/fake/path/context",
            context_files={"VISION.md": "/fake/path/context/VISION.md"},
            latest_mtime=1234567.89,
        )
        d = star.to_dict()
        self.assertEqual(d["name"], "test-star")
        self.assertEqual(d["dna_score"], 95)
        self.assertIn("VISION.md", d["context_files"])

        rebuilt = SpokeStar.from_dict(d)
        self.assertEqual(rebuilt.name, "test-star")
        self.assertEqual(rebuilt.dna_score, 95)
        self.assertEqual(rebuilt.latest_mtime, 1234567.89)

    def test_discover_spokes_synthetic_workspace(self):
        parent_dir = self.workspace_root
        hub_dir = parent_dir / "_foundation"
        hub_dir.mkdir()
        (hub_dir / ".agents").mkdir()

        # Star 1: Flutter Project
        star1 = parent_dir / "echont"
        star1.mkdir()
        (star1 / "pubspec.yaml").write_text("name: echont\n", encoding="utf-8")
        (star1 / "context").mkdir()
        (star1 / "context" / "VISION.md").write_text("# Vision\n", encoding="utf-8")
        (star1 / ".agents").mkdir()
        (star1 / ".agents" / ".dna.json").write_text(
            json.dumps({"dna_state": "LIVING", "dna_compliance_score": 96}), encoding="utf-8"
        )

        # Star 2: Node MCP Project
        star2 = parent_dir / "flutterin"
        star2.mkdir()
        (star2 / "package.json").write_text(
            json.dumps({"name": "flutterin", "dependencies": {"@modelcontextprotocol/sdk": "^1.0.0"}}),
            encoding="utf-8",
        )

        # Non-project directory (ignored)
        ignored_dir = parent_dir / "random_notes"
        ignored_dir.mkdir()

        # Discover
        discovered = discover_spokes(search_root=str(parent_dir), current_project_dir=str(hub_dir))
        names = [s.name for s in discovered]

        self.assertIn("echont", names)
        self.assertIn("flutterin", names)
        self.assertNotIn("_foundation", names)
        self.assertNotIn("random_notes", names)

        echont_star = next(s for s in discovered if s.name == "echont")
        self.assertEqual(echont_star.dna_score, 96)
        self.assertEqual(echont_star.dna_state, "LIVING")
        self.assertIn("Flutter", echont_star.stack)
        self.assertIn("VISION.md", echont_star.context_files)

        flutterin_star = next(s for s in discovered if s.name == "flutterin")
        self.assertIn("MCP", flutterin_star.stack)

    def test_cache_and_dirty_checking(self):
        cache = {"stars": {"echont": {"latest_mtime": 100.0}}, "last_full_sync": 100.0}

        star_clean = SpokeStar("echont", "/path", latest_mtime=90.0)
        self.assertFalse(is_star_dirty(star_clean, cache))

        star_dirty = SpokeStar("echont", "/path", latest_mtime=150.0)
        self.assertTrue(is_star_dirty(star_dirty, cache))

        star_new = SpokeStar("brand_new", "/path", latest_mtime=50.0)
        self.assertTrue(is_star_dirty(star_new, cache))

        # Save and load cache
        save_constellation_cache(cache, workspace_root=str(self.workspace_root))
        loaded = load_constellation_cache(workspace_root=str(self.workspace_root))
        self.assertEqual(loaded["stars"]["echont"]["latest_mtime"], 100.0)

    def test_constellation_vault_export(self):
        # Setup sample stars
        star1_ctx = self.workspace_root / "echont_vision.md"
        star1_ctx.write_text("# Echont North Star\n", encoding="utf-8")

        star2_ctx = self.workspace_root / "flutterin_arch.md"
        star2_ctx.write_text("# Flutterin Architecture\n", encoding="utf-8")

        stars = [
            SpokeStar(
                name="echont",
                root_path=str(self.workspace_root / "echont"),
                stack="Flutter / Dart",
                dna_state="LIVING",
                dna_score=100,
                context_files={"VISION.md": str(star1_ctx)},
            ),
            SpokeStar(
                name="flutterin",
                root_path=str(self.workspace_root / "flutterin"),
                stack="Node / TypeScript",
                dna_state="ADAPTED",
                dna_score=95,
                context_files={"03_Tech/ARCHITECTURE.md": str(star2_ctx)},
            ),
        ]

        vault_out = self.workspace_root / "test_constellation_vault"
        exporter = ConstellationVaultExporter(output_dir=str(vault_out))
        res = exporter.export_constellation(stars)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["total_stars"], 2)
        self.assertTrue((vault_out / "index.md").is_file())
        self.assertTrue((vault_out / "00_Hub" / "Overview.md").is_file())
        self.assertTrue((vault_out / "Stars" / "echont" / "Overview.md").is_file())
        self.assertTrue((vault_out / "Stars" / "echont" / "VISION.md").is_file())
        self.assertTrue((vault_out / "Stars" / "flutterin" / "ARCHITECTURE.md").is_file())
        self.assertTrue((vault_out / "Taxonomies" / "Flutter.md").is_file())
        self.assertTrue((vault_out / "Taxonomies" / "Node.md").is_file())
        self.assertTrue((vault_out / ".constellation_manifest.json").is_file())

        # Check content of 00_Hub/Overview.md
        hub_text = (vault_out / "00_Hub" / "Overview.md").read_text(encoding="utf-8")
        self.assertIn("[[Stars/echont/Overview|echont]]", hub_text)
        self.assertIn("[[Stars/flutterin/Overview|flutterin]]", hub_text)
        self.assertIn("100/100", hub_text)

    def test_constellation_vault_export_with_integrated_graph(self):
        star1_ctx = self.workspace_root / "echont_vision.md"
        star1_ctx.write_text("# Echont North Star\n", encoding="utf-8")

        stars = [
            SpokeStar(
                name="echont",
                root_path=str(self.workspace_root / "echont"),
                stack="Flutter / Dart",
                dna_state="LIVING",
                dna_score=100,
                context_files={"VISION.md": str(star1_ctx)},
            )
        ]

        db_path = self.workspace_root / "test_orion.db"
        conn = sqlite3.connect(str(db_path))
        conn.executescript("""
            CREATE TABLE nodes (
                id TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                source_path TEXT
            );
            CREATE TABLE edges (
                source_id TEXT,
                target_id TEXT,
                relation TEXT,
                confidence REAL DEFAULT 1.0
            );
            INSERT INTO nodes VALUES ('n1', 'Concept', 'Architecture Invariant', 'context/03_Tech/ARCHITECTURE.md');
            INSERT INTO nodes VALUES ('n2', 'Concept', 'echont', 'context/VISION.md');
            INSERT INTO edges VALUES ('n1', 'n2', 'REFERENCES', 1.0);
        """)
        conn.commit()
        conn.close()

        vault_out = self.workspace_root / "test_vault_integrated"
        exporter = ConstellationVaultExporter(output_dir=str(vault_out), db_path=str(db_path))
        res = exporter.export_constellation(stars, include_graph=True)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(res.get("graph_exported"))
        self.assertGreater(res.get("graph_notes", 0), 0)

        # Check integrated subfolder
        graph_dir = vault_out / "01_Knowledge_Graph"
        self.assertTrue(graph_dir.is_dir())
        self.assertTrue((graph_dir / "index.md").is_file())
        self.assertTrue((graph_dir / "GRAPH_REPORT.md").is_file())
        self.assertTrue((graph_dir / "nodes").is_dir())

        # Check cross-links
        hub_text = (vault_out / "00_Hub" / "Overview.md").read_text(encoding="utf-8")
        self.assertIn("[[01_Knowledge_Graph/index|Explore Graph Entities]]", hub_text)
        self.assertIn("[[01_Knowledge_Graph/GRAPH_REPORT|View Centrality Report]]", hub_text)

        star_text = (vault_out / "Stars" / "echont" / "Overview.md").read_text(encoding="utf-8")
        self.assertIn("[[01_Knowledge_Graph/nodes/echont|echont in Brain Mesh]]", star_text)

        index_text = (vault_out / "index.md").read_text(encoding="utf-8")
        self.assertIn("[[01_Knowledge_Graph/index", index_text)

    def test_constellation_registry_persistence(self):
        reg_data = {
            "search_roots": ["/custom/root1", "/custom/root2"],
            "spokes": ["/custom/spoke/project_a"],
        }
        save_constellation_registry(reg_data, workspace_root=str(self.workspace_root))
        loaded = load_constellation_registry(workspace_root=str(self.workspace_root))

        self.assertEqual(loaded["search_roots"], ["/custom/root1", "/custom/root2"])
        self.assertEqual(loaded["spokes"], ["/custom/spoke/project_a"])

    def test_arbitrary_spoke_discovery_and_registry(self):
        # Sibling hierarchy
        sibling_root = self.workspace_root / "siblings"
        sibling_root.mkdir()
        hub_dir = sibling_root / "_foundation"
        hub_dir.mkdir()
        (hub_dir / ".agents").mkdir()

        # Normal sibling star
        sibling_star = sibling_root / "app_sibling"
        sibling_star.mkdir()
        (sibling_star / "package.json").write_text('{"name": "app_sibling"}', encoding="utf-8")

        # Distant directory outside sibling hierarchy
        external_root = self.workspace_root / "other_drive" / "repos"
        external_root.mkdir(parents=True)
        external_star1 = external_root / "ext_service"
        external_star1.mkdir()
        (external_star1 / "pyproject.toml").write_text('[project]\nname = "ext_service"', encoding="utf-8")

        # Explicit individual spoke in another arbitrary location
        special_spoke = self.workspace_root / "special_agents" / "deep_agent"
        special_spoke.mkdir(parents=True)
        (special_spoke / "AGENTS.md").write_text("# Deep Agent\n", encoding="utf-8")

        # Register external root and explicit spoke
        reg = {
            "search_roots": [str(external_root)],
            "spokes": [str(special_spoke)],
        }
        save_constellation_registry(reg, workspace_root=str(hub_dir))

        discovered = discover_spokes(current_project_dir=str(hub_dir), include_well_known=False)
        names = [s.name for s in discovered]

        self.assertIn("app_sibling", names)
        self.assertIn("ext_service", names)
        self.assertIn("deep_agent", names)
        self.assertNotIn("_foundation", names)

    def test_inspect_spoke_dir_qualifications(self):
        test_dir = self.workspace_root / "test_qual"
        test_dir.mkdir()
        self.assertIsNone(inspect_spoke_dir(str(test_dir)))

        (test_dir / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
        star = inspect_spoke_dir(str(test_dir))
        self.assertIsNotNone(star)
        self.assertEqual(star.name, "test_qual")


if __name__ == "__main__":
    unittest.main()
