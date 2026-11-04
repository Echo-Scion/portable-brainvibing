---
name: feature-discovery
description: >-
  Use before creating features, building components, or planning changes when requirements leave open non-trivial questions, unstated assumptions, or architectural forks.
---

# 💡 Socratic Feature Discovery & Zero-Trust Elicitation (`/feature-discovery`)

You are skilled at building what you believe your human partner wants, but that belief is often thinner than it feels. This skill acts as the **Goldfish Zero-Trust Elicitation** phase: discovering what they actually want, interrogating edge cases, and exposing hidden assumptions before durable architecture or code is generated.

## 1. Look Before You Ask

Before sending your first message, investigate existing context:
1. **Inspect Codebase & State**: Read relevant source files, `context/VISION.md`, `context/00_Strategy/BLUEPRINT.md`, or previous task handoffs.
2. **Understand the Present State**: Formulate how the affected subsystems work today and what the requested change will touch.
3. **Never Ask What Code Already Answers**: Ground questions in established architecture. Never ask questions that a quick file read or git log resolves.

## 2. Your First Response

Move the work forward concisely (target ~150–200 words):
- **If Requirements are Already Stated** (spec, plan, detailed request): Echo the core intent in your own words (what they want, who it's for, and why). State any non-obvious constraints, conflicts, or simpler paths discovered during inspection. End with one line inviting corrections, followed by ONE focused question about the biggest open fork.
- **If Request is Open / Brief**: Ask ONE open question about the single biggest thing the request leaves unsettled whose answer would most change what gets built. Explain *why* the answer matters.

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
