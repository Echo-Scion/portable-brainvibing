---
description: Auto-generated rule for fsm-protocol
activation: always on
---
# Formal State Machine (FSM) Protocol

> This protocol dictates when and how the AI must use the `orion.py fsm` commands to track execution state.

## Why FSM?
Unlike `context.json` which only tracks static file paths, the FSM tracks your **Active Execution Tree**. If your IDE crashes midway through a complex task, this state machine allows you to resume exactly where you left off.

## Commands Reference
```bash
python .agents/scripts/orion.py fsm init <session_id>
python .agents/scripts/orion.py fsm transition <PHASE>
python .agents/scripts/orion.py fsm task_start <task_id>
python .agents/scripts/orion.py fsm task_end <task_id> <success|failed>
python .agents/scripts/orion.py fsm status
```

## Protocol Steps

1. **When Starting Execution**:
   - Immediately after the User approves your Implementation Plan, you MUST call `fsm init` and `fsm transition EXECUTING`.
2. **When Delegating to Sub-Agents**:
   - BEFORE delegating a task to a worker/sub-agent (or kicking off a long-running command), you MUST call `fsm task_start <task_id>`.
   - AFTER the sub-agent returns its result, you MUST call `fsm task_end <task_id> <success|failed>`.
3. **When Verifying**:
   - Before running tests, call `fsm transition VERIFYING`.
4. **When Done**:
   - Before calling `/session-offload`, call `fsm transition DONE` to clear the state and signal successful completion.

## Crash Recovery
If you wake up and find a `recovery_instruction` in your context payload indicating you were interrupted during `EXECUTING`, **DO NOT** restart the task. Check `fsm status` and resume the specific tasks that were running.
