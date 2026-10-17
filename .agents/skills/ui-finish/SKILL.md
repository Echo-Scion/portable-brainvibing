---
name: ui-finish
description: >-
  Applies premium, restrained aesthetics (Linear, Raycast, Stripe), visual engineering, and design token contracts. Use when applying UI polish, designing micro-interactions, refining typography, or creating design tokens.
---

# UI & Visual Design Architect (Restrained Visual Engineering)

Enforces high-craft production UI paradigms (Linear, Raycast, Stripe) by rejecting generic AI aesthetic defaults and mandating strict design token contracts.

## JIT Tool Directives (Execute this FIRST)
1. **Detect Ecosystem**: Check the project root for the ecosystem package file (`{{PACKAGE_FILE}}`).
2. **Load Ecosystem Canon**: `view_file .agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-ui-patterns.md`
3. **Mandatory Knowledge Routing**:
    - **Visual/Prompt Engineering**: `view_file .agents/skills/ui-finish/references/visual_engineering.md`
    - **Component Recipes & Cookbook**: `view_file .agents/skills/ui-finish/references/component_recipes.md`
    - **Visual Craft Floor & Category Refusals**: `view_file .agents/skills/ui-finish/references/craft_floor.md`
    - **Aesthetic Archetypes & Design Systems**: `view_file .agents/skills/ui-finish/references/aesthetic_archetypes.md`
    - **Bento Grids & Asymmetric Macrostructures**: `view_file .agents/skills/ui-finish/references/bento_and_macrostructures.md`
    - **Brief Inference & Three Dials**: `view_file .agents/skills/ui-finish/references/brief_inference_and_dials.md`
    - **Iconography & Lucide Token Contracts**: `view_file .agents/skills/ui-finish/references/lucide_tokens.md`
    - **60 FPS Motion Performance & Compositor**: `view_file .agents/skills/ui-finish/references/motion_performance.md`
    - **Accessibility & Inclusive Contracts**: `view_file .agents/skills/ui-finish/references/accessibility_contracts.md`
4. Search for theme/color definitions to maintain visual harmony.
5. Check responsive layout usage to ensure responsiveness is preserved.
6. **CI Gatekeeper**: Execute `python .agents/evals/audit_aesthetics.py --dir <target_path>` at the end of every UI task.

## Operational Posture: Restraint Over Novelty
Production UI prioritizes clarity over novelty. Interfaces mandate solid backgrounds, crisp 1px borders, verified WCAG contrast, and zero decorative animations or AI aesthetic tells.


## Critical Validations (Universal)
- **Disambiguation (UI-Finish vs Frontend-Experience)**: Use `ui-finish` STRICTLY for visual engineering, creative polish, and aesthetic craftsmanship. Do NOT use this skill for analytical widget tree debugging, state management, or structural layout fixing. For structural fixes, delegate to the `frontend-experience` skill.
- **Depth & Restraint**: NEVER use floating glassmorphism panels, oversized rounded corners (20px+), or gradient backgrounds as decoration. Use solid backgrounds with subtle borders.
- **Inclusive Visuals**: NEVER accept "Clone Faces." Mandate distinct facial structures and authentic attire.
- **Performance**: NEVER use metric-card grids as default dashboards or floating widgets unless required by product.
- **Accessibility & Semantics**:
  - NEVER ignore "Reduce Motion" / "prefers-reduced-motion" settings.
  - ALWAYS add semantic labels to icon-only buttons or custom interactive elements.
  - Ensure focus states are clearly visible for keyboard/D-pad navigation.
  - Wrap decorative images with appropriate exclusions or provide alt text for informative images.

## Purposeful Aesthetics & Structural Ergonomics (The High-Craft Standard)
- **Semantic Iconography**: Forbid generic sparkle, magic wand, or floating orb icons as thoughtless ornamentation. Every icon must represent its actual domain entity or action. 16–20px, monochrome or subtle color, no decorative backgrounds.
- **Distinct Harmonic Palettes**: Reject generic blue-to-purple / cyan-to-magenta default hero gradients. Palettes must be drawn from project design tokens (`DESIGN.md`) or concrete brand semantics. True dark mode (`#0f172a`), no blue-black gradient premium fakes.
- **Restraint Over Trend-Stacking**: Never blindly stack glassmorphism + mesh gradients + glowing borders + pill buttons. Restrict UI to solid backgrounds, subtle 1px borders, and a maximum box-shadow of `0 2px 8px rgba(0,0,0,0.08)`.
- **Cadence & Rhythm**: Avoid monotonous consecutive KPI 3-box grids. Ensure clean page structure with predictable grid/flex layouts. No asymmetric creative chaos.
- **Mandatory Data View 4-State**: Every data-fetching UI surface must explicitly implement all 4 data view states: **Loading** (shimmer/skeleton), **Empty** (clear affordance), **Error** (actionable retry), and **Success** (content view). Individual interactive controls implement the **8-State Contract** below.

## 🏛️ Structural Macrostructures (Rhythm Variety)
Match screen layout to one of 6 structural macrostructures (see `.agents/skills/ui-finish/references/bento_and_macrostructures.md`):
1. **Asymmetric Split-Masthead**, 2. **Data-Dense Cockpit**, 3. **Editorial Dossier**, 4. **Interactive Playground**, 5. **Stepped Narrative**, 6. **Minimalist Utility**.

## 🎛️ Component-Scope 8-State Contract
When building standalone interactive components (buttons, cards, inputs, selects, modals), implement code for all **8 states**:
1. `default`: Baseline resting state.
2. `hover`: Subtle tactile elevation or surface shift.
3. `:focus-visible`: High-contrast visible focus ring (minimum 2px offset for keyboard navigation).
4. `:active`: Pressed/spring compression feedback (`scale(0.98)`).
5. `disabled`: Reduced opacity, `pointer-events: none` or `disabled` attribute, accessible ARIA state.
6. `loading`: Skeleton or contained spinner; maintain component dimensions; `aria-busy="true"`.
7. `error`: High-contrast error token, clear recovery messaging, inline validation icon.
8. `success`: Affirmative completion indicator or feedback transition.

## 📐 Dimensional & Restraint Standards (Mathematical Geometry Boundaries)
When structuring layouts and interface elements, enforce strict physical restraint:
- **Sidebar & Panels**: 240–260px fixed width, solid background, 1px border-right. No floating shells or rounded outer desktop window frames.
- **Card Radii**: 8–12px maximum radius. Subtle 1px border. Shadow maximum: `0 2px 8px rgba(0,0,0,0.08)`. Forbid universal 24px+ floating pill containers.
- **Buttons**: Solid fill or subtle 1px border, 6–10px radius max. No arbitrary gradients or oversized capsules.
- **Spacing Scale**: Strict mathematical cadence across all margins/padding: `4px / 8px / 12px / 16px / 24px / 32px / 48px / 64px`. No random arbitrary gaps (`margin: 19px`).
- **Transitions**: 100–200ms ease, opacity and color shifts only. No bouncy transforms or wobbling on static containers.

## 🧭 Visitor Modes & Brief Inference
Determine visitor objective (**Persuade**, **Operate**, **Read**, or **Experience**; see `.agents/skills/ui-finish/references/craft_floor.md`) and emit a 1-line design declaration:
`Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <design system or aesthetic family>.`

## 🎛️ The Visual Pre-Flight Declaration
Before any UI implementation, declare:
```
[VISUAL PRE-FLIGHT]:
- Mode: {Persuade | Operate | Read | Experience}
- Design Read: Reading this as: {kind} for {audience}, with {vibe} language.
- Color Strategy: {dominant}:{accent}:{neutral} (e.g., 60:30:10) | Palette: {Token / Set}
- Typography: {scale} + {weights} (e.g., Golden Ratio, w400/w600/w800)
- Macrostructure: {Asymmetric Split | Cockpit | Editorial | Playground | Stepped | Minimalist}
- Restraint: {1px borders} + {solid bg} + {max 8px radius}
- Dials: VARIANCE {1-10} / MOTION {1-10} / DENSITY {1-10} (see `.agents/skills/ui-finish/references/brief_inference_and_dials.md`)
- Bounded Passes: Batch 1 (Desktop + Mobile) -> 1 Fix Pass -> 1 Confirm Pass (Max 2 Passes)
- Source of truth: {DESIGN.md or token name}
```
Coding begins ONLY after this block is emitted.

## 🛡️ Bounded Inspection Pass Mandate (Anti-Token Burn)
Verify in bounded, deterministic passes—NEVER in an open-ended loop:
1. **Pass 1 (Batched Build & Inspect)**: Build completely. Inspect desktop and mobile viewports simultaneously. Compile all defects (contrast, spacing, responsiveness) into a single batch.
2. **Pass 2 (Batched Remediation)**: Apply all fixes in one unified code edit.
3. **Pass 3 (Confirmation)**: Run final confirmation sweep. CEASE polishing immediately. Open-ended self-QA loops burn context and degrade code. Detailed layout limits (hero caps, bento rules, browser theming) are codified in `.agents/skills/ui-finish/references/bento_and_macrostructures.md` and `craft_floor.md`.

## 🔨 Tactical Refinement Directives
When refining existing surfaces, invoke explicit tactical verbs:
- **`bolder`**: Amplify safe or timid layouts with punchy typographic scale, high contrast, and distinctive asymmetrical balance.
- **`quieter`**: Tone down overstimulating UIs; strip decorative halos, gratuitous badges, and hyperactive animations.
- **`distill`**: Strip complexity to absolute essence; eliminate redundant wrapper cards, flatten visual hierarchy.
- **`harden`**: Ensure production resilience; implement error boundaries, keyboard focus traps, and long-text i18n overflow handling.
- **`onboard`**: Design purposeful first-run states, activation pathways, and empty-state guidance.

## 🧬 Visual DNA Extraction (Reference Analysis)
When a user provides a reference URL or screenshot:
1. **Macrostructure Extraction**: Identify the spatial layout rhythm and dominant content flow.
2. **Typographic Anchor**: Extract heading-to-body scale ratio and letterform tone (Grotesque, Monospace, Humanist, Editorial Serif).
3. **Harmonic Anchor**: Extract the primary brand color, background neutral shade, and accent contrast ratio.
4. **Synthesis**: Generate or update the project's `DESIGN.md` with these extracted tokens. **Never copy layout pixels, fake device chrome, or proprietary graphics verbatim.**

## 🛡️ The Visual Critique Gates & Anti-Cliché Sweep (Pre-Emit Audit)
Before delivering any frontend emit, every condition of the Visual Critique Gates must be satisfied across Visual Integrity, Structural Craft, and Typography. Refer to the full checklist in `.agents/skills/ui-finish/references/craft_floor.md#4-the-visual-critique-gates--anti-cliché-sweep-pre-emit-audit`.

## 4-Block Delivery Gate (Pre-Ship Certification)
Before declaring a UI task complete, certify:
```
[DELIVERY GATE: UI & FIDELITY AUDIT]
• Pre-Emit   : [PASS] - Critique: Hierarchy 5/5, Restraint 5/5, Resilience 5/5, Variety 5/5.
• Visual     : [PASS] - Zero unearned glow, trend-stacking, or default purple gradients.
• Copy       : [PASS] - Zero hype buzzwords, fabricated stats, or fake testimonials.
• Function   : [PASS] - All buttons/links wired; Loading/Empty/Error states handled; 8 component states verified.
• Resilience : [PASS] - WCAG contrast compliant; responsive reflow verified; no comment bloat.
```

## Workflow Patterns (Universal)
1. **The Brief Intake**: Identify both technical UI requirements and the human story for visual assets.
2. **Design Specification (DESIGN.md)**: Before coding, define the visual identity using the `DESIGN.md` format (YAML tokens + Markdown prose). Reference `.agents/skills/ui-finish/references/visual_engineering.md` for details.
3. **Implementation**: Use patterns from ecosystem canons and the `DESIGN.md` spec to build surfaces and animations.
4. **Prompt Engineering**: Use the annotation framework from `.agents/skills/ui-finish/references/visual_engineering.md` for AI-generated visual assets.

## Troubleshooting (Universal)
- **Scrolling stutters**: Excessive blur effects. Consolidate blurs.
- **AI generates identical faces**: Lack of specified variance in prompt description.
- **Skin tones washed out**: Lighting defaults to lighter skin physics. Specify melanin-friendly lighting.

---
*Generated by Portable Brainvibing Infrastructure - UI & Visual Suite*
