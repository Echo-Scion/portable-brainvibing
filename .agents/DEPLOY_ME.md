# 🚀 Agentic Deployment (Plug & Play Across 18 AI Platforms)

This document provides explicit instructions for **any AI Agent** (Antigravity, Claude Code, Cursor, Copilot, Codex, Devin, Gemini CLI, Kimi, Hermes, Muse, Droid, Grok, OpenCode, Pi, Qwen, MiniMax, MiMo, Windsurf, Cline) to deploy and adapt the Foundation into a new project—either using the automated Python engine or via **direct native instruction synthesis** when scripts cannot be executed.

## 🤖 Instructions for the AI Agent

If a user asks you to **"Setup portable-brainvibing"**, **"Deploy the foundation"**, **"Initialize .agents"**, or invokes **`/setup`**, follow this **2-Step Auto-Detected Protocol**:

### Step 1: Run Non-Interactive Diagnostic Inspector (Zero-Guessing)
Do NOT ask the user questions that the script can detect automatically. First, execute the JSON inspector in the terminal:
```bash
python .agents/scripts/orion.py setup --inspect --json
```
This command returns a complete JSON report containing:
- `workspace_mode`: `"foundation_hub"` | `"greenfield"` (empty folder) | `"brownfield"` (existing code)
- `detected_stack`: Auto-detected `framework` and `language`
- `hardware`: CPU cores, System RAM, GPU Name, VRAM in GB
- `ollama_recommendations`: Recommended coder model & embedding model (`nomic-embed-text`) tailored to host hardware tier, plus fitness warnings
- `missing_laptop_deps`: Any missing optional 4-Pillar tools (`rtk`, `ast-grep`, `ollama`, `bun`) and their `install_commands`
- `project_assets_status`: Which `.agents` and `.orion` assets are already present or missing
- `optional_features_catalog`: The 6 Orion power-features available for activation

### Step 2: Present Diagnostic Summary & Ask User Once (Interactive Q&A)
Summarize the JSON findings to the user in a concise block and ask **one interactive confirmation**:
0. **If `workspace_mode == "foundation_hub"`**: Inform the user: *"You are in the Upstream Foundation Hub. Would you like to verify Hub health here, or deploy `.agents` to an external project path on your computer?"*
1. **If `workspace_mode == "greenfield"`** (and stack is `generic`): Ask which stack they want to build with (e.g., Flutter, React/Next.js, Python, Rust/Go).
2. **If `missing_laptop_deps` is non-empty**: Mention which optional laptop tools are missing and ask if they want to auto-install them (`--install-deps`).
3. **If Ollama models are missing or sub-optimal**: Suggest pulling the hardware-recommended model (`--pull-models` or `ollama pull <model>`).
4. **Showcase the 6 Optional Orion Power-Features** and ask which ones they want to enable alongside the core deployment:
   - `1. graph-db` *(Recommended)*: Orion Local SQLite WAL GraphRAG & Omni-Buffer (`context.json`)
   - `2. second-brain` *(Recommended)*: Orion 4-Note Architecture & PageRank God-Nodes Briefing (`.orion/working/brain/`)
   - `3. vault`: Orion Interactive Obsidian Knowledge Vault (`.orion/export/vault/`)
   - `4. design-md`: `DESIGN.md` Visual & Aesthetic Token System Contract (60:30:10 & WCAG 2.1 AA)
   - `5. security-baseline`: Polyglot AST & Secret Security Baseline (`.agents/.security-baseline.json`)
   - `6. pack-hybrid`: Multi-Model Context Audit Bundles (`<=10` `.md` files in `.orion/bundles/hybrid/`)

### Step 3: Execute One-Line Unattended Setup
Once the user replies (or if the user says *"Setup everything / recommended"*), run the unified pipeline:
```bash
# Recommended Default (GraphRAG + Second Brain):
python .agents/scripts/orion.py setup --yes --target . --enable graph-db,second-brain

# Or with Obsidian Vault, DESIGN.md, and Security Baseline enabled:
python .agents/scripts/orion.py setup --yes --target . --enable graph-db,second-brain,vault,design-md,security-baseline

# Or enable ALL Orion features at once:
python .agents/scripts/orion.py setup --yes --target . --enable all

# Direct foundation deploy CLI command:
python .agents/scripts/orion.py foundation deploy --target /path/to/project
```

---

---

### 3.1. Universal 19-Platform Manifest & Discovery Matrix

Each AI coding environment has its native discovery mechanism. The Foundation supports all 19 platforms cleanly using lightweight manifests (`< 10` lines) and declarative instructions:

| # | Platform / IDE | Instruction Path | Plugin Manifest (< 10 lines) | Session Hook Dispatch |
|---|---|---|---|---|
| 1 | **Google Antigravity** | `GEMINI.md` / `AGENTS.md` | `.antigravity-plugin/plugin.json` | `.gemini/settings.json` (`SessionStart`) |
| 2 | **Android Studio (Gemini)** | `GEMINI.md` | `.idea/gemini.json` | Studio Bot session wake |
| 3 | **VS Code / Copilot** | `AGENTS.md` / `.github/copilot-instructions.md` | `.copilot-plugin/plugin.json` | Project launch |
| 4 | **Claude Code** | `CLAUDE.md` / `AGENTS.md` | `.claude-plugin/plugin.json` | `.claude/settings.json` (`SessionStart`) |
| 5 | **Cursor** | `.cursor/rules/portable-brainvibing.mdc` | `.cursor-plugin/plugin.json` | `.cursor/hooks.json` (`sessionStart`) |
| 6 | **OpenAI Codex App** | `AGENTS.md` | `.codex-plugin/plugin.json` | App session load |
| 7 | **OpenAI Codex CLI** | `AGENTS.md` | `.codex-plugin/plugin.json` | CLI wake trigger |
| 8 | **Devin CLI** | `AGENTS.md` | `.devin-plugin/plugin.json` | Devin environment boot |
| 9 | **Gemini CLI** | `GEMINI.md` | `gemini-extension.json` | Extension start |
| 10 | **Kimi Code** | `AGENTS.md` | `.kimi-plugin/plugin.json` | Kimi agent start |
| 11 | **Hermes Agent** | `AGENTS.md` | `.hermes-plugin/plugin.yaml` | Agent session start |
| 12 | **Muse Coding Agent** | `AGENTS.md` | `.muse-plugin/plugin.json` | Workspace init |
| 13 | **Factory Droid** | `AGENTS.md` | `.droid-plugin/plugin.json` | Droid runner start |
| 14 | **Grok Build CLI** | `AGENTS.md` | `.grok-plugin/plugin.json` | Grok pipeline start |
| 15 | **OpenCode** | `AGENTS.md` | `.opencode/INSTALL.md` | Local agent runtime |
| 16 | **Pi Coding Agent** | `AGENTS.md` | `.pi-plugin/plugin.json` | Interface bootstrap |
| 17 | **Qwen Code** | `AGENTS.md` | `.qwen-plugin/plugin.json` | Qwen CLI wake |
| 18 | **MiniMax** | `MINIMAX.md` / `AGENTS.md` | `.minimax-plugin/plugin.json` | Session wake |
| 19 | **Xiaomi MiMo** | `MIMO.md` / `AGENTS.md` | `.mimo-plugin/plugin.json` | Session wake |

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
  "version": "0.0.2",
  "description": "Turnkey Auto-Vibe Coding Brain Ecosystem",
  "skills": ".agents/skills"
}
```
*(For Gemini CLI, use `"contextFileName": "AGENTS.md"` in `gemini-extension.json`. For Hermes, use `.hermes-plugin/plugin.yaml` with `skills_dir: .agents/skills`.)*

#### Step 3: Wire Session-Start Hook
If the platform supports automated session hooks:
- **Antigravity / Gemini CLI**: Create `.gemini/settings.json`:
  ```json
  {
    "hooks": {
      "SessionStart": [{ "type": "command", "command": "python .agents/hooks/pre-agent-wake.py --hook" }]
    }
  }
  ```
- **Claude Code**: Create `.claude/settings.json` with the identical `SessionStart` payload.
- **Cursor**: Create `.cursor/hooks.json` with `{"version": 1, "hooks": {"sessionStart": [{"command": "python .agents/hooks/pre-agent-wake.py --hook"}]}}`.
- **Pure Shell**: Call `.agents/hooks/run-hook.cmd` (Windows) or `.agents/hooks/run-hook.sh` (macOS/Linux) on session start.

#### Step 4: Seed Omni-Buffer & Context
Ensure `.orion/working/context.json` exists in target project to prevent amnesia:
```json
{
  "timestamp_ms": 0,
  "active_file": "",
  "terminal_error": "",
  "user_intent": "",
  "evolution_overdue": false,
  "unprocessed_learnings": 0,
  "drift_warnings": [],
  "pending_cloud_handoffs": [],
  "matched_skills": [],
  "harness_skill_index": "",
  "harness_lifecycle": null
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
> **Version**: 0.0.2 (Script-Enforced Gateway & AI Direct Instruction Protocol)  
> All 18 AI coding platforms are supported natively with zero lock-in, zero cloud daemons, and zero pip dependencies.
