#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_scaffolding_evolution.py — Test Suite for 2D Cognitive Scaffolding & Dynamic Routing Evolution

Verifies:
1. compute_scaffold_discount & 2D Tier x Effort classification in capabilities.py
2. Write-Set vs Read-Set hazard blocking in scanner.py (delegate-check)
3. Live AST symbol re-anchoring in bento_slicer.py
4. Structured failure memory recording in ACTIVE_TASK.md
5. Fast-track lane execution in state_machine.py
"""

import ast
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Setup import paths
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from core.capabilities import compute_scaffold_discount, resolve_elastic_execution_plan
from core.scanner import check_delegation_safety
from commands.bento_slicer import (
    resolve_live_ast_symbol_span,
    _extract_symbol_name,
    _clean_target_path,
    read_live_target_window,
    cmd_next,
    QUEUE_FILE,
    ACTIVE_TASK_FILE,
)
from commands.state_machine import cmd_fast_track


class TestScaffoldingEvolution(unittest.TestCase):
    def setUp(self):
        self._temp_dir_ctx = tempfile.TemporaryDirectory()
        self.ws = Path(self._temp_dir_ctx.name)

    def tearDown(self):
        self._temp_dir_ctx.cleanup()

    def test_scaffold_discount_math(self):
        """Verifies gamma discount formula: raw=0%, ast=35%, bento=65%."""
        base = 10.0
        self.assertEqual(compute_scaffold_discount(base, "raw"), 10.0)
        self.assertEqual(compute_scaffold_discount(base, "ast_mapped"), 6.5)
        self.assertEqual(compute_scaffold_discount(base, "bento_card"), 3.5)

    def test_2d_tier_effort_classification(self):
        """Verifies 2D model routing tuple generation with scaffolding discount."""
        with patch("core.capabilities.resolve_ollama_base_url", return_value=None):
            # 1. Nano task with raw stage -> BUDGET [Low Effort]
            nano_plan = resolve_elastic_execution_plan("nano", blast_radius_files=1, span_lines=10, use_2d=True)
            self.assertEqual(nano_plan["recommended_cloud_tier"], "BUDGET [Low Effort]")

            # 2. Bento active card with single_fn -> BUDGET [High Effort]
            bento_plan = resolve_elastic_execution_plan(
                "single_fn", blast_radius_files=1, span_lines=40, scaffold_stage="bento_card", use_2d=True
            )
            self.assertEqual(bento_plan["recommended_cloud_tier"], "BUDGET [High Effort]")
            self.assertEqual(bento_plan["scaffold_discount_gamma"], 0.65)

            # 3. Multi-file refactor without bento -> STANDARD
            multi_plan = resolve_elastic_execution_plan("multi_fn", blast_radius_files=3, span_lines=100, use_2d=True)
            self.assertEqual(multi_plan["recommended_cloud_tier"], "STANDARD [Medium/High Effort]")

            # 4. Raw Genesis architectural task -> PREMIUM [High Effort]
            arch_plan = resolve_elastic_execution_plan("architectural", blast_radius_files=6, span_lines=500, use_2d=True)
            self.assertEqual(arch_plan["recommended_cloud_tier"], "PREMIUM [High Effort]")

    def test_delegate_check_write_write_hazard(self):
        """Verifies that tasks with overlapping write sets are hard blocked (Exit Code 1)."""
        t1_files = ["src/shared_model.py"]
        t2_files = ["src/shared_model.py"]
        exit_code = check_delegation_safety([t1_files, t2_files], threshold=0.20, as_json=True)
        self.assertEqual(exit_code, 1)

    def test_delegate_check_disjoint_tasks(self):
        """Verifies strictly disjoint tasks succeed (Exit Code 0)."""
        t1_files = ["README.md"]
        t2_files = ["LICENSE"]
        exit_code = check_delegation_safety([t1_files, t2_files], threshold=0.20, as_json=True)
        self.assertEqual(exit_code, 0)

    def test_live_ast_symbol_re_anchoring(self):
        """Verifies dynamic AST symbol line span resolution across file mutations."""
        py_file = self.ws / "math_module.py"
        # Initial file content
        py_file.write_text(
            "import os\n\n\ndef add(a, b):\n    return a + b\n\n\ndef multiply(x, y):\n    return x * y\n",
            encoding="utf-8",
        )

        span = resolve_live_ast_symbol_span(py_file, "multiply")
        self.assertIsNotNone(span)
        start, end = span
        self.assertEqual(start, 8)
        self.assertEqual(end, 9)

        # Mutate file by inserting 10 lines at the top (simulating prior card insertion)
        padding = "\n".join([f"# Pad line {i}" for i in range(10)]) + "\n"
        py_file.write_text(padding + py_file.read_text(encoding="utf-8"), encoding="utf-8")

        # Re-query symbol span: must dynamically re-anchor to lines 18-19!
        new_span = resolve_live_ast_symbol_span(py_file, "multiply")
        self.assertIsNotNone(new_span)
        new_start, new_end = new_span
        self.assertEqual(new_start, 18)
        self.assertEqual(new_end, 19)

    def test_symbol_name_and_path_cleaning(self):
        """Verifies target path cleaning and symbol extraction from target span."""
        self.assertEqual(_clean_target_path("src/core.py::run_engine"), "src/core.py")
        self.assertEqual(_clean_target_path("`src/core.py#L10-L25`"), "src/core.py")
        self.assertEqual(_extract_symbol_name("Symbol: `calculate_metrics`", "src/core.py"), "calculate_metrics")
        self.assertEqual(_extract_symbol_name("Lines 20-40", "src/core.py::process_item"), "process_item")

    def test_structured_failure_memory_generation(self):
        """Verifies failed verification records attempted approaches in ACTIVE_TASK.md."""
        orion_working = self.ws / ".orion" / "working"
        orion_working.mkdir(parents=True, exist_ok=True)
        active_task_path = orion_working / ACTIVE_TASK_FILE
        queue_path = orion_working / QUEUE_FILE

        # Create dummy python file
        target = self.ws / "app.py"
        target.write_text("def compute():\n    return 42\n", encoding="utf-8")

        # Initial queue and active task
        queue_data = {
            "current_index": 0,
            "tasks": [
                {
                    "task_id": "T-01",
                    "title": "Broken Patch",
                    "target_file": "app.py",
                    "search_code": "return 42",
                    "replacement_code": "return 100",
                    "verification_cmd": "python -c \"import sys; sys.stderr.write('AssertionError: expected 99\\n'); sys.exit(1)\"",
                }
            ],
        }
        queue_path.write_text(json.dumps(queue_data), encoding="utf-8")
        active_task_path.write_text("# Active Task T-01\nOriginal instructions\n", encoding="utf-8")

        # Apply mutation to disk so verify_patch_applied_on_disk passes
        target.write_text("def compute():\n    return 100\n", encoding="utf-8")

        # Mock workspace paths in bento_slicer
        with patch("commands.bento_slicer.get_workspace_dir", return_value=self.ws), patch(
            "commands.bento_slicer.get_orion_dir", return_value=self.ws / ".orion"
        ):
            exit_code = cmd_next(run_verify=True)
            self.assertEqual(exit_code, 1)

            # Check that ACTIVE_TASK.md now contains structured failure memory
            active_content = active_task_path.read_text(encoding="utf-8")
            self.assertIn("## ❌ Attempted & Failed Approaches", active_content)
            self.assertIn("AssertionError: expected 99", active_content)
            self.assertIn("Do NOT retry the exact same modification pattern", active_content)

    def test_fast_track_limit(self):
        """Verifies fast-track lane permits <= 2 files and rejects >= 3 files."""
        self.assertEqual(cmd_fast_track(["file1.py", "file2.py"], description="Small tweak"), 0)
        self.assertEqual(cmd_fast_track(["a.py", "b.py", "c.py"]), 1)


if __name__ == "__main__":
    unittest.main()
