#!/usr/bin/env python
"""
auto_delegate.py
----------------
Sleep-State Delegation Engine & Micro-Fix Swarm.
Usage: python auto_delegate.py <script_path>

Executes a target script locally. If it fails due to a Micro-Fix (Syntax/Lint),
it spawns a local Swarm (3 concurrent Ollama threads) to propose speculative fixes.
If it fails due to a Logical/Architecture error, it aborts analysis immediately
to prevent NanoBrain hallucination (Fake Feature prevention).
"""

import sys
import subprocess
import os
import time
import json
import urllib.request
import concurrent.futures

def truncate(text, max_len=1000):
    if not text:
        return ""
    if len(text) > max_len:
        return text[:max_len//2] + f"\n... [{len(text) - max_len} chars omitted] ...\n" + text[-max_len//2:]
    return text

def run_swarm_node(node_id, prompt):
    """Runs a single Ollama node for speculative execution."""
    try:
        payload = {
            "model": "qwen2.5:0.5b",
            "prompt": f"[Swarm Node {node_id}]\n{prompt}",
            "system": "You are a micro-fix swarm agent. Output ONLY a 1-sentence fix for this syntax/lint error. Be highly terse. Caveman English.",
            "stream": False
        }
        req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read().decode('utf-8'))
            return f"Node {node_id}: {resp.get('response', '').strip()}"
    except Exception as e:
        return f"Node {node_id}: [OFFLINE or TIMEOUT]"

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_delegate.py <script_path> [args...]")
        sys.exit(1)

    script_path = sys.argv[1]
    args = sys.argv[2:]

    if not os.path.exists(script_path):
        print(f"[ERROR] Script not found: {script_path}")
        sys.exit(1)

    ext = os.path.splitext(script_path)[1].lower()
    interpreter = []
    
    if ext == ".py":
        interpreter = [sys.executable]
    elif ext == ".sh":
        interpreter = ["bash"]
    elif ext in [".js", ".ts"]:
        interpreter = ["node"]

    cmd = interpreter + [script_path] + args

    print(f"[DELEGATE] Sleep-State Delegation Active")
    print(f"Target: {' '.join(cmd)}")
    print("-" * 40)
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        elapsed = time.time() - start_time
        
        if stdout:
            print("[STDOUT]")
            print(truncate(stdout))
            
        if stderr:
            print("[STDERR]")
            print(truncate(stderr))
            
        print("-" * 40)
        print(f"[TIME] Elapsed: {elapsed:.2f}s")
        print(f"[EXIT] Exit Code: {process.returncode}")
        
        if process.returncode != 0 and stderr:
            # Micro-Fix Guard: Only trigger swarm for syntax, lint, type, or import errors.
            err_lower = stderr.lower()
            micro_fix_keywords = ['syntaxerror', 'lint', 'import', 'typeerror', 'referenceerror', 'not defined', 'cannot find']
            
            if any(k in err_lower for k in micro_fix_keywords):
                print("\n[MICRO-FIX SWARM] Syntax/Lint error detected. Spawning 3 Speculative Nodes...")
                # 0.5b models collapse with long logs. Send only the last 300 characters.
                tail_log = stderr[-300:] if len(stderr) > 300 else stderr
                prompt = f"Propose a 1-sentence fix for this specific error:\n\n{tail_log}"
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(run_swarm_node, i, prompt) for i in range(1, 4)]
                    for future in concurrent.futures.as_completed(futures):
                        print(f" ↳ {future.result()}")
            else:
                print("\n[GUARDRAIL] Logical/Architecture error detected. Swarm analysis aborted to prevent Nano LLM hallucination.")
                print("[ACTION] Esculating to Premium AI Tier.")
                
        sys.exit(process.returncode)

    except Exception as e:
        print(f"![CRITICAL ERROR] Failed to execute delegation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
