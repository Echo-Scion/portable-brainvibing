---
name: app-lifecycle
description: >-
  Orchestrates end-to-end full lifecycle state machine routing across project initialization, feature construction, TDD, and sunsetting. Use when scaffolding new projects, migrating existing codebases, building end-to-end features, or retiring deprecated components.
---

# 🔄 Full Lifecycle Pipeline (`/full-lifecycle` / `/app-lifecycle`)

This is the standard engineering pipeline. It operates as a **State Machine**, not a rigid linear script.

## 🧭 Lifecycle Discipline Routing Matrix

| Operational Task | Target Skill / Playbook | Core Mechanism |
| :--- | :--- | :--- |
| **New Project / Scaffolding** | .agents/skills/app-lifecycle/references/project-init.md | Requirements intake, context/ scaffold, DESIGN.md generation |
| **Legacy Migration / Brownfield** | .agents/skills/app-lifecycle/references/project-migrate.md | Onboard existing project, inventory, architecture extraction |
| **Feature Construction (Surgical)** | .agents/skills/app-lifecycle/references/app-builder.md | Shape Spec, UI layout, logic models, Thompson sampling loop |
| **Testing & TDD Verification** | .agents/skills/strict-tdd/SKILL.md | RED-GREEN-REFACTOR cycle with mechanical rollback |
| **Code Review & Offensive Audit** | .agents/skills/code-review/SKILL.md | Security scan, offensive stress-tests & Lessword review format |
| **Feature Sunsetting & Deprecation** | .agents/skills/app-lifecycle/references/feature-sunset.md | 4-Phase deprecation, expand-contract & dead code purge |

---

## ⚡ The Full Lifecycle Pipeline

- **Entry Protocol**: Do not blindly start at Phase 0. Assess the current state of the workspace.
- If the project is empty -> Start at Phase 0 with .agents/skills/app-lifecycle/references/project-init.md.
- If `context/03_Tech/ARCHITECTURE.md` exists but no tests -> Jump to Phase 3.
- If tests pass but UI is missing -> Jump to Phase 4.

### Phase 0: State Initialization (MANDATORY)
- **Action**: Create or overwrite `.orion/task.md` with the checklist of this workflow.
- **Rule**: At the start of every phase below, mark its checkbox as `[/]` (in-progress) in `.orion/task.md`. At the end of every phase, mark it `[x]` (done).
- **Rule (Hardware Constraints)**: Check for resource-heavy default configs. For Flutter/Android: cap Gradle memory in `gradle.properties` (see `canons/ecosystems/flutter/flutter-workflow-commands.md`). For Node: check for memory-hungry webpack configs. Recommend lightweight IDE and physical device testing on constrained hardware.

### Phase 1: Context & Strategy
- **Trigger**: Run `python .agents/scripts/orion.py brain sync "init strategy"`
- **Output Required**: Identify the correct Domain File within `context/` based on `PROJECT_SCAFFOLD.template.md` (e.g., `context/01_Product/ROADMAP.md`). Write strategy into that file.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/project-architect/SKILL.md` IMMEDIATELY in the same turn.

### Phase 1.5: Brain Graph Compilation (If `.orion/` exists)
- **Trigger**: `view_file .agents/skills/brain-graph/SKILL.md`
- **Action**: Ingest newly created/modified `context/` files into `.orion/` by creating cross-reference nodes and ensuring `orion_refs` are injected.

### Phase 2: Architecture Blueprint (Shape Spec)
- **Trigger**: Run `python .agents/scripts/orion.py brain sync "generate architecture blueprint"`
- **Action**: Read relevant `context/` files generated in Phase 1 before planning architecture.
- **Mandatory Interview**: Ask user 1-3 clarifying questions about edge cases, state management, and UI states. Do not guess.
- **Output Required**: Write Architecture Blueprint to `context/03_Tech/ARCHITECTURE.md`.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/strict-tdd/SKILL.md` IMMEDIATELY in the same turn.

### Phase 3: Test-Driven Development (TDD)
- **Trigger**: Run `view_file .agents/skills/strict-tdd/SKILL.md` or `view_file .agents/skills/app-lifecycle/references/app-builder.md`
- **Action**: Implement domain logic following strict RED-GREEN-REFACTOR cycles.
- **Output Required**: Test execution logs showing `[PASS]`.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/ui-finish/SKILL.md` IMMEDIATELY in the same turn after tests pass.

### Phase 4: Aesthetic & UI Polish (Visual Engineering)
- **Trigger**: Run `view_file .agents/skills/ui-finish/SKILL.md`
- **Action**: Load `DESIGN.md` for project aesthetic direction and tokens. Enforce purposeful visual hierarchy, touch target ergonomics, and complete state triad (Loading/Empty/Error). Verify contrast via `python .agents/evals/audit_aesthetics.py --contrast`.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/code-review/SKILL.md` IMMEDIATELY in the same turn.

### Phase 5: Security & Optimization Audit
- **Trigger**: Run `view_file .agents/skills/code-review/SKILL.md` & `view_file .agents/skills/integrity-sentinel/SKILL.md`
- **Action**: Perform adversarial review and static AST security verification.
- **Output Required**: Mandatory Audit Output Template format.
- **Auto-Chain Directive**: Execute `view_file .agents/skills/session-offload/SKILL.md` IMMEDIATELY in the same turn.

### Phase 6: Session Offload
- **Trigger**: Run `view_file .agents/skills/session-offload/SKILL.md`
- **Action**: Clean up worktree, compress memory, and generate session handoff state.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **New Project / Scaffolding** | .agents/skills/app-lifecycle/references/project-init.md |
| **Legacy Migration / Brownfield** | .agents/skills/app-lifecycle/references/project-migrate.md |
| **Feature Construction** | .agents/skills/app-lifecycle/references/app-builder.md |
| **Feature Sunsetting** | .agents/skills/app-lifecycle/references/feature-sunset.md |

