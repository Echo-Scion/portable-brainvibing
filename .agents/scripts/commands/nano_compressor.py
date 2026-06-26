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

try:
    from commands.brain import NanoBrain
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from brain import NanoBrain

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
ORION_DIR = os.path.join(WORKSPACE_DIR, '.orion')
DB_PATH = os.path.join(ORION_DIR, 'orion.db')
HANDOFF_FILE = os.path.join(ORION_DIR, 'working', 'handoff.md')
EPISODIC_DIR = os.path.join(ORION_DIR, 'episodic')

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
        print("\n[TRIPLET_REQUEST] 1 files need graph triplet extraction.")
        print("⚡ RECOMMENDED TIER: BUDGET")
        print("Files:")
        rel_handoff = os.path.relpath(HANDOFF_FILE, WORKSPACE_DIR).replace("\\", "/")
        print(f"1. {rel_handoff} (source: {rel_handoff})")
        print("[ACTION] Read each source file, extract 3-5 Subject|Predicate|Object triplets,")
        print("then run: python .agents/scripts/orion.py orion_ops inject_triplets '<json>'")

    else:
        print("[NanoCompressor] Summarization returned empty. Aborting.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Holographic Context Pager")
    parser.add_argument("action", nargs="?", default="compress-handoff", help="Action to perform")
    parser.add_argument("target", nargs="?", help="Target file")
    args = parser.parse_args()
    
    if args.action in ("compress-handoff", "compress"):
        compress_handoff()
    else:
        print(f"[NanoCompressor] Action {args.action} not fully implemented yet.")
