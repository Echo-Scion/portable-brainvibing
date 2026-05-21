---
description: Steps for end-to-end feature creation (Model -> Provider -> UI -> Test).
---

# 🏗️ WORKFLOW: APP BUILDER (SURGICAL)

This workflow defines the precision implementation cycle for individual features, fully integrated with the 4-Pillar hierarchy and SaaS Registry.

## 0. PRE-FLIGHT (JIT CONTEXT)
- [ ] **State Initialization**: Create or update `.wiki/task.md` with the phases below. Update checkboxes to `[/]` and `[x]` as you progress.
- [ ] **Verify Environment**: Ensure `.agents/` is synced and active.
- [ ] **Rule Alignment**: Read `rules/core-guardrails.md` and `rules/context-standards.md`.


## 1. SPECIFICATION (LIVING DATA)
- [ ] **Master Update**: Add the feature summary to `.wiki/BLUEPRINT.md` and `01_Product/ROADMAP.md`.
- [ ] **Registry Expansion**: Create a new Prefix-based detail file (e.g., `01_Product/Rev_Payment_Gateways.md`) if the domain is new or requires high depth.
- [ ] **Approval**: Present the "Surgical Spec" to the user for approval before writing code.


## 2. AESTHETIC DESIGN (LIQUID GLASS)

- [ ] **Component Blueprint**: Define the `{{UI_COMPONENT}}` tree and design tokens in `02_Creative/STYLE_GUIDE.md`.
- [ ] **MANDATORY BENTO-BOX PAUSE**: You MUST run UI linting/testing before proceeding to Step 3. Do not batch Step 2 and Step 3 together.


## 3. DOMAIN & LOGIC (TECHNICAL DEPTH)

- [ ] **Security Check**: Invoke `@skills/integrity-sentinel` to audit data parsing and storage logic.
- [ ] **State Management**: Implement `{{STATE_MANAGEMENT}}` and business logic services.

- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Execute Adversarial Twin Protocol`

## 3.5 ADVERSARIAL TWIN PROTOCOL (PRE-VERIFICATION)
- [ ] **Self-Attack**: Execute `@reasoning-standards.md`. Write a unit test `test_edge_case` specifically targeting null data, race conditions, or network drops for the new logic. Run the test.
- [ ] **Defend**: Modify the core logic until the `test_edge_case` test passes (Exit Code 0).

## 4. VERIFICATION & AUDIT (CERTIFICATION & HARNESS LOOP)
- [ ] **Completeness Integrity (Coverage Gate)**: Run `test --coverage` (or equivalent). Verify all edge cases and error paths are covered by tests. "Shortcuts" (leaving TODOs in error paths) are strictly prohibited.
- [ ] **Iterative Refinement (Thompson Sampling Logic)**:
    - Treat unit tests as the "Action-Verifier" Harness.
    - **Mutation**: If a test fails (Exit Code > 0), parse the error log, mutate the code to fix the failure, and re-run.
    - **Exploration vs Exploitation**: Try new logic structures if the current approach fails 3 times, or refine the existing code if it's close to passing.
    - Loop this process automatically until the Test Pass Rate reaches exactly 1.0 (100%).
- [ ] **TDD Loop**: Invoke `@skills/integrity-sentinel`. Write and run tests (`test`). Do not proceed until the Refinement Loop reaches 1.0.
- [ ] **Logical Audit**: Invoke `@skills/integrity-sentinel` to run static analysis (`analyze` or equivalent). Zero warnings allowed.
- [ ] **Regressive Evaluation**: Run the entire test suite (`test`) to confirm no existing core logic was broken.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Update Memory and Propose Next Task`

## 5. WRAP-UP
- [ ] **Memory Persistence**: Update `00_Strategy/MEMORY.md` with the implementation log.
- [ ] **Next Step**: Propose the next logical atomic task based on the Roadmap.

---
*Portable Brainvibing Infrastructure - Surgical App Builder Protocol*
