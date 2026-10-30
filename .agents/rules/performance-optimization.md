---
activation: model_decision
description: Decision trees for performance optimization, token usage, and Bolt-level speed enforcement.

version: 0.0.3
last_updated: 2026-05-20
---

# Performance & Speed Optimization (Bolt Protocol)

## 1. Bolt Protocol: Speed vs Readability (Strict Mandate)

Before implementing ANY performance fix, pass this gate:
1. **Measurable?** [YES/NO] -> If NO, abort. No micro-optimizations.
2. **Readable?** [YES/NO] -> If NO, abort. Readability > Speed.
3. **Scope?** [LINES] -> Must be < 50 lines. No architectural rewrites.

**Forbidden Actions:**
- Do NOT modify `package.json` or `tsconfig.json` for "speed".
- Do NOT add dependencies without explicit User permission.
- Do NOT optimize cold paths (code run rarely).

## 2. Code Modularity (The Soft Modularity Guideline)

Context bloat degrades model attention. Use this guideline when editing code:
1. **Files <= 800 lines**: Safe to inspect directly in a single `read_file` call (or targeted line ranges).
2. **Files 800–1200 lines**: Advisory warning during `scan map`/`scan tokens`. Recommend module extraction once current feature tests pass (`GREEN -> REFACTOR` phase).
3. **Files > 1200 lines**: Prioritize extracting sub-modules, controllers, or domain services during the refactoring step.

*Actionable Command*: Run `python .agents/scripts/orion.py scan tokens` to identify ghost tokens.

## 2.1 Code Skeleton First (Zero Contiguous Paging)
For files >800 lines, run `python .agents/scripts/orion.py scan map <file>` to obtain exact symbol spans, then call `read_file` with exact `StartLine` and `EndLine`. Never read large files in sequential contiguous chunks. Non-contiguous symbol reads are permitted.

## 3. Application Performance Decision Tree

Before adding complexity for "performance", consult this tree:

```
Q1. Is the UI list long or dynamic?
    ├── YES -> MUST use virtualization (`ListView.builder` / `react-window`).
    └── NO -> Standard column/row is fine.

Q2. Is the data fetching slow or repetitive?
    ├── N+1 Queries detected? -> MUST batch or use SQL JOINs.
    ├── Does the data change < 1 time per minute? -> Implement Caching.
    └── Is it a single user lookup? -> Ensure DB index exists.

Q3. Is the main thread blocked?
    ├── Heavy computation? -> Move to WebWorker / Isolate.
    ├── Frequent UI events (scroll/search)? -> MUST debounce/throttle.
    └── O(n^2) nested loops? -> MUST refactor to O(n) Hash Map lookup.
```

## 4. Frontend & Backend Target Profiles

If instructed to find performance wins, target these specific patterns:

**Frontend Targets:**
- Missing `React.memo()` or un-memoized heavy computations (`useMemo`).
- Unoptimized images (missing lazy loading, wrong formats).
- Missing code-splitting for large route components.

**Backend Targets:**
- Missing database indexes on `WHERE` clause fields.
- Synchronous operations that could be asynchronous (`Promise.all`).
- Missing early returns in deep conditional logic.

## 5. Persistent Learning (Post-Mortem Protocol)

After implementing a performance fix, do NOT log routine work. Only record critical learnings in `.orion/PERFORMANCE_LEARNINGS.md`:

```
REQUIRED OUTPUT FORMAT:
## YYYY-MM-DD - [Title]
**Learning:** [Codebase-specific bottleneck or failed optimization insight]
**Action:** [How to apply this pattern next time]
```

## 6. Keyword Surgical Loading (Token Diet)

The Agent MUST NEVER read an entire file solely to locate a symbol or understanding structure.

**ALGORITHM:**
1. **Map First**: Run `python .agents/scripts/orion.py scan map --dir <target>` to get AST/Skeleton.
2. **Search Second**: Run `rtk grep "<pattern>" <target>` to find exact line numbers.
3. **Surgical Read**: When `read_file` is needed, use `StartLine` and `EndLine` to read only the target block.

## 7. Anti-Latency Execution Discipline (Zero Background Stall)

Agents MUST eliminate the four operational latency traps during file inspection and editing:
1. **Scoped Directory Traversal**: Agents MUST NEVER execute unconstrained `os.walk('.')` across the workspace root without excluding `.scratch`, `scratch`, `.git`, `.orion`, `.worktrees`, `node_modules`, and `__pycache__`.
2. **Synchronous Timeout Ceiling**: When executing synchronous repository or verification CLI commands via `run_command`, agents MUST set `WaitMsBeforeAsync` to `10000` (10s ceiling) to prevent premature background task promotion and multi-turn wait cycles.
3. **Batched Edit & Single Diff Discipline**: Agents MUST coalesce edits on a target file into minimal native file-editing calls (`edit_file`) and run `git diff` at most once after all edits complete.
4. **Delta-Scoped Verification Gate**: Agents MUST run `python .agents/scripts/orion.py verify --fast` for rapid iterative validation, running full `verify` ONLY when modifying `.agents/` internals, SQLite schemas, routers (`AGENTS.md` / `GEMINI.md`), or `VERSION`. Pure root documentation edits (`README.md`, `CHANGELOG.md`) MUST skip full-system verification.

### 7.1. Tier-Aware Batch-Edit Protocol (2-Turn Maximum vs Bento Sequential)

When implementing multi-file changes or multi-section refactors, agents MUST select the execution strategy appropriate to their model tier:
1. **PREMIUM Tier (Thinking / Opus - 2-Turn Maximum)**:
   - **Turn 1 (Parallel Inspection)**: The Agent MUST execute all required file-reading calls (`read_file`) in parallel in a single turn with exact line spans from `orion.py scan map`.
   - **Turn 2 (Parallel Batch Replacement & Verification)**:
   - Execute all native file-editing calls (`edit_file`) in parallel in the second turn.
   - Run the single verification pass (`python .agents/scripts/orion.py verify --fast` for delta gates or `verify` for system mods).
2. **BUDGET / STANDARD Tier (Flash / Sonnet / Android Studio - Bento Sequential)**:
   - Slice implementation plan into atomic cards via `python .agents/scripts/orion.py bento slice <plan.md>`.
   - Execute one atomic Bento Action Card at a time (`.orion/working/ACTIVE_TASK.md`).
   - Run verification gate (`python .agents/scripts/orion.py bento next --verify`) before proceeding to the next card to prevent line-shift corruption and hallucinated replacements.
3. **Zero Blind Binary Search (All Tiers)**: Never use identical string replacement (`+0 -0`) or probe edits to guess line numbers. Always obtain line numbers mechanically via AST code mapping (`orion.py scan map`) or search.

## 8. The 3-Tier Execution & Accelerator Model (Zero-Pip Baseline)

`.agents` enforces a strict 3-tier capability and execution model to ensure universal portability across polyglot repositories without dependency contamination:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Tier 0: Sovereign Floor (Mandatory Baseline — 100% Zero-Pip)           │
│ • Python 3.10+ Stdlib & SQLite3 (WAL + FTS5 Lexical Search)            │
│ • Zero external pip dependencies; runs anywhere without installation   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Accelerated by
┌───────────────────────────────────▼────────────────────────────────────┐
│ Tier 1: OS-Level Sovereign Binaries (Pillars 2–4 on System PATH)       │
│ • RTK (Rust CLI Token Proxy) & ast-grep (Rust Polyglot Structural AST) │
│ • difftastic (AST diffing), gitleaks (secret scan), jujutsu (VCS FSM)  │
│ • Ollama / Local AI REST API & Bun Fast Runtime / Sandbox              │
│ • Zero Python GIL bottlenecks, <5ms cold-start, single immutable bin   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Accelerated by
┌───────────────────────────────────▼────────────────────────────────────┐
│ Tier 2: Optional Ephemeral Accelerators (Global ~/.agents/cache/venv)  │
│ • sqlite-vec (SIMD vector KNN C-extension inside SQLite WAL)           │
│ • model2vec (Ultra-fast static CPU embeddings without PyTorch)         │
│ • tokenizers (Exact HuggingFace Rust BPE token budgeting)              │
│ • duckdb (Stateless in-memory OLAP query engine for telemetry JSONL)   │
│ • orjson (Ultra-fast JSON I/O, 5x-10x throughput)                      │
│ • rapidfuzz (C++ Levenshtein distance & fuzzy string matching)         │
│ • tree-sitter (Concrete syntax tree analysis across polyglot trees)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.1. Rules of Engagement & Isolation Contract

1. **Never Require Pip on Bootstrap**: `python .agents/scripts/orion.py verify_agents` and `setup` MUST execute with Exit Code 0 on a virgin OS with only standard Python 3.10+.
2. **Prioritize OS-Level Binaries over Python Wheels**: Prefer standalone Rust/Go/Zig binaries (`rtk`, `ast-grep`, `bun`) over Python packages that require C-wheel compilation or venv management.
3. **Isolation Contract for Tier 2 Wheels**:
   - **Global User Cache Only**: Optional wheels MUST be installed in the isolated user cache (`~/.agents/cache/venv` or managed via `uv`). NEVER create or modify a `.venv` inside the project workspace.
   - **Zero Host Contamination**: NEVER write to, modify, or pollute the host application's active virtual environment (`sys.prefix == sys.base_prefix`).
   - **Universal Graceful Degradation**: Every call to a Tier 2 accelerator MUST be wrapped in a fallback contract (`try: import orjson as json except ImportError: import json`). The engine MUST operate seamlessly at Tier 0 if Tier 2 is absent.


