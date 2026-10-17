# VOLUME VII: PYTHON SCRIPTS (`scripts/`) — Execution Engine

---

## Chapter 15: Modular Script Architecture & Entry Point (`orion.py`)

The execution engine resides in `.agents/scripts/`. To prevent execution fragmentation and ensure air-gapped portability, all scripts are unified under a single modular CLI entry point: `orion.py`.

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Single CLI Entry Point (orion.py)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────┬───────────────┼───────────────┬────────────────┐
    ▼               ▼               ▼               ▼                ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌────────────────┐
│  Cluster 1   ││  Cluster 2   ││  Cluster 3   ││  Cluster 4   ││   Cluster 5    │
│  Foundation  ││  Cognitive   ││   Quality    ││  Resilience  ││   Evolution    │
│ & Deployment ││ & GraphRAG   ││  & Security  ││ & Token Opt  ││   & Hooks      │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└────────────────┘
    │               │               │               │                │
    └───────────────┴───────────────┼───────────────┴────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Core Subsystem (core/)                               │
│       db.py (SQLite WAL & Telemetry)  •  capabilities.py (4 Pillars)       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Chapter 16: The 5 Functional Script Clusters

### 16.1. Core Subsystem (`core/`)
Centralized infrastructure utilities imported across the ecosystem:
- **`core/db.py`**: Centralized SQLite3 connection manager and telemetry tracer. Mandates `PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;` and row factories across all database operations.
- **`core/capabilities.py`**: Single source of truth for the 4-Pillar capability matrix (Ollama client, RTK proxy stream filter, Bun static runtime engine) with 900s TTL cache in `.orion/working/capabilities.json`.
- **`core/paths.py`**: Deterministic path resolution and persistence anchors across the repository.
- **`core/security.py`**: Static AST security scanner utilizing CST rules to identify injection patterns, leaked credentials, and unsafe calls.
- **`core/scanner.py`**: Scans for ghost tokens, generates PageRank-ordered structural AST code skeletons, computes per-extension token analytics, and isolates offensive audit targets.
- **`core/orion_graph.py`**: Pure-Python Louvain Modularity Community Detection and Dual-Level GraphRAG query engine. Summarizes macro communities while traversing micro edges.
- **`core/sandbox.py`**: Safe execution isolation and loopback validation.

---

### 16.2. Cluster 1: Foundation & Deployment Engine
- **`commands/foundation.py` (`orion.py foundation deploy`, `foundation sync-ai`, `foundation push-upstream`)**: Scaffolds Foundation into target spoke projects, resolves placeholders (`{{PROJECT_NAME}}`), and syncs improvements back to master Foundation.

---

### 16.3. Cluster 2: Cognitive Kernel & Local GraphRAG
- **`commands/brain.py` (`orion.py brain sync "<query>"`, `brain export-vault`, `orion_ops`, `raw_ingest`, `contradict`)**: Unified cognitive kernel combining FTS5 BM25 lexical ranking, packed float32 vector embeddings (`archival_vectors`), 1-hop canonical SQLite graph traversal (`entities`, `relations`), wiki note resolution, raw ingestion, and predicate collision management.
- **`commands/reflexion.py` (`orion.py linkify`, `record`, `consolidate`)**: Injects `[[wikilinks]]` across context documents for native Obsidian Vault graph visualization, records verbal reflections, and drives temporal pulse consolidation.

---

### 16.4. Cluster 3: Quality Gates, Integrity & Security
- **`commands/verify_agents.py` (`orion.py verify`, `preflight`, `adversarial`, `context-lint`, `instruction-lint`)**: Supreme ecosystem integrity gatekeeper. Combines 8-gate mechanical integrity, pre-flight diagnostics, adversarial mutation testing (`--diff`, `--fail-fast` / `-x`), context naming lint, and instruction language lint.
- **`core/security.py` (`orion.py scan security <file>`)**: Static AST security scanner utilizing CST rules to identify injection patterns, leaked credentials, and unsafe calls.

---

### 16.5. Cluster 4: Execution Resilience & Token Optimization
- **`commands/state_machine.py` (`orion.py fsm` / `orion.py state_graph`, `amnesia`, `budget`)**: Formal state machine manager and superstep cyclic execution graph engine tracking active phases, channel reducers, Git-bound snapshots, rule eviction, and budget telemetry.
- **`core/capabilities.py` (`orion.py rtk` / `orion.py bun`)**: Terminal token filter (RTK proxy) and Bun static runtime engine.
- **`commands/brain.py` (`orion.py compact`, `shrink`, `distill`, `compress`, `compile`, `matrix`, `memory`)**: Unified token optimization and rule matrix engine providing 5-tier context compaction (`lite`, `full`, `aggressive`, `ultra`, `pipeline`), AST/JSON/CSV payload shaping, corpus surprisal pruning, episodic memory compression, rule matrix compilation, and matrix query.
- **`core/scanner.py` (`orion.py scan tokens|map|targets`)**: Codebase token analytics breakdown table, PageRank AST symbol skeletons, and prioritized offensive audit targets.
- **`utils/packer.py` (`orion.py pack [audit|pr|diff|security|stats|<url>]`)**: Multi-model frontier AI audit exporter bundling auto-detected domain slices, AST skeletons, and PageRank repo-maps with zero pip dependencies.

---

### 16.6. Cluster 5: Temporal Evolution & Lifecycle Hooks
- **`commands/reflexion.py` (`orion.py consolidate` / `orion.py record`)**: Activity-based temporal pulse running Session Pulse, Milestone Synthesis, Epoch Consolidation, and verbal reflective learning.
- **`hooks/pre-agent-wake.py`**: Pre-invocation hook generating the Omni-Buffer (`context.json`) and evaluating the Darwinian evolution heartbeat.
- **`evals/audit_aesthetics.py` (`orion.py eval`)**: Automated aesthetic validator auditing UI source code for design token compliance and micro-interactions.
