#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
test_anti_myopia_packer.py
--------------------------
Unit and regression tests verifying Anti-Myopia Contract Quarantine,
Inbound Cross-Bundle Consumer Radar, and Vector 5 Pipeline Immunity.
"""

import os
import sys
import tempfile
import unittest

# Ensure scripts dir is on sys.path
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_TESTS_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from utils.packer import (
    generate_gemini_web_audit_prompt,
    _build_global_cross_bundle_router,
    extract_cross_bundle_dependency_edges,
    extract_cross_bundle_imports,
)


class TestAntiMyopiaPacker(unittest.TestCase):
    def test_gemini_web_audit_prompt_quarantine(self):
        """Verifies Turn 1-3 contract freeze, Turn 1 dead-end removal, Turn 4 seam synthesis, and Rule 9."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            bundle_files = [
                ("01_CORE", "Core Architecture", 10, 50.0, "Core invariants"),
                ("02_LOGIC", "Business Logic", 15, 80.0, "State execution"),
                ("03_ADAPTERS", "Persistence & API", 8, 40.0, "Data connectors"),
            ]
            prompt_path = generate_gemini_web_audit_prompt(
                out_dir=tmp_dir,
                project_name="TestProject",
                tier_label="AUDIT",
                bundle_files=bundle_files,
                total_tokens=150000,
            )

            self.assertTrue(os.path.isfile(prompt_path))
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Rule 9 Verification
            self.assertIn("9. **Cross-File Pipeline Contract Immunity (Anti-Myopia Mandate)**:", content)
            self.assertIn("Pipeline Contract Protection", content)
            self.assertIn("Call-Site Blast Radius Proof", content)

            # Turn 1 should NOT contain Dead-End Pipelines
            turn1_split = content.split("#### 📋 Turn 2")[0]
            self.assertNotIn("Dead-End Pipelines & Ghost Subsystems", turn1_split)
            self.assertNotIn("Flag any unwired command", turn1_split)

            # Turns 1, 2, 3 must contain Local Contract Freeze Law
            self.assertIn("LOCAL CONTRACT FREEZE LAW (ANTI-MYOPIA INVARIANT)", content)
            self.assertIn("Signature & Contract Lock", content)
            self.assertIn("No Isolated Dead-Code Claims", content)

            # Turn 4 must contain Cross-Bundle Seams & Pipeline Integrity
            turn4_split = content.split("#### 📋 Turn 4")[1]
            self.assertIn("Cross-Bundle Seams & Pipeline Integrity", turn4_split)
            self.assertIn("Dead-End Pipelines & Ghost Subsystems", turn4_split)
            self.assertIn("Call-Site Blast Radius Mandate", turn4_split)

    def test_cross_bundle_dependency_edges_and_inbound_router(self):
        """Verifies that cross-bundle edges identify target files and build inbound consumer columns."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create two files across bundle boundaries
            prod_path = os.path.join(tmp_dir, "core_engine.py")
            cons_path = os.path.join(tmp_dir, "app_service.py")

            with open(prod_path, "w", encoding="utf-8") as f:
                f.write("def calculate_tax(amount, rate=0.1):\n    return amount * rate\n")

            with open(cons_path, "w", encoding="utf-8") as f:
                f.write("from core_engine import calculate_tax\n\ndef run():\n    return calculate_tax(100)\n")

            file_to_bundle = {
                "core_engine.py": "01_CORE",
                "app_service.py": "02_SERVICES",
            }

            # Test edge extraction
            with open(cons_path, "r", encoding="utf-8") as f:
                cons_raw = f.read()
            edges = extract_cross_bundle_dependency_edges("app_service.py", cons_raw, file_to_bundle)
            self.assertTrue(len(edges) >= 1)
            t_fp, t_bid, label = edges[0]
            self.assertEqual(t_fp, "core_engine.py")
            self.assertEqual(t_bid, "01")

            # Test backward-compatible extract_cross_bundle_imports
            imports = extract_cross_bundle_imports("app_service.py", cons_raw, file_to_bundle)
            self.assertTrue(any("(Bundle 01)" in imp for imp in imports))

            # Test router output
            router_md = _build_global_cross_bundle_router(tmp_dir, file_to_bundle)
            self.assertIn("Inbound Consumers (Dependents)", router_md)
            self.assertIn("Outbound Cross-Bundle Imports", router_md)
            self.assertIn("`app_service.py` (Bundle 02)", router_md)

    def test_critical_producer_flag(self):
        """Verifies that a producer with >= 2 inbound consumers receives the critical producer warning."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            prod_path = os.path.join(tmp_dir, "schema.py")
            cons1_path = os.path.join(tmp_dir, "client_a.py")
            cons2_path = os.path.join(tmp_dir, "client_b.py")

            with open(prod_path, "w", encoding="utf-8") as f:
                f.write("class UserDTO:\n    pass\n")

            with open(cons1_path, "w", encoding="utf-8") as f:
                f.write("from schema import UserDTO\n")

            with open(cons2_path, "w", encoding="utf-8") as f:
                f.write("from schema import UserDTO\n")

            file_to_bundle = {
                "schema.py": "01_CONTRACTS",
                "client_a.py": "02_CLIENTS",
                "client_b.py": "03_CONSUMERS",
            }

            router_md = _build_global_cross_bundle_router(tmp_dir, file_to_bundle)
            self.assertIn("[CRITICAL PRODUCER]", router_md)

    def test_audit_vectors_exemption(self):
        """Verifies that audit_vectors.md contains the Vector 5 Cross-File Pipeline Contract Exemption."""
        workspace_root = os.path.dirname(os.path.dirname(_SCRIPTS_DIR))
        audit_vectors_path = os.path.join(
            workspace_root, ".agents", "skills", "integrity-sentinel", "references", "audit_vectors.md"
        )
        self.assertTrue(os.path.isfile(audit_vectors_path))
        with open(audit_vectors_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Cross-File Pipeline Contract Exemption", content)
        self.assertIn("CMD_MAP", content)


if __name__ == "__main__":
    unittest.main()
