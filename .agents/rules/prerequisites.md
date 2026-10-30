---
description: Mandatory and optional prerequisites.md for the agent ecosystem and their explicit fallback strategies.
activation: when a tool or command fails
version: 0.0.3
---

# 🛠️ Prerequisites & Graceful Fallbacks

To maintain a "plug and play" environment while avoiding brittle failures, this ecosystem relies on Graceful Fallbacks. If an advanced tool is unavailable on the host machine, the AI **MUST** gracefully degrade to native tools without halting.

## 1. Pillar 1: Python 3.10+ Stdlib (Orion Brain & Graph Engine)
- **Role**: Primary orchestration layer, knowledge graph indexing, SQLite3 FTS5 BM25 search, state machine management, and DevSecOps verification.
- **Prerequisite**: Python 3.10+ runtime installed on host machine. Zero-Pip Mandate enforced (no external heavy pip dependencies).
- **Fallback Chain**:
  1. **Primary**: Use local python CLI: `python .agents/scripts/orion.py <command>`.
  2. **Fallback**: If Python environment is degraded, use native `grep_search` on `.orion/` or `.agents/` directories to locate context manually.

## 2. Pillar 2: Cargo Rust Systems Engine (`rtk` + `ast-grep`)
- **Role**: Sub-millisecond terminal output compression (`rtk`) and polyglot Concrete Syntax Tree (CST) structural AST analysis (`ast-grep` / `sg`).
- **Prerequisites**: Installed globally via cargo (`cargo install ast-grep --locked`) or standalone precompiled binaries in system PATH.
- **Fallback Chain**:
  - If `rtk` is missing or fails: Degrade immediately to native `view_file` with targeted line ranges or `grep_search` without output compression.
  - If `ast-grep` is missing: Degrade to Python standard library `ast` for Python files, and regex-based AST signature extraction in `scanner.py` for Dart/TypeScript/Kotlin/Rust.

## 3. Pillar 3: Ollama Local Neural Coprocessor
- **Role**: Local zero-cloud vector embeddings (`nomic-embed-text`) and heuristic SLM evaluation (`127.0.0.1:11434`).
- **Prerequisite**: Local Ollama daemon running on port 11434.
- **Hardware Architecture Note**: Consumer GPU Ollama endpoints operate on single-stream FIFO queues ($N_{\text{parallel}}=1$). Parallel subagents serialize into sequential turns unless backed by CUDA continuous in-flight batching with shared prefix caching (vLLM / SGLang / TensorRT-LLM).
- **Fallback Chain**:
  - If Ollama service is offline or unreachable:
    - Automatically degrade to pure SQLite3 FTS5 BM25 lexical search inside `.orion/orion.db`.
    - Rely on native heuristic scanners and static AST parsers in `orion.py`. Zero disruption to coding workflow.

## 4. Pillar 4: Bun Static Runtime Engine (`bun` / `bun.exe`)
- **Role**: Zero-compile direct execution of TypeScript/JSX, zero-install Model Context Protocol (MCP) server launching via `bun x -y <package>`, microsecond test execution (<4ms `bun test`) for mutation testing, and headless UI verification.
- **Prerequisite**: Standalone static binary in PATH, `~/.bun/bin`, or `.agents/bin/bun.exe`. Zero global daemons, zero in-repo `node_modules`.
- **Fallback Chain**:
  - If Bun binary is absent:
    - MCP server runner degrades to system `npx` or pure Python stdio stdlib bridge (`core/capabilities.py`).
    - Test execution falls back to host test runner (`pytest` or language test runner).
    - UI verification falls back to static AST pattern scanning.

## 5. Subagent Orchestration
- **Role**: Spawning isolated sub-agents via `invoke_subagent` or MCP tools.
- **Execution Invariant**: Use subagents strictly for **Context-Isolating Scouts** with $<10\%$ context overlap. Do not fracture interdependent code construction tasks ($\ge 20\%$ shared context) across subagents.
- **Fallback**: If `invoke_subagent` is unavailable in the active runtime, execute tasks sequentially in the main thread with continuous execution and surgical file reads.

## 6. Shared Runtime Contract
- Graph, memory, state checkpoints, and telemetry share `.orion/orion.db` by default.
- Explicit database paths remain supported for isolated tests and integrations.
- Optional pillar availability is reported by `probe_capabilities`; fallback providers must be explicit and observable.
- Subprocess adapters use argv lists with `shell=False` and never interpret shell operators from command input.
