---
description: Git branching, testing harnesses, and context/memory management.
activation: always on
---

# DEVELOPMENT OPERATIONS

## Git Workflow
# Git Workflow & Conventional Commits

> **MICRO-CANON MANDATE (BUDGET MODELS)**
> If you are operating on a strict token budget, rely on this 30-second cheat sheet.
> - **Format**: `<type>(<scope>): <subject>` (feat, fix, refactor, perf, test, docs, chore, ci)
> - **Branching**: `develop` (integration), `feat/*`, `fix/*`. PR to `develop`.
> - **Pre-Commit Checks**: Run tests & lint (`flutter test`, `dart analyze`, `npm test`).
> - **Destructive Commands**: (`git reset --hard`, `git push --force`) require explicit mechanical IDE feedback block.
> - **Bypass Git**: If the project is not a git repository (e.g., no `.git` folder), skip all git commands to prevent `not a git repository` errors.

## 1. Commit Message Format (Caveman Protocol)
`<type>(<scope>): <description>`

- **Terseness**: Write commit messages terse and exact. No fluff. Why over what.
- **Subject Line**:
  - Imperative mood only: "add", "fix", "remove" (not "added", "adds").
  - Length: ≤50 chars when possible, hard cap 72.
  - No trailing period.
- **Body**: Skip entirely if subject is self-explanatory. Add body only for non-obvious *why*, breaking changes, or linked issues. Use bullets `-` not `*`.

## 2. Branching Strategy & Lifecycle
- `main`: Production-ready code (never commit directly).
- `develop`: Integration branch for features.
- `feat/<ticket-id>-short-description`: New features.
- `fix/<ticket-id>-short-description`: Bug fixes.

**Lifecycle**: Branch from `develop`. Rebase `develop` into your branch frequently. Open PR to `develop`. Squash WIP commits (`git rebase -i HEAD~N`) before merge.

**Hotfix Protocol**: Branch from `main`. After fix, PR to `main` AND cherry-pick to `develop`. Tag the release (`vX.Y.Z`).

## 3. Worktree Isolation (Parallel Development)
- **Concept**: For parallel sub-tasks or large feature refactors, use `git worktree add ../feature-branch feature-branch` to create a physically isolated workspace.
- **Benefit**: This prevents file locking issues and allows the AI to work on different parts of the project simultaneously without cross-contamination.
- **Cleanup**: Always use `git worktree remove` after the task is merged to maintain disk hygiene.

## 4. The "Save Point" Protocol (Micro-Commits)
- **Rule**: Treat Git commits like save points in a game. **Do not wait for a task to be "done" before committing.**
- **Why**: Context windows drop details. Re-reading a file later can cause the AI to accidentally revert previous changes due to state misinterpretation.
- **Action**: Commit immediately after *every* successful, significant sub-step or logic addition. If the task is complex, you should have multiple small commits.

## 5. Security & Verification
- **Drift Radar**: Execute `python .agents/scripts/orion.py verify_agents` before finalizing any commit modifying core logic to ensure AST sync.
- **Secrets Scan**: Ensure no keys are checked in.

## Auto-Harness Protocol
# Rule: AutoHarness Protocol

## 1. The Core Problem
Agents often fail not due to strategic blunders, but because of "illegal moves"—actions that violate strict environment rules, syntaxes, or state transitions (e.g., hallucinating a parameter, breaking JSON structure, violating a framework constraint).

## 2. Code-As-Harness Paradigm
Instead of relying purely on internal LLM simulation or "trying and hoping", the agent MUST proactively synthesize **Harness Scripts** to act as strict verifiers for its own proposed actions. The LLM completes itself by coding its own validation plumbing.

## 3. Harness Typology
When tackling a complex, rigid, or highly-constrained task, synthesize one of the following:

- **Harness-as-Action-Verifier**: A script that intercepts the agent's proposed action (e.g., a planned file modification, SQL query, or configuration change), validates it against constraints, and returns a strict `True`/`False` with a detailed error message before the action is executed on the real environment.
- **Harness-as-Action-Filter**: A script that computes and enumerates all *valid* actions in a given state, forcing the agent to rank or select only from a verified subset.
- **Harness-as-Policy**: For repetitive tasks or deterministic state transitions, synthesize a pure algorithmic script that executes the task without further LLM intervention.

## 4. The Synthesis Loop & Asymmetric Delegation
*Refer to `core-guardrails.md` for the strict Auto-Abort loop between Budget (Harness-Writer) and Premium (Heavy Lifter) models.*
If the Harness rejects the action, categorize the rejection reason before trying again:
- *Syntax Error*: (JSON format, YAML, Typo) ➔ Easily resolved by a small model.
- *Logic/State Error*: (Calling a non-existent function, incorrect state) ➔ Requires reading extra files/context.
- *System/Architecture Error*: (Violating RLS, Security Boundary) ➔ **High Risk Trigger**.

## 5. Storage
Store reusable and generic harnesses in `.agents/canons/global/harnesses/` so other agents can reuse them across sessions.

## 6. Mandatory Activation Triggers
AutoHarness is REQUIRED when any of the following is true:

- Operation can delete, overwrite, or migrate persistent state.
- Action depends on strict syntax/format constraints (YAML, JSON, schema, migrations).
- Previous attempt failed more than once for the same operation class.

If a trigger is present and no harness is used, the action must be blocked.

## 7. Harness Output Contract
Every harness run must emit:

1. `action_id`
2. `is_legal` (`True` or `False`)
3. `violated_rule` (or `none`)
4. `fix_hint`

Silent harness outcomes are non-compliant.



