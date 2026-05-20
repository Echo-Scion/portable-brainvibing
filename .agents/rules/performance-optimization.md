---
activation: model_decision
description: Decision trees for performance optimization, token usage, and Bolt-level speed enforcement.

version: 4.0.0
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

## 2. Code Modularity (The 500-Line Decision Tree)

Context bloat kills AI capability. Use this decision tree when modifying files:

```
Q1. Does the file exceed 500 lines?
    ├── YES -> MANDATORY REFACTOR. Proceed to Q2.
    └── NO -> Safe to edit.

Q2. How should the file be split?
    ├── Is it a UI file? -> Extract sub-widgets (e.g., `_HeaderWidget`) into separate files in a `widgets/` folder.
    ├── Is it logic + UI? -> Extract logic into a controller/provider file.
    └── Is it a mega-service? -> Split by domain (e.g., `AuthService`, `UserService`).
```

*Actionable Command*: Run `python .agents/scripts/token_audit.py` to identify ghost tokens.

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

After implementing a performance fix, do NOT log routine work. Only record critical learnings in `.wiki/PERFORMANCE_LEARNINGS.md`:

```
REQUIRED OUTPUT FORMAT:
## YYYY-MM-DD - [Title]
**Learning:** [Codebase-specific bottleneck or failed optimization insight]
**Action:** [How to apply this pattern next time]
```

## 6. QMD Surgical Loading (Token Diet)

Never read a full file to understand a codebase structure.

**ALGORITHM:**
1. **Map First**: Run `python .agents/scripts/code_map.py --dir <target>` to get AST/Skeleton.
2. **Search Second**: Run `grep_search` to find the exact line numbers.
3. **Surgical Read**: If `view_file` is needed, use `StartLine` and `EndLine` to read only the target 50-line block.

