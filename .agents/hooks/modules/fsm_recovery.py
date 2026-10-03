import os
import json

def check_fsm(fsm_state_path):
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
            
    return recovery_instruction
