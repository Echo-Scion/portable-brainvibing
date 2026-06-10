---
name: brain-graph
description: Brain Graph, Knowledge Base, Ingest, Lint, Cross-reference
activation: when user wants to ingest markdown files into the brain graph, query it, or lint it.
version: 0.0.1
---

# Skill: Brain Graph Management (`brain-graph`)

## 🚀 Ecosystem Paradigm Shift
> **Core Directive**: Proactive Oracle: Parses background logs and proactively injects historical solutions into context before an error happens.


## 🧠 Next-Gen Capabilities
> **Graph-RAG Knowledge Mapping**: Discard flat text searching. Extract entities and relationships during ingestion to construct a localized, traversable Knowledge Graph for deep, multi-hop contextual reasoning.


This skill integrates a structural Brain Graph pattern to give AI a persistent, compounding memory across the entire project. It uses a Smart Vibe Coding (Autonomy Matrix) to balance automation with human oversight.

## 1. Operations

### `/orion-ingest <path-or-glob>`
Classifies a raw markdown file, calculates its `source_sha256`, and updates the `.orion/` graph.
**Smart Vibe Coding Flow:**
1. Diff against the existing orion.
2. Auto-commit `[NEW]` pages or simple `[EXTEND]` actions silently.
3. If `[CONTRADICT]` or `[VIOLATION]` occurs, stop and emit a `TRIAGE_REPORT` for human approval.

### `/orion-query <node_name>`
**CRITICAL ACTION**: You MUST execute `run_command` with `python .agents/scripts/orion.py orion_ops resolve "<node_name>"` NOW. Do not use manual `grep_search`. The resolver will automatically inject the target file's content, its forward links, and its backlinks (the graph neighborhood) into your context.

### `/orion-lint`
Checks all ingested sources against the raw files.
- Detects Source Drift (hash mismatch).
- Flags low-confidence contradictions.
- Auto-heals high-confidence minor drifts if autonomy is `balanced` or `high`.

## 2. Harmonization Rules

- **Typed Relationships**: Use `[[page|extends]]`, `[[page|contradicts]]`, `[[page|implements]]`. Do not use plain wikilinks.
- **Context Weighting**: Assign `weight: <1-10>` in the frontmatter. High-impact nodes (e.g., core architecture) receive higher weights. `orion_ops.py resolve` prioritizes high-weight nodes during token eviction.
- **Canon Supremacy**: Canons (`.agents/canons/`) always receive `confidence: canonical`. Any context that contradicts a canon is a `[VIOLATION]`.
- **82-File Boundary**: Never write into `context/`. All orion outputs go to `.orion/`.
