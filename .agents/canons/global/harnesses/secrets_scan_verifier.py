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
_FOUNDATION_DIR = os.path.abspath(os.path.join(_HARNESS_DIR, '..', '..', '..'))
_SCRIPTS_DIR = os.path.join(_FOUNDATION_DIR, '.agents', 'scripts')
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
if _HARNESS_DIR not in sys.path:
    sys.path.insert(0, _HARNESS_DIR)

try:
    from base_action_verifier import BaseActionVerifier
except Exception:
    BaseActionVerifier = object


# Common patterns for secrets (unified from core.security)
try:
    from core.security import SECRET_PATTERNS as _CANON_SECRET_PATTERNS
    SECRET_PATTERNS = {
        name: pat.pattern if hasattr(pat, 'pattern') else str(pat)
        for name, pat in _CANON_SECRET_PATTERNS
    }
except Exception:
    SECRET_PATTERNS = {
        'AWS Access Key': r'AKIA[0-9A-Z]{16}',
        'Stripe Standard Key': r'sk_live_[0-9a-zA-Z]{24}',
        'Stripe Test Key': r'sk_test_[0-9a-zA-Z]{24}',
        'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
        'Bearer_Token': r'Bearer' + r'\s+[a-zA-Z0-9\-\._~+/]+=*',
        'Generic Private Key': r'-----BEGIN ' + r'PRIVATE KEY-----',
        'OpenAI API Key': r'sk-[a-zA-Z0-9]{48}',
        'GitHub Token': r'ghp_[a-zA-Z0-9]{36}',
        'Telegram Bot Token': r'[0-9]{9,10}:[a-zA-Z0-9_-]{35}',
        'JWT / Supabase Key': r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+'
    }

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.orion', 'venv', 'env', 'scratch', 'build', 'dist'}

def scan_file(filepath):
    # Avoid scanning self to prevent matching own regex patterns
    if os.path.normcase(os.path.abspath(filepath)) == os.path.normcase(os.path.abspath(__file__)):
        return []
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for key_name, pattern in SECRET_PATTERNS.items():
                    if re.search(pattern, line):
                        # Simple masking to prevent logging the actual secret
                        findings.append((i, key_name))
    except Exception as e:
        sys.stderr.write(f"[WARN] Secrets scan could not read {filepath}: {e}\n")
    return findings


class SecretsActionVerifier(BaseActionVerifier):
    def __init__(self, action_id: str = "secrets_scan"):
        if BaseActionVerifier is not object:
            super().__init__(action_id)
        self.action_id = action_id
        self.is_legal = True
        self.violated_rule = None
        self.fix_hint = None

    def verify_action(self, filepath: str):
        findings = scan_file(filepath)
        if findings:
            violation = f"{findings[0][1]} on line {findings[0][0]}"
            if hasattr(self, 'log_violation'):
                self.log_violation("NO_HARDCODED_SECRETS", f"Remove hardcoded secret: {violation}")
            else:
                self.is_legal = False
                self.violated_rule = "NO_HARDCODED_SECRETS"
                self.fix_hint = f"Remove hardcoded secret: {violation}"
            return False, self.violated_rule
        self.is_legal = True
        return True, None


def main():
    parser = argparse.ArgumentParser(description="Scan for hardcoded secrets.")
    parser.add_argument("--path", default=".", help="Directory to scan")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.path)
    total_findings = 0

    print(f"Scanning for secrets in: {target_dir}...")
    verifier = SecretsActionVerifier()
    for root, dirs, files in os.walk(target_dir):
        # Exclude ignored directories, but allow .agents
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and (not d.startswith('.') or d == '.agents')]
        
        for file in files:
            # Skip likely binary, minified, or sample/example files
            if file.endswith(('.jpg', '.png', '.mp4', '.sqlite', '.db', '.min.js', '.map', '.example')) or file.startswith('.env.example'):
                continue
                
            filepath = os.path.join(root, file)
            is_legal, violation = verifier.verify_action(filepath)
            if not is_legal:
                rel_path = os.path.relpath(filepath, target_dir)
                print(f" [FAIL] Found secret violation in {rel_path}: {violation}")
                total_findings += 1

    if total_findings > 0:
        print(f"\n [ERROR] {total_findings} potential secret(s) found. Release blocked.")
        sys.exit(1)
    else:
        print("\n [OK] No secrets detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
