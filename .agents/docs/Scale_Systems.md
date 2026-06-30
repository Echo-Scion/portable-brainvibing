# VOLUME IV: RULE LIBRARY (`rules/`) — 10 Law Files

---

## Chapter 9: Complete List of Rule Files

### 9.1. `core-guardrails.md` (142 lines | 11KB)
**Supreme Law.** Contains 10 sections:
1. **Unified Response Protocol**: Mandatory footer CHECKPOINT/EVIDENCE/EVALUATION/NEXT in every response.
2. **Environment Boundary Check (§1.5)**: Forbids implementing the "82-File Mandate" in the `_foundation` repo.
3. **Native Orion Execution (§1.6)**: Requires using `orion.py`, not external binaries.
4. **Omni-Buffer Context Protocol (§1.7)**: Requires reading `context.json` at the start of the session.
5. **IDE-Agnostic Tooling (§1.8)**: Translates commands to the native tools of each IDE.
6. **Reasoning Standards (§2)**: Plan Protocol, Anti-Laziness Mandate, 5-Why Script, Evidence Mandate.
7. **Edge-Case Tax (§2)**: Mandatory Edge-Case Matrix for STANDARD/PREMIUM tasks.
8. **Circuit Breaker (§4)**: 3 consecutive failures = ABORT and ask for human help.
9. **Rule Precedence (§5)**: Priority order: Security > Core > Tier > Domain > Skills.
10. **Token Efficiency (§9)**: AST Hollowing, Sleep-State Delegation, Anti-Full-Read.

### 9.2. `security-guardrails.md` (168 lines | 9.3KB)
**Security & Offensive Audit Law. Contains:**
- **Pre-Commit Secrets Scan**: Required `grep` commands before every `git commit` to detect OpenAI keys (`sk-*`), `SUPABASE_SERVICE_ROLE_KEY`, PEM private keys.
- **Prompt Injection Defense**: Deterministic algorithm detecting and rejecting malicious instructions ("Ignore previous instructions").
- **Least Privilege**: Required justification for every permission. Default = READ-ONLY.
- **Destructive Command Gate**: `rm -rf`, `DROP TABLE`, `DELETE FROM` without WHERE require `[DO: YES]` confirmation.
- **Offensive Audit Protocol**: AI is forced to act as a "Lead Quant Security Auditor" who:
  - Runs mutation testing (intentionally introducing bugs, ensuring tests catch them).
  - Checks every `catch`/`except` — if there is a silent fail, it is immediately a CRITICAL VULNERABILITY.
  - Audits vertical slices (Route → Controller → Service → Repo), not layer-by-layer.

### 9.3. `tier-execution-protocol.md` (172 lines | 11KB)
**Resource Allocation Engine. Divides tasks into 3 tiers:**

| Tier | Capabilities | Model Profile |
|:--|:--|:--|
| **BUDGET** | Fix 1 file, indexing, batch | Flash/Haiku |
| **STANDARD** | UI, code gen, testing | Sonnet/Pro |
| **PREMIUM** | Architecture, complex debugging | Opus/Thinking |

**Bento-Box Law**: BUDGET models are forbidden from multitasking. Only 1 file per iteration.
**Auto-Abort (Downgrade Guard)**: If the active model is weaker than the target tier, the agent MUST `[ABORT: TIER MISMATCH]`.
**Token Economy**: BUDGET = max 1 file read; STANDARD = 3-5 surgical reads; PREMIUM = unlimited (justified).
**Adversarial Twin Protocol**: Write exploit script → run → log results in XML `<adversarial_attack>`.

### 9.4. `development-operations.md` (155 lines | 9.3KB)
**Development Operations. Contains 3 sub-systems:**
- **Git Workflow**: Commit conventions (`<type>(<scope>): <subject>`), branching (`feat/*`, `fix/*`), Save Point Protocol (commit after every successful sub-step).
- **AutoHarness Protocol**: AI must write automated validation scripts (Harness) for destructive operations. Types: Action-Verifier, Action-Filter, Policy. Required output: `action_id`, `is_legal`, `violated_rule`, `fix_hint`.
- **Context Management**: 3-layer context hierarchy (Global → Project → App), Skeleton-First Law (BUDGET forbidden from full-read), 82-File Mandate (only for target SaaS projects).

### 9.5. `performance-optimization.md` (94 lines | 3.6KB)
**Bolt Protocol. Before any optimization, must pass 3 gates:**
1. Measurable? → If NO, cancel.
2. Readable? → If NO, cancel.
3. Scope < 50 lines? → If NO, cancel.

**500-Line Decision Tree**: Files > 500 lines = MUST refactor.
**Keyword Surgical Loading**: Map (AST) → Search (grep) → Surgical Read (view_file with line range).

### 9.6. `web-api-standards.md` (131 lines | 3.9KB)
**Web & API Standards. Contains:**
- **CSP (Content Security Policy)**: Required meta tag or header.
- **4-State Map**: Every UI component fetching data MUST handle: Loading, Error, Empty, Success.
- **Zod Schema Mandate**: NEVER trust `req.body`. Zod validation is mandatory.
- **API Response Contract**: Standard format `{ success: true/false, data/error: {...} }`.
- **Idempotency Pattern**: Critical operations require `Idempotency-Key` header.

### 9.7. `context-standards.md` (19 lines | 1.2KB)
Context boundary enforcement. Forbids implementing the "82-File Mandate" in the `_foundation` repo. Forces **AST Hollowing** (forbidding `view_file` on files > 100 lines without `rtk read`).

### 9.8. `prerequisites.md` (34 lines | 2.3KB)
**Graceful Fallback Matrix. Defines 4 prerequisites.md) and their fallbacks:**

| Prerequisite | Fallback |
|:--|:--|
| RTK (Rust) | `grep_search` or `view_file` with line range |
| Orion (Python) | Manual `grep_search` on `.orion/` |
| QMD/Ollama | Manual `grep_search` and traversal |
| Subagent Orchestration | Handle in main thread with aggressive `grep_search` |

### 9.9. `antigravity-rtk-rules.md` (54 lines | 1.6KB)
Specific rules for RTK integration in the Antigravity IDE. Decision tree and command examples.

### 9.10. `RULES_INDEX.md` (1.4KB)
Compiled index of all rules. Parsed by NanoBrain for fast filtering during JIT routing.

### 9.11. `rules/local/` (Sub-directory)
Place for project-specific rules that override global rules. Empty in `_foundation`.

---

# VOLUME V: SKILL.md) / PERSONA (`skills/`) — 16 Specializations

---

## Chapter 10: Skill Concept
Each skill is a "hat" worn by the AI. When loaded, the skill limits the AI's focus to a specific domain and enforces a specific mindset. Each skill folder contains `SKILL.md` (mandatory instructions) and optionally `references/` (in-depth supporting documents).

### 10.1. `ai-engineer`
**Domain:** Mitigating the probabilistic nature of LLMs.
**Content:** Assertion matrix, Confidence Gates, anti-hallucination. Used when the agent modifies the `.agents` folder itself.

### 10.2. `api-contract`
**Domain:** Client/server interface contracts.
**Content:** OpenAPI specifications, Zod validation, API safety patterns.
**Reference:** `references/api_safety_patterns.md`.

### 10.3. `project-architect` (formerly backend-orchestrator)
**Domain:** Master backend architect.
**Content:** Node.js memory leak management, connection pooling, SQL optimization, database indexing.
**References:** 6 sub-documents — `backend-architect.md`, `backend-optimizer.md`, `cache-optimizer.md`, `db-expert.md`, `enterprise_patterns.md`, `node_performance_tuning.md`, `postgres_patterns.md`.

### 10.4. `brain-graph`
**Domain:** Operating `orion.db` and local RAG.
**Content:** FTS5 querying, triplet injection, SQLite maintenance.

### 10.5. `caveman`
**Domain:** Ultra-terse communication compression.
**Content:** 6 intensity levels. Supports `wenyan` (classical Chinese variant).

### 10.6. `caveman-compress`
**Domain:** `.md` file compression.
**Content:** Reads markdown files and replaces them with terse versions via regex. Saves a `.original.md` backup.

### 10.7. `cost-optimizer`
**Domain:** Token and cloud budget management.
**Content:** Routing cheap models (Haiku) for simple tasks, expensive models (Opus) for complex tasks.

### 10.8. `data-logic`
**Domain:** Data immutability.
**Content:** Forbids global state, Redux/Zustand patterns, pure functions, DTOs must not be mutated.

### 10.9. `frontend-experience`
**Domain:** UI/UX debugging.
**Content:** Fixing excessive re-renders, DOM infinite loops, React/Flutter state synchronization.
**Reference:** `references/ux-designer.md`.

### 10.10. `integrity-sentinel`
**Domain:** Red Team & Automated QA.
**Content:** Architecture audit, bloat audit, duplicate audit, fail-fast audit, logic audit, performance audit, retry audit, load testing.
**References:** 11 sub-documents: `architecture-audit.md`, `bloat-audit.md`, `duplicate-audit.md`, `fail-fast-audit.md`, `flutter_testing_patterns.md`, `load_testing_tactics.md`, `logic-audit.md`, `master-audit.md`, `performance-audit.md`, `plan-checklist.md`, `retry-audit.md`, `telemetry-gate.md`.

### 10.11. `meta-agent-admin`
**Domain:** Architect of the `.agents` system itself.
**Content:** Ecosystem evolution, rule creation, routing integrity.
**References:** `agent-architect.md`, `agent-evolution.md`, `context-manager.md`, `knowledge.md`, `loop_design_patterns.md`, `system-admin.md`, `tech-writer.md`.

### 10.12. `palette`
**Domain:** Micro-aesthetics & accessibility.
**Content:** CSS tokens, smooth animations, ARIA labels, glassmorphism, color harmony, keyboard navigation.

### 10.13. `project-architect`
**Domain:** High-scale PRD & Blueprints.
**Content:** Translating user ideas into technical documents before code is written.
**References:** `architectural_standards.md`, `startup_growth.md`, `strategic_rigor.md`, `structural_pillars.md`.

### 10.14. `project-operator`
**Domain:** DevOps & resilience.
**Content:** Dockerfiles, CI/CD pipelines, Nginx, chaos engineering.
**References:** `chaos-engineer.md`, `release-manager.md`.

### 10.15. `saas-strategist`
**Domain:** SaaS business strategy.
**Content:** Viability analysis, monetization, growth, viral content.
**References:** `saas-growth.md`, `saas-viability.md`, `technical_content.md`, `viral_growth.md`.

### 10.16. `ui-finish`
**Domain:** Premium UI final polish.
**Content:** Empty states, loading spinners, error boundaries, Liquid Glass widgets.
**Reference:** `visual_engineering.md`.

---
