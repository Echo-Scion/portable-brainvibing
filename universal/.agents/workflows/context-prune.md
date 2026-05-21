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
The `compress_memory.py` script automatically archives any tasks marked as `DONE` into the `.agents/archive/` directory. Verify that no obsolete task files remain in `workflows/tasks/`.

## 4. CONTEXT HANDOFF GENERATION
Run the Session Offload workflow to finalize the context state:
```bash
# Load offload workflow
view_file .agents/workflows/session-offload.md
```