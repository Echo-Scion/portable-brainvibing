#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
test_dna_semver_universal.py
----------------------------
Comprehensive unit and integration test suite asserting that the DNA SemVer Engine
is 100% universal, agnostic, multi-platform, multi-project, and multi-OS compliant.
"""

import os
import sys
import json
import tempfile
import unittest

_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_TESTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from core.dna import (
    parse_semver,
    bump_semver_tuple,
    detect_project_version,
    update_project_version,
    stamp_changelog_release,
    compact_changelog_entries,
    evaluate_dna_semver,
    classify_file_to_tier,
)


class TestDNASemVerUniversal(unittest.TestCase):
    def test_parse_and_bump_semver(self):
        """Verifies pure SemVer parsing and arithmetic."""
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3, "", ""))
        self.assertEqual(parse_semver("v2.0.0-beta.1"), (2, 0, 0, "beta.1", ""))
        self.assertEqual(parse_semver("0.0.3+build42"), (0, 0, 3, "", "build42"))
        self.assertIsNone(parse_semver("invalid-version"))

        # Bumps
        self.assertEqual(bump_semver_tuple(1, 2, 3, "patch"), (1, 2, 4))
        self.assertEqual(bump_semver_tuple(1, 2, 3, "minor"), (1, 3, 0))
        self.assertEqual(bump_semver_tuple(1, 2, 3, "major"), (2, 0, 0))

    def test_polyglot_manifest_detection(self):
        """Verifies detection across Node, Flutter, Python, Rust, Java, and plain VERSION."""
        # 1. Plain VERSION
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "VERSION"), "w", encoding="utf-8") as f:
                f.write("2.1.4\n")
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "2.1.4")
            self.assertEqual(manifest, "VERSION")

        # 2. Node package.json
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "package.json"), "w", encoding="utf-8") as f:
                json.dump({"name": "test-app", "version": "3.0.1"}, f)
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "3.0.1")
            self.assertEqual(manifest, "package.json")

        # 3. Flutter pubspec.yaml
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "pubspec.yaml"), "w", encoding="utf-8") as f:
                f.write("name: flutter_app\nversion: 1.5.0+12\nenvironment:\n  sdk: '>=3.0.0'\n")
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "1.5.0+12")
            self.assertEqual(manifest, "pubspec.yaml")

        # 4. Python pyproject.toml
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "pyproject.toml"), "w", encoding="utf-8") as f:
                f.write('[project]\nname = "my-py"\nversion = "0.4.2"\n')
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "0.4.2")
            self.assertEqual(manifest, "pyproject.toml")

        # 5. Rust Cargo.toml
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "Cargo.toml"), "w", encoding="utf-8") as f:
                f.write('[package]\nname = "my_rust"\nversion = "0.8.0"\nedition = "2021"\n')
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "0.8.0")
            self.assertEqual(manifest, "Cargo.toml")

        # 6. Maven pom.xml
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "pom.xml"), "w", encoding="utf-8") as f:
                f.write('<project><version>4.2.0</version></project>')
            v, manifest = detect_project_version(td)
            self.assertEqual(v, "4.2.0")
            self.assertEqual(manifest, "pom.xml")

    def test_polyglot_manifest_bumping(self):
        """Verifies syntax-preserving updates across polyglot manifests."""
        with tempfile.TemporaryDirectory() as td:
            # Seed package.json, pubspec.yaml, Cargo.toml, pyproject.toml
            pkg_file = os.path.join(td, "package.json")
            pub_file = os.path.join(td, "pubspec.yaml")
            py_file = os.path.join(td, "pyproject.toml")
            cargo_file = os.path.join(td, "Cargo.toml")

            with open(pkg_file, "w", encoding="utf-8") as f:
                f.write('{\n  "name": "sample",\n  "version": "1.0.0"\n}\n')
            with open(pub_file, "w", encoding="utf-8") as f:
                f.write('name: my_app\nversion: 1.0.0+5\n')
            with open(py_file, "w", encoding="utf-8") as f:
                f.write('[project]\nversion = "1.0.0"\n')
            with open(cargo_file, "w", encoding="utf-8") as f:
                f.write('[package]\nname = "rust_app"\nversion = "1.0.0"\n')

            updated = update_project_version(td, "1.1.0")
            self.assertIn("package.json", updated)
            self.assertIn("pubspec.yaml", updated)
            self.assertIn("pyproject.toml", updated)
            self.assertIn("Cargo.toml", updated)

            # Verify contents
            with open(pkg_file, "r", encoding="utf-8") as f:
                self.assertIn('"version": "1.1.0"', f.read())
            with open(pub_file, "r", encoding="utf-8") as f:
                self.assertIn("version: 1.1.0+6", f.read())
            with open(py_file, "r", encoding="utf-8") as f:
                self.assertIn('version = "1.1.0"', f.read())
            with open(cargo_file, "r", encoding="utf-8") as f:
                self.assertIn('version = "1.1.0"', f.read())

    def test_dna_semver_evaluation_rules(self):
        """Verifies hardened Anti-AI-Slop SemVer rules."""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "VERSION"), "w", encoding="utf-8") as f:
                f.write("1.0.0\n")

            # 1. Normal contract change in Tier 1 without override defaults to PATCH (Anti-AI-Slop gate)
            eval_contract = evaluate_dna_semver(
                td,
                file_list=["src/contracts/user_dto.py"],
                commit_messages=["refactor: update user schema"],
            )
            self.assertEqual(eval_contract["recommended_bump"], "PATCH")
            self.assertEqual(eval_contract["target_version"], "1.0.1")

            # 2. Explicit human major override unlocks MAJOR
            eval_major_override = evaluate_dna_semver(
                td,
                file_list=["src/contracts/user_dto.py"],
                commit_messages=["refactor: breaking contract"],
                allow_major_override=True,
            )
            self.assertEqual(eval_major_override["recommended_bump"], "MAJOR")
            self.assertEqual(eval_major_override["target_version"], "2.0.0")

            # 3. Sacred North Star mutation (VISION.md) with [paradigm-shift] unlocks MAJOR
            eval_vision = evaluate_dna_semver(
                td,
                file_list=["context/VISION.md"],
                commit_messages=["feat: new architecture\n\n[paradigm-shift]: core rewrite"],
            )
            self.assertEqual(eval_vision["recommended_bump"], "MAJOR")
            self.assertEqual(eval_vision["target_version"], "2.0.0")

            # 4. Modifying single domain file alone stays PATCH (Incremental feature evolution)
            eval_domain = evaluate_dna_semver(
                td,
                file_list=["src/domain/billing_policy.py"],
                commit_messages=["feat: add new tier calculation policy"],
            )
            self.assertEqual(eval_domain["recommended_bump"], "PATCH")
            self.assertEqual(eval_domain["target_version"], "1.0.1")

            # 5. Explicit milestone tag or human minor override unlocks MINOR
            eval_milestone = evaluate_dna_semver(
                td,
                file_list=["src/domain/billing_policy.py"],
                commit_messages=["feat: complete milestone\n\n[milestone]: billing v1 ready"],
            )
            self.assertEqual(eval_milestone["recommended_bump"], "MINOR")
            self.assertEqual(eval_milestone["target_version"], "1.1.0")

            # 6. Leaf bugfix remains PATCH
            eval_patch = evaluate_dna_semver(
                td,
                file_list=["tests/test_math.py"],
                commit_messages=["fix: correct edge case division check"],
            )
            self.assertEqual(eval_patch["recommended_bump"], "PATCH")
            self.assertEqual(eval_patch["target_version"], "1.0.1")

    def test_lessword_changelog_compaction(self):
        """Verifies that compact_changelog_entries condenses raw bullet points into dense domain lines."""
        raw = (
            "- Added compute_scaffold_discount function in capabilities.py\n"
            "- Added resolve_elastic_execution_plan 2D model matrix\n"
            "- Added check_delegation_safety alias in scanner.py\n"
            "- Added differential AST skeleton mapping in scanner.py\n"
            "- Added fast-track subcommand in orion.py\n"
            "- Changed bento_slicer.py active task rendering\n"
            "- Fixed memory leak on unmount\n"
            "- Fixed regex ReDoS in parser\n"
        )
        compacted = compact_changelog_entries(raw)
        lines = [l for l in compacted.splitlines() if l.strip()]
        self.assertTrue(len(lines) <= 5)
        self.assertIn("**Architecture & Governance**", compacted)
        self.assertIn("**Core Services & Pipelines**", compacted)
        self.assertIn("**Integrity & Bug Fixes**", compacted)

    def test_changelog_release_stamping(self):
        """Verifies that stamp_changelog_release seals [Unreleased] with Lessword compaction."""
        with tempfile.TemporaryDirectory() as td:
            ch_file = os.path.join(td, "CHANGELOG.md")
            initial_content = (
                "# Changelog\n\n"
                "## [Unreleased]\n\n"
                "- New export to PDF capability in services\n"
                "- Resolved memory leak on unmount in tests\n\n"
                "## [1.0.0] - 2026-01-01\n"
                "- Initial release\n"
            )
            with open(ch_file, "w", encoding="utf-8") as f:
                f.write(initial_content)

            ok = stamp_changelog_release(td, "1.0.1", date_str="2026-10-30", compact=True)
            self.assertTrue(ok)

            with open(ch_file, "r", encoding="utf-8") as f:
                updated = f.read()

            self.assertIn("## [Unreleased]", updated)
            self.assertIn("## [1.0.1] - 2026-10-30", updated)
            self.assertIn("## [1.0.0] - 2026-01-01", updated)

    def test_flutter_build_number_auto_increment(self):
        """Verifies Flutter build numbers auto-increment and respect explicit override."""
        with tempfile.TemporaryDirectory() as td:
            pub_path = os.path.join(td, "pubspec.yaml")
            with open(pub_path, "w", encoding="utf-8") as f:
                f.write("name: echont\nversion: 1.0.0+1\n")

            # 1. Auto-increment from +1 to +2
            updated = update_project_version(td, "1.0.1")
            self.assertIn("pubspec.yaml", updated)
            with open(pub_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("version: 1.0.1+2", content)

            # 2. Explicit build number override
            update_project_version(td, "1.0.2", new_build_number=42)
            with open(pub_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("version: 1.0.2+42", content)

    def test_mcp_cli_multi_sink_sync(self):
        """Verifies multi-sink synchronization across Node package.json, plugin.json, and code constants."""
        with tempfile.TemporaryDirectory() as td:
            pkg_path = os.path.join(td, "package.json")
            plugin_path = os.path.join(td, "plugin.json")
            cli_dir = os.path.join(td, "src", "cli")
            mcp_dir = os.path.join(td, "src", "mcp")
            os.makedirs(cli_dir, exist_ok=True)
            os.makedirs(mcp_dir, exist_ok=True)

            cli_path = os.path.join(cli_dir, "index.ts")
            mcp_path = os.path.join(mcp_dir, "index.ts")

            with open(pkg_path, "w", encoding="utf-8") as f:
                f.write('{\n  "name": "flutterin",\n  "version": "0.0.1"\n}\n')
            with open(plugin_path, "w", encoding="utf-8") as f:
                f.write('{\n  "id": "flutterin",\n  "version": "0.0.1"\n}\n')
            with open(cli_path, "w", encoding="utf-8") as f:
                f.write('program\n  .name("flutterin")\n  .version("0.0.1");\n')
            with open(mcp_path, "w", encoding="utf-8") as f:
                f.write('const server = new Server({\n  name: "flutterin-mcp",\n  version: "0.0.1",\n});\n')

            det = detect_project_version(td)
            self.assertEqual(det.semver, "0.0.1")
            sink_paths = [s.path for s in det.sinks]
            self.assertIn("package.json", sink_paths)
            self.assertIn("plugin.json", sink_paths)
            self.assertIn("src/cli/index.ts", sink_paths)
            self.assertIn("src/mcp/index.ts", sink_paths)

            # Bump to 0.1.0
            updated = update_project_version(td, "0.1.0")
            self.assertIn("package.json", updated)
            self.assertIn("plugin.json", updated)
            self.assertIn("src/cli/index.ts", updated)
            self.assertIn("src/mcp/index.ts", updated)

            with open(pkg_path, "r", encoding="utf-8") as f:
                self.assertIn('"version": "0.1.0"', f.read())
            with open(plugin_path, "r", encoding="utf-8") as f:
                self.assertIn('"version": "0.1.0"', f.read())
            with open(cli_path, "r", encoding="utf-8") as f:
                self.assertIn('.version("0.1.0")', f.read())
            with open(mcp_path, "r", encoding="utf-8") as f:
                self.assertIn('version: "0.1.0"', f.read())

    def test_android_gradle_version_sync(self):
        """Verifies Android Gradle versionName and versionCode synchronization."""
        with tempfile.TemporaryDirectory() as td:
            app_dir = os.path.join(td, "app")
            os.makedirs(app_dir, exist_ok=True)
            g_path = os.path.join(app_dir, "build.gradle")
            with open(g_path, "w", encoding="utf-8") as f:
                f.write(
                    'defaultConfig {\n'
                    '    applicationId "com.example.app"\n'
                    '    versionCode 7\n'
                    '    versionName "2.4.0"\n'
                    '}\n'
                )

            det = detect_project_version(td)
            self.assertEqual(det.semver, "2.4.0")
            self.assertEqual(det.build_number, 7)

            # Bump to 2.4.1 (versionCode should auto-increment to 8)
            updated = update_project_version(td, "2.4.1")
            self.assertIn("app/build.gradle", updated)

            with open(g_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn('versionName "2.4.1"', content)
            self.assertIn('versionCode 8', content)

    def test_roadmap_milestone_sync(self):
        """Verifies synchronization of context/01_Product/ROADMAP.md phase milestone headings."""
        with tempfile.TemporaryDirectory() as td:
            pub_path = os.path.join(td, "pubspec.yaml")
            with open(pub_path, "w", encoding="utf-8") as f:
                f.write("name: my_app\nversion: 1.0.0+1\n")

            roadmap_dir = os.path.join(td, "context", "01_Product")
            os.makedirs(roadmap_dir, exist_ok=True)
            roadmap_path = os.path.join(roadmap_dir, "ROADMAP.md")
            with open(roadmap_path, "w", encoding="utf-8") as f:
                f.write(
                    "# Product Roadmap\n\n"
                    "### Now (v1.0.0-alpha - In Progress / Completed)\n"
                    "- Feature A\n\n"
                    "### Next (v1.1.0)\n"
                    "- Feature B\n"
                )

            det = detect_project_version(td)
            sink_paths = [s.path for s in det.sinks]
            self.assertIn("context/01_Product/ROADMAP.md", sink_paths)

            updated = update_project_version(td, "1.0.1")
            self.assertIn("context/01_Product/ROADMAP.md", updated)

            with open(roadmap_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("### Now (v1.0.1 - In Progress / Completed)", content)
            self.assertIn("### Next (v1.1.0)", content)

    def test_custom_sinks_manifest_override(self):
        """Verifies custom sinks defined in .project_manifest.json are updated."""
        with tempfile.TemporaryDirectory() as td:
            with open(os.path.join(td, "VERSION"), "w", encoding="utf-8") as f:
                f.write("0.1.0\n")

            docs_dir = os.path.join(td, "docs")
            os.makedirs(docs_dir, exist_ok=True)
            spec_path = os.path.join(docs_dir, "spec.txt")
            with open(spec_path, "w", encoding="utf-8") as f:
                f.write("System Protocol Version: 0.1.0\n")

            agents_dir = os.path.join(td, ".agents")
            os.makedirs(agents_dir, exist_ok=True)
            with open(os.path.join(agents_dir, ".project_manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"versioning": {"custom_sinks": ["docs/spec.txt"]}}, f)

            det = detect_project_version(td)
            sink_paths = [s.path for s in det.sinks]
            self.assertIn("docs/spec.txt", sink_paths)

            updated = update_project_version(td, "0.2.0")
            self.assertIn("docs/spec.txt", updated)

            with open(spec_path, "r", encoding="utf-8") as f:
                self.assertIn("System Protocol Version: 0.2.0", f.read())

    def test_multi_os_path_normalization(self):
        """Verifies that Windows backslashes and POSIX forward slashes yield identical DNA classifications."""
        tier_posix, _, slug_posix, _ = classify_file_to_tier("src/contracts/dto.py")
        tier_win, _, slug_win, _ = classify_file_to_tier("src\\contracts\\dto.py")
        self.assertEqual(tier_posix, tier_win)
        self.assertEqual(slug_posix, slug_win)
        self.assertEqual(tier_posix, "1_contracts")

    def test_uninitiated_project_detection(self):
        """Verifies that greenfield directories with no manifests are detected as uninitiated 0.0.0."""
        with tempfile.TemporaryDirectory() as td:
            det = detect_project_version(td)
            self.assertEqual(det.semver, "0.0.0")
            self.assertEqual(det.manifest, "uninitiated")
            self.assertTrue(det.is_uninitiated)
            self.assertEqual(det.release_status, "Uninitiated")

            # Updating an uninitiated project does NOT fabricate a VERSION file
            updated = update_project_version(td, "0.1.0")
            self.assertEqual(updated, [])
            self.assertFalse(os.path.exists(os.path.join(td, "VERSION")))

    def test_subfolder_repo_and_anti_framework_filter(self):
        """Verifies subfolder repo discovery and ignoring AI framework config (portable-brainvibing)."""
        with tempfile.TemporaryDirectory() as td:
            # 1. Root contains foundation gemini-extension.json
            with open(os.path.join(td, "gemini-extension.json"), "w", encoding="utf-8") as f:
                json.dump({"name": "portable-brainvibing", "version": "0.0.3"}, f)

            # 2. Subfolder contains cloned repo hermes-agent with pyproject.toml
            sub_dir = os.path.join(td, "hermes-agent")
            os.makedirs(sub_dir, exist_ok=True)
            with open(os.path.join(sub_dir, "pyproject.toml"), "w", encoding="utf-8") as f:
                f.write('[project]\nname = "hermes-agent"\nversion = "0.0.0"\n')

            det = detect_project_version(td)
            self.assertEqual(det.semver, "0.0.0")
            self.assertEqual(det.manifest, "hermes-agent/pyproject.toml")
            self.assertFalse(det.is_uninitiated)

    def test_prerelease_roadmap_phase_detection(self):
        """Verifies ROADMAP.md pre-release milestone detection sets active development phase."""
        with tempfile.TemporaryDirectory() as td:
            pub_path = os.path.join(td, "pubspec.yaml")
            with open(pub_path, "w", encoding="utf-8") as f:
                f.write("name: echont\nversion: 1.0.0+1\n")

            roadmap_dir = os.path.join(td, "context", "01_Product")
            os.makedirs(roadmap_dir, exist_ok=True)
            with open(os.path.join(roadmap_dir, "ROADMAP.md"), "w", encoding="utf-8") as f:
                f.write(
                    "# Product Roadmap\n\n"
                    "### Now (v1.0.0-alpha - In Progress / Completed)\n"
                    "- Core layout\n"
                )

            det = detect_project_version(td)
            self.assertEqual(det.semver, "1.0.0")
            self.assertEqual(det.build_number, 1)
            self.assertTrue(det.is_prerelease)
            self.assertEqual(det.phase, "v1.0.0-alpha")
            self.assertEqual(det.release_status, "In-Development (Unreleased)")

    def test_readme_and_unconventional_files_detection_and_sync(self):
        """Verifies detection and atomic syncing across README badges, version.txt, deno.json, and Makefile."""
        # 1. README.md badge detection and updating
        with tempfile.TemporaryDirectory() as td:
            rm_path = os.path.join(td, "README.md")
            with open(rm_path, "w", encoding="utf-8") as f:
                f.write(
                    "# My Custom Project\n\n"
                    "Requires Python 3.10+ and Node 18.0.0.\n\n"
                    '<a href="VERSION"><img src="https://img.shields.io/badge/version-v0.4.1-blue.svg" alt="Version"></a>\n'
                    "**Version:** 0.4.1\n"
                )
            det = detect_project_version(td)
            self.assertEqual(det.semver, "0.4.1")
            self.assertEqual(det.manifest, "README.md")

            # Update version to 0.4.2
            updated = update_project_version(td, "0.4.2")
            self.assertIn("README.md", updated)
            with open(rm_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("version-v0.4.2-blue.svg", content)
            self.assertIn("**Version:** 0.4.2", content)
            # Ensure dependency mentions remain untouched
            self.assertIn("Python 3.10+", content)
            self.assertIn("Node 18.0.0", content)

        # 2. version.txt and version.json
        with tempfile.TemporaryDirectory() as td:
            vt_path = os.path.join(td, "version.txt")
            with open(vt_path, "w", encoding="utf-8") as f:
                f.write("1.8.0\n")
            det = detect_project_version(td)
            self.assertEqual(det.semver, "1.8.0")
            self.assertEqual(det.manifest, "version.txt")

            updated = update_project_version(td, "1.8.1")
            self.assertIn("version.txt", updated)
            with open(vt_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read().strip(), "1.8.1")

        # 3. deno.json and Makefile
        with tempfile.TemporaryDirectory() as td:
            deno_path = os.path.join(td, "deno.json")
            with open(deno_path, "w", encoding="utf-8") as f:
                json.dump({"name": "deno-pkg", "version": "0.9.0"}, f)
            make_path = os.path.join(td, "Makefile")
            with open(make_path, "w", encoding="utf-8") as f:
                f.write("VERSION := 0.9.0\nall:\n\t@echo ok\n")

            det = detect_project_version(td)
            self.assertEqual(det.semver, "0.9.0")
            self.assertEqual(det.manifest, "deno.json")

            updated = update_project_version(td, "0.9.1")
            self.assertIn("deno.json", updated)
            self.assertIn("Makefile", updated)
            with open(make_path, "r", encoding="utf-8") as f:
                self.assertIn("VERSION := 0.9.1", f.read())


if __name__ == "__main__":
    unittest.main()
