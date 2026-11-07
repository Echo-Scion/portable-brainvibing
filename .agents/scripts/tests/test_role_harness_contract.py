import unittest
import sys
import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.worker import (
    ROLE_HARNESS_MATRIX,
    classify_task_role,
    _resolve_role_model,
    get_worker_status,
)


class RoleHarnessContractTests(unittest.TestCase):
    def test_role_harness_matrix_contains_all_ten_roles(self):
        expected_roles = {
            "orchestrator",
            "reviewer",
            "fixer",
            "explorer",
            "plan",
            "oracle",
            "designer",
            "librarian",
            "web-researcher",
            "councillor",
        }
        self.assertEqual(set(ROLE_HARNESS_MATRIX.keys()), expected_roles)
        for r_name, r_meta in ROLE_HARNESS_MATRIX.items():
            self.assertIn("title", r_meta)
            self.assertIn("slot_api", r_meta)
            self.assertIn("slot_local", r_meta)
            self.assertIn("turn_limit", r_meta)
            self.assertGreater(r_meta["turn_limit"], 0)

    def test_model_slot_resolution_api_and_local(self):
        models_map = {
            "api_nano": "model-nano",
            "api_fast": "model-fast",
            "api_smart": "model-smart",
            "api_council": "model-council",
            "local_fast": "local-nano",
            "local_code": "local-fast",
            "local_heavy": "local-smart",
        }
        self.assertEqual(_resolve_role_model("explorer", "api", "default", models_map), "model-nano")
        self.assertEqual(_resolve_role_model("fixer", "api", "default", models_map), "model-fast")
        self.assertEqual(_resolve_role_model("oracle", "api", "default", models_map), "model-smart")
        self.assertEqual(_resolve_role_model("councillor", "api", "default", models_map), "model-council")

        self.assertEqual(_resolve_role_model("explorer", "ollama", "default", models_map), "local-nano")
        self.assertEqual(_resolve_role_model("fixer", "ollama", "default", models_map), "local-fast")
        self.assertEqual(_resolve_role_model("oracle", "ollama", "default", models_map), "local-smart")

    def test_intent_classifier_heuristics(self):
        self.assertEqual(classify_task_role("Explore and map the symbols in db.py"), "explorer")
        self.assertEqual(classify_task_role("Audit and check security vulnerabilities in auth handler"), "reviewer")
        self.assertEqual(classify_task_role("Fix and repair the failing test in worker_test.py"), "fixer")
        self.assertEqual(classify_task_role("Write a plan and action card breakdown for caching"), "plan")
        self.assertEqual(classify_task_role("Examine strategic tradeoffs and invariants for persistence"), "oracle")
        self.assertEqual(classify_task_role("Improve UI layout and WCAG color contrast"), "designer")
        self.assertEqual(classify_task_role("Search docs and retrieve canon guidelines"), "librarian")
        self.assertEqual(classify_task_role("Find external web packages for websocket clients"), "web-researcher")
        self.assertEqual(classify_task_role("Provide a second opinion to resolve the architectural debate"), "councillor")

    def test_worker_status_includes_council_model(self):
        status = get_worker_status()
        self.assertIn("api_council", status["models"])


if __name__ == "__main__":
    unittest.main()
