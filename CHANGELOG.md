# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5] - 2026-11-02

### Added
- Adaptive project setup across new, existing, and upgrading workspaces with non-destructive section merging.
- Automated UI theme token harvesting and `DESIGN.md` catalog pruning (`orion design infer` and `orion design select`).
- Knowledge graph export and bidirectional wikilinks in multi-project `Constellation` vaults.
- Natural-language agent prompt reference in `README.md` for common setup and maintenance workflows.

### Changed
- Unified `AGENTS.md` as the single canonical instruction file with lightweight `@AGENTS.md` pointer adapters (`GEMINI.md`, `CLAUDE.md`).
- Expanded root documentation to 8 core subsystems with unified CLI and chat prompt reference.
- Suppressed terminal console popups during background hook execution on Windows.
- Updated `orion dna semver` and `/session-offload` to track all unreleased changes since the last version tag.
- Standardized concise, outcome-focused changelog formatting across templates, session handoffs, and version compaction.

## [0.0.4] - 2026-11-01

### Added
- Multi-project `Constellation` portfolio mesh (`orion constellation status|sync|export`) with sibling repository discovery and Obsidian vault projection.
- Polyglot version synchronizer (`orion dna semver|bump`) across manifests, mobile build numbers, badges, and roadmap milestones.
- W3C DTCG design token specification support in `DESIGN.md` covering colors, typography, spacing, elevation, and motion.
- Unified pre-push verification pipeline (`orion push`, `orion project install-hooks`) and prose authenticity scanner (`orion scan prose`).
- Canonical UI component taxonomy and decision matrix across Web, Flutter, and Android.
- Full-stack Flutter architectural canons covering Impeller 120Hz rendering, local SQLite WAL storage, and native FFI boundaries.

## [0.0.3] - 2026-10-31

### Added
- Transactional framework upgrade CLI (`orion upgrade`) with dry-run previews, rollback safety, and user asset protection.
- Defense-in-depth security audit runbooks covering AI prompt boundaries, native memory safety, and desktop/mobile IPC.
- Sequential Bento task slicing with AST symbol boundary resolution and model tier recommendations.
- Blueprint, roadmap, and Android ecosystem templates alongside optional isolated Tier-2 native accelerators.

### Changed
- Standardized LF line endings and cross-platform shell portability across Windows PowerShell and POSIX environments.

### Fixed
- Resolved vision brief truncation, template variable ordering, and subprocess UTF-8 encoding edge cases.

## [0.0.2] - 2026-10-27

### Added
- Tech-stack auto-detection during deployment to prune unrelated framework canons in downstream projects.
- Prose de-slopping and AI writing pattern detector (`orion compact --humanize`).
- Automatic SQLite knowledge graph schema migration for legacy workspace databases.

### Changed
- Reduced pre-tool hook latency on read-only operations and switched catch telemetry to append-only JSONL streaming.

### Fixed
- Hardened Windows CP-1252 console output with UTF-8 stream configuration and ASCII badge fallbacks under `NO_EMOJI=1`.

## [0.0.1] - 2026-10-16

### Added
- Initial release of Portable Brainvibing (`.agents`) with JIT knowledge routing and core execution guardrails.
- Unified zero-pip `orion.py` CLI gateway backed by Python 3.10+ stdlib, SQLite3 WAL, and optional Rust/Ollama/Bun pillars.
- Local hybrid RAG knowledge graph with FTS5 lexical search and 5-tier Project DNA architecture auditing.
- Core rule library, domain skills, and multi-framework canons for Flutter, Python, and React.
