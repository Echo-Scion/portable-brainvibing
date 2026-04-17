import os
import subprocess
import sys
from pathlib import Path

def get_qmd_path():
    """Locate the global QMD executable directly to bypass Windows shell errors."""
    appdata = os.environ.get('APPDATA')
    if appdata:
        qmd_js = Path(appdata) / 'npm' / 'node_modules' / '@tobilu' / 'qmd' / 'dist' / 'cli' / 'qmd.js'
        if qmd_js.exists():
            return str(qmd_js)
    return None

def main():
    print("==================================================")
    print("🚀 Automating QMD Setup for Current Project...")
    print("==================================================")
    
    # 1. Automatically detect current directory and project name
    cwd = Path.cwd()
    # Sanitize project name for QMD collection (alphanumeric and underscores)
    raw_name = cwd.name.lower().replace(' ', '_').replace('-', '_')
    project_name = ''.join(c for c in raw_name if c.isalnum() or c == '_')
    
    print(f"📁 Detected Project Name : {project_name}")
    print(f"📍 Detected Path         : {cwd}")
    
    # 2. Find the executable
    qmd_js_path = get_qmd_path()
    
    if qmd_js_path:
        print(f"✅ Found QMD executable  : {qmd_js_path}")
        base_cmd = ["node", qmd_js_path]
    else:
        print("⚠️ Direct QMD executable not found in AppData. Falling back to NPX.")
        print("   (This might fail on Windows depending on your npm setup).")
        base_cmd = ["npx", "@tobilu/qmd"]
        
    print("-" * 50)
    
    # 3. Add Collection
    add_cmd = base_cmd + ["collection", "add", ".", "--name", project_name]
    print(f"⏳ [1/2] Adding collection '{project_name}' to QMD Index...")
    try:
        subprocess.run(add_cmd, check=True)
        print("✅ Collection added successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add collection: {e}")
        sys.exit(1)
        
    print("-" * 50)
    
    # 4. Embed (Downloads 2GB model on first run)
    embed_cmd = base_cmd + ["embed"]
    print(f"⏳ [2/2] Generating embeddings...")
    print("   (NOTE: If this is your FIRST TIME running QMD globally,")
    print("    it will download a ~2GB AI Model. Please wait until 100%.)")
    print("-" * 50)
    
    try:
        # We don't capture output here so the progress bar prints directly to the user's terminal
        subprocess.run(embed_cmd, check=True)
        print("\n✅ Embedding complete! QMD is fully operational for this project.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to generate embeddings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
