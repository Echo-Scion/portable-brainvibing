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
| Is this a background/batch task, non-critical indexing, or scheduled validation? | `Tier 1` |
| Is it an ultra-fast agentic workflow, long-context code execution, or real-time interactive task? | `Tier 2` |
| Is this an automated test run, scheduled linting, or low-priority regression test? | `Tier 3` |
| Is it complex STEM problem solving, advanced coding, or comprehensive dataset analysis? | `Tier 4` |
| Is this high-quality app prototyping, advanced code generation, or requires nuanced instruction following? | `Tier 5` |
| Does it involve enterprise planning, core architecture, or highly meticulous multi-step problem solving? | `Tier 6` |
| Am I unsure which tier applies? | Escalate to `Tier 4`, declare why. |

**Golden Rule**: When defaulting to `Tier 4`, you MUST explicitly state which heuristic forced it. Silent default is a protocol violation.

> **Anti-Deliberation Clause**: If you need to *read a file to determine* whether the task qualifies as Tier 1 or 2, the task is already Tier 4. Tier 1/2 classification must be immediately obvious from the task description alone — no investigation required.

---

## 1. The Six Tiers (Calibrated)

| Tier | Queue | Required Model Allocation | Characteristic | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | `LOW` | Gemini 3.5 Flash (Low Queue) | **Multimodal / Speed** | Background indexing, non-critical telemetry, batch validations, and scheduled tasks. |
| **Tier 2** | `HIGH` | Gemini 3.5 Flash (High Queue) | **Multimodal / Speed** | Ultra-fast agentic workflows, long-context code execution, and high-frequency real-time interactive tasks. |
| **Tier 3** | `LOW` | Gemini 3.1 Pro (Low Queue) | **Deep Reasoning** | Automated unit test runs, scheduled linting, and low-priority regression testing. |
| **Tier 4** | `HIGH` | Gemini 3.1 Pro (High Queue) | **Deep Reasoning** | Complex STEM problem solving, advanced coding, and comprehensive dataset analysis. |
| **Tier 5** | `HIGH` | Claude 4.6 Sonnet (Thinking Enabled) | **Balanced Reasoning** | High-quality app prototyping, advanced code generation, and nuanced instruction following. |
| **Tier 6** | `HIGH` | Claude 4.6 Opus (Thinking Enabled) | **Max Intelligence** | Enterprise planning, deep conceptual reasoning, and highly meticulous multi-step problem solving. |

## 2. Infrastructure Special Note
- **Don't Over-Classify**: Modifying files inside `.agents/` is NOT automatically `Tier 6`.
- If the change is purely about keeping the registry/map up to date, use `Tier 4`.
- If the change modifies the *logic* of how agents operate (e.g., changing `core-guardrails.md`), use `Tier 6`.

## 3. Mandatory Declaration & Manual Routing (Anigravity IDE)
- Because **Anigravity IDE** does not have an *auto-routing* feature, switching models must be done **MANUALLY** by the user.
- Sebelum mengeksekusi **TUGAS APAPUN** (Tier 1-6) yang memanipulasi file/sistem, agent **WAJIB** mengevaluasi tier apa yang **SEHARUSNYA (TARGET TIER)** dipakai berdasarkan heuristik, BUKAN tier atau model yang sedang dipakai saat ini.
- **Auto-Abort Pre-Execution (Strict Safety Gate)**: Agent WAJIB membandingkan *Current Model* (model AI yang sedang aktif/berjalan) dengan *Target Tier* hasil rekomendasi. Jika tidak sesuai (terutama jika kapabilitas model saat ini di bawah *Target Tier*), agent **WAJIB** mengeluarkan sinyal berikut dan **BERHENTI SEPENUHNYA**:
  `[ABORT: TIER MISMATCH. TARGET TIER: <NAMA TIER YANG DIWAJIBKAN>. PLEASE SWITCH MODEL AND REPEAT PROMPT]`
- **Zero-Action on Abort**: Setelah mengeluarkan sinyal ABORT di atas, agent harus BERHENTI seketika (hentikan chat). Dilarang memanggil *tools* apa pun, dilarang memberi penjelasan tambahan, dan dilarang melanjutkan eksekusi.
- **In IDE/Anigravity mode**: Jika tier sudah sesuai (atau user memaksa lanjut), tulislah deklarasi `[TIER: <TARGET TIER>]` beserta *Required Model Allocation* di awal pesan atau `implementation_plan.md`, lalu tunggu konfirmasi `[DO: YES]` dari user (jika bukan workflow otomatis).
- **Zero Exemptions**: Tugas `Tier 1` sekalipun TIDAK BOLEH dieksekusi secara langsung. Mereka wajib melewati gerbang *pre-flight* ini agar *user* selalu memegang kendali absolut atas *routing* model.

## 4. Forced Intelligence Per Tier (Capability Harness)

The following constraints are **mandatory per tier**, not optional. They prevent lazy or "sloppy" outputs at each level.

### Tier 1 & 2 (Flash): Micro-Harness Protocol
Even simple tasks MUST satisfy the following Lightweight Validation Gate before output is accepted:
1. **Scope Confirmation** (1 sentence): State what the task is in plain English. No more, no less.
2. **Constraint Declaration** (1-3 bullets): What CANNOT be changed or broken. Serves as a self-injected guardrail.
3. **Mandatory Pre-Flight**: Output the Binary Oratory/Implementation Plan and **WAIT** for `[DO: YES]`. "Act first" is strictly prohibited.
4. **Zero-Theater Execution**: After confirmation, perform the action immediately without narrative justification.
5. **Self-Verification Micro-Check**: After execution, confirm the output satisfies the original scope (e.g., "File updated. Key: X changed to Y. No other lines modified.").
- **Token Ceiling**: Tier 1/2 tasks MUST NOT read more than 1 file in full. Use `grep_search` for targeted extraction.
- **Prohibited Actions**: No Sequential Thinking calls, no multi-file reads, no architectural scope expansion.

### Tier 3 & 4 (Pro): Lightweight Planning Gate
Before any execution:
1. State the implementation approach in ≤3 sentences.
2. List files to be touched.
3. Identify 1-2 risk points.

Then execute in parallel where possible (Turn Minimization).

After implementation, **before marking as done**: apply the Adversarial Twin Protocol (`reasoning-standards.md`). Declare `"Swapping to Breaker Persona."` and run at least 1 attack vector against the output.

### Tier 5 & 6 (Claude Thinking): Full Sequential Thinking Mandate
See `reasoning-standards.md` for the full protocol. Sequential Thinking with minimum 3 thought steps is **mandatory, not optional**.

## 5. Escalation & Transition Rules
- **Escalation**: If a task initially classified as `Tier 4` reveals unexpected complexity mid-execution (e.g., a simple script tweak breaks the entire graph), PAUSE and re-declare as `Tier 6`.
- **Tier 1/2 → Tier 4 Escalation Trigger**: If a "single-file fix" requires understanding of state shared across >2 files, escalate to `Tier 4`.
- **Downgrade (Phase-Based)**: Permitted ONLY between distinct implementation phases (e.g., move to `Tier 4` for UI after a `Tier 6` architecture phase).
- **No Silent Downgrades**: All tier changes MUST be explicitly declared.

## 6. Token Economy Rules Per Tier
| Tier | Max File Reads | Preferred Read Mode | Parallel Tool Calls |
| :--- | :--- | :--- | :--- |
| `Tier 1 & 2` | 1 (targeted grep preferred) | `grep_search` > `view_file` (header only) | Allowed |
| `Tier 3 & 4` | 3-5 (surgical sections) | `view_file` with line range | Mandatory for independent steps |
| `Tier 5 & 6` | Unlimited (justified) | Full reads when necessary | Mandatory |

## 7. Deterministic Tier Fallback (Anti-Subjectivity)
When classification is ambiguous, use this deterministic fallback:

1. Count impacted files.
2. Count cross-domain boundaries (rules, scripts, workflows, security, deployment).
3. Select tier:
	- `Tier 1-2`: 1 file and 0 cross-domain boundaries.
	- `Tier 3-4`: 2-5 files or 1 boundary.
	- `Tier 5-6`: >5 files or 2+ boundaries or any security/deployment risk.

If the declared tier is lower than this fallback result, escalation is mandatory.

## 8. Governance Evidence Block
For Tier 3-6 execution, the pre-flight declaration MUST include:

- `Heuristic Match`: Which table row triggered classification.
- `Fallback Score`: File count + boundary count.
- `Escalation Check`: `PASS` or `FAIL`.

## 9. Small Model Superiority Suite
When operating as a **Tier 1/2 Model (Flash)**, the agent **MUST** adhere to the following architectural triad to prevent hallucinations:
1. **Context Diet Protocol (`context-standards.md`)**: Mandatory *Skeleton-First* (Grep/AST), forbidden from *full-reads* on long files to avoid *context poisoning*.
2. **Bento-Box Workflow (`tier-execution-protocol.md`)**: Mandatory single *State-Machine*. One target, one evaluation. Forbidden from manipulating multiple files simultaneously.
3. **Micro-Canons (`canons/micro/README.md`)**: Mandatory reading of domain summaries before starting reasoning.
4. **KPI Telemetry (`track_budget.py`)**: All Tier 1/2 tasks MUST be tracked via `.agents/scripts/track_budget.py` to maintain the 70% resolution target.

# 2. Bento-Box Workflow (Anti-Multitasking for Flash/Tier 1-2)
# Bento-Box Workflow (Anti-Multitasking)

## 1. The Core Problem
Small models fail acutely when attempting *Zero-Shot Planning* for multiple tasks at once. If told to "Create UI, connect to DB, and write tests", the model will mix up logic, create truncated syntax, or severely hallucinate.

## 2. The Bento-Box Law (One Compartment, One Flavor)
When an execution is performed by **[TIER: 1-2 (Flash)]**, static *multitasking* is ILLEGAL. The agent **MUST** apply a *Hard Pause State-Machine*: 

1. **One-File Rule:** The agent may only manipulate *one* target per iteration (One file created/edited).
2. **Hard Pause:** After one action is completed, the agent must trigger an evaluation/lint/test for that *single* change.
3. **No Batching:** Do not fire 3 `create_file` or `replace_string` *tool calls* in parallel if the task affects architectural logic. (Except for deterministic renaming refactors).

## 3. Sequential Execution
Divide the task into isolated compartments (Bento-Box):
- Box 1: Create *Skeleton Interface*. Done. Report.
- Box 2: Fill *Business Logic*. Done. Report.
- Box 3: Connect to *UI*. Done. Report.

Each "Box" completion must be verified to run purely without depending on uncompleted boxes. If a Flash model feels the task is too layered, it must immediately trigger the *Auto-Abort* mechanism and request a *Pro/Claude Model* (Tier 4+).