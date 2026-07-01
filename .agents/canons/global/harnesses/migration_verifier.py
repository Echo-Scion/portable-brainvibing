import os
import sys
import re
import argparse

DANGEROUS_PATTERNS = {
    'Unconditional Delete': r'DELETE\s+FROM\s+\w+(?!\s+WHERE)',
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

def main():
    parser = argparse.ArgumentParser(description="Verify SQL migration files for dangerous operations.")
    parser.add_argument("--file", required=True, help="Path to the migration SQL file")
    args = parser.parse_args()

    filepath = os.path.abspath(args.file)
    
    if not os.path.exists(filepath):
        print(f" [ERROR] File not found: {filepath}")
        sys.exit(1)

    print(f"Scanning migration file: {filepath}...")
    findings = scan_migration(filepath)

    if findings:
        print("\n [WARNING] Dangerous operations detected:")
        for finding in findings:
            print(f"  - {finding}")
        print("\nACTION REQUIRED: Please review the migration file manually to ensure this is intended.")
        sys.exit(1)
    else:
        print("\n [OK] No obviously dangerous operations detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
