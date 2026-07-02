# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.1.html).

## [0.0.15] - 2026-07-02
### Changed
- **Universal AST Parser**: Upgraded AST logic from naive regex to 4-tier engine (Rust RTK -> Python `ast` -> `tree-sitter` JS/TS/Dart -> Regex fallback).
- **Unified Orion SQLite**: Unified Relational Graph from disjoint JSON/SQLite files into a single `orion.db` SQLite schema.
- **Documentation Alignment**: Synchronized `README.md` and `03-local_rag_brain.md` to reflect new AST and SQLite Graph mechanics.
- **Bug Fix**: Repaired YAML frontmatter syntax error in `knowledge-sync.md` workflow preventing IDE indexing.

## [0.0.14] - 2026-07-02
### Changed
- **Anti-GIGO Caveman Exemption**: Added explicit rule exemptions in Master BIOS to bypass Caveman Protocol for complex debugging, preserving LLM Chain-of-Thought (CoT).
- **AST Expansion Protocol**: Forced physical code reads (`view_file`) on function implementations before proposing fixes to cure Agentic Blindness.
- **Audit Alignment**: Corrected `README.md` to reflect true system mechanics, removing false "Dormant Scaffolding" warning on Vector Embeddings and marking Caveman/AST as patched vulnerabilities.
- **Deep Audit Report**: Generated exhaustive map (`comprehensive_audit.md`) confirming all README claims are backed by physical `.agents` Python scripts and workflows.

## [0.0.13] - 2026-07-02
### Changed
- **Documentation Migration**: Split monolithic `EXPLAIN.md` into modular markdown files in `.agents/docs/` for optimized RAG ingestion and removed obsolete docs.
- **Amnesia Upgrade (Usage-Based)**: Upgraded `rule_eviction.py` to use SQLite RAG metrics (`access_count` & `last_accessed`), abandoning flawed `mtime` logic for dynamic usage-based grace periods (90-day vs 30-day).
- **Amnesia Ecosystem Expansion**: Expanded eviction scope from `rules` to cover `workflows`, `canons`, and `skills` directories with smart folder-level preservation.
- **JIT Recall Improvements**: Removed hardcoded path logic in `brain.py` to allow dynamic structural restoration of archived assets.
- **Theoretical Claims Grounding**: Softened absolute terms in `README.md` ("Massive Local Swarm" -> "Sequential Delegation to Swarm").
- **Security Scanners Realized**: Deployed `secrets_scan_verifier.py` (API key leaks) and `migration_verifier.py` (dangerous SQL ops) into `preflight_check.py`, transforming ghost claims into functional mechanics.
- **Rules Index Purge**: Removed ghost/unimplemented references from `RULES_INDEX.md`.
## [0.0.12] - 2026-06-30
### Changed
- **Ecosystem Functional Audit**: Validated 10 audit points across identity, skills, and stability.
- **Skill Pruning**: Removed qualitative fluff from 13 `SKILL.md` files using `clean_fluff.py` via `re.DOTALL`.
- **Identity Sync**: Updated `pre-agent-wake.py` to seamlessly sync `.genome.json` evolutionary traits directly into `AGENT_IDENTITY.md`.
- **System Stability**: Patched log rotation logic, SQLite fail-safe retry mechanisms, and page limits in `brain.py`.

## [0.0.11] - 2026-06-30
### Changed
- **Architecture**: Upgraded to **True LightRAG Engine** (Dual-Retrieval Graph + Vector + Lexical). Added native pure Python Cosine Similarity, storing `nomic-embed-text` vectors as JSON arrays in SQLite. 
- **Granular State Routing**: Implemented `EMBED_ONLY`, `FULL`, `LLM_ONLY`, and `OFF` capabilities in NanoBrain to enforce **Graceful Degradation**. Prevents local "dumb" 0.5b LLMs from polluting complex logical extraction.

## [0.0.10] - 2026-06-30
### Changed
- **Master BIOS**: Updated `GEMINI.md` to `0.0.10 - Knowledge Sync`. Added Sequential Tool Ban, Auto-Pilot Injector hook (`pre-agent-wake.py`), Darwinian Heartbeat, and strict JIT Routing table.
- **System Defense**: Added strict Anti-Affirmation and Circuit Breaker inline micro-rules.

## [0.0.9] - 2026-06-30
### Changed
- **Ecosystem Functional Audit**: Validated structural health and scripting functionalities.

## [0.0.8] - 2026-06-27
### Changed
- **Memory Backbone Deep Audit**: Fixed bugs across `orion_ops.py`, `brain.py`, `linkify.py`, `compress_memory.py`, and `ast_parser.py` including broken `handoff.md` backups, invalid regexes, deprecated hashing, and redundant database initialization loops.
- **Agent Templates**: Synchronized `AGENTS.template.md` with active `GEMINI.md` to prevent version drift.

## [0.0.7] - 2026-06-27
### Changed
- **Knowledge Sync**: Routine knowledge base sync and triplet extraction.
- **Linkify Engine**: Reverted to `[[Wiki-links]]` for cross-OS git portability and added code block protection.

## [0.0.6] - 2026-06-27
### Changed
- **Linkify Engine**: Converted dynamic Wiki-links to Native Absolute Markdown Links for robust IDE clickability.
- **Orion Ops Audit**: Patched SQLite storage leaks in prune_orphans and inject_triplets to prevent graph corruption and ghost data.

## [0.0.5] - 2026-06-26
### Changed
- **Architecture Audit & Stability**: Fixed fatal execution blockers (bare module imports, absolute path resolution) in `evolve.py`, `track_budget.py`, `preflight_check.py`, and `nano_compressor.py`.
- **Graceful Degradation**: Hardened `evolve.py` to safely fallback to Dry Run mode without throwing `AttributeError` when NanoBrain (Local LLM) is offline.
- **SaaS Context Distribution**: Decomposed monolithic theoretical documentation (`EXPLAIN.md` and `README.md`) into a strict 82-file SaaS registry structure inside `context/`.
- **Knowledge Graph Triplet Ingestion**: Injected 33 semantic triplets into `orion.db` to logically map the newly distributed SaaS context files.
- **Code Optimization**: Pruned cosmetic stubs like `preload_wiki_nodes()` from `compress_memory.py`.

## [0.0.4] - 2026-06-26
### Changed
- Refactored `Omni-Buffer Context Protocol` in `GEMINI.md`, `core-guardrails.md`, and `AGENTS.template.md` to be explicitly Agent-Driven via `pre-agent-wake.py`, removing reliance on non-existent IDE daemons.
- Upgraded `evolve.py` to perform a dual-scan on both `LEARNINGS.md` and `MEMORY.md`, and safely fallback to DRY RUN if `NanoBrain` is offline.
- Upgraded `orion_ops.py` to perform deterministic AST-based regex Graph Triplet extraction during ingest, eliminating the need for LLMs to generate graph edges.
- Refactored `brain.py` to remove `pyyaml` dependency (replaced with native `json`) and significantly compressed the footer output.

## [0.0.3] - 2026-06-22
### Changed
- Refactored `.agents` ecosystem: Removed `backend-orchestrator` ghost references, consolidated into `project-architect`.
- Upgraded `knowledge-sync.md` to prevent version drift.
- Removed Interview Gate from `self-evolve.md` for full autonomy.
- Upgraded `audit-00-master-workflow.md` to enforce Soft Auto-Proceed (Batching) and OS-Agnostic tooling.


## [0.0.2] - 2026-06-22
### Added
- **Dynamic Local LLM Tiers**: `foundation.py` now maps local models to `Low`, `Medium`, and `High` intelligence tiers to gate features dynamically and prevent Agentic Hallucination.
- **Graceful Cloud Fallback**: Added `check_tier` in `NanoBrain` that safely outputs `[DELEGATE_TO_CLOUD]` when local LLM cannot handle a task.
- **Auto-Hydration on Deploy**: `foundation deploy` now automatically scaffolds `context/` and runs bulk graph ingestion (`orion_ops ingest`) immediately to prevent zero-day amnesia.
- **NanoBrain Toggle**: Introduced `nanobrain on/off/status` commands via `.nanobrain_status` flag to manage background RAM lockups.
- **Mandatory Caveman**: Changed `AGENTS.template.md` to make Caveman Mode active by default instead of waiting for explicit user requests.

### Fixed
- Fixed bug where `subprocess.run` hardcoded `"python"` internally, breaking virtual environments and Linux VPS aliases (replaced with `sys.executable`).

## [0.0.1] - 2026-06-12
### Added
- Clean squashed initial release (`v0.0.1`) of Portable Brainvibing foundation.
- Purged all legacy Model Context Protocol (MCP) references and servers.
- Migrated Triplet Graph extraction fully to IDE Agent Delegation workflow.
- Established baseline architecture for token-optimized autonomous agent operations.
