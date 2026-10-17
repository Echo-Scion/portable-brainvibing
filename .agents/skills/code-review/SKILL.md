---
name: code-review
description: >-
  Conducts code reviews, pull request audits, and offensive security checks using adversarial verification. Use when reviewing diffs, auditing pull requests, checking security boundaries, or evaluating code quality before merging.
---

# 🕵️ Code Review & Offensive Audit (`/code-review`)

Before accepting or approving code changes (`git diff --name-only HEAD`), perform a check on each modified file based on the following criteria. Maintain the Lessword protocol: terse, direct, zero throat-clearing.

## 1. Context Retrieval & Execution Loop
- **CRITICAL ACTION**: Audit MUST be executed **pipeline by pipeline** per phase (vertical slice), NOT layer-by-layer. Trace the full flow (e.g., Route -> Controller -> Service -> Repo) for each feature.
- **CRITICAL ACTION**: You MUST execute `run_command` with `python .agents/scripts/orion.py scan targets <DIR>` NOW if auditing the full project. Do not guess filenames.
- **CRITICAL ACTION (Ledger Auto-Sync)**: If `.orion/working/audit/00-ledger.md` exists, any findings discovered during audit MUST be logged directly into `00-ledger.md` with incremental ID (`[OPEN]`) and state pointer in `AUDIT_STATE.md` updated.
- [ ] **Subagent Delegation (Deep Audits)**: For large files, delegate deep audits to `integrity-sentinel` (`.agents/skills/integrity-sentinel/references/audit_vectors.md`) to prevent context degradation.

## 2. Standard Code Review (Quick Check)
- **CRITICAL ACTION**: Check `.agents/rules/security-guardrails.md` for **CRITICAL Security** violations (Block commit immediately):
  - Hardcoded credentials, API keys, JWT secrets, or tokens.
  - SQL injection vulnerabilities (use of string concatenation in queries).
  - XSS vulnerabilities (rendering HTML without sanitization).
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

## 3. Offensive Deep Audit (Stress-Test)
Actively try to break the code. If performing deep architectural audit, refer to `.agents/skills/integrity-sentinel/references/audit_vectors.md`:
- [ ] **Generative Exploit Synthesis**: Spawn a Red Team subagent to write a synthetic attack script (e.g., `synthetic_exploit.py`) targeting the new boundary.
- [ ] **Algorithmic Mutation Testing**: Mechanically inject deliberate bugs (flip operators, drop awaits) into memory. If tests still pass, reject PR (Survivor Bias).
- [ ] **Temporal Simulation**: Survive T=0s, T=15s, T=30s state-machine collisions?
- [ ] **Precision Truncation**: Division by zero or precision loss?
- [ ] **Rate Limits**: 429 errors block the event loop?
- [ ] **Orphaned Promises**: Unawaited async calls?
- [ ] **Data Poisoning**: NaN/null propagation?
- [ ] **Race Conditions**: Mutable shared state or unsafe DB writes?

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
- **Executable Reproduction Mandate**: Every `🔴 bug` finding MUST cite a 1-line reproduction command (e.g., `python scratch/repro_<id>.py -> Exit Code > 0` or test runner assertion). Unverified claims lacking reproduction proof are downgraded to `🟡 risk` or discarded.
- **Severity Prefixes:**
  - `🔴 bug:` — broken behavior, verified via reproduction command
  - `🟡 risk:` — fragile pattern without hard exploit (race, missing null check, swallowed error)
  - `🔵 nit:` — style, naming, micro-optim. Author can ignore
  - `❓ q:` — genuine question, not a suggestion
- **Constraints:** Keep exact line numbers, use exact symbol names in backticks, provide a concrete fix (not "consider refactoring"), drop hedging ("I think", "maybe").

## 6. Adversarial Twin Protocol (Deterministic Verification)
1. **Write Exploit Script**: Write a unit test or Python script targeting the new logic (e.g., test network drop, null data).
2. **Execute Exploit via Algorithmic Gate**: Run `python .agents/scripts/orion.py adversarial run <test_cmd>`. The gate will crash if the test passes.
3. **Write Fix**: Implement the solution in source code.
4. **Verify Fix**: Run `python .agents/scripts/orion.py adversarial verify <test_cmd>`. The gate will only pass if a prior failing test was recorded.

*Task is NOT done until `adversarial verify` completes with Exit Code 0.*

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
