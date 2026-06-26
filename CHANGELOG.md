# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.1.html).

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
