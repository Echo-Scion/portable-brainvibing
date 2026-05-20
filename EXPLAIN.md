# AGENTS: The `.agents` Ecosystem Guide

Welcome to the **Portable Brainvibing AI-Surgical Infrastructure** (v3.0.0 — Algorithmic Upgrade).

This ecosystem treats the AI as a **statistical model**, not a human employee. Every file contains **executable algorithms** (decision trees, output templates, Python harnesses) rather than vague prohibitions. The AI does not need willpower; it needs structured constraints.

---

## 🧠 Core Philosophy (v3.0)

| Principle | Old (v1–v2) | New (v3.0) |
| :--- | :--- | :--- |
| **Instruction Type** | "Don't commit secrets" (prohibition) | `python secrets_scan_verifier.py` (external enforcement) |
| **Skill Activation** | "Adopt the persona of an elite auditor" | Mandatory Output Template (fill these fields or task fails) |
| **Routing** | Load all files upfront (token bloat) | JIT Auto-Pilot Router in `GEMINI.md` (load only when triggered) |
| **Verification** | Trust AI self-discipline | Python harnesses with exit codes |

---

## 📡 GEMINI.md (The Active Router)

The root `GEMINI.md` is the **Master BIOS** — an Active Router that the AI reads on every session. It contains:

1. **Binary Oratory Template**: `[RECOMMENDED TIER] [RECOMMENDED MODEL] [DO] [DONT] [CONFIRM]` — forces the AI to predict the right model tier *before* executing, not echo the current one.
2. **Caveman Protocol**: Ultra-compressed communication (drop articles, filler, pleasantries) to save tokens.
3. **JIT Routing Table**: Keyword-triggered `view_file` commands that load the correct skill/workflow on-demand.
4. **Inline Micro-Rules**: Circuit Breaker (3x fail → abort), Anti-Affirmation, Code Skeleton First.

---

## 🏛️ CANONS (`canons/`)
**The Constitution — Immutable Architectural Laws**

- **`global/core-architecture.md`**: Overarching rules for how application layers communicate.
- **`global/harnesses/`**: Runnable Python verification scripts:
  - `secrets_scan_verifier.py` — Scans for hardcoded API keys, tokens, and passwords using regex patterns. Returns `[PASS]` or `[FAIL]` with exact file:line locations.
  - `migration_verifier.py` — Scans SQL migration files for dangerous operations (`DROP TABLE`, `TRUNCATE`, open RLS policies). Blocks deployment on failure.
  - `base_action_verifier.py` — Abstract base class for creating new harnesses.
- **`micro/`**: Budget-model cheat sheets with DO/DONT syntax patterns:
  - `flutter.md` — Riverpod 2.x, GoRouter, Freezed, common pitfalls.
  - `supabase.md` — Auth v2, RLS policy syntax, Edge Functions.
  - `git-workflow.md` — Commit format, branching model, pre-commit checklist.

---

## 🛡️ RULES (`rules/`)
**Algorithmic Guardrails & Decision Trees**

Each rule file contains concrete, machine-executable instructions:

| File | What It Does (v3.0) |
| :--- | :--- |
| `core-guardrails.md` | Binary Oratory gate + Circuit Breaker (3x fail → abort) |
| `tier-execution-protocol.md` | 6-Tier model classification with Auto-Router heuristics and Bento-Box workflow |
| `reasoning-standards.md` | **Mandatory Output Templates**: 5 Structural Questions + Adversarial Twin Attack block |
| `security-guardrails.md` | **Grep patterns** for secrets detection + Destructive Gate + RLS examples |
| `flutter-standards.md` | Architecture standards with **cross-reference to `canons/micro/flutter.md`** |
| `web.md` | Concrete CSP header pattern, XSS protection code, **4-State Component Map** |
| `api-connector-protocols.md` | **Zod validation snippets** + API Response Contract template + Idempotency algorithm |
| `performance-optimization.md` | **Decision Trees** for file splitting (>500 lines), caching, lazy loading |
| `caveman-activate.md` | Caveman mode with **3 Before/After transformation examples** |
| `antigravity-rtk-rules.md` | **RTK Decision Tree** (when to use `rtk` vs raw commands) |
| `context-standards.md` | Skeleton-First reading protocol, Surgical Munching |
| `interaction-protocols.md` | GPS Checkpoint format |
| `offensive-audit-protocol.md` | Attack vector checklist for security audits |
| `qmd-search-protocol.md` | QMD semantic search command syntax |
| `autoharness-protocol.md` | Action-Verifier loop definition |
| `git-workflow.md` | Commit conventions and branching rules |

---

## 🎯 SKILLS (`skills/`)
**Domain Expertise with Mandatory Output Templates**

Each skill now contains **concrete templates** the AI must fill out (not personas to "adopt"):

| Skill | Mandatory Output |
| :--- | :--- |
| `project-architect` | **Blueprint Checklist** (6 sections including "The Cut List" for scope reduction) |
| `backend-orchestrator` | **DB Schema Decision Tree** (SQL vs jsonb) + **RLS Policy SQL template** |
| `frontend-experience` | **Component State Map** (Loading/Empty/Error/Success Dart code) |
| `integrity-sentinel` | **Audit Report Template** (Severity, Reproduction Steps, Code Fix) |
| `saas-strategist` | **Context File Template** (`CONTEXT.md`) + **Viability Scorecard** (4-dimension scoring) |
| `api-contract` | **Zod Schema Templates** for Auth, Pagination, and Strict Update endpoints |
| `cost-optimizer` | **Token Budget Calculator** (action → estimated tokens → risk level) |
| `project-operator` | **Release Checklist** calling `secrets_scan_verifier.py` and `migration_verifier.py` |
| `meta-agent-admin` | **Ecosystem Update Protocol** (format validation → verify_agents.py → revert on fail) |
| `data-logic` | Freezed immutability patterns, `copyWith` mutation rules |
| `ui-finish` | Liquid Glass aesthetics, micro-interactions, shimmer loading states |
| `caveman` | Ultra-compressed communication mode with intensity levels |
| `caveman-compress` | File compression tool for memory files |
| `qmd` | QMD semantic search query types and command syntax |
| `index-project` | Project indexing automation for QMD |

---

## 🔄 WORKFLOWS (`workflows/`)
**Step-by-Step Pipelines with Exact Commands**

Each workflow now contains **runnable terminal commands** at every step:

| Workflow | Trigger | Key Commands |
| :--- | :--- | :--- |
| `/project-init` | New project scaffold | `view_file` per skill, `mkdir -p`, `verify_agents.py` |
| `/full-lifecycle` | End-to-end feature build | 6-phase pipeline: Strategy → Architecture → TDD → UI → Audit → Offload |
| `/strict-tdd` | Test-driven development | RED → GREEN → REFACTOR loop |
| `/app-builder` | Feature creation | Model → Provider → UI → Test pipeline |
| `/prod-deploy` | Production deployment | `secrets_scan_verifier.py`, `migration_verifier.py`, `npm audit` |
| `/context-prune` | Memory cleanup | `compress_memory.py`, scratchpad eviction, task archival |
| `/session-offload` | End-of-session | `git commit`, `compress_memory.py`, inline `SESSION_HANDOFF` template |
| `/code-review` | Pre-commit review | Code quality and security checklist |
| `/flutter-debug` | UI bug fixing | Screenshot + MCP tools |
| `/offensive-audit` | Security audit | Iterative Audit-Then-Patch loop |

---

## ⚙️ MECHANICAL TOOLING

### Scripts (`scripts/`)
Runnable Python utilities:

| Script | Purpose |
| :--- | :--- |
| `verify_agents.py` | **Master Verifier** — scans for broken links, missing frontmatter, protocol violations |
| `code_map.py` | AST/Skeleton map of a directory (~300 tokens vs ~5000 for full read) |
| `token_audit.py` | Identifies "ghost token" files exceeding 500-line limit |
| `compress_memory.py` | Compresses memory/log files to save input tokens |
| `deploy_foundation.py` | Deploys `.agents` to a new project |
| `sync_ai_configs.py` | Syncs AI config files after foundation updates |
| `track_budget.py` | Tracks Tier 1/2 task resolution rates |
| `preflight_check.py` | Pre-flight environment validation |
| `find_audit_targets.py` | Identifies files needing security audit |
| `context_naming_lint.py` | Lints context file naming conventions |
| `setup_qmd.py` | Sets up QMD semantic search |
| `sync_to_foundation.py` | Syncs changes back to the foundation repo |

### Templates (`templates/`)
Standardized file molds for session handoffs, architecture blueprints, and multi-AI config files.

### Evals & Docs (`evals/`, `docs/`)
Benchmarking tools and human-readable deployment manuals.

---

## Changelog

| Version | Date | Notes |
| :--- | :--- | :--- |
| **3.0.0** | 2026-05-20 | **Algorithmic Upgrade**: Transformed 21 cosmetic/referential files into executable algorithms. Added Decision Trees, Output Templates, Python harnesses, Zod snippets, and JIT Auto-Pilot Router. Binary Oratory upgraded to predictive model recommendation. |
| **1.3.0** | 2026-04-18 | Modernize foundation: adopt RTK, QMD, and Caveman. Remove obsolete manual catalogs. |
| **1.2.0** | 2026-03-26 | Integrate 10 Prompt Patterns, Root GEMINI.md, and evals/docs folders |
| **1.1.0** | 2026-03-20 | Unified Logic: Established a clear 4-pillar structure and the 82-file SaaS mapping protocol. |
| **1.0.0** | 2026-03-19 | Clean Reset to V1.0.0 |
| **0.9.0** | 2026-03-15 | Initial baseline |
