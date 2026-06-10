"""
Harness: Pre-Commit Secrets Scanner
Purpose: Intercept any file write or git commit and scan for leaked secrets.
Usage:
    python .agents/canons/global/harnesses/secrets_scan_verifier.py --path ./lib
    python .agents/canons/global/harnesses/secrets_scan_verifier.py --file lib/config.dart
Output Contract: action_id, is_legal (bool), violated_rule, fix_hint
"""
import re
import os
import sys
import json
import argparse
from pathlib import Path

# Patterns that indicate a leaked secret
SECRET_PATTERNS = {
    "openai_key":       r"sk-[a-zA-Z0-9]{32,}",
    "supabase_service": r"(SUPABASE_SERVICE_ROLE_KEY|service_role)\s*[=:]\s*['\"][^'\"]{10,}",
    "private_key_pem":  r"BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY",
    "hardcoded_pass":   r"password\s*[=:]\s*['\"][^'\"]{4,}['\"]",
    "hardcoded_api":    r"(api_key|API_KEY|apiKey)\s*[=:]\s*['\"][^'\"]{4,}['\"]",
    "generic_token":    r"(token|secret|auth_token)\s*[=:]\s*['\"][a-zA-Z0-9+/]{16,}",
    "firebase_key":     r"AIza[0-9A-Za-z\-_]{35}",
}

SAFE_EXTENSIONS = {".dart", ".ts", ".js", ".json", ".yaml", ".yml", ".env", ".toml", ".ini", ".xml"}
SKIP_DIRS = {".git", "node_modules", ".dart_tool", "build", ".gradle"}


def scan_file(filepath: Path) -> list[dict]:
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            for rule_name, pattern in SECRET_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "file": str(filepath),
                        "line": line_num,
                        "rule": rule_name,
                        "snippet": line.strip()[:80],
                    })
    except Exception as e:
        violations.append({"file": str(filepath), "line": 0, "rule": "read_error", "snippet": str(e)})
    return violations


def scan_path(target: Path) -> list[dict]:
    all_violations = []
    if target.is_file():
        if target.suffix in SAFE_EXTENSIONS:
            all_violations.extend(scan_file(target))
    else:
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                fpath = Path(root) / fname
                if fpath.suffix in SAFE_EXTENSIONS:
                    all_violations.extend(scan_file(fpath))
    return all_violations


def main():
    parser = argparse.ArgumentParser(description="Pre-Commit Secrets Scanner Harness")
    parser.add_argument("--path", default=".", help="Directory to scan")
    parser.add_argument("--file", help="Single file to scan (overrides --path)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    target = Path(args.file) if args.file else Path(args.path)
    violations = scan_path(target)

    is_legal = len(violations) == 0
    report = {
        "action_id": "pre_commit_secrets_scan",
        "is_legal": is_legal,
        "violated_rule": "none" if is_legal else f"{len(violations)} secret(s) found",
        "fix_hint": "none" if is_legal else "Move secrets to .env file. Add .env to .gitignore. Rotate any exposed keys immediately.",
        "violations": violations,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if is_legal:
            print("[PASS] No secrets detected. Safe to commit.")
        else:
            print(f"[FAIL] {len(violations)} secret(s) detected — DO NOT COMMIT\n")
            for v in violations:
                print(f"  [{v['rule']}] {v['file']}:{v['line']}")
                print(f"    → {v['snippet']}")
            print(f"\nFix: {report['fix_hint']}")

    sys.exit(0 if is_legal else 1)


if __name__ == "__main__":
    main()
