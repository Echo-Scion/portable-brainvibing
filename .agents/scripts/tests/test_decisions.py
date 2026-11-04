import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.decisions import (
    extract_decisions_from_markdown,
    record_plan_decisions,
    get_ledger_data,
    save_ledger_data,
    render_decisions_markdown,
    sync_decisions_markdown
)


SAMPLE_PLAN_MARKDOWN = """
# Plan: Test Feature

## 1. Goal Description
Some description here.

## 2. Open Questions

> [!IMPORTANT]
> **Q1: Which storage engine should we use?**
> - (Recommended) Option A: SQLite embedded (Zero-Pip)
> - Option B: PostgreSQL Docker container

> [!IMPORTANT]
> **Q2: Cache invalidation strategy?**
> - Option 1: TTL based (5 minutes)
> - Option 2: Event driven webhook

## 3. Proposed Changes
Some changes.
"""


class TestDecisions(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.tmp_dir.name)
        (self.workspace_root / ".orion" / "working").mkdir(parents=True, exist_ok=True)
        (self.workspace_root / ".agents").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_decisions_auto_recommended(self):
        decisions = extract_decisions_from_markdown(
            SAMPLE_PLAN_MARKDOWN,
            plan_name="test_plan.md",
            auto_resolve_recommended=True,
            date_prefix="20261103"
        )
        self.assertEqual(len(decisions), 2)

        d1 = decisions[0]
        self.assertEqual(d1["id"], "DEC-20261103-01")
        self.assertIn("Which storage engine", d1["question"])
        self.assertEqual(d1["status"], "RESOLVED_RECOMMENDED")
        self.assertIn("SQLite embedded", d1["resolution"])
        self.assertEqual(len(d1["options"]), 2)

        d2 = decisions[1]
        self.assertEqual(d2["id"], "DEC-20261103-02")
        self.assertIn("Cache invalidation", d2["question"])
        self.assertEqual(d2["status"], "PENDING")
        self.assertEqual(d2["resolution"], "")

    def test_record_plan_decisions_persists_ledger_and_markdown(self):
        plan_file = self.workspace_root / "sample_plan.md"
        plan_file.write_text(SAMPLE_PLAN_MARKDOWN, encoding="utf-8")

        recorded = record_plan_decisions(
            str(plan_file),
            auto_resolve=True,
            workspace_root=self.workspace_root
        )
        self.assertEqual(len(recorded), 2)

        # Check JSON ledger
        ledger_path = self.workspace_root / ".orion" / "working" / "decision_ledger.json"
        self.assertTrue(ledger_path.is_file())
        with open(ledger_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("decisions", data)
        self.assertEqual(len(data["decisions"]), 2)

        # Check DECISIONS.md
        dec_md_path = self.workspace_root / ".agents" / "DECISIONS.md"
        self.assertTrue(dec_md_path.is_file())
        md_text = dec_md_path.read_text(encoding="utf-8")
        self.assertIn("Architectural Decision Records", md_text)
        self.assertIn("RESOLVED_RECOMMENDED", md_text)
        self.assertIn("SQLite embedded", md_text)

    def test_deduplication_on_repeated_records(self):
        plan_file = self.workspace_root / "sample_plan.md"
        plan_file.write_text(SAMPLE_PLAN_MARKDOWN, encoding="utf-8")

        # 1st record
        rec1 = record_plan_decisions(str(plan_file), auto_resolve=True, workspace_root=self.workspace_root)
        self.assertEqual(len(rec1), 2)

        # 2nd record on identical content
        rec2 = record_plan_decisions(str(plan_file), auto_resolve=True, workspace_root=self.workspace_root)
        self.assertEqual(len(rec2), 2)

        # Ledger must still only contain 2 decisions, not 4
        ledger = get_ledger_data(self.workspace_root)
        self.assertEqual(len(ledger["decisions"]), 2)

    def test_markdown_rendering_escapes_pipes(self):
        ledger = {
            "version": "1.0.0",
            "decisions": {
                "DEC-01": {
                    "id": "DEC-01",
                    "plan": "p.md",
                    "topic": "Topic A",
                    "resolution": "Option with | pipe character",
                    "status": "RESOLVED",
                    "timestamp": "2026-11-03T00:00:00Z"
                }
            }
        }
        md = render_decisions_markdown(ledger)
        self.assertIn(r"Option with \| pipe character", md)

    def test_manual_resolve_decision(self):
        plan_file = self.workspace_root / "sample_plan.md"
        plan_file.write_text(SAMPLE_PLAN_MARKDOWN, encoding="utf-8")
        record_plan_decisions(str(plan_file), auto_resolve=True, workspace_root=self.workspace_root)

        ledger = get_ledger_data(self.workspace_root)
        # Update DEC-xxx-02 (the pending one)
        d2_id = [k for k, v in ledger["decisions"].items() if v["status"] == "PENDING"][0]
        ledger["decisions"][d2_id]["status"] = "RESOLVED_BY_USER"
        ledger["decisions"][d2_id]["resolution"] = "Option 1: TTL based"
        save_ledger_data(ledger, self.workspace_root)
        sync_decisions_markdown(ledger, self.workspace_root)

        # Check updated markdown
        md_text = (self.workspace_root / ".agents" / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("RESOLVED_BY_USER", md_text)
        self.assertIn("Option 1: TTL based", md_text)


if __name__ == "__main__":
    unittest.main()
