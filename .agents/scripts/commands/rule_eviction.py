#!/usr/bin/env python
"""
rule_eviction.py
----------------
Dynamic Rule Eviction Engine (Amnesia Mechanism).
Usage: python rule_eviction.py

Scans the `.agents/rules/` directory for files that haven't been accessed
or modified recently. Evicts (moves) them to `.orion/archive/` to prevent
LLM token bloat, relying on RAG (brain.py) to JIT retrieve them if needed.
"""

import os
import shutil
import time

def evict_rules(rules_dir=".agents/rules", archive_dir=".orion/archive", days_threshold=30):
    if not os.path.exists(rules_dir):
        print(f"Rules directory not found: {rules_dir}")
        return

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    now = time.time()
    evict_count = 0

    print(f"--- SCANNING FOR STALE RULES (> {days_threshold} days) ---")
    
    # Exclude core foundational rules from eviction
    protected_rules = {
        "core-guardrails.md", 
        "security-guardrails.md", 
        "tier-execution-protocol.md",
        "RULES_INDEX.md",
        "context-standards.md"
    }

    for file in os.listdir(rules_dir):
        if file in protected_rules or not file.endswith(".md"):
            continue

        filepath = os.path.join(rules_dir, file)
        
        # Check last modified time
        mtime = os.path.getmtime(filepath)
        days_old = (now - mtime) / (60 * 60 * 24)

        if days_old > days_threshold:
            print(f"[EVICTING] {file} ({days_old:.1f} days old) -> Archiving to {archive_dir}")
            shutil.move(filepath, os.path.join(archive_dir, file))
            evict_count += 1

    print("-" * 40)
    print(f"Eviction Complete: {evict_count} rules archived to prevent token bloat.")

if __name__ == "__main__":
    # In a real environment, you'd calculate "usage" differently, 
    # but modified time acts as a proxy for "last edited/touched".
    evict_rules(
        rules_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "rules"),
        archive_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "..", ".orion", "archive"),
        days_threshold=30
    )
