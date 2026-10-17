import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADVERSARIAL = load_module(
    "adversarial_security_tests",
    SCRIPTS_DIR / "commands" / "verify_agents.py",
)
BRAIN = load_module(
    "brain_security_tests",
    SCRIPTS_DIR / "commands" / "brain.py",
)
RTK = load_module(
    "rtk_security_tests",
    SCRIPTS_DIR / "core" / "capabilities.py",
)
SECRETS = load_module(
    "secrets_security_tests",
    SCRIPTS_DIR / "core" / "security.py",
)
SECRETS_SCAN = load_module(
    "secrets_scan_security_tests",
    SCRIPTS_DIR.parent / "canons" / "global" / "harnesses" / "secrets_scan_verifier.py",
)


class SecurityBoundaryTests(unittest.TestCase):
    def test_command_text_is_split_without_shell_operators(self):
        command = ADVERSARIAL.command_args("python -m unittest && unexpected")

        self.assertEqual(
            command,
            ["python", "-m", "unittest", "&&", "unexpected"],
        )

    def test_rtk_subprocess_disables_shell_execution(self):
        completed = type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()

        with patch.object(RTK.shutil, "which", return_value="rtk"), patch.object(
            RTK.subprocess,
            "run",
            return_value=completed,
        ) as run:
            RTK.main_with_args(["echo", "safe"])

        self.assertEqual(run.call_count, 1)
        self.assertFalse(run.call_args.kwargs["shell"])

    def test_endpoint_policy_accepts_loopback(self):
        self.assertTrue(BRAIN.validate_ollama_url("http://127.0.0.1:11434/api/generate"))
        self.assertTrue(BRAIN.validate_ollama_url("http://[::1]:11434"))
        self.assertTrue(BRAIN.validate_ollama_url("http://localhost:11434"))

    def test_endpoint_policy_rejects_external_and_malformed_urls(self):
        self.assertTrue(BRAIN.validate_ollama_url("http://127.0.0.1:11434"))
        for url in (
            "https://example.com/api/generate",
            "http://192.168.1.20:11434",
            "not-a-url",
            "http://127.0.0.1:11434?redirect=https://example.com",
        ):
            with self.subTest(url=url):
                self.assertFalse(BRAIN.validate_ollama_url(url))

    def test_secret_detector_source_does_not_self_report(self):
        findings = SECRETS_SCAN.scan_file(
            str(SCRIPTS_DIR / "core" / "security.py")
        )

        self.assertEqual(findings, [])

    def test_secret_redactor_wireup(self):
        import sys
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.harness.capture import SecretRedactor
        sanitized = SecretRedactor.redact_text("sk-" + "abcdef1234567890" * 3)
        self.assertNotIn("abcdef1234567890", sanitized)
        self.assertIn("[REDACTED_SECRET]", sanitized)

    def test_reflexion_imports_and_audit(self):
        import sys
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from commands.reflexion import PromptRuleCompiler
        compiler = PromptRuleCompiler()
        report = compiler.audit_rule_enforcement()
        self.assertIn("mechanical_coverage_pct", report)


if __name__ == "__main__":
    unittest.main()
