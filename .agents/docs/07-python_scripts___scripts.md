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
│ & Deployment ││ & GraphRAG   ││  & Security  ││ & Bento Opt  ││   & Hooks      │
└──────────────┘└──────────────┘└──────────────┘└──────────────┘└────────────────┘
    │               │               │               │                │
    └───────────────┴───────────────┼───────────────┴────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Core Subsystem (core/)                               │
│  db.py (SQLite WAL) • memory.py (Observational Memory) • capabilities  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Chapter 16: The 5 Functional Script Clusters

### 16.1. Core Subsystem (`core/`)
Centralized infrastructure utilities imported across the ecosystem:
- **`core/db.py`**: Centralized SQLite3 connection manager and telemetry tracer. Mandates `PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;` across all database operations, and guards test runners (`unittest`/`pytest`) against writing telemetry into the production `.agents/OBSERVATIONS.md`.
- **`core/memory.py`**: Virtual context manager and 3-tier Observational Memory engine. Manages dynamic token budgets (`max(3600, total // 2)`), ephemeral observation anchors (`[O1]`–`[On]`), zero-LLM generational rollover (`memory_generations` with millisecond-resolution `GEN-<count>-<ms>` IDs), `superseded_by` lineage, and on-demand anchor recall (`recall_anchor`).
- **`core/capabilities.py`**: Single source of truth for the 4-Pillar capability matrix (Universal Local AI Coprocessor with multi-port auto-probe across Ollama, llama-server, LM Studio, and vLLM; RTK proxy stream filter; Bun static runtime engine) with 900s TTL cache in `.orion/working/capabilities.json`.
- **`core/dna.py`**: Universal Project DNA sequencer classifying repository files across 5 architectural tiers (`contracts`, `domain`, `services`, `state`, `presentation`).
- **`core/paths.py`**: Deterministic path resolution and persistence anchors across the repository.
- **`core/security.py`**: Static AST security scanner utilizing CST rules to identify injection patterns, leaked credentials, and unsafe calls.
- **`core/scanner.py`**: Scans for ghost tokens, generates PageRank-ordered structural AST code skeletons, computes per-extension token analytics, and isolates offensive audit targets.
- **`core/orion_graph.py`**: Pure-Python Louvain Modularity Community Detection and Dual-Level GraphRAG query engine. Summarizes macro communities while traversing micro edges.
- **`core/sandbox.py`**: Safe execution isolation and PEP 578 syscall loopback validation.
- **`core/platform_manifests.py`**: Universal 19-platform IDE manifest generator, instruction adapter builder, and `hooks.json` compiler.
- **`core/harness/`**: Sovereign Skill Lifecycle & Code-As-Harness engine comprising 6 specialized modules:
  - `engine.py` (`HarnessEngine`): CLI orchestrator (`orion.py harness status|promote|lifecycle|curate|index|serve|record-tool`) and `synthesize_action_verifier()` generator for `.agents/canons/global/harnesses/<slug>_verifier.py`.
  - `admission.py` (`SovereignPromoter`): 14-gate deterministic admission barrier (`HARNESS-FM-01..03`, `HARNESS-STR-01..04`, `HARNESS-T0-01`, `HARNESS-SIB-01`, `HARNESS-CUR-01`, `HARNESS-REF-01`, `HARNESS-SEC-01`, `HARNESS-VERIFY-01`, `HARNESS-CMT-01`).
  - `capture.py` (`ToolQuantumCapture`, `SecretRedactor`): Opportunity-relative session quantum tracker and credential scrubber.
  - `staging.py` (`IntentQueue`, `StagedIntent`, `StagingServer`): Quarantine staging queue in `.orion/harness/intents/` and stdio JSON-RPC 2.0 MCP server (`stage_skill`).
  - `lifecycle.py` (`LifecycleManager`): Opportunity-relative skill maturity and archival evaluator (`maturity=100, capacity=50`).
  - `curator.py` (`ClusterCurator`): Prefix-overlap detector and umbrella skill consolidation engine.

---

### 16.2. Cluster 1: Foundation & Deployment Engine
- **`commands/foundation.py` (`orion.py setup`, `orion.py init`, `orion.py doctor`, `orion.py onboard`, `orion.py deploy`, `foundation sync-ai`, `foundation push-upstream`)**: Unified interactive setup, onboarding, and diagnostic wizard. Features hardware RAM/VRAM inspection, hardware-fit model recommendations (Ollama / llama-server), 4-pillar toolchain doctor checks, project scaffolding, and upstream synchronization.

---

### 16.3. Cluster 2: Cognitive Kernel & Local GraphRAG
- **`commands/brain.py` (`orion.py brain sync "<query>"`, `orion.py brain rollover`, `orion.py brain recall <anchor_id>`, `orion_ops`, `raw_ingest`, `contradict`)**: Unified cognitive kernel facade, hardware discovery (`NanoBrain`), rule matrix compiler, generational memory rollover, anchor timeline recall, raw ingestion, and predicate collision management.
- **`commands/rag.py` (`orion.py brain sync`, `diagnostics`)**: Local RAG & semantic retrieval engine combining FTS5 BM25 lexical ranking, packed float32 vector embeddings (`archival_vectors`), 1-hop canonical SQLite graph traversal (`entities`, `relations`), `superseded_by` anti-flashback filtering, wiki note resolution, and RAG diagnostic evaluations.
- **`commands/vault.py` (`orion.py export-vault`)**: Obsidian graph vault export (`.orion/export/vault/`), second-brain 4-note brief generation, and vault mirror cache maintenance.
- **`commands/reflexion.py` (`orion.py observe`, `orion.py resolve`, `orion.py linkify`, `record`, `consolidate`)**: Manages the 5-status `ObservationLedger` (`.agents/OBSERVATIONS.md` and `OBSERVATIONS.archive.md`), runs 2nd-violation Tier-0 barrier escalation (`check_rule_violations`), mines operator command habits (`mine_operator_habits`), injects `[[wikilinks]]`, and drives temporal pulse consolidation.

---

### 16.4. Cluster 3: Quality Gates, Integrity & Security
- **`commands/verify_agents.py` (`orion.py verify`, `preflight`, `adversarial`, `context-lint`, `instruction-lint`)**: Supreme ecosystem integrity gatekeeper. Combines 8-gate mechanical integrity, structural ceiling enforcement (`core_max_lines` frontmatter ratchet), pre-flight diagnostics, adversarial mutation testing (`--diff`, `--fail-fast` / `-x`), context naming lint, and instruction language lint.
- **`core/security.py` (`orion.py scan security <file>`)**: Static AST security scanner utilizing CST rules to identify injection patterns, leaked credentials, and unsafe calls.
- **`core/sandbox.py` (`orion.py sandbox --code <code>`)**: AST-gated hermetic execution sandbox enforcing PEP 578 audit hooks to isolate untrusted scripts, intercept filesystem mutations, and block subprocess execution outside `_JAIL_ROOT`.

---

### 16.5. Cluster 4: Execution Resilience, Bento Slicer & Token Optimization
- **`commands/bento_slicer.py` (`orion.py bento init <plan.md>`, `orion.py bento next --verify`, `orion.py bento status`, `orion.py bento reset`)**: Zero-escape sequential task slicer for Budget and Standard models. Parses implementation plans into atomic single-task cards (`.orion/working/ACTIVE_TASK.md`), splits multi-pair cards into sub-tasks (`1.1a`, `1.1b`), checks `TTP-*` finding coverage, sorts tasks by topological blast-radius ($T_0 \to T_5$) and bottom-up line order, recalibrates live disk line spans, auto-aligns `REPLACE` indentation, and enforces a post-condition disk mutation gate (`Exit Code 2` on unpatched files).
- **`commands/state_machine.py` (`orion.py fsm` / `orion.py state_graph`, `amnesia`, `budget`)**: Formal state machine manager and superstep cyclic execution graph engine tracking active phases, channel reducers, Git-bound snapshots, rule eviction, and budget telemetry.
- **`core/capabilities.py` (`orion.py rtk` / `orion.py bun`, PreToolUse Hook)**: Terminal token filter (RTK proxy), Bun static runtime engine, and fail-closed IDE tool execution interceptor with inline circuit breaker enforcement.
- **`commands/compact.py` (`orion.py compact`, `shrink`, `distill`, `compress`)**: Unified token optimization engine providing 5-tier context compaction (`lite`, `stream`, `full`, `aggressive`, `ultra`, `pipeline`), AST/JSON/CSV payload shaping, stream elision, corpus surprisal pruning, episodic memory compression, and Ollama/heuristic distillation.
- **`core/scanner.py` (`orion.py scan tokens|map|targets`)**: Codebase token analytics breakdown table, PageRank AST symbol skeletons, and prioritized offensive audit targets.
- **`utils/packer.py` (`orion.py pack [arch|hybrid|full|pr|diff|security|stats|<url>]`)**: Universal Project DNA context exporter bundling polyglot monorepo containers, AST skeletons, PageRank repo-maps, cross-bundle import routers, and static audit radars into at most 10 balanced Markdown bundles across isolated tier directories (`.orion/bundles/{arch,hybrid,full}/`). Also maintained as standalone CLI in `tools/digestpack/`.

---

### 16.6. Cluster 5: Temporal Evolution & Lifecycle Hooks
- **`commands/reflexion.py` (`orion.py consolidate` / `orion.py record` / `orion.py observe` / `orion.py resolve`)**: Activity-based temporal pulse running Session Pulse, Milestone Synthesis, Epoch Consolidation, Observation Ledger governance, and operator habit mining.
- **`hooks/pre-agent-wake.py`**: Pre-invocation hook generating the cache-aware Omni-Buffer (`context.json`) with a 5-minute SHA-256 structural hash gate, active Bento task injection, and Darwinian evolution heartbeat evaluation.
- **`evals/audit_aesthetics.py` (`orion.py eval`)**: Automated aesthetic validator auditing UI source code for design token compliance and micro-interactions.

---

### 16.7. The 8 Gates of `verify_agents.py` (`orion.py verify`)
`commands/verify_agents.py` executes 8 sequential verification gates to prevent structural decay, security drift, and documentation desynchronization:
1. **Gate 1 — Portability & Workspace Hygiene**: Scans tracked files for hardcoded OS home-directory paths, `file://` URI leaks in repository markdown, lingering `.bak`/`.tmp` artifacts, and transient scratch files.
2. **Gate 2 — Defensive UTF-8 I/O Compliance**: Parses Python scripts via `ast` to verify that `open()` and `Path.read_text()`/`write_text()` calls explicitly pass `encoding="utf-8"` (with `errors="replace"` where required) to prevent Windows `cp1252` crashes.
3. **Gate 3 — Mechanical, Blueprint & Link Integrity**: Validates every `[[wikilink]]`, markdown relative path, skill frontmatter (`name`, `description`, `core_max_lines`), `AGENTS_INDEX.md` registry entry, and banned ghost claims across `README.md` and `docs/*.md`.
4. **Gate 4 — Polyglot AST Security & Baseline Differential**: Runs `core/security.py` across all scripts and hooks, comparing findings against `.agents/.security-baseline.json` to block new command injection, unsafe deserialization, or credential exposure.
5. **Gate 5 — Ecosystem & SQLite 21-Table Producer-Consumer Cohesion**: Verifies that all 18 active SQLite tables (plus 3 FTS5 virtual tables) in `core/db.py` have active writer and reader paths across `commands/` and `core/`.
6. **Gate 6 — Version, JIT Router Parity & 4-Pillar Matrix**: Confirms byte-for-byte parity between `AGENTS.md`, `GEMINI.md`, and `templates/AGENTS.template.md` JIT routing tables and verifies the 4-Pillar capability contract.
7. **Gate 7 — Project DNA, Canon Matrix, Doc Metrics Sync & Shell Portability**: Validates `.dna.json`, dynamically cross-checks physical counts of rules (`13`), public skills (`21 Public Domain Skills (+1 Internal)`), SQLite tables (`18`), and ecosystem canons against documentation claims, and audits shell scripts for POSIX portability.
8. **Gate 8 — Instruction Language Lint & Ceiling Ratchet**: Enforces English-first instruction purity across `.agents/rules/` and `.agents/skills/` and verifies that no `SKILL.md` exceeds its `core_max_lines` frontmatter ceiling.

---

### 16.8. Automated Contract Test Suite Matrix (`.agents/scripts/tests/`)
All 27 test suites in `.agents/scripts/tests/` run on standard library `unittest` without external test runners:

| Test Suite | Target Subsystem & Verified Contract |
|:---|:---|
| `test_autoharness_loop_contract.py` | Closed-loop autoharness generation, verification, and regression prevention |
| `test_barrier_escalation.py` | Tier-0 to Tier-3 barrier escalations, circuit breakers, and mechanical catch gates |
| `test_bento_slicer.py` | Bento task slicing, topological blast-radius sorting ($T_0 \to T_5$), disjoint partitioning, and bottom-up ordering |
| `test_capability_contracts.py` | 4-Pillar capability contract (P1-P4 stdlib/rust/ollama/bun), tool discovery, and platform readiness probes |
| `test_cli_deployment_contract.py` | Gateway CLI subcommand routing, exit codes, and cross-platform flag forwarding in `orion.py` |
| `test_consequence_verifier.py` | Pre/post-action consequence analysis, side-effect prevention, and safety boundaries |
| `test_core_ceiling_gate.py` | Gate 8 instruction language linting, English-first purity, and `SKILL.md` `core_max_lines` ceiling ratchet |
| `test_dna_linter_contract.py` | Project DNA 5-tier strata classification, architecture boundary validation, and upward import layer violations |
| `test_dna_trend.py` | Project DNA historical trend analytics, strata compliance scoring, and drift metrics |
| `test_encoding_hygiene.py` | UTF-8 encoding mandate, zero raw `open()`, and subprocess encoding enforcement across platforms |
| `test_habit_miner.py` | Habit miner frequency analysis, workflow pattern recognition, and procedural automation triggers |
| `test_humanizer.py` | Lessword Shannon surprisal compression, 26 AI writing pattern detection, and prose de-AI filtering |
| `test_observation_capture.py` | Observation capture, session quantum incrementation, and telemetry ledger ingestion |
| `test_observation_store.py` | SQLite observation store persistence, status transitions, and query indexing |
| `test_observational_memory.py` | Observational memory primitives, anchor IDs, dynamic budgets, and generational rollover |
| `test_obsidian_vault_contract.py` | Second Brain Obsidian vault synchronization, frontmatter schema validation, and bidirectional linking |
| `test_orion_compactor_contract.py` | Context compaction, state token pruning, and conversational history compression |
| `test_packer_universal.py` | Universal multi-tier pack system (arch, hybrid, full), PageRank topological sort, and monorepo discovery |
| `test_persistence_contracts.py` | Single-sink telemetry (`mechanical_catches.jsonl`), atomic writes, and SQLite WAL durability |
| `test_phase5_lifecycle_contracts.py` | Phase 5 lifecycle state machine, opportunity-relative skill states, and sunset verification |
| `test_phase6_contract_sync.py` | Phase 6 contract synchronization, schema integrity, and ecosystem cross-validation |
| `test_plugin_manifests.py` | Multi-IDE deployment engine, platform manifests (VS Code, Cursor, JetBrains, Gemini), and hook compilation |
| `test_response_validator.py` | Unified response footer contract, Lessword output validation, and tier recommendations |
| `test_scanner_polyglot_ast.py` | Polyglot AST parsing (Python, Dart, JS/TS), symbol mapping, and syntax boundary checks |
| `test_security_boundaries.py` | Polyglot security scanner, secret redaction, AST security gate (Exit Code 126), and baseline filtering |
| `test_stack_detection.py` | Dependency-aware tech stack detection, framework profiling, and micro-canon pruning |
| `test_stream_elision_contract.py` | Real-time stream elision, token budgeting, and high-frequency log truncation |
