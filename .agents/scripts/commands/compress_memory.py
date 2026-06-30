import os
import re
import sys
import shutil
from datetime import datetime

# Force utf-8 encoding for standard output to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
ARCHIVE_DIR = os.path.join(BASE_DIR, 'archive')
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, 'compressed_memory.md')
HANDOFF_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'handoff.md')
BLUEPRINT_FILE = os.path.join(WORKSPACE_DIR, 'context', 'BLUEPRINT.md')

def generate_fractal_shorthand():
    """
    Parses architectural details from BLUEPRINT.md and translates it into a
    highly compressed Fractal State Shorthand (DSL) for small models.
    """
    if not os.path.exists(BLUEPRINT_FILE):
        return False
        
    with open(BLUEPRINT_FILE, 'r', encoding='utf-8') as f:
        blueprint = f.read()
        
    shorthand = "[ARCH: "
    
    # Holographic Context Hash Generation (Idea 1)
    import hashlib
    state_hash = hashlib.sha256(blueprint.encode()).hexdigest()[:4].upper()
    shorthand = f"[STATE_HASH: 0x{state_hash}] [ARCH: "
    
    if "flutter" in blueprint.lower(): shorthand += "Flutter]"
    elif "react" in blueprint.lower(): shorthand += "React]"
    else: shorthand += "Unknown]"
    
    if "supabase" in blueprint.lower(): shorthand += " [DB: Supabase]"
    if "riverpod" in blueprint.lower(): shorthand += " [STATE: Riverpod]"
    
    shorthand += " [TIER: BUDGET]"
    
    # Inject into handoff or memory file
    if os.path.exists(HANDOFF_FILE):
        with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
            handoff = f.read()
            
        if "# FRACTAL SHORTHAND" in handoff:
            new_handoff = re.sub(r'(# FRACTAL SHORTHAND\r?\n).*?(?=\n\n)', r'\1' + shorthand, handoff, flags=re.DOTALL)
        else:
            new_handoff = f"# FRACTAL SHORTHAND\n{shorthand}\n\n" + handoff
            
        with open(HANDOFF_FILE, 'w', encoding='utf-8') as f:
            f.write(new_handoff)
        print(f"[OK] Generated Fractal Shorthand: {shorthand}")
        return True
    return False

def compress_handoff():
    if not os.path.exists(HANDOFF_FILE):
        return False

    with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for Offload entries to compress (anything between 3. Context Offloading and 4. Anti-Goals)
    offload_pattern = r'(## 3\. Context Offloading Entry.*?\n)(?=\n## 4\.|\n## \d+\.|$)'
    
    match = re.search(offload_pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return False

    offloaded_text = match.group(1).strip()
    
    if "placeholder" in offloaded_text.lower():
        return False

    def caveman_compress(text):
        # Real caveman compression: remove stopwords to save 30-40% tokens
        stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out', 'against', 'during', 'without', 'before', 'under', 'around', 'among'}
        lines = text.split('\n')
        compressed_lines = []
        for line in lines:
            if line.strip().startswith('```'):
                compressed_lines.append(line)
                continue
            words = line.split()
            compressed_words = [w for w in words if w.lower() not in stopwords]
            compressed_lines.append(" ".join(compressed_words))
        return "\n".join(compressed_lines)

    def caveman_compress_section(m):
        text = m.group(0)
        compressed_text = caveman_compress(text)
        return f"## 3. Context Offloading Entry\n> [COMPRESSED: Caveman Token-Clipper Active]\n{compressed_text}\n\n"

    new_handoff_content = re.sub(
        r'(## 3\. Context Offloading Entry\n).*?(?=\n## 4\.|\n## \d+\.|$)',
        caveman_compress_section,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    if content == new_handoff_content:
         return False

    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        
    mode = 'a' if os.path.exists(ARCHIVE_FILE) else 'w'
    with open(ARCHIVE_FILE, mode, encoding='utf-8') as f:
        f.write(f"\n\n--- Compressed on {datetime.now()} ---\n{offloaded_text}")

    # Rewrite handoff
    with open(HANDOFF_FILE, 'w', encoding='utf-8') as f:
        f.write(new_handoff_content)
        
    print(f"[OK] Handoff memory successfully compressed.")
    return True

def compress_tasks():
    tasks_dir = os.path.join(BASE_DIR, 'workflows', 'tasks')
    if not os.path.exists(tasks_dir):
        return False
        
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    compressed = False
    for file in os.listdir(tasks_dir):
        if not file.endswith('.md'): continue
        path = os.path.join(tasks_dir, file)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Target status indicators meaning the task is done
        is_done = bool(re.search(r'Status:\s*\[x\]', content, re.IGNORECASE) or re.search(r'Status:\s*DONE', content, re.IGNORECASE))
        if is_done:
            dest = os.path.join(ARCHIVE_DIR, file)
            shutil.move(path, dest)
            print(f"[OK] Archived completed task: {file}")
            compressed = True
    return compressed
            

def check_compression_eligibility():
    """
    IDE-4: Smart Memory Compression with Eligibility Rules.
    Checks orion.db to report which pages/nodes are eligible for compression
    and which are protected. Inspired by Cloudflare's compression eligibility.
    """
    db_path = os.path.join(WORKSPACE_DIR, '.orion', 'orion.db')
    if not os.path.exists(db_path):
        print("[SKIP] No orion.db found — eligibility check skipped.")
        return
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if access_count column exists
    cursor.execute("PRAGMA table_info(pages)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'access_count' not in cols:
        print("[SKIP] pages.access_count not yet migrated — skipping eligibility filter.")
        conn.close()
        return
    
    IMPORTANCE_THRESHOLD = 4
    MIN_ACCESS_COUNT = 2
    MIN_AGE_DAYS = 14
    
    # Find eligible pages
    cursor.execute("""
        SELECT path, access_count, importance, updated 
        FROM pages 
        WHERE (importance IS NULL OR importance < ?)
        AND (access_count IS NULL OR access_count < ?)
        ORDER BY updated ASC
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT))
    
    eligible = cursor.fetchall()
    
    # Find protected pages
    cursor.execute("""
        SELECT path, access_count, importance 
        FROM pages 
        WHERE importance >= ? OR access_count >= ?
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT))
    
    protected = cursor.fetchall()
    
    print(f"[ELIGIBILITY] {len(eligible)} pages eligible for compression, {len(protected)} protected.")
    
    if eligible:
        for path, ac, imp, updated in eligible[:5]:
            print(f"  📋 {path} (access={ac or 0}, importance={imp or 1})")
    
    if protected:
        for path, ac, imp in protected[:5]:
            print(f"  🛡️ {path} (access={ac or 0}, importance={imp or 1}) — PROTECTED")
    
    conn.close()


def compress_memory():
    print("[CLEAN] Surgical Memory Compression starting...")
    check_compression_eligibility()
    generate_fractal_shorthand()
    handoff_compressed = compress_handoff()
    tasks_compressed = compress_tasks()
    
    if not handoff_compressed and not tasks_compressed:
        print("[OK] No compressable context found. System memory is lean and efficient.")
    else:
        print(f"[OK] Memory compression complete. Stale memories moved to {ARCHIVE_DIR}")

if __name__ == "__main__":
    compress_memory()