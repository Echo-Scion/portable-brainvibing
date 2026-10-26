# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Orion Compactor and Content Distillation Engine
High-density token compression, AST/code hollowing, and surgical memory compaction.
"""

import os
import sys
import re
import io
import csv
import ast
import json
import math
import time
import shutil
import hashlib
import sqlite3
import argparse
import datetime
from datetime import datetime
import urllib.request
import urllib.error
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple

# Base scripts dir in sys.path
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError, ValueError):
        pass

from core.db import connect_sqlite, atomic_write_text, log_telemetry as _log_telemetry
from core.paths import get_persistence_db_path, get_workspace_dir, get_orion_dir, get_agents_dir
from core.capabilities import parse_model_parameters_b, enqueue_cloud_handoff

WORKSPACE_DIR = str(get_workspace_dir())
BASE_DIR = str(get_agents_dir())
ORION_DIR = str(get_orion_dir())

def _get_workspace_dir() -> str:
    b = sys.modules.get("commands.brain")
    if b and hasattr(b, "WORKSPACE_DIR"):
        return getattr(b, "WORKSPACE_DIR")
    return WORKSPACE_DIR

def _get_orion_dir() -> str:
    b = sys.modules.get("commands.brain")
    if b and hasattr(b, "ORION_DIR"):
        return getattr(b, "ORION_DIR")
    return ORION_DIR


def resolve_ollama_base_url(force_refresh=False):
    try:
        from core.capabilities import resolve_ollama_base_url as _central_resolve
        return _central_resolve(force_refresh=force_refresh)
    except Exception as _e:
        _log_telemetry(_e, "compact.py:resolve_ollama_base_url")
        return None

def get_available_models(base_url=None):
    try:
        from core.capabilities import get_available_models as _central_models
        res = _central_models(base_url=base_url)
        if res:
            return res
    except Exception as _e:
        _log_telemetry(_e, "compact.py:get_available_models")

    if base_url is None:
        base_url = resolve_ollama_base_url()
    if not base_url:
        return []
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as r:
            data = json.loads(r.read().decode("utf-8"))
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []

# SECTION 3: COMPACTION, TOKEN SHRINK & DISTILLATION
# ============================================================================



ULTRA_PROTECTED_TERMS: Set[str] = {
    "db", "auth", "config", "impl", "fn", "req", "res", "ref", "param", "arg",
    "not", "no", "never", "none", "neither", "nor", "cannot", "without",
    "true", "false", "null", "if", "else", "return", "error", "fail", "pass",
    "except", "only", "always", "must"
}


class CorpusInformationCompactor:
    """Kompaktor berbasis Shannon Surprisal nyata menggunakan SQLite fts5vocab."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(get_persistence_db_path())
        self.conn: Optional[sqlite3.Connection] = None
        if os.path.exists(self.db_path):
            try:
                self.conn = connect_sqlite(self.db_path)
                self.conn.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts_vocab "
                    "USING fts5vocab(pages_fts, row);"
                )
            except Exception as _e:
                _log_telemetry(_e, "CorpusInformationCompactor:init")

    def _token_surprisal(self, tokens: List[str]) -> Dict[str, float]:
        local_counts = Counter(tokens)
        total_local = max(1, len(tokens))
        vocab_size = max(1, len(local_counts))
        scores = {
            t: -math.log2((cnt + 1.0) / (total_local + vocab_size))
            for t, cnt in local_counts.items()
        }
        if not self.conn or not tokens:
            return scores
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM pages;")
            total_docs = max(1, int(cur.fetchone()[0] or 1))
            unique_terms = list(set(tokens))
            stemmed_map = {t: re.sub(r'(?:ing|ed|es|s)$', '', t) for t in unique_terms if t}
            query_terms = list(set(unique_terms) | set(stemmed_map.values()))
            placeholders = ','.join('?' for _ in query_terms)
            cur.execute(
                f"SELECT term, doc FROM pages_fts_vocab WHERE term IN ({placeholders})",
                query_terms,
            )
            found = {}
            for term, df in cur.fetchall():
                found[term] = float(df)
            lam = 0.65
            for term in unique_terms:
                p_local = (local_counts[term] + 1.0) / (total_local + vocab_size)
                stem = stemmed_map.get(term, term)
                df = found.get(term) if term in found else found.get(stem)
                p_corpus = (df + 1.0) / (total_docs + 2.0) if df is not None else (1.0 / (total_docs + 2.0))
                p_interpolated = (lam * p_corpus) + ((1.0 - lam) * p_local)
                scores[term] = -math.log2(p_interpolated)
        except Exception as _e:
            _log_telemetry(_e, "CorpusInformationCompactor:surprisal")
        return scores

    def compact(self, text: str, keep_ratio: float = 0.5, preserve_code: bool = True) -> str:
        """Sentence-level surprisal selection: ranks whole sentences/bullets by information density without breaking grammar."""
        if keep_ratio >= 1.0 or not text.strip():
            return text
        guard = SyntaxAnchorGuard() if preserve_code else None
        work_text = guard.lock(text) if guard else text
        lines = work_text.splitlines()
        if len(lines) <= 4:
            return text
        all_tokens = [re.sub(r"[^\w]", "", w).lower() for w in work_text.split() if re.sub(r"[^\w]", "", w)]
        surprisal_map = self._token_surprisal(all_tokens)
        scored_lines: List[Tuple[int, float, str]] = []
        for idx, ln in enumerate(lines):
            stripped = ln.strip()
            if not stripped or stripped.startswith(("#", "|", "---")) or "\x00__orion_anchor_" in stripped:
                scored_lines.append((idx, 999.0, ln))
                continue
            ln_tokens = [re.sub(r"[^\w]", "", w).lower() for w in stripped.split() if re.sub(r"[^\w]", "", w)]
            has_protected = any(t in ULTRA_PROTECTED_TERMS for t in ln_tokens)
            avg_score = (sum(surprisal_map.get(t, 5.0) for t in ln_tokens) / max(1, len(ln_tokens))) + (15.0 if has_protected else 0.0)
            scored_lines.append((idx, avg_score, ln))
        non_header_scores = sorted([s for _, s, _ in scored_lines if s < 900.0], reverse=True)
        cutoff = non_header_scores[min(len(non_header_scores) - 1, max(0, int(len(non_header_scores) * keep_ratio)))] if non_header_scores else 0.0
        kept_lines = [ln for _, s, ln in scored_lines if s >= cutoff]
        result = "\n".join(kept_lines)
        return guard.unlock(result) if guard else result

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



def shrink_json(text: str, max_items: int = 2) -> str:
    """
    Compresses JSON by collapsing long repetitive lists/arrays while preserving schemas and samples.
    """
    try:
        data = json.loads(text)
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:json_parse')
        return shrink_log(text)

    def _collapse(obj):
        if isinstance(obj, list):
            if len(obj) <= max_items:
                return [_collapse(item) for item in obj]
            # Capture schema keys if list of dicts
            keys = set()
            for item in obj[:10]:
                if isinstance(item, dict):
                    keys.update(item.keys())
            
            sample_head = [_collapse(item) for item in obj[:max_items]]
            summary_meta = {
                "__collapsed_items__": len(obj) - max_items,
                "__total_items__": len(obj),
            }
            if keys:
                summary_meta["__item_schema_keys__"] = sorted(list(keys))
            return sample_head + [summary_meta]
        elif isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if isinstance(v, str) and len(v) > 500:
                    new_dict[k] = v[:150] + f"... [truncated {len(v) - 150} chars]"
                else:
                    new_dict[k] = _collapse(v)
            return new_dict
        return obj

    collapsed = _collapse(data)
    return json.dumps(collapsed, indent=2, ensure_ascii=False)


def shrink_csv(text: str, max_rows: int = 3) -> str:
    """
    Compresses CSV/TSV datasets into header, schema types, first N rows, and last M rows.
    """
    lines = text.strip().splitlines()
    if len(lines) <= (max_rows * 2) + 2:
        return text

    # Detect delimiter
    sample = "\n".join(lines[:5])
    try:
        dialect = csv.Sniffer().sniff(sample)
        delim = dialect.delimiter
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:csv_sniff')
        delim = "\t" if "\t" in lines[0] else ","

    reader = list(csv.reader(io.StringIO(text), delimiter=delim))
    if not reader:
        return text

    headers = reader[0]
    data_rows = reader[1:]
    total_rows = len(data_rows)

    if total_rows <= (max_rows * 2):
        return text

    # Infer column types from sample
    types = []
    if data_rows:
        sample_row = data_rows[0]
        for val in sample_row:
            val = val.strip()
            if val.isdigit():
                types.append("int")
            else:
                try:
                    float(val)
                    types.append("float")
                except ValueError:
                    types.append("str")

    out = io.StringIO()
    writer = csv.writer(out, delimiter=delim)
    writer.writerow(headers)
    if types and len(types) == len(headers):
        writer.writerow([f"<{t}>" for t in types])

    for row in data_rows[:max_rows]:
        writer.writerow(row)

    omitted_count = total_rows - (max_rows * 2)
    writer.writerow([f"... [omitted {omitted_count} rows | total rows: {total_rows}] ..."] + [""] * (len(headers) - 1))

    for row in data_rows[-max_rows:]:
        writer.writerow(row)

    return out.getvalue().strip()


def shrink_log(text: str, max_repeats: int = 2) -> str:
    """
    Collapses repeating log lines, strips non-essential timestamps, keeps stack traces.
    """
    lines = text.splitlines()
    if len(lines) <= 20:
        return text

    # Regex to extract core log content without timestamp/thread noise
    ts_pattern = re.compile(r"^\s*\[?\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}[^\s\]]*\]?\s*")
    
    compressed_lines = []
    prev_core = None
    repeat_count = 0
    first_raw = None

    for line in lines:
        core = ts_pattern.sub("", line).strip()
        # Keep stack traces uncompressed
        is_trace = any(marker in line for marker in ["Traceback", "File \"", "Exception:", "Error:", "Caused by:"])
        
        if core == prev_core and not is_trace:
            repeat_count += 1
        else:
            if repeat_count > 0:
                if repeat_count < max_repeats:
                    for _ in range(repeat_count):
                        compressed_lines.append(first_raw)
                else:
                    compressed_lines.append(f"  ... [repeated {repeat_count} times: {prev_core[:100]}]")
            prev_core = core
            repeat_count = 0
            first_raw = line
            compressed_lines.append(line)

    if repeat_count > 0:
        if repeat_count < max_repeats:
            for _ in range(repeat_count):
                compressed_lines.append(first_raw)
        else:
            compressed_lines.append(f"  ... [repeated {repeat_count} times: {prev_core[:100]}]")

    # If log is still excessively long (> 150 lines), sample head and decisive tail
    if len(compressed_lines) > 150:
        head = compressed_lines[:40]
        tail = compressed_lines[-60:]
        omitted = len(compressed_lines) - 100
        return "\n".join(head + [f"\n--- [... omitted {omitted} lines of routine logs ...] ---\n"] + tail)

    return "\n".join(compressed_lines)


def shrink_ast_python(text: str) -> str:
    """
    Hollows Python AST: keeps classes, methods, signatures, docstrings, replaces bodies with '...'.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return shrink_ast_generic(text)

    class HollowingTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            return self._hollow_body(node)

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            return self._hollow_body(node)

        def _hollow_body(self, node):
            new_body = []
            # Keep docstring if present
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                new_body.append(node.body[0])
            # Replace rest with Ellipsis (...)
            new_body.append(ast.Expr(value=ast.Constant(value=...)))
            node.body = new_body
            return node

    hollowed_tree = HollowingTransformer().visit(tree)
    try:
        return ast.unparse(hollowed_tree)
    except Exception as _e:
        _log_telemetry(_e, 'shrink.py:ast_unparse')
        return shrink_ast_generic(text)


def shrink_ast_generic(text: str) -> str:
    """
    Generic heuristic hollowing for Dart, TypeScript, Go, etc.
    Uses stateful delimiter tracking from core.scanner to ignore braces inside strings and comments.
    """
    try:
        from core.scanner import _count_effective_braces_stateful
    except ImportError:
        _count_effective_braces_stateful = None

    lines = text.splitlines()
    if len(lines) <= 50:
        return text

    out = []
    brace_depth = 0
    in_block_comment = False
    in_multiline_str = None
    skipped_in_block = False
    sig_re = re.compile(
        r"^\s*(?:export\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|override\s+|abstract\s+)*"
        r"(?:class|interface|enum|type|function|def|fn|struct|impl|Widget|Future|void|int|double|String|bool|final|const)\b"
    )

    for line in lines:
        stripped = line.strip()
        if _count_effective_braces_stateful is not None:
            delta, in_block_comment, in_multiline_str = _count_effective_braces_stateful(
                line, in_block_comment, in_multiline_str
            )
        else:
            delta = line.count("{") - line.count("}")

        if brace_depth <= 1:
            if sig_re.match(line) or stripped.startswith(("import ", "export ", "package ", "part ", "@", "//", "/*", "*", "*/", "#")):
                out.append(line)
                skipped_in_block = False
            elif delta != 0 or stripped in ("{", "}", "};"):
                out.append(line)
                skipped_in_block = False
            elif not stripped:
                if out and out[-1] != "":
                    out.append("")
        else:
            if not skipped_in_block:
                indent = len(line) - len(line.lstrip())
                out.append(" " * indent + "// ... [implementation elided]")
                skipped_in_block = True

        brace_depth = max(0, brace_depth + delta)
        if brace_depth <= 1:
            skipped_in_block = False

    return "\n".join(out)


def shrink_content(text: str, filename_hint: str = "", fmt: str = "auto") -> str:
    """
    Main dispatcher for shrinking content based on format or filename.
    """
    if not text or not text.strip():
        return text

    hint = filename_hint.lower()
    
    if fmt == "json" or (fmt == "auto" and (hint.endswith(".json") or text.strip().startswith(("{", "[")))):
        try:
            return shrink_json(text)
        except Exception as _e:
            _log_telemetry(_e, 'shrink.py:dispatch_json')

    if fmt == "csv" or (fmt == "auto" and (hint.endswith((".csv", ".tsv")))):
        return shrink_csv(text)

    if fmt in ("ast", "python") or (fmt == "auto" and hint.endswith(".py")):
        return shrink_ast_python(text)

    if fmt in ("ast", "python") or (fmt == "auto" and hint.endswith((".dart", ".ts", ".js", ".go", ".rs", ".java", ".cpp"))):
        return shrink_ast_generic(text)

    if fmt == "log" or (fmt == "auto" and (hint.endswith(".log") or "Traceback" in text or "Exception" in text)):
        return shrink_log(text)

    # Default fallback: check if log-like or text
    if any(m in text for m in ["Traceback", "Error:", "Exception:"]):
        return shrink_log(text)

    lines = text.splitlines()
    if len(lines) > 200:
        head = lines[:60]
        tail = lines[-60:]
        omitted = len(lines) - 120
        return "\n".join(head + [f"\n... [... omitted {omitted} lines ...] ...\n"] + tail)

    return text

def shrink_main(argv=None):
    parser = argparse.ArgumentParser(description="Orion Shrink Token Compressor")
    parser.add_argument("target", help="File to shrink or '-' for stdin")
    parser.add_argument("--format", dest="fmt", default="auto", choices=["auto", "json", "csv", "log", "ast", "python"])
    args = parser.parse_args(argv)

    if args.target == "-":
        content = sys.stdin.read()
        hint = ""
    elif os.path.exists(args.target):
        with open(args.target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        hint = args.target
    else:
        print(f"File not found: {args.target}", file=sys.stderr)
        return 1

    compressed = shrink_content(content, filename_hint=hint, fmt=args.fmt)
    orig_len = len(content)
    comp_len = len(compressed)
    ratio = (1.0 - (comp_len / orig_len)) * 100.0 if orig_len > 0 else 0.0

    print(compressed)
    print(f"\n[ORION SHRINK] Size: {orig_len:,} chars -> {comp_len:,} chars ({ratio:.1f}% reduction)", file=sys.stderr)
    return 0

def select_best_distill_model(base_url: str, user_model: str = "") -> Optional[str]:
    """
    Selects best local distillation model: strictly prioritizes models with >= 6.5B parameters.
    Returns None if no model >= 6.5B is available.
    """
    if user_model:
        if parse_model_parameters_b(user_model) >= 6.5:
            return user_model
        return None

    try:
        from core.capabilities import get_available_models
        installed = get_available_models(base_url or "http://127.0.0.1:11434")
    except Exception:
        installed = []
    if not installed:
        return None

    # Priority list for models capable of semantic distillation (>= 7B)
    preferred = [
        "qwen2.5:14b", "qwen2.5:7b", "llama3.1:8b", "mistral-nemo:12b",
        "deepseek-r1:14b", "deepseek-r1:8b", "qwen2.5-coder:7b", "qwen2.5-coder:14b"
    ]
    for pref in preferred:
        for model_name in installed:
            if model_name.startswith(pref) or pref in model_name:
                return model_name

    for model_name in installed:
        if parse_model_parameters_b(model_name) >= 6.5:
            return model_name

    return None


def distill_via_ollama(text: str, base_url: str, focus: str = "", model_name: str = "") -> str:
    """
    Executes local distillation via local AI API (Ollama or OpenAI-compatible).
    Guarded: requires >= 6.5B model. If unavailable or local AI is offline,
    enqueues DISTILL_CONTEXT cloud handoff and falls back gracefully.
    """
    if not base_url:
        enqueue_cloud_handoff("DISTILL_CONTEXT", {"focus": focus, "text_sample": text[:2000]}, reason="local_ai_offline")
        return heuristic_fallback_distill(text, focus)

    target_model = select_best_distill_model(base_url, model_name)
    if not target_model:
        enqueue_cloud_handoff(
            "DISTILL_CONTEXT",
            {"focus": focus, "text_sample": text[:2000]},
            reason="no_local_model_ge_7b",
        )
        return heuristic_fallback_distill(text, focus)

    focus_clause = f"Focus strictly on: {focus}." if focus else "Focus on root causes, errors, key entities, and metrics."
    prompt = (
        f"You are a technical data distiller for an AI coding agent.\n"
        f"{focus_clause}\n"
        f"Compress the input text into maximum 5 ultra-dense bullet points using Lessword format.\n"
        f"Omit all conversational filler, preambles, and pleasantries. Extract raw facts, file paths, line numbers, and errors.\n\n"
        f"INPUT TEXT:\n{text[:12000]}\n\n"
        f"DISTILLED EXTRACTION:"
    )

    try:
        from core.capabilities import generate_completion
        result = generate_completion(
            prompt=prompt,
            model=target_model,
            host=base_url,
            timeout_sec=15.0,
            temperature=0.1
        )
        if result and result.strip():
            return result.strip()
    except Exception as e:
        _log_telemetry(e, "compact.py:distill_via_capabilities")

    # Native Ollama API fallback
    payload = json.dumps({
        "model": target_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 250
        }
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "Orion/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        _log_telemetry(e, "compact.py:distill_via_ollama")
        enqueue_cloud_handoff("DISTILL_CONTEXT", {"focus": focus, "text_sample": text[:2000]}, reason=str(e))
        return heuristic_fallback_distill(text, focus)


def heuristic_fallback_distill(text: str, focus: str = "") -> str:
    """
    Graceful offline fallback: performs heuristic deterministic distillation in pure Python.
    """
    lines = text.splitlines()
    
    # 1. Extract critical error & status frames
    error_markers = ["error:", "exception:", "failed:", "fatal:", "critical:", "traceback", "status:", "errno"]
    signal_lines = []
    for line in lines:
        lower = line.lower()
        if any(m in lower for m in error_markers):
            cleaned = line.strip()
            if cleaned and cleaned not in signal_lines:
                signal_lines.append(cleaned)
                if len(signal_lines) >= 5:
                    break

    # 2. Extract referenced paths & symbols
    path_regex = re.compile(r"([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]{1,6}(?::\d+)?)")
    found_paths = set()
    for m in path_regex.finditer(text):
        p = m.group(1).replace("\\", "/")
        if not any(ign in p for ign in ["http://", "https://", "127.0.0.1"]):
            found_paths.add(p)
            if len(found_paths) >= 5:
                break

    # 3. Apply Layer 2 shrink
    shrunk_preview = shrink_content(text)
    preview_lines = [l for l in shrunk_preview.splitlines() if l.strip()][:4]

    out = ["[HEURISTIC EXTRACTION (Offline Fallback)]"]
    if focus:
        out.append(f"• Intent Scope: {focus}")
    if signal_lines:
        out.append("• Signals / Errors:")
        for s in signal_lines[:3]:
            out.append(f"  - {s[:120]}")
    if found_paths:
        out.append(f"• Referenced Paths: {', '.join(sorted(list(found_paths)))}")
    out.append("• Key Sample Lines:")
    for pl in preview_lines:
        out.append(f"  > {pl[:100]}")

    return "\n".join(out)


def distill_content(text: str, focus: str = "", model_name: str = "") -> str:
    """
    Unified entrypoint: tries local Ollama first, gracefully falls back to Layer 2 heuristic extraction.
    """
    base_url = resolve_ollama_base_url()
    if base_url:
        try:
            summary = distill_via_ollama(text, base_url, focus=focus, model_name=model_name)
            if summary:
                return summary
        except Exception as e:
            _log_telemetry(e, 'distill.py:call_ollama')
            print(f"[ORION DISTILL] Ollama call failed ({e}). Falling back to heuristic extraction...", file=sys.stderr)

    # Graceful Fallback
    print("[ORION DISTILL] Ollama offline or unreachable. Engaging Layer 2 heuristic fallback...", file=sys.stderr)
    return heuristic_fallback_distill(text, focus=focus)

def distill_main(argv=None):
    parser = argparse.ArgumentParser(description="Orion Distill Layer 3 Distillation")
    parser.add_argument("target", help="File or '-' for stdin")
    parser.add_argument("--focus", default="", help="Distillation focus")
    parser.add_argument("--model", dest="model_name", default="", help="Ollama model")
    args = parser.parse_args(argv)

    if args.target == "-":
        content = sys.stdin.read()
    elif os.path.exists(args.target):
        with open(args.target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        print(f"File not found: {args.target}", file=sys.stderr)
        return 1

    summary = distill_content(content, focus=args.focus, model_name=args.model_name)
    print(summary)
    return 0


# ============================================================================
# SECTION 4: SURGICAL MEMORY COMPRESSION
# ============================================================================

ARCHIVE_DIR = os.path.join(WORKSPACE_DIR, '.orion', 'archive')
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, 'compressed_memory.md')
HANDOFF_FILE = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'handoff.md')
VISION_FILE = os.path.join(WORKSPACE_DIR, 'context', 'VISION.md')
BLUEPRINT_FILE = os.path.join(WORKSPACE_DIR, 'context', '00_Strategy', 'BLUEPRINT.md')
STRATEGY_MEMORY_FILE = os.path.join(WORKSPACE_DIR, 'context', '00_Strategy', 'MEMORY.md')
LEGACY_MEMORY_FILE = os.path.join(WORKSPACE_DIR, 'MEMORY.md')

FRONTMATTER_REGEX = re.compile(r"\A(---\r?\n.*?\r?\n---\r?\n)(.*)", re.DOTALL)

SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)

SENSITIVE_PATH_COMPONENTS = frozenset({
    ".ssh", ".aws", ".gnupg", ".kube", ".docker",
    "credential", "credentials", "secret", "secrets",
})

def split_frontmatter(text: str):
    """Surgically detach YAML frontmatter before compression to prevent LLM destruction."""
    m = FRONTMATTER_REGEX.match(text)
    if m:
        return m.group(1), m.group(2)
    return "", text

def is_sensitive_path(path_str: str) -> bool:
    """Hard refusal check to protect secrets, credentials, private keys, and immutable VISION.md."""
    p = os.path.normpath(path_str)
    basename = os.path.basename(p)
    if basename.lower() == "vision.md" or p.replace("\\", "/").endswith("context/VISION.md"):
        return True
    if SENSITIVE_BASENAME_REGEX.match(basename):
        return True
    parts = set(p.lower().replace('\\', '/').split('/'))
    if parts & SENSITIVE_PATH_COMPONENTS:
        return True
    return False

# ============================================================================
# NATIVE ORION COMPACTOR & LESSWORD ENGINE (commands/brain.py)
# Pure Python 3.10+ Stdlib — Zero External Repo Fingerprints
# Implements AGENTS.md §2 & .agents/skills/lessword/SKILL.md Mechanically
# ============================================================================

LESSWORD_PHRASE_MAP: List[Tuple[re.Pattern, str]] = [
    # Pembuka percakapan & basa-basi (Ceremony & Staging)
    (re.compile(r"(?i)\b(?:sure|certainly|of course|i would be happy to|i'd be happy to|let me go ahead and|let's dive in|here is what you need to know|at its core)[,!.\s]*"), ""),
    (re.compile(r"(?i)\b(?:it might be worth|you could consider|it would be good to|please make sure to|make sure to|remember to)\s+"), ""),
    # Reduksi frasa bertele-tele menjadi kata kerja/hubung langsung
    (re.compile(r"(?i)\bin order to\b"), "to"),
    (re.compile(r"(?i)\bthe reason is because\b|\bdue to the fact that\b|\bas a result of\b"), "because"),
    (re.compile(r"(?i)\bimplement a solution for\b"), "fix"),
    (re.compile(r"(?i)\butilize\b|\butilizing\b"), "use"),
    (re.compile(r"(?i)\bfacilitate\b"), "help"),
    (re.compile(r"(?i)\bfor the purpose of\b"), "for"),
    (re.compile(r"(?i)\bin the event that\b"), "if"),
    (re.compile(r"(?i)\bwith regard to\b|\bwith respect to\b"), "on"),
    (re.compile(r"(?i)\bprior to\b"), "before"),
    (re.compile(r"(?i)\bsubsequent to\b"), "after"),
    (re.compile(r"(?i)\bis able to\b|\bhas the ability to\b"), "can"),
    (re.compile(r"(?i)\bextensive\b"), "big"),
    # Kata pengisi (Filler adverbs)
    (re.compile(r"(?i)\b(?:just|really|basically|actually|simply|essentially|generally|literally|definitely|honestly)\s+"), ""),
    (re.compile(r"(?i)\b(?:however|furthermore|additionally|in addition),?\s+"), ""),
]

LESSWORD_ULTRA_ABBREV: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"(?i)\bdatabase\b"), "DB"),
    (re.compile(r"(?i)\bauthentication\b"), "auth"),
    (re.compile(r"(?i)\bconfiguration\b"), "config"),
    (re.compile(r"(?i)\bimplementation\b"), "impl"),
    (re.compile(r"(?i)\bfunction\b"), "fn"),
    (re.compile(r"(?i)\brequest\b"), "req"),
    (re.compile(r"(?i)\bresponse\b"), "res"),
    (re.compile(r"(?i)\breference\b"), "ref"),
    (re.compile(r"(?i)\bparameter\b"), "param"),
    (re.compile(r"(?i)\bargument\b"), "arg"),
    (re.compile(r"(?i)\s+leads to\s+|\s+results in\s+|\s+causes\s+"), " -> "),
]

SAFETY_BOUNDARY_ESCAPE_RE = re.compile(
    r"(?is)\b(?:drop\s+table|delete\s+from|truncate\s+table|rm\s+-rf|git\s+reset\s+--hard|git\s+push\s+--force|cve-\d{4}-\d+|critical\s+vulnerability)\b"
    r"|\b(?:back\s*up|rollback|snapshot)\b.{1,200}\b(?:drop|delete|migrate|purge|destroy)\b"
)


class SyntaxAnchorGuard:
    """
    Pelindung payload verbatim sesuai aturan .agents/skills/lessword/references/lessword-compress.md:
    Mengisolasi code fences, inline backticks, URL, file paths, wikilinks, dan environment variables
    ke dalam slot memori sementara agar tidak pernah tersentuh oleh pemangkasan teks.
    """
    def __init__(self):
        self._slots: Dict[str, str] = {}
        self._seq: int = 0

    def _stash(self, match: re.Match) -> str:
        token = f"\x00__orion_anchor_{self._seq}__\x00"
        self._slots[token] = match.group(0)
        self._seq += 1
        return token

    def lock(self, text: str) -> str:
        # 1. Blok kode berpagar (```...``` atau ~~~...~~~) & Display LaTeX ($$...$$)
        text = re.sub(r"(?:```[\s\S]*?```|~~~[\s\S]*?~~~|\$\$[\s\S]*?\$\$)", self._stash, text)
        # 2. Inline code (`...`) & Inline LaTeX ($...$)
        text = re.sub(r"`[^`\n]+`|\$(?!\s)[^$\n]+(?<!\s)\$", self._stash, text)
        # 3. Wikilinks [[...]] & Markdown links [...](...) & URL
        text = re.sub(r"\[\[[^\]]+\]\]|\[[^\]]+\]\([^)]+\)|https?://[^\s)\]>]+", self._stash, text)
        # 4. Path file eksplisit & baris nomor (misal: .agents/scripts/orion.py:42)
        text = re.sub(r"(?<![/\w.-])[a-zA-Z0-9_.-]+/[a-zA-Z0-9_./-]+(?::\d+)?", self._stash, text)
        # 5. Environment variables & konstanta UPPER_SNAKE_CASE / akronim teknis (kecuali preposisi 2 huruf)
        text = re.sub(
            r"\$[A-Z_][A-Z0-9_]*|\b(?!(?:IN|ON|AT|TO|BY|OR|IF|IS|IT|AS|OF|DO|BE|WE|SO|AN)\b)[A-Z][A-Z0-9_]{1,}\b",
            self._stash,
            text,
        )
        # 6. Rasio matematis eksplisit (misal: 60:30:10, 16:9, 1:1)
        text = re.sub(r"\b\d+:\d+(?::\d+)?\b", self._stash, text)
        # 7. Batas pembanding fisik, persentase & unit (misal: <= 8px, >= 16000, 100%, 300 lines)
        text = re.sub(
            r"(?:[<>=!]=?|\b(?:<=|>=))\s*\d+(?:\.\d+)?\s*(?:px|%|ms|s|m|h|B|KB|MB|GB|tokens|lines|chars?|deg)?(?!\w)",
            self._stash,
            text,
        )
        text = re.sub(
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:px|%|ms|s|min|h|B|KB|MB|GB|tokens|lines|chars?)(?!\w)",
            self._stash,
            text,
        )
        # 8. Deterministic verification gates & exit code assertions (misal: Exit Code 0, exit code 1)
        text = re.sub(r"\b[Ee]xit [Cc]ode \d+\b", self._stash, text)
        return text

    def unlock(self, text: str) -> str:
        for token in reversed(list(self._slots.keys())):
            text = text.replace(token, self._slots[token])
        return text


class HumanizerEngine:
    """
    Deterministic AI-Slop & Structural Tell Detector/Cleaner (100% Python Stdlib).
    Works in tandem with SyntaxAnchorGuard in compact.py so code blocks, paths,
    and citations are 100% untouched. Grounded in Wikipedia: Signs of AI writing
    and standard structural prose guidelines (26 patterns).
    """

    AI_VOCABULARY = {
        "delve", "delves", "delving", "testament", "tapestry", "vibrant",
        "pivotal", "underscores", "underscoring", "showcasing", "garner",
        "garnered", "fostering", "intricate", "indelible", "enduring",
        "groundbreaking", "seamless", "seamlessly", "unwavering", "realm",
        "embark", "embarking", "synergy", "paramount", "multifaceted",
    }

    SAFE_SUBS: List[Tuple[re.Pattern, str]] = [
        # §22: Chatbot wrappers & openers
        (re.compile(r"(?im)\b(?:great question!|certainly!|absolutely!|sure thing!)\s*"), ""),
        (re.compile(r"(?im)\s*(?:i hope this helps!|let me know if you have any questions\.?|feel free to ask if[^\n]+)$"), ""),
        # §4: Staged run-ups
        (re.compile(r"(?im)^(?:let's dive right in\.?|let's dive in:?|without further ado,?|here's what you need to know:?|let's break this down:?)\s*"), ""),
        (re.compile(r"(?im)^(?:honestly\?|real talk:?|here's the thing:?|the thing is,?)\s+"), ""),
        # §2: Dramatic one-line clichés
        (re.compile(r"(?im)\s*\b(?:let that sink in\.|read that again\.|that is the real win\.|and that makes all the difference\.)"), ""),
        # §9: Stacked qualifiers
        (re.compile(r"\b(?:could|might)\s+potentially\s+possibly\b", re.I), "could"),
        (re.compile(r"\b(?:completely|totally|utterly)\s+and\s+(?:completely|totally|entirely)\b", re.I), "completely"),
        # §18: Copula avoidance ("serves as a" -> "is a")
        (re.compile(r"\bserves as a\b", re.I), "is a"),
        (re.compile(r"\bstands as a\b", re.I), "is a"),
        # §21: Curly quotation marks to straight ASCII
        (re.compile(r"[“”]"), '"'),
        (re.compile(r"[‘’]"), "'"),
    ]

    STRUCTURAL_DETECTORS: List[Tuple[str, str, re.Pattern]] = [
        ("§1 Not-X-but-Y Contrast", "STRONG", re.compile(
            r"\b(?:it(?:'s| is) not (?:just|merely|only) [^.;!\n]+[,;] it(?:'s| is) |not (?:just|merely|only) [^,;.\n]+, but (?:also |rather )?)", re.I
        )),
        ("§2 Post-Example Moral / Closer", "STRONG", re.compile(
            r"\b(?:this (?:shows|demonstrates|underscores|highlights) the importance of|the message was clear:|that distinction matters)\b", re.I
        )),
        ("§3 Pseudo-Deep Saying", "STRONG", re.compile(
            r"\b(?:at its core, what (?:really )?matters|the real question is whether|is the (?:currency|language|lifeblood) of|becomes a trap when)\b", re.I
        )),
        ("§5 Strawman / Arguing with No One", "STRONG", re.compile(
            r"\b(?:this isn't mainly about|i'm not saying that|don't get me wrong,|a tempting approach would be to|one might be tempted to)\b", re.I
        )),
        ("§13 Inflated Significance / Legacy", "MEDIUM", re.compile(
            r"\b(?:marking a pivotal moment|setting the stage for|a key turning point in|plays a vital role in shaping|the future looks bright)\b", re.I
        )),
        ("§15 Shallow -ing Participial Rider", "MEDIUM", re.compile(
            r",\s*(?:highlighting|underscoring|symbolizing|reflecting|showcasing|fostering)\s+(?:its|the|their|a|an)\s+[^.\n]+\.", re.I
        )),
        ("§17 Borrowed / Weasel Authority", "MEDIUM", re.compile(
            r"\b(?:experts believe that|industry leaders agree|many critics argue that|it is widely recognized that)\b", re.I
        )),
        ("§19 Decorative Bold-Label Bullet", "WEAK_ALONE", re.compile(
            r"(?m)^\s*[-*]\s+\*\*[A-Z][^*]{2,35}:\*\*\s+"
        )),
    ]

    @classmethod
    def audit_text(cls, protected_text: str) -> Dict[str, Any]:
        """Scan protected text (after SyntaxAnchorGuard) for the 26 Humanizer patterns."""
        findings: List[Dict[str, str]] = []
        for rule_name, severity, pattern in cls.STRUCTURAL_DETECTORS:
            for match in pattern.finditer(protected_text):
                snippet = match.group(0).strip().replace("\n", " ")
                findings.append({
                    "rule": rule_name,
                    "severity": severity,
                    "match": snippet[:90]
                })

        # §12 Check AI Vocabulary density
        words = re.findall(r"\b[a-zA-Z]{4,}\b", protected_text.lower())
        ai_hits = [w for w in words if w in cls.AI_VOCABULARY]
        if ai_hits:
            findings.append({
                "rule": "§12 Overused AI Vocabulary",
                "severity": "MEDIUM",
                "match": ", ".join(sorted(set(ai_hits)))
            })

        # §8 Check Em-Dash density (>3 per 1000 chars is a strong tell)
        em_dash_count = protected_text.count("—") + protected_text.count(" -- ")
        if em_dash_count >= 3:
            findings.append({
                "rule": "§8 Em-Dash Universal Connector",
                "severity": "WEAK_ALONE",
                "match": f"{em_dash_count} em-dashes detected"
            })

        return {
            "total_tells": len(findings),
            "strong_tells": sum(1 for f in findings if f["severity"] == "STRONG"),
            "findings": findings,
        }

    @classmethod
    def sanitize_deterministic(cls, protected_text: str) -> str:
        """Apply safe, meaning-preserving deterministic cleanups on prose only."""
        out = protected_text
        for pattern, replacement in cls.SAFE_SUBS:
            out = pattern.sub(replacement, out)
        out = re.sub(r"[ \t]{2,}", " ", out)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip()


STREAM_MAX_CHARS = 16000
STREAM_HEAD_LINES = 60
STREAM_TAIL_LINES = 40
STREAM_SALVAGE_MAX = 12
STREAM_SALVAGE_LINE = 300
STREAM_SPILL_KEEP = 40
STREAM_DIAGNOSTIC_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:err!|(?:error|errors|fail|failed|failure|failing|exception|traceback|panic|fatal"
    r"|denied|refused|timed?[ _-]?out|assert(?:ion)?|segfault|undefined reference|cannot find|not found|warning)"
    r"(?![A-Za-z0-9]))",
    re.IGNORECASE,
)


class OrionCompactor:
    """
    Mesin Kompresi Konteks & Memori Native .agents.
    Menyatukan protokol Lessword (lite, full, ultra), AST Hollowing,
    Payload Stream Shaping, dan Chronological Section Decay.
    """

    @staticmethod
    def requires_auto_clarity(text: str) -> bool:
        """Memeriksa apakah teks memuat peringatan keamanan atau operasi destruktif yang wajib jelas."""
        return bool(SAFETY_BOUNDARY_ESCAPE_RE.search(text))

    # -------------------------------------------------------------------------
    # TINGKAT 1: LITE (Lossless Cleanup — 0% Perubahan Semantik)
    # -------------------------------------------------------------------------
    @classmethod
    def run_lite(cls, text: str, elide: bool = True) -> str:
        if not text:
            return text
        # Bersihkan kode escape ANSI terminal
        clean = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
        # Pangkas data URI base64 gambar yang membengkakkan konteks
        clean = re.sub(
            r"data:image/[a-zA-Z+]+;base64,[a-zA-Z0-9+/=]{120,}",
            "[IMAGE_DATA_REDACTED]",
            clean,
        )
        # Lipat baris berulang yang identik & hapus trailing spaces
        lines = [line.rstrip() for line in clean.splitlines()]
        out_lines: List[str] = []
        prev = None
        dup_count = 0
        for line in lines:
            if line and line == prev:
                dup_count += 1
                continue
            if dup_count > 0:
                out_lines.append(f"  ... [repeated {dup_count}x] ...")
                dup_count = 0
            out_lines.append(line)
            prev = line
        if dup_count > 0:
            out_lines.append(f"  ... [repeated {dup_count}x] ...")

        if elide and len(out_lines) > 100:
            head = out_lines[:35]
            tail = out_lines[-45:]
            omitted = len(out_lines) - 80
            out_lines = head + [f"\n--- [... {omitted} lines omitted by Stream Filter ...] ---\n"] + tail

        return re.sub(r"\n{3,}", "\n\n", "\n".join(out_lines)).strip()

    # -------------------------------------------------------------------------
    # TINGKAT 1.5: STREAM (Bounded Tool Output — Diagnostics Survive the Cut)
    # -------------------------------------------------------------------------
    @staticmethod
    def _spill_full_output(text: str) -> Optional[str]:
        """Persist the untrimmed output so the dropped middle is searchable instead of re-run."""
        try:
            orion_dir = _get_orion_dir()
            workspace_dir = _get_workspace_dir()
            b = sys.modules.get("commands.brain")
            keep = getattr(b, "STREAM_SPILL_KEEP", STREAM_SPILL_KEEP) if b else STREAM_SPILL_KEEP
            spill_dir = os.path.join(orion_dir, "working", "spill")
            os.makedirs(spill_dir, exist_ok=True)
            digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]
            target = os.path.join(spill_dir, f"out-{digest}.txt")
            if not os.path.isfile(target):
                with open(target, "w", encoding="utf-8", errors="replace") as fh:
                    fh.write(text)
            stale = sorted(
                (os.path.join(spill_dir, n) for n in os.listdir(spill_dir) if n.endswith(".txt")),
                key=os.path.getmtime,
                reverse=True,
            )[keep:]
            for old in stale:
                os.remove(old)
            return os.path.relpath(target, workspace_dir).replace("\\", "/")
        except OSError as _e:
            _log_telemetry(_e, "OrionCompactor:_spill_full_output")
            return None

    @classmethod
    def elide_output(
        cls,
        text: str,
        max_chars: int = STREAM_MAX_CHARS,
        head: int = STREAM_HEAD_LINES,
        tail: int = STREAM_TAIL_LINES,
        spill: bool = True,
    ) -> str:
        """Bound oversized output: keep the opening and closing lines, rescue diagnostic lines from the cut middle."""
        if not text or len(text) <= max_chars:
            return text
        recover = ""
        if spill:
            path = cls._spill_full_output(text)
            if path:
                recover = f" Full output: {path} (search it; do not re-run)."
        lines = text.splitlines()
        if len(lines) <= head + tail:
            keep = max_chars // 2
            dropped = len(text) - 2 * keep
            if dropped <= 0:
                return text
            return f"{text[:keep]}\n... [elided {dropped} chars from the middle.{recover}] ...\n{text[-keep:]}"

        middle = lines[head:len(lines) - tail]
        rescued: List[str] = []
        for line in middle:
            if len(rescued) >= STREAM_SALVAGE_MAX:
                break
            if STREAM_DIAGNOSTIC_RE.search(line):
                rescued.append(line if len(line) <= STREAM_SALVAGE_LINE else line[:STREAM_SALVAGE_LINE - 1] + "…")
        note = f"; {len(rescued)} diagnostic line(s) kept below" if rescued else ""
        marker = f"... [elided {len(middle)} lines; kept first {head}, last {tail}{note}.{recover}] ..."
        bounded = "\n".join(lines[:head] + [marker] + rescued + lines[len(lines) - tail:])
        return bounded if len(bounded) < len(text) else text

    @classmethod
    def run_stream(cls, text: str) -> str:
        """Lossless cleanup followed by diagnostic-preserving elision, for terminal and tool output."""
        return cls.elide_output(cls.run_lite(text, elide=False))

    # -------------------------------------------------------------------------
    # TINGKAT 2: FULL (Standar Default Lessword — ASD-STE100 Concise Prose)
    # -------------------------------------------------------------------------
    @classmethod
    def run_full(cls, text: str, check_safety_escape: bool = True) -> str:
        if not text:
            return text
        frontmatter, body = split_frontmatter(text)
        body = cls.run_lite(body)

        # Auto-Clarity Escape: jangan pangkas kalimat jika berisi operasi destruktif/keamanan
        if check_safety_escape and cls.requires_auto_clarity(body):
            return (frontmatter + body) if frontmatter else body

        guard = SyntaxAnchorGuard()
        locked = guard.lock(body)

        for pattern, replacement in LESSWORD_PHRASE_MAP:
            locked = pattern.sub(replacement, locked)

        # Hapus artikel (a, an, the) dengan tetap menjaga heading, tabel, dan kata negasi
        processed_lines: List[str] = []
        for line in locked.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or "|" in stripped:
                processed_lines.append(line)
                continue
            compact_line = re.sub(r"(?i)\b(?:a|an|the|basically|actually|simply|certainly|surely|definitely)\s+", "", line)
            compact_line = re.sub(r"[ \t]{2,}", " ", compact_line)
            processed_lines.append(compact_line)

        unlocked = guard.unlock("\n".join(processed_lines))
        return (frontmatter + unlocked) if frontmatter else unlocked

    # -------------------------------------------------------------------------
    # PAYLOAD STREAM SHAPER (Deteksi Otomatis Kode, Grep, Traceback, JSON, CSV)
    # -------------------------------------------------------------------------
    @classmethod
    def shape_structured_payload(cls, text: str, filename_hint: str = "") -> Tuple[str, str]:
        if not text:
            return text, "prose"
        if len(text) < 180 and not filename_hint:
            return text, "prose"

        lines = text.splitlines()
        hint = filename_hint.lower()

        # 1. Kode Sumber -> AST Structural Hollowing (.py, .ts, .dart, .rs, .go, .kt)
        code_sig_re = re.compile(r"^\s*(?:import |from |export |class |def |async def |function |pub fn |fn |struct |interface )")
        code_hits = sum(1 for l in lines[:50] if code_sig_re.match(l))
        is_markdown = hint.endswith((".md", ".markdown", ".mdown", ".mkd")) or any(l.strip().startswith(("# ", "## ")) for l in lines[:10])
        if not is_markdown and (hint.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".dart", ".rs", ".go", ".kt", ".java", ".cpp", ".c", ".cs")) or code_hits >= 2):
            if hint.endswith(".py") or "def " in text:
                return shrink_ast_python(text), "ast_python"
            return shrink_ast_generic(text), "ast_polyglot"

        # 2. Output Pencarian Baris (`path:line:match` — bukan jam `12:30:00`)
        span_re = re.compile(r"^([^\s:]+):(\d+):(.*)$")
        span_hits = [l for l in lines if span_re.match(l.strip()) and not re.match(r"^\d{2}:\d{2}:\d{2}", l.strip())]
        if len(span_hits) >= 4 and len(span_hits) >= len(lines) * 0.4:
            kept = span_hits[:30]
            overflow = len(span_hits) - len(kept)
            if overflow > 0:
                files = sorted({span_re.match(l.strip()).group(1) for l in span_hits[30:] if span_re.match(l.strip())})
                kept.append(f"... [+{overflow} matches in {len(files)} files: {', '.join(files[:6])}] ...")
            return "\n".join(kept), "search_spans"

        # 3. Stack Trace / Error Frame Elision (Header + 10 first + 3 root-cause frames)
        is_traceback = "traceback (most recent call last)" in text.lower() or (
            any(lines[0].lower().startswith(p) for p in ("traceback", "exception:", "error:"))
        )
        if is_traceback and len(lines) > 16:
            elided_count = len(lines) - 14
            if elided_count > 0:
                shaped = [lines[0]] + lines[1:11] + [f"  ... [{elided_count} stack frames elided] ..."] + lines[-3:]
                return "\n".join(shaped), "error_trace"

        # 4. Struktur Data JSON & CSV
        trimmed = text.strip()
        if (hint.endswith(".json") or trimmed.startswith(("{", "["))) and len(trimmed) > 800:
            try:
                return shrink_json(trimmed, max_items=2), "json_schema"
            except Exception as _e:
                _log_telemetry(_e, "OrionCompactor:shrink_json")
        if hint.endswith((".csv", ".tsv")) and len(lines) > 12:
            return shrink_csv(text, max_rows=3), "csv_schema"

        # 5. Log Terminal Panjang
        if len(lines) > 65:
            return shrink_log(text), "log_stream"

        return text, "prose"

    # -------------------------------------------------------------------------
    # CHRONOLOGICAL SECTION DECAY (Pemadatan Memori & Handoff Berbasis Usia Seksi)
    # -------------------------------------------------------------------------
    @classmethod
    def decay_historical_sections(cls, text: str, fresh_keep: int = 2, mid_keep: int = 4) -> str:
        """
        Memadatkan seksi-seksi lama (`## ...`) pada dokumen memori/handoff/log:
          - 2 seksi terbaru : Dipertahankan 100% utuh (verbatim)
          - Seksi ke-3..4   : Dikompresi dengan mode Lessword Full
          - Seksi ke-5+     : Dipadatkan menjadi judul + 1 baris intisari (<=120 karakter)
        Seksi kritis (Resume Point, Anti-Goals, Fractal Shorthand) selalu dilindungi.
        """
        frontmatter, body = split_frontmatter(text)
        blocks = re.split(r"(?m)^(?=##\s+)", body)
        if len(blocks) <= fresh_keep + 1:
            return text

        preamble = blocks[0] if not blocks[0].startswith("## ") else ""
        sections = blocks[1:] if preamble else blocks

        protected_headers = ("resume point", "anti-goal", "fractal shorthand", "active state", "core guardrail")

        # Calculate chronological age distance across non-protected sections
        non_protected_indices = [
            i for i, sec in enumerate(sections)
            if not any(p in sec.splitlines()[0].lower() for p in protected_headers if sec.strip().splitlines())
        ]
        total_np = len(non_protected_indices)
        np_rank_map = {orig_idx: (total_np - 1 - rank) for rank, orig_idx in enumerate(non_protected_indices)}

        out_sections: List[str] = []

        for idx, sec in enumerate(sections):
            sec_lines = [l for l in sec.strip().splitlines() if l.strip()]
            if not sec_lines:
                continue

            header = sec_lines[0]
            if any(p in header.lower() for p in protected_headers):
                out_sections.append(sec.strip())
                continue
            if sec.count("```") > 0:
                out_sections.append(cls.run_full(sec.strip()))
                continue
            age_distance = np_rank_map.get(idx, 0)

            if age_distance < fresh_keep:
                out_sections.append(sec.strip())
            elif age_distance < mid_keep:
                out_sections.append(cls.run_full(sec.strip()))
            else:
                preserved_bullets = [header]
                for l in sec_lines[1:]:
                    s_l = l.strip()
                    if s_l.startswith(("#", "- ", "* ")) or re.match(r"^\d+\.\s+", s_l):
                        preserved_bullets.append(s_l[:140] + ("..." if len(s_l) > 140 else ""))
                if len(preserved_bullets) == 1 and len(sec_lines) > 1:
                    preserved_bullets.append(f"- {sec_lines[1].strip()[:140]}")
                kept = preserved_bullets[:7]
                dropped = len(sec_lines) - len(kept)
                if dropped > 0 or len(preserved_bullets) > 7:
                    total_dropped = max(1, len(sec_lines) - len(kept))
                    kept.append(f"  ... [{total_dropped} historical lines archived]")
                out_sections.append("\n".join(kept))

        combined = (preamble.rstrip() + "\n\n" if preamble.strip() else "") + "\n\n".join(out_sections)
        return (frontmatter + combined) if frontmatter else combined

    # -------------------------------------------------------------------------
    # TINGKAT 3: AGGRESSIVE (Payload Shaper + Chronological Decay + Lessword Full)
    # -------------------------------------------------------------------------
    @classmethod
    def run_aggressive(cls, text: str, filename_hint: str = "") -> Tuple[str, List[str]]:
        shaped, kind = cls.shape_structured_payload(text, filename_hint=filename_hint)
        if kind != "prose":
            return shaped, [f"shaper:{kind}"]

        steps = []
        current = text
        if current.count("\n## ") >= 3:
            current = cls.decay_historical_sections(current, fresh_keep=2, mid_keep=4)
            steps.append("chronological_decay")

        current = cls.run_full(current)
        steps.append("lessword_full")
        return current, steps

    # -------------------------------------------------------------------------
    # TINGKAT 4: ULTRA (Surprisal Pruning + Telegraphic Abbreviations)
    # -------------------------------------------------------------------------
    @classmethod
    def run_ultra(cls, text: str, filename_hint: str = "", ratio: float = 0.5) -> Tuple[str, List[str]]:
        shaped, kind = cls.shape_structured_payload(text, filename_hint=filename_hint)
        if kind in ("ast_python", "ast_polyglot", "json_schema", "csv_schema", "search_spans", "error_trace"):
            return shaped, [f"shaper:{kind}"]

        frontmatter, body = split_frontmatter(text)
        if body.count("\n## ") >= 3:
            body = cls.decay_historical_sections(body, fresh_keep=1, mid_keep=3)

        body = cls.run_full(body, check_safety_escape=True)
        if cls.requires_auto_clarity(body):
            return ((frontmatter + body) if frontmatter else body), ["safety_escape_bypass"]

        # Tier-1: Neural Distillation via Ollama if available for substantial prose
        try:
            from core.capabilities import resolve_ollama_base_url
            ollama_url = resolve_ollama_base_url()
            if ollama_url and len(body) > 500 and not filename_hint.endswith((".py", ".ts", ".dart", ".go", ".rs", ".json")):
                distilled = distill_via_ollama(body, ollama_url)
                if distilled and len(distilled) < len(body):
                    final_text = (frontmatter + "\n" + distilled) if frontmatter else distilled
                    return final_text, ["chronological_decay", "neural_distill_ollama"]
        except Exception as _e:
            _log_telemetry(_e, "compact.py:distill_via_ollama")

        guard = SyntaxAnchorGuard()
        locked = guard.lock(body)

        # Terapkan singkatan Ultra sesuai spesifikasi .agents/skills/lessword/SKILL.md
        for pattern, abbrev in LESSWORD_ULTRA_ABBREV:
            locked = pattern.sub(abbrev, locked)

        # Pangkas token bersurprisal rendah melalui fts5vocab di .orion/orion.db (preserve_code=False karena sudah di-lock oleh guard di atas)
        with CorpusInformationCompactor() as compactor:
            pruned = compactor.compact(locked, keep_ratio=ratio, preserve_code=False)

        unlocked = guard.unlock(pruned)
        final_text = (frontmatter + unlocked) if frontmatter else unlocked
        return final_text, ["chronological_decay", "lessword_ultra_abbrev", "surprisal_fts5vocab"]

    # -------------------------------------------------------------------------
    # TINGKAT 5: PIPELINE (Rantai Deterministik Multi-Tahap — Default)
    # -------------------------------------------------------------------------
    @classmethod
    def run_pipeline(cls, text: str, filename_hint: str = "") -> Tuple[str, List[str]]:
        stages: List[str] = []
        current = cls.run_lite(text)
        stages.append("lite_clean")

        shaped, kind = cls.shape_structured_payload(current, filename_hint=filename_hint)
        if kind != "prose" and len(shaped) < len(current):
            current = shaped
            stages.append(f"shaper:{kind}")

        if current.count("\n## ") >= 3:
            decayed = cls.decay_historical_sections(current, fresh_keep=2, mid_keep=4)
            if len(decayed) < len(current):
                current = decayed
                stages.append("section_decay")

        if kind not in ("ast_python", "ast_polyglot", "json_schema", "csv_schema"):
            lw = cls.run_full(current)
            if len(lw) < len(current):
                current = lw
                stages.append("lessword_full")

        return current, stages

    # -------------------------------------------------------------------------
    # INTEGRITY VERIFICATION GATE (Anti-Regression & Zero-Corruption Check)
    # -------------------------------------------------------------------------
    @classmethod
    def compress(cls, text: str, level: str = "pipeline", filename_hint: str = "", ratio: float = 0.5) -> Dict[str, Any]:
        t_start = time.time()
        lvl = level.lower().strip()

        if lvl == "off":
            out, stages = text, []
        elif lvl == "lite":
            out, stages = cls.run_lite(text), ["lite_clean"]
        elif lvl == "stream":
            out, stages = cls.run_stream(text), ["lite_clean", "stream_elide"]
        elif lvl in ("full", "standard", "pipeline", "lessword"):
            lvl = "full"
            out, stages = cls.run_pipeline(text, filename_hint=filename_hint)
        elif lvl == "aggressive":
            out, stages = cls.run_aggressive(text, filename_hint=filename_hint)
        elif lvl == "ultra":
            out, stages = cls.run_ultra(text, filename_hint=filename_hint, ratio=ratio)
        else:
            lvl = "full"
            out, stages = cls.run_pipeline(text, filename_hint=filename_hint)

        orig_tokens = max(1, math.ceil(len(text) / 4.0))
        comp_tokens = max(1, math.ceil(len(out) / 4.0))
        delta_tokens = orig_tokens - comp_tokens

        # Gate 1: Pastikan pagar kode (```) tidak ada yang terpotong
        fence_mismatch = (lvl not in ("stream", "ultra") and text.count("```") != out.count("```")) or (out.count("```") % 2 != 0)
        if fence_mismatch:
            return {
                "output": text,
                "level": lvl,
                "status": "REVERTED_FENCE_MISMATCH",
                "original_tokens": orig_tokens,
                "compressed_tokens": orig_tokens,
                "savings_pct": 0.0,
                "stages": stages,
                "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
            }

        # Gate 2: Jika tidak ada penghematan nyata, kembalikan teks asli tanpa modifikasi
        if delta_tokens <= 0 or len(out) >= len(text):
            return {
                "output": text,
                "level": lvl,
                "status": "UNCHANGED_OPTIMAL",
                "original_tokens": orig_tokens,
                "compressed_tokens": orig_tokens,
                "savings_pct": 0.0,
                "stages": stages,
                "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
            }

        return {
            "output": out,
            "level": lvl,
            "status": "COMPRESSED",
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "savings_pct": round((delta_tokens / orig_tokens) * 100.0, 2),
            "stages": stages,
            "elapsed_ms": round((time.time() - t_start) * 1000.0, 2),
        }


def telegraphic_shrink(text: str) -> str:
    """Alias kompatibilitas ke OrionCompactor level full."""
    return OrionCompactor.compress(text, level="full")["output"]


def lessword_compress_text(text: str, level: str = "full") -> str:
    """Mesin utama Lessword yang kini dilindungi SyntaxAnchorGuard."""
    return OrionCompactor.compress(text, level=level)["output"]


lessword_compress = lessword_compress_text


def compact_target(target_path: str, ratio: float = 0.5, level: str = "full") -> Tuple[str, str]:
    """Router file tunggal menggunakan OrionCompactor."""
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target not found: {target_path}")
    with open(target_path, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()
    res = OrionCompactor.compress(content, level=level, filename_hint=target_path, ratio=ratio)
    return res["output"], "+".join(res["stages"]) or "unchanged"


def compactor_main(argv=None):
    parser = argparse.ArgumentParser(description="Native Orion Compactor & Lessword Engine")
    parser.add_argument("target", nargs="?", help="Text string or path to file")
    parser.add_argument("--text", type=str, help="Prose string to compact")
    parser.add_argument("--file", type=str, help="Path to text or markdown file to compact")
    parser.add_argument("--level", type=str, default="full", choices=["lite", "stream", "full", "aggressive", "ultra", "pipeline", "off"], help="Compression level: lite, full (default), ultra")
    parser.add_argument("--ratio", type=float, default=0.5, help="Retention ratio for ultra/surprisal pruning")
    parser.add_argument("--stdin", action="store_true", help="Read the text to compact from standard input")
    parser.add_argument("--humanize", action="store_true", help="Apply deterministic de-slopping and AI-tell removal (WP:AISIGNS & prose authenticity)")
    parser.add_argument("--humanize-check", action="store_true", help="Audit prose for 26 AI writing tells without modifying text")
    parser.add_argument("--index", type=str, help="Deprecated index argument (noop)")
    args = parser.parse_args(argv)

    target_file = args.file or (args.target if args.target and os.path.exists(args.target) else None)

    if target_file and os.path.isfile(target_file):
        with open(target_file, "r", encoding="utf-8-sig", errors="replace") as f:
            raw_input = f.read()

        guard = SyntaxAnchorGuard()
        protected = guard.lock(raw_input)

        if args.humanize_check:
            report = HumanizerEngine.audit_text(protected)
            print(f"[HUMANIZER AUDIT: {target_file}] Total Tells: {report['total_tells']} (Strong: {report['strong_tells']})")
            for finding in report["findings"]:
                print(f"  - [{finding['severity']}] {finding['rule']}: {finding['match']}")
            return 1 if report["strong_tells"] > 0 else 0

        if args.humanize:
            cleaned_protected = HumanizerEngine.sanitize_deterministic(protected)
            raw_input = guard.unlock(cleaned_protected)

        res = OrionCompactor.compress(raw_input, level=args.level, filename_hint=target_file, ratio=args.ratio)
        compacted = res["output"]
        orig_words = len(raw_input.split())
        comp_words = len(compacted.split())
        stages_str = "+".join(res["stages"]) or "unchanged"
        if args.humanize:
            stages_str += "+humanize"
        print(f"[COMPACTION SUMMARY: {stages_str}] Level: {res['level']} | Status: {res['status']} | Orig: {res['original_tokens']} tok ({orig_words} words) | Compact: {res['compressed_tokens']} tok ({comp_words} words) | Savings: {res['savings_pct']}% ({res['elapsed_ms']}ms)")
        print("--------------------------------------------------------------------------------")
        print(compacted)
        return 0

    input_text = ""
    if args.stdin:
        input_text = sys.stdin.read()
    elif args.text:
        input_text = args.text
    elif args.target and not os.path.exists(args.target):
        input_text = args.target

    if not input_text:
        parser.print_help()
        return 1

    guard = SyntaxAnchorGuard()
    protected = guard.lock(input_text)

    if args.humanize_check:
        report = HumanizerEngine.audit_text(protected)
        print(f"[HUMANIZER AUDIT] Total Tells: {report['total_tells']} (Strong: {report['strong_tells']})")
        for finding in report["findings"]:
            print(f"  - [{finding['severity']}] {finding['rule']}: {finding['match']}")
        return 1 if report["strong_tells"] > 0 else 0

    if args.humanize:
        cleaned_protected = HumanizerEngine.sanitize_deterministic(protected)
        input_text = guard.unlock(cleaned_protected)

    res = OrionCompactor.compress(input_text, level=args.level, ratio=args.ratio)
    compacted = res["output"]
    orig_words = len(input_text.split())
    comp_words = len(compacted.split())
    stages_str = "+".join(res["stages"]) or "unchanged"
    if args.humanize:
        stages_str += "+humanize"
    print(f"[COMPACTION SUMMARY: {stages_str}] Level: {res['level']} | Status: {res['status']} | Orig: {res['original_tokens']} tok ({orig_words} words) | Compact: {res['compressed_tokens']} tok ({comp_words} words) | Savings: {res['savings_pct']}% ({res['elapsed_ms']}ms)")
    print("--------------------------------------------------------------------------------")
    print(compacted)
    return 0

def get_strategy_memory_file():

    if os.path.exists(STRATEGY_MEMORY_FILE):
        return STRATEGY_MEMORY_FILE
    if os.path.exists(LEGACY_MEMORY_FILE):
        return LEGACY_MEMORY_FILE
    return STRATEGY_MEMORY_FILE

def generate_fractal_shorthand(dry_run: bool = False):
    """
    Parses architectural details from BLUEPRINT.md and translates it into a
    highly compressed Fractal State Shorthand (DSL) for small models.
    """
    if not os.path.exists(BLUEPRINT_FILE):
        return False
        
    with open(BLUEPRINT_FILE, 'r', encoding='utf-8') as f:
        blueprint = f.read()
        
    shorthand = "[ARCH: "
    
    # Holographic Context Hash Generation (Idea 1)
    import hashlib
    state_hash = hashlib.sha256(blueprint.encode()).hexdigest()[:4].upper()
    shorthand = f"[STATE_HASH: 0x{state_hash}] [ARCH: "
    
    if "flutter" in blueprint.lower(): shorthand += "Flutter]"
    elif "react" in blueprint.lower(): shorthand += "React]"
    else: shorthand += "Unknown]"
    
    if "supabase" in blueprint.lower(): shorthand += " [DB: Supabase]"
    if "riverpod" in blueprint.lower(): shorthand += " [STATE: Riverpod]"
    
    shorthand += " [TIER: BUDGET]"
    
    if dry_run:
        print(f"[DRY RUN] Generated Fractal Shorthand: {shorthand}")
        return True

    updated = False
    # Inject into handoff
    if os.path.exists(HANDOFF_FILE):
        with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
            handoff = f.read()
            
        if "# FRACTAL SHORTHAND" in handoff:
            new_handoff = re.sub(r'(# FRACTAL SHORTHAND\r?\n).*?(?=\n\n)', r'\1' + shorthand, handoff, flags=re.DOTALL)
        else:
            new_handoff = f"# FRACTAL SHORTHAND\n{shorthand}\n\n" + handoff
            
        atomic_write_text(HANDOFF_FILE, new_handoff)
        updated = True

    # Inject into standard context memory file
    mem_file = get_strategy_memory_file()
    if os.path.exists(mem_file):
        with open(mem_file, 'r', encoding='utf-8') as f:
            mem_content = f.read()
        if "# FRACTAL SHORTHAND" in mem_content:
            new_mem = re.sub(r'(# FRACTAL SHORTHAND\r?\n).*?(?=\n\n)', r'\1' + shorthand, mem_content, flags=re.DOTALL)
        else:
            new_mem = f"# FRACTAL SHORTHAND\n{shorthand}\n\n" + mem_content
        if new_mem != mem_content:
            with open(mem_file, 'w', encoding='utf-8') as f:
                f.write(new_mem)
        updated = True

    if updated:
        print(f"[OK] Generated Fractal Shorthand: {shorthand}")
        return True
    return False

def compress_handoff(dry_run: bool = False):
    if not os.path.exists(HANDOFF_FILE):
        return False

    with open(HANDOFF_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for Offload entries to compress (anything between 3. Context Offloading and 4. Anti-Goals)
    offload_pattern = r'(## 3\. Context Offloading Entry.*?\n)(?=\n## 4\.|\n## \d+\.|$)'
    
    match = re.search(offload_pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return False

    offloaded_text = match.group(1).strip()
    
    if "placeholder" in offloaded_text.lower():
        return False

    def lessword_compress_section(m):
        text = m.group(0)
        compressed_text = lessword_compress_text(text)
        return f"## 3. Context Offloading Entry\n> [COMPRESSED: Lessword Token-Clipper Active]\n{compressed_text}\n\n"

    new_handoff_content = re.sub(
        r'(## 3\. Context Offloading Entry\n).*?(?=\n## 4\.|\n## \d+\.|$)',
        lessword_compress_section,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    if content == new_handoff_content:
         return False

    if dry_run:
        print("[DRY RUN] Would compress handoff memory and archive offloaded section.")
        return True

    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
    mode = 'a' if os.path.exists(ARCHIVE_FILE) else 'w'
    with open(ARCHIVE_FILE, mode, encoding='utf-8') as f:
        f.write(f"\n\n--- Compressed on {datetime.now()} ---\n{offloaded_text}")

    # Rewrite handoff
    atomic_write_text(HANDOFF_FILE, new_handoff_content)
        
    print(f"[OK] Handoff memory successfully compressed.")
    return True

def compress_tasks(dry_run: bool = False):
    tasks_dir = os.path.join(WORKSPACE_DIR, '.orion', 'working', 'tasks')
    if not os.path.exists(tasks_dir):
        return False
        
    if not os.path.exists(ARCHIVE_DIR):
        if not dry_run:
            os.makedirs(ARCHIVE_DIR, exist_ok=True)

    compressed = False
    for file in os.listdir(tasks_dir):
        if not file.endswith('.md'): continue
        path = os.path.join(tasks_dir, file)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Target status indicators meaning the task is done
        is_done = bool(re.search(r'Status:\s*\[x\]', content, re.IGNORECASE) or re.search(r'Status:\s*DONE', content, re.IGNORECASE))
        if is_done:
            dest = os.path.join(ARCHIVE_DIR, file)
            if dry_run:
                print(f"[DRY RUN] Would archive completed task: {file}")
            else:
                shutil.move(path, dest)
                print(f"[OK] Archived completed task: {file}")
            compressed = True
    return compressed
            

def check_compression_eligibility():
    """
    IDE-4: Smart Memory Compression with Eligibility Rules.
    Checks orion.db to report which pages/nodes are eligible for compression
    and which are protected. Inspired by Cloudflare's compression eligibility.
    """
    db_path = os.path.join(WORKSPACE_DIR, '.orion', 'orion.db')
    if not os.path.exists(db_path):
        print("[SKIP] No orion.db found — eligibility check skipped.")
        return
    
    conn = connect_sqlite(db_path)
    cursor = conn.cursor()
    
    # Check if access_count column exists
    cursor.execute("PRAGMA table_info(pages)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'access_count' not in cols:
        print("[SKIP] pages.access_count not yet migrated — skipping eligibility filter.")
        conn.close()
        return
    
    IMPORTANCE_THRESHOLD = 4
    MIN_ACCESS_COUNT = 2
    MIN_AGE_DAYS = 14
    
    # Find eligible pages
    cursor.execute("""
        SELECT path, access_count, importance, updated 
        FROM pages 
        WHERE (importance IS NULL OR importance < ?)
        AND (access_count IS NULL OR access_count < ?)
        AND (julianday('now') - julianday(COALESCE(updated, datetime('now')))) >= ?
        ORDER BY updated ASC
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT, MIN_AGE_DAYS))
    
    eligible = cursor.fetchall()
    
    # Find protected pages
    cursor.execute("""
        SELECT path, access_count, importance 
        FROM pages 
        WHERE importance >= ? OR access_count >= ?
    """, (IMPORTANCE_THRESHOLD, MIN_ACCESS_COUNT))
    
    protected = cursor.fetchall()
    
    print(f"[ELIGIBILITY] {len(eligible)} pages eligible for compression, {len(protected)} protected.")
    
    if eligible:
        for path, ac, imp, updated in eligible[:5]:
            print(f"  📋 {path} (access={ac or 0}, importance={imp or 1})")
    
    if protected:
        for path, ac, imp in protected[:5]:
            print(f"  🛡️ {path} (access={ac or 0}, importance={imp or 1}) — PROTECTED")
    
    conn.close()


def compress_strategy_memory(dry_run: bool = False):
    mem_file = get_strategy_memory_file()
    if not os.path.exists(mem_file):
        return False
    with open(mem_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    if len(lines) > 300:
        print(f"[NOTICE] {os.path.basename(mem_file)} has {len(lines)} lines (>300). Pruning archived entries.")
        milestone_match = re.search(r'(## ✅ Tactical Milestones\r?\n)(.*?)(?=\r?\n## |\Z)', content, re.DOTALL)
        if milestone_match:
            milestones = [m for m in milestone_match.group(2).strip().splitlines() if m.strip()]
            if len(milestones) > 5:
                to_archive = milestones[:-5]
                to_keep = milestones[-5:]
                if dry_run:
                    print(f"[DRY RUN] Would archive {len(to_archive)} completed milestones from {os.path.basename(mem_file)}.")
                    return True
                if not os.path.exists(ARCHIVE_DIR):
                    os.makedirs(ARCHIVE_DIR, exist_ok=True)
                with open(ARCHIVE_FILE, 'a', encoding='utf-8') as af:
                    af.write(f"\n\n--- Archived Milestones from MEMORY.md on {datetime.now()} ---\n" + "\n".join(to_archive))
                new_milestones_block = milestone_match.group(1) + "\n".join(to_keep) + "\n"
                content = content.replace(milestone_match.group(0), new_milestones_block)
                atomic_write_text(mem_file, content)
                print(f"[OK] Archived {len(to_archive)} completed milestones from {os.path.basename(mem_file)}.")
                return True
    return False

def compress_file(target_path: str, dry_run: bool = False) -> bool:
    """
    Compress a specific target markdown/text file into lessword format.
    Guarantees:
    - Rejects sensitive files (security policy)
    - Preserves frontmatter verbatim via split_frontmatter
    - Preserves code fences, URLs, and paths
    - Saves human-readable backup to <filename>.original.md
    """
    abs_path = os.path.abspath(target_path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] Target file does not exist: {target_path}")
        return False
    if is_sensitive_path(abs_path) or abs_path.replace("\\", "/").endswith("context/VISION.md"):
        print(f"[REFUSED] Refusing to compress immutable file: {os.path.basename(abs_path)}")
        return False
    if abs_path.endswith('.original.md'):
        print(f"[SKIP] Refusing to re-compress backup file: {os.path.basename(abs_path)}")
        return False
        
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}")
        return False
        
    compressed_content = lessword_compress_text(content)
    orig_words = len(content.split())
    comp_words = len(compressed_content.split())
    savings = (1 - (comp_words / orig_words)) * 100 if orig_words > 0 else 0

    if dry_run:
        print(f"[DRY RUN] Would compress {os.path.basename(abs_path)}: {orig_words} words -> {comp_words} words ({savings:.1f}% reduction).")
        return True

    backup_path = abs_path + ".original.md" if not abs_path.endswith('.md') else abs_path[:-3] + ".original.md"
    if not os.path.exists(backup_path):
        atomic_write_text(backup_path, content)
        print(f"[BACKUP] Original saved to: {os.path.basename(backup_path)}")
        
    atomic_write_text(abs_path, compressed_content)
        
    print(f"[OK] Compressed {os.path.basename(abs_path)}: {orig_words} words -> {comp_words} words ({savings:.1f}% reduction).")
    return True

def compress_memory(dry_run: bool = False):
    print(f"[CLEAN] Surgical Memory Compression starting... {'(DRY RUN)' if dry_run else ''}")
    check_compression_eligibility()
    generate_fractal_shorthand(dry_run=dry_run)
    strategy_compressed = compress_strategy_memory(dry_run=dry_run)
    handoff_compressed = compress_handoff(dry_run=dry_run)
    tasks_compressed = compress_tasks(dry_run=dry_run)
    
    if not strategy_compressed and not handoff_compressed and not tasks_compressed:
        print("[OK] No compressable context found. System memory is lean and efficient.")
    else:
        status_msg = "Memory compression simulated." if dry_run else f"Memory compression complete. Stale memories moved to {ARCHIVE_DIR}"
        print(f"[OK] {status_msg}")

def compress_main(argv=None):
    parser = argparse.ArgumentParser(description="Compress memory and markdown files into lessword format.")
    parser.add_argument("target", nargs="?", default=None, help="Specific file to compress")
    parser.add_argument("--file", type=str, default=None, help="Specific file to compress")
    parser.add_argument("--dry-run", action="store_true", help="Simulate compression without modifying files")
    args = parser.parse_args(argv)

    target_path = args.target or args.file
    if target_path:
        compress_file(target_path, dry_run=args.dry_run)
    else:
        compress_memory(dry_run=args.dry_run)
    return 0


def compact_main(argv=None):
    """Entry point for standalone compact CLI."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return compactor_main(["--help"])
    cmd = argv[0]
    if cmd in ("--help", "-h"):
        return compactor_main(["--help"])
    if cmd in ("compress", "compress_memory"):
        return compress_main(argv[1:])
    elif cmd == "shrink":
        return shrink_main(argv[1:])
    elif cmd == "distill":
        return distill_main(argv[1:])
    elif cmd in ("compact", "compactor"):
        return compactor_main(argv[1:])
    else:
        return compactor_main(argv)


if __name__ == "__main__":
    sys.exit(compact_main(sys.argv[1:]))



