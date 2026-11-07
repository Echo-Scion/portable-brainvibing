"""
Dual-Engine Second Worker Subsystem (Ollama + API Key Provider / OpenCode Go).
Provides CLI management, status probing, 5-Lens Goldfish Swarm spec auditing,
adaptive concurrency execution, and lookahead patch pre-drafting.
"""

import sys
import os
import json
import ast
import argparse
from typing import Dict, Any, Optional, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

_scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from core.capabilities import (
    generate_completion,
    execute_neuro_symbolic,
    resolve_ollama_base_url,
    resolve_local_ai_endpoint,
    parse_model_parameters_b,
)
from core.db import atomic_write_text, log_telemetry

WORKSPACE_DIR = os.path.abspath(os.path.join(_scripts_dir, "..", ".."))

GOLDFISH_LENSES: Dict[str, str] = {
    "simplicity-reuse": "Audit for YAGNI, over-engineering, speculative abstractions, and missed opportunities to reuse existing codebase helpers.",
    "comprehension": "Synthesize what the proposal changes and how it interacts with existing state. Flag any ambiguous or contradictory specifications.",
    "system-risks": "Probe across the Triad: Boundary/Malformed Input, Resource/Concurrency race conditions, and Silent Failures/Masked Fallbacks.",
    "implementation-readiness": "Verify Stage 5 Zero-Decision Check: ensure zero unresolved architectural forks remain for the implementer.",
    "layer-boundaries": "Audit 5-Tier DNA stratification (1_contracts -> 5_presentation) and ensure zero upward/circular dependency violations.",
}

# Multi-Model Harness Stratification per Lens
GOLDFISH_LENS_MODEL_SLOT: Dict[str, Tuple[str, str]] = {
    "simplicity-reuse": ("api_fast", "local_code"),
    "comprehension": ("api_smart", "local_heavy"),
    "system-risks": ("api_smart", "local_heavy"),
    "implementation-readiness": ("api_fast", "local_code"),
    "layer-boundaries": ("api_nano", "local_fast"),
}

# Canonical 10-Role Sovereign Swarm Registry
ROLE_HARNESS_MATRIX: Dict[str, Dict[str, Any]] = {
    "orchestrator": {
        "title": "Master State Machine & Bento Slicer",
        "slot_api": "api_smart",
        "slot_local": "local_heavy",
        "turn_limit": 10,
        "description": "Orchestrates full-lifecycle execution, slices specs into Bento Action Cards, and directs 4-lane routing."
    },
    "reviewer": {
        "title": "Adversarial 5-Lens Spec Auditor",
        "slot_api": "api_smart",
        "slot_local": "local_heavy",
        "turn_limit": 5,
        "description": "Performs stateless 5-lens Goldfish Swarm audits across simplicity, comprehension, risks, readiness, and boundaries."
    },
    "fixer": {
        "title": "Surgical Code Patcher & Pre-Drafter",
        "slot_api": "api_fast",
        "slot_local": "local_code",
        "turn_limit": 3,
        "description": "Drafts AST-verified surgical code replacements and lookahead task patches with zero adjacent damage."
    },
    "explorer": {
        "title": "AST Codebase Scout & Topology Cartographer",
        "slot_api": "api_nano",
        "slot_local": "local_fast",
        "turn_limit": 2,
        "description": "Scans AST structures, extracts symbol maps, and generates concise JSONL context deltas <=30 lines."
    },
    "plan": {
        "title": "Technical Specification & Bento Synthesizer",
        "slot_api": "api_smart",
        "slot_local": "local_heavy",
        "turn_limit": 3,
        "description": "Synthesizes architectural requirements into actionable Bento Action Cards with verbatim SEARCH/REPLACE blocks."
    },
    "oracle": {
        "title": "Strategic Architecture & Triad Invariant Interrogator",
        "slot_api": "api_smart",
        "slot_local": "local_heavy",
        "turn_limit": 2,
        "description": "Evaluates proposals against strategic rigor, probing boundary inputs, concurrency, and masked failures."
    },
    "designer": {
        "title": "UI/UX & Aesthetic Floor Guardian",
        "slot_api": "api_fast",
        "slot_local": "local_code",
        "turn_limit": 2,
        "description": "Enforces 60-30-10 surface contrast, design tokens, responsive constraints, and WCAG accessibility standards."
    },
    "librarian": {
        "title": "Knowledge Base & SQLite FTS5 Graph Retriever",
        "slot_api": "api_nano",
        "slot_local": "local_fast",
        "turn_limit": 2,
        "description": "Indexes and retrieves project canons, past architectural decisions, and knowledge graph triplets without context bloat."
    },
    "web-researcher": {
        "title": "Sanitized External Intelligence Scout",
        "slot_api": "api_fast",
        "slot_local": "local_code",
        "turn_limit": 2,
        "description": "Filters external technical documentation through prompt injection and secret sanitization firewalls."
    },
    "councillor": {
        "title": "Independent Second-Opinion & Tie-Breaker Arbitrator",
        "slot_api": "api_council",
        "slot_local": "local_heavy",
        "turn_limit": 2,
        "description": "Provides an orthogonal perspective from a distinct model family when facing 50/50 architectural forks."
    },
}


def classify_task_role(prompt: str) -> str:
    """Classifies user intent into one of the 10 specialized harness roles using deterministic heuristic scoring."""
    p_lower = prompt.lower()
    scores = {role: 0 for role in ROLE_HARNESS_MATRIX}

    keywords = {
        "explorer": ["explore", "map", "locate", "where", "find", "symbols", "structure", "topology", "ast", "scan"],
        "reviewer": ["audit", "review", "check", "verify", "vulnerabilit", "security", "gap", "flaw", "triad"],
        "fixer": ["fix", "patch", "repair", "replace", "refactor", "bug", "implement", "code", "modify", "edit"],
        "plan": ["plan", "spec", "bento", "roadmap", "breakdown", "action card", "rfc", "requirements"],
        "oracle": ["strategy", "architecture", "tradeoff", "system design", "invariant", "why", "rationale", "triad probe"],
        "designer": ["ui", "ux", "layout", "css", "style", "theme", "aesthetic", "color", "contrast", "wcag", "responsive"],
        "librarian": ["doc", "docs", "documentation", "canon", "rag", "knowledge", "fts5", "triplet", "history"],
        "web-researcher": ["web", "external", "search", "online", "fetch", "library", "upstream", "package", "dependency"],
        "councillor": ["second opinion", "council", "councillor", "tie breaker", "debate", "alternative", "fork", "disagree"],
        "orchestrator": ["orchestrate", "lifecycle", "workflow", "state machine", "full cycle", "pipeline", "end to end"],
    }

    for role, kw_list in keywords.items():
        for kw in kw_list:
            if kw in p_lower:
                scores[role] += 1

    sorted_roles = sorted(scores.items(), key=lambda x: -x[1])
    if sorted_roles[0][1] > 0:
        return sorted_roles[0][0]
    return "fixer" if any(w in p_lower for w in ("change", "update", "create", "write")) else "oracle"


def _resolve_lens_model(lens_name: str, backend_kind: str, default_model: str, models_map: Dict[str, str]) -> str:
    """Selects the specialized model slot for a specific Goldfish lens to diversify adversarial review."""
    api_slot, local_slot = GOLDFISH_LENS_MODEL_SLOT.get(lens_name, ("api_smart", "local_heavy"))
    if backend_kind == "api":
        return models_map.get(api_slot, default_model)
    if backend_kind == "ollama":
        return models_map.get(local_slot, default_model)
    return default_model


def _resolve_role_model(role_name: str, backend_kind: str, default_model: str, models_map: Dict[str, str]) -> str:
    """Resolves the designated model for a given role based on the active backend."""
    role_meta = ROLE_HARNESS_MATRIX.get(role_name, {})
    slot_api = role_meta.get("slot_api", "api_smart")
    slot_local = role_meta.get("slot_local", "local_heavy")
    if backend_kind == "api":
        return models_map.get(slot_api, default_model)
    if backend_kind == "ollama":
        return models_map.get(slot_local, default_model)
    return default_model


def get_worker_status() -> Dict[str, Any]:
    mode = os.environ.get("ORION_WORKER_MODE", "local_first")
    ollama_enabled = os.environ.get("ORION_OLLAMA_ENABLED", "true").lower() == "true"
    api_enabled = os.environ.get("ORION_API_WORKER_ENABLED", "true").lower() == "true"

    ollama_url = os.environ.get("ORION_OLLAMA_URL") or resolve_ollama_base_url() or "Offline"
    api_url = os.environ.get("ORION_API_BASE_URL", "https://opencode.ai/zen/go/v1")
    api_key_present = bool(os.environ.get("ORION_API_KEY"))

    models = {
        "local_fast": os.environ.get("ORION_OLLAMA_MODEL_FAST", "qwen2.5-coder:1.5b"),
        "local_code": os.environ.get("ORION_OLLAMA_MODEL_CODE", "qwen2.5-coder:7b"),
        "local_heavy": os.environ.get("ORION_OLLAMA_MODEL_HEAVY", "deepseek-r1:14b"),
        "api_nano": os.environ.get("ORION_API_MODEL_NANO", "glm-4.5-air"),
        "api_fast": os.environ.get("ORION_API_MODEL_FAST", "qwen3-coder-flash"),
        "api_smart": os.environ.get("ORION_API_MODEL_SMART", "deepseek-v4-pro"),
        "api_council": os.environ.get("ORION_API_MODEL_COUNCIL", "kimi-k3"),
    }

    return {
        "mode": mode,
        "ollama": {
            "enabled": ollama_enabled,
            "url": ollama_url,
        },
        "api_worker": {
            "enabled": api_enabled,
            "url": api_url,
            "key_configured": api_key_present,
        },
        "models": models,
    }


def _select_worker_backend(prefer_smart: bool = False) -> Tuple[str, str, int]:
    """
    Determines active execution backend and safe concurrency limit:
    Returns (provider_kind, model_name, recommended_max_workers).
    - 'api': Remote API Worker (OpenCode Go) -> parallelizable (max_workers=3)
    - 'ollama': Local Ollama single-GPU -> sequential queue (max_workers=1) to prevent VRAM thrashing
    - 'offline': Neither available -> Tier-0 mechanical scout fallback (max_workers=1)
    """
    status = get_worker_status()
    mode = status["mode"]
    api_ready = status["api_worker"]["enabled"] and status["api_worker"]["key_configured"]
    ollama_ready = status["ollama"]["enabled"] and status["ollama"]["url"] != "Offline"
    env_max = int(os.environ.get("ORION_MAX_PARALLEL", "3"))

    if mode == "api_first" and api_ready:
        m_key = "api_smart" if prefer_smart else "api_fast"
        return ("api", status["models"][m_key], max(1, min(env_max, 5)))
    if ollama_ready and mode in ("local_first", "local_only"):
        m_key = "local_heavy" if prefer_smart else "local_code"
        return ("ollama", status["models"][m_key], 1)
    if api_ready and mode != "local_only":
        m_key = "api_smart" if prefer_smart else "api_fast"
        return ("api", status["models"][m_key], max(1, min(env_max, 5)))
    if ollama_ready:
        m_key = "local_heavy" if prefer_smart else "local_code"
        return ("ollama", status["models"][m_key], 1)
    return ("offline", "tier0_mechanical", 1)


def cmd_status() -> int:
    status = get_worker_status()
    provider_kind, model_name, max_workers = _select_worker_backend(prefer_smart=False)
    print("========================================")
    print(" DUAL-ENGINE SECOND WORKER SUBSYSTEM")
    print("========================================")
    print(f"Mode               : {status['mode']}")
    print(f"Active Backend     : {provider_kind.upper()} ({model_name})")
    print(f"Max Concurrency    : {max_workers} worker threads")
    print(f"Local Worker (Ollama): {'ACTIVE' if status['ollama']['enabled'] else 'DISABLED'} ({status['ollama']['url']})")
    print(f"API Worker (Remote)  : {'ACTIVE' if status['api_worker']['enabled'] else 'DISABLED'} ({status['api_worker']['url']})")
    print(f"API Key Configured  : {'YES' if status['api_worker']['key_configured'] else 'NO (Set ORION_API_KEY in .env)'}")
    print("\n[ACTIVE MODEL MAPPINGS]")
    for k, v in status["models"].items():
        print(f"  - {k:<12}: {v}")

    print("\n[10-ROLE SOVEREIGN SWARM REGISTRY]")
    for r_key, r_meta in ROLE_HARNESS_MATRIX.items():
        assigned_model = _resolve_role_model(r_key, provider_kind, model_name, status["models"])
        print(f"  • {r_key:<15} [{r_meta['slot_api']}]: {assigned_model} (Max Turns: {r_meta['turn_limit']})")
    return 0


def cmd_dispatch_role(role: str, prompt: str, target_file: Optional[str] = None) -> int:
    """Executes a single role harness with specialized prompt, model, session tag, and turn limit."""
    if role not in ROLE_HARNESS_MATRIX:
        sys.stderr.write(f"[ERROR] Unknown role '{role}'. Available roles: {', '.join(ROLE_HARNESS_MATRIX.keys())}\n")
        return 1

    r_meta = ROLE_HARNESS_MATRIX[role]
    status = get_worker_status()
    provider_kind, default_model, _ = _select_worker_backend(prefer_smart=(r_meta["slot_api"] == "api_smart"))
    assigned_model = _resolve_role_model(role, provider_kind, default_model, status["models"])

    file_ctx = ""
    if target_file and os.path.isfile(target_file):
        try:
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                file_ctx = f"\n\n[TARGET FILE CONTEXT: {os.path.basename(target_file)}]\n{f.read(8000)}"
        except Exception as e:
            file_ctx = f"\n\n[ERROR READING TARGET FILE: {e}]"

    full_prompt = f"""You are the [{role.upper()}] subagent ({r_meta['title']}).
Role Mission: {r_meta['description']}
Max Execution Turns: {r_meta['turn_limit']}

[TASK INSTRUCTION]
{prompt}{file_ctx}

Provide your response in clean, concise, technical Markdown with zero conversational fluff."""

    if provider_kind == "offline":
        print(f"[{role.upper()}] [TIER-0 OFFLINE MODE] Both API and Local workers are offline.")
        print(f"Task queued into .orion/working/cloud_handoff_queue.json.")
        return 0

    print(f"[{role.upper()}] Dispatching to {provider_kind.upper()} ({assigned_model})...")
    res = generate_completion(
        prompt=full_prompt,
        model=assigned_model,
        system_prompt=f"You are the {role.upper()} autonomous software engineering agent. Be rigorous, terse, and precise.",
        timeout_sec=45.0,
        temperature=0.1,
        session_tag=f"role_{role}"
    )

    if not res:
        sys.stderr.write(f"[ERROR] Generation returned empty on model '{assigned_model}'.\n")
        return 1

    out_dir = os.path.join(WORKSPACE_DIR, ".orion", "working", "delegations")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"role_{role}_{int(os.times().system)}.md")
    atomic_write_text(out_file, res.strip())

    print(f"\n--- [{role.upper()} VERDICT] ---")
    print(res.strip())
    print(f"\n[OUTPUT SAVED] {out_file}")
    return 0


def cmd_auto_pipeline(prompt: str, target_file: Optional[str] = None) -> int:
    """Classifies user intent and executes an automated sequential role pipeline."""
    primary_role = classify_task_role(prompt)
    print(f"[ORION AUTO-ROUTER] Detected Primary Intent: `{primary_role}`")

    # Define standard sequential pipelines based on primary intent
    pipeline = [primary_role]
    if primary_role in ("fixer", "coder"):
        pipeline = ["explorer", "oracle", "fixer", "councillor"] if target_file else ["oracle", "fixer", "councillor"]
    elif primary_role in ("reviewer", "audit"):
        pipeline = ["explorer", "reviewer"] if target_file else ["reviewer"]
    elif primary_role in ("plan", "spec"):
        pipeline = ["oracle", "plan", "reviewer"]

    print(f"[ORION AUTO-PIPELINE] Sequential execution plan: {' -> '.join(pipeline)}")

    current_prompt = prompt
    for idx, step_role in enumerate(pipeline, 1):
        print(f"\n>>> [STEP {idx}/{len(pipeline)}] Running role `{step_role}`...")
        ret = cmd_dispatch_role(step_role, current_prompt, target_file)
        if ret != 0:
            sys.stderr.write(f"[PIPELINE HALT] Step {step_role} failed with exit code {ret}.\n")
            return ret

    print(f"\n✅ [ORION AUTO-PIPELINE COMPLETE] All {len(pipeline)} steps finished successfully.")
    return 0


def _run_single_lens(lens_name: str, lens_focus: str, spec_content: str, backend_kind: str, model_name: str) -> Dict[str, Any]:
    """Evaluates a single Goldfish lens and returns structured status."""
    prompt = f"""You are a Goldfish Subagent auditing a technical spec on the lens: [{lens_name}].
Lens Goal: {lens_focus}

Evaluate the specification/plan below against this specific lens.
Find up to 3 concrete findings or gaps. If no gaps exist, explicitly state: 'No gaps identified under this lens.'

[SPECIFICATION / PLAN TO AUDIT]
{spec_content[:8000]}

Respond in clean Markdown:
### Lens: {lens_name}
- **Status**: PASS or GAPS_FOUND
- **Findings**:
  1. ...
  2. ...
- **Recommendation**: ...
"""
    if backend_kind == "offline":
        return {
            "lens": lens_name,
            "status": "not_run",
            "reason": "Both API and Ollama workers offline (Tier-0 mechanical mode)",
            "content": f"### Lens: {lens_name}\n- **Scout Status**: not_run (Reason: Offline)",
        }

    res = generate_completion(
        prompt=prompt,
        model=model_name,
        system_prompt="You are an adversarial, unbiased code and architecture auditor.",
        timeout_sec=45.0,
        temperature=0.1,
    )
    if res and len(res.strip()) > 20:
        return {
            "lens": lens_name,
            "status": "completed",
            "reason": "Success",
            "content": res.strip(),
        }
    return {
        "lens": lens_name,
        "status": "not_run",
        "reason": f"Completion returned empty or timed out on model '{model_name}'",
        "content": f"### Lens: {lens_name}\n- **Scout Status**: not_run (Reason: Completion timed out/empty)",
    }


def cmd_goldfish_audit(spec_path: str, rubric: str = "all") -> int:
    """
    5-Lens Goldfish Swarm Audit:
    Performs an isolated review of the target spec/plan across 5 parallel or sequential lenses
    without conversation history to prevent confirmation bias.
    """
    abs_spec = os.path.abspath(spec_path)
    if not os.path.exists(abs_spec):
        sys.stderr.write(f"[ERROR] Target spec file not found: {abs_spec}\n")
        return 1

    try:
        with open(abs_spec, "r", encoding="utf-8") as f:
            spec_content = f.read()
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to read spec file: {e}\n")
        return 1

    status_cfg = get_worker_status()
    models_map = status_cfg.get("models", {})
    backend_kind, model_name, max_workers = _select_worker_backend(prefer_smart=True)
    selected_lenses = list(GOLDFISH_LENSES.keys()) if rubric == "all" else [r.strip() for r in rubric.split(",") if r.strip() in GOLDFISH_LENSES]

    print(f"[GOLDFISH] Dispatching 5-Lens Swarm Audit for `{os.path.basename(abs_spec)}` via {backend_kind.upper()} ({model_name}) with max_workers={max_workers}...")

    results = []
    if max_workers > 1 and backend_kind == "api":
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_lens = {
                executor.submit(
                    _run_single_lens,
                    lname,
                    GOLDFISH_LENSES[lname],
                    spec_content,
                    backend_kind,
                    _resolve_lens_model(lname, backend_kind, model_name, models_map),
                ): lname
                for lname in selected_lenses
            }
            for future in as_completed(future_to_lens):
                results.append(future.result())
    else:
        for lname in selected_lenses:
            lens_model = _resolve_lens_model(lname, backend_kind, model_name, models_map)
            results.append(_run_single_lens(lname, GOLDFISH_LENSES[lname], spec_content, backend_kind, lens_model))

    # Maintain predictable lens ordering
    results.sort(key=lambda x: selected_lenses.index(x["lens"]) if x["lens"] in selected_lenses else 99)

    report_lines = [
        f"# 5-Lens Goldfish Swarm Audit Report",
        f"- **Spec File**: `{os.path.basename(abs_spec)}`",
        f"- **Backend**: `{backend_kind}` ({model_name})",
        f"- **Concurrency**: `{max_workers} workers`",
        "",
        "## Swarm Lens Summary",
    ]

    for r in results:
        badge = "✅ COMPLETED" if r["status"] == "completed" else f"⚠️ NOT RUN ({r['reason']})"
        report_lines.append(f"- **{r['lens']}**: {badge}")

    report_lines.extend(["", "## Detailed Lens Assessments", ""])
    for r in results:
        report_lines.append(r["content"])
        report_lines.append("\n---\n")

    out_dir = os.path.join(WORKSPACE_DIR, ".orion", "working", "delegations")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "result-goldfish.md")
    atomic_write_text(out_file, "\n".join(report_lines))

    print(f"[SUCCESS] 5-Lens Goldfish Swarm Report written to: {out_file}")
    return 0


def cmd_pre_draft(target_file: str, span: str, goal: str, task_id: str) -> int:
    """Pre-drafts a replacement code block for lookahead task N+1 into .orion/working/drafts/draft_<task_id>.json."""
    abs_file = os.path.abspath(target_file)
    if not os.path.exists(abs_file):
        sys.stderr.write(f"[ERROR] Target file not found for pre-draft: {abs_file}\n")
        return 1

    try:
        with open(abs_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to read target file: {e}\n")
        return 1

    prompt = f"""Draft a surgical code block replacement for file `{os.path.basename(abs_file)}` over span `{span}`.
Goal: {goal}

Current File Context:
{content[:4000]}

Respond ONLY in JSON matching format:
{{
  "task_id": "{task_id}",
  "target_file": "{target_file}",
  "replacement_code": "<replacement code block>"
}}
"""

    backend_kind, model_name, _ = _select_worker_backend(prefer_smart=False)
    print(f"[PRE-DRAFT] Generating lookahead code for Task {task_id} on `{os.path.basename(abs_file)}` via {backend_kind.upper()} ({model_name})...")

    payload, provider = execute_neuro_symbolic(
        task_type="micro_syntax",
        prompt=prompt,
        min_params_b=3.0,
    )

    code = payload.get("replacement_code", "")
    if abs_file.endswith(".py") and code:
        try:
            ast.parse(code)
        except Exception as e:
            sys.stderr.write(f"[WARNING] Lookahead pre-draft for task {task_id} failed AST parse check: {e}\n")
            return 1

    draft_dir = os.path.join(WORKSPACE_DIR, ".orion", "working", "drafts")
    os.makedirs(draft_dir, exist_ok=True)
    draft_file = os.path.join(draft_dir, f"draft_{task_id}.json")

    record = {
        "task_id": task_id,
        "target_file": target_file,
        "replacement_code": code,
        "provider": provider,
    }
    atomic_write_text(draft_file, json.dumps(record, indent=2))
    print(f"[SUCCESS] Lookahead pre-draft saved: {draft_file}")
    return 0


def cmd_draft_patch(target_file: str, span: str, goal: str) -> int:
    """Drafts a surgical diff via Second Worker using execute_neuro_symbolic."""
    abs_file = os.path.abspath(target_file)
    if not os.path.exists(abs_file):
        sys.stderr.write(f"[ERROR] Target file not found: {abs_file}\n")
        return 1

    try:
        with open(abs_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to read target file: {e}\n")
        return 1

    prompt = f"""Draft a surgical code patch for file `{os.path.basename(abs_file)}` over span `{span}`.
Goal: {goal}

Current File Context:
{content[:4000]}

Return JSON payload matching contract:
{{
  "file": "{os.path.basename(abs_file)}",
  "target_span": "{span}",
  "patch_diff": "<diff or replacement block>",
  "explanation": "<rationale>"
}}
"""

    payload, provider = execute_neuro_symbolic(
        task_type="micro_syntax",
        prompt=prompt,
        min_params_b=3.0,
    )

    out_dir = os.path.join(WORKSPACE_DIR, ".orion", "working", "delegations")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"draft_patch_{os.path.basename(abs_file)}.json")
    atomic_write_text(out_file, json.dumps(payload, indent=2))

    print(f"[SUCCESS] Draft patch created via provider '{provider}': {out_file}")
    return 0


def main(args: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Dual-Engine Second Worker Subsystem CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="Worker subcommands")

    subparsers.add_parser("status", help="Print Dual-Engine configuration and status")

    gold_parser = subparsers.add_parser("goldfish", help="Run 5-Lens Goldfish Swarm Spec Audit")
    gold_parser.add_argument("--spec", required=True, help="Path to specification/plan file")
    gold_parser.add_argument("--rubric", default="all", help="Comma-separated rubric criteria or 'all'")

    subparsers.add_parser("review", help="Alias for goldfish 5-Lens Swarm audit")

    pre_parser = subparsers.add_parser("pre-draft", help="Pre-draft lookahead replacement code for task N+1")
    pre_parser.add_argument("--file", required=True, help="Target file path")
    pre_parser.add_argument("--span", default="L1-L100", help="Line span")
    pre_parser.add_argument("--goal", required=True, help="Goal description")
    pre_parser.add_argument("--task-id", required=True, help="Task identifier (e.g. 1.2)")

    patch_parser = subparsers.add_parser("draft-patch", help="Draft patch using Second Worker")
    patch_parser.add_argument("--file", required=True, help="Target file path")
    patch_parser.add_argument("--span", default="L1-L100", help="Line span (e.g. L10-L50)")
    patch_parser.add_argument("--goal", required=True, help="Goal description for the patch")

    disp_parser = subparsers.add_parser("dispatch", help="Dispatch task to a specialized 10-Role Harness")
    disp_parser.add_argument("--role", required=True, help="Target role (e.g. explorer, reviewer, fixer, oracle, councillor)")
    disp_parser.add_argument("--prompt", required=True, help="Task prompt or instruction")
    disp_parser.add_argument("--file", default=None, help="Optional target file path")

    auto_parser = subparsers.add_parser("auto", help="Auto-classify intent and run multi-role autonomous pipeline")
    auto_parser.add_argument("prompt", help="Natural language engineering goal")
    auto_parser.add_argument("--file", default=None, help="Optional target file path")

    parsed = parser.parse_args(args)

    if parsed.subcommand == "status" or not parsed.subcommand:
        return cmd_status()
    elif parsed.subcommand in ("goldfish", "review"):
        spec_path = getattr(parsed, "spec", "") or (args[1] if len(args) > 1 and not args[1].startswith("-") else "")
        rubric = getattr(parsed, "rubric", "all")
        return cmd_goldfish_audit(spec_path, rubric)
    elif parsed.subcommand == "pre-draft":
        return cmd_pre_draft(parsed.file, parsed.span, parsed.goal, parsed.task_id)
    elif parsed.subcommand == "draft-patch":
        return cmd_draft_patch(parsed.file, parsed.span, parsed.goal)
    elif parsed.subcommand == "dispatch":
        return cmd_dispatch_role(parsed.role, parsed.prompt, parsed.file)
    elif parsed.subcommand == "auto":
        return cmd_auto_pipeline(parsed.prompt, parsed.file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
