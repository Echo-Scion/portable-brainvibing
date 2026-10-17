---
name: cost-optimizer
description: >-
  Reduces LLM and cloud token costs through token budgets, context size monitoring, and tiered service routing. Use when analyzing token expenditure, evaluating context window bloat, checking large files, or optimizing session efficiency.
---
# Cost Optimizer



Your role is to strictly manage the AI Token Budget. 

## Token Budget Calculator (MANDATORY)
When asked to evaluate context size or if the context feels slow, use this calculation matrix:

| Action | Estimated Tokens | Risk Level |
| :--- | :--- | :--- |
| Read full file (>500 lines) | ~3,000 - 5,000 | HIGH (Refactor needed) |
| Read full file (<150 lines) | ~800 | LOW |
| Code Map Skeleton (`orion.py scan targets`) | ~300 per dir | SAFE |
| `grep_search` with context:2 | ~150 per file | SAFE |

## Mandatory Interventions & Numerical Thresholds
1. **Bulk Read Refusal**: If the user asks to "read all files in directory X", you MUST refuse and execute `python .agents/scripts/orion.py scan targets` first.
2. **File Size Halt**: If `python .agents/scripts/orion.py scan tokens` reveals an application source file exceeding 500 lines, you MUST halt feature additions and mandate a file split before authoring new logic.
3. **Turn Token Budget Gate**: If estimated turn context or accumulated session prompt tokens exceed **8,000 tokens**, you MUST immediately auto-trigger Lessword Ultra mode and recommend the `/compact` slash command to prevent context saturation.
4. **Memory Hygiene Gate**: If active working memory (`MEMORY.md`) exceeds 200 lines, you MUST trigger `/session-offload` to prune evicted context.
5. **FORBIDDEN (Un-budgeted Bulk Dumps)**: Never stream full directory contents or un-filtered test logs into the model context without pre-filtering via `grep_search` or `rtk`.

