import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENTS = ROOT / ".agents"


class Phase6ContractSyncTests(unittest.TestCase):
    def test_runtime_contracts_are_present_in_operational_index(self):
        index = (AGENTS / "scripts" / "SCRIPTS.md").read_text(encoding="utf-8")

        self.assertIn(".orion/orion.db", index)
        self.assertIn("explicit custom DB paths", index)
        self.assertIn("shell=False", index)
        self.assertIn("probe_capabilities", index)

    def test_deployment_protocol_declares_runtime_contracts(self):
        deploy = (AGENTS / "DEPLOY_ME.md").read_text(encoding="utf-8")

        self.assertIn("foundation deploy", deploy)
        self.assertIn(".orion/orion.db", deploy)
        self.assertIn("shell=False", deploy)
        self.assertIn("probe_capabilities", deploy)

    def test_github_template_matches_native_instruction_contract(self):
        template = (AGENTS / "templates" / "github-native-structure.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`AGENTS.md` is the canonical global instruction file", template)
        self.assertIn("Do not duplicate `AGENTS.md`", template)
        self.assertIn(".agents/skills/<name>/SKILL.md", template)

    def test_governance_documents_reference_runtime_contracts(self):
        skill = (AGENTS / "skills" / "integrity-sentinel" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        rules = (AGENTS / "rules" / "prerequisites.md").read_text(encoding="utf-8")

        self.assertIn(".orion/orion.db", skill)
        self.assertIn("shell=False", skill)
        self.assertIn("probe_capabilities", skill)
        self.assertIn(".orion/orion.db", rules)
        self.assertIn("fallback", rules.lower())


if __name__ == "__main__":
    unittest.main()
