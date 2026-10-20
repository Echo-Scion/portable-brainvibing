---
name: code-review
description: >-
  Conducts code reviews, pull request audits, and offensive security checks using adversarial verification. Use when reviewing diffs, auditing pull requests, checking security boundaries, or evaluating code quality before merging.
---

# 🕵️ Code Review & Offensive Audit (`/code-review`)

Before accepting or approving code changes (`git diff --name-only HEAD`), perform a check on each modified file based on the following criteria. Maintain the Lessword protocol: terse, direct, zero throat-clearing.

## 1. Context Retrieval & Execution Loop
- **CRITICAL ACTION**: Audit MUST be executed **pipeline by pipeline** per phase (vertical slice), NOT layer-by-layer. Trace the full flow (e.g., Route -> Controller -> Service -> Repo) for each feature.
- **CRITICAL ACTION (Blast Radius & Cross-Boundary Trace)**: If diff modifies signatures or calls critical sinks (SQL, subprocess, cache, memory DB, file system), MUST perform a forward trace of at least 1 hop into caller and consumer modules. Do not review diff lines in isolation.
- **CRITICAL ACTION**: You MUST execute `run_command` with `python .agents/scripts/orion.py scan targets <DIR>` NOW if auditing the full project. Do not guess filenames.
- **CRITICAL ACTION (Ledger Auto-Sync)**: If `.orion/working/audit/00-ledger.md` exists, any findings discovered during audit MUST be logged directly into `00-ledger.md` with incremental ID (`[OPEN]`) and state pointer in `AUDIT_STATE.md` updated.
- [ ] **Subagent Delegation (Deep Audits)**: For large files, delegate deep audits to `integrity-sentinel` (`.agents/skills/integrity-sentinel/references/audit_vectors.md`) to prevent context degradation.

## 2. Standard Code Review (Quick Check)
- **CRITICAL ACTION**: Check [../../rules/security-guardrails.md](../../rules/security-guardrails.md) for **CRITICAL Security** violations (Block commit immediately):
  - Hardcoded credentials, API keys, JWT secrets, or tokens.
  - SQL injection vulnerabilities (string formatting in queries or tainted variables passed to single-arg `execute()`).
  - XSS vulnerabilities (rendering HTML without sanitization).
  - Command injection (dynamic variables in subprocess/exec calls without shell escaping).
  - Missing or weak input validation on client/server-side.
  - Path traversal risks (reading files based on direct user input).
- [ ] **Step 3:** Check for **HIGH Code Quality** violations (Block commit if found):
  - **Logic/Math**: Precision loss, division by zero, contradictory branches, unsafe mutations.
  - **Performance/Financial**: Nested loops `O(N^2)`, heavy synchronous logic in `build()`, memory leaks. Evaluate Big-O as actual $ USD Cloud/Token burn rate.
  - **Tech Debt**: Hardcoded magic numbers, tight coupling across boundaries.
  - *Silent fail*: Missing error handling (empty catch blocks), orphaned async promises.
  - *Note: DO NOT focus on superficial syntax (line counts). Focus on algorithmic integrity.*
- [ ] **Step 4:** Provide **MEDIUM Best Practices** suggestions:
  - Variable mutation present (prioritize immutable patterns / data copying).
  - No unit tests for newly added logic/functions.
  - Missing JSDoc/docstrings for public functions or external APIs.

## 3. Offensive Deep Audit (Triad Stress-Test)
Actively probe for concrete failure modes. For deep vectors, refer to `.agents/skills/integrity-sentinel/references/audit_vectors.md`:
- [ ] **Boundary & Malformed Payloads**: Empty arrays, 0-byte streams, max integer boundaries, unexpected nulls, and type coercion.
- [ ] **Resource & Async Drains**: Unbounded async buffers, unclosed sockets/handles, missing timeout guards, and rate limit event-loop starvation.
- [ ] **Silent Failure & Masked Fallback**: Swallowed errors in try/catch blocks, fallback stubs returning empty collections without telemetry, or unhandled promise rejections.
- [ ] **Concurrency & Shared Mutation**: Race conditions on mutable state, missing transactional locks, and non-idempotent retry handlers.

## 4. The Plan Checklist (Execution Safety)
Every plan or logic execution must pass:
1. [ ] KISS
2. [ ] YAGNI
3. [ ] DRY
4. [ ] Fail-fast
5. [ ] Retry-safe
6. [ ] Drift-stop: Lock interface contracts. Auto-heal pipeline mismatch by generating Zod/DTO fixes (Zero-Friction Reversal).
7. [ ] Drift-stop: Write cross-layer integration tests.
8. [ ] Drift-stop: Use pipeline-aware checklists to check consumers.

## 5. Review Output Format (Lessword Protocol)
Generate a clear report using the strict Lessword format. NEVER approve code that violates CRITICAL Security points!
- **Format:** `L<line>: <problem>. <fix>.` (or `<file>:L<line>: ...` for multi-file diffs). One line per finding. No throat-clearing.
- **Evidence Mandate**: Every `🔴 bug` finding MUST cite a reproduction command (test runner assertion or script) OR a demonstrated AST vulnerability trace. Where appropriate, provide a 1-line adversarial input or snippet reproducing the fault. Structural architectural gaps (e.g. unhandled transaction aborts) that cannot easily be condensed to 1 line must include the exact collision trace.
- **Severity Prefixes:**
  - `🔴 bug:` — broken behavior, security leak, or proven structural failure
  - `🟡 risk:` — fragile pattern without hard exploit (unbounded buffer, swallowed error, missing timeout)
  - `🔵 nit:` — style, naming, micro-optim. Author can ignore
  - `❓ q:` — genuine question regarding domain requirements
- **Constraints:** Keep exact line numbers, use exact symbol names in backticks, provide a concrete fix (not "consider refactoring"), drop hedging ("I think", "maybe").

## 6. Adversarial Verification Protocol (Environment-Aware)
1. **Write Reproduction Test**: Author a unit or integration test exposing the bug or edge case (e.g., socket drop, malformed input).
2. **Execute Exploit / Red State**:
   - *In Orion/Foundation Environments*: Run `python .agents/scripts/orion.py adversarial run <test_cmd>`. The gate enforces a failing exit code.
   - *In Standalone / External Projects*: Run the project's native test command (e.g., `pytest`, `npm test`, `flutter test`, `cargo test`). Verify test fails (`Exit Code > 0`).
3. **Apply Code Fix**: Implement the solution in production source.
4. **Verify Green State**:
   - *In Orion/Foundation Environments*: Run `python .agents/scripts/orion.py adversarial verify <test_cmd>` (`Exit Code 0`).
   - *In Standalone / External Projects*: Run the native test command; verify it passes (`Exit Code 0`).

*Task is NOT complete until the verification command confirms clean exit with zero failures.*

## 7. Pre-Completion Verification Gate (The Iron Evidence Law)
**Core principle:** Evidence before claims, always. NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.
If you haven't run the verification command in this message, you cannot claim it passes.

**The Gate Function:**
1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete) via `run_command`.
3. READ: Full output, check exit code (`Exit Code 0`), count failures.
4. VERIFY: Does output confirm the claim?
5. ONLY THEN: Make the claim to the human partner. Skip any step = lying.

**Red Flags (Rationalizations to STOP):**
- "Should work now" -> RUN the verification.
- "Confidence ≠ evidence."
- "Just this once" -> No exceptions.
- "Agent said success" -> Verify independently.

## 8. Prose & Documentation Authenticity Audit
When reviewing pull request descriptions, release notes, and documentation markdown files (`.md`), verify against `.agents/rules/prose-authenticity.md` (active voice, plain English jargon purge, and 54-pattern tell taxonomy). Code blocks, JSON/YAML schemas, database tables, and URLs within documentation are strictly immutable during copy review.
