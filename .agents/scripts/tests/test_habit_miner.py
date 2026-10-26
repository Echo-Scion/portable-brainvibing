import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.reflexion import mine_operator_habits


class TestHabitMiner(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.orion_dir = os.path.join(self.tmp_dir.name, ".orion", "working")
        os.makedirs(self.orion_dir, exist_ok=True)
        self.profile_path = os.path.join(self.orion_dir, "operator_profile.json")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_mine_operator_habits(self):
        # Create dummy session telemetry/trajectory
        traj_path = os.path.join(self.orion_dir, "trajectory.jsonl")
        actions = [
            {"kind": "action", "action_type": "read_file"},
            {"kind": "action", "action_type": "replace_file_content"},
            {"kind": "action", "action_type": "run_shell_command"},
            {"kind": "action", "action_type": "read_file"},
            {"kind": "action", "action_type": "replace_file_content"},
            {"kind": "action", "action_type": "run_shell_command"},
            {"kind": "action", "action_type": "read_file"},
            {"kind": "action", "action_type": "replace_file_content"},
            {"kind": "action", "action_type": "run_shell_command"},
        ]
        with open(traj_path, "w", encoding="utf-8") as f:
            for act in actions:
                f.write(json.dumps(act) + "\n")

        res = mine_operator_habits(workspace_dir=self.tmp_dir.name, profile_path=self.profile_path)
        self.assertTrue(res.get("ok", False))
        self.assertTrue(os.path.exists(self.profile_path))

        with open(self.profile_path, "r", encoding="utf-8") as f:
            prof = json.load(f)

        self.assertIn("tool_histogram", prof)
        self.assertEqual(prof["tool_histogram"].get("read_file"), 3)
        self.assertEqual(prof["tool_histogram"].get("replace_file_content"), 3)
        self.assertIn("ngram_patterns", prof)
        self.assertGreaterEqual(len(prof["ngram_patterns"]), 1)


if __name__ == "__main__":
    unittest.main()
