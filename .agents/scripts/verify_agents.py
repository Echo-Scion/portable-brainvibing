# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import os
import re
import sys
import argparse
import json
from typing import Set, Dict, Any, List, Optional, Iterable, Tuple

# Smart Root Discovery
def discover_roots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # If we are in .agents/scripts, the .agents root is one level up
    if os.path.basename(current_dir) == "scripts" and os.path.basename(os.path.dirname(current_dir)) == ".agents":
        base_dir = os.path.dirname(current_dir)
    else:
        # Check if .agents exists in current dir
        if os.path.exists(".agents"):
            base_dir = os.path.abspath(".agents")
        else:
            base_dir = os.getcwd()
    return base_dir

BASE_DIR = discover_roots()
WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
RULES_DIR = os.path.join(BASE_DIR, "rules")
CANONS_DIR = os.path.join(BASE_DIR, "canons")
FOUNDATION_PATH_MARKER = os.path.join(BASE_DIR, ".foundation_path")

EXCLUDED_PATH_MARKERS = [".git", ".gemini", ".system_generated", "node_modules", "__pycache__"]
DOC_METADATA_KEYS = {"param", "return", "type", "description", "activation", "trigger"}
RULE_DIR_TOKENS = {"rules", "common", "flutter", "web", "canons", "auth", "notifications", "ui-patterns"}
FRONTMATTER_RE = re.compile(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', re.DOTALL)
FRONTMATTER_KEY_RE = re.compile(r'^\s*([A-Za-z0-9_-]+)\s*:\s*(.*?)\s*$', re.MULTILINE)


def iter_files(base_dir: str, extensions: Tuple[str, ...]) -> Iterable[str]:
    for root, _, files in os.walk(base_dir):
        if any(marker in root for marker in EXCLUDED_PATH_MARKERS):
            continue
        for file_name in files:
            if file_name.endswith(extensions):
                yield os.path.join(root, file_name)


def read_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def parse_frontmatter_keys(content: str) -> Dict[str, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    keys: Dict[str, str] = {}
    for key_match in FRONTMATTER_KEY_RE.finditer(match.group(1)):
        key = key_match.group(1).strip().lower()
        value = key_match.group(2).strip()
        keys[key] = value
    return keys


def severity_counts(items: List[Dict[str, Optional[str]]]) -> Dict[str, int]:
    counts: Dict[str, int] = {"BLOCKER": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in items:
        sev = str(item.get("severity") or "LOW").upper()
        if sev not in counts:
            counts[sev] = 0
        counts[sev] += 1
    return counts

class AuditResult:
    def __init__(self):
        self.errors: List[Dict[str, Optional[str]]] = []
        self.warnings: List[Dict[str, Optional[str]]] = []
        self.stats: Dict[str, int] = {"skills": 0, "rules": 0, "canons": 0}

    def add_error(self, category: str, message: str, file: Optional[str] = None, severity: str = "HIGH"):
        self.errors.append({"category": category, "message": message, "file": file, "severity": severity})

    def add_warning(self, category: str, message: str, file: Optional[str] = None, severity: str = "MEDIUM"):
        self.warnings.append({"category": category, "message": message, "file": file, "severity": severity})

def check_foundation_sync(res: AuditResult, verbose: bool = True):
    if not os.path.exists(FOUNDATION_PATH_MARKER):
        if verbose: print("[NOTE] No .foundation_path marker found. Skipping sync check.")
        return
    
    if verbose: print("\n--- FOUNDATION SYNC CHECK ---")
    
    try:
        with open(FOUNDATION_PATH_MARKER, "r", encoding="utf-8") as f:
            foundation_root = f.read().strip()
        foundation_agents = os.path.join(foundation_root, ".agents") if not (foundation_root.endswith(".agents") or os.path.basename(foundation_root) == ".agents") else foundation_root
        
        if not os.path.exists(foundation_agents):
            res.add_error("SYNC", f"Broken foundation link: {foundation_agents}")
            return
            
        if verbose: print(f"📌 Linked to Foundation: {foundation_root}")
        
        sync_folders = ["skills", "rules", "workflows", "canons"]
        for folder in sync_folders:
            local_folder = os.path.join(BASE_DIR, folder)
            found_folder = os.path.join(foundation_agents, folder)
            if not os.path.exists(found_folder): continue
            
            local_files = {f for r, d, files in os.walk(local_folder) for f in files if f.endswith(('.md', '.json', 'SKILL.md'))}
            found_files = {f for r, d, files in os.walk(found_folder) for f in files if f.endswith(('.md', '.json', 'SKILL.md'))}
            
            if local_files != found_files:
                diff_count = len(found_files - local_files)
                if diff_count > 0:
                    res.add_warning("SYNC", f"Folder {folder} is out of sync with foundation. Foundation has {diff_count} new/different items.")
                    if verbose: print(f"[SYNC] OUT-OF-SYNC ({folder}): Foundation has {diff_count} new/different items.")
                
        if verbose and len(res.warnings) > 0:
            print("👉 Run 'python .agents/scripts/deploy_foundation.py' to update your local agents.")
            
    except Exception as e:
        res.add_error("SYNC", f"Sync Check failed: {str(e)}")
        if verbose: print(f"[ERROR] Sync Check failed: {e}")

def check_mechanical_integrity(res: AuditResult, verbose: bool = True):
    if verbose: print("--- SCANNING FOR MECHANICAL INTEGRITY ERRORS ---")
    
    header_bug_pat = re.compile(r'^#+ [^#\n]+#+', re.MULTILINE)
    double_header_pat = re.compile(r'^#+ #+ ', re.MULTILINE)
    abs_path_pat = re.compile(r'[a-zA-Z]:\\[Uu]sers\\[a-zA-Z0-9_\-\.]+')
    
    for filepath in iter_files(BASE_DIR, (".md", ".py")):
        file = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            content = read_text(filepath)
            if file.endswith(".md"):
                if header_bug_pat.search(content):
                    res.add_error("MECHANICAL", "Concatenated headers detected", rel_path)
                if double_header_pat.search(content):
                    res.add_error("MECHANICAL", "Double headers (## ##) detected", rel_path)
            if file.endswith(".py") and abs_path_pat.search(content):
                if file not in ["verify_agents.py", "publish_agents.py", "audit_repo.py"]:
                    res.add_error("MECHANICAL", "Absolute path detected in Python file", rel_path)
        except Exception as e:
            res.add_error("IO", f"Could not read file: {str(e)}", rel_path)

def check_links(res: AuditResult, verbose: bool = True):
    all_skills: Set[str] = set([str(d) for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))]) if os.path.exists(SKILLS_DIR) else set([])
    all_rules: Set[str] = set([])
    all_rule_stems: Set[str] = set([])
    for d in [RULES_DIR, CANONS_DIR]:
        if os.path.exists(d):
            root_prefix = os.path.basename(d)
            for r, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".md"):
                        rel = os.path.relpath(os.path.join(r, f), d).replace("\\", "/")
                        stem = rel[:-3] if rel.endswith(".md") else rel
                        all_rules.add(f)
                        all_rules.add(rel)
                        all_rules.add(f"{root_prefix}/{rel}")
                        all_rule_stems.add(f[:-3])
                        all_rule_stems.add(stem)
                        all_rule_stems.add(f"{root_prefix}/{stem}")
    
    if verbose: print("\n--- SCANNING FOR BROKEN LINKS ---")
    
    if not os.path.exists(BASE_DIR):
        res.add_warning("LINK", "Base directory not found!", severity="LOW")
        return

    # Patterns for rule and skill links
    rule_pattern = re.compile(r'@([a-zA-Z0-9_\-\./\\]+\.md)')
    # Support for @mention without .md extension as long as it exists in rules/canons/skills
    mention_pattern = re.compile(r'(?<![\w/])@([a-zA-Z0-9][a-zA-Z0-9_\-\./\\]*)')

    for filepath in iter_files(BASE_DIR, (".md",)):
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            content = read_text(filepath)

            # Rule and Canon links (@reference.md)
            for r in rule_pattern.findall(content):
                r_clean = r.split('`')[0].strip().replace("\\", "/")
                if r_clean not in all_rules:
                    res.add_error("LINK", f"Broken rule reference: @{r_clean}", rel_path)

            # Mentions (could be rule names without extension or skill references)
            for mention in mention_pattern.findall(content):
                m = mention.strip().replace("\\", "/")
                if not m:
                    continue
                if m.lower() in DOC_METADATA_KEYS:
                    continue
                if m in RULE_DIR_TOKENS:
                    continue
                if m.endswith(".md"):
                    continue

                if m.startswith("skills/"):
                    skill_name = m.split("/", 1)[1]
                    if skill_name and skill_name not in all_skills:
                        res.add_error("LINK", f"Broken skill reference: @{m}", rel_path)
                    continue

                if m in all_skills:
                    continue
                if m in all_rule_stems:
                    continue
                if m.startswith("rules/") and m[len("rules/"):] in all_rule_stems:
                    continue
                if m.startswith("canons/") and m[len("canons/"):] in all_rule_stems:
                    continue

                # Keep implicit mentions permissive to reduce false positives.
                continue

        except Exception as e:
            res.add_error("IO", f"Could not read file: {str(e)}", rel_path)


def check_protocol_compliance(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR PROTOCOL COMPLIANCE ERRORS ---")
    
    # 1. Skill Context & Metadata (Simplified)
    if os.path.exists(SKILLS_DIR):
        for skill_name in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill_name)
            if not os.path.isdir(skill_path): continue
            skill_md = os.path.join(skill_path, "SKILL.md")
            if os.path.exists(skill_md):
                try:
                    content = read_text(skill_md)
                    frontmatter = parse_frontmatter_keys(content)
                    if not frontmatter:
                        rel = os.path.relpath(skill_md, BASE_DIR)
                        res.add_error("PROTOCOL", "Missing YAML frontmatter block", rel)
                        continue

                    # Check required metadata keys in frontmatter only.
                    if "name" not in frontmatter or "description" not in frontmatter:
                        res.add_error("PROTOCOL", "Missing essential metadata (name/description)", f"skills/{skill_name}/SKILL.md")
                except Exception as e:
                    res.add_error("IO", f"Could not read {skill_md}: {str(e)}")

    # 2. Rules Metadata
    if os.path.exists(RULES_DIR):
        for root, _, files in os.walk(RULES_DIR):
            for file in files:
                if not file.endswith(".md"): continue
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, RULES_DIR)
                try:
                    content = read_text(filepath)
                    frontmatter = parse_frontmatter_keys(content)
                    if not frontmatter:
                        res.add_error("PROTOCOL", "Missing YAML frontmatter block", rel_path)
                        continue

                    has_description = "description" in frontmatter
                    has_activation_or_trigger = "activation" in frontmatter or "trigger" in frontmatter
                    if not has_description or not has_activation_or_trigger:
                        res.add_error("PROTOCOL", "Incomplete YAML header", rel_path)
                except Exception as e:
                    res.add_error("IO", f"Could not read {file}: {str(e)}")

def run_audit(output_json: bool = False):
    res = AuditResult()
    verbose = not output_json
    
    if verbose: print("--- STARTING AUDIT ---")
    
    check_foundation_sync(res, verbose=verbose)
    check_mechanical_integrity(res, verbose=verbose)
    check_links(res, verbose=verbose)
    check_protocol_compliance(res, verbose=verbose)
    
    if output_json:
        print(json.dumps({
            "errors": res.errors,
            "warnings": res.warnings,
            "summary": {
                "total_errors": len(res.errors),
                "total_warnings": len(res.warnings),
                "error_severity": severity_counts(res.errors),
                "warning_severity": severity_counts(res.warnings)
            }
        }, indent=2))
    else:
        for err in res.errors:
            print(f"[ERROR] [{err['severity']}] [{err['category']}] {err['message']} ({err['file'] or 'N/A'})")
        for wrn in res.warnings:
            print(f"[WARNING] [{wrn['severity']}] [{wrn['category']}] {wrn['message']} ({wrn['file'] or 'N/A'})")

        if len(res.errors) > 0 or len(res.warnings) > 0:
            print("\n--- SEVERITY SUMMARY ---")
            print(f"Errors  : {severity_counts(res.errors)}")
            print(f"Warnings: {severity_counts(res.warnings)}")
        
        total_errors = len(res.errors)
        if total_errors == 0:
            print("\n[PASS] ALL CHECKS PASSED: Workspace is mechanically sound and protocol compliant.")
        else:
            print(f"\n[FAIL] FAILED: Found {total_errors} integrity/compliance issues.")
    
    sys.exit(1 if len(res.errors) > 0 else 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify workspace integrity and protocol compliance.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    args = parser.parse_args()
    
    # Ensure stdout/stderr handle UTF-8 or at least escape properly
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    run_audit(output_json=args.json)
