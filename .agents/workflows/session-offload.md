---
description: Mandatory checklist for ending a session smoothly. Evicts stale context, collects precise handoff state, and prevents token exhaustion.
---
# /session-offload.md

This workflow is the strict shutdown sequence for all AI agents finishing a session.

## 1. Scratchpad Eviction
Scan and delete temporary files. Run these exact commands:
```bash
# Windows/PowerShell: Remove temporary diagnostic files
Remove-Item -Path ".*_scratch.*", ".*_temp.*", ".*_draft.*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "tmp\*", "__debug__\*" -Recurse -Force -ErrorAction SilentlyContinue
```

## 2. Worktree Cleanup & Commit (Gated Auto-Commit)
If you have uncommitted changes and the project is a git repository, you MUST pass 3 gates before committing them:

1. **Logic Gate**: Run the test suite (e.g. `npm test` or `flutter test`). You MUST NOT commit if `Exit Code > 0`.
2. **Security Gate**: Check for hardcoded API keys/secrets and run `python .agents/scripts/orion.py verify_agents`. Block commit if secrets found.
3. **History Gate**: DO NOT use generic commit messages. Use `git diff` to generate a strict Conventional Commit (`<type>(<scope>): <description>`). 

*(If the project is NOT a git repository, skip the History Gate and do not run git commands).*

```bash
# 1. Logic Gate (Verify Exit Code == 0)
npm test # or flutter test
# 2. Security Gate
python .agents/scripts/orion.py verify_agents
# 3. History Gate (Check if git repository first)
if (Test-Path .git) {
  git diff
  git add .
  git commit -m "<type>(<scope>): <precise description>"
} else {
  Write-Host "Not a git repository. Skipping commit."
}
```

## 3. Atomic Memory Compression & Task Archival
Run the compression tool to prevent token bloat for the next session. The script automatically archives any tasks marked as `DONE`.
```bash
python .agents/scripts/orion.py compress_memory
python .agents/scripts/orion.py nano_compressor
```
Verify that no obsolete task files remain in `.agents/workflows/tasks/`.

## 3.5. Auto-Context Sync (Conversational Extraction)
If any new business rules, logic constraints, or architectural decisions were explicitly discussed with the user during this session, you MUST execute the `/auto-context` workflow now. This ensures conversational [knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/[knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/knowledge.md)) is persisted into the `context/` 82-file structure before memory is wiped.
> **TERMINATION GATE**: Execute [auto-context.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[auto-context.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/auto-context.md)) ONCE. Do not re-enter session-offload.md after [auto-context.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/[auto-context.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/workflows/auto-context.md)) completes. After injection, proceed directly to Step 4 without re-evaluating steps 1-3.5.

## 3.8. Self-Reflection (Evaluasi Diri)
- **Mandatory Action**: Before ending the session, you MUST analyze any errors, failed executions, false assumptions, and cognitive biases that occurred during the session. Document these learnings in the session log so the system and user can evolve.

## 4. Generate Precise Handoff State (MANDATORY FORMAT)
You MUST explicitly use the `write_to_file` tool to save the exact markdown block below to `.orion/working/handoff.md` SEBELUM (BEFORE) running the offload and compression scripts. Do not just output it to the chat screen. Do not leave fields empty.

## 4.5. Orion Session Log & Synthesis (The Write-Back Loop)
- **Mandatory Action**: The agent MUST append a 3-line session learning or architectural decision summary to `.orion/episodic/session_history.md`.
- **Purpose**: Closes the feedback loop to ensure project memory compounds over time.
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
- **Git Commit Changes**: [MANDATORY: Jalankan `git log -1 --stat` atau `git diff --name-status HEAD~1 HEAD` untuk mengekstrak daftar file riil yang berubah pada commit terakhir sesi ini. Cantumkan ringkasannya di sini.]
- **Session Notes**: [Ringkasan keputusan teknis atau logika bisnis selama sesi.]

## 4.6. Metrik Cost & Token Savings (MANDATORY)
Kamu WAJIB mengeksekusi *built-in feature* dari RTK untuk melaporkan penghematan token khusus untuk SESI INI:
1. Jalankan `run_command` dengan `rtk gain --history` dan filter/hitung hanya baris eksekusi yang terjadi pada rentang waktu sesi ini.
2. Tuliskan ringkasan metrik **Penghematan Token Sesi Ini Saja** dalam respons perpisahanmu (abaikan data historis lama).

## 5. Anti-Goals (Jangan Lakukan)
- [Any brittle architectural areas discovered during this session]
```

## 5. Formal Closure
Give a 1-sentence summary of the task completion and confirm that `.orion/working/handoff.md` is ready.
