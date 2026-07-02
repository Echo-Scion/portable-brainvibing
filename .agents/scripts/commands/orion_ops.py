import os
import sys
import argparse
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import re
import json
import hashlib
import datetime

import sqlite3

# --- Configuration & Globals ---
WORKSPACE_DIR = os.getcwd()
ORION_DIR = ".orion"
MANIFEST_PATH = os.path.join(ORION_DIR, "_manifest.json")
LOG_PATH = os.path.join(ORION_DIR, "log.md")
INDEX_PATH = os.path.join(ORION_DIR, "index.md")
DB_PATH = os.path.join(ORION_DIR, "orion.db")
DIRS = ["working", "episodic", "matrix"]

def normalize_path(p: str) -> str:
    return p.replace(chr(92), '/')

_DB_INITIALIZED = False

def get_db():
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        init_db()
        _DB_INITIALIZED = True
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA busy_timeout=5000;')
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA busy_timeout=5000;')
    c = conn.cursor()
    c.execute('PRAGMA journal_mode=WAL;')
    c.execute('PRAGMA temp_store=MEMORY;')
    c.execute('PRAGMA mmap_size=67108864;') # 64MB mmap
    c.execute('PRAGMA cache_size=-16000;') # 16MB buffer pinning (hybrid RAM graph)
    c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            path TEXT PRIMARY KEY,
            sha256 TEXT,
            category TEXT,
            pillar TEXT,
            updated TEXT
        )
    ''')
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
            path,
            content,
            tokenize='porter'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT,
            name TEXT,
            source_path TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS edges (
            source_id TEXT,
            target_id TEXT,
            relation TEXT,
            PRIMARY KEY (source_id, target_id, relation)
        )
    ''')
    
    # [DORMANT SCAFFOLDING] 
    # The 'telemetry' and 'contradictions' (created in contradict.py) tables are dormant structural schemas. 
    # They are provided as foundations awaiting activation by specific downstream SaaS projects.
    c.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            exit_code INTEGER,
            context_load INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS page_embeddings (
            path TEXT PRIMARY KEY,
            embedding_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_telemetry(event_type: str, exit_code: int = 0, context_load: int = 0):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO telemetry (timestamp, event_type, exit_code, context_load)
        VALUES (?, ?, ?, ?)
    ''', (datetime.datetime.now().isoformat(), event_type, exit_code, context_load))
    c.execute('DELETE FROM telemetry WHERE id NOT IN (SELECT id FROM telemetry ORDER BY id DESC LIMIT 1000)')
    conn.commit()
    conn.close()


RAW_EXTS = [".dart", ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java"]
try:
    manifest_path = os.path.join(".agents", ".project_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            if "ecosystem" in manifest and "extensions" in manifest["ecosystem"]:
                RAW_EXTS = manifest["ecosystem"]["extensions"]
except Exception:
    pass

FRONTMATTER_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', re.DOTALL)

# === BOOTSTRAP ===
def bootstrap():
    if not os.path.exists(ORION_DIR):
        os.makedirs(ORION_DIR)
        
    for d in DIRS:
        path = os.path.join(ORION_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)
            
    # Initialize SQLite DB for LightRAG
    init_db()
            
    # Create empty index and log
    for f in ["index.md", "log.md"]:
        path = os.path.join(ORION_DIR, f)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(f"# {f.split('.')[0].capitalize()}\n")
                
    # Copy template if available (mock implementation)
    schema_path = os.path.join(ORION_DIR, "_schema.md")
    if not os.path.exists(schema_path):
        with open(schema_path, "w", encoding="utf-8") as f:
            f.write("# Orion Schema\nAutonomy Level: balanced\n")
            
    # Seed essential files
    session_history_path = os.path.join(ORION_DIR, "episodic", "session_history.md")
    if not os.path.exists(session_history_path):
        with open(session_history_path, "w", encoding="utf-8") as f:
            f.write("# Session History\n\n*Chronological log of agent sessions and key architectural decisions.*\n")
            
    handoff_path = os.path.join(ORION_DIR, "working", "handoff.md")
    if not os.path.exists(handoff_path):
        with open(handoff_path, "w", encoding="utf-8") as f:
            f.write("# SESSION HANDOFF\n\n## 1. Resume Point\n\n## 2. Technical State\n\n## 4. Metrik Cost & Token Savings\n\n## 5. Anti-Goals\n")
            
    # Simple manifest
    manifest = {
        "scanned_at": datetime.datetime.now().isoformat(),
        "status": "bootstrapped",
        "layers": {"infrastructure": [], "context": [], "project_docs": [], "raw": []}
    }
    with open(os.path.join(ORION_DIR, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Orion bootstrapped successfully in .orion/")


# === INGEST ===
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
    
    _, ext = os.path.splitext(filepath_normalized.lower())
    if ext in RAW_EXTS:
        category = "raw-source"
        confidence = "raw"
        pillar = "tech"
        return category, confidence, pillar
    elif ext in [".yaml", ".json"]:
        category = "config"
        confidence = "authoritative"
        pillar = "infrastructure"
        return category, confidence, pillar
        
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
        db_conn = None
        try:
            db_conn = get_db()
            db_c = db_conn.cursor()
        except Exception:
            pass

        for layer in list(manifest.get("layers", {}).keys()):
            valid_entries = []
            for entry in manifest["layers"][layer]:
                original_path = entry.get("filepath")
                orion_file = entry.get("orion_file")
                
                # Cek jika file asli masih ada di sistem (kecuali jika pathnya memang dihapus)
                if original_path and not os.path.exists(original_path):
                    pruned_count += 1
                    print(f"[PRUNE] Pruning orphan from orion: {original_path}")
                    if orion_file:
                        full_wiki_path = os.path.join(ORION_DIR, orion_file.replace("/", os.sep))
                        if os.path.exists(full_wiki_path):
                            os.remove(full_wiki_path)
                        
                        if db_conn:
                            try:
                                norm_path = normalize_path(full_wiki_path)
                                db_c.execute('DELETE FROM edges WHERE source_id IN (SELECT id FROM nodes WHERE source_path = ? OR source_path = ?)', (full_wiki_path, norm_path))
                                db_c.execute('DELETE FROM nodes WHERE source_path = ? OR source_path = ?', (full_wiki_path, norm_path))
                                db_c.execute('DELETE FROM pages WHERE path = ? OR path = ?', (full_wiki_path, norm_path))
                                db_c.execute('DELETE FROM pages_fts WHERE path = ? OR path = ?', (full_wiki_path, norm_path))
                                db_c.execute('DELETE FROM edges WHERE source_id = ? OR source_id = ?', (full_wiki_path, norm_path))
                            except Exception as e:
                                print(f"DB cleanup error for {full_wiki_path}: {e}")
                else:
                    valid_entries.append(entry)
            manifest["layers"][layer] = valid_entries
            
        if db_conn:
            db_conn.commit()
            db_conn.close()
            
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
        name, ext = os.path.splitext(basename)
        
        target_path = os.path.relpath(filepath).replace("\\", "/")
        
        is_updated = True
        action_type = "NEW"
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT sha256 FROM pages WHERE path = ?', (target_path,))
        row = c.fetchone()
        if row:
            if row[0] == sha:
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
        
        pointer_body = f"\n> **Original Source**: `{filepath}`\n"
        
        if ext.lower() in RAW_EXTS:
            try:
                # Add agents/scripts to sys.path to find utils
                import sys
                script_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                from utils.ast_parser import generate_ast_summary
                ast_summary = generate_ast_summary(filepath, content_str)
                skeleton_lines = ast_summary.split("\n") if ast_summary else ["[AST Skipping: Not structurally parsed]"]
                triplets = []
                
                # Auto-extract basic structural triplets
                import re
                file_basename = os.path.basename(filepath)
                if ext.lower() == ".py":
                    try:
                        from utils.ast_parser import extract_python_edges_ast
                        triplets.extend(extract_python_edges_ast(content_str, file_basename))
                    except ImportError:
                        pass
                elif ext.lower() in [".js", ".ts", ".dart"]:
                    for match in re.finditer(r'^\s*import\s+.*?(?:from\s+)?[\'"](.*?)[\'"]', content_str, re.MULTILINE):
                        triplets.append((file_basename, "imports", match.group(1)))
                    for match in re.finditer(r'^\s*class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?', content_str, re.MULTILINE):
                        cls_name = match.group(1)
                        triplets.append((file_basename, "defines", cls_name))
                        if match.group(2):
                            triplets.append((cls_name, "inherits", match.group(2)))
            except Exception as e:
                skeleton_lines = [f"Error generating AST summary: {e}"]
                triplets = []
            
            skeleton_text = "\n".join(skeleton_lines) if skeleton_lines else "*No class or function signatures found.*"
            pointer_body += f"\n###  Structural Skeleton\n\n```\n{skeleton_text}\n```\n"
        elif ext.lower() in [".yaml", ".json"]:
            deps_list = []
            metadata = {}
            if ext.lower() == ".json":
                try:
                    data = json.loads(content_str)
                    metadata["name"] = data.get("name", "Unknown")
                    metadata["version"] = data.get("version", "Unknown")
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    for dep, ver in deps.items():
                        deps_list.append(f"- `{dep}`: `{ver}`")
                    for dep, ver in dev_deps.items():
                        deps_list.append(f"- `{dep}`: `{ver}` (dev)")
                except Exception:
                    pass
            elif ext.lower() == ".yaml":
                try:
                    in_deps = False
                    in_dev_deps = False
                    for line in content_str.splitlines():
                        line_stripped = line.strip()
                        if line_stripped.startswith("name:"):
                            metadata["name"] = line_stripped.split(":", 1)[1].strip()
                        elif line_stripped.startswith("version:"):
                            metadata["version"] = line_stripped.split(":", 1)[1].strip()
                        elif line_stripped == "dependencies:":
                            in_deps = True
                            in_dev_deps = False
                        elif line_stripped == "dev_dependencies:":
                            in_deps = False
                            in_dev_deps = True
                        elif line.startswith("  ") and not line.startswith("    "):
                            if ":" in line_stripped:
                                k, v = line_stripped.split(":", 1)
                                k = k.strip()
                                v = v.strip()
                                if in_deps:
                                    deps_list.append(f"- `{k}`: `{v}`")
                                elif in_dev_deps:
                                    deps_list.append(f"- `{k}`: `{v}` (dev)")
                        elif not line.startswith(" ") and line_stripped:
                            in_deps = False
                            in_dev_deps = False
                except Exception:
                    pass
            
            meta_text = "\n".join(f"- **{k.capitalize()}**: `{v}`" for k, v in metadata.items())
            deps_text = "\n".join(deps_list) if deps_list else "*No dependencies parsed.*"
            pointer_body += f"\n###  Metadata\n{meta_text}\n\n###  Dependencies\n{deps_text}\n"
        else:
            pointer_body += f"> *Content body excluded from Graph to prevent storage bloat.*\n"
        
        log_entry = f"- [{updated_date}] [{action_type}] Ingested {filepath}\n"
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write(log_entry)
            
        with open(LOG_PATH, "r", encoding="utf-8") as lf:
            lines = lf.readlines()
        if len(lines) > 500:
            with open(LOG_PATH, "w", encoding="utf-8") as lf:
                lf.writelines(lines[-500:])
            
        # LightRAG SQLite Sync
        try:
            conn = get_db()
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO pages (path, sha256, category, pillar, updated) 
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    sha256 = excluded.sha256,
                    category = excluded.category,
                    pillar = excluded.pillar,
                    updated = excluded.updated
            ''', (target_path, sha, category, existing_frontmatter.get("pillar", pillar), updated_date))
            
            c.execute('DELETE FROM pages_fts WHERE path = ?', (target_path,))
            c.execute('''
                INSERT INTO pages_fts (path, content) VALUES (?, ?)
            ''', (target_path, fm_text + "\n" + pointer_body))
            
            c.execute('DELETE FROM edges WHERE source_id = ?', (target_path,))
            
            # --- SQL-Backed WikiLinks Extraction ---
            import re
            pattern = r'\[\[(.*?)\]\]'
            wiki_links = re.findall(pattern, content_str)
            if wiki_links:
                c.execute('''
                    INSERT OR REPLACE INTO nodes (id, type, name, source_path) 
                    VALUES (?, ?, ?, ?)
                ''', (target_path, 'File', os.path.basename(target_path), target_path))
                for link in wiki_links:
                    parts = link.split('|')
                    name = parts[0].strip()
                    relation = parts[1].strip() if len(parts) > 1 else "mentions"
                    c.execute('''
                        INSERT OR REPLACE INTO nodes (id, type, name, source_path) 
                        VALUES (?, ?, ?, ?)
                    ''', (name, 'WikiNode', name, target_path))
                    c.execute('''
                        INSERT OR IGNORE INTO edges (source_id, target_id, relation)
                        VALUES (?, ?, ?)
                    ''', (target_path, name, relation))

            # --- Structural Triplets ---
            if ext.lower() in RAW_EXTS and 'triplets' in locals() and triplets:
                c.execute('''
                    INSERT OR REPLACE INTO nodes (id, type, name, source_path) 
                    VALUES (?, ?, ?, ?)
                ''', (target_path, 'File', os.path.basename(target_path), target_path))
                for caller, rel, callee in triplets:
                    c.execute('''
                        INSERT OR REPLACE INTO nodes (id, type, name, source_path) 
                        VALUES (?, ?, ?, ?)
                    ''', (callee, 'AST_Element', callee, target_path))
                    c.execute('''
                        INSERT OR IGNORE INTO edges (source_id, target_id, relation)
                        VALUES (?, ?, ?)
                    ''', (target_path, callee, rel))
            
            # Vector Embedding (Graceful Degradation)
            try:
                import sys
                script_dir = os.path.dirname(os.path.abspath(__file__))
                if script_dir not in sys.path:
                    sys.path.insert(0, script_dir)
                from brain import NanoBrain
                nb = NanoBrain()
                if nb.ping():
                    embed_text = (fm_text + "\n" + pointer_body)[:2000] # Limit size for performance
                    emb = nb.embed(embed_text)
                    if emb:
                        c.execute('''
                            INSERT INTO page_embeddings (path, embedding_json) 
                            VALUES (?, ?)
                            ON CONFLICT(path) DO UPDATE SET embedding_json = excluded.embedding_json
                        ''', (target_path, json.dumps(emb)))
            except Exception as e:
                print(f"Warning: Failed to generate vector embedding: {e}")

            conn.commit()
            conn.close()
        except Exception as db_e:
            print(f"Warning: Failed to sync to orion.db: {db_e}")
            
        manifest = {}
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                    manifest = json.load(mf)
            except Exception as e:
                print(f"Warning: Failed to load manifest: {e}")
                
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
            "orion_file": filepath.replace("\\", "/"),
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
        return target_path
    except Exception as e:
        print(f"Failed to ingest {filepath}: {e}")
        return None

def rebuild_index():
    if not os.path.exists(MANIFEST_PATH):
        return
        
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
            
        index_lines = [
            "# Orion Index",
            f"*Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "##  Infrastructure Layer"
        ]
        
        infra = manifest.get("layers", {}).get("infrastructure", [])
        if infra:
            for item in sorted(infra, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Context Layer"
        ])
        
        context = manifest.get("layers", {}).get("context", [])
        if context:
            for item in sorted(context, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Project Docs Layer"
        ])
        
        docs = manifest.get("layers", {}).get("project_docs", [])
        if docs:
            for item in sorted(docs, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No files ingested yet*")
            
        index_lines.extend([
            "",
            "##  Raw/Source Layer"
        ])
        
        raw_files = manifest.get("layers", {}).get("raw", [])
        if raw_files:
            for item in sorted(raw_files, key=lambda x: x["filepath"]):
                index_lines.append(f"- [{item['filepath']}]({item['orion_file']}) (Type: `{item['category']}`)")
        else:
            index_lines.append("- *No source files ingested yet*")
            
        with open(INDEX_PATH, "w", encoding="utf-8") as idx:
            idx.write("\n".join(index_lines) + "\n")
            
        print("Orion Index rebuilt successfully.")
    except Exception as e:
        print(f"Failed to rebuild index: {e}")


def get_smart_ignore_dirs(target_path):
    ignores = {".git", ".orion", "__pycache__", "node_modules", "build", ".dart_tool", ".idea", ".vscode", ".gradle", "target", "venv", "env"}
    if os.path.isfile(target_path):
        target_path = os.path.dirname(target_path)
    curr = os.path.abspath(target_path)
    while curr:
        g = os.path.join(curr, ".gitignore")
        if os.path.exists(g):
            try:
                with open(g, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "*" in line or "?" in line:
                                continue
                            if "/" not in line:
                                ignores.add(line)
                            elif line.endswith("/") and line.count("/") == 1:
                                ignores.add(line.replace("/", ""))
                            elif line.startswith("/") and line.endswith("/") and line.count("/") == 2:
                                ignores.add(line.replace("/", ""))
            except Exception:
                pass
            break
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return ignores

def ingest_main(paths, autonomy):
    pruned = prune_orphans()
        
    ingested_files = []
    valid_exts = tuple([".md"] + RAW_EXTS + [".yaml", ".json"])
    for path in paths:
        ignore_dirs = get_smart_ignore_dirs(path)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    
                for f in files:
                    if f.lower().endswith(valid_exts):
                        full_path = os.path.join(root, f)
                        target_path = ingest_file(full_path, autonomy)
                        if target_path:
                            ingested_files.append((full_path, target_path))
        elif os.path.isfile(path):
            target_path = ingest_file(path, autonomy)
            if target_path:
                ingested_files.append((path, target_path))
        else:
            import glob
            for g in glob.glob(path, recursive=True):
                if os.path.isfile(g) and g.lower().endswith(valid_exts):
                    if '.orion' not in g.replace('\\', '/').split('/'):
                        target_path = ingest_file(g, autonomy)
                        if target_path:
                            ingested_files.append((g, target_path))
                        
    if len(ingested_files) > 0 or pruned > 0:
        rebuild_index()
        print(f"\nBatch execution complete. Processed: {len(ingested_files)} | Pruned: {pruned}")
        
        # --- AUTO-COMPILE HOOK ---
        if len(ingested_files) > 0:
            print("\n[AUTO-COMPILE] Triggering Matrix Compilation for zero-drift...")
            compile_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compile_rules.py")
            try:
                subprocess.run([sys.executable, compile_script], check=False)
            except Exception as e:
                print(f"[ERROR] Failed to auto-compile rules: {e}")
                
            # --- AUTO-LINKIFY HOOK ---
            print("\n[AUTO-LINKIFY] Injecting Wiki-links into Markdown context...")
            linkify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkify.py")
            if os.path.exists(linkify_script):
                try:
                    subprocess.run([sys.executable, linkify_script], check=False)
                except Exception as e:
                    print(f"[ERROR] Failed to auto-linkify markdown: {e}")
                
            print(f"\n[TRIPLET_REQUEST] {len(ingested_files)} files need graph triplet extraction.")
            print("⚡ RECOMMENDED TIER: BUDGET — Ingest/deploy operations are batch tasks. Switch to Budget model.")
            print("Files:")
            for i, (orig, target) in enumerate(ingested_files, 1):
                rel_target = os.path.relpath(target, WORKSPACE_DIR).replace("\\", "/")
                rel_orig = os.path.relpath(orig, WORKSPACE_DIR).replace("\\", "/")
                print(f"{i}. {rel_target} (source: {rel_orig})")
            print("[ACTION] Read each source file, extract 3-5 Subject|Predicate|Object triplets,")
            print("then run: python .agents/scripts/orion.py orion_ops inject_triplets '<json>'")
            
    else:
        print("No new or updated markdown files found to ingest. Graph is up to date.")
        print("⚡ RECOMMENDED TIER: BUDGET — Ingest/deploy operations are batch tasks. Switch to Budget model.")

# === RESOLVER ===
def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return None
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def find_target_file(query):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT path FROM pages WHERE path LIKE ?', (f'%{query}%',))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception:
        pass
    return None

def extract_links(content):
    # Matches [[Page Name]] or [[Page Name|relation]]
    pattern = r'\[\[(.*?)\]\]'
    links = re.findall(pattern, content)
    parsed_links = []
    for link in links:
        parts = link.split('|')
        name = parts[0].strip()
        relation = parts[1].strip() if len(parts) > 1 else "mentions"
        parsed_links.append((name, relation))
    return parsed_links

def get_file_summary(filepath):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT category FROM pages WHERE path = ?', (filepath,))
        row = c.fetchone()
        conn.close()
        if row:
            return f"Category: {row[0]}"
    except Exception:
        pass
    return "Not ingested."

def find_backlinks(target_name):
    backlinks = []
    try:
        conn = get_db()
        c = conn.cursor()
        # O(1) Graph Edge Resolution instead of O(N) FTS Regex Scan
        c.execute('SELECT source_id FROM edges WHERE target_id = ?', (target_name,))
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            basename = os.path.basename(row[0])
            if basename not in backlinks:
                backlinks.append(basename)
    except Exception:
        pass
    return backlinks

def resolve_wiki(query):
    target_file = find_target_file(query)
    if not target_file:
        print(f" [ORION] No nodes found matching '{query}'.")
        return

    print(f" [ORION GRAPH RESOLVER] Node: {os.path.basename(target_file)}")
    print("=" * 60)
    
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(" CONTENT:")
    # Print up to 1500 chars to avoid overwhelming the LLM
    print(content[:1500] + ("\n...[TRUNCATED]" if len(content) > 1500 else ""))
    print("-" * 60)
    
    links = extract_links(content)
    if links:
        print(" FORWARD LINKS (Outbound):")
        for name, rel in links:
            linked_file = find_target_file(name)
            summary = get_file_summary(linked_file) if linked_file else "Not ingested."
            print(f"  -> [[{name}]] ({rel}) : {summary}")
    else:
        print(" FORWARD LINKS: None.")
        
    print("-" * 60)
    target_basename = os.path.basename(target_file).replace('.md', '')
    backlinks = find_backlinks(target_basename)
    
    if backlinks:
        print(" BACKLINKS (Inbound / Dependencies):")
        for bl in backlinks:
            bl_file = find_target_file(bl)
            summary = get_file_summary(bl_file) if bl_file else ""
            print(f"  <- [[{bl}]] : {summary}")
    else:
        print(" BACKLINKS: None.")
        
    print("=" * 60)
    print(" EXECUTION PATH (AST Edges):")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA busy_timeout=5000;')
        c = conn.cursor()
        
        # --- ACCESS COUNT INCREMENT ---
        try:
            c.execute("UPDATE pages SET access_count = IFNULL(access_count, 0) + 1, last_accessed = datetime('now') WHERE path = ?", (target_file,))
            conn.commit()
        except Exception:
            pass
            
        # 1. File-to-file AST links
        c.execute('SELECT target_id, relation FROM edges WHERE source_id = ?', (target_file,))
        rows = c.fetchall()
        has_ast = False
        if rows:
            has_ast = True
            for target_id, relation in rows:
                print(f"  [{relation}] -> {target_id}")
        
        # 2. Graph Entity Triplets
        c.execute('SELECT id FROM nodes WHERE source_path = ?', (target_file,))
        entities = [r[0] for r in c.fetchall()]
        has_graph = False
        if entities:
            first_header = True
            for ent in entities:
                c.execute('SELECT target_id, relation FROM edges WHERE source_id = ?', (ent,))
                edges_rows = c.fetchall()
                if edges_rows:
                    if first_header:
                        print(" GRAPH TRIPLETS (Semantic Knowledge):")
                        first_header = False
                    has_graph = True
                    for target_id, relation in edges_rows:
                        print(f"  ({ent}) -[{relation}]-> ({target_id})")
                        
        if not has_ast and not has_graph:
            print("  No downstream execution path or graph triplets found.")
            
        print("-" * 60)
        print(" RELATED NODES (via FTS5 BM25):")
        keywords = re.findall(r'\b[a-zA-Z0-9_]+\b', target_basename.lower())
        valid_kws = [kw for kw in keywords if len(kw) > 2]
        if valid_kws:
            query_str = " OR ".join([f'"{kw}"' for kw in valid_kws])
            c.execute('SELECT path FROM pages_fts WHERE pages_fts MATCH ? AND path != ? ORDER BY rank LIMIT 3', (query_str, target_file))
            fts_rows = c.fetchall()
            if fts_rows:
                for row in fts_rows:
                    print(f"  ~ {os.path.basename(row[0])}")
            else:
                print("  No related nodes found via text match.")
        else:
            print("  No related nodes found via text match.")
            
        conn.close()
    except Exception as e:
        print(f"  [DB Error] {e}")
        
    print("=" * 60)
    print(" Graph Neighborhood Resolved. Use this context to answer the user.")

def inject_triplets(json_data):
    try:
        import sqlite3
        if os.path.exists(json_data):
            with open(json_data, "r", encoding="utf-8") as f:
                json_data = f.read()
        triplets = json.loads(json_data)
        if not triplets:
            print("[INFO] No triplets provided.")
            return
            
        conn = get_db()
        c = conn.cursor()
        
        # Collect unique sources to clear stale triplets first
        unique_sources = set()
        for t in triplets:
            if t.get("src"):
                unique_sources.add(t.get("src"))
                
        for src in unique_sources:
            try:
                c.execute('DELETE FROM edges WHERE source_id IN (SELECT id FROM nodes WHERE source_path = ?)', (src,))
                c.execute('DELETE FROM nodes WHERE source_path = ?', (src,))
            except Exception as e:
                print(f"[WARNING] Failed to clear stale triplets for {src}: {e}")
        
        count = 0
        for t in triplets:
            sub = t.get("s")
            pred = t.get("p")
            obj = t.get("o")
            src = t.get("src", "Unknown")
            if sub and pred and obj:
                c.execute('INSERT OR REPLACE INTO nodes (id, type, name, source_path) VALUES (?, ?, ?, ?)', (sub, 'Entity', sub, src))
                c.execute('INSERT OR REPLACE INTO nodes (id, type, name, source_path) VALUES (?, ?, ?, ?)', (obj, 'Entity', obj, src))
                c.execute('INSERT OR IGNORE INTO edges (source_id, target_id, relation) VALUES (?, ?, ?)', (sub, obj, pred))
                count += 1
                
        conn.commit()
        conn.close()
        print(f"[SUCCESS] Injected {count} triplets into orion.db.")
        
        # --- IDE-1: Contradiction Engine ---
        import subprocess
        contradict_script = os.path.join(os.path.dirname(__file__), 'contradict.py')
        if os.path.exists(contradict_script):
            subprocess.Popen([sys.executable, contradict_script, "detect"],
                             stdout=sys.stdout, stderr=sys.stderr)
            
    except Exception as e:
        print(f"[ERROR] Failed to inject triplets: {e}")

# === CLI ===
def main():
    parser = argparse.ArgumentParser(description="Orion Operations System")
    subparsers = parser.add_subparsers(dest="command")
    
    parser_init = subparsers.add_parser("init", help="Bootstrap the orion directory structure")
    
    parser_ingest = subparsers.add_parser("ingest", help="Ingest files into the orion")
    parser_ingest.add_argument("paths", nargs="+", help="Paths or files to ingest")
    parser_ingest.add_argument("--autonomy", default="balanced", choices=["balanced", "high", "strict"])
    
    parser_resolve = subparsers.add_parser("resolve", help="Resolve orion nodes for context routing")
    parser_resolve.add_argument("node", help="Node name to resolve")
    
    parser_inject = subparsers.add_parser("inject_triplets", help="Inject graph triplets (JSON array)")
    parser_inject.add_argument("json_data", help="JSON string containing triplets")

    args = parser.parse_args()
    
    if args.command == "init":
        bootstrap()
    elif args.command == "ingest":
        ingest_main(args.paths, args.autonomy)
    elif args.command == "resolve":
        resolve_wiki(args.node)
    elif args.command == "inject_triplets":
        inject_triplets(args.json_data)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
