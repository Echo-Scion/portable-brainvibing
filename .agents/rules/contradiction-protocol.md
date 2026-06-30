---
description: Contradiction Resolution Protocol for .orion/ graph integrity.
activation: triggered during orion_ops ingest and brain sync
version: 1.0.0
last_updated: 2026-06-30
---

# Contradiction Resolution Protocol

## Purpose
Detect and resolve conflicting [[knowledge]] triplets in the Orion Graph to maintain data integrity.

## Detection Trigger
During `orion_ops ingest` or `brain sync`, when a new edge `(S, P, O₂)` collides with existing `(S, P, O₁)`:
1. A record is inserted into `contradictions` table with `resolution = 'unresolved'`
2. Both edges retain their data — nothing is deleted automatically
3. Agent is notified via context packet: `"unresolved_contradictions": N`

## Resolution Protocol
When the agent encounters unresolved contradictions:

1. **Read both sources** — identify the original source_path for each conflicting edge
2. **Evidence assessment** — compare recency, source credibility, and context
3. **Resolution actions**:
   - `a_wins`: Edge A confidence × 1.2, Edge B confidence × 0.5
   - `b_wins`: Edge B confidence × 1.2, Edge A confidence × 0.5
   - `merged`: Both edges preserved with clarifying `evidence` text
   - `unresolved`: Escalate to user for human judgment

4. **Update the `contradictions` table** with resolution + evidence + resolved_at timestamp
5. **Update edge confidence scores** accordingly

## Confidence Scoring
- New edges start at `confidence = 1.0`
- Winning a contradiction: `confidence = min(confidence * 1.2, 2.0)`
- Losing a contradiction: `confidence = max(confidence * 0.5, 0.1)`
- Edges with `confidence < 0.3` are candidates for pruning during compression

## Anti-Patterns
- ❌ Never silently overwrite an existing edge with contradictory data
- ❌ Never delete edges without recording the contradiction resolution
- ❌ Never resolve contradictions without reading both source files first
