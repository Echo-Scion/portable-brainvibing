#!/usr/bin/env python
import os
import re
import sys

def get_markdown_files(base_dir):
    md_files = {}
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.md'):
                basename = f[:-3]  # remove .md
                # exclude very short generic names
                if len(basename) > 4:
                    md_files[basename] = os.path.join(root, f)
    return md_files

def linkify_text(text, md_files, current_file_path):
    sorted_names = sorted(md_files.keys(), key=len, reverse=True)
    
    # Pre-process: identify protected regions
    protected = []
    for m in re.finditer(r'```.*?```', text, re.DOTALL):
        protected.append((m.start(), m.end()))
    for m in re.finditer(r'`[^`\n]+`', text):
        protected.append((m.start(), m.end()))
    for m in re.finditer(r'\[([^\]]+)\]\([^)]+\)', text):
        protected.append((m.start(), m.end()))
    for m in re.finditer(r'\[\[(.*?)\]\]', text):
        protected.append((m.start(), m.end()))
        
    def is_protected(pos):
        return any(s <= pos < e for s, e in protected)
        
    # Find all replacements across all names first in the original text
    replacements = []
    for name in sorted_names:
        target_full_path = md_files[name]
        if os.path.abspath(target_full_path) == os.path.abspath(current_file_path):
            continue
            
        pattern = r'(?<!\[)(?<!\[\[)(?<!`)(?<!\w)(' + re.escape(name) + r')(?:\.md)?(?!\w)(?!\]\])(?!\])(?!`)'
        for m in re.finditer(pattern, text):
            if not is_protected(m.start()):
                replacements.append((m.start(), m.end(), m.group(1)))
                
    # We must sort replacements by start index (descending) so we don't mess up offsets
    # and filter overlapping replacements (e.g. if 'auth' and 'auth_service' both match)
    replacements.sort(key=lambda x: x[0], reverse=True)
    
    filtered_replacements = []
    last_start = float('inf')
    for r in replacements:
        start, end, matched_text = r
        if end <= last_start:
            filtered_replacements.append(r)
            last_start = start
            
    new_text = text
    for start, end, matched_text in filtered_replacements:
        new_text = new_text[:start] + f"[[{matched_text}]]" + new_text[end:]
        
    return new_text

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
    project_root = os.path.abspath(os.path.join(agents_dir, ".."))
    
    target_dirs = [
        os.path.join(agents_dir, "rules"),
        os.path.join(agents_dir, "skills"),
        os.path.join(agents_dir, "workflows"),
        os.path.join(project_root, "context")
    ]
    
    all_md_files = {}
    for d in target_dirs:
        if os.path.exists(d):
            all_md_files.update(get_markdown_files(d))
            
    if not all_md_files:
        print("[INFO] No markdown files found to linkify.")
        return

    modified_count = 0
    for d in target_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.md'):
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='utf-16') as file:
                                content = file.read()
                        except Exception as e:
                            print(f"[ERROR] Could not read {file_path}: {e}")
                            continue
                            
                    new_content = linkify_text(content, all_md_files, file_path)
                    
                    if new_content != content:
                        try:
                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write(new_content)
                            modified_count += 1
                            print(f"[LINKIFY] Updated: {os.path.relpath(file_path, project_root)}")
                        except Exception as e:
                            print(f"[ERROR] Could not write {file_path}: {e}")
                        
    print(f"\n[SUCCESS] Linkify complete. Modified {modified_count} files.")

if __name__ == "__main__":
    main()
