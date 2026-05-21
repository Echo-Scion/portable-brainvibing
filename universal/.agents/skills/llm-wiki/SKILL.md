---
name: llm-wiki
description: Wiki, Knowledge Base, Ingest, Lint, Cross-reference, LLM Wiki
activation: when user wants to ingest markdown files into the wiki, query the wiki, or lint it.
version: 1.0.0
---

# Skill: LLM Wiki Management (`llm-wiki`)

This skill integrates Karpathy's LLM Wiki pattern to give AI a persistent, compounding memory across the entire project. It uses a Smart Vibe Coding (Autonomy Matrix) to balance automation with human oversight.

## 1. Operations

### `/wiki-ingest <path-or-glob>`
Classifies a raw markdown file, calculates its `source_sha256`, and updates the `.wiki/` graph.
**Smart Vibe Coding Flow:**
1. Diff against the existing wiki.
2. Auto-commit `[NEW]` pages or simple `[EXTEND]` actions silently.
3. If `[CONTRADICT]` or `[VIOLATION]` occurs, stop and emit a `TRIAGE_REPORT` for human approval.

### `/wiki-query <question>`
Reads `.wiki/index.md` (and uses QMD if available) to synthesize answers from the persistent graph.

### `/wiki-lint`
Checks all ingested sources against the raw files.
- Detects Source Drift (hash mismatch).
- Flags low-confidence contradictions.
- Auto-heals high-confidence minor drifts if autonomy is `balanced` or `high`.

## 2. Harmonization Rules

- **Typed Relationships**: Use `[[page|extends]]`, `[[page|contradicts]]`, `[[page|implements]]`. Do not use plain wikilinks.
- **Canon Supremacy**: Canons (`.agents/canons/`) always receive `confidence: canonical`. Any context that contradicts a canon is a `[VIOLATION]`.
- **82-File Boundary**: Never write into `context/`. All wiki outputs go to `.wiki/`.
