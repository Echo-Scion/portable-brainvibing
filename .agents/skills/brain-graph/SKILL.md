---
name: brain-graph
description: >-
  Manage Brain Graph, knowledge base indexing, FTS5 lexical queries, and Orion operations. Use when ingesting markdown files into the brain graph, querying knowledge nodes, extracting semantic triplets, or checking graph integrity.
---

# Skill: Brain Graph Management & Orion Ops (`brain-graph`)

## Retrieval Diagnostics

Run `python .agents/scripts/orion.py diagnostics` to inspect persisted RAG relevance and faithfulness summaries. Brain sync records one `rag_evaluations` row for each retrieval.

This skill integrates a structural Brain Graph pattern to give AI a persistent, compounding memory across the entire project. It uses a Smart Vibe Coding (Autonomy Matrix) to balance automation with human oversight.

## 1. Operations

### `/orion-ingest <path-or-glob>`
Executes `python .agents/scripts/orion.py orion_ops ingest <path>`.
Classifies a raw markdown file, calculates its `source_sha256`, and updates the `.orion/` graph.

**Phase 1 (Python / Background):**
1. Diff against the existing `.orion/` graph.
2. Analyze topological dependencies (parent concepts ingested before child concepts).
3. Evaluate Autonomy Matrix:
   - `[NEW]`, `[EXTEND]`: Ingests and updates graph indices.
   - `[CONTRADICT]`, `[VIOLATION]`: Under strict autonomy, halts ingestion; under balanced autonomy, records contradictory relationship in graph.
4. Outputs `[TRIPLET_REQUEST]` if successful.

**Phase 2 (IDE Agent Delegation):**
If `[TRIPLET_REQUEST]` is printed:
1. The IDE Agent MUST read the content of each ingested file.
2. Extract 3-5 Subject|Predicate|Object semantic triplets.
3. Inject them into the SQLite graph via `python .agents/scripts/orion.py orion_ops inject_triplets '<json>'`.

### `/orion-query <node_name>`
**CRITICAL ACTION**: Execute `run_command` with `python .agents/scripts/orion.py orion_ops resolve "<node_name>"`. Do not use manual `grep_search`. The resolver automatically injects target file content, forward links, and backlinks into context.

### `/orion-contradict`
Executes `python .agents/scripts/orion.py brain contradictions` to inspect active semantic contradictions, conflicting claims, and source drift across ingested nodes.

## 2. Harmonization Rules

- **Typed Relationships**: Use `page|extends`, `page|contradicts`, `page|implements`. Do not use plain wikilinks.
- **Context Weighting**: Assign `weight: <1-10>` in the frontmatter. High-impact nodes (e.g., core architecture) receive higher weights. `orion.py resolve` prioritizes high-weight nodes during token eviction.
- **Canon Supremacy**: Canons (`.agents/canons/`) always receive `confidence: canonical`. Any context that contradicts a canon is a `[VIOLATION]`.
- **82-File Boundary**: Never write into `context/`. All orion outputs go to `.orion/`.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Knowledge Extraction / Graph Triplets** | .agents/skills/brain-graph/references/knowledge-extraction.md |

