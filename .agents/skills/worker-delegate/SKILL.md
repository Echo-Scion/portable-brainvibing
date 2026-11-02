---
name: worker-delegate
description: >-
  Context-isolating read-only scout and partitioned audit delegator. Protects main thread token budget by offloading high-volume file exploration, log triage, and disjoint domain reviews to isolated sub-agents or background CLI engines.
---

# Worker Delegation Protocol (Context-Isolating Scout)

> **Core Law**: The Main Agent owns all architectural state and file mutations (Single-Writer Principle). Subagents operate strictly as **Read-Only Scouts, Patch-Spec Drafters, or Partitioned Auditors** to prevent context pollution and split-brain code modifications.

---

## 1. The 4-Way Execution Routing Gate (Choose Before Delegating)

Before spawning a subagent, the Agent MUST evaluate the task against this deterministic routing matrix:

| Task Characteristic | Context Overlap | Target Mechanism | Operational Rationale |
| :--- | :---: | :--- | :--- |
| **Multi-file feature coding / refactoring** | $\ge 20\%$ | **Main Thread (`/plan` $\to$ `implementation_plan.md`)** | Prevents split-brain state drift, interface drift, and redundant context prefill. |
| **End-to-end autonomous module / greenfield app** | High (Swarm) | **`/teamwork` (`invoke_subagent`)** | Uses platform-native multi-agent shared blackboard & internal review loop. |
| **Heavy CLI build / pack / test / AST scan** | $0\%$ (OS Process) | **Native Async (`run_command` background)** | Zero LLM token burn during execution; reactive wakeup on completion. |
| **Searching 20+ files, log triage, or disjoint read-only audit** | $< 20\%$ | **`/worker-delegate` (`invoke_subagent`)** | Condenses 50,000+ raw tokens into a 20-line surgical brief for the main thread. |

---

## 2. Pre-Delegation Mechanical Gates

The Agent MUST enforce three deterministic gates prior to dispatching any subagent:

### Gate 1: Deterministic Dependency Overlap Gate (`orion.py delegate-check`)
The Agent MUST NOT guess context overlap. Before splitting tasks across subagents, the Agent MUST run:
```bash
python .agents/scripts/orion.py delegate-check <task1_files> <task2_files> [--threshold 0.20]
```
The CLI resolves 1-hop local imports and calculates pairwise Jaccard Dependency Overlap:
$$J(T_1, T_2) = \frac{|D(T_1) \cap D(T_2)|}{|D(T_1) \cup D(T_2)|}$$
- **Exit Code 1 (`MERGE_TO_SINGLE_AGENT`)**: If $J(T_1, T_2) > 0.20$ ($20\%$), the Agent MUST abort delegation and merge all tasks into a single sequential plan (`implementation_plan.md`) on the main thread.
- **Exit Code 0 (`ALLOW_DELEGATION` / `ALLOW_PARALLEL_DISJOINT`)**: If $J(T_1, T_2) \le 0.20$, the Agent MAY proceed with subagent delegation.

### Gate 2: Tier-0 Mechanical Scout First (Zero-Token Pre-Filter)
The Agent MUST NOT dispatch an LLM subagent to read unindexed files sequentially.
1. The Agent MUST run `python .agents/scripts/orion.py scan map <target_dir>` or `rtk grep` to extract exact AST symbol spans `[Lstart-Lend]`.
2. The Agent MUST pass the generated AST skeleton map into the subagent's task specification.
3. The Subagent MUST inspect only the targeted `[Lstart-Lend]` spans using `read_file` rather than reading entire source files.

### Gate 3: Prefix-Cache Aligned Sub-Agent Prompting (Cloud LLM Parallelism)
When dispatching 2–3 subagents concurrently, the Agent MUST structure subagent prompts using an **Immutable Prefix + Variable Suffix** layout:
1. **Immutable Prefix (100% Identical Order Across Subagents)**:
   - Root rules (`AGENTS.md`)
   - Repository Map & PageRank symbol topology
   - Global symbol definitions
2. **Variable Suffix (Partition-Specific)**:
   - Specific task contract
   - Isolated partition file list
This structure maximizes Cloud LLM prefix-cache hits across concurrent subagent executions.

### Gate 4: Sub-Agent Workspace Warm-Up (`orion.py worktree seed`)
When delegating tasks using isolated branch or worktree workspaces (`Workspace: 'branch'` or `Workspace: 'share'`), the new workspace starts cold (lacking gitignored `.env`, `.orion/working/context.json`, and tool configs).
1. The Agent MUST execute worktree seeding before dispatching:
   ```bash
   python .agents/scripts/orion.py worktree seed <target_workspace_path>
   ```
2. The seeder ports all declared `.worktreeinclude` environment files instantly via reflink / hardlink, ensuring subagents never suffer from missing `.env` or missing context crashes.

---

## 3. Read-Only Subagent Archetypes (Single-Writer Principle)

The Subagent MUST NOT write or edit files in the workspace. All file mutations belong exclusively to the Main Agent.

### Archetype 1: `investigator` (Code Locating & Log Triage)
- **Role**: Discovers candidate symbol definitions, references, or error patterns across large file trees.
- **Output Contract**:
  ```
  <Header>:
  - path:line — `symbol` — short note
  totals: <counts>.
  ```

### Archetype 2: `patch-drafter` (Surgical Patch Specification Synthesizer)
- **Role**: Performs read-only inspection of candidate sites and drafts drop-in replacement specifications without touching files.
- **Output Contract**:
  ```
  path:Lstart-Lend — `symbol_signature`
  Root Cause: <1-sentence analysis>
  Replacement Code:
  ```language
  <exact replacement block>
  ```
  Verification: <expected assertion / exit code>
  ```
- **Execution**: The Main Agent reviews the patch specification and applies edits using native file-editing tools.

### Archetype 3: `reviewer` (Isolated Reviewer)
- **Role**: Stateless, read-only auditor evaluating diffs, technical blueprints (`context/00_Strategy/BLUEPRINT.md`), or architectural proposals (`context/03_Tech/ARCHITECTURE.md`) across 5 focused lenses:
  1. `simplicity-reuse`: High-altitude simplicity, YAGNI, anti-weeds, and codebase reuse.
  2. `comprehension`: Synthesizes what this proposes and how the existing system works; failure to synthesize = Blocker.
  3. `system-risks`: Probes scaling bottlenecks, unbacked assertions, and failure modes across the Triad.
  4. `implementation-readiness`: Enforces the Stage 5 Zero-Decision Check (zero design decisions left to implementers).
  5. `layer-boundaries`: Audits 5-tier layer boundaries and unidirectional dependency direction.
- **Quota-Safe Down-Tiering Mandate**: When the Main Agent runs on a `PREMIUM` model (e.g. Gemini Thinking / Claude Opus), it MUST invoke read-only Isolated Reviewers using `Model: 'flash'` (BUDGET [High Effort]). Isolated Reviewers operate on pre-digested AST maps with Scaffolding Discount ($\gamma = 0.65$), preventing high-cost quota exhaustion while reserving the premium model for main-thread synthesis.
- **Output Contract**:
  ```
  path:line: <emoji> <severity>: <problem>. <fix>.
  totals: N🔴 N🟡 N🔵 N❓
  Scout Status: completed | not_run
  ```

---

## 4. Structured Task Specification Schema

The Agent MUST write delegation task specifications to `.agents/working/delegations/task-{task_id}.md`:

```markdown
# File: .agents/working/delegations/task-{task_id}.md

## Task Contract
- task_id: "TASK-001"
- archetype: "investigator" | "patch-drafter" | "reviewer"
- intent: "[Single-sentence measurable objective]"
- target_partition:
  - "path/to/read_only_dir_or_file1"
  - "path/to/read_only_dir_or_file2"
- forbidden_files:
  - ".agents/rules/*"
  - ".orion/*"
- ast_skeleton_input: "Path to compiled AST skeleton map"
- output_artifact: ".agents/working/delegations/result-TASK-001.md"
```

---

## 5. Result Collection & Session Context Cache Ingestion

The Subagent MUST write its final output to `.agents/working/delegations/result-{task_id}.md`.
Every result file MUST include a fenced ```` ```jsonl ```` Context Delta block:

```markdown
# Result: {task_id}
## Status: SUCCESS | PARTIAL | FAILED

## Summary
[1-3 sentence lessword summary]

## Context Delta
```jsonl
{"target_file": "path/to/file.py", "ast_span": "[L120-L165]", "symbol_signature": "def process_data()", "action_recipe": "Add bounds check before indexing list"}
```

## Detailed Findings
[Structured tables, patch specifications, or audit notes]
```

### Automatic Session Context Cache Ingestion
The `pre-agent-wake.py` hook automatically scans `.agents/working/delegations/result-*.md` and extracts all Context Delta records into `context_payload["delegation_deltas"]` inside `.orion/working/context.json`. The Main Agent consumes these surgical recipes with $<5\%$ context footprint without re-reading raw files.

---

## 6. Anti-Patterns & Operational Invariants

- ❌ The Agent MUST NOT delegate tasks when $J(T_1, T_2) > 0.20$ via `delegate-check`.
- ❌ The Agent MUST NOT delegate code modification (`write_file`, `edit_file`) to subagents.
- ❌ The Subagent MUST NOT execute git worktree mutations for routine delegations.
- ❌ The Agent MUST NOT read worker output from raw stdout streams; the Agent MUST read `.agents/working/delegations/result-{task_id}.md`.
- ❌ The Agent MUST NOT spawn more than 3 subagents concurrently. Always dispatch swarms in sequential batches of $\le 3$.
- ❌ The Agent MUST NOT count a failed, timed-out, or unresponsive subagent reviewer as having "zero findings". If retry fails, its status MUST be recorded as `not run`.
- ❌ The Agent MUST NOT invoke Isolated Reviewers on `PREMIUM` models; pass `Model: 'flash'` for all read-only review delegations to preserve cloud quota.

---

## 7. Operational References

- Continuous execution rulings: `references/continuous_execution.md`
