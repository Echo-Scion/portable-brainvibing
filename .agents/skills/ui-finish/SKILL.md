---
name: ui-finish
description: >-
  Applies premium, restrained aesthetics (Linear, Raycast, Stripe), visual engineering, design tokens, craft floor rules, bento grids, 60fps motion, and accessibility contracts. Use when applying UI polish, designing micro-interactions, refining typography, or creating design tokens.
---

# UI & Visual Design Architect (Restrained Visual Engineering)

Enforces high-craft production UI paradigms (Linear, Raycast, Stripe) by rejecting generic AI aesthetic defaults and mandating strict design token contracts.

## 1. Reference Sitemap (Load On-Demand Only When Needed)
- **Aesthetic Archetypes & Tokens**: [references/aesthetic_archetypes.md](references/aesthetic_archetypes.md)
- **Canonical Component Taxonomy**: [references/component_taxonomy.md](references/component_taxonomy.md)
- **Component Decision Matrix**: [references/component_decision_matrix.md](references/component_decision_matrix.md)
- **Visual Craft Floor & Refusals**: [references/craft_floor.md](references/craft_floor.md)
- **Component Recipes**: [references/component_recipes.md](references/component_recipes.md)
- **Bento Macrostructures**: [references/bento_and_macrostructures.md](references/bento_and_macrostructures.md)
- **Brief Inference & Three Dials**: [references/brief_inference_and_dials.md](references/brief_inference_and_dials.md)
- **Motion & 60fps Compositor**: [references/motion_performance.md](references/motion_performance.md)
- **Accessibility Contracts**: [references/accessibility_contracts.md](references/accessibility_contracts.md)
- **Iconography & Lucide Tokens**: [references/lucide_tokens.md](references/lucide_tokens.md)
- **Inclusive Visual Prompts**: [references/visual_engineering.md](references/visual_engineering.md)

Verify aesthetics mechanically: `python .agents/evals/audit_aesthetics.py --dir <target_path>`.

## Operational Posture: Restraint & Soulful Engineering
Production UI prioritizes clarity and high agency over decorative novelty. However, restraint does NOT mean sterile monotony. Interfaces combine strict 5-token color contracts (`OKLCH`), APCA contrast compliance, physical materiality (135° directional lighting), and at least one bespoke Signature Soul Component so the interface never looks like an anonymous AI clone.

## Critical Validations (Universal)
- **Disambiguation (UI-Finish vs Frontend-Experience)**: Use `ui-finish` STRICTLY for visual engineering, creative polish, and aesthetic craftsmanship. Do NOT use this skill for analytical widget tree debugging, state management, or structural layout fixing. For structural fixes, delegate to the `frontend-experience` skill.
- **Depth & Restraint**: NEVER use arbitrary floating glassmorphism panels, oversized rounded corners (20px+), or gradient backgrounds as decoration. Use solid or systemically coherent surfaces with subtle borders and 135° directional light source.
- **Glass Coherence**: If using blur/glass, apply it system-wide with focus-driven opacity hierarchy (85% active / 75% inactive) and pair with low-opacity SVG noise texture to prevent 8-bit banding.
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
- **Mandatory 6-Family Screen State Machine (`UI State Expander`)**: Every data-fetching or interactive view must handle: (1) **Data States** (`loading` skeleton, `first-time-empty` with orientation + create CTA, `filtered-to-empty` with query name + `"Clear filters"` button, `populated`, `partial-data`), (2) **Interaction States**, (3) **Form States** (persistent `<label>`, `16px` mobile input floor, paste allowed), (4) **Content Gremlins** (long strings, `0`/`1`/`1000+` items, RTL logical properties), (5) **System States**, and (6) **Recovery States** (`retry`, `undo`, `restore-draft`).

## 🏛️ Task-First Layout Model & Two-Hypothesis Rule (Anti-UI-Slop)
1. **Select Layout by Primary Task**: Choose **Data Table** for multi-attribute comparison, **Split View / Inspector Rail** for simultaneous context + editing, **Compact Action List** for triage, **Command Surface** (`0ms` animation) for high-frequency power actions, and **Asymmetric Bento** strictly for heterogeneous overviews. Group with whitespace ($\ge 2\times$ outer vs inner gap) before reaching for bordered cards (prevent container fatigue).
2. **Explore Two Structural Hypotheses (`Alt A` vs. `Alt B`)**: Reject the first obvious template. Formulate `Alt A (Structural Rearrangement)` and `Alt B (First-Principles Task Flow)` holding tokens constant before coding.

## 🎛️ Component-Scope 8-State & Surface Geometry Contract
When building standalone interactive components (buttons, cards, inputs, selects, modals), implement code for all **8 states** with exact geometry:
1. `default`: Concentric radii (`outerRadius = innerRadius + padding`), optical icon padding (`icon-side = text-side - 2px`), `oklch` shadow-borders, and `1px` neutral image outlines (`outline-black/10 dark:outline-white/10`).
2. `hover`: Gated by `@media (hover: hover) and (pointer: fine)`.
3. `:focus-visible`: High-contrast `2px` focus ring with `2px` offset, never obscured by sticky headers (WCAG 2.4.11).
4. `:active`: Interruptible CSS transition `scale(0.96)` (`150ms ease-out`, zero bounce), with a `static` prop to disable scaling on `100+/day` toolbar controls.
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
Before declaring a UI task complete, verify all 6 physical criteria (tested mechanically via `python .agents/evals/audit_aesthetics.py --dir <target_path>` where applicable):
1. **Visual Restraint & Optics**: Zero unearned neon glow or default purple gradients. Contrast passes APCA $|L_c| \ge 75$ & WCAG AA; dark mode adheres to luminance elevation ($\text{Base} < \text{Card} < \text{Modal}$).
2. **Signature Soul Component**: At least 1 bespoke interactive domain control or tactile affordance is physically implemented (no anonymous templates).
3. **Copy Authenticity**: Zero placeholder buzzwords, synthetic testimonials, or ungrounded claims (per `prose-authenticity.md`).
4. **Interactive Wiring**: All buttons, links, and forms wired with handlers; full 4-state coverage (Idle, Loading, Error, Empty).
5. **Resilience & Contrast**: Responsive layout tested across mobile and desktop without viewport clipping.
6. **Code Hygiene**: Zero commented-out dead blocks or cosmetic commentary.

## Workflow Patterns (Universal)
0. **Observe, Oppose, Upscale (First-Principles UX Protocol)**:
   - *Observe*: Map the user's authentic workflow friction, click steps, and visual confusion.
   - *Oppose*: Challenge modal popups, multi-step sub-dialogs, hidden filters, and trial-and-error numeric inputs. Aim to cut interaction friction by $50\%$.
   - *Upscale*: Apply `OKLCH` 5-token balance (`60:30:10`), Dark Mode luminance elevation, and craft **1 Signature Soul Component** (domain-specific visual/tactile control).
1. **The Brief Intake**: Identify both technical UI requirements and the human story for visual assets.
2. **Design Specification (DESIGN.md)**: Before coding, define the visual identity using the `DESIGN.md` format (YAML tokens + Markdown prose). Reference `.agents/skills/ui-finish/references/visual_engineering.md` for details.
3. **Implementation**: Use patterns from ecosystem canons, 6 Systemic UX Redesign Patterns, and the `DESIGN.md` spec to build surfaces and animations.
4. **Prompt Engineering**: Use the annotation framework from `.agents/skills/ui-finish/references/visual_engineering.md` for AI-generated visual assets.

## Troubleshooting (Universal)
- **Scrolling stutters**: Excessive blur effects. Consolidate blurs.
- **AI generates identical faces**: Lack of specified variance in prompt description.
- **Skin tones washed out**: Lighting defaults to lighter skin physics. Specify melanin-friendly lighting.

---
*Generated by OrionCortex Infrastructure - UI & Visual Suite*
