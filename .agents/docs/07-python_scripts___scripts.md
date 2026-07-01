# VOLUME VII: PYTHON SCRIPTS (`scripts/`) — Execution Engine

---

## Chapter 12: Script Architecture

### 12.1. Entry Point: `orion.py`
The only script called directly. All commands are routed through this modular CLI.

### 12.2. Complete Command Table

| Command | Target Script | Function |
|:--|:--|:--|
| `verify` | `commands/verify_agents.py` | Markdown compiler — scans all links, ensures no phantom references |
| `context-lint` | `commands/context_naming_lint.py` | Validates context file naming against the 82-file registry |
| `deploy` | `commands/foundation.py` | Deploys/syncs Foundation to a new project via symlinks |
| `push-upstream` | `commands/foundation.py` | Syncs project evolutions back to master Foundation |
| `budget` | `commands/track_budget.py` | Tracks budgets and tier telemetry |
| `scan tokens` | `core/scanner.py` | Ghost Token Auditor — detects memory bloat |
| `scan map` | `core/scanner.py` | Structural Code Mapper — creates lightweight skeletons |
| `scan targets` | `core/scanner.py` | Identifies targets for Offensive Audit |
| `preflight` | `commands/preflight_check.py` | Pre-flight diagnostics (Self-Healing Routing) |
| `compress` | `commands/compress_memory.py` | Compresses episodic memory to Caveman format |
| `orion_ops init` | `commands/orion_ops.py` | Initializes the `.orion/` infrastructure |
| `orion_ops ingest` | `commands/orion_ops.py` | Ingests rules and configurations into the graph |
| `linkify` | `commands/linkify.py` | Auto-injects Absolute Native Markdown Links into context files |
| `raw_ingest` | `commands/raw_ingest.py` | Converts unstructured text in `context/raw/` into structured Obsidian Markdown |
| `amnesia` | `commands/rule_eviction.py` | Rule eviction mechanism (garbage collection) |
| `swarm` | `commands/auto_delegate.py` | Multi-Thread Micro-Fix (parallel) |
| `rtk` | `core/rtk_proxy.py` | RTK Proxy |
| `evolve bench` | `commands/evolve.py` | Benchmarks rule mutations A/B |
| `evolve mine-friction` | `commands/evolve.py` | Mines friction patterns from learnings |
| `fsm` | `commands/state_machine.py` | Engine for the Crash-Proof Formal State Machine |
| `contradict` | `commands/contradict.py` | Resolves colliding predicates in GraphRAG |
| `consolidate` | `commands/consolidate.py` | Activity-Based Temporal Pulse synthesis |

### 12.3. Supporting Utilities

| File | Function |
|:--|:--|
| `utils/ast_parser.py` | Universal AST Parser — extracts code skeletons |
| `utils/evolution_ledger.py` | Writes to `EVOLUTION_LOG.jsonl` |
| `commands/brain.py` | RAG Engine: query expansion, FTS5 search, Ollama filtering |
| `commands/compile_rules.py` | Compiles Markdown rules → YAML for `matrix/` |
| `commands/nano_compressor.py` | Ollama connection for NanoBrain compression |
| `commands/scaffold_saas.py` | SaaS project scaffold generator |

---

