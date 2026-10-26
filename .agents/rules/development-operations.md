---
description: Git branching, testing harnesses, and context/memory management.
activation: model_decision
---

# DEVELOPMENT OPERATIONS

## Git Workflow & Conventional Commits

> **MICRO-CANON MANDATE (BUDGET MODELS)**
> If you are operating on a strict token budget, rely on this 30-second cheat sheet.
> - **Format**: `<type>(<scope>): <subject>` (feat, fix, refactor, perf, test, docs, chore, ci)
> - **Branching**: `develop` (integration), `feat/*`, `fix/*`. PR to `develop`.
> - **Pre-Commit Checks**: Run tests & lint (`flutter test`, `dart analyze`, `npm test`).
> - **Destructive Commands**: (`git reset --hard`, `git push --force`) require explicit mechanical IDE feedback block.
> - **Bypass Git**: If the project is not a git repository (e.g., no `.git` folder), skip all git commands to prevent `not a git repository` errors.

## 1. Commit Message Format (Lessword Protocol)
`<type>(<scope>): <imperative summary>`

- **Terseness**: Write commit messages terse and exact. No fluff. Why over what.
- **Subject Line**:
  - Imperative mood only: "add", "fix", "remove" (not "added", "adds").
  - Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`.
  - Length: ≤50 chars when possible, hard cap 72.
  - No trailing period.
- **Body**: Skip entirely if subject is self-explanatory. Add body only for non-obvious *why*, breaking changes, or linked issues. Use bullets `-` not `*`.
- **Forbidden Commit Bloat**:
  - Never write "This commit does X", "I", "we", "now", "currently" — the diff already shows what.
  - Never write "As requested by..." — use git trailer `Co-authored-by:` instead.
  - Never include AI chatbot attributions ("Generated with AI", "Prompted by user").
  - Never restate file names if `<scope>` already specifies them.

## 2. Branching Strategy & Lifecycle
- `main`: Production-ready code (never commit directly).
- `develop`: Integration branch for features.
- `feat/<ticket-id>-short-description`: New features.
- `fix/<ticket-id>-short-description`: Bug fixes.

**Lifecycle**: Branch from `develop`. Rebase `develop` into your branch frequently. Open PR to `develop`. Squash WIP commits (`git rebase -i HEAD~N`) before merge.

**Hotfix Protocol**: Branch from `main`. After fix, PR to `main` AND cherry-pick to `develop`. Tag the release (`vX.Y.Z`).

## 3. Worktree Isolation & Branch Finishing Lifecycle
- **Worktree Sandboxing**: For parallel sub-tasks or complex feature implementations, isolate the workspace:
  ```bash
  git worktree add -b feat/<task-id> .worktrees/<task-id> HEAD
  ```
  Prevents file collisions, working tree dirtying, and lock issues.
- **The Branch Finishing Checklist**:
  Before merging any worker branch or closing a feature branch, execute:
  1. **Working Tree Cleanliness**: `git status --porcelain` must be completely empty (no untracked files or unstaged edits).
  2. **Deterministic Verification Gate**: Run the full project test suite (`pytest`, `npm test`, `flutter test`) and confirm `Exit Code 0`.
  3. **Zero Lint/AST Violations**: Run project linter and `python .agents/scripts/orion.py verify_agents`.
  4. **Fast-Forward / Squash Merge**: Merge cleanly into the integration branch (`develop`) without creating dirty merge artifacts.
  5. **Worktree & Branch Teardown**: Prune the physical worktree directory and delete the local feature branch:
     ```bash
     git worktree remove .worktrees/<task-id> --force
     git branch -d feat/<task-id>
     ```
     Never leave orphaned worktree directories on disk.

## 4. The "Save Point" Protocol (Micro-Commits)
- **Rule**: Treat Git commits like save points in a game. **Do not wait for a task to be "done" before committing.**
- **Why**: Context windows drop details. Re-reading a file later can cause the AI to accidentally revert previous changes due to state misinterpretation.
- **Action**: Commit immediately after *every* successful, significant sub-step or logic addition. If the task is complex, you MUST create multiple small commits.

## 5. Security & Verification
- **Drift Radar**: Execute `python .agents/scripts/orion.py verify_agents` before finalizing any commit modifying core logic to ensure AST sync.
- **Secrets Scan**: Ensure no keys are checked in.

## Auto-Harness Protocol

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
*Refer to AGENTS.md §1 Core Guardrails and .agents/rules/tier-execution-protocol.md for the strict Auto-Abort loop between Budget (Harness-Writer) and Premium (Heavy Lifter) models.*
If the Harness rejects the action, categorize the rejection reason before trying again:
- *Syntax Error*: (JSON format, YAML, Typo) ➔ Easily resolved by a small model.
- *Logic/State Error*: (Calling a non-existent function, incorrect state) ➔ Requires reading extra files/context.
- *System/Architecture Error*: (Violating RLS, Security Boundary) ➔ **High Risk Trigger**.

## 5. Storage
Store reusable and generic harnesses in `.agents/canons/global/harnesses/` so other agents can reuse them across sessions.

## 6. Mandatory Activation Triggers
Action-Harness verification is REQUIRED when any of the following is true:

- Operation can delete, overwrite, or migrate persistent state.
- Action depends on strict syntax/format constraints (YAML, JSON, schema, migrations).
- Previous attempt failed more than once for the same operation class.

If a trigger is present and no harness is used, the action must be blocked.

## 8. Zero-Error Tooling Execution (Anti-CLI-Crash & AST Precision)

- **No Raw CLI Patching**: You are **STRICTLY FORBIDDEN** from modifying files via `run_command` with manual string replacements (e.g., `python -c`, `sed`, `awk`).
- **Native IDE Tooling**: You MUST delegate file modifications to `replace_file_content` or `multi_replace_file_content` natively provided by the IDE.
- **Scratch Buffer**: For complex non-editing scripts, you MUST write the code to `<appDataDir>/brain/<conversation-id>/scratch/` via `write_to_file` before executing it.
- **AST Precision (Anti-Indentation Error)**: For Python or indentation-sensitive files, you MUST use `grep_search` with `MatchPerLine=true` to read the specific target lines before patching, ensuring that replacement spacing aligns perfectly with the AST.

## 9. Anti-Hardcode Path Rule (Portability Preservation)

- **No UI Links in Source**: When writing or modifying files using your IDE editing tools, you MUST NEVER write absolute paths or `file://` schemes into file contents. Absolute `file://` links are STRICTLY for chat UI responses. 
- **Relative & Wikilinks Only**: You MUST use relative paths or standard `[[wikilinks]]` in the source code.

## 10. Starter Verification & Operational Invariants

- **Pre-flight Verification (#3)**: Run `python .agents/scripts/orion.py preflight` before initiating multi-file refactors or cross-repo migrations.
- **Complete Subagent Inputs (#7)**: Worker delegations MUST specify explicit file targets, exact line spans, and output contracts — never vague instructions.
- **Surgical Pruning (#11)**: Clean up orphaned imports, unused variables, and temporary scratchpad files created during your own edits before completing the task.
- **Interrupted Operation Recovery (#16)**: After any interrupted command or mid-workflow session crash, execute `python .agents/scripts/orion.py verify` to confirm workspace state before resuming edits.
- **Surgical Diff Preservation (#20)**: Every modified line must trace directly to user intent. Do not alter adjacent formatting, comments, or unrelated modules.

## 11. Windows Shell & UTF-8 Terminal Guardrails

- **Zero Inline Quoting Traps (`python -c`)**: On Windows PowerShell, NEVER run inline `python -c` snippets that contain complex regex, quotes (`\"`, `\'`), or square brackets (`[` / `]`). Always write temporary diagnostic scripts to a dedicated scratch file (e.g. via `write_file`) and execute it via `python <script>.py`, deleting it after verification.
- **Mandatory `-X utf8` on Windows CLI**: To prevent `UnicodeEncodeError: 'charmap' codec can't encode character...` (Windows legacy `cp1252` default), all one-off Python terminal executions reading/printing UTF-8 or emoji MUST pass `python -X utf8` or set `PYTHONUTF8=1`.




