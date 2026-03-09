# Visual Engineering & Inclusive Prompts

## 🎭 Inclusive Visual Engineering (Tier-S)
When generating prompts for image/video models:
- **Analyze Brief**: Identify the core human story and potential systemic biases.
- **Annotation Framework**:
    - `[SUBJECT]`: Demographics, specific physical traits, authentic attire.
    - `[ACTION]`: Organic, non-stereotypical movements.
    - `[CONTEXT]`: Authentic geographical architecture, correct lighting for deep melanin.
    - `[CAMERA SPEC]`: Lenses, angles, resolution.
- **Negative Constraints**: Explicitly exclude "generic smiles, excessive saturation, stereotypes, logos."

## ✨ Delightful Micro-Interactions
- **Tactile Feedback**: Use restrained `AnimatedScale` (scale(0.98), 150ms ease-out without bouncy overshoot).
- **Visual Cues**: Replace generic errors with helpful feedback and subtle confetti or haptic triggers on success.

---
*Derived from Antigravity Skills Archive & Legacy Standards*

## 📄 The DESIGN.md Specification
When structuring UI visual identity, use the `DESIGN.md` format. It combines machine-readable design tokens (YAML front matter) with human-readable design rationale (markdown prose).

**Format Example:**
```md
---
name: ComponentName
colors:
  primary: "#1A1C1E"
typography:
  h1:
    fontFamily: Public Sans
---

## Overview
Architectural Minimalism meets Journalistic Gravitas.

## Colors
The palette is rooted in high-contrast neutrals.
- **Primary (#1A1C1E):** Deep ink for headlines and core text.
```

**Philosophy:**
- **Prose, not Tokens, is the focus**: The token values serve as context and are not rendering instructions. The prose is where the design lives.
- **Specific References**: A specific reference (e.g., "A 1970s graduate lecture handout") carries more than a list of adjectives. It carries the reasoning behind the values.
- Do NOT use tokens as strict rendering instructions. They are context for the prose.

---

## 🛠️ The 4 Core Design Verbs

When implementing or refining interfaces, operate through 4 structured design actions:

1. **`/build` (Archetype Construction)**:
   - Assemble full interface layouts strictly bound to a pre-selected Design Archetype from `DESIGN.md`.
   - Guarantee complete 8-state coverage on all interactive components prior to completion.

2. **`/audit` (Aesthetic Inspection)**:
   - Review layouts for AI-default tropes (generic centered hero cards, uniform 3-box Bento grids, unearned gradients).
   - Check contrast ratios via `python .agents/evals/audit_aesthetics.py`.

3. **`/redesign` (Elevation & Refinement)**:
   - Transform flat, generic templates into high-craft, asymmetric layouts using one of the 6 Structural Macrostructures.
   - Enforce strict dimensional rhythm and locked typography tokens.

4. **`/study` (System & Pattern Deconstruction)**:
   - Analyze production-grade design systems (Linear, Stripe, Raycast) and extract exact token scales, spacing cadences, and border treatments.

---

## 🎨 Curated Design Archetypes

Select a primary archetype during project scaffolding to prevent aesthetic convergence:

1. **Swiss Editorial**:
   - *Vibe*: Journalistic gravitas, cultural institutions, architectural publications.
   - *Palette*: Stark monochromatic foundation (paper whites, deep charcoal) with a single razor-sharp editorial accent (e.g., crimson or vermilion).
   - *Typography*: High-contrast serif or sharp geometric sans display with generous asymmetric margins.

2. **Refined Dark Industrial**:
   - *Vibe*: Developer infrastructure, hardware telemetry, command consoles.
   - *Palette*: Obsidian base (`#0D0F12`), dark slate surfaces (`#16191E`), precise 1px borders (`#252932`), amber or cyan status indicators.
   - *Typography*: Clean neo-grotesque sans paired with monospace data tables (`JetBrains Mono`).

3. **High-Density Cockpit**:
   - *Vibe*: Trading terminals, observability hubs, complex analytical suites.
   - *Palette*: Muted matte slate, low-saturation data visualization accents, high-contrast foreground text.
   - *Geometry*: Compact 4px/8px rhythm, collapsible sidebars (240–260px), multi-panel split views, zero decorative fluff.

4. **Neo-Brutalist Utility**:
   - *Vibe*: Open-source developer tools, modern productivity apps.
   - *Palette*: High-contrast canvas, bold 1.5px solid black/dark borders, saturated block-color highlights.
   - *Geometry*: Sharp 4–8px radius, clean hard drop-shadows (`2px 2px 0px rgba(0,0,0,1)`), tactile click physics.

5. **Tactile Ambient**:
   - *Vibe*: Premium SaaS, consumer productivity, audio/creative software.
   - *Palette*: Rich dark neutral canvas with purposeful layered depth, subtle material translucency, warm white text.
   - *Motion*: Restrained 150ms ease transitions, spring compression on click (`scale(0.98)`).

---

## 🏛️ The Craft Floor & Category Default Refusals

The craft floor establishes non-negotiable physical mechanics. Reaching for a category default when the axis is unconstrained indicates automated complacency rather than intentional craft.

### 1. Depth & Elevation Mechanics
- **Offset Requirement**: Shadows MUST carry a vertical offset (`2px–8px`) and proportionate soft blur. A zero-offset colored halo (`0 0 20px rgba(...)`) is arbitrary decoration, not depth.
- **Single Elevation Declaration**: Declare depth via border OR shadow—never stack a thick 2px border inside an aggressive soft drop-shadow ("ghost cards").

### 2. Spacing Rhythm & Visual Gravity
- **Asymmetric Vertical Cadence**: Always allocate significantly more whitespace above a section heading than below it (e.g. `mt-16 mb-4`). Headings must visually bind to the content they introduce.
- **Tight Semantic Clusters**: Group related items tightly with generous macroscopic separation between dissimilar clusters.

### 3. Category Default Refusals (Do Not Ship)
- **Identical 3-Card Feature Rows**: Forbid repeating 3 identical cards (icon + title + paragraph) across marketing surfaces. Use asymmetric split layouts, interactive sandboxes, or stepped narratives.
- **Hero-Metric Cliché**: Forbid the generic hero format (giant number + tiny label + arbitrary percent chip) unless verified by authentic telemetry.
- **Kicker / Eyebrow Overload**: Drop uppercase tracking kickers on every heading. Headings must carry their own conceptual weight.
- **Reflex Modals**: Never reach for a disruptive modal dialog for a task that requires neither focused task isolation nor external confirmation. Prefer inline expanding drawers, side sheets, or inline disclosure panels.
- **Monospace as Costume**: Monospace typography is reserved for source code, file paths, telemetry readouts, or technical measurements. Never use monospace as decorative styling for generic marketing prose.
- **Fake Browser / Device Bezels**: Never render drawn macOS traffic-light buttons or fake browser address bars inside web pages. Let real native window managers render chrome.

