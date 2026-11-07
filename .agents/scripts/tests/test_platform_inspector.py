# -*- coding: utf-8 -*-
"""Unit tests for platform_inspector.py and orion env command."""

import json
import os
import sys
import unittest
from pathlib import Path

# Add .agents/scripts to sys.path
scripts_dir = Path(__file__).resolve().parents[1]
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from core.platform_inspector import (
    detect_host_platform,
    get_environment_summary,
    format_markdown_report,
    get_jit_recommendation,
    PLATFORM_CAPABILITIES
)


class TestPlatformInspector(unittest.TestCase):
    def test_platform_capabilities_coverage(self):
        self.assertIn("antigravity", PLATFORM_CAPABILITIES)
        self.assertIn("claude", PLATFORM_CAPABILITIES)
        self.assertIn("cursor", PLATFORM_CAPABILITIES)
        self.assertIn("generic", PLATFORM_CAPABILITIES)

        ag = PLATFORM_CAPABILITIES["antigravity"]
        slash_cmd_names = [c["command"] for c in ag["slash_commands"]]
        self.assertIn("/plan", slash_cmd_names)
        self.assertIn("/grill-me", slash_cmd_names)
        self.assertIn("/teamwork", slash_cmd_names)
        self.assertIn("/boost", slash_cmd_names)

    def test_detect_host_platform(self):
        # Under Antigravity environment
        platform_key = detect_host_platform()
        self.assertIn(platform_key, ["antigravity", "claude", "cursor", "generic"])

    def test_get_environment_summary(self):
        summary = get_environment_summary()
        self.assertIn("host_platform_name", summary)
        self.assertIn("os", summary)
        self.assertIn("python", summary)
        self.assertIn("slash_commands", summary)
        self.assertIn("native_tools", summary)

    def test_format_markdown_report(self):
        summary = get_environment_summary()
        report = format_markdown_report(summary)
        self.assertIn("# 🌐 Host Platform & Environment Capabilities", report)
        self.assertIn("Slash Command", report)

    def test_get_jit_recommendation(self):
        self.assertEqual(get_jit_recommendation("I want to refactor the architecture"), "Recommend `/plan` before execution.")
        self.assertEqual(get_jit_recommendation("Which database option should we choose?"), "Recommend `/grill-me` to interview design decisions.")
        self.assertEqual(get_jit_recommendation("Coordinate a multi-agent team on parallel tasks"), "Recommend `/teamwork` for multi-agent delegation.")
        self.assertEqual(get_jit_recommendation("There is a hard bug deep in the math algorithm"), "Recommend `/boost` for maximum reasoning effort.")
        self.assertEqual(get_jit_recommendation("Simple readme edit"), "None")


if __name__ == "__main__":
    unittest.main()
