---
name: strict-tdd
description: >-
  Enforces strict Test-Driven Development (TDD) with mandatory RED-GREEN-REFACTOR gates and mechanical rollback. Use when writing new features, fixing bugs, or implementing code requiring verified test coverage before writing implementation.
---

# 🔴🟢 Strict TDD (`/strict-tdd`)

Execute the following steps sequentially when instructed to use TDD.

## 0. CONTEXT RETRIEVAL (JIT)
- [ ] Verify Binary Oratory compliance. IF unsure, use `grep_search` on `@core-guardrails.md`.
- [ ] **Persistent Audit State Hook (Automatic Bridging)**:
  - Check if target project contains `.orion/working/audit/AUDIT_STATE.md` or `00-ledger.md`.
  - IF present: Run in **Fused Mode**. Auto-load `AUDIT_STATE.md` to pick target `[OPEN]` finding, apply TDD cycle, and auto-update `00-ledger.md` to `[FIXED]` upon Exit Code 0. No manual separate workflow call required.
  - IF absent: Run lean standalone mode (no ledger overhead).

## The Strict TDD Cycle
- [ ] **1. Scaffold Interfaces**: Define types/interfaces or class/function skeletons without the actual implementation.
- [ ] **2. Write Failing Test (RED)**: Write a test that is *guaranteed to fail* because the code has not been implemented yet.
   - Enforce **State-Delta Assertion Mandate (Anti-Tautology Gate)**: Assertions MUST verify concrete state mutations (delta: before vs. after, specific property values, or invariant transitions). Banned tautologies: `toBeDefined()`, `assert True`, `assert x is not None`, or checking HTTP status without payload verification.
   - Test the happy path.
   - Test edge cases (null, empty, error boundaries, malformed input).
- [ ] **3. Run Test (Verify RED)**: Verify that the test actually fails (RED) with the *expected* error (feature missing/bug present, not a typo or compile error). If it passes, the test is faulty.
- [ ] **4. Implement Minimal Code (GREEN)**: Write as little code as possible just to make the test pass. Apply **YAGNI** (You Aren't Gonna Need It); do not over-engineer or add features not explicitly tested.
- [ ] **5. Run Test (Verify GREEN)**: Verify that all tests now *pass*.
- [ ] **6. Adversarial Mutation Self-Check**: Verify test sensitivity against false passes. If the core business logic operator is inverted (e.g., `>` to `<`, `==` to `!=`, boolean flipped, or assignment omitted), would the test turn RED? If the test would still pass with broken logic, the assertion is vacuous. Rewrite assertions before proceeding.
- [ ] **7. Refactor (Stay GREEN)**: Improve code quality or optimize production code. Re-run tests to ensure they stay green. Do NOT add new behavior during refactoring.
- [ ] **8. Repeat**: Next behavior.

## Anti-Tautology & Mutation Defense
- **State-Delta Assertion Mandate**: Tests must assert *what changed*. Tautologies (checking that an object exists, status is 200 with unverified payload, or ungrounded assertions) do NOT prove correctness. Always assert specific property deltas or state transitions.
- **Adversarial Mutation Check**: An assertion that cannot fail when code is defective is useless. Ensure every assertion deterministically fails if the underlying business logic operator is inverted or bypassed.

**THE PENALTY (Mechanical Rollback):** If implementation code was written BEFORE a verified failing test existed, execute `git stash` or `git checkout -- <file>` to revert the implementation code. You must capture an `Exit Code > 0` on the test run before proceeding.

**ABSOLUTE RULE (Log Check):** Evidence over claims. If the shell log does not explicitly show the test failing (Exit Code > 0), you do not know what you are testing. Halt and rewrite the test.

