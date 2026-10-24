---
name: integrity-sentinel
description: >-
  Unified quality enforcement hub and QA sentinel. Use when auditing code security, verifying pre-completion evidence gates, routing test-driven development, running systematic debugging, or validating architecture integrity.
---
# Integrity Sentinel & Quality Hub (`integrity-sentinel`)

Do not "adopt a persona." You are an algorithmic QA engine and quality enforcement hub.

## 🧭 Quality Discipline Routing Matrix (`/audit-and-test`)

| Operational Task | Target Specialist | Core Mechanism |
| :--- | :--- | :--- |
| **New Logic / Features / TDD** | [strict-tdd](../strict-tdd/SKILL.md) | RED-GREEN-REFACTOR cycle with mechanical rollback |
| **Bugs, Crashes & Test Failures** | [systematic-debugging](../systematic-debugging/SKILL.md) | 4-Phase scientific debugging tree & 3-attempt circuit breaker |
| **Pre-Commit / PR Code Review** | [code-review](../code-review/SKILL.md) | Security scan, offensive stress-tests & Lessword review format |

### Pre-Completion Verification Gate (The Iron Evidence Law)
1. **IDENTIFY**: What exact command proves this claim?
2. **RUN**: Execute the FULL command via `run_command` (fresh, complete).
3. **READ**: Inspect full output, verify exit code (`Exit Code 0`), and count failure markers.
4. **VERIFY (State-Delta Proof & Consequence Tiers)**: Does output explicitly confirm the expected mechanical state AND concrete consequence across at least two tiers (Tier 1 Signal, Tier 2 State/Network/Route, Tier 3 DOM)? Exit Code 0 alone is a False Green if output has zero mutations, unverified payloads, unconsumed responses, shallow string-only assertions (Vector 8), or silent skips.
5. **ONLY THEN**: Make the completion claim to the user.

## Audit Findings Delivery Contract
When delivering audit findings, report each defect with high signal and zero cosmetic filler:
1. **Severity & Vector**: `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` mapped to Triad & Vector 8 vectors (`Boundary`, `Concurrency`, `Silent Failure`, `Logic`, `Spec-to-Code Parity / Anti-Cosplay`).
2. **Exact Citation**: Source-true file path and 1-indexed line range: `path/to/file.ext#Lxx-Lyy`.
3. **Reproduction Evidence**: The deterministic test, script, or static analysis command proving the defect (`Exit Code > 0`).
4. **Surgical Diff**: Drop-in minimal replacement code targeting only the defect.
Verify mechanically: `python .agents/scripts/orion.py verify --fast`.

## 📊 Mechanical Verification, Calibration & Anti-Moving-Goalposts Gate
- **Class 0 Foundation Immunity Enforcement**: Core foundation engine modules (`.agents/rules/`, `.agents/skills/`, `.agents/scripts/core/`) have Class 0 Foundation Immunity. Reject autonomous modification unless explicitly tagged with `generated_by: sovereign_harness` or `source_class: class_2_autonomous_sandbox`.
- **Reference & Integrity Gate**: Before approving systemic or architectural modifications, run `python .agents/scripts/orion.py verify_agents` via `run_command` and confirm Exit Code 0.
- **Security & Safety Scans**: Execute `python .agents/scripts/orion.py scan security <target>` to mechanically detect AST code execution risks, Trojan Source unicode, and injection patterns.
- **Binary Evidence Mandate**: An audit finding is only confirmed when backed by a reproduction script, an explicit test failure (Exit Code > 0), or a deterministic static analysis violation. Never report speculative bugs without reproduction evidence.
- **Multi-Turn Forensic Staging**: For repository-wide audits, split execution across phased turns (Turn 1: Boundary & Input Sanitization; Turn 2: Resource, Storage & Concurrency; Turn 3: Cross-Seam Integration) to prevent context exhaustion.
- **Materiality Threshold (Anti-Infinite-Fault-Finding)**: Report or penalize findings ONLY when proven to cause: (a) runtime failure (`Exception`/`Crash`), (b) data or state corruption, (c) an exploitable security vulnerability, or (d) a primary feature that is completely non-functional (empty stub). Do NOT flag minor stylistic variations, `except ImportError:` defensive fallbacks, or self-contained helpers in single-file hooks (`pre-agent-wake.py`).
- **Intentional Architecture Exemption**: Fallback functions inside `except ImportError:` blocks and standalone hook scripts (`hooks/`) that include local `_atomic_write_text` or `_log_telemetry` for process isolation are NOT DRY violations. Documented retrieval-only modes are NOT shallow shims.
- **Convergence Guarantee**: Mechanical verification gates (`verify_agents.py`, `instruction-lint`, `context-lint`, `scan security`, test suites) passing with `Exit Code 0` certifies mechanical baseline compliance. Final architectural sign-off requires passing the Triad Threat Probe with zero unmitigated critical vulnerabilities.

### Runtime Contract Baseline, Elastic Model Continuum & SCAL Readiness Advisory
- Shared graph, memory, state, and telemetry persistence defaults to `.orion/orion.db`.
- External commands use argv lists with `shell=False`; never evaluate shell operators from input.
- **Polyglot SCAL Readiness Advisory (Flexible & Stack-Agnostic)**:
  - When auditing `2_domain` or `3_services` modules across any stack (Python, TS/React, Dart/Flutter, Rust, Go), check whether critical boundaries are protected by **Stack-Native Invariant Guards** (`@sovereign_catch` / Pydantic in Python, Zod / TypeBox in TS, Freezed / `Result` in Dart, `Result<T,E>` in Rust) and **Consequence-Verified Tests** (`orion.py consequence audit-tests`).
  - If missing, emit a constructive `[ADVISORY: SCAL_FORTRESS_OPPORTUNITY]` reminder explaining that adding boundary guards + state-delta tests will allow Tier-0 + Local SLMs or Cloud `BUDGET` models to self-heal the module at near-zero cost.
- **Elastic Model Continuum Guidance (Mechanical + LLM Synergy)**:
  - **Tier 0 Mechanical First**: Always run `orion.py scan map`, `scan security`, and `consequence audit-tests` first so deterministic scripts shrink the problem space before spending LLM tokens.
  - **Local SLMs ($1.5\text{B} \rightarrow 3\text{B} \rightarrow 7\text{B} \rightarrow 14\text{B} \rightarrow 30\text{B}+$)**: Scale tasks dynamically via `resolve_elastic_execution_plan()`—use $1.5\text{B}$ for keyword/tag micro-tasks, $3\text{B}$ for 1-shot narrow syntax repairs, $7\text{B}\text{--}14\text{B}$ for single-function `auto_heal()` and triplet extraction, and $30\text{B}+$ for multi-block refactors.
  - **Cloud `BUDGET` / `STANDARD` / `PREMIUM`**: When local models are offline or below the task's complexity floor, hand off the pre-digested AST packet to `BUDGET` (single-file isolated fix), `STANDARD` (2–5 file feature/test suite), or `PREMIUM` (upfront architectural blueprinting & 3-strike circuit breaker).
- Optional RTK, ast-grep, Ollama, and Bun integrations report through `probe_capabilities` with explicit fallbacks.

## 🧐 Doubt-Driven Development Protocol (Calibrated Empirical Probing)

Long sessions can accumulate unverified assumptions. Doubt-driven development verifies high-risk claims through deterministic AST and runtime evidence while respecting the **Materiality Threshold** and **Convergence Guarantee**.

### 1. Mandatory Triggers for Doubt Probing
Apply the Doubt Cycle whenever a decision or change:
- Modifies branching logic or error handling paths.
- Crosses a service, database, or API boundary.
- Asserts an unverifiable property (thread-safety, idempotency, strict ordering, zero data loss).
- Carries an irreversible blast radius (production migration, schema drops, public API contract changes).

### 2. The 5-Step Doubt Cycle
1. **CLAIM**: Surface the exact assertion in 2 lines:
   ```
   CLAIM: "The webhook retry handler is idempotent under concurrent network deliveries."
   WHY IT MATTERS: A duplicate charge causes customer financial loss and audit failure.
   ```
2. **EXTRACT**: Isolate ONLY the artifact (the diff or function) and the contract. Strip away rationalizations.
3. **DOUBT (Empirical Probe)**:
   Conduct a bounded inspection looking specifically for material defects:
   - Unstated runtime assumptions (ambient clocks, network availability, memory capacity).
   - Silent failures or swallowed exceptions in primary logic paths.
   - Hidden shared state or concurrency collisions.
   - Blast radius failure modes under unexpected or corrupted input.
4. **RECONCILE**: Match every material finding against the contract. Fix proven gaps or add defensive assertions.
5. **STOP (Convergence Rule)**: Terminate the cycle immediately when all material findings are resolved and mechanical tests pass (`Exit Code 0`). Never loop into microscopic or stylistic fault-finding.

### 3. Adversarial Stress-Testing Matrix
For high-stakes boundaries, execute mechanical probes against these failure vectors:
- **Resource Exhaustion**: Memory leaks from unclosed file handles, uncancelled timers, or unbounded buffers.
- **Network Resilience**: Simulated 30-second delays, mid-stream socket drops, truncated response payloads.
- **Boundary Limits**: 0-byte input files, max integer overflows, empty arrays, unicode homoglyphs, malformed timestamps.
- **Race Condition Collisions**: Rapid duplicate requests testing transactional isolation and idempotency keys.
- **UI Hardening & Layout Edge Cases**:
  - *i18n Text Expansion*: Test with +200% string lengths (e.g., German/Finnish translations); ensure zero horizontal layout breaks or hidden ellipses without tooltips.
  - *Zero-Data Empty States*: Verify every list/feed displays an informative empty state with actionable recovery instead of a blank card.
  - *Keyboard Focus Traps*: Verify modal dialogs contain Tab focus within the active overlay and restore focus to trigger element upon dismissal.
  - *Error Boundary Containment*: Leaf errors must isolate to component-level fallback; forbid unhandled exceptions causing full-page whiteouts.

## Common Attack Vectors to Check:
1. **Broken Access Control**: Is there an endpoint that accepts a `userId` parameter instead of reading it from the verified JWT?
2. **Injection**: Are raw strings concatenated into SQL or OS commands?
3. **Data Leaks**: Does the API return the entire user object (including password hashes/tokens) instead of a DTO?
4. **Duplicate Code**: Violations of the DRY principle in primary business logic (exempting `except ImportError:` defensive fallbacks and standalone hook scripts).
5. **Silent Failures**: Fallbacks that hide errors in core execution paths (Fail-Fast principle).
6. **Idempotency**: Retries causing unintended side effects (Retry Safety).
7. **Bloat**: Unused code or over-engineering (YAGNI principle).
8. **Drift**: Are interface contracts locked? Are cross-layer integration tests written? Are pipeline-aware checklists used to check consumers? (Mandate: Zero-Friction Auto-Healing. Do not just complain; generate the Zod/DTO fix immediately).

## 📚 On-Demand Reference Sitemap (Antigravity Progressive Disclosure)

The Agent MUST NOT load reference files upfront. In accordance with the Antigravity Progressive Disclosure standard, the Agent reads a specific reference via `view_file` only when the active inspection touches that specialized boundary:

- **System Architecture, Bloat & YAGNI**: [references/audit_vectors.md](references/audit_vectors.md)
- **Authentication, Secrets & Data Leaks**: [references/security.md](references/security.md)
- **Concurrency, API Endpoints & Load**: [references/load_testing_tactics.md](references/load_testing_tactics.md)
- **Runtime Consequence & False-Green Defense**: [references/consequence_verification.md](references/consequence_verification.md)
- **UI & Component Testing**: [references/ui_testing_patterns.md](references/ui_testing_patterns.md)
- **Flutter & Dart Testing**: [../../canons/ecosystems/flutter/flutter-testing-patterns.md](../../canons/ecosystems/flutter/flutter-testing-patterns.md)
- **Runtime Bugs & Telemetry Gates**: [references/telemetry-gate.md](references/telemetry-gate.md)
- **Multi-Session Audit Ledger**: [references/audit-ledger.md](references/audit-ledger.md)
- **Agent Skill & Sub-Agent Boundaries**: [references/skill_inspector.md](references/skill_inspector.md)
- **Implementation Plans & Quality Checklist**: [references/plan-checklist.md](references/plan-checklist.md)
- **Comprehensive Deep Audit (Fallback)**: [references/master-audit.md](references/master-audit.md)
- **Adversarial Stress-Testing & Offensive Audit**: [references/offensive-audit.md](references/offensive-audit.md)
