import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core.dna import record_dna_snapshot, get_dna_trend, sequence_project_dna


class TestDnaTrend(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_dir = os.path.join(self.tmp_dir.name, ".orion")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "orion.db")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_record_and_get_dna_trend(self):
        # Record 2 snapshots
        snap1 = record_dna_snapshot(self.tmp_dir.name, compliance_score=64, violations_count=12, chimera_count=0, file_count=200, db_path=self.db_path)
        self.assertTrue(snap1.get("ok", False))

        snap2 = record_dna_snapshot(self.tmp_dir.name, compliance_score=100, violations_count=0, chimera_count=0, file_count=200, db_path=self.db_path)
        self.assertTrue(snap2.get("ok", False))

        trend = get_dna_trend(self.tmp_dir.name, limit=10, db_path=self.db_path)
        self.assertEqual(len(trend["snapshots"]), 2)
        self.assertEqual(trend["snapshots"][0]["compliance_score"], 64)
        self.assertEqual(trend["snapshots"][1]["compliance_score"], 100)
        self.assertFalse(trend["has_regression"])

    def test_dna_trend_regression_detection(self):
        record_dna_snapshot(self.tmp_dir.name, compliance_score=100, violations_count=0, chimera_count=0, file_count=200, db_path=self.db_path)
        record_dna_snapshot(self.tmp_dir.name, compliance_score=64, violations_count=12, chimera_count=0, file_count=200, db_path=self.db_path)

        trend = get_dna_trend(self.tmp_dir.name, limit=10, db_path=self.db_path)
        self.assertTrue(trend["has_regression"])
        self.assertIn("64", trend["regression_reason"])


if __name__ == "__main__":
    unittest.main()
