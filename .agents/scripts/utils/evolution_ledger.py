import json
import os
import datetime
from pathlib import Path

def log_evolution(target_file: str, mutation_type: str, trigger: str, fitness_before: float = None, fitness_after: float = None):
    """
    Appends a mutation event to the Evolution Genome Ledger.
    mutation_type: e.g., 'skill_evolve', 'rule_prune'
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ledger_path = os.path.join(base_dir, "EVOLUTION_LOG.jsonl")
    genome_path = os.path.join(base_dir, ".genome.json")
    
    entry = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "type": mutation_type,
        "target": target_file,
        "trigger": trigger,
        "fitness_before": fitness_before,
        "fitness_after": fitness_after
    }
    
    try:
        # 0. Log Rotation Fail-Safe (Audit 05)
        max_log_size = 1024 * 1024 # 1 MB
        if os.path.exists(ledger_path) and os.path.getsize(ledger_path) > max_log_size:
            backup_path = ledger_path + ".bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(ledger_path, backup_path)

        # 1. Append to Ledger
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        # 2. Update Genome Fingerprint
        if os.path.exists(genome_path):
            with open(genome_path, "r", encoding="utf-8") as f:
                genome = json.load(f)
                
            genome["evolution_count"] = genome.get("evolution_count", 0) + 1
            
            if mutation_type == "skill_evolve" and target_file not in genome.get("evolved_skills", []):
                genome.setdefault("evolved_skills", []).append(target_file)
            elif mutation_type == "rule_evolve" and target_file not in genome.get("evolved_rules", []):
                genome.setdefault("evolved_rules", []).append(target_file)
            elif mutation_type == "prune" and target_file not in genome.get("pruned_assets", []):
                genome.setdefault("pruned_assets", []).append(target_file)
                
            if fitness_after is not None:
                genome.setdefault("fitness_scores", {})[target_file] = fitness_after
                
            with open(genome_path, "w", encoding="utf-8") as f:
                json.dump(genome, f, indent=2)
                
        print(f"[EVOLUTION LEDGER] Logged {mutation_type} for {target_file}")
        return True
    except Exception as e:
        print(f"[EVOLUTION LEDGER ERROR] Failed to log: {e}")
        return False
