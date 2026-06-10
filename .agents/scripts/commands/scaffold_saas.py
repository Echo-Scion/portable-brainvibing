import os
import re
import argparse

def get_ast_block(filepath, tag_name):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(f"<{tag_name}>(.*?)</{tag_name}>", content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

def scaffold_saas():
    print("NEURO-LINK ENGAGED: Compiling SaaS 82-file Registry")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(script_dir)
    workspace_dir = os.path.dirname(agents_dir)
    context_dir = os.path.join(workspace_dir, "context")
    registry_file = os.path.join(agents_dir, "templates", "PROJECT_SCAFFOLD.template.md")
    
    if not os.path.exists(registry_file):
        print(f"[FAIL] Registry file not found: {registry_file}")
        return

    ast_block = get_ast_block(registry_file, "saas-registry-matrix")
    if not ast_block:
        print("[FAIL] <saas-registry-matrix> AST block not found in PROJECT_SCAFFOLD.template.md")
        return

    current_pillar = None
    files_created = 0
    
    os.makedirs(context_dir, exist_ok=True)
    
    for line in ast_block.split("\n"):
        line = line.strip()
        pillar_match = re.search(r"##\s+\d+\.\s+Pillar:\s+`([^`]+)`", line)
        if pillar_match:
            current_pillar = pillar_match.group(1).replace("/", "")
            pillar_path = os.path.join(context_dir, current_pillar)
            os.makedirs(pillar_path, exist_ok=True)
            continue
            
        if line.startswith("|") and "Category" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4 and current_pillar:
                category_raw = parts[1] 
                prefix_raw = parts[2]   
                files_raw = parts[3]    
                
                category = category_raw.replace("*", "")
                prefix = prefix_raw.replace("`", "")
                files_list = [f.strip().replace("`", "") for f in files_raw.split(",")]
                
                for f in files_list:
                    if not f.endswith(".md"):
                        continue
                        
                    filename = f
                    if not filename.startswith(prefix) and prefix != "":
                        filename = f"{prefix}{filename}"
                        
                    file_path = os.path.join(context_dir, current_pillar, filename)
                    
                    if not os.path.exists(file_path):
                        title = filename.replace(".md", "").replace("_", " ")
                        content = f"---\nsaas_pillar: \"{current_pillar}\"\nsaas_category: \"{category}\"\nwiki_refs: []\n---\n# {title}\n\n<!-- AI: Fill this file with the relevant context for this domain. Use caveman mode if budget tier. -->\n"
                        with open(file_path, "w", encoding="utf-8") as out:
                            out.write(content)
                        files_created += 1

    print(f"Generated {files_created} granular SaaS context files across 4 Pillars.")
    print("SaaS Scaffolding Complete. AI can now freely write to these files without guessing names.")

def main():
    parser = argparse.ArgumentParser(description="Generate 82 SaaS Context Registry Files")
    parser.parse_args()
    scaffold_saas()

if __name__ == "__main__":
    main()
