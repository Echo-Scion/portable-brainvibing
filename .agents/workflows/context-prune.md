---
description: Surgical eviction of stale context, logs, and memory bloat to prevent token exhaustion.
---

# Workflow: Context Prune (`/context-prune`)

This workflow prevents context window exhaustion by mechanically compressing memory and evicting stale data. Do not rely on LLM summarization; run the automated tools.

## 1. MEMORY COMPRESSION (MANDATORY COMMAND)
Execute the compression script to truncate implementation logs while preserving system knowledge:

```bash
python .agents/scripts/compress_memory.py
```
*Wait for output confirmation before proceeding.*

## 2. SCRATCHPAD EVICTION
Scan and delete temporary files. Run these exact commands:

```bash
# Windows/PowerShell: Remove temporary diagnostic files
Remove-Item -Path ".*_scratch.*", ".*_temp.*", ".*_draft.*" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "tmp\*", "__debug__\*" -Recurse -Force -ErrorAction SilentlyContinue
```

## 3. TASK ARCHIVAL
If `workflows/tasks/` contains more than 3 `DONE` files, archive them:
1. Copy the summaries of the `DONE` tasks into `workflows/tasks/ARCHIVE.md`.
2. Delete the original `DONE` task markdown files.

## 4. CONTEXT HANDOFF GENERATION
Run the Session Offload workflow to finalize the context state:
```bash
# Load offload workflow
view_file .agents/workflows/session-offload.md
```