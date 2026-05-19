# Metrics Overview

The `metrics/` directory tracks the health, performance, and evolution of the agentic foundation.

## 1. Purpose
Metrics provide quantitative data to the `@skills/integrity-sentinel` skill, allowing for data-driven refinements.

## 2. Key Metrics
- **Context Density**: Tracks token usage across different model tiers (e.g., Premium vs Budget, Opus vs Flash).
- **Execution Velocity**: Average time taken for `/project-init` or `/strict-tdd`.
- **Logic Drift**: Qualitative score of how well agents adhere to `rules/` during complex tasks.
- **Success Rate**: Ratio of completed vs. aborted workflows.

## 3. Data Storage
Metrics are stored as `.json` or `.csv` files within this directory. They are periodically harvested by the `agent-evolution` engine to update the global behavioral rules.