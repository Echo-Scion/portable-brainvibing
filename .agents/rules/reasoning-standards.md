---
description: Unified standards for analytical rigor, reasoning depth per tier, and internal validation (Adversarial Twin).
activation: model_decision

version: 2.4.0
last_updated: 2026-05-20
---

# Analytical Standards

## 1. Evidence-Based Decisions
- All architectural recommendations MUST cite specific file paths or code patterns as evidence.
- Do not recommend patterns that contradict what already exists in the codebase.

## 2. Causal Enforcement (The "No-Fix" Policy)
- **Iron Law**: No code modifications are permitted until the root cause of an issue is isolated and a hypothesis is verified.
- **Protocol**: If a bug is reported, the agent MUST first demonstrate the failure (via test or reproduction script) and trace the data flow before proposing a fix.
- **Circuit Breaker**: See `.agents/rules/core-guardrails.md` Section 4 for failure thresholds.

## 3. Value-Density Analysis (Scope Guard)
- **MVC Principle**: Prioritize Minimum Viable Complexity. Always seek the simplest implementation that fulfills the core requirement.
- **Scope Critique**: Before finalizing a plan, the agent MUST critique the proposed scope for "feature bloat." 
- **Filtering Modes**:
    - *Reduction*: Identify and remove 10-20% of non-essential complexity.
    - *Selective Expansion*: Only expand scope if it adds 10x value to the user experience.
    - *Hold*: Strictly adhere to the original blueprint without "just-in-case" additions.

## 4. Structural Critique (The 5 Questions)
When auditing or designing a system, apply these lenses:
1. **Why does this exist?** (Root cause, not surface observation)
2. **Is this the correct abstraction?** (Is this layer necessary?)
3. **What breaks if this is removed?** (Coupling analysis)
4. **What adversary could exploit this?** (Threat modeling)
5. **Does intent match behavior?** (Verify the system does what the docs claim)

## 5. Anti-Hallucination Guard
- Never invent file contents. If a file has not been read via `view_file`, assume its contents are unknown.
- Never assume library APIs. If unsure, use Context7 or pub.dev search first.

---
# Reasoning Protocols

## 1. Tier-Matched Depth
- **BUDGET**: Atomic tasks. **No Sequential Thinking.** Apply the Micro-Harness Protocol from `tier-execution-protocol.md` — Scope Confirmation → Constraint Declaration → **Wait for [DO: YES]** → Execute → Self-Verify. Fail fast on scope creep.
- **STANDARD**: Standard coding. One lightweight planning pass (approach in ≤3 sentences + file list + 1-2 risks) before execution. Parallel tool calls are mandatory.
- **PREMIUM**: Architecture, deep debugging, audits. MUST use Sequential Thinking (minimum 3 steps). Find root causes, not symptoms.

## 2. BUDGET: Anti-Lazy Enforcement
To prevent BUDGET tasks from producing sloppy outputs, the agent MUST answer the following before any code/text modification:
- **What is the one change being made?** (If the answer cannot fit in 1 sentence, escalate to STANDARD.)
- **What constraint guarantees this change doesn't break anything adjacent?** (Justify atomicity.)

## 3. Sequential Thinking Mandate (Premium Tier)
When invoking Sequential Thinking:
1. State the problem hypothesis.
2. Break it into sub-problems.
3. Evaluate at least 2 alternative approaches.
4. Conclude with the chosen approach and its trade-offs.

## 4. Edge-Case Tax
Before finalizing any execution plan, list 2-3 potential failure modes or edge cases. This is mandatory for STANDARD and PREMIUM, optional for BUDGET.

## 5. Overthinking / Underthinking Guard
- If a `BUDGET` task exceeds one target file, it MUST escalate to `STANDARD` immediately.
- If a `PREMIUM` task cannot produce at least two alternatives, reasoning depth is insufficient and must continue.
- If the plan cannot name one concrete risk, classification is likely too low and should be escalated.

## 6. Reasoning Evidence Block
For `STANDARD` and `PREMIUM`, include a compact reasoning evidence block before completion:

1. `Chosen Path`
2. `Rejected Alternative`
3. `Primary Risk`
4. `Mitigation`

Missing this block means reasoning is not auditable.


---

# Adversarial Twin Protocol

To achieve "Small Model Superiority", the agent MUST externalize its critical thinking by adopting an "Adversarial Twin" persona before finalizing any feature. 

## The Protocol
When a task is implemented but not yet verified:
1. **Context Switch**: The agent explicitly declares: `"Swapping to Breaker Persona."`
2. **The Goal of the Breaker**: The Breaker's ONLY objective is to find a flaw in the Builder's code. It must be highly pessimistic.
3. **Attack Vectors**:
   - What happens if the network drops mid-request?
   - What if a JSON field is `null` or missing?
   - Is there a race condition if the user double-taps?
   - Does this violate any architectural boundaries (e.g., UI directly calling DB)?
4. **Dynamic Harness Generation**: For the chosen attack vector, the Breaker must formulate a failing condition (or pseudo-unit test) using principles from `autoharness-protocol.md`.
5. **Synthesis & Loop**: The Builder must then modify the original code until the Breaker's attack is neutralized.
6. **Auto-Abort (Post-Execution Circuit Breaker)**: See `.agents/rules/core-guardrails.md` Section 4 for the 3X Fail auto-abort protocol.

*Never blindly trust the first draft of the code. Always let the Twin attack it first.*

## Coverage Minimums (Mandatory)
- `STANDARD`: at least 1 attack vector + 1 concrete failing condition.
- `PREMIUM`: at least 2 distinct attack vectors, one of which MUST be data-integrity or authorization related.

## Evidence Output Contract
Before completion, include a compact Breaker evidence block:

1. `Vector Tested`
2. `Failure Condition`
3. `Observed Result`
4. `Fix Applied`
5. `Residual Risk`

If this block is missing for Tier-1+, the task status cannot be marked as done.