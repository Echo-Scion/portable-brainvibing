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
import sqlite3

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
    multiline_mode = None  # '>', '>-', '|', or '|-'

    def _flush_multiline() -> None:
        nonlocal current_key, multiline_mode
        if current_key and multiline_mode and isinstance(metadata.get(current_key), list):
            joiner = " " if multiline_mode.startswith(">") else "\n"
            metadata[current_key] = joiner.join(metadata[current_key]).strip()
        multiline_mode = None

    for line in raw_yaml.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith('#'):
            continue

        if (line.startswith(' ') or line.startswith('\t')) and current_key and multiline_mode:
            if isinstance(metadata.get(current_key), list):
                metadata[current_key].append(trimmed)
            continue
        elif multiline_mode:
            _flush_multiline()

        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()

            if val in (">", ">-", "|", "|-"):
                current_key = key
                multiline_mode = val
                metadata[key] = []
            elif val == "":
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
            if isinstance(metadata.get(current_key), list):
                metadata[current_key].append(item)

    _flush_multiline()
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

def _should_traverse_dir(d: str, ignore_dirs: Set[str], include_agents_runtime: bool = False) -> bool:
    """Unified directory traversal predicate across all scanner commands."""
    if d in ignore_dirs or d.lower() in ignore_dirs:
        return False
    if d.startswith("."):
        return (d == ".agents" and include_agents_runtime) or d in {".github", ".storybook"}
    return True


def get_audit_targets(directory: str, extensions: List[str], exclude_dirs: List[str], include_agents_runtime: bool = False) -> List[str]:
    """
    Deterministically scans a directory for files to audit.
    Filters out common boilerplate, library, and hidden directories.
    """
    targets = []
    exclude_set = {d.lower() for d in exclude_dirs}
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if _should_traverse_dir(d, exclude_set, include_agents_runtime)]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions:
                full_path = os.path.abspath(os.path.join(root, file))
                targets.append(full_path)
                
    return sorted(targets)


def cmd_targets(args: argparse.Namespace) -> None:
    target_dir = getattr(args, 'dir', '.')
    default_excludes = ["node_modules", "build", "dist", "coverage", ".git", "ios", "android", ".gemini", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion"]
    default_exts = [".py", ".dart", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".kt", ".java"]
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
        
    include_agents = (
        getattr(args, 'include_agents', False) or
        os.path.exists(os.path.join(target_dir, ".agents", "skills")) or
        os.path.basename(os.path.abspath(target_dir)) in (".agents", "_foundation")
    )
    targets = get_audit_targets(target_dir, exts, excludes, include_agents_runtime=include_agents)
    
    if getattr(args, 'json', False):
        print(json.dumps(targets, indent=2))
    else:
        print(f"--- Found {len(targets)} audit targets in '{target_dir}' ---")
        for i, target in enumerate(targets, 1):
            print(f"{i}. {target}")


# === SKELETON MAPPER ===

def _find_brace_block_end(lines: List[str], start_line: int, fallback_end: int) -> int:
    """Finds the line number of matching closing brace '}' using stateful multiline string/comment tracking."""
    depth = 0
    started = False
    in_block_comment = False
    in_multiline_str: Optional[str] = None
    max_scan = min(len(lines), start_line + 5000)

    for idx in range(start_line - 1, max_scan):
        line = lines[idx]
        net, in_block_comment, in_multiline_str = _count_effective_braces_stateful(
            line, in_block_comment, in_multiline_str
        )
        if net > 0 or ("{" in line and not in_block_comment):
            if depth + net > 0:
                started = True
        depth += net
        if started and depth <= 0:
            return idx + 1
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
        re.compile(r'^\s*(?:export\s+)?(?:abstract\s+|pub(?:\([^)]*\))?\s+|public\s+|private\s+)?(?:class|struct|interface|trait|enum)\s+([A-Za-z0-9_]+)'),
        re.compile(r'^\s*(?:def|async def|fn|function|fun|func)\b(?:\s+\([^)]+\))?\s+([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\('),
        re.compile(r'^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\('),
        re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)(?:\s*:\s*[^=]+)?\s*=\s*(?:async\s*)?(?:<[^>]+>\s*)?\([^;]*?\)\s*(?::\s*[^=]+)?=>\s*\{?'),
        re.compile(r'^\s*(?!(?:if|for|while|catch|switch|return)\s*\()((?:[a-zA-Z<>\[\],.?|&_]+\s+)?([A-Za-z0-9_]+)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?:->\s*[^;{\n]+|:\s*[^;{\n]+|\s+[A-Za-z0-9_<>\[\],.?|&()]+)?\s*(?:async\*?|sync\*)?\s*[{=>])'),
    ]

    raw_hits: List[Tuple[int, str]] = []  # (line_num, sig)
    try:
        lines = content.splitlines(keepends=True) if content is not None else None
        if lines is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            if len(line) > 500:
                continue
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


def _append_trailing_comma_safely(line: str) -> str:
    """Appends trailing comma before trailing comments, safely ignoring # inside string literals."""
    stripped = line.rstrip()
    if stripped.endswith(","):
        return line
    in_str = None
    for idx, ch in enumerate(stripped):
        if in_str:
            if ch == "\\" and idx + 1 < len(stripped):
                continue
            if ch == in_str:
                in_str = None
        elif ch in ('"', "'"):
            in_str = ch
        elif ch == "#":
            code_part = stripped[:idx].rstrip()
            comm_part = stripped[idx:]
            return f"{code_part},  {comm_part}" if not code_part.endswith(",") else line
    return stripped + ","


def skeletonize_python(code: str, include_line_numbers: bool = False) -> str:
    """
    Pillar 1 Python AST Skeletonizer.
    Extracts decorators, classes, multiline signatures, @dataclass/Enum fields,
    docstrings, and type annotations while collapsing function implementation bodies.
    Supports source-true line numbers and preserves try/except fallback blocks.
    """
    try:
        import ast
        tree = ast.parse(code)
    except SyntaxError:
        return code

    lines = code.splitlines()
    items: List[Tuple[Optional[int], str]] = []

    def emit(lineno: Optional[int], text: str) -> None:
        items.append((lineno, text))

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

    _NOISE_CALLS = {
        "len", "str", "int", "float", "bool", "list", "dict", "set", "tuple",
        "append", "extend", "join", "split", "strip", "lstrip", "rstrip",
        "replace", "lower", "upper", "startswith", "endswith", "get", "items",
        "keys", "values", "print", "isinstance", "getattr", "setattr", "hasattr",
        "max", "min", "sum", "sorted", "enumerate", "zip", "range", "any", "all",
        "round", "abs", "ord", "chr", "repr", "format", "add", "update", "pop",
    }
    _SQL_TABLE_RE = re.compile(
        r"\b(SELECT\s+[^;]{1,300}?\s+FROM|INSERT\s+(?:OR\s+\w+\s+)?INTO|UPDATE|DELETE\s+FROM|"
        r"CREATE\s+(?:VIRTUAL\s+)?TABLE(?:\s+IF\s+NOT\s+EXISTS)?|DROP\s+TABLE(?:\s+IF\s+EXISTS)?|PRAGMA)\s+([a-zA-Z0-9_]+)",
        re.IGNORECASE | re.DOTALL,
    )

    def _summarize_body_contracts(node: ast.AST) -> str:
        state_attrs: List[str] = []
        sql_ops: List[str] = []
        io_globals: List[str] = []
        raises_catches: List[str] = []
        calls: List[str] = []

        for sub in ast.walk(node):
            # 1. State attributes (self.<attr> = ...)
            if isinstance(sub, (ast.Assign, ast.AnnAssign)):
                targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
                for t in targets:
                    if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
                        entry = f"self.{t.attr}"
                        if entry not in state_attrs:
                            state_attrs.append(entry)
            # 2. Global mutations
            elif isinstance(sub, ast.Global):
                for g_name in sub.names:
                    entry = f"global {g_name}"
                    if entry not in io_globals:
                        io_globals.append(entry)
            # 3. Calls: SQL, IO/Subprocess, and domain calls
            elif isinstance(sub, ast.Call):
                call_name = None
                full_call = None
                if isinstance(sub.func, ast.Name):
                    call_name = sub.func.id
                    full_call = call_name
                elif isinstance(sub.func, ast.Attribute):
                    call_name = sub.func.attr
                    if isinstance(sub.func.value, ast.Name):
                        full_call = f"{sub.func.value.id}.{call_name}"
                    else:
                        full_call = call_name

                if call_name in ("execute", "executescript", "executemany") and sub.args:
                    arg0 = sub.args[0]
                    raw_sql = ""
                    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                        raw_sql = arg0.value
                    elif isinstance(arg0, ast.JoinedStr):
                        raw_sql = "".join(
                            p.value for p in arg0.values if isinstance(p, ast.Constant) and isinstance(p.value, str)
                        )
                    if raw_sql:
                        for m in _SQL_TABLE_RE.finditer(raw_sql):
                            verb = m.group(1).split()[0].upper()
                            tbl = m.group(2)
                            op_str = f"{verb} {tbl}"
                            if op_str not in sql_ops:
                                sql_ops.append(op_str)

                if full_call in (
                    "open", "os.replace", "os.remove", "os.unlink", "os.makedirs",
                    "shutil.move", "shutil.rmtree", "shutil.copy", "shutil.copy2",
                    "subprocess.run", "subprocess.Popen", "subprocess.check_output",
                ):
                    if full_call not in io_globals:
                        io_globals.append(full_call)
                elif call_name and call_name not in _NOISE_CALLS and call_name not in calls:
                    calls.append(call_name)

            # 4. Raises & Catches
            elif isinstance(sub, ast.Raise) and sub.exc is not None:
                exc_name = None
                if isinstance(sub.exc, ast.Call) and isinstance(sub.exc.func, ast.Name):
                    exc_name = sub.exc.func.id
                elif isinstance(sub.exc, ast.Name):
                    exc_name = sub.exc.id
                if exc_name:
                    tag = f"raise {exc_name}"
                    if tag not in raises_catches:
                        raises_catches.append(tag)
            elif isinstance(sub, ast.ExceptHandler):
                if sub.type is None:
                    tag = "except <bare>"
                elif isinstance(sub.type, ast.Name):
                    tag = f"except {sub.type.id}"
                elif isinstance(sub.type, ast.Tuple):
                    names = [elt.id for elt in sub.type.elts if isinstance(elt, ast.Name)]
                    tag = f"except ({','.join(names)})" if names else "except (...)"
                else:
                    tag = "except"
                if tag not in raises_catches:
                    raises_catches.append(tag)

        parts: List[str] = []
        if state_attrs:
            parts.append(f"State: {', '.join(state_attrs[:6])}")
        if sql_ops:
            parts.append(f"SQL: {', '.join(sql_ops[:5])}")
        if io_globals:
            parts.append(f"IO/Global: {', '.join(io_globals[:5])}")
        if raises_catches:
            parts.append(f"Raises/Catches: {', '.join(raises_catches[:5])}")
        if calls and len(parts) < 3:
            parts.append(f"Calls: {', '.join(calls[:5])}")
        return (" | " + " | ".join(parts)) if parts else ""

    def _extract_preserved_body_lines(node: ast.AST, indent: str = "    ") -> List[Tuple[int, str]]:
        """Preserves self.<attr> = ... in __init__ and SQL CREATE TABLE / schema lines inside functions."""
        preserved: List[Tuple[int, str]] = []
        seen_lines: Set[int] = set()
        is_init = getattr(node, "name", "") == "__init__"
        body = getattr(node, "body", [])

        for stmt in body:
            if is_init and isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                if any(
                    isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self"
                    for t in targets
                ):
                    s_l = stmt.lineno - 1
                    e_l = getattr(stmt, "end_lineno", None) or stmt.lineno
                    if e_l - s_l <= 4:
                        for idx in range(s_l, e_l):
                            if (idx + 1) not in seen_lines:
                                seen_lines.add(idx + 1)
                                preserved.append((idx + 1, lines[idx]))

        # Also scan for SQL CREATE TABLE / VIRTUAL TABLE / PRAGMA inside function body
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                if re.search(r"\bCREATE\s+(?:VIRTUAL\s+)?TABLE\b", sub.value, re.IGNORECASE):
                    s_l = getattr(sub, "lineno", 1) - 1
                    e_l = getattr(sub, "end_lineno", None) or (s_l + 1)
                    for idx in range(max(0, s_l - 1), min(len(lines), e_l)):
                        line_txt = lines[idx]
                        stripped_sql = line_txt.strip()
                        if any(
                            kw in stripped_sql.upper()
                            for kw in ("CREATE TABLE", "CREATE VIRTUAL TABLE", "PRIMARY KEY", "FOREIGN KEY", "UNIQUE")
                        ):
                            if (idx + 1) not in seen_lines:
                                seen_lines.add(idx + 1)
                                preserved.append((idx + 1, f"{indent}# [SQL Schema] {stripped_sql}"))

        preserved.sort(key=lambda x: x[0])
        return preserved

    def _emit_header_and_concise_doc(node: ast.AST, indent: str = "    ") -> int:
        s = _node_start_idx(node)
        e, has_doc = _header_and_doc_end_idx(node)
        if not has_doc:
            for idx in range(s, e):
                emit(idx + 1, lines[idx])
            return e
        first_stmt = node.body[0]
        doc_start = first_stmt.lineno - 1
        doc_end = (first_stmt.end_lineno or first_stmt.lineno)
        # Emit signature lines
        for idx in range(s, doc_start):
            emit(idx + 1, lines[idx])
        # Emit concise docstring (up to 2 lines; collapse verbose multi-paragraph docstrings)
        if doc_end - doc_start <= 2:
            for idx in range(doc_start, doc_end):
                emit(idx + 1, lines[idx])
        else:
            raw_doc = first_stmt.value.value.strip()
            first_line = next((ln.strip() for ln in raw_doc.splitlines() if ln.strip()), "")
            if len(first_line) > 110:
                first_line = first_line[:107].rstrip() + "..."
            emit(doc_start + 1, f'{indent}"""{first_line}"""')
        return e

    def process_function(node: ast.AST, indent: str = "    ") -> None:
        # Compute exact base indentation from actual physical definition line
        s_line_idx = node.lineno - 1
        sig_line = lines[s_line_idx] if 0 <= s_line_idx < len(lines) else ""
        phys_indent = " " * (len(sig_line) - len(sig_line.lstrip()))
        body_indent = phys_indent + "    " if phys_indent else indent

        e = _emit_header_and_concise_doc(node, indent=body_indent)
        preserved = _extract_preserved_body_lines(node, indent=body_indent)
        end_line = getattr(node, "end_lineno", None) or (e + 1)
        valid_preserved = [(p_l, p_t) for p_l, p_t in preserved if p_l > e]

        if not valid_preserved:
            start_omitted = e + 1
            end_omitted = end_line
            body_omitted = max(1, end_omitted - start_omitted + 1)
            digest = _summarize_body_contracts(node)
            if start_omitted <= end_omitted:
                if include_line_numbers:
                    emit(None, f"{body_indent}...  # [Body omitted for audit (L{start_omitted}-L{end_omitted}): {body_omitted} lines{digest}]")
                else:
                    emit(None, f"{body_indent}...  # [Body omitted for audit: {body_omitted} lines{digest}]")
        else:
            first_p = min(p[0] for p in valid_preserved)
            last_p = max(p[0] for p in valid_preserved)
            if first_p > e + 1:
                gap = first_p - (e + 1)
                if include_line_numbers:
                    emit(None, f"{body_indent}...  # [Prelude omitted for audit (L{e+1}-L{first_p-1}): {gap} lines]")
                else:
                    emit(None, f"{body_indent}...  # [Prelude omitted for audit: {gap} lines]")
            for p_lineno, p_text in valid_preserved:
                emit(p_lineno, p_text)
            if end_line > last_p:
                gap = end_line - last_p
                digest = _summarize_body_contracts(node)
                if include_line_numbers:
                    emit(None, f"{body_indent}...  # [Remaining body omitted for audit (L{last_p+1}-L{end_line}): {gap} lines{digest}]")
                else:
                    emit(None, f"{body_indent}...  # [Remaining body omitted for audit: {gap} lines{digest}]")

    def process_class(node: ast.ClassDef, depth: int = 0) -> None:
        child_indent = "    " * (depth + 2)
        class_body_indent = "    " * (depth + 1)
        _, has_doc = _header_and_doc_end_idx(node)
        _emit_header_and_concise_doc(node, indent=class_body_indent)
        emitted_members = 0

        for idx_c, child in enumerate(node.body):
            if idx_c == 0 and has_doc:
                emitted_members += 1
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                process_function(child, indent=child_indent)
                emitted_members += 1
            elif isinstance(child, ast.ClassDef):
                process_class(child, depth=depth + 1)
                emitted_members += 1
            elif isinstance(child, (ast.AnnAssign, ast.Assign)):
                _emit_assign(child, indent=child_indent)
                emitted_members += 1

        if emitted_members == 0:
            emit(None, f"{'    ' * (depth + 1)}...")

    def _emit_assign(node: ast.AST, indent: str = "") -> None:
        s = node.lineno - 1
        e = getattr(node, "end_lineno", None) or node.lineno
        val = getattr(node, "value", None)
        # Preserve SQL schema definitions completely even if >5 lines
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            if re.search(r"\bCREATE\s+(?:VIRTUAL\s+)?TABLE\b", val.value, re.IGNORECASE):
                for idx in range(s, e):
                    emit(idx + 1, lines[idx])
                return
        if e - s <= 5:
            for idx in range(s, e):
                emit(idx + 1, lines[idx])
            return

        if isinstance(val, (ast.List, ast.Set, ast.Tuple)) and val.elts:
            emitted_line_indices = set()
            first_elt = val.elts[0]
            for idx in range(s, first_elt.lineno - 1):
                if idx not in emitted_line_indices:
                    emit(idx + 1, lines[idx])
                    emitted_line_indices.add(idx)
            keep_elts = val.elts[:2]
            for elt in keep_elts:
                s_elt = elt.lineno - 1
                e_elt = getattr(elt, "end_lineno", None) or elt.lineno
                for idx in range(s_elt, e_elt):
                    if idx not in emitted_line_indices:
                        line_to_emit = lines[idx]
                        if idx == e_elt - 1:
                            line_to_emit = _append_trailing_comma_safely(line_to_emit)
                        emit(idx + 1, line_to_emit)
                        emitted_line_indices.add(idx)
            omitted = len(val.elts) - len(keep_elts)
            if omitted > 0:
                last_k = keep_elts[-1]
                last_k_end = getattr(last_k, "end_lineno", last_k.lineno)
                emit(None, f"{indent}# ... [{omitted} elements elided (L{last_k_end+1}-L{e-1})]")
            if (e - 1) not in emitted_line_indices:
                emit(e, lines[e - 1])
        elif isinstance(val, ast.Dict) and val.keys:
            emitted_line_indices = set()
            first_k = val.keys[0]
            if first_k is not None:
                for idx in range(s, first_k.lineno - 1):
                    if idx not in emitted_line_indices:
                        emit(idx + 1, lines[idx])
                        emitted_line_indices.add(idx)
            else:
                emit(s + 1, lines[s])
                emitted_line_indices.add(s)
            keep_pairs = list(zip(val.keys, val.values))[:2]
            for k, v in keep_pairs:
                if isinstance(v, ast.Constant) and isinstance(v.value, str) and ((getattr(v, "end_lineno", None) or v.lineno) - v.lineno > 2):
                    k_str = lines[k.lineno - 1].split(':')[0].strip() if k else ''
                    emit(k.lineno if k else None, f'{indent}    {k_str}: "...",  # [Template content elided]')
                    if k:
                        emitted_line_indices.add(k.lineno - 1)
                else:
                    s_p = (k.lineno - 1) if k else (v.lineno - 1)
                    e_p = getattr(v, "end_lineno", None) or v.lineno
                    for idx in range(s_p, e_p):
                        if idx not in emitted_line_indices:
                            line_to_emit = lines[idx]
                            if idx == e_p - 1:
                                line_to_emit = _append_trailing_comma_safely(line_to_emit)
                            emit(idx + 1, line_to_emit)
                            emitted_line_indices.add(idx)
            omitted = len(val.keys) - len(keep_pairs)
            if omitted > 0:
                emit(None, f"{indent}# ... [{omitted} items elided]")
            if (e - 1) not in emitted_line_indices:
                emit(e, lines[e - 1])
        else:
            emit(s + 1, lines[s])
            emit(None, f"{indent}# ... [Value elided: {e - s} lines (L{s+2}-L{e-1})]")
            emit(e, lines[e - 1])

    def _emit_child_node(sub: ast.AST, indent: str = "    ") -> None:
        if isinstance(sub, (ast.Import, ast.ImportFrom)):
            s = sub.lineno - 1
            e = getattr(sub, "end_lineno", None) or sub.lineno
            for idx in range(s, e):
                emit(idx + 1, lines[idx])
        elif isinstance(sub, (ast.Assign, ast.AnnAssign)):
            _emit_assign(sub, indent=indent)
        elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
            process_function(sub, indent=indent)
        elif isinstance(sub, ast.ClassDef):
            process_class(sub, depth=1)
        elif isinstance(sub, ast.Try):
            _emit_try(sub, indent=indent)

    def _emit_try(node: ast.Try, indent: str = "") -> None:
        s_try = node.lineno - 1
        s_body_start = node.body[0].lineno - 1 if node.body else (s_try + 1)
        for idx in range(s_try, s_body_start):
            emit(idx + 1, lines[idx])
        before_count = len(items)
        for sub in node.body:
            _emit_child_node(sub, indent=indent + "    ")
        if len(items) == before_count:
            emit(None, f"{indent}    ...  # [Implementation elided]")
        for handler in node.handlers:
            h_start = handler.lineno - 1
            h_body_start = handler.body[0].lineno - 1 if handler.body else (h_start + 1)
            for idx in range(h_start, h_body_start):
                emit(idx + 1, lines[idx])
            h_line = lines[h_start]
            base_indent = " " * (len(h_line) - len(h_line.lstrip()))
            is_import_fallback = False
            if handler.type:
                for sub_n in ast.walk(handler.type):
                    if isinstance(sub_n, ast.Name) and sub_n.id in ("ImportError", "ModuleNotFoundError"):
                        is_import_fallback = True
                        break
            h_count_before = len(items)
            if is_import_fallback:
                for sub in handler.body:
                    _emit_child_node(sub, indent=base_indent + "    ")
            if len(items) == h_count_before:
                emit(None, f"{base_indent}    ...  # [Exception handling logic]")
        if getattr(node, "orelse", None):
            for sub in node.orelse:
                _emit_child_node(sub, indent=indent + "    ")
        if getattr(node, "finalbody", None):
            for sub in node.finalbody:
                _emit_child_node(sub, indent=indent + "    ")

    def _emit_top_node(node: ast.AST) -> None:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            s = node.lineno - 1
            e = getattr(node, "end_lineno", None) or node.lineno
            for idx in range(s, e):
                emit(idx + 1, lines[idx])
        elif isinstance(node, ast.ClassDef):
            process_class(node, depth=0)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            process_function(node, indent="    ")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            _emit_assign(node, indent="")
        elif isinstance(node, ast.Try):
            _emit_try(node, indent="")
        elif isinstance(node, ast.If):
            s = node.lineno - 1
            e = getattr(node, "end_lineno", None) or node.lineno
            if e - s <= 8:
                for idx in range(s, e):
                    emit(idx + 1, lines[idx])
            else:
                body_start = node.body[0].lineno - 1 if node.body else (s + 1)
                for idx in range(s, body_start):
                    emit(idx + 1, lines[idx])
                h_line = lines[s]
                base_indent = " " * (len(h_line) - len(h_line.lstrip()))
                before_cnt = len(items)
                for sub in node.body:
                    _emit_child_node(sub, indent=base_indent + "    ")
                if len(items) == before_cnt:
                    emit(None, f"{base_indent}    ...")
                for sub in getattr(node, "orelse", []):
                    _emit_child_node(sub, indent=base_indent + "    ")

    for node in tree.body:
        _emit_top_node(node)

    if include_line_numbers:
        out_lines = []
        for lineno, text in items:
            if lineno is not None:
                out_lines.append(f"{lineno:4d} | {text}")
            else:
                out_lines.append(f" ... | {text}")
        return "\n".join(out_lines) if out_lines else code
    else:
        out_lines = [text for _, text in items]
        return "\n".join(out_lines) if out_lines else code


def skeletonize_markdown(content: str, include_line_numbers: bool = False) -> str:
    """
    Markdown Structural Skeletonizer:
    Preserves YAML frontmatter, Heading hierarchy (#/##/###), routing/rule tables, and primary command bullets;
    folds narrative prose paragraphs and example code blocks to maximize signal-to-token ratio.
    """
    lines = content.splitlines()
    items: List[Tuple[Optional[int], str]] = []
    in_frontmatter = False
    in_code_block = False
    code_block_lines = 0

    for idx, line in enumerate(lines):
        lineno = idx + 1
        stripped = line.strip()
        if idx == 0 and stripped == "---":
            in_frontmatter = True
            items.append((lineno, line))
            continue
        if in_frontmatter:
            items.append((lineno, line))
            if stripped == "---":
                in_frontmatter = False
            continue

        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lines = 0
            else:
                in_code_block = False
                if code_block_lines > 0:
                    items.append((None, f"<!-- [Code block folded: {code_block_lines} lines] -->"))
            continue

        if in_code_block:
            code_block_lines += 1
            if code_block_lines == 1 and (
                stripped.startswith("python ")
                or stripped.startswith("orion ")
                or stripped.startswith("digestpack ")
                or stripped.startswith("npm ")
            ):
                items.append((lineno, f"- Cmd: `{stripped[:240]}`"))
            continue

        if not stripped:
            continue

        if (
            stripped.startswith("#")
            or stripped.startswith("|")
            or stripped == "---"
        ):
            items.append((lineno, line))
        elif (
            stripped.startswith("- **")
            or stripped.startswith("* **")
            or re.match(r"^\d+\.\s+\*\*", stripped)
            or re.match(r"^[-*]\s+`[^`]+`", stripped)
        ):
            # Primary rule/command bullet: preserve full contract clause (<=360 chars)
            if len(line) > 360:
                truncated = line[:357]
                last_space = truncated.rfind(" ")
                if last_space > 240:
                    truncated = truncated[:last_space]
                items.append((lineno, truncated.rstrip() + "..."))
            else:
                items.append((lineno, line))
        elif (
            stripped.startswith("- ")
            or stripped.startswith("* ")
            or re.match(r"^\d+\.\s+", stripped)
        ):
            if ("python " in stripped or ".agents/" in stripped or "`" in stripped) and len(stripped) <= 240:
                items.append((lineno, line))

    if include_line_numbers:
        out_lines = []
        for lno, text in items:
            if lno is not None:
                out_lines.append(f"{lno:4d} | {text}")
            else:
                out_lines.append(f" ... | {text}")
        return "\n".join(out_lines) if out_lines else content
    else:
        out_lines = [text for _, text in items]
        return "\n".join(out_lines) if out_lines else content


SUPPORTED_SKELETON_EXTENSIONS = {
    'py', 'ts', 'tsx', 'js', 'jsx', 'mjs', 'cjs',
    'dart', 'rs', 'go', 'kt', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'swift'
}


def _count_effective_delimiters_stateful(
    line: str,
    in_block_comment: bool = False,
    in_multiline_str: Optional[str] = None,
) -> Tuple[int, int, bool, Optional[str]]:
    """Counts { / } (braces) and ( / ) (parens) while ignoring string literals and block comments."""
    i = 0
    net_braces = 0
    net_parens = 0
    in_str = in_multiline_str
    if len(line) > 2000 and in_str is None and not in_block_comment:
        line = line[:2000]
    n = len(line)
    while i < n:
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
            if len(in_str) == 3 and line[i:i+3] == in_str:
                in_str = None
                i += 3
                continue
            if len(in_str) == 1 and line[i] == in_str:
                in_str = None
            i += 1
            continue
        if line[i:i+2] == '/*':
            in_block_comment = True
            i += 2
            continue
        if line[i:i+2] == '//' or line[i] == '#':
            break
        prev_char = line[:i].rstrip()[-1:]
        if line[i] == '/' and line[i:i+2] != '/>' and (i == 0 or (prev_char and prev_char in '(=,:[({;,!&|?+*^~')):
            j = i + 1
            while j < n:
                if line[j] == '\\':
                    j += 2
                elif line[j] == '/':
                    i = j + 1
                    break
                elif line[j] in '\r\n':
                    break
                else:
                    j += 1
            else:
                i = n
            continue
        if line[i:i+3] in ('"""', "'''"):
            in_str = line[i:i+3]
            i += 3
            continue
        if line[i] in ('"', "'", '`'):
            if line[i] == "'":
                if re.match(r"^'[a-zA-Z_]\w*\b(?!')", line[i:]):
                    i += 1
                    continue
            in_str = line[i]
            i += 1
            continue
        if line[i] == '{':
            net_braces += 1
        elif line[i] == '}':
            net_braces -= 1
        elif line[i] == '(':
            net_parens += 1
        elif line[i] == ')':
            net_parens -= 1
        i += 1
    # Single-line quotes reset at EOL; multiline template backticks and triple quotes persist across lines
    if in_str in ('"', "'"):
        in_str = None
    return net_braces, net_parens, in_block_comment, in_str


def _count_effective_braces_stateful(
    line: str,
    in_block_comment: bool = False,
    in_multiline_str: Optional[str] = None,
) -> Tuple[int, bool, Optional[str]]:
    """Counts { and } while ignoring string literals and block comments."""
    nb, _, bc, ms = _count_effective_delimiters_stateful(line, in_block_comment, in_multiline_str)
    return nb, bc, ms


def _count_effective_braces(line: str) -> int:
    """Counts { and } while ignoring string literals and comments via unified single-pass tokenization."""
    return _count_effective_braces_stateful(line, False, None)[0]


def skeletonize_code(code: str, ext: str, include_line_numbers: bool = False) -> str:
    """
    Pillar 1/2 Multi-language AST/CST Skeletonizer.
    Preserves data contracts, interfaces, types, structs, enums 100% intact.
    Hollows out only method/function implementation bodies into [Lstart-Lend].
    """
    ext = ext.lower().lstrip('.')
    if ext == 'py':
        return skeletonize_python(code, include_line_numbers=include_line_numbers)
    if ext in ('md', 'mdc'):
        return skeletonize_markdown(code, include_line_numbers=include_line_numbers)
    if ext not in SUPPORTED_SKELETON_EXTENSIONS:
        return code

    lines = code.splitlines()
    out = []

    intact_type_pattern = re.compile(
        r'^\s*(?:(?:\b(?:export|pub(?:\([^)]*\))?|abstract|default|sealed|readonly)\s+)*)(?:interface|type|enum|trait|struct)\b'
    )
    func_pattern = re.compile(
        # 1. Explicit keyword functions: fn, func, fun, function, def
        r'^\s*(?:\b(?:export|pub(?:\([^)]*\))?|abstract|default|async|static|override|private|protected|public|inline|suspend|extern|const|unsafe)\s+)*'
        r'(?:func(?:\s+\([^)]+\))?|fn|fun|function|def)\b|'
        # 2. JS/TS/Dart Arrow functions & React components: [export] const/let foo [: Type] = [async] (...) [: Ret] => [{]
        r'^\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+[A-Za-z_$][A-Za-z0-9_$]*(?:\s*:\s*[^=]+)?\s*=\s*(?:async\s*)?(?:<[^>]+>\s*)?\([^;]*?\)\s*(?::\s*[^=]+)?=>\s*\{?|'
        # 3. Single-line class method declarations
        r'^\s*(?:\b(?:public|private|protected|static|final|override|async|default)\s+)*[\w<>\[\],.?]+\s+(?!(?:if|for|while|catch|switch|return|with)\b)[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?:[:\->]\s*[\w<>\[\],.?|&\s]+)?\s*(?:async\*?|sync\*?)?\s*\{|'
        # 4. Multi-line method signature declaration start (Dart, TS, Java, Kotlin, C#)
        r'^\s*(?:\b(?:public|private|protected|static|final|override|async|abstract|synchronized|virtual|inline)\s+){0,5}'
        r'(?:[\w<>\[\],.?|&]+\s+){1,3}(?!(?:if|for|while|catch|switch|return|with|new|else)\b)[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^>]+>)?\s*\([^;{]*$|'
        # 5. Direct identifier method signature
        r'^\s*(?!(?:if|for|while|catch|switch|return|with)\b)[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^>]+>)?\s*\([^)]*\)\s*(?:->\s*[^;{\n]+|:\s*[^;{\n]+|\s+[A-Za-z0-9_<>\[\],.?|&()]+)?\s*(?:async\*?|sync\*?)?\s*\{'
    )

    func_depth = 0
    func_start_idx = 0
    func_paren_depth = 0
    intact_type_depth = 0
    pending_func_open = False
    in_block_comment = False
    in_multiline_str: Optional[str] = None

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            if pending_func_open:
                pending_func_open = False
            if func_depth == 0 and not include_line_numbers:
                out.append("")
            continue

        if in_block_comment or in_multiline_str is not None:
            net, in_block_comment, in_multiline_str = _count_effective_braces_stateful(line, in_block_comment, in_multiline_str)
            if func_depth > 0:
                func_depth += net
                if func_depth <= 0:
                    func_depth = 0
                    func_end_idx = max(func_start_idx, idx - 1)
                    omitted_comment = f"    // ... [L{func_start_idx}-L{func_end_idx}] [Implementation omitted for audit] ..."
                    out.append(f" ... | {omitted_comment}" if include_line_numbers else omitted_comment)
                    out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            else:
                if intact_type_depth > 0:
                    intact_type_depth = max(0, intact_type_depth + net)
                out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            continue

        if func_depth == 0 and any(stripped.startswith(p) for p in ('import ', 'from ', 'export *', 'package ', 'use ', '#include')):
            out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            continue

        if intact_type_depth > 0 and func_depth == 0:
            out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            net_braces, in_block_comment, in_multiline_str = _count_effective_braces_stateful(line, in_block_comment, in_multiline_str)
            intact_type_depth += net_braces
            if intact_type_depth <= 0:
                intact_type_depth = 0
            continue

        if pending_func_open and func_depth == 0 and not intact_type_pattern.match(line[:500]):
            out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            net_braces, net_parens, in_block_comment, in_multiline_str = _count_effective_delimiters_stateful(line, in_block_comment, in_multiline_str)
            func_paren_depth = max(0, func_paren_depth + net_parens)
            if func_paren_depth == 0 and net_braces > 0:
                func_depth += net_braces
                func_start_idx = idx + 1
                pending_func_open = False
            elif func_paren_depth == 0 and (stripped.endswith(';') or intact_type_pattern.match(line[:500])):
                pending_func_open = False
            continue

        if func_depth == 0:
            line_head = line[:500]
            if intact_type_pattern.match(line_head):
                out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
                net, in_block_comment, in_multiline_str = _count_effective_braces_stateful(line, in_block_comment, in_multiline_str)
                if net > 0:
                    intact_type_depth += net
                continue

            if not stripped.startswith(('//', '/*', '*', '#')) and func_pattern.match(line_head):
                out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
                net_braces, net_parens, in_block_comment, in_multiline_str = _count_effective_delimiters_stateful(line, in_block_comment, in_multiline_str)
                func_paren_depth = max(0, net_parens)
                if func_paren_depth == 0 and net_braces > 0:
                    func_depth += net_braces
                    func_start_idx = idx + 1
                    pending_func_open = False
                elif not stripped.endswith((';', '}')) and '{' not in stripped:
                    pending_func_open = True
                continue

            net, in_block_comment, in_multiline_str = _count_effective_braces_stateful(line, in_block_comment, in_multiline_str)
            out.append(f"{idx:4d} | {line}" if include_line_numbers else line)
            continue

        if func_depth > 0:
            net, in_block_comment, in_multiline_str = _count_effective_braces_stateful(line, in_block_comment, in_multiline_str)
            func_depth += net
            if func_depth <= 0:
                func_depth = 0
                func_end_idx = max(func_start_idx, idx - 1)
                omitted_comment = f"    // ... [L{func_start_idx}-L{func_end_idx}] [Implementation omitted for audit] ..."
                out.append(f" ... | {omitted_comment}" if include_line_numbers else omitted_comment)
                out.append(f"{idx:4d} | {line}" if include_line_numbers else line)

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



def map_directory(dir_path: str, exclude_dirs: Set[str], valid_exts: Set[str], include_agents_runtime: bool = False) -> None:
    print(f" Generating Code Skeleton Map for: {os.path.abspath(dir_path)}")
    print("=" * 60)

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if _should_traverse_dir(d, exclude_dirs, include_agents_runtime)]
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
    valid_extensions = {".dart", ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".swift", ".java", ".kt"}

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

    include_agents = (
        getattr(args, 'include_agents', False) or
        os.path.exists(os.path.join(target_dir, ".agents", "skills")) or
        os.path.basename(os.path.abspath(target_dir)) in (".agents", "_foundation")
    )

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
                if not _should_traverse_dir(entry, ignore_dirs, include_agents):
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

COMMON_METHOD_NOISE = {
    "main", "close", "open", "load", "save", "read", "write", "get", "set",
    "run", "start", "stop", "init", "setup", "teardown", "cleanup", "reset",
    "to_dict", "from_dict", "__init__", "__enter__", "__exit__", "__repr__", "__str__"
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


def extract_file_symbols(file_path: str, conn: Optional[Any] = None) -> Tuple[Dict[str, List[Tuple[int, str]]], Set[str]]:
    """
    Extracts definitions and references from a single source file.
    Uses Python stdlib AST for .py files, and high-fidelity polyglot parser for others.
    Leverages SQLite ast_symbol_cache with (mtime_ns, size_b) invalidation for sub-15ms incremental lookups.
    Returns: (defines_dict: {sym_name: [(line_no, signature)]}, references_set: {ref_name})
    """
    norm_path = os.path.abspath(file_path).replace("\\", "/")
    mtime_ns = 0
    size_b = 0
    cache_db_path = None
    close_conn = False
    active_conn = conn

    try:
        st = os.stat(file_path)
        mtime_ns, size_b = st.st_mtime_ns, st.st_size
        if active_conn is None:
            try:
                from core.paths import get_persistence_db_path
                cache_db_path = str(get_persistence_db_path())
            except ImportError:
                orion_dir = os.path.join(os.getcwd(), ".orion")
                cache_db_path = os.path.join(orion_dir, "orion.db") if os.path.isdir(orion_dir) else None
            if cache_db_path and os.path.exists(cache_db_path):
                from core.db import connect_sqlite
                active_conn = connect_sqlite(cache_db_path, timeout_sec=5.0)
                close_conn = True

        if active_conn:
            try:
                if not getattr(active_conn, "_ast_cache_table_initialized", False):
                    active_conn.execute(
                        "CREATE TABLE IF NOT EXISTS ast_symbol_cache ("
                        "filepath TEXT PRIMARY KEY, mtime_ns INTEGER, size_b INTEGER, "
                        "defines_json TEXT, references_json TEXT)"
                    )
                    setattr(active_conn, "_ast_cache_table_initialized", True)
                cur = active_conn.cursor()
                cur.execute(
                    "SELECT mtime_ns, size_b, defines_json, references_json FROM ast_symbol_cache WHERE filepath = ?",
                    (norm_path,)
                )
                row = cur.fetchone()
                if row and row[0] == mtime_ns and row[1] == size_b:
                    raw_def = json.loads(row[2])
                    cached_defs = {k: [tuple(x) for x in v] for k, v in raw_def.items()}
                    cached_refs = set(json.loads(row[3]))
                    return cached_defs, cached_refs
            except Exception as _ce:
                _log_telemetry(_ce, "scanner.py:ast_symbol_cache_read")
    except Exception as _stat_err:
        _log_telemetry(_stat_err, f"scanner.py:stat:{file_path}")
    finally:
        if close_conn and active_conn:
            try:
                active_conn.close()
            except (OSError, sqlite3.Error) as _e:
                _log_telemetry(_e, "scanner.py:active_conn_close")
            active_conn = None

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
                    self.scope_stack: List[Tuple[str, str]] = []

                def visit_ClassDef(self, node: ast.ClassDef):
                    # Skip nested classes defined inside functions
                    if any(kind == "func" for kind, _ in self.scope_stack):
                        self.scope_stack.append(("class", node.name))
                        self.generic_visit(node)
                        self.scope_stack.pop()
                        return

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
                    self.scope_stack.append(("class", node.name))
                    self.generic_visit(node)
                    self.scope_stack.pop()

                def visit_FunctionDef(self, node: ast.FunctionDef):
                    self._handle_func(node, is_async=False)

                def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                    self._handle_func(node, is_async=True)

                def _handle_func(self, node, is_async: bool):
                    # Skip helper functions defined inside functions
                    if any(kind == "func" for kind, _ in self.scope_stack):
                        self.scope_stack.append(("func", node.name))
                        self.generic_visit(node)
                        self.scope_stack.pop()
                        return

                    prefix = "async def " if is_async else "def "
                    args_list = [a.arg for a in node.args.args if a.arg not in {"self", "cls"}]
                    arg_str = ", ".join(args_list[:4])
                    if len(args_list) > 4:
                        arg_str += ", ..."

                    parent_classes = [name for kind, name in self.scope_stack if kind == "class"]
                    if parent_classes:
                        sig = f"{prefix}{parent_classes[-1]}.{node.name}({arg_str})"
                    else:
                        sig = f"{prefix}{node.name}({arg_str})"

                    defines.setdefault(node.name, []).append((node.lineno, sig))
                    self.scope_stack.append(("func", node.name))
                    self.generic_visit(node)
                    self.scope_stack.pop()

                def visit_Name(self, node: ast.Name):
                    if isinstance(node.ctx, ast.Load) and node.id not in RESERVED_KEYWORDS:
                        references.add(node.id)
                    self.generic_visit(node)

                def visit_Attribute(self, node: ast.Attribute):
                    if isinstance(node.ctx, ast.Load) and node.attr not in RESERVED_KEYWORDS and node.attr not in COMMON_METHOD_NOISE:
                        references.add(node.attr)
                    self.generic_visit(node)

                def visit_Import(self, node: ast.Import):
                    for alias in node.names:
                        name_to_add = alias.asname or alias.name.split('.')[0]
                        if name_to_add not in RESERVED_KEYWORDS:
                            references.add(name_to_add)
                    self.generic_visit(node)

                def visit_ImportFrom(self, node: ast.ImportFrom):
                    if node.module:
                        for part in node.module.split('.'):
                            if part and part not in RESERVED_KEYWORDS:
                                references.add(part)
                    for alias in node.names:
                        sym_name = alias.asname or alias.name
                        if sym_name not in RESERVED_KEYWORDS:
                            references.add(sym_name)
                    self.generic_visit(node)

                def visit_Assign(self, node: ast.Assign):
                    if not self.scope_stack:
                        for tgt in node.targets:
                            if isinstance(tgt, ast.Name) and not tgt.id.startswith("_") and len(tgt.id) >= 3:
                                defines.setdefault(tgt.id, []).append((node.lineno, f"{tgt.id} = ..."))
                    self.generic_visit(node)

                def visit_Constant(self, node: ast.Constant):
                    if isinstance(node.value, str) and len(node.value) >= 3:
                        for token in re.findall(r'\b[A-Za-z_][A-Za-z0-9_]{2,}\b', node.value):
                            if token not in RESERVED_KEYWORDS:
                                references.add(token)
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
            if file_path.endswith('.rs'):
                # In Rust, preserve lifetime annotations (&'a, 'static) while stripping normal quotes and comments
                code_only = re.sub(r'//.*?$|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"', ' ', content, flags=re.MULTILINE)
            else:
                code_only = re.sub(r'//.*?$|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\\n])*\'', ' ', content, flags=re.MULTILINE)
            raw_tokens = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]{2,}\b', code_only)
            for tok in raw_tokens:
                if tok not in RESERVED_KEYWORDS:
                    references.add(tok)

            # Fast in-memory CST extractor (sub-millisecond, zero subprocess overhead)
            patterns = [
                (re.compile(r'^\s*(?:export\s+)?(?:abstract\s+|sealed\s+|open\s+|pub(?:\([^)]*\))?\s+|public\s+|private\s+)?(?:class|struct|interface|trait|enum|type)\s+([A-Za-z0-9_]+)'), "class"),
                (re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)(?:\s*:\s*[^=]+)?\s*=\s*(?:async\s*)?(?:<[^>]+>\s*)?\([^;]*?\)\s*(?::\s*[^=]+)?=>'), "func"),
                (re.compile(
                    r'^\s*(?:(?:export|default|async|pub(?:\([^)]*\))?|public|private|protected|internal|static|final|override|abstract|virtual|inline|suspend)\s+)*'
                    r'(?:(?:fn|def|fun|function|func)\s+(?:\([A-Za-z0-9_*,\s]+\)\s+)?|(?:[A-Za-z_][A-Za-z0-9_<>\[\],.?|&]*\s+){1,3})'
                    r'(?!(?:if|for|while|catch|switch|return|with|new|else|super|this)\b)([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>]+>)?\s*\('
                    r'(?:[^()]{0,240}\)\s*(?:\s*->\s*[^;{\n:]+|\s*:\s*[^;{\n:]+|\s+[A-Za-z0-9_<>\[\],.?|&()]+)?\s*(?:async\*?|sync\*?)?\s*[{=>;:]|[^;{}]*$)'
                ), "func"),
                (re.compile(
                    r'^\s*(?!(?:if|for|while|catch|switch|return|with|new|else|super|this)\b)([A-Za-z_][A-Za-z0-9_]*)\s*(?:<[^>]+>)?\s*\([^()]{0,240}\)'
                    r'(?:\s*->\s*[^;{\n:]+|\s*:\s*[^;{\n:]+)?\s*(?:async\*?|sync\*?)?\s*\{'
                ), "func"),
            ]
            for line_num, line in enumerate(lines, 1):
                if len(line) > 500:
                    continue
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

    if mtime_ns > 0:
        write_conn = conn
        close_write = False
        if write_conn is None:
            if not cache_db_path:
                try:
                    from core.paths import get_persistence_db_path
                    cache_db_path = str(get_persistence_db_path())
                except ImportError:
                    pass
            if cache_db_path and os.path.exists(cache_db_path):
                try:
                    from core.db import connect_sqlite
                    write_conn = connect_sqlite(cache_db_path, timeout_sec=5.0)
                    close_write = True
                except (OSError, sqlite3.Error) as _e:
                    _log_telemetry(_e, "scanner.py:connect_sqlite")
        if write_conn:
            try:
                write_conn.execute(
                    "INSERT OR REPLACE INTO ast_symbol_cache (filepath, mtime_ns, size_b, defines_json, references_json) VALUES (?, ?, ?, ?, ?)",
                    (norm_path, mtime_ns, size_b, json.dumps(defines), json.dumps(list(references)))
                )
                if close_write:
                    write_conn.commit()
            except Exception as _se:
                _log_telemetry(_se, "scanner.py:ast_symbol_cache_write")
            finally:
                if close_write:
                    try:
                        write_conn.close()
                    except (OSError, sqlite3.Error) as _e:
                        _log_telemetry(_e, "scanner.py:write_conn_close")

    return defines, references


def extract_symbols(root_dir: str, max_files: int = 500) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts code symbols and cross-file references via ast-grep or fallback AST parser.
    Fulfills interface contract: returns mapping of relative file path -> list of symbol dicts.
    """
    ignore_dirs = {
        "node_modules", "build", "dist", "coverage", ".git", "ios", "android",
        "__pycache__", "scratch", ".scratch", ".worktrees", ".orion", ".gemini",
        ".dart_tool", "target", ".venv", "venv"
    }
    valid_extensions = {f".{ext}" for ext in SUPPORTED_SKELETON_EXTENSIONS}

    file_paths: List[str] = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if _should_traverse_dir(d, ignore_dirs, True)]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_extensions:
                file_paths.append(os.path.join(root, f))
                if len(file_paths) >= max_files:
                    break
        if len(file_paths) >= max_files:
            break

    result: Dict[str, List[Dict[str, Any]]] = {}

    shared_conn = None
    try:
        from core.db import connect_sqlite
        from core.paths import get_persistence_db_path
        db_p = str(get_persistence_db_path())
        if os.path.exists(db_p):
            shared_conn = connect_sqlite(db_p)
    except (OSError, sqlite3.Error) as _e:
        _log_telemetry(_e, "scanner.py:connect_shared_db")

    try:
        for fp in file_paths:
            rel_path = os.path.relpath(fp, root_dir).replace("\\", "/")
            symbols_list: List[Dict[str, Any]] = []

            defs, refs = extract_file_symbols(fp, conn=shared_conn)
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
    finally:
        if shared_conn:
            try:
                shared_conn.commit()
                shared_conn.close()
            except (OSError, sqlite3.Error) as _e:
                _log_telemetry(_e, "scanner.py:shared_conn_close")

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

            id_match = re.search(r'\b(?:def|class|struct|interface|fn|func|type)\s+([a-zA-Z0-9_]+)', sig)
            sym_name = id_match.group(1) if id_match else ""
            if sym_name in {"__enter__", "__exit__", "__repr__", "__str__"}:
                continue
            generic_names = {'main', 'close', '__init__', 'setup', 'teardown', 'cleanup'}

            if any(kw in sig.split() for kw in ["class", "struct", "interface"]):
                boost = 2.5
            elif sym_name.lower() in generic_names:
                boost = 0.25
            elif sym_name.startswith('_') and not sym_name.startswith('__'):
                boost = 0.2
            elif len(sym_name) >= 6:
                boost = 1.6
            else:
                boost = 1.0

            sublinear_file_score = (file_score ** 0.6) if file_score > 0 else 0
            item_score = sublinear_file_score * boost
            # Sublinear token scaling prevents informative multi-param signatures from being dropped in favor of trivial stubs
            cost_weight = math.sqrt(token_est)
            items.append({
                "file": rel_path,
                "file_score": file_score,
                "line_no": line_no,
                "sig": sig,
                "score": item_score,
                "tokens": token_est,
                "density": item_score / cost_weight
            })

    # Sort candidates by value density: rho_i = score_i / tokens_i descending
    items.sort(key=lambda x: x["density"], reverse=True)

    included_files: Set[str] = set()
    included_by_file: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    consumed_tokens = 0

    for item in items:
        file_path = item["file"]
        if len(included_by_file[file_path]) >= 8:
            continue
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
    while output_lines and output_lines[-1].lstrip().startswith("📄 "):
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
    focus: Optional[List[str]] = None,
    files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Builds a PageRank-ranked repository map constrained by a token budget.
    Implements CST symbol extraction + sparse PageRank + greedy knapsack packing.
    """
    if valid_exts is None:
        valid_exts = {f".{ext}" for ext in SUPPORTED_SKELETON_EXTENSIONS}
    if ignore_dirs is None:
        ignore_dirs = {
            "node_modules", "build", "dist", "coverage", ".git", "ios", "android",
            "__pycache__", "scratch", ".scratch", ".worktrees", ".orion", ".gemini",
            ".dart_tool", "target", ".venv", "venv"
        }

    abs_target = os.path.abspath(target_dir)
    non_agent_code_exists = False
    try:
        with os.scandir(abs_target) as entries:
            for entry in entries:
                if entry.name.startswith(".") or entry.name in ignore_dirs or entry.name in ("context", "docs"):
                    continue
                if entry.is_file() and os.path.splitext(entry.name)[1].lower() in valid_exts:
                    non_agent_code_exists = True
                    break
                if entry.is_dir():
                    for sub_root, sub_dirs, sub_files in os.walk(entry.path):
                        sub_dirs[:] = [d for d in sub_dirs if d not in ignore_dirs and not d.startswith(".")]
                        if any(os.path.splitext(f)[1].lower() in valid_exts for f in sub_files):
                            non_agent_code_exists = True
                            break
                    if non_agent_code_exists:
                        break
    except OSError:
        pass

    include_agents_runtime = (
        os.path.basename(abs_target) == ".agents"
        or (os.path.isdir(os.path.join(abs_target, ".agents")) and not non_agent_code_exists)
    )

    file_paths: List[str] = []
    if files is not None:
        for rel_f in files:
            ext = os.path.splitext(rel_f)[1].lower()
            if ext in valid_exts:
                full_p = os.path.join(target_dir, rel_f)
                if os.path.isfile(full_p):
                    file_paths.append(full_p)
    else:
        for root, dirs, f_list in os.walk(target_dir):
            dirs[:] = [
                d for d in dirs
                if _should_traverse_dir(d, ignore_dirs, include_agents_runtime)
            ]
            for f in f_list:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_exts:
                    file_paths.append(os.path.join(root, f))

    if not file_paths:
        return {"ranked_files": [], "repo_map": "(No matching code files found)", "total_tokens": 0, "total_files_indexed": 0}

    file_defines: Dict[str, Dict[str, List[Tuple[int, str]]]] = {}
    file_references: Dict[str, Set[str]] = {}
    symbol_definers: Dict[str, Set[str]] = {}

    shared_conn = None
    try:
        from core.db import connect_sqlite
        from core.paths import get_persistence_db_path
        db_p = str(get_persistence_db_path())
        if os.path.exists(db_p):
            shared_conn = connect_sqlite(db_p)
    except (OSError, sqlite3.Error) as _e:
        _log_telemetry(_e, "scanner.py:connect_shared_db_repomap")

    try:
        for fp in file_paths:
            rel_p = os.path.relpath(fp, target_dir).replace("\\", "/")
            defs, refs = extract_file_symbols(fp, conn=shared_conn)
            file_defines[rel_p] = defs
            file_references[rel_p] = refs
            for sym in defs:
                symbol_definers.setdefault(sym, set()).add(rel_p)
    finally:
        if shared_conn:
            try:
                shared_conn.commit()
                shared_conn.close()
            except (OSError, sqlite3.Error) as _e:
                _log_telemetry(_e, "scanner.py:shared_conn_close_repomap")

    graph: Dict[str, Dict[str, float]] = {rel_p: {} for rel_p in file_defines}

    num_files = max(1, len(file_defines))
    # Connect reference files to defining files with IDF + Import-Affinity weighting
    for ref_file, refs in file_references.items():
        ref_dir = os.path.dirname(ref_file)
        for ident in refs:
            definers = symbol_definers.get(ident)
            if not definers:
                continue
            # Inverse Document Frequency: penalize ubiquitous names like 'main' or 'init' (smoothed BM25 IDF)
            idf_weight = math.log(1.0 + (num_files - len(definers) + 0.5) / (len(definers) + 0.5))
            if idf_weight < 0.15:
                continue
            for def_file in definers:
                if def_file == ref_file:
                    continue
                def_stem = os.path.splitext(os.path.basename(def_file))[0]
                # Boost edge if ref_file explicitly references the defining module stem or shares package dir
                affinity = 4.0 if (def_stem in refs or os.path.dirname(def_file) == ref_dir) else 1.0
                edge_w = idf_weight * affinity
                graph[ref_file][def_file] = graph[ref_file].get(def_file, 0.0) + edge_w

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
            tok = max(1, int(math.ceil(len(content) / 3.8)))
        except OSError:
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
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from core.security import SecurityAuditor

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


# === WORKER DELEGATION OVERLAP GATE ===

def _resolve_local_1hop_closure(raw_paths: List[str], root_dir: str = ".") -> Set[str]:
    """
    Resolves target files and their 1-hop local repository imports into a closed dependency set.
    Each item in raw_paths can be a file or a directory.
    Directories are recursively expanded to source files.
    Returns a set of normalized relative paths (using forward slashes).
    """
    abs_root = os.path.abspath(root_dir)
    target_files: Set[str] = set()
    source_exts = {".py", ".dart", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".kt", ".java"}
    ignore_dirs = {"node_modules", "build", "dist", "coverage", ".git", "ios", "android", ".gemini", "__pycache__", "scratch", ".scratch", ".worktrees", ".orion"}

    # 1. Expand raw paths
    for item in raw_paths:
        item_str = str(item).strip().strip("'\"")
        if not item_str:
            continue
        sub_items = [p.strip() for p in item_str.split(",") if p.strip()] if "," in item_str else [item_str]

        for p in sub_items:
            # Strip task label prefix if present, e.g. "task1:path/to/file"
            if ":" in p and not (len(p) > 2 and p[1] == ":" and p[2] in ("\\", "/")):
                parts = p.split(":", 1)
                p = parts[1].strip()

            candidate = os.path.abspath(os.path.join(abs_root, p)) if not os.path.isabs(p) else os.path.abspath(p)
            if os.path.isfile(candidate):
                target_files.add(candidate)
            elif os.path.isdir(candidate):
                for r, d_list, f_list in os.walk(candidate):
                    d_list[:] = [d for d in d_list if _should_traverse_dir(d, ignore_dirs, include_agents_runtime=True)]
                    for f in f_list:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in source_exts:
                            target_files.add(os.path.abspath(os.path.join(r, f)))

    closure: Set[str] = set()

    def _add_to_closure(p: str) -> None:
        try:
            rel = os.path.relpath(p, abs_root).replace("\\", "/")
            if not rel.startswith("../"):
                closure.add(rel)
        except ValueError:
            pass

    for f_path in target_files:
        _add_to_closure(f_path)
        f_dir = os.path.dirname(f_path)
        ext = os.path.splitext(f_path)[1].lower()

        if ext == ".py":
            try:
                import ast as _ast
                with open(f_path, "r", encoding="utf-8", errors="ignore") as pf:
                    tree = _ast.parse(pf.read(), filename=f_path)

                def _probe_python_module(mod_name: str, base_dir: str) -> None:
                    if not mod_name:
                        return
                    rel_mod = mod_name.replace(".", os.sep)
                    search_bases = [
                        base_dir,
                        abs_root,
                        os.path.join(abs_root, ".agents", "scripts"),
                        os.path.join(abs_root, "src"),
                        os.path.join(abs_root, "lib"),
                    ]
                    for s_base in search_bases:
                        cand_file = os.path.join(s_base, rel_mod + ".py")
                        cand_pkg = os.path.join(s_base, rel_mod, "__init__.py")
                        if os.path.isfile(cand_file):
                            _add_to_closure(cand_file)
                            return
                        elif os.path.isfile(cand_pkg):
                            _add_to_closure(cand_pkg)
                            return

                for node in _ast.walk(tree):
                    if isinstance(node, _ast.Import):
                        for alias in node.names:
                            _probe_python_module(alias.name, f_dir)
                    elif isinstance(node, _ast.ImportFrom):
                        mod_name = node.module or ""
                        if node.level > 0:
                            cur_dir = f_dir
                            for _ in range(node.level - 1):
                                cur_dir = os.path.dirname(cur_dir)
                            rel_mod = mod_name.replace(".", os.sep) if mod_name else ""
                            base_target = os.path.join(cur_dir, rel_mod)
                            for alias in node.names:
                                cand_sub = os.path.join(base_target, alias.name + ".py")
                                if os.path.isfile(cand_sub):
                                    _add_to_closure(cand_sub)
                            cand_f = base_target + ".py"
                            cand_init = os.path.join(base_target, "__init__.py")
                            if os.path.isfile(cand_f):
                                _add_to_closure(cand_f)
                            elif os.path.isfile(cand_init):
                                _add_to_closure(cand_init)
                        else:
                            _probe_python_module(mod_name, f_dir)
                            for alias in node.names:
                                sub_mod = f"{mod_name}.{alias.name}" if mod_name else alias.name
                                _probe_python_module(sub_mod, f_dir)
            except Exception as _pe:
                _log_telemetry(_pe, f"resolve_1hop_closure:py:{f_path}")

        else:
            try:
                with open(f_path, "r", encoding="utf-8", errors="ignore") as poly_f:
                    p_content = poly_f.read()
                rel_matches = re.findall(r'''(?:import|from|require)\s*\(?['"](\.[^'"]+)['"]''', p_content)
                dart_matches = re.findall(r'''import\s+['"]([^'"]+\.dart)['"]''', p_content)
                for rel_imp in rel_matches + dart_matches:
                    clean_imp = rel_imp.split("?")[0].split("#")[0]
                    cand_base = os.path.normpath(os.path.join(f_dir, clean_imp))
                    candidates = [cand_base]
                    for s_ext in [".ts", ".tsx", ".js", ".jsx", ".dart", ".go", ".rs", ".kt", ".java"]:
                        candidates.append(cand_base + s_ext)
                        candidates.append(os.path.join(cand_base, f"index{s_ext}"))
                    for cand in candidates:
                        if os.path.isfile(cand):
                            _add_to_closure(cand)
                            break
            except Exception as _poly_e:
                _log_telemetry(_poly_e, f"resolve_1hop_closure:polyglot:{f_path}")

    return closure


def check_delegation_overlap(
    task_groups: List[List[str]],
    threshold: float = 0.20,
    root_dir: str = ".",
    as_json: bool = False
) -> int:
    """
    Calculates Jaccard Dependency Overlap across multiple task file sets.
    Formula: J(T1, T2) = |D(T1) ∩ D(T2)| / |D(T1) ∪ D(T2)|
    Exit Code 1: If max Jaccard > threshold (MERGE_TO_SINGLE_AGENT).
    Exit Code 0: If max Jaccard <= threshold (ALLOW_DELEGATION / ALLOW_PARALLEL_DISJOINT).
    """
    if len(task_groups) < 2:
        msg = "Error: At least 2 task groups are required for dependency overlap check."
        if as_json:
            print(json.dumps({"error": msg, "exit_code": 1}))
        else:
            print(f"[DELEGATE-CHECK] ❌ {msg}", file=sys.stderr)
            print("Usage: python .agents/scripts/orion.py delegate-check <task1_files> <task2_files> [--threshold 0.20]", file=sys.stderr)
        return 1

    closures: List[Set[str]] = [_resolve_local_1hop_closure(tg, root_dir=root_dir) for tg in task_groups]
    pairs = []
    max_jaccard = 0.0

    for i in range(len(closures)):
        for j in range(i + 1, len(closures)):
            d_i, d_j = closures[i], closures[j]
            intersection = d_i.intersection(d_j)
            union = d_i.union(d_j)
            jaccard = len(intersection) / len(union) if union else 0.0
            if jaccard > max_jaccard:
                max_jaccard = jaccard
            pairs.append({
                "task_a_index": i + 1,
                "task_b_index": j + 1,
                "task_a_closure_size": len(d_i),
                "task_b_closure_size": len(d_j),
                "shared_count": len(intersection),
                "union_count": len(union),
                "shared_dependencies": sorted(list(intersection)),
                "jaccard": round(jaccard, 4),
                "jaccard_pct": round(jaccard * 100, 2)
            })

    if max_jaccard > threshold:
        verdict = "MERGE_TO_SINGLE_AGENT"
        exit_code = 1
        summary = (
            f"Dependency overlap exceeds threshold ({max_jaccard * 100:.1f}% > {threshold * 100:.1f}%). "
            "Parallel sub-agents will experience split-brain state drift and broken KV-cache locality. "
            "Merge all tasks into a single sequential plan (implementation_plan.md) on the main thread."
        )
    elif max_jaccard == 0.0:
        verdict = "ALLOW_PARALLEL_DISJOINT"
        exit_code = 0
        summary = (
            "Tasks are strictly disjoint (0.0% overlap). "
            "Safe to delegate to parallel read-only scouts or execute concurrently in background."
        )
    else:
        verdict = "ALLOW_DELEGATION"
        exit_code = 0
        summary = (
            f"Dependency overlap is within acceptable threshold ({max_jaccard * 100:.1f}% <= {threshold * 100:.1f}%). "
            "Pendelegasian disetujui. Ensure shared dependencies are treated as read-only."
        )

    if as_json:
        payload = {
            "verdict": verdict,
            "max_jaccard": round(max_jaccard, 4),
            "max_jaccard_pct": round(max_jaccard * 100, 2),
            "threshold": threshold,
            "threshold_pct": round(threshold * 100, 2),
            "exit_code": exit_code,
            "summary": summary,
            "tasks": [
                {
                    "task_index": idx + 1,
                    "input_spec": task_groups[idx],
                    "closure_size": len(closures[idx]),
                    "closure_files": sorted(list(closures[idx]))
                }
                for idx in range(len(task_groups))
            ],
            "pairs": pairs
        }
        print(json.dumps(payload, indent=2))
        return exit_code

    print("\n⚖️ Worker Delegation Dependency Overlap Gate")
    print("=" * 64)
    print(f"Task Partitions : {len(task_groups)}")
    print(f"Max Threshold   : {threshold * 100:.1f}%\n")

    for idx, c in enumerate(closures, 1):
        sample = sorted(list(c))
        display = sample[:4]
        suffix = f" ... (+{len(sample) - 4} more)" if len(sample) > 4 else ""
        print(f"Task {idx} Closure ({len(c)} files):")
        for item in display:
            print(f"  • {item}")
        if suffix:
            print(f"  {suffix}")
        print()

    for p in pairs:
        print(f"Pair ({p['task_a_index']} ↔ {p['task_b_index']}) Jaccard Overlap: {p['jaccard_pct']}% (|D1 ∩ D2| = {p['shared_count']}, |D1 ∪ D2| = {p['union_count']})")
        if p["shared_dependencies"]:
            print("  Shared Dependencies:")
            for s in p["shared_dependencies"][:6]:
                print(f"    - {s}")
            if len(p["shared_dependencies"]) > 6:
                print(f"    ... (+{len(p['shared_dependencies']) - 6} more)")
        print()

    print("-" * 64)
    if exit_code == 1:
        print(f"[DELEGATE-CHECK] ❌ VERDICT: {verdict} (Exit Code 1)")
        print(f"REASON: {summary}\n")
    else:
        print(f"[DELEGATE-CHECK] ✅ VERDICT: {verdict} (Exit Code 0)")
        print(f"REASON: {summary}\n")

    return exit_code


def cmd_delegate_check(args: argparse.Namespace) -> None:
    raw_tasks: List[str] = []
    if getattr(args, "task_flags", None):
        raw_tasks.extend(args.task_flags)
    if getattr(args, "tasks", None):
        raw_tasks.extend(args.tasks)

    task_groups: List[List[str]] = []
    for t_spec in raw_tasks:
        parts = [p.strip() for p in t_spec.split(",") if p.strip()]
        if parts:
            task_groups.append(parts)

    threshold = getattr(args, "threshold", 0.20)
    as_json = getattr(args, "json", False)
    root_dir = getattr(args, "root_dir", ".")
    exit_code = check_delegation_overlap(task_groups, threshold=threshold, root_dir=root_dir, as_json=as_json)
    sys.exit(exit_code)


# === CLI DISPATCH ===

def main() -> None:
    # Direct invocation support: python scanner.py <path> [--budget 1500]
    known_subcmds = {"targets", "map", "repomap", "tokens", "security", "delegate-check", "-h", "--help"}
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

    # Delegate Check
    parser_del = subparsers.add_parser("delegate-check", help="Deterministic Jaccard dependency overlap gate for worker delegation")
    parser_del.add_argument("tasks", nargs="*", help="Task file groups (e.g. task1_files task2_files)")
    parser_del.add_argument("--task", action="append", dest="task_flags", help="Task file group (repeatable)")
    parser_del.add_argument("--threshold", type=float, default=0.20, help="Maximum allowed Jaccard dependency overlap (default: 0.20)")
    parser_del.add_argument("--json", action="store_true", help="Output in raw JSON format")

    for sub_p in (parser_targets, parser_map, parser_repomap, parser_tokens, parser_sec, parser_del):
        sub_p.add_argument("--dir", dest="dir_flag", help="Target directory or file override")

    parsed_args = parser.parse_args()
    if getattr(parsed_args, "dir_flag", None):
        parsed_args.dir = parsed_args.dir_flag
        if hasattr(parsed_args, "root_dir"):
            parsed_args.root_dir = parsed_args.dir_flag
    
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
    elif parsed_args.command == "delegate-check":
        cmd_delegate_check(parsed_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
