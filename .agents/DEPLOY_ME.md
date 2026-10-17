# 🚀 Agentic Deployment (Plug & Play Across 18 AI Platforms)

This document provides explicit instructions for **any AI Agent** (Antigravity, Claude Code, Cursor, Copilot, Codex, Devin, Gemini CLI, Kimi, Hermes, Muse, Droid, Grok, OpenCode, Pi, Qwen, MiniMax, MiMo, Windsurf, Cline) to deploy and adapt the Foundation into a new project—either using the automated Python engine or via **direct native instruction synthesis** when scripts cannot be executed.

## 🤖 Instructions for the AI Agent

If a user asks you to "Deploy the foundation" or "Initialize the agents" in a new project, follow these steps strictly:

### 1. Identify Target & Stack (Interactive Step)
Confirm the target directory (usually the current working directory `.`). Identify the project name from the folder name (e.g., `my_app` from path `/Users/USER/Projects/my_app`).

> [!IMPORTANT]
> **MANDATORY Q&A**: If the target project does not already have an `.agents/.project_manifest.json` file, pause and verify three details with the user before proceeding:
> 1. "What framework or ecosystem are we building in? (e.g., react, flutter, nextjs, python)"
> 2. "What is the primary language? (e.g., typescript, dart, python)"
> 3. "Are you planning to use a Local LLM for this project? If yes, roughly how many parameters does it have? (e.g., 0.5B, 8B, 32B, 70B, or type 'None' if using a Cloud LLM like Antigravity/Claude)"
> Do not guess. You need these answers for the CLI arguments or direct configuration below.

### 2. Gitignore Pre-flight (Dynamic Generation)
Check if the target project has a `.gitignore` file. If it does NOT, generate the repository's standard framework-specific `.gitignore` BEFORE running deployment. Verify that build-artifact patterns are present before auto-ingest.

### 3. Automated Execution (The Python Engine)
When terminal execution is available, trigger the engine via a single zero-dependency command:

**Default (Universal: Auto-detects stack and deploys all supported platform adapters):**
```bash
python .agents/scripts/orion.py foundation deploy --target /path/to/project [--framework <framework> --language <language>] [--use-local-llm --llm-params <params_in_billions>]
```
*(Note: `--framework` and `--language` are optional. If omitted, the engine automatically detects them from project markers like `pubspec.yaml`, `package.json`, `pyproject.toml`, `Cargo.toml`, or `go.mod`.)*

**Selective AIs (e.g., Cursor, Claude, Copilot):**
```bash
python .agents/scripts/orion.py foundation deploy --target /path/to/project --ai cursor,claude,copilot
```

---

### 3.1. Universal 18-Platform Manifest & Discovery Matrix

Each AI coding environment has its native discovery mechanism. The Foundation supports all 18 platforms cleanly using lightweight manifests (`< 10` lines) and declarative instructions:

| # | Platform / IDE | Instruction Path | Plugin Manifest (< 10 lines) | Session Hook Dispatch |
|---|---|---|---|---|
| 1 | **Google Antigravity** | `GEMINI.md` / `AGENTS.md` | `.antigravity-plugin/plugin.json` | `.gemini/settings.json` (`SessionStart`) |
| 2 | **VS Code / Copilot** | `AGENTS.md` / `.github/copilot-instructions.md` | `.copilot-plugin/plugin.json` | Project launch |
| 3 | **Claude Code** | `CLAUDE.md` / `AGENTS.md` | `.claude-plugin/plugin.json` | `.claude/settings.json` (`SessionStart`) |
| 4 | **Cursor** | `.cursor/rules/portable-brainvibing.mdc` | `.cursor-plugin/plugin.json` | `.cursor/hooks.json` (`sessionStart`) |
| 5 | **OpenAI Codex App** | `AGENTS.md` | `.codex-plugin/plugin.json` | App session load |
| 6 | **OpenAI Codex CLI** | `AGENTS.md` | `.codex-plugin/plugin.json` | CLI wake trigger |
| 7 | **Devin CLI** | `AGENTS.md` | `.devin-plugin/plugin.json` | Devin environment boot |
| 8 | **Gemini CLI** | `GEMINI.md` | `gemini-extension.json` | Extension start |
| 9 | **Kimi Code** | `AGENTS.md` | `.kimi-plugin/plugin.json` | Kimi agent start |
| 10 | **Hermes Agent** | `AGENTS.md` | `.hermes-plugin/plugin.yaml` | Agent session start |
| 11 | **Muse Coding Agent** | `AGENTS.md` | `.muse-plugin/plugin.json` | Workspace init |
| 12 | **Factory Droid** | `AGENTS.md` | `.droid-plugin/plugin.json` | Droid runner start |
| 13 | **Grok Build CLI** | `AGENTS.md` | `.grok-plugin/plugin.json` | Grok pipeline start |
| 14 | **OpenCode** | `AGENTS.md` | `.opencode/INSTALL.md` | Local agent runtime |
| 15 | **Pi Coding Agent** | `AGENTS.md` | `.pi-plugin/plugin.json` | Interface bootstrap |
| 16 | **Qwen Code** | `AGENTS.md` | `.qwen-plugin/plugin.json` | Qwen CLI wake |
| 17 | **MiniMax** | `MINIMAX.md` / `AGENTS.md` | `.minimax-plugin/plugin.json` | Session wake |
| 18 | **Xiaomi MiMo** | `MIMO.md` / `AGENTS.md` | `.mimo-plugin/plugin.json` | Session wake |

---

### 3.5. Direct AI Instructions (Scriptless Fallback & Native Synthesis)

When running inside an AI chat without Python execution capabilities (or restricted container/OS permissions), the AI agent must synthesize these files directly:

#### Step 1: Synthesize Instruction File
Read `.agents/templates/AGENTS.template.md`, replace `{project_name}` with the target directory basename, and write to:
- `AGENTS.md` (universal for Copilot, Codex, Devin, Kimi, Hermes, Muse, Droid, Grok, OpenCode, Pi, Qwen).
- `GEMINI.md` (for Antigravity and Gemini CLI).
- `CLAUDE.md` (for Claude Code).
- `.cursor/rules/portable-brainvibing.mdc` (for Cursor).
- `MINIMAX.md` (for MiniMax) or `MIMO.md` (for Xiaomi MiMo).

#### Step 2: Create Lightweight Plugin Manifest (`< 10` lines)
For the active AI platform, create its manifest in the target project root pointing skills to `.agents/skills`:
```json
{
  "name": "portable-brainvibing",
  "version": "1.0.0",
  "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
  "skills": ".agents/skills"
}
```
*(For Gemini CLI, use `"contextFileName": "GEMINI.md"` in `gemini-extension.json`. For Hermes, use `.hermes-plugin/plugin.yaml` with `skills_dir: .agents/skills`.)*

#### Step 3: Wire Session-Start Hook
If the platform supports automated session hooks:
- **Antigravity / Gemini CLI**: Create `.gemini/settings.json`:
  ```json
  {
    "hooks": {
      "SessionStart": [{ "type": "command", "command": "python .agents/hooks/pre-agent-wake.py" }]
    }
  }
  ```
- **Claude Code**: Create `.claude/settings.json` with the identical `SessionStart` payload.
- **Cursor**: Create `.cursor/hooks.json` with `{"version": 1, "hooks": {"sessionStart": [{"command": "python .agents/hooks/pre-agent-wake.py"}]}}`.
- **Pure Shell**: Call `.agents/hooks/run-hook.cmd` (Windows) or `.agents/hooks/run-hook.sh` (macOS/Linux) on session start.

#### Step 4: Seed Omni-Buffer & Context
Ensure `.orion/working/context.json` exists in target project to prevent amnesia:
```json
{
  "active_document": "",
  "cursor_line": "1",
  "evolution_overdue": false,
  "drift_warnings": [],
  "harness_skill_index": {},
  "harness_lifecycle": {},
  "state": "init",
  "memory": []
}
```

---

### 4. Seed Collective Memory
Create a persistent post-mortem tracker in the target project at `LEARNINGS.md`:
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
If terminal execution is permitted, safely index the knowledge base without touching heavy build directories:
```bash
python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons context/
```

> [!WARNING]
> **ROOT AUTO-INGEST BANNED**: NEVER run `ingest .` without arguments during deploy. Build directories (`node_modules`, `build/`, `target/`) will freeze the indexer. Only use the targeted Safe Auto-Ingest command above.

---

## 🔄 Syncing & Upstream Management

**Sync After Foundation Updates:**
```bash
python .agents/scripts/orion.py foundation sync-ai --target /path/to/project
```

**Push Project Improvements Upstream:**
```bash
python .agents/scripts/orion.py foundation push-upstream --source /path/to/project
```

---

### Runtime Contract Invariants

Deployed runtime state defaults to `.orion/orion.db`, including graph, memory,
state checkpoints, and span telemetry. Explicit database paths remain supported
for isolated tests and integrations.

External commands are executed as argv lists with `shell=False`; deployment
never evaluates shell operators from user-provided command text.

Optional RTK, ast-grep, Ollama, and Bun integrations are detected through the
shared `probe_capabilities` contract and report explicit fallback providers
when unavailable.

---
> [!NOTE]
> **Version**: 0.0.1 (Script-Enforced Gateway & AI Direct Instruction Protocol)  
> All 18 AI coding platforms are supported natively with zero lock-in, zero cloud daemons, and zero pip dependencies.
