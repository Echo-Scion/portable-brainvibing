---
name: worker-delegate
description: >-
  Splits heavy tasks into parallel sub-agent delegatable units to save tokens and enable asynchronous execution. Use when collecting data across many files, running bulk codebase searches, or performing multi-worker research.
---

# Worker Delegation Protocol

> Split heavy tasks into sub-agent delegatable units to save tokens and enable parallel execution.

## When to Delegate

### DELEGATE (to sub-agent or script)
- Data collection: `grep_search`, file listing, bulk API calls
- Batch file operations: rename, move, format multiple files
- Static analysis: lint, count, measure across codebase
- Research: web search, repo analysis (non-reasoning tasks)

### KEEP IN MAIN (never delegate)
- Architecture decisions and reasoning
- Code review synthesis and judgment
- User interaction and clarification
- Security-sensitive operations
- Contradiction resolution

## Protocol

### 1. Structured Worker Task Specification Schema

Every delegation requires an explicit, contractually bounded specification:

```markdown
# File: .agents/working/delegations/task-{task_id}.md

## Task Contract
- task_id: "TASK-001"
- intent: "[Single-sentence measurable objective]"
- target_files:
  - "path/to/writable/file1.ext"
  - "path/to/writable/file2.ext"
- forbidden_files:
  - "path/to/protected/file.ext"
  - ".agents/rules/*"
- context_inputs:
  - "path/to/read_only_reference.md"
- verification_command: "pytest tests/test_task.py"  # MUST return Exit Code 0
- output_artifact: ".agents/working/delegations/result-TASK-001.md"
```

#### Field Invariants:
- **`target_files` (Strict Write Whitelist)**: Worker is permitted to modify ONLY these listed paths. Any modification outside this list constitutes a contract violation.
- **`forbidden_files` (Strict Write Blacklist)**: Critical configuration, security guardrails, and master registries that must never be altered by the subagent.
- **`context_inputs` (Zero Context Bloat)**: Inject only strictly necessary reference files and type interfaces. Never dump entire session conversation history or unneeded logs.
- **`verification_command` (Evidence Mandate)**: Deterministic mechanical command proving success. Worker must not declare completion without fresh Exit Code 0 proof.
- **`output_artifact`**: Standardized destination for output synthesis and results.

### 2. Execution
- **Sub-agents**: Use native `invoke_subagent`, `browser_subagent`, or MCP servers to delegate reasoning or browser tasks.
- **Background Tasks**: Execute heavy scripts via `run_command` (async) and monitor with `manage_task`.
- **Lessword compression**: Task specs and results use lessword mode.

### 2.2 Subagent Archetypes & Structured Output Contracts
Subagents return compressed, machine-parseable outputs to preserve main context budget:

**1. `investigator` (Code Locating & Scouting)**
- Output contract:
  ```
  <Header>:
  - path:line — `symbol` — short note
  totals: <counts>.
  ```
  Or `No match.` Always file-path-first, line-number-attached, backticked symbols. Safe to grep with `path:\d+`.

**2. `builder` (Surgical Code Modification, ≤2 files)**
- Output contract:
  ```
  <path:line-range> — <change ≤10 words>.
  verified: <re-read OK | mismatch @ path:line>.
  ```
  Or boundary token: `too-big.` / `needs-confirm.` / `ambiguous.` / `regressed.`.

**3. `reviewer` (Adversarial Diff & Vulnerability Audit)**
- Output contract:
  ```
  path:line: <emoji> <severity>: <problem>. <fix>.
  totals: N🔴 N🟡 N🔵 N❓
  ```
  Or `No issues.` Findings sorted by file and line number ascending.

### 2.3 Chaining Protocols
- **Locate → Fix → Verify** (Standard): `investigator` finds candidate sites → `builder` executes surgical edit on 1-2 sites → `reviewer` verifies diff.
- **Parallel Scout**: Spawn 2-3 `investigators` concurrently across defs vs callers vs test coverage. Main thread aggregates findings.
- **Single-Shot Edit**: Target file and line are already proven; pass directly to `builder` without preliminary investigation.

### 2.5 Worktree Isolation Protocol (Parallel / High-Risk Tasks)
When delegating tasks that perform file modifications or risky experimental edits:
1. **Spawn Worktree**: Create an isolated worktree branch to keep main working tree pristine:
   ```bash
   git worktree add -b worker/{task-name} .worktrees/{task-name} HEAD
   ```
2. **Isolated Execution**: Worker executes file edits and tests exclusively inside `.worktrees/{task-name}`.
3. **Verification Gate**: Worker confirms mechanical pass (`Exit Code 0`) before notifying main agent.
4. **Merge & Teardown**: Main agent fast-forwards verified branch and prunes worktree:
   ```bash
   git merge worker/{task-name} && git worktree remove .worktrees/{task-name} --force
   ```

### 2.6 Parallel Execution & Non-Collision Contracts
When dispatching multiple subagents concurrently:
1. **File Disjointness Invariant**: Parallel workers MUST have mutually exclusive `target_files` whitelists (`target_files(A) ∩ target_files(B) = ∅`).
2. **Worktree Sandboxing**: Each concurrent worker must operate within its own dedicated git worktree (`.worktrees/worker-{id}`).
3. **Read-Only Common Foundations**: Shared utility libraries, schemas, and type definitions are treated as immutable during parallel runs.

### 2.7 Continuous Execution & Decision Rulings Protocol
A coordinating agent must not stall execution or barrage the user with trivial status queries:
1. **Continuous Forward Motion**: Execute planned tasks sequentially to completion without pausing for "Should I continue?" check-ins.
2. **Deterministic Rulings, Not Stalls**: When facing minor plan ambiguities or implementation edge cases, rule autonomously based on specification authority:
   ```
   Ruling: <what you decided> — <why> — <what it costs if wrong>
   ```
   Log every ruling in the task ledger and keep moving forward.
3. **The Four Absolute Hard Stops**:
   Pause for human intervention ONLY when:
   - Operation is irreversible or destructive (data loss, force push).
   - Operation crosses a security or privilege boundary.
   - External side-effect outside the workspace occurs (production release, unprompted network mutation).
   - Plan is fundamentally broken where every forward path is a blind guess.

For full continuous execution details and ruling formats, refer to:
`.agents/skills/worker-delegate/references/continuous_execution.md`

### 3. Result Collection
Worker writes result to: `.agents/working/delegations/result-{task_id}.md`

Main agent reads result file for synthesis — **NEVER from worker stdout stream** (token waste).

### 4. Cleanup
- Results auto-pruned after 24h (or end of session).
- Task specs archived to `.agents/archive/delegations/` monthly.

## Result File Format

```markdown
# Result: {task-name}
## Status: SUCCESS | PARTIAL | FAILED
## Summary
[1-3 sentence lessword summary]

## Data
[Structured output: tables, lists, code blocks]

## Errors (if any)
[What went wrong, what was skipped]
```

## Integration with Existing Tools

| IDE Tool | Delegation Pattern |
|---|---|
| `invoke_subagent` / MCP | Spawn independent sub-agent → read returned artifacts or transcript |
| `run_command` (async) | Launch background script → use `manage_task` to check status → read result file |
| `browser_subagent` | Describe task → subagent executes → read DOM/screenshot |
| `schedule` | Queue delayed polling/task → receive notification when done |

## Anti-Patterns
- ❌ Don't delegate reasoning or architecture decisions
- ❌ Don't read worker stdout — read result files
- ❌ Don't delegate to more than 3 workers in parallel (context fragmentation)
- ❌ Don't skip task spec — it's the contract between main and worker
