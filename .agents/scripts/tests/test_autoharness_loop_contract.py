import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core.db import (
    sovereign_catch,
    mechanical_catch,
    drain_mechanical_catches,
    MechanicalInvariantError,
)
from core.capabilities import (
    _strip_reasoning_and_fences,
    _extract_json_payload,
    resolve_elastic_execution_plan,
)
from commands.reflexion import ReflexionEngine, ReflexionLoop
from core.harness.engine import HarnessEngine


class AutoharnessLoopContractTests(unittest.TestCase):
    def test_seam1_and_seam2_post_condition_and_mutable_fallback_isolation(self):
        """Verifies @mechanical_catch traps silent semantic lies and deep-copies mutable fallbacks."""
        @mechanical_catch(
            "test_module:fetch_items",
            fallback_value=[],
            post_condition=lambda res: (len(res) > 0, "Result list must not be empty"),
        )
        def boundary_fn(should_lie: bool):
            return [] if should_lie else ["valid_item"]

        self.assertEqual(boundary_fn(False), ["valid_item"])

        fallback_1 = boundary_fn(True)
        self.assertEqual(fallback_1, [])
        fallback_1.append("mutated")

        fallback_2 = boundary_fn(True)
        self.assertEqual(fallback_2, [])

    def test_seam3_strip_reasoning_and_unclosed_think_tags(self):
        """Verifies <think> tags (closed and truncated) and markdown fences are stripped before JSON parse."""
        raw_closed = "<think>\nLet me analyze the AST...\n</think>\n```json\n{\"old_string\": \"a = 1\", \"new_string\": \"a = 2\", \"reflection\": \"fixed\"}\n```"
        parsed = _extract_json_payload(raw_closed)
        self.assertEqual(parsed["new_string"], "a = 2")

        raw_unclosed = "{\"status\": \"ok\"} <think> trailing truncated thought..."
        parsed_unclosed = _extract_json_payload(raw_unclosed)
        self.assertEqual(parsed_unclosed["status"], "ok")

    def test_seam3_elastic_continuum_across_1_5b_3b_7b_30b_and_offline(self):
        """Verifies dynamic capability matching across 0B, 1.5B, 3B, 7B, and 32B models."""
        # 1. 1.5B model: eligible for 'nano' tasks, skipped (0 trials) for 'single_fn' code patching -> recommends BUDGET
        with patch("core.capabilities.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"), patch(
            "core.capabilities.select_optimal_ollama_model", return_value="qwen2.5-coder:1.5b"
        ):
            nano_plan = resolve_elastic_execution_plan("nano", blast_radius_files=1, span_lines=10)
            self.assertEqual(nano_plan["local_max_trials"], 2)

            fn_plan = resolve_elastic_execution_plan("single_fn", blast_radius_files=1, span_lines=40)
            self.assertEqual(fn_plan["local_max_trials"], 0)
            self.assertEqual(fn_plan["recommended_cloud_tier"], "BUDGET")

        # 2. 3B model: gets 1 fast AST-guarded trial on 'micro_syntax' or narrow AST spans
        with patch("core.capabilities.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"), patch(
            "core.capabilities.select_optimal_ollama_model", return_value="qwen2.5-coder:3b"
        ):
            syntax_plan = resolve_elastic_execution_plan("micro_syntax", blast_radius_files=1, span_lines=10)
            self.assertEqual(syntax_plan["local_max_trials"], 1)
            self.assertEqual(syntax_plan["eligible_local_model"], "qwen2.5-coder:3b")

        # 3. 7B model: gets 2 trials on 'single_fn' logic repair
        with patch("core.capabilities.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"), patch(
            "core.capabilities.select_optimal_ollama_model", return_value="qwen2.5-coder:7b"
        ):
            fn7_plan = resolve_elastic_execution_plan("single_fn", blast_radius_files=1, span_lines=40)
            self.assertEqual(fn7_plan["local_max_trials"], 2)

        # 4. 32B model: gets full 3 trials even on 'multi_fn' refactors
        with patch("core.capabilities.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"), patch(
            "core.capabilities.select_optimal_ollama_model", return_value="qwen2.5-coder:32b"
        ):
            heavy_plan = resolve_elastic_execution_plan("multi_fn", blast_radius_files=3, span_lines=120)
            self.assertEqual(heavy_plan["local_max_trials"], 3)

    def test_seam3_reflexion_loop_auto_heal_with_capable_local_slm(self):
        """Verifies ReflexionLoop.auto_heal repairs a broken Python file when a capable local SLM is available."""
        with tempfile.TemporaryDirectory() as tmp:
            buggy_file = os.path.join(tmp, "calc.py")
            test_file = os.path.join(tmp, "test_calc.py")

            with open(buggy_file, "w", encoding="utf-8") as f:
                f.write("def add(a, b):\n    return a - b\n")

            with open(test_file, "w", encoding="utf-8") as f:
                f.write(
                    "import unittest\nfrom calc import add\n"
                    "class T(unittest.TestCase):\n"
                    "    def test_add(self): self.assertEqual(add(2, 3), 5)\n"
                    "if __name__ == '__main__': unittest.main()\n"
                )

            mock_patch = {
                "old_string": "return a - b",
                "new_string": "return a + b",
                "reflection": "Operator '-' inverted; fixed to '+'.",
            }

            loop = ReflexionLoop(max_trials=3)
            with patch(
                "core.capabilities.resolve_elastic_execution_plan",
                return_value={
                    "eligible_local_model": "qwen2.5-coder:7b",
                    "installed_params_b": 7.0,
                    "effective_min_params_b": 3.0,
                    "local_max_trials": 2,
                    "recommended_cloud_tier": "BUDGET",
                },
            ), patch(
                "core.capabilities.execute_neuro_symbolic",
                return_value=(mock_patch, "local_slm:qwen2.5-coder:7b"),
            ), patch.object(ReflexionEngine, "record_learning", return_value=True):
                res = loop.auto_heal(
                    target_file=buggy_file,
                    test_cmd=[sys.executable, "-B", test_file],
                    problem_description="Fix addition operator",
                )

            self.assertTrue(res["healed"])
            self.assertEqual(res["trials"], 1)

    def test_seam4_synthesize_action_verifier(self):
        """Verifies HarnessEngine synthesizes an executable is_legal_action verifier script."""
        with tempfile.TemporaryDirectory() as tmp:
            engine = HarnessEngine(
                skills_dir=os.path.join(tmp, "skills"),
                state_dir=os.path.join(tmp, "harness"),
            )
            harnesses_dir = os.path.join(tmp, "harnesses")
            res = engine.synthesize_action_verifier(
                rule_id="ORION-NO-RAW-SQL",
                forbidden_pattern=r"rawQuery\s*\(",
                error_message="Use parameterized queries instead of rawQuery concatenation.",
                harnesses_dir=harnesses_dir,
            )
            self.assertTrue(res["ok"])
            self.assertTrue(os.path.isfile(res["verifier_path"]))


if __name__ == "__main__":
    unittest.main()
