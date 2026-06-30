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
WORKSPACE_DIR = BASE_DIR  # Alias for clarity in identity layer code


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
        # Simplified: flag overdue if >=3 unprocessed learnings exist
        # Recency check not implemented yet (would need timestamp parsing)
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

    # --- IDE-8: Knowledge Base Auto-Sync (Drift Detection) ---
    manifest_path = os.path.join(BASE_DIR, '.orion', '_manifest.json')
    needs_sync = False
    try:
        rules_dir = os.path.join(base_agents_dir, 'rules')
        if os.path.exists(rules_dir) and os.path.exists(manifest_path):
            manifest_mtime = os.path.getmtime(manifest_path)
            latest_rule_mtime = 0
            for root, _, files in os.walk(rules_dir):
                for f in files:
                    if f.endswith('.md'):
                        f_mtime = os.path.getmtime(os.path.join(root, f))
                        if f_mtime > latest_rule_mtime:
                            latest_rule_mtime = f_mtime
            
            if latest_rule_mtime > manifest_mtime:
                needs_sync = True
        elif not os.path.exists(manifest_path) and os.path.exists(rules_dir):
            needs_sync = True
            
        if needs_sync:
            print("[AUTO-SYNC] Ecosystem drift detected. Triggering background graph sync...")
            import subprocess
            import sys
            orion_script = os.path.join(base_agents_dir, 'scripts', 'orion.py')
            print("[AUTO-SYNC] Running synchronous ingest to prevent race conditions...")
            subprocess.run([sys.executable, orion_script, 'orion_ops', 'ingest'], 
                             stdout=sys.stdout, stderr=sys.stderr,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except Exception as e:
        print(f"[AUTO-SYNC] Failed to run sync: {e}")

    # --- IDE-5: Identity Layer Bootstrap ---
    identity_path = os.path.join(WORKSPACE_DIR, 'context', 'AGENT_IDENTITY.md')
    identity_exists = os.path.exists(identity_path)
    top_lessons = []
    
    if not identity_exists:
        # Auto-generate from template + LEARNINGS.md
        template_path = os.path.join(base_agents_dir, 'templates', 'agent-identity-template.md')
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # Extract top lessons from LEARNINGS.md
                if os.path.exists(learnings_path):
                    with open(learnings_path, 'r', encoding='utf-8') as f:
                        learnings_content = f.read()
                    # Extract bullet points (lines starting with - )
                    lesson_lines = [l.strip() for l in learnings_content.split('\n') 
                                    if l.strip().startswith('- ') and len(l.strip()) > 10]
                    top_lessons = lesson_lines[:5]
                
                lessons_str = '\n'.join(f"{i+1}. {l[2:]}" for i, l in enumerate(top_lessons)) if top_lessons else "_(no lessons recorded yet)_"
                
                # Fill template placeholders
                from datetime import datetime
                identity_content = template.replace('{{project_name}}', os.path.basename(WORKSPACE_DIR))
                identity_content = identity_content.replace('{{framework}}', 'detected at runtime')
                identity_content = identity_content.replace('{{user_name}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{user_role}}', '_(set during onboarding)_')
                identity_content = identity_content.replace('{{timezone}}', time.strftime('%Z'))
                identity_content = identity_content.replace('{{primary_stack}}', '_(extracted from BLUEPRINT.md)_')
                identity_content = identity_content.replace('{{top_lessons}}', lessons_str)
                identity_content = identity_content.replace('{{anti_goals}}', '- Do NOT re-initialize .orion.db repeatedly\n- Do NOT destroy handoff.md during brain sync\n- Do NOT use sed/awk for file modifications')
                identity_content = identity_content.replace('{{timestamp}}', datetime.now().strftime('%Y-%m-%d'))
                
                context_dir_path = os.path.dirname(identity_path)
                if not os.path.exists(context_dir_path):
                    os.makedirs(context_dir_path)
                with open(identity_path, 'w', encoding='utf-8') as f:
                    f.write(identity_content)
                identity_exists = True
                print(f"[IDENTITY] Auto-generated {identity_path}")
            except Exception as e:
                print(f"[IDENTITY] Failed to generate identity: {e}")
    else:
        # Extract top lessons for context injection even if identity exists
        if os.path.exists(learnings_path):
            with open(learnings_path, 'r', encoding='utf-8') as f:
                learnings_content = f.read()
            lesson_lines = [l.strip() for l in learnings_content.split('\n') 
                            if l.strip().startswith('- ') and len(l.strip()) > 10]
            top_lessons = [l[2:] for l in lesson_lines[:5]]
            
            # --- IDENTITY WRITE-BACK LOGIC ---
            if top_lessons and os.path.exists(identity_path):
                try:
                    with open(identity_path, 'r', encoding='utf-8') as f:
                        identity_content = f.read()
                        
                    import re
                    lessons_str = '\n'.join(f"{i+1}. {l}" for i, l in enumerate(top_lessons))
                    
                    new_content = re.sub(
                        r'(## Active Lessons \(Top 5\)).*?(?=## |$)', 
                        f'\\1\n\n{lessons_str}\n\n', 
                        identity_content, flags=re.DOTALL)
                        
                    if new_content != identity_content:
                        with open(identity_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print("[IDENTITY] Synced top lessons to AGENT_IDENTITY.md")
                except Exception as e:
                    print(f"[IDENTITY] Failed to write-back lessons: {e}")

    # --- IDE-6: Formal State Machine (Recovery Hook) ---
    fsm_state_path = os.path.join(CONTEXT_DIR, 'execution_state.json')
    recovery_instruction = ""
    if os.path.exists(fsm_state_path):
        try:
            with open(fsm_state_path, 'r', encoding='utf-8') as f:
                fsm_state = json.load(f)
            
            phase = fsm_state.get("phase", "IDLE")
            if phase not in ("IDLE", "DONE"):
                active_tasks = fsm_state.get("active_tasks", {})
                tasks_info = ", ".join([f"{k} ({v.get('status')})" for k, v in active_tasks.items()])
                recovery_instruction = (
                    f"CRITICAL RECOVERY STATE: You were interrupted during phase '{phase}'. "
                    f"Active tasks pending: {tasks_info if tasks_info else 'None'}. "
                    "Resume your exact task immediately and do NOT restart from scratch."
                )
        except Exception as e:
            print(f"[FSM] Failed to parse execution state: {e}")

    # --- IDE-7: Architectural Code Drift (Active Dependency Alerts) ---
    drift_warnings = []
    if args.active_file:
        active_base = os.path.basename(args.active_file)
        if active_base and active_base != "unknown":
            try:
                import sqlite3
                db_path = os.path.join(BASE_DIR, '.orion', 'orion.db')
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute("SELECT source_id, relation FROM edges WHERE target_id LIKE ? LIMIT 5", (f"%{active_base}%",))
                    rows = c.fetchall()
                    for source_id, relation in rows:
                        source_base = os.path.basename(source_id)
                        if source_base != active_base:
                            drift_warnings.append(f"CRITICAL DRIFT RISK: `{source_base}` {relation} this active file. If you modify `{active_base}`, you MUST verify if `{source_base}` needs updating!")
                    conn.close()
            except Exception as e:
                print(f"[DRIFT] Failed to query graph: {e}")
            
    context_payload = {
        "timestamp_ms": int(time.time() * 1000),
        "active_file": args.active_file,
        "terminal_error": args.terminal_error,
        "user_intent": args.user_intent,
        "ide_source": args.ide_source,
        "evolution_overdue": evolution_overdue,
        "unprocessed_learnings": unprocessed_learnings,
        "identity_path": identity_path if identity_exists else None,
        "top_lessons": top_lessons,
        "drift_warnings": drift_warnings
    }
    
    if recovery_instruction:
        context_payload["recovery_instruction"] = recovery_instruction
        
    temp_file = CONTEXT_FILE + ".tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(context_payload, f, indent=2)
    os.replace(temp_file, CONTEXT_FILE)
        
    print(f"[OK] Omni-Buffer updated at {CONTEXT_FILE}")

if __name__ == "__main__":
    main()
