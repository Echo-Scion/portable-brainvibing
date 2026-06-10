# Workspace Rules & Mandates: {project_name}

> **v0.0.1 Core Router (Slim & Pragmatic)**: This is the entry point for the `_foundation` ecosystem. It relies on the Graceful Fallback strategy to maximize context window efficiency.

## 1. MANDATORY: The Core Guardrails
Before writing any code or making structural changes, you MUST read `.agents/rules/core-guardrails.md` using the `view_file` tool.
*Note: This is the ONLY mandatory read.*

## 2. THE GRACEFUL FALLBACK LAW (Zero-Crash Policy)
The `.agents` ecosystem uses advanced tools (RTK, Orion, Python scripts, Ollama). However, **you must never crash or halt if a prerequisite tool is missing.**

If an advanced tool fails (e.g., `command not found`, `ModuleNotFoundError`, connection refused):
1. **DO NOT PANIC or declare a fatal error.**
2. **IMMEDIATELY** switch to your native IDE fallback tools (`grep_search`, `view_file`, `list_dir`).
3. See `.agents/rules/prerequisites.md` for the explicit mapping of fallbacks.
4. **Prioritize Native MCP**: Always use MCP Server tools (e.g., `orion-brain` tools like `orion_ingest`) instead of executing raw terminal scripts when available.

## 3. CONTEXT ECONOMY
- **Do not output bureaucratic footers** (like `🚦 CHECKPOINT`) unless explicitly requested. Just do the work and provide a brief status summary.
- **Caveman Mode**: Default to Caveman Mode (ultra-compressed, terse English) to save tokens, unless explaining complex architecture.

## 4. KNOWLEDGE ROUTING (Opt-in, NOT Mandatory)
Do NOT automatically read 10 different files based on user keywords.
Instead, use your judgment. If you are lacking context on a specific domain (e.g., how to build a Flutter UI, how to write tests here), read the master index first:
**`.agents/rules/RULES_INDEX.md`** or **`.agents/AGENTS_INDEX.md`**

## 5. CIRCUIT BREAKER
If you fail the same operation 3 times, ABORT immediately and ask the user for help.

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->
