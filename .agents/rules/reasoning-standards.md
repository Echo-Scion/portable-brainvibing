---
description: Unified standards for analytical rigor, reasoning depth per tier, and internal validation (Adversarial Twin).
activation: model_decision

version: 3.0.0
last_updated: 2026-05-20
---

# Analytical Standards & Adversarial Protocol

## 1. The 5 Structural Questions (Deterministic Gateway)
Before executing `write_file` or `replace` for a complex feature or system design, execute the following block in your response:

```xml
<structural_critique>
  <root_cause>Why does this exist?</root_cause>
  <abstraction_layer>Is this layer necessary?</abstraction_layer>
  <coupling_risk>What breaks if this is removed?</coupling_risk>
  <threat_model>What adversary could exploit this?</threat_model>
  <intent_match>Does intent match behavior?</intent_match>
</structural_critique>
```
*If this XML block is absent, DO NOT proceed to implementation.*

## 2. Adversarial Twin Protocol (Deterministic Execution)
"Adopting a persona" is probabilistic and fails. To achieve "Small Model Superiority", execute this strict verification protocol:

1. **Write Exploit Script**: Write a unit test or Python script targeting the newly written feature (e.g., test network drop, null data).
2. **Execute Exploit**: Run the test.
3. **Log & Mitigate**: Output the following XML block:
```xml
<adversarial_attack>
  <vector_tested>[Exact test case run]</vector_tested>
  <exit_code>[0 or >0]</exit_code>
  <fix_applied>[Code added to mitigate the failure]</fix_applied>
  <residual_risk>[Remaining risk]</residual_risk>
</adversarial_attack>
```
*Task is NOT done until `exit_code` matches the expected failure/mitigation cycle.*

## 3. Causal Enforcement (The "No-Fix" Policy)
- **Iron Law**: No code modifications are permitted until the root cause is deterministically proven.
- **Protocol**:
  1. Write `reproduce_bug.py` or `<feature>_test.dart`.
  2. Run the script.
  3. If script succeeds (no bug found), ABORT fix.
  4. If script fails (bug proven), proceed with implementation.

## 4. Value-Density Analysis (Scope Guard)
- **MVC Principle**: Prioritize Minimum Viable Complexity via mechanical filtering:
  - *Reduction Pass*: Run `grep` or analyze code to delete 10-20% of dead code/unused imports before adding new logic.
  - *Selective Expansion*: Require user's explicit `[DO: YES]` before expanding scope beyond the original blueprint.
  - *Hold*: Strictly adhere to the original blueprint layout.