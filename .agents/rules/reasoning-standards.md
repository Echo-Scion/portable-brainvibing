---
description: Unified standards for analytical rigor, reasoning depth per tier, and internal validation (Adversarial Twin).
activation: model_decision

version: 3.0.0
last_updated: 2026-05-20
---

# Analytical Standards & Adversarial Protocol

## 1. The 5 Structural Questions (MANDATORY TEMPLATE)
Before designing a system or writing code for a complex feature, you MUST output this template filled out with your analysis:

```markdown
### Structural Critique
1. **Why does this exist?** (Root cause of the requirement)
2. **Is this the correct abstraction?** (Is this layer necessary?)
3. **What breaks if this is removed?** (Coupling analysis)
4. **What adversary could exploit this?** (Threat modeling)
5. **Does intent match behavior?** (Verify implementation matches docs)
```

## 2. Adversarial Twin Protocol (MANDATORY TEMPLATE)
To achieve "Small Model Superiority", you MUST explicitly attack your own code before finalizing a feature. "Adopting a persona" does not work. You MUST output this exact block:

```markdown
### Adversarial Twin Attack
- **Vector Tested**: [e.g., Network drop mid-request]
- **Failure Condition**: [What would break in the current code?]
- **Fix Applied**: [What was added to mitigate this?]
- **Residual Risk**: [What is still a slight risk?]
```
*If this block is missing for Tier-1/Tier-2 tasks, the task is NOT done.*

## 3. Causal Enforcement (The "No-Fix" Policy)
- **Iron Law**: No code modifications are permitted until the root cause of an issue is isolated and a hypothesis is verified.
- **Protocol**: If a bug is reported, you MUST first demonstrate the failure (via test or reproduction script) and trace the data flow before proposing a fix.

## 4. Value-Density Analysis (Scope Guard)
- **MVC Principle**: Prioritize Minimum Viable Complexity. 
- **Filtering Modes**:
    - *Reduction*: Identify and remove 10-20% of non-essential complexity.
    - *Selective Expansion*: Only expand scope if it adds 10x value.
    - *Hold*: Strictly adhere to the original blueprint.