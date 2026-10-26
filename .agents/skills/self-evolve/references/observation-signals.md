# Observation Signals Catalogue & Funnel SOP

This reference defines the signal catalogue, status lifecycle, 2nd-violation barrier escalation rules, and observation evaluation heuristics for `.agents`.

## 1. Signal Taxonomy

| Kind | Trigger / Origin | Destination Action |
| :--- | :--- | :--- |
| **`improve`** | Tool friction, performance drop, or DNA compliance regression | Refine existing rule/skill contract in `.agents/` |
| **`new-skill`** | Missing capability or new workflow requested by user | Stage new skill via `SovereignPromoter` (`admission.py`) |
| **`simplify`** | Code bloat, redundant files, or oversized skill core | Prune dead code, ratchet ceiling down, or fold into umbrella |
| **`violation`** | Tool failure (Exit Code > 0), layer violation, or telemetry catch | Log violation against `rule_id` and evaluate barrier escalation |
| **`habit`** | Action n-gram sequence repeated $\ge 3$ times | Propose workflow automation skill in `.agents/skills/` |

## 2. Observation Lifecycle & Statuses

```
[Signal Captured] -> status: open -> [Review / Pulse] -> status: actioned -> Archived (.archive.md)
                           |
                           +---------> status: parked   -> [Parked Until Date]
                           |
                           +---------> status: declined -> Archived (.archive.md)
                           |
                           +---------> status: superseded -> Archived (.archive.md)
```

- **Restatement Check**: Before creating a new observation, the ledger computes `fingerprint = SHA256(kind:target/rule_id:title)[:12]`. Matching open/parked observations extend evidence rather than creating duplicates.
- **Subagent Refusal**: Subagent sessions (`ANTIGRAVITY_SUBAGENT=1`) cannot mutate `.agents/OBSERVATIONS.md` directly. Findings are returned in subagent telemetry reports.

## 3. Review Loop & Bounded Slice

- **Temporal Pulse (`consolidate milestone`)**:
  - Scans active observations in `.agents/OBSERVATIONS.md`.
  - **Bounded Slice Rule**: When open observations exceed 15, the review slice is capped at the 10 oldest open items.
  - Groups open observations by `rule_id` to detect recurring failure patterns.

## 4. Second Violation Structural Barrier Escalation

> **Tier-0 Forced Barrier Rule**: If a single `rule_id` incurs a **second violation** with no intervening `actioned` / resolved row, its proposal type is **forced to Tier-0** (AST check, assertion, or mutation test).

- **Admission Enforcement (`admission.py`)**:
  - Text-only markdown rule proposals for forced Tier-0 barriers are **rejected** (`HARNESS-T0-01`).
  - The proposal MUST include executable Python AST checks (`security.py`), assertions (`verify_agents.py`), or script subfiles in `scripts/`.

## 5. Core Observation Heuristics & Decision Gates

### A. The Generalisability Test (Anti-Overfitting)
Before recording a candidate improvement, ask:
1. Would this correction still make sense in another project?
2. Would it apply to another task using the same skill?
3. Does it identify a missing rule, workflow step, or invariant, rather than merely fixing this immediate task?
4. Is there evidence the issue is likely to recur?
*If the answers are mostly NO*, treat it as task-specific context, not an observation. A workaround specific to one repo or one temporary constraint is not a reusable invariant.

### B. Unresolved Defect Boundary (2-Hypothesis Cap)
When an unexpected defect (not part of the primary task deliverable) consumes a session with repeated probe failures:
- **Halt after the second hypothesis**: Do not burn 5 consecutive speculative probes on third-party code, permissions, or frozen environment bugs.
- **Output a falsifiable problem report**: Document the exact symptom, what was eliminated, and the cheapest next verification step. Log it as an observation (`kind: violation` or `kind: improve`) and resume primary deliverables.

### C. Deferral Disguised as Diligence
Never defer action with vague diligence phrases ("let's wait until we see more data", "we should test this in production first").
- A valid deferral MUST name two concrete items:
  1. Which specific future observation or event would change the decision.
  2. When that event will realistically arrive.
- If you cannot name both, the evidence is either already conclusive (act now) or waiting adds zero signal (act now).

### D. Instructions Handed Across a Boundary
When generating shell commands or checklists for a user or external execution environment:
- Explanations go in surrounding prose, NEVER as trailing comments on command lines (unsupported shell comment modes silently execute garbage).
- Multi-step dependencies must be chained (`&&` or structured scripts) so an early failure immediately halts execution.
- Verification must check the resulting system property, not merely exit code 0.

### E. Command Risk Classification (Location Over Intent)
Classify a command's risk by its **physical effect and target location**, NEVER by the intent for which it was reached.
- A command chosen for read analysis that executes writes performs those writes regardless of intent.
- Respect read-only, default branch, or production boundaries: convenience shortcuts taken "just this once" are primary vectors for silent state corruption.
