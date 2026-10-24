"""
Tests for Observational Memory Primitives, Anchor IDs, Dynamic Budgets, and Generational Rollover.
"""

import os
import sys
import unittest
import tempfile
import sqlite3

_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.memory import (
    inject_anchor_ids,
    strip_anchor_ids,
    parse_anchor_id,
    calculate_dynamic_memory_budget,
    RecallMemoryManager,
    ArchivalMemoryManager,
)


class TestObservationalMemory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_orion.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_anchor_id_injection_and_stripping(self):
        raw = (
            "## Group `abc`\n"
            "_range: `1:10`_\n"
            "First observation item\n"
            "  Sub-detail under first\n"
            "Second observation item\n"
        )
        anchored = inject_anchor_ids(raw)
        self.assertIn("[O1] First observation item", anchored)
        self.assertIn("[O1-N1] Sub-detail under first", anchored)
        self.assertIn("[O2] Second observation item", anchored)
        self.assertNotIn("[O", "## Group `abc`")

        stripped = strip_anchor_ids(anchored)
        self.assertEqual(stripped.strip(), raw.strip())

    def test_dynamic_memory_budget_and_retention_floor(self):
        budget_small = calculate_dynamic_memory_budget(
            observation_tokens=500,
            max_message_budget=12000,
            max_observation_budget=4000,
            retention_floor=2000,
        )
        self.assertFalse(budget_small["needs_rollover"])
        self.assertEqual(budget_small["effective_message_budget"], 15500)

        budget_large = calculate_dynamic_memory_budget(
            observation_tokens=4500,
            max_message_budget=12000,
            max_observation_budget=4000,
            retention_floor=2000,
        )
        self.assertTrue(budget_large["needs_rollover"])
        self.assertGreaterEqual(budget_large["effective_message_budget"], 2000)

    def test_generational_rollover_and_superseded_filtering(self):
        with RecallMemoryManager(db_path=self.db_path) as recall:
            for i in range(10):
                recall.record_turn("user", f"Turn message {i}")

            active_turns_before = recall.get_recent_turns(limit=20)
            self.assertEqual(len(active_turns_before), 10)

            # Create reflection generation keeping retention floor = 4
            gen_res = recall.create_reflection_generation(
                reflection_text="Head Reflection: user discussed 10 turns.",
                anchor_map={"O1": "Turn message 0", "O2": "Turn message 5"},
                retention_floor_turns=4,
            )
            self.assertEqual(gen_res["generation_count"], 1)

            # Active turns should only return the 4 retention floor turns
            active_turns_after = recall.get_recent_turns(limit=20, include_superseded=False)
            self.assertEqual(len(active_turns_after), 4)

            # All turns still accessible when requested
            all_turns = recall.get_recent_turns(limit=20, include_superseded=True)
            self.assertEqual(len(all_turns), 10)

            # Head generation retrieval
            head_gen = recall.get_head_generation()
            self.assertIsNotNone(head_gen)
            self.assertEqual(head_gen["generation_count"], 1)
            self.assertIn("Head Reflection", head_gen["active_reflection"])

            # Timeline paging
            timeline = recall.page_generation_timeline(anchor_or_group_id="GEN-1", direction="after", limit=3)
            self.assertEqual(timeline["count"], 1)
            self.assertEqual(timeline["results"][0]["generation_id"], gen_res["id"])

    def test_archival_memory_superseded_filtering(self):
        with ArchivalMemoryManager(db_path=self.db_path) as archival:
            archival.insert("docs/active_note.md", "Active invariant rules", category="docs")
            archival.insert("docs/deprecated_note.md", "Deprecated old rules", category="docs")

            # Manually mark deprecated note as superseded
            conn = archival._get_connection()
            with conn:
                conn.execute("UPDATE pages SET superseded_by = 'GEN-1' WHERE path = 'docs/deprecated_note.md'")

            # Search without superseded (default)
            hits_active = archival.search("rules", include_superseded=False)
            hit_paths = [h["path"] for h in hits_active]
            self.assertIn("docs/active_note.md", hit_paths)
            self.assertNotIn("docs/deprecated_note.md", hit_paths)

            # Search with superseded
            hits_all = archival.search("rules", include_superseded=True)
            all_paths = [h["path"] for h in hits_all]
            self.assertIn("docs/active_note.md", all_paths)
            self.assertIn("docs/deprecated_note.md", all_paths)


if __name__ == "__main__":
    unittest.main()
