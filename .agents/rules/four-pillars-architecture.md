---
description: Four (4) Permanently Anchored Pillars and hierarchical graceful degradation protocol.
activation: model_decision
---

# 🏛️ Four (4) Permanently Anchored Pillars & Graceful Fallback Protocol

> **LESSWORD MANDATE**: Absolute architectural specification for sovereign local execution, bridging 57 reference repositories with zero cloud telemetry and zero daemon bloat.

## 1. The Four (4) Anchored Pillars

1. **Pillar 1: Python 3.10+ Standard Library (Cognitive & GraphRAG Orchestrator)**:
   - In-process mathematical execution: PageRank centrality, pure-Python Newman-Girvan Louvain modularity clustering, 3-tier virtual memory (Core, Recall, Archival).
   - SQLite3 with FTS5 Robertson BM25 full-text indexing, WAL journal mode, and atomic synchronization triggers.
   - Zero-Pip Mandate: strictly avoid heavy external packages (no PyTorch, HuggingFace, NetworkX, LangChain).

2. **Pillar 2: Cargo Rust Native Systems Engine (`rtk` + `ast-grep`)**:
   - Zero-daemon standalone compiled binaries:
     - `rtk` (Rust Token Killer): Sub-millisecond terminal stream filtering, ANSI code stripping, context compression by 60–90%.
     - `ast-grep` (`sg`): Polyglot Tree-sitter Concrete Syntax Tree (CST) engine providing structural AST pattern matching and code rewrites across Dart, Kotlin, Java, Rust, and TS.

3. **Pillar 3: Local Neural Coprocessor (Ollama / llama.cpp / OpenAI-Compatible on `127.0.0.1`)**:
   - Local dense embeddings (`nomic-embed-text`) stored as SQLite BLOBs for archival similarity.
   - Local Small Language Model (SLM) for heuristic judging, token perplexity estimation, and pre-evaluations.
   - Multi-Runtime Support: Native Ollama API (:11434) and OpenAI-compatible endpoints (:8080 `llama-server`, :1234 LM Studio, :8000 vLLM).

4. **Pillar 4: Bun Static Runtime Engine (`bun.exe` / `bun`)**:
   - Single standalone static binary (~85 MB) providing zero-compile TypeScript and JSX execution.
   - On-the-fly TypeScript Model Context Protocol (MCP) server execution (`bun x -y @modelcontextprotocol/...`).
   - Microsecond test runner (`bun test`) for polyglot AST mutation cycles (<4ms per run).
   - Headless UI DOM and ARIA contract validation without browser hypervisors.
   - Zero-In-Repo-node_modules: all caching stored in user cache (`~/.bun/install/cache`), keeping workspace pristine.

## 2. Hierarchical Graceful Degradation Protocol (Pure Python Floor)

If Pillars 2, 3, or 4 are absent or offline, execution MUST NOT fail. The engine downshifts automatically:

- **If Pillar 2 (Rust) absent**:
  - `scanner.py` falls back to `ast.parse` for `.py` and polyglot deterministic regex for Dart, Kotlin, Java, TS, and Rust.
  - `commands/compact.py` (`shrink`, via `brain.py`) applies pure-Python regex ANSI stripping and schema collapsing.
- **If Pillar 3 (Ollama) offline**:
  - `assertion_engine.py`, `commands/rag.py`, and `commands/brain.py` fall back to SQLite3 FTS5 Robertson BM25 lexical ranking and pure-Python Jaccard n-gram token similarity.
- **If Pillar 4 (Bun) absent**:
  - `commands/verify_agents.py` (`adversarial`) falls back to host project CLI test runners (`dart test`, `cargo test`, `pytest`).
  - MCP sidecar runners restrict spawning to native Python stdio servers via `core/capabilities.py`.
  - UI checks fall back to static AST token matrices and CSS contrast evaluators.

## 3. Operational Guarantees
- Zero background daemons running persistently.
- Complete air-gapped data sovereignty: zero external cloud telemetry.
- Exit Code 0 with evidence mandate enforced across all execution tiers.
