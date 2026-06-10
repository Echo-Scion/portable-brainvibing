"""
Harness: Supabase Migration Verifier
Purpose: Validate a SQL migration file before executing it against the database.
         Detects destructive ops, missing RLS, missing WHERE clauses, and schema violations.
Usage:
    python .agents/canons/global/harnesses/migration_verifier.py --file supabase/migrations/001_init.sql
Output Contract: action_id, is_legal (bool), violated_rule, fix_hint
"""
import re
import sys
import json
import argparse
from pathlib import Path


VIOLATIONS_CATALOG = {
    "drop_table": {
        "pattern": r"\bDROP\s+TABLE\b",
        "severity": "CRITICAL",
        "fix": "Ensure DROP TABLE is intentional. Consider soft-delete patterns instead. Requires [DO: YES] gate.",
    },
    "drop_column": {
        "pattern": r"\bDROP\s+COLUMN\b",
        "severity": "HIGH",
        "fix": "Dropping a column is irreversible. Back up data first. Requires [DO: YES] gate.",
    },
    "delete_without_where": {
        "pattern": r"\bDELETE\s+FROM\s+\w+\s*;",
        "severity": "CRITICAL",
        "fix": "DELETE without WHERE deletes all rows. Add a WHERE clause or confirm this is a full wipe.",
    },
    "truncate": {
        "pattern": r"\bTRUNCATE\b",
        "severity": "CRITICAL",
        "fix": "TRUNCATE wipes all rows irreversibly. Requires [DO: YES] gate.",
    },
    "rls_not_enabled": {
        "pattern": r"CREATE\s+TABLE",
        "severity": "HIGH",
        "fix": "New table detected. Ensure RLS is enabled: ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;",
        "check_absence": r"ENABLE\s+ROW\s+LEVEL\s+SECURITY",
    },
    "open_rls_policy": {
        "pattern": r"USING\s*\(\s*true\s*\)",
        "severity": "HIGH",
        "fix": "USING (true) grants access to ALL rows for ALL users. Restrict with auth.uid() = user_id or similar.",
    },
    "public_schema_risk": {
        "pattern": r"GRANT\s+ALL\s+ON\s+TABLE",
        "severity": "MEDIUM",
        "fix": "GRANT ALL is overly permissive. Specify exact privileges (SELECT, INSERT, etc.).",
    },
    "alter_column_type": {
        "pattern": r"ALTER\s+COLUMN\s+\w+\s+TYPE",
        "severity": "HIGH",
        "fix": "Changing column type can cause data loss or casting errors. Verify data compatibility first.",
    },
}


def scan_migration(filepath: Path) -> list[dict]:
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()

        for rule_name, rule in VIOLATIONS_CATALOG.items():
            for line_num, line in enumerate(lines, start=1):
                if re.search(rule["pattern"], line, re.IGNORECASE):
                    # Special case: check_absence — only flag if the paired safety check is missing
                    if "check_absence" in rule:
                        if not re.search(rule["check_absence"], content, re.IGNORECASE):
                            violations.append({
                                "rule": rule_name,
                                "severity": rule["severity"],
                                "line": line_num,
                                "snippet": line.strip()[:100],
                                "fix": rule["fix"],
                            })
                            break  # one violation per rule
                    else:
                        violations.append({
                            "rule": rule_name,
                            "severity": rule["severity"],
                            "line": line_num,
                            "snippet": line.strip()[:100],
                            "fix": rule["fix"],
                        })

    except Exception as e:
        violations.append({"rule": "read_error", "severity": "CRITICAL", "line": 0, "snippet": str(e), "fix": "Check file path."})

    return violations


def main():
    parser = argparse.ArgumentParser(description="Supabase Migration Verifier Harness")
    parser.add_argument("--file", required=True, help="Path to the .sql migration file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    violations = scan_migration(filepath)
    critical = [v for v in violations if v["severity"] == "CRITICAL"]
    high = [v for v in violations if v["severity"] == "HIGH"]

    is_legal = len(critical) == 0 and len(high) == 0

    report = {
        "action_id": f"migration_verify:{filepath.name}",
        "is_legal": is_legal,
        "violated_rule": "none" if is_legal else f"{len(violations)} issue(s): {len(critical)} CRITICAL, {len(high)} HIGH",
        "fix_hint": "none" if is_legal else "Review violations below. All CRITICAL and HIGH must be resolved before applying migration.",
        "violations": violations,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if is_legal:
            if violations:
                print(f"[WARN] Migration has {len(violations)} MEDIUM issue(s) — review recommended.")
                for v in violations:
                    print(f"  [{v['severity']}] line {v['line']}: {v['rule']}")
                    print(f"    SQL: {v['snippet']}")
                    print(f"    Fix: {v['fix']}")
            else:
                print("[PASS] Migration looks safe. No destructive or insecure patterns found.")
        else:
            print(f"[FAIL] Migration BLOCKED — {len(violations)} issue(s) detected\n")
            for v in violations:
                print(f"  [{v['severity']}] line {v['line']}: {v['rule']}")
                print(f"    SQL: {v['snippet']}")
                print(f"    Fix: {v['fix']}\n")
            print("DO NOT apply this migration until all CRITICAL/HIGH issues are resolved.")

    sys.exit(0 if is_legal else 1)


if __name__ == "__main__":
    main()
