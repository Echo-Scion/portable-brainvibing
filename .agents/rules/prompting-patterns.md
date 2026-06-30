---
description: Advanced prompting patterns for sub-agent orchestration and determinism.
activation: agent_delegation

version: 0.0.1
last_updated: 2026-06-30
---
# Advanced Prompting Patterns (For Sub-Agent Orchestration)
When delegating to sub-agents or creating internal prompts, follow these patterns:
- **Anchor Pattern (Pattern 1)**: Start complex sub-tasks with a single sentence defining the exact output format.
- **Constraint Stack (Pattern 2)**: Structure internal prompts as: Ask → Constraints → Context.
- **Persona Boundary (Pattern 3)**: Define not just who the agent is, but what it MUST NOT do (e.g., "You are a Security Auditor. You do not offer 'quick fixes' that bypass RLS").
- **Failure Injection (Pattern 4)**: Provide a negative example of a "bad" response to reduce generic outputs.
- **Confidence Gate (Pattern 5)**: Explicitly state: "Do not include any claim you cannot support with specific reasoning or codebase evidence."
- **Step Separator (Pattern 6)**: For multi-phase migrations, use hard stops: "Complete step 1. Stop. Wait for verification. Then proceed."
- **Reframe Test (Pattern 9)**: For controversial architecture choices, force the agent to argue the opposite position with equal conviction before deciding.
