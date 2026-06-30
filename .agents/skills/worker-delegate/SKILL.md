---
name: worker-delegate
description: >
  Worker Delegation Protocol for splitting heavy tasks into sub-agent 
  delegatable units. Workers write results to files, main agent reads 
  for synthesis. Inspired by COG's 6-worker architecture and henrydaum's 
  /tmp/ result relay pattern.
trigger: "delegate", "split task", "worker", "sub-agent", heavy data collection tasks
activation: manual or automatic when task matches delegation criteria
version: 1.0.0
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

### 1. Task Specification
Main agent writes a task spec to working directory:

```markdown
# File: .agents/working/delegations/task-{descriptive-name}.md

## Objective
[Clear, measurable goal]

## Input
[Files to read, paths to scan, queries to run]

## Output Format
[Exact structure expected in result file]

## Constraints
- Max output: 500 lines
- Max files to read: 20
- Timeout: [estimated time]

## Completion Criteria
[How to know the task is done]
```

### 2. Execution
- **IDE Sub-agent**: Use native `browser_subagent` or `run_command` to spawn worker
- **Script Delegation**: Write Python script, execute via `run_command`
- **Caveman compression**: Task specs and results use caveman mode

### 3. Result Collection
Worker writes result to: `.agents/working/delegations/result-{same-name}.md`

Main agent reads result file for synthesis — **NEVER from worker stdout stream** (token waste).

### 4. Cleanup
- Results auto-pruned after 24h (or end of session)
- Task specs archived to `.agents/archive/delegations/` monthly

## Result File Format

```markdown
# Result: {task-name}
## Status: SUCCESS | PARTIAL | FAILED
## Summary
[1-3 sentence caveman summary]

## Data
[Structured output: tables, lists, code blocks]

## Errors (if any)
[What went wrong, what was skipped]
```

## Integration with Existing Tools

| IDE Tool | Delegation Pattern |
|---|---|
| `run_command` | Write script → execute → read result file |
| `browser_subagent` | Describe task → subagent executes → read DOM/screenshot |
| `schedule` | Queue delayed task → result appears later |

## Anti-Patterns
- ❌ Don't delegate reasoning or architecture decisions
- ❌ Don't read worker stdout — read result files
- ❌ Don't delegate to more than 3 workers in parallel (context fragmentation)
- ❌ Don't skip task spec — it's the contract between main and worker
