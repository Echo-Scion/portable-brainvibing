# VOLUME IV: RULE LIBRARY (`rules/`) — 10 Law Files

---

## Chapter 9: Complete List of Rule Files

### 9.1. `core-guardrails.md`
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

### 9.2. `security-guardrails.md`
**Security & Offensive Audit Law. Contains:**
- **Pre-Commit Secrets Scan**: Required `grep` commands before every `git commit` to detect OpenAI keys (`sk-*`), `SUPABASE_SERVICE_ROLE_KEY`, PEM private keys.
- **Prompt Injection Defense**: Deterministic algorithm detecting and rejecting malicious instructions ("Ignore previous instructions").
- **Least Privilege**: Required justification for every permission. Default = READ-ONLY.
- **Destructive Command Gate**: `rm -rf`, `DROP TABLE`, `DELETE FROM` without WHERE require `[DO: YES]` confirmation.
- **Offensive Audit Protocol**: AI is forced to act as a "Lead Quant Security Auditor" who:
  - Runs mutation testing (intentionally introducing bugs, ensuring tests catch them).
  - Checks every `catch`/`except` — if there is a silent fail, it is immediately a CRITICAL VULNERABILITY.
  - Audits vertical slices (Route → Controller → Service → Repo), not layer-by-layer.

### 9.3. `tier-execution-protocol.md`
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

### 9.4. `development-operations.md`
**Development Operations. Contains 3 sub-systems:**
- **Git Workflow**: Commit conventions (`<type>(<scope>): <subject>`), branching (`feat/*`, `fix/*`), Save Point Protocol (commit after every successful sub-step).
- **AutoHarness Protocol**: AI must write automated validation scripts (Harness) for destructive operations. Types: Action-Verifier, Action-Filter, Policy. Required output: `action_id`, `is_legal`, `violated_rule`, `fix_hint`.
- **Context Management**: 3-layer context hierarchy (Global → Project → App), Skeleton-First Law (BUDGET forbidden from full-read), 82-File Mandate (only for target SaaS projects).

### 9.5. `performance-optimization.md`
**Bolt Protocol. Before any optimization, must pass 3 gates:**
1. Measurable? → If NO, cancel.
2. Readable? → If NO, cancel.
3. Scope < 50 lines? → If NO, cancel.

**500-Line Decision Tree**: Files > 500 lines = MUST refactor.
**Keyword Surgical Loading**: Map (AST) → Search (grep) → Surgical Read (view_file with line range).

### 9.6. `web-api-standards.md`
**Web & API Standards. Contains:**
- **CSP (Content Security Policy)**: Required meta tag or header.
- **4-State Map**: Every UI component fetching data MUST handle: Loading, Error, Empty, Success.
- **Zod Schema Mandate**: NEVER trust `req.body`. Zod validation is mandatory.
- **API Response Contract**: Standard format `{ success: true/false, data/error: {...} }`.
- **Idempotency Pattern**: Critical operations require `Idempotency-Key` header.

### 9.7. `context-standards.md`
Context boundary enforcement. Forbids implementing the "82-File Mandate" in the `_foundation` repo. Forces **AST Hollowing** (forbidding `view_file` on files > 100 lines without `rtk read`).

### 9.8. `prerequisites.md`
**Graceful Fallback Matrix. Defines 4 prerequisites and their fallbacks:**

| Prerequisite | Fallback |
|:--|:--|
| RTK (Rust) | `grep_search` or `view_file` with line range |
| Orion (Python) | Manual `grep_search` on `.orion/` |
| QMD/Ollama | Manual `grep_search` and traversal |
| Subagent Orchestration | Handle in main thread with aggressive `grep_search` |

### 9.9. `antigravity-rtk-rules.md`
Specific rules for RTK integration in the Antigravity IDE. Decision tree and command examples.

### 9.10. `RULES_INDEX.md`
Compiled index of all rules. Parsed by NanoBrain for fast filtering during JIT routing.

### 9.11. `rules/local/` (Sub-directory)
Place for project-specific rules that override global rules. Empty in `_foundation`.

---

