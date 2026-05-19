import os
import sys
import json
import argparse

def get_audit_targets(directory, extensions, exclude_dirs):
    """
    Deterministically scans a directory for files to audit.
    Filters out common boilerplate, library, and hidden directories.
    """
    targets = []
    
    # Standardize excluded directories to absolute or lowercase match
    exclude_set = {d.lower() for d in exclude_dirs}
    
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to prevent os.walk from scanning excluded directories
        dirs[:] = [d for d in dirs if d.lower() not in exclude_set and not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                full_path = os.path.abspath(os.path.join(root, file))
                targets.append(full_path)
                
    return sorted(targets)

def main():
    parser = argparse.ArgumentParser(description="Deterministic script to find real files for AI code audit.")
    parser.add_argument("dir", help="The root directory to scan.")
    parser.add_argument("--ext", nargs="+", default=[".py", ".dart", ".js", ".ts", ".go", ".rs"], help="File extensions to include.")
    parser.add_argument("--exclude", nargs="+", default=["node_modules", "build", "dist", "coverage", ".git", "ios", "android", ".agents", ".gemini"], help="Directories to exclude.")
    parser.add_argument("--json", action="store_true", help="Output in raw JSON format.")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"Error: {args.dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)
        
    targets = get_audit_targets(args.dir, args.ext, args.exclude)
    
    if args.json:
        print(json.dumps(targets, indent=2))
    else:
        print(f"--- Found {len(targets)} audit targets in '{args.dir}' ---")
        for i, target in enumerate(targets, 1):
            print(f"{i}. {target}")

if __name__ == "__main__":
    main()
