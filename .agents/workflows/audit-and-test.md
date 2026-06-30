---
description: Quality enforcement workflows including Strict TDD and PR Code Review checklists.
---

# AUDIT AND TESTING WORKFLOWS

## Strict TDD Cycle
# Strict TDD Workflow

Execute the following steps sequentially when instructed to use TDD.

## 0. CONTEXT RETRIEVAL (JIT)
- [ ] Verify Binary Oratory compliance. IF unsure, use `grep_search` on `@core-guardrails).md`.

- [ ] **1. Scaffold Interfaces**: Define types/interfaces or class/function skeletons without the actual implementation.
- [ ] **2. Write Failing Test (RED)**: Write a test that is *guaranteed to fail* because the code has not been implemented yet.
   - Test the happy path.
   - Test edge cases (null, empty, error boundaries).
- [ ] **3. Run Test (Verify RED)**: Verify that the test actually fails (RED) with the *expected* error (feature missing/bug present, not a typo or compile error). If it passes, the test is faulty.
- [ ] **4. Implement Minimal Code (GREEN)**: Write as little code as possible just to make the test pass. Apply **YAGNI** (You Aren't Gonna Need It); do not over-engineer or add features not explicitly tested.
- [ ] **5. Run Test (Verify GREEN)**: Verify that all tests now *pass*.
- [ ] **6. Refactor (Stay GREEN)**: Improve code quality or optimize production code. Re-run tests to ensure they stay green. Do NOT add new behavior during refactoring.
- [ ] **7. Repeat**: Next behavior.

**THE PENALTY (Mechanical Rollback):** If implementation code was written BEFORE a verified failing test existed, execute `git stash` or `git checkout -- <file>` to revert the implementation code. You must capture an `Exit Code > 0` on the test run before proceeding.

**ABSOLUTE RULE (Log Check):** Evidence over claims. If the shell log does not explicitly show the test failing (Exit Code > 0), you do not know what you are testing. Halt and rewrite the test.

## Code Review & Security Audit
# Code Review & Offensive Audit Workflow

Before accepting or approving code changes (`git diff --name-only HEAD`), perform a check on each modified file based on the following criteria. **Remember: Maintain the "Caveman" protocol. Be terse and direct, do not use pleasantries or empathy.**

## 1. Context Retrieval & Execution Loop
- **CRITICAL ACTION**: Audit MUST be executed **pipeline by pipeline** per phase (vertical slice), NOT layer-by-layer. Trace the full flow (e.g., Route -> Controller -> Service -> Repo) for each feature.
- **CRITICAL ACTION**: You MUST execute `view_file .agents/rules/core-guardrails).md` NOW if unsure about Binary Oratory.
- **CRITICAL ACTION**: You MUST execute `view_file .agents/skills/meta-agent-admin/SKILL).md` NOW to properly map code relations.
- **CRITICAL ACTION**: You MUST execute `view_file .agents/rules/development-operations).md` NOW to enforce Git Standards.
- **CRITICAL ACTION**: You MUST execute `run_command` with `python .agents/scripts/orion.py scan targets <DIR>` NOW if auditing the full project. Do not guess filenames.
- [ ] **Subagent Delegation (Deep Audits)**: For large files, execute `view_file .agents/skills/integrity-sentinel/SKILL).md` and delegate deep audits to the integrity-sentinel skill to prevent context degradation.

## 2. Standard Code Review (Quick Check)
- **CRITICAL ACTION**: You MUST execute `view_file .agents/rules/core-guardrails).md` NOW.
- **CRITICAL ACTION**: You MUST execute `view_file .agents/rules/security-guardrails)-guardrails.md)-guardrails.md).md` NOW. Check for **CRITICAL Security** violations (Block commit immediately):
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
Actively try to break the code. You MUST execute `view_file .agents/skills/integrity-sentinel/SKILL).md` NOW to load and run these checks:
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

## 5. Review Output Format (Caveman Protocol)
Generate a clear report using the strict Caveman format. NEVER approve code that violates CRITICAL Security points!
- **Format:** `L<line>: <problem>. <fix>.` (or `<file>:L<line>: ...` for multi-file diffs). One line per finding. No throat-clearing.
- **Severity Prefixes:**
  - `🔴 bug:` — broken behavior, will cause incident
  - `🟡 risk:` — works but fragile (race, missing null check, swallowed error)
  - `🔵 nit:` — style, naming, micro-optim. Author can ignore
  - `❓ q:` — genuine question, not a suggestion
- **Constraints:** Keep exact line numbers, use exact symbol names in backticks, provide a concrete fix (not "consider refactoring"), drop hedging ("I think", "maybe").

