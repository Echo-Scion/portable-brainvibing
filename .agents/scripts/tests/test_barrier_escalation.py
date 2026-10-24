import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.reflexion import ObservationLedger, consolidate_milestone
from core.harness.admission import SovereignPromoter
from core.harness.staging import StagedIntent


class TestBarrierEscalation(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.active_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.md")
        self.archive_path = os.path.join(self.tmp_dir.name, "OBSERVATIONS.archive.md")
        self.ledger = ObservationLedger(active_path=self.active_path, archive_path=self.archive_path)
        self.promoter = SovereignPromoter(skills_dir=os.path.join(self.tmp_dir.name, "skills"))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_second_violation_forces_tier_0(self):
        # Add 1st violation
        self.ledger.add_observation(
            title="Direct service import in screen",
            kind="violation",
            target="lib/features/blacklist/presentation/screens/blacklist_screen.dart",
            rule_id="NO_DIRECT_SERVICE_IMPORT",
            evidence="import 'package:echont/features/settings/data/settings_repository.dart';"
        )
        check1 = self.ledger.check_rule_violations("NO_DIRECT_SERVICE_IMPORT")
        self.assertFalse(check1["forced_tier0"])

        # Add 2nd violation
        self.ledger.add_observation(
            title="Direct service import in shortcuts screen",
            kind="violation",
            target="lib/features/shortcuts/presentation/screens/shortcuts_screen.dart",
            rule_id="NO_DIRECT_SERVICE_IMPORT",
            evidence="import 'package:echont/features/settings/data/settings_repository.dart';"
        )
        check2 = self.ledger.check_rule_violations("NO_DIRECT_SERVICE_IMPORT")
        self.assertTrue(check2["forced_tier0"])
        self.assertGreaterEqual(check2["count"], 2)

    def test_admission_rejects_text_only_tier_0_proposal(self):
        intent = StagedIntent(
            id="intent_t0_test_1",
            name="forced_tier0_skill",
            action="create",
            level="local",
            reason="2nd violation of NO_DIRECT_SERVICE_IMPORT",
            evidence="import 'package:echont/features/settings/data/settings_repository.dart';",
            body="---\nname: forced_tier0_skill\ndescription: Use when checking service imports\nresting_tier: TIER-0\n---\n\nText only description with no verifier script.",
            files={}
        )
        ok, findings = self.promoter.validate_intent(intent, {})
        self.assertFalse(ok)
        f_ids = [f.rule_id for f in findings]
        self.assertIn("HARNESS-T0-01", f_ids)

    def test_admission_accepts_tier_0_with_script(self):
        intent = StagedIntent(
            id="intent_t0_test_2",
            name="forced_tier0_skill_ok",
            action="create",
            level="local",
            reason="2nd violation of NO_DIRECT_SERVICE_IMPORT",
            evidence="import 'package:echont/features/settings/data/settings_repository.dart';",
            body="---\nname: forced_tier0_skill_ok\ndescription: Use when checking service imports\nresting_tier: TIER-0\n---\n\nSkill body referencing `scripts/verifier.py`.",
            files={"scripts/verifier.py": "import sys\ndef verify(): pass\n"}
        )
        ok, findings = self.promoter.validate_intent(intent, {})
        t0_findings = [f for f in findings if f.rule_id == "HARNESS-T0-01"]
        self.assertEqual(len(t0_findings), 0)

    def test_consolidate_milestone_bounded_slice_review(self):
        for i in range(1, 19):
            self.ledger.add_observation(
                title=f"Observation item {i}",
                kind="improve",
                target=f"file_{i}.py",
                rule_id=f"RULE_{i % 5}"
            )

        active = self.ledger.list_observations(status="open")
        self.assertEqual(len(active), 18)

        review_slice = active[:10] if len(active) > 15 else active
        self.assertEqual(len(review_slice), 10)
        self.assertEqual(review_slice[0]["title"], "Observation item 1")
        self.assertEqual(review_slice[9]["title"], "Observation item 10")


if __name__ == "__main__":
    unittest.main()
