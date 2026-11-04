import json
import os
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.brain import compile_skill_routes, normalize_bilingual_query


class TestJitReferenceRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure fresh skill_routes.json
        compile_skill_routes()
        routes_path = os.path.join(SCRIPTS_DIR.parent.parent, ".orion", "matrix", "skill_routes.json")
        with open(routes_path, "r", encoding="utf-8") as f:
            cls.routes = json.load(f)

    def _match_query(self, query: str):
        normalized = normalize_bilingual_query(query.lower())
        scored = []
        for r in self.routes:
            score = 0
            name = r.get("name", "")
            for trig in r.get("triggers", []):
                t_low = trig.lower().strip()
                if not t_low:
                    continue
                if " " in t_low or "_" in t_low:
                    if t_low in normalized or t_low.replace("_", " ") in normalized:
                        score += 3 if t_low == name.lower() else 2
                else:
                    import re
                    if re.search(rf"\b{re.escape(t_low)}\b", normalized):
                        score += 3 if t_low == name.lower() else 1

            matched_refs = []
            for ref_item in r.get("reference_routes", []):
                ref_score = 0
                ref_path = ref_item.get("path", "")
                for r_trig in ref_item.get("triggers", []):
                    rt_low = r_trig.lower().strip()
                    if not rt_low:
                        continue
                    matched = False
                    if " " in rt_low or "_" in rt_low or "-" in rt_low:
                        if (rt_low in normalized or 
                            rt_low.replace("_", " ") in normalized or 
                            rt_low.replace("-", " ") in normalized or
                            rt_low.replace(" ", "_") in normalized):
                            matched = True
                    else:
                        import re
                        if re.search(rf"\b{re.escape(rt_low)}\b", normalized):
                            matched = True
                    if matched:
                        ref_score += 3
                if ref_score > 0:
                    matched_refs.append(ref_path)
                    score += ref_score

            if score > 0:
                scored.append((score, r, matched_refs))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def test_bilingual_ai_hallucination_routes_to_ai_llm_attacks(self):
        query = "Apakah ada keamanan untuk AI berhalusinasi package / slopsquatting?"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0, "No skills matched")
        top_score, top_skill, matched_refs = matches[0]
        self.assertGreaterEqual(top_score, 3)
        self.assertEqual(top_skill["name"], "integrity-sentinel")
        self.assertTrue(
            any("ai_llm_attacks.md" in ref for ref in matched_refs),
            f"Expected ai_llm_attacks.md in matched_refs, got: {matched_refs}"
        )

    def test_mcp_prompt_injection_routes_to_ai_llm_attacks(self):
        query = "Check MCP server prompt injection and RAG poisoning"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0)
        top_score, top_skill, matched_refs = matches[0]
        self.assertGreaterEqual(top_score, 3)
        self.assertTrue(
            any("ai_llm_attacks.md" in ref for ref in matched_refs),
            f"Expected ai_llm_attacks.md in matched_refs, got: {matched_refs}"
        )

    def test_unsafe_rust_routes_to_memory_safety(self):
        query = "Audit unsafe Rust FFI buffer overflow"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0)
        top_score, top_skill, matched_refs = matches[0]
        self.assertGreaterEqual(top_score, 3)
        self.assertTrue(
            any("memory_safety_and_binary.md" in ref for ref in matched_refs),
            f"Expected memory_safety_and_binary.md in matched_refs, got: {matched_refs}"
        )

    def test_mobile_ipc_routes_to_desktop_mobile_ipc(self):
        query = "Check Android deep link CSRF and WebView JS bridge"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0)
        top_score, top_skill, matched_refs = matches[0]
        self.assertGreaterEqual(top_score, 3)
        self.assertTrue(
            any("desktop_mobile_ipc.md" in ref for ref in matched_refs),
            f"Expected desktop_mobile_ipc.md in matched_refs, got: {matched_refs}"
        )

    def test_bento_grid_and_motion_routes_to_ui_finish_references(self):
        query = "Bikin layout bento grid dan animasi 60fps"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0)
        top_score, top_skill, matched_refs = matches[0]
        self.assertEqual(top_skill["name"], "ui-finish")
        self.assertGreaterEqual(top_score, 3)
        self.assertTrue(
            any("bento_and_macrostructures.md" in ref for ref in matched_refs) or
            any("motion_performance.md" in ref for ref in matched_refs),
            f"Expected bento or motion in matched_refs, got: {matched_refs}"
        )

    def test_literal_filename_ai_llm_attacks_matches(self):
        query = "ai_llm_attacks.md"
        matches = self._match_query(query)
        self.assertTrue(len(matches) > 0)
        top_score, top_skill, matched_refs = matches[0]
        self.assertGreaterEqual(top_score, 3)
        self.assertTrue(
            any("ai_llm_attacks.md" in ref for ref in matched_refs),
            f"Expected ai_llm_attacks.md for literal filename, got: {matched_refs}"
        )


if __name__ == "__main__":
    unittest.main()
