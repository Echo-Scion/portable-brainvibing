---
description: Mandatory checklist for ending a session smoothly. Triggers LEARNINGS updates, precise handoff state collection, and memory compression.
---
# /session-offload

This workflow is the **strict, mandatory shutdown sequence** for all AI agents finishing a session. It is designed to prevent "cold starts" and memory bloat.

You MUST execute the following steps precisely:

## 1. Post-Mortem & Insight Reflection
> **Action**: Reflect on the current session. Did you encounter any profound bugs, systemic failures, or design constraints that future agents must know?
> ```markdown
> > **[DATE]** | **[TASK_ID/ISSUE]** | **[TIER]**
> > - **Issue**: Brief description of the complexity.
> > - **Root Cause**: The foundational reason for the failure.
> > - **Solution**: The specific pattern or fix that worked.
> > - **Debt/Warning**: Future considerations or brittle areas discovered.
> ```
> **No?** Proceed to Step 2. Do NOT hallucinate trivial learnings.

## 2. Generate Precise Handoff State
> **Action**: Read `.agents/templates/SESSION_HANDOFF.template.md`. 
> **MANDATE**: You must fill out EVERY field with high fidelity context. Do not use placeholders.
> - **Resume Point**: Exactly what the next agent should do first.
> - **Technical State**: Which files were actively being edited.
> - **Anti-Goals**: What the next agent should NOT do.

## 3. Worktree Cleanup & Merge Check (If Applicable)
> **Action**: If you are operating inside an isolated git worktree branch (not `main`), you MUST handle cleanup before closing the session.
> 1. Check `git status` for uncommitted changes. If any, commit them (`git add . && git commit -m "chore: session offload commit"`).
> 2. Execute merge sequence: `git checkout main`, `git merge <branch>`, `git worktree remove <path>`.
> 3. If conflict occurs during merge, ABORT automation immediately. Present conflict diff to user. Wait for manual resolution or explicit override. NEVER force-overwrite.

## 4. Atomic Memory Compression (Optional but Recommended)
> **Action**: Run the memory compression tool. 
> Execute the following terminal command (do NOT ask for permission unless the user prompt demands it):
```bash
python .agents/scripts/compress_memory.py
```

## 5. Formal Closure
> **Action**: Output a final response to the user confirming:
> 1. Give a 1-sentence summary of the next task the user (or new AI) should initiate later.