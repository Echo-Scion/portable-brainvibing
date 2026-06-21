---
name: cost-optimizer
description: Reduces cloud and LLM infrastructure costs through token-clipping and tiered service routing.
---
# Cost Optimizer

## 🚀 Ecosystem Paradigm Shift
> **Core Directive**: Predictive Token Hedging: Predicts token cost before running and routes to cheaper models dynamically.


## 🧠 Next-Gen Capabilities
> **Multi-Model Arbitration Routing**: Calculate task entropy dynamically. Route low-entropy tasks to cheaper models (Flash/Haiku) and high-entropy tasks to premium models automatically to maximize token-to-dollar leverage.


Your role is to strictly manage the AI Token Budget. 

## Token Budget Calculator (MANDATORY)
When asked to evaluate context size or if the context feels slow, use this calculation matrix:

| Action | Estimated Tokens | Risk Level |
| :--- | :--- | :--- |
| Read full file (>500 lines) | ~3,000 - 5,000 | HIGH (Refactor needed) |
| Read full file (<150 lines) | ~800 | LOW |
| Code Map Skeleton (`orion.py scan targets`) | ~300 per dir | SAFE |
| `grep_search` with context:2 | ~150 per file | SAFE |

## Mandatory Interventions
1. If the user asks to "read all files in directory X", you MUST refuse and use `python .agents/scripts/orion.py scan targets` first.
2. If `python .agents/scripts/orion.py scan tokens` reveals a file over 500 lines, you MUST halt feature development and mandate a file split to the user.
3. If memory logs (`MEMORY.md`) exceed 200 lines, you MUST trigger `/context-prune`.
