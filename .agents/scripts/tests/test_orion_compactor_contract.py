import unittest
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPTS_ROOT not in sys.path:
    sys.path.insert(0, SCRIPTS_ROOT)

from commands.brain import (
    OrionCompactor,
    SyntaxAnchorGuard,
    lessword_compress_text,
    telegraphic_shrink,
    compact_target,
)


class OrionCompactorContractTests(unittest.TestCase):
    def test_lite_removes_ansi_and_folds_duplicates(self):
        sample = "\x1b[31mRed text\x1b[0m   \n\n\nRepeated line\nRepeated line\nRepeated line\nEnd"
        result = OrionCompactor.run_lite(sample)
        self.assertNotIn("\x1b[31m", result)
        self.assertIn("Repeated line", result)
        self.assertIn("[repeated 2x]", result)
        self.assertTrue(result.endswith("End"))

    def test_full_syntax_anchor_guard(self):
        text = (
            "In order to implement a solution for the problem, make sure to execute `python manage.py test` "
            "and check $DATABASE_URL and [[ObsidianLink]]."
        )
        res = OrionCompactor.compress(text, level="full")
        self.assertEqual(res["status"], "COMPRESSED")
        output = res["output"]
        self.assertIn("to fix problem", output)
        self.assertIn("`python manage.py test`", output)
        self.assertIn("$DATABASE_URL", output)
        self.assertIn("[[ObsidianLink]]", output)

    def test_full_syntax_anchor_guard_preserves_invariants(self):
        text = (
            "In order to style the interface, make sure to use 60:30:10 ratio, radius <= 8px, "
            "16,000 chars limit, and require Exit Code 0 with >= 95% test coverage."
        )
        res = OrionCompactor.compress(text, level="full")
        self.assertEqual(res["status"], "COMPRESSED")
        output = res["output"]
        self.assertIn("60:30:10", output)
        self.assertIn("<= 8px", output)
        self.assertIn("16,000 chars", output)
        self.assertIn("Exit Code 0", output)
        self.assertIn(">= 95%", output)

    def test_safety_boundary_escape_auto_clarity(self):
        dangerous = "Please make sure to drop table users if critical vulnerability is found."
        res = OrionCompactor.compress(dangerous, level="full")
        self.assertEqual(res["status"], "UNCHANGED_OPTIMAL")
        self.assertEqual(res["output"], dangerous)

    def test_aggressive_payload_shaper_ast_hollowing(self):
        code = (
            "import os\n\n"
            "def calculate_total(items: list) -> float:\n"
            "    '''Calculates sum of items.'''\n"
            "    total = 0.0\n"
            "    for item in items:\n"
            "        total += item.price\n"
            "    return total\n"
        )
        res = OrionCompactor.compress(code, level="aggressive", filename_hint="service.py")
        self.assertEqual(res["status"], "COMPRESSED")
        self.assertIn("shaper:ast_python", res["stages"])
        self.assertIn("def calculate_total", res["output"])
        self.assertIn("...", res["output"])
        self.assertNotIn("total += item.price", res["output"])

    def test_chronological_section_decay(self):
        doc = (
            "# Execution Log\n\n"
            "## Resume Point\nCritical checkpoint verbatim.\n\n"
            "## Anti-Goals\nNever do X.\n\n"
            "## Old Section 0\n" + ("Historical detail line.\n" * 15) + "\n"
            "## Old Section 1\n" + ("Historical detail line.\n" * 15) + "\n"
            "## Old Section 2\n" + ("Historical detail line.\n" * 15) + "\n"
            "## Mid Section\nIn order to utilize the cache, check config.\n\n"
            "## Recent Section\nFresh verbatim state.\n"
        )
        res = OrionCompactor.compress(doc, level="aggressive")
        self.assertEqual(res["status"], "COMPRESSED")
        output = res["output"]
        self.assertIn("## Resume Point\nCritical checkpoint verbatim.", output)
        self.assertIn("## Anti-Goals\nNever do X.", output)
        self.assertIn("## Recent Section\nFresh verbatim state.", output)
        self.assertIn("historical lines archived", output)

    def test_ultra_abbreviations(self):
        text = "The database authentication configuration function request leads to response."
        res = OrionCompactor.compress(text, level="ultra")
        self.assertEqual(res["status"], "COMPRESSED")
        output = res["output"]
        self.assertIn("DB", output)
        self.assertIn("auth", output)
        self.assertIn("config", output)
        self.assertIn("fn", output)
        self.assertIn("req", output)
        self.assertIn("->", output)
        self.assertIn("res", output)

    def test_integrity_verification_gate_fence_preservation(self):
        text = "```python\nprint('hello')\n```"
        # Simulate fence count match
        res = OrionCompactor.compress(text, level="pipeline")
        self.assertEqual(text.count("```"), res["output"].count("```"))

    def test_legacy_aliases(self):
        self.assertTrue(callable(telegraphic_shrink))
        self.assertTrue(callable(lessword_compress_text))
        self.assertTrue(callable(compact_target))
        comp = lessword_compress_text("In order to implement a solution for the bug")
        self.assertIn("to fix", comp)


if __name__ == "__main__":
    unittest.main()
