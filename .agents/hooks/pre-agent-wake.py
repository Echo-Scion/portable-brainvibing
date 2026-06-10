#!/usr/bin/env python
"""
pre-agent-wake.py
-----------------
Omni-Buffer Hook. This script is called by the IDE extension or background watcher
before the AI agent starts processing. It drops the current state into a standardized
JSON file (context.json) so the agent has a single source of truth for context,
eliminating the need to parse raw terminal stdout.
"""

import os
import json
import time
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
CONTEXT_DIR = os.path.join(BASE_DIR, '.orion', 'working')
CONTEXT_FILE = os.path.join(CONTEXT_DIR, 'context.json')

def main():
    parser = argparse.ArgumentParser(description="Omni-Buffer Hook for AI Agents")
    parser.add_argument("--active-file", type=str, default="", help="Path to the currently active file in the IDE")
    parser.add_argument("--terminal-error", type=str, default="", help="The last active terminal error or exception")
    parser.add_argument("--ide-source", type=str, default="unknown", help="The source IDE calling this hook (e.g., vscode, cursor, antigravity, oriontation)")
    parser.add_argument("--user-intent", type=str, default="", help="Any pre-processed user intent")
    
    args = parser.parse_args()
    
    if not os.path.exists(CONTEXT_DIR):
        os.makedirs(CONTEXT_DIR)
        
    base_agents_dir = os.path.dirname(SCRIPT_DIR)
    learnings_path = os.path.join(base_agents_dir, "LEARNINGS.md")
    evolution_log_path = os.path.join(base_agents_dir, "EVOLUTION_LOG.jsonl")
    
    # 1. Heartbeat Cron Logic
    evolution_overdue = False
    unprocessed_learnings = 0
    if os.path.exists(learnings_path):
        with open(learnings_path, 'r', encoding='utf-8') as f:
            unprocessed_learnings = f.read().count("[Darwinian Hook]")
    
    if unprocessed_learnings >= 3:
        # Check if we evolved recently
        last_evolution_ts = 0
        if os.path.exists(evolution_log_path):
            with open(evolution_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    try:
                        last_line = json.loads(lines[-1])
                        # Simplified check: just flag if we have >=3 failures since last evolution
                        # In a real setup, we'd parse the ISO timestamp
                    except json.JSONDecodeError:
                        pass
        evolution_overdue = True
        
        # [RADICAL INNOVATION]: Autonomic Evolution Hook
        # Spawn the evolution engine in the background so the AI doesn't have to manually trigger it
        import subprocess
        import sys
        try:
            orion_script = os.path.join(base_agents_dir, 'scripts', 'orion.py')
            subprocess.Popen([sys.executable, orion_script, 'evolve', 'mine-friction'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            print("[AUTO-EVOLVE] Triggered background evolution via orion.py")
        except Exception as e:
            print(f"[AUTO-EVOLVE] Failed to start background evolution: {e}")

    context_data = {
        "timestamp_ms": int(time.time() * 1000),
        "active_file": args.active_file,
        "terminal_error": args.terminal_error,
        "user_intent": args.user_intent,
        "ide_source": args.ide_source,
        "evolution_overdue": evolution_overdue,
        "unprocessed_learnings": unprocessed_learnings
    }
    
    temp_file = CONTEXT_FILE + ".tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2)
    os.replace(temp_file, CONTEXT_FILE)
        
    print(f"[OK] Omni-Buffer updated at {CONTEXT_FILE}")

if __name__ == "__main__":
    main()
