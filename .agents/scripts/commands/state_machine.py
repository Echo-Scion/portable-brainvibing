#!/usr/bin/env python
"""
state_machine.py — Formal State Machine (FSM) Engine
Provides a crash-proof runtime execution tracker for AI agents.
"""
import os
import sys
import json
from datetime import datetime

# Force utf-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
STATE_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'execution_state.json')

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None

def save_state(state_data):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_data, f, indent=2)

def cmd_init(session_id="default"):
    state = {
        "session_id": session_id,
        "phase": "IDLE",
        "active_tasks": {},
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    save_state(state)
    print(f"[FSM] Initialized new execution state (Session: {session_id})")

def cmd_transition(new_phase):
    state = load_state()
    if not state:
        print("[FSM] Error: No active state found. Run 'init' first.")
        sys.exit(1)
        
    old_phase = state.get("phase", "UNKNOWN")
    state["phase"] = new_phase.upper()
    state["last_updated"] = datetime.now().isoformat()
    
    if new_phase.upper() == "DONE":
        # Clear out tasks if done
        state["active_tasks"] = {}
        print(f"[FSM] Session completed. State cleared. ({old_phase} -> DONE)")
    else:
        print(f"[FSM] Phase transition: {old_phase} -> {state['phase']}")
        
    save_state(state)

def cmd_task_start(task_id):
    state = load_state()
    if not state:
        print("[FSM] Error: No active state found.")
        sys.exit(1)
        
    if task_id in state["active_tasks"]:
        # Increment retry if it already exists
        state["active_tasks"][task_id]["retry_count"] += 1
        state["active_tasks"][task_id]["status"] = "running"
        print(f"[FSM] Resuming task '{task_id}' (Retry: {state['active_tasks'][task_id]['retry_count']})")
    else:
        state["active_tasks"][task_id] = {
            "status": "running",
            "retry_count": 0,
            "started_at": datetime.now().isoformat()
        }
        print(f"[FSM] Started task '{task_id}'")
        
    state["last_updated"] = datetime.now().isoformat()
    save_state(state)

def cmd_task_end(task_id, status):
    state = load_state()
    if not state:
        print("[FSM] Error: No active state found.")
        sys.exit(1)
        
    if task_id not in state.get("active_tasks", {}):
        print(f"[FSM] Warning: Task '{task_id}' not found in active tasks.")
        sys.exit(1)
        
    if status.lower() == "success":
        del state["active_tasks"][task_id]
        print(f"[FSM] Task '{task_id}' marked as SUCCESS and removed.")
    else:
        state["active_tasks"][task_id]["status"] = status
        print(f"[FSM] Task '{task_id}' marked as {status.upper()}.")
        
    state["last_updated"] = datetime.now().isoformat()
    save_state(state)

def cmd_status():
    state = load_state()
    if not state:
        print("No active execution state.")
    else:
        print(json.dumps(state, indent=2))

def main():
    if len(sys.argv) < 2:
        print("Usage: state_machine.py [init|transition|task_start|task_end|status]")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    
    if action == "init":
        session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
        cmd_init(session_id)
    elif action == "transition":
        if len(sys.argv) < 3:
            print("Usage: state_machine.py transition <PHASE>")
            sys.exit(1)
        cmd_transition(sys.argv[2])
    elif action == "task_start":
        if len(sys.argv) < 3:
            print("Usage: state_machine.py task_start <task_id>")
            sys.exit(1)
        cmd_task_start(sys.argv[2])
    elif action == "task_end":
        if len(sys.argv) < 4:
            print("Usage: state_machine.py task_end <task_id> <status>")
            sys.exit(1)
        cmd_task_end(sys.argv[2], sys.argv[3])
    elif action == "status":
        cmd_status()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()
