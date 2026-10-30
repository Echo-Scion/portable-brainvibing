#!/usr/bin/env python3
"""Unit tests for Sovereign Surgical Foundation Upgrade Engine.

Verifies Sacred File Shield, Surgical BIOS Splicing, and Two-Phase Transactional Rollback.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core.upgrade_engine import (
    SacredFileShield,
    SurgicalBiosSplicer,
    SplicerMarkerMissingError,
    TransactionalUpgrader,
    UpgradeVerificationError,
)


class TestSacredFileShield(unittest.TestCase):
    """Verifies that user-owned and private assets are shielded from upstream clobbering."""

    def test_shielded_paths(self):
        shielded = [
            "context/VISION.md",
            "context/AGENT_IDENTITY.md",
            "context/03_Tech/ARCHITECTURE.md",
            ".orion/orion.db",
            ".orion/working/context.json",
            ".agents/rules/local/custom_rule.md",
            ".agents/skills/local/custom_skill/SKILL.md",
            ".agents/canons/local/readme.md",
            ".agents/evals/local/eval.py",
            "VERSION",
            "README.md",
            "CHANGELOG.md",
            "package.json",
            "pubspec.yaml",
            "Cargo.toml",
            ".agents/.foundation_path",
            ".agents/.dna.json",
            ".agents/OBSERVATIONS.md",
            ".agents/LEARNINGS.md",
            ".git/config",
            ".scratch/temp.txt",
        ]
        for p in shielded:
            self.assertTrue(SacredFileShield.is_shielded(p), f"Path should be shielded: {p}")

    def test_allowed_framework_paths(self):
        allowed = [
            ".agents/scripts/core/scanner.py",
            ".agents/scripts/core/upgrade_engine.py",
            ".agents/scripts/orion.py",
            ".agents/rules/tier-execution-protocol.md",
            ".agents/rules/performance-optimization.md",
            ".agents/skills/strict-tdd/SKILL.md",
            ".agents/canons/ecosystems/flutter/flutter-architecture.md",
            ".agents/canons/ecosystems/react/react-patterns.md",
        ]
        for p in allowed:
            self.assertFalse(SacredFileShield.is_shielded(p), f"Path should be upgradeable: {p}")


class TestSurgicalBiosSplicer(unittest.TestCase):
    """Verifies precision splicing of AGENTS.md and GEMINI.md."""

    def setUp(self):
        self.sample_spoke_bios = (
            "# Workspace Rules & Mandates: MySpokeApp\n\n"
            "<!-- START FOUNDATION MANDATES (Version: 0.0.1 - English First & Built-In Lessword) -->\n"
            "Old foundation mandate v0.0.1 text here.\n"
            "- Rule 1: old\n"
            "<!-- END FOUNDATION MANDATES -->\n\n"
            "## PROJECT-SPECIFIC MANDATES\n"
            "- Cross-Platform Invariant: Custom Windows PowerShell port 8080.\n"
            "- Team Mandate: All models must use snake_case JSON serialization.\n"
        )

        self.sample_upstream_bios = (
            "# Workspace Rules & Mandates: {{PROJECT_NAME}}\n\n"
            "<!-- START FOUNDATION MANDATES (Version: 0.0.3 - English First & Built-In Lessword) -->\n"
            "New foundation mandate v0.0.3 text here.\n"
            "- Rule 1: new and improved\n"
            "- Rule 2: Tier 2 accelerators enabled\n"
            "<!-- END FOUNDATION MANDATES -->\n\n"
            "## PROJECT-SPECIFIC MANDATES\n"
            "<!-- Default empty upstream template instructions -->\n"
        )

    def test_splice_preserves_user_mandates(self):
        spliced = SurgicalBiosSplicer.splice(self.sample_spoke_bios, self.sample_upstream_bios)

        # 1. Contains new upstream mandates
        self.assertIn("Version: 0.0.3", spliced)
        self.assertIn("Tier 2 accelerators enabled", spliced)
        self.assertNotIn("Old foundation mandate v0.0.1", spliced)

        # 2. Contains user mandates byte-for-byte
        self.assertIn("## PROJECT-SPECIFIC MANDATES", spliced)
        self.assertIn("- Cross-Platform Invariant: Custom Windows PowerShell port 8080.", spliced)
        self.assertIn("- Team Mandate: All models must use snake_case JSON serialization.", spliced)

        # 3. Does NOT leak upstream template placeholder text
        self.assertNotIn("<!-- Default empty upstream template instructions -->", spliced)

    def test_missing_marker_raises_error(self):
        broken_bios = "Just random text without delimiters."
        with self.assertRaises(SplicerMarkerMissingError):
            SurgicalBiosSplicer.splice(broken_bios, self.sample_upstream_bios)


class TestTransactionalUpgrader(unittest.TestCase):
    """Verifies staging, check, dry-run, and transactional rollback."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_upgrader_")
        self.spoke_root = Path(self.test_dir) / "spoke"
        self.upstream_root = Path(self.test_dir) / "upstream"

        self.spoke_root.mkdir(parents=True)
        self.upstream_root.mkdir(parents=True)

        # Setup spoke project
        (self.spoke_root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        (self.spoke_root / "context").mkdir()
        (self.spoke_root / "context" / "VISION.md").write_text("# Spoke Sacred Vision\n", encoding="utf-8")

        spoke_agents = self.spoke_root / ".agents"
        spoke_agents.mkdir()
        (spoke_agents / "rules").mkdir()
        (spoke_agents / "rules" / "rule.md").write_text("version: 0.0.1\nold rule content\n", encoding="utf-8")

        # Setup upstream hub
        (self.upstream_root / "VERSION").write_text("0.0.3\n", encoding="utf-8")
        (self.upstream_root / "context").mkdir()
        (self.upstream_root / "context" / "VISION.md").write_text("# Upstream Vision (MUST NOT OVERWRITE)\n", encoding="utf-8")

        upstream_agents = self.upstream_root / ".agents"
        upstream_agents.mkdir()
        (upstream_agents / "rules").mkdir()
        (upstream_agents / "rules" / "rule.md").write_text("version: 0.0.3\nnew upgraded rule content\n", encoding="utf-8")

    def tearDown(self):
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except OSError:
                    pass
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass

    def test_check_respects_shield(self):
        upgrader = TransactionalUpgrader(self.spoke_root)
        res = upgrader.check(str(self.upstream_root))

        self.assertTrue(res["has_updates"])
        self.assertEqual(res["current_version"], "1.0.0")
        self.assertEqual(res["upstream_version"], "0.0.3")

        # rule.md should be in changed files
        self.assertIn(".agents/rules/rule.md", res["changed_files"])

        # Sacred files must NOT be in changed files
        self.assertNotIn("VERSION", res["changed_files"])
        self.assertNotIn("context/VISION.md", res["changed_files"])

    def test_dry_run_leaves_disk_unmodified(self):
        upgrader = TransactionalUpgrader(self.spoke_root)
        res = upgrader.upgrade(str(self.upstream_root), dry_run=True, run_verify=False)

        self.assertEqual(res["status"], "dry_run")
        # Rule file should still have old content
        local_rule = (self.spoke_root / ".agents" / "rules" / "rule.md").read_text(encoding="utf-8")
        self.assertIn("old rule content", local_rule)

    def test_live_upgrade_applies_and_protects_sacred(self):
        upgrader = TransactionalUpgrader(self.spoke_root)
        res = upgrader.upgrade(str(self.upstream_root), dry_run=False, run_verify=False)

        self.assertEqual(res["status"], "success")

        # Rule file upgraded
        local_rule = (self.spoke_root / ".agents" / "rules" / "rule.md").read_text(encoding="utf-8")
        self.assertIn("new upgraded rule content", local_rule)

        # Sacred files untouched
        self.assertEqual((self.spoke_root / "VERSION").read_text(encoding="utf-8").strip(), "1.0.0")
        self.assertEqual((self.spoke_root / "context" / "VISION.md").read_text(encoding="utf-8").strip(), "# Spoke Sacred Vision")


if __name__ == "__main__":
    unittest.main()
