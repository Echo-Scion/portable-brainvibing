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
import shlex
import time
import subprocess
import shutil
import ast
import builtins
from dataclasses import dataclass
from typing import Set, Dict, List, Optional, Iterable, Tuple, Any, Sequence

# Prevent Python from writing .pyc and __pycache__ inside .agents ecosystem
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Import unified primitives from core.kernel
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

try:
    from commands.foundation import resolve_template_string
except ImportError:
    try:
        from foundation import resolve_template_string
    except ImportError:
        resolve_template_string = None

try:
    from core import connect_sqlite, log_telemetry as _kernel_log_telemetry
    def _log_telemetry(err: Exception, context: str = "") -> None:
        _kernel_log_telemetry(err, context)
except ImportError:
    def _log_telemetry(err: Exception, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
    def connect_sqlite(db_path, wal=True, timeout_sec=5.0):
        import sqlite3
        conn = sqlite3.connect(db_path, timeout=timeout_sec)
        conn.execute(f"PRAGMA busy_timeout={int(timeout_sec * 1000)};")
        return conn

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'verify_agents.py:17')

# Smart Root Discovery
def discover_roots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Ascend to .agents root
    cur = current_dir
    while cur and os.path.basename(cur) != "":
        if os.path.basename(cur) == ".agents":
            return cur
        cur = os.path.dirname(cur)
    
    # Fallback to CWD traversal
    cur = os.getcwd()
    while True:
        if os.path.exists(os.path.join(cur, ".agents")):
            return os.path.join(cur, ".agents")
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    
    return os.path.join(os.getcwd(), ".agents")

BASE_DIR = discover_roots()
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CONTEXT_DIR = os.path.join(PROJECT_ROOT, "context")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
RULES_DIR = os.path.join(BASE_DIR, "rules")
CANONS_DIR = os.path.join(BASE_DIR, "canons")
FOUNDATION_PATH_MARKER = os.path.join(BASE_DIR, ".foundation_path")
IS_SPOKE = os.path.exists(FOUNDATION_PATH_MARKER)

# ==============================================================================
# CONTEXT NAMING LINT (Absorbed from context_naming_lint.py)
# ==============================================================================

PILLAR_MASTERS: Dict[str, str] = {
    "00_Strategy": "BLUEPRINT.md",
    "01_Product": "ROADMAP.md",
    "02_Creative": "STYLE_GUIDE.md",
    "03_Tech": "ARCHITECTURE.md",
}

# 25-File Golden Ratio Registry: 1 Master + 4-5 Cohesive Domain Facets per Pillar (<=6 files/folder)
STANDARD_MASTERS: Dict[str, Set[str]] = {
    "00_Strategy": {
        "MEMORY.md",
        "PERSONAS_AND_MARKET.md",
        "ACQUISITION_AND_GROWTH.md",
        "MONETIZATION_AND_PRICING.md",
        "RETENTION_AND_LEGAL.md",
    },
    "01_Product": {
        "PRD_CORE_FEATURES.md",
        "USER_JOURNEYS_AND_FLOWS.md",
        "ANALYTICS_AND_METRICS.md",
        "INTEGRATIONS_AND_WEBHOOKS.md",
        "FEEDBACK_AND_BACKLOG.md",
    },
    "02_Creative": {
        "UI_COMPONENTS_AND_PATTERNS.md",
        "UX_AND_ACCESSIBILITY.md",
        "BRAND_VOICE_AND_COPY.md",
        "VISUAL_ASSETS_AND_MEDIA.md",
    },
    "03_Tech": {
        "DATABASE_AND_STORAGE.md",
        "API_AND_CONTRACTS.md",
        "STATE_AND_DOMAIN_LOGIC.md",
        "SECURITY_AND_AUTH.md",
        "INFRA_AND_DEVOPS.md",
    },
}

TRANSITIONAL_ALLOWED: Dict[str, Set[str]] = {
    "00_Strategy": {"MARKET_AND_GROWTH.md"},
    "01_Product": {"PRD.md", "PRD_SPECS.md", "USER_ANALYTICS.md"},
    "02_Creative": {"UX_AND_COPY.md"},
    "03_Tech": {"DATA_AND_API.md", "INFRA_AND_SECURITY.md"},
}

ROOT_ALLOWED = {
    "VISION.md",
    "README.md",
    "MIGRATION_MAP.md",
    "AGENT_IDENTITY.md",
}


def parse_registry(path: str) -> Dict[str, Set[str]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Registry not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    allowed: Dict[str, Set[str]] = {k: set() for k in PILLAR_MASTERS.keys()}
    current_pillar = None

    pillar_pattern = re.compile(r"##\s+\d+\.\s+Pillar:\s+`([^`]+)/`")
    row_pattern = re.compile(r"\|\s*\*\*[^|]+\*\*\s*\|\s*`([^`]+)`\s*\|(.+)\|")

    for raw in lines:
        line = raw.strip()
        p_match = pillar_pattern.match(line)
        if p_match:
            current_pillar = p_match.group(1)
            continue

        r_match = row_pattern.match(line)
        if not r_match or current_pillar not in allowed:
            continue

        prefix = r_match.group(1)
        files_col = r_match.group(2)
        file_parts = re.findall(r"`([^`]+\.md)`", files_col)
        for file_name in file_parts:
            if not file_name.endswith(".md"):
                continue
            allowed[current_pillar].add(f"{prefix}{file_name}")

    return allowed


def lint_context(strict: bool = True) -> Tuple[int, int, List[str]]:
    errors = 0
    warnings = 0
    output: List[str] = []

    context_dir = os.path.join(PROJECT_ROOT, "context")
    registry_file = os.path.join(BASE_DIR, "templates", "PROJECT_SCAFFOLD.template.md")

    if not os.path.isdir(context_dir):
        output.append("[INFO] Workspace lacks context/ dir. Bypassing context naming lint.")
        return 0, 0, output

    # Load optional epigenetic context_aliases from .agents/.dna.json for brownfield flexibility
    epigenetic_context_files: Set[str] = set()
    dna_json_path = os.path.join(BASE_DIR, ".dna.json")
    if os.path.isfile(dna_json_path):
        try:
            with open(dna_json_path, "r", encoding="utf-8") as _df:
                _dna_data = json.load(_df)
                for _src_rel in (_dna_data.get("context_aliases") or {}).keys():
                    epigenetic_context_files.add(_src_rel.replace("\\", "/"))
        except Exception:
            pass

    # Source Code Collision Shield: check if context/ contains source code files
    code_extensions = {".ts", ".tsx", ".js", ".jsx", ".py", ".dart", ".go", ".rs", ".kt", ".java", ".cpp", ".c"}
    has_source_code_in_context = False
    for root, _, files in os.walk(context_dir):
        if any(os.path.splitext(f)[1].lower() in code_extensions for f in files):
            has_source_code_in_context = True
            break

    if has_source_code_in_context:
        output.append("[INFO] [CODE_COLLISION_GUARD] Source code detected inside context/ directory. Bypassing context naming lint.")
        return 0, 0, output

    allowed_from_registry = parse_registry(registry_file) if os.path.isfile(registry_file) else {}

    root_files = [f for f in os.listdir(context_dir) if os.path.isfile(os.path.join(context_dir, f))]
    for f in sorted(root_files):
        rel_p = f"context/{f}"
        if f not in ROOT_ALLOWED and not f.startswith("local-") and rel_p not in epigenetic_context_files:
            errors += 1
            output.append(
                f"[ERROR] context/{f} is not allowed at context root. "
                f"Allowed root files: {', '.join(sorted(ROOT_ALLOWED))} (or 'local-*')"
            )

    has_any_pillar = any(os.path.isdir(os.path.join(context_dir, p)) for p in PILLAR_MASTERS.keys())
    if not has_any_pillar:
        output.append("[INFO] Workspace context/ is in lean/foundation mode (no SaaS pillars scaffolded yet). Bypassing pillar check.")
        return errors, warnings, output

    for pillar, master in PILLAR_MASTERS.items():
        pillar_path = os.path.join(context_dir, pillar)
        if not os.path.isdir(pillar_path):
            errors += 1
            output.append(f"[ERROR] Missing required pillar directory: context/{pillar}")
            continue

        files = [f for f in os.listdir(pillar_path) if os.path.isfile(os.path.join(pillar_path, f))]
        if master not in files:
            errors += 1
            output.append(f"[ERROR] Missing required master file: context/{pillar}/{master}")

        allowed = set(allowed_from_registry.get(pillar, set()))
        allowed.add(master)
        allowed.update(STANDARD_MASTERS.get(pillar, set()))
        allowed.update(TRANSITIONAL_ALLOWED.get(pillar, set()))

        for f in sorted(files):
            rel_p = f"context/{pillar}/{f}"
            if f in allowed or rel_p in epigenetic_context_files:
                if f in TRANSITIONAL_ALLOWED.get(pillar, set()):
                    warnings += 1
                    output.append(
                        f"[WARNING] Transitional file kept for compatibility: context/{pillar}/{f}"
                    )
                continue

            if strict:
                errors += 1
                output.append(
                    f"[ERROR] Non-registry file in context/{pillar}: {f}. "
                    f"Use 25-file Golden Ratio registry names or add epigenetic alias."
                )
            else:
                warnings += 1
                output.append(
                    f"[WARNING] Non-registry file in context/{pillar}: {f}. "
                    f"Use 25-file Golden Ratio registry names or add epigenetic alias."
                )

    return errors, warnings, output


def main_context_lint(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="verify_agents.py context-lint", description="Lint context naming against 25-File Golden Ratio + Epigenetic Registry.")
    parser.add_argument("--non-strict", action="store_true", help="Downgrade non-registry files to warnings.")
    args = parser.parse_args(argv if argv is not None else sys.argv[2:])

    strict = not args.non_strict
    print("Running Context Naming Lint (25-File Golden Ratio + Epigenetic Registry)...")

    try:
        errors, warnings, output = lint_context(strict=strict)
    except Exception as ex:
        _log_telemetry(ex, "verify_agents:main_context_lint")
        print(f"[ERROR] Lint failed unexpectedly: {ex}")
        return 1

    for line in output:
        print(line)

    if errors:
        print(f"\nContext naming lint failed: {errors} error(s), {warnings} warning(s).")
        return 1

    print(f"\nContext naming lint passed: 0 error(s), {warnings} warning(s).")
    return 0


EXCLUDED_PATH_MARKERS = [".git", ".gemini", ".system_generated", "node_modules", "__pycache__", "archive", ".archive", "teamwork", "scratch", "internal", "local"]
DOC_METADATA_KEYS = {"param", "return", "type", "description", "activation", "trigger"}
RULE_DIR_TOKENS = {"rules", "common", "flutter", "web", "canons", "auth", "notifications", "ui-patterns"}


def get_folder_hashes(folder_path: str) -> Dict[str, str]:
    """
    Computes MD5 hashes for all files in a folder, normalized for CRLF to prevent sync false positives.
    """
    hashes = {}
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not any(marker in d for marker in EXCLUDED_PATH_MARKERS)]
        for f in files:
            if f.endswith(('.sidecar.json', '.ledger.jsonl')) or f.startswith('.'):
                continue
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


def iter_files(base_dir: str, extensions: Tuple[str, ...], include_root_configs: bool = True) -> Iterable[str]:
    if include_root_configs:
        workspace_root = os.path.dirname(base_dir)
        for root_cfg in ["GEMINI.md", "AGENTS.md", "CLAUDE.md", "README.md", "DEPLOY_ME.md"]:
            cfg_path = os.path.join(workspace_root, root_cfg)
            if os.path.isfile(cfg_path) and any(cfg_path.endswith(ext) for ext in extensions):
                yield cfg_path

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if not any(marker in d for marker in EXCLUDED_PATH_MARKERS)]
        for file_name in files:
            if file_name.endswith(extensions):
                yield os.path.join(root, file_name)


_TEXT_CACHE: Dict[str, str] = {}
_CTRL_STR_PAT = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def read_text(filepath: str) -> str:
    cached = _TEXT_CACHE.get(filepath)
    if cached is not None:
        return cached
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    _TEXT_CACHE[filepath] = content
    return content


def parse_frontmatter_keys(content: str) -> Dict[str, str]:
    try:
        from core.scanner import parse_frontmatter
        data, _ = parse_frontmatter(content)
        if data:
            return {
                str(k).strip().lower(): (str(v).strip() if not isinstance(v, (dict, list)) else json.dumps(v))
                for k, v in data.items()
            }
        return {}
    except Exception as _e:
        _log_telemetry(_e, "verify_agents:parse_frontmatter_keys")
        return {}


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
        
        sync_folders = ["skills", "rules", "canons"]
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
                raw_modified = {k for k in local_keys & found_keys if local_hashes[k] != found_hashes[k]}
                modified = set()
                manifest_path = os.path.join(BASE_DIR, ".project_manifest.json")
                manifest = {}
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as mf:
                            manifest = json.load(mf)
                    except Exception as _me:
                        _log_telemetry(_me, "verify_agents:load_manifest")
                        manifest = {}

                project_name = os.path.basename(os.path.dirname(BASE_DIR))
                for k in raw_modified:
                    found_file = os.path.join(found_folder, k)
                    if manifest and resolve_template_string and k.endswith(".md") and os.path.exists(found_file):
                        try:
                            with open(found_file, "r", encoding="utf-8") as ff:
                                found_text = ff.read()
                            if "{{" in found_text:
                                resolved = resolve_template_string(found_text, manifest, project_name)
                                norm_resolved = resolved.replace("\r\n", "\n").encode("utf-8")
                                if hashlib.sha256(norm_resolved).hexdigest() == local_hashes[k]:
                                    continue
                        except Exception as _te:
                            _log_telemetry(_te, "verify_agents:template_diff_check")
                    modified.add(k)
                
                if missing or modified or extra:
                    diff_count = len(missing) + len(modified)
                    if diff_count > 0:
                        res.add_warning("SYNC", f"Folder {folder} is out of sync with foundation. {len(missing)} missing, {len(modified)} modified, {len(extra)} extra items.")
                        if verbose:
                            print(f"[SYNC] OUT-OF-SYNC ({folder}): {len(missing)} missing, {len(modified)} modified, {len(extra)} extra.")
                
        if verbose and len(res.warnings) > 0:
            print(" Run 'python .agents/scripts/orion.py foundation deploy --target <path>' to update your local agents.")
            
    except Exception as e:
        res.add_error("SYNC", f"Sync Check failed: {str(e)}")
        if verbose: print(f"[ERROR] Sync Check failed: {e}")

def check_mechanical_integrity(res: AuditResult, verbose: bool = True):
    if verbose: print("--- SCANNING FOR MECHANICAL INTEGRITY ERRORS ---")
    
    header_bug_pat = re.compile(r'^#+ [^#\n]+#+(?!\s*$)', re.MULTILINE)
    double_header_pat = re.compile(r'^#+ #+ ', re.MULTILINE)
    abs_path_pat = re.compile(r'(?:[a-zA-Z]:\\[Uu]sers\\[a-zA-Z0-9_\-\.]+)|(?:\/(?:home|[Uu]sers)\/[a-zA-Z0-9_\-\.]+)')
    corrupt_wikilink_pat = re.compile(r'\[\[[a-zA-Z0-9_\-\./]+\]\]\)')
    
    for filepath in iter_files(BASE_DIR, (".md", ".py", ".json", ".jsonl")):
        file = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, BASE_DIR)
        
        try:
            content = read_text(filepath)
            ctrl_match = _CTRL_STR_PAT.search(content)
            if ctrl_match:
                byte_idx = len(content[:ctrl_match.start()].encode("utf-8"))
                b = ord(ctrl_match.group(0))
                res.add_error("MECHANICAL", f"Unwanted control character (0x{b:02x}) at byte {byte_idx}", rel_path)
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".py":
                try:
                    ast.parse(content, filename=filepath)
                except SyntaxError as se:
                    res.add_error("SYNTAX", f"Python syntax error: {se}", rel_path)
            elif ext == ".json":
                try:
                    json.loads(content)
                except Exception as je:
                    res.add_error("SYNTAX", f"JSON syntax error: {je}", rel_path)
            if file.endswith(".md"):
                if header_bug_pat.search(content):
                    res.add_error("MECHANICAL", "Concatenated headers detected", rel_path)
                if double_header_pat.search(content):
                    res.add_error("MECHANICAL", "Double headers (## ##) detected", rel_path)
                if corrupt_wikilink_pat.search(content):
                    res.add_error("MECHANICAL", "Malformed wikilink with trailing parenthesis detected (linkify corruption)", rel_path)
            if file.endswith(".py") and abs_path_pat.search(content):
                if file not in ["verify_agents.py", "publish_agents.py", "audit_repo.py"]:
                    res.add_error("MECHANICAL", "Absolute path detected in Python file", rel_path)
        except Exception as e:
            res.add_error("IO", f"Could not read file: {str(e)}", rel_path)

def find_line_num(text: str, token: str) -> int:
    idx = text.find(token)
    if idx == -1:
        return 1
    return text[:idx].count('\n') + 1

def check_links(res: AuditResult, verbose: bool = True):
    all_skills: Set[str] = set([str(d) for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))]) if os.path.exists(SKILLS_DIR) else set([])
    all_rules: Set[str] = set([])
    all_rule_stems: Set[str] = set([])
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    for d in [RULES_DIR, CANONS_DIR, TEMPLATES_DIR]:
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
    md_link_pattern = re.compile(r'\[[^\]]*\]\(([^)]+\.(?:md|py|json|ya?ml)(?:#[^)]*)?)\)')
    concept_wikilinks = {"knowledge", "context", "wikilinks"}

    for filepath in iter_files(BASE_DIR, (".md",)):
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            content = read_text(filepath)

            # Rule and Canon links (@reference.md)
            for r in rule_pattern.findall(content):
                r_clean = r.split('`')[0].strip().replace("\\", "/")
                if r_clean not in all_rules:
                    line_no = find_line_num(content, f"@{r}")
                    res.add_error("LINK", f"Broken rule reference: @{r_clean}", f"{rel_path}:{line_no}")

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
                        line_no = find_line_num(content, f"@{mention}")
                        res.add_error("LINK", f"Broken skill reference: @{m}", f"{rel_path}:{line_no}")
                    continue

                if m.startswith("rules/"):
                    rule_stem = m[len("rules/"):]
                    if rule_stem not in all_rule_stems:
                        line_no = find_line_num(content, f"@{mention}")
                        res.add_error("LINK", f"Broken rule reference: @{m}", f"{rel_path}:{line_no}")
                    continue

                if m.startswith("canons/"):
                    canon_stem = m[len("canons/"):]
                    if canon_stem not in all_rule_stems:
                        line_no = find_line_num(content, f"@{mention}")
                        res.add_error("LINK", f"Broken canon reference: @{m}", f"{rel_path}:{line_no}")
                    continue

                if m in all_skills or m in all_rule_stems:
                    continue

                # Keep implicit mentions permissive to reduce false positives.
                continue
                
            # Validate file paths inside inline backticks before stripping them
            workspace_root = os.path.dirname(BASE_DIR)
            backtick_file_pat = re.compile(r'`(?:\.?\.agents/)?((?:rules|skills|canons|templates|scripts|evals|hooks|references)/[a-zA-Z0-9_\-/\.]+\.(?:md|py|json|jsonl|ya?ml|toml|sql|sh))`')
            for match in backtick_file_pat.finditer(content):
                target = match.group(1).replace('\\', '/')
                if any(tok in target for tok in ['{{', '}}', '<', '>', '*', '$']):
                    continue
                
                # Check resolution
                workspace_target = os.path.normpath(os.path.join(workspace_root, target))
                agents_target = os.path.normpath(os.path.join(BASE_DIR, target))
                doc_target = os.path.normpath(os.path.join(os.path.dirname(filepath), target))
                
                # Check skill-relative reference if in skills/
                skill_dir_target = ""
                parts = rel_path.replace('\\', '/').split('/')
                if target.startswith("references/") and "skills" in parts:
                    s_idx = parts.index("skills")
                    if s_idx + 1 < len(parts):
                        skill_dir_target = os.path.normpath(os.path.join(BASE_DIR, "skills", parts[s_idx + 1], target))

                exists = (
                    os.path.exists(workspace_target) or
                    os.path.exists(agents_target) or
                    os.path.exists(doc_target) or
                    (skill_dir_target and os.path.exists(skill_dir_target))
                )
                if not exists and "skills/internal" not in target.replace('\\', '/'):
                    if not (IS_SPOKE and target.replace('\\', '/').startswith("canons/ecosystems/")):
                        line_no = find_line_num(content, match.group(0))
                        res.add_error("LINK", f"Broken backticked file reference: `{target}`", f"{rel_path}:{line_no}")

            # Strip code fences and inline backticks to avoid false positives on doc examples
            non_code_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            non_code_content = re.sub(r'`[^`\n]*`', '', non_code_content)

            # Standard Markdown Links
            for link in md_link_pattern.findall(non_code_content):
                l_clean = link.split('#')[0].strip()
                if not l_clean or l_clean.startswith(('http', 'mailto')):
                    continue
                if l_clean.startswith('file://'):
                    line_no = find_line_num(content, link)
                    res.add_error("LINK", f"Forbidden file:// scheme in source markdown: {l_clean}", f"{rel_path}:{line_no}")
                    continue
                if any(token in l_clean for token in ['{{', '}}', '<', '>']):
                    continue
                # Resolve relative path
                target_path = os.path.normpath(os.path.join(os.path.dirname(filepath), l_clean))
                if not os.path.exists(target_path):
                    if not (IS_SPOKE and "canons/ecosystems/" in l_clean.replace('\\', '/')):
                        line_no = find_line_num(content, link)
                        res.add_error("LINK", f"Broken markdown link: {l_clean}", f"{rel_path}:{line_no}")

            # Wikilinks [[target]]
            wikilink_pat = re.compile(r'\[\[([a-zA-Z0-9_\-\./\\]+)\]\]')
            for wl in wikilink_pat.findall(non_code_content):
                wl_clean = wl.strip().replace('\\', '/')
                matched = (
                    wl_clean in concept_wikilinks or
                    wl_clean in all_skills or 
                    wl_clean in all_rule_stems or 
                    wl_clean in all_rules or 
                    os.path.exists(os.path.join(BASE_DIR, wl_clean)) or
                    os.path.exists(os.path.join(BASE_DIR, wl_clean + '.md'))
                )
                if not matched:
                    line_no = find_line_num(content, f"[[{wl}]]")
                    res.add_error("LINK", f"Broken wikilink: [[{wl_clean}]]", f"{rel_path}:{line_no}")

            # view_file targets
            view_file_pat = re.compile(r'view_file\s+([a-zA-Z0-9_\-\./\\]+\.md)')
            for vf in view_file_pat.findall(content):
                vf_clean = vf.strip().replace('\\', '/')
                if any(token in vf_clean for token in ['{{', '}}', '<', '>']):
                    continue
                workspace_target = os.path.normpath(os.path.join(os.path.dirname(BASE_DIR), vf_clean))
                agents_target = os.path.normpath(os.path.join(BASE_DIR, vf_clean))
                doc_target = os.path.normpath(os.path.join(os.path.dirname(filepath), vf_clean))
                if not (os.path.exists(workspace_target) or os.path.exists(agents_target) or os.path.exists(doc_target)):
                    line_no = find_line_num(content, vf)
                    res.add_error("LINK", f"Broken view_file target: {vf_clean}", f"{rel_path}:{line_no}")

        except Exception as e:
            res.add_error("IO", f"Could not read file: {str(e)}", rel_path)


def check_ghost_references(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR GHOST REFERENCES ---")
    
    script_pat = re.compile(r'(?<![a-zA-Z0-9_/-])(?P<prefix>scripts/|commands/|core/|utils/|evals/|hooks/)(?P<name>[a-zA-Z0-9_/-]+)\.py')
    skill_pat = re.compile(r'\.agents/skills/([a-zA-Z0-9_-]+)/SKILL\.md')
    skill_ref_pat = re.compile(r'(?:(\.agents/skills/[a-zA-Z0-9_-]+/)?references/([a-zA-Z0-9_\-\.]+\.md))')
    orion_cmd_pat = re.compile(r'python\s+\.?\.agents/scripts/orion\.py\s+([a-zA-Z0-9_-]+)')

    orion_py = os.path.join(BASE_DIR, 'scripts', 'orion.py')
    valid_orion_cmds = set()
    if os.path.exists(orion_py):
        try:
            o_txt = read_text(orion_py)
            cmd_map_match = re.search(r'CMD_MAP\s*=\s*\{([^}]+)\}', o_txt)
            if cmd_map_match:
                valid_orion_cmds = set(re.findall(r'"([a-zA-Z0-9_-]+)"\s*:', cmd_map_match.group(1)))
        except Exception as _e:
            _log_telemetry(_e, 'verify_agents.py:380')

    # Check skill references/ files exist and enforce canonical workspace-relative paths
    if os.path.exists(SKILLS_DIR):
        for skill_name in os.listdir(SKILLS_DIR):
            skill_folder = os.path.join(SKILLS_DIR, skill_name)
            if not os.path.isdir(skill_folder):
                continue
            skill_md = os.path.join(skill_folder, "SKILL.md")
            if os.path.exists(skill_md):
                try:
                    s_content = read_text(skill_md)
                    rel_skill_path = os.path.relpath(skill_md, BASE_DIR)
                    for match in skill_ref_pat.finditer(s_content):
                        prefix, ref_file = match.group(1), match.group(2)
                        if not prefix:
                            ref_path = os.path.join(skill_folder, "references", ref_file)
                        else:
                            workspace_root = os.path.dirname(BASE_DIR)
                            clean_prefix = prefix.strip()
                            if clean_prefix.startswith("./"):
                                clean_prefix = clean_prefix[2:]
                            clean_prefix = clean_prefix.strip("/\\")
                            ref_path = os.path.normpath(os.path.join(workspace_root, clean_prefix, "references", ref_file))
                        if not os.path.exists(ref_path):
                            if "skills/internal" in ref_path or "skills\\internal" in ref_path:
                                continue
                            res.add_error("GHOST", f"Ghost skill reference: {match.group(0)}", rel_skill_path)

                    ref_folder = os.path.join(skill_folder, "references")
                    if os.path.isdir(ref_folder):
                        for disk_ref in os.listdir(ref_folder):
                            if disk_ref.startswith("evidence-"):
                                continue
                            if disk_ref.endswith(".md") and disk_ref not in s_content:
                                res.add_warning("PROTOCOL", f"Unindexed reference file: {disk_ref} exists in references/ but is not linked in {skill_name}/SKILL.md", rel_skill_path, severity="LOW")
                except Exception as e:
                    res.add_error("IO", f"Could not read {skill_md}: {str(e)}")

    for filepath in iter_files(BASE_DIR, (".md",)):
        if os.path.basename(filepath) in ("OBSERVATIONS.md", "OBSERVATIONS.archive.md", "LEARNINGS.md"):
            continue
        rel_path = os.path.relpath(filepath, BASE_DIR)
        try:
            content = read_text(filepath)
            
            for script_match in script_pat.finditer(content):
                prefix = script_match.group("prefix")
                script_name = script_match.group("name")
                scripts_root = os.path.join(BASE_DIR, "scripts")
                root_dir = {
                    "scripts/": scripts_root,
                    "evals/": os.path.join(BASE_DIR, "evals"),
                    "hooks/": os.path.join(BASE_DIR, "hooks"),
                }.get(prefix, os.path.join(scripts_root, prefix.rstrip("/")))
                script_path = os.path.join(root_dir, f"{script_name}.py")
                workspace_script_path = os.path.join(PROJECT_ROOT, f"{prefix}{script_name}.py")
                if not os.path.exists(script_path) and not os.path.exists(workspace_script_path):
                    res.add_error("GHOST", f"Ghost script reference: {script_name}.py", rel_path)
            
            for skill_name in skill_pat.findall(content):
                skill_path = os.path.join(BASE_DIR, 'skills', skill_name, 'SKILL.md')
                workspace_skill_path = os.path.join(PROJECT_ROOT, 'skills', skill_name, 'SKILL.md')
                if not os.path.exists(skill_path) and not os.path.exists(workspace_skill_path) and skill_name != "internal":
                    res.add_error("GHOST", f"Ghost skill reference: {skill_name}", rel_path)

            # Universal skill reference validation across all scanned documents
            for match in skill_ref_pat.finditer(content):
                prefix, ref_file = match.group(1), match.group(2)
                if prefix:
                    workspace_root = os.path.dirname(BASE_DIR)
                    clean_prefix = prefix.strip()
                    if clean_prefix.startswith("./"):
                        clean_prefix = clean_prefix[2:]
                    clean_prefix = clean_prefix.strip("/\\")
                    ref_path = os.path.normpath(os.path.join(workspace_root, clean_prefix, "references", ref_file))
                    if not os.path.exists(ref_path) and "skills/internal" not in ref_path.replace("\\", "/"):
                        line_no = find_line_num(content, match.group(0))
                        res.add_error("GHOST", f"Ghost skill reference: {match.group(0)}", f"{rel_path}:{line_no}")

            raw_agents_path_pat = re.compile(r'(?:\.?\.agents/|(?:^|[\s|`(]))((?:rules|skills|canons|templates|scripts|evals|hooks)/[a-zA-Z0-9_\-/\.]+\.(?:md|py|json|jsonl|ya?ml))')
            for match in raw_agents_path_pat.finditer(content):
                target_rel = match.group(1).rstrip(')`\'"')
                if any(tok in target_rel for tok in ['{{', '}}', '<', '>']):
                    continue
                target_full = os.path.normpath(os.path.join(BASE_DIR, target_rel))
                target_workspace = os.path.normpath(os.path.join(PROJECT_ROOT, target_rel))
                if not os.path.exists(target_full) and not os.path.exists(target_workspace) and "skills/internal" not in target_rel.replace('\\', '/'):
                    if not (IS_SPOKE and target_rel.replace('\\', '/').startswith("canons/ecosystems/")):
                        line_no = find_line_num(content, match.group(0))
                        res.add_error("GHOST", f"Ghost path reference: `{target_rel}`", f"{rel_path}:{line_no}")

            # Check public routers for leaked skills/internal
            if rel_path in ("AGENTS.md", "GEMINI.md", "AGENTS_INDEX.md", "README.md",
                            os.path.join(".agents", "AGENTS_INDEX.md"), "AGENTS_INDEX.md"):
                if "skills/internal" in content:
                    line_no = find_line_num(content, "skills/internal")
                    res.add_error("GHOST", "Public router leaks maintainer-only skills/internal path", f"{rel_path}:{line_no}")

            if valid_orion_cmds:
                for orion_sub in orion_cmd_pat.findall(content):
                    if orion_sub not in valid_orion_cmds:
                        line_no = find_line_num(content, orion_sub)
                        res.add_error("GHOST", f"Invalid orion CLI subcommand: '{orion_sub}'", f"{rel_path}:{line_no}", severity="HIGH")
                    
        except Exception as e:
            res.add_error("IO", f"Could not read file for ghost check: {str(e)}", rel_path)

def check_protocol_compliance(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR PROTOCOL COMPLIANCE ERRORS ---")
    
    # 1. Skill Context & Metadata (Antigravity Gold Standard: docs/skills.md)
    # Skills are loaded on-demand via Progressive Disclosure (name + description required; no hard byte cap, 500-line advisory guideline).
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
                lines = content.splitlines()
                line_count = len(lines)
                if line_count > 500:
                    res.add_warning("PROTOCOL", f"SKILL.md exceeds 500-line progressive disclosure guideline ({line_count} lines); move bulky docs to references/", f"skills/{skill_name}/SKILL.md", severity="LOW")
                frontmatter = parse_frontmatter_keys(content)
                if not frontmatter:
                    rel = os.path.relpath(skill_md, BASE_DIR)
                    res.add_error("PROTOCOL", "Missing required YAML frontmatter block in SKILL.md", rel)
                    continue

                if "core_max_lines" in frontmatter:
                    try:
                        c_max = int(frontmatter["core_max_lines"])
                        rel_skill_path = os.path.relpath(skill_md, BASE_DIR)
                        if line_count > c_max:
                            res.add_error("PROTOCOL", f"Line count ({line_count}) exceeds declared ceiling core_max_lines ({c_max})", rel_skill_path)
                        elif c_max - line_count > 50:
                            res.add_warning("PROTOCOL", f"core_max_lines ceiling ({c_max}) sits >50 lines above actual count ({line_count}). Ratchet ceiling down to {line_count + 10}.", rel_skill_path)
                    except ValueError:
                        pass

                # Check required metadata keys in frontmatter (name, description per docs/skills.md)
                if "name" not in frontmatter or "description" not in frontmatter:
                    res.add_error("PROTOCOL", "Missing essential metadata (name/description)", f"skills/{skill_name}/SKILL.md")
            except Exception as e:
                res.add_error("IO", f"Could not read {skill_md}: {str(e)}")

    # 2. Rules Metadata & Antigravity Engine Limits (docs/rules.md: 24,000 bytes per file, 20,000 tokens defaultRulesBudget)
    RULE_PER_FILE_BYTE_LIMIT = 24000
    DEFAULT_RULES_TOKEN_BUDGET = 20000
    always_on_tokens = 0

    workspace_root = os.path.dirname(BASE_DIR)
    for root_rule_name in ("GEMINI.md", "AGENTS.md"):
        root_rule_path = os.path.join(workspace_root, root_rule_name)
        if os.path.exists(root_rule_path):
            try:
                r_content = read_text(root_rule_path)
                r_bytes = len(r_content.encode("utf-8"))
                if r_bytes > RULE_PER_FILE_BYTE_LIMIT:
                    res.add_error("PROTOCOL", f"Exceeds Antigravity 24,000-byte per-file rule limit ({r_bytes} bytes)", root_rule_name)
                if root_rule_name == "GEMINI.md":
                    always_on_tokens += (len(r_content) + 3) // 4
            except Exception as e:
                res.add_error("IO", f"Could not read {root_rule_name}: {str(e)}")

    if os.path.exists(RULES_DIR):
        for root, _, files in os.walk(RULES_DIR):
            for file in files:
                if not file.endswith(".md"): continue
                res.stats["rules"] += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, RULES_DIR)
                try:
                    content = read_text(filepath)
                    byte_len = len(content.encode("utf-8"))
                    if byte_len > RULE_PER_FILE_BYTE_LIMIT:
                        res.add_error("PROTOCOL", f"Exceeds Antigravity 24,000-byte per-file rule limit ({byte_len} bytes)", rel_path)
                    if file == "RULES_INDEX.md":
                        continue
                    frontmatter = parse_frontmatter_keys(content)
                    if not frontmatter:
                        res.add_warning("PROTOCOL", "Missing YAML frontmatter block.", rel_path)
                        continue

                    has_description = "description" in frontmatter
                    has_activation_or_trigger = "activation" in frontmatter or "trigger" in frontmatter
                    if not has_description or not has_activation_or_trigger:
                        res.add_error("PROTOCOL", "Incomplete YAML header", rel_path)

                    if re.search(r'^(?:activation|trigger):\s*always[_ ]on\b', content, re.MULTILINE | re.IGNORECASE):
                        always_on_tokens += (len(content) + 3) // 4
                except Exception as e:
                    res.add_error("IO", f"Could not read {file}: {str(e)}")

    if always_on_tokens > DEFAULT_RULES_TOKEN_BUDGET:
        res.add_error("PROTOCOL", f"Always-on rules exceed Antigravity 20,000-token defaultRulesBudget ({always_on_tokens} tokens)", "rules/")

    # 3. Canons Count
    if os.path.exists(CANONS_DIR):
        for root, _, files in os.walk(CANONS_DIR):
            for file in files:
                if not file.endswith(".md"): continue
                res.stats["canons"] += 1

def check_ast_blueprint_drift(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR AST BLUEPRINT DRIFT ---")
    candidates = [
        os.path.join(os.path.dirname(BASE_DIR), "context", "00_Strategy", "BLUEPRINT.md"),
        os.path.join(os.path.dirname(BASE_DIR), "context", "BLUEPRINT.md"),
        os.path.join(os.path.dirname(BASE_DIR), "BLUEPRINT.md"),
        os.path.join(BASE_DIR, "BLUEPRINT.md"),
    ]
    blueprint_path = None
    for c in candidates:
        if os.path.exists(c):
            blueprint_path = c
            break
    if not blueprint_path:
        if verbose: print(" [SKIP] BLUEPRINT.md not configured. AST drift check skipped.")
        return
    try:
        content = read_text(blueprint_path)
        if len(content.strip()) < 10:
            res.add_error("DRIFT", "BLUEPRINT.md is virtually empty", blueprint_path)
        else:
            rel_display = os.path.relpath(blueprint_path, os.path.dirname(BASE_DIR)).replace("\\", "/")
            if verbose: print(f" [PASS] Blueprint verified ({rel_display}).")
    except Exception as e:
        res.add_error("IO", f"Could not read BLUEPRINT.md: {str(e)}", blueprint_path)

def check_nano_brain(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR LOCAL AI / NANO BRAIN ---")
    try:
        # Use centralized resolver across Ollama, llama-server, LM Studio, vLLM
        script_dir = os.path.dirname(os.path.abspath(__file__))
        core_dir = os.path.join(os.path.dirname(script_dir), "core")
        import sys
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)

        from capabilities import resolve_local_ai_endpoint
        local_ai = resolve_local_ai_endpoint()
        if local_ai and local_ai.get("base_url"):
            provider_name = local_ai.get("name", local_ai.get("provider", "Local AI"))
            base_url = local_ai.get("base_url")
            if verbose: print(f" [PASS] {provider_name} service detected at {base_url}.")
        else:
            res.add_warning("ENVIRONMENT", "Local AI (Ollama, llama-server, LM Studio, vLLM) not reachable on standard ports (11434, 8080, 1234, 8000). NanoBrain features will be disabled.", severity="LOW")
    except Exception:
        # Fallback: direct probes across 11434, 8080, 1234, 8000
        import urllib.request
        detected = False
        candidates = [
            ("Ollama", "http://127.0.0.1:11434/"),
            ("llama-server", "http://127.0.0.1:8080/health"),
            ("LM Studio", "http://127.0.0.1:1234/v1/models"),
            ("vLLM", "http://127.0.0.1:8000/v1/models"),
        ]
        for name, url in candidates:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=1) as r:
                    if r.status in (200, 404):
                        if verbose: print(f" [PASS] {name} service detected (direct probe).")
                        detected = True
                        break
            except Exception:
                pass
        if not detected:
            res.add_warning("ENVIRONMENT", "Local AI service not reachable. NanoBrain features will be disabled.", severity="LOW")

def check_telemetry_health(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING AGENT TELEMETRY (SQLite) ---")
    db_path = os.path.join(os.path.dirname(BASE_DIR), ".orion", "orion.db")
    if not os.path.exists(db_path):
        if verbose: print(" [NOTE] orion.db not found. Skipping telemetry check.")
        return
        
    try:
        conn = connect_sqlite(db_path)
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

def check_ecosystem_cohesion(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING ECOSYSTEM COHESION (CONTEXT & ORION) ---")
    workspace_root = os.path.dirname(BASE_DIR)
    
    # 1. Context Naming & 4 Lean Pillars check
    context_dir = os.path.join(workspace_root, "context")
    if os.path.exists(context_dir):
        try:
            errs, wrns, out_lines = lint_context(strict=False)
            if errs > 0:
                for line in out_lines:
                    if "[ERROR]" in line:
                        res.add_error("CONTEXT_LINT", line.replace("[ERROR] ", ""), "context/")
            elif wrns > 0:
                for line in out_lines:
                    if "[WARNING]" in line:
                        res.add_warning("CONTEXT_LINT", line.replace("[WARNING] ", ""), "context/", severity="LOW")
            else:
                if verbose: print(" [PASS] Context Naming & 4 Lean Pillars: Compliant (0 errors, 0 warnings).")
        except Exception as e:
            res.add_warning("CONTEXT_LINT", f"Context naming lint failed to run: {e}", severity="LOW")

    orion_db = os.path.join(workspace_root, ".orion", "orion.db")
    if os.path.exists(orion_db):
        try:
            conn = connect_sqlite(orion_db)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('pages', 'pages_fts', 'nodes', 'edges', 'entities', 'relations', 'archival_vectors', 'communities')")
            found_tables = {row[0] for row in c.fetchall()}
            expected = {'pages', 'pages_fts', 'entities', 'relations', 'archival_vectors'}
            if expected.issubset(found_tables):
                c.execute("SELECT COUNT(*) FROM pages")
                page_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM entities")
                ent_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM relations")
                rel_cnt = c.fetchone()[0]
                if verbose: print(f" [PASS] Orion Canonical Graph Database: Healthy ({page_cnt} pages, {ent_cnt} entities, {rel_cnt} relations across FTS5 & graph tables).")
            else:
                res.add_warning("ORION_DB", f"Missing expected Orion tables: {expected - found_tables}", severity="LOW")
            conn.close()
        except Exception as e:
            res.add_warning("ORION_DB", f"Failed to verify orion.db: {e}", severity="LOW")

    # 3. Rule Matrix Freshness
    matrix_dir = os.path.join(workspace_root, ".orion", "matrix")
    if os.path.exists(matrix_dir):
        json_count = len([f for f in os.listdir(matrix_dir) if f.endswith('.json')])
        if json_count > 0:
            if verbose: print(f" [PASS] Compiled Rule Matrices: {json_count} JSON rule matrices active in .orion/matrix/.")
        else:
            res.add_warning("MATRIX", "Matrix directory exists but contains 0 compiled JSON rules. Run 'python .agents/scripts/orion.py compile'.", severity="LOW")

    # 4. Audit Ledger Discovery (Generic / Stack-Agnostic)
    audit_dir = os.path.join(workspace_root, ".orion", "working", "audit")
    if os.path.exists(audit_dir):
        ledgers = [os.path.join(r, f) for r, _, fs in os.walk(audit_dir) for f in fs if f == "00-ledger.md"]
        if ledgers and verbose:
            print(f" [PASS] Project Audit Ledgers: {len(ledgers)} active ledger(s) tracked in .orion/working/audit/.")

    # 5. Semantic Fact-Checking & Anti-Hallucination Gate
    banned_claims = [
        (re.compile(r'\bLightRAG\b', re.IGNORECASE), "Ungrounded reference to 'LightRAG' found. Repo implements independent SQLite graph."),
        (re.compile(r'\bNeuro-Link\b', re.IGNORECASE), "Ungrounded buzzword 'Neuro-Link' found. Use 'Brain & Context Engine'."),
        (re.compile(r'nano_compressor', re.IGNORECASE), "Ghost CLI command 'nano_compressor' referenced. Use 'compress_memory'."),
        (re.compile(r'auto_delegate\.py', re.IGNORECASE), "Ghost script 'auto_delegate.py' referenced."),
        (re.compile(r'commands/evolve\.py', re.IGNORECASE), "Ghost script 'commands/evolve.py' referenced."),
        (re.compile(r'evolve\s+mine-friction', re.IGNORECASE), "Ghost command 'evolve mine-friction' referenced."),
        (re.compile(r'evolve\s+bench', re.IGNORECASE), "Ghost command 'evolve bench' referenced.")
    ]
    fact_violations = []
    docs_dir = os.path.join(BASE_DIR, "docs")
    check_files = ["README.md"]
    if os.path.exists(docs_dir):
        for df in os.listdir(docs_dir):
            if df.endswith(".md"):
                check_files.append(os.path.join("docs", df))

    for check_file in check_files:
        full_check_path = os.path.join(workspace_root if not check_file.startswith("docs") else BASE_DIR, check_file)
        if os.path.exists(full_check_path):
            try:
                txt = read_text(full_check_path)
                for pat, msg in banned_claims:
                    if pat.search(txt):
                        fact_violations.append((check_file, msg))
            except Exception as _e:
                _log_telemetry(_e, 'verify_agents.py:657')
    if fact_violations:
        for f, m in fact_violations:
            res.add_error("FACT_CHECK", f"{m} in {f}", f, severity="HIGH")
    elif verbose:
        print(" [PASS] Semantic Fact-Check: Zero ungrounded buzzwords or ghost CLI commands detected.")

def check_schema_producer_consumer(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING SCHEMA PRODUCER-CONSUMER COHESION ---")
    workspace_root = os.path.dirname(BASE_DIR)
    orion_db = os.path.join(workspace_root, ".orion", "orion.db")
    if not os.path.exists(orion_db):
        return

    try:
        conn = connect_sqlite(orion_db)
        c = conn.cursor()
        c.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        raw_tables = c.fetchall()
        shadow_suffixes = ("_data", "_idx", "_content", "_docsize", "_config")
        tables = []
        for name, sql in raw_tables:
            if name.startswith("sqlite_"):
                continue
            if any(name.endswith(s) for s in shadow_suffixes):
                continue
            if sql and "fts5vocab" in sql.lower():
                continue
            tables.append(name)
        conn.close()
    except Exception as e:
        res.add_warning("SCHEMA_COHESION", f"Could not inspect orion.db tables: {e}", severity="LOW")
        return

    scripts_dir = os.path.join(BASE_DIR, "scripts")
    script_sources = []
    for root, _, files in os.walk(scripts_dir):
        if "__pycache__" in root: continue
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                try:
                    script_sources.append((p, read_text(p)))
                except Exception as _e:
                    _log_telemetry(_e, 'verify_agents.py:692')

    combined_scripts = "\n".join(content for _, content in script_sources)
    disconnected = []
    for tbl in tables:
        write_pat = re.compile(rf'\b(?:INSERT\s+(?:OR\s+[A-Z]+\s+)?INTO|UPDATE|REPLACE\s+INTO)\s+{tbl}\b', re.IGNORECASE)
        read_pat = re.compile(rf'\b(?:FROM|JOIN)\s+{tbl}\b', re.IGNORECASE)
        has_write = bool(write_pat.search(combined_scripts))
        has_read = bool(read_pat.search(combined_scripts))

        if not has_write and not has_read:
            disconnected.append((tbl, "Orphan table: 0 writes, 0 reads across runtime codebase"))
        elif not has_write:
            disconnected.append((tbl, "Consumer without producer: 0 writes detected in runtime codebase"))
        elif not has_read:
            disconnected.append((tbl, "Dead table (Producer without consumer): 0 reads detected in runtime codebase"))

    if disconnected:
        for tbl, msg in disconnected:
            res.add_error("SCHEMA_COHESION", f"Table '{tbl}': {msg}", "orion.db", severity="HIGH")
            if verbose: print(f" [FAIL] Schema Cohesion: Table '{tbl}' -> {msg}")
    elif verbose:
        print(f" [PASS] Schema Producer-Consumer Cohesion: All {len(tables)} active SQLite tables have verified data producers and consumers.")

def check_version_and_router_parity(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING VERSION SYNCHRONIZATION & ROUTER PARITY ---")
    workspace_root = os.path.dirname(BASE_DIR)
    version_file = os.path.join(workspace_root, "VERSION")
    if not os.path.exists(version_file):
        return

    expected_ver = read_text(version_file).strip()
    if not expected_ver:
        return

    version_targets = [
        ("CHANGELOG.md", re.compile(rf'##\s*\[{re.escape(expected_ver)}\]'), f"Release header for [{expected_ver}] in CHANGELOG.md"),
        ("README.md", re.compile(rf'badge/version-v{re.escape(expected_ver)}-blue'), f"Version badge v{expected_ver} in README.md"),
        ("AGENTS.md", re.compile(rf'Mandate Version:\s*{re.escape(expected_ver)}'), f"Mandate Version: {expected_ver} in AGENTS.md"),
        ("GEMINI.md", re.compile(rf'Mandate Version:\s*{re.escape(expected_ver)}'), f"Mandate Version: {expected_ver} in GEMINI.md"),
        (os.path.join(".agents", "templates", "AGENTS.template.md"), re.compile(rf'Mandate Version:\s*{re.escape(expected_ver)}'), f"Mandate Version: {expected_ver} in AGENTS.template.md"),
        (os.path.join(".agents", "docs", "00-intro.md"), re.compile(rf'v{re.escape(expected_ver)}'), f"v{expected_ver} in docs/00-intro.md"),
        (os.path.join(".agents", "DEPLOY_ME.md"), re.compile(rf'Version\*\*:\s*{re.escape(expected_ver)}'), f"Version: {expected_ver} in DEPLOY_ME.md"),
        (os.path.join("context", "AGENT_IDENTITY.md"), re.compile(rf'Foundation\s+v{re.escape(expected_ver)}'), f"Foundation v{expected_ver} in AGENT_IDENTITY.md")
    ]

    mismatches = []
    for rel_path, pat, desc in version_targets:
        full_path = os.path.join(workspace_root, rel_path)
        if os.path.exists(full_path):
            try:
                content = read_text(full_path)
                if not pat.search(content):
                    mismatches.append((rel_path, f"Version drift: Expected {desc}"))
            except Exception as e:
                mismatches.append((rel_path, f"Could not read for version check: {e}"))

    # Check every rule in .agents/rules/*.md for version: expected_ver
    rules_dir = os.path.join(BASE_DIR, "rules")
    if os.path.isdir(rules_dir):
        for r_file in sorted(os.listdir(rules_dir)):
            if r_file.endswith(".md"):
                r_path = os.path.join(rules_dir, r_file)
                rel_r = os.path.relpath(r_path, workspace_root)
                try:
                    r_content = read_text(r_path)
                    ver_match = re.search(r'^version:\s*([^\s\n]+)', r_content, re.MULTILINE)
                    if ver_match:
                        found_v = ver_match.group(1).strip()
                        if found_v != expected_ver:
                            mismatches.append((rel_r, f"Version drift in rule: Expected version: {expected_ver}, found {found_v}"))
                except Exception as e:
                    mismatches.append((rel_r, f"Could not read rule for version check: {e}"))

    if mismatches:
        for f, m in mismatches:
            res.add_error("VERSION_DRIFT", m, f, severity="HIGH")
            if verbose: print(f" [FAIL] {m} ({f})")
    elif verbose:
        print(f" [PASS] Version Synchronization: All entrypoints, rules, and manifests match VERSION ({expected_ver}).")

    # Check JIT Router Table line-by-line parity between AGENTS.md and GEMINI.md
    agents_md = os.path.join(workspace_root, "AGENTS.md")
    gemini_md = os.path.join(workspace_root, "GEMINI.md")
    if os.path.exists(agents_md) and os.path.exists(gemini_md):
        try:
            a_txt = read_text(agents_md)
            g_txt = read_text(gemini_md)
            
            def extract_jit_rows(txt: str) -> List[str]:
                m = re.search(r'## 4\. JIT.*?\| :--- \|\n(.*?)\n## 5\.', txt, re.DOTALL)
                if not m:
                    return []
                return [line.strip() for line in m.group(1).strip().splitlines() if line.strip().startswith('|')]

            a_rows = extract_jit_rows(a_txt)
            g_rows = extract_jit_rows(g_txt)

            if not a_rows or not g_rows or a_rows != g_rows:
                res.add_error("ROUTER_DRIFT", "JIT Routing table in AGENTS.md and GEMINI.md are out of sync", "AGENTS.md / GEMINI.md", severity="HIGH")
                if verbose: print(" [FAIL] JIT Routing table in AGENTS.md and GEMINI.md are out of sync.")
            elif verbose:
                print(f" [PASS] Router Parity: JIT Routing tables in AGENTS.md and GEMINI.md are 100% synchronized ({len(a_rows)} rows).")
        except Exception as e:
            res.add_error("IO", f"Could not read router tables for parity check: {e}")
    elif os.path.exists(agents_md) and verbose:
        print(" [PASS] Router Canonical: AGENTS.md active as single root router.")

check_version_synchronization = check_version_and_router_parity

def check_security_integrity(res: AuditResult, verbose: bool = True, fast_delta: bool = False):
    if verbose: print("\n--- SCANNING FOR SECURITY & AST INTEGRITY ---" + (" [DELTA]" if fast_delta else ""))
    try:
        scripts_dir = os.path.join(BASE_DIR, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        core_dir = os.path.join(scripts_dir, "core")
        if core_dir not in sys.path:
            sys.path.insert(0, core_dir)

        try:
            from core.security import SecurityAuditor
        except ImportError:
            from security import SecurityAuditor  # type: ignore[import-not-found]
        
        auditor = SecurityAuditor(BASE_DIR)
        
        if fast_delta:
            active: List[Dict[str, Any]] = []
            suppressed: List[Dict[str, Any]] = []
            try:
                import subprocess
                diff_out = subprocess.check_output(
                    ["git", "diff", "--name-only", "HEAD"],
                    cwd=BASE_DIR,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stderr=subprocess.DEVNULL
                ).splitlines()
                status_out = subprocess.check_output(
                    ["git", "status", "--porcelain"],
                    cwd=BASE_DIR,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    stderr=subprocess.DEVNULL
                ).splitlines()
                target_files = set(diff_out)
                for line in status_out:
                    if len(line) > 3:
                        path_part = line[3:].strip()
                        if "->" in path_part:
                            path_part = path_part.split("->")[-1].strip()
                        target_files.add(path_part.strip('"'))
                
                ignored_prefixes = ('.orion/', '.git/', '.scratch/', 'scratch/', 'build/', 'dist/', 'node_modules/', '.dart_tool/')
                valid_exts = ('.py', '.md', '.json', '.yaml', '.yml', '.txt', '.js', '.ts', '.tsx', '.jsx', '.dart', '.kt', '.java', '.go', '.rs', '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd')
                for rel_f in target_files:
                    norm_rel = rel_f.replace('\\', '/').lstrip('/')
                    if any(norm_rel.startswith(p) or f'/{p}' in norm_rel for p in ignored_prefixes):
                        continue
                    cand_proj = os.path.join(PROJECT_ROOT, rel_f)
                    fp = rel_f if os.path.isabs(rel_f) else (cand_proj if os.path.isfile(cand_proj) else os.path.join(BASE_DIR, rel_f))
                    if os.path.isfile(fp) and fp.endswith(valid_exts):
                        act, sup = auditor.audit_directory(target_dir=fp)
                        active.extend(act)
                        suppressed.extend(sup)
            except Exception:
                active, suppressed = auditor.audit_directory()
        else:
            active, suppressed = auditor.audit_directory()
        
        if active:
            for item in active:
                msg = f"{item['category']}: {item['message']} (line {item.get('line', '?')})"
                sev = item.get('severity', 'HIGH')
                if sev in ('CRITICAL', 'HIGH'):
                    res.add_error("SECURITY", msg, item.get('file'), severity=sev)
                else:
                    res.add_warning("SECURITY", msg, item.get('file'), severity=sev)
        else:
            if verbose: print(f" [PASS] Security & AST Integrity: 0 vulnerabilities detected ({len(suppressed)} baselined).")
    except Exception as e:
        res.add_warning("SECURITY", f"Security scan encountered error: {e}", severity="LOW")

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
            if any(tok in response.upper() for tok in ["PASS", "YES"]):
                if verbose: print(" [PASS] Semantic Integrity Verified.")
            else:
                if verbose: print(f" [WARNING] NanoBrain flagged potential semantic drift:\n  {response}")
                res.add_warning("SEMANTIC", f"NanoBrain drift warning: {response}", filepath)
        else:
            if verbose: print(" [SKIP] No response from NanoBrain.")
            
    except Exception as e:
        res.add_error("SEMANTIC", f"Semantic check failed: {str(e)}", filepath)

def check_portability_and_hygiene(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR PORTABILITY & HYGIENE LEAKS ---")
    
    # 1. Auto-clean ephemeral bytecode artifacts to prevent git pollution
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".gemini", ".system_generated")]
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            try:
                for sub_f in os.listdir(pycache_dir):
                    if sub_f.endswith((".pyc", ".pyo")):
                        try:
                            os.remove(os.path.join(pycache_dir, sub_f))
                        except OSError:
                            pass
                os.rmdir(pycache_dir)
            except OSError:
                pass

    # 2. Verify zero residual or un-cleanable bytecode leaks
    bytecode_leaks = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".gemini", ".system_generated")]
        if "__pycache__" in dirs:
            bytecode_leaks.append(os.path.join(root, "__pycache__"))
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                bytecode_leaks.append(os.path.join(root, f))
                
    for leak in set(bytecode_leaks):
        rel_leak = os.path.relpath(leak, BASE_DIR).replace("\\", "/")
        res.add_error("HYGIENE", f"Bytecode cache leak detected: {rel_leak}", rel_leak, severity="BLOCKER")
        if verbose: print(f" [FAIL] Hygiene Leak: Bytecode artifact {rel_leak}")

    path_leaks = []
    hygiene_extensions = (".md", ".py", ".json", ".ts", ".js", ".dart", ".yaml", ".yml", ".sh", ".toml")
    excluded_hygiene_dirs = set(EXCLUDED_PATH_MARKERS) | {".orion", ".scratch", "scratch", "dist", "build", ".dart_tool", ".idea"}

    scanned_roots = [BASE_DIR]
    if os.path.isdir(PROJECT_ROOT) and PROJECT_ROOT != BASE_DIR:
        scanned_roots.append(PROJECT_ROOT)

    seen_files = set()
    for s_root in scanned_roots:
        for root, dirs, files in os.walk(s_root):
            dirs[:] = [d for d in dirs if d not in excluded_hygiene_dirs and not any(marker in d for marker in EXCLUDED_PATH_MARKERS)]
            for file_name in files:
                if not file_name.endswith(hygiene_extensions):
                    continue
                filepath = os.path.join(root, file_name)
                norm_path = filepath.replace("\\", "/")
                if filepath in seen_files:
                    continue
                seen_files.add(filepath)

                if "archive" in norm_path.split("/") or os.path.basename(filepath) in ("verify_agents.py", "OBSERVATIONS.md", "OBSERVATIONS.archive.md", "failures.log"):
                    continue
                try:
                    content = read_text(filepath)
                    rel_path = os.path.relpath(filepath, PROJECT_ROOT).replace("\\", "/")
                    if re.search(r'[a-zA-Z]:[\\/]Users[\\/]', content, re.IGNORECASE) or re.search(r'/(?:Users|home)/[a-zA-Z0-9_-]+/', content):
                        path_leaks.append((rel_path, "Hardcoded user machine path"))
                    if "file:///" in content:
                        path_leaks.append((rel_path, "Hardcoded file:/// URI scheme"))
                except Exception as _e:
                    _log_telemetry(_e, 'verify_agents.py:839')
            
    for rel_path, msg in path_leaks:
        res.add_error("HYGIENE", f"{msg} found in {rel_path}", rel_path, severity="BLOCKER")
        if verbose: print(f" [FAIL] Hygiene Leak: {msg} in {rel_path}")
        
    if not path_leaks and not bytecode_leaks and verbose:
        print(" [PASS] Hygiene & Portability: Zero hardcoded machine paths, file:/// schemes, or bytecode leaks.")

def check_encoding_and_io_hygiene(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- SCANNING FOR DEFENSIVE UTF-8 I/O & SUBPROCESS ENCODING ---")
    encoding_violations = []

    # Persistent Verification Cache for AST acceleration
    cache_path = os.path.join(os.path.dirname(BASE_DIR), ".orion", "verify_ast_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as cf:
                cache = json.load(cf)
        except Exception:
            cache = {}
    new_cache = {}

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in (".git", ".gemini", ".system_generated", "node_modules", "__pycache__", "scratch", ".scratch")]
        for file_name in files:
            if not file_name.endswith(".py"):
                continue
            filepath = os.path.join(root, file_name)
            rel_path = os.path.relpath(filepath, BASE_DIR).replace("\\", "/")

            try:
                st = os.stat(filepath)
                sig = f"{st.st_mtime_ns}:{st.st_size}"
                new_cache[rel_path] = sig
                if cache.get(rel_path) == sig:
                    continue  # Verified clean in previous run
            except Exception:
                sig = None

            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    source = f.read()
                tree = ast.parse(source, filename=filepath)
            except Exception as e:
                res.add_error("HYGIENE", f"AST parse error in {rel_path}: {e}", rel_path, severity="HIGH")
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func

                # 1. subprocess calls (run, Popen, check_output, check_call)
                is_subproc = False
                subproc_fn = ""
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                    is_subproc = True
                    subproc_fn = func.attr

                if is_subproc and subproc_fn in ("run", "Popen", "check_output", "check_call"):
                    kw_dict = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                    is_text = False
                    if "text" in kw_dict:
                        val = kw_dict["text"]
                        if isinstance(val, ast.Constant) and val.value is True:
                            is_text = True
                    if "universal_newlines" in kw_dict:
                        val = kw_dict["universal_newlines"]
                        if isinstance(val, ast.Constant) and val.value is True:
                            is_text = True
                    if "capture_output" in kw_dict:
                        val = kw_dict["capture_output"]
                        if isinstance(val, ast.Constant) and val.value is True:
                            is_text = True

                    has_encoding = ("encoding" in kw_dict)

                    if is_text and not has_encoding:
                        encoding_violations.append((
                            rel_path,
                            node.lineno,
                            f"subprocess.{subproc_fn}() text mode missing explicit encoding='utf-8'"
                        ))

                # 2. open() and Path.read_text() / Path.write_text() calls
                is_open = False
                is_path_text_io = False
                if isinstance(func, ast.Name) and func.id == "open":
                    is_open = True
                elif isinstance(func, ast.Attribute) and func.attr == "open" and isinstance(func.value, ast.Name) and func.value.id in ("builtins", "io"):
                    is_open = True
                elif isinstance(func, ast.Attribute) and func.attr in ("read_text", "write_text"):
                    is_path_text_io = True

                if is_open:
                    kw_dict = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                    is_binary = False
                    mode_str = None
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                        mode_str = node.args[1].value
                    elif "mode" in kw_dict and isinstance(kw_dict["mode"], ast.Constant) and isinstance(kw_dict["mode"].value, str):
                        mode_str = kw_dict["mode"].value

                    if mode_str and "b" in mode_str:
                        is_binary = True

                    has_encoding = ("encoding" in kw_dict)

                    if not is_binary and not has_encoding:
                        encoding_violations.append((
                            rel_path,
                            node.lineno,
                            "open() text mode missing explicit encoding='utf-8'"
                        ))
                elif is_path_text_io:
                    kw_dict = {kw.arg: kw.value for kw in node.keywords if kw.arg}
                    if "encoding" not in kw_dict:
                        encoding_violations.append((
                            rel_path,
                            node.lineno,
                            f"Path.{func.attr}() missing explicit encoding='utf-8'"
                        ))

    for rel_path, lineno, msg in encoding_violations:
        res.add_error("HYGIENE", f"{msg} ({rel_path}:{lineno})", rel_path, severity="BLOCKER")
        if verbose: print(f" [FAIL] Defensive I/O Leak: {msg} ({rel_path}:{lineno})")

    if not encoding_violations:
        if new_cache:
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as cf:
                    json.dump(new_cache, cf)
            except Exception:
                pass
        if verbose:
            print(" [PASS] Defensive I/O & Encoding: All text subprocess and open() calls explicitly specify encoding='utf-8'.")

def check_command_parity(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING SKILL JIT ROUTING PARITY ---")
    skills_dir = os.path.join(BASE_DIR, "skills")
    agents_path = os.path.join(os.path.dirname(BASE_DIR), "AGENTS.md")
    gemini_path = os.path.join(os.path.dirname(BASE_DIR), "GEMINI.md")
    instruction_path = agents_path if os.path.exists(agents_path) else gemini_path

    if not os.path.exists(skills_dir):
        return

    skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith(".") and d != "internal"]

    instruction_content = ""
    if os.path.exists(instruction_path):
        instruction_content = read_text(instruction_path)

    missing_routing = []
    for skill in sorted(skills):
        if skill not in instruction_content:
            missing_routing.append(skill)

    if missing_routing:
        for m in missing_routing:
            res.add_warning("PARITY", f"Skill '{m}' is not mapped in {os.path.basename(instruction_path)} JIT routing table", severity="LOW")
            if verbose: print(f" [WARN] JIT Parity: Skill '{m}' not found in {os.path.basename(instruction_path)} JIT table")

    if not missing_routing and verbose:
        print(f" [PASS] Skill JIT Parity: All {len(skills)} domain skills are mapped in {os.path.basename(instruction_path)} JIT routing table.")

    routes_json = os.path.join(os.path.dirname(BASE_DIR), ".orion", "matrix", "skill_routes.json")
    if os.path.exists(routes_json):
        try:
            with open(routes_json, "r", encoding="utf-8") as f:
                compiled_data = json.load(f)
            if isinstance(compiled_data, list):
                route_names = {entry.get("name") for entry in compiled_data if isinstance(entry, dict)}
            elif isinstance(compiled_data, dict):
                route_names = set(compiled_data.get("routes", {}).keys())
            else:
                route_names = set()
            missing_compiled = [s for s in skills if s not in route_names]
            if missing_compiled:
                for m in missing_compiled:
                    res.add_warning("PARITY", f"Skill '{m}' missing from .orion/matrix/skill_routes.json", severity="LOW")
            elif verbose:
                print(f" [PASS] Skill Route Matrix: All {len(skills)} domain skills compiled in .orion/matrix/skill_routes.json.")
        except Exception as e:
            res.add_warning("PARITY", f"Failed to verify skill_routes.json: {e}", severity="LOW")
    else:
        res.add_warning("PARITY", "Missing .orion/matrix/skill_routes.json. Run 'python .agents/scripts/orion.py compile'.", severity="LOW")

    # 3. Master AGENTS_INDEX.md Exhaustiveness & Tier-3 Reference Drift Check
    agents_index_path = os.path.join(BASE_DIR, "AGENTS_INDEX.md")
    if os.path.exists(agents_index_path):
        try:
            index_content = read_text(agents_index_path)
            unindexed_refs = []
            for r_root, _, r_files in os.walk(skills_dir):
                if os.path.basename(r_root) == "references":
                    skill_parent = os.path.basename(os.path.dirname(r_root))
                    if skill_parent == "internal":
                        continue
                    for rf in r_files:
                        if rf.endswith(".md"):
                            rel_ref = os.path.relpath(os.path.join(r_root, rf), os.path.dirname(BASE_DIR)).replace("\\", "/")
                            if rel_ref not in index_content and rf not in index_content:
                                unindexed_refs.append(rel_ref)
            if unindexed_refs:
                for ur in unindexed_refs:
                    res.add_error("INDEX_DRIFT", f"Tier-3 reference file on disk is not registered in AGENTS_INDEX.md: '{ur}'", "AGENTS_INDEX.md", severity="HIGH")
                    if verbose: print(f" [FAIL] AGENTS_INDEX Drift: Unindexed reference '{ur}'")
            elif verbose:
                print(" [PASS] AGENTS_INDEX Reference Parity: All active Tier-3 skill references are registered in AGENTS_INDEX.md.")
        except Exception as e:
            res.add_warning("PARITY", f"Failed to verify AGENTS_INDEX.md reference exhaustiveness: {e}", severity="LOW")


def check_capability_pillars(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING 4-PILLAR CAPABILITY MATRIX ---")
    try:
        scripts_dir = os.path.join(BASE_DIR, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from core.capabilities import probe_capabilities
        caps = probe_capabilities()
        pillars = caps.get("pillars", {})
        p1 = pillars.get("pillar_1", {})
        p2 = pillars.get("pillar_2", {})
        p3 = pillars.get("pillar_3", {})
        p4 = pillars.get("pillar_4", {})
        
        if not p1.get("available", False):
            res.add_error("CAPABILITIES", "Pillar 1 failure: Python 3.10+ / SQLite unavailable.", severity="CRITICAL")
        if sys.version_info < (3, 10):
            res.add_error("CAPABILITIES", "Pillar 1 failure: Python 3.10+ required.", severity="HIGH")
            
        if verbose:
            p2_stat = f"ACTIVE ({p2.get('details', '')})" if p2.get("available") else "FALLBACK (Python ast/stream)"
            p3_stat = f"ACTIVE ({p3.get('details', '')})" if p3.get("available") else "FALLBACK (SQLite FTS5 BM25)"
            p4_stat = f"ACTIVE ({p4.get('details', '')})" if p4.get("available") else "FALLBACK (Host test runner)"
            print(f" [PASS] 4-Pillar Matrix: P1 (Python stdlib) OK | P2 (Rust): {p2_stat} | P3 (Ollama): {p3_stat} | P4 (Bun): {p4_stat}")
    except Exception as e:
        res.add_warning("CAPABILITIES", f"Failed to probe 4-pillar capabilities: {e}", severity="LOW")


def check_cli_dispatcher_integrity(res: AuditResult, verbose: bool = True):
    """Ensure canonical and alias CLI routes point to real scripts."""
    try:
        import importlib.util
        dispatcher_path = os.path.join(BASE_DIR, "scripts", "orion.py")
        spec = importlib.util.spec_from_file_location("orion_dispatcher", dispatcher_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        scripts_dir = os.path.dirname(dispatcher_path)
        documented = read_text(os.path.join(scripts_dir, "SCRIPTS.md"))
        missing = []
        for command, route in {**module.CANONICAL_CMD_MAP, **module.ALIAS_CMD_MAP}.items():
            target = os.path.normpath(os.path.join(scripts_dir, *route))
            if not os.path.isfile(target):
                missing.append(f"{command} -> {target}")
        compact_group = getattr(module, "COMPACT_GROUP", {})
        for command, route in compact_group.items():
            script_parts = route[:2]
            target = os.path.normpath(os.path.join(scripts_dir, *script_parts))
            if not os.path.isfile(target):
                missing.append(f"compact {command} -> {target}")
        undocumented = [
            command for command in module.CANONICAL_CMD_MAP
            if command not in documented
        ]
        for item in missing:
            res.add_error("DISPATCH", f"Missing CLI target: {item}")
        for command in undocumented:
            res.add_warning("DISPATCH", f"Canonical command not documented in SCRIPTS.md: {command}")
        if verbose and not missing and not undocumented:
            print(" [PASS] CLI Dispatcher Integrity: all routes exist and canonical commands are documented.")
    except Exception as exc:
        res.add_error("DISPATCH", f"CLI dispatcher integrity check failed: {exc}")


def check_project_dna_integrity(res: AuditResult, verbose: bool = True):
    """Ensure Project DNA engine sequences cleanly and .dna.json (if present) satisfies canonical schema."""
    if verbose:
        print("\n--- CHECKING PROJECT DNA ENGINE INTEGRITY ---")
    try:
        from core.dna import sequence_project_dna, CANONICAL_5_TIERS
        workspace_root = os.path.dirname(BASE_DIR)
        dna = sequence_project_dna(workspace_root, allow_foundation=True)
        if not dna or not dna.file_tier_map:
            res.add_error("DNA_ENGINE", "sequence_project_dna() returned empty tier map", "core/dna.py")
            return
        invalid_tiers = {t for t in dna.file_tier_map.values() if t not in CANONICAL_5_TIERS}
        if invalid_tiers:
            res.add_error("DNA_ENGINE", f"Invalid DNA tiers emitted: {invalid_tiers}", "core/dna.py")
            return
        if verbose:
            print(f" [PASS] Project DNA Sequencer: {len(dna.file_tier_map)} files sequenced across 5-Tier strata (Compliance: {dna.dna_compliance_score}/100).")
    except Exception as exc:
        res.add_error("DNA_ENGINE", f"Project DNA integrity check failed: {exc}", "core/dna.py")

def check_ecosystem_canon_matrix(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING ECOSYSTEM CANON MATRIX ---")
    ecosystems_dir = os.path.join(BASE_DIR, "canons", "ecosystems")
    if not os.path.exists(ecosystems_dir):
        return

    workspace_root = os.path.dirname(BASE_DIR)
    gemini_path = os.path.join(workspace_root, "GEMINI.md")
    agents_path = os.path.join(workspace_root, "AGENTS.md")
    agents_template_path = os.path.join(BASE_DIR, "templates", "AGENTS.template.md")

    template_canons = set()
    for p in [gemini_path, agents_path, agents_template_path]:
        if os.path.exists(p):
            txt = read_text(p)
            for m in re.findall(r'\{\{FRAMEWORK\}\}-([a-zA-Z0-9_\-]+\.md)', txt):
                template_canons.add(m)

    if not template_canons:
        template_canons = {
            "feature-recipe.md",
            "ui-patterns.md",
            "tests.md",
            "debug.md",
            "release.md",
            "init.md",
            "standards.md"
        }

    # Filter target application frameworks (exclude runtime/tooling canons like ast-grep, bun, obsidian, rtk)
    target_frameworks = {"flutter", "react", "python"}
    discovered_ecosystems = [
        d for d in os.listdir(ecosystems_dir)
        if d in target_frameworks and os.path.isdir(os.path.join(ecosystems_dir, d))
    ]

    missing_matrix_entries = []
    for fw in discovered_ecosystems:
        fw_dir = os.path.join(ecosystems_dir, fw)
        
        eco_json = os.path.join(fw_dir, "ecosystem.json")
        if not os.path.exists(eco_json):
            missing_matrix_entries.append((fw, "ecosystem.json", f"canons/ecosystems/{fw}/ecosystem.json"))

        for tc in template_canons:
            expected_filename = f"{fw}-{tc}"
            expected_file = os.path.join(fw_dir, expected_filename)
            if not os.path.exists(expected_file):
                missing_matrix_entries.append((fw, expected_filename, f"canons/ecosystems/{fw}/{expected_filename}"))

    if missing_matrix_entries:
        for fw, expected_name, rel_path in missing_matrix_entries:
            res.add_error("ECOSYSTEM_MATRIX", f"Framework '{fw}' is missing required JIT canon: {expected_name}", rel_path, severity="HIGH")
            if verbose: print(f" [FAIL] Ecosystem Matrix: Framework '{fw}' lacks {expected_name}")
    elif verbose:
        print(f" [PASS] Ecosystem Canon Matrix: All {len(discovered_ecosystems)} frameworks ({', '.join(discovered_ecosystems)}) satisfy 100% of JIT canonical requirements.")

def check_doc_metrics_sync(res: AuditResult, verbose: bool = True):
    if verbose: print("\n--- CHECKING DOCUMENTATION METRICS SYNCHRONIZATION ---")
    workspace_root = os.path.dirname(BASE_DIR)

    actual_rules = len([
        f for f in os.listdir(RULES_DIR)
        if f.endswith(".md") and f != "RULES_INDEX.md" and not f.startswith(".")
    ]) if os.path.exists(RULES_DIR) else 0

    actual_public_skills = len([
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith(".") and d != "internal"
    ]) if os.path.exists(SKILLS_DIR) else 0

    flutter_dir = os.path.join(CANONS_DIR, "ecosystems", "flutter")
    actual_flutter_canons = len([
        f for f in os.listdir(flutter_dir)
        if not f.startswith(".") and f != ".gitkeep"
    ]) if os.path.exists(flutter_dir) else 0

    templates_dir = os.path.join(BASE_DIR, "templates")
    actual_templates = len([
        f for f in os.listdir(templates_dir)
        if not f.startswith(".") and f != ".gitkeep"
    ]) if os.path.exists(templates_dir) else 0

    actual_tables = 18

    metric_checks = [
        ("docs/00-intro.md", [
            (re.compile(r'\b11\s+Active\s+Standards\b', re.IGNORECASE), f"Claim '11 Active Standards' is stale; actual is {actual_rules}"),
            (re.compile(r'\b11\s+behavioral\s+laws\b', re.IGNORECASE), f"Claim '11 behavioral laws' is stale; actual is {actual_rules}"),
            (re.compile(r'\b31\s+Domain\s+Pillars\b', re.IGNORECASE), f"Claim '31 Domain Pillars' is stale; actual is {actual_public_skills}"),
        ]),
        ("docs/03-local_rag_brain.md", [
            (re.compile(r'\b13\s+cohesive/active\s+tables\b', re.IGNORECASE), f"Claim '13 cohesive/active tables' is stale; actual is {actual_tables}"),
        ]),
        ("docs/04-rule_library___rules.md", [
            (re.compile(r'\b11\s+Active\s+Standards\b', re.IGNORECASE), f"Claim '11 Active Standards' is stale; actual is {actual_rules}"),
        ]),
        ("docs/05-skill___persona___skills.md", [
            (re.compile(r'\b31\s+Skills\b', re.IGNORECASE), f"Claim '31 Skills' is stale; actual is {actual_public_skills}"),
            (re.compile(r'\b22\s+Domain\s+Skills\b', re.IGNORECASE), f"Claim '22 Domain Skills' is stale; should specify 21 Public Domain Skills (+1 Internal)"),
        ]),
        ("docs/08-canons__templates__hooks__evals__and_archives.md", [
            (re.compile(r'flutter/\s*#\s*16\s*canon', re.IGNORECASE), f"Claim '16 canon files' in flutter/ is stale; actual is {actual_flutter_canons}"),
        ]),
        ("README.md", [
            (re.compile(r'\b11\s+behavioral\s+laws\b', re.IGNORECASE), f"Claim '11 behavioral laws' is stale; actual is {actual_rules}"),
            (re.compile(r'\b13\s+behavioral\s+laws\b', re.IGNORECASE), f"Claim '13 behavioral laws' is stale; actual is {actual_rules}"),
            (re.compile(r'\b31\s+Domain\s+Skills\b', re.IGNORECASE), f"Claim '31 Domain Skills' is stale; actual is {actual_public_skills}"),
        ]),
    ]

    metric_violations = []
    for rel_doc, checks in metric_checks:
        doc_path = os.path.join(workspace_root, rel_doc) if not rel_doc.startswith("docs") else os.path.join(BASE_DIR, rel_doc)
        if os.path.exists(doc_path):
            try:
                content = read_text(doc_path)
                for pat, msg in checks:
                    if pat.search(content):
                        metric_violations.append((rel_doc, msg))
            except Exception as e:
                metric_violations.append((rel_doc, f"Could not read for metric sync check: {e}"))

    if metric_violations:
        for doc_file, msg in metric_violations:
            res.add_error("DOC_METRICS_DRIFT", msg, doc_file, severity="HIGH")
            if verbose: print(f" [FAIL] Documentation Metrics Drift: {msg} ({doc_file})")
    elif verbose:
        print(f" [PASS] Documentation Metrics Synchronization: All claims ({actual_rules} rules, {actual_public_skills} skills, {actual_tables} tables, {actual_flutter_canons} flutter canons, {actual_templates} templates) match physical reality.")

def check_operational_ergonomics(res: AuditResult, verbose: bool = True):
    """
    Operational Ergonomics & Storage SLA Gate (Anti-Bloat & Negative Quality Metrics).
    Audits runtime storage footprint, cross-shell portability, and progressive disclosure.
    """
    if verbose: print("\n--- CHECKING OPERATIONAL ERGONOMICS & STORAGE SLA ---")
    workspace_root = os.path.dirname(BASE_DIR)

    # 1. .orion Lean Storage SLA & Redundant Vault Check
    orion_dir = os.path.join(workspace_root, ".orion")
    if os.path.exists(orion_dir):
        file_count = 0
        total_bytes = 0
        for r, dirs, files in os.walk(orion_dir):
            dirs[:] = [d for d in dirs if d not in ("bundles", "export")]
            file_count += len(files)
            for f in files:
                try:
                    total_bytes += os.path.getsize(os.path.join(r, f))
                except OSError:
                    pass

        vault_dir = os.path.join(orion_dir, "vault")
        if os.path.exists(vault_dir):
            vault_files = [f for _, _, fs in os.walk(vault_dir) for f in fs]
            if vault_files:
                res.add_warning(
                    "OPERATIONAL_SLA",
                    f"Redundant vault mirror directory detected at .orion/vault/ ({len(vault_files)} files). Vault exports must target .orion/export/vault/ or be cleaned with 'orion.py gc'.",
                    ".orion/vault",
                    severity="MEDIUM"
                )

        if file_count > 50:
            res.add_warning(
                "OPERATIONAL_SLA",
                f".orion file count ({file_count}) exceeds lean storage threshold (50). Run 'python .agents/scripts/orion.py gc'.",
                ".orion/",
                severity="MEDIUM"
            )
        elif verbose:
            print(f" [PASS] Lean Storage SLA: .orion is compact ({file_count} files, {total_bytes / (1024*1024):.2f} MB, <= 50 file threshold).")
    elif verbose:
        print(" [PASS] Lean Storage SLA: .orion directory not present.")

    # 2. Windows PowerShell Portability in Quickstarts
    readme_path = os.path.join(workspace_root, "README.md")
    if os.path.exists(readme_path):
        try:
            readme_text = read_text(readme_path)
            code_blocks = re.findall(r'```(?:bash|sh|powershell|cmd)?\r?\n(.*?)```', readme_text, re.DOTALL)
            chained_cmd_found = False
            for block in code_blocks:
                for line in block.splitlines():
                    line_s = line.strip()
                    if not line_s.startswith("#") and " && " in line_s and ("git clone" in line_s or "deploy" in line_s):
                        chained_cmd_found = True
                        res.add_warning(
                            "SHELL_PORTABILITY",
                            f"Chained '&&' detected in quickstart command: '{line_s}'. PowerShell does not support '&&' statement separator. Use sequential lines or ';'.",
                            "README.md",
                            severity="MEDIUM"
                        )
            if not chained_cmd_found and verbose:
                print(" [PASS] Shell Portability: README quickstarts are cross-shell compatible (zero Windows PowerShell '&&' statement separator violations).")
        except Exception as _e:
            _log_telemetry(_e, "verify_agents:readme_shell_check")

    # 3. Progressive Disclosure Architecture Mandate
    target_instruction = os.path.join(workspace_root, "GEMINI.md")
    if not os.path.exists(target_instruction):
        target_instruction = os.path.join(workspace_root, "AGENTS.md")
    if os.path.exists(target_instruction):
        try:
            guardrails_text = read_text(target_instruction)
            if "Progressive Disclosure" not in guardrails_text and "Zero Sequential Paging" not in guardrails_text:
                res.add_warning(
                    "PROGRESSIVE_DISCLOSURE",
                    f"{os.path.basename(target_instruction)} missing Antigravity Progressive Disclosure directive. Skills must not mandate upfront recursive reference loading.",
                    os.path.relpath(target_instruction, workspace_root),
                    severity="LOW"
                )
            elif verbose:
                print(f" [PASS] Progressive Disclosure: Antigravity cognitive load guardrails verified in {os.path.basename(target_instruction)}.")
        except Exception as _ge:
            _log_telemetry(_ge, "verify_agents:guardrails_prog_check")

def run_audit(output_json: bool = False, vibe_check_file: Optional[str] = None, fast_delta: bool = False):
    res = AuditResult()
    verbose = not output_json
    
    if verbose: print("--- STARTING AUDIT ---" + (" [FAST DELTA MODE]" if fast_delta else ""))
    
    if not fast_delta:
        check_foundation_sync(res, verbose=verbose)
    check_portability_and_hygiene(res, verbose=verbose)
    check_encoding_and_io_hygiene(res, verbose=verbose)
    check_mechanical_integrity(res, verbose=verbose)
    check_ast_blueprint_drift(res, verbose=verbose)
    if not fast_delta:
        check_links(res, verbose=verbose)
        check_ghost_references(res, verbose=verbose)
        check_protocol_compliance(res, verbose=verbose)
    check_security_integrity(res, verbose=verbose, fast_delta=fast_delta)
    if not fast_delta:
        check_nano_brain(res, verbose=verbose)
    check_telemetry_health(res, verbose=verbose)
    check_ecosystem_cohesion(res, verbose=verbose)
    check_schema_producer_consumer(res, verbose=verbose)
    check_version_synchronization(res, verbose=verbose)
    check_command_parity(res, verbose=verbose)
    if not fast_delta:
        check_capability_pillars(res, verbose=verbose)
    check_cli_dispatcher_integrity(res, verbose=verbose)
    check_project_dna_integrity(res, verbose=verbose)
    check_ecosystem_canon_matrix(res, verbose=verbose)
    check_doc_metrics_sync(res, verbose=verbose)
    check_operational_ergonomics(res, verbose=verbose)
    if verbose: print("\n--- CHECKING INSTRUCTION LANGUAGE LINT (GATE 8) ---")
    try:
        findings = lint_instruction_language(list(DEFAULT_INSTRUCTION_ROOTS))
        for f in findings:
            if f.severity == "ERROR":
                res.add_error(f.rule, f.message, f.path)
            else:
                res.add_warning(f.rule, f.message, f.path, severity="LOW")
        if verbose and not any(f.severity == "ERROR" for f in findings):
            print(f" [PASS] Gate 8 Instruction Language Lint: {len(findings)} informational warning(s), 0 errors.")
    except Exception as _ile:
        _log_telemetry(_ile, "verify_agents:lint_instruction_language")

    
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
            actual_rules = len([
                f for f in os.listdir(RULES_DIR)
                if f.endswith(".md") and f != "RULES_INDEX.md" and not f.startswith(".")
            ]) if os.path.exists(RULES_DIR) else 0
            actual_public_skills = len([
                d for d in os.listdir(SKILLS_DIR)
                if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith(".") and d != "internal"
            ]) if os.path.exists(SKILLS_DIR) else 0
            actual_canons = sum(len(files) for _, _, files in os.walk(CANONS_DIR)) if os.path.exists(CANONS_DIR) else 0
            print("\n--- DUAL-TIER REPOSITORY ARCHITECTURE METRICS ---")
            print(f" Verified Domain Assets : {actual_public_skills} Skills, {actual_rules} Rules, {actual_canons} Canons")
            print("\n[PASS] ALL CHECKS PASSED: Workspace is mechanically sound and protocol compliant.")
        else:
            print(f"\n[FAIL] FAILED: Found {total_errors} integrity/compliance issues.")
            try:
                from commands.reflexion import ObservationLedger
                ledger = ObservationLedger()
                for err in res.errors[:5]:
                    cat = err.get("category", "AUDIT")
                    msg = err.get("message", "audit_error")
                    safe_msg = msg.replace("file:" + "///", "file:[scheme]").replace("\\", "/")
                    safe_msg = re.sub(r'[a-zA-Z]:/[^\s]+', '[path]', safe_msg)
                    target = err.get("file", "verify_agents")
                    ledger.add_observation(
                        title=f"Verify gate failure: {cat} - {safe_msg[:60]}",
                        kind="violation",
                        target=target,
                        rule_id=f"VERIFY_GATE_{cat}",
                        evidence=safe_msg[:200]
                    )
            except Exception:
                pass
    
    sys.exit(1 if len(res.errors) > 0 else 0)


# ==============================================================================
# INSTRUCTION LANGUAGE LINT (Absorbed from instruction_language_lint.py)
# ==============================================================================

DEFAULT_INSTRUCTION_ROOTS = (
    os.path.join(PROJECT_ROOT, ".agents"),
    os.path.join(PROJECT_ROOT, "AGENTS.md"),
    os.path.join(PROJECT_ROOT, "GEMINI.md"),
)
DIRECTIVE_RE = re.compile(
    r"^\s*(?:[-*+]\s+|\d+[.)]\s+|>\s*)?(?:\[[ xX]\]\s+)?(?:\*\*[^*]+\*\*[:\s-]*)?(?:[A-Za-z0-9_-]+\s+){0,4}(?:MUST|SHOULD|MAY|NEVER|ALWAYS|Do not|Do NOT|"
    r"Never|Always|Use|Run|Verify|Ensure|Check|Avoid|Prefer|Ask|Add|Update|Read|Inspect|must|never|always|do not|don't|required|shall)\b"
)
WEAK_MODALITY_RE = re.compile(r"\b(?:should|try to|as needed)\b", re.IGNORECASE)
VAGUE_TERM_RE = re.compile(r"\b(?:appropriate|correctly|cleanly|properly)\b", re.IGNORECASE)
VENDOR_TOOL_RE = re.compile(
    r"\b(?:view_file|read_file|grep_search|replace_file_content|edit_file|StrReplace|run_command|"
    r"invoke_subagent|RequestFeedback)\b"
)
STALE_PHRASES = (
    "Agent-Voluntary",
    "Current hooks.json exposes no post-generation hook",
    "host exposes a post-generation hook",
    "Lessword is default style.",
    "Do NOT claim success without proof",
)
ACTORS = ("Agent", "Host", "Script", "User", "Validator", "Harness")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    message: str
    severity: str


def iter_instruction_markdown_files(root: str) -> Iterable[str]:
    if os.path.isfile(root):
        if root.lower().endswith(".md"):
            yield root
        return
    if not os.path.isdir(root):
        return
    for directory, directories, files in os.walk(root):
        directories[:] = sorted(d for d in directories if d not in {".git", "__pycache__", "archive"})
        for filename in sorted(files):
            if filename.lower().endswith(".md"):
                yield os.path.join(directory, filename)


def relative_instruction_path(path: str) -> str:
    return os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")


def lint_instruction_file(path: str) -> List[Finding]:
    findings: List[Finding] = []
    in_code_fence = False
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except (OSError, UnicodeError) as exc:
        return [Finding(relative_instruction_path(path), 0, "IO", f"Cannot read file: {exc}", "ERROR")]

    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence or not stripped:
            continue

        for phrase in STALE_PHRASES:
            if phrase in raw_line:
                findings.append(
                    Finding(relative_instruction_path(path), line_number, "STALE", f"Replace stale phrase: {phrase}", "ERROR")
                )

        if not DIRECTIVE_RE.search(raw_line):
            continue

        if WEAK_MODALITY_RE.search(raw_line):
            findings.append(
                Finding(
                    relative_instruction_path(path),
                    line_number,
                    "MODALITY",
                    "Use MUST, MAY, or descriptive wording instead of weak directive language.",
                    "WARNING",
                )
            )
        if VAGUE_TERM_RE.search(raw_line):
            findings.append(
                Finding(
                    relative_instruction_path(path),
                    line_number,
                    "VAGUE",
                    "Replace vague quality wording with an observable acceptance criterion.",
                    "WARNING",
                )
            )
        if VENDOR_TOOL_RE.search(raw_line) and not any(actor in raw_line for actor in ACTORS):
            findings.append(
                Finding(
                    relative_instruction_path(path),
                    line_number,
                    "ACTOR",
                    "Name responsible actor or use capability-oriented tool wording.",
                    "WARNING",
                )
            )

    return findings


def lint_instruction_language(roots: Sequence[str]) -> List[Finding]:
    files = sorted({os.path.abspath(path) for root in roots for path in iter_instruction_markdown_files(root)})
    findings: List[Finding] = []
    for path in files:
        findings.extend(lint_instruction_file(path))
    return findings


def main_instruction_lint(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_agents.py instruction-lint",
        description="Audit agent instruction diction for explicit actors, modality, and measurable wording."
    )
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        help="Markdown file or directory to scan; repeatable. Defaults to .agents and runtime adapters.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero for warnings as well as errors.",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[2:])
    roots = args.roots or list(DEFAULT_INSTRUCTION_ROOTS)

    findings = lint_instruction_language(roots)
    errors = [finding for finding in findings if finding.severity == "ERROR"]
    warnings = [finding for finding in findings if finding.severity == "WARNING"]
    for finding in findings:
        print(f"[{finding.severity}] {finding.path}:{finding.line} [{finding.rule}] {finding.message}")

    print(
        f"\nInstruction language lint {'failed' if errors or (args.strict and warnings) else 'passed'}: "
        f"{len(errors)} error(s), {len(warnings)} warning(s)."
    )
    if errors or (args.strict and warnings):
        return 1
    return 0


# ==============================================================================
# PRE-FLIGHT DIAGNOSTICS (Absorbed from preflight_check.py)
# ==============================================================================

def load_valid_skills() -> Set[str]:
    skills_dir = os.path.join(BASE_DIR, 'skills')
    if not os.path.exists(skills_dir):
        return set()
    return {d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))}


def get_all_valid_files() -> Set[str]:
    valid_files = set()
    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR).replace('\\', '/')
            valid_files.add(rel_path)
    return valid_files


def run_preflight() -> int:
    print(" Initiating Pre-Flight Diagnostic (Self-Healing Routing)...")

    from core.capabilities import probe_capabilities
    capabilities = probe_capabilities()
    print("\n [OPTIONAL PILLARS] Capability status:")
    for name in ("rtk", "ast-grep", "ollama", "bun"):
        if name in capabilities:
            status = capabilities[name]
            state = "ACTIVE" if status.get("available") else f"FALLBACK -> {status.get('fallback')}"
            print(f"  {name}: {state}")

    if shutil.which("rtk"):
        print("\n [RTK ANALYTICS] Gathering token savings...")
        try:
            rtk_result = subprocess.run(["rtk", "gain"], capture_output=True, text=True, encoding='utf-8')
            if rtk_result.returncode == 0:
                print(rtk_result.stdout.strip())
        except Exception as e:
            print(f" [RTK INFO] Could not load stats: {e}")

    secrets_scan_script = os.path.join(BASE_DIR, "canons", "global", "harnesses", "secrets_scan_verifier.py")
    if os.path.exists(secrets_scan_script):
        print("\n [SECRETS SCAN] Checking for hardcoded API keys...")
        secrets_result = subprocess.run([sys.executable, secrets_scan_script, "--path", PROJECT_ROOT], capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(secrets_result.stdout.strip())
        if secrets_result.returncode != 0:
            print("\n Pre-Flight Failed: Secrets scan detected hardcoded keys.")
            return 1

    try:
        errors, warnings, output = lint_context(strict=True)
        for line in output:
            print(line)
        if errors != 0:
            print("\n Pre-Flight Failed: context naming lint did not pass.")
            return 1
    except Exception as ex:
        print(f" [WARNING] Context naming lint check skipped: {ex}")

    valid_skills = load_valid_skills()
    valid_filenames = get_all_valid_files()

    scan_dirs = ["skills", "rules", "canons", "templates"]
    files_to_scan = []

    root_agents = os.path.join(PROJECT_ROOT, 'AGENTS.md')
    if os.path.exists(root_agents):
        files_to_scan.append(root_agents)
    root_gemini = os.path.join(PROJECT_ROOT, 'GEMINI.md')
    if os.path.exists(root_gemini) and root_gemini not in files_to_scan:
        files_to_scan.append(root_gemini)

    for d in scan_dirs:
        folder = os.path.join(BASE_DIR, d)
        if not os.path.exists(folder): continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".md"):
                    files_to_scan.append(os.path.join(root, file))

    errors = 0
    warnings = 0

    print("\n Checking OS Prerequisites...")
    missing_tools = []
    for tool in ["node", "rtk", "ollama"]:
        if not shutil.which(tool):
            missing_tools.append(tool)
    if missing_tools:
        print(f"  [WARNING] Missing binaries in PATH: {', '.join(missing_tools)}")
        print("  Check PREREQUISITES.md. Advanced token routing (NanoBrain/RTK) will fail.")
        warnings += len(missing_tools)
    else:
        print("  [OK] Node, RTK, and Ollama found.")

    ignore_list = [
        "README.md", "LICENSE.md", "CONTRIBUTING.md", "example.md", "template.md",
        "BLUEPRINT.md", "MEMORY.md", "ROADMAP.md", "CHANGELOG.md", 
        "ARCHITECTURE.md", "TASK.md", "task-id.md", 
        "SESSION_HANDOFF.md", "PLAN.md", "WALKTHROUGH.md", "LEARNINGS.md"
    ]

    for file_path in files_to_scan:
        rel_src_path = os.path.relpath(file_path, BASE_DIR)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if "GEMINI.md" in rel_src_path or "rules" in rel_src_path:
            potential_skills = re.findall(r'`([a-z0-9]+-[a-z0-9-]+)`', content)
            for ps in set(potential_skills):
                ignore_terms = ["fail-fast", "anti-goals", "no-sweetwords", "high-fidelity", "pre-flight", "session-handoff", "zero-trust", "multi-agent", "front-end", "back-end", "try-catch", "react-window", "game-changer", "cutting-edge", "next-level", "deep-dive", "ast-grep", "nomic-embed-text"]
                if ps not in valid_skills and ps not in ignore_terms and len(ps) > 5:
                    print(f"  [WARNING] Possible broken skill reference '{ps}' in {rel_src_path}")
                    warnings += 1

        md_links = re.findall(r'\]\(([^)]+\.md)\)', content)
        code_path_refs = re.findall(r'`([^`\n]*/[^`\n]*\.md)`', content)
        raw_refs = set(md_links + code_path_refs)

        for ref in raw_refs:
            ref_norm = ref.replace('\\', '/').strip()
            if ref_norm.startswith(("http://", "https://", "file://")):
                continue
            if any(token in ref_norm for token in ["{", "}", "<", ">", "[", "]", "*", "?"]):
                continue

            if ref_norm.startswith('.agents/'):
                candidate = ref_norm.split('.agents/', 1)[1]
            elif ref_norm.startswith(("rules/", "skills/", "canons/", "templates/", "scripts/")):
                candidate = ref_norm
            else:
                continue

            base_name = os.path.basename(candidate)
            if base_name in ignore_list:
                continue
            if candidate not in valid_filenames:
                print(f" [ERROR] Broken file reference '{ref_norm}' in {rel_src_path}")
                errors += 1

        non_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        non_code = re.sub(r'`[^`\n]*`', '', non_code)
        wikilink_pat = re.compile(r'\[\[([a-zA-Z0-9_\-\./\\]+)\]\]')
        for wl in wikilink_pat.findall(non_code):
            wl_clean = wl.strip().replace('\\', '/')
            if wl_clean in ["knowledge", "context", "wikilinks", "page"]: continue
            if not any(vf.endswith(wl_clean) or vf.endswith(wl_clean + '.md') for vf in valid_filenames) and not os.path.exists(os.path.join(BASE_DIR, '..', wl_clean)):
                print(f" [ERROR] Broken wikilink '[[{wl_clean}]]' in {rel_src_path}")
                errors += 1

    if errors > 0:
        print(f"\n Pre-Flight Failed: {errors} broken references, {warnings} warnings.")
        print("ACTION REQUIRED: Fix routing architecture before proceeding.")
        return 1
    else:
        print(f"\n Pre-Flight Passed: Routing architecture is structurally sound ({warnings} warnings).")
        return 0


def main_preflight(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[2:]
    if any(arg in args for arg in ['--pillars', '-p']):
        from core.capabilities import print_pillars_matrix
        print_pillars_matrix()
        return 0
    if any(arg in args for arg in ['--help', '-h']):
        print("Usage: python verify_agents.py preflight [--pillars]")
        print("Runs pre-flight diagnostics: RTK analytics, secrets scan, link validation, or 4-pillar matrix.")
        return 0
    return run_preflight()


# ==============================================================================
# ADVERSARIAL MUTATION ENGINE (Absorbed from adversarial.py)
# ==============================================================================

def command_args(command: str) -> List[str]:
    # Prevent posix mode on Windows from stripping backslashes from paths
    return shlex.split(command, posix=(os.name != "nt"))


def get_diff_changed_lines(file_path: str) -> Optional[Set[int]]:
    try:
        norm_path = os.path.normpath(file_path)
        res = subprocess.run(
            ["git", "diff", "-U0", "HEAD", "--", norm_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5
        )
        output = res.stdout if res.returncode == 0 else ""
        if not output.strip():
            res = subprocess.run(
                ["git", "diff", "-U0", "--", norm_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5
            )
            output = res.stdout if res.returncode == 0 else ""

        if not output.strip():
            return None

        changed_lines: Set[int] = set()
        for line in output.splitlines():
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)(?:,(\d+))?", line)
                if match:
                    start_line = int(match.group(1))
                    count = int(match.group(2)) if match.group(2) is not None else 1
                    for l in range(start_line, start_line + max(count, 1)):
                        changed_lines.add(l)
        return changed_lines
    except Exception as _e:
        _log_telemetry(_e, "get_diff_changed_lines")
        return None


def make_fail_fast_cmd(cmd: str) -> str:
    if not cmd:
        return cmd
    cmd_lower = cmd.lower()
    parts = cmd.split()
    if "pytest" in cmd_lower and "-x" not in parts:
        return f"{cmd} -x"
    if "bun test" in cmd_lower and "--bail" not in parts:
        return f"{cmd} --bail"
    if "flutter test" in cmd_lower and "--fail-fast" not in parts:
        return f"{cmd} --fail-fast"
    return cmd


def _find_ast_grep_bin() -> Optional[str]:
    from core.capabilities import find_ast_grep
    return find_ast_grep()


class AdversarialMutationEngine:
    POLYGLOT_MUTATION_RULES: List[Tuple[str, str, str]] = [
        (r'===', '!==', 'EQUALITY_STRICT_INVERT'),
        (r'!==', '===', 'INEQUALITY_STRICT_INVERT'),
        (r'==', '!=', 'EQUALITY_INVERT'),
        (r'!=', '==', 'INEQUALITY_INVERT'),
        (r'<=', '>', 'RELATIONAL_LTE_TO_GT'),
        (r'>=', '<', 'RELATIONAL_GTE_TO_LT'),
        (r'(?<!<)<(?![=<])', '>=', 'RELATIONAL_LT_TO_GTE'),
        (r'(?<!>)>(?![=>])', '<=', 'RELATIONAL_GT_TO_LTE'),
        (r'\band\b', 'or', 'LOGICAL_AND_TO_OR'),
        (r'\bor\b', 'and', 'LOGICAL_OR_TO_AND'),
        (r'&&', '||', 'LOGICAL_AMP_TO_PIPE'),
        (r'\|\|', '&&', 'LOGICAL_PIPE_TO_AMP'),
        (r'\bTrue\b', 'False', 'BOOL_TRUE_TO_FALSE'),
        (r'\bFalse\b', 'True', 'BOOL_FALSE_TO_TRUE'),
        (r'\btrue\b', 'false', 'BOOL_LOWER_TRUE_TO_FALSE'),
        (r'\bfalse\b', 'true', 'BOOL_LOWER_FALSE_TO_TRUE'),
        (r'\bis\s+None\b', 'is not None', 'NONE_CHECK_INVERT'),
        (r'\bis\s+not\s+None\b', 'is None', 'NOT_NONE_CHECK_INVERT'),
        (r'==\s*null\b', '!= null', 'NULL_EQ_TO_NEQ'),
        (r'!=\s*null\b', '== null', 'NULL_NEQ_TO_EQ'),
        (r'\+\s*1\b', '- 1', 'ARITHMETIC_INC_TO_DEC'),
        (r'-\s*1\b', '+ 1', 'ARITHMETIC_DEC_TO_INC'),
        (r'\breturn\s+True\b', 'return False', 'RETURN_BOOL_TRUE'),
        (r'\breturn\s+False\b', 'return True', 'RETURN_BOOL_FALSE'),
        (r'\breturn\s+true\b', 'return false', 'RETURN_BOOL_LOWER_TRUE'),
        (r'\breturn\s+false\b', 'return true', 'RETURN_BOOL_LOWER_FALSE'),
        (r'\breturn\s+0\b', 'return 1', 'RETURN_ZERO_TO_ONE'),
        (r'\breturn\s+1\b', 'return 0', 'RETURN_ONE_TO_ZERO'),
        (r'\?\?', '?:', 'DART_NULL_COALESCE_TO_ELVIS'),
        (r'\bis!\s+', 'is ', 'DART_IS_NOT_TO_IS'),
        (r'\?\.', '.', 'DART_SAFE_CALL_TO_DIRECT'),
        (r'\?:', '!! ?: ', 'KOTLIN_ELVIS_TO_FORCE'),
        (r'\.unwrap\(\)', '.expect("mutant")', 'RUST_UNWRAP_TO_EXPECT'),
        (r'\.is_some\(\)', '.is_none()', 'RUST_IS_SOME_TO_IS_NONE'),
        (r'\.is_none\(\)', '.is_some()', 'RUST_IS_NONE_TO_IS_SOME'),
        (r'\.is_ok\(\)', '.is_err()', 'RUST_IS_OK_TO_IS_ERR'),
        (r'\.is_err\(\)', '.is_ok()', 'RUST_IS_ERR_TO_IS_OK'),
        (r'\bOk\(', 'Err(', 'RUST_OK_TO_ERR'),
        (r'\bErr\(', 'Ok(', 'RUST_ERR_TO_OK'),
    ]

    def __init__(self, test_cmd: str, target_dir: str = "", target_file: str = ""):
        self.test_cmd = test_cmd.strip()
        self.target_dir = target_dir or (os.path.dirname(target_file) if target_file else ".")
        self.target_file = target_file
        # Auto-detect Bun for JS/TS if default test command or empty
        if self.target_file and any(self.target_file.endswith(ext) for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs")):
            if not self.test_cmd or self.test_cmd in ("npm test", "yarn test", "pnpm test"):
                try:
                    from core.capabilities import BunRuntimeEngine
                    bun = BunRuntimeEngine()
                    avail, _ = bun.is_available()
                    if avail:
                        self.test_cmd = "bun test"
                except Exception as _e:
                    _log_telemetry(_e, "verify_agents:bun_detection")
        self.baseline_duration = 5.0
        self.baseline_verified = False
        self.restore_stale_backups(self.target_dir)

    def restore_stale_backups(self, root_dir: str = "") -> List[str]:
        search_dir = root_dir or self.target_dir or "."
        restored = []
        try:
            if os.path.isfile(search_dir):
                bak = search_dir + ".orion_mut_bak"
                if os.path.exists(bak):
                    shutil.copy2(bak, search_dir)
                    os.remove(bak)
                    restored.append(search_dir)
            elif os.path.isdir(search_dir):
                for root, _, files in os.walk(search_dir):
                    for f in files:
                        if f.endswith(".orion_mut_bak"):
                            bak_path = os.path.join(root, f)
                            orig_path = bak_path[:-14]
                            try:
                                shutil.copy2(bak_path, orig_path)
                                os.remove(bak_path)
                                restored.append(orig_path)
                                sys.stderr.write(f"[ADVERSARIAL] Auto-restored orphaned backup: {orig_path}\n")
                            except Exception as _e:
                                _log_telemetry(_e, f"restore_stale_backup:{bak_path}")
        except Exception as _e:
            _log_telemetry(_e, "restore_stale_backups")
        return restored

    def verify_green_baseline(self) -> bool:
        print("[BASELINE] Running unmodified test suite to establish green baseline...")
        t0 = time.time()
        try:
            proc = subprocess.run(
                command_args(self.test_cmd),
                shell=False,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=60
            )
            duration = time.time() - t0
            self.baseline_duration = max(0.5, duration)

            if proc.returncode != 0:
                sys.stderr.write(
                    f"\n[ADVERSARIAL ERROR] Baseline test suite failed with exit code {proc.returncode}.\n"
                    f"Stdout: {proc.stdout[:400]}\n"
                    f"Stderr: {proc.stderr[:400]}\n"
                    "Mutation testing aborted. Fix test suite before injecting mutants.\n"
                )
                self.baseline_verified = False
                return False

            print(f"[BASELINE] Green baseline verified in {self.baseline_duration:.2f}s (Exit Code 0).")
            self.baseline_verified = True
            return True

        except subprocess.TimeoutExpired:
            sys.stderr.write("[ADVERSARIAL ERROR] Baseline test suite timed out (>60s). Aborting.\n")
            self.baseline_verified = False
            return False
        except Exception as e:
            sys.stderr.write(f"[ADVERSARIAL ERROR] Could not execute baseline test command: {e}\n")
            self.baseline_verified = False
            return False

    def generate_mutations(self, file_path: str, max_mutants: int = 15, diff_only: bool = False) -> List[Dict[str, Any]]:
        if not os.path.isfile(file_path):
            return []

        changed_lines = None
        if diff_only:
            changed_lines = get_diff_changed_lines(file_path)
            if changed_lines is not None and len(changed_lines) == 0:
                print(f"[DIFF-SCOPED] No modified lines detected in git diff for {file_path}. Skipping.")
                return []
            elif changed_lines is not None:
                print(f"[DIFF-SCOPED] Scoping mutations strictly to {len(changed_lines)} modified lines in {os.path.basename(file_path)}.")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            _log_telemetry(e, f"generate_mutations:read:{file_path}")
            return []

        return self.generate_mutations_for_code(content, file_path, max_mutants, changed_lines=changed_lines)

    def generate_mutations_for_code(self, content: str, file_path: str, max_mutants: int = 30, changed_lines: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
        ext = os.path.splitext(file_path)[1].lower()
        mutations: List[Dict[str, Any]] = []

        if ext == ".py":
            py_mutants = self._generate_python_ast_mutations(content, file_path, max_mutants, changed_lines=changed_lines)
            if py_mutants:
                return py_mutants

        lines = content.splitlines(keepends=True)
        str_com_pattern = re.compile(r'//.*$|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
        seen_hashes: Set[int] = set()

        for line_idx, line in enumerate(lines):
            line_no = line_idx + 1
            if changed_lines is not None and line_no not in changed_lines:
                continue

            stripped = line.strip()
            if not stripped or stripped.startswith(('#', '//', '/*', '*', '"""', "'''", '@', 'import ', 'from ')):
                continue

            protected_spans = [m.span() for m in str_com_pattern.finditer(line)]

            for pattern, replacement, rule_id in self.POLYGLOT_MUTATION_RULES:
                try:
                    regex = re.compile(pattern)
                except Exception:
                    continue

                for match in regex.finditer(line):
                    m_start, m_end = match.span()
                    if any(p_start <= m_start and m_end <= p_end for p_start, p_end in protected_spans):
                        continue

                    mutated_line = line[:m_start] + replacement + line[m_end:]
                    mutated_lines = list(lines)
                    mutated_lines[line_idx] = mutated_line
                    mut_content = "".join(mutated_lines)
                    mut_hash = hash(mut_content)
                    if mut_hash in seen_hashes:
                        continue
                    seen_hashes.add(mut_hash)

                    mutations.append({
                        "line_num": line_idx + 1,
                        "rule_id": rule_id,
                        "original_snippet": line.strip(),
                        "mutated_snippet": mutated_line.strip(),
                        "mutation_applied": f"{pattern} -> {replacement}",
                        "mutated_content": mut_content,
                        "file_path": file_path
                    })
                    if len(mutations) >= max_mutants:
                        return mutations

        return mutations

    def _generate_python_ast_mutations(self, content: str, file_path: str, max_mutants: int, changed_lines: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(content, filename=file_path)
        except Exception:
            return []

        mutants: List[Dict[str, Any]] = []
        lines = content.splitlines(keepends=True)

        class CmpReplacer(ast.NodeTransformer):
            def __init__(self, target_lineno: int, target_col: int, op_type: type, new_op: ast.AST):
                self.target_lineno = target_lineno
                self.target_col = target_col
                self.op_type = op_type
                self.new_op = new_op
                self.replaced = False

            def visit_Compare(self, node: ast.Compare):
                new_ops = []
                for op in node.ops:
                    col_match = (self.target_col < 0 or abs(getattr(node, 'col_offset', 0) - self.target_col) <= 8)
                    if isinstance(op, self.op_type) and node.lineno == self.target_lineno and col_match and not self.replaced:
                        new_ops.append(self.new_op)
                        self.replaced = True
                    else:
                        new_ops.append(op)
                node.ops = new_ops
                return node

        class BinOpReplacer(ast.NodeTransformer):
            def __init__(self, target_lineno: int, target_col: int, op_type: type, new_op: ast.AST):
                self.target_lineno = target_lineno
                self.target_col = target_col
                self.op_type = op_type
                self.new_op = new_op
                self.replaced = False

            def visit_BinOp(self, node: ast.BinOp):
                col_match = (self.target_col < 0 or abs(getattr(node, 'col_offset', 0) - self.target_col) <= 8)
                if isinstance(node.op, self.op_type) and node.lineno == self.target_lineno and col_match and not self.replaced:
                    node.op = self.new_op
                    self.replaced = True
                return self.generic_visit(node)

        class UnaryOpReplacer(ast.NodeTransformer):
            def __init__(self, target_lineno: int, target_col: int):
                self.target_lineno = target_lineno
                self.target_col = target_col
                self.replaced = False

            def visit_UnaryOp(self, node: ast.UnaryOp):
                col_match = (self.target_col < 0 or abs(getattr(node, 'col_offset', 0) - self.target_col) <= 8)
                if isinstance(node.op, ast.Not) and node.lineno == self.target_lineno and col_match and not self.replaced:
                    self.replaced = True
                    return node.operand
                return self.generic_visit(node)

        cmp_replacements = [
            (ast.Eq, ast.NotEq(), "==", "!="),
            (ast.NotEq, ast.Eq(), "!=", "=="),
            (ast.Lt, ast.GtE(), "<", ">="),
            (ast.Gt, ast.LtE(), ">", "<="),
            (ast.LtE, ast.Gt(), "<=", ">"),
            (ast.GtE, ast.Lt(), ">=", "<"),
            (ast.Is, ast.IsNot(), "is", "is not"),
            (ast.IsNot, ast.Is(), "is not", "is"),
        ]

        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                if changed_lines is not None and node.lineno not in changed_lines:
                    continue
                for op in node.ops:
                    for old_cls, new_instance, old_sym, new_sym in cmp_replacements:
                        if isinstance(op, old_cls):
                            try:
                                tree_copy = ast.parse(content, filename=file_path)
                                replacer = CmpReplacer(node.lineno, getattr(node, 'col_offset', 0), old_cls, new_instance)
                                modified_tree = replacer.visit(tree_copy)
                                ast.fix_missing_locations(modified_tree)
                                builtins.compile(modified_tree, filename=file_path, mode="exec")
                                mutated_code = ast.unparse(modified_tree)
                                orig_line = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                                mutants.append({
                                    "line_num": node.lineno,
                                    "rule_id": f"AST_CMP_{old_sym}_TO_{new_sym}",
                                    "original_snippet": orig_line,
                                    "mutated_snippet": f"[AST {old_sym} -> {new_sym}] in line {node.lineno}",
                                    "mutation_applied": f"{old_sym} -> {new_sym}",
                                    "mutated_content": mutated_code,
                                    "file_path": file_path
                                })
                                if len(mutants) >= max_mutants:
                                    return mutants
                            except Exception as _e:
                                _log_telemetry(_e, "python_ast_unparse")

        binop_replacements = [
            (ast.Add, ast.Sub(), "+", "-"),
            (ast.Sub, ast.Add(), "-", "+"),
            (ast.Mult, ast.FloorDiv(), "*", "//"),
            (ast.FloorDiv, ast.Mult(), "//", "*"),
        ]

        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if changed_lines is not None and node.lineno not in changed_lines:
                    continue
                for old_cls, new_instance, old_sym, new_sym in binop_replacements:
                    if isinstance(node.op, old_cls):
                        try:
                            tree_copy = ast.parse(content, filename=file_path)
                            replacer = BinOpReplacer(node.lineno, getattr(node, 'col_offset', 0), old_cls, new_instance)
                            modified_tree = replacer.visit(tree_copy)
                            ast.fix_missing_locations(modified_tree)
                            builtins.compile(modified_tree, filename=file_path, mode="exec")
                            mutated_code = ast.unparse(modified_tree)
                            orig_line = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                            mutants.append({
                                "line_num": node.lineno,
                                "rule_id": f"AST_BINOP_{old_sym}_TO_{new_sym}",
                                "original_snippet": orig_line,
                                "mutated_snippet": f"[AST {old_sym} -> {new_sym}] in line {node.lineno}",
                                "mutation_applied": f"{old_sym} -> {new_sym}",
                                "mutated_content": mutated_code,
                                "file_path": file_path
                            })
                            if len(mutants) >= max_mutants:
                                return mutants
                        except Exception as _e:
                            _log_telemetry(_e, "python_ast_binop_unparse")

        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                if changed_lines is not None and node.lineno not in changed_lines:
                    continue
                try:
                    tree_copy = ast.parse(content, filename=file_path)
                    replacer = UnaryOpReplacer(node.lineno, getattr(node, 'col_offset', 0))
                    modified_tree = replacer.visit(tree_copy)
                    ast.fix_missing_locations(modified_tree)
                    builtins.compile(modified_tree, filename=file_path, mode="exec")
                    mutated_code = ast.unparse(modified_tree)
                    orig_line = lines[node.lineno - 1].strip() if node.lineno <= len(lines) else ""
                    mutants.append({
                        "line_num": node.lineno,
                        "rule_id": "AST_UNARY_NOT_INVERT",
                        "original_snippet": orig_line,
                        "mutated_snippet": f"[AST not -> identity] in line {node.lineno}",
                        "mutation_applied": "not x -> x",
                        "mutated_content": mutated_code,
                        "file_path": file_path
                    })
                    if len(mutants) >= max_mutants:
                        return mutants
                except Exception as _e:
                    _log_telemetry(_e, "python_ast_unary_unparse")

        return mutants

    def apply_mutation(self, file_path: str, mutation: Dict[str, Any]) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(mutation["mutated_content"])

    def restore_backup(self, file_path: str) -> None:
        backup_file = file_path + ".orion_mut_bak"
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, file_path)
                os.remove(backup_file)
            except Exception as e:
                _log_telemetry(e, f"restore_backup:{file_path}")

    def run_mutation_cycle(
        self,
        target_file: Optional[str] = None,
        max_mutants: int = 15,
        threshold: float = 80.0,
        diff_only: bool = False,
        fail_fast: bool = True
    ) -> Dict[str, Any]:
        target = target_file or self.target_file
        if not target or not os.path.isfile(target):
            return {
                "status": "ERROR",
                "error": f"Target file not found: {target}",
                "total": 0, "killed": 0, "survived": 0, "timed_out": 0, "score": 0.0, "passed": False
            }

        if not self.verify_green_baseline():
            return {
                "status": "BASELINE_FAILED",
                "error": "Baseline test suite failed on unmodified code.",
                "total": 0, "killed": 0, "survived": 0, "timed_out": 0, "score": 0.0, "passed": False
            }

        mutations = self.generate_mutations(target, max_mutants=max_mutants, diff_only=diff_only)
        if not mutations:
            return {
                "status": "NO_MUTANTS",
                "message": f"No eligible mutation sites found in {target}",
                "total": 0, "killed": 0, "survived": 0, "timed_out": 0, "score": 100.0, "passed": True,
                "mutants": []
            }

        exec_cmd = make_fail_fast_cmd(self.test_cmd) if fail_fast else self.test_cmd

        print(f"\n🧬 Adversarial Mutation Test: {os.path.basename(target)}")
        print(f"Test Command : {exec_cmd}")
        print(f"Mutants      : {len(mutations)} generated (Passing threshold: {threshold}%)\n")

        backup_file = target + ".orion_mut_bak"
        try:
            shutil.copy2(target, backup_file)
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Failed to create atomic backup: {e}",
                "total": 0, "killed": 0, "survived": 0, "timed_out": 0, "score": 0.0, "passed": False
            }

        killed = 0
        survived = 0
        timed_out = 0
        errors = 0
        results = []

        timeout_seconds = max(20.0, 2.5 * self.baseline_duration)
        try:
            for idx, mut in enumerate(mutations, 1):
                self.apply_mutation(target, mut)

                t_start = time.time()
                try:
                    proc = subprocess.run(
                        command_args(exec_cmd),
                        shell=False,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        timeout=timeout_seconds
                    )
                    test_exit = proc.returncode
                    duration = time.time() - t_start

                    if test_exit != 0:
                        killed += 1
                        status = "KILLED"
                    else:
                        survived += 1
                        status = "SURVIVED"

                except subprocess.TimeoutExpired:
                    timed_out += 1
                    status = "TIMED_OUT"
                except Exception as _e:
                    _log_telemetry(_e, "mutation_test_exec")
                    errors += 1
                    status = "ERROR"

                results.append({
                    "mutant_id": idx,
                    "line": mut["line_num"],
                    "rule": mut.get("rule_id", "SYNTACTIC_MUTATION"),
                    "mutation": mut["mutation_applied"],
                    "original": mut["original_snippet"][:60],
                    "mutated": mut["mutated_snippet"][:60],
                    "status": status
                })

                marker = "✓" if status in {"KILLED", "TIMED_OUT"} else "✗"
                print(f"[{marker}] Mutant #{idx:02d} (Line {mut['line_num']:4d}): {status:<9} | {mut['original_snippet'][:35]} -> {mut['mutated_snippet'][:35]}")

        finally:
            self.restore_backup(target)

        total_valid = len(mutations) - errors
        effective_killed = killed + timed_out
        score = (effective_killed / total_valid * 100.0) if total_valid > 0 else 100.0
        passed = score >= threshold

        print("\n" + "=" * 55)
        print(f" Mutation Score: {score:.1f}% ({effective_killed}/{total_valid} killed, {survived} survived)")
        print(f" Status        : {'PASS' if passed else 'FAIL (Weak test coverage)'}")
        print("=" * 55)
        if survived > 0:
            print(f"[WARNING] {survived} mutant(s) survived! Test suite failed to detect logical defects.")

        return {
            "status": "COMPLETED",
            "target": target,
            "total": len(mutations),
            "killed": killed,
            "survived": survived,
            "timed_out": timed_out,
            "errors": errors,
            "score": round(score, 2),
            "threshold": threshold,
            "passed": passed,
            "mutants": results
        }


def load_adversarial_state() -> Dict[str, Any]:
    state_file = os.path.join(PROJECT_ROOT, '.orion', 'working', 'adversarial.json')
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ts = float(data.get("timestamp", 0))
            if ts <= 0:
                ts = os.path.getmtime(state_file)
            if time.time() - ts <= 600:
                return data
            return {}
        except Exception:
            return {}
    return {}


def save_adversarial_state(state: Dict[str, Any]) -> None:
    orion_dir = os.path.join(PROJECT_ROOT, '.orion', 'working')
    state_file = os.path.join(orion_dir, 'adversarial.json')
    if not os.path.exists(orion_dir):
        os.makedirs(orion_dir, exist_ok=True)
    try:
        if "timestamp" not in state:
            state["timestamp"] = time.time()
        from core.db import atomic_write_text
        atomic_write_text(state_file, json.dumps(state, indent=2))
    except Exception as _e:
        _log_telemetry(_e, "save_adversarial_state")


def print_adversarial_banner(msg: str) -> None:
    print("\n========================================")
    print(f" {msg}")
    print("========================================\n")


def main_adversarial(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args and args[0] in ("adversarial", "mutate"):
        if args[0] == "adversarial":
            args = args[1:]
    if not args or (len(args) == 1 and args[0] in ['--help', '-h']):
        print("Usage:")
        print("  python verify_agents.py adversarial <target_file> --test-cmd '<cmd>' [--diff] [--fail-fast] [--threshold 80] [--max-mutants 15]")
        print("  python verify_agents.py adversarial mutate <target_file> --test '<cmd>' [--diff] [--fail-fast]")
        print("  python verify_agents.py adversarial run <test_cmd...>")
        print("  python verify_agents.py adversarial verify <test_cmd...>")
        return 0

    first_arg = args[0].lower()

    if first_arg == "run":
        cmd = args[1:]
        if not cmd:
            print("[ERROR] Please provide a test command to run.")
            return 1
        print(f"[ADVERSARIAL] Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, shell=False)
        exit_code = result.returncode

        state = load_adversarial_state()
        if exit_code == 0:
            print_adversarial_banner("[!] ADVERSARIAL PROTOCOL VIOLATION [!]")
            print("ERROR: Test PASSED (Exit Code 0).")
            print("The Adversarial Twin Protocol requires you to write a FAILING test BEFORE implementation.")
            print("Status: AUTHORIZATION DENIED.")
            return 1
        else:
            print_adversarial_banner("[+] ADVERSARIAL SUCCESS [+]")
            print(f"Test FAILED as expected (Exit Code {exit_code}).")
            print("Status: AUTHORIZATION GRANTED to write implementation.")
            state["test_failed_at"] = time.time()
            state["command"] = " ".join(cmd)
            save_adversarial_state(state)
            return 0

    elif first_arg == "verify":
        cmd = args[1:]
        if not cmd:
            print("[ERROR] Please provide a test command to verify.")
            return 1
        state = load_adversarial_state()
        if "test_failed_at" not in state:
            print_adversarial_banner("[!] ADVERSARIAL PROTOCOL VIOLATION [!]")
            print("ERROR: No failing test was recorded.")
            print("You must first run: `adversarial run <test_cmd>` and prove it fails.")
            return 1

        result = subprocess.run(cmd, shell=False)
        exit_code = result.returncode

        if exit_code > 0:
            print_adversarial_banner("[-] ADVERSARIAL FAILURE [-]")
            print(f"ERROR: Test is still FAILING (Exit Code {exit_code}).")
            return 1
        else:
            print_adversarial_banner("[+] ADVERSARIAL VERIFIED [+]")
            print("Test PASSED (Exit Code 0). Implementation successful.")
            state_file = os.path.join(PROJECT_ROOT, '.orion', 'working', 'adversarial.json')
            if os.path.exists(state_file):
                try:
                    os.remove(state_file)
                except OSError:
                    pass
            return 0

    else:
        target_file = args[1] if first_arg == "mutate" else args[0]
        raw_args = args[2:] if first_arg == "mutate" else args[1:]

        mut_parser = argparse.ArgumentParser(description="Adversarial AST Mutation Testing Engine")
        mut_parser.add_argument("--test", "--test-cmd", dest="test_cmd", required=True, help="Test command to run (or 'auto')")
        mut_parser.add_argument("--runner", choices=["auto", "bun", "host"], default="auto", help="Test execution runner (Pillar 4 Bun or host CLI)")
        mut_parser.add_argument("--max-mutants", type=int, default=15, help="Maximum mutants to generate (default: 15)")
        mut_parser.add_argument("--threshold", type=float, default=80.0, help="Minimum mutation kill score %% (default: 80.0)")
        mut_parser.add_argument("--diff", action="store_true", help="Scope mutations strictly to lines modified in git diff")
        mut_parser.add_argument("--fail-fast", "-x", dest="fail_fast", action="store_true", default=True, help="Stop test on first assertion failure (default: True)")
        mut_parser.add_argument("--json", action="store_true", help="Output JSON report")

        parsed = mut_parser.parse_args(raw_args)

        test_command = parsed.test_cmd
        if (test_command == "auto" or parsed.runner == "bun") and target_file.endswith(('.ts', '.tsx', '.js', '.jsx')):
            try:
                from core.capabilities import BunRuntimeEngine
                bun = BunRuntimeEngine()
                avail, _ = bun.is_available()
                if avail:
                    test_command = f"{bun.bun_bin} test"
            except Exception as _e:
                _log_telemetry(_e, "adversarial:bun_runner_resolve")

        engine = AdversarialMutationEngine(test_command, target_file=target_file)
        res = engine.run_mutation_cycle(
            target_file=target_file,
            max_mutants=parsed.max_mutants,
            threshold=parsed.threshold,
            diff_only=parsed.diff,
            fail_fast=parsed.fail_fast
        )

        if parsed.json:
            print(json.dumps(res, indent=2))

        return 0 if res.get("passed", False) else 1


if __name__ == "__main__":
    raw_args = sys.argv[1:]
    first_arg = raw_args[0].lower() if raw_args else ""

    if first_arg in ("context-lint", "context_lint", "context_naming_lint"):
        sys.exit(main_context_lint(raw_args[1:]))
    elif first_arg in ("instruction-lint", "instruction_lint", "instruction_language_lint"):
        sys.exit(main_instruction_lint(raw_args[1:]))
    elif first_arg in ("preflight", "preflight_check"):
        sys.exit(main_preflight(raw_args[1:]))
    elif first_arg in ("adversarial", "mutate"):
        sys.exit(main_adversarial(raw_args))
    else:
        parser = argparse.ArgumentParser(description="Verify workspace integrity and protocol compliance.")
        parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
        parser.add_argument("--fast", "--delta", action="store_true", help="Fast delta-scoped verification gate for iterative dev.")
        parser.add_argument("--vibe-check", type=str, metavar="FILE", help="Perform a semantic integrity check using NanoBrain on the specified file.")
        filtered_args = [a for a in raw_args if a not in ("verify", "verify_agents")]
        args = parser.parse_args(filtered_args)
        run_audit(output_json=args.json, vibe_check_file=args.vibe_check, fast_delta=args.fast)
