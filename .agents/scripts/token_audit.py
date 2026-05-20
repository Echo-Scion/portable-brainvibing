import os
import sys
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Heuristic token estimator (approx 3.2 chars per token for code/configs, 4 chars for plain prose)
def estimate_tokens(text):
    # Code and structured markdown contain more symbols/formatting,
    # leading to higher token density. 3.2 is a much better empirical average than 4.
    return int(len(text) / 3.2)

def audit_directory(dir_path, exclude_dirs):
    token_counts = {}
    total_tokens = 0

    for root, dirs, files in os.walk(dir_path):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Skip non-text or binary files loosely based on extension
            if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf', '.pyc', '.so', '.dll')):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tokens = estimate_tokens(content)
                    token_counts[file_path] = tokens
                    total_tokens += tokens
            except Exception:
                # Skip files that cannot be read as UTF-8 (likely binaries)
                pass

    return token_counts, total_tokens

def main():
    parser = argparse.ArgumentParser(description="Audit codebase for excessive token usage ('ghost tokens').")
    parser.add_argument("--dir", default=".", help="Directory to audit")
    parser.add_argument("--exclude", nargs="*", default=[".git", "node_modules", "build", "dist", ".agents", ".dart_tool", "ios", "android"], help="Directories to exclude")
    parser.add_argument("--threshold", type=int, default=1500, help="Warning threshold for token count per file")

    args = parser.parse_args()

    print(f"🔍 Auditing {os.path.abspath(args.dir)} for token usage...")
    token_counts, total = audit_directory(args.dir, args.exclude)

    print("\n⚠️ Files exceeding token threshold (potential 'ghost tokens'):")
    exceeded = False
    for filepath, tokens in sorted(token_counts.items(), key=lambda item: item[1], reverse=True):
        if tokens > args.threshold:
            print(f"  - {os.path.relpath(filepath, args.dir)}: ~{tokens} tokens")
            exceeded = True

    if not exceeded:
        print("  ✅ All files are within acceptable token limits.")

    print(f"\n📊 Total Estimated Project Tokens: ~{total}")

if __name__ == "__main__":
    main()
