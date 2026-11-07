---
name: feature-discovery
description: >-
  Use before creating features, building components, or planning changes when requirements leave open non-trivial questions, unstated assumptions, or architectural forks.
core_max_lines: 75
---

# 💡 5-Lens Feature Discovery & Zero-Trust Elicitation (`/feature-discovery`)

This skill combines **Zero-Trust Codebase Reconnaissance** with **Turn-1 5-Lens Creative Expansion** (`@generate-fresh-ideas` + `screen-alternatives`). Never stall momentum with a bare intake questionnaire when you can surface high-leverage blind spots and structural alternatives immediately on Turn 1.

## 1. Look Before You Ask

Before sending your first message, investigate existing context:
1. **Inspect Codebase & State**: Read relevant source files, `context/VISION.md`, `context/00_Strategy/BLUEPRINT.md`, `DESIGN.md`, or previous task handoffs.
2. **Understand the Present State**: Formulate how the affected subsystems work today and what the requested change will touch.
3. **Never Ask What Code Already Answers**: Ground analysis in established architecture. Never ask questions that a quick file read or git log resolves.

## 2. Turn-1 5-Lens Discovery Matrix (Deliver Immediately on Turn 1)

After inspecting the codebase, deliver a compact **5-Lens Discovery Brief** before asking your single highest-leverage fork question:
1. **🔥 Contrarian Assumption Check**: Challenge the default premise—is the requested feature solving a symptom rather than the root workflow bottleneck, or can an existing codebase primitive solve 90% of it with zero new bloat?
2. **📖 Real-World User Scenario (Goal-Based)**: Frame the feature as a concrete user goal (Setup $\to$ Friction moment $\to$ Observable success state), never mechanical UI clicks (`"click the Save button"`).
3. **📊 Evidence, State & Scale Footprint**: Identify what data shapes, boundary counts (`0`, `1`, `1,000+` items), partial-data failures, or `[benchmark metrics]` determine success.
4. **📐 Two Structural Hypotheses (`Alt A` vs. `Alt B`)**: For any user-facing feature, contrast two distinct structural approaches holding tokens constant:
   - `Alt A (Structural Rearrangement)`: Integrates into existing view hierarchy with minimal layout disruption.
   - `Alt B (First-Principles Flow)`: Rebuilds the interaction around the fewest moves for the primary user job.
5. **🎯 What Was Missed (Second-Order Edge Cases)**: Surface the adjacent workflow, recovery state (`undo`, `retry`, `filtered-to-empty`, `offline draft`), or permission boundary the initial prompt overlooked.

### The Dive-In Escape Hatch
If the user did not explicitly invoke `/feature-discovery` or ask for interactive elicitation, they may simply want direct action. Always append a lightweight escape hatch:
> *"Or if you'd rather I just dive in, say so."*

If the user accepts, conclude discovery immediately, state key technical choices in one plain line, and proceed with implementation.

## 3. The Conversation & Single-Question Rule

When conversing:
- **Single Question Ending**: Each turn MUST end with at most ONE focused question. Never attach multi-bullet lists of options unless the user explicitly asks for ideas or is stuck.
- **Plain Vocabulary**: Match the user's terms; eliminate process jargon.
- **Open Questions First**: Let the user describe intent in their own words.

## 4. Sizing the Work & Design Sign-Off

Before moving to implementation planning:
1. **Lay Out Approaches**: Present up to 2–3 defensible architectural approaches with trade-offs.
2. **Draft Design Doc**: Document chosen approach into `context/03_Tech/ARCHITECTURE.md` or a feature specification.
3. **Builder-Check Subagent Review**: Once the written design exists, dispatch a fresh read-only subagent to sanity-check implementation readiness:
   ```markdown
   You are an engineer handed this design document: [DOCUMENT_PATH].
   Report only the questions you'd still need answered before implementing:
   places where you'd have to guess and a wrong guess would matter.
   If nothing important is left, report: "nothing important left".
   ```
4. **Transition Gate**: Once design questions are resolved and user signs off, hand off to `/project-architect` and invoke `/plan` to generate `implementation_plan.md`.
