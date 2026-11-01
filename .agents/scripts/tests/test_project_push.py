#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Tests for `scan prose`, changelog gate, test-runner detection, and pre-push hook install."""

import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_TESTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from core.scanner import audit_prose_text
from commands.foundation import (
    _check_changelog_unreleased,
    _detect_test_command,
    cmd_project_install_hooks,
    cmd_project_push,
)


class ProseAuditTests(unittest.TestCase):
    def test_flags_ai_tells(self):
        cats = {f["category"] for f in audit_prose_text("We delve into a pivotal design.\n")}
        self.assertIn("AI_TELL", cats)

    def test_flags_binary_contrast(self):
        cats = {f["category"] for f in audit_prose_text("The answer isn't speed. It's safety.\n")}
        self.assertIn("BINARY_CONTRAST", cats)

    def test_clean_text_passes(self):
        self.assertEqual(audit_prose_text("Run the audit. It reports violations.\n"), [])

    def test_code_fence_and_inline_code_ignored(self):
        text = "```\ndelve pivotal\n```\nUse `delve` here.\n"
        self.assertEqual(audit_prose_text(text), [])

    def test_duplicate_sentence_flagged(self):
        s = "The scanner reports every violation it finds across all tracked source files."
        cats = {f["category"] for f in audit_prose_text(f"{s}\n\nOther text.\n\n{s}\n")}
        self.assertIn("SSOT_DUPLICATE", cats)


class ChangelogGateTests(unittest.TestCase):
    def _write(self, d, body):
        with open(os.path.join(d, "CHANGELOG.md"), "w", encoding="utf-8") as f:
            f.write(body)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(_check_changelog_unreleased(d)[0])

    def test_empty_unreleased_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self._write(d, "# Changelog\n\n## [Unreleased]\n\n## [1.0.0]\n- Added x\n")
            self.assertFalse(_check_changelog_unreleased(d)[0])

    def test_populated_unreleased_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            self._write(d, "# Changelog\n\n## [Unreleased]\n\n### Added\n- Add push command\n")
            self.assertTrue(_check_changelog_unreleased(d)[0])


class RunnerAndHookTests(unittest.TestCase):
    def test_detect_runner(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(_detect_test_command(d))
            open(os.path.join(d, "go.mod"), "w", encoding="utf-8").close()
            self.assertEqual(_detect_test_command(d)[0], "go")

    def test_install_hook(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(cmd_project_install_hooks(SimpleNamespace(target=d)))
            os.makedirs(os.path.join(d, ".git", "hooks"))
            self.assertTrue(cmd_project_install_hooks(SimpleNamespace(target=d)))
            hook = os.path.join(d, ".git", "hooks", "pre-push")
            with open(hook, encoding="utf-8") as f:
                self.assertIn("push --pre-push-hook", f.read())
            self.assertTrue(cmd_project_install_hooks(SimpleNamespace(target=d)))

    def test_existing_hook_backed_up(self):
        with tempfile.TemporaryDirectory() as d:
            hooks = os.path.join(d, ".git", "hooks")
            os.makedirs(hooks)
            with open(os.path.join(hooks, "pre-push"), "w", encoding="utf-8") as f:
                f.write("#!/bin/sh\necho custom\n")
            cmd_project_install_hooks(SimpleNamespace(target=d))
            self.assertTrue(os.path.exists(os.path.join(hooks, "pre-push.bak")))

    def test_push_blocked_without_changelog(self):
        with tempfile.TemporaryDirectory() as d:
            args = SimpleNamespace(target=d, dry_run=True, pre_push_hook=False, skip_tests=True,
                                   remote="origin", branch="main")
            self.assertFalse(cmd_project_push(args))


if __name__ == "__main__":
    unittest.main()
