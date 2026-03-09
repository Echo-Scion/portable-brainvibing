---
name: frontend-experience
description: >-
  Orchestrates frontend architecture audits, 4-state component lifecycle, and UI debugging. Use when auditing frontend components, debugging UI state anomalies, verifying form interactions, or testing browser/widget trees.
---
# Frontend Experience

Your primary role is to audit and debug frontend architecture.
*(Note: For purely aesthetic/animation polish, you MUST execute `view_file .agents/skills/ui-finish/SKILL.md` NOW.)*

## JIT Tool Directives (Execute this FIRST)
1. **Detect Ecosystem**: Check the project root for ecosystem markers (`pubspec.yaml` = Flutter, `package.json` = Node/React, `Cargo.toml` = Rust).
2. **Load Ecosystem Canon**: Based on detected ecosystem, load the relevant canon:
   - **Flutter**: `canons/ecosystems/flutter/flutter-state-map.md`
   - **Web/React**: Apply standard React 19 / Server Component state patterns and modern hooks.
   - **Other**: Apply universal 4-state mandate below.

## 🛠️ Mechanical Verification & Lint Gate (Hard Gate)

Before marking any frontend task complete or approving a UI pull request, you MUST execute mechanical linters via `run_command` and achieve `Exit Code 0`:

1. **Static Analysis & Type Integrity**:
   - **Flutter**: Execute `flutter analyze` or `dart analyze`. Zero issues allowed.
   - **Web / React**: Execute `npm run lint` or `npx eslint .`. Zero lint errors allowed.
2. **Automated Aesthetic Linter**:
   - Execute `python .agents/evals/audit_aesthetics.py --dir <target_dir>`.
   - Rejects hardcoded generic colors (`Colors.red`, inline generic hexes) and validates responsive primitives. Must return `Exit Code 0`.
3. **Test Suite Verification**:
   - Execute `flutter test` or `npm test` covering the modified components. Must return `Exit Code 0`.

## 🔍 UI Testing: Reconnaissance-then-Action Pattern
When writing UI automation scripts (Playwright, Puppeteer, Integration Tests), do NOT blindly guess DOM selectors or widget keys.
1. **Wait for Network Idle**: Dynamic apps must finish JS execution (`wait_for_load_state('networkidle')` or pump widget frames).
2. **Reconnaissance**: Read the rendered DOM/Tree or capture a screenshot FIRST.
3. **Discover**: Identify accurate selectors (`role=`, `text=`, semantic IDs) from the actual rendered state.
4. **Action**: Execute interactions only using confirmed, discovered selectors.
Never attempt to interact with the DOM before the network is idle.

## Component State Map (MANDATORY — Universal)

When creating or auditing a frontend component that interacts with a backend, you MUST mechanically verify all 4 states are implemented in code:

1. **SUCCESS** — Data loaded, display content.
2. **EMPTY** — Data loaded but collection is empty, show dedicated empty state message.
3. **ERROR** — Request failed, show actionable error with retry callback.
4. **LOADING** — Request in-flight, show skeleton shimmer or spinner.

> **Verification Action**: Use `grep_search` on the target component file to verify that branches for error, empty, and loading states are physically present in the widget/component tree. If you submit or approve a component that only handles the SUCCESS state, you have violated protocol.

## Micro-UX & Form Interaction Standards (Universal)
When auditing interactions, verify mechanical compliance:

- **Actionable Error Clarity**: Error displays must not expose raw system stack traces or uncaught exception strings. Provide clear recovery actions (e.g., "Network error. Tap to retry.").
- **Disabled States During In-Flight Requests**: Form submit buttons MUST be mechanically disabled (`disabled={isLoading}` or `onPressed: isLoading ? null : ...`) while async requests are active to prevent double-submit anomalies.
- **Form Validation & Inline Feedback**: Inputs must display validation error text inline below the field upon validation failure.
- **Destructive Actions**: Irreversible operations (Delete, Reset, Purge) MUST be gated by a confirmation modal or alert dialog.
- **Notifications**: Critical actions must trigger feedback toast/snackbar upon completion or failure.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Flutter Debugger** | .agents/canons/ecosystems/flutter/flutter-debugger.md |
| **UX Designer** | .agents/skills/frontend-experience/references/ux-designer.md |
