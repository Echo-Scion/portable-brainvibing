# 🚀 Agentic Deployment (Plug & Play)

This file allows any AI Agent (like Gemini CLI, GitHub Copilot, Cursor, Windsurf, Cline, or Claude) to deploy the Foundation to a new project **without requiring Python or external scripts**.

## 🤖 Instructions for the AI Agent

If a user asks you to "Deploy the foundation" or "Initialize the agents" in a new project, follow these steps using your internal tools:

### 1. Identify Target
Confirm the target directory (usually the current working directory `.`). Identify the project name from the folder name (e.g., `my_app` from path `/Users/USER/Projects/my_app`).

### 2. Create Structure
> [!WARNING]
> **CRITICAL COUPLING**: If you modify the directory list or logic below, you MUST also sync the `FOLDERS_TO_SYNC` list in `.agents/scripts/deploy_foundation.py`!

Ensure the `.agents/` directory structure exists in the target:
- `.agents/skills/`
- `.agents/rules/`
- `.agents/workflows/`
- `.agents/canons/`
- `.agents/templates/`
- `.agents/scripts/`
- `.agents/docs/`
- `.agents/evals/`

### 3. Execution (Terminal First Mode)
[DONT] Do not read and create files one by one (this causes context limit exhaustion).
[DO] Use your terminal tools. 
First Choice: Run `.agents/scripts/deploy_foundation.py` via python.
Fallback Choice: Use native OS shell copy commands:
- Windows (PowerShell): `Copy-Item -Path source\* -Destination target\ -Recurse -Force`
- Mac/Linux: `cp -a source/* target/`
Use agentic one-by-one file writing ONLY as an absolute last resort if terminal execution is completely unavailable.

### 3.5. Seed Collective Memory
```markdown
# Persistent Learnings & Post-Mortems

This file serves as the collective memory for AI agents working in this workspace. It documents systemic failures, complex bug fixes, and architectural "gotchas" to prevent repetition of errors.

## 0. Log Template
> **[DATE]** | **[TASK_ID]** | **[TIER]**
> - **Issue**: Brief description of what went wrong or the complexity faced.
> - **Root Cause**: The foundational reason for the failure.
> - **Solution**: The specific pattern or fix that worked.
> - **Debt/Warning**: Future considerations or brittle areas discovered.

---
```

### 4. Deploy Multi-AI Configurations

**CRITICAL**: The Foundation now supports 6 AI assistants. Deploy configuration files for all relevant AIs.

Available AI Configurations:
- **Gemini** → `GEMINI.md` (root)
- **GitHub Copilot** → `.github/copilot-instructions.md`
- **Cursor** → `.cursorrules` (root)
- **Windsurf** → `.windsurfrules` (root)
- **Cline** → `.clinerules` (root)
- **Claude** → `CLAUDE.md` (root)

#### Smart Merge Logic Per AI

For each AI, follow this merge strategy:

**A. Markdown Format** (Gemini, Copilot, Claude):
1. Read `.agents/templates/AGENTS.template.md` from source
2. Extract the `<!-- START FOUNDATION MANDATES -->...<!-- END FOUNDATION MANDATES -->` block
3. Replace `{project_name}` with actual project name
4. Check if target file exists:
   - **Has markers**: Replace ONLY the foundation block between `<!-- START FOUNDATION MANDATES -->` and `<!-- END FOUNDATION MANDATES -->`, preserve custom content
   - **No markers**: Prepend foundation block, wrap existing content as "PROJECT-SPECIFIC" below it
   - **Doesn't exist**: Create new from template

**B. Rules Format** (Cursor, Windsurf, Cline):
1. Read `.agents/templates/{AI}RULES.template` from source
2. Extract the `# === FOUNDATION RULES START ===...# === END ===` block
3. Replace `{project_name}` with actual project name
4. Same merge logic as markdown, but using rules markers

#### Deployment Checklist

For EACH AI you're deploying:
- [ ] Read appropriate template from `.agents/templates/`
- [ ] Inject project name
- [ ] Create target directory if needed (e.g., `.github/` for Copilot)
- [ ] Smart merge with existing file (if any)
- [ ] Verify markers are present in final file

#### Recommended Deployment Strategy

**Default**: Deploy ALL 6 AI configs to ensure maximum compatibility

**Selective**: If user specifies, deploy only requested AIs:
- User uses VS Code → Deploy `copilot`
- User uses Cursor → Deploy `cursor`
- User uses Gemini CLI → Deploy `gemini`
- Multi-tool team → Deploy all

### 5. Create Path Marker
Write the absolute path of THIS source foundation directory into a file named `.agents/.foundation_path` in the target project. This is critical for enabling the `sync_ai_configs.py` tool.

### 6. Track Deployed AIs
Create `.agents/.deployed_ais` JSON file:
```json
{
  "project_name": "my_project",
  "deployed_ais": ["gemini", "copilot", "cursor"],
  "results": { ... }
}
```

### 7. Validate
Verify ALL deployed AI configs:
- [ ] Each file exists at correct path
- [ ] Each file contains appropriate markers
- [ ] Project name is correctly injected
- [ ] `.foundation_path` exists and points to foundation
- [ ] `.deployed_ais` tracks all deployed configs
- [ ] `python .agents/scripts/verify_agents.py` returns PASS in target project
- [ ] Deployment summary records source version and deployment date

### 8. Compatibility Guard
Before deployment, confirm target environment supports:
- Python 3.10+ for script-based maintenance tooling
- UTF-8 file encoding for markdown and instruction files
- Write access to target root and hidden folders (including `.agents` and `.github`)

If compatibility checks fail, do not deploy partial foundation state.

---

## 🐍 Python Script Deployment (Alternative)

If the AI or user prefers to use the Python script:

### Preflight Check (Recommended)
```bash
python .agents/scripts/preflight_check.py
```

### Deploy All AIs (Default)
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/project
```

### Deploy Specific AI Only
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/project --ai copilot
```

### Deploy Multiple AIs
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/project --ai gemini,copilot,cursor
```

### Preview Changes (Dry Run)
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/project --dry-run
```

### List Available AIs
```bash
python .agents/scripts/deploy_foundation.py --list-ais
```

---

## 🔄 Syncing After Foundation Updates

When the foundation is updated, sync all deployed AI configs:

### Sync All Deployed AIs
```bash
python .agents/scripts/sync_ai_configs.py --target /path/to/project
```

### Sync Specific AIs Only
```bash
python .agents/scripts/sync_ai_configs.py --target /path/to/project --ai gemini,copilot
```

### Preview Sync Changes
```bash
python .agents/scripts/sync_ai_configs.py --target /path/to/project --dry-run
```

---

## 🔼 Reverse Sync (Project to Foundation)

If you modify rules or agents inside a specific project and want to push those improvements back up to the master Foundation:

```bash
python .agents/scripts/sync_to_foundation.py --source /path/to/project
```

---

## 📋 AI Configuration Matrix

| AI Assistant | Config File | Auto-Loaded? | Format |
|--------------|-------------|--------------|--------|
| Gemini CLI | `GEMINI.md` | ✅ Yes (manual) | Markdown |
| GitHub Copilot | `.github/copilot-instructions.md` | ✅ Yes (auto) | Markdown |
| Cursor | `.cursorrules` | ✅ Yes (auto) | Rules |
| Windsurf | `.windsurfrules` | ✅ Yes (auto) | Rules |
| Cline | `.clinerules` | ✅ Yes (auto) | Rules |
| Claude | `CLAUDE.md` | ⚠️ Unofficial | Markdown |

---

> [!TIP]
> **Multi-AI Strategy**: Deploy all configs by default. This ensures the project works seamlessly regardless of which AI assistant team members use. The configs are lightweight and don't conflict.

> [!IMPORTANT]
> **Merge, Never Overwrite**: The Smart Merge strategy ensures a project's custom rules are ALWAYS preserved. The Foundation block is treated as an updateable zone; everything else is inviolable.

> [!NOTE]
> **Version**: 2.4.0 (Multi-AI Gateway)  
> This deployment system supports 6 major AI assistants with consistent foundation mandates across all platforms.

---

*Portable Brainvibing Foundation - Multi-AI Deployment Protocol*