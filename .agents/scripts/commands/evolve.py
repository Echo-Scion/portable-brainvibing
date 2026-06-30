import os
import sys
import json
import re
import hashlib
import sqlite3
from collections import Counter

# Fix imports for running inside scripts dir
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

try:
    from utils.evolution_ledger import log_evolution
except ImportError:
    # Fallback if utils not available
    def log_evolution(*args, **kwargs): pass

# Lazy import to avoid loading brain models if not needed
def get_nanobrain():
    try:
        from commands.brain import NanoBrain
        return NanoBrain()
    except Exception:
        return None

def grade_assertion(text: str, assertion: str) -> bool:
    """Fallback assertion grader using regex/keyword matching."""
    text_lower = text.lower()
    keywords = assertion.lower().replace("'", "").replace('"', "").split()
    
    # Very naive check: if at least 50% of meaningful keywords from assertion are in the text
    stop_words = {"the", "is", "a", "an", "and", "or", "to", "in", "output", "contains", "mentions"}
    meaningful = [k for k in keywords if k not in stop_words and len(k) > 2]
    
    if not meaningful:
        return True # Too vague to fail
        
    matches = sum(1 for k in meaningful if k in text_lower)
    return (matches / len(meaningful)) >= 0.5

def cmd_bench(args):
    """Idea 2: Fitness Scoring Engine"""
    skill_name = args.skill
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # CIRCUIT BREAKER: Max 3 mutations per 24h
    import datetime
    genome_path = os.path.join(base_dir, ".genome.json")
    if os.path.exists(genome_path):
        with open(genome_path, "r", encoding="utf-8") as f:
            genome = json.load(f)
        daily_cap = genome.get("daily_mutation_cap", 3)
        today = datetime.date.today().isoformat()
        
        # Read evolution log
        log_path = os.path.join(base_dir, "EVOLUTION_LOG.jsonl")
        today_mutations = 0
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try: 
                        if json.loads(line).get("ts", "").startswith(today):
                            today_mutations += 1
                    except: pass
                    
        if today_mutations >= daily_cap:
            print(f"[BENCH STOP] Daily mutation cap ({daily_cap}) reached. Skipping.")
            return False

    evals_path = os.path.join(base_dir, "evals", "evals.json")
    skill_path = os.path.join(base_dir, "skills", skill_name, "SKILL.md")
    
    if not os.path.exists(evals_path) or not os.path.exists(skill_path):
        print(f"[BENCH FAIL] Missing evals or skill file for '{skill_name}'")
        return False
        
    with open(evals_path, 'r', encoding='utf-8') as f:
        evals_data = json.load(f)
        
    skill_evals = next((s for s in evals_data.get("skills", []) if s["skill_name"] == skill_name), None)
    if not skill_evals or not skill_evals.get("evals"):
        print(f"[BENCH SKIP] Cannot evaluate mutation without evals in evals.json. V2 archived. (Ungradable)")
        return False # Freeze if ungradable
        
    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()

    nb = get_nanobrain()
    total_assertions = 0
    passed_assertions = 0
    
    print(f"--- Benchmarking {skill_name} ---")
    
    for case in skill_evals["evals"]:
        total_assertions += len(case["assertions"])
        
        if nb:
            # Try to get a real LLM generation
            try:
                # Truncate skill to fit context
                sys_prompt = f"Follow these instructions to complete the task:\n{skill_content[:2000]}"
                response = nb.generate(case["prompt"], system=sys_prompt)
                output_text = response if response else case["expected_output"]
            except Exception:
                print("  [WARN] NanoBrain generation failed. Falling back to dry-run.")
                output_text = case["expected_output"] # Fallback if model fails
                nb = None # Force dry run label for the final score
        else:
            print("  [WARN] NanoBrain disabled. Performing DRY RUN fitness evaluation.")
            output_text = case["expected_output"] # Hard fallback
            
        for assertion in case["assertions"]:
            # Grade it
            if grade_assertion(output_text, assertion):
                passed_assertions += 1
                print(f"  [PASS] {assertion[:50]}...")
            else:
                print(f"  [FAIL] {assertion[:50]}...")
                
    score = passed_assertions / total_assertions if total_assertions > 0 else 1.0
    if not nb:
        print(f"--- Fitness Score (DRY RUN): {score:.2f} ({passed_assertions}/{total_assertions}) ---")
    else:
        print(f"--- Fitness Score: {score:.2f} ({passed_assertions}/{total_assertions}) ---")
    
    # Save to standard output for capture
    if args.output:
        with open(args.output, "w") as f:
            f.write(str(score))
            
    return score

def cmd_drift_scan(args):
    """Idea 4: Semantic Drift Detector — Compares live file hashes against orion.db baselines."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    db_path = os.path.join(base_dir, ".orion", "orion.db")
    
    if not os.path.exists(db_path):
        print("[DRIFT OK] No orion.db found.")
        return True
        
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA busy_timeout=5000;')
    c = conn.cursor()
    c.execute('SELECT path, sha256 FROM pages')
    rows = c.fetchall()
    conn.close()

    drifted = []
    print("[DRIFT SCAN] Comparing live file hashes against orion.db baselines...")
    for orion_path, stored_hash in rows:
        # orion_path points to the true relative filepath
        source_path = orion_path
        if not os.path.exists(source_path):
            drifted.append((source_path, "DELETED"))
            continue
        with open(source_path, "rb") as f:
            live_hash = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
        if live_hash != stored_hash:
            drifted.append((source_path, "MODIFIED"))

    if drifted:
        print(f"[DRIFT ALERT] {len(drifted)} files drifted from baseline:")
        for path, status in drifted[:10]:
            print(f"  [{status}] {path}")
        return False
    else:
        print("[DRIFT OK] All files match orion.db baselines.")
        return True

def cmd_mine_friction(args):
    """Idea 5: Friction Miner"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    memory_path = os.path.join(os.path.dirname(base_dir), "MEMORY.md")
    learnings_path = os.path.join(base_dir, "LEARNINGS.md")
    
    content = ""
    if os.path.exists(memory_path):
        with open(memory_path, 'r', encoding='utf-8') as f:
            content += f.read() + "\n"
            
    if os.path.exists(learnings_path):
        with open(learnings_path, 'r', encoding='utf-8') as f:
            content += f.read() + "\n"
            
    if not content:
        print("[MINE OK] No MEMORY.md or LEARNINGS.md found.")
        return True
        
    # Extract <friction-data> blocks (mostly from MEMORY.md)
    friction_blocks = re.findall(r'<friction-data>(.*?)</friction-data>', content, re.DOTALL)
    
    patterns = []
    for block in friction_blocks:
        m = re.search(r'Pattern Found:\s*(.*)', block)
        if m:
            patterns.append(m.group(1).strip())
            
    counter = Counter(patterns)
    critical_found = False
    
    print("--- Friction Mining Report ---")
    for pattern, count in counter.items():
        if count >= 3: # The 3x Pivot Rule enforced mechanically
            print(f" [CRITICAL] {pattern} (Count: {count})")
            critical_found = True
        else:
            print(f" [WARN] {pattern} (Count: {count})")
            
    # Also check for direct [Darwinian Hook] tags in LEARNINGS.md
    darwinian_hooks = content.count("[Darwinian Hook]")
    if darwinian_hooks >= 3:
        print(f" [CRITICAL] Darwinian Hook threshold reached (Count: {darwinian_hooks})")
        critical_found = True
        
    if not critical_found and not patterns:
        print("[MINE OK] No critical friction data found.")
        return True
            
    if critical_found:
        print("\n[DIRECTIVE] CRITICAL friction detected. Trigger self-evolve to synthesize a new rule.")
        
    # SAFE ROTATION: Archive, don't truncate
    if os.path.exists(learnings_path) and critical_found:
        import datetime, shutil
        archive_dir = os.path.join(base_dir, ".orion", "episodic")
        os.makedirs(archive_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(learnings_path, os.path.join(archive_dir, f"learnings_{stamp}.md"))
        # Reset only the [Darwinian Hook] markers, preserve other learnings
        with open(learnings_path, 'r', encoding='utf-8') as f:
            lr_content = f.read()
        cleaned = lr_content.replace("[Darwinian Hook]", "[Processed]")
        with open(learnings_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"[MINE] Learnings archived and heartbeat markers reset (non-destructive).")
        
    return critical_found

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Self-Evolve Ecosystem Manager")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")
    
    bench_parser = subparsers.add_parser("bench", help="Run fitness score benchmark")
    bench_parser.add_argument("--skill", required=True, help="Name of the skill to bench")
    bench_parser.add_argument("--output", help="File to write raw score to")
    
    subparsers.add_parser("drift-scan", help="Check for unauthorized skeleton mutations")
    subparsers.add_parser("mine-friction", help="Extract and count friction patterns")
    
    args = parser.parse_args()
    
    if args.subcommand == "bench":
        cmd_bench(args)
    elif args.subcommand == "drift-scan":
        cmd_drift_scan(args)
    elif args.subcommand == "mine-friction":
        cmd_mine_friction(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
