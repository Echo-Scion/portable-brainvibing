---
name: session-offload
description: >-
  Mandatory checklist for ending a session smoothly, evicting stale scratchpads, running gated commits, and persisting handoff state. Use when finishing a session, handing off context to a future session, or when the user invokes /session-offload.
---

# Session Offload (`/session-offload`)

This skill defines the strict shutdown sequence for all AI agents finishing a session.

> **MANDATORY CHECKLIST RULE**: Before executing the steps below, you MUST create a `task.md` artifact (or use the existing one) containing a checklist of all steps 1 to 5. You must physically update the checklist `[x]` as you complete each step. You are NOT allowed to skip any step.

## 1. Scratchpad Eviction
Scan and delete temporary files. Run these exact commands:
```bash
# Clean temporary diagnostic artifacts and stale backups cross-platform
python .agents/scripts/orion.py gc
```

## 2. Worktree Cleanup & Commit (Gated Auto-Commit)
If you have uncommitted changes and the project is a git repository, you MUST pass 3 gates before committing them:

1. **Logic Gate**: Run the test suite (e.g. `npm test` or `flutter test`). You MUST NOT commit if `Exit Code > 0`.
2. **Security Gate**: Check for hardcoded API keys/secrets and run `python .agents/scripts/orion.py verify_agents`. Block commit if secrets found.
3. **History Gate**: DO NOT use generic commit messages. Use `git diff` to generate a strict Conventional Commit (`<type>(<scope>): <description>`). 

*(If the project is NOT a git repository, skip the History Gate and do not run git commands).*

```bash
# 1. Logic Gate (Verify Exit Code == 0)
# (Run stack-specific test command here, e.g., 'npm test' or 'flutter test')

# 2. Security Gate
python .agents/scripts/orion.py verify_agents

# 3. History Gate (Review exact diff and stage modified files surgically)
git diff
git add -u
git commit -m "<type>(<scope>): <precise description>"
```

## 3. Atomic Memory Compression & Task Archival
Run the compression tool to prevent token bloat for the next session. The script automatically archives any tasks marked as `DONE`.
```pwsh
python .agents/scripts/orion.py compress
```
Verify that no obsolete task files remain in `.orion/working/tasks/`.

## 3.2. Sovereign Harness Drain & Skill Promotion
Drain the staging intent queue so any self-learned skills, umbrellas, or rule patches proposed during this session are validated against the 6 admission classes and atomically committed:
```pwsh
python .agents/scripts/orion.py harness promote
```

## 3.5. Auto-Context Sync (Conversational Extraction)
If any new business rules, logic constraints, or architectural decisions were explicitly discussed with the user during this session, you MUST execute the `/auto-context` workflow now. This ensures conversational knowledge is persisted into the `context/` 82-file structure before memory is wiped.
> **TERMINATION GATE**: Execute `/auto-context` ONCE. Do not re-enter session-offload.md after `/auto-context` completes. After injection, proceed directly to Step 4 without re-evaluating steps 1-3.5.

## 3.8. Self-Reflection
- **Mandatory Action**: Before ending the session, you MUST analyze any errors, failed executions, false assumptions, and cognitive biases that occurred during the session. Document these learnings in the session log so the system and user can evolve.

## 4. Generate Precise Handoff State (MANDATORY FORMAT)
You MUST explicitly use the `write_to_file` tool to save the exact markdown block below to `.orion/working/handoff.md` BEFORE running the offload and compression scripts. Do not just output it to the chat screen. Do not leave fields empty.

## 4.5. Orion Session Log & Synthesis (Awareness Push)
- **Mandatory Action**: The agent MUST append a 3-line session learning or architectural decision summary to `.orion/episodic/session_history.md`.
- **High-Signal Episodic Observation Tags**: You MUST categorize and tag the session's critical events into the log using these strict prefix tags:
  - `[decision]`: Architectural choices or tradeoffs made.
  - `[bugfix]`: Root causes and solutions for errors encountered.
  - `[feature]`: Completed capabilities or deliverables.
  - `[refactor]`: Structural code improvements or AST hardenings.
  - `[discovery]`: Non-obvious codebase quirks or dependencies found.
  - `[security_alert]`: Any boundary bypasses or sensitive data risks.
  - `[sensitive]`: Secrets or environment configurations modified.
  - `[open_loop]`: Unresolved issues or deferred tasks.
- **Purpose**: Closes the feedback loop to ensure project memory compounds over time via structured needle observations.
- **Session Pulse**: Execute `python .agents/scripts/orion.py consolidate session` to synthesize the session and trigger any pending Milestones.
- Archive `.orion/working/handoff.md` content as an episodic entry in `.orion/log.md`.

```markdown
# SESSION HANDOFF

## 1. Resume Point
[Exactly what the next agent should do first. Provide exact file paths.]

## 2. Technical State
- **Active Files**: [List the 1-3 files actively being edited]
- **Current Blocker**: [Any unresolved errors or pending test results]
- **Pending Migrations**: [Any unapplied SQL changes?]

## 3. Context Offloading Entry
- **Git Commit Changes**: [MANDATORY: Execute `git log -1 --stat` or `git diff --name-status HEAD~1 HEAD` to extract the actual files modified in the last commit. Provide the summary here.]
- **Session Notes**: [Summary of technical decisions or business logic changes made during the session.]

## 4.6. Metrik Cost & Token Savings (MANDATORY)
You MUST execute the RTK built-in feature to report token savings specific to THIS SESSION:
1. Run `rtk gain --history` and filter/count only the execution rows that occurred during this session's timeframe.
2. Write a summary metric **Session Token Savings** in your farewell response (ignore historical data).

## 5. Anti-Goals (Do Not Do)
- [Any brittle architectural areas discovered during this session]
```

## 5. Formal Closure
Give a 1-sentence summary of the task completion and confirm that `.orion/working/handoff.md` is ready.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Business Rule Extraction / Auto-Context** | .agents/skills/session-offload/references/auto-context.md |

