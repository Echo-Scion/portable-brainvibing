import os
import json
import datetime

WIKI_DIR = ".wiki"
DIRS = ["sources", "entities", "concepts", "synthesis"]

def bootstrap():
    if not os.path.exists(WIKI_DIR):
        os.makedirs(WIKI_DIR)
        
    for d in DIRS:
        path = os.path.join(WIKI_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)
            
    # Create empty index and log
    for f in ["index.md", "log.md"]:
        path = os.path.join(WIKI_DIR, f)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(f"# {f.split('.')[0].capitalize()}\n")
                
    # Copy template if available (mock implementation)
    schema_path = os.path.join(WIKI_DIR, "_schema.md")
    if not os.path.exists(schema_path):
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write("# Wiki Schema\nAutonomy Level: balanced\n")
            
    # Simple manifest
    manifest = {
        "scanned_at": datetime.datetime.now().isoformat(),
        "status": "bootstrapped",
        "layers": {"infrastructure": [], "context": [], "project_docs": [], "raw": []}
    }
    with open(os.path.join(WIKI_DIR, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Wiki bootstrapped successfully in .wiki/")

if __name__ == "__main__":
    bootstrap()
