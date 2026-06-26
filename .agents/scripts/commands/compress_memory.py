import os
import re
import shutil
from datetime import datetime

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
    state_hash = hashlib.md5(blueprint.encode()).hexdigest()[:4].upper()
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

    def ast_aware_preserve(m):
        text = m.group(0)
        compressed_text = caveman_compress(text)
        return f"## 3. Context Offloading Entry\n> [COMPRESSED: Caveman Token-Clipper Active]\n{compressed_text}\n\n"

    new_handoff_content = re.sub(
        r'(## 3\. Context Offloading Entry\n).*?(?=\n## 4\.|\n## \d+\.|$)',
        ast_aware_preserve,
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
            

def compress_memory():
    print("[CLEAN] Surgical Memory Compression starting...")
    generate_fractal_shorthand()
    handoff_compressed = compress_handoff()
    tasks_compressed = compress_tasks()
    
    if not handoff_compressed and not tasks_compressed:
        print("[OK] No compressable context found. System memory is lean and efficient.")
    else:
        print(f"[OK] Memory compression complete. Stale memories moved to {ARCHIVE_DIR}")

if __name__ == "__main__":
    compress_memory()