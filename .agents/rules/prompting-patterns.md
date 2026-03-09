---
description: Advanced prompting patterns for sub-agent orchestration and determinism.
activation: agent_delegation

version: 0.0.1
last_updated: 2026-09-26
---
# Advanced Prompting Patterns (For Sub-Agent Orchestration)
When delegating to sub-agents or creating internal prompts, follow these patterns:

## Core Reasoning Patterns
- **Anchor Pattern**: Start complex sub-tasks with a single sentence defining the exact output format.
- **Constraint Stack**: Structure internal prompts as: Ask → Constraints → Context.
- **Persona Boundary**: Define not just who the agent is, but what it MUST NOT do (e.g., "You are a Security Auditor. You do not offer 'quick fixes' that bypass RLS").
- **Failure Injection**: Provide a negative example of a "bad" response to reduce generic outputs.
- **Confidence Gate**: Explicitly state: "Do not include any claim you cannot support with specific reasoning or codebase evidence."
- **Step Separator**: For multi-phase migrations, use hard stops: "Complete step 1. Stop. Wait for verification. Then proceed."
- **Reframe Test**: For controversial architecture choices, force the agent to argue the opposite position with equal conviction before deciding.

## Modern Agent Tooling Patterns (MCP & Computer-Use)
- **MCP Resource Linking**: When invoking an MCP server, explicitly require the agent to `view_file` the MCP's `instructions.md` before execution. Never guess tool parameters.
- **Subagent State Passing**: When chaining sub-agents, pass context via discrete Artifacts (`.md` files) or conversational transcripts rather than huge prompt strings.
- **Computer-Use Verification (Browser/Desktop)**: If delegating to a `browser_subagent`, require it to take a screenshot OR extract specific DOM selectors before returning. Never accept "task completed" without visual/DOM evidence.
- **Async Polling Protocol**: For long-running `run_command` tasks, explicitly forbid tight-polling. Instruct the agent to use `schedule` or rely on the system's reactive wakeup.
