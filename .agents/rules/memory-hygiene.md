---
description: Memory Hygiene Policy — smart compression eligibility rules protecting important [[knowledge]] from pruning.
activation: triggered during orion compress and [[skills/session-offload/SKILL.md]]
version: 0.0.2
last_updated: 2026-06-30
---

# Memory Hygiene Policy

## Purpose
Prevent accidental pruning of important [[knowledge]] during memory compression. Ensures that frequently accessed, recently created, or highly connected [[knowledge]] nodes are protected.

## Compression Eligibility Rules

A [[knowledge]] node (page or source) is eligible for compression **ONLY** if ALL conditions are met:

| Rule | Threshold | Rationale |
|---|---|---|
| Low importance | `importance < 4` | High-importance nodes are always protected |
| Rarely accessed | `access_count < 2` in last 30 days | Frequently recalled nodes have proven value |
| Sufficiently old | Created `> 14 days` ago | Recent [[knowledge]] needs time to prove its worth |
| Few graph links | `linked_edges < 3` active edges | Highly connected nodes are structural anchors |
| No contradiction wins | `contradiction_wins == 0` | Knowledge that survived contradiction is battle-tested |

## Access Tracking
- Every time `brain sync` resolves a node into the context packet, increment `access_count` and update `last_accessed`
- Access counts reset monthly (or use rolling 30-day window)

## Compression Actions (when eligible)
1. **Archive**: Move raw content to `.orion/archive/` with timestamp
2. **Summarize**: Replace detailed content with lessword-compressed summary
3. **Preserve metadata**: Keep the node entry in DB with `importance = 0` marker

## Protected Categories (never compress regardless of rules)
- `context/VISION.md` — immutable foundational vision (HUMAN_ONLY)
- `context/AGENT_IDENTITY.md` — agent identity layer
- `.orion/working/handoff.md` — active session handoff
- Any file with `importance >= 4` set manually by user or agent

## Monitoring
Run `python .agents/scripts/orion.py compress --dry-run` to see what WOULD be compressed without actually doing it.

## Omni-Buffer Synchronization Protocol

1. **Buffer Mechanics**: In Antigravity IDE, `hooks.json` automatically updates `.orion/working/context.json` via `pre-agent-wake.py` before agent invocation. Fallback: `python .agents/hooks/pre-agent-wake.py --active-file "<path>"`.
2. **Tier-Aware Reads**: For STANDARD and PREMIUM tasks, if `.orion/working/context.json` exists, read it to extract `active_file`, `recent_errors`, and evolution flags.
3. **Evolution Trigger**: If `context.json` contains `"evolution_overdue": true`, trigger the `/self-evolve` skill (`.agents/skills/self-evolve/SKILL.md`).
4. **JIT Active Drift Alert**: If `context.json` contains `drift_warnings`, you MUST immediately read (via `view_file`) the warning target files before modifying code.

## Pre-Flight Knowledge Consultation (Anti-Amnesia Protocol)

1. **Keyword Search**: For STANDARD and PREMIUM tasks, execute `grep_search` on `.orion/` or key project directories when encountering unfamiliar context.
2. **Repository Search**: Rely on direct `grep_search` and manual file traversals across the codebase rather than external embedding servers.
3. **Standard Injection**: When detecting planning phases, read `.agents/rules/RULES_INDEX.md` and propose relevant standards before writing code.
