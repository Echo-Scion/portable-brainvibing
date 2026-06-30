---
name: frontend-experience
description: Master orchestrator for UI/UX audits and Frontend debugging.
tags: ['ui', 'ux', 'debugging', 'state management', 'accessibility']
portable: true
---
# Frontend Experience

Your primary role is to audit and debug frontend architecture.
*(Note: For purely aesthetic/animation polish, you MUST execute `view_file .agents/skills/ui-finish/SKILL.md` NOW.)*

## JIT Tool Directives (Execute this FIRST)
1. **Detect Ecosystem**: Check the project root for ecosystem markers (`pubspec.yaml` = Flutter, `package.json` = Node/React, `Cargo.toml` = Rust).
2. **Load Ecosystem Canon**: Based on detected ecosystem, load the relevant canon:
   - **Flutter**: `canons/ecosystems/flutter/flutter-state-map.md`
   - **Web/React**: Apply standard React/HTML state patterns.
   - **Other**: Apply universal 4-state mandate below.

## Component State Map (MANDATORY — Universal)

When creating or auditing a frontend component that interacts with a backend, you MUST ensure all 4 states are handled:

1. **SUCCESS** — Data loaded, display content.
2. **EMPTY** — Data loaded but collection is empty, show empty state message.
3. **ERROR** — Request failed, show actionable error with retry option.
4. **LOADING** — Request in-flight, show skeleton/spinner.

> For framework-specific code patterns implementing this map, load the relevant ecosystem canon.

If you submit a PR or code snippet that only handles the SUCCESS state, you have failed.

## Micro-UX & Form Interaction Standards (Universal)
When auditing interactions, ensure that the user experience is smooth and informative.

**Mandatory UX Checks:**
- **Actionable Error Clarity:** Error displays must not show raw stack traces to the user. Provide actionable steps (e.g., "Network error. Tap to retry.")
- **Disabled States & Explanations:** If a submit button is disabled due to invalid form data or an active async process, visually indicate the disabled state.
- **Form Validation & Inline Feedback:** Inputs should clearly display validation errors beneath them. Ensure "required" indicators are present.
- **Destructive Actions:** Ensure destructive actions (e.g., Delete, Remove) have a confirmation dialog to prevent accidental data loss.
- **Success/Error Notifications:** Trigger appropriate toast/snackbar notifications after form submissions or critical operations.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute iew_file on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Flutter Debugger** | references/flutter-debugger.md |
| **Ux Designer** | references/[[ux-designer]]) |
