#!/usr/bin/env python
"""
compile_rules.py
----------------
Converts human-readable Markdown rules into dense YAML matrices.
Used to dramatically reduce token cost when feeding rules to LLM agents.
"""

import os
import re
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
RULES_DIR = os.path.join(BASE_DIR, 'rules')
MATRIX_DIR = os.path.abspath(os.path.join(WORKSPACE_DIR, '.orion', 'matrix'))

def parse_markdown_to_dict(md_content):
    """
    Very basic heuristic parser: 
    Converts Markdown headings to dict keys, bullets to lists.
    """
    matrix = {}
    current_section = "global"
    matrix[current_section] = []
    
    for line in md_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Match headings ## 1. Section
        header_match = re.match(r'^#+\s+(.+)$', line)
        if header_match:
            current_section = header_match.group(1).strip()
            matrix[current_section] = []
            continue
            
        # Match bullets
        if line.startswith('- ') or line.startswith('* '):
            matrix[current_section].append(line[2:].strip())
        elif line.startswith('> '):
            matrix[current_section].append("CONSTRAINT: " + line[2:].strip())
        else:
            # Append to last item if exists, else append as new
            if matrix[current_section]:
                matrix[current_section][-1] += " " + line
            else:
                matrix[current_section].append(line)
                
    # Remove empty sections
    return {k: v for k, v in matrix.items() if v}

def compile_all():
    if not os.path.exists(MATRIX_DIR):
        os.makedirs(MATRIX_DIR)
        
    rule_files = glob.glob(os.path.join(RULES_DIR, '*.md'))
    count = 0
    
    for rule_file in rule_files:
        filename = os.path.basename(rule_file)
        if filename.startswith('_'):
            continue
            
        with open(rule_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        yaml_dict = parse_markdown_to_dict(content)
        
        out_name = filename.replace('.md', '.json')
        out_path = os.path.join(MATRIX_DIR, out_name)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(yaml_dict, f, indent=2)
            
        count += 1
        
    print(f"[OK] Compiled {count} Markdown rules into JSON Matrices at {MATRIX_DIR}")

if __name__ == "__main__":
    compile_all()
