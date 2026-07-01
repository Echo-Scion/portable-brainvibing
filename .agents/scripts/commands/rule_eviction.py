#!/usr/bin/env python
"""
rule_eviction.py
----------------
Dynamic Asset Eviction Engine (Amnesia Mechanism).
Usage: python rule_eviction.py

Scans the `.agents/` directories (rules, workflows, canons, skills) for assets
that haven't been accessed or modified recently. Evicts (moves) them to `.orion/archive/` 
preserving relative paths to prevent LLM token bloat, relying on RAG (brain.py) 
to JIT retrieve them if needed.

Now upgraded to use SQLite RAG metrics (access_count, last_accessed) for usage-based 
eviction instead of relying purely on filesystem mtime.
"""

import os
import shutil
import time
import sqlite3
from datetime import datetime

def evict_assets(agents_dir, orion_db_path, archive_dir=".orion/archive", base_days_threshold=30):
    if not os.path.exists(agents_dir):
        print(f"Agents directory not found: {agents_dir}")
        return

    # 1. Load database usage metrics
    usage_data = {}
    if os.path.exists(orion_db_path):
        try:
            conn = sqlite3.connect(orion_db_path)
            c = conn.cursor()
            # path, access_count, last_accessed (datetime string)
            # handle cases where access_count or last_accessed might be missing/null in older DB versions
            c.execute("PRAGMA table_info(pages)")
            columns = [info[1] for info in c.fetchall()]
            
            if 'access_count' in columns and 'last_accessed' in columns:
                c.execute("SELECT path, access_count, last_accessed FROM pages")
                for row in c.fetchall():
                    path, access_count, last_accessed = row
                    
                    if not access_count:
                        access_count = 0
                        
                    if path:
                        # Normalize path for matching
                        norm_path = os.path.abspath(path).replace('\\', '/')
                        usage_data[norm_path] = {
                            'access_count': access_count,
                            'last_accessed': last_accessed
                        }
            conn.close()
            print(f"[DB] Loaded usage metrics for {len(usage_data)} items from orion.db")
        except Exception as e:
            print(f"[DB] Error loading metrics from orion.db: {e}")

    now = time.time()
    evict_count = 0

    target_dirs = ["rules", "workflows", "canons", "skills"]

    print(f"--- SCANNING FOR STALE ASSETS ---")
    
    # Exclude core foundational rules and active skills from eviction
    protected_assets = {
        "core-guardrails.md", 
        "security-guardrails.md", 
        "tier-execution-protocol.md",
        "RULES_INDEX.md",
        "context-standards.md",
        "app-lifecycle.md",
        "AGENTS_INDEX.md",
        "project-migrate.md"
    }

    for t_dir in target_dirs:
        active_dir = os.path.join(agents_dir, t_dir)
        if not os.path.exists(active_dir):
            continue

        for item in os.listdir(active_dir):
            if item in protected_assets:
                continue
                
            # Skip hidden files
            if item.startswith('.'):
                continue

            filepath = os.path.join(active_dir, item)
            norm_filepath = os.path.abspath(filepath).replace('\\', '/')
            
            days_old = 0
            threshold = base_days_threshold
            evict_reason = ""
            
            # 2. Check DB Usage Metrics
            db_record = usage_data.get(norm_filepath)
            if db_record and db_record.get('last_accessed'):
                last_acc_str = db_record['last_accessed']
                try:
                    # SQLite datetime('now') produces 'YYYY-MM-DD HH:MM:SS'
                    last_acc_dt = datetime.strptime(last_acc_str, "%Y-%m-%d %H:%M:%S")
                    days_old = (datetime.now() - last_acc_dt).days
                    
                    # Dynamic Grace Period based on usage
                    if db_record['access_count'] > 3:
                        threshold = 90  # High value asset
                    else:
                        threshold = 30  # Normal asset
                        
                    evict_reason = f"Usage (Acc: {db_record['access_count']}, Last: {days_old}d ago)"
                except Exception as e:
                    # Fallback to mtime if parsing fails
                    mtime = os.path.getmtime(filepath)
                    days_old = (now - mtime) / (60 * 60 * 24)
                    evict_reason = f"Mtime Fallback ({days_old:.1f}d ago)"
            else:
                # 3. Fallback: No DB record (never read by RAG) -> use Mtime
                mtime = os.path.getmtime(filepath)
                days_old = (now - mtime) / (60 * 60 * 24)
                evict_reason = f"Mtime ({days_old:.1f}d ago)"

            if days_old > threshold:
                # Calculate relative destination path
                dest_dir = os.path.join(archive_dir, t_dir)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                dest_path = os.path.join(dest_dir, item)
                
                print(f"[EVICTING] {t_dir}/{item} -> Archiving to {dest_dir}")
                print(f"  └─ Reason: {evict_reason} (Threshold: {threshold}d)")
                
                # Move the item
                try:
                    shutil.move(filepath, dest_path)
                    evict_count += 1
                except Exception as e:
                    print(f"  [ERROR] Could not move {filepath}: {e}")

    print("-" * 40)
    print(f"Eviction Complete: {evict_count} assets archived to prevent token bloat.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_d = os.path.abspath(os.path.join(script_dir, "..", ".."))
    orion_archive_d = os.path.abspath(os.path.join(agents_d, "..", ".orion", "archive"))
    orion_db_p = os.path.abspath(os.path.join(agents_d, "..", ".orion", "orion.db"))
    
    evict_assets(
        agents_dir=agents_d,
        orion_db_path=orion_db_p,
        archive_dir=orion_archive_d,
        base_days_threshold=30
    )
