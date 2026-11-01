# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.2.html).

## [Unreleased]

- 

## [0.0.4] - 2026-11-01

### Added
- **Orion Constellation Multi-Project Knowledge Mesh & Supervisory Vault (`core/spoke_mesh.py`, `commands/constellation.py`, `core/memory.py`)**:
  - Added autonomous spoke star discovery (`discover_spokes`) across sibling developer repositories.
  - Added metadata harvesting for DNA states, compliance scores, archetype profiles, and domain context files (`VISION.md`, `MEMORY.md`, `ARCHITECTURE.md`, `BLUEPRINT.md`).
  - Added timestamp-based dirty cache checking (`.orion/working/constellation_cache.json`) to skip unedited repositories during periodic scans.
  - Added `ConstellationVaultExporter` generating unified Obsidian vaults under `constellation/` with portfolio scorecards (`00_Hub/Overview.md`), namespaced notes (`[[Stars/<project>/<file>]]`), and technology concept hubs (`Taxonomies/<tech>.md`).
  - Added unified CLI commands: `orion constellation status`, `orion constellation sync`, and `orion constellation export`.
  - Added comprehensive test suite in `test_spoke_mesh_constellation.py` (4 unit tests).
- **Universal Dynamic Polyglot Version Synchronizer (`core/dna.py`, `commands/foundation.py`)**:
  - Replaced rigid, static manifest chain with `DynamicVersionScanner` and rich `VersionState` / `VersionSink` architecture.
  - Dynamically discovers structured manifests (`package.json`, `pubspec.yaml`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, `build.gradle*`, `deno.json`, `composer.json`, `Makefile`, `CMakeLists.txt`, `Directory.Build.props`, `tauri.conf.json`, `app.json`, `plugin.json`, `VERSION`).
  - Added discovery and atomic syncing for unconventional version files (`version.txt`, `version.json`, `version.yaml`) and `README.md` shields badges and version headers with dependency noise exclusion.
  - Added dynamic mobile/Flutter build number auto-incrementing (`version: 1.0.0+1` -> `1.0.1+2` and Gradle `versionCode 1` -> `2`) with explicit `--build-number <N>` CLI override.
  - Added source code constant discovery and atomic synchronization (`.version("...")`, `version: "..."`, `__version__ = "..."`, `const VERSION = "..."`).
  - Added context roadmap phase milestone sync (`context/01_Product/ROADMAP.md`), foundation metadata sync (`.project_manifest.json`, `.dna.json`), and epigenetic custom sinks.
  - Enforced strict uninitiated greenfield protection (`0.0.0`) preventing fabricated version files or artificial bumps.
  - Added 16 comprehensive universal unit test suites in `test_dna_semver_universal.py`.
- **Google Labs `design.md` DTCG Token Specification Interoperability (`.agents/templates/DESIGN.template.md`, `ui-finish`)**:
  - Upgraded `DESIGN.template.md` to full parity with Google Labs `design.md` W3C DTCG YAML front matter tokens (`tokens.colors`, `tokens.typography`, `tokens.spacing`, `tokens.rounded`, `tokens.elevation`, `tokens.motion`, `tokens.breakpoints`).
  - Added comprehensive standards for corner radii scale, 4-tier elevation surface layering, motion transitions with `@media (prefers-reduced-motion)`, iconography standards, and strict Do's & Don'ts agent behavioral constraints.
- **Internal Workspace Asset Isolation (`.gitignore`)**:
  - Explicitly isolated `/constellation/` and `/.worktrees/` in root `.gitignore`, ensuring internal supervisory star nodes and git worktrees are never committed to public repositories.
- **Unified Project Push Pipeline & Git Pre-Push Hook (`commands/foundation.py`, `core/scanner.py`, `orion.py`)**:
  - Added `orion push` and `orion project push` with 5-Gate pre-flight verification sequence (Security & Secret scan, Test Suite, Living DNA Architecture Audit, Documentary Knowledge Sync & Prose Authenticity, SemVer & Keep a Changelog sync).
  - Added `orion project install-hooks` generating POSIX and MinGW compatible `.git/hooks/pre-push` with non-destructive backup (`pre-push.bak`).
  - Added `orion scan prose` auditing Markdown files against AI tell vocabulary, phrase clusters, binary contrast reversals, and SSOT section duplication with example quote filtering.
  - Added comprehensive test suite in `test_project_push.py` (12 unit tests).
- **Automated Spoke Changelog Seeding & Template Propagation (`commands/foundation.py`, `session-offload`)**:
  - Linked `CHANGELOG.template.md` to deployment seed files and added automatic seeding fallback to `/session-offload` Step 3.6.
- **Anti-Split Stack Formula Master Canon & Unfair Architecture (`canons/ecosystems/flutter/`)**:
  - Added master canon `flutter-anti-split-formula.md` codifying the 5 Pillars of Unfair Flutter (Impeller 120Hz GPU canvas, Rust FFI compute companion, split-domain WasmGC web, local-first Drift SQLite WAL sovereignty, and AOT binary hardening).
  - Refactored `flutter-standards.md` to purge legacy split-stack assumptions (such as syncing between Next.js Web and Flutter Mobile) and mandate 120Hz Impeller framerates and zero-copy FFI memory pointers.
  - Refactored `flutter-init.md` to scaffold `shaders/`, `native/`, and Drift SQLite WAL directories on turn 1.
  - Updated `pubspec.md` micro-canon to blessed Drift, SQLite, and Rust FFI dependencies.
- **Canonical Component Taxonomy & Design System Decision Matrix (`ui-finish`, `DESIGN.template.md`)**:
  - Cataloged ~60 canonical UI primitives across 6 functional domains in `.agents/skills/ui-finish/references/component_taxonomy.md` with multi-platform parity across Web (HTML5/Radix/Tailwind), Flutter (M3), and Android (Jetpack Compose).
  - Defined 4 contextual selection trees (Overlay triage, Data display triage, Form input triage, Navigation triage) and design system archetype pairings (Linear, Carbon, Polaris, Apple HIG) in `.agents/skills/ui-finish/references/component_decision_matrix.md`.
  - Added Section 8.1 "Canonical Component Primitive Contract (Anti-Slop Alignment)" to `.agents/templates/DESIGN.template.md` to bind local project design tokens to verified canonical primitives.
  - Added ad-hoc wrapper soup and modal overuse refusal patterns to `.agents/skills/ui-finish/references/craft_floor.md`.
  - Attributed design system cataloging inspiration to [The Component Gallery](https://component.gallery/) (curated by Iain Bean) across documentation and reference headers.

## [0.0.3] - 2026-10-31

### Added
- **Framework Upgrade & Upstream Deployment Engine (`orion upgrade`, `commands/foundation.py`)**: Added `orion upgrade` (`foundation-upgrade`) with `--check`, `--dry-run`, and `--source` flags for automated, transactional upstream syncing with rollback safety, user asset protection shields, and automated mandate splicing in `AGENTS.md` and `GEMINI.md`.
- **Dynamic Path Resolver & Anti-Brittleness Architecture (`core/paths.py`, `commands/verify_agents.py`)**: Added unified `get_workspace_files()` leveraging `git ls-files` (<50ms execution), promoted pure standard library `GitIgnoreFilter`, added in-place `dirs[:]` traversal pruning, bounded in-memory text cache (`_TEXT_CACHE` LRU), and dynamic SQLite schema and framework discovery.
- **12-Vector Defense-in-Depth Security Suite (`integrity-sentinel`, `audit_vectors.md`, `core/scanner.py`)**: Added dedicated runbooks for AI boundary validation (`ai_llm_attacks.md`), native memory safety (`memory_safety_and_binary.md`), and IPC access control (`desktop_mobile_ipc.md`) with 3-branch classification (`confirmed`, `needs_validation`, `rejected`).
- **Cognitive Scaffolding & Dynamic AST Boundary Engine (`commands/bento_slicer.py`, `tier-execution-protocol.md`)**: Added live AST symbol span resolution, pre-flight syntax checks, task complexity scoring, execution tier recommendations (`BUDGET`, `STANDARD`, `PREMIUM`), and fast-track execution.
- **Ecosystem Templates & Minor Tooling Enhancements**: Added templates for Blueprint and Roadmap strategy pillars (`.agents/templates/`), Android ecosystem standards (Kotlin, Compose, XML views), invariant comment annotations (`INVARIANT [<TAG>]: <WHY>`), non-blocking stdin hook auto-pipe detection, and isolated Tier-2 optional native accelerators (`orjson`, `rapidfuzz`).

### Changed
- **Reconnaissance & Quarantine Refinements**: Refined reconnaissance thresholds to permit inspecting AST skeletons without tier escalation, added concurrency conflict detection to sub-agent delegation, and quarantined agent runtime directories from audit bundles.
- **Cross-Platform & Portability Standards**: Standardized `.gitattributes` to LF line endings, unified PowerShell and POSIX invariants, and synchronized JIT routing tables across root instructions.

### Fixed
- **Parsing, Deployment & Encoding Hardening**: Resolved vision brief parsing truncation, fixed template variable substitution order, corrected setup scaffold paths, eliminated subprocess text encoding ambiguities across hooks, and addressed false positives in ghost reference checks.

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
