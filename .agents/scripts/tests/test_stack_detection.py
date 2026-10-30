import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands.foundation import (
    _read_python_deps,
    _python_profile,
    get_stack_defaults,
    prune_unmatched_canons,
    resolve_template_string,
    TEMPLATE_VARS,
)


class TestStackDetection(unittest.TestCase):
    def setUp(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.test_dir = self._temp_dir_obj.name

    def tearDown(self):
        self._temp_dir_obj.cleanup()

    def test_read_python_deps_requirements_and_comments(self):
        req_path = os.path.join(self.test_dir, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(
                "# This is a comment mentioning fastapi\n"
                "ccxt>=4.0.0\n"
                "SQLAlchemy==2.0.20\n"
                "pydantic>=2.0.0\n"
                "optuna\n"
                "pytest-asyncio\n"
                "redis\n"
            )
        deps = _read_python_deps(self.test_dir)
        self.assertIn("ccxt", deps)
        self.assertIn("sqlalchemy", deps)
        self.assertIn("pydantic", deps)
        self.assertIn("optuna", deps)
        self.assertIn("redis", deps)
        self.assertNotIn("fastapi", deps)

    def test_read_python_deps_pyproject_toml(self):
        pyproj_path = os.path.join(self.test_dir, "pyproject.toml")
        with open(pyproj_path, "w", encoding="utf-8") as f:
            f.write(
                '[project]\n'
                'dependencies = [\n'
                '    "fastapi>=0.100.0",\n'
                '    "uvicorn[standard]",\n'
                ']\n'
            )
        deps = _read_python_deps(self.test_dir)
        self.assertIn("fastapi", deps)
        self.assertIn("uvicorn", deps)

    def test_python_profile_scionlog_shape_headless(self):
        deps = {"ccxt", "sqlalchemy", "pydantic", "optuna", "redis"}
        profile = _python_profile(deps, has_ui=False)
        self.assertEqual(profile["frontend_framework"], "Headless / CLI / Daemon")
        self.assertEqual(profile["ui_framework"], "None (headless / CLI)")
        self.assertIn("SQLAlchemy", profile["backend_persistence"])
        self.assertIn("SQLite", profile["backend_persistence"])
        self.assertIn("Pydantic", profile["state_management"])
        self.assertNotIn("FastAPI", profile["frontend_framework"])
        self.assertNotIn("Tailwind", profile["ui_framework"])

    def test_python_profile_fastapi_with_ui(self):
        deps = {"fastapi", "sqlalchemy", "pydantic"}
        profile = _python_profile(deps, has_ui=True)
        self.assertEqual(profile["frontend_framework"], "FastAPI")
        self.assertEqual(profile["ui_framework"], "HTML / Tailwind CSS")

    def test_template_vars_no_riverpod_in_neutral_defaults(self):
        self.assertNotIn("riverpod", TEMPLATE_VARS["decision_1_title"].lower())
        self.assertNotIn("riverpod", TEMPLATE_VARS["decision_1_logic"].lower())
        self.assertNotIn("autodispose", TEMPLATE_VARS["knowledge_1"].lower())

    def test_get_stack_defaults_flutter_gets_riverpod_adr(self):
        defaults = get_stack_defaults("flutter", "dart")
        self.assertIn("Riverpod", defaults.get("decision_1_title", ""))
        self.assertIn("AutoDispose", defaults.get("knowledge_1", ""))

    def test_get_stack_defaults_python_no_riverpod_adr(self):
        req_path = os.path.join(self.test_dir, "requirements.txt")
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("ccxt\nSQLAlchemy\n")
        defaults = get_stack_defaults("python", "python", target_dir=self.test_dir)
        self.assertNotIn("Riverpod", defaults.get("decision_1_title", ""))
        self.assertEqual(defaults["frontend_framework"], "Headless / CLI / Daemon")

    def test_prune_unmatched_canons_micro(self):
        agents_dir = os.path.join(self.test_dir, ".agents")
        micro_dir = os.path.join(agents_dir, "canons", "micro")
        os.makedirs(micro_dir, exist_ok=True)
        for fname in ["flutter.md", "pubspec.md", "react.md", "python.md", "supabase.md", "README.md"]:
            with open(os.path.join(micro_dir, fname), "w", encoding="utf-8") as f:
                f.write("# Dummy canon\n")

        prune_unmatched_canons(agents_dir, active_framework="python")
        remaining = os.listdir(micro_dir)
        self.assertIn("python.md", remaining)
        self.assertIn("README.md", remaining)
        self.assertNotIn("flutter.md", remaining)
        self.assertNotIn("pubspec.md", remaining)
        self.assertNotIn("react.md", remaining)
        self.assertNotIn("supabase.md", remaining)


if __name__ == "__main__":
    unittest.main()
