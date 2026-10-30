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
    compute_file_gravity_and_cluster,
    is_audit_worthy,
    ContextPacker,
    DEFAULT_IGNORE_FILENAMES,
    DEFAULT_IGNORE_DIRS,
    export_audit_bundles,
)


class TestUniversalPacker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["ORION_OFFLINE_PACK"] = "1"

    def test_foundation_detection(self):
        # Current repo root is the foundation root (if running in _foundation) or app workspace
        if os.path.exists("src") or os.path.exists("lib"):
            self.assertFalse(is_foundation_root("."))
        else:
            self.assertTrue(is_foundation_root("."))
        # tools/flutterin is an application subproject
        if os.path.exists("tools/flutterin"):
            self.assertFalse(is_foundation_root("tools/flutterin"))

    def test_classify_app_file(self):
        self.assertEqual(compute_file_gravity_and_cluster("bin/cli.mjs")[0], 8)
        self.assertEqual(compute_file_gravity_and_cluster("src/ir/types.ts")[0], 1)
        self.assertEqual(compute_file_gravity_and_cluster("src/models/user.ts")[0], 1)
        self.assertEqual(compute_file_gravity_and_cluster("src/generators/codegen.ts")[0], 5)
        self.assertEqual(compute_file_gravity_and_cluster("src/services/api.ts")[0], 6)
        self.assertEqual(compute_file_gravity_and_cluster("src/controllers/auth.ts")[0], 6)
        self.assertEqual(compute_file_gravity_and_cluster("src/ui/Button.tsx")[0], 7)
        self.assertEqual(compute_file_gravity_and_cluster("package.json")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster("context/00_Strategy/BLUEPRINT.md")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster("AGENTS.md")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/rules/security-guardrails.md")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster("test/unit.test.ts")[0], 9)

    def test_ignore_lists(self):
        self.assertIn("package-lock.json", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("yarn.lock", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("pubspec.lock", DEFAULT_IGNORE_FILENAMES)
        self.assertIn("scratch", DEFAULT_IGNORE_DIRS)
        self.assertIn("node_modules", DEFAULT_IGNORE_DIRS)

    def test_is_audit_worthy_lean_vs_all(self):
        # App project lean excludes docs and examples
        self.assertFalse(is_audit_worthy("docs/intro.md", mode="lean"))
        self.assertFalse(is_audit_worthy("examples/sample.json", mode="lean"))
        self.assertFalse(is_audit_worthy("tests/test_api.py", mode="lean"))
        self.assertTrue(is_audit_worthy("src/index.ts", mode="lean"))
        self.assertTrue(is_audit_worthy("context/BLUEPRINT.md", mode="lean"))

        # App project all includes docs and examples
        self.assertTrue(is_audit_worthy("docs/intro.md", mode="all"))
        self.assertTrue(is_audit_worthy("examples/sample.json", mode="all"))
        self.assertTrue(is_audit_worthy("tests/test_api.py", mode="all"))

    def test_export_audit_bundles_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock application
            os.makedirs(os.path.join(temp_dir, "src", "core"))
            os.makedirs(os.path.join(temp_dir, "bin"))
            os.makedirs(os.path.join(temp_dir, "scratch"))

            with open(os.path.join(temp_dir, "package.json"), "w", encoding="utf-8") as f:
                f.write('{"name": "mock-app"}')
            with open(os.path.join(temp_dir, "src", "core", "domain.ts"), "w", encoding="utf-8") as f:
                f.write("export interface MockDomain { id: string; }")
            with open(os.path.join(temp_dir, "bin", "cli.ts"), "w", encoding="utf-8") as f:
                f.write("console.log('cli');")
            # This should be ignored by DEFAULT_IGNORE_FILENAMES
            with open(os.path.join(temp_dir, "package-lock.json"), "w", encoding="utf-8") as f:
                f.write('{"lockfileVersion": 3}')
            # This should be ignored by DEFAULT_IGNORE_DIRS
            with open(os.path.join(temp_dir, "scratch", "junk.txt"), "w", encoding="utf-8") as f:
                f.write("junk data")

            out_dir = os.path.join(temp_dir, "export")
            bundles = export_audit_bundles(temp_dir, out_dir=out_dir, num_bundles=10, mode="lean")

            self.assertTrue(len(bundles) >= 2)
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    content = bf.read()
                self.assertNotIn("package-lock.json", content)
                self.assertNotIn("junk.txt", content)

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

            # 3. Hybrid Audit: Core execution bundles (01-07) full, governance/docs (08-10) condensed
            out_hybrid = os.path.join(temp_dir, "out_hybrid")
            bundles_hybrid = export_audit_bundles(temp_dir, out_dir=out_hybrid, skeleton=False, line_numbers=True, hybrid=True)
            hybrid_texts = {}
            for b in bundles_hybrid:
                with open(b, "r", encoding="utf-8") as f:
                    hybrid_texts[os.path.basename(b)] = f.read()
            core_bundle = next((v for k, v in hybrid_texts.items() if 'path="core/models.py"' in v or "CORE" in k), "")
            cli_bundle = next((v for k, v in hybrid_texts.items() if 'path="cli/commands.py"' in v or "CLI" in k), "")
            self.assertIn("result = a + b", core_bundle)
            self.assertIn("print('CLI running')", cli_bundle)

    def test_skeleton_syntax_validity_py_compile(self):
        """TEST-01: Skeleton of try/except and long variables compiles without SyntaxError."""
        import py_compile
        from core.scanner import skeletonize_python
        code = '''
import os
import sys

try:
    from core.security import sanitize_text, SECRET_PATTERNS
except ImportError:
    try:
        from .security import sanitize_text, SECRET_PATTERNS
    except Exception:
        SECRET_PATTERNS = [
            ("KEY_1", "val1"),
            ("KEY_2", "val2"),
            ("KEY_3", "val3"),
            ("KEY_4", "val4"),
            ("KEY_5", "val5"),
            ("KEY_6", "val6"),
        ]

LONG_CONFIG = {
    "key1": "val1",
    "key2": "val2",
    "key3": "val3",
    "key4": "val4",
    "key5": "val5",
    "key6": "val6",
}

class SampleService:
    """Service docstring."""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE
            )
        """)

    def run(self, flag: bool = True):
        # Implementation to omit
        x = 100
        return x * 2
'''
        skel = skeletonize_python(code, include_line_numbers=False)
        self.assertIn("self.db_path = db_path", skel)
        self.assertIn("CREATE TABLE IF NOT EXISTS users", skel)
        self.assertIn("SQL: CREATE users", skel)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(skel)
            tf_name = tf.name
        try:
            py_compile.compile(tf_name, doraise=True)
        finally:
            if os.path.exists(tf_name):
                os.remove(tf_name)

    def test_source_true_line_numbers(self):
        """TEST-02: Skeletonized code retains true original line numbers (deviation 0)."""
        from core.scanner import skeletonize_python
        code = "import os\n\n\ndef add(a, b):\n    return a + b\n\n\nclass Calc:\n    def mul(self, a, b):\n        return a * b\n"
        skel = skeletonize_python(code, include_line_numbers=True)
        lines = skel.splitlines()
        
        # Line 4 should be def add
        add_line = next((l for l in lines if "def add(a, b):" in l), "")
        self.assertTrue(add_line.startswith("   4 | "))

        # Line 8 should be class Calc:
        calc_line = next((l for l in lines if "class Calc:" in l), "")
        self.assertTrue(calc_line.startswith("   8 | "))

    def test_foundation_bundle_07_and_09_routing(self):
        """TEST-03: Route memory.py, reflexion.py, and state_machine.py to grav 4, foundation.py to grav 8, db.py to grav 2."""
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/core/memory.py")[0], 4)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/core/orion_graph.py")[0], 4)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/commands/reflexion.py")[0], 4)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/commands/state_machine.py")[0], 4)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/commands/foundation.py")[0], 8)
        self.assertEqual(compute_file_gravity_and_cluster(".agents/scripts/core/db.py")[0], 2)

    def test_cmd_extension_included(self):
        """TEST-04: .cmd extension included in DEFAULT_TEXT_EXTENSIONS."""
        from utils.packer import DEFAULT_TEXT_EXTENSIONS
        self.assertIn(".cmd", DEFAULT_TEXT_EXTENSIONS)

    def test_bundle_file_inventory_table(self):
        """TEST-05: pack_digest generates Bundle File Inventory, <artifact> envelopes, and Auditor Sandbox rule."""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "alpha.py"), "w", encoding="utf-8") as f:
                f.write("def alpha():\n    pass\n")
            with open(os.path.join(td, "beta.ts"), "w", encoding="utf-8") as f:
                f.write("export const beta = 10;\n")
            packer = ContextPacker(td)
            digest = packer.pack_digest(["alpha.py", "beta.ts"], bundle_name="TEST_BUNDLE")
            self.assertIn("## Bundle File Inventory", digest)
            self.assertIn("| 1 | `alpha.py` |", digest)
            self.assertIn("| 2 | `beta.ts` |", digest)
            self.assertIn("- Domain Bundle: TEST_BUNDLE", digest)
            self.assertIn("[AUDITOR SANDBOX RULE]", digest)
            self.assertIn('<artifact index="1" path="alpha.py"', digest)
            self.assertIn("</artifact>", digest)

    def test_directive_quarantine_and_pre_audit_radar(self):
        """TEST-06: Neutralizes prompt tags (<system-instruction>, <route>) and emits Pre-Computed Static Audit Radar."""
        from utils.packer import neutralize_prompt_tags, generate_bundle_pre_audit_radar
        raw = "Hello <system-instruction>hijack</system-instruction> and <route>target</route>"
        cleaned = neutralize_prompt_tags(raw)
        self.assertIn("&lt;system-instruction&gt;", cleaned)
        self.assertIn("&lt;/system-instruction&gt;", cleaned)
        self.assertIn("&lt;route&gt;", cleaned)

        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "risky.py")
            with open(py_file, "w", encoding="utf-8") as fh:
                fh.write("import subprocess\ndef run_cmd():\n    try:\n        subprocess.run(['ls'])\n    except Exception:\n        pass\n")
            radar = generate_bundle_pre_audit_radar(td, ["risky.py"])
            self.assertIn("Pre-Computed Static Audit Radar", radar)
            self.assertIn("subprocess.run()", radar)
            self.assertIn("except Exception:", radar)

    def test_tier_output_subfolders_isolation(self):
        """TEST-07: Verifies that Tier 1 (arch), Tier 2 (hybrid), and Tier 3 (full) default to distinct subfolders."""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "main.py"), "w", encoding="utf-8") as fh:
                fh.write("def calculate(x):\n    return x * 2\n")

            # 1. Tier 1: Arch
            arch_bundles = export_audit_bundles(td, out_dir=None, skeleton=True, hybrid=False, mode="lean")
            self.assertTrue(len(arch_bundles) >= 1)
            self.assertTrue(any(os.path.normpath(".orion/bundles/arch") in os.path.normpath(b) for b in arch_bundles))

            # 2. Tier 2: Hybrid
            hybrid_bundles = export_audit_bundles(td, out_dir=None, skeleton=False, hybrid=True, mode="lean")
            self.assertTrue(len(hybrid_bundles) >= 1)
            self.assertTrue(any(os.path.normpath(".orion/bundles/hybrid") in os.path.normpath(b) for b in hybrid_bundles))

            # 3. Tier 3: Full
            full_bundles = export_audit_bundles(td, out_dir=None, skeleton=False, hybrid=False, mode="all")
            self.assertTrue(len(full_bundles) >= 1)
            self.assertTrue(any(os.path.normpath(".orion/bundles/full") in os.path.normpath(b) for b in full_bundles))

            # Verify all three subdirectories coexist simultaneously
            arch_dir = os.path.join(td, ".orion", "bundles", "arch")
            hybrid_dir = os.path.join(td, ".orion", "bundles", "hybrid")
            full_dir = os.path.join(td, ".orion", "bundles", "full")
            self.assertTrue(os.path.isdir(arch_dir))
            self.assertTrue(os.path.isdir(hybrid_dir))
            self.assertTrue(os.path.isdir(full_dir))

    def test_markdown_line_numbers_in_skeleton(self):
        """TEST-08: skeletonize_markdown retains 1-indexed line numbers when requested."""
        from core.scanner import skeletonize_markdown
        md = "# Heading 1\n\nSome paragraph text that is long.\n\n## Heading 2\n\n- Item 1\n- Item 2\n"
        skel = skeletonize_markdown(md, include_line_numbers=True)
        self.assertIn("   1 | # Heading 1", skel)
        self.assertIn("   5 | ## Heading 2", skel)

    def test_gitignore_dir_only_direct_file_match(self):
        """TEST-09: GitIgnoreFilter matches direct files inside dir_only ignore patterns."""
        from utils.packer import GitIgnoreFilter
        with tempfile.TemporaryDirectory() as td:
            gi_path = os.path.join(td, ".gitignore")
            with open(gi_path, "w", encoding="utf-8") as f:
                f.write("build/\n.gradle/\n!/.agents/\n")
            gif = GitIgnoreFilter(td, exclude_agent_tooling=False)
            self.assertTrue(gif.is_ignored("build/output.apk", is_dir=False))
            self.assertTrue(gif.is_ignored("android/build/intermediates/res.xml", is_dir=False))
            self.assertTrue(gif.is_ignored(".gradle/caches/file.bin", is_dir=False))
            self.assertFalse(gif.is_ignored(".agents/rules/security-guardrails.md", is_dir=False))

    def test_detect_project_dna(self):
        """TEST-10: detect_project_dna accurately identifies an app with .agents DNA and active native roots."""
        import json
        from utils.packer import detect_project_dna
        with tempfile.TemporaryDirectory() as td:
            # Not an app, empty dir
            self.assertIsNone(detect_project_dna(td))

            # Scaffold mock DNA app
            agents_dir = os.path.join(td, ".agents")
            context_tech = os.path.join(td, "context", "03_Tech")
            android_src = os.path.join(td, "android", "app", "src", "main", "kotlin", "com", "app")
            ios_runner = os.path.join(td, "ios", "Runner")
            os.makedirs(agents_dir, exist_ok=True)
            os.makedirs(context_tech, exist_ok=True)
            os.makedirs(android_src, exist_ok=True)
            os.makedirs(ios_runner, exist_ok=True)

            with open(os.path.join(context_tech, "ARCHITECTURE.md"), "w", encoding="utf-8") as f:
                f.write("# Architecture\n")
            with open(os.path.join(td, "pubspec.yaml"), "w", encoding="utf-8") as f:
                f.write("name: mock_flutter_app\n")
            with open(os.path.join(agents_dir, ".project_manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"framework": "flutter", "language": "dart"}, f)
            with open(os.path.join(android_src, "MainActivity.kt"), "w", encoding="utf-8") as f:
                f.write("class MainActivity\n")
            with open(os.path.join(android_src, "AppService.kt"), "w", encoding="utf-8") as f:
                f.write("class AppService\n")
            with open(os.path.join(ios_runner, "AppDelegate.swift"), "w", encoding="utf-8") as f:
                f.write("// Stock AppDelegate\n")

            dna = detect_project_dna(td)
            self.assertIsNotNone(dna)
            self.assertTrue(dna.is_dna_app)
            self.assertEqual(dna.blueprint_path, "context/03_Tech/ARCHITECTURE.md")
            self.assertTrue(any("android" in r for r in dna.active_native_roots))
            self.assertIn("ios", dna.dormant_roots)

            # Test universal flag bypasses DNA
            dna_univ = detect_project_dna(td, force_universal=True)
            self.assertIsNone(dna_univ)

    def test_classify_dna_app_file(self):
        """TEST-11: compute_file_gravity_and_cluster maps files to standardized gravity slots."""
        from utils.packer import compute_file_gravity_and_cluster
        self.assertEqual(compute_file_gravity_and_cluster("context/03_Tech/ARCHITECTURE.md")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster("pubspec.yaml")[0], 0)
        self.assertEqual(compute_file_gravity_and_cluster("lib/models/user_model.dart")[0], 1)
        self.assertEqual(compute_file_gravity_and_cluster("lib/controllers/menu_viewmodel.dart")[0], 6)
        self.assertEqual(compute_file_gravity_and_cluster("test/widget_test.dart")[0], 9)

    def test_dna_packaging_end_to_end(self):
        """TEST-12: Full end-to-end DNA packaging excludes .agents runtime, creates prompt file and DNA stamp."""
        from utils.packer import export_audit_bundles
        with tempfile.TemporaryDirectory() as td:
            agents_dir = os.path.join(td, ".agents", "skills", "test-skill")
            context_tech = os.path.join(td, "context", "03_Tech")
            lib_dir = os.path.join(td, "lib", "models")
            res_drawable = os.path.join(td, "android", "app", "src", "main", "res", "drawable")
            res_values = os.path.join(td, "android", "app", "src", "main", "res", "values")
            res_values_es = os.path.join(td, "android", "app", "src", "main", "res", "values-es")
            os.makedirs(agents_dir, exist_ok=True)
            os.makedirs(context_tech, exist_ok=True)
            os.makedirs(lib_dir, exist_ok=True)
            os.makedirs(res_drawable, exist_ok=True)
            os.makedirs(res_values, exist_ok=True)
            os.makedirs(res_values_es, exist_ok=True)

            with open(os.path.join(td, "pubspec.yaml"), "w", encoding="utf-8") as f:
                f.write("name: sample_dna_app\n")
            with open(os.path.join(context_tech, "ARCHITECTURE.md"), "w", encoding="utf-8") as f:
                f.write("# Architecture Blueprint\nDetails here.\n")
            with open(os.path.join(lib_dir, "item_model.dart"), "w", encoding="utf-8") as f:
                f.write("class ItemModel { final String id; ItemModel(this.id); }\n")
            # .agents internal skill that MUST be excluded
            with open(os.path.join(agents_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("# Agent Skill Internal\n")
            # Vector icon that MUST be excluded
            with open(os.path.join(res_drawable, "ic_launcher.xml"), "w", encoding="utf-8") as f:
                f.write("<vector>icon</vector>\n")
            # Canonical string that MUST be kept
            with open(os.path.join(res_values, "strings.xml"), "w", encoding="utf-8") as f:
                f.write("<resources><string name='app_name'>Test</string></resources>\n")
            # Secondary string variant that MUST be excluded
            with open(os.path.join(res_values_es, "strings.xml"), "w", encoding="utf-8") as f:
                f.write("<resources><string name='app_name'>Prueba</string></resources>\n")

            out_dir = os.path.join(td, "audit_dna")
            bundles = export_audit_bundles(td, out_dir=out_dir, hybrid=True)

            # Assert .agents skill was NOT packed into any bundle
            bundle_contents = {}
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    bundle_contents[os.path.basename(b)] = bf.read()
            all_text = "\n".join(bundle_contents.values())
            self.assertNotIn("Agent Skill Internal", all_text)
            self.assertNotIn("ic_launcher.xml", all_text)
            self.assertNotIn("values-es/strings.xml", all_text)
            self.assertIn("Architecture Blueprint", all_text)
            self.assertIn("ItemModel", all_text)

            # Assert Bundle 01 has DNA Governance Stamp
            b1_text = next((v for k, v in bundle_contents.items() if k.startswith("01_")), "")
            self.assertIn("DNA & Governance Stamp", b1_text)

            # Assert 00_GEMINI_WEB_AUDIT_PROMPT.txt was generated
            prompt_path = os.path.join(out_dir, "00_GEMINI_WEB_AUDIT_PROMPT.txt")
            self.assertTrue(os.path.isfile(prompt_path))
            with open(prompt_path, "r", encoding="utf-8") as pf:
                prompt_content = pf.read()
            self.assertIn("bundles are attached in your context window", prompt_content)
            self.assertIn("Triad Threat Probe Enforcement", prompt_content)

    def test_global_ast_symbol_compass(self):
        """TEST-13: Global AST Symbol Compass extracts top-level classes and functions mapped to bundles."""
        from utils.packer import _build_global_ast_symbol_compass
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "engine.py"), "w", encoding="utf-8") as f:
                f.write("class DatabaseEngine:\n    pass\n\ndef run_pipeline():\n    pass\n")
            compass = _build_global_ast_symbol_compass(td, {"engine.py": "01_ENGINE"})
            self.assertIn("Global AST Symbol Compass", compass)
            self.assertIn("`DatabaseEngine`", compass)
            self.assertIn("`run_pipeline`", compass)
            self.assertIn("`Bundle 01`", compass)

    def test_phased_audit_playbooks_in_prompt(self):
        """TEST-14: Companion audit prompt generates Phased Audit Playbooks A, B, and C."""
        from utils.packer import generate_gemini_web_audit_prompt
        with tempfile.TemporaryDirectory() as td:
            p_path = generate_gemini_web_audit_prompt(
                td,
                project_name="my_project",
                tier_label="TIER 2: HYBRID",
                bundle_files=[
                    ("01_CORE", "Core logic", 2, 10.5, "Audit core invariants"),
                    ("02_SERVICES", "Services", 3, 15.0, "Audit services"),
                    ("03_UI", "Presentation", 4, 12.0, "Audit UI"),
                ],
                total_tokens=2500,
            )
            self.assertTrue(os.path.isfile(p_path))
            with open(p_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Phase 1: Workspace Architecture, Core Contracts", content)
            self.assertIn("Phase 2: Core Services, Business Logic", content)
            self.assertIn("Phase 3: Presentation Screens, UI Tokens", content)
            self.assertIn("INTERACTIVE 4-TURN AUDIT PROTOCOL", content)
            self.assertIn("BEGIN IMMEDIATELY WITH TURN 1", content)
            self.assertIn("Signature Preservation Mandate", content)
            self.assertIn("inspect your diff, preserve signatures, integrate the logic, and verify with automated tests", content)
            txt_files = [f for f in os.listdir(td) if f.endswith(".txt")]
            self.assertEqual(txt_files, ["00_GEMINI_WEB_AUDIT_PROMPT.txt"])

    def test_expanded_pre_audit_radar(self):
        """TEST-16: Expanded Pre-Audit Static Radar flags deep nesting, ReDoS, and implicit encoding."""
        from utils.packer import generate_bundle_pre_audit_radar
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "risky.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write(
                    "import re\n"
                    "def deeply_nested():\n"
                    "    if True:\n"
                    "        for i in range(1):\n"
                    "            while True:\n"
                    "                try:\n"
                    "                    with open('x.txt') as h:\n"
                    "                        pass\n"
                    "                except Exception:\n"
                    "                    pass\n"
                    "                break\n"
                    "def redos():\n"
                    "    return re.compile(r'(a+)+')\n"
                )
            radar = generate_bundle_pre_audit_radar(td, ["risky.py"])
            self.assertIn("Deep Control Flow Nesting (>=4 levels)", radar)
            self.assertIn("Regex ReDoS Risk Vectors", radar)
            self.assertIn("Implicit Text Encoding I/O Sinks", radar)

    def test_agents_root_manifests_in_bundle_01(self):
        """TEST-17: .agents root manifests map to Gravity 0 (Workspace Root Config & Manifests)."""
        from utils.packer import compute_file_gravity_and_cluster
        g, slug, desc = compute_file_gravity_and_cluster(".agents/AGENTS_INDEX.md")
        self.assertEqual(g, 0)
        self.assertEqual(slug, "workspace_manifests")
        g2, slug2, _ = compute_file_gravity_and_cluster(".agents/DEPLOY_ME.md")
        self.assertEqual(g2, 0)
        self.assertEqual(slug2, "workspace_manifests")
        g3, slug3, _ = compute_file_gravity_and_cluster(".agents/hooks.json")
        self.assertEqual(g3, 0)
        self.assertEqual(slug3, "workspace_manifests")

    def test_polyglot_function_return_types_and_receivers(self):
        """TEST-18: Polyglot function signatures with return types and receivers are extracted."""
        from core.scanner import skeletonize_code, extract_file_symbols
        with tempfile.TemporaryDirectory() as td:
            ts_code = (
                "export async function fetchUser(id: string): Promise<User> {\n"
                "    const res = await api.get('/user/' + id);\n"
                "    return res.data;\n"
                "}\n"
            )
            skel_ts = skeletonize_code(ts_code, ext="ts")
            self.assertIn("Implementation omitted for audit", skel_ts)
            self.assertIn("export async function fetchUser(id: string): Promise<User> {", skel_ts)

            rust_code = (
                "pub fn compute_hash(data: &[u8]) -> Result<String, Error> {\n"
                "    let hash = sha256(data);\n"
                "    Ok(hash)\n"
                "}\n"
            )
            skel_rs = skeletonize_code(rust_code, ext="rs")
            self.assertIn("Implementation omitted for audit", skel_rs)
            self.assertIn("pub fn compute_hash(data: &[u8]) -> Result<String, Error> {", skel_rs)

            go_code = (
                "func (s *Server) Start(ctx context.Context) error {\n"
                "    s.running = true\n"
                "    return nil\n"
                "}\n"
            )
            skel_go = skeletonize_code(go_code, ext="go")
            self.assertIn("Implementation omitted for audit", skel_go)
            self.assertIn("func (s *Server) Start(ctx context.Context) error {", skel_go)

            f_ts = os.path.join(td, "user.ts")
            with open(f_ts, "w", encoding="utf-8") as f:
                f.write(ts_code)
            defs, _ = extract_file_symbols(f_ts)
            self.assertIn("fetchUser", defs)

    def test_polyglot_multiline_block_comment_brace_tracking(self):
        """TEST-19: Multiline block comments with braces do not scramble skeletonizer depth."""
        from core.scanner import skeletonize_code
        code = (
            "/*\n"
            " * Config object:\n"
            " * { key: value, nested: { x: 1 } }\n"
            " */\n"
            "function processItem() {\n"
            "    const a = 1;\n"
            "    return a;\n"
            "}\n"
            "function nextItem() {\n"
            "    return 2;\n"
            "}\n"
        )
        skel = skeletonize_code(code, ext="js")
        self.assertIn("function processItem() {", skel)
        self.assertIn("function nextItem() {", skel)
        self.assertIn("Implementation omitted for audit", skel)

    def test_dna_detection_not_triggered_by_agents_md_alone(self):
        """TEST-20: detect_project_dna returns None for general repos with AGENTS.md alone."""
        from utils.packer import detect_project_dna
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "AGENTS.md"), "w", encoding="utf-8") as f:
                f.write("# General Agents Config\n")
            with open(os.path.join(td, "package.json"), "w", encoding="utf-8") as f:
                f.write('{"name": "standard-node-app"}\n')
            dna = detect_project_dna(td)
            self.assertIsNone(dna)

    def test_hybrid_mode_secondary_skeletonization(self):
        """TEST-21: Hybrid mode skeletonizes secondary utilities (>150 lines) while keeping core models full."""
        from utils.packer import export_audit_bundles
        with tempfile.TemporaryDirectory() as td:
            core_dir = os.path.join(td, "core")
            bin_dir = os.path.join(td, "tools")
            os.makedirs(core_dir, exist_ok=True)
            os.makedirs(bin_dir, exist_ok=True)

            with open(os.path.join(core_dir, "models.py"), "w", encoding="utf-8") as f:
                body = "def get_model():\n" + "\n".join(f"    line_{i} = {i}" for i in range(200)) + "\n    return line_0\n"
                f.write(body)

            with open(os.path.join(bin_dir, "tool_helper.py"), "w", encoding="utf-8") as f:
                body = "def run_tool():\n" + "\n".join(f"    work_{i} = {i}" for i in range(200)) + "\n    return work_0\n"
                f.write(body)

            out_hybrid = os.path.join(td, "out_hybrid")
            bundles = export_audit_bundles(td, out_dir=out_hybrid, skeleton=False, hybrid=True, line_numbers=True, reclaim=False)
            bundle_contents = []
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    bundle_contents.append(bf.read())
            joined = "\n".join(bundle_contents)

            # Core models.py must remain FULL
            self.assertIn('mode="FULL"', joined)
            # Secondary tool_helper.py (>150 lines) must be SKELETON when reclaim=False
            self.assertIn('mode="SKELETON"', joined)

    def test_hybrid_mode_universal_water_filling(self):
        """TEST-23: Hybrid mode with reclaim=True promotes candidate skeletons when headroom is under soft cap."""
        from utils.packer import export_audit_bundles
        with tempfile.TemporaryDirectory() as td:
            core_dir = os.path.join(td, "core")
            bin_dir = os.path.join(td, "tools")
            os.makedirs(core_dir, exist_ok=True)
            os.makedirs(bin_dir, exist_ok=True)

            with open(os.path.join(core_dir, "models.py"), "w", encoding="utf-8") as f:
                body = "def get_model():\n" + "\n".join(f"    line_{i} = {i}" for i in range(200)) + "\n    return line_0\n"
                f.write(body)

            with open(os.path.join(bin_dir, "tool_helper.py"), "w", encoding="utf-8") as f:
                body = "def run_tool():\n" + "\n".join(f"    work_{i} = {i}" for i in range(200)) + "\n    return work_0\n"
                f.write(body)

            out_hybrid = os.path.join(td, "out_hybrid")
            bundles = export_audit_bundles(td, out_dir=out_hybrid, skeleton=False, hybrid=True, line_numbers=True, reclaim=True)
            bundle_contents = []
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    bundle_contents.append(bf.read())
            joined = "\n".join(bundle_contents)

            # With reclaim=True and tiny total size (~2.5k tokens << 45k soft cap), tool_helper.py is reclaimed to FULL
            self.assertIn('mode="FULL"', joined)
            self.assertNotIn('mode="SKELETON"', joined)

    def test_symbol_compass_excludes_private_and_main(self):
        """TEST-22: Global AST Symbol Compass filters out private functions and generic main."""
        from utils.packer import _build_global_ast_symbol_compass
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "cli.py"), "w", encoding="utf-8") as f:
                f.write(
                    "def _log_telemetry():\n    pass\n"
                    "def main():\n    pass\n"
                    "def real_feature():\n    pass\n"
                )
            compass = _build_global_ast_symbol_compass(td, {"cli.py": "01_CLI"})
            self.assertNotIn("`_log_telemetry`", compass)
            self.assertNotIn("`main`", compass)
            self.assertIn("`real_feature`", compass)

    def test_fence_safe_prompt_tag_neutralization(self):
        """F-07: DEFECT-04 hardening: tags are neutralized unconditionally across fences."""
        from utils.packer import neutralize_prompt_tags, escape_artifact_boundaries
        raw = (
            "Outside <system>tag</system> and <artifact identifier='test'>body</artifact>\n"
            "```python\n"
            "<system>code tag</system>\n"
            "```\n"
        )
        escaped = escape_artifact_boundaries(raw)
        self.assertIn("&lt;artifact", escaped)
        neutralized = neutralize_prompt_tags(raw, is_markdown=True)
        # Outside tag neutralized
        self.assertIn("&lt;system&gt;", neutralized)
        # Inside fenced code block also neutralized to prevent prompt-in-data bleed (DEFECT-04)
        self.assertIn("&lt;system&gt;code tag&lt;/system&gt;", neutralized)

    def test_js_dart_arrow_function_skeletonization(self):
        """F-04: JS/TS and Dart arrow functions recognized during skeletonization."""
        from core.scanner import skeletonize_code
        js_code = (
            "const sum = (a, b) => {\n"
            "    const c = a + b;\n"
            "    return c;\n"
            "};\n"
        )
        skel = skeletonize_code(js_code, "js")
        self.assertIn("sum", skel)
        self.assertIn("...", skel)

    def test_universal_manifesto_generation(self):
        """F-02: Universal audit manifesto produces clean repository-specific header."""
        from utils.packer import build_universal_audit_manifesto
        manifesto = build_universal_audit_manifesto("my_awesome_app", "hybrid")
        self.assertIn("REPOSITORY ARCHITECTURE & AUDIT MANIFESTO: `my_awesome_app`", manifesto)
        self.assertIn("MULTI-BUNDLE CONTEXT PACKAGE — HYBRID TIER", manifesto)


class TestPackerF01ToF08(unittest.TestCase):
    """Forensic verification tests for findings F-01 through F-08."""

    def test_f01_kotlin_multiline_class_preservation(self):
        """F-01: Multi-line class declarations in Kotlin/Dart do not hollow out the whole class."""
        from core.scanner import skeletonize_code
        kt_code = (
            "package com.example\n\n"
            "data class UserProfile(\n"
            "    val id: String,\n"
            "    val email: String,\n"
            "    val displayName: String\n"
            ") : Serializable {\n"
            "    fun formattedName(): String {\n"
            "        val prefix = \"Name: \"\n"
            "        return prefix + displayName\n"
            "    }\n"
            "}\n"
        )
        skel = skeletonize_code(kt_code, "kt")
        # Class header must be intact
        self.assertIn("data class UserProfile", skel)
        # Inner method signature must be preserved, not swallowed by class header
        self.assertIn("fun formattedName(): String", skel)
        # Inner method body implementation must be hollowed out
        self.assertNotIn("val prefix = \"Name: \"", skel)

    def test_f02_reserved_keywords_and_non_functions(self):
        """F-02: Control flow, throw, await, and keywords are not extracted as functions."""
        from core.scanner import extract_file_symbols, RESERVED_KEYWORDS
        self.assertIn("when", RESERVED_KEYWORDS)
        self.assertIn("late", RESERVED_KEYWORDS)
        self.assertIn("required", RESERVED_KEYWORDS)

        ts_code = (
            "function process(x: any) {\n"
            "    if (x == null) {\n"
            "        throw new Error('missing x');\n"
            "    }\n"
            "    const val = await fetchData();\n"
            "}\n"
        )
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "test.ts")
            with open(p, "w", encoding="utf-8") as f:
                f.write(ts_code)
            defs, refs = extract_file_symbols(p)
            self.assertIn("process", defs)
            self.assertNotIn("Error", defs)
            self.assertNotIn("throw", defs)
            self.assertNotIn("fetchData", defs)

    def test_f03_android_and_feature_subpackage_clustering(self):
        """F-03: Sub-clusters native Android source trees and recognizes custom feature containers."""
        from utils.packer import _compute_natural_bucket_prefix
        # Android kotlin package clustering
        prefix_kt = _compute_natural_bucket_prefix("android/app/src/main/kotlin/com/example/echont/MainActivity.kt")
        self.assertTrue(prefix_kt.startswith("android/app/src/main/kotlin/com"))
        # Android res clustering
        prefix_res = _compute_natural_bucket_prefix("android/app/src/main/res/values/strings.xml")
        self.assertEqual(prefix_res, "android/res")
        # Feature container targets
        prefix_targets = _compute_natural_bucket_prefix("src/targets/compiler/visitor.ts")
        self.assertEqual(prefix_targets, "src/targets/compiler")

    def test_f04_cross_bundle_stem_map_filters_non_code(self):
        """F-04: Non-code files (.md, .json) do not pollute cross-bundle code imports."""
        from utils.packer import extract_cross_bundle_imports
        file_to_bundle = {
            "README.md": "01_ROOT",
            "src/user_service.ts": "02_CORE",
            "src/index.ts": "03_APP",
        }
        # Code importing user_service should link to 02_CORE
        imports = extract_cross_bundle_imports("src/index.ts", "import { getUser } from './user_service';", file_to_bundle)
        self.assertTrue(any("Bundle 02" in imp for imp in imports))

        # Code referencing 'README' shouldn't link to Bundle 01
        imports_md = extract_cross_bundle_imports("src/index.ts", "const text = 'README';", file_to_bundle)
        self.assertFalse(any("Bundle 01" in imp for imp in imports_md))

    def test_f05_mode_label_parity(self):
        """F-05: render_bundle_file_entry and pack_digest preserve exact mode tags."""
        from utils.packer import ContextPacker
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "doc.md"), "w", encoding="utf-8") as f:
                f.write("# Heading\n" * 150)
            packer = ContextPacker(td)
            digest = packer.pack_digest(["doc.md"], skeleton={"doc.md": True})
            self.assertIn('mode="MD-SKELETON"', digest)
            self.assertIn("MD-SKELETON", digest)

    def test_f06_json_compaction_and_gemini_offset(self):
        """F-06: Large JSON compaction and GEMINI.md line numbering offset."""
        from utils.packer import render_bundle_file_entry, is_minified_or_asset
        # 1. l10n generated file recognized
        self.assertTrue(is_minified_or_asset("lib/l10n/app_localizations.dart"))
        self.assertTrue(is_minified_or_asset("lib/l10n/app_localizations_en.dart"))

        # 2. Large JSON compacting (> AUTO_SKELETON_LINE_THRESHOLD=350)
        large_json = '{\n  "items": [\n' + ",\n".join(f'    {{"id": {i}, "name": "item_{i}"}}' for i in range(400)) + '\n  ]\n}'
        block, tok = render_bundle_file_entry("catalog.json", large_json, adaptive=True)
        self.assertIn('mode="JSON-SCHEMA-SAMPLE"', block)
        self.assertIn("__collapsed_items__", block)

        # 3. GEMINI.md line numbers start after mandates marker (line 51)
        gemini_content = "Intro\n" * 50 + "## PROJECT-SPECIFIC MANDATES\nSpecific mandate line 1\n"
        block_gemini, _ = render_bundle_file_entry("GEMINI.md", gemini_content)
        self.assertIn('lines="51-52"', block_gemini)

    def test_f07_bundle_overflow_penalty(self):
        """F-07: balance_into_k_bundles applies penalty when merging clusters exceeding max_tokens."""
        from utils.packer import balance_into_k_bundles, ProjectTaxonomy
        with tempfile.TemporaryDirectory() as td:
            files = ["a.py", "b.py", "c.py"]
            for f in files:
                with open(os.path.join(td, f), "w", encoding="utf-8") as fh:
                    fh.write("def foo():\n    pass\n" * 50)
            taxonomy = ProjectTaxonomy(
                tree_hash="test",
                provider="test",
                project_summary="test",
                clusters={
                    "cluster_a": {"gravity": 2, "title": "A", "files": ["a.py"]},
                    "cluster_b": {"gravity": 3, "title": "B", "files": ["b.py"]},
                    "cluster_c": {"gravity": 4, "title": "C", "files": ["c.py"]},
                }
            )
            # k=2 should merge smallest
            bundles = balance_into_k_bundles(td, files, k=2, max_tokens_per_bundle=50000, taxonomy=taxonomy)
            self.assertEqual(len(bundles), 2)

    def test_f08_static_radar_precision(self):
        """F-08: Radar flags Node/TS async execution sinks and multi-line empty catches."""
        from utils.packer import generate_bundle_pre_audit_radar
        with tempfile.TemporaryDirectory() as td:
            sub = os.path.join(td, "src", "services")
            os.makedirs(sub, exist_ok=True)
            ts_file = os.path.join(sub, "runner.ts")
            with open(ts_file, "w", encoding="utf-8") as fh:
                fh.write(
                    "import { execAsync, spawnSync } from 'child_process';\n"
                    "export function runTask() {\n"
                    "    execAsync('ls');\n"
                    "    spawnSync('pwd');\n"
                    "    try {\n"
                    "        doWork();\n"
                    "    } catch (err) {\n"
                    "        // ignored\n"
                    "    }\n"
                    "}\n"
                )
            radar = generate_bundle_pre_audit_radar(td, ["src/services/runner.ts"])
            self.assertIn("execAsync()", radar)
            self.assertIn("`catch {}` [SILENT]", radar)
            self.assertIn("services/runner.ts:L", radar)

    def test_f09_polyglot_invariant_harvesting_and_vision_anti_vision(self):
        """TEST-F09: Polyglot invariant harvesting, full VISION.md extraction, Rule 7, and .hermes isolation."""
        import json
        from utils.packer import export_audit_bundles, harvest_invariant_anchors
        from core.dna import sequence_project_dna
        with tempfile.TemporaryDirectory() as td:
            src_dir = os.path.join(td, "src")
            context_dir = os.path.join(td, "context")
            hermes_dir = os.path.join(td, ".hermes")
            agents_dir = os.path.join(td, ".agents")
            os.makedirs(src_dir, exist_ok=True)
            os.makedirs(context_dir, exist_ok=True)
            os.makedirs(hermes_dir, exist_ok=True)
            os.makedirs(agents_dir, exist_ok=True)

            with open(os.path.join(td, "package.json"), "w", encoding="utf-8") as f:
                f.write('{"name": "test-universal-invariants"}\n')

            # 1. Polyglot in-code invariant anchors
            with open(os.path.join(src_dir, "trade.py"), "w", encoding="utf-8") as f:
                f.write(
                    "def execute(is_live: bool):\n"
                    "    if not is_live:\n"
                    "        # INVARIANT [Optuna-Sim]: Early exit in paper mode prevents virtual state drift\n"
                    "        return\n"
                    "    print('Live trade')\n"
                )

            with open(os.path.join(src_dir, "process.ts"), "w", encoding="utf-8") as f:
                f.write(
                    "export function launch() {\n"
                    "    // ARCH-DECISION [Win-IPC]: Native child_process spawn used instead of PM2\n"
                    "    return true;\n"
                    "}\n"
                )

            # 2. Hermes config that MUST be excluded from host app bundle
            with open(os.path.join(hermes_dir, "hermes.yaml"), "w", encoding="utf-8") as f:
                f.write("agent: hermes\nworkspace: isolated\n")

            # 3. Full VISION.md with Core Essence, Invariants, and Anti-Vision
            with open(os.path.join(context_dir, "VISION.md"), "w", encoding="utf-8") as f:
                f.write(
                    "# 🌟 FOUNDATIONAL VISION: TradeBot\n"
                    "## 1. Core Essence\n"
                    "Autonomous algorithmic trading platform with zero latency.\n"
                    "## 2. Non-Negotiable Invariants\n"
                    "1. Simulation-to-live mathematical parity verified by Optuna engine.\n"
                    "## 3. Anti-Vision (What This App Is NOT & WILL NEVER BE)\n"
                    "- ❌ **Not Enterprise ERP**: Never introduce PM2 daemons or multi-role queues.\n"
                )

            # 4. .agents/.dna.json with custom_invariants
            with open(os.path.join(agents_dir, ".dna.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "framework": "node",
                    "language": "typescript",
                    "custom_invariants": ["SQLite WAL single-writer concurrency must be isolated"]
                }, f)

            # Assert harvester finds anchors
            anchors = harvest_invariant_anchors(td, ["src/trade.py", "src/process.ts"])
            self.assertEqual(len(anchors), 2)
            self.assertTrue(any("[Optuna-Sim]" in a for a in anchors))
            self.assertTrue(any("[Win-IPC]" in a for a in anchors))

            # Run bundle export
            out_dir = os.path.join(td, "bundles")
            bundles = export_audit_bundles(td, out_dir=out_dir, hybrid=True)

            # Assert .hermes was NOT included
            bundle_texts = {}
            for b in bundles:
                with open(b, "r", encoding="utf-8") as bf:
                    bundle_texts[os.path.basename(b)] = bf.read()
            merged_bundles = "\n".join(bundle_texts.values())
            self.assertNotIn("agent: hermes", merged_bundles)
            self.assertIn("Early exit in paper mode", merged_bundles)

            # Assert Bundle 01 Pre-Audit Radar includes Invariants
            b1_text = next((v for k, v in bundle_texts.items() if k.startswith("01_")), "")
            self.assertIn("Declared Architectural Invariants", b1_text)

            # Assert 00_GEMINI_WEB_AUDIT_PROMPT.txt has full invariants, anti-vision, and Rule 7
            prompt_file = os.path.join(out_dir, "00_GEMINI_WEB_AUDIT_PROMPT.txt")
            self.assertTrue(os.path.isfile(prompt_file))
            with open(prompt_file, "r", encoding="utf-8") as pf:
                prompt_text = pf.read()

            self.assertIn("Negative Constraints, Conditional Returns & Invariant Immunity Law", prompt_text)
            self.assertIn("Conditional Early-Return Guards", prompt_text)
            self.assertIn("Simulation-to-live mathematical parity", prompt_text)
            self.assertIn("Anti-Vision & Non-Goals", prompt_text)
            self.assertIn("Not Enterprise ERP", prompt_text)
            self.assertIn("IN-CODE ARCHITECTURAL ANCHORS", prompt_text)
            self.assertIn("[Optuna-Sim]", prompt_text)

            # Assert sequence_project_dna preserves custom + VISION.md invariants
            dna = sequence_project_dna(td)
            self.assertIsNotNone(dna)
            self.assertTrue(any("SQLite WAL" in inv for inv in dna.invariants))
            self.assertTrue(any("Simulation-to-live" in inv for inv in dna.invariants))


class TestProjectDNALivingSystem(unittest.TestCase):
    """
    Forensic verification suite for the Universal Living Project DNA:
    1. Canonical 5-Tier Strata classification (Standard & Option A Feature Organs)
    2. Execution Spine & Pillar protection against hybrid skeletonization
    3. Architecture Layer Violation detection & Radar integration
    4. Brownfield Epigenetic Mutation & Scaffolding
    """

    def test_dna_canonical_5_tier_classification(self):
        """Verifies classify_file_to_tier maps paths and AST stereotypes accurately across 5 tiers."""
        from core.dna import classify_file_to_tier

        # Tier 1 Contracts
        t1, g1, _, _ = classify_file_to_tier("lib/contracts/api_contract.dart")
        self.assertEqual(t1, "1_contracts")
        self.assertEqual(g1, 1)

        # Tier 2 Domain
        t2, g2, _, _ = classify_file_to_tier("lib/domain/usecases/login_usecase.dart")
        self.assertEqual(t2, "2_domain")
        self.assertEqual(g2, 2)

        # Tier 3 Services
        t3, g3, _, _ = classify_file_to_tier("lib/services/api_service.dart")
        self.assertEqual(t3, "3_services")
        self.assertEqual(g3, 4)

        # Tier 4 State
        t4, g4, _, _ = classify_file_to_tier("lib/state/auth_notifier.dart")
        self.assertEqual(t4, "4_state")
        self.assertEqual(g4, 6)

        # Tier 5 Presentation
        t5, g5, _, _ = classify_file_to_tier("lib/presentation/screens/home_screen.dart")
        self.assertEqual(t5, "5_presentation")
        self.assertEqual(g5, 7)

        # Option A Adaptive Hybrid: feature organ nesting
        t_feat_dom, _, _, _ = classify_file_to_tier("lib/features/billing/domain/invoice.dart")
        self.assertEqual(t_feat_dom, "2_domain")

        t_feat_ui, _, _, _ = classify_file_to_tier("lib/features/billing/presentation/invoice_page.dart")
        self.assertEqual(t_feat_ui, "5_presentation")

    def test_dna_execution_spine_protection(self):
        """Verifies files in dna.execution_spine and dna.pillars are NEVER skeletonized in hybrid mode."""
        from utils.packer import balance_into_k_bundles, ProjectTaxonomy
        from core.dna import ProjectDNA

        with tempfile.TemporaryDirectory() as td:
            spine_file = "lib/main.dart"
            full_p = os.path.join(td, spine_file)
            os.makedirs(os.path.dirname(full_p), exist_ok=True)
            # Create a 250-line file that would normally be a candidate for skeletonization
            with open(full_p, "w", encoding="utf-8") as fh:
                fh.write("void main() {\n" + "\n".join(f"  print({i});" for i in range(250)) + "\n}\n")

            mock_dna = ProjectDNA(
                is_dna_app=True,
                archetype="Flutter App",
                version="0.0.1",
                blueprint_path=None,
                stacks=["Flutter/Dart"],
                active_native_roots=[],
                dormant_roots=[],
                verified_gates="",
                origin="test",
                dna_state="GREENFIELD",
                primary_framework="flutter",
                execution_spine=[spine_file],
                pillars={},
            )

            mock_tax = ProjectTaxonomy(
                tree_hash="test_hash",
                provider="test",
                project_summary="Spine App",
                clusters={"core": {"gravity": 8, "title": "Core", "files": [spine_file]}},
                file_to_cluster={spine_file: (8, "core", "Core")},
                skeleton_candidates={spine_file},
            )

            bundles = balance_into_k_bundles(
                td,
                audit_files=[spine_file],
                hybrid=True,
                taxonomy=mock_tax,
                dna=mock_dna,
            )

            self.assertEqual(len(bundles), 1)
            b_code, b_title, b_files, b_skel_map, _ = bundles[0]
            # Verify spine file is protected (apply_skel is False)
            self.assertFalse(b_skel_map[spine_file])

    def test_dna_layer_violations_radar(self):
        """Verifies generate_bundle_pre_audit_radar includes architectural layer violation warnings."""
        from utils.packer import generate_bundle_pre_audit_radar
        from core.dna import ProjectDNA

        mock_dna = ProjectDNA(
            is_dna_app=True,
            archetype="Architecture App",
            version="0.0.1",
            blueprint_path=None,
            stacks=["Flutter/Dart"],
            active_native_roots=[],
            dormant_roots=[],
            verified_gates="",
            origin="test",
            dna_state="GREENFIELD",
            primary_framework="flutter",
            layer_violations=[
                {
                    "file": "lib/domain/usecase.dart",
                    "line": 4,
                    "source_tier": "2_domain",
                    "target_tier": "5_presentation",
                    "import_target": "lib/presentation/screen.dart",
                }
            ],
        )

        with tempfile.TemporaryDirectory() as td:
            f = "lib/domain/usecase.dart"
            full_p = os.path.join(td, f)
            os.makedirs(os.path.dirname(full_p), exist_ok=True)
            with open(full_p, "w", encoding="utf-8") as fh:
                fh.write("import '../presentation/screen.dart';\nclass Usecase {}\n")

            radar = generate_bundle_pre_audit_radar(td, [f], dna=mock_dna)
            self.assertIn("DNA Architecture Layer Violations", radar)
            self.assertIn("2_domain -> 5_presentation", radar)

    def test_dna_brownfield_mutation(self):
        """Verifies mutate_project_dna generates plan, epigenetic aliases, and scaffolds."""
        from core.dna import mutate_project_dna, classify_file_to_tier

        with tempfile.TemporaryDirectory() as td:
            os.makedirs(os.path.join(td, "lib", "network"), exist_ok=True)
            os.makedirs(os.path.join(td, "lib", "models"), exist_ok=True)
            with open(os.path.join(td, "pubspec.yaml"), "w", encoding="utf-8") as f:
                f.write("name: brownfield_app\n")
            with open(os.path.join(td, "lib", "network", "client.dart"), "w", encoding="utf-8") as f:
                f.write("class Client {}\n")
            with open(os.path.join(td, "lib", "models", "dto.dart"), "w", encoding="utf-8") as f:
                f.write("class Dto {}\n")

            # 1. Plan mode
            plan_res = mutate_project_dna(td, mode="plan")
            self.assertEqual(plan_res["status"], "success")
            self.assertIn("plan_file", plan_res)

            # 2. Epigenetic mode
            epi_res = mutate_project_dna(td, mode="epigenetic")
            self.assertEqual(epi_res["status"], "success")
            self.assertIn("lib/network", epi_res["epigenetic_aliases"])
            dna_path = os.path.join(td, ".agents", ".dna.json")
            self.assertTrue(os.path.isfile(dna_path))

            # Epigenetic mapping verification
            tier_mapped, _, _, _ = classify_file_to_tier(
                "lib/network/client.dart",
                epigenetic_aliases=epi_res["epigenetic_aliases"]
            )
            self.assertEqual(tier_mapped, "3_services")

            # 3. Scaffold mode
            scaff_res = mutate_project_dna(td, mode="scaffold")
            self.assertEqual(scaff_res["status"], "success")
            self.assertTrue(os.path.isdir(os.path.join(td, "lib", "services")))
            self.assertTrue(os.path.isdir(os.path.join(td, "lib", "presentation")))


if __name__ == "__main__":
    unittest.main()


