---
description: End-to-End creation workflows spanning from project initialization to feature construction.
---

# APP LIFECYCLE & CREATION WORKFLOWS

## Project Initialization
# Workflow: Project Initialization (`/project-init`)

Follow these steps exactly when creating a new project or scaffolding a new major feature directory.

## 1. Requirements Intake
Read the user's prompt. If it is vague, do NOT guess.
- **MANDATORY BLOCK**: You MUST output the prompt: *"Please provide the core functionality, target audience, and primary platform."*
- **STOP EXECUTION**: You are FORBIDDEN from proceeding to Step 2 until the user has explicitly answered this question. Do not anticipate or hallucinate requirements.

## 2. Generate Context (Lean 4-Pillar Scaffolding)
Create the foundational [knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/[knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/knowledge.md)) structure for the AI.
- **Action**: Use `run_command` to physically scaffold the directories: `mkdir -p context/00_Strategy context/01_Product context/02_Creative context/03_Tech`.
- **Action**: Generate ONLY the 4 Master files inside `context/` (`00_Strategy/[BLUEPRINT](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/[BLUEPRINT.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/BLUEPRINT.md)).md`, `01_Product/[ROADMAP](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/01_Product/[ROADMAP.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/01_Product/ROADMAP.md)).md`, `02_Creative/[STYLE_GUIDE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/02_Creative/[STYLE_GUIDE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/02_Creative/STYLE_GUIDE.md)).md`, `03_Tech/[ARCHITECTURE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/[ARCHITECTURE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/ARCHITECTURE.md)).md`) using their respective templates in `.agents/templates/`.
- **Rule (Anti-Bloat)**: DO NOT generate the other 82 detail files here. Detail files are generated Just-In-Time (JIT) later in the lifecycle.

## 3. Scaffold Architecture (Codebase) & Apply Constraints
Generate the source directory structure for the app itself.
- **Command**: `view_file .agents/skills/project-architect/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`
- **Action**: Generate the structural blueprint based on `context/03_Tech/[ARCHITECTURE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/[ARCHITECTURE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/ARCHITECTURE.md)).md` and execute it using `run_command` (e.g. `mkdir -p src/features/auth/presentation`).
- **Hardware Constraint Rule**: Check for resource-heavy defaults in the scaffolded project. Load the relevant ecosystem canon from `canons/ecosystems/` for platform-specific memory/resource optimizations. Recommend lightweight IDE and physical device testing on constrained hardware.

## 4. Install Infrastructure Tooling
Set up the mechanical verifiers.
- **Action**: Run `python .agents/scripts/orion.py verify_agents` to ensure the ecosystem is intact in the new directory.

## 5. First-Pass Semantic Indexing
Ensure the new project is searchable.
- **Command**: Run `python .agents/scripts/orion.py scan map` to generate an architectural skeleton.

## 6. Bootstrap & Safe Auto-Ingest Brain Graph
- **Command**: `python .agents/scripts/orion.py orion_ops init`
- **Action**: Scaffolds `.orion/` + scans all layers into `_manifest.json`
- **Command (Safe Auto-Ingest)**: `python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/`
- **Note**: Auto-ingest is SAFE here because it strictly targets high-signal [knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/[knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/knowledge.md)) directories, preventing SQLite bloat from `build/` or `android/` folders.

## Full Lifecycle Pipeline
# Workflow: Full Lifecycle (`/full-lifecycle`)

This is the standard pipeline. It operates as a **State Machine**, not a rigid script.
- **Entry Protocol**: Do not blindly start at Phase 0. Assess the current state of the workspace.
- If the project is empty -> Start at Phase 0.
- If `context/03_Tech/[ARCHITECTURE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/[ARCHITECTURE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/ARCHITECTURE.md)).md` exists but no tests -> Jump to Phase 3.
- If tests pass but UI is missing -> Jump to Phase 4.

## Phase 0: State Initialization (MANDATORY)
- **Action**: Create or overwrite `.orion/task.md` with the checklist of this workflow.
- **Rule**: At the start of every phase below, you MUST mark its checkbox as `[/]` (in-progress) in `.orion/task.md`. At the end of every phase, mark it `[x]` (done).
- **Rule (Hardware Constraints)**: Check for resource-heavy default configs. For Flutter/Android: cap Gradle memory in `gradle.properties` (see `canons/ecosystems/flutter/flutter-workflow-commands.md`). For Node: check for memory-hungry webpack configs. Always recommend lightweight IDE and physical device testing on constrained hardware.

## Phase 1: Context & Strategy
- **Trigger**: Run `python .agents/scripts/orion.py brain sync "init strategy"`
- **Output Required**: Identify the correct Domain File within the `context/` directory based on `PROJECT_SCAFFOLD.template.md` (e.g., `context/01_Product/Plan_MVP_Scope.md`). Write the strategy into that specific file.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/project-architect/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` IMMEDIATELY in the same turn. Do NOT yield to the user or wait for approval.

## Phase 1.5: Brain Graph Compilation (If `.orion/` exists)
- **Trigger**: `view_file .agents/skills/brain-graph/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`
- **Action**: Ingest the newly created/modified `context/` file into `.orion/` by creating a cross-reference node and ensuring `orion_refs` are injected in the context file.

## Phase 2: Architecture Blueprint (Shape Spec)
- **Trigger**: Run `python .agents/scripts/orion.py brain sync "generate architecture blueprint"`
- **Action**: You MUST read the relevant `context/` files generated in Phase 1 before planning the architecture.
- **Mandatory Interview (Agent-OS Shape)**: Before writing the blueprint, ask the user 1-3 clarifying questions about edge cases, state management, and UI states. Wait for their answers. Do not guess.
- **Output Required**: Write the Architecture Blueprint to `context/03_Tech/[ARCHITECTURE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/[ARCHITECTURE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/ARCHITECTURE.md)).md` (or the relevant sub-file like `Dev_Frontend.md`) ensuring the approved standards are referenced.
- **Auto-Chain Directive**: Execute `view_file .agents/workflows/[audit-and-test](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[audit-and-test.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/audit-and-test.md)).md` IMMEDIATELY in the same turn. Do NOT yield to the user or wait for approval unless you have explicitly asked questions in the step above.

## Phase 3: Test-Driven Development (TDD)
- **Trigger**: Run `view_file .agents/workflows/[audit-and-test](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[audit-and-test.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/audit-and-test.md)).md`
- **Action**: Read `context/03_Tech/[ARCHITECTURE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/[ARCHITECTURE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/03_Tech/ARCHITECTURE.md)).md` and related Dev files, then implement the logic. Write failing tests first, then pass them.
- **Output Required**: Test execution logs showing `[PASS]`.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/ui-finish/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` IMMEDIATELY in the same turn after tests pass.

## Phase 4: Aesthetic & UI Polish
- **Trigger**: Run `view_file .agents/skills/ui-finish/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`
- **Action**: Apply Liquid Glass design, micro-interactions, and 4-state error handling.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/integrity-sentinel/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` IMMEDIATELY in the same turn.

## Phase 5: Security & Optimization Audit
- **Trigger**: Run `view_file .agents/skills/integrity-sentinel/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`
- **Action**: Perform an adversarial review.
- **Output Required**: Mandatory Audit Output Template format.
- **Auto-Chain Directive**: Execute `view_file .agents/workflows/[session-offload](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[session-offload.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/session-offload.md)).md` IMMEDIATELY in the same turn.

## Phase 6: Session Offload
- **Trigger**: Run `view_file .agents/workflows/[session-offload](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[session-offload.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/session-offload.md)).md`
- **Action**: Clean up worktree, compress memory, output `SESSION_HANDOFF`.

## App Builder Feature Creation
# 🏗️ WORKFLOW: APP BUILDER (SURGICAL)

This workflow defines the precision implementation cycle for individual features.
It operates as a **State Machine**. Do not blindly execute steps 1 to 5 sequentially if the feature is partially built. Assess the codebase first and jump directly to the relevant Phase (e.g., if Logic is done, jump to Phase 4: Verification).

> **MANDATE:** If this feature involves heavy database migrations or core architecture refactors, you MUST escalate to `[TIER: PREMIUM]` before proceeding.

## 0. PRE-FLIGHT (JIT CONTEXT)
- [ ] **State Initialization**: Create or update `.orion/task.md` with the phases below. Update checkboxes to `[/]` and `[x]` as you progress.
- [ ] **Verify Environment**: Ensure `.agents/` is synced and active.
- [ ] **Rule Alignment**: Read `rules/[core-guardrails](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[core-guardrails.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/core-guardrails.md)).md` and `rules/[context-standards](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[context-standards.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/context-standards.md)).md`.
- [ ] **Surgical Entry**: Identify the target folder (00-03) and the relevant Prefix from `templates/PROJECT_SCAFFOLD.template.md`.

## 1. SHAPE SPEC & SPECIFICATION (LIVING DATA)
- [ ] **Reference Check**: Find Reference Implementations (similar existing code) and consult `.agents/rules/[RULES_INDEX](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[RULES_INDEX.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/RULES_INDEX.md)).md` to deploy relevant standards.
- [ ] **Draft Shape**: Write a Shape Document (e.g., in `.orion/specs/`) outlining the scope, visual/UX goals, references, and deployed standards.
- [ ] **Master Update**: Add the feature summary to `.orion/[BLUEPRINT](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/[BLUEPRINT.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/BLUEPRINT.md)).md` and `01_Product/[ROADMAP](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/01_Product/[ROADMAP.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/01_Product/ROADMAP.md)).md`.
- [ ] **Registry Expansion**: Create a new Prefix-based detail file (e.g., `01_Product/Rev_Payment_Gateways.md`) if the domain is new or requires high depth.
- [ ] **Approval**: Present the "Shape Spec" to the user for approval `[DO: YES]` before writing any code.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: view_file .agents/skills/ui-finish/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`

## 2. AESTHETIC DESIGN (LIQUID GLASS)
- [ ] **Vibe Check**: You MUST execute `view_file .agents/skills/ui-finish/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW to design the UI layout and micro-interactions.
- [ ] **Component Blueprint**: Define the `{{UI_COMPONENT}}` tree and design tokens in `02_Creative/[STYLE_GUIDE](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/02_Creative/[STYLE_GUIDE.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/02_Creative/STYLE_GUIDE.md)).md`.
- [ ] **MANDATORY BENTO-BOX PAUSE**: You MUST run UI linting/testing before proceeding to Step 3. Do not batch Step 2 and Step 3 together.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Execute lint and proceed to data-logic`

## 3. DOMAIN & LOGIC (TECHNICAL DEPTH)
- [ ] **Data Modeling**: You MUST execute `view_file .agents/skills/data-logic/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW to create immutable `{{MODEL_TYPE}}` models.
- [ ] **Security Check**: You MUST execute `view_file .agents/skills/integrity-sentinel/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW to audit data parsing and storage logic.
- [ ] **State Management**: Implement `{{STATE_MANAGEMENT}}` and business logic services.
- [ ] **API Contract**: You MUST execute `view_file .agents/skills/api-contract/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW if backend interaction is required.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Execute Adversarial Twin Protocol`

## 3.5 ADVERSARIAL TWIN PROTOCOL (PRE-VERIFICATION)
- [ ] **Self-Attack**: Execute `@[core-guardrails](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[core-guardrails.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/core-guardrails.md)).md`. Write a unit test targeting null data, race conditions, or network drops for the new logic. Run the test.
- [ ] **Defend**: Modify the core logic until the edge-case test passes (Exit Code 0).

## 4. VERIFICATION & AUDIT (CERTIFICATION & HARNESS LOOP)
- [ ] **Completeness Integrity (Coverage Gate)**: Run the platform test command with coverage (`{{CLI_TEST_COVERAGE}}`). Verify all edge cases and error paths are covered. "Shortcuts" (leaving TODOs in error paths) are strictly prohibited.
- [ ] **Iterative Refinement (Thompson Sampling Logic)**: 
    - Treat unit tests as the "Action-Verifier" Harness.
    - **Mutation**: If a test fails (Exit Code > 0), parse the error log, mutate the code to fix the failure, and re-run.
    - **Exploration vs Exploitation**: Try new logic structures if the current approach fails 3 times, or refine the existing code if it's close to passing.
    - Loop this process automatically until the Test Pass Rate reaches exactly 1.0 (100%).
- [ ] **TDD Loop**: You MUST execute `view_file .agents/skills/integrity-sentinel/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW. Write and run tests using the platform test command. Do not proceed until the Refinement Loop reaches 1.0.
- [ ] **Logical Audit**: You MUST execute `view_file .agents/skills/integrity-sentinel/[SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md` NOW to run static analysis (platform lint command). Zero warnings allowed.
- [ ] **Regressive Evaluation**: Run the entire test suite to confirm no existing core logic was broken.
- [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Update Memory and Propose Next Task`

## 5. WRAP-UP
- [ ] **Memory Persistence**: Update `00_Strategy/MEMORY.md` with the implementation log.
- [ ] **Next Step**: Propose the next logical atomic task based on the Roadmap.

---
*Portable Brainvibing Infrastructure - Surgical App Builder Protocol*

