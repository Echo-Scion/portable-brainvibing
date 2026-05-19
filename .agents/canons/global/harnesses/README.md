# Code-As-Harness Library

> **Inspiration:** "AutoHarness: improving LLM agents by automatically synthesizing a code harness" (Google DeepMind, 2026)

This directory contains reusable code snippets, unit tests, and programmatic constraints designed to act as **Action-Verifiers** or **Action-Filters** for the agents. 

Rather than relying purely on an agent's internal reasoning (which is prone to "illegal moves" and hallucinations), agents must synthesize and utilize these strict, external code harnesses to validate their actions before execution.

## The AutoHarness Paradigm
1. **Agent Proposes Action**: The agent decides what to do (e.g., generate a block of code, modify a file, run a command).
2. **Harness Verification**: The proposed action is passed through a harness script (`is_legal_action`).
3. **Rejection & Refinement**: If the harness rejects the action, the exact error trace is fed back to the agent. The agent refines its proposal until it achieves a 100% legal action rate.
4. **Execution**: Only upon passing the harness is the action committed to the environment.

## Harness Types
- **Harness-as-Action-Verifier**: A script that intercepts an agent's proposed code/action and validates it strictly against rules, returning `True` or `False` + Error message.
- **Harness-as-Action-Filter**: A script that enumerates valid actions for a given state, narrowing the agent's choices beforehand.
- **Harness-as-Policy**: A purely deterministic script that codifies a fully verified agent policy, removing the need for LLM inference at runtime.

## Files
- [`base_action_verifier.py`](base_action_verifier.py): A boilerplate template for creating a new custom action-verifier. Use this when synthesizing a new harness for a complex task.