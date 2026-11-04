---
description: Formal State Machine execution tracking, checkpointing, and crash recovery protocol.
activation: model_decision
---
# Formal State Machine (FSM) Protocol

> This protocol dictates when and how the AI must use the `orion.py fsm` commands to track execution state. Cyclic graph execution is managed natively by `.agents/scripts/commands/state_machine.py` with superstep execution semantics.

## Why FSM?
Unlike `context.json` which only tracks static file paths, the FSM tracks your **Active Execution Tree**. If your IDE crashes midway through a complex task, this state machine allows you to resume exactly where you left off.
- **Node Execution**: Pure functions mapping `(state) -> state_delta`.
- **Channel Reducers**: Additive, replacement, or set union reducers.
- **Checkpoint Persistence**: Atomic SQLite transaction commits recording `session_id`, `step`, and snapshot payload for interruption recovery.

## Commands Reference
```bash
python .agents/scripts/orion.py fsm init <session_id>
python .agents/scripts/orion.py fsm transition <PHASE>
python .agents/scripts/orion.py fsm task_start <task_id>
python .agents/scripts/orion.py fsm task_end <task_id> <success|failed>
python .agents/scripts/orion.py fsm status
```

## Execution Modes & Protocol Steps

### 1. Interactive IDE Mode (Default)
In interactive environments (Antigravity IDE), execution state is maintained natively via Markdown artifacts (`task.md`, `implementation_plan.md`), subagent message channels, and reactive wakeups.
- Agents are **exempt** from calling repetitive CLI transitions (`fsm init`, `transition EXECUTING`, `task_start`) in routine interactive turns.
- Use native task checkmarks and implementation plans instead of burning CLI roundtrips.

### 2. Headless Daemon & CI Mode (Autonomous Pipelines)
When operating in autonomous background daemons, cron tasks, or headless CI/CD scripts without an interactive IDE:
1. **Starting Execution**: Call `fsm init <session_id>` and `fsm transition EXECUTING`.
2. **Sub-Agent Delegation**: Call `fsm task_start <task_id>` before and `fsm task_end <task_id> <status>` after.
3. **Verifying**: Call `fsm transition VERIFYING` before running automated test gates.
4. **Done**: Call `fsm transition DONE` before session offload.

## Crash Recovery & Rollback Safety
- **Resumption**: If you wake up and find a `recovery_instruction` in your context payload indicating you were interrupted during `EXECUTING`, **DO NOT** restart the task. Check `fsm status` and resume the specific tasks that were running.
- **Rollback Safety**: Transaction failures automatically revert to the previous verified superstep snapshot.

