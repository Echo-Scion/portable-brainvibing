import re
import sys
import argparse
from pathlib import Path

# --- CORE CONFIGURATION ---

# We scan common source and config files.
SAFE_EXTENSIONS = {".ts", ".js", ".json", ".yaml", ".yml", ".env", ".toml", ".ini", ".xml", ".py", ".go", ".java", ".cpp", ".rs", ".rb", ".php"}

# Directories we should never scan to avoid false positives and noise.
SKIP_DIRS = {".git", "node_modules", "build", "dist", ".venv", "venv", "target", "vendor", ".gradle"}

# The regex patterns that define what a "secret" looks like.
SECRET_PATTERNS = {
    # Generic API Keys and Tokens
    "generic_api_key": r"(?i)(api[_-]?key|secret|token|password|auth|access[_-]?token)\s*[=:]\s*['\"][A-Za-z0-9\-_]{16,}['\"]",

    # Generic Private Keys (RSA, EC, etc.)
    "private_key": r"-----BEGIN (?:RSA |EC |PGP |OPENSSH )?PRIVATE KEY-----",

    # Provider specific formats (Abstracted)
    "cloud_service_key": r"(?i)(service[_-]?role|admin[_-]?key)\s*[=:]\s*['\"][^'\"]{10,}['\"]",
    "jwt_token": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
}

def scan_file_for_secrets(filepath):
    """
    Reads a file line-by-line and checks against all SECRET_PATTERNS.
    """
    violations = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_number, line in enumerate(f, 1):
                for pattern_name, regex in SECRET_PATTERNS.items():
                    if re.search(regex, line):
                        # Mask the matched line to prevent leaking the secret in CI logs
                        masked_line = re.sub(r'([\'"]).*?([\'"])', r'\1********\2', line.strip())
                        violations.append({
                            "line_num": line_number,
                            "type": pattern_name,
                            "preview": masked_line
                        })
    except Exception as e:
        print(f"[WARN] Could not read {filepath}: {e}")

    return violations

def find_files_to_scan(root_dir):
    """
    Recursively finds all files in the directory that match SAFE_EXTENSIONS
    and are not inside SKIP_DIRS.
    """
    scan_list = []
    for path in Path(root_dir).rglob('*'):
        if path.is_file():
            # Check if any parent dir is in SKIP_DIRS
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix in SAFE_EXTENSIONS:
                scan_list.append(path)
    return scan_list

def main():
    parser = argparse.ArgumentParser(description="Universal Mechanical Sentinel: Secret Scanning Harness")
    parser.add_argument("--dir", default=".", help="Root directory to scan recursively")
    parser.add_argument("--file", help="Specific file to scan (overrides --dir)")

    args = parser.parse_args()

    files_to_scan = [Path(args.file)] if args.file else find_files_to_scan(args.dir)

    total_violations = 0

    print(f"--- STARTING SECRET SCAN ON {len(files_to_scan)} FILES ---")

    for filepath in files_to_scan:
        violations = scan_file_for_secrets(filepath)
        if violations:
            print(f"\n[CRITICAL ERROR] Secrets detected in: {filepath}")
            for v in violations:
                print(f"  Line {v['line_num']} | Type: {v['type']} | {v['preview']}")
            total_violations += len(violations)

    if total_violations > 0:
        print(f"\n[FATAL] Scan failed. Found {total_violations} leaked secrets. REMOVE THEM IMMEDIATELY.")
        sys.exit(1)

    print("\n[PASS] No secrets detected. Code is clean.")
    sys.exit(0)

if __name__ == "__main__":
    main()
