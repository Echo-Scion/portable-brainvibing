import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.orion_graph import OrionGraphStore
from core.capabilities import python_fallback_stream_filter


class Phase5LifecycleContractTests(unittest.TestCase):
    def test_fallback_filter_removes_ansi_and_collapses_long_output(self):
        output = "\n".join(["\x1b[31mPASS\x1b[0m"] + ["."] * 120 + ["FAILED decisive error"])

        filtered = python_fallback_stream_filter(output)

        self.assertNotIn("\x1b[31m", filtered)
        self.assertIn("PASS", filtered)
        self.assertIn("FAILED decisive error", filtered)
        self.assertIn("repeated", filtered)

    def test_graph_reopens_persisted_entity_and_close_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "orion.db")
            first = OrionGraphStore(db_path)
            first.add_entity("deployment", "phase", "Phase 5 deployment lifecycle")
            first.close()
            first.close()

            reopened = OrionGraphStore(db_path)
            try:
                result = reopened.search_dual_level("deployment")
                self.assertEqual(result["micro_entities"][0]["name"], "deployment")
                self.assertFalse(reopened.is_closed)
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
