---
description: Standard workflow for creating new projects or major features (Automated Lifecycle).
---

# Workflow: Full Lifecycle (`/full-lifecycle`)

This is the standard pipeline for building a complete, production-ready feature from scratch. You MUST follow this order sequentially. Do not skip phases.

## Phase 1: Context & Strategy
- **Trigger**: Run `view_file .agents/skills/saas-strategist/SKILL.md`
- **Output Required**: `CONTEXT.md` (Filled out Context Template) and Viability Scorecard.
- **Gate**: Wait for user approval on the context.

## Phase 2: Architecture Blueprint
- **Trigger**: Run `view_file .agents/skills/project-architect/SKILL.md`
- **Output Required**: Architecture Blueprint containing the 6 mandatory sections.
- **Gate**: Wait for user approval on the blueprint.

## Phase 3: Test-Driven Development (TDD)
- **Trigger**: Run `view_file .agents/workflows/strict-tdd.md`
- **Action**: Implement the logic. Write failing tests first, then pass them.
- **Output Required**: Test execution logs showing `[PASS]`.

## Phase 4: Aesthetic & UI Polish
- **Trigger**: Run `view_file .agents/skills/ui-finish/SKILL.md`
- **Action**: Apply Liquid Glass design, micro-interactions, and 4-state error handling.

## Phase 5: Security & Optimization Audit
- **Trigger**: Run `view_file .agents/skills/integrity-sentinel/SKILL.md`
- **Action**: Perform an adversarial review.
- **Output Required**: Mandatory Audit Output Template format.

## Phase 6: Session Offload
- **Trigger**: Run `view_file .agents/workflows/session-offload.md`
- **Action**: Clean up worktree, compress memory, output `SESSION_HANDOFF`.