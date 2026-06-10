# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.1.html).

## [0.9.3] - 2026-06-09
### Changed
- feat: Transformed linear SOPs in `app-lifecycle.md` into dynamic State Machines to eliminate Procedural Rigidity.
- feat: Injected Explicit Internal Arbitration protocol into `core-guardrails.md` to prevent silent conflict resolution.
- feat: Added Cross-Domain Synthesis micro-rule to `GEMINI.md` to ensure cohesive, unfragmented multi-layer code logic.

## [0.9.2] - 2026-06-09
### Changed
- feat: Migrated Caveman Protocol from a mandatory global language gate to an opt-in, on-demand JIT skill hook.
- feat: Deployed `prerequisites.md` to enforce the Graceful Fallback Strategy (Zero-Crash Policy) for advanced tools.
- feat: Integrated Self-Reflection (Evaluasi Diri) step and precise session-only RTK metrics into the `session-offload` workflow.
- docs: Updated `EXPLAIN.md` directory map and synchronized JIT routing tables after reversing over-optimized token cuts.

## [0.9.1] - 2026-06-07
### Changed
- feat: Implemented Self-Evolve Engine (Darwinian Evolution 2.0) with Heartbeat Cron, Friction Miner, and Canary Deploy rules.
- feat: Added `orion.py evolve` subcommand (`bench`, `mine-friction`, `drift-scan`).
- feat: Introduced Evolution Ledger (`EVOLUTION_LOG.jsonl`) and Genome auto-merge logic in `foundation.py push-upstream`.
- feat: Updated `orion_mcp.py` to expose `orion_evolve` and `orion_push_upstream` as native JSON-RPC tools.

## [0.9.0] - 2026-06-07
### Changed
- feat: Introduced Native MCP Server (`orion_mcp.py`) allowing zero-dependency JSON-RPC communication for `ingest`, `resolve`, and `verify`.
- feat: Developed Universal AST Parser to optimize SQLite Graph ingestion and prevent token bloat.
- feat: Deployed Omni-Buffer (`context.json`) hook for cross-IDE active tab synchronization.
- docs: Slashed `DEPLOY_ME.md` bloat by 60%, enforcing strict `orion.py deploy` python script execution for deployments.
- refactor: Eradicated `python3` explicit calls globally to enforce 100% OS-Agnostic Plug and Play execution.
## [0.8.1] - 2026-06-07
### Changed
- feat: Added `/auto-context` workflow to capture organic business rules from chat conversations.
- refactor: Unified command invocations and paths to use modular CLI (`orion.py`) instead of old standalone python scripts.
- fix: Updated verify-agents logic to support modular structure, path fallback, and automated check routines.

## [0.8.0] - 2026-06-06
### Changed
- feat: Executed massive architectural shift to **Modular CLI** (`orion.py`). Consolidated 15 scattered Python automation scripts into a unified entrypoint with `commands/` and `core/` structure.
- docs: Complete visionary rewrite of `README.md` and `EXPLAIN.md`. Introduced the "Orion Agentic OS" terminology, the Darwinian Evolution Loop, and the "Advanced Vision" (unbound hardware scalability).
- fix: Updated all internal markdown cross-references and pre-commit hooks to utilize the new `orion.py` architecture.


## [0.7.8] - 2026-06-06
### Changed
- fix: Globally refactored `.agents` framework to replace hardcoded `python` commands with `python3` for cross-platform VPS compatibility.
- feat: Added rule `1.6 OS-Aware Python Execution` to `GEMINI.md` and `core-guardrails.md` for Windows fallback handling.

## [0.7.7] - 2026-06-06
### Changed
- feat: Introduced `/project-migrate` workflow for safe onboarding of existing brownfield codebases.
- feat: Implemented Technical Inference inside `/project-migrate` to automatically extract language, framework, and dependencies into `03_Tech/ARCHITECTURE.md` without hallucinating business strategy.
- feat: Added dynamic JIT routing triggers for legacy migration onboarding.

## [0.7.6] - 2026-06-06
### Changed
- feat: Deployed `Session Offload Soft Trigger` to proactively prompt context eviction upon major milestone completion.
- feat: Injected `Implementation Smoothness Audit` into `AGENTS.template.md` `EVALUATION` footer block to systematically detect and route AI tool-use failures to `self-evolve` based on terminal logs.

## [0.7.5] - 2026-06-05
### Changed
- feat: Implemented Hybrid RAM-Disk Graph. `orion_ops.py` now leverages `PRAGMA cache_size=-64000` to natively pin a 64MB hot graph in RAM while pushing cold edges to disk.
- feat: Deployed `Auto-Suture Protocol` in `verify_agents.py` to auto-inject missing YAML frontmatter into broken rules and skills rather than crashing the mechanical integrity check.
- feat: Bound `LEARNINGS.md` semantic ingestion directly to the `.git/hooks/pre-commit` pipeline to force physical execution of the neuroplasticity loop.
- fix: Eliminated the root `context/` matrix from the `_foundation` baseline to enforce Rule 1.5 (avoiding overlap with SaaS target deployment logic).

## [0.7.4] - 2026-06-05
### Changed
- feat: Implemented Memory-Mapped (mmap) Graph in `orion_ops.py` via SQLite PRAGMAs (`mmap_size`, `WAL`, `MEMORY`) to bypass RAM constraints for massive graphs.
- feat: Implemented Deterministic Execution Path RAG. `code_map.py` now extracts AST execution triplets which are queried during Orion RAG.
- feat: Added Nano-Speculative Drafting (`draft_boilerplate`) to `brain.py` to generate zero-shot code skeletons locally.
- fix: Enforced strict English-only outputs in `NanoBrain` Caveman compressor to prevent cross-lingual hallucinations on the 0.5B model.

## [0.7.3] - 2026-06-05
### Changed
- feat: Deployed `ORION_SMART_INGEST_ARCHITECTURE`.
- feat: Restored `code_map.py` as a Zero-Dependency Regex Parser for lightning-fast code skeleton extraction.
- refactor: Replaced hardcoded blacklist in `orion_ops.py` with dynamic `.gitignore` parsing (`get_smart_ignore_dirs`) and a universal baseline (`node_modules`, `build`, etc.).
- fix: Enforced `.gitignore` generation pre-flight step in `DEPLOY_ME.md` for safer AI ingestion.
- fix: Raised NanoBrain Circuit Breaker RAM limit in `brain.py` from 85% to 90% for constrained environments.

## [0.7.2] - 2026-06-04
### Changed
- feat: Implemented "Safe Auto-Ingest" pattern during app-lifecycle and deployment, specifically targeting high-signal knowledge directories (`.agents/` and `context/`) while maintaining the strict ban on root-level wildcard ingestion.

## [0.7.1] - 2026-06-04
### Changed
- fix: Updated DEPLOY_ME and PREREQUISITES to explicitly require manual Ollama OS-level installation and strictly forbid auto-ingest during deployment due to RAM/token constraints.

## [0.7.0] - 2026-06-04
### Changed
- feat: Eradicated legacy "wiki" terminology; ecosystem fully canonicalized to Orion Graph (`.orion/`).
- feat: Deployed Active JIT Reference Routing Tables across all 10 core skills, eliminating "sleeping knowledge".
- refactor: Merged semantic ghost-link detection (`synapse_check.py`) directly into the mechanical linter (`verify_agents.py`) for unified integrity checks.
- fix: Strict enforcement of Caveman Mode and Language Gate across generated files.

## [0.6.1] - 2026-06-03
### Changed
- feat: Enforce mandatory validation block in Project Intake workflow to prevent hallucinated requirements.
- refactor: Prune ecosystem-specific workflows (Flutter/Dart) from the framework-agnostic universal agent baseline.
- fix: Correct environment lint/deploy configurations in generic production deploy pipeline.

## [0.6.0] - 2026-06-03
### Changed
- feat: Executed massive architectural defragmentation of `.agents/` to eliminate redundancy.
- refactor: Merged Context Hierarchy and Context Standards into a unified `context-management.md`.
- refactor: Merged all Git Workflow instructions into a single `git-workflow.md` source of truth.
- refactor: Isolated 9 scattered framework-specific rules into a dedicated `canons/ecosystems/flutter/` namespace to protect token cohesion.
- feat: Implemented the **Whitelist Gitignore Paradigm** (`/*`) allowing users to safely test `.agents` at the repository root without polluting version control.

## [0.5.0] - 2026-06-03
### Changed
- feat: Deployed the **Neuro-Link Engine** (`brain.py`) to auto-harmonize `.agents`, `.wiki`, and `context/` state.
- feat: Implemented AST-Aware Semantic Tagging across all 13 core templates for deterministic Python extraction.
- feat: Deployed the **Universal Distiller** (`sync_universal.py`) to maintain a 100% framework-agnostic baseline in `universal/.agents/`.
- refactor: Replaced legacy monolithic `CONTEXT.md` generation with explicit 4-Pillar `context/` 82-file scaffolding in init workflows.
- fix: Mandated `wiki_refs` in SaaS frontmatter to bidirectionally link working memory and long-term wiki knowledge.

## [0.4.0] - 2026-05-20
### Changed
- feat: MetaGPT Pattern Injection (Output-as-Input, State Machine Persistence, Auto-Chain Trigger)
- refactor: Unified Response Footer, simplified 3-Tier model (BUDGET, STANDARD, PREMIUM), and removed redundant "always on" rules
- feat: Introduced Flutter Code Recipes (init, feature, liquid-glass, tests, release) and mapped them into the JIT router
- fix: Consolidated AI template into a single AGENTS.template.md for true DRY deployment

## [0.3.4] - 2026-04-18
### Changed
- feat(token): integrated Rank 1-3 token optimization tools (rtk, caveman, code_map, token_audit)


## [0.3.3] - 2026-04-18
### Changed
- Fix missing YAML frontmatter in rules


## [0.3.2] - 2026-04-18
### Changed
- Update setup scripts with improved path resolution and sanitization


## [0.3.1] - 2026-04-18
### Changed
- Final cleanup of stale documentation and workflow references.


## [0.3.0] - 2026-04-18
### Changed
- Modernize foundation: adopt RTK and Caveman. Remove obsolete manual catalogs.


## [0.2.31] - 2026-03-31
### Changed
- solve deploy problem & Dual Lean naming policy


## [0.2.30] - 2026-03-31
### Changed
- Automated agent synchronization and sanitization.


## [0.2.29] - 2026-03-29
### Changed
- Audit & Remediation of Publishing Engine: Fixed SCRIPTS.md inclusion


## [0.2.28] - 2026-03-29
### Changed
- Audit & Remediation of Publishing Engine


## [0.2.27] - 2026-03-29
### Changed
- Foundation Sync: Fixed sanitization and hardening


## [0.2.26] - 2026-03-29
### Changed
- Foundation Sync: Hardened Rules & Seeding update


## [0.2.25] - 2026-03-29
### Changed
- Update table to show only major/minor versions


## [0.2.24] - 2026-03-29
### Changed
- Refactor publish_agents regex for table changelog


## [0.2.23] - 2026-03-29
### Changed
- Automated agent synchronization and sanitization.


## [0.2.22] - 2026-03-28
### Changed
- **Ecosystem Refactor**: Re-indexed structure to exactly 11 core skills (merged redundancies like `db-expert` into `backend-orchestrator`), formalized `scripts/`/`templates/`/`evals/` pillars, and synchronized `AGENTS.md` and repository layouts.

## [0.2.21] - 2026-03-28
### Changed
- Automated agent synchronization and sanitization.


## [0.2.20] - 2026-03-28
### Changed
- Architectural adaptation: Added IDE / Antigravity exemption to Binary Oratory rules, shifting DO/DONT to implementation_plan.md.


## [0.2.19] - 2026-03-28
### Changed
- Validated version update fix for bollded README indicators.


## [0.2.18] - 2026-03-28
### Changed
- Removed redundant GEMINI.md from portable root; relying on template-driven generation.


## [0.2.17] - 2026-03-28
### Changed
- BIOS Optimization: Stripped GEMINI.md redundancies and moved operational protocols to core-guardrails.md.


## [0.2.16] - 2026-03-28
### Changed
- Fixed YAML header for autoharness-protocol.md compliance.


## [0.2.15] - 2026-03-28
### Changed
- Atomic Rule Decomposition, rich metadata extraction for Rules, and global Workflow audit.


## [0.2.14] - 2026-03-28
### Changed
- Automated agent synchronization and sanitization.


## [0.2.13] - 2026-03-28
### Changed
- feat: optimize metadata token usage, fix knowledge graph validation, and inject anti-amnesia protocol


## [0.2.12] - 2026-03-28
### Changed
- Fix: Regenerate catalog post-sync correctly by disabling aggressive line pruning for Python files


## [0.2.11] - 2026-03-28
### Changed
- Refactor publish_agents to regenerate catalog post-sync (with import fix)


## [0.2.10] - 2026-03-28
### Changed
- Fix broken rule reference in app-builder.md


## [0.2.9] - 2026-03-28
### Changed
- Integrate AutoHarness, English Anti-Affirmation Mandate, and fix harnesses whitelist


## [0.2.8] - 2026-03-28
### Changed
- Integrate AutoHarness principles and English Anti-Affirmation Mandate


## [0.2.7] - 2026-03-28
### Changed
- Fix: removed deprecated tier protocol check from verify_agents.py


## [0.2.6] - 2026-03-28
### Changed
- Structural audit: flattened skill metadata, merged triggers into tags, and deprecated tiers


## [0.2.5] - 2026-03-27
### Changed
- Automated agent synchronization and sanitization.


## [0.2.4] - 2026-03-27
### Changed
- Refactor: Consolidate Security, QA, and Audit into `integrity-sentinel`
- Fix: Harmonized broken skill references across all global workflows
- Sync: Clean foundation update with Neural Impact Analysis


## [0.2.3] - 2026-03-27
### Changed
- Integrated advanced analytical protocols, adversarial testing, and completeness mandate


## [0.2.2] - 2026-03-27
### Changed
- Deploy Token-Optimized Context Routing and Neural Task Templates


## [0.2.1] - 2026-03-26
### Changed
- Finalize Neural Impact Analysis logic and README enhancements


## [0.2.0] - 2026-03-26
### Changed
- Integrate 10 Prompt Patterns, Root GEMINI.md, and evals/docs folders


## [0.1.17] - 2026-03-26
### Changed
- v0.0.1 - Logical Integrity & Cross-Platform Pathing Update


## [0.1.16] - 2026-03-26
### Changed
- v0.0.1 - Unified Pillar Patch & Global Sanitization


## [0.1.15] - 2026-03-26
### Changed
- Restore empty local and tasks structures with .gitkeep


## [0.1.14] - 2026-03-26
### Changed
- Prune safe-migration workflow, tasks, and local canons from portable version


## [0.1.13] - 2026-03-26
### Changed
- Prune internal global canons, only export core-architecture.md


## [0.1.12] - 2026-03-26
### Changed
- Deploy enhanced deployment script with selective AI bridges and logging


## [0.1.11] - 2026-03-22
### Changed
- Fix broken rule links in workflows after rule consolidation


## [0.1.10] - 2026-03-22
### Changed
- Integration of Advanced Engineering and Reality Checker principles


## [0.1.9] - 2026-03-21
### Changed
- Update Model Tier Protocol with Transitional Tiering and Mismatch Firewall


## [0.1.8] - 2026-03-21
### Changed
- Flatten canons/local structure to one-level


## [0.1.7] - 2026-03-21
### Changed
- Feat: 100% Automated Workspace Mapping (Rules, Workflows, Scripts, Canons)


## [0.1.6] - 2026-03-21
### Changed
- Fix: Corrected BLACKLIST and hardened script mirroring


## [0.1.5] - 2026-03-21
### Changed
- Audit: Manual cleanup of blacklisted scripts


## [0.1.4] - 2026-03-21
### Changed
- Fix: Hardened script mirroring and explicit blacklist removal


## [0.1.3] - 2026-03-21
### Changed
- Update Foundation: Harmonized workspace map and pruned portable exports


## [0.1.2] - 2026-03-20
### Changed
- Implements Monorepo (Double Lean) hierarchy, JIT SaaS context expansion, and Absolute English linguistic integrity for international export.


## [0.1.1] - 2026-03-20
### Changed
- Patch: Surgical enhancement to project-relocator deep cache clearing tactics


## [0.1.0] - 2026-03-20
### Changed
- **Unified Logic**: Established a clear 4-pillar structure and the 82-file SaaS mapping protocol.


## [0.0.2] - 2026-03-20
### Changed
- Fix sync paths and update v0.0.1



## [0.0.2] - 2026-03-20
### Added
- **Smart Init (No Flags)**: Redesigned `/project-init` to use passive environment detection instead of technical flags.
- **Surgical Context Expansion**: Protocol to "promote" Lean projects to Startup-grade granular structure file-by-file.
- **U2S Mapping**: Unstructured-to-Surgical mapping for info-dumps and monolithic blueprints during init and app building.
- **Legacy Ingestion**: Reverse-Engineered mapping for existing half-finished projects.
- **Consultant Role**: Reframed AI behavior from "Scribe" to "Senior Consultant" via Canon 04 and Interaction Protocols.

## [0.0.1] - 2026-03-19
### Changed
- Surgical deploy and workspace map safety update


## [0.0.0] - 2026-03-19
### Changed
- Clean Reset to v0.0.1
- Update .agents foundation to portable brainvibing (Dual-Canon Patch)
- Added Session Handoff and Atomic Tasking workflows
- Enhanced Protocol for surgical context management

## [0.9.0] - 2026-03-15
### Added
- Initial baseline
- Standardized .agents structure for portability
- Initial suite of 20+ specialized agent skills
