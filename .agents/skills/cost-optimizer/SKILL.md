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
1. **Bulk Read Refusal**: If the user asks to "read all files in directory X", execute `python .agents/scripts/orion.py scan targets` first.
2. **Soft Modularity Advisory (350–500 Lines)**: Files `<= 350 lines` may be read in a single `view_file` call. Files exceeding **350 lines** trigger an advisory warning during `scan map` / `scan tokens` recommending cohesive module extraction once the current feature test passes (`GREEN -> REFACTOR` phase). For files `> 350 lines`, map symbol spans first (`python .agents/scripts/orion.py scan map <file>`) to get `[Lstart-Lend]` boundaries, then read targeted spans.
3. **Soft Session Attention Watermark (~40,000 Tokens)**: When accumulated session context crosses **~40,000 active tokens**, recommend `/session-offload` or sub-agent delegation (`worker-delegate`) to keep the active reasoning window sharp and prevent attention decay.
4. **Memory Hygiene Gate**: If active working memory (`MEMORY.md`) exceeds 200 lines, trigger `/session-offload` to prune evicted context.
5. **FORBIDDEN (Un-budgeted Bulk Dumps)**: Never stream full directory contents or un-filtered test logs into the model context without pre-filtering via `grep_search` or `rtk`.

