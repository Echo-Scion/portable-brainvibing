# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v0.0.2.html).

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
- **Engine & Verifier Hardening**: Corrected SQL regex lookahead backtracking in `migration_verifier.py`, directory traversal in `secrets_scan_verifier.py`, `ObservationLedger._append_to_archive` sink in `reflexion.py`, and hook relative CWD path resolution.

## [0.0.1] - 2026-10-16

### Added
- Initial Commit
