#!/usr/bin/env python3
"""
Universal Living Project DNA Sequencer & Epigenetic Mutation Engine (core/dna.py)
--------------------------------------------------------------------------------
Ground-truth architectural genome of the Portable Brainvibing ecosystem.
Codifies the 6 Biological DNA Layers across any language or framework:
  1. Topological & Dependency Law (The Nervous System) - 5-Tier Strata & Forbidden Edges
  2. Naming, Symbol & Pattern Signatures (Cell Morphology) - AST Symbol Stereotypes
  3. Bounded Contexts & Feature Verticals (Organ Map) - Adaptive Hybrid Tiers & Organs
  4. Critical Invariants & Lethal Mutations (Immune System) - Project & Domain Laws
  5. Entrypoints & Lifecycle Spine (Circulatory System) - High-Gravity Execution Spine
  6. Evolutionary & Mutation Ledger (Epigenetics) - Brownfield Mutation & Compliance Score

Zero-pip runtime: 100% Python 3 standard library.
"""

from __future__ import annotations

import os
import sys
import json
import re
import math
import hashlib
import fnmatch
import sqlite3
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional, Any

# Telemetry helper
try:
    from core.db import log_telemetry as _log_telemetry
except ImportError:
    def _log_telemetry(err: Optional[Exception] = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG") and err:
            sys.stderr.write(f"[DNA_DEBUG] {context}: {err}\n")

def atomic_write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    """Atomic file write using PID-unique temporary file."""
    import uuid
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    temp_path = f"{path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}"
    try:
        with open(temp_path, "w", encoding=encoding, errors="replace") as f:
            f.write(text)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# Canonical 5-Tier Strata Archetype Definitions
CANONICAL_5_TIERS: Dict[str, Dict[str, Any]] = {
    "0_pillars_and_manifests": {
        "gravity": 0,
        "slug": "WORKSPACE_PILLARS_AND_MANIFESTS",
        "title": "Workspace Manifests, Foundational Vision & 4-Pillar Architecture Blueprint",
        "folder_tokens": ["context", "vision", "blueprint", "architecture", "style_guide", "roadmap", "design"],
        "manifest_files": [
            "vision.md", "pubspec.yaml", "package.json", "tsconfig.json", "cargo.toml", "go.mod",
            "pom.xml", "build.gradle", "build.gradle.kts", "pyproject.toml", "requirements.txt",
            "cmakelists.txt", "gemini.md", "agents.md", "claude.md", "design.md", "readme.md"
        ],
        "symbol_stereotypes": [],
        "audit_focus": "Audit alignment with foundational VISION.md invariants, build constraints, dependency pins, security configurations, and global architectural blueprints."
    },
    "1_contracts": {
        "gravity": 1,
        "slug": "CONTRACTS_AND_IMMUTABLE_MODELS",
        "title": "Data Contracts, Schemas & Immutable Models",
        "folder_tokens": ["contracts", "models", "entities", "schemas", "types", "dto", "dtos", "ir"],
        "manifest_files": [],
        "symbol_stereotypes": [
            "model", "dto", "entity", "schema", "contract", "record", "type",
            "freezed", "basemodel", "dataclass", "interface", "struct"
        ],
        "audit_focus": "Audit data integrity, nullability contracts, serialization safety, schema boundary validation, and immutability."
    },
    "2_domain": {
        "gravity": 2,
        "slug": "DOMAIN_LOGIC_AND_USECASES",
        "title": "Core Domain Entities, Use Cases & Business Rules",
        "folder_tokens": ["domain", "usecases", "interactors", "policies", "rules", "domain_logic", "spec"],
        "manifest_files": [],
        "symbol_stereotypes": [
            "usecase", "interactor", "policy", "domain", "calculator", "validator", "rule", "command"
        ],
        "audit_focus": "Audit pure business logic, boundary conditions, malformed input handling, financial precision, and invariant enforcement."
    },
    "3_services": {
        "gravity": 4,
        "slug": "SERVICES_REPOSITORIES_AND_DATA",
        "title": "Repositories, API Services & Persistence Adapters",
        "folder_tokens": ["services", "repositories", "repos", "data", "db", "database", "api", "network", "client", "storage", "dao"],
        "manifest_files": [],
        "symbol_stereotypes": [
            "repository", "service", "datasource", "client", "dao", "adapter", "api", "database", "storage"
        ],
        "audit_focus": "Audit network resilience, SQLite/ORM schemas, connection pooling, idempotency, auth header injection, and retry policies."
    },
    "4_state": {
        "gravity": 6,
        "slug": "STATE_ORCHESTRATION_AND_CONTROLLERS",
        "title": "State Orchestration, Notifiers, Workers & Daemon Controllers",
        "folder_tokens": ["state", "providers", "controllers", "bloc", "cubit", "notifier", "store", "viewmodel", "reducer", "apps", "daemons", "workers", "jobs", "pipelines"],
        "manifest_files": [],
        "symbol_stereotypes": [
            "notifier", "provider", "bloc", "cubit", "controller", "store", "viewmodel", "reducer", "statemachine"
        ],
        "audit_focus": "Audit state orchestration, task pipelines, concurrency safety, stream/task lifecycles, race conditions, and error transitions."
    },
    "5_presentation": {
        "gravity": 7,
        "slug": "PRESENTATION_UI_AND_DESIGN_SYSTEM",
        "title": "Presentation Screens, Widgets, Navigation & Design Tokens",
        "folder_tokens": ["presentation", "screens", "views", "widgets", "pages", "components", "ui", "theme", "router", "routing", "l10n"],
        "manifest_files": [],
        "symbol_stereotypes": [
            "screen", "page", "view", "widget", "dialog", "sheet", "component", "router", "route",
            "consumerwidget", "statelesswidget", "statefulwidget", "theme"
        ],
        "audit_focus": "Audit 5-State visual coverage (Loading, Empty, Success, Error, Shimmer), accessibility/WCAG AA contrast, and zero raw DB/HTTP calls in UI."
    },
    "8_native_and_cli": {
        "gravity": 8,
        "slug": "NATIVE_BRIDGES_AND_CLI_RUNTIME",
        "title": "Native Platform Bridges, FFI & CLI Entrypoints",
        "folder_tokens": ["android", "ios", "macos", "windows", "linux", "web", "bin", "cli", "commands", "ffi", "bridge"],
        "manifest_files": [],
        "symbol_stereotypes": ["plugin", "bridge", "channel", "mainactivity", "appdelegate", "cli", "command"],
        "audit_focus": "Audit platform channel safety, memory leaks in native interop, permissions, subprocess escaping, and CLI signal handling."
    },
    "9_verification": {
        "gravity": 9,
        "slug": "VERIFICATION_AND_TEST_SUITES",
        "title": "Automated Unit, Widget & Integration Verification Suites",
        "folder_tokens": ["test", "tests", "__tests__", "spec", "specs", "e2e", "integration_test", "evals", "harness"],
        "manifest_files": [],
        "symbol_stereotypes": ["test", "spec", "mock", "fixture", "harness"],
        "audit_focus": "Audit test assertion completeness, false green detection, mocking fidelity, and edge-case regression coverage."
    }
}

CANONICAL_DEPENDENCY_LAWS: Dict[str, Any] = {
    "allowed_flow": [
        "5_presentation -> 4_state -> 2_domain -> 1_contracts",
        "4_state -> 3_services -> 2_domain -> 1_contracts",
        "3_services -> 1_contracts",
        "8_native_and_cli -> 3_services -> 1_contracts",
        "9_verification -> [ALL]"
    ],
    "forbidden_edges": [
        {
            "from_tier": "1_contracts",
            "to_tier": ["2_domain", "3_services", "4_state", "5_presentation", "8_native_and_cli"],
            "reason": "Contracts & Data Models must be pure leaf definitions with zero upward dependencies."
        },
        {
            "from_tier": "2_domain",
            "to_tier": ["3_services", "4_state", "5_presentation", "8_native_and_cli"],
            "reason": "Pure Domain Logic must not depend on UI presentation, state managers, or infrastructure services."
        },
        {
            "from_tier": "3_services",
            "to_tier": ["4_state", "5_presentation"],
            "reason": "Services/Repositories must never import UI widgets or state controllers."
        },
        {
            "from_tier": "5_presentation",
            "to_tier": ["3_services"],
            "reason": "Presentation screens/widgets must never bypass State controllers to talk directly to DB/Network."
        }
    ]
}


def get_stack_adapted_tier_meta(tier_key: str, framework: str = "generic", has_ui: bool = False) -> Dict[str, Any]:
    """Returns a stack-accurate copy of canonical tier metadata without leaking mobile/UI bias into headless/backend projects."""
    if tier_key not in CANONICAL_5_TIERS:
        return {"gravity": 4, "slug": "MODULE", "title": "Module", "audit_focus": "Audit core logic and boundaries."}
    meta = dict(CANONICAL_5_TIERS[tier_key])
    fw_l = (framework or "generic").lower()
    if not has_ui or fw_l in ("python", "rust", "go", "node"):
        if tier_key == "4_state":
            meta["title"] = "State Orchestration, Pipelines, Workers & Daemon Controllers"
            meta["audit_focus"] = "Audit state orchestration, task pipelines, concurrency safety, race conditions, and error transitions."
        elif tier_key == "3_services":
            meta["title"] = "Repositories, API Services, Engines & Persistence"
            meta["audit_focus"] = "Audit network resilience, SQLite/ORM schemas, connection pooling, idempotency, and retry policies."
        elif tier_key == "5_presentation":
            meta["title"] = "CLI Commands, Gateways & External Presentation"
            meta["audit_focus"] = "Audit CLI argument parsing, output formatting, terminal safety, and API gateway routing."
    return meta


@dataclass
class ProjectDNA:
    # --- 100% Backward Compatible Fields with legacy packer.py ---
    is_dna_app: bool
    archetype: str
    version: str
    blueprint_path: Optional[str]
    stacks: List[str]
    active_native_roots: List[str]
    dormant_roots: List[str]
    verified_gates: str

    # --- Living Architectural Genome Extensions (6 Biological Layers) ---
    schema_version: str = "0.0.1"
    dna_state: str = "BORN"  # "BORN" | "MUTATING" | "MUTATED" | "BORN_FROM_REVERSE" | "SYNTHESIZED"
    origin: str = "foundation_init"
    primary_framework: str = "generic"
    primary_language: str = "generic"
    vision_path: Optional[str] = None
    context_topology: str = "adaptive_25"
    context_aliases: Dict[str, str] = field(default_factory=dict)
    workspaces: List[Dict[str, Any]] = field(default_factory=list)
    pillars: Dict[str, str] = field(default_factory=dict)
    tiers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    feature_organs: List[Dict[str, Any]] = field(default_factory=list)
    execution_spine: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    layer_violations: List[Dict[str, Any]] = field(default_factory=list)
    chimera_files: List[str] = field(default_factory=list)
    epigenetic_aliases: Dict[str, str] = field(default_factory=dict)
    dna_compliance_score: int = 100
    file_tier_map: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_foundation_root(root_dir: str) -> bool:
    """Checks if root_dir is the upstream foundation hub repository itself."""
    abs_p = os.path.abspath(root_dir)
    return (
        os.path.basename(abs_p) == "_foundation"
        or (
            os.path.isdir(os.path.join(abs_p, ".agents", "canons", "ecosystems"))
            and os.path.isfile(os.path.join(abs_p, ".agents", "scripts", "commands", "foundation.py"))
            and os.path.isdir(os.path.join(abs_p, "tools", "digestpack"))
        )
    )

def is_foundation_agents(root_dir: str) -> bool:
    """Checks if path is directly inside .agents directory."""
    abs_p = os.path.abspath(root_dir)
    return os.path.basename(abs_p) == ".agents" or "/.agents/" in abs_p.replace("\\", "/") or "\\.agents\\" in abs_p


_SHORT_TIER_MAP: Dict[str, str] = {
    "pillars": "0_pillars_and_manifests",
    "manifests": "0_pillars_and_manifests",
    "contracts": "1_contracts",
    "models": "1_contracts",
    "domain": "2_domain",
    "usecases": "2_domain",
    "services": "3_services",
    "data": "3_services",
    "repositories": "3_services",
    "state": "4_state",
    "controllers": "4_state",
    "presentation": "5_presentation",
    "ui": "5_presentation",
    "native": "8_native_and_cli",
    "cli": "8_native_and_cli",
    "verification": "9_verification",
    "tests": "9_verification",
}

_FILE_STEM_PATTERNS: Dict[str, Tuple[str, ...]] = {
    "1_contracts": (
        "_model", ".model", "_dto", ".dto", "_entity", ".entity",
        "_schema", ".schema", "_contract", ".contract", "_types", ".types",
        "types", "schema", "models", "contracts", "entities",
    ),
    "2_domain": (
        "_usecase", ".usecase", "_interactor", ".interactor",
        "_policy", ".policy", "_validator", ".validator", "_rule", ".rule",
        "_calculator", "_domain",
    ),
    "3_services": (
        "_service", ".service", "_repository", ".repository", "_repo", ".repo",
        "_datasource", ".datasource", "_client", ".client", "_dao", ".dao",
        "_adapter", ".adapter", "_api", ".api", "_db", "database",
    ),
    "4_state": (
        "_state", ".state", "_store", ".store", "_notifier", ".notifier",
        "_provider", ".provider", "_controller", ".controller",
        "_bloc", ".bloc", "_cubit", ".cubit", "_viewmodel", ".viewmodel",
        "_reducer", ".reducer", "_slice", ".slice", "state_machine",
    ),
    "5_presentation": (
        "_screen", ".screen", "_page", ".page", "_view", ".view",
        "_widget", ".widget", "_dialog", ".dialog", "_modal", ".modal",
        "_sheet", "_component", ".component", "_router", ".router",
        "_theme", ".theme", "app_router",
    ),
}


def normalize_epigenetic_aliases(raw_aliases: Any) -> Dict[str, str]:
    """
    Normalizes epigenetic_aliases into canonical {folder_prefix: canonical_tier_key} format.
    Supports both canonical Dict[str, str] and inverted Dict[str, List[str]] (e.g. from flutterin).
    """
    if not isinstance(raw_aliases, dict):
        return {}
    normalized: Dict[str, str] = {}
    for k, v in raw_aliases.items():
        if not isinstance(k, str):
            continue
        if isinstance(v, str):
            canon_tier = _SHORT_TIER_MAP.get(v.lower(), v)
            if canon_tier in CANONICAL_5_TIERS:
                normalized[k.replace("\\", "/").strip("/")] = canon_tier
        elif isinstance(v, list):
            canon_tier = _SHORT_TIER_MAP.get(k.lower(), k)
            if canon_tier in CANONICAL_5_TIERS:
                for prefix in v:
                    if isinstance(prefix, str) and prefix.strip():
                        normalized[prefix.replace("\\", "/").strip("/")] = canon_tier
    return normalized


def _match_stem_tier(stem_lower: str) -> Optional[str]:
    """Matches a file's lowercase stem against canonical 5-Tier suffix/stem morphology."""
    for tier_key in ("1_contracts", "5_presentation", "4_state", "3_services", "2_domain"):
        patterns = _FILE_STEM_PATTERNS[tier_key]
        if any(stem_lower == p.lstrip("_.") or stem_lower.endswith(p) for p in patterns):
            return tier_key
    return None


def _is_matching_stereotype(sym_lower: str, stereotype: str) -> bool:
    """Checks if a stereotype matches as a word boundary, prefix, or suffix in an AST symbol, preventing false positives like 'review' matching 'view' or 'screener' matching 'screen'."""
    if stereotype == sym_lower:
        return True
    if len(stereotype) >= 7 and stereotype in sym_lower:
        return True
    # For UI tokens like 'view', 'screen', 'page', 'theme', 'route', 'router', require explicit UI morphology
    # e.g. UserView, view_user, app_router vs review_candidate, preview_data, build_screener_prompt, ScreeningPipeline
    if stereotype in ("view", "screen", "page", "route", "router", "theme"):
        if sym_lower.startswith(f"{stereotype}_") or sym_lower.endswith(f"_{stereotype}"):
            return True
        if sym_lower.endswith(stereotype) and not any(sym_lower.endswith(fp) for fp in ("review", "overview", "preview", "interview")):
            return True
        if sym_lower.startswith(stereotype) and not any(sym_lower.startswith(fp) for fp in ("review", "preview", "screen_data")):
            # Distinguish UI screen from filter/scanner screener
            if stereotype == "screen" and ("screener" in sym_lower or "screening" in sym_lower):
                return False
            return True
        return False
    return stereotype in sym_lower


def classify_file_to_tier(
    rel_path: str,
    symbols: Optional[List[str]] = None,
    epigenetic_aliases: Optional[Dict[str, str]] = None
) -> Tuple[str, int, str, str]:
    """
    Classifies a relative file path into the canonical 5-Tier Architectural Strata.
    Combines 4 stages: Epigenetic Aliases -> Path Tokens -> Filename Stem Morphology -> AST Symbol Stereotypes.
    Returns (tier_key, gravity, slug, title).
    """
    norm = rel_path.replace("\\", "/").strip("/")
    norm_lower = norm.lower()
    base_lower = os.path.basename(norm_lower)
    stem_lower = os.path.splitext(base_lower)[0]
    parts = norm_lower.split("/")
    syms_lower = [s.lower() for s in (symbols or [])]

    # 1. Check epigenetic aliases first (supports canonical, list-inverted, and wildcard glob schemas)
    if epigenetic_aliases:
        safe_aliases = normalize_epigenetic_aliases(epigenetic_aliases)
        for alias_prefix, mapped_tier in sorted(safe_aliases.items(), key=lambda x: -len(x[0])):
            prefix_lower = alias_prefix.lower()
            matched = False
            if "*" in prefix_lower or "?" in prefix_lower:
                if (
                    fnmatch.fnmatchcase(norm_lower, prefix_lower)
                    or fnmatch.fnmatchcase(norm_lower, f"{prefix_lower}/*")
                    or fnmatch.fnmatchcase(f"/{norm_lower}", f"*/{prefix_lower}/*")
                ):
                    matched = True
            else:
                matched = (
                    norm_lower.startswith(prefix_lower + "/")
                    or norm_lower == prefix_lower
                    or f"/{prefix_lower}/" in f"/{norm_lower}"
                )
            if matched:
                if isinstance(mapped_tier, str) and mapped_tier in CANONICAL_5_TIERS:
                    t_info = CANONICAL_5_TIERS[mapped_tier]
                    return mapped_tier, t_info["gravity"], t_info["slug"], t_info["title"]

    # 2. Tier 0: Pillars, Manifests, Blueprints, Rules, Skills & Configs
    if (
        norm_lower.startswith(("context/", ".agents/rules/", ".agents/docs/", ".agents/skills/", ".agents/canons/", "agents/", "skills/"))
        or base_lower in CANONICAL_5_TIERS["0_pillars_and_manifests"]["manifest_files"]
        or base_lower.endswith((".manifest.json", ".dna.json", ".pack.json", ".security-baseline.json"))
    ):
        t0 = CANONICAL_5_TIERS["0_pillars_and_manifests"]
        return "0_pillars_and_manifests", t0["gravity"], t0["slug"], t0["title"]

    # 3. Tier 9: Verification, Tests & Evals
    if (
        any(seg in CANONICAL_5_TIERS["9_verification"]["folder_tokens"] for seg in parts[:-1])
        or base_lower.startswith(("test_", "spec_", "verify_", "audit_", "consequence_", "assertion_"))
        or base_lower.endswith(("_test.dart", "_test.py", ".test.ts", ".spec.ts", ".test.tsx", ".spec.tsx", "_test.go", ".test.js"))
        or any(s.endswith("test") for s in syms_lower)
    ):
        t9 = CANONICAL_5_TIERS["9_verification"]
        return "9_verification", t9["gravity"], t9["slug"], t9["title"]

    # 4. Tier 8: Native Bridges, MCP Servers & CLI Runtime (Platform folders match at root/workspace level, not inside submodules)
    native_root_tokens = {"android", "ios", "macos", "windows", "linux", "web"}
    cli_bridge_tokens = {"bin", "cli", "commands", "ffi", "hooks", "mcp", "bridges"}
    is_native_root = len(parts) > 1 and (
        parts[0] in native_root_tokens
        or (len(parts) > 2 and parts[0] in ("apps", "packages", "services") and parts[2] in native_root_tokens)
    )
    is_root_barrel = norm_lower in ("src/index.ts", "src/index.js", "src/main.ts", "lib/main.dart", "lib/index.ts") or base_lower in ("main.dart", "main.py", "main.rs", "main.go", "app.py")
    if (
        is_native_root
        or is_root_barrel
        or any(seg in cli_bridge_tokens for seg in parts[:-1])
        or base_lower.endswith((".mjs", ".sh", ".bash", ".bat", ".cmd"))
        or base_lower == "orion.py"
    ):
        t8 = CANONICAL_5_TIERS["8_native_and_cli"]
        return "8_native_and_cli", t8["gravity"], t8["slug"], t8["title"]

    # 5. Check Filename Stem Morphology first for Feature-First / flat directories
    stem_tier = _match_stem_tier(stem_lower)

    # Tier 1: Contracts, Schemas & Immutable Models
    is_contract_path = any(seg in CANONICAL_5_TIERS["1_contracts"]["folder_tokens"] for seg in parts[:-1])
    non_contract_folders = {"screens", "views", "controllers", "services", "commands", "apps", "batch", "daemon", "engine", "tools", "persistence", "scripts", "workers", "jobs"}
    is_contract_sym = (
        bool(syms_lower)
        and not any(seg in non_contract_folders for seg in parts[:-1])
        and any(
            any(s.endswith(st) or s == st or f"_{st}" in s for st in ("model", "dto", "entity", "schema", "contract", "dataclass", "basemodel", "freezed", "struct"))
            for s in syms_lower[:5]
        )
    )
    if is_contract_path or stem_tier == "1_contracts" or is_contract_sym:
        t1 = CANONICAL_5_TIERS["1_contracts"]
        return "1_contracts", t1["gravity"], t1["slug"], t1["title"]

    # Tier 4: State Orchestration, Notifiers & Controllers
    # NOTE: Evaluated before Tier 5 to properly classify controllers/providers/state within presentation/ or feature-first directories
    is_state_path = any(seg in CANONICAL_5_TIERS["4_state"]["folder_tokens"] for seg in parts[:-1])
    is_state_sym = any(any(st in s for st in CANONICAL_5_TIERS["4_state"]["symbol_stereotypes"]) for s in syms_lower)
    if is_state_path or stem_tier == "4_state" or is_state_sym:
        t4 = CANONICAL_5_TIERS["4_state"]
        return "4_state", t4["gravity"], t4["slug"], t4["title"]

    # Tier 5: Presentation, Screens, Widgets & Design System
    is_pres_path = any(seg in CANONICAL_5_TIERS["5_presentation"]["folder_tokens"] for seg in parts[:-1]) or norm_lower.endswith((".tsx", ".jsx", ".vue", ".svelte", ".arb"))
    is_pres_sym = any(any(_is_matching_stereotype(s, st) for st in CANONICAL_5_TIERS["5_presentation"]["symbol_stereotypes"]) for s in syms_lower)
    if is_pres_path or stem_tier == "5_presentation" or is_pres_sym:
        t5 = CANONICAL_5_TIERS["5_presentation"]
        return "5_presentation", t5["gravity"], t5["slug"], t5["title"]

    # Tier 3: Services, Repositories & Data Persistence
    is_srv_path = any(seg in CANONICAL_5_TIERS["3_services"]["folder_tokens"] for seg in parts[:-1]) or base_lower.startswith(("db.", "orion_graph.", "memory.", "capabilities."))
    is_srv_sym = any(any(st in s for st in CANONICAL_5_TIERS["3_services"]["symbol_stereotypes"]) for s in syms_lower)
    if is_srv_path or stem_tier == "3_services" or is_srv_sym:
        t3 = CANONICAL_5_TIERS["3_services"]
        return "3_services", t3["gravity"], t3["slug"], t3["title"]

    # Tier 2: Domain Logic & Use Cases
    is_dom_path = any(seg in CANONICAL_5_TIERS["2_domain"]["folder_tokens"] for seg in parts[:-1])
    is_dom_sym = any(any(st in s for st in CANONICAL_5_TIERS["2_domain"]["symbol_stereotypes"]) for s in syms_lower)
    if is_dom_path or stem_tier == "2_domain" or is_dom_sym:
        t2 = CANONICAL_5_TIERS["2_domain"]
        return "2_domain", t2["gravity"], t2["slug"], t2["title"]

    # Fallback assignment based on parent directory position
    if any(seg in ("core", "internal", "engine", "lib", "src") for seg in parts[:-1]):
        t2 = CANONICAL_5_TIERS["2_domain"]
        return "2_domain", t2["gravity"], t2["slug"], t2["title"]

    t3 = CANONICAL_5_TIERS["3_services"]
    return "3_services", t3["gravity"], t3["slug"], t3["title"]


def detect_execution_spine(root_dir: str, audit_files: List[str]) -> List[str]:
    """Identifies application boot, CLI, MCP, router & dependency injection entrypoints across workspaces."""
    spine_candidates = [
        "lib/main.dart", "lib/app.dart", "src/main.ts", "src/index.ts", "src/app.tsx",
        "src/cli/index.ts", "src/mcp/index.ts", "src/main.py", "main.py", "app.py",
        "src/index.js", "src/main.rs", "main.go", ".agents/scripts/orion.py",
        "lib/core/routing/app_router.dart", "lib/router.dart", "src/router.ts",
        "lib/core/di/injection.dart", "lib/injection.dart", "src/di.ts"
    ]
    discovered: List[str] = []
    norm_set = {f.replace("\\", "/").lower(): f for f in audit_files}
    for cand in spine_candidates:
        if cand.lower() in norm_set and norm_set[cand.lower()] not in discovered:
            discovered.append(norm_set[cand.lower()])

    # Inspect package.json 'main' and 'bin' entrypoints if present
    pkg_json_path = os.path.join(root_dir, "package.json")
    if os.path.isfile(pkg_json_path):
        try:
            with open(pkg_json_path, "r", encoding="utf-8", errors="ignore") as pf:
                pkg_data = json.load(pf)
            raw_entries: List[str] = []
            if isinstance(pkg_data.get("main"), str):
                raw_entries.append(pkg_data["main"])
            if isinstance(pkg_data.get("bin"), str):
                raw_entries.append(pkg_data["bin"])
            elif isinstance(pkg_data.get("bin"), dict):
                raw_entries.extend(v for v in pkg_data["bin"].values() if isinstance(v, str))
            for entry in raw_entries:
                clean_e = entry.lstrip("./").replace("\\", "/").lower()
                src_guess = re.sub(r'^dist/', 'src/', re.sub(r'\.js$', '.ts', clean_e))
                for cand_e in (clean_e, src_guess):
                    if cand_e in norm_set and norm_set[cand_e] not in discovered:
                        discovered.append(norm_set[cand_e])
        except Exception:
            pass

    if not discovered:
        for rel_f in audit_files:
            base = os.path.basename(rel_f).lower()
            if base in ("main.dart", "main.py", "index.ts", "app.tsx", "main.rs", "main.go", "orion.py"):
                discovered.append(rel_f)
                break
    return discovered


def detect_feature_organs(audit_files: List[str]) -> List[Dict[str, Any]]:
    """Discovers Bounded Context feature verticals (e.g. features/auth, modules/billing)."""
    organ_roots = ("features", "modules", "packages", "apps", "services", "domains")
    organs: Dict[str, Dict[str, Any]] = {}

    for f in audit_files:
        norm = f.replace("\\", "/").strip("/")
        parts = norm.split("/")
        for idx, seg in enumerate(parts[:-1]):
            if seg.lower() in organ_roots and idx + 1 < len(parts) - 1:
                organ_name = parts[idx + 1].lower()
                root_prefix = "/".join(parts[:idx + 2])
                if organ_name not in organs:
                    organs[organ_name] = {
                        "name": organ_name,
                        "root_prefix": root_prefix,
                        "files": [],
                        "detected_tiers": set()
                    }
                organs[organ_name]["files"].append(norm)
                # Assign tier
                tier_key, _, _, _ = classify_file_to_tier(norm)
                organs[organ_name]["detected_tiers"].add(tier_key)
                break

    results = []
    for o_name, info in sorted(organs.items()):
        results.append({
            "name": o_name,
            "root_prefix": info["root_prefix"],
            "file_count": len(info["files"]),
            "detected_tiers": sorted(list(info["detected_tiers"]))
        })
    return results


def check_layer_violations(
    root_dir: str,
    file_tier_map: Dict[str, str],
    sample_files: Optional[List[str]] = None,
    feature_organs: Optional[List[Dict[str, Any]]] = None
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Mechanically verifies Directed Dependency Laws, Horizontal Feature-Organ Isolation,
    and Chimera Files across Python, TypeScript/JS, Dart, Rust, Go, and Kotlin/Java.
    """
    violations: List[Dict[str, Any]] = []
    chimera_files: List[str] = []
    files_to_check = sample_files or list(file_tier_map.keys())

    import_re = re.compile(
        r'^\s*(?:'
        r'import\s+(?:type\s+)?(?:[^\'";]+?\s+from\s+)?[\'"]([^\'"]+)[\'"]|'
        r'export\s+(?:type\s+)?[^\'";]+?\s+from\s+[\'"]([^\'"]+)[\'"]|'
        r'(?:const|let|var)\s+[^=]+=\s*require\(\s*[\'"]([^\'"]+)[\'"]\s*\)|'
        r'from\s+([a-zA-Z0-9_\.]+)\s+import\b|'
        r'import\s+([a-zA-Z0-9_\.]+)|'
        r'use\s+(?:crate::)?([a-zA-Z0-9_:]+)'
        r')'
    )

    forbidden_rules = CANONICAL_DEPENDENCY_LAWS["forbidden_edges"]

    # Build lookup index for internal file resolution
    norm_tier_map: Dict[str, str] = {}
    for fp, t_key in file_tier_map.items():
        norm_fp = fp.replace("\\", "/").lower()
        norm_tier_map[norm_fp] = t_key
        no_ext = os.path.splitext(norm_fp)[0]
        norm_tier_map[no_ext] = t_key
        if no_ext.endswith("/__init__") or no_ext.endswith("/index"):
            norm_tier_map[no_ext.rsplit("/", 1)[0]] = t_key

    organ_prefixes: List[Tuple[str, str]] = []
    if feature_organs:
        for org in feature_organs:
            if org.get("root_prefix") and org.get("name"):
                organ_prefixes.append((org["root_prefix"].lower().strip("/"), org["name"]))

    for rel_f in files_to_check:
        src_tier = file_tier_map.get(rel_f)
        if not src_tier or src_tier in ("0_pillars_and_manifests", "9_verification"):
            continue

        full_p = os.path.join(root_dir, rel_f)
        try:
            with open(full_p, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read(32768)
        except OSError:
            continue

        # 1. Chimera Detection: Presentation file mixing raw SQL/HTTP/DB drivers
        norm_rel_f = rel_f.replace("\\", "/").lower()
        base_rel_f = os.path.basename(norm_rel_f)
        is_l10n_asset = norm_rel_f.startswith(("lib/l10n/", "l10n/")) or base_rel_f.startswith("app_localizations")
        if src_tier == "5_presentation" and not is_l10n_asset:
            has_raw_sql = bool(re.search(
                r'\b(?:SELECT\s+.+?\s+FROM|INSERT\s+INTO\s+\w+|UPDATE\s+\w+\s+SET|DELETE\s+FROM\s+\w+|CREATE\s+TABLE)\b',
                content, re.IGNORECASE
            ))
            has_raw_http = bool(re.search(
                r'\b(?:http\.(?:get|post|put|delete)|dio\.(?:get|post|put|delete)|fetch\(|axios\.(?:get|post|put|delete)|sqlite3\.connect|rawQuery\()\b',
                content
            ))
            if has_raw_sql or has_raw_http:
                chimera_files.append(rel_f)
        cur_dir = os.path.dirname(norm_rel_f)
        src_organ = next((o_name for o_pref, o_name in organ_prefixes if norm_rel_f.startswith(o_pref + "/")), None)

        # 2. Check import lines against Directed Dependency Laws & Organ Isolation
        for line_no, line in enumerate(content.splitlines(), 1):
            m = import_re.match(line)
            if not m:
                continue
            raw_imp = next((g for g in m.groups() if g), "")
            if not raw_imp:
                continue

            norm_imp = raw_imp.replace("\\", "/").replace("::", "/").lower()
            resolved_target_tier: Optional[str] = None
            resolved_target_path: Optional[str] = None

            if raw_imp.startswith("."):
                # Handle Python relative dots (e.g. '..services.db') vs JS/Dart relative paths ('../services/db')
                if "/" not in raw_imp and re.match(r'^\.+[a-zA-Z0-9_\.]+$', raw_imp):
                    dots = len(raw_imp) - len(raw_imp.lstrip("."))
                    tail = raw_imp.lstrip(".").replace(".", "/")
                    base_d = cur_dir
                    for _ in range(max(0, dots - 1)):
                        base_d = os.path.dirname(base_d)
                    cand_rel = f"{base_d}/{tail}".strip("/")
                else:
                    cand_rel = os.path.normpath(os.path.join(cur_dir, raw_imp)).replace("\\", "/").lower()
                cand_no_ext = re.sub(r'\.(?:js|ts|tsx|jsx|mjs|cjs|dart|py|rs|go)$', '', cand_rel)
                resolved_target_tier = norm_tier_map.get(cand_rel) or norm_tier_map.get(cand_no_ext)
                resolved_target_path = cand_no_ext
            else:
                # Check internal workspace module paths (e.g. 'core.db', 'package:app/services/api.dart', '@/services/api')
                clean_pkg = re.sub(r'^(?:package:[^/]+/|@/|~/|src/|lib/)', '', norm_imp)
                if "." in clean_pkg and "/" not in clean_pkg:
                    clean_pkg = clean_pkg.replace(".", "/")
                clean_no_ext = re.sub(r'\.(?:js|ts|tsx|jsx|mjs|cjs|dart|py|rs|go)$', '', clean_pkg)
                for prefix_cand in ("", "src/", "lib/", ".agents/scripts/"):
                    probe = f"{prefix_cand}{clean_no_ext}".strip("/")
                    if probe in norm_tier_map:
                        resolved_target_tier = norm_tier_map[probe]
                        resolved_target_path = probe
                        break

            # Fallback token matching only for internal-looking paths (avoid false positives on external packages)
            if not resolved_target_tier and (raw_imp.startswith((".", "@/", "~/", "src/", "lib/", "package:")) or "/" in norm_imp):
                for rule in forbidden_rules:
                    if rule["from_tier"] == src_tier:
                        for target_tier in rule["to_tier"]:
                            t_info = CANONICAL_5_TIERS.get(target_tier, {})
                            if any(f"/{tok}/" in f"/{norm_imp}/" or norm_imp.endswith(f"/{tok}") for tok in t_info.get("folder_tokens", [])):
                                resolved_target_tier = target_tier
                                break

            if resolved_target_tier:
                for rule in forbidden_rules:
                    if rule["from_tier"] == src_tier and resolved_target_tier in rule["to_tier"]:
                        violations.append({
                            "file": rel_f,
                            "line": line_no,
                            "source_tier": src_tier,
                            "target_tier": resolved_target_tier,
                            "import": raw_imp,
                            "import_target": raw_imp,
                            "reason": rule["reason"]
                        })
                        break

            # Check Horizontal Feature-Organ Isolation (Organ A importing Organ B's internal state/presentation/services)
            if src_organ and resolved_target_path and resolved_target_tier in ("3_services", "4_state", "5_presentation"):
                target_organ = next((o_name for o_pref, o_name in organ_prefixes if resolved_target_path.startswith(o_pref + "/")), None)
                if target_organ and target_organ != src_organ:
                    violations.append({
                        "file": rel_f,
                        "line": line_no,
                        "source_tier": f"{src_tier} (organ:{src_organ})",
                        "target_tier": f"{resolved_target_tier} (organ:{target_organ})",
                        "import": raw_imp,
                        "import_target": raw_imp,
                        "reason": f"Feature Organ '{src_organ}' must not directly import internal '{resolved_target_tier}' of sibling Organ '{target_organ}'; communicate via '1_contracts' or '2_domain'."
                    })

    return violations, chimera_files


def extract_local_imports(file_path: str, content: Optional[str] = None) -> List[Tuple[int, str]]:
    """
    Extracts import lines and imported spec strings from Dart, TypeScript/JavaScript, and Python files.
    Returns: List of (line_number, raw_import_target).
    """
    if content is None:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(65536)
        except OSError:
            return []

    results: List[Tuple[int, str]] = []
    import_re = re.compile(
        r'^\s*(?:'
        r'import\s+(?:type\s+)?(?:[^\'";]+?\s+from\s+)?[\'"]([^\'"]+)[\'"]|'
        r'export\s+(?:type\s+)?[^\'";]+?\s+from\s+[\'"]([^\'"]+)[\'"]|'
        r'(?:const|let|var)\s+[^=]+=\s*require\(\s*[\'"]([^\'"]+)[\'"]\s*\)|'
        r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)|'
        r'from\s+([a-zA-Z0-9_\.]+)\s+import\b|'
        r'import\s+([a-zA-Z0-9_\.]+)|'
        r'use\s+(?:crate::)?([a-zA-Z0-9_:]+)'
        r')'
    )

    for line_no, line in enumerate(content.splitlines(), 1):
        m = import_re.match(line)
        if not m:
            continue
        raw_imp = next((g for g in m.groups() if g), "")
        if raw_imp:
            results.append((line_no, raw_imp.strip()))

    return results


def lint_file_dependencies(
    file_path: str,
    content: Optional[str] = None,
    root_dir: Optional[str] = None,
    epigenetic_aliases: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Active real-time JIT Dependency Linter.
    Classifies file into source tier, extracts local imports, maps them to target tiers,
    and returns detected violations against CANONICAL_DEPENDENCY_LAWS['forbidden_edges'].
    """
    abs_file = os.path.abspath(file_path)
    if not root_dir:
        probe = os.path.dirname(abs_file)
        root_dir = probe
        for _ in range(8):
            if any(os.path.exists(os.path.join(probe, marker)) for marker in (".agents", ".git", "pubspec.yaml", "package.json", "pyproject.toml")):
                root_dir = probe
                break
            parent = os.path.dirname(probe)
            if parent == probe:
                break
            probe = parent

    abs_root = os.path.abspath(root_dir)
    rel_path = os.path.relpath(abs_file, abs_root).replace("\\", "/")

    # Classify source tier
    from_tier, _, _, _ = classify_file_to_tier(rel_path, epigenetic_aliases=epigenetic_aliases)
    if from_tier in ("0_pillars_and_manifests", "9_verification", "8_native_and_cli"):
        return []
    base_lower = os.path.basename(rel_path.lower())
    if rel_path.lower().startswith(("lib/l10n/", "l10n/")) or base_lower.startswith("app_localizations"):
        return []

    if content is None:
        try:
            with open(abs_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(65536)
        except OSError:
            return []

    cur_dir = os.path.dirname(rel_path).replace("\\", "/")
    imports = extract_local_imports(abs_file, content=content)
    forbidden_rules = CANONICAL_DEPENDENCY_LAWS["forbidden_edges"]
    violations: List[Dict[str, Any]] = []

    ext_prefixes = ("flutter/", "flutter_test/", "react", "vue", "angular", "node:", "@angular", "dart:")
    node_builtins = {"fs", "path", "os", "crypto", "util", "events", "stream", "http", "https", "child_process", "buffer", "url", "assert", "cluster", "dns", "readline", "zlib", "net", "tls"}

    for line_no, raw_imp in imports:
        norm_imp = raw_imp.replace("\\", "/").replace("::", "/")

        if any(norm_imp.startswith(p) for p in ext_prefixes):
            continue

        root_token = norm_imp.split("/")[0].split(".")[0].lower()
        if hasattr(sys, "stdlib_module_names") and root_token in sys.stdlib_module_names:
            continue
        if root_token in node_builtins:
            continue

        resolved_target_rel: Optional[str] = None

        if raw_imp.startswith("."):
            if "/" not in raw_imp and re.match(r'^\.+[a-zA-Z0-9_\.]+$', raw_imp):
                dots = len(raw_imp) - len(raw_imp.lstrip("."))
                tail = raw_imp.lstrip(".").replace(".", "/")
                base_d = cur_dir
                for _ in range(max(0, dots - 1)):
                    base_d = os.path.dirname(base_d)
                resolved_target_rel = f"{base_d}/{tail}".strip("/")
            else:
                resolved_target_rel = os.path.normpath(os.path.join(cur_dir, raw_imp)).replace("\\", "/")
        elif raw_imp.startswith(("@/", "~/", "src/", "lib/")):
            resolved_target_rel = re.sub(r'^[@~]/', 'src/', norm_imp)
        elif raw_imp.startswith("package:"):
            pkg_part = norm_imp.removeprefix("package:").split("/")[0]
            if pkg_part in ("flutter", "flutter_test", "flutter_localizations", "intl"):
                continue
            project_pkg = None
            pubspec_p = os.path.join(abs_root, "pubspec.yaml")
            if os.path.exists(pubspec_p):
                try:
                    with open(pubspec_p, "r", encoding="utf-8", errors="ignore") as pf:
                        for pl in pf:
                            if pl.startswith("name:"):
                                project_pkg = pl.split(":", 1)[1].strip()
                                break
                except OSError:
                    pass
            if project_pkg and pkg_part != project_pkg:
                continue
            pkg_tail = norm_imp.split("/", 1)[1] if "/" in norm_imp else ""
            if pkg_tail:
                resolved_target_rel = f"lib/{pkg_tail}"
        elif "." in norm_imp and "/" not in norm_imp:
            resolved_target_rel = norm_imp.replace(".", "/")

        to_tier: Optional[str] = None
        if resolved_target_rel:
            to_tier, _, _, _ = classify_file_to_tier(resolved_target_rel, epigenetic_aliases=epigenetic_aliases)

        if not to_tier and (raw_imp.startswith((".", "@/", "~/", "src/", "lib/", "package:")) or "/" in norm_imp):
            for rule in forbidden_rules:
                if rule["from_tier"] == from_tier:
                    for target_tier in rule["to_tier"]:
                        t_info = CANONICAL_5_TIERS.get(target_tier, {})
                        if any(f"/{tok}/" in f"/{norm_imp}/" or norm_imp.endswith(f"/{tok}") or f"/{tok}." in norm_imp for tok in t_info.get("folder_tokens", [])):
                            to_tier = target_tier
                            break

        if to_tier:
            for rule in forbidden_rules:
                if rule["from_tier"] == from_tier and to_tier in rule["to_tier"]:
                    violations.append({
                        "file": rel_path,
                        "line": line_no,
                        "from_tier": from_tier,
                        "to_tier": to_tier,
                        "imported_path": raw_imp,
                        "reason": rule["reason"]
                    })
                    break

    # Chimera Detection: Presentation mixing raw SQL/HTTP drivers directly in UI
    if from_tier == "5_presentation":
        has_raw_sql = bool(re.search(
            r'\b(?:SELECT\s+.+?\s+FROM|INSERT\s+INTO\s+\w+|UPDATE\s+\w+\s+SET|DELETE\s+FROM\s+\w+|CREATE\s+TABLE)\b',
            content, re.IGNORECASE
        ))
        has_raw_http = bool(re.search(
            r'\b(?:http\.(?:get|post|put|delete)|dio\.(?:get|post|put|delete)|fetch\(|axios\.(?:get|post|put|delete)|sqlite3\.connect|rawQuery\()\b',
            content
        ))
        if has_raw_sql or has_raw_http:
            violations.append({
                "file": rel_path,
                "line": 1,
                "from_tier": "5_presentation",
                "to_tier": "3_services",
                "imported_path": "[CHIMERA: RAW DRIVER IN UI]",
                "reason": "Presentation screens/widgets must not mix raw SQL/HTTP drivers directly in UI code."
            })

    return violations


def lint_dependencies_path(
    target_path: str,
    root_dir: Optional[str] = None,
    epigenetic_aliases: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Lints dependencies for a single file or recursively for an entire directory."""
    abs_target = os.path.abspath(target_path)
    if os.path.isfile(abs_target):
        return lint_file_dependencies(abs_target, root_dir=root_dir, epigenetic_aliases=epigenetic_aliases)

    all_violations: List[Dict[str, Any]] = []
    if os.path.isdir(abs_target):
        for root, dirs, files in os.walk(abs_target):
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".")
                and d not in (
                    "node_modules", ".dart_tool", "build", "dist", "target", "__pycache__",
                    "cache", "venv", "env", "site-packages", ".scratch", "scratch", ".orion", ".git"
                )
            ]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".dart", ".ts", ".tsx", ".js", ".jsx", ".py"):
                    fp = os.path.join(root, f)
                    violations = lint_file_dependencies(fp, root_dir=root_dir, epigenetic_aliases=epigenetic_aliases)
                    all_violations.extend(violations)
    return all_violations


def discover_epigenetic_aliases(root_dir: str, files: List[str], existing_aliases: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Dynamically discovers brownfield epigenetic aliases by analyzing the dominant file morphology
    and AST symbol stereotypes inside each directory, combined with standard legacy folder mappings.
    """
    abs_root = os.path.abspath(root_dir)
    discovered: Dict[str, str] = normalize_epigenetic_aliases(existing_aliases or {})

    # 1. Baseline legacy mappings (Multi-platform & multi-paradigm: Mobile, Web, Backend, Daemon & Quantitative)
    baseline_mappings = [
        # Standard Clean / Frontend / Mobile Mappings
        ("src/api", "3_services"), ("src/services", "3_services"), ("src/repositories", "3_services"),
        ("src/network", "3_services"), ("lib/network", "3_services"), ("lib/services", "3_services"),
        ("lib/data", "3_services"), ("src/views", "5_presentation"), ("src/pages", "5_presentation"),
        ("src/components", "5_presentation"), ("src/ui", "5_presentation"), ("lib/ui", "5_presentation"),
        ("lib/screens", "5_presentation"), ("lib/widgets", "5_presentation"), ("src/store", "4_state"),
        ("src/state", "4_state"), ("lib/controllers", "4_state"), ("lib/providers", "4_state"),
        ("lib/bloc", "4_state"), ("src/types", "1_contracts"), ("src/schemas", "1_contracts"),
        ("src/models", "1_contracts"), ("lib/models", "1_contracts"), ("lib/contracts", "1_contracts"),
        ("src/domain", "2_domain"), ("lib/domain", "2_domain"),
        # Backend / Python / Daemon / Pipeline / CLI Orchestrators
        ("src/apps", "4_state"), ("apps", "4_state"), ("src/daemons", "4_state"),
        ("src/workers", "4_state"), ("src/jobs", "4_state"), ("src/pipelines", "4_state"),
        ("src/runners", "4_state"), ("hermes_cli", "4_state"),
        # Core Services, Engines, Persistence & Tools
        ("src/engine", "3_services"), ("src/persistence", "3_services"), ("src/tools", "3_services"),
        ("src/brain", "3_services"), ("src/adapters", "3_services"), ("src/infra", "3_services"),
        ("src/infrastructure", "3_services"), ("src/storage", "3_services"), ("src/db", "3_services"),
        ("scripts", "3_services"), ("plugins", "3_services"),
        # Pure Domain, Math, Indicators & Rules
        ("src/core", "2_domain"), ("src/math", "2_domain"), ("src/indicators", "2_domain"),
        ("src/strategies", "2_domain"), ("src/rules", "2_domain"),
    ]
    for rel_folder, target_tier in baseline_mappings:
        if os.path.isdir(os.path.join(abs_root, rel_folder)) and rel_folder not in discovered:
            discovered[rel_folder] = target_tier

    # 1.5. Feature-First modular subtrees auto-detection (lib/features/* and src/features/*)
    for root_prefix in ("lib/features", "src/features", "features"):
        full_prefix = os.path.join(abs_root, root_prefix)
        if os.path.isdir(full_prefix):
            try:
                for feature_name in os.listdir(full_prefix):
                    feat_dir = os.path.join(full_prefix, feature_name)
                    if not os.path.isdir(feat_dir) or feature_name.startswith("."):
                        continue
                    feat_rel = f"{root_prefix}/{feature_name}"
                    feature_sub_mappings = [
                        (f"{feat_rel}/data", "3_services"),
                        (f"{feat_rel}/data/repositories", "3_services"),
                        (f"{feat_rel}/data/models", "1_contracts"),
                        (f"{feat_rel}/domain", "2_domain"),
                        (f"{feat_rel}/domain/models", "1_contracts"),
                        (f"{feat_rel}/domain/usecases", "2_domain"),
                        (f"{feat_rel}/presentation/controllers", "4_state"),
                        (f"{feat_rel}/presentation/providers", "4_state"),
                        (f"{feat_rel}/presentation/state", "4_state"),
                        (f"{feat_rel}/state", "4_state"),
                        (f"{feat_rel}/controllers", "4_state"),
                        (f"{feat_rel}/presentation/screens", "5_presentation"),
                        (f"{feat_rel}/presentation/widgets", "5_presentation"),
                        (f"{feat_rel}/presentation", "5_presentation"),
                    ]
                    for sub_rel, target_tier in feature_sub_mappings:
                        if os.path.isdir(os.path.join(abs_root, sub_rel)) and sub_rel not in discovered:
                            discovered[sub_rel] = target_tier
            except OSError:
                pass

    # 2. Dynamic AST & Stem Morphology Clustering across non-standard brownfield directories
    dir_votes: Dict[str, Counter] = defaultdict(Counter)
    for rel_f in files:
        norm = rel_f.replace("\\", "/").strip("/")
        parts = norm.split("/")
        if len(parts) < 2 or parts[0].startswith(".") or parts[0] in ("context", "docs", "test", "tests"):
            continue
        parent_dir = "/".join(parts[:-1][:3])
        if parent_dir in discovered:
            continue
        stem_lower = os.path.splitext(parts[-1].lower())[0]
        inferred = _match_stem_tier(stem_lower)
        if inferred:
            dir_votes[parent_dir][inferred] += 1

    for folder_pref, counts in dir_votes.items():
        total_voted = sum(counts.values())
        if total_voted >= 2:
            top_tier, top_cnt = counts.most_common(1)[0]
            if (top_cnt / total_voted) >= 0.65:
                discovered[folder_pref] = top_tier

    return discovered


def discover_context_epigenetic_map(root_dir: str) -> Tuple[str, Dict[str, str]]:
    """
    Analyzes the context/ directory structure to detect its topology and generate
    semantic context_aliases for non-canonical files or custom brownfield layouts.
    Returns (topology, context_aliases).
    Topologies:
    - 'code_collision_shield': Source code (.tsx, .ts, .py, .go, .dart, .rs, .kt, .java) found inside context/
    - 'seed_7': Minimal 7-file seed topology
    - 'adaptive_25': 25-File Golden Ratio topology
    - 'legacy_82': 82-file legacy SaaS topology
    - 'epigenetic_custom': Non-standard custom brownfield context topology
    """
    abs_root = os.path.abspath(root_dir)
    context_dir = os.path.join(abs_root, "context")
    context_aliases: Dict[str, str] = {}

    if not os.path.isdir(context_dir):
        return "seed_7", context_aliases

    # Guard 0: Code Collision Shield
    code_extensions = {".ts", ".tsx", ".js", ".jsx", ".py", ".dart", ".go", ".rs", ".kt", ".java", ".cpp", ".c"}
    for root, _, files in os.walk(context_dir):
        if any(os.path.splitext(f)[1].lower() in code_extensions for f in files):
            return "code_collision_shield", context_aliases

    facet_keyword_map = [
        ("vision", "VISION.md"),
        ("blueprint", "00_Strategy/BLUEPRINT.md"),
        ("memory", "00_Strategy/MEMORY.md"),
        ("persona", "00_Strategy/PERSONAS_AND_MARKET.md"),
        ("market", "00_Strategy/PERSONAS_AND_MARKET.md"),
        ("acquisition", "00_Strategy/ACQUISITION_AND_GROWTH.md"),
        ("growth", "00_Strategy/ACQUISITION_AND_GROWTH.md"),
        ("monetization", "00_Strategy/MONETIZATION_AND_PRICING.md"),
        ("pricing", "00_Strategy/MONETIZATION_AND_PRICING.md"),
        ("retention", "00_Strategy/RETENTION_AND_LEGAL.md"),
        ("legal", "00_Strategy/RETENTION_AND_LEGAL.md"),
        ("roadmap", "01_Product/ROADMAP.md"),
        ("prd", "01_Product/PRD_CORE_FEATURES.md"),
        ("feature", "01_Product/PRD_CORE_FEATURES.md"),
        ("journey", "01_Product/USER_JOURNEYS_AND_FLOWS.md"),
        ("flow", "01_Product/USER_JOURNEYS_AND_FLOWS.md"),
        ("analytics", "01_Product/ANALYTICS_AND_METRICS.md"),
        ("metric", "01_Product/ANALYTICS_AND_METRICS.md"),
        ("integration", "01_Product/INTEGRATIONS_AND_WEBHOOKS.md"),
        ("webhook", "01_Product/INTEGRATIONS_AND_WEBHOOKS.md"),
        ("feedback", "01_Product/FEEDBACK_AND_BACKLOG.md"),
        ("backlog", "01_Product/FEEDBACK_AND_BACKLOG.md"),
        ("style_guide", "02_Creative/STYLE_GUIDE.md"),
        ("style", "02_Creative/STYLE_GUIDE.md"),
        ("component", "02_Creative/UI_COMPONENTS_AND_PATTERNS.md"),
        ("ux", "02_Creative/UX_AND_ACCESSIBILITY.md"),
        ("accessibility", "02_Creative/UX_AND_ACCESSIBILITY.md"),
        ("brand", "02_Creative/BRAND_VOICE_AND_COPY.md"),
        ("copy", "02_Creative/BRAND_VOICE_AND_COPY.md"),
        ("asset", "02_Creative/VISUAL_ASSETS_AND_MEDIA.md"),
        ("media", "02_Creative/VISUAL_ASSETS_AND_MEDIA.md"),
        ("architecture", "03_Tech/ARCHITECTURE.md"),
        ("database", "03_Tech/DATABASE_AND_STORAGE.md"),
        ("storage", "03_Tech/DATABASE_AND_STORAGE.md"),
        ("api", "03_Tech/API_AND_CONTRACTS.md"),
        ("contract", "03_Tech/API_AND_CONTRACTS.md"),
        ("state", "03_Tech/STATE_AND_DOMAIN_LOGIC.md"),
        ("logic", "03_Tech/STATE_AND_DOMAIN_LOGIC.md"),
        ("security", "03_Tech/SECURITY_AND_AUTH.md"),
        ("auth", "03_Tech/SECURITY_AND_AUTH.md"),
        ("infra", "03_Tech/INFRA_AND_DEVOPS.md"),
        ("devops", "03_Tech/INFRA_AND_DEVOPS.md"),
    ]

    all_context_files = []
    for root, _, files in os.walk(context_dir):
        for f in files:
            if f.endswith((".md", ".txt")):
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, abs_root).replace("\\", "/")
                all_context_files.append(rel_p)

    has_legacy_prefixes = False
    for rel_p in all_context_files:
        filename = os.path.basename(rel_p)
        if any(filename.startswith(pfx) for pfx in ("Acq_", "Conv_", "Rev_", "Ret_", "Plan_", "Idea_", "Data_", "Dev_", "Infra_", "Design_")):
            has_legacy_prefixes = True
            break

    for rel_p in all_context_files:
        fn_lower = os.path.basename(rel_p).lower()
        mapped_target = None
        for kw, target in facet_keyword_map:
            if kw in fn_lower:
                mapped_target = target
                break
        if mapped_target:
            context_aliases[rel_p] = mapped_target

    if len(all_context_files) <= 7 and not has_legacy_prefixes:
        topology = "seed_7"
    elif has_legacy_prefixes or len(all_context_files) > 25:
        topology = "legacy_82"
    elif len(context_aliases) > 0 and len(context_aliases) != len(all_context_files):
        topology = "epigenetic_custom"
    else:
        topology = "adaptive_25"

    return topology, context_aliases


def sequence_project_dna(
    root_dir: str,
    audit_files: Optional[List[str]] = None,
    force_universal: bool = False,
    allow_foundation: bool = False
) -> Optional[ProjectDNA]:
    """
    Tier-0 Deterministic Living DNA Sequencer.
    Works for Greenfield, Brownfield, Reverse-Engineered, and Untouched External repositories.
    Zero LLM required.
    """
    if force_universal or ((is_foundation_root(root_dir) or is_foundation_agents(root_dir)) and not allow_foundation):
        return None

    abs_root = os.path.abspath(root_dir)

    # 1. Discover or synthesize basic manifests
    dna_path = os.path.join(abs_root, ".agents", ".dna.json")
    manifest_path = os.path.join(abs_root, ".agents", ".project_manifest.json")
    
    stored_dna: Dict[str, Any] = {}
    if os.path.isfile(dna_path):
        try:
            with open(dna_path, "r", encoding="utf-8", errors="ignore") as fh:
                stored_dna = json.load(fh)
        except Exception as _e:
            _log_telemetry(_e, "sequence_project_dna:read_dna")

    stored_manifest: Dict[str, Any] = {}
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8", errors="ignore") as fh:
                stored_manifest = json.load(fh)
        except Exception as _e:
            _log_telemetry(_e, "sequence_project_dna:read_manifest")

    # Has explicit .agents DNA presence?
    has_explicit_dna = bool(stored_dna or stored_manifest or os.path.isdir(os.path.join(abs_root, "context")))

    # 2. Collect scan files if not provided
    files = list(audit_files) if audit_files is not None else []
    if not files:
        for r, dirs, filenames in os.walk(abs_root):
            # prune noise
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".")
                and d not in (
                    "node_modules", "build", "dist", "target", "__pycache__", ".dart_tool",
                    "cache", "venv", "env", "site-packages", ".scratch", "scratch", ".orion", ".git"
                )
            ]
            for fn in filenames:
                rel = os.path.relpath(os.path.join(r, fn), abs_root).replace("\\", "/")
                files.append(rel)

    # 3. Detect Framework & Language
    stacks: List[str] = []
    pkg_fw = "node"
    pkg_json_p = os.path.join(abs_root, "package.json")
    if os.path.isfile(pkg_json_p):
        try:
            with open(pkg_json_p, "r", encoding="utf-8", errors="ignore") as pf:
                pdata = json.load(pf)
            deps = {**pdata.get("dependencies", {}), **pdata.get("devDependencies", {})}
            if "next" in deps or "react" in deps:
                pkg_fw = "react"
        except Exception:
            pass

    manifest_markers = [
        ("pubspec.yaml", "Flutter/Dart", "flutter", "dart"),
        ("package.json", "TypeScript/Node.js", pkg_fw, "typescript" if os.path.isfile(os.path.join(abs_root, "tsconfig.json")) else "javascript"),
        ("tsconfig.json", "TypeScript", pkg_fw, "typescript"),
        ("Cargo.toml", "Rust", "rust", "rust"),
        ("go.mod", "Go", "go", "go"),
        ("pyproject.toml", "Python", "python", "python"),
        ("requirements.txt", "Python", "python", "python"),
        ("pom.xml", "Java/Maven", "java", "java"),
        ("build.gradle.kts", "Kotlin/Gradle", "kotlin", "kotlin"),
        ("build.gradle", "Android/Gradle", "android", "kotlin"),
    ]
    detected_fw = (
        stored_dna.get("primary_framework")
        or stored_dna.get("framework")
        or stored_dna.get("ecosystem")
        or stored_manifest.get("framework")
        or "generic"
    )
    detected_lang = (
        stored_dna.get("primary_language")
        or stored_dna.get("language")
        or stored_manifest.get("language")
        or ("dart" if detected_fw == "flutter" else "generic")
    )

    for m_file, stack_lbl, fw, lang in manifest_markers:
        if os.path.isfile(os.path.join(abs_root, m_file)):
            if stack_lbl not in stacks:
                stacks.append(stack_lbl)
            if detected_fw == "generic":
                detected_fw = fw
                detected_lang = lang

    # 4. Detect Active vs Dormant Native Roots
    active_native: List[str] = []
    dormant_roots: List[str] = []

    android_dir = os.path.join(abs_root, "android")
    if os.path.isdir(android_dir):
        custom_android = sum(
            1 for r, _, fl in os.walk(android_dir)
            for f in fl if f.endswith((".kt", ".java", ".c", ".cpp")) and not f.startswith("GeneratedPluginRegistrant")
        )
        if custom_android >= 2:
            active_native.append(f"android ({custom_android} files)")
        else:
            dormant_roots.append("android")

    ios_dir = os.path.join(abs_root, "ios")
    if os.path.isdir(ios_dir):
        stock_ios = {
            "appdelegate.swift", "scenedelegate.swift", "generatedpluginregistrant.h",
            "generatedpluginregistrant.m", "runner-bridging-header.h", "runnertests.swift"
        }
        custom_ios = sum(
            1 for r, _, fl in os.walk(ios_dir)
            for f in fl if f.endswith((".swift", ".m", ".mm", ".c", ".cpp")) and f.lower() not in stock_ios
        )
        if custom_ios > 0:
            active_native.append(f"ios ({custom_ios} files)")
        else:
            dormant_roots.append("ios")

    for plat in ("windows", "macos", "linux", "web"):
        plat_dir = os.path.join(abs_root, plat)
        if os.path.isdir(plat_dir) and "Flutter/Dart" in stacks:
            dormant_roots.append(plat)

    archetype = f"Multi-Stack Workspace ({', '.join(stacks[:3])})" if stacks else "Software Repository"

    # 5. Extract Lean Pillars, Foundational Vision & Design Contract
    pillars: Dict[str, str] = {}
    pillar_candidates = {
        "vision": "context/VISION.md",
        "strategy": "context/00_Strategy/BLUEPRINT.md",
        "product": "context/01_Product/ROADMAP.md",
        "creative": "context/02_Creative/STYLE_GUIDE.md",
        "tech": "context/03_Tech/ARCHITECTURE.md",
        "design_contract": "DESIGN.md"
    }
    for p_key, p_path in pillar_candidates.items():
        if os.path.isfile(os.path.join(abs_root, p_path)):
            pillars[p_key] = p_path

    vision_path = pillars.get("vision") or ("context/VISION.md" if os.path.isfile(os.path.join(abs_root, "context/VISION.md")) else None)
    blueprint_path = pillars.get("tech") or pillars.get("strategy") or ("ARCHITECTURE.md" if os.path.isfile(os.path.join(abs_root, "ARCHITECTURE.md")) else None)

    # 6. Epigenetic Aliases from Stored DNA & Dynamic Context Topology
    raw_aliases = stored_dna.get("mutation_ledger", {}).get("epigenetic_aliases", {}) or stored_dna.get("epigenetic_aliases", {})
    epigenetic_aliases = discover_epigenetic_aliases(abs_root, files, existing_aliases=raw_aliases)
    context_topology, discovered_context_aliases = discover_context_epigenetic_map(abs_root)
    stored_context_aliases = stored_dna.get("context_aliases", {}) or {}
    if discovered_context_aliases:
        stored_context_aliases.update(discovered_context_aliases)

    # 7. Classify all files to 5-Tier Strata (enriched with cached AST symbols when available)
    file_tier_map: Dict[str, str] = {}
    extract_fn = None
    try:
        from core.scanner import extract_file_symbols as _ext_syms
        extract_fn = _ext_syms
    except Exception:
        pass
    for rel_f in files:
        f_syms: Optional[List[str]] = None
        if extract_fn and len(files) <= 500:
            try:
                defs, _ = extract_fn(os.path.join(abs_root, rel_f))
                f_syms = list(defs.keys())
            except Exception:
                f_syms = None
        tier_key, _, _, _ = classify_file_to_tier(rel_f, symbols=f_syms, epigenetic_aliases=epigenetic_aliases)
        file_tier_map[rel_f] = tier_key

    # 8. Detect Feature Organs & Execution Spine
    organs = detect_feature_organs(files)
    spine = detect_execution_spine(abs_root, files)

    # 9. Invariants Synthesis
    has_ui = detected_fw in ("flutter", "react", "vue", "svelte", "nextjs", "angular") or sum(
        1 for t in file_tier_map.values() if t == "5_presentation"
    ) >= 3
    # Dynamic synthesis ensures non-UI / headless / backend projects don't carry stale UI invariants
    invariants = _synthesize_invariants_for_stack(detected_fw, has_ui=has_ui)

    # Preserve custom project-specific invariants from .dna.json
    custom_invs = stored_dna.get("custom_invariants") or stored_dna.get("invariants") or []
    if isinstance(custom_invs, list):
        for ci in custom_invs:
            if isinstance(ci, str):
                ci_clean = ci.strip()
                if ci_clean and not ci_clean.startswith("[SCAL_ADVISORY]") and ci_clean not in invariants:
                    invariants.append(ci_clean)

    # Ingest real invariants and anti-vision statements from VISION.md
    if vision_path:
        full_v_path = vision_path if os.path.isabs(vision_path) else os.path.join(abs_root, vision_path)
        for vi in _extract_vision_invariants(full_v_path):
            if vi not in invariants:
                invariants.append(vi)

    # Polyglot Invariant Guard & Test Suite Evaluation (SCAL Readiness)
    verification_count = sum(1 for t in file_tier_map.values() if t == "9_verification")
    has_test_suite = verification_count > 0 or any(
        f.lower().endswith(("_test.py", "_spec.ts", ".test.ts", ".test.tsx", "_test.dart", "_test.go", "test.rs", "test.kt"))
        for f in files
    )
    if not has_test_suite:
        invariants.append(
            "[SCAL_ADVISORY]: Detected domain/service modules with incomplete verification suites. "
            "Authoring unit tests + boundary invariant guards will enable zero-cost local SLM and Cloud BUDGET self-healing."
        )

    # 10. Check Layer Violations & Chimera Files
    violations, chimeras = check_layer_violations(abs_root, file_tier_map, sample_files=files[:300], feature_organs=organs)

    # Compute DNA compliance score (100 minus penalty for violations and chimeras)
    penalty = (len(violations) * 3) + (len(chimeras) * 5)
    compliance_score = max(20, 100 - penalty)

    # DNA state determination
    if stored_dna.get("dna_state"):
        dna_state = stored_dna["dna_state"]
    elif stored_dna.get("origin") == "flutterin":
        dna_state = "BORN_FROM_REVERSE"
    elif has_explicit_dna:
        dna_state = "BORN"
    else:
        dna_state = "SYNTHESIZED"

    # Multi-workspace / Monorepo discovery
    workspaces = [{"path": ".", "framework": detected_fw, "language": detected_lang, "role": "primary_app"}]
    for mono_dir in ("apps", "packages", "services", "modules", "tools", "plugins"):
        full_mono = os.path.join(abs_root, mono_dir)
        if os.path.isdir(full_mono):
            for sub_d in sorted(os.listdir(full_mono)):
                sub_p = os.path.join(full_mono, sub_d)
                if os.path.isdir(sub_p) and not sub_d.startswith("."):
                    sub_fw = "node" if os.path.isfile(os.path.join(sub_p, "package.json")) else ("flutter" if os.path.isfile(os.path.join(sub_p, "pubspec.yaml")) else "generic")
                    sub_lang = "typescript" if sub_fw == "node" else ("dart" if sub_fw == "flutter" else "generic")
                    workspaces.append({
                        "path": f"{mono_dir}/{sub_d}",
                        "framework": sub_fw,
                        "language": sub_lang,
                        "role": "workspace_module"
                    })

    # Auto-persist synchronized DNA state to .agents/.dna.json when it exists
    if os.path.isfile(dna_path):
        try:
            changed = False
            if stored_dna.get("invariants") != invariants:
                stored_dna["invariants"] = invariants
                changed = True
            if stored_dna.get("dna_compliance_score") != compliance_score:
                stored_dna["dna_compliance_score"] = compliance_score
                changed = True
            clean_viols = violations[:15]
            if stored_dna.get("layer_violations") != clean_viols:
                stored_dna["layer_violations"] = clean_viols
                changed = True
            clean_chims = chimeras[:15]
            if stored_dna.get("chimera_files") != clean_chims:
                stored_dna["chimera_files"] = clean_chims
                changed = True
            if epigenetic_aliases and stored_dna.get("epigenetic_aliases") != epigenetic_aliases:
                stored_dna["epigenetic_aliases"] = epigenetic_aliases
                changed = True
            if stored_dna.get("dna_state") != dna_state:
                stored_dna["dna_state"] = dna_state
                changed = True
            if changed:
                if "mutation_ledger" not in stored_dna or not isinstance(stored_dna["mutation_ledger"], dict):
                    stored_dna["mutation_ledger"] = {}
                stored_dna["mutation_ledger"]["dna_compliance_score"] = compliance_score
                stored_dna["mutation_ledger"]["layer_violations"] = clean_viols
                stored_dna["mutation_ledger"]["epigenetic_aliases"] = epigenetic_aliases
                atomic_write_text(dna_path, json.dumps(stored_dna, indent=2))
        except Exception as _e:
            _log_telemetry(_e, "sequence_project_dna:sync_dna_state")

    return ProjectDNA(
        is_dna_app=has_explicit_dna,
        archetype=archetype,
        version="0.0.1",
        blueprint_path=blueprint_path,
        stacks=stacks,
        active_native_roots=active_native,
        dormant_roots=dormant_roots,
        verified_gates="Strict Host Isolation | Polyglot AST Radar | Living Architectural DNA",
        schema_version="0.0.1",
        dna_state=dna_state,
        origin=stored_dna.get("origin", "foundation_init" if has_explicit_dna else "virtual_sequencer"),
        primary_framework=detected_fw,
        primary_language=detected_lang,
        vision_path=vision_path,
        context_topology=context_topology,
        context_aliases=stored_context_aliases,
        workspaces=workspaces,
        pillars=pillars,
        tiers=CANONICAL_5_TIERS,
        feature_organs=organs,
        execution_spine=spine,
        invariants=invariants,
        layer_violations=violations,
        chimera_files=chimeras,
        epigenetic_aliases=epigenetic_aliases,
        dna_compliance_score=compliance_score,
        file_tier_map=file_tier_map
    )


def _extract_vision_invariants(vision_path: str) -> List[str]:
    """Extracts populated architectural invariants and anti-vision statements from VISION.md."""
    if not vision_path or not os.path.isfile(vision_path):
        return []
    try:
        with open(vision_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []

    extracted: List[str] = []
    sections = re.split(r"(?m)^##\s+", content)
    for sec in sections:
        sec_str = sec.strip()
        sec_lower = sec_str.split("\n", 1)[0].lower() if sec_str else ""
        if any(k in sec_lower for k in ("invariant", "anti-vision", "non-goal", "guardrail")):
            for line in sec_str.splitlines()[1:]:
                clean_l = line.strip()
                if not clean_l or clean_l.startswith("#"):
                    continue
                m_bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", clean_l)
                if m_bullet:
                    val = m_bullet.group(1).strip()
                    if "[Invariant" in val or "[X]" in val or "[Y]" in val or "[Z]" in val or "e.g." in val:
                        continue
                    if len(val) >= 10 and val not in extracted:
                        extracted.append(val)
    return extracted


def _synthesize_invariants_for_stack(framework: str, has_ui: bool) -> List[str]:
    """Synthesizes domain-accurate architectural invariants based on whether the project has UI or is headless/backend."""
    if has_ui:
        invariants = [
            "Unidirectional Data Flow (UI -> State Notifier -> Domain/Service -> Immutable Model)",
            "5-State Visual Coverage (Loading, Empty, Success, Error, Shimmer)",
            "Zero raw DB/HTTP calls inside Presentation widgets",
            "Deterministic verification with mechanical exit code assertion",
            "SCAL Synergy: Pair domain/service logic with verification tests and stack-native invariant guards (@sovereign_catch, Zod, Freezed, Pydantic, Result<T,E>) to unlock low-cost autonomous self-healing",
        ]
        if framework == "flutter":
            invariants.append("Thread Isolation: heavy JSON parsing must run in compute() / Isolate on mobile")
            invariants.append("Type-Safe Native Bridge: use Pigeon for mobile channels")
    else:
        invariants = [
            "Deterministic Pipeline & Sim-to-Live Mathematical Parity (Simulation/Backtest <-> Live Execution Engine)",
            "Strict Concurrency & Persistence Hygiene (Zero unclosed DB connections, dangling transactions, or thread-local locks)",
            "Zero Blocking I/O or Unbounded Retries in Critical Real-Time Execution Paths",
            "Cross-Module Contract & Schema Integrity (Producer <-> Consumer JSON/DTO key and type parity)",
            "Deterministic verification with mechanical exit code assertion and production DB isolation in tests",
            "SCAL Synergy: Pair domain/service logic with verification tests and stack-native invariant guards (@sovereign_catch, Pydantic, Zod, Result<T,E>) to unlock low-cost autonomous self-healing",
        ]
    return invariants


def build_initial_dna_manifest(
    framework: str,
    language: str,
    target_dir: str = "."
) -> Dict[str, Any]:
    """Generates the canonical .agents/.dna.json payload during project initialization or brownfield deploy."""
    abs_p = os.path.abspath(target_dir)
    has_ui = framework.lower() in ("flutter", "react", "vue", "svelte", "nextjs", "angular")
    return {
        "schema_version": "0.0.1",
        "dna_state": "BORN",
        "origin": "foundation_init",
        "framework": framework,
        "language": language,
        "primary_framework": framework,
        "primary_language": language,
        "ecosystem": framework,
        "dna_compliance_score": 100,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "pillars": {
            "vision": "context/VISION.md",
            "strategy": "context/00_Strategy/BLUEPRINT.md",
            "product": "context/01_Product/ROADMAP.md",
            "creative": "context/02_Creative/STYLE_GUIDE.md",
            "tech": "context/03_Tech/ARCHITECTURE.md",
            "design_contract": "DESIGN.md"
        },
        "context_topology": "adaptive_25",
        "context_aliases": {},
        "architecture_topology": {
            "layout_style": "adaptive_hybrid",
            "tiers": CANONICAL_5_TIERS,
            "dependency_laws": CANONICAL_DEPENDENCY_LAWS
        },
        "invariants": _synthesize_invariants_for_stack(framework, has_ui=has_ui),
        "epigenetic_aliases": {},
        "layer_violations": [],
        "chimera_files": [],
        "mutation_ledger": {
            "dna_compliance_score": 100,
            "epigenetic_aliases": {},
            "layer_violations": [],
            "chimera_files": []
        }
    }


def mutate_project_dna(
    root_dir: str,
    mode: str = "epigenetic",
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Brownfield DNA Mutation Engine:
      - 'epigenetic': Maps existing non-standard folders to 5-Tier strata inside .agents/.dna.json without moving files.
      - 'plan': Generates .orion/working/dna_mutation_plan.md with surgical refactoring steps and violation audits.
      - 'scaffold': Non-destructively scaffolds canonical 5-Tier folders and context/ pillars alongside existing code.
    """
    abs_root = os.path.abspath(root_dir)
    dna = sequence_project_dna(abs_root)
    if not dna:
        return {"status": "error", "message": "Failed to sequence repository DNA."}

    # Discover candidate non-standard folders to map to 5-Tier strata
    files = list(dna.file_tier_map.keys())
    discovered_aliases = discover_epigenetic_aliases(abs_root, files, existing_aliases=dna.epigenetic_aliases)

    target_agents = os.path.join(abs_root, ".agents")
    dna_file = os.path.join(target_agents, ".dna.json")

    if mode == "epigenetic":
        payload = build_initial_dna_manifest(dna.primary_framework, dna.primary_language, abs_root)
        payload["dna_state"] = "MUTATING"
        payload["origin"] = "brownfield_mutation"
        payload["archetype"] = dna.archetype
        payload["ecosystem"] = dna.primary_framework
        payload["stacks"] = dna.stacks
        payload["execution_spine"] = dna.execution_spine
        payload["dna_compliance_score"] = dna.dna_compliance_score
        payload["epigenetic_aliases"] = discovered_aliases
        ctx_topology, discovered_context_aliases = discover_context_epigenetic_map(abs_root)
        payload["context_topology"] = ctx_topology
        if discovered_context_aliases:
            merged_ctx = payload.get("context_aliases", {}) or {}
            merged_ctx.update(discovered_context_aliases)
            payload["context_aliases"] = merged_ctx
        payload["layer_violations"] = dna.layer_violations[:15]
        payload["chimera_files"] = dna.chimera_files[:15]
        payload["mutation_ledger"]["epigenetic_aliases"] = discovered_aliases
        payload["mutation_ledger"]["dna_compliance_score"] = dna.dna_compliance_score
        payload["mutation_ledger"]["layer_violations"] = dna.layer_violations[:15]
        payload["mutation_ledger"]["chimera_files"] = dna.chimera_files[:15]

        if not dry_run:
            atomic_write_text(dna_file, json.dumps(payload, indent=2))
        return {
            "status": "success",
            "mode": "epigenetic",
            "dna_state": "MUTATING",
            "epigenetic_aliases": discovered_aliases,
            "dna_compliance_score": dna.dna_compliance_score,
            "violations_count": len(dna.layer_violations),
            "chimera_count": len(dna.chimera_files)
        }

    elif mode == "plan":
        plan_dir = os.path.join(abs_root, ".orion", "working")
        plan_file = os.path.join(plan_dir, "dna_mutation_plan.md")
        
        md_lines = [
            f"# 🧬 DNA Mutation Blueprint: `{os.path.basename(abs_root)}`",
            "",
            f"> **Current DNA State**: `{dna.dna_state}` | **Compliance Score**: `{dna.dna_compliance_score}/100`",
            f"> **Primary Stack**: `{dna.primary_framework}` ({dna.primary_language})",
            "",
            "## 1. Mapped Epigenetic Aliases (Safe Non-Breaking Aliases)",
            "| Legacy Path | Canonical DNA Stratum | Status |",
            "|---|---|---|",
        ]
        for legacy_p, stratum in sorted(discovered_aliases.items()):
            md_lines.append(f"| `{legacy_p}` | `{stratum}` | Active Epigenetic Adapter |")
        md_lines.append("")

        md_lines.extend([
            "## 2. Illegal Cross-Layer Dependency Violations",
            f"Detected **{len(dna.layer_violations)}** violations where lower layers depend on higher layers:",
            "",
            "| Source File | Line | Source Stratum | Illegal Target Stratum | Import Statement |",
            "|---|---|---|---|---|",
        ])
        for v in dna.layer_violations[:20]:
            md_lines.append(f"| `{v['file']}` | L{v['line']} | `{v['source_tier']}` | `{v['target_tier']}` | `{v['import']}` |")
        md_lines.append("")

        md_lines.extend([
            "## 3. Chimera Files (Refactoring Priority)",
            f"Detected **{len(dna.chimera_files)}** files mixing UI widgets with raw DB/Network calls:",
            "",
        ])
        for cf in dna.chimera_files[:15]:
            md_lines.append(f"- [ ] `{cf}`: Extract data queries into `3_services` repository")
        md_lines.append("")

        md_lines.extend([
            "## 4. Canonical 5-Tier Target Structure (Option A: Adaptive Hybrid)",
            "```plaintext",
            "lib/ (or src/)",
            "├── contracts/       # 1_contracts: Immutable models, DTOs, Zod/Freezed schemas",
            "├── domain/          # 2_domain: Pure business logic & use cases",
            "├── services/        # 3_services: API clients, repositories & database drivers",
            "├── state/           # 4_state: Notifiers, Riverpod providers, Zustand stores, Blocs",
            "├── presentation/    # 5_presentation: Screens, widgets, design tokens & UI",
            "└── core/            # Shared kernels: theme, routing, constants, utils",
            "```",
            ""
        ])

        if not dry_run:
            atomic_write_text(plan_file, "\n".join(md_lines))

        return {
            "status": "success",
            "mode": "plan",
            "plan_file": os.path.relpath(plan_file, abs_root).replace("\\", "/"),
            "compliance_score": dna.dna_compliance_score,
            "violations": len(dna.layer_violations),
            "chimeras": len(dna.chimera_files)
        }

    elif mode == "scaffold":
        scaffolded = []
        if os.path.isdir(os.path.join(abs_root, "src")):
            base_src = "src"
        elif os.path.isdir(os.path.join(abs_root, "lib")):
            base_src = "lib"
        elif os.path.isdir(os.path.join(abs_root, "app")):
            base_src = "app"
        else:
            is_dart = dna.primary_language == "dart" or "flutter" in dna.primary_framework
            base_src = "lib" if is_dart else "src"

        target_dirs = [
            f"{base_src}/contracts",
            f"{base_src}/domain",
            f"{base_src}/services",
            f"{base_src}/state",
            f"{base_src}/presentation/screens",
            f"{base_src}/presentation/widgets",
            f"{base_src}/core/theme",
            f"{base_src}/core/routing",
            "context/00_Strategy",
            "context/01_Product",
            "context/02_Creative",
            "context/03_Tech"
        ]
        for td in target_dirs:
            full_td = os.path.join(abs_root, td)
            if not os.path.exists(full_td):
                if not dry_run:
                    os.makedirs(full_td, exist_ok=True)
                scaffolded.append(td)

        return {
            "status": "success",
            "mode": "scaffold",
            "scaffolded_directories": scaffolded
        }

    return {"status": "error", "message": f"Unknown mutation mode: {mode}"}


def record_dna_snapshot(
    root_dir: str,
    compliance_score: Optional[int] = None,
    violations_count: Optional[int] = None,
    chimera_count: Optional[int] = None,
    file_count: Optional[int] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    abs_root = os.path.abspath(root_dir)
    if not db_path:
        db_path = os.path.join(abs_root, ".orion", "orion.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if compliance_score is None:
        dna = sequence_project_dna(abs_root, allow_foundation=True)
        if not dna:
            return {"ok": False, "error": "Failed to sequence project DNA"}
        compliance_score = dna.dna_compliance_score
        violations_count = len(dna.layer_violations)
        chimera_count = len(dna.chimera_files)
        file_count = len(dna.file_tier_map)
        archetype = dna.archetype
        dna_state = dna.dna_state
        v_dict = {}
        for v in dna.layer_violations:
            pair = f"{v['source_tier']} -> {v['target_tier']}"
            v_dict[pair] = v_dict.get(pair, 0) + 1
        violations_json = json.dumps(v_dict)
    else:
        violations_count = violations_count if violations_count is not None else 0
        chimera_count = chimera_count if chimera_count is not None else 0
        file_count = file_count if file_count is not None else 0
        archetype = "Software Repository"
        dna_state = "BORN"
        violations_json = "{}"

    now_iso = datetime.now().isoformat()

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dna_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                compliance_score INTEGER,
                violations_count INTEGER,
                chimera_count INTEGER,
                file_count INTEGER,
                archetype TEXT,
                dna_state TEXT,
                violations_json TEXT
            )
        """)
        conn.execute(
            "INSERT INTO dna_snapshots (timestamp, compliance_score, violations_count, chimera_count, file_count, archetype, dna_state, violations_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (now_iso, compliance_score, violations_count, chimera_count, file_count, archetype, dna_state, violations_json)
        )
        conn.commit()
        conn.close()
        return {
            "ok": True,
            "timestamp": now_iso,
            "compliance_score": compliance_score,
            "violations_count": violations_count,
            "chimera_count": chimera_count,
            "file_count": file_count
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_dna_trend(root_dir: str, limit: int = 10, db_path: Optional[str] = None) -> Dict[str, Any]:
    abs_root = os.path.abspath(root_dir)
    if not db_path:
        db_path = os.path.join(abs_root, ".orion", "orion.db")

    if not os.path.exists(db_path):
        return {"ok": True, "snapshots": [], "has_regression": False, "regression_reason": ""}

    try:
        conn = sqlite3.connect(db_path, timeout=5.0)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dna_snapshots'")
        if not c.fetchone():
            conn.close()
            return {"ok": True, "snapshots": [], "has_regression": False, "regression_reason": ""}

        c.execute(
            "SELECT timestamp, compliance_score, violations_count, chimera_count, file_count, archetype, dna_state, violations_json FROM dna_snapshots ORDER BY id ASC"
        )
        rows = c.fetchall()
        conn.close()

        if limit > 0 and len(rows) > limit:
            rows = rows[-limit:]

        snapshots = []
        for r in rows:
            snapshots.append({
                "timestamp": r[0],
                "compliance_score": r[1],
                "violations_count": r[2],
                "chimera_count": r[3],
                "file_count": r[4],
                "archetype": r[5],
                "dna_state": r[6],
                "violations_json": r[7]
            })

        has_regression = False
        regression_reason = ""
        if len(snapshots) >= 2:
            prev_score = snapshots[-2]["compliance_score"]
            curr_score = snapshots[-1]["compliance_score"]
            if curr_score < prev_score:
                has_regression = True
                regression_reason = f"Compliance score dropped from {prev_score}/100 to {curr_score}/100"
                try:
                    from commands.reflexion import ObservationLedger
                    ledger = ObservationLedger()
                    ledger.add_observation(
                        title=f"DNA compliance score regression ({prev_score} -> {curr_score})",
                        kind="improve",
                        target="core/dna.py",
                        rule_id="DNA_COMPLIANCE_REGRESSION",
                        evidence=f"Latest snapshot score {curr_score} lower than previous {prev_score}"
                    )
                except Exception:
                    pass

        return {
            "ok": True,
            "snapshots": snapshots,
            "has_regression": has_regression,
            "regression_reason": regression_reason
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "snapshots": [], "has_regression": False, "regression_reason": ""}


# ==============================================================================
# UNIVERSAL POLYGLOT DNA SEMVER & CHANGELOG ENGINE
# ==============================================================================

SEMVER_REGEX = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")

def parse_semver(version_str: str) -> Optional[Tuple[int, int, int, str, str]]:
    """Parses SemVer string into (major, minor, patch, prerelease, build)."""
    clean_v = version_str.strip().lstrip("vV")
    m = SEMVER_REGEX.match(clean_v)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) or "", m.group(5) or ""


def bump_semver_tuple(major: int, minor: int, patch: int, bump_type: str = "patch") -> Tuple[int, int, int]:
    """Increments major, minor, or patch."""
    b = bump_type.lower()
    if b == "major":
        return major + 1, 0, 0
    elif b == "minor":
        return major, minor + 1, 0
    else:
        return major, minor, patch + 1


def detect_project_version(root_dir: str = ".") -> Tuple[str, str]:
    """
    Universal polyglot version detector.
    Scans in order:
      1. Root VERSION file (plain text)
      2. package.json ("version": "x.y.z")
      3. pubspec.yaml (version: x.y.z+build or x.y.z)
      4. pyproject.toml (version = "x.y.z")
      5. Cargo.toml (version = "x.y.z")
      6. pom.xml (<version>x.y.z</version>)
      7. build.gradle / build.gradle.kts (version = 'x.y.z')
      8. CHANGELOG.md (first ## [x.y.z])
    Returns (version_string, manifest_relpath).
    Defaults to ("0.1.0", "VERSION") if none found.
    """
    abs_root = os.path.abspath(root_dir)

    # 1. Plain root VERSION file
    ver_path = os.path.join(abs_root, "VERSION")
    if os.path.isfile(ver_path):
        try:
            with open(ver_path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if parse_semver(raw):
                    return raw.lstrip("vV"), "VERSION"
        except OSError:
            pass

    # 2. Node.js / Web / TypeScript package.json
    pkg_path = os.path.join(abs_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                v = data.get("version")
                if v and parse_semver(v):
                    return v.lstrip("vV"), "package.json"
        except (OSError, json.JSONDecodeError):
            pass

    # 3. Flutter / Dart pubspec.yaml
    pub_path = os.path.join(abs_root, "pubspec.yaml")
    if os.path.isfile(pub_path):
        try:
            with open(pub_path, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"^version:\s*([0-9a-zA-Z.+_-]+)", line.strip())
                    if m:
                        v = m.group(1).strip("'\"")
                        if parse_semver(v):
                            return v.lstrip("vV"), "pubspec.yaml"
        except OSError:
            pass

    # 4. Python pyproject.toml
    pyproj_path = os.path.join(abs_root, "pyproject.toml")
    if os.path.isfile(pyproj_path):
        try:
            with open(pyproj_path, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^\s*version\s*=\s*["\']([^"\']+)["\']', line)
                    if m:
                        v = m.group(1)
                        if parse_semver(v):
                            return v.lstrip("vV"), "pyproject.toml"
        except OSError:
            pass

    # 5. Rust Cargo.toml
    cargo_path = os.path.join(abs_root, "Cargo.toml")
    if os.path.isfile(cargo_path):
        try:
            with open(cargo_path, "r", encoding="utf-8") as f:
                in_package = False
                for line in f:
                    sline = line.strip()
                    if sline == "[package]":
                        in_package = True
                        continue
                    elif sline.startswith("[") and in_package:
                        in_package = False
                    if in_package:
                        m = re.match(r'^\s*version\s*=\s*["\']([^"\']+)["\']', sline)
                        if m:
                            v = m.group(1)
                            if parse_semver(v):
                                return v.lstrip("vV"), "Cargo.toml"
        except OSError:
            pass

    # 6. Java / Maven pom.xml
    pom_path = os.path.join(abs_root, "pom.xml")
    if os.path.isfile(pom_path):
        try:
            with open(pom_path, "r", encoding="utf-8") as f:
                m = re.search(r'<version>([0-9a-zA-Z.+_-]+)</version>', f.read())
                if m:
                    v = m.group(1)
                    if parse_semver(v):
                        return v.lstrip("vV"), "pom.xml"
        except OSError:
            pass

    # 7. Gradle build.gradle / build.gradle.kts
    for g_name in ("build.gradle.kts", "build.gradle"):
        g_path = os.path.join(abs_root, g_name)
        if os.path.isfile(g_path):
            try:
                with open(g_path, "r", encoding="utf-8") as f:
                    for line in f:
                        m = re.match(r'^\s*(?:version\s*=\s*|version\s+)["\']([^"\']+)["\']', line.strip())
                        if m:
                            v = m.group(1)
                            if parse_semver(v):
                                return v.lstrip("vV"), g_name
            except OSError:
                pass

    # 8. CHANGELOG.md (topmost release header)
    ch_path = os.path.join(abs_root, "CHANGELOG.md")
    if os.path.isfile(ch_path):
        try:
            with open(ch_path, "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^##\s*\[([0-9a-zA-Z.+_-]+)\]', line.strip())
                    if m:
                        v = m.group(1)
                        if v.lower() != "unreleased" and parse_semver(v):
                            return v.lstrip("vV"), "CHANGELOG.md"
        except OSError:
            pass

    return "0.1.0", "VERSION"


def update_project_version(root_dir: str = ".", new_version: str = "0.1.0") -> List[str]:
    """
    Updates the detected primary version manifest(s) with new_version using pure stdlib atomic writes.
    Returns list of modified relative paths.
    """
    clean_v = new_version.strip().lstrip("vV")
    abs_root = os.path.abspath(root_dir)
    updated: List[str] = []

    # 1. Update VERSION if it exists or if no other manifest exists
    ver_path = os.path.join(abs_root, "VERSION")
    has_known_manifest = any(
        os.path.isfile(os.path.join(abs_root, m))
        for m in ("package.json", "pubspec.yaml", "pyproject.toml", "Cargo.toml")
    )
    if os.path.isfile(ver_path) or not has_known_manifest:
        atomic_write_text(ver_path, clean_v + "\n")
        updated.append("VERSION")

    # 2. Update package.json
    pkg_path = os.path.join(abs_root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                raw = f.read()
            subbed = re.sub(r'("version"\s*:\s*")([^"]+)(")', rf'\g<1>{clean_v}\g<3>', raw, count=1)
            if subbed != raw:
                atomic_write_text(pkg_path, subbed)
                updated.append("package.json")
        except OSError:
            pass

    # 3. Update pubspec.yaml
    pub_path = os.path.join(abs_root, "pubspec.yaml")
    if os.path.isfile(pub_path):
        try:
            with open(pub_path, "r", encoding="utf-8") as f:
                raw = f.read()
            def _pub_repl(m):
                old_v = m.group(1)
                build_part = ""
                if "+" in old_v:
                    build_part = "+" + old_v.split("+", 1)[1]
                return f"version: {clean_v}{build_part}"
            subbed = re.sub(r'^version:\s*([^\r\n]+)', _pub_repl, raw, flags=re.MULTILINE, count=1)
            if subbed != raw:
                atomic_write_text(pub_path, subbed)
                updated.append("pubspec.yaml")
        except OSError:
            pass

    # 4. Update pyproject.toml
    pyproj_path = os.path.join(abs_root, "pyproject.toml")
    if os.path.isfile(pyproj_path):
        try:
            with open(pyproj_path, "r", encoding="utf-8") as f:
                raw = f.read()
            subbed = re.sub(r'(version\s*=\s*["\'])([^"\']+)(["\'])', rf'\g<1>{clean_v}\g<3>', raw, count=1)
            if subbed != raw:
                atomic_write_text(pyproj_path, subbed)
                updated.append("pyproject.toml")
        except OSError:
            pass

    # 5. Update Cargo.toml
    cargo_path = os.path.join(abs_root, "Cargo.toml")
    if os.path.isfile(cargo_path):
        try:
            with open(cargo_path, "r", encoding="utf-8") as f:
                raw = f.read()
            parts = re.split(r'(\[package\])', raw, maxsplit=1)
            if len(parts) >= 3:
                pkg_section = parts[2]
                subbed_pkg = re.sub(r'(version\s*=\s*["\'])([^"\']+)(["\'])', rf'\g<1>{clean_v}\g<3>', pkg_section, count=1)
                full_cargo = parts[0] + parts[1] + subbed_pkg
                atomic_write_text(cargo_path, full_cargo)
                updated.append("Cargo.toml")
        except OSError:
            pass

    return updated


def compact_changelog_entries(raw_content: str) -> str:
    """
    Lessword Compact Changelog Synthesizer:
    Consolidates raw bullet points into 3-5 dense domain sentences.
    Eliminates AI slop, conversational filler, and verbose multi-line laundry lists.
    """
    lines = [l.strip() for l in raw_content.splitlines() if l.strip()]
    if not lines:
        return "- Maintenance release and performance hardening."

    raw_items: List[str] = []
    for line in lines:
        if line.startswith(("#", "---")):
            continue
        cleaned = re.sub(r"^[-*+]\s*(\[[ x]\]\s*)?", "", line).strip()
        cleaned = re.sub(r"^(?:Added|Changed|Fixed|Breaking Changes?|Security|Deprecated):\s*", "", cleaned, flags=re.IGNORECASE).strip()
        if cleaned and len(cleaned) > 2:
            raw_items.append(cleaned)

    if not raw_items:
        return "- Maintenance release and performance hardening."

    core_items: List[str] = []
    services_items: List[str] = []
    ui_items: List[str] = []
    verification_items: List[str] = []
    general_items: List[str] = []

    for item in raw_items:
        low = item.lower()
        if any(k in low for k in ("dna", "strata", "ast", "scaffold", "semver", "vision", "blueprint", "rule", "guardrail", "manifest", "contract", "tier")):
            core_items.append(item)
        elif any(k in low for k in ("service", "repo", "api", "bento", "packer", "bundle", "pipeline", "db", "sqlite", "query", "state", "cache", "hazard")):
            services_items.append(item)
        elif any(k in low for k in ("ui", "screen", "widget", "token", "view", "theme", "design", "css", "layout", "craft")):
            ui_items.append(item)
        elif any(k in low for k in ("test", "spec", "verify", "gate", "bugfix", "fix", "regression", "leak", "clean")):
            verification_items.append(item)
        else:
            general_items.append(item)

    def _condense(items: List[str]) -> str:
        phrases: List[str] = []
        for it in items:
            p = re.sub(r"^(?:Added|Changed|Implemented|Created|Updated|Fixed|Resolved|Supported)\s+", "", it, flags=re.IGNORECASE).strip()
            p = p.rstrip(".")
            if p and p not in phrases:
                phrases.append(p)
        if not phrases:
            return ""
        if len(phrases) == 1:
            return phrases[0] + "."
        elif len(phrases) <= 3:
            return ", ".join(phrases[:-1]) + ", and " + phrases[-1] + "."
        else:
            return ", ".join(phrases[:3]) + f", and {len(phrases) - 3} auxiliary improvements."

    dense_lines: List[str] = []
    if core_items:
        dense_lines.append(f"- **Architecture & Governance**: {_condense(core_items)}")
    if services_items:
        dense_lines.append(f"- **Core Services & Pipelines**: {_condense(services_items)}")
    if ui_items:
        dense_lines.append(f"- **Presentation & UI Craft**: {_condense(ui_items)}")
    if verification_items:
        dense_lines.append(f"- **Integrity & Bug Fixes**: {_condense(verification_items)}")
    if general_items and len(dense_lines) < 4:
        dense_lines.append(f"- **Operational Polish**: {_condense(general_items)}")

    if not dense_lines:
        dense_lines.append("- Maintenance update and performance hardening.")

    return "\n".join(dense_lines)


def stamp_changelog_release(root_dir: str = ".", version: str = "0.1.0", date_str: Optional[str] = None, compact: bool = True) -> bool:
    """
    Transitions ## [Unreleased] in root CHANGELOG.md into ## [vX.Y.Z] - YYYY-MM-DD
    synthesizing dense, Lessword-compact domain paragraphs, and reseeds a clean ## [Unreleased] template.
    """
    abs_root = os.path.abspath(root_dir)
    ch_path = os.path.join(abs_root, "CHANGELOG.md")
    if not os.path.isfile(ch_path):
        return False

    clean_v = version.strip().lstrip("vV")
    today = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        with open(ch_path, "r", encoding="utf-8") as f:
            content = f.read()

        unreleased_match = re.search(r"^##\s*\[Unreleased\]\s*([\s\S]*?)(?=^##\s*\[|\Z)", content, flags=re.MULTILINE)
        if not unreleased_match:
            return False

        unreleased_body = unreleased_match.group(1).strip()
        if compact and unreleased_body:
            synthesized_body = compact_changelog_entries(unreleased_body)
        elif unreleased_body:
            synthesized_body = unreleased_body
        else:
            synthesized_body = "- Maintenance release and performance hardening."

        new_unreleased_header = (
            "## [Unreleased]\n\n"
            "- \n\n"
            f"## [{clean_v}] - {today}\n\n"
            f"{synthesized_body}\n\n"
        )

        updated = content[:unreleased_match.start()] + new_unreleased_header + content[unreleased_match.end():]
        atomic_write_text(ch_path, updated)
        return True
    except OSError:
        return False


def evaluate_dna_semver(
    root_dir: str = ".",
    since_ref: Optional[str] = None,
    file_list: Optional[List[str]] = None,
    commit_messages: Optional[List[str]] = None,
    allow_major_override: bool = False,
    allow_minor_override: bool = False,
) -> Dict[str, Any]:
    """
    Evaluates changed files and commit messages against Project DNA 5-Tier Strata
    to deterministically calculate SemVer impact (MAJOR, MINOR, or PATCH) with
    strict Anti-AI-Slop and Lessword thresholds.
    """
    abs_root = os.path.abspath(root_dir)
    curr_v_str, manifest_src = detect_project_version(abs_root)
    parsed = parse_semver(curr_v_str)
    maj, minr, pat = (parsed[0], parsed[1], parsed[2]) if parsed else (0, 1, 0)

    # 1. Collect modified files
    changed_files = list(file_list or [])
    if not changed_files:
        try:
            ref = since_ref or "HEAD"
            cmd = ["git", "diff", "--name-only", ref]
            proc = subprocess.run(cmd, cwd=abs_root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if proc.returncode == 0 and proc.stdout.strip():
                changed_files = [f.strip().replace("\\", "/") for f in proc.stdout.strip().splitlines() if f.strip()]
            else:
                proc2 = subprocess.run(["git", "status", "--porcelain"], cwd=abs_root, capture_output=True, text=True, encoding="utf-8", errors="replace")
                if proc2.returncode == 0 and proc2.stdout.strip():
                    for line in proc2.stdout.splitlines():
                        parts = line.strip().split(None, 1)
                        if len(parts) >= 2:
                            changed_files.append(parts[1].strip().replace("\\", "/"))
        except (OSError, subprocess.SubprocessError):
            pass

    # 2. Collect commit messages / session tags if available
    msgs = list(commit_messages or [])
    if not msgs:
        try:
            cmd = ["git", "log", "-n", "10", "--pretty=format:%B---COMMIT_DELIM---"]
            proc = subprocess.run(cmd, cwd=abs_root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if proc.returncode == 0 and proc.stdout.strip():
                msgs = [m.strip() for m in proc.stdout.split("---COMMIT_DELIM---") if m.strip()]
        except (OSError, subprocess.SubprocessError):
            pass

    session_history_path = os.path.join(abs_root, ".orion", "episodic", "session_history.md")
    if os.path.isfile(session_history_path):
        try:
            with open(session_history_path, "r", encoding="utf-8", errors="ignore") as f:
                msgs.append(f.read())
        except OSError:
            pass

    # 3. Analyze Tiers and Gravity
    tier_counts: Dict[str, int] = defaultdict(int)
    file_tier_map: Dict[str, str] = {}
    reasons: List[str] = []

    for f_rel in changed_files:
        t_key, gravity, slug, title = classify_file_to_tier(f_rel)
        tier_counts[t_key] += 1
        file_tier_map[f_rel] = t_key

    # 4. Strict Major Gate (Quarantined against AI slop)
    is_major = False
    is_minor = False
    combined_text = " ".join(msgs).lower()

    if allow_major_override:
        is_major = True
        reasons.append("Explicit human authorization for MAJOR release override")
    else:
        vision_modified = any("context/vision.md" in f.lower() or f.lower().endswith("vision.md") for f in changed_files)
        if vision_modified and any(k in combined_text for k in ("[paradigm-shift]", "[breaking-vision]")):
            is_major = True
            reasons.append("Sacred North Star (context/VISION.md) paradigm shift confirmed in history")
        elif vision_modified:
            reasons.append("⚠️ Sacred North Star (context/VISION.md) modified without explicit [paradigm-shift] tag; autonomous Major Quarantine preserves minor/patch stability")

    # 5. Strict Minor Gate (High-Threshold: requires new feature organ, new pillar, or milestone)
    if not is_major:
        if allow_minor_override:
            is_minor = True
            reasons.append("Explicit human authorization for MINOR release override")
        elif any(k in combined_text for k in ("[milestone]", "[epoch]", "[new-organ]")):
            is_minor = True
            reasons.append("Explicit Milestone or New Feature Organ tag detected in session history")
        elif any("0_pillars_and_manifests" in file_tier_map.get(f, "") and "pillar" in f.lower() for f in changed_files):
            is_minor = True
            reasons.append("New capability pillar introduced in Tier 0")
        else:
            # Check if any new feature organ directory was added (e.g. src/organ/ or features/organ/)
            detected_organs = set()
            for f in changed_files:
                parts = f.replace("\\", "/").split("/")
                if len(parts) >= 3 and parts[0] in ("src", "lib", "features", "packages", "apps", "services"):
                    detected_organs.add(f"{parts[0]}/{parts[1]}")
            if len(detected_organs) >= 2:
                # Multiple broad organs touched simultaneously with feature tag
                if any(k in combined_text for k in ("[feature]", "feat:", "feat(")):
                    is_minor = True
                    reasons.append(f"Broad multi-organ feature evolution across {len(detected_organs)} contexts ({', '.join(sorted(detected_organs)[:3])})")

    # 6. Universal Patch Default
    if is_major:
        bump = "MAJOR" if maj >= 1 else "MINOR"
        next_maj, next_min, next_pat = bump_semver_tuple(maj, minr, pat, "major" if maj >= 1 else "minor")
    elif is_minor:
        bump = "MINOR"
        next_maj, next_min, next_pat = bump_semver_tuple(maj, minr, pat, "minor")
    else:
        bump = "PATCH"
        next_maj, next_min, next_pat = bump_semver_tuple(maj, minr, pat, "patch")
        reasons.append("Incremental development: routine endpoints, UI polish, bugfixes, refactorings, and test additions stay strictly PATCH (Anti-AI-Slop Invariant)")

    target_v = f"{next_maj}.{next_min}.{next_pat}"

    return {
        "current_version": curr_v_str,
        "manifest_source": manifest_src,
        "recommended_bump": bump,
        "target_version": target_v,
        "changed_files_count": len(changed_files),
        "tier_distribution": dict(tier_counts),
        "reasons": reasons,
        "file_tier_map": file_tier_map,
    }
