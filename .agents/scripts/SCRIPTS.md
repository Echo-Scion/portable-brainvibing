# 🚀 Scripts & Automation Index

This directory contains the central engine and automation scripts for the **Portable Brainvibing** infrastructure.

## Modular CLI: `orion.py`

This framework uses a **Unified Zero-Pip Modular CLI** architecture. Instead of calling fragmented scripts directly, invoke the centralized entrypoint:

```bash
python .agents/scripts/orion.py <command> [args...]
```

### 1. Knowledge Base & Hybrid RAG (Brain Graph)
| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `brain sync "<intent>"` | Hierarchical hybrid RAG (FTS5 + vectors + 1-hop graph + Louvain macro-clusters). | `commands/rag.py` (via `commands/brain.py`) |
| `context "<intent>"` | Orion-powered unified RAG context retrieval (alias of brain sync). | `commands/rag.py` (via `commands/brain.py`) |
| `ingest <paths...>` | Ingests files and structural code triplets into brain graph. | `commands/brain.py` |
| `gc` / `clean` | Garbage collects orphaned caches, stale test backups, loose vault mirrors, and vacuums SQLite orion.db. | `commands/brain.py` |
| `brain export-vault` | Generates the Obsidian-compatible graph projection under `.orion/vault/` without modifying authored `context/` or `.agents/` sources. | `commands/vault.py` (via `commands/brain.py`) |
| `orion_ops init` | Initializes `.orion/` database and companion schemas. | `commands/brain.py` |
| `orion_ops ingest` | Ingests rules, configs, and triplets into the `.orion/` knowledge store. | `commands/brain.py` |
| `orion_ops resolve <query>`| Resolves wikilink nodes and returns graph neighborhood context. | `commands/brain.py` |
| `graph <action>` | Direct interface to Pure-Python Louvain Modularity & Dual-Level GraphRAG. | `core/orion_graph.py` |
| `linkify` | Auto-injects wikilinks across context and agent files. | `commands/reflexion.py` |
| `compile` | Compiles Markdown rules into dense JSON matrices in `.orion/matrix/`. | `commands/brain.py` |
| `matrix <query>` | Queries compiled JSON rule matrices. | `commands/brain.py` |
| `contradict` | Detects and resolves colliding triplet predicates. | `commands/brain.py` |
| `raw_ingest` | Ingests unstructured files in `context/raw/` into markdown wiki nodes. | `commands/brain.py` |
| `diagnostics` | Evaluates RAG retrieval relevance, context grounding, and latency metrics. | `commands/rag.py` |

### 2. Quality Enforcement & Security Gatekeepers
| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `verify` / `verify_agents` | 8-Gate mechanical integrity, AST security, and portability audit. | `commands/verify_agents.py` |
| `scan security [dir]` | AST static vulnerability scanner with Trojan Source unicode inspection. | `core/scanner.py` |
| `scan tokens [dir]` | Codebase token analytics: per-extension breakdown table, share %, and largest token consumers. | `core/scanner.py` |
| `scan map [dir]` | Generates PageRank-ranked repository AST symbol skeleton map. | `core/scanner.py` |
| `scan targets [dir]` | Discovers prioritized file targets for offensive code audits. | `core/scanner.py` |
| `preflight` | Pre-flight diagnostic, self-healing route validation, and 4-pillar capability matrix (`--pillars`). | `commands/verify_agents.py` |
| `context-lint` | Validates `context/` 4 Lean Pillars and naming standards. | `commands/verify_agents.py` |
| `adversarial` | Enforces red-green test-driven assertions & delta-scoped mutation testing (`--diff`, `--fail-fast`). | `commands/verify_agents.py` |
| `eval` / `contrast` | CI/CD gatekeeper for UI aesthetics and Lucide token contracts. | `evals/audit_aesthetics.py` |
| `assert` | Deterministic assertion evaluation engine. | `evals/assertion_engine.py` |
| `instruction-lint` | Validates natural language and imperative modality across agent instructions. | `commands/verify_agents.py` |
| `consequence` | Static consequence assertion analysis and false-green test audit. | `commands/verify_agents.py` |
| `validate-response` | Validates agent output formatting against mandatory footer contract. | `evals/assertion_engine.py` |
| `delegate-check <tasks...>` | Deterministic Jaccard dependency overlap gate for worker delegation (<20% threshold). | `core/scanner.py` |

### 3. Execution State, Runtime & Orchestration
| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `fsm <action>` | Crash-proof formal state machine tracker with Git-bound checkpoint rollbacks (`--restore-code`). | `commands/state_machine.py` |
| `state_graph` | Superstep cyclic execution graph engine with channel reducers. | `commands/state_machine.py` |
| `harness` | Sovereign autonomous evolution harness engine. | `core/harness/engine.py` |
| `rtk` | Rust Token Killer proxy for CLI token minimization. | `core/capabilities.py` |
| `bun` | Probes Bun standalone runtime and JS/TS execution capabilities. | `core/capabilities.py` |
| `telemetry` | Structured span and execution trace telemetry logger. | `core/db.py` |
| `sandbox` | Provides ephemeral isolated execution scratchpads for command safety. | `core/sandbox.py` |

### 4. Memory Hygiene & Context Evolution
| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `compress` | Compresses episodic memory into English Lessword format. | `commands/compact.py` (via `commands/brain.py`) |
| `consolidate` | Activity-based temporal pulse knowledge synthesis. | `commands/reflexion.py` |
| `record` | Verbal reflective learning and failure invariant logging. | `commands/reflexion.py` |
| `amnesia` | Rule eviction mechanism (usage-based pruning). | `commands/state_machine.py` |
| `compact` | Native 5-tier context compactor (`orion compact <lite|full|aggressive|ultra|pipeline>` or `<shrink|distill|fts5|stopword>`). | `commands/compact.py` |
| `memory` | Virtual Core Memory & Archival store manager. | `commands/brain.py` |
| `budget` | Tracks token expenditure, tiers, and model cost telemetry. | `commands/state_machine.py` |

### 5. Deployment & Foundation Synchronization
| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `setup` | Unified interactive onboarding, workspace detector, hardware doctor, and feature wizard (aliases: `init`, `onboard`, `doctor`). | `commands/foundation.py` |
| `foundation deploy` | Physically deploys/syncs Foundation template to a local project. | `commands/foundation.py` |
| `foundation sync-ai` | Syncs AI brand configs to a local project. | `commands/foundation.py` |
| `foundation push-upstream` | Guides manual curation and promotion of local learnings to Foundation. | `commands/foundation.py` |
| `pack` | Universal context packager & multi-platform AI audit exporter with auto-intent vibe coding (`orion pack [audit|arch|hybrid|pr|diff|security|stats|<url>]`). | `utils/packer.py` |

---

## 🏛️ Architecture & Governance Policy

1. **Global Entrypoint Invariant**: Always invoke capabilities via `orion.py`.
2. **Standard Library Purity (Four Anchored Pillars)**: Pure Python 3 (`re`, `ast`, `sqlite3`, `hashlib`, `urllib`), Cargo Rust (`rtk`), Ollama, and Bun. Zero mandatory external `pip` dependencies.
3. **Kernel Primitives**: All commands and core engines share database connections, loopback endpoint validation, and telemetry via `core/db.py` and `core/capabilities.py`.
4. **Unified Persistence**: State checkpoints, graph entities, memory layers, and span telemetry default to `.orion/orion.db`; explicit custom DB paths remain supported for isolation and tests.
5. **Subprocess Boundary**: External commands use argv lists with `shell=False`; command text is parsed before execution and shell operators are never evaluated.
6. **Capability Contracts**: Optional RTK, ast-grep, Ollama, and Bun integrations expose `probe_capabilities` status with explicit fallback providers.
7. **Log Hygiene**: Scripts must NEVER write persistent log artifacts to workspace root. Use `.orion/` or session-specific temporary directories.
