import os
import subprocess
import sys

def check_heartbeat(learnings_path, base_agents_dir):
    evolution_overdue = False
    unprocessed_learnings = 0
    if os.path.exists(learnings_path):
        with open(learnings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            unprocessed_learnings = content.count("[Darwinian Hook]")
            if unprocessed_learnings == 0:
                entries = [line for line in content.split('\n') if line.startswith('## 20') and '[Processed]' not in line]
                unprocessed_learnings = len(entries)
    
    if unprocessed_learnings >= 3:
        evolution_overdue = True
        try:
            orion_script = os.path.join(base_agents_dir, 'scripts', 'orion.py')
            subprocess.Popen([sys.executable, orion_script, 'evolve', 'mine-friction'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            print("[AUTO-EVOLVE] Triggered background evolution via orion.py", file=sys.stderr)
        except Exception as e:
            print(f"[AUTO-EVOLVE] Failed to start background evolution: {e}", file=sys.stderr)
            
    return evolution_overdue, unprocessed_learnings

