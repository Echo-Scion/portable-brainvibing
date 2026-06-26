---
description: Mandatory and optional prerequisites.md for the agent ecosystem and their explicit fallback strategies.
activation: when a tool or command fails
version: 0.0.1
---

# 🛠️ Prerequisites & Graceful Fallbacks

To maintain a "plug and play" environment while avoiding brittle failures, this ecosystem relies on Graceful Fallbacks. If an advanced tool is unavailable on the host machine, the AI **MUST** gracefully degrade to native tools without halting.

## 1. RTK (Rust Token Killer)
- **Role**: Token-optimized CLI proxy for commands. Used specifically for **AST Hollowing** (`rtk read <file> --level aggressive`) to read large files without burning context.
- **Prerequisite**: Installed globally via cargo or binary.
- **Fallback**: If `rtk` commands fail (e.g., `command not found`), **immediately fallback to native tools**:
  - Instead of `rtk read <file> --level aggressive`, use the native `grep_search` tool to find signatures, or `view_file` with narrow `startLine`/`endLine` parameters.
  - Instead of `rtk grep`, use the native `grep_search` tool.

## 2. Orion (Agent Memory & Brain Graph)
- **Role**: Context syncing and [knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/[knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/knowledge.md)) indexing via the `orion.py` CLI.
- **Prerequisite**: Python environment.
- **Fallback Chain**:
  1. **Primary**: Use the local python bridge: `python .agents/scripts/orion.py`.
  2. **Fallback**: If Python fails entirely, use native `grep_search` on the `.orion/` or `.agents/` directories to find context manually.

## 3. Semantic Search (QMD / Local Rerankers)
- **Role**: Node.js/npx based semantic search or local Ollama instances.
- **Prerequisite**: Node.js, npx, enough GPU VRAM.
- **Fallback**: If an `npx` command or an Ollama request fails (e.g., OOM error, timeout, command not found):
  - **Fallback**: Rely exclusively on `grep_search` and manual file traversal (`list_dir`, `view_file`).

## 4. Subagent Orchestration
- **Role**: Using `invoke_subagent` or similar MCP tools to spawn isolated agents.
- **Fallback**: If the `invoke_subagent` tool is not available in the current IDE environment (like Antigravity), handle the task yourself within the main thread, but aggressively use `grep_search` to keep your context window clean. Do not attempt to call missing tools.
