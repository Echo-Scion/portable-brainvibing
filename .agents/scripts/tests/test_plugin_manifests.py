# -*- coding: utf-8 -*-
"""Unit tests for universal multi-IDE deployment engine and platform manifests."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure .agents/scripts is on sys.path
scripts_dir = Path(__file__).resolve().parents[1]
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from core.platform_manifests import (
    PLATFORM_SPECS,
    deploy_all_platform_manifests,
    deploy_platform_manifest,
)


class TestPluginManifests(unittest.TestCase):
    """Verifies 18-platform multi-IDE deployment generator and foundation root cleanliness."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[3]

    def test_platform_specs_coverage(self):
        """Ensure all 18 platforms are supported in the deployment manifest registry."""
        required_platforms = {
            "antigravity",
            "android_studio",
            "claude",
            "cursor",
            "codex_app",
            "codex_cli",
            "devin",
            "gemini",
            "copilot",
            "kimi",
            "hermes",
            "muse",
            "droid",
            "grok",
            "opencode",
            "pi",
            "qwen",
            "minimax",
            "mimo",
        }
        for plat in required_platforms:
            self.assertIn(plat, PLATFORM_SPECS, f"Platform {plat} missing from PLATFORM_SPECS")

    def test_deploy_manifests_to_target_project(self):
        """Ensure generator deploys lightweight, valid manifests (< 15 lines) to target repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            deployed = deploy_all_platform_manifests(temp_dir)
            self.assertGreaterEqual(len(deployed), 15)

            # Validate each deployed file
            for file_path_str in deployed:
                file_path = Path(file_path_str)
                self.assertTrue(file_path.exists(), f"Target manifest missing: {file_path}")

                content = file_path.read_text(encoding="utf-8")
                line_count = len(content.strip().splitlines())
                self.assertLessEqual(
                    line_count,
                    15,
                    f"{file_path.name} exceeds minimal line count limit ({line_count} lines)",
                )

                if file_path.suffix == ".json":
                    data = json.loads(content)
                    self.assertEqual(data.get("name"), "portable-brainvibing")
                    self.assertEqual(data.get("version"), "0.0.2")

    def test_foundation_root_cleanliness(self):
        """Ensure foundation repository root is not polluted by non-active platform folders."""
        forbidden_root_entries = [
            ".claude-plugin",
            ".cursor-plugin",
            ".codex-plugin",
            ".devin-plugin",
            "gemini-extension.json",
            ".kimi-plugin",
            ".hermes-plugin",
            ".muse-plugin",
            ".qwen-plugin",
            ".minimax-plugin",
            ".mimo-plugin",
            ".opencode",
            ".windsurf",
            ".clinerules",
            ".cursor",
        ]
        for entry in forbidden_root_entries:
            path = self.repo_root / entry
            self.assertFalse(
                path.exists(),
                f"Foundation root must not be polluted with {entry}. It belongs only in deployed targets.",
            )

        # Active in foundation: Antigravity plugin manifest
        ag_path = self.repo_root / ".antigravity-plugin/plugin.json"
        self.assertTrue(ag_path.exists(), "Antigravity plugin manifest missing from foundation")

    def test_hook_scripts_exist_and_dispatch(self):
        cmd_hook = self.repo_root / ".agents/hooks/run-hook.cmd"
        sh_hook = self.repo_root / ".agents/hooks/run-hook.sh"

        self.assertTrue(cmd_hook.exists(), "run-hook.cmd missing")
        self.assertTrue(sh_hook.exists(), "run-hook.sh missing")

        cmd_content = cmd_hook.read_text(encoding="utf-8")
        self.assertIn("pre-agent-wake.py", cmd_content)
        self.assertIn("python", cmd_content)

        sh_content = sh_hook.read_text(encoding="utf-8")
        self.assertIn("pre-agent-wake.py", sh_content)

    def test_ai_brands_coverage(self):
        ai_brands_path = self.repo_root / ".agents/canons/global/ai_brands.json"
        self.assertTrue(ai_brands_path.exists(), "ai_brands.json missing")

        with open(ai_brands_path, "r", encoding="utf-8") as f:
            brands = json.load(f)

        brand_keys = set(brands.keys())
        required_brands = {"claude", "copilot", "minimax", "mimo", "codex", "qwen", "devin", "kimi"}
        for rb in required_brands:
            self.assertIn(rb, brand_keys, f"Missing brand config for: {rb}")


if __name__ == "__main__":
    unittest.main()
