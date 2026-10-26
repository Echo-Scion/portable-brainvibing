import os
import sys
import re
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

try:
    from base_action_verifier import BaseActionVerifier
except Exception:
    BaseActionVerifier = object


DANGEROUS_PATTERNS = {
    'Unconditional Delete': r'DELETE\s+FROM\s+(?:[\w."`\[\]]+)\b(?!\s+WHERE\b)',
    'Drop Table': r'DROP\s+TABLE\s+',
    'Truncate Table': r'TRUNCATE\s+TABLE\s+'
}

def scan_migration(filepath):
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove comments to avoid false positives
            content_no_comments = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
            content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
            
            for key_name, pattern in DANGEROUS_PATTERNS.items():
                if re.search(pattern, content_no_comments, re.IGNORECASE):
                    findings.append(key_name)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []
    return findings


class MigrationActionVerifier(BaseActionVerifier):
    def __init__(self, action_id: str = "migration_check"):
        if BaseActionVerifier is not object:
            super().__init__(action_id)
        self.action_id = action_id
        self.is_legal = True
        self.violated_rule = None
        self.fix_hint = None

    def verify_action(self, filepath: str):
        findings = scan_migration(filepath)
        if findings:
            if hasattr(self, 'log_violation'):
                self.log_violation(findings[0], "Review SQL migration for destructive statements")
            else:
                self.is_legal = False
                self.violated_rule = findings[0]
                self.fix_hint = "Review SQL migration for destructive statements"
            return False, findings[0]
        self.is_legal = True
        return True, None

def main():
    parser = argparse.ArgumentParser(description="Verify SQL migration files for dangerous operations.")
    parser.add_argument("--file", required=True, help="Path to the migration SQL file")
    args = parser.parse_args()

    filepath = os.path.abspath(args.file)
    
    if not os.path.exists(filepath):
        print(f" [ERROR] File not found: {filepath}")
        sys.exit(1)

    print(f"Scanning migration file: {filepath}...")
    verifier = MigrationActionVerifier()
    is_legal, violation = verifier.verify_action(filepath)

    if not is_legal:
        print("\n [WARNING] Dangerous operations detected:")
        print(f"  - {violation}")
        print("\nACTION REQUIRED: Please review the migration file manually to ensure this is intended.")
        sys.exit(1)
    else:
        print("\n [OK] No obviously dangerous operations detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
