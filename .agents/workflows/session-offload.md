---
description: Mandatory checklist for ending a session smoothly. Collects precise handoff state.
---
# /session-offload

This workflow is the strict shutdown sequence for all AI agents finishing a session.

## 1. Worktree Cleanup & Commit
If you have uncommitted changes, you MUST commit them before generating the handoff.
```bash
git add .
git commit -m "chore: session offload state save"
```

## 2. Atomic Memory Compression
Run the compression tool to prevent token bloat for the next session:
```bash
python .agents/scripts/compress_memory.py
```

## 3. Generate Precise Handoff State (MANDATORY FORMAT)
Output this exact markdown block for the user to copy/paste, or save it to `HANDOFF.md`. Do not leave fields empty.

```markdown
# SESSION HANDOFF

## 1. Resume Point
[Exactly what the next agent should do first. Provide exact file paths.]

## 2. Technical State
- **Active Files**: [List the 1-3 files actively being edited]
- **Current Blocker**: [Any unresolved errors or pending test results]
- **Pending Migrations**: [Any unapplied SQL changes?]

## 3. Anti-Goals
- [What the next agent should NOT do or attempt to change]

## 4. Post-Mortem Insights
- [Any brittle architectural areas discovered during this session]
```

## 4. Formal Closure
Give a 1-sentence summary of the task completion and confirm that `HANDOFF.md` is ready.