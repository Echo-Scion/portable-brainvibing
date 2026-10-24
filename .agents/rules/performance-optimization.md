---
activation: model_decision
description: Decision trees for performance optimization, token usage, and Bolt-level speed enforcement.

version: 0.0.1
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
1. **Files <= 350 lines**: Safe to edit directly in a single `view_file` call.
2. **Files 350–500 lines**: Advisory warning during `scan map`/`scan tokens`. Recommend module extraction once current feature tests pass (`GREEN -> REFACTOR` phase).
3. **Files > 500 lines**: Prioritize extracting sub-modules, controllers, or domain services during the refactoring step.

*Actionable Command*: Run `python .agents/scripts/orion.py scan tokens` to identify ghost tokens.

## 2.1 Code Skeleton First (Zero Contiguous Paging)
For files >350 lines, run `python .agents/scripts/orion.py scan map <file>` to obtain exact symbol spans, then call `view_file` with exact `StartLine` and `EndLine`. Never read large files in sequential contiguous chunks. Non-contiguous symbol reads are permitted.

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

Never read a full file to understand a codebase structure.

**ALGORITHM:**
1. **Map First**: Run `python .agents/scripts/orion.py scan map --dir <target>` to get AST/Skeleton.
2. **Search Second**: Run `grep_search` to find the exact line numbers.
3. **Surgical Read**: If `view_file` is needed, use `StartLine` and `EndLine` to read only the target 50-line block.

## 7. Anti-Latency Execution Discipline (Zero Background Stall)

Agents MUST eliminate the four operational latency traps during file inspection and editing:
1. **Scoped Directory Traversal**: Agents MUST NEVER execute unconstrained `os.walk('.')` across the workspace root without excluding `.scratch`, `scratch`, `.git`, `.orion`, `.worktrees`, `node_modules`, and `__pycache__`.
2. **Synchronous Timeout Ceiling**: When executing synchronous repository or verification CLI commands via `run_command`, agents MUST set `WaitMsBeforeAsync` to `10000` (10s ceiling) to prevent premature background task promotion and multi-turn wait cycles.
3. **Batched Edit & Single Diff Discipline**: Agents MUST coalesce edits on a target file into minimal `replace_file_content` calls (`AllowMultiple=true` when applicable) and run `git diff` at most once after all edits complete.
4. **Delta-Scoped Verification Gate**: Agents MUST run `python .agents/scripts/orion.py verify --fast` for rapid iterative validation, running full `verify` ONLY when modifying `.agents/` internals, SQLite schemas, routers (`AGENTS.md` / `GEMINI.md`), or `VERSION`. Pure root documentation edits (`README.md`, `CHANGELOG.md`) MUST skip full-system verification.

### 7.1. Tier-Aware Batch-Edit Protocol (2-Turn Maximum vs Bento Sequential)

When implementing multi-file changes or multi-section refactors, agents MUST select the execution strategy appropriate to their model tier:
1. **PREMIUM Tier (Thinking / Opus - 2-Turn Maximum)**:
   - **Turn 1 (Parallel Inspection)**: Execute all required `view_file` calls in parallel in a single turn with exact line spans from `orion.py scan map`.
   - **Turn 2 (Parallel Batch Replacement & Verification)**:
   - Execute all `replace_file_content` calls in parallel in the second turn.
   - Run the single verification pass (`python .agents/scripts/orion.py verify --fast` for delta gates or `verify` for system mods).
2. **BUDGET / STANDARD Tier (Flash / Sonnet / Android Studio - Bento Sequential)**:
   - Slice implementation plan into atomic cards via `python .agents/scripts/orion.py bento slice <plan.md>`.
   - Execute one atomic Bento Action Card at a time (`.orion/working/ACTIVE_TASK.md`).
   - Run verification gate (`python .agents/scripts/orion.py bento next --verify`) before proceeding to the next card to prevent line-shift corruption and hallucinated replacements.
3. **Zero Blind Binary Search (All Tiers)**: Never use identical string replacement (`+0 -0`) or probe edits to guess line numbers. Always obtain line numbers mechanically via AST code mapping (`orion.py scan map`) or search.

