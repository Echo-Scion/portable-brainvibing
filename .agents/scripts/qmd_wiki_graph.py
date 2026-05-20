import os
import sys
import subprocess
import json
import argparse
import re
from pathlib import Path

def find_project_root():
    markers = [".git", ".agents", "pubspec.yaml", "package.json"]
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent
    return Path.cwd()

def get_qmd_js_path():
    appdata = os.environ.get('APPDATA')
    if appdata:
        p = Path(appdata) / 'npm' / 'node_modules' / '@tobilu' / 'qmd' / 'dist' / 'cli' / 'qmd.js'
        if p.exists(): return str(p)
    p = Path('/usr/local/lib/node_modules/@tobilu/qmd/dist/cli/qmd.js')
    if p.exists(): return str(p)
    root = find_project_root()
    p = root / 'qmd-main' / 'dist' / 'cli' / 'qmd.js'
    if p.exists(): return str(p)
    return None

def query_qmd_wiki(query_str):
    root = find_project_root()
    query_json = {
        "searches": [{"type": "vec", "query": query_str}],
        "collections": ["wiki_index"],
        "limit": 1
    }
    
    qmd_js = get_qmd_js_path()
    if qmd_js:
        cmd = ["node", qmd_js, "query", json.dumps(query_json), "--json"]
    else:
        cmd = ["npx.cmd" if os.name == 'nt' else "npx", "-y", "@tobilu/qmd", "query", json.dumps(query_json), "--json"]
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
        if result.returncode != 0:
            print(f"❌ QMD Query failed: {result.stderr or result.stdout}")
            return None
            
        data = json.loads(result.stdout)
        if not data or len(data) == 0:
            return None
        return data[0] # Top document
    except Exception as e:
        print(f"❌ Error invoking QMD: {e}")
        return None

def parse_frontmatter(content):
    frontmatter_re = re.compile(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', re.DOTALL)
    match = frontmatter_re.match(content)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    frontmatter = {}
    for line in yaml_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            frontmatter[k.strip().lower()] = v.strip().strip('"').strip("'")
    return frontmatter

def extract_relations(frontmatter):
    # Looking for values that contain [[page|relation]] 
    # Or frontmatter keys like "extends", "implements", "contradicts"
    relations = []
    
    # Direct relation keys
    for key in ["extends", "implements", "contradicts", "relates"]:
        if key in frontmatter:
            val = frontmatter[key]
            # Handle array string like "[foo, bar]"
            if val.startswith("[") and val.endswith("]"):
                items = [x.strip() for x in val[1:-1].split(",") if x.strip()]
                for item in items:
                    relations.append((key, item))
            else:
                relations.append((key, val))
                
    # Also check all string values for [[target|relation]] format
    link_re = re.compile(r'\[\[(.*?)\]\]')
    for k, v in frontmatter.items():
        if isinstance(v, str):
            matches = link_re.findall(v)
            for m in matches:
                if "|" in m:
                    target, rel = m.split("|", 1)
                    relations.append((rel.strip(), target.strip()))
                else:
                    relations.append(("links", m.strip()))
                    
    return relations

def get_wiki_content(filepath):
    root = find_project_root()
    full_path = root / filepath
    if not full_path.exists():
        return None
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def build_tree(start_file, depth=0, max_depth=3, visited=None):
    if visited is None:
        visited = set()
        
    prefix = "  " * depth + ("└── " if depth > 0 else "🎯 ")
    
    if start_file in visited:
        print(f"{prefix}{start_file} [Recursive/Already Visited]")
        return
        
    visited.add(start_file)
    
    content = get_wiki_content(start_file)
    if not content:
        print(f"{prefix}{start_file} [Not Found]")
        return
        
    fm = parse_frontmatter(content)
    category = fm.get("source-category", "unknown")
    pillar = fm.get("pillar", "unknown")
    
    print(f"{prefix}{start_file} (Type: {category}, Pillar: {pillar})")
    
    if depth >= max_depth:
        return
        
    relations = extract_relations(fm)
    for rel_type, target in relations:
        print(f"  " * (depth + 1) + f"🔗 {rel_type} -> {target}")
        # Assuming target is just a basename, try to resolve it in .wiki/sources/
        target_path = target
        if not target_path.startswith(".wiki/sources/"):
            target_path = f".wiki/sources/{target}"
        if not target_path.endswith(".md"):
            target_path += ".md"
            
        # Recursive build
        build_tree(target_path, depth + 2, max_depth, visited)

def main():
    parser = argparse.ArgumentParser(description="QMD Semantic Search & Graph Traversal")
    parser.add_argument("query", type=str, help="Semantic query to search the wiki")
    args = parser.parse_args()
    
    print(f"🔍 Semantic Search: '{args.query}' in wiki_index...")
    top_doc = query_qmd_wiki(args.query)
    
    if not top_doc:
        print("❌ No matching wiki documents found.")
        return
        
    # Output structure from QMD can be { id, score, doc: { ... } } or just properties
    filepath = top_doc.get("id") or top_doc.get("filepath") or top_doc.get("path")
    if not filepath and "doc" in top_doc:
        filepath = top_doc["doc"].get("id") or top_doc["doc"].get("path") or top_doc["doc"].get("filepath")
        
    if not filepath:
        print(f"❌ Could not resolve file path from QMD output. Keys: {list(top_doc.keys())}")
        return
        
    # Standardize to relative path from root
    if os.path.isabs(filepath):
        root = str(find_project_root())
        if filepath.startswith(root):
            filepath = os.path.relpath(filepath, root)
            
    filepath = filepath.replace("\\", "/")
    
    print(f"✅ Found top match: {filepath} (Score: {top_doc.get('score', 'N/A')})")
    print("-" * 50)
    print("🌳 Wiki Dependency Graph")
    print("-" * 50)
    
    build_tree(filepath)

if __name__ == "__main__":
    main()
