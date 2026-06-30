---
description: Step-by-step procedures for operating the Brain Graph (Ingest, Query, Lint)
---

# Workflow: Brain Graph Ops (`orion-ops`)

## 1. `/orion-ingest <path>`
1. Calculate `source_sha256` of the target file.
2. Classify the file using the Source Taxonomy (Rule, Skill, Canon, Context, etc.).
3. **Analyze Topological Dependencies**: Identify parent concepts and ensure they are ingested/parsed before this child concept.
4. Diff the [knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/[knowledge.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/meta-agent-admin/references/knowledge.md)) against `.orion/`.
4. **Evaluate Autonomy Matrix**:
   - `[NEW]`, `[EXTEND]`: Execute auto-commit.
   - `[CONTRADICT]`, `[VIOLATION]`: Pause and emit a `TRIAGE_REPORT`. Wait for user approval.
5. Create/update files in `.orion/` with Typed Relationships in frontmatter.
6. **CRITICAL ACTION (Agent-OS Index)**: If the ingested file is a rule or standard, you MUST append it to `.agents/rules/[RULES_INDEX](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/[RULES_INDEX.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/rules/RULES_INDEX.md)).md` NOW. You MUST automatically generate a single-sentence description. If no description can be perfectly inferred, explicitly ask the user: *"New standard needs an index entry. Suggested description: [draft]. Accept this description? (yes / or type a better one)"*. Keep descriptions extremely lightweight to aid AI context routing (e.g., `- path/to/rule.md: Enforces Zod schemas`).
7. **CRITICAL ACTION**: Execute `run_command` with `python .agents/scripts/orion.py orion_ops ingest <path>` NOW to build the mechanical graph and copy sources. You MUST check the exit code and terminal output. If it fails or warns, STOP execution and log the error.

## 2. `/orion-lint`
1. Read `.orion/sources/` to get all registered `source_sha256`.
2. Compare hashes with live files in the workspace.
3. Flag **Source Drift** for any mismatch.
4. Scan `.orion/` for orphans or missing cross-references.
5. Generate a Markdown lint report.
