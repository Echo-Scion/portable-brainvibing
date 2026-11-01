#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
test_worktree_universal.py
--------------------------
Unit and integration test suite asserting that the Worktree Seeder Engine
is 100% universal, cross-platform, zero-pip compliant, and preserves
declarative whitelist environments.
"""

import os
import sys
import tempfile
import unittest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_TESTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from core.worktree import WorktreeSeeder, WorktreeSeedReport, DEFAULT_WORKTREE_PATTERNS


class TestWorktreeUniversal(unittest.TestCase):
    def test_pattern_matching(self):
        """Verifies wildcard and directory matching for .worktreeinclude."""
        patterns = [
            ".env",
            ".env.local",
            ".env.*.local",
            ".orion/working/context.json",
            "local/",
            "config/*.json",
        ]

        self.assertTrue(WorktreeSeeder.match_path(".env", patterns))
        self.assertTrue(WorktreeSeeder.match_path(".env.local", patterns))
        self.assertTrue(WorktreeSeeder.match_path(".env.staging.local", patterns))
        self.assertTrue(WorktreeSeeder.match_path(".orion/working/context.json", patterns))
        self.assertTrue(WorktreeSeeder.match_path("local/secret.key", patterns))
        self.assertTrue(WorktreeSeeder.match_path("config/db.json", patterns))

        # Negatives
        self.assertFalse(WorktreeSeeder.match_path("src/main.py", patterns))
        self.assertFalse(WorktreeSeeder.match_path("README.md", patterns))
        self.assertFalse(WorktreeSeeder.match_path(".orion/cache/large.db", patterns))

    def test_seeding_into_target_worktree(self):
        """Verifies files matching .worktreeinclude are cloned into target worktree."""
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as target_dir:
            # 1. Setup source assets
            with open(os.path.join(src_dir, ".env"), "w", encoding="utf-8") as f:
                f.write("SECRET_KEY=super-secret-123\n")

            os.makedirs(os.path.join(src_dir, ".orion", "working"), exist_ok=True)
            with open(os.path.join(src_dir, ".orion", "working", "context.json"), "w", encoding="utf-8") as f:
                f.write('{"active_task": "TASK-42"}\n')

            os.makedirs(os.path.join(src_dir, "local"), exist_ok=True)
            with open(os.path.join(src_dir, "local", "dev_override.txt"), "w", encoding="utf-8") as f:
                f.write("local override content\n")

            # Non-whitelisted file (must NOT be seeded)
            with open(os.path.join(src_dir, "regular_code.py"), "w", encoding="utf-8") as f:
                f.write("print('hello')\n")

            # Custom .worktreeinclude
            with open(os.path.join(src_dir, ".worktreeinclude"), "w", encoding="utf-8") as f:
                f.write(".env\n.orion/working/context.json\nlocal/\n")

            # 2. Seed worktree
            report = WorktreeSeeder.seed_worktree(source_root=src_dir, target_worktree=target_dir)

            self.assertEqual(len(report.errors), 0)
            self.assertIn(".env", report.files_seeded)
            self.assertIn(os.path.join(".orion", "working", "context.json").replace("\\", "/"), [p.replace("\\", "/") for p in report.files_seeded])
            self.assertIn(os.path.join("local", "dev_override.txt").replace("\\", "/"), [p.replace("\\", "/") for p in report.files_seeded])
            self.assertNotIn("regular_code.py", report.files_seeded)

            # 3. Verify physical contents in target worktree
            target_env = os.path.join(target_dir, ".env")
            target_context = os.path.join(target_dir, ".orion", "working", "context.json")
            target_local = os.path.join(target_dir, "local", "dev_override.txt")
            target_regular = os.path.join(target_dir, "regular_code.py")

            self.assertTrue(os.path.isfile(target_env))
            self.assertTrue(os.path.isfile(target_context))
            self.assertTrue(os.path.isfile(target_local))
            self.assertFalse(os.path.isfile(target_regular))

            with open(target_env, "r", encoding="utf-8") as f:
                self.assertIn("SECRET_KEY=super-secret-123", f.read())

    def test_dry_run_simulation(self):
        """Verifies dry run reports candidate files without writing to disk."""
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as target_dir:
            with open(os.path.join(src_dir, ".env"), "w", encoding="utf-8") as f:
                f.write("KEY=VAL\n")

            report = WorktreeSeeder.seed_worktree(source_root=src_dir, target_worktree=target_dir, dry_run=True)

            self.assertIn(".env", report.files_seeded)
            self.assertEqual(report.reflink_count, 0)
            self.assertEqual(report.hardlink_count, 0)
            self.assertEqual(report.copy_count, 0)
            self.assertFalse(os.path.exists(os.path.join(target_dir, ".env")))

    def test_copy_fallback_integrity(self):
        """Verifies copy_only disallows hardlinks and uses standard copy."""
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as target_dir:
            with open(os.path.join(src_dir, ".env"), "w", encoding="utf-8") as f:
                f.write("COPIED_CONTENT=1\n")

            report = WorktreeSeeder.seed_worktree(source_root=src_dir, target_worktree=target_dir, allow_hardlink=False)

            self.assertEqual(report.hardlink_count, 0)
            self.assertGreater(report.copy_count + report.reflink_count, 0)
            with open(os.path.join(target_dir, ".env"), "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "COPIED_CONTENT=1\n")


if __name__ == "__main__":
    unittest.main()
