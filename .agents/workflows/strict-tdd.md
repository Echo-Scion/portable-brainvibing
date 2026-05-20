---
description: Strict test-driven development cycle (RED-GREEN-REFACTOR).
---

# Strict TDD Workflow

Execute the following steps sequentially when instructed to use TDD.

## 0. CONTEXT RETRIEVAL (JIT)
- [ ] Verify Binary Oratory compliance. IF unsure, use `grep_search` on `@core-guardrails.md`.

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