# 🚀 Agentic Deployment (Plug & Play)

This file allows any AI Agent (like Gemini CLI, GitHub Copilot, Cursor, Windsurf, Cline, or Claude) to deploy the Foundation to a new project **using the automated Python engine**.

## 🤖 Instructions for the AI Agent

If a user asks you to "Deploy the foundation" or "Initialize the agents" in a new project, follow these steps strictly:

### 1. Identify Target & Stack (Interactive Step)
Confirm the target directory (usually the current working directory `.`). Identify the project name from the folder name (e.g., `my_app` from path `/Users/USER/Projects/my_app`).

> [!IMPORTANT]
> **MANDATORY Q&A**: If the target project does not already have an `.agents/.project_manifest.json` file, you MUST pause and ask the user two questions before proceeding:
> 1. "What framework or ecosystem are we building in? (e.g., react, flutter, nextjs, python)"
> 2. "What is the primary language? (e.g., typescript, dart, python)"
> Do not guess. You need these answers for the `--framework` and `--language` CLI arguments below.

### 2. Gitignore Pre-flight (Dynamic Generation)
Check if the target project has a `.gitignore` file. If it does NOT, you MUST proactively generate a standard `.gitignore` appropriate for the project's framework (using your internal LLM knowledge) BEFORE running any deployment commands. This guarantees Orion skips build artifacts during auto-ingest.

### 3. Execution (The Engine)
Do not attempt to create symlinks, files, or merge rules manually. Use your terminal tool to trigger the Python engine:

**Default (Gemini Only)**
```bash
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework <framework> --language <language>
```

**Selective AIs (e.g., Cursor, Copilot)**
```bash
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework <framework> --language <language> --ai cursor,copilot
```

**Deploy All 6 Supported AIs**
```bash
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework <framework> --language <language> --ai all
```

*(This script automatically handles Symlinking, Smart Merging `AGENTS.md`, and path marker tracking).*

### 3.5. Manual Fallback (Emergency Only)
If the deployment engine fails due to severe OS/permissions restrictions (e.g., symlinks blocked by Windows UAC or Docker), perform these 3 manual steps:
1. Copy the entire `.agents/` directory into the target project root.
2. Manually copy `.agents/templates/AGENTS.template.md` to `GEMINI.md` and `CLAUDE.md` in the target project root, replacing `{project_name}` with the actual name.
3. Run the Safe Auto-Ingest command shown in Step 5 below.

### 4. Seed Collective Memory
Create a persistent post-mortem tracker in the target project.
```markdown
# Persistent Learnings & Post-Mortems

This file serves as the collective memory for AI agents working in this workspace. 

## 0. Log Template
> **[DATE]** | **[TASK_ID]** | **[TIER]**
> - **Issue**: Brief description of what went wrong.
> - **Root Cause**: The foundational reason for the failure.
> - **Solution**: The specific pattern or fix that worked.
> - **Debt/Warning**: Future considerations or brittle areas discovered.

---
```

### 5. Safe Auto-Ingest
Execute the following to safely index the knowledge base without touching heavy code directories:
```bash
python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/
```

> [!WARNING]
> **ROOT AUTO-INGEST BANNED**: You MUST NEVER run `ingest .` or ingest without arguments during deploy. Repositories with massive build directories will cause root-level auto-ingest to freeze the system or blow up the SQLite database. Only use the targeted Safe Auto-Ingest command above.

---

### 6. Model Context Protocol (MCP) Setup

Orion comes with a zero-dependency local MCP Server. Integrating it allows your IDE (Claude Desktop, Cursor, Antigravity) to natively call Orion Graph tools via JSON-RPC instead of typing shell commands.

> [!WARNING]
> **IDE PERMISSION BLOCKER**: AI Agents (like Copilot, Cursor, Antigravity) are generally **BLOCKED** from writing or modifying global IDE MCP configuration files for security reasons. 
> 
> **MANDATORY AI ACTION**: When deploying, you (the AI) MUST explicitly remind the user to install the MCP server manually. Provide them with the JSON snippet below. Do NOT attempt to auto-edit their `claude_desktop_config.json` or `mcp.json`.

**Manual Setup (Provide this to the User):**
Instruct the user to add this to their `claude_desktop_config.json` or IDE MCP settings:
```json
"mcpServers": {
  "orion-brain": {
    "command": "python",
    "args": [
      "${workspaceFolder}/.agents/scripts/orion_mcp.py"
    ]
  }
}
```

---

## 🔄 Syncing & Management (For Humans/AIs)

**Sync After Foundation Updates:**
```bash
python .agents/scripts/orion.py foundation sync-ai --target /path/to/project
```

**Push Project Improvements Upstream:**
```bash
python .agents/scripts/orion.py foundation push-upstream --source /path/to/project
```

---
> [!NOTE]
> **Version**: 2.5.0 (Script-Enforced Gateway)  
> This deployment protocol delegates 100% of physical file orchestration to `orion.py deploy` to prevent LLM token exhaustion and hallucination.
