# How to Create a Workflow

Workflows in the `.agents` foundation are deterministic DAGs (Directed Acyclic Graphs) that guide agents through complex, multi-step processes.

## 1. Directory Structure
All workflows MUST be stored in `.agents/workflows/` as `.md` files.

## 2. File Format
Every workflow file MUST start with a YAML frontmatter:
```yaml
---
description: [short title, e.g. how to deploy the application]
---
```

## 3. Core Principles
- **Atomic Nodes**: Each step should be one logical unit of work.
- **Merge-Back Nodes**: Ensure every branch (e.g., Step 6/7) has a clear path back to the main flow (Step 8).
- **Tool Integration**: Use standard markdown checkboxes `[ ]` for tracking progress.
- **Recursive Logic**: Workflows can reference other workflows using `// workflow:[name]` syntax.

## 4. Automation (Turbo Mode)
- Use `// turbo` above a step involving `run_command` to allow auto-execution.
- Use `// turbo-all` at the top of the file to auto-execute ALL tool calls in the workflow.

## 5. Registration
After creating a new workflow, run `@index-project` to index the new path into the system's brain.
