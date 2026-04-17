---
description: Surgical eviction of stale context, logs, and memory bloat to prevent token exhaustion.
---

# Workflow: Context Prune (`/context-prune`)

This workflow prevents context window exhaustion on long-running projects by surgically compressing, archiving, and evicting stale information.

> [!IMPORTANT]
> Run this workflow when `MEMORY.md` exceeds 200 lines, or when more than 5 completed tasks exist in `workflows/tasks/`.

## 0. PRE-FLIGHT
- [ ] Verify Binary Oratory compliance via `rules/core-guardrails.md`.
- [ ] **Token Economy Protocol**: Load `rules/performance-optimization.md` to enforce surgical extraction and token caps.


---

## 1. MEMORY COMPRESSION
- [ ] **Read** `context/00_Strategy/MEMORY.md`.
- [ ] **Identify Stale Entries**: Any implementation log entry older than 2 sprints or marked `[DONE]` is a candidate.
- [ ] **Compress**: Replace verbose implementation logs with a single-line summary per entry.
  - *Before*: 15 lines describing step-by-step how auth was implemented.
  - *After*: `[2026-03-15] Auth: Supabase RLS + JWT refresh implemented. See commit abc123.`
- [ ] **Preserve**: Never compress entries tagged `[LEARNING]`, `[RISK]`, or `[DECISION]`. These are permanent memory.

---

## 2. TASK ARCHIVAL
- [ ] **Scan** `workflows/tasks/` for files with `Status: DONE` or `Status: CANCELLED`.
  - // turbo
  ```
  - [task-id] | [date] | [objective summary] | [outcome: DONE/CANCELLED]
  ```

---

## 3. SCRATCHPAD EVICTION
- [ ] **Scan** the workspace for temporary files:
  - Files matching `*_scratch.*`, `*_temp.*`, `*_draft.*`
  - Files in `/tmp/` or any `__debug__/` directories
- [ ] **Delete** all identified scratchpads. No confirmation needed for files matching these patterns.
- [ ] **Exception**: Do NOT delete files that are referenced by an active (non-DONE) task.

---

## 4. SESSION HANDOFF RESET
  1. Current atomic task status (max 3 active items)
  2. Next-step directives
  3. Critical blockers (if any)

---

## 5. VERIFICATION & REPORT
- [ ] **Deleted Scratchpads**: List deleted temporary files.
- [ ] **Infrastructure Sync**: Run `@index-project` to update the semantic index.

---

> [!TIP]
> Schedule this workflow after every 3rd `/verify-loop` run, or whenever the AI reports slow context loading times.