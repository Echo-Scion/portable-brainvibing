"""
Tests for Tier 2 Optional Ephemeral Accelerators subsystem.
Verifies discovery, fast JSON serialization, fuzzy string matching,
and graceful degradation to standard library floor (Zero-Pip baseline).
"""

import os
import sys
import unittest

# Ensure .agents/scripts is on sys.path
SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from core.accelerators import (
    bootstrap_accelerators,
    get_accelerator_status,
    fast_json_dumps,
    fast_json_loads,
    fuzzy_ratio,
    fuzzy_find_best,
    HAS_ORJSON,
    HAS_RAPIDFUZZ,
    HAS_TREE_SITTER,
)


class TestTier2Accelerators(unittest.TestCase):
    def test_bootstrap_and_status(self):
        """Verify accelerator status payload structure and bootstrap integrity."""
        status = get_accelerator_status()
        self.assertIn("tier", status)
        self.assertIn("accelerators", status)
        self.assertIn("active_count", status)
        self.assertEqual(status["tier"], "Tier 2: Optional Ephemeral Accelerators")

        acc = status["accelerators"]
        self.assertIn("orjson", acc)
        self.assertIn("rapidfuzz", acc)
        self.assertIn("tree-sitter", acc)

        # Check each accelerator contract
        for name in ("orjson", "rapidfuzz", "tree-sitter"):
            item = acc[name]
            self.assertIn("available", item)
            self.assertIn("role", item)
            self.assertIn("fallback", item)
            if not item["available"]:
                self.assertIsNotNone(item["fallback"])

    def test_fast_json_roundtrip(self):
        """Verify fast JSON serialization and deserialization matches expected data."""
        sample_payload = {
            "name": "foundation",
            "version": "0.0.2",
            "tags": ["zero-pip", "accelerators", "sovereign"],
            "count": 42,
            "nested": {"active": True, "ratio": 0.85},
        }

        # Compact serialization
        raw_compact = fast_json_dumps(sample_payload, indent=False)
        self.assertIsInstance(raw_compact, str)
        decoded = fast_json_loads(raw_compact)
        self.assertEqual(decoded, sample_payload)

        # Indented serialization
        raw_indented = fast_json_dumps(sample_payload, indent=True)
        self.assertIn("\n", raw_indented)
        decoded_indented = fast_json_loads(raw_indented)
        self.assertEqual(decoded_indented, sample_payload)

    def test_fuzzy_matching_operations(self):
        """Verify fuzzy ratio and best match search work accurately."""
        # Exact match
        self.assertAlmostEqual(fuzzy_ratio("performance", "performance"), 1.0, places=2)

        # High similarity
        sim = fuzzy_ratio("performance", "perforamnce")
        self.assertGreater(sim, 0.8)

        # Dissimilar
        low_sim = fuzzy_ratio("performance", "completely_different")
        self.assertLess(low_sim, 0.4)

        # Best candidate selection
        candidates = ["performance_optimization", "security_baseline", "code_review", "strict_tdd"]
        match = fuzzy_find_best("performance", candidates, cutoff=0.5)
        self.assertIsNotNone(match)
        self.assertEqual(match[0], "performance_optimization")
        self.assertGreater(match[1], 0.5)

        # Unmatched query below cutoff
        no_match = fuzzy_find_best("unknown_term_xyz", candidates, cutoff=0.8)
        self.assertIsNone(no_match)

    def test_zero_pip_graceful_fallback_invariants(self):
        """Verify that fallback functions never raise uncaught exceptions."""
        # Test serialization of various edge case types
        edge_cases = [{}, [], {"unicode": "こんにちは", "emoji": "⚡"}]
        for ec in edge_cases:
            serialized = fast_json_dumps(ec)
            self.assertEqual(fast_json_loads(serialized), ec)

        # Test fuzzy with empty lists
        self.assertIsNone(fuzzy_find_best("target", [], cutoff=0.5))

    def test_opt_in_polyglot_ephemeral_primitives(self):
        """Verify Opt-In Rust and Bun ephemeral execution abstractions."""
        from core.accelerators import (
            find_bun_bin,
            find_ast_grep_bin,
            find_rtk_bin,
            run_ephemeral_bunx,
            run_ephemeral_ast_grep,
        )

        status = get_accelerator_status()
        self.assertIn("opt_in_pillars", status)
        self.assertIn("rust_fabric", status["opt_in_pillars"])
        self.assertIn("bun_fabric", status["opt_in_pillars"])

        # Test Bun ephemeral execution
        bun_res = run_ephemeral_bunx("--version")
        self.assertIn(bun_res["status"], ("SUCCESS", "DEGRADED_FALLBACK"))

        # Test ast-grep ephemeral execution
        sg_res = run_ephemeral_ast_grep("def normalize_path($$$): $$$", "python", ".agents/scripts/core/paths.py")
        self.assertIn(sg_res["status"], ("SUCCESS", "DEGRADED_FALLBACK"))


if __name__ == "__main__":
    unittest.main()
