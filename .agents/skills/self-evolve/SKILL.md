---
name: self-evolve
description: >-
  Post-task reflection and deterministic learning loop to extract patterns and prevent recurring mistakes. Use when tasks fail repeatedly, after resolving complex bugs, or when extracting new rules into LEARNINGS.md.
---

# 🧠 Self-Evolve (Mechanical Learning & Reflection Loop)

This workflow defines how the agent ecosystem learns and updates itself to prevent recurring mistakes.

## 1. ERROR EXTRACTION (SYNCHRONOUS)
- [ ] **Trace Extraction**: If a tool call fails (Exit Code > 0) or the user corrects you, mechanically extract the error trace into an XML block `<error_trace>`.
- [ ] **Root Cause Analysis**: Identify if the failure was due to a missing rule, contradictory instruction, or a missing context link.

## 2. MEMORY WRITE (PERSISTENCE)
- [ ] **Update Learnings**: Use `replace_file_content` or `python .agents/scripts/orion.py reflexion record` to inject the finding into `.agents/LEARNINGS.md`. Do not wait or queue this action.
- [ ] **4-Tuple Failure Pattern Contract (Harness-Zero Protocol)**:
  Every systemic reflection MUST capture:
  1. `Trigger`: Recognizable condition in the unexecuted proposal.
  2. `Evidence`: Concrete trajectory proof (failing exit code, diff, or error message).
  3. `Intervention (Action Recipe)`: Targeted student-native correction.
  4. `Do-Not-Trigger Guard`: False-positive boundary to prevent over-correction.

## 3. LOWEST VIABLE TIER (LVT) & HARNESS ADAPTATION (ANTI-REDUCTIONIST MANDATE)
> **Irreducible Complexity Notice**: Do NOT force every problem into Tier 0. Some tasks possess irreducible cognitive complexity and require model reasoning. Every distilled invariant must rest at its **Lowest Viable Tier (LVT)**:
> - **Tier 0 (Harness Zero / Deterministic)**: Syntactic, static, or binary checks (AST checks in `security.py`, assertions in `verify_agents.py`, RTK hooks). Cost: $0, Latency: <5ms.
> - **Tier 1 (Budget Prompt / Heuristic)**: High-density checklists in prompt memory, single-file triage, or lightweight heuristic regex.
> - **Tier 2 (Standard Model Reasoning)**: Multi-file semantic reasoning, stateful test synthesis, UI design token contracts, and code review.
> - **Tier 3 (Premium Cognitive Reasoning)**: Novel system design, cross-domain contradictions, or enterprise architectural overhauls.

- [ ] **Harness Adaptation Matrix**:
  When graduating external capabilities or learnings into `.agents`:
  - **Tool** $\to$ **Action Recipe** (`references/` bash/python heredoc script).
  - **Middleware** $\to$ **Review Gate / Pre-Tool Hook** (`hooks.json` + `security.py`).
  - **Skill** $\to$ **Diagnostic Review Guidance** (SOP failure checks).
  - **Memory** $\to$ **4-Tuple Failure Pattern Bank** (`.orion/matrix/`).

- [ ] **Executable Verification Mandate (Anti-Graveyard Gate)**:
  - Text-only rules without code checks are treated as informal advisories, NEVER promoted to permanent core guardrails.
  - If a rule targets Tier 0, it MUST include an executable mechanical check:
    1. **AST Pattern Check**: In `.agents/scripts/core/security.py`, OR
    2. **Static/Integration Assertion**: In `.agents/scripts/commands/verify_agents.py`, OR
    3. **Deterministic Mutation Test**: In `.agents/scripts/commands/verify_agents.py` (adversarial suite) or test harness.
  - If a rule targets Tier 1/2, it must specify concrete behavioral evidence criteria in its contract.
- [ ] **Developer Review**: Present the drafted rule, its resting tier, and its verification test to the developer. Ask for explicit approval.
- [ ] **Promotion**: If the developer approves and tests pass, apply changes to the target skill or rule file.

## 3.5. OFFENSIVE OPTIMIZATION (SUCCESS LOOP)
> **ESCAPE HATCH**: Maximum 1 optimization proposal per session. If already triggered once, skip this step.
- [ ] **Token & Path Audit**: If a task succeeds flawlessly, analyze the session for token waste, redundant tool calls, or slow paths.
- [ ] **Propose Compression**: If inefficiency is found, proactively synthesize a skill compression patch (Darwinian evolution driven by optimization, not just failure).

## 4. PATTERN RECOGNITION & SYNTHESIS (DISCOVER)
> **CIRCUIT BREAKER**: Maximum 2 autonomous synthesis operations per session. Beyond that, queue for next session.
- **CRITICAL ACTION**: **Pattern Scan**: At the end of a session, execute `grep_search` on BOTH `.agents/LEARNINGS.md` AND `MEMORY.md` (specifically for `<friction-data>` tags) NOW for repetitive manual tasks to fuse short-term and long-term friction.
- **CRITICAL ACTION**: **Synthesis Matrix (HITL Gate)**: 
  - If a pattern is found, determine its type BEFORE creation:
    - **Rule**: Dictates general AI behavior (e.g., "always use X"). Destination: `.agents/rules/`. **REQUIRES HUMAN APPROVAL via `[DO: YES]` before creation.**
    - **Procedural Playbook / Skill**: Step-by-step situational operation. Destination: `.agents/skills/` (or nested Tier-3 `references/`). Can be generated autonomously.
    - **Skill**: Relies on specific API/Tooling. Destination: `.agents/skills/`. Can be generated autonomously.
- [ ] **Generate Asset & Sovereign Harness Staging**: 
  For autonomous skills, stage them through the Sovereign Harness admission gatekeeper:
  1. Stage proposal: emit intent via `stage_skill` or stage via CLI:
     ```pwsh
     python .agents/scripts/orion.py harness promote
     ```
  2. The deterministic promoter validates 6 admission classes (AST safety, frontmatter schema, progressive disclosure cap <= 500 lines, no absolute host paths, ledger evidence) before committing to `.agents/skills/`.
- [ ] **Integrate & Self-Audit**: Update JIT triggers and ensure the new file is indexed correctly (Rules in `RULES_INDEX.md`). If modifying `.agents/` engine itself, verify against `.agents/skills/meta-agent-admin/references/meta-agent-audit.md` and ensure `python .agents/scripts/orion.py verify` returns Exit Code 0. You MUST execute `python .agents/scripts/orion.py orion_ops ingest` to store them back into `.orion/`.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Temporal Pulse, Activity-Based Cadence** | .agents/skills/self-evolve/references/temporal-pulse.md |

