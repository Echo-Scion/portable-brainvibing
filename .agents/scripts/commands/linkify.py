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
    new_text = text
    current_dir = os.path.dirname(current_file_path)
    
    for name in sorted_names:
        target_full_path = md_files[name]
        
        # Skip linking to itself
        if os.path.abspath(target_full_path) == os.path.abspath(current_file_path):
            continue
            
        target_full_path_fwd = target_full_path.replace(chr(92), '/')
        
        def replacer(match):
            matched_text = match.group(0)
            return f"[{matched_text}](file:///{target_full_path_fwd})"
            
        # Match standard markdown links so we can overwrite them if they already exist
        # We'll first clean existing links, then apply new ones.
        # Actually, since we might already have [name](...), we should just let the cleaner run first.
        # Wait, the current text might have [ROADMAP.md](../../context/...)
        pattern = r'(?<!\[)(?<!\[\[)(?<!`)\b(' + re.escape(name) + r')(?:\.md)?\b(?!\]\])(?!\])(?!`)'
        new_text = re.sub(pattern, replacer, new_text)
        
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
