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
4. **VERIFY (State-Delta Proof & Consequence Tiers)**: Does output explicitly confirm the expected mechanical state AND concrete consequence across at least two tiers (Tier 1 Signal, Tier 2 State/Network/Route, Tier 3 DOM)? Exit Code 0 alone is a False Green if output has zero mutations, unverified payloads, unconsumed responses, or silent skips.
5. **ONLY THEN**: Make the completion claim to the user.

## Audit Output Template (MANDATORY)
When asked to perform a security audit or QA check on a file, you MUST return the results using this exact format. Do not use conversational text.

```markdown
## Audit Report: `[Filename]`

### [Vulnerability 1 / Bug 1]
- **Severity**: [CRITICAL | HIGH | MEDIUM | LOW]
- **Description**: [Exactly what is wrong]
- **Reproduction**: [Step-by-step or exact input that triggers the bug]
- **Code Fix**:
  ```[language]
  // Provide the exact replacement code
  ```

### [Vulnerability 2]
...
```

## 📊 Mechanical Verification, Calibration & Anti-Moving-Goalposts Gate
- **Reference & Integrity Gate**: Before approving systemic or architectural modifications, run `python .agents/scripts/orion.py verify_agents` via `run_command` and confirm Exit Code 0.
- **Security & Safety Scans**: Execute `python .agents/scripts/orion.py scan security <target>` to mechanically detect AST code execution risks, Trojan Source unicode, and injection patterns.
- **Binary Evidence Mandate**: An audit finding is only confirmed when backed by a reproduction script, an explicit test failure (Exit Code > 0), or a deterministic static analysis violation. Never report speculative bugs without reproduction evidence.
- **Materiality Threshold (Anti-Infinite-Fault-Finding)**: Report or penalize findings ONLY when proven to cause: (a) runtime failure (`Exception`/`Crash`), (b) data or state corruption, (c) an exploitable security vulnerability, or (d) a primary feature that is completely non-functional (empty stub). Do NOT flag minor stylistic variations, `except ImportError:` defensive fallbacks, or self-contained helpers in single-file hooks (`pre-agent-wake.py`).
- **Intentional Architecture Exemption**: Fallback functions inside `except ImportError:` blocks and standalone hook scripts (`hooks/`) that include local `_atomic_write_text` or `_log_telemetry` for process isolation are NOT DRY violations. Documented retrieval-only modes are NOT shallow shims.
- **Convergence Guarantee**: When all mechanical verification gates (`verify_agents.py`, `instruction-lint`, `context-lint`, `scan security`, test suites) pass with `Exit Code 0` and zero active runtime or mathematical bugs exist, the audit MUST converge and approve without inventing microscopic nitpicks.

### Runtime Contract Baseline
- Shared graph, memory, state, and telemetry persistence defaults to `.orion/orion.db`.
- External commands use argv lists with `shell=False`; never evaluate shell operators from input.
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

## 📚 Pre-Audit Routing Hook (Hard Gate)

> **MANDATORY**: You suffer from Agentic Amnesia. You are FORBIDDEN from generating the `## Audit Report` until you have executed a `view_file` tool call on at least one relevant reference file from the table below based on the context of the code you are auditing.

| If Code Involves... | Immediately Load (view_file) |
| :--- | :--- |
| **System Architecture, High-Level Structure** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Large Files, Unused Code, YAGNI** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Repeated Logic, Missing DRY** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Error Handling, Try/Catch, Fallbacks** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Logic, Broken Math, State Mutation, Data Drift** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Optimization, Big-O, Memory Leaks, Rebuilds** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **UI & Component Tests** | .agents/skills/integrity-sentinel/references/ui_testing_patterns.md |
| **Flutter & Dart Testing, Widget Tests** | .agents/canons/ecosystems/flutter/flutter-testing-patterns.md |
| **API Endpoints, Concurrency, Load** | .agents/skills/integrity-sentinel/references/load_testing_tactics.md |
| **Implementation Plans, Review** | .agents/skills/integrity-sentinel/references/plan-checklist.md |
| **Network Requests, Retries, Idempotency** | .agents/skills/integrity-sentinel/references/audit_vectors.md |
| **Authentication, JWT, SQL, Passwords, Security** | .agents/skills/integrity-sentinel/references/security.md |
| **Runtime Bugs, Crashes, Errors, Debugging** | .agents/skills/integrity-sentinel/references/telemetry-gate.md |
| **General QA, Edge Cases** | .agents/skills/integrity-sentinel/references/master-audit.md |
| **Codebase Audit, Audit Ledger, Multi-Session Audit** | .agents/skills/integrity-sentinel/references/audit-ledger.md |
| **Agent Skill Audit, Sub-Agent Permissions, Tool Boundary** | .agents/skills/integrity-sentinel/references/skill_inspector.md |
| **Runtime Consequence, False Green Prevention, Journey Replay** | .agents/skills/integrity-sentinel/references/consequence_verification.md |
| **Comprehensive Deep Audit (Fallback)** | .agents/skills/integrity-sentinel/references/master-audit.md |

### The Reference Evidence Flag
Before writing the `## Audit Report`, you MUST output the following XML block to prove you have read the reference:
```xml
<reference_loaded>
I have executed view_file on [Path to Reference] and applied its standards.
</reference_loaded>
```
If this block is missing, your response is invalid.
