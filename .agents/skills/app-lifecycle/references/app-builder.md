---
name: app-builder
description: Surgical feature creation workflow spanning Shape Spec, logic, adversarial testing, and verification loop.
---

# 🏗️ WORKFLOW: APP BUILDER (SURGICAL) (`/app-builder`)

This workflow defines the precision implementation cycle for individual features.
It operates as a **State Machine**. Do not blindly execute steps 1 to 5 sequentially if the feature is partially built. Assess the codebase first and jump directly to the relevant Phase (e.g., if Logic is done, jump to Phase 4: Verification).

> **MANDATE:** If this feature involves heavy database migrations or core architecture refactors, you MUST escalate to `[TIER: PREMIUM]` before proceeding.

## 0. PRE-FLIGHT (JIT CONTEXT)
- [ ] **State Initialization**: Create or update `.orion/task.md` with the phases below. Update checkboxes to `[/]` and `[x]` as you progress.
- [ ] **Verify Environment**: Ensure `.agents/` is synced and active.
- [ ] **Rule Alignment**: Verify alignment with active Master BIOS mandates and `rules/memory-hygiene.md`.
- [ ] **Surgical Entry**: Identify the target folder (00-03) and the relevant Prefix from `templates/PROJECT_SCAFFOLD.template.md`.

## 1. SHAPE SPEC & SPECIFICATION (LIVING DATA)
- [ ] **Reference Check**: Find Reference Implementations (similar existing code) and consult `.agents/rules/RULES_INDEX.md` to deploy relevant standards.
- [ ] **Draft Shape**: Write a Shape Document (e.g., in `.orion/specs/`) outlining the scope, visual/UX goals, references, and deployed standards.
- [ ] **Master Update**: Add the feature summary to `context/00_Strategy/BLUEPRINT.md` and `01_Product/ROADMAP.md`.
- [ ] **Registry Expansion**: Create a new Prefix-based detail file (e.g., `01_Product/Rev_Payment_Gateways.md`) if the domain is new or requires high depth.
- [ ] **Approval**: Present the "Shape Spec" to the user for approval via IDE Artifact RequestFeedback before writing any code.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Design layout and implement logic`

## 2. AESTHETIC DESIGN (RESTRAINED SOLID & TACTILE SURFACES)
- **Vibe Check**: Design the UI layout based on the provided Shape Spec.
- **Component Blueprint (DESIGN.md)**: Define the visual identity in a `DESIGN.md` file.
- **Style Guide Sync**: Sync the `DESIGN.md` properties into `02_Creative/STYLE_GUIDE.md`.
- **MANDATORY BENTO-BOX PAUSE**: You MUST run UI linting/testing before proceeding to Step 3. Do not batch Step 2 and Step 3 together.
- **Auto-Chain Trigger**: Set `NEXT TASK: Execute lint and proceed to logic implementation`

## 3. DOMAIN & LOGIC (TECHNICAL DEPTH)
- [ ] **Data Modeling**: Create immutable `{{MODEL_TYPE}}` models based on the Architecture.
- [ ] **Security Check**: Audit data parsing and storage logic against security guardrails if handling external inputs.
- [ ] **State Management**: Implement `{{STATE_MANAGEMENT}}` and business logic services.
- [ ] **API Contract**: Validate backend interactions using the schema defined in the Architecture.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Execute Adversarial Twin Protocol`

## 3.5 ADVERSARIAL TWIN PROTOCOL (PRE-VERIFICATION)
- [ ] **Self-Attack**: Execute Adversarial Twin Protocol. Write a unit test targeting null data, race conditions, or network drops for the new logic. Run the test.
- [ ] **Defend**: Modify the core logic until the edge-case test passes (Exit Code 0).

## 4. VERIFICATION & AUDIT (CERTIFICATION & HARNESS LOOP)
- [ ] **Completeness Integrity (Coverage Gate)**: Run the platform test command with coverage (`{{CLI_TEST_COVERAGE}}`). Verify all edge cases and error paths are covered. "Shortcuts" (leaving TODOs in error paths) are strictly prohibited.
- [ ] **Iterative Refinement (Thompson Sampling Logic)**: 
    - Treat unit tests as the "Action-Verifier" Harness.
    - **Mutation**: If a test fails (Exit Code > 0), parse the error log, mutate the code to fix the failure, and re-run.
    - **Exploration vs Exploitation**: Try new logic structures if the current approach fails 3 times, or refine the existing code if it's close to passing.
    - Loop this process automatically until the Test Pass Rate reaches exactly 1.0 (100%).
- [ ] **TDD Loop**: Apply Test-Driven Development via `.agents/skills/strict-tdd/SKILL.md`. Write and run tests using the platform test command.
- [ ] **Logical Audit**: Run static analysis (platform lint command). Zero warnings allowed.
- [ ] **Regressive Evaluation**: Run the entire test suite to confirm no existing core logic was broken.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Update Memory and Propose Next Task`

## 5. WRAP-UP
- [ ] **Memory Persistence**: Update `00_Strategy/MEMORY.md` with the implementation log.
- [ ] **Next Step**: Propose the next logical atomic task based on the Roadmap.
