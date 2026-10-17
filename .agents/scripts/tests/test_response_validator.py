import unittest

from pathlib import Path
import sys

EVALS_DIR = Path(__file__).resolve().parents[2] / "evals"
sys.path.insert(0, str(EVALS_DIR))

from assertion_engine import validate_response


FOOTER = """
CHECKPOINT: Done.
EVIDENCE: Exit Code 0.
NEXT TASK: None.
"""


class ResponseValidatorTests(unittest.TestCase):
    def test_accepts_english_response_with_footer(self):
        self.assertEqual(validate_response(f"Fixed the issue.\n{FOOTER}"), [])

    def test_rejects_missing_footer(self):
        findings = validate_response("Fixed the issue.")
        self.assertTrue(any(finding.rule == "footer" for finding in findings))

    def test_rejects_clear_non_english_response(self):
        findings = validate_response(f"Kenapa ini harus diperbaiki?\n{FOOTER}")
        self.assertTrue(any(finding.rule == "english" for finding in findings))

    def test_ignores_non_english_code(self):
        findings = validate_response(f"Use this command:\n```text\nkenapa ini\n```\n{FOOTER}")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
