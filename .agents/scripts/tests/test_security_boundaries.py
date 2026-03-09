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

    def test_ast_security_catches_aliased_and_from_imports(self):
        import sys, tempfile, os
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.security import SecurityAuditor
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, "snippet.py")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("import os as my_os\nfrom os import system as sys_call\nmy_os.system('ls')\nsys_call('ls')\n")
            auditor = SecurityAuditor(td)
            findings = auditor.scan_file(fpath)
            cats = [f["category"] for f in findings]
            self.assertEqual(cats.count("AST_COMMAND_INJECTION"), 2)

    def test_sandbox_blocks_unsupported_extensions(self):
        import sys
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.sandbox import SovereignSandbox
        code, stdout, stderr = SovereignSandbox.execute_snippet("echo 1", extension=".exe")
        self.assertEqual(code, 126)
        self.assertIn("[SANDBOX BLOCKED]", stderr)

    def test_sql_taint_and_constant_folding(self):
        import sys, tempfile, os
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.security import SecurityAuditor
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, "sql_checks.py")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(
                    "# False positive cases\n"
                    "def run_tasks(runner, id):\n"
                    "    runner.execute(f'task_{id}')\n"
                    "    task_name = 'abc'\n"
                    "    runner.execute(task_name)\n"
                    "\n"
                    "def run_const_sql(cursor):\n"
                    "    cursor.execute('SELECT ' + '1')\n"
                    "\n"
                    "# True positive case\n"
                    "def run_injected_sql(cursor, user_id):\n"
                    "    query = 'SELECT * FROM users WHERE id = ' + user_id\n"
                    "    cursor.execute(query)\n"
                )
            auditor = SecurityAuditor(td)
            findings = auditor.scan_file(fpath)
            sql_findings = [f for f in findings if f["category"] == "AST_SQL_INJECTION"]
            self.assertEqual(len(sql_findings), 1)
            self.assertEqual(sql_findings[0]["line"], 13)

    def test_unicode_trojan_ignores_bom(self):
        import sys, tempfile, os
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.security import scan_unicode_trojan
        with tempfile.TemporaryDirectory() as td:
            bom_file = os.path.join(td, "bom.py")
            with open(bom_file, "w", encoding="utf-8") as f:
                f.write("\ufeff# Valid python with BOM\nx = 1\n")
            bom_findings = scan_unicode_trojan(bom_file)
            self.assertEqual(bom_findings, [])

            trojan_file = os.path.join(td, "trojan.py")
            with open(trojan_file, "w", encoding="utf-8") as f:
                f.write("admin = False # \u202e if admin: pass\n")
            trojan_findings = scan_unicode_trojan(trojan_file)
            self.assertEqual(len(trojan_findings), 1)
            self.assertIn("BiDi Trojan override", trojan_findings[0])

            from core.security import SecurityAuditor
            auditor = SecurityAuditor(td)
            auditor_bom_findings = [f for f in auditor.scan_file(bom_file) if f["category"] == "TROJAN_UNICODE"]
            self.assertEqual(auditor_bom_findings, [])

    def test_semgrep_multiline_block_scalar(self):
        import sys
        if str(SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPTS_DIR))
        from core.security import AstRuleCompiler
        yaml_snippet = (
            "rules:\n"
            "  - id: sample-multiline-rule\n"
            "    languages: [python]\n"
            "    message: Disallow multiline pattern\n"
            "    severity: ERROR\n"
            "    pattern: |\n"
            "      def dangerous_func():\n"
            "          evil_call()\n"
        )
        res = AstRuleCompiler.parse_semgrep_string(yaml_snippet)
        rules = res.get("rules", []) if isinstance(res, dict) else res
        self.assertTrue(len(rules) >= 1)
        target = rules[0]
        self.assertEqual(target.get("id"), "sample-multiline-rule")
        pattern = target.get("pattern", "")
        self.assertIn("def dangerous_func():", pattern)
        self.assertIn("evil_call()", pattern)

    def test_sql_taint_conditional_branching(self):
        """F-06: Taint should not be discarded across conditional branches."""
        import tempfile, os
        from core.security import SecurityAuditor
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, "handler.py")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(
                    "def query_handler(user_input, flag, cursor):\n"
                    "    target = user_input\n"
                    "    if flag:\n"
                    "        target = 'safe_literal'\n"
                    "    query = 'SELECT * FROM users WHERE id = ' + target\n"
                    "    cursor.execute(query)\n"
                )
            auditor = SecurityAuditor(td)
            findings = auditor.scan_file(fpath)
            sql_findings = [f for f in findings if f["category"] == "AST_SQL_INJECTION"]
            self.assertTrue(len(sql_findings) >= 1)

    def test_subprocess_shell_wrapper_taint(self):
        """F-06: Subprocess shell wrappers ('sh', '-c', tainted) detected."""
        import tempfile, os
        from core.security import SecurityAuditor
        with tempfile.TemporaryDirectory() as td:
            fpath = os.path.join(td, "runner.py")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(
                    "import subprocess\n"
                    "def run_user_cmd(cmd):\n"
                    "    subprocess.run(['sh', '-c', cmd])\n"
                )
            auditor = SecurityAuditor(td)
            findings = auditor.scan_file(fpath)
            cmd_findings = [f for f in findings if f["category"] == "AST_COMMAND_INJECTION"]
            self.assertTrue(len(cmd_findings) >= 1)

    def test_semgrep_zero_pip_nested_lists(self):
        """F-08: Zero-Pip parser correctly parses nested yaml lists."""
        from core.security import AstRuleCompiler
        yaml_snippet = (
            "rules:\n"
            "  - id: rule-nested-test\n"
            "    languages:\n"
            "      - python\n"
            "      - javascript\n"
            "    message: Test message\n"
            "    severity: WARNING\n"
            "    pattern: dangerous()\n"
        )
        res = AstRuleCompiler.parse_semgrep_string(yaml_snippet)
        rules = res.get("rules", []) if isinstance(res, dict) else res
        self.assertTrue(len(rules) >= 1)
        self.assertIn("python", rules[0].get("languages", []))
        self.assertIn("javascript", rules[0].get("languages", []))


if __name__ == "__main__":
    unittest.main()

