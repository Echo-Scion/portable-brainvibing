---
description: Unified initialization for both Root and Sub-projects (Canon). Includes Auto-Population Intake Gate.
---

# Workflow: Project Initialization (`/project-init`)

Follow these steps exactly when creating a new project or scaffolding a new major feature directory.

## 1. Requirements Intake
Read the user's prompt. If it is vague, do NOT guess.
- **Command**: Output the prompt: *"Please provide the core functionality, target audience, and primary platform."*

## 2. Generate Context
Create the foundational knowledge file for the AI.

- **Action**: Generate `CONTEXT.md` using the template.

## 3. Scaffold Architecture
Generate the directory structure and base files.
- **Command**: `view_file .agents/skills/project-architect/SKILL.md`
- **Action**: Generate the structural blueprint and execute it using `run_command` (e.g. `mkdir -p src/features/auth/presentation`).

## 4. Install Infrastructure Tooling
Set up the mechanical verifiers.
- **Action**: Run `python .agents/scripts/verify_agents.py` to ensure the ecosystem is intact in the new directory.

## 5. First-Pass Semantic Indexing
Ensure the new project is searchable.
- **Command**: Trigger the `@index-project` skill or run `python .agents/scripts/index_project.py` (if available).

## 6. Bootstrap LLM Wiki (Optional)
- **Command**: `python .agents/scripts/bootstrap_wiki.py`
- **Action**: Scaffolds `.wiki/` + scans all layers into `_manifest.json`
- **Note**: Does NOT auto-ingest. User triggers `/wiki-ingest` when ready.