import os
import sys
import re
import argparse

# Common patterns for secrets
SECRET_PATTERNS = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'Stripe Standard Key': r'sk_live_[0-9a-zA-Z]{24}',
    'Stripe Test Key': r'sk_test_[0-9a-zA-Z]{24}',
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'Bearer Token': r'Bearer\s+[a-zA-Z0-9\-\._~+/]+=*',
    'Generic Private Key': r'-----BEGIN PRIVATE KEY-----'
}

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.orion', 'venv', 'env', '.agents'}

def scan_file(filepath):
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                for key_name, pattern in SECRET_PATTERNS.items():
                    if re.search(pattern, line):
                        # Simple masking to prevent logging the actual secret
                        findings.append((i, key_name))
    except Exception as e:
        pass
    return findings

def main():
    parser = argparse.ArgumentParser(description="Scan for hardcoded secrets.")
    parser.add_argument("--path", default=".", help="Directory to scan")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.path)
    total_findings = 0

    print(f"Scanning for secrets in: {target_dir}...")
    for root, dirs, files in os.walk(target_dir):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        
        for file in files:
            # Skip likely binary or minified files
            if file.endswith(('.jpg', '.png', '.mp4', '.sqlite', '.db', '.min.js', '.map')):
                continue
                
            filepath = os.path.join(root, file)
            findings = scan_file(filepath)
            if findings:
                rel_path = os.path.relpath(filepath, target_dir)
                for line_num, key_name in findings:
                    print(f" [FAIL] Found possible {key_name} in {rel_path} on line {line_num}")
                total_findings += len(findings)

    if total_findings > 0:
        print(f"\n [ERROR] {total_findings} potential secret(s) found. Release blocked.")
        sys.exit(1)
    else:
        print("\n [OK] No secrets detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
