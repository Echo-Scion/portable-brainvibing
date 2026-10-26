import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.verify_agents import AuditResult, check_protocol_compliance
from core.harness.admission import SovereignPromoter
from core.harness.staging import StagedIntent


class TestCoreCeilingGate(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.skills_dir = os.path.join(self.tmp_dir.name, "skills")
        os.makedirs(self.skills_dir, exist_ok=True)
        self.promoter = SovereignPromoter(skills_dir=self.skills_dir)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_core_max_lines_exceeded(self):
        skill_dir = os.path.join(self.skills_dir, "test-skill-exceed")
        os.makedirs(skill_dir, exist_ok=True)
        skill_md = os.path.join(skill_dir, "SKILL.md")

        lines = ["---", "name: test-skill-exceed", "description: Use when testing ceiling", "core_max_lines: 10", "---"]
        lines.extend([f"Line {i}" for i in range(15)])
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        res = AuditResult()
        with patch("commands.verify_agents.SKILLS_DIR", self.skills_dir):
            check_protocol_compliance(res, verbose=False)

        err_msgs = [e["message"] for e in res.errors]
        self.assertTrue(any("exceeds declared ceiling core_max_lines" in m for m in err_msgs))

    def test_core_max_lines_ratchet_warning(self):
        skill_dir = os.path.join(self.skills_dir, "test-skill-ratchet")
        os.makedirs(skill_dir, exist_ok=True)
        skill_md = os.path.join(skill_dir, "SKILL.md")

        lines = ["---", "name: test-skill-ratchet", "description: Use when testing ratchet", "core_max_lines: 200", "---"]
        lines.extend([f"Line {i}" for i in range(100)])  # 105 lines total (200 - 105 = 95 > 50)
        with open(skill_md, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        res = AuditResult()
        with patch("commands.verify_agents.SKILLS_DIR", self.skills_dir):
            check_protocol_compliance(res, verbose=False)

        warn_msgs = [w["message"] for w in res.warnings]
        self.assertTrue(any("sits >50 lines above actual count" in m for m in warn_msgs))

    def test_unquoted_colon_frontmatter_linter(self):
        intent = StagedIntent(
            id="intent_unquoted_colon",
            name="unquoted_colon_skill",
            action="create",
            level="local",
            reason="Testing unquoted colon linter",
            evidence="evidence",
            body="---\nname: unquoted_colon_skill\ndescription: Use when doing x: y\n---\n\nSkill body text.",
            files={}
        )
        ok, findings = self.promoter.validate_intent(intent, {})
        self.assertFalse(ok)
        f_ids = [f.rule_id for f in findings]
        self.assertIn("HARNESS-FM-01", f_ids)


if __name__ == "__main__":
    unittest.main()
