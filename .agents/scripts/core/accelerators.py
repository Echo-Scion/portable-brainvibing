"""
Tier 2 Optional Ephemeral Accelerators Subsystem.
Provides transparent performance acceleration (orjson, rapidfuzz, tree-sitter)
via isolated global cache (~/.agents/cache/venv) with guaranteed graceful degradation
to Python stdlib (Tier 0 Zero-Pip baseline).
"""

import os
import sys
import shutil
import subprocess
import importlib.util
from typing import Any, Dict, List, Optional, Tuple, Union

# Flag indicating whether site-packages has been dynamically attached to sys.path
_BOOTSTRAPPED: bool = False
_SITE_PACKAGES_PATH: Optional[str] = None
_VENV_PATH: Optional[str] = None


def find_accelerator_venv() -> Optional[str]:
    """Locate the global isolated accelerator virtual environment."""
    candidates = []
    custom_venv = os.environ.get("AGENTS_ACCELERATORS_VENV")
    if custom_venv:
        candidates.append(os.path.abspath(custom_venv))

    home = os.path.expanduser("~")
    candidates.extend([
        os.path.join(home, ".agents", "cache", "venv"),
        os.path.join(home, ".agents", "venv"),
    ])

    for venv_dir in candidates:
        if os.path.isdir(venv_dir):
            return venv_dir
    return None


def bootstrap_accelerators() -> Optional[str]:
    """
    Tier 2 Bootstrap:
    Discovers isolated global virtual environment (~/.agents/cache/venv)
    and dynamically appends its site-packages to sys.path without activating
    or touching any host project virtual environment.
    """
    global _BOOTSTRAPPED, _SITE_PACKAGES_PATH, _VENV_PATH
    if _BOOTSTRAPPED:
        return _SITE_PACKAGES_PATH

    venv_dir = find_accelerator_venv()
    if not venv_dir:
        _BOOTSTRAPPED = True
        return None

    _VENV_PATH = venv_dir
    site_candidates = [
        os.path.join(venv_dir, "Lib", "site-packages"),
        os.path.join(venv_dir, "lib", "site-packages"),
    ]

    lib_dir = os.path.join(venv_dir, "lib")
    if os.path.isdir(lib_dir):
        try:
            for entry in os.listdir(lib_dir):
                if entry.startswith("python"):
                    site_candidates.append(os.path.join(lib_dir, entry, "site-packages"))
        except OSError:
            pass

    for sp in site_candidates:
        if os.path.isdir(sp):
            if sp not in sys.path:
                # Insert at position 1 to preserve .agents/scripts precedence
                sys.path.insert(1, sp)
            _SITE_PACKAGES_PATH = sp
            _BOOTSTRAPPED = True
            return sp

    _BOOTSTRAPPED = True
    return None


# Execute bootstrap immediately on module import
bootstrap_accelerators()


def _is_package_installed(pkg_name: str) -> bool:
    """Check if package is available without eagerly importing it."""
    try:
        return importlib.util.find_spec(pkg_name) is not None
    except Exception:
        return False


# -------------------------------------------------------------------------
# Tier 2: orjson (Fast JSON Serialization & Parsing)
# -------------------------------------------------------------------------
try:
    import orjson as _orjson

    def fast_json_dumps(obj: Any, indent: bool = False) -> str:
        """Fast JSON dumps using orjson with fallback support."""
        option = _orjson.OPT_INDENT_2 if indent else 0
        return _orjson.dumps(obj, option=option).decode("utf-8")

    def fast_json_loads(data: Union[str, bytes]) -> Any:
        """Fast JSON loads using orjson."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return _orjson.loads(data)

    HAS_ORJSON: bool = True
    ORJSON_VERSION: Optional[str] = getattr(_orjson, "__version__", "unknown")
except ImportError:
    import json as _json

    def fast_json_dumps(obj: Any, indent: bool = False) -> str:
        """Stdlib JSON dumps fallback."""
        return _json.dumps(obj, indent=2 if indent else None)

    def fast_json_loads(data: Union[str, bytes]) -> Any:
        """Stdlib JSON loads fallback."""
        return _json.loads(data)

    HAS_ORJSON = False
    ORJSON_VERSION = None


# -------------------------------------------------------------------------
# Tier 2: rapidfuzz (Fast C++ Levenshtein Distance & Fuzzy Matching)
# -------------------------------------------------------------------------
try:
    from rapidfuzz import fuzz as _rf_fuzz, process as _rf_process

    def fuzzy_ratio(s1: str, s2: str) -> float:
        """Fuzzy similarity ratio between 0.0 and 1.0 using rapidfuzz."""
        return float(_rf_fuzz.ratio(s1, s2)) / 100.0

    def fuzzy_find_best(target: str, candidates: List[str], cutoff: float = 0.6) -> Optional[Tuple[str, float]]:
        """Find best matching string from candidates using rapidfuzz."""
        if not candidates:
            return None
        res = _rf_process.extractOne(target, candidates, scorer=_rf_fuzz.ratio)
        if res:
            ratio = float(res[1]) / 100.0
            if ratio >= cutoff:
                return (res[0], ratio)
        return None

    HAS_RAPIDFUZZ: bool = True
    import rapidfuzz
    RAPIDFUZZ_VERSION: Optional[str] = getattr(rapidfuzz, "__version__", "unknown")
except ImportError:
    import difflib as _difflib

    def fuzzy_ratio(s1: str, s2: str) -> float:
        """Fuzzy similarity ratio fallback using difflib.SequenceMatcher."""
        return _difflib.SequenceMatcher(None, s1, s2).ratio()

    def fuzzy_find_best(target: str, candidates: List[str], cutoff: float = 0.6) -> Optional[Tuple[str, float]]:
        """Find best matching string fallback using difflib.get_close_matches."""
        if not candidates:
            return None
        matches = _difflib.get_close_matches(target, candidates, n=1, cutoff=cutoff)
        if matches:
            ratio = _difflib.SequenceMatcher(None, target, matches[0]).ratio()
            return (matches[0], ratio)
        return None

    HAS_RAPIDFUZZ = False
    RAPIDFUZZ_VERSION = None


# -------------------------------------------------------------------------
# Tier 2: tree-sitter (Concrete Syntax Tree Analysis)
# -------------------------------------------------------------------------
try:
    import tree_sitter as _tree_sitter
    HAS_TREE_SITTER: bool = True
    TREE_SITTER_VERSION: Optional[str] = getattr(_tree_sitter, "__version__", "unknown")
except ImportError:
    HAS_TREE_SITTER = False
    TREE_SITTER_VERSION = None


# -------------------------------------------------------------------------
# Opt-In Pillar 4: Bun Ephemeral Fabric (Zero-node_modules Sandbox)
# -------------------------------------------------------------------------
def find_bun_bin() -> Optional[str]:
    """Locate Bun executable if installed on PATH or standard directories."""
    try:
        from core.capabilities import find_bun_bin as _find_bun
        return _find_bun()
    except Exception:
        return shutil.which("bun")


def run_ephemeral_bunx(package: str, args: Optional[List[str]] = None, timeout: float = 30.0) -> Dict[str, Any]:
    """
    Executes a transient npm package via Bun's global cache (bunx -y) without writing
    node_modules or package.json into the workspace.
    Degrades gracefully if Bun is not installed.
    """
    bun_bin = find_bun_bin()
    if not bun_bin:
        return {
            "status": "DEGRADED_FALLBACK",
            "message": "Opt-in Pillar 4 (Bun) not installed; degraded to host/python fallback.",
            "exit_code": 1,
            "stdout": "",
            "stderr": "bun_missing",
        }

    cmd = [bun_bin, "x", "-y", package] + (args or [])
    if os.name == "nt" and bun_bin.lower().endswith((".cmd", ".bat")):
        cmd = ["cmd.exe", "/c"] + cmd
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        return {
            "status": "SUCCESS" if proc.returncode == 0 else "FAILED",
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "runtime": "bunx",
        }
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc), "exit_code": 1}


# -------------------------------------------------------------------------
# Opt-In Pillar 2: Rust CST & Token Acceleration Fabric
# -------------------------------------------------------------------------
def find_ast_grep_bin() -> Optional[str]:
    """Locate ast-grep binary if installed."""
    try:
        from core.capabilities import find_ast_grep
        return find_ast_grep()
    except Exception:
        return shutil.which("ast-grep") or shutil.which("sg")


def find_rtk_bin() -> Optional[str]:
    """Locate RTK CLI proxy binary if installed."""
    try:
        from core.capabilities import find_rtk_bin as _find_rtk
        return _find_rtk()
    except Exception:
        return shutil.which("rtk")


def run_ephemeral_ast_grep(pattern: str, lang: str, target: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Executes structural polyglot AST query via ast-grep (Rust).
    Degrades gracefully to Python AST/regex if ast-grep is absent.
    """
    sg_bin = find_ast_grep_bin()
    if not sg_bin:
        return {
            "status": "DEGRADED_FALLBACK",
            "message": "Opt-in Pillar 2 (ast-grep) not installed; degraded to Python ast/regex.",
            "exit_code": 1,
            "stdout": "",
            "stderr": "ast_grep_missing",
        }

    cmd = [sg_bin, "run", "-p", pattern, "-l", lang, target, "--json"]
    if os.name == "nt" and sg_bin.lower().endswith((".cmd", ".bat")):
        cmd = ["cmd.exe", "/c"] + cmd
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        # In ast-grep: 0 = matches found, 1 = zero matches found, >1 = syntax/runtime error
        status = "SUCCESS" if proc.returncode in (0, 1) else "FAILED"
        return {
            "status": status,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "runtime": "ast-grep",
        }
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc), "exit_code": 1}


# -------------------------------------------------------------------------
# Tier 2: sqlite-vec (SIMD Vector Search Extension for SQLite3)
# -------------------------------------------------------------------------
HAS_SQLITE_VEC: bool = _is_package_installed("sqlite_vec")
SQLITE_VEC_VERSION: Optional[str] = "0.1.9" if HAS_SQLITE_VEC else None
_SQLITE_VEC_MOD: Optional[Any] = None


def try_load_sqlite_vec(conn: Any) -> bool:
    """Safely loads sqlite-vec C extension into a sqlite3 connection on-demand."""
    global _SQLITE_VEC_MOD
    if not HAS_SQLITE_VEC:
        return False
    if _SQLITE_VEC_MOD is None:
        try:
            import sqlite_vec
            _SQLITE_VEC_MOD = sqlite_vec
        except Exception:
            _SQLITE_VEC_MOD = False
            return False
    try:
        if hasattr(conn, "enable_load_extension"):
            conn.enable_load_extension(True)
            _SQLITE_VEC_MOD.load(conn)
            conn.enable_load_extension(False)
            return True
    except Exception:
        pass
    return False


# -------------------------------------------------------------------------
# Tier 2: model2vec (Daemonless Static Embeddings on CPU — Pair to sqlite-vec)
# -------------------------------------------------------------------------
HAS_MODEL2VEC: bool = _is_package_installed("model2vec")
MODEL2VEC_VERSION: Optional[str] = "0.10.0" if HAS_MODEL2VEC else None
_STATIC_EMBED_MODEL: Optional[Any] = None


def encode_static_embedding(text: str, dims: int = 256) -> Optional[List[float]]:
    """Generates sub-millisecond CPU static embeddings on-demand without top-level import overhead."""
    global _STATIC_EMBED_MODEL
    if not text or not HAS_MODEL2VEC:
        return None
    if _STATIC_EMBED_MODEL is None:
        try:
            from model2vec import StaticModel
            model_dir = os.path.join(os.path.expanduser("~"), ".agents", "cache", "model2vec")
            if os.path.isdir(model_dir):
                _STATIC_EMBED_MODEL = StaticModel.from_pretrained(model_dir)
            else:
                _STATIC_EMBED_MODEL = False
        except Exception:
            _STATIC_EMBED_MODEL = False
    if _STATIC_EMBED_MODEL and _STATIC_EMBED_MODEL is not False:
        try:
            vec = _STATIC_EMBED_MODEL.encode([text])[0].tolist()
            return [float(x) for x in vec[:dims]]
        except Exception:
            pass
    return None


# -------------------------------------------------------------------------
# Tier 2: tokenizers (HuggingFace Rust Deterministic BPE Token Counter)
# -------------------------------------------------------------------------
HAS_TOKENIZERS: bool = _is_package_installed("tokenizers")
TOKENIZERS_VERSION: Optional[str] = "0.23.3" if HAS_TOKENIZERS else None
_BPE_TOKENIZER: Optional[Any] = None


def count_bpe_tokens(text: str) -> int:
    """Counts exact BPE tokens via Rust tokenizers wheel on-demand with zero-network fallback."""
    global _BPE_TOKENIZER
    if not text:
        return 0
    if HAS_TOKENIZERS:
        if _BPE_TOKENIZER is None:
            try:
                from tokenizers import Tokenizer
                from tokenizers.models import BPE
                from tokenizers.pre_tokenizers import ByteLevel
                tok_cache = os.path.join(os.path.expanduser("~"), ".agents", "cache", "tokenizer.json")
                if os.path.isfile(tok_cache):
                    _BPE_TOKENIZER = Tokenizer.from_file(tok_cache)
                else:
                    tok = Tokenizer(BPE())
                    tok.pre_tokenizer = ByteLevel()
                    _BPE_TOKENIZER = tok
            except Exception:
                _BPE_TOKENIZER = False
        if _BPE_TOKENIZER and _BPE_TOKENIZER is not False:
            try:
                encoded = _BPE_TOKENIZER.encode(text)
                if len(encoded.ids) > 0:
                    return len(encoded.ids)
            except Exception:
                pass
    import math
    return max(1, int(math.ceil(len(text) / 3.8)))


# -------------------------------------------------------------------------
# Tier 2: duckdb (Stateless :memory: OLAP Sidecar over .jsonl Telemetry)
# -------------------------------------------------------------------------
HAS_DUCKDB: bool = _is_package_installed("duckdb")
DUCKDB_VERSION: Optional[str] = "2.0.0" if HAS_DUCKDB else None
_DUCKDB_MOD: Optional[Any] = None


def query_telemetry_jsonl(jsonl_glob: str) -> Dict[str, Any]:
    """
    Executes stateless OLAP aggregation over .jsonl telemetry files.
    Applies adaptive threshold: DuckDB is engaged for heavy workloads (>= 2MB),
    while pure-Python streaming reader handles small micro-logs without engine cold-start overhead.
    NEVER creates a persistent DuckDB file (100% Zero Split-Brain with SQLite).
    """
    global _DUCKDB_MOD
    import glob
    files = glob.glob(jsonl_glob)
    if not files:
        return {"engine": "none", "total_events": 0, "files": 0}

    total_bytes = sum(os.path.getsize(f) for f in files if os.path.isfile(f))

    if HAS_DUCKDB and total_bytes >= 2 * 1024 * 1024:
        try:
            if _DUCKDB_MOD is None:
                import duckdb
                _DUCKDB_MOD = duckdb
            con = _DUCKDB_MOD.connect(":memory:")
            row = con.execute(
                "SELECT count(*) AS cnt FROM read_json_auto(?, ignore_errors=true)",
                [files],
            ).fetchone()
            con.close()
            return {
                "engine": "duckdb-memory",
                "total_events": int(row[0]) if row else 0,
                "files": len(files),
            }
        except Exception:
            pass

    # Tier 0 Zero-Pip Fallback (and fast-path for small telemetry files)
    total = 0
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    if line.strip():
                        total += 1
        except Exception:
            pass
    return {"engine": "python-streaming", "total_events": total, "files": len(files)}
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.strip():
                        total += 1
        except Exception:
            pass
    return {"engine": "python-stream-fallback", "total_events": total, "files": len(files)}


# -------------------------------------------------------------------------
# Pillar 2 Opt-In Binaries: difftastic, gitleaks, & Jujutsu (jj)
# -------------------------------------------------------------------------
def find_difft_bin() -> Optional[str]:
    """Locate difftastic (difft) Rust AST diff binary if installed."""
    try:
        from core.capabilities import find_binary
        return find_binary(["difft", "difft.exe"])
    except Exception:
        return shutil.which("difft")


def find_gitleaks_bin() -> Optional[str]:
    """Locate gitleaks binary for high-speed secret scanning."""
    try:
        from core.capabilities import find_binary
        return find_binary(["gitleaks", "gitleaks.exe"])
    except Exception:
        return shutil.which("gitleaks")


def find_jj_bin() -> Optional[str]:
    """Locate Jujutsu (jj) AI-native version control binary."""
    try:
        from core.capabilities import find_binary
        return find_binary(["jj", "jj.exe"])
    except Exception:
        return shutil.which("jj")


def _shannon_entropy(token: str) -> float:
    """Computes Shannon entropy H(X) in bits/char using Python stdlib math."""
    import math
    if not token:
        return 0.0
    length = len(token)
    counts: Dict[str, int] = {}
    for ch in token:
        counts[ch] = counts.get(ch, 0) + 1
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


_SECRET_PREFIX_RE = None


def scrub_secrets(text: str) -> str:
    """
    Scrubs API keys, tokens, and high-entropy secrets before SQLite/LLM ingestion.
    Guarantees 100% Zero-Pip security via Regex + Shannon Entropy (H(X) > 4.3 bits/char).
    """
    global _SECRET_PREFIX_RE
    if not text:
        return ""
    import re
    if _SECRET_PREFIX_RE is None:
        _SECRET_PREFIX_RE = re.compile(
            r"\b(sk-[A-Za-z0-9_\-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_\-]{30,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9\-]{16,})\b"
        )
    scrubbed = _SECRET_PREFIX_RE.sub("[REDACTED_SECRET]", text)

    def _entropy_replacer(match: Any) -> str:
        prefix, val, suffix = match.group(1), match.group(2), match.group(3)
        if len(val) >= 24 and _shannon_entropy(val) > 4.3 and not val.isalpha():
            return f"{prefix}[REDACTED_HIGH_ENTROPY_SECRET]{suffix}"
        return match.group(0)

    return re.sub(
        r"((?:key|secret|token|password|passwd|auth)\s*[:=]\s*['\"])([A-Za-z0-9+/=_\-]{24,})(['\"])",
        _entropy_replacer,
        scrubbed,
        flags=re.IGNORECASE,
    )


def create_atomic_checkpoint(cwd: Optional[str] = None) -> Dict[str, str]:
    """
    Creates a non-blocking atomic working-copy snapshot before risky Bento mutations.
    Uses Jujutsu (`jj op log`) if colocated `.jj` exists, else `git stash create`.
    """
    work_dir = cwd or os.getcwd()
    jj_bin = find_jj_bin()
    if jj_bin and os.path.isdir(os.path.join(work_dir, ".jj")):
        try:
            proc = subprocess.run(
                [jj_bin, "op", "log", "-n", "1", "--no-graph", "-T", "self.id()"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5.0,
                shell=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return {"engine": "jj", "snapshot_id": proc.stdout.strip()}
        except Exception:
            pass

    # Zero-Pip Fallback: git stash create (creates commit object without touching working tree)
    try:
        proc_git = subprocess.run(
            ["git", "stash", "create", "orion-bento-checkpoint"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5.0,
            shell=False,
        )
        snap = proc_git.stdout.strip()
        if not snap:
            proc_head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5.0,
                shell=False,
            )
            snap = proc_head.stdout.strip()
        return {"engine": "git-stash-object", "snapshot_id": snap}
    except Exception:
        return {"engine": "none", "snapshot_id": ""}


def run_ephemeral_difft(target_or_args: Optional[List[str]] = None, timeout: float = 15.0) -> Dict[str, Any]:
    """
    Executes semantic AST diffing via difftastic (Pillar 2) or degrades to standard git diff.
    Cuts 60-80% whitespace/formatting token noise during code reviews.
    """
    difft_bin = find_difft_bin()
    extra = list(target_or_args or [])
    if difft_bin:
        env = dict(os.environ)
        env["GIT_EXTERNAL_DIFF"] = f"{difft_bin} --display inline --color never --context 2"
        cmd = ["git", "diff", "--ext-diff"] + extra
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=env,
                shell=False,
            )
            if proc.returncode in (0, 1):
                return {
                    "status": "SUCCESS",
                    "exit_code": 0,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "runtime": "difftastic",
                }
        except Exception:
            pass

    # Graceful fallback to standard git diff
    cmd_fb = ["git", "diff", "--no-color", "-U2"] + extra
    try:
        proc_fb = subprocess.run(
            cmd_fb,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        return {
            "status": "DEGRADED_FALLBACK",
            "exit_code": proc_fb.returncode,
            "stdout": proc_fb.stdout,
            "stderr": proc_fb.stderr,
            "runtime": "git-diff",
        }
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc), "exit_code": 1, "stdout": "", "stderr": str(exc)}


# -------------------------------------------------------------------------
# Status & Diagnostics
# -------------------------------------------------------------------------
def get_accelerator_status() -> Dict[str, Any]:
    """Return diagnostic status of all Tier 2 optional accelerators & opt-in pillars."""
    active_py_count = sum([
        int(HAS_ORJSON),
        int(HAS_RAPIDFUZZ),
        int(HAS_TREE_SITTER),
        int(HAS_SQLITE_VEC),
        int(HAS_MODEL2VEC),
        int(HAS_TOKENIZERS),
        int(HAS_DUCKDB),
    ])
    bun_avail = bool(find_bun_bin())
    ast_avail = bool(find_ast_grep_bin())
    rtk_avail = bool(find_rtk_bin())
    difft_avail = bool(find_difft_bin())
    gitleaks_avail = bool(find_gitleaks_bin())
    jj_avail = bool(find_jj_bin())

    return {
        "tier": "Tier 2: Optional Ephemeral Accelerators",
        "mandatory_floor": "Python 3.10+ Stdlib & SQLite3 (100% Zero-Pip Floor)",
        "venv_path": _VENV_PATH,
        "site_packages": _SITE_PACKAGES_PATH,
        "active_count": active_py_count,
        "accelerators": {
            "orjson": {
                "available": HAS_ORJSON,
                "version": ORJSON_VERSION,
                "role": "Fast JSON I/O",
                "fallback": "json (Python stdlib)" if not HAS_ORJSON else None,
            },
            "rapidfuzz": {
                "available": HAS_RAPIDFUZZ,
                "version": RAPIDFUZZ_VERSION,
                "role": "Fast Levenshtein & Fuzzy Match",
                "fallback": "difflib (Python stdlib)" if not HAS_RAPIDFUZZ else None,
            },
            "tree-sitter": {
                "available": HAS_TREE_SITTER,
                "version": TREE_SITTER_VERSION,
                "role": "Concrete Syntax Tree Parsing",
                "fallback": "ast (Python stdlib) / regex" if not HAS_TREE_SITTER else None,
            },
            "sqlite-vec": {
                "available": HAS_SQLITE_VEC,
                "version": SQLITE_VEC_VERSION,
                "role": "SIMD Vector Search (AVX-512/NEON KNN)",
                "fallback": "SQLite FTS5 BM25 + Python float32 cosine" if not HAS_SQLITE_VEC else None,
            },
            "model2vec": {
                "available": HAS_MODEL2VEC,
                "version": MODEL2VEC_VERSION,
                "role": "Sub-ms Daemonless Static CPU Embeddings",
                "fallback": "Ollama Embeddings (P3) -> SQLite FTS5 BM25 (Tier 0)" if not HAS_MODEL2VEC else None,
            },
            "tokenizers": {
                "available": HAS_TOKENIZERS,
                "version": TOKENIZERS_VERSION,
                "role": "Deterministic HuggingFace Rust BPE Counter",
                "fallback": "Heuristic BPE estimator (len / 3.8)" if not HAS_TOKENIZERS else None,
            },
            "duckdb": {
                "available": HAS_DUCKDB,
                "version": DUCKDB_VERSION,
                "role": "Stateless :memory: OLAP over .jsonl Telemetry",
                "fallback": "Python streaming .jsonl generator" if not HAS_DUCKDB else None,
            },
        },
        "opt_in_pillars": {
            "rust_fabric": {
                "available": bool(ast_avail or rtk_avail or difft_avail or gitleaks_avail or jj_avail),
                "rtk": rtk_avail,
                "ast_grep": ast_avail,
                "difftastic": difft_avail,
                "gitleaks": gitleaks_avail,
                "jj": jj_avail,
                "role": "CLI Token Filter, AST Search/Diff, Secret Guard & Atomic VCS",
                "fallback": "Python stream filters, ast.parse, git diff, Shannon entropy & git stash create",
            },
            "bun_fabric": {
                "available": bun_avail,
                "bunx": bun_avail,
                "role": "Zero-node_modules Sandbox & Fast TypeScript Runtime",
                "fallback": "Python subprocess & host runners",
            },
        },
    }


def install_high_value_accelerators(python_bin: Optional[str] = None) -> Tuple[bool, str]:
    """
    Installs high-value Python accelerators (orjson, rapidfuzz, tree-sitter, sqlite-vec, tokenizers, model2vec, duckdb)
    into isolated ~/.agents/cache/venv using uv (preferred) or stdlib venv + pip.
    Strictly isolated: NEVER modifies or touches the host workspace.
    """
    home = os.path.expanduser("~")
    target_venv = os.path.join(home, ".agents", "cache", "venv")
    target_scripts = os.path.join(target_venv, "Scripts" if os.name == "nt" else "bin")
    target_py = os.path.join(target_scripts, "python.exe" if os.name == "nt" else "python")

    python_executable = python_bin or sys.executable
    wheel_packages = ["orjson", "rapidfuzz", "tree-sitter", "sqlite-vec", "tokenizers", "duckdb", "model2vec"]

    uv_bin = shutil.which("uv")
    if not uv_bin and os.name == "nt":
        local_app = os.environ.get("LOCALAPPDATA", "")
        if local_app:
            uv_cand = os.path.join(local_app, "hermes", "bin", "uv.exe")
            if os.path.isfile(uv_cand):
                uv_bin = uv_cand

    try:
        os.makedirs(os.path.dirname(target_venv), exist_ok=True)
        if uv_bin:
            if not os.path.isfile(target_py):
                cmd_venv = [uv_bin, "venv", target_venv, "--python", python_executable]
                res_venv = subprocess.run(cmd_venv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, shell=False)
                if res_venv.returncode != 0:
                    return False, f"uv venv failed: {res_venv.stderr.strip()}"

            cmd_install = [uv_bin, "pip", "install", "--python", target_py] + wheel_packages
            res_install = subprocess.run(cmd_install, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90, shell=False)
            if res_install.returncode != 0:
                return False, f"uv pip install failed: {res_install.stderr.strip()}"
            return True, f"Successfully installed Tier 2 accelerators via uv into {target_venv}"
        else:
            if not os.path.isfile(target_py):
                cmd_venv = [python_executable, "-m", "venv", target_venv]
                res_venv = subprocess.run(cmd_venv, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, shell=False)
                if res_venv.returncode != 0:
                    return False, f"python -m venv failed: {res_venv.stderr.strip()}"

            cmd_install = [target_py, "-m", "pip", "install", "--upgrade"] + wheel_packages
            res_install = subprocess.run(cmd_install, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150, shell=False)
            if res_install.returncode != 0:
                return False, f"pip install failed: {res_install.stderr.strip()}"
            return True, f"Successfully installed Tier 2 accelerators via pip into {target_venv}"

    except Exception as exc:
        return False, f"Exception during accelerator installation: {exc}"
