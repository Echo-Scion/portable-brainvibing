---
description: Mandatory pre-flight search protocol using QMD to retrieve historical context and architectural documentation.
activation: always on
---
# QMD Search Protocol (The Context Locator)

## 1. Mandatory Knowledge Base Consultation

Before initiating ANY `STANDARD` or `PREMIUM` tier task that involves new feature development, significant refactoring, or architectural decisions, the agent **MUST** perform a QMD search.

**Trigger Conditions:**
- The task involves adding a new system component.
- The user asks an architectural or domain-specific question.
- The agent encounters unfamiliar terminology, patterns, or abstractions specific to this project.
- The task requires context from past meetings, PRDs, or historical decision records.

## 2. Execution Standards (Windows Compatibility)

> **CRITICAL WINDOWS EXECUTION RULE**: Due to an ABI/shell compatibility issue on this Windows machine, the agent **MUST NEVER** call `qmd` directly via the shell. 

Instead, the agent **MUST ALWAYS** invoke QMD using NPX:
```bash
npx @tobilu/qmd query "your search query"
npx @tobilu/qmd get "#docid"
```

## 3. The "Search First, Ask Later" Mandate

If an agent is missing context or unsure about a project-specific implementation detail:
1. **First**, formulate a `vec` (semantic) or `lex` (keyword) query using `npx @tobilu/qmd query "..."`.
2. **Second**, read the returned snippets or full documents.
3. **Only if** the QMD search returns no relevant results should the agent pause and ask the user for clarification. 

Do not guess project-specific business logic or architectural decisions without consulting the QMD index first.