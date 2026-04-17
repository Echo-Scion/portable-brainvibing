import os
import json
import re
import sys
import subprocess

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

def load_valid_skills():
    skills_dir = os.path.join(BASE_DIR, 'skills')
    if not os.path.exists(skills_dir):
        return set()
    return {d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))}

def get_all_valid_files():
    valid_files = set()
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            valid_files.add(file)
            # Add relative paths as well
            rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR).replace('\\', '/')
            valid_files.add(rel_path)
    return valid_files

def run_preflight():
    print("🚀 Initiating Pre-Flight Diagnostic (Self-Healing Routing)...")

    # 0. Context naming gate (82-file registry + master anchors)
    context_lint_script = os.path.join(SCRIPT_DIR, "context_naming_lint.py")
    if os.path.exists(context_lint_script):
        lint_result = subprocess.run([sys.executable, context_lint_script], capture_output=True, text=True)
        print(lint_result.stdout.strip())
        if lint_result.returncode != 0:
            if lint_result.stderr:
                print(lint_result.stderr.strip())
            print("\n❌ Pre-Flight Failed: context naming lint did not pass.")
            sys.exit(1)
    
    valid_skills = load_valid_skills()
    valid_filenames = get_all_valid_files()
    
    scan_dirs = ["skills", "rules", "workflows", "canons", "templates"]
    files_to_scan = []
    
    if os.path.exists(os.path.join(BASE_DIR, "GEMINI.md")):
        files_to_scan.append(os.path.join(BASE_DIR, "GEMINI.md"))
        

    for d in scan_dirs:
        folder = os.path.join(BASE_DIR, d)
        if not os.path.exists(folder): continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".md"):
                    files_to_scan.append(os.path.join(root, file))

    errors = 0
    warnings = 0
    
    # Exceptions that are not broken links or exist at project root
    ignore_list = [
        "README.md", "LICENSE.md", "CONTRIBUTING.md", "example.md", "template.md",
        "BLUEPRINT.md", "MEMORY.md", "ROADMAP.md", "STYLE_GUIDE.md", "CHANGELOG.md", 
        "ARCHITECTURE.md", "TASK.md", "task-id.md", "model_tier_protocol.md", 
        "reasoning_protocols.md", "SESSION_HANDOFF.md", "PLAN.md", "WALKTHROUGH.md"
    ]
    
    for file_path in files_to_scan:
        rel_src_path = os.path.relpath(file_path, BASE_DIR)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 1. Check Skill Routing
        if rel_src_path == "GEMINI.md" or "rules" in rel_src_path:
            potential_skills = re.findall(r'`([a-z0-9]+-[a-z0-9-]+)`', content)
            for ps in set(potential_skills):
                # Ignore common hyphenated terms that aren't skills
                ignore_terms = ["fail-fast", "anti-goals", "no-sweetwords", "high-fidelity", "pre-flight", "session-handoff", "zero-trust", "multi-agent", "front-end", "back-end", "try-catch"]
                if ps not in valid_skills and ps not in ignore_terms and len(ps) > 5:
                    print(f"⚠️  [WARNING] Possible broken skill reference '{ps}' in {rel_src_path}")
                    warnings += 1

        # 2. Check explicit markdown references only
        # Avoid false positives from plain text tokens like "Problem_Discovery.md" in registries/examples.
        md_links = re.findall(r'\]\(([^)]+\.md)\)', content)
        code_path_refs = re.findall(r'`([^`\n]*/[^`\n]*\.md)`', content)
        raw_refs = set(md_links + code_path_refs)
        
        for ref in raw_refs:
            ref_norm = ref.replace('\\', '/').strip()

            # Skip URLs and placeholders/examples
            if ref_norm.startswith(("http://", "https://", "file://")):
                continue
            if any(token in ref_norm for token in ["{", "}", "<", ">", "[", "]"]):
                continue

            # Enforce only local .agents references; examples to context/ are informative, not mandatory.
            if ref_norm.startswith('.agents/'):
                candidate = ref_norm.split('.agents/', 1)[1]
            elif ref_norm.startswith(("rules/", "skills/", "workflows/", "canons/", "templates/", "scripts/")):
                candidate = ref_norm
            else:
                continue

            base_name = os.path.basename(candidate)
            if base_name in ignore_list:
                continue
            if candidate not in valid_filenames and base_name not in valid_filenames:
                print(f"❌ [ERROR] Broken file reference '{ref_norm}' in {rel_src_path}")
                errors += 1

    if errors > 0:
        print(f"\n❌ Pre-Flight Failed: {errors} broken references, {warnings} warnings.")
        print("ACTION REQUIRED: Fix routing architecture before proceeding.")
        sys.exit(1)
    else:
        print(f"\n✅ Pre-Flight Passed: Routing architecture is structurally sound ({warnings} warnings).")
        sys.exit(0)

if __name__ == "__main__":
    import io
    # Ensure stdout/stderr handle UTF-8 on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    run_preflight()
fer, encoding='utf-8')
    run_preflight()
