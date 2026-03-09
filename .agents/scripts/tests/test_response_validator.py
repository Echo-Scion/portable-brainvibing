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
        self.assertEqual(validate_response(f"Fixed the issue.\n{FOOTER}", require_footer=True), [])

    def test_rejects_missing_footer_when_required(self):
        findings = validate_response("Fixed the issue.", require_footer=True)
        self.assertTrue(any(finding.rule == "footer" for finding in findings))

    def test_accepts_response_without_footer_by_default(self):
        self.assertEqual(validate_response("Fixed the issue."), [])

    def test_accepts_multilingual_response(self):
        findings = validate_response("Kenapa ini harus diperbaiki?")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
