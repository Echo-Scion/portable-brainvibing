# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.2.html).

## [Unreleased]

- 

## [0.0.3] - 2026-10-31

### Added
- **Framework Upgrade Command (`orion upgrade`)**:
  - Added `orion upgrade` (`foundation-upgrade`) with `--check`, `--dry-run`, `--source`, and `--force` options to update framework assets from upstream repositories.
  - Added protection shield for user configuration, custom rules, local canons, and `.orion/` state during upgrades.
  - Added automated mandate splicing to update core guardrails in `AGENTS.md` and `GEMINI.md` while preserving custom `## PROJECT-SPECIFIC MANDATES`.
  - Added transactional staging with automated rollback on verification failure.
- **Plain Engineering Language Guidelines (`lessword`, `AGENTS.md`, `GEMINI.md`)**:
  - Added section 3.5 to `lessword` enforcing concise, active verbs (use, fix, check) per ASD-STE100 guidelines to eliminate archaic phrasing and fragmented sentences.
  - Synchronized language guidelines across root instruction files and templates within size limits.
- **Multi-Session Cold-Start Registry (`pre-agent-wake.py`)**:
  - Added session-keyed registry to track cold-start states across concurrent chat sessions without state collisions.
  - Added UTF-8 BOM decoding for non-blocking stdin pipes.
- **Index Reference Verification (`verify_agents.py`)**:
  - Added bidirectional verification ensuring documented tools and references in `AGENTS_INDEX.md` match existing repository files.
- **12-Vector Security Suite & 3-Branch Findings Validator (`integrity-sentinel`, `audit_vectors.md`, `core/scanner.py`, `orion.py`)**:
  - Added security audit modules covering AI boundary validation, native memory safety, and IPC security.
  - Added dedicated runbooks: `ai_llm_attacks.md` (prompt injection, tool argument validation, RAG boundary security), `memory_safety_and_binary.md` (buffer bounds, use-after-free, integer overflow allocations), and `desktop_mobile_ipc.md` (peer authentication, deep-link validation, IPC access control).
  - Expanded diagnostic vectors in `audit_vectors.md` from 9 to 12 categories.
  - Added report schema validation (`orion.py scan audit-validate <json>`) with 3-branch classification (`confirmed`, `needs_validation`, `rejected`).
- **Auto-Pipe Detection for Agent Wake Hooks (`pre-agent-wake.py`, `foundation.py`)**:
  - Added automatic detection for stdin JSON payloads in `pre-agent-wake.py`, enabling hook mode without requiring explicit command-line flags.
  - Synchronized hook definitions across Gemini, Claude Code, and Cursor environment templates.
  - Added `SessionStart` event array to `.agents/hooks.json` and normalized `.gemini/settings.json`.
- **Optional Isolated Accelerators (`performance-optimization.md`, `core/accelerators.py`)**:
  - Added isolated accelerator support (`orjson`, `rapidfuzz`, `tree-sitter`) in user cache directory without modifying workspace dependencies.
  - Added fallback paths to standard library modules when accelerators are absent.
  - Added test suite `test_tier2_accelerators.py` covering standard and accelerated execution paths.
- **Execution Tier Recommendations (`tier-execution-protocol.md`, `AGENTS.md`, `GEMINI.md`)**:
  - Added model tier recommendations (`BUDGET`, `STANDARD`, `PREMIUM`) across turn responses and implementation plans.
- **Scaffolding Optimization Metric (`core/capabilities.py`)**:
  - Added dynamic task complexity scoring to route pre-analyzed tasks to cost-effective model tiers.
- **Dynamic Symbol Boundary Resolution (`commands/bento_slicer.py`)**:
  - Added AST symbol span resolution to dynamically locate modified function and class line ranges on disk before editing.
- **Pre-Flight Syntax and Scope Validation (`commands/bento_slicer.py`)**:
  - Added pre-flight AST syntax checks and file scope verification before running test gates.
- **Task Failure Error Tracing (`commands/bento_slicer.py`)**:
  - Added automatic capture of command failure traces and error context during task verification.
- **Fast-Track Task Execution (`commands/state_machine.py`, `orion.py`)**:
  - Added `fast-track` command for direct single-task execution without multi-stage planning overhead.
- **Differential Code Mapping (`core/scanner.py`, `orion.py`)**:
  - Added `--diff` flag to `orion scan map` to extract symbol skeletons only for modified or untracked files.
- **Cognitive Scaffolding Test Suite (`.agents/scripts/tests/test_scaffolding_evolution.py`)**:
  - Added 8 unit and contract tests verifying scaffolding scoring, hazard detection, live AST symbol resolution, and fast-track boundaries.
- **Project Vision Hydration (`commands/foundation.py`, `orion.py`)**:
  - Added `hydrate-vision` command to generate and update project vision documentation from local models or user input.
  - Enforced draft isolation (`context/VISION.draft.md`) requiring explicit user confirmation before replacing existing vision files.
  - Added zero-overwrite safety preserving existing custom `VISION.md` files unless `--force` is specified.
- **Context Pillar Templates (`.agents/templates/`)**:
  - Added `BLUEPRINT.template.md`, `ROADMAP.template.md`, and updated `STYLE_GUIDE.template.md` for project strategy and architecture structure.
  - Indexed all templates in `.agents/templates/TEMPLATES.md`.
- **Strict TDD Verification Suite (`.agents/scripts/tests/test_vision_hydration_and_fixes.py`)**:
  - Added 6 unit tests validating template references, Git hook portability, CLI routing, draft isolation, and overwrite safety.
- **Architectural Invariant Scanning (`utils/packer.py`)**:
  - Added comment parser for invariant intent tags (`INVARIANT`, `ARCH-DECISION`, `OS-WORKAROUND`, `INTENTIONAL-BYPASS`) across supported languages.
  - Integrated invariant discovery into audit specification bundles under declared architectural invariants.
- **Early-Return and Constraint Analysis (`utils/packer.py`)**:
  - Added explicit handling for conditional return guards and intentional bypasses in web audit specifications.
- **Full Vision Guidance Extraction (`utils/packer.py`)**:
  - Added extraction of core principles, invariants, and non-goals into audit specifications.
- **Custom Invariant Preservation (`core/dna.py`)**:
  - Added preservation of user-defined invariants during project DNA analysis.
- **Code Authenticity Invariant Mandate (`templates/AGENTS.template.md`, `AGENTS.md`, `GEMINI.md`)**:
  - Codified requirement that intentional bypasses and workarounds be documented with `INVARIANT [<TAG>]: <WHY>` annotations.
- **Android Ecosystem Specifications (`.agents/canons/ecosystems/android/`)**:
  - Added reference standards and tooling manifests for Kotlin, Jetpack Compose, XML layouts, and emulator management.

### Changed
- **Reconnaissance Rule Refinement (`tier-execution-protocol.md`)**:
  - Allowed reading AST skeleton maps and inspecting active tasks or targeted functions (<= 100 lines) without triggering tier escalation.
- **Task Delegation Hazard Verification (`core/scanner.py`)**:
  - Added write-set and read-set conflict detection to prevent concurrent execution on shared files.
- **Cross-Platform Shell & Line-Ending Invariants (`AGENTS.md`, `GEMINI.md`, `AGENTS.template.md`)**:
  - Standardized `.gitattributes` (`* text=auto eol=lf`) and `core.autocrlf false` to prevent Windows CRLF byte-mismatch issues.
  - Updated OS invariants to support both Windows PowerShell and POSIX/macOS environments.
  - Synchronized JIT Routing Tables to 34 rows across instruction files.
- **Agent Tooling Directory Quarantine (`utils/packer.py`)**:
  - Added agent runtime metadata folders (`.hermes`) to default ignore lists, preventing agent metadata from entering project audit bundles.
- **Stub Detection Refinement (`utils/packer.py`)**:
  - Exempted code lines tagged with invariant anchors from stub smell warnings.
- **Spoke Deployment Configuration Preservation (`commands/foundation.py`)**:
  - Preserved existing `.dna.json` properties during spoke repository updates.
- **Cross-Platform Git Hook Generation (`commands/foundation.py`)**:
  - Used dynamic Python binary discovery (`command -v python3 || command -v python`) in generated hooks for Linux and macOS compatibility.
- **Workspace Path Resolution in Verifier (`commands/verify_agents.py`)**:
  - Added project root fallback and exempted reflection logs from ghost reference false positives.
- **Observation Tracking Synchronization (`commands/compact.py`, `.security-baseline.json`)**:
  - Added generation-based observation digest and updated security pattern baseline.

### Fixed
- **Vision Document Brief Parsing (`utils/packer.py`)**:
  - Resolved parsing truncation where brief extraction stopped after early section lines.
- **Spoke Deployment Verification**:
  - Verified clean synchronization across downstream target projects with test suites passing.
- **Template Reference in Setup Pipeline (`commands/foundation.py`)**:
  - Corrected template path reference for architecture scaffolds in `execute_setup_pipeline`.
- **Template Variable Replacement (`commands/foundation.py`)**:
  - Fixed variable substitution order to prevent single-brace syntax leaks in generated documentation.
- **Framework Detection Accuracy (`commands/compact.py`)**:
  - Checked `.project_manifest.json` before string matching to ensure accurate architectural tagging in summaries.
- **Tool Reference Cleanup**:
  - Removed outdated tool references across rule and skill documentation.
- **Defensive Subprocess Encoding (`commands/foundation.py`)**:
  - Added explicit UTF-8 text encoding to `orion_ops ingest` subprocess invocations.

## [0.0.2] - 2026-10-27

### Added
- **Dynamic Stack-Aware Deployment (`commands/foundation.py`)**: Implemented dynamic tech stack profiling (`_read_python_deps`, `_detect_ui_project`) and automated micro-canon pruning, preventing hardcoded framework pollution across spoke project deployments.
- **Prose Authenticity & De-AI Engine (`commands/compact.py`)**: Integrated native 26-tell structural AI writing detector and syntax-anchored prose de-slopping (`--humanize` & `--humanize-check`), unified under `.agents/skills/lessword/SKILL.md`.
- **Idempotent SQLite RAG Auto-Migration (`commands/brain.py`)**: Added in-place schema auto-migration for `pages` and `archival_vectors` tables (`superseded_by` and `generation_id` lineage columns), resolving legacy database retrieval crashes.
- **Contract Test Suite Expansion & AST Caching**: Expanded `.agents/scripts/tests/` to 27 test suites (210 unit and contract tests) backed by persistent `(mtime_ns, size)` AST caching in `.orion/verify_ast_cache.json` (<50ms Gate 2 runs).

### Performance & Optimization
- **Zero-Latency Hook Execution (`.agents/hooks.json`)**: Pruned read-only tools (`view_file`, `Read`, `grep_search`) from pre-tool hooks, eliminating Python process startup latency on code navigation.
- **Append-Only Telemetry Streaming (`core/db.py`)**: Replaced $\mathcal{O}(N)$ whole-file JSON rewrites with single-sink append-only `.jsonl` streaming (`mechanical_catches.jsonl`).

### Fixed & Hardened (Consolidated)
- **Resilient UTF-8 Stream & Semantic Emoji Architecture (`core/db.py`, `orion.py`, `hooks/`)**: Implemented auto-invoked `configure_utf8(errors="replace")` on `core.db` import, `-X utf8` and `PYTHONUTF8=1` child process propagation in `orion.py` / `rtk-pre-tool.py`, and `transliterate_emojis()` with `safe_print()` fallback mapping emojis (`🟢`, `🟡`, `🔴`, `⚡`, `🧠`, `•`) to semantic ASCII badges under `NO_EMOJI=1` or Windows CP-1252 console pipes.
- **Engine & Verifier Hardening**: Corrected SQL regex lookahead backtracking in `migration_verifier.py`, directory traversal in `secrets_scan_verifier.py`, `ObservationLedger._append_to_archive` sink in `reflexion.py`, and hook relative CWD path resolution.

## [0.0.1] - 2026-10-16

### Added
- **Master BIOS & Progressive JIT Router (`AGENTS.md`, `GEMINI.md`)**:
  - *Philosophy*: Zero-context bloat; load runbooks only when triggered.
  - *Action*: Implemented Master BIOS with 33-route JIT matrix, Core Guardrails, and Tier-Aware execution.
- **4-Pillar Autonomous Engine (`.agents/scripts/orion.py`)**:
  - *Philosophy*: Zero-friction local-first resilience with minimal runtime overhead.
  - *Action*: Built 4-pillar CLI engine spanning P1 (Python stdlib), P2 (Rust / RTK proxy), P3 (Local Ollama), and P4 (Bun).
- **Orion Knowledge Graph & Living DNA (`core/dna.py`, `commands/brain.py`)**:
  - *Philosophy*: Project context must be deterministic, queryable, and immune to amnesia.
  - *Action*: Implemented SQLite FTS5 lexical search, semantic relation graph, and 5-tier project DNA sequencing.
- **Unified Defense-in-Depth (`rules/`, `skills/`, `canons/`)**:
  - *Philosophy*: Enforce non-negotiable code quality, security bounds, and operational parity.
  - *Action*: Shipped 13 core rule guardrails, 21 specialized domain skills, and multi-framework canons (Flutter, Python, React).
- **Darwinian Reflection Loop (`hooks/`, `evals/`, `OBSERVATIONS.md`)**:
  - *Philosophy*: Agent ecosystems must self-correct from real failure signals.
  - *Action*: Integrated pre-tool interception hooks, mechanical catch telemetry (`.jsonl`), and observation archiving.
