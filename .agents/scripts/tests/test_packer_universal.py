import os
import sys
import unittest
import tempfile
import shutil

# Ensure .agents/scripts is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from utils.packer import (
    is_foundation_root,
    classify_app_file,
    classify_foundation_file,
    is_audit_worthy,
    ContextPacker,
    DEFAULT_IGNORE_FILENAMES,
    DEFAULT_IGNORE_DIRS,
    export_audit_bundles,
    export_gemini_bundles,
)


class TestUniversalPacker(unittest.TestCase):
    def test_foundation_detection(self):
        # Current repo root is the foundation root
        self.assertTrue(is_foundation_root("."))
        # tools/flutterin is an application subproject
        if os.path.exists("tools/flutterin"):
            self.assertFalse(is_foundation_root("tools/flutterin"))

    def test_classify_app_file(self):
        self.assertEqual(classify_app_file("bin/cli.mjs"), "07_CLI_MCP_AND_TOOLS")
        self.assertEqual(classify_app_file("src/cli/index.ts"), "07_CLI_MCP_AND_TOOLS")
        self.assertEqual(classify_app_file("src/ir/types.ts"), "02_CORE_DOMAIN_AND_TYPES")
        self.assertEqual(classify_app_file("src/models/user.ts"), "02_CORE_DOMAIN_AND_TYPES")
        self.assertEqual(classify_app_file("src/generators/codegen.ts"), "04_TARGETS_AND_GENERATORS")
        self.assertEqual(classify_app_file("src/targets/android/view.ts"), "04_TARGETS_AND_GENERATORS")
        self.assertEqual(classify_app_file("src/services/api.ts"), "03_SERVICES_AND_DATA")
        self.assertEqual(classify_app_file("src/controllers/auth.ts"), "05_STATE_AND_CONTROLLERS")
        self.assertEqual(classify_app_file("src/ui/Button.tsx"), "06_UI_AND_PRESENTATION")
        self.assertEqual(classify_app_file("package.json"), "01_PROJECT_CONFIG_AND_BLUEPRINT")
        self.assertEqual(classify_app_file("context/00_Strategy/BLUEPRINT.md"), "01_PROJECT_CONFIG_AND_BLUEPRINT")
        self.assertEqual(classify_app_file("AGENTS.md"), "08_AGENTIC_AND_GOVERNANCE")
        self.assertEqual(classify_app_file(".agents/rules/core-guardrails.md"), "08_AGENTIC_AND_GOVERNANCE")
        self.assertEqual(classify_app_file("test/unit.test.ts"), "09_TESTS_AND_VERIFICATION")
        self.assertEqual(classify_app_file("examples/sample.json"), "10_DOCS_AND_EXAMPLES")

    def test_ignore_lists(self):
        self.assertIn("package-lock.json", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("yarn.lock", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("pubspec.lock", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("scratch", DEFAULT_IGNORE_DIRS)
        self.assertIn("node_modules", DEFAULT_IGNORE_DIRS)

    def test_is_audit_worthy_lean_vs_all(self):
        # App project lean excludes docs and examples
        self.assertFalse(is_audit_worthy("docs/intro.md", is_foundation=False, mode="lean"))
        self.assertFalse(is_audit_worthy("examples/sample.json", is_foundation=False, mode="lean"))
        self.assertFalse(is_audit_worthy("tests/test_api.py", is_foundation=False, mode="lean"))
        self.assertTrue(is_audit_worthy("src/index.ts", is_foundation=False, mode="lean"))
        self.assertTrue(is_audit_worthy("context/BLUEPRINT.md", is_foundation=False, mode="lean"))

        # App project all includes docs and examples
        self.assertTrue(is_audit_worthy("docs/intro.md", is_foundation=False, mode="all"))
        self.assertTrue(is_audit_worthy("examples/sample.json", is_foundation=False, mode="all"))
        self.assertTrue(is_audit_worthy("tests/test_api.py", is_foundation=False, mode="all"))

    def test_export_gemini_bundles_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock application
            os.makedirs(os.path.join(temp_dir, "src", "core"))
            os.makedirs(os.path.join(temp_dir, "bin"))
            os.makedirs(os.path.join(temp_dir, "scratch"))

            with open(os.path.join(temp_dir, "package.json"), "w") as f:
                f.write('{"name": "mock-app"}')
            with open(os.path.join(temp_dir, "src", "core", "domain.ts"), "w") as f:
                f.write("export interface MockDomain { id: string; }")
            with open(os.path.join(temp_dir, "bin", "cli.ts"), "w") as f:
                f.write("console.log('cli');")
            # This should be ignored by DEFAULT_IGNORE_FILENAMES
            with open(os.path.join(temp_dir, "package-lock.json"), "w") as f:
                f.write('{"lockfileVersion": 3}')
            # This should be ignored by DEFAULT_IGNORE_DIRS
            with open(os.path.join(temp_dir, "scratch", "junk.txt"), "w") as f:
                f.write("junk data")

            out_dir = os.path.join(temp_dir, "export")
            bundles = export_audit_bundles(temp_dir, out_dir=out_dir, num_bundles=10, mode="lean")

            self.assertTrue(len(bundles) >= 2)
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    content = bf.read()
                self.assertNotIn("package-lock.json", content)
                self.assertNotIn("junk.txt", content)
            
            # Verify alias
            self.assertIs(export_gemini_bundles, export_audit_bundles)

    def test_skeletonize_python(self):
        from utils.packer import skeletonize_code
        code = '''import os\n\ndef add(a: int, b: int) -> int:\n    """Adds two integers."""\n    res = a + b\n    return res\n\nclass Calculator:\n    """Simple calc."""\n    def multiply(self, x: int, y: int) -> int:\n        return x * y\n'''
        skel = skeletonize_code(code, "py")
        self.assertIn("def add(a: int, b: int) -> int:", skel)
        self.assertIn("class Calculator:", skel)
        self.assertIn("Simple calc.", skel)
        self.assertIn("[Body omitted for audit", skel)
        self.assertNotIn("res = a + b", skel)

    def test_skeletonize_c_like(self):
        from utils.packer import skeletonize_code
        ts_code = 'export interface User { id: string; }\nexport class ApiService {\n    async getData() {\n        return await fetch("/api");\n    }\n}'
        skel = skeletonize_code(ts_code, "ts")
        self.assertIn("export interface User", skel)
        self.assertIn("export class ApiService", skel)
        self.assertIn("[Implementation omitted for audit]", skel)

    def test_add_line_numbers_and_dynamic_fence(self):
        from utils.packer import add_line_numbers, get_dynamic_fence
        content = "line one\nline two\nline three"
        numbered = add_line_numbers(content)
        self.assertIn("  1 | line one", numbered)
        self.assertIn("  2 | line two", numbered)
        self.assertIn("  3 | line three", numbered)

        # Dynamic fence check
        fence = get_dynamic_fence("regular code")
        self.assertEqual(fence, "```")
        nested_fence = get_dynamic_fence("nested ``` markdown")
        self.assertEqual(nested_fence, "````")

    def test_calculate_token_stats(self):
        from utils.packer import calculate_token_stats
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "test.py"), "w", encoding="utf-8") as f:
                f.write("print('hello world')\n")
            with open(os.path.join(temp_dir, "doc.md"), "w", encoding="utf-8") as f:
                f.write("# Title\n")
            stats = calculate_token_stats(temp_dir, ["test.py", "doc.md"])
            self.assertEqual(stats["total_files"], 2)
            self.assertIn(".py", stats["by_extension"])
            self.assertIn(".md", stats["by_extension"])
            self.assertTrue(stats["total_tokens"] > 0)

    def test_render_prompt_template(self):
        from utils.packer import render_prompt_template
        ctx = {"repo_name": "test_repo", "file_count": 5, "token_count": 100, "tree": "src/", "files": "dummy files"}
        rendered = render_prompt_template("audit", ctx)
        self.assertIn("SYSTEM ARCHITECTURE & SECURITY AUDIT PROMPT", rendered)
        self.assertIn("Repository: test_repo", rendered)
        self.assertIn("dummy files", rendered)

    def test_pack_claude_xml(self):
        from utils.packer import ContextPacker
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "test.py"), "w", encoding="utf-8") as f:
                f.write("x = 42\n")
            packer = ContextPacker(temp_dir)
            xml = packer.pack_claude_xml(["test.py"], line_numbers=True)
            self.assertIn("<documents>", xml)
            self.assertIn('<document index="1">', xml)
            self.assertIn("<source>test.py</source>", xml)
            self.assertIn("  1 | x = 42", xml)
            self.assertIn("</documents>", xml)

    def test_vibe_intent_audit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write("def run():\n    pass\n")
            out_dir = os.path.join(temp_dir, "audit_out")
            bundles = export_audit_bundles(temp_dir, out_dir=out_dir, skeleton=True, line_numbers=True)
            self.assertTrue(len(bundles) >= 1)
            with open(bundles[0], "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("def run():", content)

    def test_audit_full_vs_skeleton_vs_hybrid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            core_dir = os.path.join(temp_dir, "core")
            cli_dir = os.path.join(temp_dir, "cli")
            os.makedirs(core_dir, exist_ok=True)
            os.makedirs(cli_dir, exist_ok=True)

            with open(os.path.join(core_dir, "models.py"), "w", encoding="utf-8") as f:
                f.write("def calculate_total(a, b):\n    result = a + b\n    return result\n")
            with open(os.path.join(cli_dir, "commands.py"), "w", encoding="utf-8") as f:
                f.write("def cli_entrypoint():\n    print('CLI running')\n    sys.exit(0)\n")

            # 1. Full Audit (default): bodies are 100% preserved
            out_full = os.path.join(temp_dir, "out_full")
            bundles_full = export_audit_bundles(temp_dir, out_dir=out_full, skeleton=False, line_numbers=True)
            full_texts = []
            for b in bundles_full:
                with open(b, "r", encoding="utf-8") as f:
                    full_texts.append(f.read())
            combined_full = "\n".join(full_texts)
            self.assertIn("result = a + b", combined_full)
            self.assertIn("print('CLI running')", combined_full)
            self.assertNotIn("[Body omitted for audit", combined_full)

            # 2. Skeleton Audit: bodies are collapsed into signatures
            out_skel = os.path.join(temp_dir, "out_skel")
            bundles_skel = export_audit_bundles(temp_dir, out_dir=out_skel, skeleton=True, line_numbers=True)
            skel_texts = []
            for b in bundles_skel:
                with open(b, "r", encoding="utf-8") as f:
                    skel_texts.append(f.read())
            combined_skel = "\n".join(skel_texts)
            self.assertIn("[Body omitted for audit", combined_skel)

            # 3. Hybrid Audit: Core domain full, secondary tools skeletonized
            out_hybrid = os.path.join(temp_dir, "out_hybrid")
            bundles_hybrid = export_audit_bundles(temp_dir, out_dir=out_hybrid, skeleton=False, line_numbers=True, hybrid=True)
            hybrid_texts = {}
            for b in bundles_hybrid:
                with open(b, "r", encoding="utf-8") as f:
                    hybrid_texts[os.path.basename(b)] = f.read()
            # Find bundle containing core models vs CLI
            core_bundle = next((v for k, v in hybrid_texts.items() if "02_CORE_DOMAIN" in k or "models.py" in v), "")
            cli_bundle = next((v for k, v in hybrid_texts.items() if "07_CLI" in k or "commands.py" in v), "")
            self.assertIn("result = a + b", core_bundle)
            self.assertIn("[Body omitted for audit", cli_bundle)


if __name__ == "__main__":
    unittest.main()


