---
description: Post-Task Reflection & Learning Loop (Deterministic Self-Evolution)
activation: After task completion or upon encountering systemic errors.
---
# 🧠 WORKFLOW: SELF-EVOLVE (MECHANICAL EVOLUTION)

This workflow defines how the agent ecosystem learns and updates itself to prevent recurring mistakes.

## 1. ERROR EXTRACTION (SYNCHRONOUS)
- [ ] **Trace Extraction**: If a tool call fails (Exit Code > 0) or the user corrects you, mechanically extract the error trace into an XML block `<error_trace>`.
- [ ] **Root Cause Analysis**: Identify if the failure was due to a missing rule, contradictory instruction, or a missing context link.

## 2. MEMORY WRITE (PERSISTENCE)
- [ ] **Update Learnings**: Use the `replace_file_content` or `write_to_file` tool to inject the finding into `.agents/LEARNINGS.md`. Do not wait or queue this action.

## 3. DARWINIAN A/B [SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)) EVOLUTION (ANTI-DRIFT)
- [ ] **Evolve Rule (V2 Fork)**: If a missing or contradictory rule caused the error, you MUST NOT blindly overwrite the rule. Instead, fork the rule (e.g. `cp [SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)) [SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md))-v2.md`).
- [ ] **A/B Benchmark (MANDATORY)**: Run `python .agents/scripts/orion.py evolve bench --skill <skill_name>` on BOTH V1 and V2. 
- [ ] **Fitness Gate**: If `score(V2) >= score(V1)`, promote it: `mv [SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md))-v2.md [SKILL](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)).md`. If it fails, ARCHIVE it (do not delete).
- [ ] **Ledger Logging**: You MUST log this mutation. Run a Python script or write directly to `.agents/EVOLUTION_LOG.jsonl` noting the target, trigger, and fitness delta.

## 3.5. OFFENSIVE OPTIMIZATION (SUCCESS LOOP)
> **ESCAPE HATCH**: Maximum 1 optimization proposal per session. If already triggered once, skip this step.
- [ ] **Token & Path Audit**: If a task succeeds flawlessly, analyze the session for token waste, redundant tool calls, or slow paths.
- [ ] **Propose Compression**: If inefficiency is found, proactively synthesize a skill compression patch (Darwinian evolution driven by optimization, not just failure).

## 4. PATTERN RECOGNITION & SYNTHESIS (DISCOVER)
> **CIRCUIT BREAKER**: Maximum 2 autonomous synthesis operations per session. Beyond that, queue for next session.
- **CRITICAL ACTION**: **Pattern Scan**: At the end of a session, execute `grep_search` on BOTH `.agents/LEARNINGS.md` AND `MEMORY.md` (specifically for `<friction-data>` tags) NOW for repetitive manual tasks to fuse short-term and long-term friction.
- **CRITICAL ACTION**: **Autonomous Synthesis**: If a pattern is found, proactively synthesize the rule without waiting for user approval. Darwinian mutation must be 100% autonomous.
- [ ] **Generate Asset**: Use `.agents/templates/custom-rule.template.md` (or equivalent structure) to generate the new standalone [SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/[SKILL.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/ui-finish/SKILL.md)), rule, or workflow file.
- [ ] **Integrate**: Update JIT triggers and ensure the new rule is indexed in `.agents/rules/[RULES_INDEX](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[RULES_INDEX.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/RULES_INDEX.md)).md` so future sessions load it automatically. You MUST execute `python .agents/scripts/orion.py orion_ops ingest` to store them back into the `.orion/`.
