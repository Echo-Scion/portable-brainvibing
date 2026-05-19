import os
import sys
import re
import argparse

def generate_skeleton(file_path):
    """
    Extracts class and function definitions to create a structural skeleton
    of a codebase file for token-efficient context ingestion.
    Supports Python, Dart/Flutter, and Javascript/Typescript.
    """
    skeleton = []

    # Patterns for different languages
    patterns = [
        re.compile(r'^\s*(class\s+\w+.*?):?\s*$'), # Python/JS/Dart classes
        re.compile(r'^\s*(def\s+\w+\s*\(.*?\).*?):?\s*$'), # Python functions
        re.compile(r'^\s*((?:export\s+)?(?:async\s+)?function\s+\w+\s*\(.*?\).*?)\s*[{]?\s*$'), # JS functions
        re.compile(r'^\s*(?!(?:if|for|while|catch|switch)\s*\()((?:[a-zA-Z<>\[\]_]+\s+)?\w+\s*\([^)]*\)\s*(?:async\*?|sync\*)?\s*[{=>])'), # Dart methods/functions
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    match = pattern.match(line)
                    if match:
                        # Extract the signature, strip trailing braces or colons
                        sig = match.group(1).strip().rstrip('{:').strip()
                        skeleton.append(f"  Line {line_num}: {sig}")
                        break
    except (OSError, UnicodeDecodeError) as e:
        sys.stderr.write(f"⚠️ Warning: Could not read {file_path}: {e}\n")

    return skeleton

def map_directory(dir_path, exclude_dirs):
    print(f"🗺️ Generating Code Skeleton Map for: {os.path.abspath(dir_path)}")
    print("=" * 60)

    for root, dirs, files in os.walk(dir_path):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Only map specific code extensions to save time/noise
            if file.endswith(('.py', '.dart', '.js', '.ts', '.jsx', '.tsx')):
                file_path = os.path.join(root, file)
                skeleton = generate_skeleton(file_path)

                if skeleton:
                    rel_path = os.path.relpath(file_path, dir_path)
                    print(f"\n📄 {rel_path}")
                    for line in skeleton:
                        print(line)

def main():
    parser = argparse.ArgumentParser(description="Generate a structural skeleton of the codebase for token-efficient context mapping.")
    parser.add_argument("--dir", default=".", help="Directory to map")
    parser.add_argument("--exclude", nargs="*", default=[".git", "node_modules", "build", "dist", ".agents", ".dart_tool", "ios", "android"], help="Directories to exclude")

    args = parser.parse_args()
    map_directory(args.dir, args.exclude)

if __name__ == "__main__":
    main()
