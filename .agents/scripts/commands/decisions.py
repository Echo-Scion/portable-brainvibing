# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Native Architectural Decision Ledger & Zero-Stall Execution Tracker.
Extracts, records, and tracks plan design trade-offs and resolutions.
Pure Python standard library; zero host-IDE coupling.
"""

import os
import sys
import re
import json
import argparse
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

if getattr(sys.stdout, "encoding", None) and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

from core.db import atomic_write_text, log_telemetry as _log_telemetry
from core.paths import get_workspace_dir, get_orion_dir, get_agents_dir

WORKSPACE_DIR = Path(get_workspace_dir())
ORION_DIR = Path(get_orion_dir())
AGENTS_DIR = Path(get_agents_dir())

LEDGER_JSON_PATH = ORION_DIR / "working" / "decision_ledger.json"
DECISIONS_MD_PATH = AGENTS_DIR / "DECISIONS.md"


def get_ledger_data(workspace_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load existing decision ledger JSON from .orion/working/."""
    ws = workspace_root or WORKSPACE_DIR
    path = ws / ".orion" / "working" / "decision_ledger.json"
    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            _log_telemetry(e, "decisions:get_ledger_data")
    return {"version": "1.0.0", "decisions": {}}


def save_ledger_data(ledger: Dict[str, Any], workspace_root: Optional[Path] = None) -> None:
    """Save decision ledger JSON atomically to .orion/working/."""
    ws = workspace_root or WORKSPACE_DIR
    path = ws / ".orion" / "working" / "decision_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(str(path), json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")


def render_decisions_markdown(ledger: Dict[str, Any]) -> str:
    """Render human-readable living markdown table for .agents/DECISIONS.md."""
    decisions = ledger.get("decisions", {})
    rows = []
    for dec_id in sorted(decisions.keys()):
        item = decisions[dec_id]
        plan = item.get("plan", "plan.md")
        topic = item.get("topic", "Architectural Decision")
        res = item.get("resolution") or "Pending"
        res_display = res.replace("|", "\\|")
        if len(res_display) > 60:
            res_display = res_display[:57] + "..."
        status = item.get("status", "PENDING")
        date = item.get("timestamp", "")[:10] or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        rows.append(f"| `{dec_id}` | `{plan}` | {topic} | `{res_display}` | `{status}` | {date} |")

    table_body = "\n".join(rows) if rows else "| _None_ | _None_ | _No decisions recorded yet_ | - | - | - |"

    return (
        "# 🏛️ Architectural Decision Records (.agents/DECISIONS.md)\n\n"
        "> Canonical living ledger of design trade-offs and plan resolutions across .agents.\n"
        "> Maintained automatically via `python .agents/scripts/orion.py decisions`.\n\n"
        "| ID | Plan | Topic | Chosen Resolution | Status | Date |\n"
        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"{table_body}\n"
    )


def sync_decisions_markdown(ledger: Dict[str, Any], workspace_root: Optional[Path] = None) -> None:
    """Update .agents/DECISIONS.md with latest state."""
    ws = workspace_root or WORKSPACE_DIR
    path = ws / ".agents" / "DECISIONS.md"
    content = render_decisions_markdown(ledger)
    atomic_write_text(str(path), content)


def extract_decisions_from_markdown(
    markdown_text: str,
    plan_name: str = "plan.md",
    auto_resolve_recommended: bool = True,
    date_prefix: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Parse questions, options, and recommended selections from markdown text.
    Handles '## Open Questions', '## User Review Required', 'Q1: ...', etc.
    """
    decisions: List[Dict[str, Any]] = []
    today = date_prefix or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")

    # Scope candidates to target sections if present
    section_pat = re.compile(
        r"(?ims)(?:##\s*(?:\d+[\.\)]\s*)?(?:Open Questions|User Review Required|Decisions Needed|Trade-offs?)|Two decisions I need from you).*?(?=\n##\s+|\Z)"
    )
    section_matches = list(section_pat.finditer(markdown_text))
    scope_blocks = [m.group(0) for m in section_matches] if section_matches else [markdown_text]

    counter = 1
    for block in scope_blocks:
        # Detect individual question blocks
        # e.g., "**Q1: ...**" or "Q1: ..." or "**1. Topic**: ..."
        q_regex = re.compile(
            r"(?m)(?:^>\s*\[!(?:IMPORTANT|WARNING|NOTE)\]\s*\n>\s*)?(?:(?:\*\*|\b)Q\d+:|\*\*\d+[\.\)]\s*)\s*([^\n\*]+?)(?:\*\*)?(?:\n|$)"
        )
        splits = list(q_regex.finditer(block))
        if not splits:
            continue

        for i, match in enumerate(splits):
            start = match.start()
            end = splits[i + 1].start() if i + 1 < len(splits) else len(block)
            raw_chunk = block[start:end]

            # Skip markdown section headers (e.g., ## 1. Goal Description)
            first_line = raw_chunk.splitlines()[0].strip() if raw_chunk.splitlines() else ""
            if first_line.startswith("#"):
                continue

            raw_question = match.group(1).strip().strip(":")
            # Options list items
            option_lines = re.findall(r"(?m)^\s*(?:>\s*)?[-*]\s+(.*)$", raw_chunk)
            clean_options = []
            recommended_opt = None

            for opt in option_lines:
                clean_opt = opt.strip()
                if clean_opt.startswith("**") and clean_opt.endswith("**"):
                    clean_opt = clean_opt[2:-2].strip()
                clean_options.append(clean_opt)
                if "(recommended)" in clean_opt.lower():
                    recommended_opt = clean_opt

            if not clean_options and not recommended_opt:
                continue

            dec_id = f"DEC-{today}-{counter:02d}"
            counter += 1

            topic = raw_question
            if "?" in topic:
                topic = topic.split("?")[0].strip()
            if len(topic) > 60:
                topic = topic[:57] + "..."

            status = "PENDING"
            resolution = ""
            if auto_resolve_recommended and recommended_opt:
                status = "RESOLVED_RECOMMENDED"
                resolution = recommended_opt

            decisions.append({
                "id": dec_id,
                "plan": os.path.basename(plan_name),
                "topic": topic,
                "question": raw_question,
                "options": clean_options,
                "status": status,
                "resolution": resolution,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

    return decisions


def record_plan_decisions(
    plan_path_or_text: str,
    auto_resolve: bool = True,
    workspace_root: Optional[Path] = None,
    plan_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Record decisions from a plan file or text payload into ledger and DECISIONS.md."""
    ws = workspace_root or WORKSPACE_DIR
    text = ""
    source_name = plan_name or "plan.md"

    # Check if input is a filepath
    target_path = Path(plan_path_or_text)
    if not target_path.is_absolute():
        candidate = ws / plan_path_or_text
        if candidate.is_file():
            target_path = candidate

    if target_path.is_file():
        source_name = target_path.name
        with open(target_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = plan_path_or_text

    extracted = extract_decisions_from_markdown(
        text,
        plan_name=source_name,
        auto_resolve_recommended=auto_resolve
    )

    if not extracted:
        return []

    ledger = get_ledger_data(ws)
    existing = ledger.setdefault("decisions", {})

    for item in extracted:
        # Avoid duplicate questions for the same plan
        found_existing = False
        for ex_id, ex_item in existing.items():
            if ex_item.get("plan") == item["plan"] and ex_item.get("question") == item["question"]:
                # Update existing if newly resolved
                if item["status"] != "PENDING" and ex_item.get("status") == "PENDING":
                    ex_item["status"] = item["status"]
                    ex_item["resolution"] = item["resolution"]
                    ex_item["timestamp"] = item["timestamp"]
                item["id"] = ex_id
                found_existing = True
                break

        if not found_existing:
            existing[item["id"]] = item

    save_ledger_data(ledger, ws)
    sync_decisions_markdown(ledger, ws)
    return extracted


def cmd_record(args: argparse.Namespace) -> int:
    plan_input = args.plan
    if not plan_input:
        if not sys.stdin.isatty():
            plan_input = sys.stdin.read()
        else:
            sys.stderr.write("[ERROR] Must provide --plan <file> or pipe text through stdin.\n")
            return 1

    extracted = record_plan_decisions(
        plan_input,
        auto_resolve=not args.no_auto_resolve,
        plan_name=args.name
    )

    if not extracted:
        print("[INFO] No decision points (Open Questions / User Review) detected in plan.")
        return 0

    print(f"[OK] Recorded {len(extracted)} decision(s) into .orion/working/decision_ledger.json & .agents/DECISIONS.md:")
    for d in extracted:
        print(f"  • {d['id']}: {d['topic']} -> [{d['status']}] {d['resolution']}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    ledger = get_ledger_data()
    decisions = ledger.get("decisions", {})
    if not decisions:
        print("[INFO] No decisions currently recorded in ledger.")
        return 0

    filter_st = (args.status or "all").lower()
    print(f"\n🏛️  ARCHITECTURAL DECISION LEDGER ({len(decisions)} total):")
    print(f"{'ID':<18} {'STATUS':<22} {'PLAN':<25} {'TOPIC'}")
    print("-" * 85)

    count = 0
    for dec_id in sorted(decisions.keys()):
        d = decisions[dec_id]
        st = d.get("status", "PENDING")
        if filter_st != "all" and st.lower() != filter_st:
            continue
        count += 1
        plan = d.get("plan", "")
        topic = d.get("topic", "")
        print(f"{dec_id:<18} {st:<22} {plan:<25} {topic}")

    print("-" * 85)
    print(f"Displaying {count} decision(s).\n")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    dec_id = args.id
    choice = args.choice
    ledger = get_ledger_data()
    decisions = ledger.get("decisions", {})

    if dec_id not in decisions:
        sys.stderr.write(f"[ERROR] Decision ID '{dec_id}' not found in ledger.\n")
        return 1

    decisions[dec_id]["status"] = "RESOLVED_BY_USER"
    decisions[dec_id]["resolution"] = choice
    decisions[dec_id]["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    save_ledger_data(ledger)
    sync_decisions_markdown(ledger)
    print(f"[OK] Decision {dec_id} updated to RESOLVED_BY_USER: '{choice}'")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """Audit active ledger for pending or unresolved decisions."""
    ledger = get_ledger_data()
    decisions = ledger.get("decisions", {})
    pending = [d for d in decisions.values() if d.get("status") == "PENDING"]

    print(f"\n--- DECISION AUDIT GATE ---")
    print(f"Total decisions recorded : {len(decisions)}")
    print(f"Pending resolutions      : {len(pending)}")

    if pending:
        print("\n⚠️  PENDING ARCHITECTURAL DECISIONS:")
        for p in pending:
            print(f"  • {p['id']} [{p['plan']}]: {p['question']}")
            for opt in p.get("options", []):
                print(f"      - {opt}")
        print("\nResolve them using: python .agents/scripts/orion.py decisions resolve <id> '<choice>'")
        return 1

    print("[PASS] Zero unresolved decisions. All plan choices recorded and accounted for.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="orion decisions",
        description="Native Architectural Decision Ledger & Zero-Stall Execution Tracker."
    )
    sub = parser.add_subparsers(dest="action")

    # record
    p_rec = sub.add_parser("record", help="Extract and record decisions from a plan markdown file or text.")
    p_rec.add_argument("--plan", "-p", help="Path to markdown plan file.")
    p_rec.add_argument("--name", "-n", help="Optional name label for the plan.")
    p_rec.add_argument("--no-auto-resolve", action="store_true", help="Do not auto-resolve options tagged (Recommended).")

    # list
    p_list = sub.add_parser("list", help="List recorded decisions.")
    p_list.add_argument("--status", "-s", default="all", choices=["all", "pending", "resolved_recommended", "resolved_by_user"], help="Filter by status.")

    # resolve
    p_res = sub.add_parser("resolve", help="Manually resolve a pending decision.")
    p_res.add_argument("id", help="Decision ID (e.g. DEC-20261103-01).")
    p_res.add_argument("choice", help="Selected resolution text.")

    # audit
    sub.add_parser("audit", help="Audit ledger for pending or unresolved decisions.")

    args = parser.parse_args(argv)
    if not args.action:
        parser.print_help()
        return 0

    if args.action == "record":
        return cmd_record(args)
    elif args.action == "list":
        return cmd_list(args)
    elif args.action == "resolve":
        return cmd_resolve(args)
    elif args.action == "audit":
        return cmd_audit(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
