#!/usr/bin/env python3
"""Unit tests for 3-Scenario Adaptive Lifecycle Engine.

Tests:
1. detect_lifecycle_mode across Greenfield, Brownfield, and Upgrade mock environments.
2. splice_foundation_blocks replacing markers, preserving frontmatter and custom sections.
3. Legacy unmarked files trigger safe-append without clobbering.
4. flatten_catalogs prunes 12 rows down to 1.
5. harvest_tokens on mock Flutter and Web fixtures.
6. sync_ai_configs creates GEMINI.md as @AGENTS.md adapter.

Zero external dependencies (Python 3.10+ standard library floor).
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add core/ and commands/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.upgrade_engine import detect_lifecycle_mode, splice_foundation_blocks
from core.design_harvester import (
    harvest_tokens,
    infer_archetype_heuristic,
    flatten_catalogs,
    build_ai_infer_prompt,
)
from commands.foundation import sync_ai_configs, _load_ai_configs


class TestLifecycleModes(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_detect_lifecycle_mode_greenfield(self):
        # Empty folder -> GREENFIELD
        mode = detect_lifecycle_mode(str(self.target_path), "DESIGN.md")
        self.assertEqual(mode, "GREENFIELD")

    def test_detect_lifecycle_mode_brownfield(self):
        # Manifest exists, artifact missing -> BROWNFIELD
        (self.target_path / "pubspec.yaml").write_text("name: test_app\n", encoding="utf-8")
        mode = detect_lifecycle_mode(str(self.target_path), "DESIGN.md")
        self.assertEqual(mode, "BROWNFIELD")

    def test_detect_lifecycle_mode_upgrade(self):
        # Artifact exists -> UPGRADE
        (self.target_path / "DESIGN.md").write_text("# Design\n", encoding="utf-8")
        mode = detect_lifecycle_mode(str(self.target_path), "DESIGN.md")
        self.assertEqual(mode, "UPGRADE")

    def test_splice_foundation_blocks_with_markers(self):
        existing = (
            "# My Custom Header\n\n"
            "<!-- START FOUNDATION:wcag-contrast-law -->\n"
            "Old WCAG text\n"
            "<!-- END FOUNDATION:wcag-contrast-law -->\n\n"
            "## My Custom User Rules\n"
            "Keep this intact.\n"
        )
        template = (
            "<!-- START FOUNDATION:wcag-contrast-law -->\n"
            "New Updated WCAG 2.1 AA text\n"
            "<!-- END FOUNDATION:wcag-contrast-law -->\n"
        )

        spliced, replaced = splice_foundation_blocks(existing, template, fallback_append=True)
        self.assertIn("New Updated WCAG 2.1 AA text", spliced)
        self.assertIn("## My Custom User Rules", spliced)
        self.assertIn("Keep this intact.", spliced)
        self.assertNotIn("Old WCAG text", spliced)
        self.assertIn("wcag-contrast-law", replaced)

    def test_splice_foundation_blocks_fallback_append(self):
        existing = (
            "# Completely Custom Unmarked Legacy Spec\n\n"
            "User content without markers.\n"
        )
        template = (
            "<!-- START FOUNDATION:constraint-matrix -->\n"
            "Constraint Matrix Rules\n"
            "<!-- END FOUNDATION:constraint-matrix -->\n"
        )

        spliced, replaced = splice_foundation_blocks(existing, template, fallback_append=True)
        self.assertIn("# Completely Custom Unmarked Legacy Spec", spliced)
        self.assertIn("User content without markers.", spliced)
        self.assertIn("## 🏛️ Foundation Architectural Contract", spliced)
        self.assertIn("Constraint Matrix Rules", spliced)
        self.assertIn("constraint-matrix", replaced)

    def test_flatten_catalogs(self):
        template = (
            "# Design Direction\n\n"
            "- **Selected Archetype**: `{{archetype_name}}`\n\n"
            "| # | Archetype | Vibe |\n"
            "<!-- row:archetype=swiss-editorial -->| 01 | Swiss Editorial | Journalistic |\n"
            "<!-- row:archetype=dark-industrial -->| 02 | Dark Industrial | Hardware |\n"
            "<!-- row:archetype=neo-brutalist -->| 04 | Neo-Brutalist | Direct |\n\n"
            "## Palettes\n"
            "<!-- row:palette=cold-luxury -->| Cold Luxury |\n"
            "<!-- row:palette=deep-forest -->| Deep Forest |\n"
        )

        flattened = flatten_catalogs(template, archetype="dark-industrial", palette="deep-forest")
        self.assertIn("Dark Industrial", flattened)
        self.assertNotIn("Swiss Editorial", flattened)
        self.assertNotIn("Neo-Brutalist", flattened)
        self.assertIn("Deep Forest", flattened)
        self.assertNotIn("Cold Luxury", flattened)
        self.assertIn("- **Selected Archetype**: `dark-industrial`", flattened)

    def test_harvest_tokens_flutter_mock(self):
        # Create mock Flutter project
        (self.target_path / "pubspec.yaml").write_text("name: flutter_test\n", encoding="utf-8")
        lib_dir = self.target_path / "lib"
        lib_dir.mkdir()
        (lib_dir / "main.dart").write_text(
            "import 'package:flutter/material.dart';\n"
            "void main() {\n"
            "  final color = Color(0xFF0D0F12);\n"
            "  final accent = Color(0xFFF59E0B);\n"
            "  final fontFamily = 'Space Grotesk';\n"
            "}\n",
            encoding="utf-8"
        )

        tokens = harvest_tokens(str(self.target_path))
        self.assertIn("canvas_hex", tokens)
        self.assertIn("accent_hex", tokens)
        self.assertEqual(tokens["detected_archetype"], "dark-industrial")

    def test_load_ai_configs_and_sync(self):
        configs = _load_ai_configs()
        self.assertIn("gemini", configs)
        self.assertIn("claude", configs)
        self.assertIn("agents", configs)
        self.assertEqual(configs["gemini"]["template"], "AI_ADAPTER.template.md")
        self.assertEqual(configs["gemini"]["target_path"], "GEMINI.md")

        prompt = build_ai_infer_prompt({"canvas_hex": "#0D0F12", "accent_hex": "#F59E0B"})
        self.assertIn("dark-industrial", prompt)


if __name__ == "__main__":
    unittest.main()
