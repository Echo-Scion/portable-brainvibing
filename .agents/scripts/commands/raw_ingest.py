#!/usr/bin/env python
import os
import sys
import datetime
import re
from collections import Counter

def extract_keywords(text):
    """Fallback simple keyword extraction without heavy LLMs."""
    # Find words with 5 or more letters
    words = re.findall(r'\b[A-Za-z]{5,}\b', text.lower())
    # Exclude common stop words (simplified list)
    stopwords = {"these", "those", "their", "there", "which", "would", "could", "should", "about", "other"}
    filtered = [w for w in words if w not in stopwords]
    common = Counter(filtered).most_common(5)
    return [w[0] for w in common]

def process_raw_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(os.path.dirname(script_dir))
    project_root = os.path.dirname(agents_dir)
    
    raw_dir = os.path.join(project_root, "context", "raw")
    wiki_dir = os.path.join(project_root, "context", "wiki")
    
    if not os.path.exists(raw_dir):
        print(f"[INFO] No context/raw/ directory found at {raw_dir}")
        return
        
    os.makedirs(wiki_dir, exist_ok=True)
    
    files = [f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]
    if not files:
        print("[INFO] No raw files to ingest.")
        return
        
    processed_count = 0
    for f in files:
        if f.startswith('.'):
            continue
            
        raw_path = os.path.join(raw_dir, f)
        base_name = os.path.splitext(f)[0]
        
        # Clean up filename for wiki standard
        safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', base_name).strip('_')
        if not safe_name:
            safe_name = f"ingest_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        wiki_path = os.path.join(wiki_dir, f"{safe_name}.md")
        
        try:
            with open(raw_path, 'r', encoding='utf-8', errors='replace') as infile:
                content = infile.read()
        except Exception as e:
            print(f"[ERROR] Could not read {f}: {e}")
            continue
            
        keywords = extract_keywords(content)
        tags_str = ", ".join([f'"{k}"' for k in keywords]) if keywords else ""
        inline_tags = " ".join([f"#{k}" for k in keywords])
        
        # Structure the markdown
        structured = f"""---
title: {safe_name.replace('_', ' ').title()}
ingested_at: {datetime.datetime.now().isoformat()}
source: context/raw/{f}
tags: [{tags_str}]
---

# {safe_name.replace('_', ' ').title()}

> **Auto-Ingested Document**
> Extracted Tags: {inline_tags}

## Raw Content
{content}
"""
        try:
            with open(wiki_path, 'w', encoding='utf-8') as outfile:
                outfile.write(structured)
            os.remove(raw_path)
            processed_count += 1
            print(f"[SUCCESS] Ingested '{f}' -> 'context/wiki/{safe_name}.md'")
        except Exception as e:
            print(f"[ERROR] Could not write or remove {f}: {e}")
            
    print(f"\n[DONE] Processed {processed_count} raw files.")

if __name__ == "__main__":
    process_raw_files()
