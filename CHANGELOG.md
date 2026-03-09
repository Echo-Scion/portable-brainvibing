# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.1.html).

## [Unreleased] - 2026-10-19

### Fixed & Hardened (Panoramic Audit Remediation):
- **Centaur Security & Host Containment (`core/capabilities.py`, `core/sandbox.py`)**:
  - Fixed discrete token evaluation in `run_rtk_proxy()` (`flag in cmd` for `--help`/`-h`) preventing substrings like `test-harness` from triggering help proxying.
  - Enforced fail-closed circuit breaker check before reading stdin in `rtk hook antigravity` to eliminate indefinite hangs on empty input.
  - Restricted `ORION_LLM_URL` to local loopback addresses (`127.0.0.1`, `::1`, `localhost`), switched liveness probe to `GET /api/tags == 200`, and set `stdin=subprocess.DEVNULL, timeout=180`.
  - Stripped host environment paths (`HOME`, `USERPROFILE`, `TMP`, `TEMP`, `PYTHONPATH`) from `SAFE_ENV_VARS` in `sandbox.py` and pinned them strictly to `<workspace>/.scratch/` to prevent host credential leakage.
- **SQLite Database, GraphRAG & Transaction Concurrency (`core/db.py`, `core/memory.py`, `core/orion_graph.py`, `commands/state_machine.py`)**:
  - Enforced `PRAGMA foreign_keys=ON;` and `PRAGMA synchronous=NORMAL;` across SQLite connections.
  - Handled FTS5 shadow table deletion prior to page updates in `ArchivalMemoryManager.insert()` to prevent orphaned index entries.
  - Added missing `communities_au` trigger and purged stale rows before Louvain re-clustering in `orion_graph.py`.
  - Protected vector unpacking with 4-byte alignment checks and guarded cosine similarity against `NaN`/`Inf`.
  - Wrapped state machine step persistence in `BEGIN IMMEDIATE` transactions to prevent colliding step sequences under concurrency.
- **Context Packer & AST Scanner Topology (`core/scanner.py`, `utils/packer.py`)**:
  - Stripped multi-line block comments (`/* ... */`) and bounded line parsing (>2000 chars) in `_count_effective_braces()` to prevent AST brace depth drift.
  - Upgraded hybrid packing algorithm (`balance_into_k_bundles()`) to preserve full code for gravity 1–4 kernel primitives $\le 350$ lines (`sandbox.py`), eliminating blanket skeletonization.
  - Scoped prompt tag neutralization strictly to markdown files (`is_md`) to prevent mutating raw Python string literals.
  - Embedded the full `.agents` Subsystem Catalog, Zenith Benchmarks, 7-Seam Synergy Matrix, and Materiality Floor stopping criteria (score $\ge 85$, 0 blockers) into Gemini Web audit prompts with dual-mode detection (`is_foundation` vs Universal Multi-Platform App).
- **Cross-Shell Portability & Governance Parity (`AGENTS.md`, `.agents/skills/`)**:
  - Synchronized "Code Skeleton First" direct read threshold from 300 to 350 lines in `AGENTS.md`.
  - Replaced compound `&&` shell commands with separate lines in `worker-delegate/SKILL.md` for Windows PowerShell compatibility.
  - Corrected deprecated command alias `compress_memory` to `compress` in `session-offload/SKILL.md`.
  - Clarified vector storage as binary float32 SQLite BLOBs in `meta-agent-admin/SKILL.md`.

## [0.0.1] - 2026-10-16

### Released:
- **Universal Master BIOS & JIT Knowledge Router**: Standardized `AGENTS.md` featuring inlined Core Guardrails, English First Mandate, built-in Lessword protocol, unified response footers, tier-aware session bootstrap, and 35-row JIT auto-pilot knowledge routing.
- **4-Pillar Context Architecture (Lean Knowledge Base)**: Canonical 4-pillar context layout in `context/` (`00_Strategy`, `01_Product`, `02_Creative`, `03_Tech`) with SaaS registry standards and strict boundary enforcement.
- **Centaur Exoskeleton & Fail-Closed Enforcement (`core/capabilities.py`, `core/sandbox.py`, `utils/packer.py`)**: Fail-closed `PreToolUse` hook physically blocking IDE tools (Exit Code 3) upon circuit breaker trip or unhandled exceptions; PEP 578 syscall containment in `SovereignSandbox` intercepting filesystem mutations and subprocess creation outside `_JAIL_ROOT`; 10-minute TTL expiration on adversarial/TDD bypass flags with test-gated failure counter resets; and XML `</artifact>` escaping with imperative directive neutralization across markdown tables and lists.
- **Modular Gateway CLI Architecture (`commands/`)**: Monolithic `commands/brain.py` (5,211 lines) decomposed into dedicated Gateway CLI engines (`commands/compact.py` for 5-tier compaction and Lessword; `commands/rag.py` for hybrid FTS5/vector/graph retrieval and diagnostics; `commands/vault.py` for Obsidian vault exports and Second Brain briefs; and `commands/brain.py` as unified facade router with backward-compatible re-exports), scaling runtime to 25 active engine files and 217 tracked physical files.
- **Orion GraphRAG & Cognitive Kernel (`commands/brain.py`, `commands/rag.py`, `commands/vault.py`)**: Local SQLite FTS5 lexical ranking, packed float32 vector similarity via NanoBrain Ollama embeddings (`nomic-embed-text`), 1-hop bidirectional graph traversal (`entities`, `relations`), wiki note resolution, Obsidian-compatible graph vault export (`brain export-vault` via `commands/vault.py`), and predicate contradiction collision detection (`contradict`).
- **Native 3-Tier Orion Compactor & Lessword Engine (`commands/compact.py`)**: 100% self-contained token compactor unified with chat intensity levels across 3 tiers (`lite`, `full` default pipeline, `ultra` surprisal pruning), featuring `SyntaxAnchorGuard` (collision-free slot isolation for code blocks, backticks, URLs, file paths, `$ENV` vars), `PayloadStreamShaper` (AST hollowing for code, schema sampling for JSON/CSV, span grouping for tracebacks/searches), `ChronologicalSectionDecay` (decay for multi-section logs and memories while protecting sacred anchors), and `SafetyBoundaryEscape` (auto-clarity preservation for destructive SQL/Git/CVE operations).
- **Formal State Machine & Superstep Cyclic Execution Graph (`commands/state_machine.py`)**: 8-phase lifecycle state machine (Scaffold, TDD, Design, Architecture, Backend, Frontend, Polish, Release), LangGraph-style superstep cyclic graphs (`orion.py state_graph`), channel state reducers, and Git-bound non-destructive snapshots (`fsm rollback --restore-code`).
- **Strict TDD & Quality Assurance (`commands/verify_agents.py`, `strict-tdd`)**: Mandatory RED-GREEN-REFACTOR cycle with mechanical rollback on premature code modifications, pre-flight diagnostics, 8-gate mechanical integrity audit (`orion.py verify`), and instruction/context naming linting.
- **Adversarial Verification & AST Security Scanner (`commands/verify_agents.py`, `core/security.py`)**: Delta-scoped mutation testing (`adversarial mutate --diff --fail-fast` / `-x`) probing boundary inputs, concurrency, and fallback paths; CST-based static AST security scanner (`orion.py scan security`) flagging injection patterns, credential leaks, and unsafe calls.
- **Automated Aesthetic & Design Token Validator (`evals/audit_aesthetics.py`)**: Static UI and design token auditing checking design token conformance, micro-interactions, responsive containers, craft floor standards, and accessibility attributes.
- **Cognitive Reflexion & Activity-Based Temporal Pulse (`commands/reflexion.py`)**: Automated Obsidian-style `[[wikilinks]]` graph linking (`linkify`), verbal reflective learning and failure invariant logging (`record`), and 3-stage activity-based pulse consolidation (`Session Pulse`, `Milestone Synthesis`, `Epoch Consolidation`).
- **Rule Eviction & Token Governance (`core/scanner.py`, `commands/state_machine.py`)**: Usage-based rule eviction (`amnesia`), code map outline generation (`scan map`), offensive audit target isolation (`scan targets`), and real-time session token budget monitoring (`budget`, `scan tokens`).
- **Foundation Hub-and-Spoke Lifecycle (`commands/foundation.py`)**: Automated template deployment (`foundation deploy`), AI configuration synchronization (`foundation sync-ai`), and bidirectional upstream learning promotion (`foundation push-upstream`).
- **Universal Context Bundler & Multi-Project Exporter (`utils/packer.py`)**: Multi-project domain bundle exporter (`orion.py pack --gemini-10`, `--lean`, `--all`, `--dir`) generating token-optimized packages for external audits.
- **Modern 21-Domain Skills-Only Ecosystem (`.agents/skills/`)**: Consolidated modular skills covering AI engineering, app lifecycle, API contracts, local RAG graph, cost optimization, data logic, frontend UI/UX, integrity sentinel, lessword compression, palette a11y, project architecture, DevOps operator, SaaS strategist, self-evolution, session offload, strict TDD, systematic debugging, visual craft, worker delegation, and maintainer internals.
- **Cross-Platform Engine Reliability**: Windows CP1252/UTF-8 subprocess decoders, non-blocking stdin deadlock protection, and auto-sync cooldown debounce.
