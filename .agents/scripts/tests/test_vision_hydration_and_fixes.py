import os
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
ORION = SCRIPTS_DIR / "orion.py"
FOUNDATION = SCRIPTS_DIR / "commands" / "foundation.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SCRIPTS_DIR / "commands") not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR / "commands"))


def run_script(script, *args, cwd=None):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class VisionHydrationAndFixesTests(unittest.TestCase):
    def test_setup_pipeline_pillars_map_references_project_scaffold(self):
        """Pillars map in execute_setup_pipeline must reference PROJECT_SCAFFOLD.template.md."""
        with open(FOUNDATION, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('"03_Tech/ARCHITECTURE.md": "PROJECT_SCAFFOLD.template.md"', content)
        self.assertNotIn('"03_Tech/ARCHITECTURE.md": "ARCHITECTURE.template.md"', content)

    def test_git_hooks_use_posix_resilient_python_bin(self):
        """Git pre-commit and post-commit hooks must resolve python3/python dynamically."""
        with open(FOUNDATION, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("PYTHON_BIN=$(command -v python3 || command -v python)", content)
        self.assertNotIn('python -X utf8 .agents/scripts/orion.py scan security', content)

    def test_orion_cli_dispatches_hydrate_vision(self):
        """orion.py hydrate-vision --help must exit 0 and show options."""
        result = run_script(ORION, "hydrate-vision", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("hydrate-vision", result.stdout)
        self.assertIn("--target", result.stdout)
        self.assertIn("--force", result.stdout)

    def test_hydrate_vision_draft_and_confirmation_lifecycle(self):
        """hydrate_vision must produce a draft first, then promote to immutable VISION.md on confirmation."""
        from commands.foundation import hydrate_vision

        with tempfile.TemporaryDirectory() as tmp_dir:
            readme_path = os.path.join(tmp_dir, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# TaskMaster\n\nA local-first, terminal-based personal task manager.\n")

            # Phase 1: Draft generation (unconfirmed)
            res = hydrate_vision(tmp_dir, auto_confirm=False)
            draft_path = os.path.join(tmp_dir, "context", "VISION.draft.md")
            final_path = os.path.join(tmp_dir, "context", "VISION.md")

            self.assertTrue(os.path.isfile(draft_path), "Expected context/VISION.draft.md to be created")
            self.assertFalse(os.path.isfile(final_path), "context/VISION.md should NOT be created before confirmation")

            with open(draft_path, "r", encoding="utf-8") as df:
                draft_content = df.read()

            self.assertIn("# 🌟 FOUNDATIONAL VISION: TaskMaster", draft_content)
            self.assertIn("## 1. Core Essence", draft_content)
            self.assertIn("## 2. Non-Negotiable Invariants", draft_content)
            self.assertIn("## 3. Anti-Vision", draft_content)
            self.assertIn("## 4. The AI \"Improvement\" Filter", draft_content)

            # Phase 2: Confirmation
            res_confirm = hydrate_vision(tmp_dir, auto_confirm=True)
            self.assertTrue(os.path.isfile(final_path), "Expected context/VISION.md to be promoted")

            with open(final_path, "r", encoding="utf-8") as ff:
                final_content = ff.read()

            self.assertIn("ownership: HUMAN_ONLY", final_content)
            self.assertIn("# 🌟 FOUNDATIONAL VISION: TaskMaster", final_content)

    def test_hydrate_vision_preserves_customized_vision_without_force(self):
        """hydrate_vision must not overwrite human-customized VISION.md without --force."""
        from commands.foundation import hydrate_vision

        with tempfile.TemporaryDirectory() as tmp_dir:
            ctx_dir = os.path.join(tmp_dir, "context")
            os.makedirs(ctx_dir, exist_ok=True)
            vision_path = os.path.join(ctx_dir, "VISION.md")
            custom_content = "# 🌟 FOUNDATIONAL VISION: CustomApp\n\nCustom human rules.\n"
            with open(vision_path, "w", encoding="utf-8") as f:
                f.write(custom_content)

            # Attempt hydrate without force
            res = hydrate_vision(tmp_dir, auto_confirm=True, force=False)
            self.assertEqual(res.get("status"), "SKIPPED_EXISTING")

            with open(vision_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), custom_content)


    def test_hydrate_vision_with_creator_statement(self):
        """hydrate_vision must prioritize direct creator statement above fallbacks."""
        from commands.foundation import hydrate_vision

        with tempfile.TemporaryDirectory() as tmp_dir:
            creator_statement = "Ultra-fast P2P file sharing with zero cloud storage and zero telemetry."
            res = hydrate_vision(tmp_dir, statement=creator_statement, auto_confirm=False)

            draft_path = os.path.join(tmp_dir, "context", "VISION.draft.md")
            self.assertTrue(os.path.isfile(draft_path))

            with open(draft_path, "r", encoding="utf-8") as df:
                content = df.read()

            self.assertIn(creator_statement, content)
            self.assertIn("## 1. Core Essence", content)


if __name__ == "__main__":
    unittest.main()
