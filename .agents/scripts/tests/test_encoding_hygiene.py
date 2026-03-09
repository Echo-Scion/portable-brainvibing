import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from commands.verify_agents import AuditResult, check_encoding_and_io_hygiene
import commands.verify_agents as va


class EncodingHygieneContractTests(unittest.TestCase):
    def test_clean_workspace_passes(self):
        res = AuditResult()
        check_encoding_and_io_hygiene(res, verbose=False)
        self.assertEqual(len(res.errors), 0, f"Expected 0 errors in clean workspace, got {res.errors}")

    def test_subprocess_without_encoding_flagged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "bad_subprocess.py")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("import subprocess\nsubprocess.run(['git', 'status'], capture_output=True, text=True)\n")

            original_base = va.BASE_DIR
            try:
                va.BASE_DIR = temp_dir
                res = AuditResult()
                check_encoding_and_io_hygiene(res, verbose=False)
                self.assertEqual(len(res.errors), 1)
                self.assertIn("subprocess.run() text mode missing explicit encoding='utf-8'", res.errors[0]["message"])
            finally:
                va.BASE_DIR = original_base

    def test_open_text_mode_without_encoding_flagged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "bad_open.py")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("with open('file.txt', 'r') as f:\n    content = f.read()\n")

            original_base = va.BASE_DIR
            try:
                va.BASE_DIR = temp_dir
                res = AuditResult()
                check_encoding_and_io_hygiene(res, verbose=False)
                self.assertEqual(len(res.errors), 1)
                self.assertIn("open() text mode missing explicit encoding='utf-8'", res.errors[0]["message"])
            finally:
                va.BASE_DIR = original_base

    def test_open_binary_mode_without_encoding_allowed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "good_binary.py")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("with open('file.bin', 'rb') as f:\n    data = f.read()\n")

            original_base = va.BASE_DIR
            try:
                va.BASE_DIR = temp_dir
                res = AuditResult()
                check_encoding_and_io_hygiene(res, verbose=False)
                self.assertEqual(len(res.errors), 0)
            finally:
                va.BASE_DIR = original_base

    def test_explicit_encoding_allowed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "good_io.py")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(
                    "import subprocess\n"
                    "subprocess.run(['git'], capture_output=True, text=True, encoding='utf-8', errors='replace')\n"
                    "with open('file.txt', 'w', encoding='utf-8') as f:\n"
                    "    f.write('hello')\n"
                )

            original_base = va.BASE_DIR
            try:
                va.BASE_DIR = temp_dir
                res = AuditResult()
                check_encoding_and_io_hygiene(res, verbose=False)
                self.assertEqual(len(res.errors), 0)
            finally:
                va.BASE_DIR = original_base


if __name__ == "__main__":
    unittest.main()
