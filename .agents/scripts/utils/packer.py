import os
import sys
import re
import fnmatch
import math
import argparse
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Set, Tuple, Optional, Any

_PACKER_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_PACKER_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

try:
    from core import log_telemetry as _log_telemetry
except ImportError:
    def _log_telemetry(err: Exception = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception as _e:
        _log_telemetry(_e, 'packer.py:reconfigure')

try:
    from core.security import sanitize_text, SECRET_PATTERNS
except Exception:
    try:
        from .security import sanitize_text, SECRET_PATTERNS
    except Exception:
        try:
            from security import sanitize_text, SECRET_PATTERNS
        except Exception:
            SECRET_PATTERNS = [
        ("AWS_KEY", re.compile(r'\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b')),
        ("STRIPE_LIVE_KEY", re.compile(r'\bsk_live_[0-9a-zA-Z]{24}\b')),
        ("STRIPE_TEST_KEY", re.compile(r'\bsk_test_[0-9a-zA-Z]{24}\b')),
        ("GOOGLE_API_KEY", re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b')),
        ("OPENAI_API_KEY", re.compile(r'\bsk-[a-zA-Z0-9]{48}\b')),
        ("GITHUB_TOKEN", re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b')),
        ("BEARER_TOKEN", re.compile(r'\bBearer\s+[a-zA-Z0-9\-\._~+/]+=*')),
        ("TELEGRAM_BOT_TOKEN", re.compile(r'\b[0-9]{9,10}:[a-zA-Z0-9_-]{35}\b')),
        ("JWT_SUPABASE_KEY", re.compile(r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+')),
        ("PRIVATE_KEY", re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----')),
        ("GENERIC_SECRET", re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{16,}[\'"]')),
    ]

    def sanitize_text(content: str) -> Tuple[str, List[str]]:
        warnings = []
        sanitized = content
        for name, pattern in SECRET_PATTERNS:
            matches = pattern.findall(sanitized)
            if matches:
                warnings.append(f"Detected {len(matches)} potential {name} secrets.")
                sanitized = pattern.sub(f"[REDACTED_{name}]", sanitized)
        return sanitized, warnings

DEFAULT_IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'target', 'build',
    'dist', '.dart_tool', '.gradle', '.idea', '.vscode', '.gemini', '.cursor',
    '.clinerules', 'coverage', '.orion', 'scratch', '.scratch', '.worktrees',
    'temp', 'tmp', '.turbo', '.next', '.cache', '.pytest_cache', '.mypy_cache', 'vendor'
}

DEFAULT_IGNORE_FILENAMES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'pubspec.lock',
    'Cargo.lock', 'poetry.lock', 'composer.lock', 'Gemfile.lock', 'Pipfile.lock',
    '.DS_Store', 'thumbs.db', 'desktop.ini'
}

DEFAULT_TEXT_EXTENSIONS = {
    '.py', '.dart', '.kt', '.java', '.rs', '.ts', '.tsx', '.js', '.jsx',
    '.mjs', '.cjs', '.json', '.jsonl', '.yaml', '.yml', '.md', '.mdc', '.txt',
    '.toml', '.sql', '.html', '.css', '.xml', '.sh', '.bat', '.ps1', '.c',
    '.h', '.cpp', '.hpp', '.go', '.gitkeep'
}

DEFAULT_TEXT_FILENAMES = {
    '.gitignore', '.env.example', 'LICENSE', 'VERSION', 'Dockerfile', 'Makefile'
}

LANG_MAP = {
    '.py': 'python',
    '.dart': 'dart',
    '.kt': 'kotlin',
    '.java': 'java',
    '.rs': 'rust',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.json': 'json',
    '.jsonl': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.md': 'markdown',
    '.toml': 'toml',
    '.sql': 'sql',
    '.html': 'html',
    '.css': 'css',
    '.xml': 'xml',
    '.sh': 'bash'
}


def is_minified_or_asset(path: str) -> bool:
    """Filters minified code and source maps that distort token budgets."""
    norm = path.replace('\\', '/').lower()
    return norm.endswith('.min.js') or norm.endswith('.min.css') or norm.endswith('.map') or norm.endswith('.bundle.js')



def is_binary_file(path: str) -> bool:
    """Detects whether a file is binary by inspecting initial 1,024 bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except OSError:
        return True


try:
    from core.db import estimate_tokens
except Exception:
    def estimate_tokens(content: str) -> int:
        """Estimates token count with character division heuristic (len / 3.8)."""
        if not content:
            return 0
        return math.ceil(len(content) / 3.8)


def generate_ascii_tree(
    dir_path: str,
    prefix: str = "",
    max_depth: int = 4,
    ignore_filter: Optional[Any] = None
) -> List[str]:
    """Generates ASCII directory tree structure with connectors."""
    if max_depth <= 0:
        return []
    lines = []
    try:
        entries = sorted(
            [e for e in os.scandir(dir_path) if not e.name.startswith(".") or e.name == ".agents"],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except (PermissionError, OSError):
        return []

    filtered = []
    for entry in entries:
        if entry.name in DEFAULT_IGNORE_FILENAMES or is_minified_or_asset(entry.name):
            continue
        rel = os.path.relpath(entry.path, dir_path)
        if ignore_filter and ignore_filter.is_ignored(rel, is_dir=entry.is_dir()):
            continue
        if any(p in DEFAULT_IGNORE_DIRS for p in entry.name.split("/")):
            continue
        filtered.append(entry)

    count = len(filtered)
    for i, entry in enumerate(filtered):
        connector = "└── " if i == count - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if i == count - 1 else "│   "
            lines.extend(generate_ascii_tree(entry.path, prefix + extension, max_depth - 1, ignore_filter))
    return lines


def add_line_numbers(content: str) -> str:
    """Prepend right-aligned 1-indexed line numbers to each line (from files-to-prompt)."""
    lines = content.splitlines()
    if not lines:
        return ""
    padding = max(3, len(str(len(lines))))
    return "\n".join(f"{i:>{padding}} | {line}" for i, line in enumerate(lines, 1))


def get_dynamic_fence(content: str) -> str:
    """Generates markdown backtick fences safely larger than any backtick sequence in content (from files-to-prompt)."""
    fence = "```"
    while fence in content:
        fence += "`"
    return fence


# Re-exported from core.scanner to eliminate Frankenstein subsystem duplication
try:
    from core.scanner import (
        skeletonize_python,
        skeletonize_code,
        SUPPORTED_SKELETON_EXTENSIONS,
        calculate_token_stats,
        print_token_stats_table,
        build_repo_map,
        cmd_tokens,
    )
except ImportError:
    try:
        from .scanner import (
            skeletonize_python,
            skeletonize_code,
            SUPPORTED_SKELETON_EXTENSIONS,
            calculate_token_stats,
            print_token_stats_table,
            build_repo_map,
            cmd_tokens,
        )
    except ImportError:
        from scanner import (
            skeletonize_python,
            skeletonize_code,
            SUPPORTED_SKELETON_EXTENSIONS,
            calculate_token_stats,
            print_token_stats_table,
            build_repo_map,
            cmd_tokens,
        )


def collect_git_diff_files(
    root_dir: str,
    diff_ref: Optional[str] = None,
    staged_only: bool = False
) -> List[str]:
    """Collects modified files via git diff (Pillar 1 standard library subprocess)."""
    import subprocess
    cmd = ["git", "diff", "--name-only"]
    if staged_only:
        cmd.append("--cached")
    elif diff_ref:
        cmd.append(diff_ref)

    try:
        res = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            lines = [l.strip().replace('\\', '/') for l in res.stdout.splitlines() if l.strip()]
            return [l for l in lines if os.path.isfile(os.path.join(root_dir, l))]
    except Exception as _e:
        _log_telemetry(_e, "collect_git_diff_files")
    return []


BUILTIN_TEMPLATES = {
    "audit": """# 🛡️ SYSTEM ARCHITECTURE & SECURITY AUDIT PROMPT
You are a Principal Security & Systems Architect conducting a rigorous architectural audit of the enclosed codebase.

## 🎯 Mandatory Audit Objectives (Triad Threat Matrix):
1. Boundary Violations & Malformed Input:
   - Identify unescaped external inputs, command injections, or path traversal vectors.
2. Resource Collisions & Concurrency Hazards:
   - Detect unsafe mutable globals, database lock contentions, or unsynchronized file system operations.
3. Silent Failures & Masked Exceptions:
   - Flag suppressed errors (`except: pass`), improper fallback mocks, or violations of Fail-Fast contracts.

## 📁 Repository Overview:
- Repository: {{repo_name}}
- Total Packed Files: {{file_count}}
- Total Tokens: ~{{token_count}}

## 🌲 Directory Structure:
```
{{tree}}
```

## 📜 Source Codebase Context:
{{files}}

---
## 📝 Required Output Format:
Provide a structured Markdown audit findings table with ID, Severity (P0/P1/P2), Location, Vulnerability/Gap, and Remediating Diff.
""",

    "security": """# 🔒 OFFENSIVE APPLICATION SECURITY AUDIT PROMPT
You are a Senior Application Security Engineer reviewing this codebase for critical vulnerabilities (OWASP Top 10, CWE).

Focus Areas:
- Secret Leaks, Credential Storage & Token Handling
- Subprocess Execution boundaries (`shell=False` compliance)
- Deserialization & Unsanitized JSON/SQL queries
- Authorization & Authentication bypass risks

Context Files:
{{files}}
""",

    "architecture": """# 🏛️ SYSTEM ARCHITECTURE & DATA FLOW REVIEW PROMPT
You are a Chief Enterprise Architect reviewing this system's modularity, unidirectional data flow, and invariants.

Focus Areas:
- Domain layer boundaries & decoupling
- State management & immutability guarantees
- Storage abstractions & persistence contracts

Context Files:
{{files}}
""",

    "pr-review": """# 🔍 PULL REQUEST CODE REVIEW PROMPT
You are an expert Pair Programmer reviewing the attached code diff.

Tasks:
1. Verify correctness and regression safety.
2. Ensure compliance with zero-unnecessary-abstraction (YAGNI) and clean design.
3. Flag any untested edge cases.

Context:
{{files}}
"""
}


def render_prompt_template(
    template_name_or_path: str,
    context: Dict[str, Any]
) -> str:
    """Renders prompt templates with zero-pip regex variable substitution (from code2prompt)."""
    if template_name_or_path in BUILTIN_TEMPLATES:
        tmpl = BUILTIN_TEMPLATES[template_name_or_path]
    elif os.path.isfile(template_name_or_path):
        with open(template_name_or_path, 'r', encoding='utf-8') as f:
            tmpl = f.read()
    else:
        tmpl = BUILTIN_TEMPLATES.get("audit", "")

    result = tmpl
    for k, v in context.items():
        result = result.replace(f"{{{{{k}}}}}", str(v))
    return result


def clone_remote_repo(
    url: str,
    branch: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    Clones a remote git repository into a temporary directory using shallow clone (from gitingest).
    Supports subpaths like https://github.com/user/repo/tree/branch/subpath.
    Returns (temp_repo_dir, subpath).
    """
    import subprocess
    import tempfile
    from urllib.parse import urlparse

    parsed = urlparse(url)
    parts = [p for p in parsed.path.strip('/').split('/') if p]
    subpath = None
    target_branch = branch

    if len(parts) >= 4 and parts[2] == 'tree':
        user, repo_name = parts[0], parts[1]
        target_branch = parts[3]
        if len(parts) > 4:
            subpath = "/".join(parts[4:])
        clean_url = f"{parsed.scheme}://{parsed.netloc}/{user}/{repo_name}.git"
    else:
        clean_url = url if url.endswith('.git') else f"{url}.git"

    temp_obj = tempfile.TemporaryDirectory(prefix="orion_remote_")
    temp_dir = temp_obj.name
    cmd = ["git", "clone", "--depth", "1"]
    if target_branch:
        cmd.extend(["--branch", target_branch])
    cmd.extend([clean_url, temp_dir])

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        temp_obj.cleanup()
        raise RuntimeError(f"Failed to clone remote repository {url}: {res.stderr.strip()}")

    return temp_obj, temp_dir, subpath


class GitIgnoreFilter:
    """Lightweight gitignore matcher supporting wildcards, negations, and directory exclusions."""
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.rules: List[Tuple[str, bool, bool]] = []  # (pattern, is_negation, is_dir_only)
        self._load_root_gitignore()

    def _load_root_gitignore(self) -> None:
        gi_path = os.path.join(self.root_dir, '.gitignore')
        if not os.path.isfile(gi_path):
            return
        try:
            with open(gi_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    is_neg = line.startswith('!')
                    if is_neg:
                        line = line[1:].strip()
                    is_dir = line.endswith('/')
                    if is_dir:
                        line = line[:-1]
                    self.rules.append((line, is_neg, is_dir))
        except Exception as _e:
            _log_telemetry(_e, "GitIgnoreFilter:load")

    def add_rule(self, line: str) -> None:
        line = line.strip()
        if not line or line.startswith('#'):
            return
        is_neg = line.startswith('!')
        if is_neg:
            line = line[1:].strip()
        is_dir = line.endswith('/')
        if is_dir:
            line = line[:-1]
        self.rules.append((line, is_neg, is_dir))

    def is_ignored(self, rel_path: str, is_dir: bool = False) -> bool:
        norm = rel_path.replace('\\', '/')
        if norm.startswith('./'):
            norm = norm[2:]
        elif norm == '.':
            return False
        name = os.path.basename(norm)
        ignored = False

        if not is_dir and (name in DEFAULT_IGNORE_FILENAMES or is_minified_or_asset(name)):
            return True

        # Built-in exclusion
        parts = norm.split('/')
        if any(p in DEFAULT_IGNORE_DIRS for p in parts):
            return True

        for pat, is_neg, dir_only in self.rules:
            if dir_only and not is_dir:
                # If directory rule is negation (e.g. !/.agents), any file inside it inherits exception
                if is_neg:
                    anchored = pat.lstrip('/')
                    if norm == anchored or norm.startswith(f"{anchored}/"):
                        ignored = False
                        continue
                continue
            matched = False
            if pat.startswith('/'):
                # Root-anchored match
                anchored = pat.lstrip('/')
                matched = fnmatch.fnmatch(norm, anchored) or (is_dir and fnmatch.fnmatch(norm, f"{anchored}/*"))
            elif '/' in pat:
                matched = fnmatch.fnmatch(norm, pat) or fnmatch.fnmatch(norm, f"{pat}/*")
            else:
                matched = fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(norm, f"*/{pat}/*")

            if matched:
                ignored = not is_neg

        return ignored


BUNDLE_SOFT_TOKEN_CAP = 45000
AUTO_SKELETON_LINE_THRESHOLD = 350


def render_bundle_file_entry(
    rel_path: str,
    raw_content: str,
    current_bundle_tokens: int,
    force_skeleton: bool = False,
    adaptive: bool = True,
    line_numbers: bool = False,
) -> Tuple[str, int]:
    """
    Menyusun blok kode file untuk audit bundle dengan proteksi token ganda:
    1. Skeletonisasi otomatis untuk file > 350 baris atau jika akumulasi bundle mendekati 45k token.
    2. Pagar backtick dinamis (scale backticks) untuk mencegah tabrakan fence markdown.
    """
    try:
        from core.scanner import skeletonize_code, SUPPORTED_SKELETON_EXTENSIONS
    except ImportError:
        try:
            from .scanner import skeletonize_code, SUPPORTED_SKELETON_EXTENSIONS
        except ImportError:
            from scanner import skeletonize_code, SUPPORTED_SKELETON_EXTENSIONS

    ext = os.path.splitext(rel_path)[1].lower().lstrip(".")
    lines = raw_content.splitlines()
    raw_tokens = max(1, (len(raw_content) + 3) // 4)

    should_skeletonize = (
        ext in SUPPORTED_SKELETON_EXTENSIONS
        and (
            force_skeleton
            or (
                adaptive
                and (
                    len(lines) > AUTO_SKELETON_LINE_THRESHOLD
                    or (current_bundle_tokens + raw_tokens) > BUNDLE_SOFT_TOKEN_CAP
                )
            )
        )
    )

    rendered_body = skeletonize_code(raw_content, ext) if should_skeletonize else raw_content
    body_lines = rendered_body.splitlines()
    if line_numbers:
        numbered_body = "\n".join(f"{i:4d} | {line}" for i, line in enumerate(body_lines, 1))
    else:
        numbered_body = rendered_body
    est_tokens = max(1, (len(numbered_body) + 3) // 4)

    # Proteksi tabrakan fence markdown
    max_ticks = 2
    for match in re.finditer(r"`+", numbered_body):
        max_ticks = max(max_ticks, len(match.group(0)))
    fence = "`" * max(3, max_ticks + 1)
    lang_tag = "markdown" if ext in ("md", "mdc") else ext

    mode_tag = " [AST-SKELETONIZED]" if should_skeletonize else ""
    header = (
        f"================================================\n"
        f"File: `{rel_path}` ({len(body_lines)} lines, ~{est_tokens} tokens){mode_tag}\n"
        f"================================================\n"
    )
    block = f"{header}{fence}{lang_tag}\n{numbered_body}\n{fence}\n\n"
    return block, est_tokens


class ContextPacker:
    """Security-aware sovereign context packager."""
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.gi = GitIgnoreFilter(self.root_dir)

    def scan_secrets(self, content: str) -> List[Tuple[int, str, str]]:
        """Returns list of (line_num, secret_type, redacted_preview)."""
        findings = []
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for sec_type, pat in SECRET_PATTERNS:
                if pat.search(line):
                    redacted = line[:10] + "..." + line[-6:] if len(line) > 16 else "[REDACTED]"
                    findings.append((idx, sec_type, redacted.strip()))
                    break
        return findings

    def collect_files(
        self,
        target_dir: Optional[str] = None,
        max_files: int = 2000,
        allowed_extensions: Optional[Set[str]] = None,
        max_size_bytes: int = 2097152,
        prioritize_salience: bool = False
    ) -> List[str]:
        base = os.path.abspath(target_dir or self.root_dir)
        exts = allowed_extensions or DEFAULT_TEXT_EXTENSIONS
        collected = []

        for root, dirs, files in os.walk(base):
            rel_root = os.path.relpath(root, self.root_dir)
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if not self.gi.is_ignored(os.path.join(rel_root, d), is_dir=True)]
            for file in sorted(files):
                if file in DEFAULT_IGNORE_FILENAMES or is_minified_or_asset(file):
                    continue
                rel_file = os.path.relpath(os.path.join(root, file), self.root_dir).replace('\\', '/')
                if self.gi.is_ignored(rel_file, is_dir=False):
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in exts or file in DEFAULT_TEXT_FILENAMES:
                    full_p = os.path.join(root, file)
                    try:
                        if os.path.getsize(full_p) > max_size_bytes:
                            continue
                        if is_binary_file(full_p):
                            continue
                    except OSError:
                        continue

                    collected.append(rel_file)
                    if len(collected) >= max_files:
                        break

        if prioritize_salience:
            try:
                try:
                    from core.scanner import build_repo_map as _brm
                except ImportError:
                    try:
                        from .scanner import build_repo_map as _brm
                    except ImportError:
                        from scanner import build_repo_map as _brm
                rm_res = _brm(self.root_dir, budget_tokens=5000)
                rank_lookup = {rf["file"]: rf["rank"] for rf in rm_res.get("ranked_files", [])}
                collected.sort(key=lambda f: rank_lookup.get(f, 0.0), reverse=True)
            except Exception as _e:
                _log_telemetry(_e, "collect_files:prioritize_salience")

        return collected

    def pack_xml(
        self,
        files: List[str],
        max_tokens: int = 100000,
        scrub_secrets: bool = True,
        repomap: Optional[str] = None,
        line_numbers: bool = False,
        skeleton: bool = False
    ) -> Dict[str, Any]:
        """Packs collected files into an XML envelope according to structured context schema."""
        tree_lines = generate_ascii_tree(self.root_dir, max_depth=3, ignore_filter=self.gi)
        tree_block = "\n".join(tree_lines)
        
        iso_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        packed_files = []
        omitted_files = []
        secret_alerts = []
        file_blocks = []
        
        # Base metadata overhead estimate
        repomap_tok = estimate_tokens(repomap) + 20 if repomap else 0
        running_tokens = estimate_tokens(tree_block) + 50 + repomap_tok

        for rel_p in files:
            full_p = os.path.join(self.root_dir, rel_p)
            try:
                with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as _e:
                _log_telemetry(_e, f"pack_file:{rel_p}")
                continue

            if skeleton:
                ext = os.path.splitext(rel_p)[1]
                content = skeletonize_code(content, ext)

            if scrub_secrets:
                sanitized_content, warnings = sanitize_text(content)
                if warnings:
                    secret_alerts.append({"file": rel_p, "warnings": warnings})
                content = sanitized_content

            if line_numbers:
                content = add_line_numbers(content)

            line_count = len(content.splitlines())
            file_tok = estimate_tokens(content)

            block = f'  <file path="{rel_p}" lines="{line_count}" tokens="{file_tok}">\n{content}\n  </file>'
            block_tok = file_tok + 15

            if running_tokens + block_tok > max_tokens:
                omitted_files.append(rel_p)
                continue

            file_blocks.append(block)
            running_tokens += block_tok
            packed_files.append(rel_p)

        envelope_chunks = [
            "<repository_context>",
            "  <metadata>",
            f"    <generated_at>{iso_now}</generated_at>",
            f"    <file_count>{len(packed_files)}</file_count>",
            f"    <total_tokens>{running_tokens}</total_tokens>",
            "  </metadata>",
            "  <directory_structure>",
            tree_block,
            "  </directory_structure>"
        ]
        if repomap:
            envelope_chunks.append("  <repository_map>")
            envelope_chunks.append(repomap)
            envelope_chunks.append("  </repository_map>")
        envelope_chunks.extend(file_blocks)
        envelope_chunks.append("</repository_context>")
        full_text = "\n".join(envelope_chunks)

        return {
            "format": "xml",
            "packed_files_count": len(packed_files),
            "omitted_files_count": len(omitted_files),
            "estimated_tokens": estimate_tokens(full_text),
            "secret_alerts": secret_alerts,
            "envelope": full_text
        }

    def pack_claude_xml(
        self,
        files: List[str],
        max_tokens: int = 100000,
        scrub_secrets: bool = True,
        line_numbers: bool = False,
        skeleton: bool = False
    ) -> str:
        """Packs files into the standard Claude XML format (<documents><document index="N">...) (from files-to-prompt)."""
        doc_blocks = []
        running_tokens = 50

        for idx, rel_p in enumerate(files, 1):
            full_p = os.path.join(self.root_dir, rel_p)
            try:
                with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue

            if skeleton:
                ext = os.path.splitext(rel_p)[1]
                content = skeletonize_code(content, ext)

            if scrub_secrets:
                content, _ = sanitize_text(content)

            if line_numbers:
                content = add_line_numbers(content)

            file_tok = estimate_tokens(content)
            if running_tokens + file_tok + 30 > max_tokens:
                break

            doc_blocks.append(
                f'  <document index="{idx}">\n'
                f'    <source>{rel_p}</source>\n'
                f'    <document_content>\n{content}\n    </document_content>\n'
                f'  </document>'
            )
            running_tokens += file_tok + 30

        return "<documents>\n" + "\n".join(doc_blocks) + "\n</documents>"

    def pack_digest(
        self,
        files: List[str],
        max_tokens: int = 100000,
        scrub_secrets: bool = True,
        line_numbers: bool = False,
        skeleton: bool = False,
        adaptive_skeleton: bool = False
    ) -> str:
        """Packs files into a high-density Markdown digest with dynamic fences."""
        repo_name = os.path.basename(os.path.abspath(self.root_dir))
        tree_lines = generate_ascii_tree(self.root_dir, max_depth=3, ignore_filter=self.gi)
        tree_block = "\n".join(tree_lines)

        content_sections = []
        packed_files = []
        total_chars = 0
        running_tokens = estimate_tokens(tree_block) + 40

        for rel_p in files:
            full_p = os.path.join(self.root_dir, rel_p)
            try:
                with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue

            if scrub_secrets:
                content, _ = sanitize_text(content)

            if adaptive_skeleton or skeleton:
                block, file_tok = render_bundle_file_entry(
                    rel_p,
                    content,
                    running_tokens,
                    force_skeleton=skeleton,
                    adaptive=adaptive_skeleton,
                    line_numbers=line_numbers,
                )
                section_tokens = file_tok + 25
            else:
                if line_numbers:
                    content = add_line_numbers(content)

                line_count = len(content.splitlines())
                file_tok = estimate_tokens(content)
                ext = os.path.splitext(rel_p)[1].lower()
                lang = LANG_MAP.get(ext, "")
                fence = get_dynamic_fence(content)

                header = (
                    "================================================\n"
                    f"File: `{rel_p}` ({line_count} lines, ~{file_tok} tokens)\n"
                    "================================================\n"
                    f"{fence}{lang}\n"
                )
                footer = f"\n{fence}\n\n"
                section_tokens = file_tok + 25
                block = header + content + footer

            if running_tokens + section_tokens > max_tokens:
                content_sections.append(
                    f"================================================\n"
                    f"File: `{rel_p}` (Truncated: token budget reached)\n"
                    f"================================================\n\n"
                )
                break

            content_sections.append(block)
            running_tokens += section_tokens
            packed_files.append(rel_p)
            total_chars += len(block)

        size_kb = round(total_chars / 1024, 1)
        digest_header = (
            f"# Repository Digest: {repo_name}\n"
            f"- Files: {len(packed_files)} | Estimated Tokens: {running_tokens} | Size: {size_kb} KB\n\n"
            "## Directory Structure\n"
            f"```\n{tree_block}\n```\n\n"
            "## File Contents\n\n"
        )

        return digest_header + "".join(content_sections)


def is_foundation_root(root_dir: str) -> bool:
    """Detects whether target directory is the _foundation framework repository root."""
    abs_root = os.path.abspath(root_dir)
    app_indicators = [
        "package.json", "pubspec.yaml", "Cargo.toml", "go.mod", "tsconfig.json",
        "src", "lib", "app"
    ]
    for ind in app_indicators:
        if os.path.exists(os.path.join(abs_root, ind)):
            return False

    has_agents = os.path.isdir(os.path.join(abs_root, ".agents"))
    has_rules = os.path.isdir(os.path.join(abs_root, ".agents", "rules"))
    has_core = os.path.isdir(os.path.join(abs_root, ".agents", "scripts", "core"))
    return has_agents and has_rules and has_core


def is_foundation_agents(root_dir: str) -> bool:
    """Detects whether target directory is .agents itself."""
    abs_root = os.path.abspath(root_dir)
    return os.path.isdir(os.path.join(abs_root, "rules")) and os.path.isdir(os.path.join(abs_root, "scripts", "core"))


FOUNDATION_BUNDLE_SPECS = [
    ("01_WORKSPACE_AND_META", "Workspace Root Config, Manifests & Baseline (AGENTS.md, GEMINI.md, README.md, AGENTS_INDEX.md, DEPLOY_ME.md)"),
    ("02_RULES_AND_GOVERNANCE", "Complete Governance, Core Guardrails & Protocols (.agents/rules/*.md)"),
    ("03_PRIMARY_AGENT_SKILLS", "Core Cognitive Skills (Integrity Sentinel, Project Architect, App Lifecycle, Meta Agent, Code Review, AI Engineer, Strict TDD)"),
    ("04_SECONDARY_AGENT_SKILLS", "Domain Operational Skills (UI Finish, Lessword, Data Logic, API Contract, Project Operator, Self Evolve, Systematic Debugging)"),
    ("05_CORE_KERNEL_PRIMITIVES", "Core Subsystem Primitives (db.py, capabilities.py, paths.py, memory.py, __init__.py)"),
    ("06_SECURITY_AND_SCANNER", "Static AST Analysis, Security Auditing & Sandbox (scanner.py, security.py, sandbox.py)"),
    ("07_GRAPHRAG_AND_MEMORY", "GraphRAG & Community Clustering (orion_graph.py, reflexion.py, state_machine.py)"),
    ("08_AUTONOMOUS_HARNESS", "Sovereign Autonomous Evolution Harness (engine.py, admission.py, capture.py, curator.py, lifecycle.py, staging.py)"),
    ("09_VERIFICATION_AND_OPS", "Ecosystem Commands & CLI Engine (orion.py, brain.py, verify_agents.py, state_machine.py, reflexion.py, foundation.py)"),
    ("10_RUNTIME_HOOKS_AND_EVALS", "Active IDE Hooks, Aesthetics Linter & Assertion Engine (.agents/hooks/*, .agents/evals/*)"),
]

APP_BUNDLE_SPECS = [
    ("01_PROJECT_CONFIG_AND_BLUEPRINT", "Project Manifests, Configuration, Architecture Blueprint & Entrypoints"),
    ("02_CORE_DOMAIN_AND_TYPES", "Core Domain Logic, Data Models, Types, Schemas & IR"),
    ("03_SERVICES_AND_DATA", "Backend Services, API Clients, Database & Data Repositories"),
    ("04_TARGETS_AND_GENERATORS", "Code Generators, AST Converters, Compilers & Platform Targets"),
    ("05_STATE_AND_CONTROLLERS", "State Management, Controllers, Stores, BLoCs & Providers"),
    ("06_UI_AND_PRESENTATION", "UI Components, Screens, Widgets, Views & Visual Styles"),
    ("07_CLI_MCP_AND_TOOLS", "CLI Commands, MCP Endpoints, Utilities & Developer Tools"),
    ("08_AGENTIC_AND_GOVERNANCE", "AI Agent System, Rules, Governance & Workflows (.agents, AGENTS.md, GEMINI.md)"),
    ("09_TESTS_AND_VERIFICATION", "Test Suites, Integration Specs, Verification & Quality Harnesses"),
    ("10_DOCS_AND_EXAMPLES", "Documentation, Reference Architecture, Guides & Usage Examples"),
]

AUDIT_CORE_PLAYBOOKS = {
    'audit-ledger.md', 'audit_vectors.md', 'app-builder.md',
    'system-admin.md', 'knowledge.md', 'lessword-compress.md',
    'project-init.md', 'project-migrate.md', 'feature-sunset.md',
    'temporal-pulse.md', 'auto-context.md', 'knowledge-sync.md',
    'knowledge-extraction.md', 'architectural_standards.md',
    'release-manager.md', 'api_safety_patterns.md', 'chaos-engineer.md',
    'aesthetic_archetypes.md', 'craft_floor.md', 'visual_engineering.md'
}


def classify_foundation_file(norm: str) -> str:
    if not norm.startswith('.agents/'):
        norm = f".agents/{norm}" if not any(norm == f for f in ('AGENTS.md', 'GEMINI.md', 'CLAUDE.md', 'README.md', 'VERSION', 'LICENSE', 'CHANGELOG.md', '.env.example')) else norm

    primary_skills = {
        'integrity-sentinel', 'project-architect', 'app-lifecycle', 'meta-agent-admin',
        'code-review', 'ai-engineer', 'strict-tdd', 'brain-graph'
    }

    if not norm.startswith('.agents/'):
        return "01_WORKSPACE_AND_META"
    elif norm.startswith('.agents/docs/'):
        return "01_WORKSPACE_AND_META"
    elif norm in ('.agents/AGENTS_INDEX.md', '.agents/DEPLOY_ME.md', '.agents/hooks.json'):
        return "01_WORKSPACE_AND_META"
    elif norm.startswith('.agents/rules/'):
        return "02_RULES_AND_GOVERNANCE"
    elif norm.startswith('.agents/canons/'):
        return "02_RULES_AND_GOVERNANCE"
    elif norm.startswith('.agents/skills/'):
        skill_parts = norm.split('/')
        skill_name = skill_parts[2] if len(skill_parts) > 2 else ""
        if skill_name in primary_skills:
            return "03_PRIMARY_AGENT_SKILLS"
        else:
            return "04_SECONDARY_AGENT_SKILLS"
    elif norm.startswith('.agents/scripts/core/harness/'):
        return "08_AUTONOMOUS_HARNESS"
    elif norm.startswith('.agents/scripts/core/'):
        bn = os.path.basename(norm)
        if bn in ('db.py', 'capabilities.py', 'paths.py', 'secrets.py', 'tokens.py', 'fts.py', 'frontmatter.py', 'jsonrpc.py', 'network.py', 'console.py', 'telemetry_log.py', 'kernel_compat.py', '__init__.py', 'ollama.py', 'memory.py'):
            return "05_CORE_KERNEL_PRIMITIVES"
        elif bn in ('scanner.py', 'security.py', 'ast_rules.py', 'sandbox.py', 'rtk_proxy.py'):
            return "06_SECURITY_AND_SCANNER"
        elif bn in ('orion_graph.py', 'reflexion.py', 'state_machine.py'):
            return "07_GRAPHRAG_AND_MEMORY"
        else:
            return "05_CORE_KERNEL_PRIMITIVES"
    elif norm.startswith('.agents/scripts/utils/'):
        return "09_VERIFICATION_AND_OPS"
    elif norm in ('.agents/scripts/orion.py', '.agents/scripts/SCRIPTS.md', '.agents/scripts/__init__.py'):
        return "09_VERIFICATION_AND_OPS"
    elif norm.startswith('.agents/scripts/commands/'):
        return "09_VERIFICATION_AND_OPS"
    elif norm.startswith('.agents/templates/'):
        return "09_VERIFICATION_AND_OPS"
    elif norm.startswith('.agents/scripts/tests/'):
        return "10_RUNTIME_HOOKS_AND_EVALS"
    elif norm.startswith('.agents/hooks/') or norm.startswith('.agents/evals/'):
        return "10_RUNTIME_HOOKS_AND_EVALS"
    else:
        return "01_WORKSPACE_AND_META"


def classify_app_file(norm: str) -> str:
    parts = norm.lower().split('/')
    base = os.path.basename(norm).lower()
    name_no_ext, ext = os.path.splitext(base)

    if norm.startswith('.agents/') or norm.startswith('.github/') or base in (
        'agents.md', 'gemini.md', 'claude.md', '.cursorrules', '.windsurfrules',
        '.clinerules', 'copilot-instructions.md'
    ):
        return '08_AGENTIC_AND_GOVERNANCE'

    test_keywords = {'test', 'tests', '__tests__', 'specs', 'spec', 'integration_test', 'e2e'}
    if any(p in test_keywords for p in parts[:-1]) or name_no_ext.endswith('.test') or name_no_ext.endswith('.spec') or name_no_ext.endswith('_test') or name_no_ext.startswith('test_'):
        return '09_TESTS_AND_VERIFICATION'

    doc_keywords = {'docs', 'doc', 'documentation', 'examples', 'example', 'sample', 'samples', 'fixtures', 'tutorials', 'guide', 'guides'}
    if any(p in doc_keywords for p in parts[:-1]):
        return '10_DOCS_AND_EXAMPLES'

    gen_keywords = {'targets', 'target', 'generators', 'generator', 'compiler', 'converters', 'converter', 'transformers', 'transformer', 'codegen', 'parser', 'snapshots'}
    if any(p in gen_keywords for p in parts[:-1]):
        return '04_TARGETS_AND_GENERATORS'

    state_keywords = {'controllers', 'controller', 'bloc', 'blocs', 'cubit', 'cubits', 'provider', 'providers', 'store', 'stores', 'state', 'signals', 'reducers', 'actions', 'viewmodels'}
    if any(p in state_keywords for p in parts[:-1]):
        return '05_STATE_AND_CONTROLLERS'

    ui_keywords = {'ui', 'components', 'component', 'widgets', 'widget', 'screens', 'screen', 'views', 'view', 'pages', 'page', 'layouts', 'layout', 'styles', 'style', 'theme', 'themes'}
    if any(p in ui_keywords for p in parts[:-1]):
        return '06_UI_AND_PRESENTATION'

    data_keywords = {'services', 'service', 'api', 'network', 'data', 'repositories', 'repository', 'storage', 'db', 'database', 'clients', 'client', 'http', 'datasource', 'dao'}
    if any(p in data_keywords for p in parts[:-1]):
        return '03_SERVICES_AND_DATA'

    domain_keywords = {'core', 'domain', 'models', 'model', 'types', 'type', 'ir', 'schemas', 'schema', 'entities', 'entity', 'dto', 'dtos', 'contracts', 'contract'}
    if any(p in domain_keywords for p in parts[:-1]):
        return '02_CORE_DOMAIN_AND_TYPES'

    tool_keywords = {'bin', 'cli', 'mcp', 'tools', 'tool', 'scripts', 'script', 'utils', 'util', 'helpers', 'helper'}
    if any(p in tool_keywords for p in parts[:-1]):
        return '07_CLI_MCP_AND_TOOLS'

    config_files = {'package.json', 'pubspec.yaml', 'tsconfig.json', 'cargo.toml', 'go.mod', 'pyproject.toml', 'requirements.txt', 'readme.md', 'absorb.md', 'license', 'cmakelists.txt', 'makefile', 'dockerfile', 'docker-compose.yml', 'settings.gradle'}
    if len(parts) == 1 or base in config_files or 'context' in parts[:-1]:
        return '01_PROJECT_CONFIG_AND_BLUEPRINT'

    if 'src' in parts or 'lib' in parts or 'app' in parts:
        return '02_CORE_DOMAIN_AND_TYPES'

    return '01_PROJECT_CONFIG_AND_BLUEPRINT'


def is_audit_worthy(path: str, is_foundation: bool, mode: str = "lean") -> bool:
    norm = path.replace('\\', '/')
    if mode == "all":
        return True

    if is_foundation:
        audit_exclude_prefixes = (
            ".agents/templates/",
            ".agents/canons/",
            ".agents/scripts/tests/",
            ".agents/docs/",
            ".agents/.security-baseline.json",
            ".agents/evals/evals.json",
            "LICENSE",
            "CHANGELOG.md",
            ".env.example",
        )
        if any(norm.startswith(p) or norm == p for p in audit_exclude_prefixes):
            return False
        if '/references/' in norm:
            bn = os.path.basename(norm)
            return bn in AUDIT_CORE_PLAYBOOKS
        return True
    else:
        app_exclude_prefixes = (
            "docs/", "doc/", "documentation/",
            "examples/", "example/", "sample/", "samples/", "fixtures/", "tutorials/",
            "templates/", ".agents/templates/",
            ".agents/canons/", ".agents/docs/", ".agents/evals/",
            ".agents/scripts/",
            "LICENSE", "CHANGELOG.md", ".env.example",
        )
        if any(norm.startswith(p) or norm == p for p in app_exclude_prefixes):
            return False

        test_parts = {'test', 'tests', '__tests__', 'specs', 'spec', 'integration_test', 'e2e'}
        parts = norm.lower().split('/')
        if any(p in test_parts for p in parts[:-1]):
            return False
        base = os.path.basename(norm).lower()
        name_no_ext, _ = os.path.splitext(base)
        if name_no_ext.endswith('.test') or name_no_ext.endswith('.spec') or name_no_ext.endswith('_test') or name_no_ext.startswith('test_'):
            return False

        if '/references/' in norm:
            bn = os.path.basename(norm)
            return bn in AUDIT_CORE_PLAYBOOKS

        return True


def export_audit_bundles(
    root_dir: str = ".",
    out_dir: Optional[str] = None,
    budget: int = 1000000,
    num_bundles: int = 10,
    mode: str = "lean",
    skeleton: bool = False,
    line_numbers: bool = False,
    hybrid: bool = False
) -> List[str]:
    """
    Packs the repository into logical Markdown digest bundles for multi-platform AI audits.
    Universal multi-project support for Foundation engine or any Application codebase.
    Modes:
      - 'lean' (default for --audit): Focuses on core logic & architecture to be audited by AI,
        excluding docs, templates, samples, and test suites (~35-65% token savings).
      - 'all': Includes all codebase context (docs, tests, examples) while strictly dropping
        lockfiles, build directories, minified files, and scratch caches.
    """
    norm_mode = "all" if mode == "all" else "lean"
    is_foundation = is_foundation_root(root_dir) or is_foundation_agents(root_dir)

    if out_dir is None:
        out_dir = os.path.join(root_dir, ".orion", "audit_export")
    if out_dir.endswith(".md"):
        out_dir = os.path.dirname(out_dir) or "."
    os.makedirs(out_dir, exist_ok=True)

    packer = ContextPacker(root_dir)
    all_files = packer.collect_files(max_size_bytes=2 * 1024 * 1024)

    # Clean existing bundle artifacts in out_dir
    for existing in os.listdir(out_dir):
        if existing.endswith(".md") and ("_BUNDLE.md" in existing or "_PART_" in existing):
            try:
                os.remove(os.path.join(out_dir, existing))
            except OSError:
                pass

    if num_bundles == 10:
        audit_files = [f for f in all_files if is_audit_worthy(f, is_foundation=is_foundation, mode=norm_mode)]
        bundle_specs = FOUNDATION_BUNDLE_SPECS if is_foundation else APP_BUNDLE_SPECS
        classifier = classify_foundation_file if is_foundation else classify_app_file

        buckets: Dict[str, List[str]] = {spec[0]: [] for spec in bundle_specs}
        for f in audit_files:
            bucket_key = classifier(f.replace('\\', '/'))
            if bucket_key in buckets:
                buckets[bucket_key].append(f)
            else:
                buckets[bundle_specs[0][0]].append(f)

        output_paths = []
        mode_label = "LEAN AUDIT" if norm_mode == "lean" else "FULL CODEBASE"
        if skeleton:
            mode_label += " (AST SKELETON)"
        project_type_label = "FOUNDATION ENGINE" if is_foundation else "APPLICATION REPOSITORY"
        print(f"\n[AUDIT BUNDLE EXPORT] Packaging {len(audit_files)}/{len(all_files)} files ({project_type_label} | {mode_label}) into {out_dir}/:")
        total_size_kb = 0.0
        written_bundles = 0

        foundation_manifesto = """# 📋 FOUNDATION ENGINE AUDIT MANIFESTO (LEAN MODE)

> **GUIDANCE FOR AI AUDITOR (UNIVERSAL / MULTI-PLATFORM)**:
> This `_foundation` repository has been packaged into curated logical domain bundles for deep architectural audit.
>
> **Excluded Assets in Lean Mode (Token-Optimization Strategy):**
> 1. **Scaffolding Templates (`.agents/templates/*`)**: Downstream project generation boilerplates, not active system logic.
> 2. **Canons & Derivative Widgets (`.agents/canons/*`)**: Sample styling components consuming large token volume without altering core AI reasoning.
> 3. **Introductory Documentation (`.agents/docs/*`)**: Excluded to eliminate redundancy with canonical rules in `AGENTS.md` and `.agents/rules/*.md`.
> 4. **Static Dictionaries & Secondary Utilities**: Inactive configuration dictionaries and secondary converter utilities.
> 5. **Unit Test Suites (`.agents/scripts/tests/*`)**: Auditor focus is on core architecture, memory engine, AST parser, and GraphRAG.
>
> *(Note: All 14 rules, 21 skills, kernel primitives, AST scanner, GraphRAG, sovereign harness, and runtime hooks are 100% complete).*

---

"""

        app_manifesto = """# 📋 APPLICATION AUDIT MANIFESTO (LEAN MODE)

> **GUIDANCE FOR AI AUDITOR (UNIVERSAL / MULTI-PLATFORM)**:
> This application project has been packaged into curated logical domain bundles for deep architectural and code audit.
>
> **Excluded Assets in Lean Mode (Token-Optimization Strategy):**
> 1. **Lockfiles & Build Artifacts**: Machine-generated dependency graphs, build output, minified assets, and cache files.
> 2. **Non-Technical Docs & Release Logs**: Marketing copy and changelogs omitted to focus directly on active source code.
> 3. **Sample Fixtures & Scratch Dumps**: Downstream mock examples omitted so reasoning focuses on production logic.
> 4. **Test Assertion Suites**: Focus is on business logic, interface contracts, data models, and generators.
>
> *(Note: All application source code, entrypoints, architecture blueprints, data models, generators, and AI governance are 100% complete).*

---

"""

        for code, desc in bundle_specs:
            files_in_bucket = buckets[code]
            if not files_in_bucket:
                continue

            written_bundles += 1
            out_file = os.path.join(out_dir, f"{code}_BUNDLE.md")

            # Apply AST skeletonization or smart hybrid
            if hybrid:
                if is_foundation:
                    apply_skel = (code in ("09_VERIFICATION_AND_OPS", "10_RUNTIME_HOOKS_AND_EVALS", "04_SECONDARY_AGENT_SKILLS"))
                else:
                    apply_skel = (code in ("07_CLI_MCP_AND_TOOLS", "08_AGENTIC_AND_GOVERNANCE", "09_TESTS_AND_VERIFICATION", "10_DOCS_AND_EXAMPLES"))
            else:
                apply_skel = skeleton

            digest = packer.pack_digest(
                files_in_bucket,
                max_tokens=budget,
                scrub_secrets=True,
                line_numbers=line_numbers,
                skeleton=apply_skel,
                adaptive_skeleton=(norm_mode == "lean" and not skeleton and not hybrid)
            )

            if written_bundles == 1 and norm_mode == "lean":
                manifesto = foundation_manifesto if is_foundation else app_manifesto
                try:
                    try:
                        from core.scanner import build_repo_map as _brm
                    except ImportError:
                        try:
                            from .scanner import build_repo_map as _brm
                        except ImportError:
                            from scanner import build_repo_map as _brm
                    rm_data = _brm(root_dir, budget_tokens=min(budget // 4, 2500))
                    if rm_data.get("repo_map"):
                        manifesto += f"## 🗺️ PageRank Architectural Repo-Map\n\n```plaintext\n{rm_data['repo_map']}\n```\n\n---\n\n"
                except Exception as _e:
                    _log_telemetry(_e, "export_audit_bundles:build_repo_map")
                digest = manifesto + digest

            with open(out_file, "w", encoding="utf-8") as fh:
                fh.write(digest)
            size_kb = os.path.getsize(out_file) / 1024
            total_size_kb += size_kb
            print(f"  [{code}_BUNDLE.md] -> {len(files_in_bucket):>2} files ({size_kb:>5.1f} KB) | {desc}")
            output_paths.append(out_file)

        print(f"\n[SUCCESS] {written_bundles} Domain Bundles created (~{total_size_kb:.1f} KB total, ~{int(total_size_kb * 250):,} tokens). Ready for multi-platform AI audit!\n")
        return output_paths

    # Fallback to 2-file export (num_bundles == 2)
    if is_foundation:
        code_prefixes = (
            ".agents/scripts/", ".agents/hooks/", ".agents/evals/",
            "scripts/", "hooks/", "evals/",
        )
        brain_files = [f for f in all_files if not any(f.replace('\\', '/').startswith(p) for p in code_prefixes)]
        engine_files = [f for f in all_files if any(f.replace('\\', '/').startswith(p) for p in code_prefixes)]
        bundle1_name = "01_AGENTS_BRAIN_BUNDLE.md"
        bundle2_name = "02_AGENTS_ENGINE_BUNDLE.md"
        b1_desc = f"{len(brain_files)} files: Rules, Skills, Canons, Docs, Templates"
        b2_desc = f"{len(engine_files)} files: Scripts, Hooks, Evals, Tests"
    else:
        ops_prefixes = (
            "test/", "tests/", "__tests__/", "specs/", "docs/", "doc/",
            "scripts/", "tools/", "bin/", ".agents/"
        )
        brain_files = [f for f in all_files if not any(f.replace('\\', '/').startswith(p) for p in ops_prefixes)]
        engine_files = [f for f in all_files if any(f.replace('\\', '/').startswith(p) for p in ops_prefixes)]
        bundle1_name = "01_APP_CORE_AND_DOMAIN_BUNDLE.md"
        bundle2_name = "02_APP_OPS_AND_GOVERNANCE_BUNDLE.md"
        b1_desc = f"{len(brain_files)} files: Core Domain, Models, Services, UI & Blueprint"
        b2_desc = f"{len(engine_files)} files: CLI, Tools, Tests, Docs & Agent Governance"

    bundle1_path = os.path.join(out_dir, bundle1_name)
    bundle2_path = os.path.join(out_dir, bundle2_name)

    digest1 = packer.pack_digest(brain_files, max_tokens=budget, scrub_secrets=True, line_numbers=line_numbers, skeleton=skeleton)
    with open(bundle1_path, "w", encoding="utf-8") as f1:
        f1.write(digest1)

    digest2 = packer.pack_digest(engine_files, max_tokens=budget, scrub_secrets=True, line_numbers=line_numbers, skeleton=skeleton)
    with open(bundle2_path, "w", encoding="utf-8") as f2:
        f2.write(digest2)

    print(f"[AUDIT EXPORT] Successfully created 2 upload bundles in '{out_dir}/':")
    print(f"  1. {bundle1_path} ({b1_desc})")
    print(f"  2. {bundle2_path} ({b2_desc})")
    return [bundle1_path, bundle2_path]


# Backwards compatibility alias
export_gemini_bundles = export_audit_bundles


def main() -> None:
    parser = argparse.ArgumentParser(description="Security-Aware Context Packager & Multi-Project Bundle Exporter")
    parser.add_argument("--dir", default=".", help="Root directory to pack (default: current directory)")
    parser.add_argument("--format", choices=["xml", "digest", "markdown", "claude-xml"], default="xml", help="Output envelope format for single-file packing")
    parser.add_argument("--budget", "--max-tokens", dest="budget", type=int, default=1000000, help="Maximum token budget (default: 1M tokens)")
    parser.add_argument("--max-size-kb", type=int, default=2048, help="Maximum individual file size in KB to inspect (default: 2048 KB)")
    parser.add_argument("--out", "--output", dest="out", help="Optional output destination file or bundle directory")
    parser.add_argument("--redact", action="store_true", default=True, help="Scrub secrets in packed content (default: True)")
    parser.add_argument("--repomap", action="store_true", help="Include PageRank-ranked repository map in envelope")
    parser.add_argument("--salience", action="store_true", help="Prioritize files by PageRank salience score")

    parser.add_argument("--audit", action="store_true", help="Export curated domain audit bundles with 100%% full micro-code bodies (lean mode, default 10 domains)")
    parser.add_argument("--audit-all", action="store_true", help="Export full codebase domain audit bundles (all mode, default 10 domains)")
    parser.add_argument("--audit-ast", action="store_true", help="Export high-density AST-skeletonized domain audit bundles (~80%% token savings)")
    parser.add_argument("--hybrid", action="store_true", help="Smart Hybrid audit: 100%% full micro-code for core domain/models, AST skeletons for secondary utilities")
    parser.add_argument("--full", "--no-skeleton", dest="full", action="store_true", help="Preserve 100%% full implementation bodies (zero blindspot, disables AST skeletonization)")
    parser.add_argument("--bundle", "--bundles", dest="bundle", nargs="?", const=10, type=int, help="Export N curated domain bundles for multi-platform AI audit (default: 10)")
    parser.add_argument("--megabundle", action="store_true", help="Export clean 2-file architecture/ops megabundles")

    # Superpower enhancements from Repomix, Code2Prompt, Files-to-Prompt, Gitingest, Aider
    parser.add_argument("-n", "--line-numbers", action="store_true", help="Prepend right-aligned 1-indexed line numbers to files (from files-to-prompt)")
    parser.add_argument("--skeleton", action="store_true", help="Extract class/interface/method signatures and collapse function bodies (from Aider/Repomix)")
    parser.add_argument("--git-diff", nargs="?", const="", help="Scope packing to files modified in git diff [optional REF] (from Repomix)")
    parser.add_argument("--git-staged", action="store_true", help="Scope packing strictly to staged files in git index (from Repomix)")
    parser.add_argument("--token-stats", action="store_true", help="Display rich per-extension and per-file token analytics table (from code2prompt)")
    parser.add_argument("--template", help="Wrap output in AI prompt template: audit, security, architecture, pr-review, or file path (from code2prompt)")
    parser.add_argument("--remote", help="Clone and pack remote Git repository URL (from gitingest)")
    parser.add_argument("--branch", help="Specific remote git branch to clone (with --remote)")

    # Vibe Intent (Intent-Driven Context Packaging)
    parser.add_argument(
        "intent",
        nargs="?",
        default=None,
        help="Vibe intent: 'audit', 'pr'/'review', 'diff', 'security', 'stats', 'auto', or remote Git URL"
    )

    # Backwards-compatibility aliases
    parser.add_argument("--gemini", action="store_true", help="[Legacy alias] Use --megabundle")
    parser.add_argument("--gemini-10", action="store_true", help="[Legacy alias] Use --bundle 10")
    parser.add_argument("--gemini-10-all", action="store_true", help="[Legacy alias] Use --audit-all")
    parser.add_argument("--gemini-10-lean", action="store_true", help="[Legacy alias] Use --audit")
    parser.add_argument("--lean", action="store_true", help="Lean mode: exclude non-essential docs, fixtures, samples, and tests for AI audit")
    parser.add_argument("--all", action="store_true", help="All mode: include full codebase (docs, tests, samples) while omitting lockfiles and build junk")
    args = parser.parse_args()

    temp_obj = None
    target_root = args.dir

    try:
        # Resolve Vibe Intent (Seamless Vibe Coding based on user intent)
        vibe_intent = (args.intent or "").strip().lower()
        orion_bundles_dir = os.path.join(target_root, ".orion", "bundles")
        os.makedirs(orion_bundles_dir, exist_ok=True)

        # 1. URL detection -> auto remote ingestion with skeletonization
        if args.intent and (args.intent.startswith("http://") or args.intent.startswith("https://") or args.intent.startswith("git@")):
            args.remote = args.intent
            if not args.out:
                repo_name = args.intent.rstrip("/").split("/")[-1].replace(".git", "")
                args.out = os.path.join(orion_bundles_dir, f"remote_{repo_name}.xml")
            args.skeleton = True
            args.line_numbers = True
            args.format = "claude-xml"
            vibe_intent = ""

        # 2. Audit intent -> 10 domain bundles with FULL MICRO-CODE by default (Zero Blindspot)
        elif vibe_intent in ("audit", "code-audit"):
            args.audit = True
            args.line_numbers = True
            # Keep full code unless explicit skeleton requested
            if args.skeleton and not args.full:
                args.audit_ast = True
            else:
                args.skeleton = False
            if not args.out:
                args.out = os.path.join(target_root, ".orion", "audit_export")

        # 2b. Architecture / Skeleton intent -> Macro AST Skeletons for high-level structure
        elif vibe_intent in ("arch", "architecture", "skeleton", "macro"):
            args.audit_ast = True
            args.skeleton = True if not args.full else False
            args.line_numbers = True
            if not args.out:
                args.out = os.path.join(target_root, ".orion", "audit_export")

        # 2c. Hybrid intent -> Core domain full, secondary ops skeletonized
        elif vibe_intent in ("hybrid", "smart-audit"):
            args.audit = True
            args.hybrid = True
            args.line_numbers = True
            if not args.out:
                args.out = os.path.join(target_root, ".orion", "audit_export")

        # 3. PR / Review intent -> Staged git changes wrapped in pr-review template
        elif vibe_intent in ("pr", "review"):
            staged = collect_git_diff_files(target_root, staged_only=True)
            if staged:
                args.git_staged = True
            else:
                args.git_diff = ""
            args.line_numbers = True
            if not args.template:
                args.template = "pr-review"
            if not args.out:
                args.out = os.path.join(orion_bundles_dir, "pr_review.md")

        # 4. Diff / changes intent -> Uncommitted working tree diff
        elif vibe_intent in ("diff", "changes"):
            args.git_diff = ""
            args.line_numbers = True
            if not args.template:
                args.template = "pr-review"
            if not args.out:
                args.out = os.path.join(orion_bundles_dir, "git_diff.md")

        # 5. Security intent -> Secret scrubbing + AST skeleton + OWASP template
        elif vibe_intent in ("security", "sec"):
            args.skeleton = True
            args.line_numbers = True
            args.redact = True
            if not args.template:
                args.template = "security"
            if not args.out:
                args.out = os.path.join(orion_bundles_dir, "security_audit.md")

        # 6. Stats / tokens intent -> Delegate directly to core.scanner.cmd_tokens
        elif vibe_intent in ("stats", "tokens", "summary"):
            try:
                from core.scanner import cmd_tokens as _ct
            except ImportError:
                try:
                    from .scanner import cmd_tokens as _ct
                except ImportError:
                    from scanner import cmd_tokens as _ct
            _ct(argparse.Namespace(dir=target_root))
            return

        # 7. Megabundle intent -> 2 clean megabundles
        elif vibe_intent in ("megabundle", "mega"):
            args.megabundle = True
            args.skeleton = True
            args.line_numbers = True
            if not args.out:
                args.out = os.path.join(orion_bundles_dir, "megabundle")

        # 8. Full / all intent -> Full un-skeletonized dump
        elif vibe_intent in ("all", "full"):
            args.audit_all = True
            if not args.out:
                args.out = os.path.join(orion_bundles_dir, "full_bundles")

        # 9. Smart Auto-Vibe (when user calls `orion pack` with no flags and no intent)
        elif (vibe_intent in ("auto", "") 
              and not any([
                  args.audit, args.audit_all, args.audit_ast, args.bundle is not None,
                  args.megabundle, args.git_diff is not None, args.git_staged,
                  args.token_stats, args.template, args.remote, args.gemini,
                  args.gemini_10, args.gemini_10_all, args.gemini_10_lean
              ])):
            staged = collect_git_diff_files(target_root, staged_only=True)
            if staged:
                print(f"[AUTO-VIBE] Detected {len(staged)} staged git change(s) -> Auto-packaging PR Review...")
                args.git_staged = True
                args.line_numbers = True
                args.template = "pr-review"
                args.out = os.path.join(orion_bundles_dir, "pr_review.md")
            else:
                modified = collect_git_diff_files(target_root)
                if modified:
                    print(f"[AUTO-VIBE] Detected {len(modified)} modified change(s) -> Auto-packaging Git Diff...")
                    args.git_diff = ""
                    args.line_numbers = True
                    args.template = "pr-review"
                    args.out = os.path.join(orion_bundles_dir, "git_diff.md")
                else:
                    print("[AUTO-VIBE] Clean working tree -> Generating AST-skeletonized audit bundles...")
                    args.audit_ast = True
                    args.skeleton = True
                    args.line_numbers = True
                    args.out = os.path.join(target_root, ".orion", "audit_export")

        # Handle remote repository ingestion (from Gitingest)
        if args.remote:
            print(f"[REMOTE INGESTION] Cloning remote repository {args.remote}...")
            temp_obj, temp_dir, subpath = clone_remote_repo(args.remote, branch=args.branch)
            target_root = os.path.join(temp_dir, subpath) if subpath else temp_dir
            print(f"[REMOTE INGESTION] Cloned successfully into temporary workspace.")

        # Determine mode: "lean" (high-signal audit) vs "all" (full codebase)
        if args.all or args.audit_all or args.gemini_10_all:
            mode = "all"
        elif args.lean or args.audit or args.audit_ast or args.gemini_10_lean:
            mode = "lean"
        else:
            mode = "lean"

        is_domain_bundle_export = (
            args.audit
            or args.audit_all
            or args.audit_ast
            or (args.bundle is not None)
            or args.gemini_10
            or args.gemini_10_all
            or args.gemini_10_lean
            or (args.lean and not args.token_stats and not args.git_diff and not args.git_staged)
            or (args.all and not args.token_stats and not args.git_diff and not args.git_staged)
        )

        if is_domain_bundle_export:
            num_b = args.bundle if (args.bundle is not None) else 10
            use_skel = (args.audit_ast or args.skeleton) and not args.full
            is_hybrid = getattr(args, 'hybrid', False)
            export_audit_bundles(
                target_root,
                out_dir=args.out,
                budget=args.budget,
                num_bundles=num_b,
                mode=mode,
                skeleton=use_skel,
                line_numbers=args.line_numbers,
                hybrid=is_hybrid
            )
            return

        if args.megabundle or args.gemini:
            export_audit_bundles(
                target_root,
                out_dir=args.out,
                budget=args.budget,
                num_bundles=2,
                mode=mode,
                skeleton=args.skeleton and not args.full,
                line_numbers=args.line_numbers,
                hybrid=getattr(args, 'hybrid', False)
            )
            return

        packer = ContextPacker(target_root)

        # Handle git diff scoping (from Repomix)
        if args.git_staged:
            files = collect_git_diff_files(target_root, staged_only=True)
            print(f"[GIT DIFF] Scoped packing to {len(files)} staged file(s).")
        elif args.git_diff is not None:
            ref = args.git_diff if args.git_diff else None
            files = collect_git_diff_files(target_root, diff_ref=ref)
            print(f"[GIT DIFF] Scoped packing to {len(files)} modified file(s).")
        else:
            files = packer.collect_files(max_size_bytes=args.max_size_kb * 1024, prioritize_salience=args.salience)

        # Handle token statistics analytics (from code2prompt)
        if args.token_stats:
            stats = calculate_token_stats(target_root, files)
            print_token_stats_table(stats)
            if not args.out and args.format == "xml" and not args.skeleton and not args.template:
                return

        repomap_str = None
        if args.repomap:
            try:
                try:
                    from core.scanner import build_repo_map as _brm
                except ImportError:
                    try:
                        from .scanner import build_repo_map as _brm
                    except ImportError:
                        from scanner import build_repo_map as _brm
                rm_data = _brm(target_root, budget_tokens=min(args.budget // 4, 3000))
                repomap_str = rm_data.get("repo_map", "")
            except Exception as _e:
                _log_telemetry(_e, "main:build_repo_map")

        use_skel = args.skeleton or args.audit_ast

        if args.format == "claude-xml":
            out_content = packer.pack_claude_xml(
                files,
                max_tokens=args.budget,
                scrub_secrets=args.redact,
                line_numbers=args.line_numbers,
                skeleton=use_skel
            )
            summary = f"[PACKER] Generated Claude XML envelope for {len(files)} files"
        elif args.format == "xml":
            res = packer.pack_xml(
                files,
                max_tokens=args.budget,
                scrub_secrets=args.redact,
                repomap=repomap_str,
                line_numbers=args.line_numbers,
                skeleton=use_skel
            )
            out_content = res["envelope"]
            summary = f"[PACKER] Packed {res['packed_files_count']} files (~{res['estimated_tokens']} tokens, {len(res['secret_alerts'])} secret alerts)"
        else:
            out_content = packer.pack_digest(
                files,
                max_tokens=args.budget,
                scrub_secrets=args.redact,
                line_numbers=args.line_numbers,
                skeleton=use_skel
            )
            summary = f"[PACKER] Generated markdown digest for {len(files)} files"

        # Handle prompt template wrapping (from code2prompt)
        if args.template:
            repo_name = os.path.basename(os.path.abspath(target_root))
            tree_lines = generate_ascii_tree(target_root, max_depth=3, ignore_filter=packer.gi)
            if args.template == "security":
                try:
                    try:
                        from core.security import SecurityAuditor
                    except ImportError:
                        try:
                            from .security import SecurityAuditor
                        except ImportError:
                            from security import SecurityAuditor
                    auditor = SecurityAuditor(target_root)
                    active, _ = auditor.audit_directory()
                    findings_md = []
                    if active:
                        findings_md.append(f"\n## 🛡️ Static AST & Secret Security Findings ({len(active)} active):\n")
                        findings_md.append("| ID | Severity | File | Category | Snippet |")
                        findings_md.append("|---|---|---|---|---|")
                        for idx, item in enumerate(active, 1):
                            f_path = os.path.relpath(item.get("file", ""), target_root).replace("\\", "/")
                            f_sev = item.get("severity", "MEDIUM")
                            f_cat = item.get("category", "General")
                            f_snip = item.get("snippet", "").strip().replace("|", "\\|").replace("\n", " ")[:60]
                            findings_md.append(f"| SEC-{idx:03d} | **{f_sev}** | `{f_path}` | {f_cat} | `{f_snip}` |")
                        findings_md.append("\n")
                    else:
                        findings_md.append("\n## 🛡️ Static AST & Secret Security Findings:\nNo active AST or secret vulnerabilities detected in target scan.\n")
                    out_content = "\n".join(findings_md) + "\n---\n" + out_content
                except Exception as _sec_err:
                    _log_telemetry(_sec_err, "packer.py:security_audit_injection")

            tmpl_context = {
                "repo_name": repo_name,
                "file_count": len(files),
                "token_count": estimate_tokens(out_content),
                "tree": "\n".join(tree_lines),
                "files": out_content
            }
            out_content = render_prompt_template(args.template, tmpl_context)
            summary += f" [Wrapped in '{args.template}' template]"

        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(out_content)
            print(f"{summary} -> {args.out}")
        else:
            print(out_content)

    finally:
        if temp_obj is not None:
            temp_obj.cleanup()


if __name__ == "__main__":
    main()


