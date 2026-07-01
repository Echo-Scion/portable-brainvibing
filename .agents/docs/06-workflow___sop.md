# VOLUME VI: WORKFLOW / SOP — 10 Standard Operating Procedures

---

## Chapter 11: Complete List of Workflows

### 11.1. `app-lifecycle.md`
**Mega E2E workflow.** 10 steps:
1. Requirements Intake (Interview).
2. Blueprint Generation.
3. Scaffold Database.
4. API Layer.
5. UI Layer.
6. Integration.
7. Testing.
8. Polish.
9. Pre-Deploy.
10. Launch.

### 11.2. `audit-and-test.md`
**Strict TDD Loop** (Red → Green → Refactor) + PR Code Review Checklist.

### 11.3. `auto-context.md`
**Organic Extraction.** If the user repeatedly corrects the AI ("No, I meant X"), the system automatically extracts rule X, formalizes it, and saves it to `orion.db`.

### 11.4. `knowledge-extraction.md`
Instructs the AI to read code files, extract 3-5 Semantic Triplets, and run `orion_ops inject_triplets`.

### 11.5. `knowledge-sync.md`
Internal DevOps: version bumping, integrity verification, Git commits.

### 11.6. `orion-ops.md`
SOP for rebuilding the FTS5 database, querying the graph, and repairing corrupt SQLite state.

### 11.7. `prod-deploy.md`
Pre-production checklist: environment variables, minification, security headers.

### 11.8. `project-migrate.md`
Guide to migrating legacy/brownfield projects to the `.agents` architecture without breaking running systems.

### 11.9. `self-evolve.md`
**Deterministic Reflection Loop.** 4 phases:
1. **Error Extraction**: Extract error traces to XML.
2. **Memory Write**: Write to `LEARNINGS.md`.
3. **Darwinian A/B Evolution**: Fork rules → Benchmark V1 vs V2 → Promote winner.
4. **Pattern Recognition**: Scan `LEARNINGS.md` for recurring patterns → Synthesize new rules/skills/workflows.

### 11.10. `session-offload.md`
**Shutdown Sequence.** 5 steps:
1. **Scratchpad Eviction**: Clean temporary files.
2. **Gated Auto-Commit**: Logic Gate → Security Gate → History Gate before committing.
3. **Memory Compression**: `compress_memory` + `nano_compressor` to shrink logs.
4. **Handoff State**: Write `handoff.md` with Resume Point, Technical State, Anti-Goals.
5. **RTK Metrics**: Report token savings for this session.

---

