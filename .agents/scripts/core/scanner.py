import os
import sys
import json
import argparse
import re
import math
import shutil
import subprocess
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

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
        _log_telemetry(_e, 'scanner.py:reconfigure')



FRONTMATTER_PATTERN = re.compile(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', re.DOTALL)


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter at the beginning of a markdown document.
    Returns (metadata_dict, markdown_body).
    """
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    raw_yaml = match.group(1)
    body = content[match.end():]
    metadata: Dict[str, Any] = {}

    current_key = None
    for line in raw_yaml.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith('#'):
            continue

        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()

            if val == "":
                current_key = key
                metadata[key] = []
            elif val.lower() == "true":
                metadata[key] = True
                current_key = None
            elif val.lower() == "false":
                metadata[key] = False
                current_key = None
            elif val.startswith('"') and val.endswith('"'):
                metadata[key] = val[1:-1]
                current_key = None
            elif val.startswith("'") and val.endswith("'"):
                metadata[key] = val[1:-1]
                current_key = None
            elif val.startswith('[') and val.endswith(']'):
                items = [x.strip().strip('"\'') for x in val[1:-1].split(',') if x.strip()]
                metadata[key] = items
                current_key = None
            else:
                try:
                    if '.' in val:
                        metadata[key] = float(val)
                    else:
                        metadata[key] = int(val)
                except ValueError:
                    metadata[key] = val
                current_key = None
        elif (line.startswith('  - ') or line.startswith('- ')) and current_key:
            item = line.split('-', 1)[1].strip().strip('"\'')
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(item)

    return metadata, body


def dump_frontmatter(metadata: Dict[str, Any], body: str) -> str:
    """Serialize metadata dictionary into YAML frontmatter and attach body."""
    lines = ["---"]
    for k, v in metadata.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            str_val = str(v)
            if any(ch in str_val for ch in [':', '#', '[', ']', '{', '}', '\n']):
                lines.append(f'{k}: "{str_val}"')
            else:
                lines.append(f"{k}: {str_val}")
    lines.append("---")
    lines.append("")
    lines.append(body.lstrip('\r\n'))
    return "\n".join(lines)


# === AUDIT TARGETS DISCOVERY ===

def get_audit_targets(directory: str, extensions: List[str], exclude_dirs: List[str]) -> List[str]:
    """
    Deterministically scans a directory for files to audit.
    Filters out common boilerplate, library, and hidden directories.
    """
    targets = []
    exclude_set = {d.lower() for d in exclude_dirs}
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d.lower() not in exclude_set and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                full_path = os.path.abspath(os.path.join(root, file))
                targets.append(full_path)
                
    return sorted(targets)


def cmd_targets(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    default_excludes = ["node_modules", "build", "dist", "coverage", ".git", "ios", "android", ".agents", ".gemini", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion"]
    default_exts = [".py", ".dart", ".js", ".ts", ".go", ".rs", ".kt", ".java"]
    try:
        manifest_path = os.path.join(target_dir, ".agents", ".project_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                if "ecosystem" in manifest:
                    if "ignore_dirs" in manifest["ecosystem"]:
                        default_excludes = manifest["ecosystem"]["ignore_dirs"]
                    if "extensions" in manifest["ecosystem"]:
                        default_exts = manifest["ecosystem"]["extensions"]
    except Exception as _e:
        _log_telemetry(_e, 'scanner.py:targets_manifest')

    exts = args.ext if args.ext is not None else default_exts
    excludes = args.exclude if args.exclude is not None else default_excludes

    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)
        
    targets = get_audit_targets(target_dir, exts, excludes)
    
    if getattr(args, 'json', False):
        print(json.dumps(targets, indent=2))
    else:
        print(f"--- Found {len(targets)} audit targets in '{target_dir}' ---")
        for i, target in enumerate(targets, 1):
            print(f"{i}. {target}")


# === SKELETON MAPPER ===

def _find_brace_block_end(lines: List[str], start_line: int, fallback_end: int) -> int:
    """Finds the line number of matching closing brace '}' for polyglot block definitions."""
    depth = 0
    started = False
    in_block_comment = False
    max_scan = min(len(lines), start_line + 5000)
    for idx in range(start_line - 1, max_scan):
        line = lines[idx]
        curr_line_num = idx + 1
        i = 0
        in_str = None
        while i < len(line):
            if in_block_comment:
                if line[i:i+2] == '*/':
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue
            if in_str:
                if line[i] == '\\':
                    i += 2
                    continue
                if line[i] == in_str:
                    in_str = None
                i += 1
                continue
            if line[i:i+2] == '/*':
                in_block_comment = True
                i += 2
                continue
            if line[i:i+2] == '//' or line[i] == '#':
                break
            if line[i] in ('"', "'", '`'):
                in_str = line[i]
                i += 1
                continue
            if line[i] == '{':
                depth += 1
                started = True
            elif line[i] == '}':
                if started:
                    depth -= 1
                    if depth == 0:
                        return curr_line_num
            i += 1
    return fallback_end


def generate_skeleton(file_path: str, content: Optional[str] = None) -> List[str]:
    """
    Extracts class and function definitions to create a structural skeleton
    of a codebase file for token-efficient context ingestion.
    Supports Python, Dart, TypeScript, JavaScript, Rust, Go, Kotlin, Java.
    Emits [Lstart-Lend] spans to enable surgical single-call view_file reads.
    If content is provided, uses it directly to avoid redundant disk I/O.
    """
    skeleton = []
    ext = os.path.splitext(file_path)[1].lower()

    # Python path: use ast for precise end_lineno
    if ext == ".py":
        try:
            import ast as _ast
            if content is None:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
            else:
                file_content = content
            tree = _ast.parse(file_content, filename=file_path)
            hits = []
            for node in _ast.walk(tree):
                if isinstance(node, (_ast.ClassDef, _ast.FunctionDef, _ast.AsyncFunctionDef)):
                    end_line = getattr(node, 'end_lineno', node.lineno)
                    prefix = "async def " if isinstance(node, _ast.AsyncFunctionDef) else (
                        "class " if isinstance(node, _ast.ClassDef) else "def "
                    )
                    hits.append((node.lineno, end_line, prefix, node.name))
            hits.sort(key=lambda x: x[0])
            for lineno, end_line, prefix, name in hits:
                skeleton.append(f"  [L{lineno}-L{end_line}] {prefix}{name}")
            return skeleton
        except Exception as e:
            _log_telemetry(e, f"generate_skeleton_ast:{file_path}")
            # Fall through to regex path

    # Polyglot regex path: track line numbers; estimate end as next-symbol - 1
    patterns = [
        re.compile(r'^\s*(?:export\s+)?(?:abstract\s+|pub\s+|public\s+|private\s+)?(?:class|struct|interface|trait|enum)\s+([A-Za-z0-9_]+)'),
        re.compile(r'^\s*(?:def|async def|fn|function|fun)\s+([A-Za-z0-9_]+)\s*\('),
        re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*\('),
        re.compile(r'^\s*(?!(?:if|for|while|catch|switch|return)\s*\()((?:[a-zA-Z<>\[\]_]+\s+)?([A-Za-z0-9_]+)\s*\([^)]*\)\s*(?:async\*?|sync\*)?\s*[{=>])'),
    ]

    raw_hits: List[Tuple[int, str]] = []  # (line_num, sig)
    try:
        lines = content.splitlines(keepends=True) if content is not None else None
        if lines is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith(('#', '//', '/*', '*', '"""', "'''")):
                continue
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    sig = clean_line.rstrip('{:;').strip()
                    raw_hits.append((line_num, sig))
                    break
    except Exception as e:
        _log_telemetry(e, f"generate_skeleton:{file_path}")

    total_lines = len(lines) if lines else (line_num if 'line_num' in locals() else 1)
    for i, (lnum, sig) in enumerate(raw_hits):
        fallback_end = raw_hits[i + 1][0] - 1 if i + 1 < len(raw_hits) else total_lines
        end_line = _find_brace_block_end(lines, lnum, fallback_end) if lines else fallback_end
        if end_line < lnum:
            end_line = lnum
        skeleton.append(f"  [L{lnum}-L{end_line}] {sig}")

    return skeleton


def skeletonize_python(code: str) -> str:
    """
    Pillar 1 Python AST Skeletonizer.
    Mengekstrak dekorator, kelas, signature multi-baris, field @dataclass/Enum,
    docstring, dan anotasi tipe sambil mengosongkan implementasi fungsi secara valid.
    """
    try:
        import ast
        tree = ast.parse(code)
    except Exception:
        return code

    lines = code.splitlines()
    out: List[str] = []

    def _node_start_idx(node: ast.AST) -> int:
        dec_list = getattr(node, "decorator_list", None)
        if dec_list:
            return min(d.lineno for d in dec_list) - 1
        return getattr(node, "lineno", 1) - 1

    def _header_and_doc_end_idx(node: ast.AST) -> Tuple[int, bool]:
        body = getattr(node, "body", [])
        if not body:
            return getattr(node, "end_lineno", getattr(node, "lineno", 1)), False
        first_stmt = body[0]
        if (
            isinstance(first_stmt, ast.Expr)
            and isinstance(getattr(first_stmt, "value", None), ast.Constant)
            and isinstance(first_stmt.value.value, str)
        ):
            return (first_stmt.end_lineno or first_stmt.lineno), True
        return max(getattr(node, "lineno", 1), first_stmt.lineno - 1), False

    def _summarize_body_contracts(node: ast.AST) -> str:
        calls: List[str] = []
        raises: List[str] = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name) and sub.func.id not in calls:
                    calls.append(sub.func.id)
                elif isinstance(sub.func, ast.Attribute) and sub.func.attr not in calls:
                    calls.append(sub.func.attr)
            elif isinstance(sub, ast.Raise) and sub.exc is not None:
                exc_name = None
                if isinstance(sub.exc, ast.Call) and isinstance(sub.exc.func, ast.Name):
                    exc_name = sub.exc.func.id
                elif isinstance(sub.exc, ast.Name):
                    exc_name = sub.exc.id
                if exc_name and exc_name not in raises:
                    raises.append(exc_name)
        parts: List[str] = []
        if calls:
            parts.append(f"Calls: {', '.join(calls[:5])}")
        if raises:
            parts.append(f"Raises: {', '.join(raises[:3])}")
        return (" | " + " | ".join(parts)) if parts else ""

    def process_function(node: ast.AST, indent: str = "    ") -> str:
        s = _node_start_idx(node)
        e, _ = _header_and_doc_end_idx(node)
        end_line = getattr(node, "end_lineno", None) or (e + 1)
        body_omitted = max(1, (end_line - s) - (e - s))
        header_block = "\n".join(lines[s:e])
        digest = _summarize_body_contracts(node)
        return f"{header_block}\n{indent}...  # [Body omitted for audit: {body_omitted} lines{digest}]"

    def process_class(node: ast.ClassDef, depth: int = 0) -> str:
        res: List[str] = []
        s = _node_start_idx(node)
        e, has_doc = _header_and_doc_end_idx(node)
        res.append("\n".join(lines[s:e]))
        child_indent = "    " * (depth + 2)
        emitted_members = 0

        for idx, child in enumerate(node.body):
            if idx == 0 and has_doc:
                emitted_members += 1
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                res.append(process_function(child, indent=child_indent))
                emitted_members += 1
            elif isinstance(child, ast.ClassDef):
                res.append(process_class(child, depth=depth + 1))
                emitted_members += 1
            elif isinstance(child, (ast.AnnAssign, ast.Assign)):
                cs = child.lineno - 1
                ce = child.end_lineno or child.lineno
                if ce - cs <= 8:
                    res.append("\n".join(lines[cs:ce]))
                    emitted_members += 1

        if emitted_members == 0:
            res.append(f"{'    ' * (depth + 1)}...")
        return "\n".join(res)

    def _emit_top_node(node: ast.AST) -> None:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            s = node.lineno - 1
            e = node.end_lineno or node.lineno
            out.append("\n".join(lines[s:e]))
        elif isinstance(node, ast.ClassDef):
            out.append(process_class(node, depth=0))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(process_function(node, indent="    "))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            s = node.lineno - 1
            e = node.end_lineno or node.lineno
            if e - s <= 5:
                out.append("\n".join(lines[s:e]))
        elif isinstance(node, ast.Try):
            for sub in node.body:
                _emit_top_node(sub)

    for node in tree.body:
        _emit_top_node(node)

    return "\n\n".join(out) if out else code


SUPPORTED_SKELETON_EXTENSIONS = {
    'py', 'ts', 'tsx', 'js', 'jsx', 'mjs', 'cjs',
    'dart', 'rs', 'go', 'kt', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'swift'
}


def skeletonize_code(code: str, ext: str) -> str:
    """
    Pillar 1/2 Multi-language AST/CST Skeletonizer.
    Strips implementation bodies while preserving contracts, interfaces, classes, and docstrings.
    Supported: Python (ast), TypeScript/JS, Dart, Rust, Go (CST regex with Pillar 2 acceleration capability).
    """
    ext = ext.lower().lstrip('.')
    if ext not in SUPPORTED_SKELETON_EXTENSIONS:
        return code
    if ext == 'py':
        return skeletonize_python(code)

    lines = code.splitlines()
    out = []
    in_block = False
    brace_depth = 0

    sig_pattern = re.compile(
        r'^\s*(?:export\s+|pub\s+|abstract\s+|default\s+|async\s+)*'
        r'(?:class|interface|type|enum|trait|struct|impl|func|fn|function|def)\b'
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not in_block:
                out.append("")
            continue

        if any(stripped.startswith(p) for p in ('import ', 'from ', 'export *', 'package ', 'use ', '#include')):
            out.append(line)
            continue

        if sig_pattern.match(line):
            out.append(line)
            if '{' in line:
                brace_depth += line.count('{') - line.count('}')
                in_block = True
                out.append("    // ... [Implementation omitted for audit] ...")
            continue

        if brace_depth > 0:
            brace_depth += line.count('{') - line.count('}')
            if brace_depth <= 0:
                brace_depth = 0
                out.append("}")
                in_block = False

    return '\n'.join(out) if out else code


def extract_python_edges_ast(content: str, file_basename: str) -> List[Tuple[str, str, str]]:
    """Extracts structural AST triplets and # WHY: / # NOTE: rationale nodes in a single pass."""
    import ast as _ast
    triplets: List[Tuple[str, str, str]] = []
    try:
        tree = _ast.parse(content)
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Import):
                for alias in node.names:
                    triplets.append((file_basename, "imports", alias.name))
            elif isinstance(node, _ast.ImportFrom) and node.module:
                triplets.append((file_basename, "imports", node.module))
            elif isinstance(node, _ast.ClassDef):
                triplets.append((file_basename, "defines", node.name))
                for base in node.bases:
                    if isinstance(base, _ast.Name):
                        triplets.append((node.name, "inherits", base.id))
            elif isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                triplets.append((file_basename, "defines", node.name))
    except Exception as _e:
        _log_telemetry(_e, f"extract_python_edges_ast:{file_basename}")

    # Extract Rationale comments (# WHY:, # NOTE:, // WHY:)
    for match in re.finditer(r'(?:#|//)\s*(WHY|NOTE|ADR-\d+)\s*:\s*(.+)', content):
        tag, rationale_text = match.group(1), match.group(2).strip()[:120]
        if rationale_text:
            triplets.append((file_basename, f"rationale_{tag.lower()}", rationale_text))
    return triplets


def generate_ast_summary(filepath: str, content: Optional[str] = None) -> str:
    """Unified single-pass AST skeleton summary generator."""
    header = f"--- AST Summary for {os.path.basename(filepath)} ---\n"
    skel = generate_skeleton(filepath, content=content)
    if skel:
        return header + "\n".join(skel)
    return header + "No structural elements found."



def map_directory(dir_path: str, exclude_dirs: Set[str], valid_exts: Set[str]) -> None:
    print(f" Generating Code Skeleton Map for: {os.path.abspath(dir_path)}")
    print("=" * 60)

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        for file in files:
            if any(file.endswith(ext) for ext in valid_exts):
                file_path = os.path.join(root, file)
                skeleton = generate_skeleton(file_path)
                if skeleton:
                    rel_path = os.path.relpath(file_path, dir_path)
                    print(f"\n {rel_path}")
                    for line in skeleton:
                        print(line)


def cmd_map(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    ignore_dirs = {"node_modules", "build", "dist", "coverage", ".git", "ios", "android", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion", ".gemini", ".dart_tool"}
    valid_extensions = {".dart", ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java", ".kt"}

    if os.path.isfile(target_dir):
        print(f"📦 Code Map for File: {os.path.abspath(target_dir)}\n")
        skeleton = generate_skeleton(target_dir)
        if skeleton:
            for line in skeleton:
                print(f"  │ {line}")
        else:
            print("  │ [No classes or functions found]")
        return
    
    try:
        manifest_path = os.path.join(target_dir, ".agents", ".project_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                if "ecosystem" in manifest:
                    if "ignore_dirs" in manifest["ecosystem"]:
                        ignore_dirs = set(manifest["ecosystem"]["ignore_dirs"])
                    if "extensions" in manifest["ecosystem"]:
                        valid_extensions = set(manifest["ecosystem"]["extensions"])
    except Exception as _e:
        _log_telemetry(_e, 'scanner.py:map_manifest')

    if getattr(args, 'ranked', False):
        cmd_repomap(args)
        return

    def build_tree(current_dir: str, current_depth: int) -> None:
        if current_depth > getattr(args, 'max_depth', 5):
            return
        try:
            entries = sorted(os.listdir(current_dir))
        except PermissionError:
            return

        for entry in entries:
            path = os.path.join(current_dir, entry)
            if os.path.isdir(path):
                if entry in ignore_dirs or entry.startswith('.'):
                    continue
                print(f"{'  ' * current_depth}📁 {entry}/")
                build_tree(path, current_depth + 1)
            elif os.path.isfile(path):
                _, ext = os.path.splitext(entry)
                if ext in valid_extensions:
                    print(f"{'  ' * current_depth}📄 {entry}")
                    skeleton = generate_skeleton(path)
                    for line in skeleton:
                        print(f"{'  ' * (current_depth + 1)}│ {line}")

    print(f"📦 Code Map for: {os.path.abspath(target_dir)}\n")
    build_tree(target_dir, 0)


# === AST & POLYGLOT SYMBOL EXTRACTION ===

RESERVED_KEYWORDS = {
    "if", "else", "elif", "while", "for", "switch", "case", "return", "break",
    "continue", "import", "from", "as", "class", "def", "function", "fn",
    "fun", "interface", "struct", "trait", "enum", "type", "const", "let",
    "var", "val", "pub", "public", "private", "protected", "final", "static",
    "abstract", "void", "int", "string", "bool", "boolean", "true", "false",
    "null", "nil", "None", "self", "this", "super", "try", "catch", "except",
    "finally", "throw", "raise", "async", "await", "yield", "default", "new",
    "package", "in", "is", "not", "and", "or", "with", "pass", "lambda"
}

def _find_ast_grep_bin(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Checks if ast-grep / sg static binary is available via centralized capabilities or standalone PATH search."""
    try:
        from core.capabilities import find_ast_grep
        return find_ast_grep(extra_dirs=extra_dirs)
    except ImportError:
        search_dirs = list(extra_dirs or [])
        search_dirs.extend([
            os.path.expanduser("~/.cargo/bin"),
            os.path.expanduser("~/.bun/bin"),
            os.path.join(os.getcwd(), ".agents", "bin"),
        ])
        for candidate in ("sg", "ast-grep", "sg.exe", "ast-grep.exe"):
            found = shutil.which(candidate)
            if found:
                return found
            for directory in search_dirs:
                path = os.path.join(directory, candidate)
                if os.name == "nt" and not os.path.splitext(path)[1]:
                    path += ".exe"
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    return path
        return None


def extract_file_symbols(file_path: str) -> Tuple[Dict[str, List[Tuple[int, str]]], Set[str]]:
    """
    Extracts definitions and references from a single source file.
    Uses Python stdlib AST for .py files, and high-fidelity polyglot parser for others.
    Leverages SQLite ast_symbol_cache with (mtime_ns, size_b) invalidation for sub-15ms incremental lookups.
    Returns: (defines_dict: {sym_name: [(line_no, signature)]}, references_set: {ref_name})
    """
    mtime_ns = 0
    size_b = 0
    cache_db_path = None
    try:
        st = os.stat(file_path)
        mtime_ns, size_b = st.st_mtime_ns, st.st_size
        try:
            from core.paths import get_persistence_db_path
            cache_db_path = str(get_persistence_db_path())
        except ImportError:
            orion_dir = os.path.join(os.getcwd(), ".orion")
            cache_db_path = os.path.join(orion_dir, "orion.db") if os.path.isdir(orion_dir) else None
        if cache_db_path and os.path.exists(cache_db_path):
            import sqlite3
            conn = sqlite3.connect(cache_db_path, timeout=2.0)
            try:
                with conn:
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS ast_symbol_cache ("
                        "filepath TEXT PRIMARY KEY, mtime_ns INTEGER, size_b INTEGER, "
                        "defines_json TEXT, references_json TEXT)"
                    )
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT mtime_ns, size_b, defines_json, references_json FROM ast_symbol_cache WHERE filepath = ?",
                        (file_path,)
                    )
                    row = cur.fetchone()
                    if row and row[0] == mtime_ns and row[1] == size_b:
                        raw_def = json.loads(row[2])
                        cached_defs = {k: [tuple(x) for x in v] for k, v in raw_def.items()}
                        cached_refs = set(json.loads(row[3]))
                        return cached_defs, cached_refs
            finally:
                conn.close()
    except Exception as _ce:
        _log_telemetry(_ce, "scanner.py:ast_symbol_cache_read")

    defines: Dict[str, List[Tuple[int, str]]] = {}
    references: Set[str] = set()
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".py":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            import ast

            class PySymbolVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.scope_stack = []

                def visit_ClassDef(self, node: ast.ClassDef):
                    sig = f"class {node.name}"
                    if node.bases:
                        base_names = []
                        for b in node.bases:
                            if isinstance(b, ast.Name):
                                base_names.append(b.id)
                            elif isinstance(b, ast.Attribute):
                                base_names.append(b.attr)
                        if base_names:
                            sig += f"({', '.join(base_names)})"
                    defines.setdefault(node.name, []).append((node.lineno, sig))
                    self.scope_stack.append(node.name)
                    self.generic_visit(node)
                    self.scope_stack.pop()

                def visit_FunctionDef(self, node: ast.FunctionDef):
                    self._handle_func(node, is_async=False)

                def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                    self._handle_func(node, is_async=True)

                def _handle_func(self, node, is_async: bool):
                    prefix = "async def " if is_async else "def "
                    args_list = [a.arg for a in node.args.args if a.arg not in {"self", "cls"}]
                    arg_str = ", ".join(args_list[:4])
                    if len(args_list) > 4:
                        arg_str += ", ..."
                    sig = f"{prefix}{node.name}({arg_str})"
                    defines.setdefault(node.name, []).append((node.lineno, sig))
                    self.scope_stack.append(node.name)
                    self.generic_visit(node)
                    self.scope_stack.pop()

                def visit_Name(self, node: ast.Name):
                    if isinstance(node.ctx, ast.Load) and node.id not in RESERVED_KEYWORDS:
                        references.add(node.id)
                    self.generic_visit(node)

                def visit_Attribute(self, node: ast.Attribute):
                    if isinstance(node.ctx, ast.Load) and node.attr not in RESERVED_KEYWORDS:
                        references.add(node.attr)
                    self.generic_visit(node)

            tree = ast.parse(content, filename=file_path)
            visitor = PySymbolVisitor()
            visitor.visit(tree)
        except Exception as _e:
            _log_telemetry(_e, f"extract_file_symbols_py:{file_path}")
    else:
        # Polyglot parser for Dart, TypeScript, JavaScript, Rust, Kotlin, Java, Go
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            content = "".join(lines)
            raw_tokens = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]{2,}\b', content)
            for tok in raw_tokens:
                if tok not in RESERVED_KEYWORDS:
                    references.add(tok)

            sg_bin = _find_ast_grep_bin()
            extracted_via_sg = False
            if sg_bin:
                try:
                    patterns_to_probe = [
                        ("class $NAME", "class"),
                        ("interface $NAME", "interface"),
                        ("struct $NAME", "struct"),
                        ("function $NAME($$$ARGS)", "function"),
                        ("fn $NAME($$$ARGS)", "function"),
                    ]
                    for pat, _kind in patterns_to_probe:
                        cmd = [sg_bin, "run", "--pattern", pat, "--json=stream", file_path]
                        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if proc.returncode == 0 and proc.stdout.strip():
                            for line in proc.stdout.splitlines():
                                if not line.strip():
                                    continue
                                data = json.loads(line)
                                meta = data.get("metaVariables", {}).get("single", {})
                                name = meta.get("NAME", {}).get("text", "")
                                line_no = data.get("range", {}).get("start", {}).get("line", 1)
                                sig = data.get("text", name).splitlines()[0].rstrip('{:;').strip()
                                if name and name not in RESERVED_KEYWORDS:
                                    defines.setdefault(name, []).append((line_no, sig))
                                    references.discard(name)
                    extracted_via_sg = len(defines) > 0
                except Exception as _e:
                    _log_telemetry(_e, f"extract_file_symbols_ast_grep:{file_path}")

            if not extracted_via_sg:
                patterns = [
                    (re.compile(r'^\s*(?:export\s+)?(?:abstract\s+|pub\s+|public\s+|private\s+)?(?:class|struct|interface|trait|enum)\s+([A-Za-z0-9_]+)'), "class"),
                    (re.compile(r'^\s*(?:export\s+)?(?:async\s+)?(?:pub\s+|public\s+|private\s+|protected\s+|static\s+|fn\s+|def\s+|fun\s+|function\s+)?(?:[A-Za-z0-9_<>\[\],\s]+\s+)?([A-Za-z0-9_]+)\s*\((.*?)\)\s*(?:async\*?|sync\*?)?\s*[{=>;]'), "func"),
                ]
                for line_num, line in enumerate(lines, 1):
                    clean = line.strip()
                    if not clean or clean.startswith(('#', '//', '/*', '*', '"""', "'''")):
                        continue
                    for pat, _ in patterns:
                        m = pat.match(clean)
                        if m:
                            sym_name = m.group(1).strip()
                            if sym_name in RESERVED_KEYWORDS:
                                continue
                            sig = clean.rstrip('{:;').strip()
                            defines.setdefault(sym_name, []).append((line_num, sig))
                            references.discard(sym_name)
                            break
        except Exception as _e:
            _log_telemetry(_e, f"extract_file_symbols_polyglot:{file_path}")

    if cache_db_path and os.path.exists(cache_db_path) and mtime_ns > 0:
        try:
            import sqlite3
            conn = sqlite3.connect(cache_db_path, timeout=2.0)
            try:
                with conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO ast_symbol_cache (filepath, mtime_ns, size_b, defines_json, references_json) VALUES (?, ?, ?, ?, ?)",
                        (file_path, mtime_ns, size_b, json.dumps(defines), json.dumps(list(references)))
                    )
            finally:
                conn.close()
        except Exception as _se:
            _log_telemetry(_se, "scanner.py:ast_symbol_cache_write")

    return defines, references


def extract_symbols(root_dir: str, max_files: int = 500) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts code symbols and cross-file references via ast-grep or fallback AST parser.
    Fulfills interface contract: returns mapping of relative file path -> list of symbol dicts.
    """
    ignore_dirs = {"node_modules", "build", "dist", "coverage", ".git", "ios", "android", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion", ".gemini", ".dart_tool"}
    valid_extensions = {".dart", ".ts", ".js", ".py", ".go", ".rs", ".kt", ".java"}

    file_paths: List[str] = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_extensions:
                file_paths.append(os.path.join(root, f))
                if len(file_paths) >= max_files:
                    break
        if len(file_paths) >= max_files:
            break

    result: Dict[str, List[Dict[str, Any]]] = {}

    for fp in file_paths:
        rel_path = os.path.relpath(fp, root_dir).replace("\\", "/")
        symbols_list: List[Dict[str, Any]] = []

        defs, refs = extract_file_symbols(fp)
        for sym_name, occurrences in defs.items():
            for line_no, sig in occurrences:
                kind = "class" if "class" in sig.split() or "struct" in sig.split() else "function"
                symbols_list.append({
                    "name": sym_name,
                    "kind": kind,
                    "line": line_no,
                    "signature": sig,
                    "file": rel_path,
                    "references_count": len(refs)
                })

        result[rel_path] = symbols_list

    return result


# === SPARSE POWER-ITERATION PAGERANK ===

def compute_pagerank(
    graph: Dict[str, Dict[str, float]],
    d: float = 0.85,
    epsilon: float = 1e-6,
    max_iter: int = 100,
    personalization: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Computes sparse power-iteration PageRank scores with guaranteed Perron-Frobenius convergence.
    Complexity per iteration: O(|V| + |E|).
    
    Formulation:
      r_v^{(t+1)} = d * ( sum_{u in Pred(v)} r_u^{(t)} * W_{uv} / k_u^{out} + S_dangling * p_v ) + (1 - d) * p_v
    """
    nodes = list(graph.keys())
    N = len(nodes)
    if N == 0:
        return {}
    if N == 1:
        return {nodes[0]: 1.0}

    # 1. Precompute out-degree weights: k_u^{out}
    out_weights: Dict[str, float] = {}
    for u in nodes:
        out_weights[u] = sum(graph.get(u, {}).values())

    # 2. Inverted in-edge adjacency lists: in_edges[v] = [(u, W_{uv})]
    in_edges: Dict[str, List[Tuple[str, float]]] = {v: [] for v in nodes}
    for u in nodes:
        u_out = out_weights[u]
        if u_out > 0.0:
            for v, weight in graph.get(u, {}).items():
                if v in in_edges and weight > 0.0:
                    in_edges[v].append((u, float(weight)))

    # 3. Identify dangling nodes (out-degree == 0)
    dangling_nodes: List[str] = [u for u in nodes if out_weights[u] <= 0.0]

    # 4. Personalization probability vector p (sum(p) == 1.0)
    p_vec: Dict[str, float] = {}
    if personalization:
        tot = sum(personalization.get(n, 0.0) for n in nodes)
        if tot > 0.0:
            for n in nodes:
                p_vec[n] = max(0.0, personalization.get(n, 0.0)) / tot
        else:
            uniform_p = 1.0 / N
            for n in nodes:
                p_vec[n] = uniform_p
    else:
        uniform_p = 1.0 / N
        for n in nodes:
            p_vec[n] = uniform_p

    # 5. Initialize stationary vector r^{(0)} = p
    r: Dict[str, float] = dict(p_vec)

    # 6. Sparse power iteration with L1 residual convergence check
    for _ in range(max_iter):
        # Accumulate dangling mass: S_dangling = sum_{u in D} r_u
        dangling_sum = sum(r[u] for u in dangling_nodes)

        next_r: Dict[str, float] = {}
        l1_diff = 0.0

        for v in nodes:
            # Sparse inward edge accumulation: sum_{u in Pred(v)} r_u * W_{uv} / out_weight[u]
            in_flow = 0.0
            for u, weight in in_edges[v]:
                in_flow += r[u] * (weight / out_weights[u])

            new_rank = d * (in_flow + dangling_sum * p_vec[v]) + (1.0 - d) * p_vec[v]
            next_r[v] = new_rank
            l1_diff += abs(new_rank - r[v])

        r = next_r
        if l1_diff < epsilon:
            break

    # Normalize final distribution
    norm_sum = sum(r.values())
    if norm_sum > 0.0:
        for n in nodes:
            r[n] = r[n] / norm_sum

    return r


# Alias pagerank for backwards compatibility with existing calls
def pagerank(
    graph: Dict[str, Dict[str, float]],
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
    personalization: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    return compute_pagerank(graph, d=damping, epsilon=tol, max_iter=max_iter, personalization=personalization)


# === VALUE-DENSITY GREEDY KNAPSACK BUDGET PACKING ===

def pack_repomap_budget(files_salience: List[Tuple[str, float, Any]], max_tokens: int = 1500) -> str:
    """
    Packs high-salience symbol signatures into prompt envelope using value-density greedy knapsack.
    files_salience: list of tuples: (file_rel_path, salience_score, definitions_or_lines)
    """
    if not files_salience:
        return "(Empty repo map)"

    # Flatten into candidate items: (file_path, file_score, line_no, sig, item_score, token_cost)
    items: List[Dict[str, Any]] = []

    for rel_path, file_score, defs_data in files_salience:
        parsed_defs: List[Tuple[int, str]] = []
        if isinstance(defs_data, dict):
            for _sym, occs in defs_data.items():
                for line_no, sig in occs:
                    parsed_defs.append((line_no, sig))
        elif isinstance(defs_data, list):
            for elem in defs_data:
                if isinstance(elem, tuple) and len(elem) >= 2:
                    parsed_defs.append((elem[0], elem[1]))
                elif isinstance(elem, dict) and "line" in elem and "signature" in elem:
                    parsed_defs.append((elem["line"], elem["signature"]))
                elif isinstance(elem, str):
                    # parse "Line X: signature"
                    m = re.match(r'^\s*(?:Line\s+)?(\d+)[:\s]+(.*)$', elem)
                    if m:
                        parsed_defs.append((int(m.group(1)), m.group(2)))
                    else:
                        parsed_defs.append((1, elem.strip()))
        elif isinstance(defs_data, str):
            for line in defs_data.splitlines():
                line_str = line.strip()
                if not line_str:
                    continue
                m = re.match(r'^\s*(?:Line\s+)?(\d+)[:\s]+(.*)$', line_str)
                if m:
                    parsed_defs.append((int(m.group(1)), m.group(2)))
                else:
                    parsed_defs.append((1, line_str))

        for line_no, sig in parsed_defs:
            # Estimate tokens: ~3.8 chars per BPE token, including rendered line prefix ('  │ Line {line_no:4d}: ')
            formatted_line = f"  │ Line {line_no:4d}: {sig}"
            token_est = max(1, math.ceil(len(formatted_line) / 3.8))
            # Definition score combines file salience with base declaration importance
            boost = 1.5 if any(kw in sig.split() for kw in ["class", "struct", "interface"]) else 1.0
            item_score = file_score * boost
            items.append({
                "file": rel_path,
                "file_score": file_score,
                "line_no": line_no,
                "sig": sig,
                "score": item_score,
                "tokens": token_est,
                "density": item_score / token_est
            })

    # Sort candidates by value density: rho_i = score_i / tokens_i descending
    items.sort(key=lambda x: x["density"], reverse=True)

    included_files: Set[str] = set()
    included_by_file: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    consumed_tokens = 0

    for item in items:
        file_path = item["file"]
        header_str = f"📄 {file_path} (rank: {item['file_score']:.4f})\n"
        header_tokens = max(1, math.ceil(len(header_str) / 3.8)) if file_path not in included_files else 0
        total_cost = item["tokens"] + header_tokens

        if consumed_tokens + total_cost <= max_tokens:
            consumed_tokens += total_cost
            included_files.add(file_path)
            included_by_file[file_path].append((item["line_no"], item["sig"]))

    file_scores = {rel_path: score for rel_path, score, _ in files_salience}

    # Render structured hierarchical output sorted by file rank descending
    sorted_included_files = sorted(
        included_by_file.keys(),
        key=lambda f: file_scores.get(f, 0.0),
        reverse=True
    )

    output_lines: List[str] = []
    total_chars = 0
    for f in sorted_included_files:
        f_score = file_scores.get(f, 0.0)
        line_header = f"\n📄 {f} (rank: {f_score:.4f})"
        output_lines.append(line_header)
        total_chars += len(line_header) + 1
        # Sort lines inside each file by line number
        lines_sorted = sorted(included_by_file[f], key=lambda x: x[0])
        for line_no, sig in lines_sorted:
            line_str = f"  │ Line {line_no:4d}: {sig}"
            output_lines.append(line_str)
            total_chars += len(line_str) + 1

    # Enforce strict post-render boundary clamp with O(L) incremental char subtraction
    while output_lines and math.ceil(total_chars / 3.8) > max_tokens:
        removed = output_lines.pop()
        total_chars -= (len(removed) + 1)

    rendered = "\n".join(output_lines).strip()
    if math.ceil(len(rendered) / 3.8) > max_tokens and rendered != "(Empty repo map)":
        max_chars = int(max_tokens * 3.8)
        rendered = rendered[:max_chars].rstrip()

    return rendered


# === REPOMAP BUILDER & CLI ===

def build_repo_map(
    target_dir: str,
    valid_exts: Optional[Set[str]] = None,
    ignore_dirs: Optional[Set[str]] = None,
    budget_tokens: int = 1500,
    focus: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Builds a PageRank-ranked repository map constrained by a token budget.
    Implements CST symbol extraction + sparse PageRank + greedy knapsack packing.
    """
    if valid_exts is None:
        valid_exts = {".dart", ".ts", ".js", ".py", ".go", ".rs", ".swift", ".java", ".kt"}
    if ignore_dirs is None:
        ignore_dirs = {"node_modules", "build", "dist", "coverage", ".git", "ios", "android", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion", ".gemini", ".dart_tool"}

    file_paths: List[str] = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and (not d.startswith('.') or d == '.agents')]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_exts:
                file_paths.append(os.path.join(root, f))

    if not file_paths:
        return {"ranked_files": [], "repo_map": "(No matching code files found)", "total_tokens": 0, "total_files_indexed": 0}

    file_defines: Dict[str, Dict[str, List[Tuple[int, str]]]] = {}
    file_references: Dict[str, Set[str]] = {}
    symbol_definers: Dict[str, Set[str]] = {}

    for fp in file_paths:
        rel_p = os.path.relpath(fp, target_dir).replace("\\", "/")
        defs, refs = extract_file_symbols(fp)
        file_defines[rel_p] = defs
        file_references[rel_p] = refs
        for sym in defs:
            symbol_definers.setdefault(sym, set()).add(rel_p)

    graph: Dict[str, Dict[str, float]] = {rel_p: {} for rel_p in file_defines}

    num_files = max(1, len(file_defines))
    # Connect reference files to defining files with IDF + Import-Affinity weighting
    for ref_file, refs in file_references.items():
        ref_dir = os.path.dirname(ref_file)
        for ident in refs:
            definers = symbol_definers.get(ident)
            if not definers:
                continue
            # Inverse Document Frequency: penalize ubiquitous names like 'main' or 'init'
            idf_weight = math.log(num_files / float(len(definers)))
            if idf_weight < 0.25:
                continue
            for def_file in definers:
                if def_file == ref_file:
                    continue
                def_stem = os.path.splitext(os.path.basename(def_file))[0]
                # Boost edge if ref_file explicitly references the defining module stem or shares package dir
                affinity = 4.0 if (def_stem in refs or os.path.dirname(def_file) == ref_dir) else 1.0
                edge_w = idf_weight * affinity
                graph[ref_file][def_file] = graph[ref_file].get(def_file, 0.0) + edge_w

    # Self-connection baseline
    for rel_p in graph:
        graph[rel_p][rel_p] = graph[rel_p].get(rel_p, 0.0) + 0.1

    # Personalization vector for focus files
    pers: Optional[Dict[str, float]] = None
    if focus:
        pers = {}
        focus_set = set(f.lower().replace("\\", "/") for f in focus)
        for rel_p in graph:
            if any(fc in rel_p.lower() for fc in focus_set):
                pers[rel_p] = 10.0
            elif any(fc in [s.lower() for s in file_defines[rel_p]] for fc in focus_set):
                pers[rel_p] = 5.0

    scores = compute_pagerank(graph, d=0.85, epsilon=1e-6, max_iter=100, personalization=pers)
    sorted_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    files_salience: List[Tuple[str, float, Any]] = []
    ranked_files_meta: List[Dict[str, Any]] = []

    for rel_p, score in sorted_files:
        defs = file_defines[rel_p]
        files_salience.append((rel_p, score, defs))
        ranked_files_meta.append({
            "file": rel_p,
            "rank": round(score, 5),
            "definitions_count": sum(len(v) for v in defs.values())
        })

    repo_map_str = pack_repomap_budget(files_salience, max_tokens=budget_tokens)
    est_tokens = max(1, math.ceil(len(repo_map_str) / 3.8)) if repo_map_str else 0

    return {
        "ranked_files": ranked_files_meta,
        "repo_map": repo_map_str,
        "total_tokens": est_tokens,
        "total_files_indexed": len(file_paths)
    }


def cmd_repomap(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    budget = getattr(args, 'budget', 1500)
    focus = getattr(args, 'focus', None)

    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    result = build_repo_map(target_dir, budget_tokens=budget, focus=focus)

    if getattr(args, 'json', False):
        print(json.dumps(result, indent=2))
    else:
        print(f"🗺️ PageRank Repo-Map (Budget: {budget} tokens, Indexed: {result['total_files_indexed']} files, Output: ~{result['total_tokens']} tokens)")
        print("=" * 70)
        print(result["repo_map"])


# === TOKEN AUDIT & ANALYTICS ===

def calculate_token_stats(root_dir: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Generates per-extension and per-file token analytics across codebase."""
    if files is None:
        ignore_dirs = {'.git', 'node_modules', '.dart_tool', 'build', 'dist', 'ios', 'android', '__pycache__', 'scratch', '.scratch', '.worktrees', '.orion', '.gemini', 'coverage', '.idea', '.vscode', '.gradle', 'target'}
        valid_extensions = {".dart", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".swift", ".java", ".kt", ".md", ".json", ".yaml", ".yml", ".txt", ".html", ".css", ".sql", ".toml"}
        files = []
        for root, dirs, f_list in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in f_list:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_extensions or f in {"Dockerfile", "Makefile", "LICENSE", "VERSION"}:
                    rel_p = os.path.relpath(os.path.join(root, f), root_dir).replace("\\", "/")
                    files.append(rel_p)

    ext_stats: Dict[str, Dict[str, Any]] = {}
    file_records = []
    total_tokens = 0
    total_bytes = 0

    for rel_p in files:
        full_p = os.path.join(root_dir, rel_p)
        try:
            sz = os.path.getsize(full_p)
            with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            tok = max(1, math.ceil(len(content) / 4))
        except Exception:
            continue

        ext = os.path.splitext(rel_p)[1].lower() or "[no-ext]"
        if ext not in ext_stats:
            ext_stats[ext] = {"count": 0, "tokens": 0, "bytes": 0}
        ext_stats[ext]["count"] += 1
        ext_stats[ext]["tokens"] += tok
        ext_stats[ext]["bytes"] += sz

        total_tokens += tok
        total_bytes += sz
        file_records.append((tok, rel_p, sz))

    file_records.sort(reverse=True, key=lambda x: x[0])
    return {
        "total_files": len(files),
        "total_tokens": total_tokens,
        "total_bytes": total_bytes,
        "by_extension": ext_stats,
        "top_files": file_records[:10]
    }


def print_token_stats_table(stats: Dict[str, Any]) -> None:
    """Formats and prints rich token analytics table."""
    print("\n=======================================================")
    print(" 📊 CODEBASE TOKEN & EXTENSION ANALYTICS")
    print("=======================================================")
    print(f"Total Tracked Files: {stats.get('total_files', 0)}")
    print(f"Total Size         : {stats.get('total_bytes', 0) / 1024:.1f} KB")
    print(f"Estimated Tokens   : ~{stats.get('total_tokens', 0):,} tokens\n")

    print(f"{'Extension':<12} {'Files':>8} {'Size (KB)':>12} {'Tokens':>12} {'Share %':>10}")
    print("-" * 57)
    tot_tok = max(1, stats.get("total_tokens", 1))
    for ext, d in sorted(stats.get("by_extension", {}).items(), key=lambda item: item[1]["tokens"], reverse=True):
        pct = (d["tokens"] / tot_tok) * 100
        print(f"{ext:<12} {d['count']:>8} {d['bytes']/1024:>12.1f} {d['tokens']:>12,} {pct:>9.1f}%")

    print("\nTop 5 Largest Files by Token Volume:")
    for tok, path, sz in stats.get("top_files", [])[:5]:
        print(f"  • {path:<45} ~{tok:>7,} tokens ({sz/1024:>6.1f} KB)")
    print("=======================================================\n")


def cmd_tokens(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    stats = calculate_token_stats(target_dir)
    print_token_stats_table(stats)


# === SECURITY AUDIT ===

def cmd_security(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    baseline_file = getattr(args, 'baseline', None)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    for p in (script_dir, parent_dir):
        if p not in sys.path:
            sys.path.insert(0, p)
    from security import SecurityAuditor

    auditor = SecurityAuditor(target_dir, baseline_file=baseline_file)
    active, suppressed = auditor.audit_directory()

    if getattr(args, 'record_baseline', False):
        auditor.baseline.save(active, auditor.root_dir)
        print(f"[BASELINE] Recorded {len(active)} findings to {auditor.baseline_path}")
        sys.exit(0)

    if getattr(args, 'json', False):
        print(json.dumps({
            "target": os.path.abspath(target_dir),
            "active_findings": active,
            "suppressed_count": len(suppressed),
            "verdict": "REJECT" if any(f.get('severity') == 'CRITICAL' for f in active) else ("CAUTION" if active else "APPROVE")
        }, indent=2))
        sys.exit(1 if active else 0)

    print(f"\n🛡️ Security & Integrity Audit: {os.path.abspath(target_dir)}")
    print("=" * 60)
    print(f"Active Findings : {len(active)}")
    print(f"Suppressed      : {len(suppressed)} baselined items\n")

    if active:
        for idx, item in enumerate(active, 1):
            sev = item.get('severity', 'HIGH')
            print(f"[{idx}] [{sev}] {item.get('category')}: {item.get('message')}")
            print(f"     File: {item.get('file')}:{item.get('line', '?')}")
            if item.get('snippet'):
                print(f"     Code: {item.get('snippet')}")
        print("\n[FAIL] Security violations detected.")
        sys.exit(1)
    else:
        print("[PASS] Security & AST Integrity Verified: 0 vulnerabilities found.")
        sys.exit(0)


# === CLI DISPATCH ===

def main() -> None:
    # Direct invocation support: python scanner.py <path> [--budget 1500]
    known_subcmds = {"targets", "map", "repomap", "tokens", "security", "-h", "--help"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_subcmds:
        if sys.argv[1].startswith("-") and sys.argv[1] not in {"-h", "--help"}:
            sys.argv.insert(1, "repomap")
        elif not sys.argv[1].startswith("-"):
            sys.argv.insert(1, "repomap")

    parser = argparse.ArgumentParser(description="Code Analysis, AST Symbol Extraction & Salience Scanner")
    subparsers = parser.add_subparsers(dest="command")
    
    # Targets
    parser_targets = subparsers.add_parser("targets", help="Find files eligible for auditing")
    parser_targets.add_argument("dir", nargs="?", default=".", help="Root directory to scan (default: .)")
    parser_targets.add_argument("--ext", nargs="+", help="File extensions to include")
    parser_targets.add_argument("--exclude", nargs="+", help="Directories to exclude")
    parser_targets.add_argument("--json", action="store_true", help="Output in raw JSON format")
    
    # Map
    parser_map = subparsers.add_parser("map", help="Generate structural code map of directory")
    parser_map.add_argument("dir", nargs="?", default=".", help="Directory to map (default: .)")
    parser_map.add_argument("--max-depth", type=int, default=5, help="Maximum directory depth")
    parser_map.add_argument("--ranked", action="store_true", help="Rank code map using PageRank symbol topology")
    parser_map.add_argument("--budget", type=int, default=1500, help="Token budget for ranked map (default: 1500)")
    parser_map.add_argument("--focus", nargs="+", help="Files or symbols to personalize/focus PageRank on")

    # RepoMap (PageRank-ranked code map)
    parser_repomap = subparsers.add_parser("repomap", help="Generate PageRank-ranked repository map within token budget")
    parser_repomap.add_argument("dir", nargs="?", default=".", help="Directory to map (default: .)")
    parser_repomap.add_argument("--budget", type=int, default=1500, help="Maximum token budget (default: 1500)")
    parser_repomap.add_argument("--focus", nargs="+", help="Files or symbols to personalize/focus PageRank on")
    parser_repomap.add_argument("--json", action="store_true", help="Output in raw JSON format")
    
    # Tokens
    parser_tokens = subparsers.add_parser("tokens", help="Audit token consumption across directory")
    parser_tokens.add_argument("dir", nargs="?", default=".", help="Directory to audit (default: .)")

    # Security
    parser_sec = subparsers.add_parser("security", help="Audit AST and code security")
    parser_sec.add_argument("dir", nargs="?", default=".", help="Directory to audit (default: .)")
    parser_sec.add_argument("--baseline", help="Custom baseline file path")
    parser_sec.add_argument("--record-baseline", action="store_true", help="Save active findings to baseline file")
    parser_sec.add_argument("--json", action="store_true", help="Output results in JSON format")

    for sub_p in (parser_targets, parser_map, parser_repomap, parser_tokens, parser_sec):
        sub_p.add_argument("--dir", dest="dir_flag", help="Target directory or file override")

    parsed_args = parser.parse_args()
    if getattr(parsed_args, "dir_flag", None):
        parsed_args.dir = parsed_args.dir_flag
    
    if parsed_args.command == "targets":
        cmd_targets(parsed_args)
    elif parsed_args.command == "map":
        cmd_map(parsed_args)
    elif parsed_args.command == "repomap":
        cmd_repomap(parsed_args)
    elif parsed_args.command == "tokens":
        cmd_tokens(parsed_args)
    elif parsed_args.command == "security":
        cmd_security(parsed_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
