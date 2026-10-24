---
name: ui-finish
description: >-
  Applies premium, restrained aesthetics (Linear, Raycast, Stripe), visual engineering, and design token contracts. Use when applying UI polish, designing micro-interactions, refining typography, or creating design tokens.
---

# UI & Visual Design Architect (Restrained Visual Engineering)

Enforces high-craft production UI paradigms (Linear, Raycast, Stripe) by rejecting generic AI aesthetic defaults and mandating strict design token contracts.

## 1. Reference Sitemap (Load On-Demand Only When Needed)
- **Aesthetic Archetypes & Tokens**: [references/aesthetic_archetypes.md](references/aesthetic_archetypes.md)
- **Visual Craft Floor & Refusals**: [references/craft_floor.md](references/craft_floor.md)
- **Component Recipes**: [references/component_recipes.md](references/component_recipes.md)
- **Bento Macrostructures**: [references/bento_and_macrostructures.md](references/bento_and_macrostructures.md)
- **Brief Inference & Three Dials**: [references/brief_inference_and_dials.md](references/brief_inference_and_dials.md)
- **Motion & 60fps Compositor**: [references/motion_performance.md](references/motion_performance.md)
- **Accessibility Contracts**: [references/accessibility_contracts.md](references/accessibility_contracts.md)
- **Iconography & Lucide Tokens**: [references/lucide_tokens.md](references/lucide_tokens.md)
- **Inclusive Visual Prompts**: [references/visual_engineering.md](references/visual_engineering.md)

Verify aesthetics mechanically: `python .agents/evals/audit_aesthetics.py --dir <target_path>`.

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

## 🎛️ The Visual Pre-Flight (Core Parameters)
Before authoring UI code, calibrate these technical parameters (internal alignment; no decorative chat block required):
- **Mode**: Identify visitor intent (`Persuade` | `Operate` | `Read` | `Experience`; see `references/craft_floor.md`).
- **Color Strategy**: Enforce strict `60:30:10` ratio (60% dominant background, 30% structural/card neutral, 10% purposeful accent). Never scatter arbitrary colors.
- **Typography**: Single mathematical scale (`scale` + `w400/w600/w800`) mapped to design tokens; max 2 typefaces.
- **Macrostructure**: Select archetype: `Asymmetric Split`, `Cockpit`, `Editorial`, `Playground`, `Stepped`, or `Minimalist`.
- **Three Dials**: Calibrate `VARIANCE` (1-10 layout asymmetry), `MOTION` (1-10 transition dynamism), `DENSITY` (1-10 information compactness; see `references/brief_inference_and_dials.md`).
- **Physical Restraint**: Crisp 1px borders (`border: 1px solid var(--border)`), solid backgrounds, max 8px border radii.
- **Bounded Passes**: Max 2 passes (Batch 1: Desktop + Mobile Build -> 1 Fix Pass -> 1 Confirm Pass).

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

## 🚢 Delivery Verification Checklist (Physical Criteria)
Before declaring a UI task complete, verify all 5 physical criteria (tested mechanically via `python .agents/evals/audit_aesthetics.py --dir <target_path>` where applicable):
1. **Visual Restraint**: Zero unearned neon glow, decorative backdrop blurs, or default purple gradients. Crisp 1px borders, solid fills.
2. **Copy Authenticity**: Zero placeholder buzzwords, synthetic testimonials, or ungrounded claims (per `prose-authenticity.md`).
3. **Interactive Wiring**: All buttons, links, and forms wired with handlers; full 4-state coverage (Idle, Loading, Error, Empty).
4. **Resilience & Contrast**: WCAG AA contrast ratio verified; responsive layout tested across mobile and desktop.
5. **Code Hygiene**: Zero commented-out dead blocks or cosmetic commentary.

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
