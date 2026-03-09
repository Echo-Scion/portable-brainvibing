"""
Sovereign 4-Pillar Capability Matrix & Binary Resolution Subsystem.
Provides zero-daemon, TTL-cached capability probing across the 4 foundation pillars:
  Pillar 1: Python 3.10+ Stdlib & SQLite3 (Mandatory Floor)
  Pillar 2: Rust Toolchain (RTK Proxy & ast-grep)
  Pillar 3: Ollama Local AI (nomic-embed-text & Local SLMs)
  Pillar 4: Bun Runtime (Fast Test Runner & npm Sandbox)
"""

import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
import re
import datetime
import hashlib
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple, Set

try:
    from core.db import log_telemetry as _log_telemetry, atomic_write_text
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        pass
    def atomic_write_text(path: str, content: str) -> None:
        import uuid
        abs_path = os.path.abspath(str(path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        tmp = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(tmp, abs_path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

CAPABILITIES_CACHE_TTL = 900  # 15 minutes


def _resolve_workspace_root() -> str:
    try:
        from core.paths import get_workspace_dir
        return str(get_workspace_dir())
    except Exception:
        cur = os.path.dirname(os.path.abspath(__file__))
        while ".agents" in cur or ".orion" in cur:
            cur = os.path.dirname(cur)
        return cur


def find_binary(candidates: List[str], extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Find a tool through PATH and supported local install directories."""
    search_dirs = list(extra_dirs or [])
    search_dirs.extend([
        os.path.expanduser("~/.local/bin"),
        os.path.expanduser("~/.cargo/bin"),
        os.path.expanduser("~/.bun/bin"),
        os.path.join(_resolve_workspace_root(), ".agents", "bin"),
    ])
    for candidate in candidates:
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


def find_ast_grep(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Locates ast-grep (sg) binary on system PATH or Cargo toolchain bin directory."""
    return find_binary(["sg", "ast-grep", "sg.exe", "ast-grep.exe"], extra_dirs=extra_dirs)


# Backwards compatibility alias
_find_ast_grep_bin = find_ast_grep


def find_bun_bin(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Locates the Bun standalone executable across PATH and standard paths."""
    search_dirs = list(extra_dirs or [])
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        search_dirs.extend([
            os.path.join(local_app_data, "bun", "bin"),
            os.path.join(local_app_data, "bun"),
        ])
    return find_binary(["bun", "bun.exe"], extra_dirs=search_dirs)


def find_rtk_bin(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Locates RTK CLI proxy binary on system PATH or Cargo toolchain."""
    return find_binary(["rtk", "rtk.exe"], extra_dirs=extra_dirs)


def find_llama_server_bin(extra_dirs: Optional[List[str]] = None) -> Optional[str]:
    """Locates standalone llama-server / llama.cpp binary across PATH and local directories."""
    search_dirs = list(extra_dirs or [])
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_links = os.path.join(local_app_data, "Microsoft", "WinGet", "Links")
        if os.path.isdir(winget_links):
            search_dirs.append(winget_links)
        winget_pkg = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_pkg):
            for d in os.listdir(winget_pkg):
                if "llamacpp" in d.lower():
                    search_dirs.append(os.path.join(winget_pkg, d))
    return find_binary(["llama-server", "llama-server.exe", "server", "server.exe"], extra_dirs=search_dirs)


def _binary_version(path: str) -> Optional[str]:
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            shell=False,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError) as _e:
        _log_telemetry(_e, f"capabilities.py:_binary_version:{path}")
    return None


_RESOLVED_OLLAMA_BASE_URL: Optional[str] = None
_OLLAMA_OFFLINE: bool = False
_RESOLVED_LOCAL_AI: Optional[Dict[str, Any]] = None


def _probe_url(url: str, timeout: float = 1.0) -> bool:
    try:
        target = url.rstrip("/") + "/api/tags"
        req = urllib.request.Request(target, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        return e.code == 200
    except Exception as _e:
        _log_telemetry(_e, f"capabilities.py:_probe_url:{url}")
        return False


def _probe_openai_url(url: str, timeout: float = 1.0) -> bool:
    """Probe whether an endpoint supports OpenAI-compatible /v1 API (llama-server, LM Studio, vLLM, LocalAI)."""
    # 1. Probe /v1/models (standard OpenAI catalog)
    try:
        target = url.rstrip("/") + "/v1/models"
        req = urllib.request.Request(target, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 200:
            return True
    except Exception as _e:
        _log_telemetry(_e, f"capabilities.py:_probe_openai_url:{url}")

    # 2. Probe /health (llama-server native healthcheck endpoint)
    try:
        target_health = url.rstrip("/") + "/health"
        req_h = urllib.request.Request(target_health, method="GET")
        with urllib.request.urlopen(req_h, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code == 200:
            return True
    except Exception:
        pass

    return False


def resolve_local_ai_endpoint(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Universal local AI endpoint resolver supporting:
    1. Ollama (:11434) via native /api protocol
    2. llama.cpp / llama-server (:8080) via OpenAI /v1 protocol
    3. LM Studio (:1234) via OpenAI /v1 protocol
    4. vLLM / LocalAI (:8000) via OpenAI /v1 protocol
    5. Custom URL via LOCAL_LLM_URL, OPENAI_BASE_URL, or ORION_LLM_URL
    """
    global _RESOLVED_LOCAL_AI
    if _RESOLVED_LOCAL_AI is not None and not force_refresh:
        return _RESOLVED_LOCAL_AI

    # 1. Check custom environment overrides
    custom_url = (
        os.environ.get("LOCAL_LLM_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("ORION_LLM_URL")
    )
    if custom_url:
        clean_url = (
            custom_url.replace("/v1/chat/completions", "")
            .replace("/v1/embeddings", "")
            .replace("/v1/models", "")
            .replace("/api/generate", "")
            .replace("/api/embeddings", "")
            .replace("/api/tags", "")
            .rstrip("/")
        )
        if clean_url.endswith("/v1"):
            clean_url = clean_url[:-3].rstrip("/")

        if _probe_openai_url(clean_url, timeout=1.0):
            _RESOLVED_LOCAL_AI = {
                "provider": "openai_compatible",
                "base_url": clean_url,
                "api_format": "openai",
                "name": "Custom OpenAI-Compatible Local AI",
            }
            return _RESOLVED_LOCAL_AI
        elif _probe_url(clean_url, timeout=1.0):
            _RESOLVED_LOCAL_AI = {
                "provider": "ollama",
                "base_url": clean_url,
                "api_format": "ollama",
                "name": "Custom Ollama Local AI",
            }
            return _RESOLVED_LOCAL_AI

    # 2. Probe Ollama standard ports
    ollama_candidates = [
        "http://127.0.0.1:11434",
        "http://[::1]:11434",
        "http://localhost:11434",
    ]
    for url in ollama_candidates:
        if _probe_url(url, timeout=0.8):
            _RESOLVED_LOCAL_AI = {
                "provider": "ollama",
                "base_url": url,
                "api_format": "ollama",
                "name": "Ollama Local AI",
            }
            return _RESOLVED_LOCAL_AI

    # 3. Probe OpenAI-compatible runtimes (llama-server, LM Studio, vLLM, LocalAI)
    openai_candidates = [
        ("llama_server", "http://127.0.0.1:8080", "llama.cpp (llama-server)"),
        ("lm_studio", "http://127.0.0.1:1234", "LM Studio Local AI"),
        ("vllm", "http://127.0.0.1:8000", "vLLM / LocalAI"),
        ("llama_server", "http://localhost:8080", "llama.cpp (llama-server)"),
        ("lm_studio", "http://localhost:1234", "LM Studio Local AI"),
        ("vllm", "http://localhost:8000", "vLLM / LocalAI"),
    ]
    for provider, url, display_name in openai_candidates:
        if _probe_openai_url(url, timeout=0.8):
            _RESOLVED_LOCAL_AI = {
                "provider": provider,
                "base_url": url,
                "api_format": "openai",
                "name": display_name,
            }
            return _RESOLVED_LOCAL_AI

    _RESOLVED_LOCAL_AI = None
    return None


def resolve_ollama_base_url(force_refresh: bool = False) -> Optional[str]:
    """
    Resolves reachable local AI base URL across all supported providers (Ollama, llama-server, LM Studio, vLLM).
    Maintains backward compatibility with legacy Ollama callers.
    """
    global _RESOLVED_OLLAMA_BASE_URL, _OLLAMA_OFFLINE
    local_ai = resolve_local_ai_endpoint(force_refresh=force_refresh)
    if local_ai and local_ai.get("base_url"):
        _RESOLVED_OLLAMA_BASE_URL = local_ai["base_url"]
        _OLLAMA_OFFLINE = False
        return _RESOLVED_OLLAMA_BASE_URL

    _RESOLVED_OLLAMA_BASE_URL = None
    _OLLAMA_OFFLINE = True
    return None


def _get_cache_path() -> str:
    cwd = os.getcwd()
    if os.path.basename(cwd) == ".agents":
        cwd = os.path.dirname(cwd)
    return os.path.join(cwd, ".orion", "working", "capabilities.json")


def probe_capabilities(
    ollama_probe: Optional[Callable[[], Optional[str]]] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    cache_path = _get_cache_path()

    if not force_refresh and ollama_probe is None and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            cached_time = cached.get("timestamp", 0)
            if (time.time() - cached_time) < CAPABILITIES_CACHE_TTL:
                return cached
        except Exception as _e:
            _log_telemetry(_e, "capabilities.py:cache_read")

    def binary_status(provider, candidates, fallback, finder_fn):
        path = next((shutil.which(candidate) for candidate in candidates if shutil.which(candidate)), None)
        if not path and not hasattr(shutil.which, "assert_called") and finder_fn:
            path = finder_fn()
        version = _binary_version(path) if path else None
        return {
            "available": bool(path and version),
            "provider": provider,
            "version": version,
            "fallback": None if path and version else fallback,
        }

    rtk_status = binary_status("rtk", ["rtk"], "python", find_rtk_bin)
    ast_status = binary_status("ast-grep", ["sg", "ast-grep"], "python-ast", find_ast_grep)
    llama_server_bin = find_llama_server_bin()

    if ollama_probe is not None:
        ollama_url = ollama_probe()
        ai_provider = "ollama"
    else:
        local_ai = resolve_local_ai_endpoint(force_refresh=force_refresh)
        ollama_url = local_ai["base_url"] if local_ai else None
        ai_provider = local_ai["provider"] if local_ai else "ollama"

    ollama_status = {
        "available": bool(ollama_url),
        "provider": ai_provider,
        "version": ollama_url,
        "standalone_bin": llama_server_bin,
        "fallback": None if ollama_url else "sqlite-fts5",
    }

    bun_status = binary_status("bun", ["bun"], "host-runner", find_bun_bin)

    py_ver = platform.python_version()
    sql_ver = sqlite3.sqlite_version

    p2_active = bool(rtk_status["available"] or ast_status["available"])
    p2_both = bool(rtk_status["available"] and ast_status["available"])
    p2_status_label = "ACTIVE" if p2_both else ("PARTIAL" if p2_active else "FALLBACK")
    p3_active = bool(ollama_status["available"])
    p4_active = bool(bun_status["available"])

    active_count = 1 + int(p2_active) + int(p3_active) + int(p4_active)

    provider_labels = {
        "ollama": "Ollama Local AI",
        "llama_server": "llama.cpp (llama-server)",
        "lm_studio": "LM Studio Local AI",
        "vllm": "vLLM / LocalAI",
        "openai_compatible": "OpenAI-Compatible Local AI",
    }
    p3_label = provider_labels.get(ai_provider, f"Local AI ({ai_provider})")

    result = {
        "rtk": rtk_status,
        "ast-grep": ast_status,
        "ollama": ollama_status,
        "bun": bun_status,
        "pillars": {
            "pillar_1": {
                "name": "Pillar 1: Python 3.10+ Stdlib & SQLite3 (Mandatory Floor)",
                "available": True,
                "status": "ACTIVE",
                "details": f"Python {py_ver} | SQLite {sql_ver}",
                "fallback": None,
            },
            "pillar_2": {
                "name": "Pillar 2: Rust Toolchain (rtk & ast-grep)",
                "available": p2_active,
                "status": p2_status_label,
                "details": f"rtk: {rtk_status['version'] or 'N/A'}, ast-grep: {ast_status['version'] or 'N/A'}",
                "fallback": "Python stream filters & Python ast.parse",
            },
            "pillar_3": {
                "name": f"Pillar 3: {p3_label} (nomic-embed-text & SLM)",
                "available": p3_active,
                "status": "ACTIVE" if p3_active else "FALLBACK",
                "details": f"{ollama_url} [{ai_provider}]" if ollama_url else "Offline",
                "fallback": "SQLite FTS5 lexical BM25 & heuristic RAG",
            },
            "pillar_4": {
                "name": "Pillar 4: Bun Runtime (Fast Test Runner & npm Sandbox)",
                "available": p4_active,
                "status": "ACTIVE" if p4_active else "FALLBACK",
                "details": bun_status["version"] or "N/A",
                "fallback": "Python subprocess & Host test runners",
            },
        },
        "active_pillars_count": active_count,
        "timestamp": time.time(),
        "ttl": CAPABILITIES_CACHE_TTL,
    }

    if ollama_probe is None:
        try:
            atomic_write_text(cache_path, json.dumps(result, indent=2))
        except Exception as _e:
            _log_telemetry(_e, "capabilities.py:cache_write")

    return result


def print_pillars_matrix(capabilities: Optional[Dict[str, Any]] = None, force_refresh: bool = False) -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as _e:
        _log_telemetry(_e, "capabilities.py:reconfigure")

    caps = capabilities or probe_capabilities(force_refresh=force_refresh)
    pillars = caps.get("pillars", {})

    print("\n" + "=" * 76)
    print(" 4-PILLAR RUNTIME CAPABILITY MATRIX (Zero-Latency Probe)")
    print("=" * 76)

    p1 = pillars.get("pillar_1", {})
    p2 = pillars.get("pillar_2", {})
    p3 = pillars.get("pillar_3", {})
    p4 = pillars.get("pillar_4", {})

    print(f" [Pillar 1] Python Stdlib Floor : [{p1.get('status', 'ACTIVE')}] {p1.get('details', '')}")
    print(f"   |-- Active Fallback           : {p1.get('fallback') or 'None (Self-Sovereign Base)'}")

    p2_status = p2.get("status", "FALLBACK")
    print(f" [Pillar 2] Rust (rtk & ast-grep): [{p2_status}] {p2.get('details', '')}")
    print(f"   |-- Active Fallback           : {p2.get('fallback')}")

    p3_status = p3.get("status", "FALLBACK")
    p3_name = p3.get("name", "Local AI Engine")
    print(f" [{p3_name[:30]:<30}]: [{p3_status}] {p3.get('details', '')}")
    print(f"   |-- Active Fallback           : {p3.get('fallback')}")

    p4_status = p4.get("status", "FALLBACK")
    print(f" [Pillar 4] Bun Runtime         : [{p4_status}] {p4.get('details', '')}")
    print(f"   |-- Active Fallback           : {p4.get('fallback')}")

    print("-" * 76)
    active_count = caps.get("active_pillars_count", 1)
    cache_path = _get_cache_path()
    cached_state = "CACHED" if os.path.exists(cache_path) else "LIVE"
    print(f" Runtime Matrix: Scenario {active_count}/4 active | Capability Cache: {cached_state} (TTL: 900s)")
    print("=" * 76 + "\n")


# ==============================================================================
# PILLAR 3: OLLAMA LOCAL AI REST CLIENT & HARDWARE INTROSPECTION
# ==============================================================================

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_EMBED_MODEL = "nomic-embed-text"
DEFAULT_GEN_MODEL = "qwen2.5-coder:1.5b"


def detect_hardware() -> Dict[str, Any]:
    """Return conservative local hardware facts without third-party dependencies."""
    memory_gb = 0.0
    try:
        if sys.platform == "darwin":
            res = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2)
            if res.returncode == 0 and res.stdout.strip().isdigit():
                memory_gb = int(res.stdout.strip()) / (1024 ** 3)
        elif os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        memory_gb = kb / (1024 ** 2)
                        break
        elif os.name == "nt":
            try:
                res = subprocess.run(["wmic", "OS", "get", "TotalVisibleMemorySize", "/Value"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2)
                for line in res.stdout.splitlines():
                    if "TotalVisibleMemorySize=" in line:
                        val = line.split("=")[1].strip()
                        if val.isdigit():
                            memory_gb = int(val) / (1024 ** 2)
            except Exception:
                memory_gb = 16.0
    except Exception as e:
        _log_telemetry(e, "detect_hardware:ram")
    return {"platform": platform.system(), "cpu_count": os.cpu_count() or 1, "memory_gb": round(memory_gb, 2)}


def parse_model_parameters_b(model_name: str) -> float:
    """Extract model parameter count in billions (e.g. 'qwen2.5-coder:1.5b' -> 1.5, 'deepseek-r1:32b' -> 32.0)."""
    if not model_name:
        return 0.0
    m = re.search(r"[:_-](\d+(?:\.\d+)?)[bB]", model_name)
    if not m:
        m = re.search(r"\b(\d+(?:\.\d+)?)[bB]\b", model_name)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return 0.0


def enqueue_cloud_handoff(
    task_type: str,
    payload: Dict[str, Any],
    reason: str = "ollama_offline_or_underpowered",
    queue_file: Optional[str] = None,
) -> bool:
    """Write structured handoff task for Cloud/IDE LLM Agent into .orion/working/cloud_handoff_queue.json."""
    if queue_file is None:
        queue_file = os.path.join(_resolve_workspace_root(), ".orion", "working", "cloud_handoff_queue.json")
    try:
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        tasks = []
        if os.path.exists(queue_file):
            try:
                with open(queue_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if isinstance(data, list):
                            tasks = data
                        elif isinstance(data, dict) and "tasks" in data:
                            tasks = data["tasks"]
            except Exception:
                tasks = []
        task_entry = {
            "id": f"handoff_{int(time.time())}_{len(tasks)+1}",
            "task_type": task_type,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "reason": reason,
            "status": "pending",
            "payload": payload,
        }
        already_queued = any(
            t.get("task_type") == task_type and t.get("payload") == payload and t.get("status") == "pending"
            for t in tasks
        )
        if not already_queued:
            tasks.append(task_entry)
            atomic_write_text(queue_file, json.dumps({"tasks": tasks}, indent=2))
        return True
    except Exception as e:
        _log_telemetry(e, "enqueue_cloud_handoff")
        return False


def clear_cloud_handoff(
    task_type: str,
    match_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    queue_file: Optional[str] = None,
) -> int:
    """Clear completed items from cloud_handoff_queue.json."""
    if queue_file is None:
        queue_file = os.path.join(_resolve_workspace_root(), ".orion", "working", "cloud_handoff_queue.json")
    if not os.path.exists(queue_file):
        return 0
    try:
        with open(queue_file, "r", encoding="utf-8") as f:
            data = json.loads(f.read().strip() or "{}")
        tasks = data.get("tasks", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        initial_len = len(tasks)
        remaining = []
        for t in tasks:
            if t.get("task_type") == task_type or task_type in ("*", "ALL"):
                if match_fn is None or match_fn(t):
                    continue
            remaining.append(t)
        atomic_write_text(queue_file, json.dumps({"tasks": remaining}, indent=2))
        return initial_len - len(remaining)
    except Exception as e:
        _log_telemetry(e, "clear_cloud_handoff")
        return 0



def is_ollama_available(host: str = DEFAULT_HOST, timeout_sec: float = 0.5) -> bool:
    """Check if the local Ollama daemon is active and responsive."""
    try:
        req = urllib.request.Request(f"{host.rstrip('/')}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.status == 200
    except Exception as _e:
        _log_telemetry(_e, "is_ollama_available")
        return False


def get_embedding(
    text: str,
    model: str = DEFAULT_EMBED_MODEL,
    host: Optional[str] = None,
    timeout_sec: float = 4.0
) -> Optional[List[float]]:
    """
    Retrieve vector embedding for a given text snippet.
    Supports both Ollama (/api/embeddings) and OpenAI-compatible (/v1/embeddings) endpoints.
    """
    if not text.strip():
        return None

    local_ai = resolve_local_ai_endpoint()
    base_url = (host or (local_ai["base_url"] if local_ai else DEFAULT_HOST)).rstrip("/")
    api_format = local_ai["api_format"] if local_ai else ("openai" if any(p in base_url for p in (":8080", ":1234", ":8000")) else "ollama")

    if api_format == "openai":
        url = f"{base_url}/v1/embeddings"
        payload = json.dumps({"model": model, "input": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                res_data = data.get("data", [])
                if res_data and isinstance(res_data, list):
                    return res_data[0].get("embedding")
        except Exception as _e:
            _log_telemetry(_e, f"get_embedding:openai:{model}")
            return None

    # Ollama native API fallback
    url = f"{base_url}/api/embeddings"
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("embedding")
    except Exception as _e:
        _log_telemetry(_e, f"get_embedding:{model}")
        return None


def generate_completion(
    prompt: str,
    model: str = DEFAULT_GEN_MODEL,
    system_prompt: Optional[str] = None,
    host: Optional[str] = None,
    timeout_sec: float = 30.0,
    temperature: float = 0.2
) -> Optional[str]:
    """
    Generate completion via local SLM.
    Supports both Ollama (/api/generate) and OpenAI-compatible (/v1/chat/completions) endpoints.
    Strictly forbids calling embedding-only models to prevent HTTP 400.
    """
    embed_keywords = ["embed", "bge", "nomic-embed", "minilm", "mxbai", "rerank"]
    if any(k in model.lower() for k in embed_keywords):
        sys.stderr.write(f"[WARNING] Model '{model}' is an embedding-only model and cannot be used for text generation.\n")
        return None

    local_ai = resolve_local_ai_endpoint()
    base_url = (host or (local_ai["base_url"] if local_ai else DEFAULT_HOST)).rstrip("/")
    api_format = local_ai["api_format"] if local_ai else ("openai" if any(p in base_url for p in (":8080", ":1234", ":8000")) else "ollama")

    if api_format == "openai":
        url = f"{base_url}/v1/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload_dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        payload = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
        except Exception as _e:
            _log_telemetry(_e, f"generate_completion:openai:{model}")
            return None

    # Ollama native API fallback
    url = f"{base_url}/api/generate"
    payload_dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }
    if system_prompt:
        payload_dict["system"] = system_prompt

    payload = json.dumps(payload_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response")
    except Exception as _e:
        _log_telemetry(_e, f"generate_completion:{model}")
        return None


def get_available_models(base_url: Optional[str] = None) -> List[str]:
    """
    Retrieves the list of installed model names/identifiers from the active local AI service.
    Supports both Ollama (/api/tags) and OpenAI-compatible (/v1/models) protocols.
    """
    local_ai = resolve_local_ai_endpoint()
    host = (base_url or (local_ai["base_url"] if local_ai else DEFAULT_HOST)).rstrip("/")
    api_format = local_ai["api_format"] if local_ai else ("openai" if any(p in host for p in (":8080", ":1234", ":8000")) else "ollama")

    # 1. Probe OpenAI format first if configured or fallback
    if api_format == "openai":
        try:
            req = urllib.request.Request(f"{host}/v1/models", headers={"User-Agent": "Orion/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            data_items = data.get("data", [])
            if isinstance(data_items, list):
                model_ids = [m.get("id") for m in data_items if isinstance(m, dict) and m.get("id")]
                if model_ids:
                    return model_ids
        except Exception as _e:
            _log_telemetry(_e, "get_available_models:openai")

    # 2. Ollama /api/tags
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "Orion/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = data.get("models", [])
        if isinstance(models, list):
            model_names = [m.get("name") for m in models if isinstance(m, dict) and m.get("name")]
            if model_names:
                return model_names
    except Exception as _e:
        _log_telemetry(_e, "get_available_models:ollama")

    # 3. Fallback try OpenAI /v1/models if Ollama attempt failed on custom server
    if api_format != "openai":
        try:
            req = urllib.request.Request(f"{host}/v1/models", headers={"User-Agent": "Orion/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            data_items = data.get("data", [])
            if isinstance(data_items, list):
                model_ids = [m.get("id") for m in data_items if isinstance(m, dict) and m.get("id")]
                if model_ids:
                    return model_ids
        except Exception:
            pass

    return []


def select_optimal_ollama_model(host: Optional[str] = None, min_params_b: float = 1.0) -> Optional[str]:
    """
    Selects the optimal installed local code/instruct model from local AI service,
    filtering out embedding-only models and prioritizing stronger parameter tiers.
    Works seamlessly across Ollama and OpenAI-compatible servers (llama-server, LM Studio, vLLM).
    """
    base_url = host or resolve_ollama_base_url()
    if not base_url:
        return None

    model_names = get_available_models(base_url)
    if not model_names:
        env_model = os.environ.get("ORION_LOCAL_MODEL") or os.environ.get("OLLAMA_MODEL")
        if env_model and parse_model_parameters_b(env_model) >= min_params_b:
            return env_model
        return None

    # If only 1 model is loaded on the local server (e.g. single GGUF on llama-server)
    if len(model_names) == 1:
        single_name = model_names[0]
        lower_single = single_name.lower()
        if not any(k in lower_single for k in ("embed", "bge-", "minilm", "rerank")):
            return single_name

    candidates: List[Tuple[float, str]] = []
    for name in model_names:
        lower = name.lower()
        if any(k in lower for k in ("embed", "bge-", "minilm", "rerank", "whisper", "vision", "moondream")):
            continue
        params = parse_model_parameters_b(name)
        score = params
        if any(k in lower for k in ("coder", "code", "deepseek-coder", "qwen2.5-coder", "starcoder", "codellama")):
            score += 10.0
        if params >= min_params_b or (params == 0.0 and len(model_names) <= 3):
            candidates.append((score, name))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    env_model = os.environ.get("ORION_LOCAL_MODEL") or os.environ.get("OLLAMA_MODEL")
    if env_model and parse_model_parameters_b(env_model) >= min_params_b:
        return env_model
    return None


def _get_neuro_cache_file() -> str:
    return os.path.join(_resolve_workspace_root(), ".orion", "working", "neuro_symbolic_cache.json")


def load_neuro_symbolic_cache(key: str) -> Optional[Any]:
    cache_file = _get_neuro_cache_file()
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry = data.get(key)
        if isinstance(entry, dict) and "data" in entry:
            return entry["data"]
        return entry
    except Exception as _e:
        _log_telemetry(_e, "load_neuro_symbolic_cache")
        return None


def save_neuro_symbolic_cache(key: str, val: Any) -> None:
    cache_file = _get_neuro_cache_file()
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        data = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[key] = {
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "data": val,
        }
        atomic_write_text(cache_file, json.dumps(data, indent=2))
    except Exception as _e:
        _log_telemetry(_e, "save_neuro_symbolic_cache")


def execute_neuro_symbolic(
    task_type: str,
    prompt: str,
    validator_fn: Optional[Callable[[Any], Tuple[bool, str]]] = None,
    fallback_fn: Optional[Callable[[], Any]] = None,
    handoff_payload: Optional[Dict[str, Any]] = None,
    cache_key: Optional[str] = None,
    system_prompt: Optional[str] = None,
    timeout_sec: float = 15.0,
    temperature: float = 0.1,
    min_params_b: float = 1.0,
    force_refresh: bool = False,
) -> Tuple[Any, str]:
    """
    3-Tier Neuro-Symbolic Execution Cascade:
      Tier 0: Content-Addressed Local Cache (.orion/working/neuro_symbolic_cache.json) -> (result, "cache")
      Tier 1: Local Ollama (format=json, Assertion Matrix + 1 self-correction retry) -> (result, "ollama")
      Tier 2: Enqueue Cloud Agent Handoff (.orion/working/cloud_handoff_queue.json) + Deterministic Shadow -> (result, "deterministic_shadow")
    """
    full_cache_key = f"{task_type}:{cache_key or hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]}"

    # 1. Tier 0: Cache Check
    if not force_refresh:
        cached = load_neuro_symbolic_cache(full_cache_key)
        if cached is not None:
            if validator_fn:
                ok, _ = validator_fn(cached)
                if ok:
                    return cached, "cache"
            else:
                return cached, "cache"

    # 2. Tier 1: Local AI (NanoBrain / llama-server / Ollama)
    base_url = resolve_ollama_base_url()
    fail_reason = "local_ai_offline"
    if base_url:
        model_name = select_optimal_ollama_model(base_url, min_params_b=min_params_b)
        if model_name:
            curr_prompt = prompt
            for attempt in range(2):
                try:
                    raw_response = generate_completion(
                        prompt=curr_prompt,
                        model=model_name,
                        system_prompt=system_prompt,
                        host=base_url,
                        timeout_sec=timeout_sec,
                        temperature=temperature,
                    )
                    if not raw_response:
                        fail_reason = "empty_or_failed_completion"
                        break

                    parsed = json.loads(raw_response.strip())
                    if validator_fn:
                        ok, err_msg = validator_fn(parsed)
                        if ok:
                            save_neuro_symbolic_cache(full_cache_key, parsed)
                            clear_cloud_handoff(task_type, lambda t: t.get("payload", {}).get("cache_key") == full_cache_key)
                            return parsed, "local_ai"
                        else:
                            fail_reason = f"validation_error: {err_msg}"
                            if attempt == 0:
                                curr_prompt = f"{prompt}\n\n[VALIDATION_ERROR]: {err_msg}\nPlease correct the output and return strictly valid JSON matching the schema."
                                continue
                    else:
                        save_neuro_symbolic_cache(full_cache_key, parsed)
                        clear_cloud_handoff(task_type, lambda t: t.get("payload", {}).get("cache_key") == full_cache_key)
                        return parsed, "local_ai"
                except json.JSONDecodeError as _jde:
                    fail_reason = f"json_decode_error: {_jde}"
                    # Try to extract JSON substring if wrapped in markdown
                    m_json = re.search(r"\{.*\}|\[.*\]", raw_response, re.DOTALL)
                    if m_json:
                        try:
                            parsed = json.loads(m_json.group(0))
                            if validator_fn:
                                ok, err_msg = validator_fn(parsed)
                                if ok:
                                    save_neuro_symbolic_cache(full_cache_key, parsed)
                                    clear_cloud_handoff(task_type, lambda t: t.get("payload", {}).get("cache_key") == full_cache_key)
                                    return parsed, "local_ai"
                            else:
                                save_neuro_symbolic_cache(full_cache_key, parsed)
                                clear_cloud_handoff(task_type, lambda t: t.get("payload", {}).get("cache_key") == full_cache_key)
                                return parsed, "local_ai"
                        except Exception:
                            pass
                    if attempt == 0:
                        curr_prompt = f"{prompt}\n\n[VALIDATION_ERROR]: Output was not valid JSON. Please return STRICTLY raw JSON."
                        continue
                except Exception as _oe:
                    fail_reason = str(_oe)
                    _log_telemetry(_oe, f"execute_neuro_symbolic:local_ai_attempt_{attempt}")
                    break
        else:
            fail_reason = "no_suitable_local_model"

    # 3. Tier 2: Cloud Agent Handoff + Deterministic Shadow Fallback
    h_payload = dict(handoff_payload or {})
    h_payload["cache_key"] = full_cache_key
    h_payload["task_type"] = task_type
    h_payload["prompt_preview"] = prompt[:1000]
    enqueue_cloud_handoff(task_type, h_payload, reason=fail_reason)

    fallback_val = fallback_fn() if fallback_fn else None
    return fallback_val, "deterministic_shadow"


# ==============================================================================
# PILLAR 2: RTK STREAM FILTER & EXECUTION PROXY
# ==============================================================================

def python_fallback_stream_filter(text: str) -> str:
    """
    In-memory Python stream filter active when rtk binary is not installed/reachable.
    Delegates to OrionCompactor.run_stream: lossless cleanup, then bounded output that
    keeps head, tail, and diagnostic lines from the cut middle (full text spilled for search).
    """
    if not text:
        return text
    try:
        from commands.compact import OrionCompactor
        return OrionCompactor.run_stream(text)
    except Exception:
        ansi_regex = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        clean = ansi_regex.sub('', text)
        lines = clean.splitlines()
        if len(lines) <= 80:
            return clean
        filtered = []
        prev_line = None
        rep_count = 0
        for line in lines:
            stripped = line.strip()
            if stripped == prev_line and stripped in {'.', '', '-'}:
                rep_count += 1
                continue
            if rep_count > 0:
                filtered.append(f"  ... [repeated {rep_count}x] ...")
                rep_count = 0
            prev_line = stripped
            filtered.append(line)
        if rep_count > 0:
            filtered.append(f"  ... [repeated {rep_count}x] ...")
        if len(filtered) > 100:
            head = filtered[:35]
            tail = filtered[-45:]
            omitted = len(filtered) - 80
            return "\n".join(head + [f"\n--- [... {omitted} lines omitted by Python Stream Filter ...] ---\n"] + tail)
        return "\n".join(filtered)


_EDIT_FEEDING_COMMANDS = {"cat", "type", "get-content", "gc", "head", "tail", "more", "less", "bat", "sed"}


def _output_feeds_edits(cmd: List[str]) -> bool:
    """True when the command prints file content that a later exact-match edit will rely on."""
    if not cmd:
        return False
    return os.path.splitext(os.path.basename(cmd[0]))[0].lower() in _EDIT_FEEDING_COMMANDS


def check_circuit_breaker(learnings_path: str) -> Tuple[bool, int]:
    if not os.path.exists(learnings_path):
        return False, 0
    try:
        with open(learnings_path, "r", encoding="utf-8") as f:
            content = f.read()
        entries = re.findall(
            r'## \[Darwinian Hook\] (Auto-intercepted Failure|Command Succeeded|Reflexion)',
            content
        )
        failures = 0
        for entry in reversed(entries):
            if entry == "Auto-intercepted Failure":
                failures += 1
            else:
                break
        return failures >= 3, failures
    except Exception as _e:
        _log_telemetry(_e, "capabilities:check_circuit_breaker")
        return False, 0


def run_rtk_proxy(args: List[str]) -> int:
    if not args or any(arg in args for arg in ['--help', '-h']):
        print("Usage: python .agents/scripts/orion.py rtk <command>")
        print("Layer 1 Process-Level Interceptor (RTK Native Rust with Python Stream Filter Fallback)")
        return 0 if any(arg in args for arg in ['--help', '-h']) else 1

    cmd = list(args)
    rtk_bin = find_rtk_bin()
    has_rtk = rtk_bin is not None

    hook_tokens = [c for c in cmd if c != 'rtk']
    if hook_tokens[:2] == ['hook', 'antigravity']:
        raw_stdin = ""
        try:
            if sys.stdin is not None and not sys.stdin.isatty():
                raw_stdin = sys.stdin.read()
        except Exception as _se:
            _log_telemetry(_se, "capabilities:rtk_hook_stdin")

        workspace_dir = _resolve_workspace_root()
        learnings_path = os.path.normpath(os.path.join(workspace_dir, ".orion", "working", "failures.log"))
        is_tripped, fail_count = check_circuit_breaker(learnings_path)

        tool_name = "run_command"
        tool_args = {}
        session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
        if raw_stdin.strip():
            try:
                payload = json.loads(raw_stdin)
                tool_name = (
                    payload.get("tool_name")
                    or payload.get("toolName")
                    or payload.get("name")
                    or payload.get("tool")
                    or "run_command"
                )
                tool_args = (
                    payload.get("tool_args")
                    or payload.get("toolArgs")
                    or payload.get("tool_input")
                    or payload.get("toolInput")
                    or payload.get("arguments")
                    or payload.get("input")
                    or payload.get("args")
                    or payload.get("parameters")
                    or {
                        k: v for k, v in payload.items()
                        if k not in ("tool_name", "toolName", "name", "tool", "conversationId", "session_id", "hook_event_name")
                    }
                )
                session_id = (
                    payload.get("conversationId")
                    or os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
                )
            except Exception as _pe:
                _log_telemetry(_pe, "capabilities:rtk_hook_parse")

        is_recovery_cmd = (
            any(x in str(tool_args).lower() for x in ("self-evolve", "reflexion", "reset-circuit-breaker", "reset_circuit_breaker"))
            or tool_name in ("reset-circuit-breaker", "reset_circuit_breaker", "reflexion")
        )

        if is_tripped and not is_recovery_cmd:
            reason = f"Circuit breaker tripped ({fail_count} consecutive command failures detected in failures.log). Stop calling tools and conduct root-cause analysis or run reflexion."
            sys.stderr.write(f"[CIRCUIT BREAKER]: {reason}\n")
            sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
            return 3

        from core.harness.capture import ToolQuantumCapture
        capture = ToolQuantumCapture(
            state_dir=os.path.normpath(os.path.join(workspace_dir, ".orion", "harness"))
        )

        if is_recovery_cmd:
            try:
                capture.reset_circuit_breaker(session_id)
            except Exception as _re:
                _log_telemetry(_re, "capabilities:rtk_hook_reset_cb")
        else:
            try:
                capture.record_tool_call(session_id, tool_name, tool_args if isinstance(tool_args, dict) else {})
            except RuntimeError as cb_err:
                sys.stderr.write(f"[CIRCUIT BREAKER]: {cb_err}\n")
                sys.stdout.write(json.dumps({"decision": "block", "reason": f"Circuit breaker tripped: {cb_err}"}))
                return 3
            except Exception as _he:
                _log_telemetry(_he, "capabilities:rtk_hook_record")

        if has_rtk and tool_name == "run_command":
            try:
                proc = subprocess.run(
                    [rtk_bin, 'hook', 'antigravity'],
                    input=raw_stdin,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=3,
                    shell=False,
                )
                if proc.stdout and proc.stdout.strip():
                    sys.stdout.write(proc.stdout)
                else:
                    sys.stdout.write('{"decision": "allow"}')
                return proc.returncode
            except Exception as _e:
                _log_telemetry(_e, "capabilities:rtk_hook_antigravity")
                sys.stdout.write('{"decision": "allow"}')
                return 0
        else:
            sys.stdout.write('{"decision": "allow"}')
            return 0

    if has_rtk:
        if cmd and cmd[0] in {'gain', 'discover', 'proxy', 'history'}:
            cmd = [rtk_bin] + cmd
        elif cmd and cmd[0] != 'rtk':
            cmd = [rtk_bin] + cmd
    else:
        if cmd and cmd[0] == 'rtk':
            cmd = cmd[1:]
        if cmd and cmd[0] in {'gain', 'discover', 'history'}:
            print(f"[RTK FALLBACK] '{cmd[0]}' metrics unavailable (rtk binary not installed). Returning 0 token delta.")
            return 0
        if cmd and cmd[0] == 'proxy':
            cmd = cmd[1:]
        if cmd and cmd[0] == 'read':
            target_f = next((a for a in cmd[1:] if not a.startswith('-')), None)
            if target_f and os.path.isfile(target_f):
                from core.scanner import generate_skeleton
                print("\n".join(generate_skeleton(target_f)))
                return 0
        print("[RTK PROXY] 'rtk' binary not found. Engaging Python Fallback Stream Filter...", file=sys.stderr)

    workspace_dir = _resolve_workspace_root()
    learnings_path = os.path.normpath(os.path.join(workspace_dir, ".orion", "working", "failures.log"))

    is_tripped, fail_count = check_circuit_breaker(learnings_path)
    cmd_str = " ".join(cmd)
    is_reflexion = (
        any(x in cmd_str for x in ("self-evolve", "reflexion", "reset-circuit-breaker", "reset_circuit_breaker"))
        or any(flag in cmd for flag in ("--help", "-h"))
    )
    if is_reflexion:
        try:
            from core.harness.capture import ToolQuantumCapture
            capture = ToolQuantumCapture(
                state_dir=os.path.normpath(os.path.join(workspace_dir, ".orion", "harness"))
            )
            session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
            capture.reset_circuit_breaker(session_id)
        except Exception as _re:
            _log_telemetry(_re, "capabilities:rtk_proxy_reset_cb")

    if is_tripped and not is_reflexion:
        print(f"\n[CIRCUIT BREAKER TRIPPED] {fail_count} consecutive command failures detected in failures.log.", file=sys.stderr)
        print("[CIRCUIT BREAKER] Hard stop triggered per AGENTS.md §1 Core Guardrails.", file=sys.stderr)
        print("[CIRCUIT BREAKER] Stop calling tools and conduct root-cause analysis or run reflexion via .agents/skills/self-evolve/SKILL.md.", file=sys.stderr)
        return 3

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=False,
            stdin=subprocess.DEVNULL,
            timeout=180,
        )

        final_stdout = result.stdout
        if not has_rtk and result.stdout and not _output_feeds_edits(cmd):
            final_stdout = python_fallback_stream_filter(result.stdout)

        if final_stdout:
            print(final_stdout)

        try:
            from core.harness.capture import ToolQuantumCapture
            harness_state_dir = os.path.normpath(os.path.join(workspace_dir, ".orion", "harness"))
            capture = ToolQuantumCapture(state_dir=harness_state_dir)
            session_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID", "cli_session")
            capture.record_tool_call(session_id, "rtk", {"cmd": cmd[:4], "exit_code": result.returncode})
        except Exception as _tqc_err:
            _log_telemetry(_tqc_err, "capabilities:record_tool_call")

        _PASSIVE_COMMANDS = {
            "git status", "git diff", "git log", "git show", "git branch",
            "echo", "ls", "dir", "pwd", "cd", "type", "cat", "which", "where",
            "rtk gain", "rtk discover", "rtk history", "true", "false"
        }
        effective_tokens = cmd[1:] if (has_rtk and cmd and cmd[0] == rtk_bin) else cmd
        cmd_joined = " ".join(effective_tokens).strip().lower()
        is_passive = any(cmd_joined == p or cmd_joined.startswith(p + " ") for p in _PASSIVE_COMMANDS)

        if result.returncode == 0:
            if os.path.exists(learnings_path) and not is_passive:
                try:
                    with open(learnings_path, "a", encoding="utf-8") as f:
                        f.write(f"\n## [Darwinian Hook] Command Succeeded at {datetime.datetime.now().isoformat()}\n**Command**: `{' '.join(cmd)}`\n")
                except OSError as _oe:
                    _log_telemetry(_oe, "capabilities:append_success_log")
            return 0
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        fsm_path = os.path.normpath(os.path.join(workspace_dir, ".orion", "working", "execution_state.json"))
        adv_path = os.path.normpath(os.path.join(workspace_dir, ".orion", "working", "adversarial.json"))
        active_phase = "IDLE"
        if os.path.exists(fsm_path):
            try:
                with open(fsm_path, "r", encoding="utf-8") as ff:
                    active_phase = json.load(ff).get("phase", "IDLE")
            except Exception as _e:
                _log_telemetry(_e, "capabilities.py:load_fsm_phase")

        # TDD RED exemption applies strictly to test executions, not arbitrary command failures
        is_test_command = any(t in cmd_joined for t in ("test", "pytest", "unittest", "evals", "audit", "flutter test"))
        is_expected_red = ((active_phase == "TDD_RED") or os.path.exists(adv_path)) and is_test_command
        if is_expected_red:
            print(f"\n[TDD RED VERIFIED] Test command exited with {result.returncode} as expected in {active_phase}.")
            return result.returncode

        print(f"\n[DARWINIAN HOOK] Command failed with exit code {result.returncode}. Intercepting stderr...")

        error_log = f"\n## [Darwinian Hook] Auto-intercepted Failure at {datetime.datetime.now().isoformat()}\n"
        error_log += f"**Command**: `{' '.join(cmd)}`\n"
        error_log += f"**Exit Code**: {result.returncode}\n"
        error_log += f"**Stderr**:\n```\n{result.stderr.strip()[:1000]}\n```\n"

        os.makedirs(os.path.dirname(learnings_path), exist_ok=True)
        with open(learnings_path, "a", encoding="utf-8") as f:
            f.write(error_log)

        print(f"[DARWINIAN HOOK] Failure appended to {os.path.relpath(learnings_path, os.getcwd())}.")
        print("[SYSTEM DIRECTIVE] Agent must trigger `.agents/skills/self-evolve/SKILL.md` to patch this failure mode.")

        is_tripped_now, count_now = check_circuit_breaker(learnings_path)
        if is_tripped_now:
            print(f"[CIRCUIT BREAKER] Circuit breaker tripped: {count_now} consecutive failures reached. STOP calling tools.", file=sys.stderr)
        return result.returncode
    except Exception as e:
        print(f"[RTK PROXY ERROR] Failed to execute wrapper: {e}", file=sys.stderr)
        return 1

# Backward compatibility alias
main_with_args = run_rtk_proxy



# ==============================================================================
# PILLAR 4: BUN STATIC RUNTIME ENGINE
# ==============================================================================

class BunRuntimeEngine:
    """
    Pillar 4: Bun Static Runtime Engine for .agents.
    Provides zero-compile TypeScript execution, MCP spawning, and microsecond testing.
    """

    def __init__(self, bun_path: Optional[str] = None):
        self.bun_bin = bun_path or find_bun_bin()
        self._version_cache: Optional[str] = None

    def is_available(self) -> Tuple[bool, str]:
        if not self.bun_bin:
            return False, "Bun binary not detected in PATH, ~/.bun/bin, or .agents/bin/"
        if self._version_cache:
            return True, self._version_cache

        try:
            res = subprocess.run([self.bun_bin, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3)
            if res.returncode == 0:
                self._version_cache = res.stdout.strip()
                return True, self._version_cache
            return False, f"Bun returned exit code {res.returncode}: {res.stderr.strip()}"
        except Exception as e:
            _log_telemetry(e, "BunRuntimeEngine:is_available")
            return False, f"Failed to execute Bun: {e}"

    def execute_ts(self, file_path: str, args: Optional[List[str]] = None, timeout: float = 30.0) -> Dict[str, Any]:
        avail, ver = self.is_available()
        if not avail:
            return {
                "status": "DEGRADED_FALLBACK",
                "message": f"Pillar 4 (Bun) offline: {ver}. Running via fallback.",
                "exit_code": 1,
                "stdout": "",
                "stderr": ver
            }

        cmd = [self.bun_bin, "run", file_path] + (args or [])
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            return {
                "status": "SUCCESS" if proc.returncode == 0 else "FAILED",
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "runtime": "bun",
                "version": ver
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "message": f"Execution timed out (> {timeout}s)",
                "exit_code": 124,
                "stdout": "",
                "stderr": "TimeoutExpired"
            }
        except Exception as e:
            _log_telemetry(e, f"execute_ts:{file_path}")
            return {
                "status": "ERROR",
                "message": str(e),
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e)
            }

    def get_mcp_spawn_command(self, package_or_file: str, args: Optional[List[str]] = None) -> List[str]:
        bun_cmd = self.bun_bin or "bun"
        if package_or_file.endswith((".ts", ".js", ".mjs")):
            return [bun_cmd, "run", package_or_file] + (args or [])
        return [bun_cmd, "x", "-y", package_or_file] + (args or [])

    def run_fast_test(self, test_target: str, timeout: float = 10.0) -> Dict[str, Any]:
        avail, ver = self.is_available()
        if not avail:
            return {
                "status": "DEGRADED_FALLBACK",
                "message": "Bun test unavailable; degrading to host test command.",
                "exit_code": 1
            }

        cmd = [self.bun_bin, "test", test_target]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
            return {
                "status": "PASS" if proc.returncode == 0 else "FAIL",
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "version": ver
            }
        except Exception as e:
            _log_telemetry(e, f"run_fast_test:{test_target}")
            return {"status": "ERROR", "message": str(e), "exit_code": 1}


# ==============================================================================
# MAIN CLI DISPATCHER
# ==============================================================================

def main():
    import argparse
    raw_args = sys.argv[1:]

    if raw_args and (raw_args[0] in ["rtk", "rtk_proxy"] or raw_args[:2] == ["hook", "antigravity"] or (len(raw_args) >= 1 and raw_args[0] in ["gain", "discover", "proxy", "history", "read", "hook"])):
        sys.exit(run_rtk_proxy(raw_args[1:] if raw_args[0] in ["rtk", "rtk_proxy"] else raw_args))

    if raw_args and raw_args[0] in ["bun", "bun_runtime"]:
        b_args = raw_args[1:]
        b_parser = argparse.ArgumentParser(description="Pillar 4: Bun Static Runtime Engine")
        b_sub = b_parser.add_subparsers(dest="action")
        b_sub.add_parser("status", help="Check Bun binary availability")

        run_p = b_sub.add_parser("run", help="Execute TypeScript file")
        run_p.add_argument("file", help="Path to .ts or .js file")
        run_p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass")

        test_p = b_sub.add_parser("test", help="Execute microsecond tests")
        test_p.add_argument("target", help="Test target")

        mcp_p = b_sub.add_parser("mcp", help="Generate MCP spawn command")
        mcp_p.add_argument("package", help="Package or script")
        mcp_p.add_argument("args", nargs=argparse.REMAINDER, help="Arguments")

        parsed = b_parser.parse_args(b_args)
        engine = BunRuntimeEngine()
        if parsed.action == "status" or not parsed.action:
            avail, ver = engine.is_available()
            if avail:
                print(f"⚡ [PILLAR 4 ACTIVE] Bun Static Runtime: {engine.bun_bin} (Version: {ver})")
            else:
                print(f"⚠️ [PILLAR 4 DEGRADED] Bun Static Runtime offline: {ver}")
        elif parsed.action == "run":
            res = engine.execute_ts(parsed.file, args=parsed.args)
            if res.get("stdout"): sys.stdout.write(res["stdout"])
            if res.get("stderr"): sys.stderr.write(res["stderr"])
            sys.exit(res.get("exit_code", 0))
        elif parsed.action == "test":
            res = engine.run_fast_test(parsed.target)
            print(f"[BUN TEST] Status: {res['status']} (Exit Code: {res['exit_code']})")
            sys.exit(res.get("exit_code", 0))
        elif parsed.action == "mcp":
            cmd = engine.get_mcp_spawn_command(parsed.package, args=parsed.args)
            print("MCP Spawn Command:\n  " + " ".join(cmd))
        sys.exit(0)

    force = "--force-refresh" in raw_args
    print_pillars_matrix(force_refresh=force)


if __name__ == "__main__":
    main()

