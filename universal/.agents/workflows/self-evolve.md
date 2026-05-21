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
- [ ] **Update Learnings**: Use `replace` or `write_file` to append the finding to `.agents/LEARNINGS.md` or the appropriate memory file within the current execution turn. Do not wait or queue this action.

## 3. RULE COMPILATION (ANTI-DRIFT)
- [ ] **Evolve Rule**: If a missing or contradictory rule caused the error, you MUST output a JSON block: `{"action": "evolve_rule", "target": ".agents/rules/...", "proposed_addition": "..."}`.
- [ ] **Inject Rule**: Mechanically execute the `replace` tool to inject this new constraint into the target rule file before declaring the task `DONE`.
- [ ] **Verify**: Run `python .agents/scripts/verify_agents.py` to ensure the new rule hasn't broken mechanical integrity.
