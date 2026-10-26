import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.reflexion import ObservationLedger


class TestObservationStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.active_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.md")
        self.archive_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.archive.md")
        self.ledger = ObservationLedger(active_path=self.active_path, archive_path=self.archive_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_add_and_parse_observations(self):
        item = self.ledger.add_observation(
            title="Fix controller classification in dna.py",
            kind="improve",
            target="core/dna.py",
            rule_id="LAYER_BOUNDARIES",
            scope="foundation",
            evidence="12 violations in feature-first presentation/controllers/",
            status="open"
        )
        self.assertEqual(item["id"], 1)
        self.assertEqual(item["title"], "Fix controller classification in dna.py")
        self.assertEqual(item["kind"], "improve")
        self.assertEqual(item["target"], "core/dna.py")
        self.assertEqual(item["rule_id"], "LAYER_BOUNDARIES")
        self.assertEqual(item["scope"], "foundation")

        all_obs = self.ledger.get_all_observations()
        self.assertEqual(len(all_obs), 1)
        self.assertEqual(all_obs[0]["id"], 1)
        self.assertEqual(all_obs[0]["title"], "Fix controller classification in dna.py")

    def test_restatement_check_extends_evidence(self):
        item1 = self.ledger.add_observation(
            title="Unnecessary double write",
            kind="violation",
            target="app_blacklist_screen.dart",
            evidence="First trace"
        )
        item2 = self.ledger.add_observation(
            title="Unnecessary double write",
            kind="violation",
            target="app_blacklist_screen.dart",
            evidence="Second trace"
        )
        self.assertEqual(item1["id"], item2["id"])
        all_obs = self.ledger.get_all_observations()
        self.assertEqual(len(all_obs), 1)
        self.assertIn("First trace", all_obs[0]["evidence"])
        self.assertIn("Second trace", all_obs[0]["evidence"])

    def test_get_digest_and_broken_probe_guard(self):
        self.ledger.add_observation(
            title="Test item 1",
            kind="improve",
            target="target1.py"
        )
        self.ledger.add_observation(
            title="Test item 2",
            kind="improve",
            target="target2.py",
            status="parked",
            parked_until="2026-12-31"
        )
        digest = self.ledger.get_digest()
        self.assertIn("open=1", digest)
        self.assertIn("parked=1", digest)
        self.assertIn("top-target=target1.py", digest)

        # Force broken probe scenario (header present but unparseable id/title)
        with open(self.active_path, "w", encoding="utf-8") as f:
            f.write("## Observation #notanumber: Broken entry\n\nSome invalid data\n")

        broken_digest = self.ledger.get_digest()
        self.assertEqual(broken_digest, "OBSERVATION SCAN BROKEN")

    def test_resolve_and_archive_observation(self):
        item = self.ledger.add_observation(
            title="Item to be resolved",
            kind="simplify",
            target="commands/foundation.py"
        )
        obs_id = item["id"]
        ok = self.ledger.resolve_observation(obs_id, resolution="Merged upstream", status="actioned")
        self.assertTrue(ok)

        active = self.ledger.get_all_observations()
        self.assertEqual(len(active), 0)

        arch = self.ledger.get_archive_observations()
        self.assertEqual(len(arch), 1)
        self.assertEqual(arch[0]["id"], obs_id)
        self.assertEqual(arch[0]["status"], "actioned")
        self.assertEqual(arch[0]["resolution"], "Merged upstream")

    def test_parked_requires_valid_parked_until(self):
        with self.assertRaises(ValueError):
            self.ledger.add_observation(
                title="Invalid parked entry",
                status="parked"
            )

    def test_curator_propose_siblings(self):
        from core.harness.curator import ClusterCurator
        skills_tmp = tempfile.TemporaryDirectory()
        try:
            os.makedirs(os.path.join(skills_tmp.name, "dart-analyze"))
            with open(os.path.join(skills_tmp.name, "dart-analyze", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: dart-analyze\ndescription: Run static analysis for dart.\n---\n")

            os.makedirs(os.path.join(skills_tmp.name, "dart-fix"))
            with open(os.path.join(skills_tmp.name, "dart-fix", "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("---\nname: dart-fix\ndescription: Automatically fix mechanical lint issues in dart.\n---\n")

            curator = ClusterCurator(skills_tmp.name)
            siblings = curator.propose_siblings("dart-format")
            self.assertIn("dart-analyze", siblings)
            self.assertIn("dart-fix", siblings)
        finally:
            skills_tmp.cleanup()

    def test_upstream_cross_project_observation_sync(self):
        from commands.foundation import sync_upstream_observations
        spoke_tmp = tempfile.TemporaryDirectory()
        hub_tmp = tempfile.TemporaryDirectory()
        try:
            spoke_root = spoke_tmp.name
            spoke_agents = os.path.join(spoke_root, ".agents")
            hub_agents = os.path.join(hub_tmp.name, ".agents")
            os.makedirs(spoke_agents, exist_ok=True)
            os.makedirs(hub_agents, exist_ok=True)

            with open(os.path.join(spoke_agents, ".dna.json"), "w", encoding="utf-8") as f:
                f.write('{"primary_framework": "flutter", "archetype": "Flutter/Dart"}')

            spoke_obs_path = os.path.join(spoke_agents, "OBSERVATIONS.md")
            spoke_ledger = ObservationLedger(active_path=spoke_obs_path, archive_path=os.path.join(spoke_agents, "OBSERVATIONS.archive.md"))
            spoke_ledger.add_observation(
                title="Universal rule on memory leaks",
                kind="improve",
                target="core/dna.py",
                scope="foundation",
                count=1
            )
            spoke_ledger.add_observation(
                title="Local project widget detail",
                kind="improve",
                target="lib/screen.dart",
                scope="project",
                count=1
            )

            created, updated = sync_upstream_observations(spoke_root, spoke_agents, hub_agents, dry_run=False)
            self.assertEqual(created, 1)
            self.assertEqual(updated, 0)

            hub_ledger = ObservationLedger(active_path=os.path.join(hub_agents, "OBSERVATIONS.md"), archive_path=os.path.join(hub_agents, "OBSERVATIONS.archive.md"))
            hub_items = hub_ledger.get_all_observations()
            self.assertEqual(len(hub_items), 1)
            self.assertEqual(hub_items[0]["title"], "Universal rule on memory leaks")
            self.assertEqual(hub_items[0]["applies_to"], "flutter")
            self.assertTrue(hub_items[0]["seen_in"].startswith("p_"))

            spoke2_tmp = tempfile.TemporaryDirectory()
            spoke2_root = spoke2_tmp.name
            spoke2_agents = os.path.join(spoke2_root, ".agents")
            os.makedirs(spoke2_agents, exist_ok=True)
            with open(os.path.join(spoke2_agents, ".dna.json"), "w", encoding="utf-8") as f:
                f.write('{"primary_framework": "node", "archetype": "Node/TS"}')
            spoke2_ledger = ObservationLedger(active_path=os.path.join(spoke2_agents, "OBSERVATIONS.md"), archive_path=os.path.join(spoke2_agents, "OBSERVATIONS.archive.md"))
            spoke2_ledger.add_observation(
                title="Universal rule on memory leaks",
                kind="improve",
                target="core/dna.py",
                scope="foundation",
                count=2
            )

            created2, updated2 = sync_upstream_observations(spoke2_root, spoke2_agents, hub_agents, dry_run=False)
            self.assertEqual(created2, 0)
            self.assertEqual(updated2, 1)

            hub_items_after = hub_ledger.get_all_observations()
            self.assertEqual(len(hub_items_after), 1)
            self.assertEqual(hub_items_after[0]["count"], 3)
            self.assertIn(",", hub_items_after[0]["seen_in"])
            self.assertIn("flutter", hub_items_after[0]["applies_to"])
            self.assertIn("node", hub_items_after[0]["applies_to"])
            self.assertTrue(hub_items_after[0]["title"].startswith("[CROSS-PROJECT CANDIDATE]"))
            spoke2_tmp.cleanup()
        finally:
            spoke_tmp.cleanup()
            hub_tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
