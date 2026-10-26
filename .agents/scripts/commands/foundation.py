import os
import shutil
import argparse
import re
import json
import sys
import subprocess
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

try:
    from core.db import log_telemetry as _log_telemetry, atomic_write_text
except ImportError:
    def _log_telemetry(err: Exception = None, context: str = "") -> None:
        if os.environ.get("ORION_DEBUG"):
            msg = f": {err}" if err else ""
            sys.stderr.write(f"[ORION_TELEMETRY] Non-fatal catch in {context}{msg}\n")
    def atomic_write_text(filepath: str, content: str) -> None:
        import uuid
        abs_path = os.path.abspath(str(filepath))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        temp_file = f"{abs_path}.tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(temp_file, abs_path)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

try:
    from core.platform_manifests import deploy_platform_manifest, deploy_all_platform_manifests
except ImportError:
    try:
        from .core.platform_manifests import deploy_platform_manifest, deploy_all_platform_manifests
    except ImportError:
        deploy_platform_manifest = None
        deploy_all_platform_manifests = None


if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError, ValueError):
        pass


AI_CONFIGS = {
    "gemini": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "AGENTS.md", "format": "md", "canonical": "agents"},
    # VS Code/Copilot natively discovers project-root AGENTS.md. Keep it as
    # the single canonical global instruction file instead of duplicating it
    # under .github/copilot-instructions.md.
    "copilot": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "AGENTS.md", "format": "md", "canonical": "agents"},
    "cursor": {"template": "CURSOR_RULE.template.mdc", "target_dir": ".cursor/rules", "target_path": "portable-brainvibing.mdc", "format": "mdc"},
    "windsurf": {"template": "AI_ADAPTER.template.md", "target_dir": ".windsurf/rules", "target_path": "portable-brainvibing.md", "format": "md"},
    "cline": {"template": "AI_ADAPTER.template.md", "target_dir": ".clinerules", "target_path": "portable-brainvibing.md", "format": "md", "legacy_target_path": ".clinerules"},
    "claude": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "AGENTS.md", "format": "md", "canonical": "agents"},
    "agents": {"template": "AGENTS.template.md", "target_dir": "", "target_path": "AGENTS.md", "format": "md"}
}

def get_ecosystem_config(foundation_dir, framework):
    if not framework:
        return {}
    eco_json_path = os.path.join(foundation_dir, ".agents", "canons", "ecosystems", framework.lower(), "ecosystem.json")
    if not os.path.exists(eco_json_path):
        eco_json_path = os.path.join(foundation_dir, "canons", "ecosystems", framework.lower(), "ecosystem.json")
    if os.path.exists(eco_json_path):
        try:
            with open(eco_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as _e:
            _log_telemetry(_e, 'foundation.py:37')
    return {}


def prune_unmatched_canons(target_agents_dir, active_framework):
    """
    Removes framework ecosystem canon directories that do not match the target project's active framework.
    For example, if framework is 'flutter', removes 'react', 'python', etc. from .agents/canons/ecosystems/.
    """
    if not active_framework or active_framework == "generic":
        return []
    target_root = os.path.dirname(os.path.abspath(target_agents_dir))
    if _is_foundation_hub_repo(target_root):
        return []

    eco_dir = os.path.join(target_agents_dir, "canons", "ecosystems")
    micro_dir = os.path.join(target_agents_dir, "canons", "micro")
    if not os.path.exists(eco_dir) and not os.path.exists(micro_dir):
        return

    fw_clean = active_framework.lower().strip()
    active_canon_dir = fw_clean
    if fw_clean in ["next", "react", "vue", "svelte", "node", "express", "javascript", "typescript"]:
        active_canon_dir = "react"
    elif fw_clean in ["flutter", "dart"]:
        active_canon_dir = "flutter"
    elif fw_clean in ["python", "django", "fastapi", "flask"]:
        active_canon_dir = "python"

    framework_canons = {"flutter", "react", "python"}

    if os.path.exists(eco_dir):
        for item in os.listdir(eco_dir):
            item_lower = item.lower()
            item_path = os.path.join(eco_dir, item)
            if os.path.isdir(item_path) and item_lower in framework_canons and item_lower != active_canon_dir:
                try:
                    for root, dirs, files in os.walk(item_path, topdown=False):
                        for f in files:
                            os.remove(os.path.join(root, f))
                        for d in dirs:
                            os.rmdir(os.path.join(root, d))
                    os.rmdir(item_path)
                    print(f"  -> Pruned irrelevant ecosystem canon: canons/ecosystems/{item}/")
                except Exception as e:
                    _log_telemetry(e, "prune_unmatched_canons:ecosystems")

    micro_dir = os.path.join(target_agents_dir, "canons", "micro")
    if os.path.exists(micro_dir):
        micro_framework_map = {
            "flutter.md": "flutter",
            "pubspec.md": "flutter",
            "react.md": "react",
            "python.md": "python",
        }
        for fname in os.listdir(micro_dir):
            fpath = os.path.join(micro_dir, fname)
            if not os.path.isfile(fpath) or fname == "README.md":
                continue
            should_prune = False
            if fname in micro_framework_map:
                if micro_framework_map[fname] != active_canon_dir:
                    should_prune = True
            elif fname == "supabase.md":
                has_supabase = False
                try:
                    for check_file in ["requirements.txt", "package.json", "pubspec.yaml"]:
                        cfp = os.path.join(target_root, check_file)
                        if os.path.isfile(cfp):
                            with open(cfp, "r", encoding="utf-8", errors="ignore") as _f:
                                if "supabase" in _f.read().lower():
                                    has_supabase = True
                                    break
                except Exception as _se:
                    _log_telemetry(_se, "prune_unmatched_canons:supabase_check")
                if not has_supabase:
                    should_prune = True

            if should_prune:
                try:
                    os.remove(fpath)
                    print(f"  -> Pruned irrelevant micro canon: canons/micro/{fname}")
                except Exception as _me:
                    _log_telemetry(_me, f"prune_unmatched_canons:micro:{fname}")

def _read_python_deps(root: str) -> set[str]:
    """Extract normalized package dependencies from requirements.txt or pyproject.toml."""
    deps = set()
    if not root or not os.path.isdir(root):
        return deps

    # 1. Inspect requirements.txt
    req_file = os.path.join(root, "requirements.txt")
    if os.path.isfile(req_file):
        try:
            with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    clean = line.strip()
                    if not clean or clean.startswith(("#", "-", "@")):
                        continue
                    # Match package name before delimiters [<>=~! ;#]
                    match = re.match(r"^([a-zA-Z0-9_\-\.]+)", clean)
                    if match:
                        deps.add(match.group(1).lower().replace("_", "-"))
        except Exception as e:
            _log_telemetry(e, "_read_python_deps:requirements")

    # 2. Inspect pyproject.toml
    pyproject_file = os.path.join(root, "pyproject.toml")
    if os.path.isfile(pyproject_file):
        try:
            with open(pyproject_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    clean = line.strip()
                    if not clean or clean.startswith("#"):
                        continue
                    # Match inside quotes if in dependencies list, e.g. "fastapi>=0.100.0"
                    m = re.search(r'["\']([a-zA-Z0-9_\-\.]+)', clean)
                    if m:
                        pkg = m.group(1).lower().replace("_", "-")
                        # Skip table headers or common non-pkg words
                        if pkg not in ("project", "build-system", "tool", "dependencies", "true", "false"):
                            deps.add(pkg)
        except Exception as e:
            _log_telemetry(e, "_read_python_deps:pyproject")

    return deps


def _python_profile(deps: set[str], has_ui: bool = False) -> dict:
    """Generate dynamic stack configuration for Python projects based on detected dependencies."""
    # Web Framework
    if "fastapi" in deps:
        fw_name = "FastAPI"
        arch_fw = "FastAPI Clean Architecture"
    elif "django" in deps:
        fw_name = "Django"
        arch_fw = "Django MVT / Clean Architecture"
    elif "flask" in deps:
        fw_name = "Flask"
        arch_fw = "Flask Application Factory Architecture"
    else:
        fw_name = "Headless / CLI / Daemon"
        arch_fw = "Clean Python Architecture"

    # UI Framework
    if has_ui:
        ui_fw = "HTML / Tailwind CSS" if fw_name != "Headless / CLI / Daemon" else "Modular UI"
        ui_ref = "Tailwind CSS"
    else:
        ui_fw = "None (headless)"
        ui_ref = "N/A — headless project"

    # Persistence
    pers_parts = []
    if "sqlalchemy" in deps:
        pers_parts.append("SQLAlchemy")
    if "sqlmodel" in deps:
        pers_parts.append("SQLModel")
    if "tortoise-orm" in deps or "tortoise" in deps:
        pers_parts.append("Tortoise ORM")
    if "peewee" in deps:
        pers_parts.append("Peewee")
    if "redis" in deps:
        pers_parts.append("Redis")
    if "asyncpg" in deps or "psycopg" in deps or "psycopg2" in deps:
        pers_parts.append("Postgres")
    if "pymongo" in deps or "motor" in deps:
        pers_parts.append("MongoDB")

    if not pers_parts or any("sql" in p.lower() for p in pers_parts) or "sqlite3" in deps or "sqlite" in deps:
        pers_parts.append("SQLite")

    backend_persistence = " / ".join(dict.fromkeys(pers_parts)) if pers_parts else "Persistent Storage / SQLite"

    # State / Models
    if "pydantic" in deps or "pydantic-core" in deps:
        model_type = "pydantic"
        state_mgmt = "Pydantic Models"
    elif "attrs" in deps:
        model_type = "attrs"
        state_mgmt = "Attrs Models"
    else:
        model_type = "dataclasses"
        state_mgmt = "Dataclasses / Typed Dicts"

    tech_stack_parts = ["Python"]
    if fw_name != "Headless / CLI / Daemon":
        tech_stack_parts.append(fw_name)
    if pers_parts:
        tech_stack_parts.append(pers_parts[0])
    tech_stack = ", ".join(tech_stack_parts)

    return {
        "FRAMEWORK": "python",
        "LANGUAGE": "python",
        "STATE_MANAGEMENT": model_type,
        "MODEL_TYPE": model_type,
        "tech_stack": tech_stack,
        "primary_languages": "Python",
        "frontend_framework": fw_name,
        "backend_persistence": backend_persistence,
        "state_management_choice": state_mgmt,
        "arch_framework": arch_fw,
        "state_management": state_mgmt,
        "ui_framework": ui_fw,
        "ui_kit_reference": ui_ref,
        "decision_1_title": "Adopt Layered Architecture with Explicit Boundaries",
        "decision_1_logic": "Separates domain logic from I/O for testability.",
        "decision_1_tradeoffs": "Requires disciplined abstraction between layers.",
        "topic_1": "Codebase Invariants & Quirks",
        "knowledge_1": "Document operational runtime quirks and concurrency rules here.",
    }


def scan_monorepo_workspaces(target_dir):
    """Scan root and sub-directories (apps, packages, services, etc.) to detect distinct workspaces."""
    candidate_roots = [target_dir]
    for sub in ("apps", "packages", "services", "modules", "crates", "libs"):
        sp = os.path.join(target_dir, sub)
        if os.path.isdir(sp):
            try:
                for entry in os.scandir(sp):
                    if entry.is_dir() and not entry.name.startswith("."):
                        candidate_roots.append(entry.path)
            except OSError:
                pass

    workspaces = []
    for c_root in candidate_roots:
        rel_p = os.path.relpath(c_root, target_dir).replace("\\", "/")
        if rel_p == ".":
            rel_p = ""
        fw, lang = None, None
        if os.path.exists(os.path.join(c_root, "pubspec.yaml")):
            fw, lang = "flutter", "dart"
        elif os.path.exists(os.path.join(c_root, "package.json")):
            try:
                with open(os.path.join(c_root, "package.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    if "next" in deps or "react" in deps:
                        is_ts = os.path.exists(os.path.join(c_root, "tsconfig.json"))
                        fw, lang = "react", "typescript" if is_ts else "javascript"
            except Exception as _e:
                _log_telemetry(_e, 'foundation.py:scan_package_json')
            if not fw:
                is_ts = os.path.exists(os.path.join(c_root, "tsconfig.json"))
                fw, lang = "node", "typescript" if is_ts else "javascript"
        elif os.path.exists(os.path.join(c_root, "pyproject.toml")) or os.path.exists(os.path.join(c_root, "requirements.txt")):
            fw, lang = "python", "python"
        elif os.path.exists(os.path.join(c_root, "Cargo.toml")):
            fw, lang = "rust", "rust"
        elif os.path.exists(os.path.join(c_root, "go.mod")):
            fw, lang = "go", "go"

        if fw and lang:
            workspaces.append({
                "path": rel_p or ".",
                "framework": fw,
                "language": lang
            })

    return workspaces


def detect_stack(target_dir):
    """
    Auto-detect framework and language from target project markers (including sub-workspaces).
    Returns (dominant_framework, dominant_language).
    """
    workspaces = scan_monorepo_workspaces(target_dir)
    if not workspaces:
        return "generic", "generic"

    root_ws = next((w for w in workspaces if w["path"] == "."), None)
    if root_ws:
        return root_ws["framework"], root_ws["language"]

    return workspaces[0]["framework"], workspaces[0]["language"]

def get_stack_defaults(framework, language, target_dir=None):
    fw_lower = (framework or "generic").lower()
    lang_lower = (language or "generic").lower()
    if fw_lower == "flutter" or lang_lower == "dart":
        return {
            "FRAMEWORK": "flutter",
            "LANGUAGE": "dart",
            "STATE_MANAGEMENT": "riverpod",
            "MODEL_TYPE": "Freezed",
            "tech_stack": "Dart/Flutter, SQLite",
            "primary_languages": "Dart",
            "frontend_framework": "Flutter",
            "backend_persistence": "Supabase / SQLite",
            "state_management_choice": "Riverpod 2.x",
            "arch_framework": "Flutter Clean Architecture",
            "state_management": "Riverpod",
            "ui_framework": "Flutter Material 3",
            "ui_kit_reference": "Tailwind / Flutter Material 3",
            "decision_1_title": "Adopt Feature-First Riverpod Architecture",
            "decision_1_logic": "Isolates feature domains and enables concurrent development.",
            "decision_1_tradeoffs": "Slight initial boilerplate in exchange for testability.",
            "topic_1": "State Management Lifecycle",
            "knowledge_1": "AutoDispose providers require explicit watch or keepAlive to maintain cache.",
        }
    if fw_lower in ["react", "next"]:
        return {
            "FRAMEWORK": fw_lower,
            "LANGUAGE": lang_lower if lang_lower != "generic" else "typescript",
            "STATE_MANAGEMENT": "zustand",
            "MODEL_TYPE": "zod",
            "tech_stack": f"{lang_lower.capitalize()}, {fw_lower.capitalize()}, Node.js",
            "primary_languages": lang_lower.capitalize(),
            "frontend_framework": fw_lower.capitalize(),
            "backend_persistence": "Postgres / Prisma / SQLite",
            "state_management_choice": "Zustand",
            "arch_framework": f"{fw_lower.capitalize()} Clean Architecture",
            "state_management": "Zustand",
            "ui_framework": "Tailwind CSS / Radix UI",
            "ui_kit_reference": "Tailwind CSS / shadcn/ui",
            "decision_1_title": "Adopt Unidirectional State Flow with Zustand",
            "decision_1_logic": "Centralizes transient state without prop-drilling.",
            "decision_1_tradeoffs": "Requires distinct selectors to prevent unnecessary re-renders.",
            "topic_1": "Component Re-render Boundaries",
            "knowledge_1": "Keep selector functions granular to avoid whole-tree re-renders.",
        }
    if fw_lower == "node":
        return {
            "FRAMEWORK": "node",
            "LANGUAGE": lang_lower if lang_lower != "generic" else "typescript",
            "STATE_MANAGEMENT": "modular",
            "MODEL_TYPE": "zod",
            "tech_stack": f"{lang_lower.capitalize()}, Node.js ESM",
            "primary_languages": lang_lower.capitalize(),
            "frontend_framework": "CLI / Headless / API",
            "backend_persistence": "SQLite / Postgres",
            "state_management_choice": "Immutable State Services",
            "arch_framework": "Modular 5-Tier Node.js Architecture",
            "state_management": "Service & State Layer",
            "ui_framework": "CLI / MCP / Web",
            "ui_kit_reference": "Standard Design Tokens",
            "decision_1_title": "Adopt Layered Service Architecture",
            "decision_1_logic": "Decouples business services from HTTP transport and storage.",
            "decision_1_tradeoffs": "Requires dedicated service and repository interfaces.",
            "topic_1": "Service Lifecycle & Disposal",
            "knowledge_1": "Ensure asynchronous handles and db pools gracefully close on SIGTERM.",
        }
    if fw_lower == "python" or lang_lower == "python":
        if target_dir:
            has_ui = _detect_ui_project(target_dir)
            deps = _read_python_deps(target_dir)
            return _python_profile(deps, has_ui=has_ui)
        # Fallback if no target_dir provided
        return {
            "FRAMEWORK": "python",
            "LANGUAGE": "python",
            "STATE_MANAGEMENT": "dataclasses",
            "MODEL_TYPE": "dataclasses",
            "tech_stack": "Python, SQLite",
            "primary_languages": "Python",
            "frontend_framework": "Not detected — fill in manually",
            "backend_persistence": "Persistent Storage / SQLite",
            "state_management_choice": "Dataclasses / Typed Dicts",
            "arch_framework": "Clean Python Architecture",
            "state_management": "Dataclasses / Typed Dicts",
            "ui_framework": "None (headless)",
            "ui_kit_reference": "N/A — headless project",
            "decision_1_title": "Adopt Layered Architecture with Explicit Boundaries",
            "decision_1_logic": "Separates domain logic from I/O for testability.",
            "decision_1_tradeoffs": "Requires disciplined abstraction between layers.",
            "topic_1": "Codebase Invariants & Quirks",
            "knowledge_1": "Document operational runtime quirks and concurrency rules here.",
        }
    return {
        "FRAMEWORK": fw_lower,
        "LANGUAGE": lang_lower,
        "STATE_MANAGEMENT": "modular",
        "MODEL_TYPE": "typed_models",
        "tech_stack": "Modular Architecture",
        "primary_languages": lang_lower.capitalize(),
        "frontend_framework": "Modular Architecture",
        "backend_persistence": "Persistent Storage",
        "state_management_choice": "Predictable State",
        "arch_framework": "Feature-First Clean Architecture",
        "state_management": "Unidirectional State Flow",
        "ui_framework": "Standard UI Kit",
        "ui_kit_reference": "Standard Design System",
        "decision_1_title": "Adopt Layered Architecture with Explicit Boundaries",
        "decision_1_logic": "Separates domain logic from I/O for testability.",
        "decision_1_tradeoffs": "Requires disciplined abstraction between layers.",
        "topic_1": "Codebase Invariants & Quirks",
        "knowledge_1": "Document operational runtime quirks and concurrency rules here.",
    }

TEMPLATE_VARS = {
    "FRAMEWORK": "generic",
    "LANGUAGE": "generic",
    "STATE_MANAGEMENT": "modular",
    "CLI_TEST_COVERAGE": "80%",
    "MODEL_TYPE": "standard",
    "LLM_TIER": "cloud_agent",
    "project_name": "foundation",
    "framework": "generic",
    "language": "generic",
    "primary_stack": "Universal Stack",
    "date": "2026-10-05",
    "timestamp": "2026-10-05T00:00:00Z",
    "timezone": "UTC",
    "current_phase": "Phase 1: Architecture & Design",
    "category_name": "Core",
    "domain_overview": "Domain architecture and strategic objectives.",
    "strategic_insights": "High leverage opportunities and market position.",
    "data_points": "Primary business and technical metrics.",
    "next_actions": "Complete MVP scope and technical verification.",
    "tagline": "Intelligent, autonomous agentic workspace.",
    "core_problem": "Friction and fragmentation in developer workflows.",
    "primary_persona": "Full-stack and mobile engineers.",
    "value_proposition": "Autonomous, verified development workflows.",
    "node_identifier": "foundation-core",
    "etymology": "Core structural baseline.",
    "trinity_keywords": "Autonomy, Verification, Performance",
    "core_intent": "Build rock-solid software systems.",
    "relationship_to_mission": "Foundational architecture layer.",
    "big_claim": "High-fidelity agentic engineering.",
    "dual_lens_concept": "Tactical execution paired with strategic reflection.",
    "first_30_seconds": "Immediate context awareness and zero-friction startup.",
    "retention_strategy": "Self-healing verification gates.",
    "fragmentation_risk": "Isolated sub-modules with divergent conventions.",
    "scale_limitations": "Context window limits and token latency.",
    "security_notes": "Zero hardcoded secrets, strict input validation.",
    "competitor_gap": "Lack of mechanical verification and self-evolving knowledge.",
    "unfair_advantage": "Portable brain graph and deterministic execution loops.",
    "mvp_scope": "End-to-end verification, deterministic routing, and zero data loss.",
    "peak_scope": "Autonomous evolution, multi-agent mesh, and predictive synthesis.",
    "proactive_feature_recommendations": "Continuous background verification and automatic linting.",
    "scalability_roadmap": "Modular expansion into cross-platform spokes.",
    "tech_stack": "Universal Stack",
    "visual_aesthetic": "Modern Bento UI with Spatial Glassmorphism",
    "visual_aesthetic_keywords": "clean, tactile, modern, glassmorphic",
    "database_schema_detail": "Relational/Document storage with integrity checks",
    "shared_services_mapping": "Orion Ops, Heartbeat Monitor, Telemetry Logger",
    "data_flow_hooks": "Pre/Post tool execution hooks",
    "sovereignty_notes": "Local-first execution with zero third-party lock-in",
    "saas_startup_mapping": "Lean 4-Pillar hierarchy",
    "context_mapping_summary": "Strategy, Product, Creative, Tech",
    "structural_pillars_checklist": "8 structural pillars satisfied",
    "primary_languages": "Polyglot",
    "frontend_framework": "Universal UI",
    "backend_persistence": "Database / API Storage",
    "hosting_provider": "Self-hosted / Cloud",
    "folder_architecture_pattern": "Feature-First Clean Architecture",
    "state_management_choice": "Predictable State Management",
    "api_contract_type": "REST / Realtime Channels",
    "auth_strategy": "Standard Auth Strategy",
    "performance_focus": "High throughput and low latency",
    "ci_cd_provider": "GitHub Actions",
    "testing_philosophy": "Strict Test-Driven Development (TDD)",
    "user_name": "Engineer",
    "user_role": "Architect",
    "tier": "Standard",
    "task_id": "INIT-001",
    "task_name": "Project Initialization",
    "priority": "High",
    "top_lessons": "Verify exit codes mechanically.",
    "arch_framework": "Modular Architecture",
    "state_management": "Unidirectional State Flow",
    "database": "Database",
    "ui_framework": "Standard UI",
    "layout_approach": "Responsive Grid & Flexbox",
    "brand_voice": "Technical, precise, confident",
    "primary_palette": "Deep Indigo, Slate Neutral, Cyan Accent",
    "typography_stack": "Inter, Roboto Mono",
    "ui_kit_reference": "Standard Design System",
    "north_star_metric": "Weekly Active Productive Hours",
    "anti_goals": "No slow blocking UI calls, no monolithic single files",
    "out_of_scope_list": "Legacy migrations outside active scope",
    "phase_1_goal": "Foundational architecture and core models",
    "phase_1_timeline": "Sprint 1",
    "phase_2_goal": "Feature implementation and state wiring",
    "phase_2_timeline": "Sprint 2",
    "phase_3_goal": "End-to-end testing and production release",
    "idea_category_summary": "Core concepts and problem discovery.",
    "validation_category_summary": "Customer feedback and demand testing.",
    "planning_category_summary": "Product roadmap and feature priorities.",
    "design_category_summary": "Visual system and component tokens.",
    "development_category_summary": "Application logic and system implementation.",
    "infrastructure_category_summary": "Hosting, storage, and deployment pipelines.",
    "testing_category_summary": "Unit, integration, and security verification.",
    "launch_category_summary": "Release milestones and distribution channels.",
    "acquisition_category_summary": "User discovery and outreach strategies.",
    "distribution_category_summary": "Marketplaces, communities, and partnerships.",
    "conversion_category_summary": "Onboarding and user journey optimization.",
    "revenue_category_summary": "Pricing models and monetization mechanics.",
    "analytics_category_summary": "Metrics, events, and performance tracking.",
    "retention_category_summary": "Engagement loops and churn prevention.",
    "growth_category_summary": "Viral mechanics and referral programs.",
    "scaling_category_summary": "System automation and capacity scaling.",
    "decision_1_title": "Adopt Layered Architecture with Explicit Boundaries",
    "decision_1_logic": "Separates domain logic from I/O for testability.",
    "decision_1_tradeoffs": "Requires disciplined abstraction between layers.",
    "topic_1": "Codebase Invariants & Quirks",
    "knowledge_1": "Document operational runtime quirks and concurrency rules here.",
    "friction_pattern_description": "Manual template variable substitution across fresh spokes.",
    "proposed_automation_fix": "Comprehensive TEMPLATE_VARS substitution engine in foundation.py.",
    "feature_1": "Authentication",
    "feature_2": "Core Dashboard",
    "feature_3": "Data Sync Engine",
    "feature_4": "Audit Verifier",
    "feature_5": "Telemetry Logger",
    "feature_6": "Offline Cache",
    "metric_1": "App startup latency < 1.5s",
    "metric_2": "Zero unhandled exceptions",
    "next_step_1": "Run full test suite",
    "next_step_2": "Deploy to staging",
    "issue_id": "DEBT-001",
    "description": "Clean up unused imports",
    "completed_feature_1": "Project scaffolding",
    "slots": "template slots",
    "x": "example-value",
    "canvas_hex": "#0D0F12",
    "surface_hex": "#16191E",
    "border_hex": "#262B35",
    "text_primary": "#F3F4F6",
    "text_muted": "#9CA3AF",
    "accent_hex": "#3B82F6",
    "display_font": "Space Grotesk",
    "body_font": "Inter",
    "mono_font": "JetBrains Mono",
    "nav_patterns": "Command Palette + Sidebar Master-Detail",
    "archetype_name": "Dark Industrial",
    "macrostructure_name": "Data-Dense Cockpit",
    "brand_voice": "Technical, precise, and terse engineering prose",
}

def resolve_template_string(content: str, manifest: dict, project_name: str = "") -> str:
    framework = manifest.get("framework") or TEMPLATE_VARS.get("FRAMEWORK")
    language = manifest.get("language") or TEMPLATE_VARS.get("LANGUAGE")
    
    new_content = content
    if project_name:
        new_content = new_content.replace("{project_name}", project_name).replace("{{PROJECT_NAME}}", project_name).replace("{{project_name}}", project_name)

    if framework:
        # Prevent broken links by checking if the ecosystem canon directory exists in the active foundation
        foundation_ecosystems_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "canons", "ecosystems")
        canon_fw = framework.lower()
        if not os.path.isdir(os.path.join(foundation_ecosystems_dir, canon_fw)):
            # If the detected framework has no canon directory, fallback to "generic" or keep a placeholder?
            # Actually, the template uses {{FRAMEWORK}} in file paths. If the directory doesn't exist, we can fallback to the most generic available, e.g. python, or just leave it as is but warn.
            # A better approach: fallback to the default "python" or "react" for generic code if we want, or create an empty directory? No, let's fallback to "python" since it has standard recipes, or just omit replacing to let verify fail loudly?
            # Actually, `verify_agents` complains about Ghost path reference. Let's just create the missing framework directory and empty files to satisfy the references. Or we can just fallback to "python" or "react" if it's JS.
            if canon_fw in ["node", "express", "vue", "svelte"]:
                canon_fw = "react" # fallback for JS/TS
            else:
                canon_fw = "python" # generic fallback

        new_content = new_content.replace("{{FRAMEWORK}}", canon_fw).replace("{{framework}}", canon_fw)
    if language:
        new_content = new_content.replace("{{LANGUAGE}}", language).replace("{{language}}", language)
        
    primary_stack = manifest.get("primary_stack") or manifest.get("tech_stack") or TEMPLATE_VARS.get("primary_stack", "Universal Stack")
    new_content = new_content.replace("{{PRIMARY_STACK}}", primary_stack).replace("{{primary_stack}}", primary_stack)

    # Derive package file & ecosystem tools
    fw_lower = (framework or "flutter").lower()
    lang_lower = (language or "dart").lower()
    if fw_lower == "flutter" or lang_lower == "dart":
        pkg_file, pkg_mgr, test_cmd = "pubspec.yaml", "flutter pub", "flutter test"
    elif fw_lower in ["react", "next", "node"] or lang_lower in ["javascript", "typescript"]:
        pkg_file, pkg_mgr, test_cmd = "package.json", "npm", "npm test"
    elif lang_lower == "python":
        pkg_file, pkg_mgr, test_cmd = "requirements.txt", "pip", "pytest"
    elif lang_lower == "rust":
        pkg_file, pkg_mgr, test_cmd = "Cargo.toml", "cargo", "cargo test"
    else:
        pkg_file, pkg_mgr, test_cmd = "package.json", "npm", "npm test"

    new_content = new_content.replace("{{PACKAGE_FILE}}", pkg_file)
    new_content = new_content.replace("{{PACKAGE_MANAGER}}", pkg_mgr)
    new_content = new_content.replace("{{TEST_RUNNER}}", test_cmd)
        
    llm_profile = manifest.get("llm_profile", {})
    if llm_profile:
        new_content = new_content.replace("{{LLM_TIER}}", llm_profile.get("intelligence_tier", "cloud_agent"))

    effective_vars = dict(TEMPLATE_VARS)
    effective_vars.update(manifest)

    for var_key, default_val in effective_vars.items():
        placeholder_curly = "{{" + var_key + "}}"
        if placeholder_curly in new_content:
            val = manifest.get(var_key) or default_val
            new_content = new_content.replace(placeholder_curly, str(val))

    for m in re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", new_content):
        if m in effective_vars:
            new_content = new_content.replace("{{" + m + "}}", str(effective_vars[m]))
            
    return new_content


def resolve_templates(target_dir, manifest, target_files=None):
    if target_files is None:
        target_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".md"):
                    target_files.append(os.path.join(root, file))
    else:
        target_files = [os.path.join(target_dir, f) for f in target_files]
        
    project_name = os.path.basename(os.path.abspath(target_dir))

    # Pull target_dir context if present in manifest
    ctx_target_dir = manifest.get("_target_dir") or target_dir
    stack_vars = get_stack_defaults(manifest.get("framework"), manifest.get("language"), target_dir=ctx_target_dir)
    effective_manifest = dict(manifest)
    for k, v in stack_vars.items():
        if k not in effective_manifest or not effective_manifest[k]:
            effective_manifest[k] = v

    for filepath in target_files:
        if not os.path.exists(filepath):
            continue
        norm_path = filepath.replace('\\', '/')
        is_template_definition = "/templates/" in norm_path or norm_path.endswith("/templates")
        if is_template_definition:
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = resolve_template_string(content, effective_manifest, project_name)
            if new_content != content:
                atomic_write_text(filepath, new_content)
        except Exception as e:
            print(f"    [WARNING] Failed to resolve templates in {filepath}: {e}")

def get_foundation_path(target_root):
    marker = os.path.join(target_root, ".agents", ".foundation_path")
    if os.path.exists(marker):
        with open(marker, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def load_deployed_ais(target_root):
    marker = os.path.join(target_root, ".agents", ".deployed_ais")
    if os.path.exists(marker):
        try:
            with open(marker, "r", encoding="utf-8") as f:
                return json.load(f).get("deployed_ais", [])
        except Exception as _e:
            _log_telemetry(_e, 'foundation.py:337')
    return None

def detect_active_ais(target_root):
    """Smart-detect active AI/IDE environments in target directory based on filesystem markers."""
    detected = set()

    # Check previously deployed tracking
    deployed = load_deployed_ais(target_root)
    if deployed:
        return [ai for ai in deployed if ai in AI_CONFIGS or ai == "agents"]

    # Filesystem markers
    if os.path.exists(os.path.join(target_root, ".gemini")) or os.path.exists(os.path.join(target_root, "GEMINI.md")):
        detected.add("gemini")
    if os.path.exists(os.path.join(target_root, ".claude")) or os.path.exists(os.path.join(target_root, "CLAUDE.md")):
        detected.add("claude")
    if os.path.exists(os.path.join(target_root, ".cursor")) or os.path.exists(os.path.join(target_root, ".cursorrules")):
        detected.add("cursor")
    if os.path.exists(os.path.join(target_root, ".windsurf")) or os.path.exists(os.path.join(target_root, ".windsurfrules")):
        detected.add("windsurf")
    if os.path.exists(os.path.join(target_root, ".clinerules")):
        detected.add("cline")
    if os.path.exists(os.path.join(target_root, ".github", "copilot-instructions.md")):
        detected.add("copilot")

    # Default to single canonical instruction file based on detected environment
    if not detected:
        detected.add("agents")

    return sorted(list(detected))

def smart_merge_config(template_content, target_path, project_name, fmt, dry_run, manifest):
    content = resolve_template_string(template_content, manifest, project_name)
    if manifest:
        for var_key, default_val in TEMPLATE_VARS.items():
            placeholder_curly = "{{" + var_key + "}}"
            if placeholder_curly in content:
                val = manifest.get(var_key) or default_val
                content = content.replace(placeholder_curly, str(val))
    
    merge_status = "Deployed (Fresh)"
    
    if os.path.exists(target_path):
        with open(target_path, "r", encoding="utf-8") as f:
            old_content = f.read()
            
        if not dry_run:
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            shutil.copy2(target_path, target_path + "." + ts + ".bak")
            
        marker = "<!-- END FOUNDATION MANDATES -->"
        idx = old_content.find(marker)
        if idx != -1:
            user_content = old_content[idx + len(marker):].strip()
            idx_new = content.find(marker)
            if idx_new != -1:
                base_new = content[:idx_new + len(marker)]
                content = base_new + "\n\n" + user_content + "\n"
                merge_status = "Merged (Preserved user config)"
            else:
                content += "\n\n" + user_content + "\n"
                merge_status = "Merged (Preserved user config, marker missing in template)"
        else:
            # Marker not found, preserve the entire old config if not already present to avoid data loss / infinite duplication
            if content.strip() in old_content:
                content = old_content
                merge_status = "Unchanged (Template already present)"
            elif old_content.strip() in content:
                merge_status = "Unchanged (Already up to date)"
            else:
                content += "\n\n" + old_content + "\n"
                merge_status = "Merged (Appended missing marker config)"

    if not dry_run:
        atomic_write_text(target_path, content)
    return content, merge_status

# Folders that represent "The Brain" and should evolve
EVOLVABLE_FOLDERS = ["skills", "rules", "canons", "templates", "scripts", "evals", "docs", "hooks"]
ROOT_SYNC_FILES = ["DEPLOY_ME.md", "AGENTS_INDEX.md", "hooks.json", ".security-baseline.json"]
SEED_FILES = [
    "context/VISION.md",
    "context/00_Strategy/BLUEPRINT.md",
    "context/00_Strategy/MEMORY.md",
    "context/01_Product/ROADMAP.md",
    "context/02_Creative/STYLE_GUIDE.md",
    "context/03_Tech/ARCHITECTURE.md",
    "context/AGENT_IDENTITY.md",
    "context/README.md"
]
SEED_FILE_MAP = {
    "context/VISION.md": ".agents/templates/VISION.template.md",
    "context/00_Strategy/BLUEPRINT.md": ".agents/templates/PROJECT_SCAFFOLD.template.md",
    "context/00_Strategy/MEMORY.md": ".agents/templates/MEMORY.template.md",
    "context/01_Product/ROADMAP.md": ".agents/templates/TASK_PLANNING.template.md",
    "context/02_Creative/STYLE_GUIDE.md": ".agents/templates/STYLE_GUIDE.template.md",
    "context/03_Tech/ARCHITECTURE.md": ".agents/templates/PROJECT_SCAFFOLD.template.md",
    "context/AGENT_IDENTITY.md": ".agents/templates/agent-identity-template.md",
}
VERSION_BUMP_FILES = {"SKILL.md"}
BLACKLIST = {
    "local", "tasks", "personal", "debug_scripts",
    "pull_planning_context.py", ".git", "node_modules",
    "__pycache__", "vitals", "MEMORY.md", "SAAS_MEMORY.md",
    "EVOLUTION_LOG.jsonl", ".project_manifest.json",
    ".foundation_path", ".deployed_ais", ".genome.json",
    ".sidecar.json", ".ledger.jsonl"
}

# === DEPLOY ===


def cmd_deploy(args):
    # args.target, args.framework, args.language, args.dry_run
    target_dir = os.path.abspath(args.target)
    foundation_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    target_agents_dir = os.path.join(target_dir, ".agents")
    
    # Auto-detect framework & language if omitted
    framework = args.framework
    language = args.language
    if not framework or not language:
        det_fw, det_lang = detect_stack(target_dir)
        framework = framework or det_fw
        language = language or det_lang
        print(f"  -> Stack Auto-Detected: framework='{framework}', language='{language}'")
    
    try:
        from core.capabilities import probe_capabilities
        caps = probe_capabilities(force_refresh=True)
        pillars = caps.get("pillars", {})
        p1 = pillars.get("pillar_1", {})
        p2 = pillars.get("pillar_2", {})
        p3 = pillars.get("pillar_3", {})
        p4 = pillars.get("pillar_4", {})
        print(f"  -> Host Capabilities: P1 (Python): {p1.get('status', 'OK')} ({p1.get('details', '')}) | P2 (Rust): {p2.get('status', 'FALLBACK')} ({p2.get('details', '')}) | P3 (Ollama): {p3.get('status', 'FALLBACK')} | P4 (Bun): {p4.get('status', 'FALLBACK')} ({p4.get('details', '')})")
    except Exception as _pe:
        _log_telemetry(_pe, "cmd_deploy:capabilities")

    try:
        from core.platform_manifests import is_flutterin_installed
        fl_detected = is_flutterin_installed(target_dir)
        if fl_detected:
            print("  -> Reverse-Engineering: Flutterin suite detected on system (Auto-linking MCP bridge)")
        else:
            print("  -> Reverse-Engineering: Flutterin not detected (Lean mode, optional external suite)")
    except Exception as _fe:
        _log_telemetry(_fe, "cmd_deploy:flutterin_check")
    
    if args.dry_run:
        print(f"[DRY RUN] Deploying Foundation to: {target_dir}")
        print(f"[DRY RUN] Framework: {framework}, Language: {language}")
    else:
        print(f"Deploying Foundation to: {target_dir}")
        print(f"Framework: {framework}, Language: {language}")

    os.makedirs(target_agents_dir, exist_ok=True)
    
    manifest_path = os.path.join(target_agents_dir, ".project_manifest.json")
    llm_tier = "cloud_agent"
    if args.use_local_llm or args.llm_params > 0:
        if args.llm_params >= 30:
            llm_tier = "high_intelligence"
        elif args.llm_params >= 8:
            llm_tier = "medium_intelligence"
        elif args.llm_params > 0:
            llm_tier = "low_intelligence"
        else:
            llm_tier = "unknown_local"

    stack_vars = get_stack_defaults(framework, language, target_dir=target_dir)
    workspaces = scan_monorepo_workspaces(target_dir)
    manifest = {
        "framework": framework,
        "language": language,
        "workspaces": workspaces,
        "ecosystem": get_ecosystem_config(foundation_dir, framework),
        "llm_profile": {
            "is_local": args.use_local_llm or args.llm_params > 0,
            "parameters_b": args.llm_params,
            "intelligence_tier": llm_tier
        },
        **stack_vars
    }
    
    print(f"  -> LLM Profile: {llm_tier} (Local: {args.use_local_llm}, Params: {args.llm_params}B)")
    
    if not args.dry_run:
        atomic_write_text(manifest_path, json.dumps(manifest, indent=2))
        print(f"  -> Created {manifest_path}")
        
        genome_path = os.path.join(target_agents_dir, ".genome.json")
        atomic_write_text(genome_path, json.dumps({"evolution_count": 0, "daily_mutation_cap": 10}, indent=2))

        dna_path = os.path.join(target_agents_dir, ".dna.json")
        try:
            scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from core.dna import build_initial_dna_manifest, sequence_project_dna
            dna_data = build_initial_dna_manifest(framework, language, target_dir)
            seq_dna = sequence_project_dna(target_dir)
            has_brownfield_code = bool(
                seq_dna and any(t != "0_pillars_and_manifests" for t in seq_dna.file_tier_map.values())
            )
            if seq_dna and has_brownfield_code:
                dna_data["dna_state"] = "MUTATING" if seq_dna.epigenetic_aliases else "BORN"
                dna_data["origin"] = "brownfield_mutation" if seq_dna.epigenetic_aliases else "foundation_init"
                dna_data["archetype"] = seq_dna.archetype
                dna_data["stacks"] = seq_dna.stacks
                dna_data["execution_spine"] = seq_dna.execution_spine
                dna_data["dna_compliance_score"] = seq_dna.dna_compliance_score
                dna_data["epigenetic_aliases"] = seq_dna.epigenetic_aliases
                dna_data["layer_violations"] = seq_dna.layer_violations[:15]
                dna_data["mutation_ledger"]["epigenetic_aliases"] = seq_dna.epigenetic_aliases
                dna_data["mutation_ledger"]["dna_compliance_score"] = seq_dna.dna_compliance_score
                dna_data["mutation_ledger"]["layer_violations"] = seq_dna.layer_violations[:15]
        except Exception as _de:
            _log_telemetry(_de, "cmd_deploy:build_dna_manifest")
            dna_data = {
                "schema_version": "0.0.1",
                "dna_state": "BORN",
                "framework": framework,
                "language": language,
                "deployed_at": datetime.now(timezone.utc).isoformat(),
                "pillars": {
                    "tech": "context/03_Tech/ARCHITECTURE.md"
                }
            }
        atomic_write_text(dna_path, json.dumps(dna_data, indent=2))
        print(f"  -> Created {dna_path} (Living Architectural DNA: {dna_data.get('dna_state', 'BORN')})")
    else:
        print(f"  [SIMULATED] -> Created {manifest_path} with ecosystem variables")
        print(f"  [SIMULATED] -> Created .dna.json specification")

    marker_path = os.path.join(target_agents_dir, ".foundation_path")
    if not args.dry_run:
        atomic_write_text(marker_path, foundation_dir)
        print(f"  -> Created {marker_path}")
    else:
        print(f"  [SIMULATED] -> Created {marker_path}")

    deploy_ignore = shutil.ignore_patterns(
        "internal", "local", ".archive", "archive", "scratch", "teamwork",
        "__pycache__", "*.pyc", ".sidecar.json", ".ledger.jsonl"
    )
    is_same_target = os.path.abspath(target_dir) == os.path.abspath(foundation_dir)

    for folder in EVOLVABLE_FOLDERS:
        src = os.path.join(foundation_dir, ".agents", folder)
        dest = os.path.join(target_agents_dir, folder)
        if os.path.exists(src):
            if not args.dry_run:
                if not is_same_target:
                    shutil.copytree(src, dest, dirs_exist_ok=True, ignore=deploy_ignore)
                    resolve_templates(dest, manifest)
            else:
                print(f"  [SIMULATED] -> Copied & Resolved Templates for {folder}/")

    if not args.dry_run:
        prune_unmatched_canons(target_agents_dir, framework)

    for root_file in ROOT_SYNC_FILES:
        src_root = os.path.join(foundation_dir, ".agents", root_file)
        dest_root = os.path.join(target_agents_dir, root_file)
        if os.path.exists(src_root):
            if not args.dry_run:
                shutil.copy2(src_root, dest_root)
            else:
                print(f"  [SIMULATED] -> Copied {root_file}")

    for seed_file in SEED_FILES:
        if seed_file.startswith(".agents/"):
            dest_seed = os.path.join(target_agents_dir, seed_file.replace(".agents/", ""))
        else:
            dest_seed = os.path.join(target_dir, seed_file)
            
        src_seed = None
        template_rel = SEED_FILE_MAP.get(seed_file)
        if template_rel:
            candidate = os.path.join(foundation_dir, template_rel)
            if os.path.exists(candidate):
                src_seed = candidate
        if not src_seed:
            candidate = os.path.join(foundation_dir, seed_file)
            if os.path.exists(candidate):
                src_seed = candidate

        if src_seed and os.path.exists(src_seed):
            if not os.path.exists(dest_seed):
                if not args.dry_run:
                    parent_dir = os.path.dirname(dest_seed)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    shutil.copy2(src_seed, dest_seed)
                    if seed_file.startswith(".agents/"):
                        rel_seed = seed_file.replace(".agents/", "")
                        resolve_templates(target_agents_dir, manifest, target_files=[rel_seed])
                    else:
                        resolve_templates(target_dir, manifest, target_files=[seed_file])
                    print(f"  -> Seeded {seed_file}")
                else:
                    print(f"  [SIMULATED] -> Seeded {seed_file}")
            else:
                if not args.dry_run:
                    print(f"  -> Preserved existing {seed_file}")

    template_dir = os.path.join(foundation_dir, ".agents", "templates")
    if os.path.exists(template_dir):
        if not args.dry_run:
            target_template_dir = os.path.join(target_agents_dir, "templates")
            os.makedirs(target_template_dir, exist_ok=True)
            ai_brands_path = os.path.join(foundation_dir, ".agents", "canons", "global", "ai_brands.json")
            if os.path.exists(ai_brands_path):
                with open(ai_brands_path, "r", encoding="utf-8") as f:
                    ai_brands = json.load(f)
                
                ai_arg = getattr(args, "ai", "auto")
                if not ai_arg or ai_arg.lower() == "auto":
                    selected_ais = detect_active_ais(target_dir)
                    print(f"  -> Smart-detected active AIs: {', '.join(selected_ais)}")
                elif ai_arg.lower() == "all":
                    selected_ais = list(ai_brands.keys())
                else:
                    selected_ais = [x.strip() for x in ai_arg.split(",") if x.strip()]
                deployed_ais_list = []
                
                for ai_name, brand in ai_brands.items():
                    if ai_name not in selected_ais:
                        continue
                    
                    deployed_ais_list.append(ai_name)
                    template_name = brand.get("template")
                    target_filename = brand.get("target_path")
                    
                    src_template = os.path.join(template_dir, template_name)
                    dest_template = os.path.join(target_template_dir, template_name)
                    
                    if os.path.exists(src_template):
                        shutil.copy2(src_template, dest_template)
                        resolve_templates(target_template_dir, manifest, target_files=[template_name])
            else:
                print("    [WARNING] ai_brands.json not found. Skipping root AI config propagation.")
            
            try:
                deployed_file = os.path.join(target_agents_dir, ".deployed_ais")
                project_name = os.path.basename(os.path.abspath(target_dir))
                atomic_write_text(deployed_file, json.dumps({
                    "project_name": project_name, 
                    "deployed_ais": deployed_ais_list,
                    "sync_results": {ai: {"status": "SUCCESS", "message": "Deployed"} for ai in deployed_ais_list}
                }, indent=2))
            except Exception as e:
                print(f"    [WARNING] Could not write .deployed_ais: {e}")
                
            if not args.dry_run and deployed_ais_list:
                sync_ai_configs(
                    target_dir,
                    selected_ais=deployed_ais_list,
                    dry_run=args.dry_run,
                    include_flutterin=getattr(args, "with_flutterin", None),
                )
                
        else:
            print("  [SIMULATED] -> Processed Templates and propagated root AI configs")

    if not args.dry_run:
        print("  -> Initializing Orion Brain Graph...")
        orion_script = os.path.join(foundation_dir, ".agents", "scripts", "orion.py")
        if os.path.exists(orion_script):
            try:
                # 1. Initialize empty Graph Database
                subprocess.run([sys.executable, orion_script, "orion_ops", "init"], cwd=target_dir, check=True)
                
                # 2. Scaffold Base Context Directory to prevent amnesia
                context_dir = os.path.join(target_dir, "context")
                os.makedirs(context_dir, exist_ok=True)
                
                # Clean up legacy context/context.json if present (enforces 82-file boundary)
                legacy_context_json = os.path.join(context_dir, "context.json")
                if os.path.exists(legacy_context_json):
                    try:
                        os.remove(legacy_context_json)
                    except Exception as _e:
                        _log_telemetry(_e, "remove_legacy_context_json")

                # Ensure Omni-Buffer is present in .orion/working/context.json
                orion_working_dir = os.path.join(target_dir, ".orion", "working")
                os.makedirs(orion_working_dir, exist_ok=True)
                omni_buffer = os.path.join(orion_working_dir, "context.json")
                if not os.path.exists(omni_buffer):
                    atomic_write_text(omni_buffer, json.dumps({
                        "active_document": "",
                        "cursor_line": "1",
                        "evolution_overdue": False,
                        "drift_warnings": [],
                        "harness_skill_index": {},
                        "harness_lifecycle": {},
                        "state": "init",
                        "memory": []
                    }, indent=2))
                        
                readme_md = os.path.join(target_dir, "README.md")
                if not os.path.exists(readme_md):
                    atomic_write_text(readme_md, f"# {os.path.basename(os.path.abspath(target_dir))}\n\nProject initialized by Portable Brainvibing.\n")

                # 3. Auto-Hydrate Graph with Rules, Skills, and Context
                print("  -> Auto-Hydrating Rules & Context into Brain Graph...")
                subprocess.run([sys.executable, orion_script, "orion_ops", "ingest", ".agents/rules", ".agents/skills", "context", "README.md"], cwd=target_dir, check=True)
                
            except Exception as e:
                print(f"    [WARNING] Failed to initialize Orion Brain Graph: {e}")
        else:
            print(f"    [WARNING] orion.py not found at {orion_script}")

    # 4. Proactive Git Hooks
    git_hooks_dir = os.path.join(target_dir, ".git", "hooks")
    if os.path.exists(git_hooks_dir):
        pre_commit_path = os.path.join(git_hooks_dir, "pre-commit")
        pre_commit_script = "#!/bin/sh\n# Pre-commit secret scanning gatekeeper\npython .agents/scripts/orion.py scan security . || exit 1\n"
        post_commit_path = os.path.join(git_hooks_dir, "post-commit")
        hook_script = "#!/bin/sh\n# Auto-sync Orion Brain Graph after commit\npython .agents/scripts/orion.py brain sync \"post-commit auto sync\" >/dev/null 2>&1 &\n"
        if not args.dry_run:
            try:
                # Pre-commit hook
                if not os.path.exists(pre_commit_path):
                    atomic_write_text(pre_commit_path, pre_commit_script)
                    if os.name != 'nt':
                        os.chmod(pre_commit_path, 0o755)
                    print(f"  -> Injected pre-commit Git hook at {pre_commit_path}")

                existing_hook = ""
                if os.path.exists(post_commit_path):
                    with open(post_commit_path, "r", encoding="utf-8") as f:
                        existing_hook = f.read()
                
                if "orion.py brain sync" not in existing_hook:
                    with open(post_commit_path, "a" if existing_hook else "w", encoding="utf-8", newline="\n") as f:
                        if not existing_hook:
                            f.write(hook_script)
                        else:
                            f.write("\n# Auto-sync Orion Brain Graph after commit\npython .agents/scripts/orion.py brain sync \"post-commit auto sync\" >/dev/null 2>&1 &\n")
                    
                    if os.name != 'nt':
                        os.chmod(post_commit_path, 0o755)
                    print(f"  -> Injected post-commit Git hook at {post_commit_path}")
            except Exception as e:
                print(f"    [WARNING] Failed to inject Git hooks: {e}")
        else:
            print("  [SIMULATED] -> Injected pre-commit and post-commit Git hooks")
    else:
        print(f"    [WARNING] Target is not a Git repository (.git not found). Post-commit hooks will not be active.")

    print("\nDeployment Complete!")
    print("AI Agents in the target project are now connected to the Foundation.")
    print("⚡ [RECOMMENDED TIER: BUDGET] — Deploy operations are batch tasks. Switch back to Budget model for subsequent operations.")

# === PUSH UPSTREAM ===
def increment_patch_version(content):
    """
    Finds 'version: "x.y.z"' or 'version: x.y.z' and increments z.
    """
    version_pattern = r'^(version:\s*["\']?)(\d+\.\d+\.)(\d+)(["\']?)$'
    
    def replace_version(match):
        prefix = match.group(1)
        base = match.group(2)
        patch = int(match.group(3))
        suffix = match.group(4)
        return f"{prefix}{base}{patch + 1}{suffix}"

    new_content, count = re.subn(version_pattern, replace_version, content, flags=re.MULTILINE)
    return new_content, count > 0


def extract_semver(content: str):
    """Extract (major, minor, patch) from content if present."""
    m = re.search(r'(?:version|Version|Version:)\s*[:=]?\s*["\']?(\d+)\.(\d+)\.(\d+)', content)
    if m:
        try:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except (ValueError, TypeError):
            return None
    return None



def resolve_foundation_agents(project_agents: str) -> str:
    """
    Resolve target foundation .agents path from marker file when available.
    Supports marker values that point either to foundation root OR directly to .agents.
    """
    foundation_path_marker = os.path.join(project_agents, ".foundation_path")

    if not os.path.exists(foundation_path_marker):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".agents")

    with open(foundation_path_marker, "r", encoding="utf-8") as f:
        marker_path = f.read().strip()

    marker_path = os.path.abspath(marker_path)

    # Case A: marker already points to .agents directory.
    if os.path.basename(marker_path).lower() == ".agents":
        return marker_path

    # Case B: marker points to foundation root.
    return os.path.join(marker_path, ".agents")


def files_differ(src: str, dest: str) -> bool:
    if not os.path.exists(dest):
        return True
    with open(src, "rb") as f:
        src_bytes = f.read()
    with open(dest, "rb") as f:
        dest_bytes = f.read()
    return src_bytes != dest_bytes


def copy_with_optional_version_bump(local_file: str, foundation_file: str, file_name: str, dry_run: bool) -> bool:
    """
    Copy local file to foundation path. Returns True if a version bump happened.
    """
    if dry_run:
        return False

    os.makedirs(os.path.dirname(foundation_file), exist_ok=True)

    if file_name in VERSION_BUMP_FILES:
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, bumped = increment_patch_version(content)

            atomic_write_text(foundation_file, new_content)

            return bumped
        except Exception as e:
            print(f"    [WARNING] Could not auto-bump {file_name}: {e}")
            shutil.copy2(local_file, foundation_file)
            return False

    shutil.copy2(local_file, foundation_file)
    return False


def _sanitize_for_foundation(text: str, project_root: str) -> str:
    """
    Strips local file paths, usernames, and project specific tokens for Foundation generalisation.
    """
    if not text:
        return ""
    norm_root = project_root.replace("\\", "/").rstrip("/")
    s = text.replace("\\", "/")
    if norm_root:
        s = s.replace(norm_root, ".")
    # Strip drive letters and local absolute path prefixes
    s = re.sub(r"[A-Za-z]:/[^\s\)\]\"']+", lambda m: m.group(0).split("/")[-1], s)
    # Strip file URI schemes
    file_uri_prefix = "file:" + "///"
    s = re.sub(re.escape(file_uri_prefix) + r"[^\s\)\]\"']+", lambda m: m.group(0).split("/")[-1], s)
    return s.strip()


def sync_upstream_observations(
    project_root: str,
    project_agents: str,
    foundation_agents: str,
    dry_run: bool = False
) -> Tuple[int, int]:
    """
    Section 4c Cross-Project Merging:
    Merges 'scope: foundation' observations from spoke's OBSERVATIONS.md into Hub's OBSERVATIONS.md.
    - Matches by fingerprint: bumps count, adds opaque spoke alias to seen_in (e.g. p_a1b2c3), appends applies_to.
    - If count >= 2, flags as cross-project rule/skill candidate.
    - Strips local paths, project names, and raw evidence.
    Returns (created_count, updated_count).
    """
    spoke_obs_path = os.path.join(project_agents, "OBSERVATIONS.md")
    hub_obs_path = os.path.join(foundation_agents, "OBSERVATIONS.md")
    if not os.path.exists(spoke_obs_path):
        return (0, 0)

    try:
        from commands.reflexion import ObservationLedger
    except ImportError:
        try:
            from .reflexion import ObservationLedger
        except ImportError:
            return (0, 0)

    abs_proj = os.path.abspath(project_root).lower().replace("\\", "/")
    spoke_id = f"p_{hashlib.sha256(abs_proj.encode('utf-8')).hexdigest()[:6]}"

    spoke_applies_to = ""
    dna_candidates = [
        os.path.join(project_agents, ".dna.json"),
        os.path.join(project_root, ".dna.json")
    ]
    for dp in dna_candidates:
        if os.path.exists(dp):
            try:
                with open(dp, "r", encoding="utf-8", errors="ignore") as f:
                    dna_data = json.load(f)
                    spoke_applies_to = dna_data.get("primary_framework") or dna_data.get("framework") or ""
                    if not spoke_applies_to and dna_data.get("stacks"):
                        spoke_applies_to = dna_data["stacks"][0].lower().split("/")[0]
            except Exception as _de:
                _log_telemetry(_de, "foundation:read_spoke_dna")
            if spoke_applies_to:
                break

    spoke_archive_path = os.path.join(project_agents, "OBSERVATIONS.archive.md")
    hub_archive_path = os.path.join(foundation_agents, "OBSERVATIONS.archive.md")

    spoke_ledger = ObservationLedger(active_path=spoke_obs_path, archive_path=spoke_archive_path)
    spoke_entries = spoke_ledger.get_all_observations()

    foundation_entries = [e for e in spoke_entries if str(e.get("scope", "")).lower() == "foundation"]
    if not foundation_entries:
        return (0, 0)

    hub_ledger = ObservationLedger(active_path=hub_obs_path, archive_path=hub_archive_path)
    hub_active = hub_ledger.get_all_observations()
    hub_archive = hub_ledger.get_archive_observations()
    all_hub = hub_active + hub_archive

    fp_to_hub_active = {e.get("fingerprint"): e for e in hub_active if e.get("fingerprint")}
    fp_to_hub_all = {e.get("fingerprint"): e for e in all_hub if e.get("fingerprint")}

    created_count = 0
    updated_count = 0

    for entry in foundation_entries:
        kind = entry.get("kind", "improve")
        raw_rule = entry.get("rule_id") or entry.get("target", "")
        raw_title = entry.get("title", "")

        clean_title = _sanitize_for_foundation(raw_title, project_root)
        clean_target = _sanitize_for_foundation(entry.get("target", ""), project_root)
        clean_rule = _sanitize_for_foundation(entry.get("rule_id", ""), project_root)
        clean_target_or_rule = clean_rule if clean_rule else clean_target
        clean_evidence = _sanitize_for_foundation(entry.get("evidence", ""), project_root)

        fp = entry.get("fingerprint")
        if not fp:
            fp = hub_ledger.compute_fingerprint(kind, clean_target_or_rule, clean_title)

        spoke_count = int(entry.get("count", 1))

        if fp in fp_to_hub_active:
            target_item = fp_to_hub_active[fp]
            target_item["count"] = int(target_item.get("count", 1)) + spoke_count

            seen_set = set(s.strip() for s in str(target_item.get("seen_in", "")).split(",") if s.strip())
            seen_set.add(spoke_id)
            target_item["seen_in"] = ", ".join(sorted(seen_set))

            if spoke_applies_to:
                app_set = set(a.strip() for a in str(target_item.get("applies_to", "")).split(",") if a.strip())
                app_set.add(spoke_applies_to)
                target_item["applies_to"] = ", ".join(sorted(app_set))

            if len(seen_set) >= 2 or int(target_item["count"]) >= 2:
                if not target_item["title"].startswith("[CROSS-PROJECT CANDIDATE]"):
                    target_item["title"] = f"[CROSS-PROJECT CANDIDATE] {target_item['title']}".replace("[CROSS-PROJECT CANDIDATE] [CROSS-PROJECT CANDIDATE]", "[CROSS-PROJECT CANDIDATE]")

            updated_count += 1
        elif fp not in fp_to_hub_all:
            next_id = hub_ledger.get_next_id() + created_count
            new_item = {
                "id": next_id,
                "fingerprint": fp,
                "title": clean_title,
                "status": "open",
                "kind": kind,
                "target": clean_target,
                "rule_id": clean_rule,
                "siblings_checked": entry.get("siblings_checked", "true"),
                "scope": "foundation",
                "parked_until": "",
                "evidence": clean_evidence,
                "created": datetime.now().isoformat(),
                "resolved": "",
                "resolution": "",
                "count": spoke_count,
                "seen_in": spoke_id,
                "applies_to": spoke_applies_to
            }
            hub_active.append(new_item)
            fp_to_hub_active[fp] = new_item
            fp_to_hub_all[fp] = new_item
            created_count += 1

    if not dry_run and (created_count > 0 or updated_count > 0):
        hub_ledger._write_active_list(hub_active)

    return (created_count, updated_count)


def cmd_upstream(args):
    """
    Sync local project changes back to Foundation hub.
    Honors --project, --dry-run, and --force-hub-override.
    """
    project_root = getattr(args, "project", ".")
    dry_run = getattr(args, "dry_run", False)
    force_hub = getattr(args, "force_hub_override", False)

    project_agents = os.path.join(project_root, ".agents")
    if not os.path.exists(project_agents):
        print(f"[ERROR] Target project .agents directory not found: {project_agents}", file=sys.stderr)
        return False

    foundation_agents = resolve_foundation_agents(project_agents)
    if not os.path.exists(foundation_agents):
        print(f"[ERROR] Foundation .agents target not found: {foundation_agents}", file=sys.stderr)
        return False

    print("========================================")
    print(" 🔄 SYNCING LOCAL ASSETS TO FOUNDATION ")
    print("========================================")
    print(f"Source Spoke:     {os.path.abspath(project_agents)}")
    print(f"Target Hub:       {os.path.abspath(foundation_agents)}")
    print(f"Dry Run:          {dry_run}")
    print(f"Force Hub Override: {force_hub}")
    print("----------------------------------------")

    synced_count = 0
    bumped_count = 0

    filter_paths = [
        p.replace("\\", "/").removeprefix(".agents/").lstrip("/")
        for p in (getattr(args, "paths", []) or [])
    ]
    git_diff_only = getattr(args, "git_diff", False)
    if git_diff_only:
        try:
            import subprocess
            out = subprocess.check_output(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=project_root,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            for line in out.splitlines():
                line = line.strip().replace("\\", "/")
                if line.startswith(".agents/"):
                    filter_paths.append(line.removeprefix(".agents/").lstrip("/"))
        except (subprocess.SubprocessError, OSError):
            pass

    # Sync evolvable directories: skills, rules, canons, templates, evals, docs, hooks (+ optionally scripts)
    sync_dirs = [d for d in EVOLVABLE_FOLDERS if d != "scripts"]
    if getattr(args, "include_scripts", False) or any(p.startswith("scripts") for p in filter_paths):
        sync_dirs.append("scripts")
    for d in sync_dirs:
        src_dir = os.path.join(project_agents, d)
        if not os.path.exists(src_dir):
            continue
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [sub_d for sub_d in dirs if sub_d not in BLACKLIST]
            rel_dir = os.path.relpath(root, project_agents)
            if any(part in BLACKLIST for part in rel_dir.replace("\\", "/").split("/")):
                continue
            dest_dir = os.path.join(foundation_agents, rel_dir)
            for f in files:
                if f in BLACKLIST or f.endswith((".sidecar.json", ".ledger.jsonl")) or f.startswith("."):
                    continue
                rel_path = os.path.join(rel_dir, f).replace("\\", "/")
                if filter_paths and not any(rel_path == p or rel_path.startswith(p.rstrip("/") + "/") for p in filter_paths):
                    continue
                src_file = os.path.join(root, f)
                dest_file = os.path.join(dest_dir, f)
                if files_differ(src_file, dest_file):
                    if not force_hub and os.path.exists(dest_file):
                        if not f.endswith((".md", ".json", ".py")):
                            continue
                        try:
                            with open(dest_file, "r", encoding="utf-8", errors="ignore") as dhf:
                                hub_content = dhf.read()
                            with open(src_file, "r", encoding="utf-8", errors="ignore") as dsf:
                                src_content = dsf.read()

                            # 1. Protect Hub against semver regression from outdated Spoke versions
                            hub_ver = extract_semver(hub_content)
                            src_ver = extract_semver(src_content)
                            if hub_ver and src_ver and hub_ver > src_ver:
                                hub_str = ".".join(map(str, hub_ver))
                                src_str = ".".join(map(str, src_ver))
                                print(f"  [PROTECTED HUB VERSION] Skipped {os.path.join(rel_dir, f)}: Hub version ({hub_str}) is newer than Spoke version ({src_str}). Run 'foundation deploy' to update spoke, or --force-hub-override.")
                                continue

                            # 2. Protect Hub mustache templates {{...}} from being overwritten by resolved Spoke files
                            if f.endswith(".md"):
                                hub_tags = set(re.findall(r"\{\{[A-Za-z0-9_]+\}\}", hub_content))
                                if hub_tags:
                                    src_tags = set(re.findall(r"\{\{[A-Za-z0-9_]+\}\}", src_content))
                                    if not hub_tags.issubset(src_tags):
                                        missing = hub_tags - src_tags
                                        print(f"  [PROTECTED HUB TEMPLATE] Skipped {os.path.join(rel_dir, f)}: Spoke file is resolved (missing Hub placeholders: {missing}). Use --force-hub-override to overwrite.")
                                        continue
                        except Exception as _te:
                            _log_telemetry(_te, "foundation:upstream_guard")
                    synced_count += 1
                    bumped = copy_with_optional_version_bump(src_file, dest_file, f, dry_run)
                    if bumped:
                        bumped_count += 1
                    status = "[SIMULATED]" if dry_run else "[SYNCED]"
                    print(f"  {status} {os.path.join(rel_dir, f)}{' (Version Bumped)' if bumped else ''}")

    # Merge .genome.json traits via set-union
    src_genome = os.path.join(project_agents, ".genome.json")
    dest_genome = os.path.join(foundation_agents, ".genome.json")
    if os.path.exists(src_genome):
        try:
            with open(src_genome, "r", encoding="utf-8") as gf:
                src_data = json.load(gf)
            dest_data = {}
            if os.path.exists(dest_genome):
                with open(dest_genome, "r", encoding="utf-8") as gf:
                    dest_data = json.load(gf)
            # Union traits / skills lists, use max for evolution_count
            merged = dict(dest_data)
            for k, v in src_data.items():
                if k == "evolution_count":
                    dest_val = dest_data.get(k, 0)
                    try:
                        merged[k] = max(int(dest_val), int(v))
                    except (ValueError, TypeError):
                        merged[k] = v
                elif isinstance(v, list) and isinstance(dest_data.get(k), list):
                    merged[k] = sorted(list(set(dest_data[k]) | set(v)))
                elif k not in merged:
                    merged[k] = v
            if not dry_run:
                atomic_write_text(dest_genome, json.dumps(merged, indent=2))
            print(f"  {'[SIMULATED]' if dry_run else '[MERGED]'} .genome.json traits unioned")
        except Exception as _ge:
            _log_telemetry(_ge, "foundation:genome_sync")

    # Sync root files (DEPLOY_ME.md, AGENTS_INDEX.md, hooks.json, .security-baseline.json, LEARNINGS.md)
    root_sync_candidates = list(ROOT_SYNC_FILES)
    if "LEARNINGS.md" not in root_sync_candidates:
        root_sync_candidates.append("LEARNINGS.md")

    for rf in root_sync_candidates:
        src_file = os.path.join(project_agents, rf)
        dest_file = os.path.join(foundation_agents, rf)
        if not os.path.exists(src_file):
            continue
        if filter_paths and not any(rf == p for p in filter_paths):
            continue
        if files_differ(src_file, dest_file):
            if rf == "LEARNINGS.md" and os.path.exists(dest_file):
                try:
                    with open(src_file, "r", encoding="utf-8", errors="ignore") as sf:
                        src_content = sf.read()
                    with open(dest_file, "r", encoding="utf-8", errors="ignore") as df:
                        dest_content = df.read()
                    pattern_blocks = re.findall(r"(### \[LP-\d+\].*?)(?=\n### \[LP-|\Z)", src_content, re.DOTALL)
                    added_patterns = []
                    for pb in pattern_blocks:
                        match_id = re.search(r"### \[(LP-\d+)\]", pb)
                        if match_id and match_id.group(1) not in dest_content:
                            added_patterns.append(pb.strip())
                    if added_patterns:
                        merged_content = dest_content.rstrip() + "\n\n" + "\n\n".join(added_patterns) + "\n"
                        if not dry_run:
                            atomic_write_text(dest_file, merged_content)
                        synced_count += 1
                        print(f"  {'[SIMULATED]' if dry_run else '[MERGED]'} {rf} ({len(added_patterns)} new failure pattern(s) appended)")
                        continue
                except Exception as _le:
                    _log_telemetry(_le, "foundation:learnings_sync")
            if not force_hub and os.path.exists(dest_file) and rf.endswith(".md"):
                try:
                    with open(dest_file, "r", encoding="utf-8", errors="ignore") as dhf:
                        hub_content = dhf.read()
                    with open(src_file, "r", encoding="utf-8", errors="ignore") as dsf:
                        src_content = dsf.read()
                    hub_tags = set(re.findall(r"\{\{[A-Za-z0-9_]+\}\}", hub_content))
                    if hub_tags:
                        src_tags = set(re.findall(r"\{\{[A-Za-z0-9_]+\}\}", src_content))
                        if not hub_tags.issubset(src_tags):
                            missing = hub_tags - src_tags
                            print(f"  [PROTECTED HUB TEMPLATE] Skipped {rf}: Spoke file is resolved (missing Hub placeholders: {missing}). Use --force-hub-override to overwrite.")
                            continue
                except Exception as _te:
                    _log_telemetry(_te, "foundation:upstream_guard_root")
            synced_count += 1
            bumped = copy_with_optional_version_bump(src_file, dest_file, rf, dry_run)
            if bumped:
                bumped_count += 1
            status = "[SIMULATED]" if dry_run else "[SYNCED]"
            print(f"  {status} {rf}{' (Version Bumped)' if bumped else ''}")

    # Section 4c: Sync spoke foundation-scoped observations to Hub
    try:
        obs_created, obs_updated = sync_upstream_observations(
            project_root=project_root,
            project_agents=project_agents,
            foundation_agents=foundation_agents,
            dry_run=dry_run
        )
        if obs_created > 0 or obs_updated > 0:
            synced_count += obs_created + obs_updated
            status = "[SIMULATED]" if dry_run else "[MERGED]"
            print(f"  {status} OBSERVATIONS.md ({obs_created} new, {obs_updated} updated from spoke)")
    except Exception as _oe:
        _log_telemetry(_oe, "foundation:upstream_observations")

    print("----------------------------------------")
    print(f"Upstream sync completed: {synced_count} file(s) synced, {bumped_count} version(s) bumped.")

    if getattr(args, "verify", False) and not dry_run:
        print("\n--- RUNNING POST-SYNC VERIFICATION ON FOUNDATION HUB ---")
        hub_root = os.path.dirname(foundation_agents)
        try:
            import subprocess
            ver_cmd = [sys.executable, os.path.join(foundation_agents, "scripts", "orion.py"), "verify"]
            res = subprocess.run(ver_cmd, cwd=hub_root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if res.returncode == 0:
                print("  ✅ [PASS] Foundation Hub verification succeeded.")
            else:
                print(f"  ⚠️ [WARN] Foundation Hub verification reported issues (Exit Code {res.returncode}):\n{res.stdout[-400:]}")
        except Exception as _ve:
            print(f"  ⚠️ Could not run verification: {_ve}")

    return True

# === SYNC AI CONFIGS ===
def sync_ai_configs(
    target_root: str,
    selected_ais: list | None = None,
    dry_run: bool = False,
    include_flutterin: bool | None = None,
):
    """
    Sync AI configuration files with latest foundation templates.
    
    Args:
        target_root: Path to target project
        selected_ais: List of AI names to sync. If None, syncs all deployed.
        dry_run: If True, simulate without writing
    
    Returns:
        dict: Sync results per AI
    """
    # Find foundation path
    foundation_path = get_foundation_path(target_root)
    if not foundation_path:
        if os.path.exists(os.path.join(target_root, ".agents", "templates", "AGENTS.template.md")):
            foundation_path = target_root
            print(" Running inside foundation.")
        else:
            print(" Error: Foundation path not found.")
            print("   This project may not be deployed from a foundation.")
            print("   Run foundation.py deploy first.")
            return {}
    
    if not os.path.exists(foundation_path):
        print(f" Error: Foundation not found at: {foundation_path}")
        return {}
    
    print(f" Foundation: {foundation_path}")
    
    # Determine which AIs to sync
    is_foundation_root = os.path.abspath(target_root) == os.path.abspath(foundation_path)
    if selected_ais is None:
        if is_foundation_root:
            selected_ais = ["gemini"]
            print(f" Syncing active foundation platforms: {', '.join(selected_ais)}")
        else:
            # Try to load from tracking file
            deployed = load_deployed_ais(target_root)
            if deployed:
                selected_ais = deployed
                print(f" Syncing deployed AIs: {', '.join(selected_ais)}")
            else:
                # Smart-detect active AIs from project filesystem
                selected_ais = detect_active_ais(target_root)
                print(f" Smart-detected active AIs: {', '.join(selected_ais)}")
    
    # Get project name
    project_name = os.path.basename(os.path.abspath(target_root))
    
    # Sync each AI
    results = {}
    source_templates = os.path.join(foundation_path, ".agents", "templates")
    
    print(f"\n Syncing AI configurations...")
    if dry_run:
        print(" [DRY RUN] No files will be modified.\n")
    
    # Read project manifest if available
    manifest = {}
    manifest_path = os.path.join(target_root, ".agents", ".project_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as _e:
            _log_telemetry(_e, 'foundation.py:797')

    synced_paths = {}
    for ai_name in selected_ais:
        if ai_name not in AI_CONFIGS:
            results[ai_name] = {"status": "ERROR", "message": f"Unknown AI: {ai_name}"}
            continue
        
        config = AI_CONFIGS[ai_name]
        template_path = os.path.join(source_templates, config["template"])
        
        if not os.path.exists(template_path):
            results[ai_name] = {"status": "ERROR", "message": "Template not found"}
            print(f"    {ai_name}: Template not found")
            continue
        
        # Build target path
        if config["target_dir"]:
            target_path = os.path.join(target_root, config["target_dir"], os.path.basename(config["target_path"]))
        else:
            target_path = os.path.join(target_root, config["target_path"])

        legacy_target_path = config.get("legacy_target_path")
        legacy_path = os.path.join(target_root, legacy_target_path) if legacy_target_path else None
        if legacy_path and os.path.isfile(legacy_path):
            target_path = legacy_path
            print(f"    {ai_name}: Using existing legacy file {legacy_target_path}")

        canonical_ai = config.get("canonical")
        if target_path in synced_paths:
            results[ai_name] = {
                "status": "SUCCESS",
                "message": f"Uses canonical {synced_paths[target_path]} configuration"
            }
            print(f"    {ai_name}: Uses canonical {synced_paths[target_path]} configuration")
            continue
        synced_paths[target_path] = canonical_ai or ai_name
        
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Smart merge
            content, status = smart_merge_config(
                template_content,
                target_path,
                project_name,
                config["format"],
                dry_run,
                manifest
            )
            
            if content is None:
                results[ai_name] = {"status": "SKIPPED", "message": status}
                print(f"    {ai_name}: {status}")
            else:
                results[ai_name] = {"status": "SUCCESS", "message": status}
                print(f"   {ai_name}: {status}{' (SIMULATED)' if dry_run else ''}")
        except Exception as e:
            results[ai_name] = {"status": "ERROR", "message": str(e)}
            print(f"   {ai_name}: {e}")
    
    # Deploy Cross-IDE Session Start Hooks & Platform Manifests
    if not dry_run:
        is_foundation_root = os.path.abspath(target_root) == os.path.abspath(foundation_path)

        # 1. Antigravity / Gemini settings hook
        gemini_settings_dir = os.path.join(target_root, ".gemini")
        os.makedirs(gemini_settings_dir, exist_ok=True)
        gemini_settings_file = os.path.join(gemini_settings_dir, "settings.json")
        if not os.path.exists(gemini_settings_file):
            gemini_hook_payload = {
                "hooks": {
                    "SessionStart": [
                        {
                            "type": "command",
                            "command": "python .agents/hooks/pre-agent-wake.py"
                        }
                    ]
                }
            }
            atomic_write_text(gemini_settings_file, json.dumps(gemini_hook_payload, indent=2))

        # Only deploy platform manifests & external IDE hooks when deploying to a target repository
        if not is_foundation_root:
            if deploy_platform_manifest:
                for ai_name in selected_ais:
                    deploy_platform_manifest(
                        target_root,
                        ai_name,
                        dry_run=dry_run,
                        include_flutterin=include_flutterin,
                    )

            # 2. Claude Code settings hook
            if "claude" in selected_ais:
                claude_dir = os.path.join(target_root, ".claude")
                os.makedirs(claude_dir, exist_ok=True)
                claude_settings_file = os.path.join(claude_dir, "settings.json")
                if not os.path.exists(claude_settings_file):
                    claude_hook_payload = {
                        "hooks": {
                            "SessionStart": [
                                {
                                    "type": "command",
                                    "command": "python .agents/hooks/pre-agent-wake.py"
                                }
                            ]
                        }
                    }
                    atomic_write_text(claude_settings_file, json.dumps(claude_hook_payload, indent=2))

            # 3. Cursor hooks.json
            if "cursor" in selected_ais:
                cursor_dir = os.path.join(target_root, ".cursor")
                os.makedirs(cursor_dir, exist_ok=True)
                cursor_hooks_file = os.path.join(cursor_dir, "hooks.json")
                if not os.path.exists(cursor_hooks_file):
                    cursor_hook_payload = {
                        "version": 1,
                        "hooks": {
                            "sessionStart": [
                                {
                                    "command": "python .agents/hooks/pre-agent-wake.py"
                                }
                            ]
                        }
                    }
                    atomic_write_text(cursor_hooks_file, json.dumps(cursor_hook_payload, indent=2))

    # Update tracking file
    if not dry_run:
        deployed_file = os.path.join(target_root, ".agents", ".deployed_ais")
        try:
            tracking_payload = {
                "project_name": project_name,
                "deployed_ais": selected_ais,
                "sync_results": results
            }
            atomic_write_text(deployed_file, json.dumps(tracking_payload, indent=2))
        except Exception as e:
            print(f"\n  Warning: Could not update tracking file: {e}")

        if not is_foundation_root:
            dna_file = os.path.join(target_root, ".agents", ".dna.json")
            if not os.path.exists(dna_file):
                manifest_file = os.path.join(target_root, ".agents", ".project_manifest.json")
                fw = "generic"
                lang = "generic"
                if os.path.exists(manifest_file):
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as mfh:
                            mdata = json.load(mfh)
                            fw = mdata.get("framework", fw)
                            lang = mdata.get("language", lang)
                    except Exception as _me:
                        _log_telemetry(_me, "sync_ai_configs:dna_manifest")
                try:
                    from core.dna import build_initial_dna_manifest
                    dna_payload = build_initial_dna_manifest(fw, lang, target_root)
                except Exception:
                    dna_payload = {
                        "schema_version": "0.0.1",
                        "dna_state": "BORN",
                        "origin": "foundation_sync",
                        "framework": fw,
                        "language": lang,
                        "primary_framework": fw,
                        "primary_language": lang,
                        "ecosystem": fw,
                        "deployed_at": datetime.now(timezone.utc).isoformat(),
                        "pillars": {
                            "strategy": "context/00_Strategy/BLUEPRINT.md",
                            "product": "context/01_Product/ROADMAP.md",
                            "creative": "context/02_Creative/STYLE_GUIDE.md",
                            "tech": "context/03_Tech/ARCHITECTURE.md",
                            "design_contract": "DESIGN.md"
                        },
                        "mutation_ledger": {
                            "dna_compliance_score": 100,
                            "epigenetic_aliases": {},
                            "layer_violations": [],
                            "chimera_files": []
                        }
                    }
                atomic_write_text(dna_file, json.dumps(dna_payload, indent=2))
    
    print(f"\n Sync completed{' (SIMULATED)' if dry_run else ''}.")
    return results


def cmd_sync_ai(args):
    ai_arg = getattr(args, "ai", None)
    selected_ais = None if not ai_arg or ai_arg.lower() == "all" else ai_arg.split(",")
    sync_ai_configs(
        args.target,
        selected_ais=selected_ais,
        dry_run=args.dry_run,
        include_flutterin=getattr(args, "with_flutterin", None),
    )


# ==============================================================================
# UNIFIED INTERACTIVE SETUP, ONBOARDING & DOCTOR WIZARD (orion.py setup)
# ==============================================================================

OPTIONAL_ORION_FEATURES = [
    {
        "id": "graph-db",
        "name": "Orion Local GraphRAG & Omni-Buffer (.orion/orion.db + IDE Wake Hook)",
        "desc": "Stores cross-session memory, AST relationships, and automatic drift detection.",
        "default": True,
    },
    {
        "id": "second-brain",
        "name": "Orion Second Brain 4-Note Briefing (.orion/working/brain/00..03)",
        "desc": "Generates 4 concise architecture & PageRank God Node notes so AI instantly grasps the project.",
        "default": True,
    },
    {
        "id": "vault",
        "name": "Orion Interactive Obsidian Knowledge Vault (.orion/export/vault/)",
        "desc": "Exports knowledge graph into Markdown with [[wikilinks]] ready to open in Obsidian.",
        "default": False,
    },
    {
        "id": "design-md",
        "name": "DESIGN.md Visual & Aesthetic Token System Contract",
        "desc": "Generates 60:30:10 color balance, typography, and WCAG 2.1 AA contrast guardrails.",
        "default": False,
    },
    {
        "id": "security-baseline",
        "name": "Orion AST Security Scan & Baseline (.agents/.security-baseline.json)",
        "desc": "Scans polyglot AST secrets/keys and records current security baseline.",
        "default": False,
    },
    {
        "id": "pack-hybrid",
        "name": "Orion Multi-Model Context Audit Bundles (.orion/bundles/hybrid/)",
        "desc": "Packs project code into <=10 balanced .md bundles ready for upload to Gemini Web or Claude.",
        "default": False,
    },
]


def _is_foundation_hub_repo(target_dir: str) -> bool:
    """Detects whether target_dir is the upstream portable-brainvibing (_foundation) hub repository itself."""
    abs_root = os.path.abspath(target_dir)
    app_markers = [
        "package.json", "pubspec.yaml", "Cargo.toml", "go.mod",
        "pyproject.toml", "requirements.txt", "pom.xml", "build.gradle",
        "src", "lib", "app", "apps", "packages", "services",
    ]
    if any(os.path.exists(os.path.join(abs_root, m)) for m in app_markers):
        return False
    has_orion = os.path.isfile(os.path.join(abs_root, ".agents", "scripts", "orion.py"))
    has_core = os.path.isdir(os.path.join(abs_root, ".agents", "scripts", "core"))
    has_rules = os.path.isdir(os.path.join(abs_root, ".agents", "rules"))
    return has_orion and has_core and has_rules


def _detect_ui_project(target_dir: str) -> bool:
    """Detects whether target_dir contains frontend UI, mobile screens, or web surfaces."""
    pubspec = os.path.join(target_dir, "pubspec.yaml")
    if os.path.isfile(pubspec):
        try:
            with open(pubspec, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
                if "sdk: flutter" in c or "flutter:" in c:
                    return True
        except Exception:
            pass

    pkg = os.path.join(target_dir, "package.json")
    if os.path.isfile(pkg):
        try:
            with open(pkg, "r", encoding="utf-8", errors="ignore") as f:
                c = f.read()
                ui_markers = ["\"react\"", "\"react-native\"", "\"vue\"", "\"svelte\"", "\"@angular/core\"", "\"next\"", "\"electron\"", "\"vite\"", "\"tailwind\""]
                if any(m in c for m in ui_markers):
                    return True
        except Exception:
            pass

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".agents", ".orion", "dist", "build", "scratch")]
        for f in files:
            if f.endswith((".tsx", ".jsx", ".vue", ".svelte", ".html", ".css", ".scss", ".storyboard")):
                return True
            if f.endswith(".xml") and "layout" in root.replace("\\", "/").split("/"):
                return True

    return False


def _detect_workspace_mode(target_dir: str) -> str:
    """
    Returns one of:
      - 'foundation_hub' : In upstream portable-brainvibing (_foundation) repository
      - 'greenfield'     : New/empty project folder without app code or manifests
      - 'brownfield'     : Existing project with application code or manifests
    """
    abs_root = os.path.abspath(target_dir)
    if _is_foundation_hub_repo(abs_root):
        return "foundation_hub"

    ignore_entries = {
        ".agents", ".orion", ".git", ".gitignore", ".env", ".env.example",
        "README.md", "LICENSE", "VERSION", "CHANGELOG.md", "PREREQUISITES.md",
        "AGENTS.md", "GEMINI.md", "CLAUDE.md", "DESIGN.md", "context",
        ".vscode", ".idea", ".cursor", ".claude", ".gemini",
    }
    try:
        entries = [e for e in os.listdir(abs_root) if e not in ignore_entries and not e.endswith("-plugin")]
    except OSError:
        entries = []

    return "brownfield" if len(entries) > 0 else "greenfield"


def _get_missing_pillar_install_commands() -> dict:
    """Returns OS-specific automatic install commands for missing dependencies."""
    is_win = os.name == "nt"
    is_mac = sys.platform == "darwin"
    cmds = {
        "ast-grep": (
            ["winget", "install", "--id", "ast-grep.ast-grep", "-e", "--accept-source-agreements", "--accept-package-agreements"]
            if is_win else (["brew", "install", "ast-grep"] if is_mac else ["cargo", "install", "ast-grep", "--locked"])
        ),
        "rtk": ["cargo", "install", "--git", "https://github.com/rtk-ai/rtk"],
        "bun": (
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "irm bun.sh/install.ps1 | iex"]
            if is_win else ["sh", "-c", "curl -fsSL https://bun.sh/install | bash"]
        ),
        "ollama_embed": ["ollama", "pull", "nomic-embed-text"],
        "llamacpp": (
            ["winget", "install", "--id", "ggml.llamacpp", "-e", "--accept-source-agreements", "--accept-package-agreements"]
            if is_win else (["brew", "install", "llama.cpp"] if is_mac else [])
        ),
    }
    return cmds


def recommend_ollama_models_for_hardware(hw_info: dict, installed_models: List[str]) -> dict:
    """
    Evaluates host hardware specs (RAM, GPU, VRAM, Apple Silicon) and installed Ollama models.
    Produces hardware tier classification, recommended models, and fitness scoring.
    """
    ram_gb = float(hw_info.get("ram_gb", hw_info.get("memory_gb", 16.0)))
    vram_gb = float(hw_info.get("vram_gb", 0.0))
    gpu_name = hw_info.get("gpu_name", "")
    is_apple_silicon = "Apple Silicon" in gpu_name or (sys.platform == "darwin" and "arm64" in sys.version.lower())

    # 1. Determine Hardware Capacity Tier
    # Tiers: LEAN_EDGE (<12GB RAM or <4GB VRAM), BALANCED_PRO (12-21GB RAM / 4-7.9GB VRAM),
    #        HIGH_CAPACITY (22-31GB RAM / 8-15.9GB VRAM), WORKSTATION_TITAN (>=32GB RAM / >=16GB VRAM)
    if is_apple_silicon:
        if ram_gb >= 32.0:
            hw_tier = "WORKSTATION_TITAN"
            rec_model = "qwen2.5-coder:32b"
            rec_params_b = 32.0
        elif ram_gb >= 24.0:
            hw_tier = "HIGH_CAPACITY"
            rec_model = "qwen2.5-coder:14b"
            rec_params_b = 14.0
        elif ram_gb >= 16.0:
            hw_tier = "BALANCED_PRO"
            rec_model = "qwen2.5-coder:7b"
            rec_params_b = 7.0
        else:
            hw_tier = "LEAN_EDGE"
            rec_model = "qwen2.5-coder:1.5b"
            rec_params_b = 1.5
    else:
        if (ram_gb >= 32.0 and vram_gb >= 15.0) or vram_gb >= 20.0:
            hw_tier = "WORKSTATION_TITAN"
            rec_model = "qwen2.5-coder:32b"
            rec_params_b = 32.0
        elif (ram_gb >= 22.0 and vram_gb >= 7.5) or vram_gb >= 10.0:
            hw_tier = "HIGH_CAPACITY"
            rec_model = "qwen2.5-coder:14b"
            rec_params_b = 14.0
        elif ram_gb >= 12.0 and (vram_gb >= 3.8 or vram_gb == 0.0):
            hw_tier = "BALANCED_PRO"
            rec_model = "qwen2.5-coder:7b"
            rec_params_b = 7.0
        else:
            hw_tier = "LEAN_EDGE"
            rec_model = "qwen2.5-coder:1.5b"
            rec_params_b = 1.5

    rec_embed_model = "nomic-embed-text"

    # 2. Categorize Installed Models
    embed_keywords = ["embed", "bge", "nomic", "minilm", "mxbai", "rerank"]
    installed_embed = []
    installed_gen = []

    for m in installed_models:
        m_lower = m.lower()
        if any(k in m_lower for k in embed_keywords):
            installed_embed.append(m)
        else:
            # Parse parameter size
            param_match = re.search(r"[:_-](\d+(?:\.\d+)?)[bB]", m)
            if not param_match:
                param_match = re.search(r"\b(\d+(?:\.\d+)?)[bB]\b", m)
            p_b = float(param_match.group(1)) if param_match else 3.0
            installed_gen.append({"name": m, "params_b": p_b})

    has_recommended_gen = any(rec_model.lower() in g["name"].lower() for g in installed_gen)
    has_recommended_embed = any("nomic-embed" in e.lower() for e in installed_embed)

    # 3. Select Best Installed Model for Active Use
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    best_installed_model = None
    if installed_gen:
        try:
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            from commands.brain import select_optimal_local_model
            best_installed_model = select_optimal_local_model(hw_info)
        except Exception:
            best_installed_model = installed_gen[0]["name"]

    # 4. Fitness Evaluation & Warnings
    warnings = []
    if not installed_gen:
        warnings.append(f"No generative code model found in Ollama. Recommended: 'ollama pull {rec_model}'.")
    elif best_installed_model:
        # Check if installed model parameter count is wildly mismatched
        p_match = re.search(r"[:_-](\d+(?:\.\d+)?)[bB]", best_installed_model)
        installed_p_b = float(p_match.group(1)) if p_match else 3.0
        if hw_tier in ("HIGH_CAPACITY", "WORKSTATION_TITAN") and installed_p_b <= 3.5:
            warnings.append(f"Installed model '{best_installed_model}' ({installed_p_b}B) is underutilizing your high-end hardware ({vram_gb:.1f}GB VRAM). Consider upgrading: 'ollama pull {rec_model}'.")
        elif hw_tier == "LEAN_EDGE" and installed_p_b >= 14.0:
            warnings.append(f"Installed model '{best_installed_model}' ({installed_p_b}B) may experience severe memory thrashing on this machine ({ram_gb:.1f}GB RAM). Recommended: 'ollama pull {rec_model}'.")

    if not has_recommended_embed:
        warnings.append(f"Recommended embedding model missing. Run: 'ollama pull {rec_embed_model}'.")

    return {
        "hardware_tier": hw_tier,
        "recommended_generative_model": rec_model,
        "recommended_params_b": rec_params_b,
        "recommended_embedding_model": rec_embed_model,
        "installed_generative_models": [g["name"] for g in installed_gen],
        "installed_embedding_models": installed_embed,
        "best_active_installed_model": best_installed_model,
        "has_recommended_generative": has_recommended_gen,
        "has_recommended_embedding": has_recommended_embed,
        "fitness_warnings": warnings,
        "pull_commands": {
            "generative": f"ollama pull {rec_model}",
            "embedding": f"ollama pull {rec_embed_model}",
        },
    }


def inspect_environment_and_workspace(target_dir: str = ".") -> dict:
    """
    Performs comprehensive zero-question inspection of:
    1. Hardware specs (RAM, GPU VRAM, Apple Silicon) & 4-Pillar dependencies
    2. Ollama model discovery and hardware-tailored model recommendations
    3. Workspace mode (Foundation Hub vs Greenfield vs Brownfield)
    4. Auto-detected tech stack & active AI IDEs
    5. Status of all Portable Brainvibing & Orion assets in workspace
    6. Catalog of optional Orion power-features
    """
    abs_target = os.path.abspath(target_dir)
    scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from core.capabilities import probe_capabilities
    except Exception:
        probe_capabilities = lambda **k: {}

    try:
        from commands.brain import detect_hardware, get_available_ollama_models
        hw = detect_hardware()
    except Exception:
        hw = {}
        get_available_ollama_models = lambda: []

    if "platform" not in hw:
        import platform as _pl
        hw["platform"] = _pl.system()
    if "cpu_count" not in hw:
        hw["cpu_count"] = os.cpu_count() or 1

    caps = probe_capabilities(force_refresh=True)
    ollama_avail = bool(caps.get("ollama", {}).get("available"))
    ollama_models = get_available_ollama_models() if ollama_avail else []

    ollama_rec = recommend_ollama_models_for_hardware(hw, ollama_models)

    missing_deps = []
    if not caps.get("rtk", {}).get("available"):
        missing_deps.append("rtk")
    if not caps.get("ast-grep", {}).get("available"):
        missing_deps.append("ast-grep")
    if not ollama_avail:
        missing_deps.append("ollama")
    else:
        if not ollama_rec["has_recommended_embedding"]:
            missing_deps.append(f"ollama:{ollama_rec['recommended_embedding_model']}")
        if not ollama_rec["has_recommended_generative"] and not ollama_rec["installed_generative_models"]:
            missing_deps.append(f"ollama:{ollama_rec['recommended_generative_model']}")
    if not caps.get("bun", {}).get("available"):
        missing_deps.append("bun")

    ws_mode = _detect_workspace_mode(abs_target)
    framework, language = detect_stack(abs_target)
    sub_workspaces = scan_monorepo_workspaces(abs_target)
    detected_ais = detect_active_ais(abs_target)

    # Check status of Portable Brainvibing & Orion assets in target_dir
    assets_status = {
        "gitignore": os.path.isfile(os.path.join(abs_target, ".gitignore")),
        "agents_md": os.path.isfile(os.path.join(abs_target, "AGENTS.md")),
        "context_pillars": all(
            os.path.isfile(os.path.join(abs_target, p))
            for p in [
                "context/00_Strategy/BLUEPRINT.md",
                "context/01_Product/ROADMAP.md",
                "context/02_Creative/STYLE_GUIDE.md",
                "context/03_Tech/ARCHITECTURE.md",
            ]
        ),
        "design_md": os.path.isfile(os.path.join(abs_target, "DESIGN.md")),
        "orion_db": os.path.isfile(os.path.join(abs_target, ".orion", "orion.db")),
        "omni_buffer": os.path.isfile(os.path.join(abs_target, ".orion", "working", "context.json")),
        "second_brain": os.path.isfile(os.path.join(abs_target, ".orion", "working", "brain", "00-Overview.md")),
        "obsidian_vault": os.path.isfile(os.path.join(abs_target, ".orion", "export", "vault", "index.md")),
        "security_baseline": os.path.isfile(os.path.join(abs_target, ".agents", ".security-baseline.json")),
        "hybrid_bundles": os.path.isdir(os.path.join(abs_target, ".orion", "bundles", "hybrid")),
    }

    raw_cmds = _get_missing_pillar_install_commands()
    raw_cmds["ollama_generative"] = ["ollama", "pull", ollama_rec["recommended_generative_model"]]
    install_cmds = {k: " ".join(v) for k, v in raw_cmds.items()}

    return {
        "project_name": os.path.basename(abs_target),
        "target_dir": abs_target,
        "workspace_mode": ws_mode,
        "detected_stack": {"framework": framework, "language": language},
        "monorepo_workspaces": sub_workspaces,
        "detected_ides": detected_ais,
        "hardware": hw,
        "pillars": {
            "python": caps.get("pillars", {}).get("pillar_1", {}),
            "rtk": caps.get("rtk", {}),
            "ast_grep": caps.get("ast-grep", {}),
            "ollama": {
                **caps.get("ollama", {}),
                "installed_models": ollama_models,
                "hardware_tier": ollama_rec["hardware_tier"],
                "recommended_generative_model": ollama_rec["recommended_generative_model"],
                "recommended_embedding_model": ollama_rec["recommended_embedding_model"],
                "best_active_model": ollama_rec["best_active_installed_model"],
                "has_embedding_model": ollama_rec["has_recommended_embedding"],
                "fitness_warnings": ollama_rec["fitness_warnings"],
                "pull_commands": ollama_rec["pull_commands"],
            },
            "bun": caps.get("bun", {}),
        },
        "ollama_recommendations": ollama_rec,
        "missing_laptop_deps": missing_deps,
        "install_commands": install_cmds,
        "project_assets_status": assets_status,
        "optional_features_catalog": OPTIONAL_ORION_FEATURES,
    }


def _run_orion_subcommand(orion_py: str, sub_args: list, cwd: str, timeout: int = 120) -> Tuple[bool, str]:
    """Helper executing orion.py subcommand safely with UTF-8."""
    try:
        proc = subprocess.run(
            [sys.executable, "-B", orion_py] + sub_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return proc.returncode == 0, out.strip()
    except Exception as e:
        _log_telemetry(e, f"setup:_run_orion_subcommand:{sub_args}")
        return False, str(e)


def execute_setup_pipeline(
    target_dir: str,
    framework: Optional[str] = None,
    language: Optional[str] = None,
    ais: Optional[str] = None,
    enabled_features: Optional[List[str]] = None,
    auto_install_deps: bool = False,
    auto_pull_models: bool = False,
) -> dict:
    """
    Executes the entire Portable Brainvibing setup pipeline and activates selected Orion features.
    """
    abs_target = os.path.abspath(target_dir)
    agents_dir = os.path.join(abs_target, ".agents")
    if not os.path.isdir(agents_dir):
        # Fallback if executed from foundation hub to external spoke
        script_agents_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        orion_py = os.path.join(script_agents_dir, "scripts", "orion.py")
        templates_dir = os.path.join(script_agents_dir, "templates")
    else:
        orion_py = os.path.join(agents_dir, "scripts", "orion.py")
        templates_dir = os.path.join(agents_dir, "templates")

    if enabled_features is None:
        enabled_features = ["graph-db", "second-brain"]

    steps_log = []
    info = inspect_environment_and_workspace(abs_target)
    rec = info["ollama_recommendations"]

    # 0. Optional Auto-Install Missing Laptop Dependencies & Models
    if auto_install_deps or auto_pull_models:
        install_map = _get_missing_pillar_install_commands()
        if auto_install_deps:
            for dep in info["missing_laptop_deps"]:
                cmd_list = None
                if dep == "ast-grep":
                    cmd_list = install_map["ast-grep"]
                elif dep == "rtk" and shutil.which("cargo"):
                    cmd_list = install_map["rtk"]
                elif dep == "bun":
                    cmd_list = install_map["bun"]

                if cmd_list:
                    print(f"  [⏳] Installing dependency '{dep}': {' '.join(cmd_list)} ...")
                    try:
                        res = subprocess.run(
                            cmd_list,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=180,
                            shell=False,
                        )
                        steps_log.append({
                            "step": f"install:{dep}",
                            "ok": res.returncode == 0,
                            "detail": "Installed" if res.returncode == 0 else res.stderr[:200],
                        })
                    except Exception as ie:
                        steps_log.append({"step": f"install:{dep}", "ok": False, "detail": str(ie)})

        if auto_pull_models and shutil.which("ollama"):
            # Pull embedding model if missing
            if not rec["has_recommended_embedding"]:
                emb_cmd = ["ollama", "pull", rec["recommended_embedding_model"]]
                print(f"  [⏳] Pulling embedding model: {' '.join(emb_cmd)} ...")
                try:
                    res = subprocess.run(emb_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300, shell=False)
                    steps_log.append({"step": "pull_embedding", "ok": res.returncode == 0, "detail": rec["recommended_embedding_model"]})
                except Exception as _pe:
                    steps_log.append({"step": "pull_embedding", "ok": False, "detail": str(_pe)})

            # Pull generative coder model if missing
            if not rec["has_recommended_generative"] and not rec["installed_generative_models"]:
                gen_cmd = ["ollama", "pull", rec["recommended_generative_model"]]
                print(f"  [⏳] Pulling hardware-recommended model: {' '.join(gen_cmd)} ...")
                try:
                    res = subprocess.run(gen_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, shell=False)
                    steps_log.append({"step": "pull_generative", "ok": res.returncode == 0, "detail": rec["recommended_generative_model"]})
                except Exception as _ge:
                    steps_log.append({"step": "pull_generative", "ok": False, "detail": str(_ge)})

    # Determine local LLM parameter size for deployment manifest
    has_local_gen = bool(rec["best_active_installed_model"]) or auto_pull_models
    llm_params = float(rec["recommended_params_b"]) if has_local_gen else 0.0

    # 1. Core Foundation Deploy (AGENTS.md, context/ 4 Pillars, IDE Manifests & Hooks)
    ws_mode = _detect_workspace_mode(abs_target)
    if ws_mode == "foundation_hub":
        try:
            hub_marker = os.path.expanduser("~/.orion_foundation_path")
            atomic_write_text(hub_marker, abs_target)
        except Exception as _he:
            _log_telemetry(_he, "setup:write_hub_marker")
        steps_log.append({"step": "foundation_hub_anchor", "ok": True, "detail": f"Global Hub anchored at {abs_target}"})
    else:
        deploy_ns = argparse.Namespace(
            target=abs_target,
            framework=framework,
            language=language,
            ai=ais or "auto",
            dry_run=False,
            use_local_llm=has_local_gen,
            llm_params=llm_params,
            with_flutterin=False,
        )
        try:
            cmd_deploy(deploy_ns)
            steps_log.append({"step": "foundation_deploy", "ok": True, "detail": "Deployed AGENTS.md, IDE hooks, & 4 Context Pillars"})
        except SystemExit as se:
            steps_log.append({"step": "foundation_deploy", "ok": se.code in (0, None), "detail": f"Exit code {se.code}"})
        except Exception as de:
            steps_log.append({"step": "foundation_deploy", "ok": False, "detail": str(de)})

    # Ensure 4 Lean Context Pillars exist in target project
    context_dir = os.path.join(abs_target, "context")
    pillars_map = {
        "00_Strategy/BLUEPRINT.md": "BLUEPRINT.template.md",
        "01_Product/ROADMAP.md": "ROADMAP.template.md",
        "02_Creative/STYLE_GUIDE.md": "STYLE_GUIDE.template.md",
        "03_Tech/ARCHITECTURE.md": "ARCHITECTURE.template.md",
    }
    proj_name = os.path.basename(abs_target)
    for rel_pillar, tpl_name in pillars_map.items():
        pillar_full = os.path.join(context_dir, rel_pillar)
        if not os.path.isfile(pillar_full):
            tpl_path = os.path.join(templates_dir, tpl_name)
            content = f"# {os.path.splitext(os.path.basename(rel_pillar))[0]} — {proj_name}\n"
            if os.path.isfile(tpl_path):
                try:
                    with open(tpl_path, "r", encoding="utf-8") as f:
                        content = f.read().replace("{{PROJECT_NAME}}", proj_name).replace("{project_name}", proj_name)
                except Exception:
                    pass
            atomic_write_text(pillar_full, content)

    # Re-resolve orion_py at target
    target_orion_py = os.path.join(abs_target, ".agents", "scripts", "orion.py")
    if os.path.isfile(target_orion_py):
        orion_py = target_orion_py

    # 2. Optional Feature 1: Orion Local GraphRAG & Omni-Buffer (`graph-db`)
    if "graph-db" in enabled_features or "all" in enabled_features:
        ok_init, _ = _run_orion_subcommand(orion_py, ["orion_ops", "init"], cwd=abs_target)
        ingest_targets = [
            p for p in [".agents/rules", ".agents/skills", ".agents/canons", "context"]
            if os.path.exists(os.path.join(abs_target, p))
        ]
        ok_ing = True
        if ingest_targets:
            ok_ing, _ = _run_orion_subcommand(orion_py, ["orion_ops", "ingest"] + ingest_targets, cwd=abs_target)
        wake_hook = os.path.join(abs_target, ".agents", "hooks", "pre-agent-wake.py")
        if os.path.isfile(wake_hook):
            try:
                subprocess.run(
                    [sys.executable, "-B", wake_hook],
                    cwd=abs_target,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=15,
                )
            except Exception as _we:
                _log_telemetry(_we, "setup:wake_hook")
        steps_log.append({
            "step": "graph-db",
            "ok": ok_init and ok_ing,
            "detail": "Initialized .orion/orion.db (SQLite WAL + FTS5 + Louvain) & synced Omni-Buffer context.json",
        })

    # 3. Optional Feature 2: Orion Second Brain 4-Note Briefing (`second-brain`)
    if "second-brain" in enabled_features or "all" in enabled_features:
        ok_sb, _ = _run_orion_subcommand(orion_py, ["memory", "second-brain"], cwd=abs_target)
        steps_log.append({
            "step": "second-brain",
            "ok": ok_sb,
            "detail": "Generated 00-Overview.md, 01-Map.md (PageRank God Nodes), 02-Decisions.md, 03-Status.md",
        })

    # 4. Optional Feature 3: Orion Interactive Obsidian Vault (`vault`)
    if "vault" in enabled_features or "all" in enabled_features:
        ok_v, _ = _run_orion_subcommand(orion_py, ["brain", "export-vault"], cwd=abs_target)
        steps_log.append({
            "step": "vault",
            "ok": ok_v,
            "detail": "Exported linked Obsidian Knowledge Vault to .orion/export/vault/ (index.md & GRAPH_REPORT.md)",
        })

    # 5. Optional Feature 4: DESIGN.md Aesthetic & Visual Token Contract (`design-md`)
    should_deploy_design = "design-md" in enabled_features
    if not should_deploy_design and "all" in enabled_features:
        should_deploy_design = _detect_ui_project(abs_target)

    if should_deploy_design:
        design_dest = os.path.join(abs_target, "DESIGN.md")
        design_tpl = os.path.join(templates_dir, "DESIGN.template.md")
        if not os.path.exists(design_dest):
            if os.path.isfile(design_tpl):
                try:
                    with open(design_tpl, "r", encoding="utf-8") as f:
                        tpl_text = f.read()
                    manifest_path_cand = os.path.join(abs_target, ".agents", ".project_manifest.json")
                    manifest_data = {}
                    if os.path.isfile(manifest_path_cand):
                        with open(manifest_path_cand, "r", encoding="utf-8") as mf:
                            manifest_data = json.load(mf)
                    resolved_design = resolve_template_string(tpl_text, manifest_data, proj_name)
                    atomic_write_text(design_dest, resolved_design)
                    steps_log.append({"step": "design-md", "ok": True, "detail": "Created DESIGN.md from template"})
                except Exception as de:
                    steps_log.append({"step": "design-md", "ok": False, "detail": str(de)})
            else:
                default_design = (
                    f"# 🎨 DESIGN SYSTEM CONTRACT — {proj_name}\n\n"
                    "- **Color Balance**: 60% Canvas (`#0D0F12`), 30% Surface (`#16191E`), 10% Accent (`#3B82F6`)\n"
                    "- **Contrast Floor**: WCAG 2.1 AA (>= 4.5:1 normal text, >= 3.0:1 UI components)\n"
                    "- **Spacing Grid**: 8pt modular cadence (4/8/12/16/24/32/48/64px)\n"
                )
                atomic_write_text(design_dest, default_design)
                steps_log.append({"step": "design-md", "ok": True, "detail": "Created baseline DESIGN.md"})
        else:
            steps_log.append({"step": "design-md", "ok": True, "detail": "DESIGN.md already exists (preserved)"})
    elif "all" in enabled_features:
        steps_log.append({"step": "design-md", "ok": True, "detail": "Skipped DESIGN.md (headless CLI/backend project detected)"})

    # 6. Optional Feature 5: Orion AST Security Scan & Baseline (`security-baseline`)
    if "security-baseline" in enabled_features or "all" in enabled_features:
        ok_sec, _ = _run_orion_subcommand(orion_py, ["scan", "security", ".", "--record-baseline"], cwd=abs_target)
        steps_log.append({
            "step": "security-baseline",
            "ok": ok_sec,
            "detail": "Recorded polyglot AST & secret security baseline in .agents/.security-baseline.json",
        })

    # 7. Optional Feature 6: Orion Multi-Model Context Audit Bundles (`pack-hybrid`)
    if "pack-hybrid" in enabled_features or "all" in enabled_features:
        ok_pack, _ = _run_orion_subcommand(orion_py, ["pack", "hybrid"], cwd=abs_target, timeout=180)
        steps_log.append({
            "step": "pack-hybrid",
            "ok": ok_pack,
            "detail": "Exported <=10 balanced hybrid audit bundles to .orion/bundles/hybrid/",
        })

    # 8. Fast Mechanical Gate Verification
    ok_ver, _ = _run_orion_subcommand(orion_py, ["verify", "--fast"], cwd=abs_target)
    steps_log.append({"step": "verify_fast", "ok": ok_ver, "detail": "Mechanical verification gate passed (Exit Code 0)"})

    return {
        "status": "SUCCESS" if all(s["ok"] for s in steps_log) else "PARTIAL",
        "target_dir": abs_target,
        "workspace_mode": ws_mode,
        "enabled_features": enabled_features,
        "steps": steps_log,
    }


def cmd_setup(args: argparse.Namespace) -> None:
    """
    Main entrypoint for `orion.py setup` (supports Interactive TUI Wizard, --inspect --json, --doctor, and --yes).
    """
    target_dir = getattr(args, "target", None) or "."
    abs_target = os.path.abspath(target_dir)
    info = inspect_environment_and_workspace(abs_target)

    # Mode 1: Non-Interactive JSON Inspector (Invoked by AI Agent in Chat IDE)
    if getattr(args, "inspect", False) or getattr(args, "json", False):
        print(json.dumps(info, indent=2))
        return

    # Diagnostic Banner Presentation
    hw = info["hardware"]
    p_info = info["pillars"]
    ol_info = p_info["ollama"]
    rec = info["ollama_recommendations"]
    ws_mode = info["workspace_mode"]
    assets = info["project_assets_status"]

    ram_val = hw.get("memory_gb", hw.get("ram_gb", 0.0))
    vram_val = hw.get("vram_gb", 0.0)
    gpu_label = f" | GPU: {hw.get('gpu_name')} ({vram_val} GB VRAM)" if hw.get("gpu_name") else ""

    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║ 🧠 PORTABLE BRAINVIBING — ORION UNIFIED SETUP & DOCTOR WIZARD (v0.0.2)     ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    print("\n[1/4] 💻 LAPTOP & 4-PILLAR DEPENDENCY DIAGNOSTIC")
    print(f"  • OS & Hardware : {hw.get('platform')} ({hw.get('cpu_count')} Cores | {ram_val} GB RAM{gpu_label})")
    print(f"  • Pillar 1 (Py) : ✅ {p_info['python'].get('details', 'Python 3.10+ & SQLite3 Active')}")

    rtk_ok = "✅ Installed" if p_info["rtk"].get("available") else "⚠️ Missing (Fallback: Python Stream Filter)"
    sg_ok = "✅ Installed" if p_info["ast_grep"].get("available") else "⚠️ Missing (Fallback: Python AST/Regex)"
    print(f"  • Pillar 2 (Rust): rtk: {rtk_ok} | ast-grep: {sg_ok}")

    if ol_info.get("available"):
        provider_name = ol_info.get("provider", "ollama")
        provider_display = {
            "ollama": "Ollama Local AI",
            "llama_server": "llama.cpp (llama-server)",
            "lm_studio": "LM Studio Local AI",
            "vllm": "vLLM / LocalAI",
            "openai_compatible": "OpenAI-Compatible Local AI",
        }.get(provider_name, f"Local AI ({provider_name})")

        gen_models_list = rec.get("installed_generative_models", [])
        emb_models_list = rec.get("installed_embedding_models", [])

        print(f"  • Pillar 3 (AI) : ✅ {provider_display} Online [Tier: {rec['hardware_tier']}]")
        print(f"                     Endpoint     : {ol_info.get('version', 'http://127.0.0.1:11434')}")
        print(f"                     Active Code  : {rec['best_active_installed_model'] or 'None installed'}")
        if gen_models_list:
            print(f"                     Code Models  : {', '.join(gen_models_list)}")
        if emb_models_list:
            print(f"                     Embed Models : {', '.join(emb_models_list)} ✅")
        else:
            print(f"                     Embed Models : ⚠️ None found (Rec: {rec['recommended_embedding_model']})")
        print(f"                     Hardware Rec : {rec['recommended_generative_model']} ({rec['recommended_params_b']}B)")
        if rec["fitness_warnings"]:
            for fw in rec["fitness_warnings"]:
                print(f"                     💡 {fw}")
    else:
        print(f"  • Pillar 3 (AI) : ⚠️ Local AI Offline (Ollama, llama-server, LM Studio, or vLLM)")
        print(f"                     Fallback     : SQLite FTS5 BM25 Lexical & Cloud Handoff Queue")
        print(f"                     Hardware Fit : Machine qualifies for Tier [{rec['hardware_tier']}]. Rec: {rec['recommended_generative_model']}.")

    bun_ok = f"✅ {p_info['bun'].get('version')}" if p_info["bun"].get("available") else "⚠️ Missing (Fallback: Host Node/Pytest)"
    print(f"  • Pillar 4 (Bun): {bun_ok}")

    print("\n[2/4] 📂 WORKSPACE & PROJECT DIAGNOSTIC")
    mode_labels = {
        "foundation_hub": "🏛️  FOUNDATION GLOBAL HUB (Upstream Repository)",
        "greenfield": "🌱 EMPTY WORKSPACE (Greenfield — New Project)",
        "brownfield": f"📦 EXISTING PROJECT (Brownfield) — '{info['project_name']}'",
    }
    print(f"  • Detected Mode : {mode_labels.get(ws_mode, ws_mode)}")
    print(f"  • Detected Stack: {info['detected_stack']['framework']} / {info['detected_stack']['language']}")
    print(f"  • Detected IDEs : {', '.join(info['detected_ides'])}")
    print("  • Component Status in this Workspace:")
    print(f"     {'✅' if assets['agents_md'] else '❌'} AGENTS.md Master BIOS Router")
    print(f"     {'✅' if assets['context_pillars'] else '❌'} context/ 4 Lean Pillars (BLUEPRINT, ROADMAP, STYLE_GUIDE, ARCHITECTURE)")
    print(f"     {'✅' if assets['orion_db'] else '❌'} .orion/orion.db (Orion Local GraphRAG & Memory Store)")
    print(f"     {'✅' if assets['second_brain'] else '❌'} .orion/working/brain/ (Orion Second Brain 4-Note Briefing)")
    print(f"     {'✅' if assets['obsidian_vault'] else '❌'} .orion/export/vault/ (Orion Interactive Obsidian Vault)")
    print(f"     {'✅' if assets['design_md'] else '❌'} DESIGN.md (Visual & Aesthetic Token Contract)")

    # Doctor Mode Exit
    if getattr(args, "doctor", False):
        print("\n🩺 [DOCTOR SUMMARY]")
        if info["missing_laptop_deps"]:
            print(f"  • Optional Tools Missing: {', '.join(info['missing_laptop_deps'])}")
            for k, cmd_str in info["install_commands"].items():
                print(f"    -> Install {k:<15}: {cmd_str}")
        else:
            print("  • All 4 Pillar dependencies are fully optimal!")
        print("  • Run `python .agents/scripts/orion.py setup` to scaffold or activate any missing components.\n")
        return

    # Non-Interactive vs Interactive Execution
    is_interactive = sys.stdin is not None and sys.stdin.isatty() and not getattr(args, "yes", False) and not getattr(args, "non_interactive", False)

    chosen_framework = getattr(args, "framework", None) or info["detected_stack"]["framework"]
    chosen_language = getattr(args, "language", None) or info["detected_stack"]["language"]
    chosen_ais = getattr(args, "ai", None)
    auto_install = getattr(args, "install_deps", False)
    auto_pull = getattr(args, "pull_models", False)

    raw_enable = getattr(args, "enable", None)
    if raw_enable:
        if raw_enable.strip().lower() == "all":
            enabled_features = [f["id"] for f in OPTIONAL_ORION_FEATURES]
        else:
            enabled_features = [x.strip().lower() for x in raw_enable.split(",") if x.strip()]
    else:
        enabled_features = [f["id"] for f in OPTIONAL_ORION_FEATURES if f["default"]]

    # Interactive TUI Wizard
    if is_interactive:
        # Step 1: Missing Tooling & Model Pull Prompt
        if info["missing_laptop_deps"]:
            print(f"\n  💡 Missing tools detected: {', '.join(info['missing_laptop_deps'])}")
            ans_dep = input("  👉 Attempt automatic installation for missing OS dependencies? [y/N]: ").strip().lower()
            if ans_dep in ("y", "yes", "1"):
                auto_install = True

        if ol_info.get("available") and (not rec["has_recommended_generative"] or not rec["has_recommended_embedding"]):
            print(f"\n  💡 Hardware Recommendation: Pull '{rec['recommended_generative_model']}' & '{rec['recommended_embedding_model']}'.")
            ans_pull = input(f"  👉 Automatically pull recommended Ollama models now? [y/N]: ").strip().lower()
            if ans_pull in ("y", "yes", "1"):
                auto_pull = True

        # Step 2: Workspace Confirmation
        if ws_mode == "foundation_hub":
            print("\n  👉 You are currently inside the Global Hub `portable-brainvibing`. What would you like to do?")
            print("     [1] Setup & Verify hub health (Self-Hosting Mode) [Default]")
            print("     [2] Deploy .agents to another project folder on this computer")
            ans_hub = input("  Choice [1/2, Enter=1]: ").strip()
            if ans_hub == "2":
                spoke_path = input("  📂 Enter target project path: ").strip().strip("\"'")
                if spoke_path:
                    os.makedirs(spoke_path, exist_ok=True)
                    abs_target = os.path.abspath(spoke_path)
                    info = inspect_environment_and_workspace(abs_target)
                    ws_mode = info["workspace_mode"]
                    chosen_framework = info["detected_stack"]["framework"]
                    chosen_language = info["detected_stack"]["language"]

        if ws_mode == "greenfield" and chosen_framework == "generic":
            print("\n  🌱 Empty workspace detected (Greenfield). Select primary project stack:")
            print("     [0] Design later with AI Agent (/project-init) [Default]")
            print("     [1] Flutter / Dart (Mobile & Multi-platform)")
            print("     [2] React / Next.js / TypeScript (Web & Fullstack)")
            print("     [3] Python (FastAPI / AI / CLI)")
            print("     [4] Rust / Go (Systems / Microservice)")
            st_choice = input("  Stack choice [0-4, Enter=0]: ").strip()
            stack_map = {
                "1": ("flutter", "dart"),
                "2": ("react", "typescript"),
                "3": ("python", "python"),
                "4": ("rust", "rust"),
            }
            if st_choice in stack_map:
                chosen_framework, chosen_language = stack_map[st_choice]

        # Step 3: Optional Features Showcase Checklist
        print("\n[3/4] 🎛️  ORION OPTIONAL POWER-FEATURES SHOWCASE & ACTIVATION")
        print("  Select optional Orion features to activate in this workspace:")
        for idx, feat in enumerate(OPTIONAL_ORION_FEATURES, 1):
            mark = "x" if feat["default"] else " "
            rec_tag = " [RECOMMENDED]" if feat["default"] else ""
            print(f"  [{mark}] {idx}. {feat['name']}{rec_tag}")
            print(f"         -> {feat['desc']}")

        feat_ans = input("\n  👉 Enter comma-separated numbers (Enter = 1,2 | 'all' = Enable All | e.g. 1,2,3,4): ").strip().lower()
        if feat_ans == "all":
            enabled_features = [f["id"] for f in OPTIONAL_ORION_FEATURES]
        elif feat_ans:
            picked = []
            for part in feat_ans.split(","):
                part = part.strip()
                if part.isdigit():
                    f_idx = int(part) - 1
                    if 0 <= f_idx < len(OPTIONAL_ORION_FEATURES):
                        picked.append(OPTIONAL_ORION_FEATURES[f_idx]["id"])
                else:
                    picked.append(part)
            if picked:
                enabled_features = picked

    # Step 4: Execute Setup Pipeline
    print("\n[4/4] ⚙️  EXECUTING ORION SETUP PIPELINE...")
    res = execute_setup_pipeline(
        target_dir=abs_target,
        framework=chosen_framework,
        language=chosen_language,
        ais=chosen_ais,
        enabled_features=enabled_features,
        auto_install_deps=auto_install,
        auto_pull_models=auto_pull,
    )

    for st in res["steps"]:
        icon = "✓" if st["ok"] else "!"
        print(f"  [{icon}] {st['step']:<20}: {st['detail']}")

    print("\n🎉 SETUP COMPLETE! Workspace is now powered by Portable Brainvibing & Orion Brain.")
    print("\n📌 CHEAT SHEET — WHAT CAN YOU DO NEXT?")
    if ws_mode == "greenfield":
        print("  • Build New App     : Open AI Chat and run '/project-init' or state your product vision")
    else:
        print("  • Build / Audit     : In AI Chat, run '/app-lifecycle' (new feature) or '/integrity-sentinel' (audit)")
    if "vault" in enabled_features:
        print("  • Open Obsidian     : Launch Obsidian -> 'Open folder as vault' -> select '.orion/export/vault'")
    if "second-brain" in enabled_features:
        print("  • View Architecture : Check '.orion/working/brain/00-Overview.md' and God Nodes")
    print("  • Doctor Diagnostic : python .agents/scripts/orion.py doctor\n")

def cmd_dna(args: argparse.Namespace) -> None:
    action = getattr(args, "dna_action", "sequence") or "sequence"
    target_dir = getattr(args, "target", ".") or "."
    abs_target = os.path.abspath(target_dir)

    try:
        from core.dna import sequence_project_dna, mutate_project_dna
    except ImportError:
        scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from core.dna import sequence_project_dna, mutate_project_dna

    if action == "sequence":
        dna = sequence_project_dna(abs_target, allow_foundation=True)
        if not dna:
            print(f"[DNA ERROR] Failed to sequence Project DNA for target '{os.path.basename(abs_target)}'.")
            return
        print(f"\n🧬 PROJECT ARCHITECTURAL DNA: {os.path.basename(abs_target)}")
        print(f"  • DNA State       : {dna.dna_state} (Origin: {dna.origin})")
        print(f"  • Archetype       : {dna.archetype}")
        print(f"  • Primary Stack   : {dna.primary_framework} ({dna.primary_language})")
        print(f"  • Compliance Score: {dna.dna_compliance_score}/100")
        print(f"  • Active Roots    : {', '.join(dna.active_native_roots) if dna.active_native_roots else 'None'}")
        print(f"  • Dormant Roots   : {', '.join(dna.dormant_roots) if dna.dormant_roots else 'None'}")
        print(f"  • Feature Organs  : {len(dna.feature_organs)} ({', '.join(o['name'] for o in dna.feature_organs[:5])})")
        print(f"  • Execution Spine : {', '.join(dna.execution_spine) if dna.execution_spine else 'Auto-detected'}")
        print(f"  • Layer Violations: {len(dna.layer_violations)}")
        print(f"  • Chimera Files   : {len(dna.chimera_files)}")
        print(f"  • Classified Files: {len(dna.file_tier_map)} files across 5-Tier strata\n")

    elif action == "mutate":
        mode = getattr(args, "mode", "epigenetic")
        dry_run = getattr(args, "dry_run", False)
        res = mutate_project_dna(abs_target, mode=mode, dry_run=dry_run)
        print(f"\n🧬 BROWNFIELD DNA MUTATION: Mode='{mode}' (Dry Run: {dry_run})")
        if res.get("status") == "success":
            if mode == "epigenetic":
                print(f"  • DNA State       : {res['dna_state']}")
                print(f"  • Compliance Score: {res['dna_compliance_score']}/100")
                print(f"  • Epigenetic Mappings:")
                for k, v in res.get("epigenetic_aliases", {}).items():
                    print(f"    - `{k}` -> `{v}`")
                print(f"  • Violations Found: {res['violations_count']}")
                print(f"  • Chimera Files   : {res['chimera_count']}")
            elif mode == "plan":
                print(f"  • Blueprint File  : {res.get('plan_file')}")
                print(f"  • Compliance Score: {res.get('compliance_score')}/100")
                print(f"  • Violations Found: {res.get('violations')}")
                print(f"  • Chimera Files   : {res.get('chimeras')}")
            elif mode == "scaffold":
                print(f"  • Scaffolded Dirs : {', '.join(res.get('scaffolded_directories', []))}")
        else:
            print(f"  • Error: {res.get('message')}")
            sys.exit(1)

    elif action == "audit":
        dna = sequence_project_dna(abs_target, allow_foundation=True)
        if not dna:
            print(f"[DNA ERROR] Failed to sequence Project DNA for target '{os.path.basename(abs_target)}'.")
            return
        print(f"\n🛡️  DNA ARCHITECTURAL INTEGRITY AUDIT: {os.path.basename(abs_target)}")
        print(f"  • Compliance Score: {dna.dna_compliance_score}/100")
        if dna.layer_violations:
            print(f"  • ⚠️  Layer Violations ({len(dna.layer_violations)}):")
            for v in dna.layer_violations[:10]:
                print(f"    - {v['file']}:L{v['line']} ({v['source_tier']} -> {v['target_tier']}): {v['reason']}")
        else:
            print(f"  • ✅ Zero Illegal Cross-Layer Dependency Violations")

        if dna.chimera_files:
            print(f"  • ⚠️  Chimera Files ({len(dna.chimera_files)}):")
            for cf in dna.chimera_files[:5]:
                print(f"    - {cf} (Presentation mixing raw DB/HTTP)")
        else:
            print(f"  • ✅ Zero Chimera Files Detected")

        if dna.dna_compliance_score < 70:
            print(f"\n[AUDIT FAILED] Compliance score {dna.dna_compliance_score} is below 70 threshold.")
            sys.exit(1)
        else:
            print(f"\n[AUDIT PASSED] Architecture complies with 5-Tier DNA standards.\n")

    elif action == "lint":
        file_arg = getattr(args, "file", None)
        path_to_lint = file_arg if file_arg else getattr(args, "target", ".") or "."
        from core.dna import lint_dependencies_path
        violations = lint_dependencies_path(path_to_lint, root_dir=abs_target)

        print(f"\n🧬 JIT DNA ARCHITECTURAL LINTER: {path_to_lint}")
        print("------------------------------------------------------------")
        if violations:
            for v in violations:
                print(f"[DNA_VIOLATION] {v['file']}:L{v['line']} ({v['from_tier']} -> {v['to_tier']})")
                print(f"  Import: \"{v['imported_path']}\"")
                print(f"  Reason: {v['reason']}\n")
            print(f"Summary: ⚠️ {len(violations)} architectural violations detected.")
            if getattr(args, "strict", False):
                sys.exit(1)
        else:
            print("✅ Zero dependency violations. All imports conform to 5-Tier Directed Dependency Laws.\n")

    elif action == "snapshot":
        from core.dna import record_dna_snapshot
        res = record_dna_snapshot(abs_target)
        if res.get("ok"):
            print(f"\n🧬 DNA SNAPSHOT RECORDED: {os.path.basename(abs_target)}")
            print(f"  • Timestamp       : {res['timestamp']}")
            print(f"  • Compliance Score: {res['compliance_score']}/100")
            print(f"  • Violations      : {res['violations_count']}")
            print(f"  • Chimera Files   : {res['chimera_count']}")
            print(f"  • Classified Files: {res['file_count']}\n")
        else:
            print(f"[DNA ERROR] Failed to record DNA snapshot: {res.get('error')}")
            sys.exit(1)

    elif action == "trend":
        from core.dna import get_dna_trend
        limit = getattr(args, "limit", 10) or 10
        res = get_dna_trend(abs_target, limit=limit)
        snaps = res.get("snapshots", [])
        print(f"\n📈 DNA ARCHITECTURAL COMPLIANCE TREND ({len(snaps)} snapshots): {os.path.basename(abs_target)}")
        print("--------------------------------------------------------------------------------")
        if snaps:
            print(f"{'Timestamp':<25} | {'Score':<8} | {'Violations':<10} | {'Chimeras':<8} | {'Files':<6}")
            print("-" * 75)
            for s in snaps:
                ts_short = s['timestamp'][:19]
                print(f"{ts_short:<25} | {s['compliance_score']:<3}/100 | {s['violations_count']:<10} | {s['chimera_count']:<8} | {s['file_count']:<6}")
            if res.get("has_regression"):
                print(f"\n⚠️ REGRESSION DETECTED: {res.get('regression_reason')}\n")
            else:
                print(f"\n✅ Trend stable (no regressions detected).\n")
        else:
            print("No DNA snapshots recorded yet. Run 'orion dna snapshot' to record one.\n")


# === CLI ===
def cmd_evolve(args):
    """
    Evolves project archetype dynamically (Evolutionary Sync).
    Allows a local utility project to pull expanded connected/SaaS templates from Foundation Hub.
    """
    target_dir = os.path.abspath(args.target)
    target_agents_dir = os.path.join(target_dir, ".agents")
    dna_path = os.path.join(target_agents_dir, ".dna.json")

    archetype_map = {
        "utility": "LOCAL_UTILITY",
        "connected": "CONNECTED_APP",
        "saas": "B2B_SAAS",
    }
    target_archetype = archetype_map.get(args.archetype.lower(), "B2B_SAAS")

    print(f"⚡ Evolutionary Sync: Upgrading project archetype to '{target_archetype}' ({args.archetype})")

    dna_data = {}
    if os.path.isfile(dna_path):
        try:
            with open(dna_path, "r", encoding="utf-8") as f:
                dna_data = json.load(f)
        except Exception:
            pass

    dna_data["dna_state"] = "MUTATING"
    dna_data["archetype"] = target_archetype
    dna_data["archetype_profile"] = target_archetype
    dna_data["evolved_at"] = datetime.now(timezone.utc).isoformat()

    if not args.dry_run:
        os.makedirs(target_agents_dir, exist_ok=True)
        atomic_write_text(dna_path, json.dumps(dna_data, indent=2))
        print(f"  -> Updated {dna_path} with archetype '{target_archetype}' (State: MUTATING)")

    try:
        from core.platform_manifests import is_flutterin_installed
        if is_flutterin_installed(target_dir):
            print("  -> Triggering flutterin context re-synthesis...")
            setattr(args, "framework", dna_data.get("framework", "flutter"))
            setattr(args, "language", dna_data.get("language", "dart"))
            cmd_deploy(args)
    except Exception as e:
        _log_telemetry(e, "cmd_evolve:resynthesize")

    print(f"✔ Evolutionary Sync Complete! Target project archetype upgraded to '{target_archetype}'.")


def main():
    parser = argparse.ArgumentParser(description="Foundation Package & Deployment Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommands: setup / init / onboard / doctor
    for setup_alias in ("setup", "init", "onboard", "doctor"):
        p_setup = subparsers.add_parser(setup_alias, help="Unified interactive setup, workspace detector, hardware doctor, and feature wizard")
        p_setup.add_argument("--target", default=".", help="Target workspace directory (default: current directory)")
        p_setup.add_argument("--inspect", action="store_true", help="Output full laptop & workspace diagnostic as JSON for AI Agent")
        p_setup.add_argument("--json", action="store_true", help="Alias for --inspect (JSON output)")
        p_setup.add_argument("--doctor", action="store_true", default=(setup_alias == "doctor"), help="Run health check on laptop pillars & workspace assets")
        p_setup.add_argument("--yes", "-y", "--non-interactive", dest="yes", action="store_true", help="Run non-interactively with selected features")
        p_setup.add_argument("--enable", type=str, default=None, help="Comma-separated optional features: graph-db,second-brain,vault,design-md,security-baseline,pack-hybrid or 'all'")
        p_setup.add_argument("--install-deps", action="store_true", help="Attempt automatic OS installation for missing optional pillars")
        p_setup.add_argument("--pull-models", action="store_true", help="Attempt automatic pull for hardware-recommended Ollama models")
        p_setup.add_argument("--framework", type=str, default=None, help="Override detected framework")
        p_setup.add_argument("--language", type=str, default=None, help="Override detected language")
        p_setup.add_argument("--ai", type=str, default=None, help="Comma-separated AI platforms to configure")

    # Deploy
    parser_deploy = subparsers.add_parser("deploy", help="Deploy Foundation to a target project")
    parser_deploy.add_argument("--target", required=True, help="Target project root directory")
    parser_deploy.add_argument("--framework", default=None, help="Framework (e.g., react, flutter, python, node). Auto-detected if omitted.")
    parser_deploy.add_argument("--language", default=None, help="Language (e.g., typescript, dart, python). Auto-detected if omitted.")
    parser_deploy.add_argument("--ai", default="auto", help="Comma-separated list of AIs to deploy (or 'auto'/'all'). Defaults to 'auto'.")
    parser_deploy.add_argument("--dry-run", action="store_true", help="Simulate deployment without modifying files")
    parser_deploy.add_argument("--use-local-llm", action="store_true", help="Flag to indicate if using a local LLM")
    parser_deploy.add_argument("--llm-params", type=float, default=0.0, help="Parameter size of the local LLM in Billions (e.g., 8.0, 70.0)")
    parser_deploy.add_argument("--with-flutterin", action="store_true", help="Include flutterin MCP server definitions in deployed manifests")
    
    # Push Upstream
    parser_upstream = subparsers.add_parser("push-upstream", help="Sync local project changes back to Foundation")
    parser_upstream.add_argument("--project", "--source", default=".", dest="project", help="Path to the local project root")
    parser_upstream.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files")
    parser_upstream.add_argument("--force-hub-override", action="store_true", help="Force overwriting generic hub templates with spoke-resolved assets")
    parser_upstream.add_argument("--include-scripts", action="store_true", help="Include .agents/scripts engine updates in upstream sync")
    parser_upstream.add_argument("--path", "--file", action="append", default=[], dest="paths", help="Specific file(s) or relative path(s) under .agents to sync")
    parser_upstream.add_argument("--git-diff", action="store_true", help="Only sync files modified in the latest git commit")
    parser_upstream.add_argument("--verify", action="store_true", help="Run full verification audit on foundation hub after sync")
    
    # Sync AI
    parser_syncai = subparsers.add_parser("sync-ai", help="Sync AI brand configs to local templates")
    parser_syncai.add_argument("--target", required=True, help="Target project root directory")
    parser_syncai.add_argument("--ai", help="Comma-separated list of AIs to sync")
    parser_syncai.add_argument("--dry-run", action="store_true", help="Simulate sync without modifying files")
    parser_syncai.add_argument("--with-flutterin", action="store_true", help="Include flutterin MCP server definitions in deployed manifests")

    # DNA Manager (Living Genome, Epigenetic Mutation & Dependency Audit)
    parser_dna = subparsers.add_parser("dna", help="Universal Living Project DNA manager, brownfield sequencer & epigenetic mutation engine")
    parser_dna.add_argument("dna_action", choices=["sequence", "mutate", "audit", "lint", "snapshot", "trend"], nargs="?", default="sequence", help="Action: sequence DNA, mutate brownfield code, audit 5-tier dependency laws, snapshot DNA metrics, or view trend")
    parser_dna.add_argument("--target", default=".", help="Target project root directory (default: current directory)")
    parser_dna.add_argument("--file", help="Specific file to lint for architectural dependency violations")
    parser_dna.add_argument("--strict", action="store_true", help="Fail with non-zero exit code on violations")
    parser_dna.add_argument("--mode", choices=["epigenetic", "plan", "scaffold"], default="epigenetic", help="Mutation mode: epigenetic (safe mapping), plan (blueprint), or scaffold (directories)")
    parser_dna.add_argument("--dry-run", action="store_true", help="Simulate action without writing files")

    parser_dnalint = subparsers.add_parser("dna-lint", help="Direct JIT dependency linter for 5-Tier Directed Dependency Laws")
    parser_dnalint.add_argument("file", nargs="?", default=".", help="File or directory path to lint")
    parser_dnalint.add_argument("--strict", action="store_true", help="Fail with non-zero exit code on violations")

    # Evolutionary Sync
    parser_evolve = subparsers.add_parser("evolve", help="Evolve project archetype (utility -> connected -> saas) and sync expanded templates")
    parser_evolve.add_argument("archetype", choices=["utility", "connected", "saas"], help="Target archetype profile: utility, connected, or saas")
    parser_evolve.add_argument("--target", default=".", help="Target project root directory (default: current directory)")
    parser_evolve.add_argument("--dry-run", action="store_true", help="Simulate evolution without writing files")

    args = parser.parse_args()
    
    if args.command in ("setup", "init", "onboard", "doctor"):
        cmd_setup(args)
    elif args.command == "deploy":
        cmd_deploy(args)
    elif args.command == "evolve":
        cmd_evolve(args)
    elif args.command == "push-upstream":
        cmd_upstream(args)
    elif args.command == "sync-ai":
        cmd_sync_ai(args)
    elif args.command == "dna":
        cmd_dna(args)
    elif args.command == "dna-lint":
        setattr(args, "dna_action", "lint")
        setattr(args, "target", args.file)
        cmd_dna(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
