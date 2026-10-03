import json
import os
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "budget_telemetry.json")

def log_task_execution(task_name, tier, model_used, was_harness_used, aborted_to_premium):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task_name,
        "declared_tier": tier,
        "model": model_used,
        "harness_driven": was_harness_used,
        "auto_aborted": aborted_to_premium
    }
    
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass
            
    data.append(entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"[INFO] Telemetry logged. Task: {task_name} | Tier: {tier} | Aborted: {aborted_to_premium}")

def print_telemetry_report():
    if not os.path.exists(LOG_FILE):
        print("No telemetry data found. Start executing tasks to build Small Model Superiority metrics.")
        return
        
    with open(LOG_FILE, 'r') as f:
        data = json.load(f)
        
    total_tasks = len(data)
    budget_only = sum(1 for d in data if d["declared_tier"] == "BUDGET" and not d["auto_aborted"])
    premium_handoffs = sum(1 for d in data if d["auto_aborted"])
    
    print("==================================================")
    print(" SMALL MODEL SUPERIORITY KPIs (ANTIGRAVITY IDE)")
    print("==================================================")
    print(f"Total Tasks Evaluated : {total_tasks}")
    print(f"Tasks Handled 100% by BUDGET Model: {budget_only} ({budget_only/total_tasks*100:.1f}%)")
    print(f"Tasks Handing off to PREMIUM (Harness Built): {premium_handoffs} ({premium_handoffs/total_tasks*100:.1f}%)")
    print("==================================================")
    print("Goal: Maintain >70% BUDGET resolution for Tier-0 tasks.")

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="Track budget, tiers, and Small Model Superiority KPIs.")
    parser.add_argument("--report", action="store_true", help="View KPI summary report.")
    parser.add_argument("--tier", "-t", type=str, choices=["BUDGET", "STANDARD", "PREMIUM", "budget", "standard", "premium"], help="Declared model tier.")
    parser.add_argument("--task", type=str, default="adhoc_task", help="Name or description of task.")
    parser.add_argument("--model", type=str, default="auto", help="Model name used.")
    parser.add_argument("--harness", action="store_true", help="Was a test harness used.")
    parser.add_argument("--aborted", action="store_true", help="Was task aborted / escalated to premium.")
    
    args = parser.parse_args()
    
    if args.tier:
        log_task_execution(
            task_name=args.task,
            tier=args.tier.upper(),
            model_used=args.model,
            was_harness_used=args.harness,
            aborted_to_premium=args.aborted
        )
    else:
        print_telemetry_report()