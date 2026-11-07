import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.capabilities import probe_capabilities


class CapabilityContractTests(unittest.TestCase):
    def test_missing_optional_tools_report_fallback_contracts(self):
        with patch("core.capabilities.shutil.which", return_value=None):
            statuses = probe_capabilities(ollama_probe=lambda: None)

        self.assertEqual(
            statuses["rtk"],
            {
                "available": False,
                "provider": "rtk",
                "version": None,
                "fallback": "python",
            },
        )
        self.assertEqual(
            statuses["ast-grep"],
            {
                "available": False,
                "provider": "ast-grep",
                "version": None,
                "fallback": "python-ast",
            },
        )
        self.assertEqual(statuses["ollama"]["fallback"], "sqlite-fts5")
        self.assertEqual(statuses["bun"]["fallback"], "host-runner")

    def test_available_binary_contracts_preserve_provider_and_version(self):
        def which(name):
            return {"rtk": "rtk.exe", "sg": "sg.exe", "bun": "bun.exe"}.get(name)

        with patch("core.capabilities.shutil.which", side_effect=which), patch(
            "core.capabilities._binary_version",
            side_effect={"rtk.exe": "1.0.0", "sg.exe": "0.9.0", "bun.exe": "1.1.0"}.get,
        ):
            statuses = probe_capabilities(ollama_probe=lambda: "http://127.0.0.1:11434")

        self.assertEqual(statuses["rtk"]["version"], "1.0.0")
        self.assertEqual(statuses["ast-grep"]["version"], "0.9.0")
        self.assertEqual(statuses["bun"]["version"], "1.1.0")
        self.assertTrue(statuses["ollama"]["available"])
        self.assertEqual(statuses["ollama"]["fallback"], None)

    def test_all_eight_pillar_combinations_never_crash(self):
        for rtk_on in (False, True):
            for ollama_on in (False, True):
                for bun_on in (False, True):
                    with self.subTest(rtk=rtk_on, ollama=ollama_on, bun=bun_on):
                        def which_mock(name):
                            if name in ("rtk", "sg", "ast-grep") and rtk_on:
                                return f"{name}.exe"
                            if name == "bun" and bun_on:
                                return "bun.exe"
                            return None

                        with patch("core.capabilities.shutil.which", side_effect=which_mock), patch(
                            "core.capabilities._binary_version", return_value="1.0.0"
                        ):
                            statuses = probe_capabilities(
                                ollama_probe=(lambda: "http://127.0.0.1:11434") if ollama_on else (lambda: None),
                                force_refresh=True,
                            )
                            self.assertTrue(statuses["pillars"]["pillar_1"]["available"])
                            self.assertEqual(statuses["pillars"]["pillar_2"]["available"], rtk_on)
                            self.assertEqual(statuses["pillars"]["pillar_3"]["available"], ollama_on)
                            self.assertEqual(statuses["pillars"]["pillar_4"]["available"], bun_on)

    def test_parse_dotenv_value_hygiene(self):
        """Verifies robust parsing of .env values with quotes and comments."""
        from core.capabilities import _parse_dotenv_value

        self.assertEqual(_parse_dotenv_value('"https://llm.chutes.ai/v1"'), "https://llm.chutes.ai/v1")
        self.assertEqual(_parse_dotenv_value("'secret_key_123'"), "secret_key_123")
        self.assertEqual(_parse_dotenv_value("sk-test-1234 # inline comment"), "sk-test-1234")
        self.assertEqual(_parse_dotenv_value('"val with # inside quotes"'), "val with # inside quotes")
        self.assertEqual(_parse_dotenv_value(""), "")

    def test_resolve_api_slot_config(self):
        """Verifies multi-provider slot resolution for Chutes and 9Router loopback."""
        import os
        from core.capabilities import resolve_api_slot_config

        # 1. Chutes slot configuration
        dummy_chutes_key = "cpk_" + "test1234567890abcdef"
        with patch.dict(os.environ, {
            "ORION_API_URL": "https://llm.chutes.ai/v1",
            "CHUTES_API_KEY": dummy_chutes_key,
            "ORION_API_MODEL_COUNCIL": "Qwen/Qwen2.5-Coder-32B-Instruct",
        }, clear=False):
            cfg = resolve_api_slot_config("council")
            self.assertEqual(cfg["base_url"], "https://llm.chutes.ai/v1")
            self.assertEqual(cfg["api_key"], dummy_chutes_key)
            self.assertEqual(cfg["model"], "Qwen/Qwen2.5-Coder-32B-Instruct")
            self.assertTrue(cfg["has_api"])

        # 2. 9Router loopback keyless resolution
        with patch.dict(os.environ, {
            "ORION_API_URL": "http://127.0.0.1:20128/v1",
            "ORION_API_KEY": "",
            "CHUTES_API_KEY": "",
            "OPENROUTER_API_KEY": "",
        }, clear=False):
            cfg = resolve_api_slot_config("fast")
            self.assertEqual(cfg["base_url"], "http://127.0.0.1:20128/v1")
            self.assertTrue(cfg["has_api"])
            self.assertTrue(cfg["api_key"])  # Placeholder key for loopback


if __name__ == "__main__":
    unittest.main()
