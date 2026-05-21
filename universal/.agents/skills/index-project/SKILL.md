---
name: index-project
description: >
  Automates the indexing of the current project into the QMD semantic search engine.
  Use this when starting a new project or when significant documentation changes have occurred
  that need to be searchable by the AI. Triggered by mentioning @index-project or asking to "index the project".
---

# Index Project Workflow (QMD)

## Purpose

To automatically register the current project directory as a collection in the local QMD (Query Markup Documents) database and generate vector embeddings for all markdown files. This allows the AI agent to use semantic search to find project context.

## Trigger

`/index-project`, `@index-project`, or when the user explicitly asks to "index the project" or "update qmd".

## Process

When this skill is triggered, the agent MUST perform the following steps automatically:

1. **Locate the Script**: Ensure the script `.agents/scripts/setup_qmd.py` exists in the workspace.
2. **Execute the Script**: Run the script using the `run_command` tool.

   ```bash
   python .agents/scripts/setup_qmd.py
   ```

3. **Validation**:
   - Check the output of the command.
   - If successful, it should indicate that the collection was added and embeddings were generated.
   - If it fails (e.g., QMD is not installed globally), inform the user of the error and provide the installation command (`npm install -g @tobilu/qmd`).

4. **Confirmation**: Once complete, briefly notify the user that the project has been successfully indexed and is now semantically searchable by the AI.

## Constraints

- Do not attempt to run the raw `qmd` shell commands (like `qmd collection add .`) directly on Windows, as they will fail due to shell script incompatibility. ALWAYS rely on the Python script (`setup_qmd.py`) which contains the robust workaround for Windows environments.
- This skill assumes the initial 2GB global model download has already been completed by the user. If the script hangs for more than 2 minutes, it is likely doing the initial download. In this rare edge case, you may need to advise the user to run it manually.