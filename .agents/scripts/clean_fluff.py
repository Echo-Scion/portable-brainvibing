import os
import re

def clean_skill_fluff(directory):
    count = 0
    pattern1 = r'##.*?Ecosystem Paradigm Shift\s*> \*\*Core Directive\*\*.*?\n\n'
    pattern2 = r'##.*?Next-Gen Capabilities\s*> \*\*.*?\n\n'
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "SKILL.md":
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = re.sub(pattern1, '', content, flags=re.MULTILINE | re.DOTALL)
                new_content = re.sub(pattern2, '', new_content, flags=re.MULTILINE | re.DOTALL)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Cleaned fluff from: {filepath}")
                    count += 1
    print(f"Total files cleaned: {count}")

if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'skills'))
    clean_skill_fluff(base_dir)
