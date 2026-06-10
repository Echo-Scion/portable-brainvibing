#!/usr/bin/env python
"""
nano_compressor.py
------------------
Single-shot Holographic Context Pager.
Compresses .orion/working/handoff.md using Ollama and extracts 
knowledge graph triplets to orion.db.
"""

import os
import json
import urllib.request
import sqlite3
import datetime
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
ORION_DIR = os.path.join(WORKSPACE_DIR, '.orion')
DB_PATH = os.path.join(ORION_DIR, 'orion.db')
HANDOFF_FILE = os.path.join(ORION_DIR, 'working', 'handoff.md')
EPISODIC_DIR = os.path.join(ORION_DIR, 'episodic')

class NanoBrain:
    def __init__(self, model="qwen2.5:0.5b"):
        self.endpoint = "http://localhost:11434/api/generate"
        self.model = model

    def ping(self):
        try:
            req = urllib.request.Request("http://localhost:11434/", method="GET")
            with urllib.request.urlopen(req, timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def generate(self, prompt, system="You are an expert summarizer. Use Caveman English. Output terse, telegraphic fragments ONLY."):
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
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read().decode('utf-8'))
                return resp.get('response', '')
        except Exception as e:
            print(f"[NanoCompressor] Ollama generation failed: {e}")
            return None

    def extract_and_store_triplets(self, text, source_id):
        if not self.ping(): return
        print(f"[NanoCompressor] Extracting Triplets for LightRAG Graph from {os.path.basename(source_id)}...")
        sys_prompt = "You are an extraction engine. Output raw lines using the | delimiter ONLY. Do not use JSON."
        prompt = f"Extract 3-5 high-value architectural triplets from this text:\n\n{text[:2000]}\n\nFormat EACH line EXACTLY as: Subject | Predicate | Object"
        response = self.generate(prompt, system=sys_prompt)
        if not response: return
        
        try:
            triplets = []
            for line in response.split('\n'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    triplets.append(parts[:3])
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for triplet in triplets:
                if len(triplet) == 3:
                    sub, pred, obj = triplet
                    c.execute('INSERT OR IGNORE INTO nodes (id, type, name, source_path) VALUES (?, ?, ?, ?)', (sub, 'Entity', sub, source_id))
                    c.execute('INSERT OR IGNORE INTO nodes (id, type, name, source_path) VALUES (?, ?, ?, ?)', (obj, 'Entity', obj, source_id))
                    c.execute('INSERT OR IGNORE INTO edges (source_id, target_id, relation) VALUES (?, ?, ?)', (sub, obj, pred))
            conn.commit()
            conn.close()
            print(f"[NanoCompressor] Successfully ingested {len(triplets)} triplets into orion.db")
        except Exception as e:
            print(f"[NanoCompressor] Triplet parsing failed: {e}")

def compress_handoff():
    if not os.path.exists(HANDOFF_FILE):
        print(f"[NanoCompressor] No handoff file found at {HANDOFF_FILE}")
        return

    with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    if "[CAVEMAN_COMPRESSED]" in content or not content.strip():
        print("[NanoCompressor] Handoff already compressed or empty. Aborting.")
        return

    nb = NanoBrain()
    if not nb.ping():
        print("[NanoCompressor] Ollama offline. Aborting compression.")
        return

    print("[NanoCompressor] Engaging local model for Holographic Paging...")
    prompt = f"Summarize this session handoff using technical caveman mode. Keep codes/paths exact.\n\nTEXT:\n{content}"
    
    summary = nb.generate(prompt)
    
    if summary:
        if not os.path.exists(EPISODIC_DIR):
            os.makedirs(EPISODIC_DIR)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(EPISODIC_DIR, f"handoff_raw_{stamp}.md")
        shutil.copy2(HANDOFF_FILE, backup_path)
        
        new_content = f"# Handoff (Holographic Paging Active)\n\n> [CAVEMAN_COMPRESSED]\n{summary}\n"
        with open(HANDOFF_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"[NanoCompressor] Compression complete. Original backed up to {backup_path}")
        
        nb.extract_and_store_triplets(summary, HANDOFF_FILE)
    else:
        print("[NanoCompressor] Summarization returned empty. Aborting.")

if __name__ == "__main__":
    compress_handoff()
