import sys
import os
import json

def get_workspace_dir():
    # If we are in .agents/scripts/commands, go up to workspace root
    current = os.path.dirname(os.path.abspath(__file__))
    # up to scripts
    parent = os.path.dirname(current)
    # up to .agents
    grandparent = os.path.dirname(parent)
    # up to workspace
    workspace = os.path.dirname(grandparent)
    return workspace

def query_matrix(keywords):
    workspace = get_workspace_dir()
    matrix_dir = os.path.join(workspace, ".orion", "matrix")
    
    if not os.path.exists(matrix_dir):
        print(f"Matrix directory not found at {matrix_dir}.")
        return
        
    results = {}
    for filename in os.listdir(matrix_dir):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(matrix_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            file_results = {}
            for key, rules in data.items():
                if key == "global": continue
                
                # Check if keyword in key or any rule
                match = False
                for kw in keywords:
                    kw_lower = kw.lower()
                    if kw_lower in key.lower():
                        match = True
                        break
                    
                    if isinstance(rules, list):
                        for rule in rules:
                            if kw_lower in rule.lower():
                                match = True
                                break
                    elif isinstance(rules, str):
                        if kw_lower in rules.lower():
                            match = True
                    if match:
                        break
                            
                if match:
                    file_results[key] = rules
                    
            if file_results:
                results[filename] = file_results
        except Exception as e:
            print(f"Error parsing {filename}: {e}", file=sys.stderr)
            
    if results:
        print(json.dumps(results, indent=2))
    else:
        print("{}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_matrix(sys.argv[1:])
    else:
        print("Usage: python matrix_query.py <keyword1> <keyword2> ...")
