import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.reflexion import ObservationLedger
from core.harness.capture import ToolQuantumCapture


class TestObservationCapture(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.active_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.md")
        self.archive_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.archive.md")
        self.ledger = ObservationLedger(active_path=self.active_path, archive_path=self.archive_path)

    def tearDown(self):
        self.tmp_dir.cleanup()
        if "ANTIGRAVITY_SUBAGENT" in os.environ:
            del os.environ["ANTIGRAVITY_SUBAGENT"]

    def test_subagent_write_refusal(self):
        os.environ["ANTIGRAVITY_SUBAGENT"] = "1"
        res = self.ledger.add_observation(
            title="Subagent finding",
            kind="improve",
            target="subagent_target.py"
        )
        self.assertEqual(res["id"], -1)
        self.assertEqual(res["status"], "refused_subagent")
        active = self.ledger.get_all_observations()
        self.assertEqual(len(active), 0)

    def test_tool_failure_auto_promotion(self):
        capture = ToolQuantumCapture(self.tmp_dir.name)
        session_id = f"sess_fail_{os.getpid()}_{Path(__file__).stat().st_mtime}"
        capture.record_tool_call(session_id, "run_shell_command", {"command": "pytest", "exit_code": 1})

        # Check that observation was created in isolated test ledger
        test_ledger = ObservationLedger(active_path=self.active_path, archive_path=self.archive_path)
        obs_list = test_ledger.list_observations()
        tool_obs = [o for o in obs_list if "TOOL_EXIT_NONZERO" in o.get("rule_id", "")]
        self.assertGreaterEqual(len(tool_obs), 1)
        matching_targets = [o["target"] for o in tool_obs if "run_shell_command" in o.get("target", "")]
        self.assertGreaterEqual(len(matching_targets), 1)

    def test_pre_agent_wake_digest_surfacing(self):
        digest_ledger = ObservationLedger(active_path=self.active_path, archive_path=self.archive_path)
        digest_ledger.add_observation(
            title="Pre-agent wake surfacing test",
            kind="improve",
            target="hooks/pre-agent-wake.py"
        )
        digest = digest_ledger.get_digest()
        self.assertIn("open=1", digest)
        self.assertIn("top-target=hooks/pre-agent-wake.py", digest)


if __name__ == "__main__":
    unittest.main()
