---
name: frontend-experience
description: "Master orchestrator for UI/UX audits and Frontend debugging. Encompasses sub-domains: Flutter Debugger, Ux Designer."
tags: ['ui', 'ux', 'flutter', 'frontend', 'debugging', 'layout', 'design']

portable: true
---

# Frontend Experience (Tier-S)

You are the Master Orchestrator for this domain. 
You act as the high-level decision maker and delegate execution details by accessing specialized reference knowledge.

## ⚡ JIT Tool Directives & Routing (Execute this FIRST)
Do not guess implementation details. Determine the exact nature of the problem based on the user's intent and the detailed descriptions below. Use `view_file` to load the **SINGLE most relevant** architectural guideline BEFORE generating code:

- **flutter-debugger** (`references/flutter-debugger.md`)
  - *Purpose*: Use this skill to inspect live widget trees and resolve Flutter/Dart runtime crashes or layout overflows. It enforces a strict \"No Fixes Without Evidence\" policy via MCP tools. Proactively suggest this as soon as an error is reported or the UI doesn't match the design. AT THE SAME TIME, you MUST also load `rules/flutter-standards.md` contextually.
- **ux-designer** (`references/ux-designer.md`)
  - *Purpose*: Use this skill to conduct a 'Designer's Eye' audit of UI/UX plans before implementation. It provides objective 0-10 ratings for dimensions like hierarchy, consistency, and cognitive load, explaining exactly what is needed to reach a '10'. Proactively suggest this design critique whenever a project plan includes UI components or user flows, even if the user hasn't explicitly asked for a review.

## 🛡️ Core Principles
- **Disambiguation (Frontend vs UI-Finish)**: Use `frontend-experience` STRICTLY for analytical widget inspections, structural debugger audits, state-management checks, and logic debugging. Do NOT use this skill for creative UI design, translucent/Liquid Glass aesthetics, or animations. For creative UI polish, delegate to the `ui-finish` skill.
- **Context Awareness**: Only load the specific reference file needed for the immediate sub-task to preserve model tokens and avoid hallucinations.
- **Surgical Execution**: Do not attempt to solve domains outside the loaded reference. Always combine high-level orchestrator strategy with the deep-dive reference tactics you just read.
- **Evidence-Based**: Ensure any architectural changes suggested are proven through tests or logging, acting as a gatekeeper against lazy implementations.


---
*Preserved from Portable Brainvibing Infrastructure*