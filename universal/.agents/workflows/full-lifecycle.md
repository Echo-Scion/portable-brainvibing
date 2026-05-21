---
description: Standard workflow for creating new projects or major features (Automated Lifecycle).
---

# Workflow: Full Lifecycle (`/full-lifecycle`)

This is the standard pipeline for building a complete, production-ready feature from scratch. You MUST follow this order sequentially. Do not skip phases.

## Phase 0: State Initialization (MANDATORY)
- **Action**: Create or overwrite `.wiki/task.md` with the checklist of this workflow.
- **Rule**: At the start of every phase below, you MUST mark its checkbox as `[/]` (in-progress) in `.wiki/task.md`. At the end of every phase, mark it `[x]` (done).

## Phase 1: Context & Strategy
- **Trigger**: Run `view_file .agents/skills/saas-strategist/SKILL.md`
- **Output Required**: Write the context to `.wiki/CONTEXT.md`
- **Auto-Chain Trigger**: In your response footer, set `NEXT TASK: view_file .agents/skills/project-architect/SKILL.md`
- **Gate**: Wait for user approval (`[DO: YES]`).

## Phase 1.5: Wiki Compilation (If `.wiki/` exists)
- **Trigger**: `view_file .agents/skills/llm-wiki/SKILL.md`
- **Action**: Ingest newly created CONTEXT.md and any generated pillar files using Smart Vibe Coding rules (auto-commit non-destructive changes).

## Phase 2: Architecture Blueprint
- **Trigger**: Run `view_file .agents/skills/project-architect/SKILL.md`
- **Action**: You MUST read `.wiki/CONTEXT.md` first before generating the blueprint.
- **Output Required**: Write Architecture Blueprint to `.wiki/BLUEPRINT.md`.
- **Auto-Chain Trigger**: In your response footer, set `NEXT TASK: view_file .agents/workflows/strict-tdd.md`
- **Gate**: Wait for user approval on the blueprint.

## Phase 3: Test-Driven Development (TDD)
- **Trigger**: Run `view_file .agents/workflows/strict-tdd.md`
- **Action**: Read `.wiki/BLUEPRINT.md`, then implement the logic. Write failing tests first, then pass them.
- **Output Required**: Test execution logs showing `[PASS]`.
- **Auto-Chain Trigger**: In your response footer, set `NEXT TASK: view_file .agents/skills/ui-finish/SKILL.md`

## Phase 4: Aesthetic & UI Polish
- **Trigger**: Run `view_file .agents/skills/ui-finish/SKILL.md`
- **Action**: Apply Liquid Glass design, micro-interactions, and 4-state error handling.
- **Auto-Chain Trigger**: In your response footer, set `NEXT TASK: view_file .agents/skills/integrity-sentinel/SKILL.md`

## Phase 5: Security & Optimization Audit
- **Trigger**: Run `view_file .agents/skills/integrity-sentinel/SKILL.md`
- **Action**: Perform an adversarial review.
- **Output Required**: Mandatory Audit Output Template format.
- **Auto-Chain Trigger**: In your response footer, set `NEXT TASK: view_file .agents/workflows/session-offload.md`

## Phase 6: Session Offload
- **Trigger**: Run `view_file .agents/workflows/session-offload.md`
- **Action**: Clean up worktree, compress memory, output `SESSION_HANDOFF`.