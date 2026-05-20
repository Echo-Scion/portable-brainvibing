---
activation: model_decision
description: Decision trees for performance optimization and context token usage.

version: 3.0.0
last_updated: 2026-05-20
---

# Performance & LLM Token Optimization

## 1. Code Modularity (The 500-Line Decision Tree)

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

## 2. Application Performance Decision Tree

Before adding complexity for "performance", consult this tree:

```
Q1. Is the UI list long or dynamic?
    ├── YES -> MUST use lazy loading (`ListView.builder` in Flutter, `react-window` in Web).
    └── NO -> Standard column/row is fine.

Q2. Is the data fetching slow or repetitive?
    ├── Does the data change < 1 time per minute? -> Implement Caching (Redis/In-memory).
    ├── Does the data change constantly? -> Use WebSockets/Realtime.
    └── Is it a single user lookup? -> Simple DB query is fine.
```

## 3. QMD Surgical Loading (Token Diet)

Never read a full file to understand a codebase structure.

**ALGORITHM:**
1. **Map First**: Run `python .agents/scripts/code_map.py --dir <target>` to get AST/Skeleton.
2. **Search Second**: Run `grep_search` to find the exact line numbers.
3. **Surgical Read**: If `view_file` is needed, use `StartLine` and `EndLine` to read only the target 50-line block.

## 4. One-Turn Execution (Turn Minimization)
- Group independent tool calls into a single response (Parallel Tool Calling).
- Do not ask for permission to run read-only tools (`list_dir`, `grep_search`). Just run them.
