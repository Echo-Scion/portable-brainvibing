# Claude Instructions: {project_name}

<!-- START FOUNDATION MANDATES -->
> **CRITICAL HABITAT NOTICE:** This directory is a satellite deployment of the Master Habitat. This file defines the **absolute operational constraints** for all agents operating within `{project_name}`. It is always-on and non-negotiable.

## 1. MANDATORY BOOTSTRAP (Session Resume)
- **Goal:** Immediately recover context, atomic task status, and architectural constraints.
- **CRITICAL**: Read `.agents/rules/core-guardrails.md` at the start of **every** task. This file contains the "Pre-Execution Firewall" (Binary Oratory), "Surgical Munching" protocols, and "Reasoning Standards" that are no longer hardcoded in this BIOS.
- For task-specific rules, execute search on `.agents/rules/` to find domain-specific files.
- **ANTI-AFFIRMATION MANDATE**: Never simply agree with or affirm the user's ideas/code. You must proactively find flaws, logical gaps, missed edge cases, or scalability issues. Treat every initial idea as flawed until proven otherwise. You MUST provide exactly 3 specific points of criticism along with 3 corresponding actionable solutions before proceeding.

## 2. ABSOLUTE [DONT] LIST
- `[DONT]` Delete production databases or their contents.
- `[DONT]` Commit secrets, API keys, or credentials to any file.
- `[DONT]` Execute `rm -rf` or `Remove-Item -Recurse` without explicit confirmation.
- `[DONT]` Modify `GEMINI.md` or `rules/` without a Binary Oratory pre-flight.

## 3. MASTER ROUTING INDEX
> Use QMD (npx @tobilu/qmd query) for semantic discovery.

### 3.1 CORE RULES (Constraints)
| Focus Area | Rule File to Load |
| :--- | :--- |
| **Behavior & Logic** | `rules/core-guardrails.md`, `rules/reasoning-standards.md` |
| **Tier & Context** | `rules/tier-execution-protocol.md`, `rules/context-standards.md` |
| **Coding Limits** | `rules/autoharness-protocol.md`, `rules/flutter-standards.md` |
| **Security & Git** | `rules/security-guardrails.md`, `rules/git-workflow.md` |

### 3.2 DOMAIN CANONS (Architecture)
| Domain | Canon Path | Purpose |
| :--- | :--- | :--- |
| **System-wide** | `canons/global/core-architecture.md` | Non-negotiable global software patterns |
| **AI Harness** | `canons/global/harnesses/README.md` | Automated Action-Verifier execution loops |
| **Microservices**| `canons/micro/README.md` | Edge-functions & lightweight service limits |

### 3.3 SKILL ORCHESTRATORS (Actions)
| Task involves... | Invoke skill |
| :--- | :--- |
| SaaS validation, business logic, growth, monetization | `saas-strategist` |
| System architecture, blueprints, technical APIs, database, backend | `backend-orchestrator` |
| Mobile/Web UI, UX flow, layout debugging, Liquid Glass | `frontend-experience` |
| Modifying `.agents/` rules, doc writing, knowledge ingestion | `meta-agent-admin` |
| Release pipeline, CI/CD, relocations, tech debt, bug chaos | `project-operator` |
| Strict API type-safety, zod schemas, swagger | `api-contract` |
| State immutability, pipeline schemas, strict data objects | `data-logic` |
| Core security bounding, QA, evaluations, STRIDE limits | `integrity-sentinel` |

## 4. THREE-TIER REASONING MODEL
- **BUDGET**: Atomic, single-file, deterministic (use Haiku/fast model)
- **STANDARD**: Multi-file, cross-module (use Sonnet/standard model)
- **PREMIUM**: Architecture, security, complex reasoning (use Opus/premium model + extended thinking)

See `.agents/rules/tier-execution-protocol.md` for tier determination logic.

## 5. CONTEXT HIERARCHY (4-Pillar System)
When working with projects using this foundation:

```
context/
├── 00_Strategy/    # Business goals, monetization
├── 01_Product/     # Features, roadmap
├── 02_Creative/    # Design, UX, style
└── 03_Tech/        # Architecture, API, data models
```

Core files: `BLUEPRINT.md`, `ROADMAP.md`, `STYLE_GUIDE.md`, `ARCHITECTURE.md`

## 6. TOKEN-EFFICIENT PROTOCOL (Context Economy)
- **Code Skeleton First**: Before wide refactors or exploring large codebases, run `python .agents/scripts/code_map.py` to extract class/function layouts without blowing up context.
- **Token Audits**: If context gets heavy or slow, run `python .agents/scripts/token_audit.py` to identify ghost tokens and refactor files > 500 lines.
- **Telegraphic Communication**: Short sentences (8-10 words max). No filler, no preamble, no pleasantries.
- **English Compression**: Code stays normal. English gets compressed.
- **Surgical Execution**: Think before acting. Read once. Prefer editing over rewriting.
- **Size Limits**: Skip files >100KB unless explicitly required.
- **Tool-First**: Result first. No explanation unless asked. Avoid parenthetical clauses.
- **Surgical Munching**: Lazy-load via QMD. Check LEARNINGS before PREMIUM tasks.

## 7. CRITICAL FILES

### Always Read First
- `.agents/rules/core-guardrails.md` - Core protocols, reasoning standards
- `.agents/workspace_map.md` - Orchestration entry point
- `GEMINI.md` - Workspace mandates (if exists)

### Never Modify Without Binary Oratory
- `GEMINI.md`
- Anything in `.agents/rules/`

## 8. SYNCHRONIZATION SCRIPTS

Located in `.agents/scripts/`:

| Script | Purpose | When to Use |
| `verify_agents.py` | Structural integrity check | Before publishing changes |
| `deploy_foundation.py` | Deploy foundation to project | Setting up new project |
| `setup_qmd.py` | Project indexing | When starting new project |

Run verification before any .agents/ changes:
```bash
python .agents/scripts/verify_agents.py
```

## 9. SPECIAL PROTOCOLS

### Circuit Breaker
If any operation fails 3x consecutively → ABORT and request human intervention

### Evidence Mandate
PREMIUM tasks only complete when verified through:
- Empirical reproduction
- Test execution
- Explicit output validation

### Edge-Case Tax
Before finalizing features, document 2-3 failure modes and their handling

### Assumption Audit
For PREMIUM tasks, list every technical assumption before proceeding

---
*Mandate Version: 2.4.0 (Multi-AI Gateway)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC INSTRUCTIONS
<!-- Add your custom Claude instructions here. They will be preserved during foundation updates. -->