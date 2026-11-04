---
description: Git branching, testing harnesses, and context/memory management.
activation: model_decision
---

# DEVELOPMENT OPERATIONS

## Git Workflow & Conventional Commits

> **MICRO-CANON MANDATE (BUDGET MODELS)**
> If you are operating on a strict token budget, rely on this 30-second cheat sheet.
> - **Format**: `<type>(<scope>): <subject>` (feat, fix, refactor, perf, test, docs, chore, ci)
> - **Dual-Loop Git**: Micro-commits for local step safety (Inner Loop); Trunk release discipline on `main` (Outer Loop).
> - **Pre-Commit Checks**: Run tests & lint (`flutter test`, `dart analyze`, `python .agents/scripts/orion.py verify_agents`).
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

### 1.1. Release Commits (Trunk Discipline Invariant)
When committing or squashing a release milestone on `main` (e.g. `chore(release): ...`), the commit message MUST NOT be an opaque generic stub like `chore(release): sync foundation vX.Y.Z`.
- **Thematic Macro Summary**: The commit message MUST summarize the core breakthroughs and deliverables of that version from `CHANGELOG.md` in 1 cohesive, high-signal sentence (e.g. `chore(release): v0.0.6 - HippoRAG GraphRAG engine, zero-trust command guard, Dual-Loop Git, and BIOS rules rationalization`).
- **Release Exemption to 72-Char Cap**: Release commit messages are explicitly exempt from the 72-character ceiling so that the version's macro deliverables can be stated clearly in a single sentence.

## 1.5. Changelog Integrity & Public Neutrality
`CHANGELOG.md` is a public, user-facing document adhering to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- **Public-Facing Perspective**: Write for external developers and end-users, describing observable features, CLI options, public APIs, performance metrics, and bug fixes.
- **Strictly Exclude Internal Minutiae**: Do not document internal maintainer scripts (e.g. `bump_foundation.py`), local workspace paths, gitignored tooling, or internal LLM prompt engineering discussions.
- **Zero AI Tells & Metaphorical Verbs**: Strictly avoid AI tell verbs (*absorb, supercharge, harness, empower, revolutionize, delve*). Use neutral engineering verbs (*add, fix, update, replace, remove, enforce*).
- **Universal Standards**: Use standard sections (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`). Keep entries factual, concise, and neutral.

## 1.6. Engine vs Host Product Version Sovereignty Law
The **Agentic Framework Engine** (`.agents`, `orion.py`, `gemini-extension.json`, `.dna.json`) and the **Host Product Application** (`package.json`, `pubspec.yaml`, `pyproject.toml`, `Cargo.toml`) reside in two strictly decoupled domains.
- **Zero Framework Leakage**: Agents MUST NOT treat `.agents` framework version, `gemini-extension.json`, or `.project_manifest.json` as the host project's version.
- **Greenfield Invariant**: An uninitiated project (lacking application manifests) is strictly `0.0.0 (Uninitiated / Greenfield)`. Agents MUST NOT synthesize a `VERSION` file or stamp a release header onto greenfield directories.
- **Pre-Release Invariant**: In-development alpha/beta projects (`ROADMAP.md` phase milestones or 0 git release tags) MUST keep session deliverables under `## [Unreleased]`. Never stamp production release tags without explicit human command.

## 2. Dual-Loop Git Strategy: Micro-Commits & Trunk Discipline
Both **Micro-Commits** and **Trunk Discipline** are essential and operate together:

- **Inner Loop (Active Local Development & Save-Points)**:
  - Commit immediately after every successful, significant sub-step, green test, or logic addition.
  - Granular micro-commits prevent context-drop regressions and enable safe rollback of isolated sub-steps.
- **Outer Loop (Trunk Release Discipline & Public History)**:
  - On single-branch trunk repositories (`main`), maintain `1 Release Version = 1 Commit` on `origin/main`.
  - When preparing a release milestone, squash development micro-commits (`git rebase -i` or `/internal` release squash) while preserving local history in `backup-local`.
  - When working on multi-branch teams with integration branches (`develop`), open PRs to `develop` and squash WIP commits before final merge.

**Hotfix Protocol**: Branch from `main`. Verify with tests, then commit/squash to `main` with release tag (`vX.Y.Z`).

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
- **Rule**: Treat Git commits like save points in a game during local development. **Do not wait for an entire complex task to be "done" before saving state.**
- **Why**: LLM context windows drop details. Re-reading a file later can cause the AI to accidentally revert previous changes due to state misinterpretation.
- **Action**: Commit immediately after *every* successful, significant sub-step, green test, or logic addition locally. If the task is complex, you MUST create multiple small local commits. At release or push time, squash these into a clean atomic release commit to preserve Trunk Discipline.

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
Store reusable and generic harnesses in `.agents/canons/global/harnesses/` when created for complex repetitive migrations.

## 6. Verification Triggers
Rigorous verification (via `orion.py verify --fast`, language linters, or deterministic scripts) is REQUIRED when:
- Operation can delete, overwrite, or migrate persistent state.
- Action modifies schemas, configurations, or structured manifests (YAML, JSON, SQLite migrations).
- A previous attempt failed more than once for the same operation class.

## 8. Zero-Error Tooling Execution (Anti-CLI-Crash & AST Precision)

- **Native IDE Tooling First**: The Agent MUST delegate file modifications to native IDE file-editing tools (`edit_file`, `write_file`) as the primary default.
- **No Raw CLI String Replacement**: You are **STRICTLY FORBIDDEN** from modifying files via terminal/CLI commands with manual string replacements (e.g., `python -c`, `sed`, `awk`).
- **Pragmatic Scratch Buffer**: For read-only diagnostics, data extraction, dry-runs, or complex programmatic regex transformations, write scripts to `<appDataDir>/brain/<conversation-id>/scratch/` via native `write_file` before executing. Do not use scratch scripts as a bypass for standard text editing.
- **AST Precision (Anti-Indentation Error)**: For Python or indentation-sensitive files, the Agent MUST inspect the specific target lines via `read_file` or `rtk grep` before patching, ensuring that replacement spacing aligns perfectly with the AST.

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

- **Zero Inline Quoting Traps (`python -c`)**: On Windows PowerShell, NEVER run inline `python -c` snippets that contain complex regex, quotes (`\"`, `\'`), or square brackets (`[` / `]`). Use temporary diagnostic scratch files or native file tools to prevent PowerShell quote stripping and syntax errors.
- **Mandatory `-X utf8` on Windows CLI**: To prevent `UnicodeEncodeError: 'charmap' codec can't encode character...` (Windows legacy `cp1252` default), all one-off Python terminal executions reading/printing UTF-8 or emoji MUST pass `python -X utf8` or set `PYTHONUTF8=1`.
- **Automatic Post-Action Hook**: In Antigravity IDE, `hooks.json` automatically runs `post-agent-action.py` via `PostToolUse` after file changes. Do not invoke it manually via `run_command`.




