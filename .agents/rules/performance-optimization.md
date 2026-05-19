---
activation: model_decision
description: Guidelines for optimizing application performance and context token usage.

version: 2.4.0
last_updated: 2026-05-20
---

# Performance & LLM Model Tiers (The Lean Protocol)

## 1. The Lean Protocol (Efficiency Standards)
- **Telegraphic Mandate**: For routine tasks (boilerplate, styling, fixes), skip long narrative explanations. Perform `replace` or `write_file` as soon as the strategy is understood. See `.agents/rules/caveman-activate.md`.
- **Dynamic Context Ingestion (QMD-First)**:
    - **L0 (Semantic Index)**: See `.agents/rules/qmd-search-protocol.md` for mandatory QMD usage.
    - **L1 (Surgical Read)**: Use `grep_search` with `context: 5` to read ONLY the relevant code block. Avoid full file reads unless refactoring the entire file.
- **Command Output Optimization (The RTK Mandate)**:
    - See `.agents/rules/antigravity-rtk-rules.md` for mandatory `rtk` proxy usage.
- **Turn Minimization**: Prioritize parallel tool calls. Aim for **"One-Turn Execution"** for simple and clear directives. (Note: Parallel tool calls are NOT allowed under the BUDGET tier Bento-Box workflow).

## 2. LLM Model Tiers (Experimental Routing)
- See `.agents/rules/tier-execution-protocol.md` for official Tier definitions and routing rules.

## 3. Application Performance
- **Caching**: Use Redis or local caching for frequently accessed, slow-changing data.
- **Lazy Loading**: In Flutter, use `ListView.builder` for long lists.
- **Tree Shaking**: Ensure unused dependencies are removed from production builds.

## 4. Modularization & Context Integrity (Vibecode)
- **Modularity over Line Counts**: Prioritize Single Responsibility Principle (SRP), but respect the AI token window.
- **Vibecode Hard Cap (500 Lines)**: No single file should exceed 500 lines. This is a STRICT architectural boundary to prevent token overflow and context loss.
- **Mandatory Splitting**: If a feature naturally pushes a file past 500 lines, you MUST pause feature development and refactor immediately (extract widgets, helper classes, or state logic to separate files).
- **Optimization**: Extract private widgets, helper classes, or providers into separate files when they represent distinct sub-responsibilities. Use barrel exports (`export 'file.dart';`) to maintain a clean public API.

## 5. Tooling & MCP Awareness
- **Pre-Flight Check**: Verify the status of active MCP servers (Dart, Supabase, GitHub, etc.). If a required server is missing, notify the USER before taking technical action.
## 6. Structural Mapping & Audit
- **Skeleton Map First**: Before beginning broad refactors or when exploring new, unfamiliar directories, you MUST execute `python .agents/scripts/code_map.py --dir <target_directory>`. This generates a lightweight, structural skeleton of classes and functions, saving thousands of tokens compared to reading full files.
- **Ghost Token Defense**: If the AI feels that context is becoming diluted or responses are sluggish, execute `python .agents/scripts/token_audit.py`. This script identifies "ghost tokens" (files exceeding acceptable length limits). Any file flagged by this audit must be slated for immediate modularization to preserve the context window.
