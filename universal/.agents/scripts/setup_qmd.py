import os
import subprocess
import sys
import shutil
from pathlib import Path
import argparse

def find_project_root():
    """Traverses up from current file to find the project root based on markers."""
    markers = [".git", ".agents", "pubspec.yaml", "package.json"]
    # Get the directory where this script is located
    current = Path(__file__).resolve().parent

    # Start searching from the script location up to root
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent
    return Path.cwd() # Fallback to CWD

def get_qmd_path():
    """Locate the global QMD executable cross-platform."""
    # 1. Check common global npm paths for qmd.js first (bypassing broken .CMD wrappers on Windows)
    paths_to_check = []

    appdata = os.environ.get('APPDATA')
    if appdata:
        paths_to_check.append(Path(appdata) / 'npm' / 'node_modules' / '@tobilu' / 'qmd' / 'dist' / 'cli' / 'qmd.js')

    paths_to_check.append(Path('/usr/local/lib/node_modules/@tobilu/qmd/dist/cli/qmd.js'))

    root = find_project_root()
    paths_to_check.append(root / 'qmd-main' / 'dist' / 'cli' / 'qmd.js')

    for p in paths_to_check:
        if p.exists():
            return str(p)

    # 2. Check if 'qmd' is in PATH as fallback
    qmd_bin = shutil.which("qmd")
    if qmd_bin:
        return qmd_bin

    return None

def main():
    root = find_project_root()

    parser = argparse.ArgumentParser(description="Agnostic QMD Setup for any AI-engineered project.")
    parser.add_argument("--with-embed", action="store_true", help="Trigger embedding (downloads ~2GB model if not present)")
    parser.add_argument("--name", type=str, default=root.name, help=f"Collection name (default: {root.name})")
    parser.add_argument("--path", type=str, default=str(root), help=f"Path to index (default: {root})")
    args = parser.parse_args()

    project_name = args.name
    project_path = Path(args.path).resolve()

    print("==================================================")
    print("🚀 Automating QMD Setup (Project Agnostic)...      ")
    print("==================================================")

    print(f"📁 Project Name : {project_name}")
    print(f"📍 Root Path    : {project_path}")

    qmd_exe = get_qmd_path()

    if qmd_exe:
        if qmd_exe.endswith('.js'):
            print(f"✅ Found QMD script : {qmd_exe}")
            base_cmd = ["node", qmd_exe]
        else:
            print(f"✅ Found QMD binary : {qmd_exe}")
            base_cmd = [qmd_exe]
    else:
        print("⚠️ Direct QMD not found. Falling back to NPX.")
        base_cmd = ["npx.cmd" if os.name == 'nt' else "npx", "-y", "@tobilu/qmd"]

    print("-" * 50)

    # 1. Add Collections
    wiki_path = project_path / ".wiki"

    collections_to_add = [
        {"path": str(project_path), "name": "raw_docs"},
    ]
    if wiki_path.exists():
        collections_to_add.append({"path": str(wiki_path), "name": "wiki_index"})

    for col in collections_to_add:
        c_path = col["path"]
        c_name = col["name"]
        add_cmd = base_cmd + ["collection", "add", c_path, "--name", c_name]
        print(f"⏳ Indexing collection '{c_name}' at {c_path}...")

        try:
            result = subprocess.run(add_cmd, capture_output=True, text=True, cwd=str(project_path))
            if result.returncode == 0:
                print(f"✅ Collection '{c_name}' added successfully!")
            elif "already exists" in result.stdout or "already exists" in result.stderr:
                print(f"ℹ️ Collection '{c_name}' already exists. Skipping registration.")
            else:
                print(f"❌ Failed to add collection '{c_name}': {result.stderr or result.stdout}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error adding '{c_name}': {e}")
            sys.exit(1)

    print("-" * 50)

    # 2. Conditional Embed
    if args.with_embed:
        embed_cmd = base_cmd + ["embed"]
        print(f"⏳ Generating embeddings (this may take a while)...")
        try:
            subprocess.run(embed_cmd, check=True, cwd=str(project_path))
            print("✅ Embedding complete!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate embeddings: {e}")
            sys.exit(1)
    else:
        print("💡 Skipping 'qmd embed' (Keyword search active).")
        print(f"   To generate vectors, run: qmd embed")

    print("-" * 50)
    print(f"🏁 Setup complete. QMD is ready for '{project_name}'.")

if __name__ == "__main__":
    main()
