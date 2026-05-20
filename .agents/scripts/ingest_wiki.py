import os
import re
import json
import hashlib
import datetime
import argparse

WIKI_DIR = ".wiki"
MANIFEST_PATH = os.path.join(WIKI_DIR, "_manifest.json")
LOG_PATH = os.path.join(WIKI_DIR, "log.md")
INDEX_PATH = os.path.join(WIKI_DIR, "index.md")

FRONTMATTER_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', re.DOTALL)

def compute_sha256(content: bytes) -> str:
    normalized = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()

def parse_frontmatter(content: str) -> dict:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    frontmatter = {}
    for line in yaml_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            frontmatter[k.strip().lower()] = v.strip().strip('"').strip("'")
    return frontmatter

def classify_file(filepath: str, content: str) -> tuple:
    filepath_normalized = filepath.replace("\\", "/")
    
    category = "project-doc"
    confidence = "authoritative"
    pillar = "cross-cutting"
    
    if "rules/" in filepath_normalized:
        category = "rule"
        confidence = "authoritative"
        pillar = "infrastructure"
        if "flutter" in filepath_normalized:
            pillar = "tech"
    elif "skills/" in filepath_normalized:
        category = "skill"
        confidence = "authoritative"
        pillar = "tech"
    elif "workflows/" in filepath_normalized:
        category = "workflow"
        confidence = "authoritative"
        pillar = "infrastructure"
    elif "canons/" in filepath_normalized:
        category = "canon"
        confidence = "canonical"
        pillar = "cross-cutting"
    elif "context/" in filepath_normalized or filepath_normalized.endswith("CONTEXT.md"):
        category = "context-master" if filepath_normalized.endswith("CONTEXT.md") else "context-pillar"
        confidence = "authoritative"
        pillar = "tech"
        
    return category, confidence, pillar

def prune_orphans() -> int:
    if not os.path.exists(MANIFEST_PATH):
        return 0
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
            
        pruned_count = 0
        for layer in list(manifest.get("layers", {}).keys()):
            valid_entries = []
            for entry in manifest["layers"][layer]:
                original_path = entry.get("filepath")
                wiki_file = entry.get("wiki_file")
                
                # Cek jika file asli masih ada di sistem (kecuali jika pathnya memang dihapus)
                if original_path and not os.path.exists(original_path):
                    pruned_count += 1
                    print(f"🗑️ Pruning orphan from wiki: {original_path}")
                    if wiki_file:
                        full_wiki_path = os.path.join(WIKI_DIR, wiki_file.replace("/", os.sep))
                        if os.path.exists(full_wiki_path):
                            os.remove(full_wiki_path)
                else:
                    valid_entries.append(entry)
            manifest["layers"][layer] = valid_entries
            
        if pruned_count > 0:
            with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)
        return pruned_count
    except Exception as e:
        print(f"Failed during orphan pruning: {e}")
        return 0

def ingest_file(filepath: str, autonomy_level="balanced") -> bool:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
        
    try:
        with open(filepath, "rb") as f:
            raw_bytes = f.read()
        sha = compute_sha256(raw_bytes)
        
        try:
            content_str = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = raw_bytes.decode("latin-1")
            
        existing_frontmatter = parse_frontmatter(content_str)
        category, confidence, pillar = classify_file(filepath, content_str)
        
        basename = os.path.basename(filepath)
        if basename == "SKILL.md":
            folder_name = os.path.basename(os.path.dirname(filepath))
            wiki_filename = f"skill-{folder_name}.md"
        else:
            wiki_filename = basename
            
        target_path = os.path.join(WIKI_DIR, "sources", wiki_filename)
        
        is_updated = True
        action_type = "NEW"
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as tf:
                target_content = tf.read()
            target_fm = parse_frontmatter(target_content)
            if target_fm.get("source_sha256") == sha:
                print(f"Skipping {filepath} (Already matches hash)")
                return False
            action_type = "EXTEND"
            
        updated_date = datetime.datetime.now().strftime("%Y-%m-%d")
        created_date = existing_frontmatter.get("created", updated_date)
        
        wiki_fm = {
            "type": "source-summary",
            "source-category": category,
            "sources": [os.path.relpath(filepath).replace("\\", "/")],
            "source_sha256": sha,
            "pillar": existing_frontmatter.get("pillar", pillar),
            "confidence": confidence,
            "created": created_date,
            "updated": updated_date
        }
        
        fm_lines = ["---"]
        for k, v in wiki_fm.items():
            if isinstance(v, list):
                fm_lines.append(f"{k}: [{', '.join(v)}]")
            else:
                fm_lines.append(f"{k}: {v}")
        fm_lines.append("---")
        fm_text = "\n".join(fm_lines)
        
        # IMPROVEMENT 2: Anti-Bloat Pointer (No duplicate body text)
        pointer_body = f"\n> **Original Source**: `{filepath}`\n> *Content body excluded from Wiki to prevent storage bloat and duplicate QMD embeddings.*\n"
        
        with open(target_path, "w", encoding="utf-8") as wf:
            wf.write(fm_text + "\n" + pointer_body)
            
        log_entry = f"- [{updated_date}] [{action_type}] Ingested {filepath} -> sources/{wiki_filename}\n"
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(log_entry)
            
        manifest = {}
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                    manifest = json.load(mf)
            except Exception:
                pass
                
        if "layers" not in manifest:
            manifest["layers"] = {"infrastructure": [], "context": [], "project_docs": [], "raw": []}
            
        layer_key = "infrastructure"
        if category in ["context-master", "context-pillar", "memory", "handoff"]:
            layer_key = "context"
        elif category in ["project-doc"]:
            layer_key = "project_docs"
        elif category in ["raw-source"]:
            layer_key = "raw"
            
        manifest_entry = {
            "filepath": filepath.replace("\\", "/"),
            "wiki_file": f"sources/{wiki_filename}",
            "sha256": sha,
            "category": category,
            "updated": updated_date
        }
        
        manifest["layers"][layer_key] = [e for e in manifest["layers"][layer_key] if e["filepath"] != manifest_entry["filepath"]]
        manifest["layers"][layer_key].append(manifest_entry)
        manifest["status"] = "active"
        manifest["scanned_at"] = datetime.datetime.now().isoformat()
        
        with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, indent=2)
            
        print(f"Ingested: {filepath} -> {target_path} [{action_type}]")
        return True
    except Exception as e:
        print(f"Failed to ingest {filepath}: {e}")
        return False

def rebuild_index():
    if not os.path.exists(MANIFEST_PATH):
        return
        
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
            
        index_lines = [
            "# Wiki Index",
            f"*Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## 📌 Infrastructure Layer"
        ]
        
        infra = manifest.get("layers", {}).get("infrastructure", [])
        if infra:
            for item in sorted(infra, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}](file:///{item['wiki_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "## 📊 Context Layer"
        ])
        
        context = manifest.get("layers", {}).get("context", [])
        if context:
            for item in sorted(context, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}](file:///{item['wiki_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "## 📄 Project Docs Layer"
        ])
        
        docs = manifest.get("layers", {}).get("project_docs", [])
        if docs:
            for item in sorted(docs, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}](file:///{item['wiki_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        with open(INDEX_PATH, "w", encoding="utf-8") as idx:
            idx.write("\n".join(index_lines) + "\n")
            
        print("Wiki Index rebuilt successfully.")
    except Exception as e:
        print(f"Failed to rebuild index: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ingest markdown files into .wiki/")
    parser.add_argument("paths", nargs="+", help="Paths or files to ingest")
    parser.add_argument("--autonomy", default="balanced", choices=["balanced", "high", "strict"])
    args = parser.parse_args()
    
    sources_dir = os.path.join(WIKI_DIR, "sources")
    if not os.path.exists(sources_dir):
        os.makedirs(sources_dir)
        
    # IMPROVEMENT 3: Garbage Collection
    pruned = prune_orphans()
        
    ingested_count = 0
    for path in args.paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                # IMPROVEMENT 1: Exclude .wiki recursion
                if '.wiki' in root.replace('\\', '/').split('/'):
                    continue
                    
                for f in files:
                    if f.endswith(".md"):
                        full_path = os.path.join(root, f)
                        if ingest_file(full_path, args.autonomy):
                            ingested_count += 1
        elif os.path.isfile(path):
            if ingest_file(path, args.autonomy):
                ingested_count += 1
        else:
            import glob
            for g in glob.glob(path, recursive=True):
                if os.path.isfile(g) and g.endswith(".md"):
                    if '.wiki' not in g.replace('\\', '/').split('/'):
                        if ingest_file(g, args.autonomy):
                            ingested_count += 1
                        
    if ingested_count > 0 or pruned > 0:
        rebuild_index()
        print(f"\nBatch execution complete. Processed: {ingested_count} | Pruned: {pruned}")
        
        # Trigger QMD Harmonization
        print("\n⏳ Triggering QMD index and embed for harmonization...")
        setup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_qmd.py")
        if os.path.exists(setup_script):
            import sys, subprocess
            subprocess.run([sys.executable, setup_script, "--with-embed"])
    else:
        print("No new or updated markdown files found to ingest. Graph is up to date.")

if __name__ == "__main__":
    main()
