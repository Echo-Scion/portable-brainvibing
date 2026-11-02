---
description: Mandatory and optional prerequisites for the agent ecosystem and their explicit fallback strategies.
activation: when a tool or command fails
version: 0.0.5
---

# 🛠️ Prerequisites & Graceful Fallbacks

To maintain a "plug and play" environment while avoiding brittle failures, this ecosystem relies on Graceful Fallbacks. If an advanced tool is unavailable on the host machine, the AI **MUST** gracefully degrade to native tools without halting.

## 1. Pillar 1: Python 3.10+ Stdlib (Orion Brain & Graph Engine)
- **Role**: Primary orchestration layer, knowledge graph indexing, SQLite3 FTS5 BM25 search, state machine management, and DevSecOps verification.
- **Prerequisite**: Python 3.10+ runtime installed on host machine. Zero-Pip Mandate enforced (no external heavy pip dependencies).
- **Fallback Chain**:
  1. **Primary**: Use local python CLI: `python .agents/scripts/orion.py <command>`.
  2. **Fallback**: If Python environment is degraded, use native `grep_search` on `.orion/` or `.agents/` directories to locate context manually.

## 2. Pillar 2: Cargo Rust Systems Engine & Ephemeral Binaries (`rtk` + `ast-grep`)
- **Role**: Sub-millisecond terminal output compression (`rtk`), polyglot Concrete Syntax Tree (CST) structural AST analysis (`ast-grep` / `sg`), syntax diffing (`difftastic`), secret detection (`gitleaks`), and atomic snapshotting (`jujutsu`).
- **Prerequisites**: Installed globally via cargo (`cargo install ast-grep --locked`, `cargo install --git https://github.com/rtk-ai/rtk`) or standalone precompiled binaries in system PATH.
- **Fallback Chain**:
  - **`rtk`**: Degrade immediately to native `view_file` / `read_file` with targeted line ranges or `grep` without output compression.
  - **`ast-grep` (`sg`)**: Degrade to Python standard library `ast` for Python files, and regex-based AST signature extraction in `core/scanner.py` for Dart/TypeScript/Kotlin/Rust.
  - **`difftastic` (`difft`)**: Degrade to Python standard library `difflib.unified_diff`.
  - **`gitleaks`**: Degrade to pure-Python regex & Shannon Entropy ($H(X) > 4.3$) secret scrubber (`core/scanner.py`).
  - **`jujutsu` (`jj`)**: Degrade to non-destructive atomic `git stash create` snapshots (`commands/foundation.py`).

## 3. Pillar 3: Local Neural Coprocessor (Ollama / llama.cpp / OpenAI-Compatible)
- **Role**: Local zero-cloud vector embeddings (`nomic-embed-text`) and heuristic SLM evaluation (`qwen2.5-coder:1.5b` or `3b`).
- **Supported Runtimes**:
  - Local Ollama daemon running on `127.0.0.1:11434`.
  - Standalone `llama.cpp` (`llama-server`) on `127.0.0.1:8080` (placed in PATH or `.agents/bin/`).
  - OpenAI-compatible endpoints (LM Studio, vLLM, LocalAI) on `127.0.0.1:1234` or `:8000`.
- **Hardware Architecture Note**: Consumer GPU endpoints operate on single-stream FIFO queues ($N_{\text{parallel}}=1$). Parallel subagents serialize into sequential turns unless backed by CUDA continuous in-flight batching with shared prefix caching (vLLM / SGLang / TensorRT-LLM).
- **Fallback Chain**:
  - If local AI services are offline or unreachable:
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

## 5. Tier 2: Optional Ephemeral Accelerators (Isolated User Cache & PATH)
- **Role**: High-performance execution acceleration (vector KNN, BPE token counting, fast serialization, fuzzy matching, and deep polyglot CST parsing).
- **Runtime Isolation**: Resides strictly in isolated user cache (`~/.agents/cache/venv` or `AGENTS_ACCELERATORS_VENV`). Never committed to project repositories or injected into application virtualenvs. Dynamically bootstrapped via `core/accelerators.py`.
- **Fallback Chain (Zero-Pip Baseline Guarantee)**:
  - **`sqlite-vec`**: Degrade to pure-Python float32 cosine similarity calculations (`core/db.py`).
  - **`model2vec`**: Degrade to Ollama `nomic-embed-text` or SQLite3 FTS5 lexical matching.
  - **`tokenizers`**: Degrade to standard heuristic ratio estimation (`chars / 3.8`).
  - **`duckdb`**: Degrade to streaming pure-Python `.jsonl` parser (`core/db.py`).
  - **`orjson`**: Degrade to Python standard library `json`.
  - **`rapidfuzz`**: Degrade to Python standard library `difflib`.
  - **`tree-sitter`**: Degrade to Python standard library `ast` and regex scanner.

## 6. Subagent Orchestration
- **Role**: Spawning isolated sub-agents via `invoke_subagent` or MCP tools.
- **Execution Invariant**: Use subagents strictly for **Context-Isolating Scouts** with $<10\%$ context overlap. Do not fracture interdependent code construction tasks ($\ge 20\%$ shared context) across subagents.
- **Fallback**: If `invoke_subagent` is unavailable in the active runtime, execute tasks sequentially in the main thread with continuous execution and surgical file reads.

## 7. Shared Runtime Contract
- Graph, memory, state checkpoints, and telemetry share `.orion/orion.db` by default.
- Explicit database paths remain supported for isolated tests and integrations.
- Optional pillar availability is reported by `probe_capabilities`; fallback providers must be explicit and observable.
- Subprocess adapters use argv lists with `shell=False` and never interpret shell operators from command input.
