"""Core scripts package for .agents ecosystem.

Exposes the 8 Canonical Core Modules with lazy loading (PEP 562):
- capabilities
- db
- paths
- security
- scanner
- orion_graph
- sandbox
- memory
"""

import importlib
from typing import Any

_MODULE_MAP = {
    # capabilities
    "find_binary": ".capabilities",
    "find_rtk_bin": ".capabilities",
    "find_bun_bin": ".capabilities",
    "probe_capabilities": ".capabilities",
    "run_rtk_proxy": ".capabilities",
    "check_circuit_breaker": ".capabilities",
    "detect_hardware": ".capabilities",
    "enqueue_cloud_handoff": ".capabilities",
    "clear_cloud_handoff": ".capabilities",
    "execute_neuro_symbolic": ".capabilities",
    "select_optimal_ollama_model": ".capabilities",
    "load_neuro_symbolic_cache": ".capabilities",
    "save_neuro_symbolic_cache": ".capabilities",
    "BunRuntimeEngine": ".capabilities",
    # db
    "connect_sqlite": ".db",
    "log_telemetry": ".db",
    "atomic_write_text": ".db",
    "table_exists": ".db",
    "sanitize_fts_query": ".db",
    "build_fts_query_or": ".db",
    "pack_vector": ".db",
    "unpack_vector": ".db",
    "cosine_similarity": ".db",
    "estimate_tokens": ".db",
    "truncate_tokens": ".db",
    "ActionObservationStream": ".db",
    "SovereignTracer": ".db",
    # paths
    "normalize_path": ".paths",
    "get_workspace_dir": ".paths",
    "get_agents_dir": ".paths",
    "get_orion_dir": ".paths",
    "get_persistence_db_path": ".paths",
    "get_context_dir": ".paths",
    "get_scratch_dir": ".paths",
    # security
    "redact_secrets": ".security",
    "scan_for_secrets": ".security",
    "redact_data": ".security",
    "SecurityAuditor": ".security",
    "SecurityBaseline": ".security",
    "PromptSecurityDefense": ".security",
    "CanaryDefense": ".security",
    "ASTSecurityVisitor": ".security",
    # scanner
    "build_repo_map": ".scanner",
    "generate_skeleton": ".scanner",
    "scan_code_map": ".scanner",
    # orion_graph
    "OrionGraphStore": ".orion_graph",
    # sandbox
    "execute_snippet": ".sandbox",
    "parse_jsonrpc_request": ".sandbox",
    "format_jsonrpc_response": ".sandbox",
    "format_jsonrpc_error": ".sandbox",
    # memory
    "MultiLayerMemoryManager": ".memory",
    "CoreMemoryManager": ".memory",
    "ArchivalMemoryManager": ".memory",
    "RecallMemoryManager": ".memory",
    "SecondBrainManager": ".memory",
    "louvain_clustering": ".memory",
}

_SUBMODULES = {
    "capabilities",
    "db",
    "paths",
    "security",
    "scanner",
    "orion_graph",
    "sandbox",
    "memory",
}


def __getattr__(name: str) -> Any:
    if name in _SUBMODULES:
        mod = importlib.import_module(f".{name}", __name__)
        globals()[name] = mod
        return mod

    target_mod = _MODULE_MAP.get(name)
    if target_mod:
        mod = importlib.import_module(target_mod, __name__)
        val = getattr(mod, name)
        globals()[name] = val
        return val

    # Fallback: scan submodules
    for sub in _SUBMODULES:
        try:
            mod = importlib.import_module(f".{sub}", __name__)
            if hasattr(mod, name):
                val = getattr(mod, name)
                globals()[name] = val
                return val
        except ImportError:
            continue

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals().keys()) + list(_SUBMODULES) + list(_MODULE_MAP.keys()))
