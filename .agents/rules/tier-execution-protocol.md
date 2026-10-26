---
description: Protocol for selecting the correct model tier and the enforced workflows per tier (Bento Box, Auto-router).
activation: model_decision

version: 0.0.2
last_updated: 2026-09-26
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

> **Anti-Deliberation Clause**: If you need to *read a file to determine* whether the task qualifies as BUDGET, the task is already STANDARD. BUDGET classification must be immediately obvious from the task description alone.

---

## 1. The Elastic Neuro-Symbolic Continuum (Mechanical + Local SLM + Cloud 3-Tier Ecosystem)

`.agents` dynamically pairs **Tier 0 Mechanical Pre-Digestion** (`scanner.py`, `db.py`, `consequence_verifier.py`) with whatever Local SLM ($0\text{B}$ offline, $1.5\text{B}$, $3\text{B}$, $7\text{B}$, $14\text{B}$, $30\text{B}+$) and Cloud Model Tier are available:

| Execution Layer / Tier | Dynamic Scope (After Tier-0 AST Pre-Digestion) | Target Engine / Model Spectrum |
| :--- | :--- | :--- |
| **Tier 0: Mechanical Kernel** | AST skeleton mapping `[Lstart-Lend]`, PageRank centrality, `@sovereign_catch` post-conditions, FTS5 BM25, False-Green test scanning. | **Pure Python 3.10+ Stdlib + Rust (`rtk`/`sg`) + Bun** ($0\text{ cost}$, deterministic) |
| **Tier 1: Elastic Local SLM** | • **$1\text{B}\text{--}2\text{B}$ (`1.5b`)**: RAG keyword expansion, binary tags, short slugging.<br>• **$3\text{B}\text{--}4\text{B}$ (`3b`)**: Above + 1-shot narrow syntax/import repair guarded by `ast.parse`.<br>• **$7\text{B}\text{--}14\text{B}$**: Single-function `auto_heal()`, GraphRAG triplet extraction, Stage 2 security triage.<br>• **$30\text{B}\text{--}70\text{B}+$**: Multi-block refactoring, cross-encoder reranking, deep local autonomy. | **Ollama / `llama-server` / LM Studio / vLLM** ($0\text{ cloud cost}$; auto-skips if offline or task exceeds model envelope) |
| **Cloud `BUDGET`** | Targeted single-file fixes, routine day-to-day execution, and resolving pre-digested AST failure packets when Local SLM is offline or $\le 3\text{B}$. | **Gemini Flash / Claude Haiku** (Fast, ultra-low token cost via Bento-Box workflow) |
| **Cloud `STANDARD`** | Multi-file feature development (2–5 files), authoring standard test suites & invariant guards, UI prototyping. | **Gemini Pro / Claude Sonnet** (Balanced reasoning & coding) |
| **Cloud `PREMIUM`** | Phase 1 Genesis Blueprinting, designing complex cross-layer Invariant Fortresses, or resolving 3-attempt Circuit Breaker escalations. | **Gemini Thinking / Claude Opus** (Maximum intelligence, invoked $O(1)$ upfront) |

## 2. Infrastructure Special Note
- **Don't Over-Classify**: Modifying files inside `.agents/` is NOT automatically `PREMIUM`.
- If the change is purely about keeping the registry/map up to date, use `STANDARD`.
- If the change modifies the *logic* of how agents operate (e.g., changing Section 1 Core Guardrails in `AGENTS.md`), use `PREMIUM`.

## 3. Mandatory Declaration & Manual Routing (Cloud-First / All IDEs)
- Because most IDEs (including **Antigravity IDE**) do not auto-route models and not all users have a Local LLM installed, model switching is performed **MANUALLY** by the user via the IDE model dropdown.
- **Every-Turn Next-Task Reminder**: Whenever a response includes a non-empty `NEXT TASK` (i.e. not `"None"`), the agent **MUST** include `⚡ **RECOMMENDED TIER**` in the response footer specifying `BUDGET (Flash/Haiku)`, `STANDARD (Pro/Sonnet)`, or `PREMIUM (Thinking/Opus)` with a 1-phrase rationale for the next step.
- **Pre-Implementation Plan Gate**: Every `implementation_plan.md` MUST include `> ⚡ **EXECUTION TIER RECOMMENDATION**: ...` at the top so the user can switch down (e.g. from `PREMIUM` planning to `STANDARD`/`BUDGET` execution) or escalate before approving the plan.
- **Diagnosis-to-Plan Gate**: When a turn uncovers a defect, error, or architectural solution, `NEXT TASK` MUST NOT be `"None"`. It MUST proactively recommend `/plan` (or `/strict-tdd` for isolated bug fixes) to transition diagnosis into an executable plan.
- **Escalation Advice**: If a user prompts for an architectural overhaul or deep audit on a BUDGET model, the agent MUST recommend switching to `PREMIUM (Gemini Thinking / Claude Opus)` in the initial plan.
- **Overpowered Exemption**: If the user uses a PREMIUM model for a BUDGET task, proceed immediately without aborting, then recommend `BUDGET` for the follow-up turn.

## 4. Forced Intelligence Per Tier (Capability Harness)

The following constraints are **mandatory per tier**, not optional.

### BUDGET: Micro-Harness Protocol
Even simple tasks MUST satisfy the following Validation Gate before output is accepted:
1. **Telegraphic Execution**: Perform the action immediately without narrative justification.
2. **Self-Verification Micro-Check**: After execution, mechanically assert that the target file contains the expected state (e.g., run `grep_search` to verify string substitution).
- **Token Ceiling**: BUDGET tasks MUST NOT read more than 1 file in full. Use `grep_search` for targeted extraction.
- **Prohibited Actions**: No heavy architectural scope expansion.

### STANDARD: Lightweight Planning Gate
Before multi-file execution:
1. Initialize or update an execution plan Artifact (`task.md` or `implementation_plan.md`) outlining `[Approach, Files, Risks]`.
2. Execute code modifications using native IDE tools (`replace_file_content`, `multi_replace_file_content`).
3. Verify changes with an automated test or linter (`flutter test`, `dart analyze`, or `pytest`) ensuring `Exit Code 0`.

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

### Subagent Delegation (Lessword & 20% Overlap Gate)
To preserve the main thread's token context during long sessions, use subagents for investigative or atomic tasks.
- **20% Overlap Gate**: Never delegate tasks with $\ge 20\%$ shared context or interdependent code modifications to subagents. Validate before delegating using `python .agents/scripts/orion.py delegate-check <task1> <task2>`. If Exit Code 1 (`MERGE_TO_SINGLE_AGENT`), use single-agent sequential execution (`implementation_plan.md`) to maintain KV-cache prefix locality and prevent split-brain state drift. Delegate strictly to **Context-Isolating Scouts** (scanning raw logs, docs, or test outputs with $<10\%$ context overlap).
- **Lessword Rule**: When delegating to subagents (e.g., `research` or `self`), ALWAYS instruct them to return their final output in the compressed **Lessword Format** (terse, no fluff). 
- **Why**: Subagent tool results are injected into the main context verbatim. A 2k token prose response eats 2k tokens of main budget. A lessword response cuts this by ~60%, allowing the main session to last longer.
## 7. Deterministic Tier Fallback (Anti-Subjectivity)
When classification is ambiguous, use this deterministic fallback:

1. Count impacted files.
2. Count cross-domain boundaries (rules, scripts, workflows, security, deployment).
3. Select tier:
	- `BUDGET`: 1 file and 0 cross-domain boundaries.
	- `STANDARD`: 2-5 files or 1 boundary.
	- `PREMIUM`: >5 files or 2+ boundaries or any security/deployment risk.

If the declared tier is lower than this fallback result, escalation is mandatory.

## 8. Small Model Superiority Suite
When operating as a **BUDGET Model**, the agent **MUST** adhere to the following architectural triad:
1. **Context Diet Protocol (`performance-optimization.md`)**: Mandatory *Skeleton-First* (Grep/AST), forbidden from *full-reads* on long files to avoid *context poisoning*.
2. **Bento-Box Workflow**: Mandatory single *State-Machine*. Focus on 1 primary logic file (maximum 3 files total including test/scaffolding per iteration). Forbidden from multi-domain sprawling.
3. **Micro-Canons (`canons/micro/README.md`)**: Mandatory reading of domain summaries before starting reasoning.

# 2. Bento-Box Workflow (Anti-Multitasking for BUDGET)

## 1. The Core Problem
Small models fail acutely when attempting *Zero-Shot Planning* for multiple tasks at once. If told to "Create UI, connect to DB, and write tests", the model will mix up logic or severely hallucinate.

## 2. The Bento-Box Law (One Compartment, One Flavor)
When an execution is performed by a **BUDGET** tier model, static *multitasking* is ILLEGAL. The agent **MUST** apply a *Hard Pause State-Machine*: 

1. **Three-File Rule:** The agent may manipulate at most 1 primary logic file (maximum 3 files total including accompanying test/scaffolding) per iteration.
2. **Hard Pause:** After one iteration is completed, the agent must trigger an evaluation/lint/test for the changes.
3. **No Heavy Batching:** Do not fire >3 `create_file` or `replace_string` *tool calls* in parallel if the task affects architectural logic. (Except for deterministic renaming refactors).

## 3. Sequential Execution
Divide the task into isolated compartments (Bento-Box):
- Box 1: Create *Skeleton Interface*. Done. Report.
- Box 2: Fill *Business Logic*. Done. Report.
- Box 3: Connect to *UI*. Done. Report.

Each "Box" completion must be verified to run purely without depending on uncompleted boxes. If a BUDGET model detects a task spanning >2 sub-modules or requiring >3 architectural mutations, it MUST immediately trigger the *Auto-Abort* mechanism and request a *STANDARD* or *PREMIUM* Model.

## Reasoning Standards
# Analytical Standards & Adversarial Protocol

## 1. The 5 Structural Questions (Deterministic Gateway)
Before executing `write_file` or `replace` for a complex feature or system design, you MUST internally evaluate the following 5 dimensions. You do not need to output XML, but your reasoning must be evident in your plan:

1. **Root Cause**: Why does this exist?
2. **Abstraction Layer**: Is this layer necessary?
3. **Coupling Risk**: What breaks if this is removed?
4. **Threat Model**: What adversary could exploit this?
5. **Intent Match**: Does intent match behavior?

## 2. Adversarial & Causal Verification
*Consolidated into `.agents/skills/integrity-sentinel/SKILL.md` — load that file when performing TDD or verification.*



## 3. Value-Density Analysis (Scope Guard)
- **MVC Principle**: Prioritize Minimum Viable Complexity via mechanical filtering:
  - *Reduction Pass*: Run `grep` or analyze code to delete 10-20% of dead code/unused imports before adding new logic.
  - *Selective Expansion*: Request user's explicit permission before expanding scope beyond the original blueprint.
  - *Hold*: Strictly adhere to the original blueprint layout.

## 5. Evidence Contract (Done Gate)

All tasks MUST include a machine-verifiable evidence block matched to their tier:

| Tier | Action Proof | Validation Proof | Scope Proof |
| :--- | :--- | :--- | :--- |
| **BUDGET** | Required (which file changed) | Skippable (but must state why) | Required (confirm only target was touched) |
| **STANDARD** | Required | Required | Required |
| **PREMIUM** | Required | Required | Required |

- **Action Proof**: Which file/command/tool changed state.
- **Validation Proof**: Test/lint/check command output summary (pass/fail). BUDGET may skip if no automated test exists, but MUST document the blocker.
- **Scope Proof**: Explicit confirmation that only intended targets were modified.

If validation cannot be run, the agent MUST mark status as `PARTIAL` and state the exact blocker. Claiming `DONE` without evidence is **prohibited for all tiers**.

**Binary Oratory Mandate**: Validation proofs MUST rely strictly on binary exit codes (0 for success, >0 for failure). Subjective claims of success (e.g. "The logic looks correct") are strictly banned.
