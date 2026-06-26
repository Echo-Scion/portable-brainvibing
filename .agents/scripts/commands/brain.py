import argparse
import os
import re
import sys
import json
import urllib.request
from pathlib import Path

# Force utf-8 encoding for standard output to avoid UnicodeEncodeError on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

try:
    import psutil
except ImportError:
    psutil = None

class NanoBrain:
    def __init__(self, model="qwen2.5:0.5b"):
        self.endpoint = "http://localhost:11434/api/generate"
        self.model = model
        self.tier_level = 1 # 1: Low, 2: Medium, 3: High
        self.tier_name = "low_intelligence"
        
        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        manifest_path = os.path.join(agents_dir, ".project_manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    profile = manifest.get("llm_profile", {})
                    self.tier_name = profile.get("intelligence_tier", "low_intelligence")
                    
                    if self.tier_name == "high_intelligence": self.tier_level = 3
                    elif self.tier_name == "medium_intelligence": self.tier_level = 2
                    elif self.tier_name == "low_intelligence": self.tier_level = 1
                    else: self.tier_level = 0 # cloud_agent / none
            except Exception:
                pass

    def check_tier(self, required_level, feature_name):
        if self.tier_level < required_level:
            return f"[DELEGATE_TO_CLOUD] Error: Required Medium Intelligence (or higher) for {feature_name}. Current tier is '{self.tier_name}'. Fallback gracefully to Cloud Agent LLM."
        return None

    def ping(self):
        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        if os.path.exists(status_file):
            try:
                with open(status_file, "r") as f:
                    if f.read().strip().upper() == "OFF":
                        return False
            except Exception:
                pass

        if psutil:
            try:
                mem = psutil.virtual_memory()
                if mem.percent > 90:
                    print(f"\n[WARNING] System RAM at {mem.percent}%. Disabling NanoBrain to prevent lockup.")
                    return False
            except Exception:
                pass
        try:
            req = urllib.request.Request("http://localhost:11434/", method="GET")
            with urllib.request.urlopen(req, timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def generate(self, prompt, system="You are Orion NanoBrain, a strict JSON extracting router. You do NOT write code."):
        if not self.ping():
            return None
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read().decode('utf-8'))
                return resp.get('response', '')
        except Exception as e:
            return None



    def vibe_check(self, text):
        prompt = f"Does this code use hardcoded colors or raw pixel values instead of theme variables?\n\nCODE: {text[:1000]}\n\nAnswer YES or NO."
        return self.generate(prompt, system="You are a binary linter. Answer ONLY with YES or NO.")

    def caveman_compress(self, text):
        system = "You are an English compression engine. You MUST output ONLY in English. Do not use any other languages. Use terse, telegraphic fragments."
        prompt = f"Convert this text to English Caveman Mode (terse, fragment sentences, 100% technical facts):\n\nTEXT: {text}\n\nENGLISH CAVEMAN OUTPUT:"
        return self.generate(prompt, system=system)

    def draft_boilerplate(self, intent):
        # Requires Medium Intelligence
        block_msg = self.check_tier(2, "Boilerplate Drafting")
        if block_msg:
            return block_msg
            
        system = "You are a Senior Architect LLM. Generate standard boilerplate code for the given intent. Output ONLY the code, no markdown wrappers."
        prompt = f"Draft the boilerplate component for this intent:\n\n{intent}"
        code = self.generate(prompt, system=system)
        return code if code else "[DELEGATE_TO_CLOUD] Error: Generation failed. Fallback to Cloud Agent."

    def extract_triplets(self, text):
        # Requires High Intelligence
        block_msg = self.check_tier(3, "Complex Triplet Extraction")
        if block_msg:
            return block_msg
            
        system = "You are a Brainvibing Knowledge Extractor. Extract triplets in JSON format."
        prompt = f"Extract (Subject, Predicate, Object) from this text:\n{text}"
        res = self.generate(prompt, system=system)
        return res if res else "[DELEGATE_TO_CLOUD] Error: Extraction failed. Fallback to Cloud Agent."

def extract_keywords(text):
    stop_words = {'i', 'need', 'to', 'build', 'the', 'a', 'an', 'and', 'or', 'for', 'with', 'on', 'in', 'of', 'how', 'do', 'what', 'create', 'make', 'update', 'fix'}
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    base_keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Semantic Expansion via NanoBrain
    try:
        nb = NanoBrain()
        if nb.ping():
            sys_prompt = "You are a synonym generator. Output exactly 3 comma-separated technical synonyms for the intent. NO other text. Example: 'login' -> 'auth,authentication,session'"
            prompt = f"Intent: {text}\nSynonyms:"
            expansion = nb.generate(prompt, system=sys_prompt)
            if expansion:
                expanded_words = [w.strip().lower() for w in expansion.split(",") if w.strip()]
                # Filter out hallucinated sentences
                expanded_words = [w for w in expanded_words if len(w.split()) == 1 and w.isalpha()]
                return list(set(base_keywords + expanded_words))
    except Exception:
        pass
        
    return base_keywords

def search_files(directory, keywords):
    matches = []
    if not os.path.exists(directory):
        return matches
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.md'):
                continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    score = sum(1 for kw in keywords if kw in content)
                    if score > 0:
                        if any(kw in file.lower() for kw in keywords):
                            score += 3
                        matches.append((score, filepath))
            except Exception:
                pass
                
    matches.sort(reverse=True, key=lambda x: x[0])
    return [m[1] for m in matches[:3]]

def get_ast_block(filepath, tag_name):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(f'<{tag_name}>(.*?)</{tag_name}>', content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

def sync(intent):
    print(f" NEURO-LINK ENGAGED: Syncing Brain for intent: '{intent}'")
    keywords = extract_keywords(intent)
    print(f" Extracted Tokens: {keywords}")
    
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, '.orion')
    context_dir = os.path.join(workspace_dir, 'context')
    
    skills = search_files(os.path.join(agents_dir, 'skills'), keywords)
    
    # Rute Semantic via LightRAG (SQLite FTS5 BM25)
    rules = []
    db_path = os.path.join(orion_dir, 'orion.db')
    if os.path.exists(db_path):
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            conn.execute('PRAGMA busy_timeout=5000;')
            c = conn.cursor()
            # FTS5 BM25 query: Search for any of the keywords
            query_str = " OR ".join([f'"{kw}"' for kw in keywords])
            c.execute('SELECT path FROM pages_fts WHERE pages_fts MATCH ? ORDER BY rank LIMIT 3', (query_str,))
            for row in c.fetchall():
                path = row[0]
                if "archive/" in path.replace("\\", "/").lower():
                    basename = os.path.basename(path)
                    dest = os.path.join(agents_dir, "rules", basename)
                    try:
                        import shutil
                        if os.path.exists(path):
                            shutil.copy(path, dest)
                            print(f"  [AMNESIA RECALL] JIT Retrieved rule '{basename}' from archive!")
                        rules.append(dest)
                    except Exception as e:
                        print(f"  [AMNESIA ERROR] Could not recall {basename}: {e}")
                else:
                    rules.append(path)
            conn.close()
        except Exception as e:
            print(f"  [ERROR] LightRAG Query Failed: {e}")
            
    wiki_nodes = search_files(orion_dir, keywords)
    saas_nodes = search_files(context_dir, keywords)
    
    print("\n" + "="*60)
    print(" UNIFIED CONTEXT PACKET (LIGHTRAG-HARMONIZED)")
    print("="*60)
    
    # --- Brainvibing Injection (RULES_INDEX.md line-by-line) ---
    rules_index_path = os.path.join(agents_dir, "rules", "RULES_INDEX.md")
    if os.path.exists(rules_index_path):
        with open(rules_index_path, "r", encoding="utf-8") as f:
            rules_content = f.read()
            
        print("\n##  Standard Operating Procedures (Micro-Rules)")
        matches = []
        nb = None
        try:
            temp_nb = NanoBrain()
            if temp_nb.ping():
                nb = temp_nb
        except:
            pass
            
        for line in rules_content.split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            line_lower = line.lower()
            
            # Global rules always apply
            if "global" in line_lower:
                matches.append(line.strip())
                continue
                
            is_match = False
            # Semantic filter via NanoBrain
            if nb:
                sys_prompt = "You are a binary classifier. Answer ONLY with YES or NO. Is the RULE relevant to the INTENT?"
                prompt = f"INTENT: {intent}\nRULE: {line.strip()}\nRelevant (YES/NO):"
                try:
                    resp = nb.generate(prompt, system=sys_prompt)
                    if resp and "YES" in resp.upper():
                        is_match = True
                except: pass
                
            # Fallback to lexical
            if not is_match and any(kw in line_lower for kw in keywords):
                is_match = True
                
            if is_match:
                matches.append(line.strip())
                
        if matches:
            for m in matches[:5]:
                print(f"  {m}")
        else:
            print("  No specific standards matched. Proceeding with global baseline.")
    # ---------------------------------------------------------
    
    if skills or rules:
        print("\n##  Motor Cortex (Rules & Skills)")
        for r in (rules + skills)[:3]:
            rel_path = os.path.relpath(r, workspace_dir)
            print(f"- [Mandatory Execution Protocol]: {rel_path}")
            
            # Apply NanoBrain compression ONLY to .md rules/skills
            if r.endswith('.md'):
                try:
                    with open(r, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) < 4000: # Limit size to prevent 0.5b timeout
                        temp_nb = NanoBrain()
                        if temp_nb.ping():
                            compressed = temp_nb.caveman_compress(content)
                            if compressed and len(compressed) > 10:
                                print(f"  [COMPRESSED CONTEXT]: {compressed.replace(chr(10), ' ')}")
                except Exception:
                    pass
            
    if wiki_nodes:
        print("\n##  Hippocampus (Orion Knowledge)")
        for w in wiki_nodes:
            rel_path = os.path.relpath(w, workspace_dir)
            print(f"- [Concept Node]: {rel_path}")
            
    # --- Orion Manifest RAG injection ---
    manifest_path = os.path.join(orion_dir, "_manifest.json")
    wiki_hits = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                for layer, entries in manifest.get("layers", {}).items():
                    for entry in entries:
                        filepath = entry.get("filepath", "").lower()
                        if any(kw in filepath for kw in keywords):
                            wiki_hits.append(os.path.basename(entry.get("orion_file", "")).replace(".md", ""))
        except Exception:
            pass
            
    if wiki_hits:
        print("\n##  Deep RAG (Orion Graph Hits)")
        print(f"  Found potential nodes: {', '.join(wiki_hits[:3])}")
        top_node = wiki_hits[0]
        print(f"  [AUTO-RAG]: Resolving primary node '{top_node}' automatically...\n")
        try:
            import subprocess
            ops_script = os.path.join(agents_dir, "scripts", "orion.py")
            # We output directly instead of capturing so it prints immediately in sync stream
            subprocess.run([sys.executable, ops_script, "orion_ops", "resolve", top_node], check=False)
        except Exception as e:
            print(f"  [ERROR] Could not execute Auto-RAG: {e}")
    # -----------------------------------
    
    # --- NanoBrain Active Ping ---
    nb = NanoBrain()
    if nb.ping():
        print("\n## [NanoBrain] NanoBrain (Ollama) is ONLINE")
        print("  [CAPABILITY]: You can use `python .agents/scripts/orion.py brain nanobrain vibe_check <text>` for instant UI aesthetic validation without consuming major tokens.")
            
    # --- Working Memory (Holographic Handoff) ---
    handoff_path = os.path.join(orion_dir, "working", "handoff.md")
    if os.path.exists(handoff_path):
        print("\n##  Working Memory (Session Handoff)")
        try:
            with open(handoff_path, "r", encoding="utf-8") as f:
                handoff_content = f.read()
            print("  [ACTIVE HANDOFF DETECTED]:")
            for line in handoff_content.splitlines():
                print(f"    {line}")
                
            # Auto-Archive
            import datetime, shutil
            episodic_dir = os.path.join(orion_dir, "episodic")
            if not os.path.exists(episodic_dir): os.makedirs(episodic_dir)
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.move(handoff_path, os.path.join(episodic_dir, f"handoff_{stamp}.md"))
            print("  [INFO] Handoff archived to episodic memory to prevent future loop.")
        except Exception as e:
            print(f"  [ERROR] Failed to process working memory: {e}")
    # --------------------------------------------

    if saas_nodes:
        print("\n##  Working Memory (SaaS State)")
        for s in saas_nodes:
            rel_path = os.path.relpath(s, workspace_dir)
            print(f"- [Active State]: {rel_path}")
            if get_ast_block(s, 'saas-state'):
                print("  [DATA-NODE]: Extracted semantic state successfully.")
    
    if not (skills or rules or wiki_nodes or saas_nodes):
        print("\n[WARNING]: No contextual nodes found for these tokens. AI must rely on zero-shot reasoning.")
        
    print("\n---\n[DIRECTIVE] Read the above files with `view_file` BEFORE modifying code. Adhere to rules. Proceed.")

def page_context(keywords):
    agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    workspace_dir = os.path.dirname(agents_dir)
    orion_dir = os.path.join(workspace_dir, ".orion")
    if not os.path.exists(orion_dir):
        os.makedirs(orion_dir)
        
    page_path = os.path.join(orion_dir, "page.md")
    targets = [os.path.join(agents_dir, "rules"), os.path.join(agents_dir, "skills")]
    relevant_chunks = []
    
    for target in targets:
        for root, dirs, files in os.walk(target):
            for file in files:
                if not file.endswith(".md"): continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    chunks = re.split(r'\n(?=#+ )', content)
                    try:
                        import sys
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        if script_dir not in sys.path:
                            sys.path.insert(0, script_dir)
                        from compile_rules import parse_markdown_to_dict
                        
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                
                                # Ephemeral Caveman Compilation
                                chunk_dict = parse_markdown_to_dict(chunk.strip())
                                dense_json = json.dumps(chunk_dict, indent=2)
                                relevant_chunks.append(f"### Source: {file} | {header}\n```json\n{dense_json}\n```\n")
                    except Exception as e:
                        # Fallback if parsing fails
                        for chunk in chunks:
                            chunk_lower = chunk.lower()
                            if any(kw.lower() in chunk_lower for kw in keywords):
                                header_match = re.match(r'(#+ .*?)\n', chunk)
                                header = header_match.group(1) if header_match else f"Excerpt from {file}"
                                relevant_chunks.append(f"### Source: {file} | {header}\n{chunk.strip()}\n")
                except Exception:
                    pass
                    
    with open(page_path, "w", encoding="utf-8") as f:
        f.write("# Ephemeral Pager Context\n\n")
        f.write("\n---\n".join(relevant_chunks))
        
    print(f"Paging complete. {len(relevant_chunks)} chunks swapped into {os.path.relpath(page_path, workspace_dir)}")


def main():
    parser = argparse.ArgumentParser(description="Neuro-Link Brain Engine")
    subparsers = parser.add_subparsers(dest='command')
    
    sync_parser = subparsers.add_parser('sync', help='Sync brain context')
    sync_parser.add_argument('intent', type=str, help='The task or intent')
    
    nb_parser = subparsers.add_parser('nanobrain', help='Execute NanoBrain tasks')
    nb_parser.add_argument('action', choices=['vibe_check', 'extract', 'compress', 'draft', 'on', 'off', 'status'], help='Action to perform')
    nb_parser.add_argument('text', nargs='?', type=str, default='', help='Input text')
    
    page_parser = subparsers.add_parser('page', help='Ephemeral context slicer')
    page_parser.add_argument('keywords', nargs='+', help='Keywords to extract')
    
    args = parser.parse_args()
    if args.command == 'sync':
        sync(args.intent)
    elif args.command == 'nanobrain':
        agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        status_file = os.path.join(agents_dir, ".nanobrain_status")
        
        if args.action == 'on':
            with open(status_file, "w") as f: f.write("ON")
            print("🟢 NanoBrain is now ENABLED.")
            return
        elif args.action == 'off':
            with open(status_file, "w") as f: f.write("OFF")
            print("🔴 NanoBrain is now DISABLED.")
            return
        elif args.action == 'status':
            state = "ON"
            if os.path.exists(status_file):
                with open(status_file, "r") as f: state = f.read().strip().upper()
            print(f"NanoBrain Toggle: {state}")
            return

        nb = NanoBrain()
        if not nb.ping():
            print("Error: NanoBrain is DISABLED or Ollama is not running on localhost:11434")
            return
            
        if args.action == 'vibe_check':
            print(nb.vibe_check(args.text))
        elif args.action == 'extract':
            print(nb.extract_triplets(args.text))
        elif args.action == 'compress':
            print(nb.caveman_compress(args.text))
        elif args.action == 'draft':
            print(nb.draft_boilerplate(args.text))
    elif args.command == 'page':
        page_context(args.keywords)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
