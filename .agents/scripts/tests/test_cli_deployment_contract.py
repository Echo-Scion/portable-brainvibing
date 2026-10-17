import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
ORION = SCRIPTS_DIR / "orion.py"
FOUNDATION = SCRIPTS_DIR / "commands" / "foundation.py"


def run_script(script, *args, cwd=None):
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class CliDeploymentContractTests(unittest.TestCase):
    def test_orion_help_lists_unified_commands(self):
        result = run_script(ORION, "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage: python .agents/scripts/orion.py <command> [args...]", result.stdout)
        self.assertIn("foundation", result.stdout)
        self.assertIn("deploy", result.stdout)

    def test_unknown_orion_command_fails_explicitly(self):
        result = run_script(ORION, "missing-command")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip(), "Unknown command: missing-command")
        self.assertEqual(result.stderr, "")

    def test_foundation_help_is_reachable_through_orion(self):
        result = run_script(ORION, "foundation", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Foundation Package & Deployment Manager", result.stdout)
        self.assertIn("deploy", result.stdout)
        self.assertIn("sync-ai", result.stdout)

    def test_brain_export_vault_command_is_reachable(self):
        brain = SCRIPTS_DIR / "commands" / "brain.py"
        result = run_script(brain, "export-vault", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Export Orion graph into an Obsidian vault", result.stdout)

    def test_orion_routes_export_vault_command(self):
        result = run_script(ORION, "brain", "export-vault", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Export Orion graph into an Obsidian vault", result.stdout)

    def test_deploy_dry_run_does_not_create_target_files(self):
        with tempfile.TemporaryDirectory() as target:
            result = run_script(
                ORION,
                "deploy",
                "--target",
                target,
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("SIMULATED", result.stdout)
            agents_dir = Path(target) / ".agents"
            self.assertEqual(list(Path(target).iterdir()), [agents_dir])
            self.assertEqual(list(agents_dir.iterdir()), [])

    def test_sync_ai_dry_run_is_supported_by_foundation_command(self):
        target = SCRIPTS_DIR.parents[1]
        result = run_script(
            FOUNDATION,
            "sync-ai",
            "--target",
            str(target),
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Sync completed (SIMULATED).", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(target, ".agents", ".deployed_ais")))

    def test_sync_ai_dry_run_is_supported_by_orion_compatibility_alias(self):
        target = SCRIPTS_DIR.parents[1]
        result = run_script(
            ORION,
            "sync-ai",
            "--target",
            str(target),
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Sync completed (SIMULATED).", result.stdout)

    def test_top_level_deploy_alias_warns_on_stderr(self):
        with tempfile.TemporaryDirectory() as target:
            result = run_script(
                ORION,
                "deploy",
                "--target",
                target,
                "--dry-run",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr,
            "[DEPRECATION] 'deploy' is deprecated; use 'foundation deploy'.\n",
        )

    def test_top_level_push_upstream_alias_warns_on_stderr(self):
        result = run_script(ORION, "push-upstream", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr,
            "[DEPRECATION] 'push-upstream' is deprecated; "
            "use 'foundation push-upstream'.\n",
        )

    def test_top_level_sync_ai_alias_warns_on_stderr(self):
        target = SCRIPTS_DIR.parents[1]
        result = run_script(
            ORION,
            "sync-ai",
            "--target",
            str(target),
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stderr,
            "[DEPRECATION] 'sync-ai' is deprecated; use 'foundation sync-ai'.\n",
        )

    def test_canonical_foundation_command_has_no_deprecation_warning(self):
        result = run_script(ORION, "foundation", "--help")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_sync_ai_non_dry_run_updates_tracking_file(self):
        with tempfile.TemporaryDirectory() as target:
            agents_dir = Path(target) / ".agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / ".foundation_path").write_text(str(SCRIPTS_DIR.parents[1]), encoding="utf-8")
            result = run_script(
                FOUNDATION,
                "sync-ai",
                "--target",
                str(target),
                "--ai",
                "agents"
            )
            self.assertEqual(result.returncode, 0)
            tracking_file = agents_dir / ".deployed_ais"
            self.assertTrue(tracking_file.is_file())
            import json
            data = json.loads(tracking_file.read_text(encoding="utf-8"))
            self.assertIn("deployed_ais", data)
            self.assertIn("sync_results", data)

    def test_detect_active_ais_smart_defaults_and_markers(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        from commands.foundation import detect_active_ais

        with tempfile.TemporaryDirectory() as target:
            # 1. Clean directory -> defaults strictly to canonical agents + gemini
            detected = detect_active_ais(target)
            self.assertEqual(detected, ["agents", "gemini"])

            # 2. Add Cursor marker -> includes cursor
            (Path(target) / ".cursorrules").write_text("# cursor", encoding="utf-8")
            detected = detect_active_ais(target)
            self.assertIn("cursor", detected)
            self.assertIn("agents", detected)
            self.assertNotIn("windsurf", detected)
            self.assertNotIn("cline", detected)

            # 3. Add Claude marker -> includes claude
            (Path(target) / "CLAUDE.md").write_text("# claude", encoding="utf-8")
            detected = detect_active_ais(target)
            self.assertIn("claude", detected)
            self.assertIn("cursor", detected)
            self.assertNotIn("windsurf", detected)


if __name__ == "__main__":
    unittest.main()
