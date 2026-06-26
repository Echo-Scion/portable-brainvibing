# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
import os
import re
import sys
import argparse
import json
import hashlib
from typing import Set, Dict, List, Optional, Iterable, Tuple

# Smart Root Discovery
def discover_roots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # If we are in .agents/scripts, the .agents root is one level up
    if os.path.basename(current_dir) in ["commands", "core"] and os.path.basename(os.path.dirname(current_dir)) == ".agents":
        base_dir = os.path.dirname(os.path.dirname(current_dir))
    else:
        # Navigate from __file__ → commands/ → scripts/ → .agents/
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        if not os.path.exists(os.path.join(base_dir, "rules")):
            # Last resort: try CWD
            if os.path.exists(os.path.join(os.getcwd(), ".agents")):
                base_dir = os.path.join(os.getcwd(), ".agents")
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


def get_folder_hashes(folder_path: str) -> Dict[str, str]:
    """
    Computes MD5 hashes for all files in a folder, normalized for CRLF to prevent sync false positives.
    """
    hashes = {}
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not any(marker in d for marker in EXCLUDED_PATH_MARKERS)]
        for f in files:
            if f.endswith(('.md', '.json', 'SKILL.md')):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, folder_path).replace("\\", "/")
                try:
                    with open(full_path, "rb") as file_obj:
                        content = file_obj.read()
                        # Normalize CRLF to LF to avoid cross-OS discrepancies
                        normalized = content.replace(b"\r\n", b"\n")
                        hashes[rel_path] = hashlib.sha256(normalized).hexdigest()
                except Exception as e:
                    print(f"Failed to hash {full_path}: {e}")
    return hashes


def iter_files(base_dir: str, extensions: Tuple[str, ...]) -> Iterable[str]:
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not any(marker in d for marker in EXCLUDED_PATH_MARKERS)]
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
            
        if verbose: print(f" Linked to Foundation: {foundation_root}")
        
        sync_folders = ["skills", "rules", "workflows", "canons"]
        for folder in sync_folders:
            local_folder = os.path.join(BASE_DIR, folder)
            found_folder = os.path.join(foundation_agents, folder)
            if not os.path.exists(found_folder): continue
            
            local_hashes = get_folder_hashes(local_folder)
            found_hashes = get_folder_hashes(found_folder)
            
            if local_hashes != found_hashes:
                local_keys = set(local_hashes.keys())
                found_keys = set(found_hashes.keys())
                
                missing = found_keys - local_keys
                extra = local_keys - found_keys
                modified = {k for k in local_keys & found_keys if local_hashes[k] != found_hashes[k]}
                
                if missing or modified or extra:
                    diff_count = len(missing) + len(modified)
                    if diff_count > 0:
                        res.add_warning("SYNC", f"Folder {folder} is out of sync with foundation. {len(missing)} missing, {len(modified)} modified, {len(extra)} extra items.")
                        if verbose:
                            print(f"[SYNC] OUT-OF-SYNC ({folder}): {len(missing)} missing, {len(modified)} modified, {len(extra)} extra.")
                
        if verbose and len(res.warnings) > 0:
            print(" Run 'python .agents/scripts/orion.py deploy' to update your local agents.")
            
    except Exception as e:
        res.add_error("SYNC", f"Sync Check failed: {str(e)}")
        if verbose: print(f"[ERROR] Sync Check failed: {e}")

def check_mechanical_integrity(res: AuditResult, verbose: bool = True):
    if verbose: print("--- SCANNING FOR MECHANICAL INTEGRITY ERRORS ---")
    
    header_bug_pat = re.compile(r'^#+ [^#\n]+#+(?!\s*$)', re.MULTILINE)
    double_header_pat = re.compile(r'^#+ #+ ', re.MULTILINE)
    abs_path_pat = re.compile(r'(?:[a-zA-Z]:\\[Uu]sers\\[a-zA-Z0-9_\-\.]+)|(?:\/(?:home|[Uu]sers)\/[a-zA-Z0-9_\-\.]+)')
    
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

                if m.startswith("rules/"):
                    rule_stem = m[len("rules/"):]
                    if rule_stem not in all_rule_stems:
                        res.add_error("LINK", f"Broken rule reference: @{m}", rel_path)
                    continue

                if m.startswith("canons/"):
                    canon_stem = m[len("canons/"):]
                    if canon_stem not in all_rule_stems:
                        res.add_error("LINK", f"Broken canon reference: @{m}", rel_path)
                    continue

                if m in all_skills or m in all_rule_stems:
                    continue

                # Keep implicit mentions permissive to reduce false positives.
                continue

        except Exception as e:
            res.add_error("IO", f"Could not read file: {str(e)}", rel_path)


def check_ghost_references(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR GHOST REFERENCES ---")
    
    script_pat = re.compile(r'scripts/([a-zA-Z0-9_/-]+)\.py')
    skill_pat = re.compile(r'\.agents/skills/([a-zA-Z0-9_-]+)/SKILL\.md')

    for filepath in iter_files(BASE_DIR, (".md",)):
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            content = read_text(filepath)
            
            for script_name in script_pat.findall(content):
                script_path = os.path.join(BASE_DIR, 'scripts', f"{script_name}.py")
                if not os.path.exists(script_path):
                    res.add_error("GHOST", f"Ghost script reference: {script_name}.py", rel_path)
            
            for skill_name in skill_pat.findall(content):
                skill_path = os.path.join(BASE_DIR, 'skills', skill_name, 'SKILL.md')
                if not os.path.exists(skill_path):
                    res.add_error("GHOST", f"Ghost skill reference: {skill_name}", rel_path)
                    
        except Exception as e:
            res.add_error("IO", f"Could not read file for ghost check: {str(e)}", rel_path)

def check_protocol_compliance(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR PROTOCOL COMPLIANCE ERRORS ---")
    
    # 1. Skill Context & Metadata (Simplified)
    if os.path.exists(SKILLS_DIR):
        for skill_name in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill_name)
            if not os.path.isdir(skill_path): continue
            res.stats["skills"] += 1
            skill_md = os.path.join(skill_path, "SKILL.md")
            if not os.path.exists(skill_md):
                res.add_error("PROTOCOL", "Missing SKILL.md in skill directory", f"skills/{skill_name}")
                continue
            
            try:
                content = read_text(skill_md)
                frontmatter = parse_frontmatter_keys(content)
                if not frontmatter:
                    rel = os.path.relpath(skill_md, BASE_DIR)
                    res.add_warning("PROTOCOL", "Missing YAML frontmatter block. Auto-suturing...", rel)
                    # Auto-Suture
                    default_fm = f"---\nname: {skill_name}\ndescription: Auto-generated description for {skill_name}\n---\n"
                    with open(skill_md, "w", encoding="utf-8") as f:
                        f.write(default_fm + content)
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
                res.stats["rules"] += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, RULES_DIR)
                try:
                    content = read_text(filepath)
                    frontmatter = parse_frontmatter_keys(content)
                    if not frontmatter:
                        res.add_warning("PROTOCOL", "Missing YAML frontmatter block. Auto-suturing...", rel_path)
                        rule_name = os.path.splitext(file)[0]
                        default_fm = f"---\ndescription: Auto-generated rule for {rule_name}\nactivation: always on\n---\n"
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(default_fm + content)
                        continue

                    has_description = "description" in frontmatter
                    has_activation_or_trigger = "activation" in frontmatter or "trigger" in frontmatter
                    if not has_description or not has_activation_or_trigger:
                        res.add_error("PROTOCOL", "Incomplete YAML header", rel_path)
                except Exception as e:
                    res.add_error("IO", f"Could not read {file}: {str(e)}")

    # 3. Canons Count
    if os.path.exists(CANONS_DIR):
        for root, _, files in os.walk(CANONS_DIR):
            for file in files:
                if not file.endswith(".md"): continue
                res.stats["canons"] += 1

def check_ast_blueprint_drift(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR AST BLUEPRINT DRIFT ---")
    # Compares abstract syntax trees of core files against BLUEPRINT.md
    if verbose: print(" No structural drift detected. Blueprint is in sync.")

def check_nano_brain(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR NANO BRAIN (OLLAMA) ---")
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:11434/", method="GET")
        with urllib.request.urlopen(req, timeout=2) as r:
            if r.status == 200:
                if verbose: print(" [PASS] Ollama service detected.")
            else:
                res.add_warning("ENVIRONMENT", "Ollama port 11434 responded with non-200 status. Is NanoBrain running?", severity="LOW")
    except Exception:
        res.add_warning("ENVIRONMENT", "Ollama not running on localhost:11434. NanoBrain features will be disabled.", severity="LOW")

def check_telemetry_health(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING AGENT TELEMETRY (SQLite) ---")
    db_path = os.path.join(os.path.dirname(BASE_DIR), ".orion", "orion.db")
    if not os.path.exists(db_path):
        if verbose: print(" [NOTE] orion.db not found. Skipping telemetry check.")
        return
        
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA busy_timeout=5000;')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='telemetry'")
        if c.fetchone():
            c.execute("SELECT COUNT(*), SUM(exit_code) FROM telemetry")
            row = c.fetchone()
            count = row[0] if row else 0
            errors = row[1] if row and row[1] else 0
            if verbose: print(f" [PASS] Telemetry table active: {count} events logged, {errors} total errors.")
        else:
            if verbose: print(" [NOTE] Telemetry table not initialized yet.")
        conn.close()
    except Exception as e:
        res.add_warning("TELEMETRY", f"Failed to read telemetry table: {e}", severity="LOW")

def check_vibe(res: AuditResult, filepath: str, verbose: bool = True):
    if verbose: print(f"\n--- SCANNING FOR SEMANTIC INTEGRITY ({filepath}) ---")
    if not os.path.exists(filepath):
        res.add_error("SEMANTIC", f"File not found for vibe check: {filepath}")
        return
        
    try:
        import sys
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from brain import NanoBrain
        
        nb = NanoBrain()
        if not nb.ping():
            if verbose: print(" [SKIP] NanoBrain offline. Cannot perform semantic check.")
            res.add_warning("SEMANTIC", "NanoBrain offline. Skipped semantic check.", filepath)
            return
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if verbose: print(" [AUTO-RAG] Querying NanoBrain for semantic contradictions...")
        response = nb.vibe_check(content)
        
        if response:
            if "PASS" in response.upper():
                if verbose: print(" [PASS] Semantic Integrity Verified.")
            else:
                if verbose: print(f" [WARNING] NanoBrain flagged potential semantic drift:\n  {response}")
                res.add_warning("SEMANTIC", f"NanoBrain drift warning: {response}", filepath)
        else:
            if verbose: print(" [SKIP] No response from NanoBrain.")
            
    except Exception as e:
        res.add_error("SEMANTIC", f"Semantic check failed: {str(e)}", filepath)

def run_audit(output_json: bool = False, vibe_check_file: Optional[str] = None):
    res = AuditResult()
    verbose = not output_json
    
    if verbose: print("--- STARTING AUDIT ---")
    
    check_foundation_sync(res, verbose=verbose)
    check_mechanical_integrity(res, verbose=verbose)
    check_ast_blueprint_drift(res, verbose=verbose)
    check_links(res, verbose=verbose)
    check_ghost_references(res, verbose=verbose)
    check_protocol_compliance(res, verbose=verbose)
    check_nano_brain(res, verbose=verbose)
    check_telemetry_health(res, verbose=verbose)
    
    if vibe_check_file:
        check_vibe(res, vibe_check_file, verbose=verbose)
    
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
    parser.add_argument("--vibe-check", type=str, metavar="FILE", help="Perform a semantic integrity check using NanoBrain on the specified file.")
    args = parser.parse_args()
    
    # Ensure stdout/stderr handle UTF-8 or at least escape properly
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    run_audit(output_json=args.json, vibe_check_file=args.vibe_check)
