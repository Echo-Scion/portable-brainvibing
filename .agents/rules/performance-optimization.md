---
trigger: model_decision
description: Guidelines for optimizing application performance and context token usage.
---

# Performance & LLM Model Tiers (The Lean Protocol)

## 1. The Lean Protocol (Efficiency Standards)
- **Zero-Theater Policy**: For routine tasks (boilerplate, styling, fixes), skip long narrative explanations. Perform `replace` or `write_file` as soon as the strategy is understood.
- **Dynamic Context Ingestion (QMD-First)**:
    - **L0 (Semantic Index)**: ALWAYS use QMD (`npx @tobilu/qmd query`) first to semantically map dependencies and find relevant files instead of relying on outdated manual catalogs (`catalog.json` or `workspace_map.md`).
    - **L1 (Surgical Read)**: Use `grep_search` with `context: 5` to read ONLY the relevant code block. Avoid full file reads unless refactoring the entire file.
- **Command Output Optimization (The RTK Mandate)**:
    - **Rule**: You MUST use the `rtk` proxy when executing shell commands (e.g., `rtk git status`, `rtk cargo build`, `rtk npm test`).
    - **Why**: RTK (Rust Token Killer) filters, groups, and truncates massive CLI outputs, saving 60-90% of tokens and keeping the context window clean. Never execute raw builds/tests without it if `rtk` is available.
- **Turn Minimization**: Prioritize parallel tool calls. Aim for **"One-Turn Execution"** for simple and clear directives.

## 2. LLM Model Tiers (Experimental Routing)
Optimizing cost and speed without sacrificing quality:
- **Budget (Atomic/Stylistic)**: Single-file fixes, docs, formatting, basic boilerplate. Apply Micro-Harness Protocol. Max 1 file read. No Sequential Thinking.
- **Standard (Integrative/Feature)**: Multi-file features, state management, registry maintenance. Adversarial Twin validation mandatory before marking done.
- **Premium (Architectural/Risky)**: Refactors, security audits, RLS. Full Sequential Thinking (≥3 steps) mandatory.

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
