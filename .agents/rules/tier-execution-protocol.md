---
description: Protocol for selecting the correct model tier and the enforced workflows per tier (Bento Box, Auto-router).
activation: model_decision

version: 0.0.1
last_updated: 2026-05-20
---

# 1. Model Tier Classification & Routing

## 0. Tier Classification Heuristics (Read First)

> **Auto-Router**: Before choosing a tier, answer these questions in order. Stop at the first match.

| Question | Yes → Tier |
| :--- | :--- |
| Is this an `orion_ops ingest`, `deploy`, or batch indexing operation? | `BUDGET` |
| Is this a background/batch task, non-critical indexing, or simple targeted file fix? | `BUDGET` |
| Is this an automated test run, scheduled linting, UI creation, or standard feature development? | `STANDARD` |
| Does it involve enterprise planning, complex STEM logic, core architecture, or deep debugging? | `PREMIUM` |
| Am I unsure which tier applies? | Escalate to `PREMIUM`, declare why. |

**Golden Rule (Mechanical Artifact)**: When escalating or defaulting to `PREMIUM`, you MUST output a strict JSON block `{"tier_decision": "PREMIUM", "heuristic_triggered": "<exact_reason>"}` in your response before executing tools.

> **Anti-Deliberation Clause**: If you need to *read a file to determine* whether the task qualifies as BUDGET, the task is already STANDARD. BUDGET classification must be immediately obvious from the task description alone.

---

## 1. The 3-Tier Model Ecosystem

| Task Tier | Capabilities & Practical Scope | Recommended Model Profile |
| :--- | :--- | :--- |
| **BUDGET** | Background indexing, telemetry, targeted single-file fixes, high-frequency real-time tasks. | Fast, Low Latency (e.g., Flash/Haiku) |
| **STANDARD** | UI prototyping, standard code generation, test runs, nuanced instruction following. | Balanced Reasoning (e.g., Sonnet/Pro) |
| **PREMIUM** | Enterprise planning, deep conceptual reasoning, complex multi-step problem solving. | Max Intelligence (e.g., Opus/Thinking) |

## 2. Infrastructure Special Note
- **Don't Over-Classify**: Modifying files inside `.agents/` is NOT automatically `PREMIUM`.
- If the change is purely about keeping the registry/map up to date, use `STANDARD`.
- If the change modifies the *logic* of how agents operate (e.g., changing `core-guardrails.md`), use `PREMIUM`.

## 3. Mandatory Declaration & Manual Routing (Antigravity IDE)
- Because **Antigravity IDE** does not have an *auto-routing* feature, switching models must be done **MANUALLY** by the user.
- Before executing **ANY TASK** that manipulates files/systems, the agent **MUST** evaluate which tier **SHOULD (TARGET TIER)** be used based on heuristics, NOT the currently active model.
- **Auto-Abort Pre-Execution (Downgrade Guard)**: The agent MUST compare the *Current Model* with the *Target Tier*. If the current model's capability is **LOWER** than the *Target Tier* (a downgrade), the agent **MUST** emit this signal and **STOP COMPLETELY**:
  `[ABORT: TIER MISMATCH. TARGET TIER: <REQUIRED TIER>. PLEASE SWITCH MODEL AND REPEAT PROMPT]`
- **Overpowered Exemption**: If the current model is *higher* than the Target Tier (e.g., using a PREMIUM model for a BUDGET task), the agent should **PROCEED**. Do not abort when overpowered.
- **Read-Only Exemption**: Tasks that only read files or query information (investigatory) do not require user confirmation `[DO: YES]` to proceed.

## 4. Forced Intelligence Per Tier (Capability Harness)

The following constraints are **mandatory per tier**, not optional.

### BUDGET: Micro-Harness Protocol
Even simple tasks MUST satisfy the following Validation Gate before output is accepted:
1. **Telegraphic Execution**: Perform the action immediately without narrative justification.
2. **Self-Verification Micro-Check**: After execution, mechanically assert that the target file contains the expected state (e.g., run `grep_search` to verify string substitution).
- **Token Ceiling**: BUDGET tasks MUST NOT read more than 1 file in full. Use `grep_search` for targeted extraction.
- **Prohibited Actions**: No Sequential Thinking calls, no architectural scope expansion.

### STANDARD: Lightweight Planning Gate
Before any execution:
1. Write a temporary file `.orion/standard_plan.md` containing `[Approach, Files, Risks]`.
2. Do not execute implementation until this file exists.
After implementation, **before marking as done**: 
a) Mechanically execute a test script (`test_adversarial.dart` or `pytest`) targeting the logic. Task is only done if exit code is 0.
b) Run `python .agents/scripts/orion.py track_budget --tier STANDARD` to log telemetry.

### PREMIUM: Full Sequential Thinking Mandate
See `Reasoning Standards` (Section 4 below) for the full protocol. Sequential Thinking with minimum 3 thought steps is **mandatory, not optional**.

## 5. Escalation & Transition Rules
- **Escalation**: If a task initially classified as `STANDARD` reveals unexpected complexity mid-execution, PAUSE and re-declare as `PREMIUM`.
- **BUDGET → STANDARD Escalation**: If a "single-file fix" requires understanding of state shared across >2 files, escalate to `STANDARD`.
- **No Silent Downgrades**: All tier changes MUST be explicitly declared.

## 6. Token Economy Rules Per Tier
| Tier | Max File Reads | Preferred Read Mode | Parallel Tool Calls |
| :--- | :--- | :--- | :--- |
| `BUDGET` | 1 (targeted grep preferred) | `grep_search` > `view_file` (header only) | Allowed |
| `STANDARD` | 3-5 (surgical sections) | `view_file` with line range | Mandatory for independent steps |
| `PREMIUM` | Unlimited (justified) | Full reads when necessary | Mandatory |

### Subagent Delegation (Cavecrew Protocol)
To preserve the main thread's token context during long sessions, use subagents for investigative or atomic tasks.
- **Rule**: When delegating to subagents (e.g., `research` or `self`), ALWAYS instruct them to return their final output in the compressed **Caveman Format** (terse, no fluff). 
- **Why**: Subagent tool results are injected into the main context verbatim. A 2k token prose response eats 2k tokens of main budget. A caveman response cuts this by ~60%, allowing the main session to last longer.
## 7. Deterministic Tier Fallback (Anti-Subjectivity)
When classification is ambiguous, use this deterministic fallback:

1. Count impacted files.
2. Count cross-domain boundaries (rules, scripts, workflows, [security.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/integrity-sentinel/references/[security.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/integrity-sentinel/references/security.md)), deployment).
3. Select tier:
	- `BUDGET`: 1 file and 0 cross-domain boundaries.
	- `STANDARD`: 2-5 files or 1 boundary.
	- `PREMIUM`: >5 files or 2+ boundaries or any [security.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/integrity-sentinel/references/[security.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/integrity-sentinel/references/security.md))/deployment risk.

If the declared tier is lower than this fallback result, escalation is mandatory.

## 8. Small Model Superiority Suite
When operating as a **BUDGET Model**, the agent **MUST** adhere to the following architectural triad:
1. **Context Diet Protocol (`context-standards.md`)**: Mandatory *Skeleton-First* (Grep/AST), forbidden from *full-reads* on long files to avoid *context poisoning*.
2. **Bento-Box Workflow**: Mandatory single *State-Machine*. One target, one evaluation. Forbidden from manipulating multiple files simultaneously.
3. **Micro-Canons (`canons/micro/[README](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/caveman-compress/[README.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/caveman-compress/README.md)).md`)**: Mandatory reading of domain summaries before starting reasoning.

# 2. Bento-Box Workflow (Anti-Multitasking for BUDGET)

## 1. The Core Problem
Small models fail acutely when attempting *Zero-Shot Planning* for multiple tasks at once. If told to "Create UI, connect to DB, and write tests", the model will mix up logic or severely hallucinate.

## 2. The Bento-Box Law (One Compartment, One Flavor)
When an execution is performed by a **BUDGET** tier model, static *multitasking* is ILLEGAL. The agent **MUST** apply a *Hard Pause State-Machine*: 

1. **One-File Rule:** The agent may only manipulate *one* target per iteration (One file created/edited).
2. **Hard Pause:** After one action is completed, the agent must trigger an evaluation/lint/test for that *single* change.
3. **No Batching:** Do not fire 3 `create_file` or `replace_string` *tool calls* in parallel if the task affects architectural logic. (Except for deterministic renaming refactors).

## 3. Sequential Execution
Divide the task into isolated compartments (Bento-Box):
- Box 1: Create *Skeleton Interface*. Done. Report.
- Box 2: Fill *Business Logic*. Done. Report.
- Box 3: Connect to *UI*. Done. Report.

Each "Box" completion must be verified to run purely without depending on uncompleted boxes. If a BUDGET model feels the task is too layered, it must immediately trigger the *Auto-Abort* mechanism and request a *STANDARD* or *PREMIUM* Model.

## Reasoning Standards
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
