---
description: Protocol for selecting the correct model tier and the enforced workflows per tier (Bento Box, Auto-router).
trigger: model_decision
---

# 1. Model Tier Classification & Routing
# Model Tier Protocol

## 0. Tier Classification Heuristics (Read First)

> **Auto-Router**: Before choosing a tier, answer these questions in order. Stop at the first match.

| Question | Yes → Tier |
| :--- | :--- |
| Can I describe the full change in 1 sentence and it touches only 1 file? | `BUDGET` |
| Does the change require reading state from >1 file to understand impact? | `STANDARD` |
| Does it touch auth, RLS, global config, or cross-system architecture? | `PREMIUM` |
| Am I unsure which tier applies? | Escalate to `STANDARD`, declare why. |

**Golden Rule**: When defaulting to `STANDARD`, you MUST explicitly state which heuristic forced it. Silent default to STANDARD is a protocol violation.

> **Anti-Deliberation Clause**: If you need to *read a file to determine* whether the task qualifies as BUDGET, the task is already STANDARD. BUDGET classification must be immediately obvious from the task description alone — no investigation required.

---

## 1. The Three Tiers (Calibrated)

| Tier | Label | Required Model Allocation | Practical Scope | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | `BUDGET` | Claude Haiku / Gemini Flash | **Atomic / Stylistic** | Documentation, log updates, formatting, minor CSS/styling, single-file bug fixes (localized logic), basic boilerplate generation, basic unit test additions. |
| **Tier 1** | `STANDARD` | Claude Sonnet / Gemini Pro Low | **Integrative / Feature** | Multi-file feature implementation, domain-specific state management, complex bug fixes spanning multiple modules. |
| **Tier 2** | `PREMIUM` | Claude Opus / Gemini Pro High | **Architectural / Risky** | Global system refactors, security/Auth/RLS logic changes, high-risk infrastructure updates, deep performance bottleneck resolution. |

## 2. Infrastructure Special Note
- **Don't Over-Classify**: Modifying files inside `.agents/` is NOT automatically `PREMIUM`.
- If the change is purely about keeping the registry/map up to date, use `STANDARD`.
- If the change modifies the *logic* of how agents operate (e.g., changing `core-guardrails.md`), use `PREMIUM`.

## 3. Mandatory Declaration & Manual Routing (Anigravity IDE)
- Because **Anigravity IDE** does not have an *auto-routing* feature, switching models must be done **MANUALLY** by the user.
- Sebelum mengeksekusi **TUGAS APAPUN** (Tier 0, 1, 2) yang memanipulasi file/sistem, agent **WAJIB** membuat Implementation Plan / pesan Binary Oratory dan mendeklarasikan: `[TIER: <NAMA TIER>]` beserta **Required Model Allocation**.
- **Auto-Abort Pre-Execution (Safety Gate)**: If the agent is currently running on a *BUDGET/Small* model but the deterministic calculation demands *PREMIUM*, the agent must emit the signal `[ABORT: TIER MISMATCH - PLEASE SWITCH MODEL AND REPEAT PROMPT]`.
- **In IDE/Anigravity mode**: Write this at the top of `implementation_plan.md` atau pesan *Binary Oratory*. Setelah menulisnya, **BERHENTI SEPENUHNYA (STOP COMPLETELY)**. Jangan jalankan tool perbaikan file apa pun. Tunggu konfirmasi `[DO: YES]` (jika model yang aktif saat ini dirasa cukup) atau *Retry* (setelah mengganti model).
- This gives the user the opportunity to **change the Chat Agent (Model) in the IDE dropdown** (misalnya pindah dari Claude Haiku ke Claude Sonnet / Gemini Pro) spesifik untuk eksekusi tersebut.
- **Zero Exemptions**: Tugas `BUDGET` sekalipun TIDAK BOLEH dieksekusi secara langsung. Mereka wajib melewati gerbang *pre-flight* ini agar *user* selalu memegang kendali absolut atas *routing* model.

## 4. Forced Intelligence Per Tier (Capability Harness)

The following constraints are **mandatory per tier**, not optional. They prevent lazy or "sloppy" outputs at each level.

### BUDGET: Micro-Harness Protocol
Even simple tasks MUST satisfy the following Lightweight Validation Gate before output is accepted:
1. **Scope Confirmation** (1 sentence): State what the task is in plain English. No more, no less.
2. **Constraint Declaration** (1-3 bullets): What CANNOT be changed or broken. Serves as a self-injected guardrail.
3. **Mandatory Pre-Flight**: Output the Binary Oratory/Implementation Plan and **WAIT** for `[DO: YES]`. "Act first" is strictly prohibited.
4. **Zero-Theater Execution**: After confirmation, perform the action immediately without narrative justification.
5. **Self-Verification Micro-Check**: After execution, confirm the output satisfies the original scope (e.g., "File updated. Key: X changed to Y. No other lines modified.").
- **Token Ceiling**: BUDGET tasks MUST NOT read more than 1 file in full. Use `grep_search` for targeted extraction.
- **Prohibited Actions in BUDGET**: No Sequential Thinking calls, no multi-file reads, no architectural scope expansion.

### STANDARD: Lightweight Planning Gate
Before any execution:
1. State the implementation approach in ≤3 sentences.
2. List files to be touched.
3. Identify 1-2 risk points.

Then execute in parallel where possible (Turn Minimization).

After implementation, **before marking as done**: apply the Adversarial Twin Protocol (`reasoning-standards.md`). Declare `"Swapping to Breaker Persona."` and run at least 1 attack vector against the output.

### PREMIUM: Full Sequential Thinking Mandate
See `reasoning-standards.md` for the full protocol. Sequential Thinking with minimum 3 thought steps is **mandatory, not optional**.

## 5. Escalation & Transition Rules
- **Escalation**: If a task initially classified as `STANDARD` reveals unexpected complexity mid-execution (e.g., a simple script tweak breaks the entire graph), PAUSE and re-declare as `PREMIUM`.
- **BUDGET → STANDARD Escalation Trigger**: If a "single-file fix" requires understanding of state shared across >2 files, escalate to `STANDARD`.
- **Downgrade (Phase-Based)**: Permitted ONLY between distinct implementation phases (e.g., move to `STANDARD` for UI after a `PREMIUM` architecture phase).
- **No Silent Downgrades**: All tier changes MUST be explicitly declared.

## 6. Token Economy Rules Per Tier
| Tier | Max File Reads | Preferred Read Mode | Parallel Tool Calls |
| :--- | :--- | :--- | :--- |
| `BUDGET` | 1 (targeted grep preferred) | `grep_search` > `view_file` (header only) | Allowed |
| `STANDARD` | 3-5 (surgical sections) | `view_file` with line range | Mandatory for independent steps |
| `PREMIUM` | Unlimited (justified) | Full reads when necessary | Mandatory |

## 7. Deterministic Tier Fallback (Anti-Subjectivity)
When classification is ambiguous, use this deterministic fallback:

1. Count impacted files.
2. Count cross-domain boundaries (rules, scripts, workflows, security, deployment).
3. Select tier:
	- `BUDGET`: 1 file and 0 cross-domain boundaries.
	- `STANDARD`: 2-5 files or 1 boundary.
	- `PREMIUM`: >5 files or 2+ boundaries or any security/deployment risk.

If the declared tier is lower than this fallback result, escalation is mandatory.

## 8. Governance Evidence Block
For Tier-1+ execution, the pre-flight declaration MUST include:

- `Heuristic Match`: Which table row triggered classification.
- `Fallback Score`: File count + boundary count.
- `Escalation Check`: `PASS` or `FAIL`.

## 9. Small Model Superiority Suite
When operating as a **BUDGET Model**, the agent **MUST** adhere to the following architectural triad to prevent hallucinations:
1. **Context Diet Protocol (`context-standards.md`)**: Mandatory *Skeleton-First* (Grep/AST), forbidden from *full-reads* on long files to avoid *context poisoning*.
2. **Bento-Box Workflow (`tier-execution-protocol.md`)**: Mandatory single *State-Machine*. One target, one evaluation. Forbidden from manipulating multiple files simultaneously.
3. **Micro-Canons (`canons/micro/README.md`)**: Mandatory reading of domain summaries before starting reasoning.
4. **KPI Telemetry (`track_budget.py`)**: All BUDGET/Small model tasks MUST be tracked via `.agents/scripts/track_budget.py` to maintain the 70% resolution target.

# 2. Bento-Box Workflow (Anti-Multitasking for Budget Models)
# Bento-Box Workflow (Anti-Multitasking)

## 1. The Core Problem
Small models fail acutely when attempting *Zero-Shot Planning* for multiple tasks at once. If told to "Create UI, connect to DB, and write tests", the model will mix up logic, create truncated syntax, or severely hallucinate.

## 2. The Bento-Box Law (One Compartment, One Flavor)
When an execution is performed by **[TIER: BUDGET]**, static *multitasking* is ILLEGAL. The agent **MUST** apply a *Hard Pause State-Machine*: 

1. **One-File Rule:** The agent may only manipulate *one* target per iteration (One file created/edited).
2. **Hard Pause:** After one action is completed, the agent must trigger an evaluation/lint/test for that *single* change.
3. **No Batching:** Do not fire 3 `create_file` or `replace_string` *tool calls* in parallel if the task affects architectural logic. (Except for deterministic renaming refactors).

## 3. Sequential Execution
Divide the task into isolated compartments (Bento-Box):
- Box 1: Create *Skeleton Interface*. Done. Report.
- Box 2: Fill *Business Logic*. Done. Report.
- Box 3: Connect to *UI*. Done. Report.

Each "Box" completion must be verified to run purely without depending on uncompleted boxes. If a budget model feels the task is too layered, it must immediately trigger the *Auto-Abort* mechanism and request a *Premium Model*.