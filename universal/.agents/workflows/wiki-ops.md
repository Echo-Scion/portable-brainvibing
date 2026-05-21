---
description: Step-by-step procedures for operating the LLM Wiki (Ingest, Query, Lint)
---

# Workflow: Wiki Ops (`wiki-ops`)

## 1. `/wiki-ingest <path>`
1. Calculate `source_sha256` of the target file.
2. Classify the file using the Source Taxonomy (Rule, Skill, Canon, Context, etc.).
3. Diff the knowledge against `.wiki/`.
4. **Evaluate Autonomy Matrix**:
   - `[NEW]`, `[EXTEND]`: Execute auto-commit.
   - `[CONTRADICT]`, `[VIOLATION]`: Pause and emit a `TRIAGE_REPORT`. Wait for user approval.
5. Create/update files in `.wiki/` with Typed Relationships in frontmatter.
6. **Mandatory Script Execution**: Run `python .agents/scripts/ingest_wiki.py <path>` to build the mechanical graph, copy sources, and trigger QMD embeddings.
7. (Optional) Run `python .agents/scripts/qmd_wiki_graph.py` to generate visual relationship graphs.

## 2. `/wiki-lint`
1. Read `.wiki/sources/` to get all registered `source_sha256`.
2. Compare hashes with live files in the workspace.
3. Flag **Source Drift** for any mismatch.
4. Scan `.wiki/` for orphans or missing cross-references.
5. Generate a Markdown lint report.
