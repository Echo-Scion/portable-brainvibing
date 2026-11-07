---
name: "{{project_name}}"
version: "1.0.0"
description: "Design system specification, visual tokens, and constraints for {{project_name}}"
colors:
  # OKLCH 5-Token Perceptual Color System (60:30:10 Balance, <= 12 total tokens)
  bg: "{{bg_oklch_or_hex}}"           # 60% Dominant canvas surface (e.g. oklch(0.14 0.02 260))
  text: "{{text_oklch_or_hex}}"       # High-contrast text (APCA |Lc| >= 75)
  primary: "{{primary_oklch_or_hex}}" # High-contrast primary action CTA
  secondary: "{{secondary_oklch_or_hex}}" # 30% Structural cards, panels, sidebars
  accent: "{{accent_oklch_or_hex}}"   # 10% Focus indicator / status dot
  canvas: "{{canvas_hex}}"
  surface: "{{surface_hex}}"
  surface_border: "{{border_hex}}"
  text_primary: "{{text_primary}}"
  text_muted: "{{text_muted}}"
  brand_accent: "{{accent_hex}}"
  status_error: "#EF4444"
  status_success: "#10B981"
  status_warning: "#F59E0B"
  status_info: "#3B82F6"
typography:
  headline-display:
    fontFamily: "{{display_font}}"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  headline-lg:
    fontFamily: "{{display_font}}"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.3
  headline-md:
    fontFamily: "{{display_font}}"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.35
  body-lg:
    fontFamily: "{{body_font}}"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.5
  body-md:
    fontFamily: "{{body_font}}"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: "{{body_font}}"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.4
  label-caps:
    fontFamily: "{{mono_font}}"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.05em"
spacing:
  "3xs": "2px"
  "2xs": "4px"
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  "2xl": "48px"
  "3xl": "64px"
  "4xl": "96px"
  "5xl": "128px"
rounded:
  none: "0px"
  xs: "2px"
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  "2xl": "24px"
  full: "9999px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.bg}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.md}"
    padding: "12px 20px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.brand_accent}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "10px 16px"
  card-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.lg}"
    padding: "24px"
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "10px 14px"
    height: "40px"
optics:
  lighting_angle: "135deg"            # Directional top-left light source
  apca_body_min: 75                   # APCA |Lc| >= 75 for body text
  apca_ui_min: 45                     # APCA |Lc| >= 45 for large headings & UI controls
  dark_base_min_lightness: 0.12       # Forbid pure #000000; minimum OKLCH lightness L=0.12-0.15
  elevation_ladder: "base < card < modal" # Luminance increases with surface elevation
  glass_opacity_active: 0.85          # Focus-driven active pane opacity
  glass_opacity_inactive: 0.75        # Inactive pane opacity with backdrop-blur
  noise_overlay_opacity: 0.04         # SVG feTurbulence grain to prevent 8-bit banding
elevation:
  none: "none"
  sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
  md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
  lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"
  xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"
motion:
  duration:
    instant: "75ms"
    fast: "150ms"
    normal: "250ms"
    deliberate: "400ms"
  easing:
    default: "cubic-bezier(0.4, 0, 0.2, 1)"
    in: "cubic-bezier(0.4, 0, 1, 1)"
    out: "cubic-bezier(0, 0, 0.2, 1)"
    bounce: "cubic-bezier(0.34, 1.56, 0.64, 1)"
breakpoints:
  sm: "640px"
  md: "768px"
  lg: "1024px"
  xl: "1280px"
  "2xl": "1536px"
---

# Design Direction: {{project_name}}

> **Design Read & Soul**: This document supplies project-specific aesthetic direction, locked design tokens, and structural rules.
> The AI agent treats this file as **immutable data to apply**, not speculative instructions to improvise.
> Fully compliant with the [Google Labs DESIGN.md specification](https://github.com/google-labs-code/design.md).

---

## Overview

### 1. 🎭 Identity & Archetype Selection

Select exactly **one** primary archetype during scaffolding to eliminate generic aesthetic convergence:

| # | Archetype | Target Vibe & Use Case | Display + Body Typography | Canvas & Surface Palette | Accent & Footprint (<=5%) |
| :- | :--- | :--- | :--- | :--- | :--- |
<!-- row:archetype=swiss-editorial -->| **01** | **Swiss Editorial** | Journalistic gravitas, cultural institutions, essays | Newsreader (Serif) + Public Sans | Paper `#F9F9FB` / Clean Slate `#FFFFFF` | Razor Crimson (`#D92D20`) |
<!-- row:archetype=dark-industrial -->| **02** | **Dark Industrial** | Developer infra, hardware telemetry, CLI tooling | Space Grotesk + JetBrains Mono | Obsidian `#0D0F12` / Dark Slate `#16191E` | Amber Phosphor (`#F59E0B`) |
<!-- row:archetype=density-cockpit -->| **03** | **Density Cockpit** | Trading terminals, observability suites, analytics | Inter + IBM Plex Mono | Matte Charcoal `#111318` / Panel `#191C24` | Cyan Telemetry (`#06B6D4`) |
<!-- row:archetype=neo-brutalist -->| **04** | **Neo-Brutalist** | Developer tools, indie hacking, direct utility | Archivo (Black) + Space Mono | Canvas `#F8F9FA` / Stark Border `2px #000` | Electric Yellow (`#FACC15`) |
<!-- row:archetype=tactile-ambient -->| **05** | **Tactile Ambient** | Premium SaaS, audio tools, creative workflows | Plus Jakarta Sans + Inter | Dusk Neutral `#131418` / Layer `#1E2026` | Iris Purple (`#6366F1`) |
<!-- row:archetype=modern-minimal -->| **06** | **Modern Minimal** | Production SaaS, API platforms, financial engines | Geist Sans + Inter | Paper `#FFFFFF` / Mist Card `#F8FAFC` | Electric Blue (`#2563EB`) |
<!-- row:archetype=retro-futuristic -->| **07** | **Retro-Futuristic** | Sci-fi interfaces, simulation tools, synth editors | VT323 / Share Tech + Overpass Mono | CRT Carbon `#12100E` / Rust Surface `#1C1814` | CRT Amber (`#FFB000`) |
<!-- row:archetype=academic-mono -->| **08** | **Academic Mono** | Research repositories, theorem provers, archives | Playfair Display + Courier Prime | Newsprint Cream `#F5F2EB` / Warm Tint `#EDE8DC` | Deep Bronze (`#5A4A42`) |
<!-- row:archetype=warm-editorial -->| **09** | **Warm Editorial** | Food/hospitality, lifestyle products, storytelling | Fraunces + Cabinet Grotesk | Oatmeal `#FBF9F4` / Surface `#F2EDE2` | Terracotta Clay (`#C85A32`) |
<!-- row:archetype=cyber-terminal -->| **10** | **Cyber Terminal** | Security dashboards, forensic scanners, protocol monitors | Red Hat Mono + Fira Code | Deep Abyss `#05080E` / Grid Panel `#0B111C` | Matrix Emerald (`#10B981`) |
<!-- row:archetype=luxury-atelier -->| **11** | **Luxury Atelier** | Fashion, bespoke architecture, premium portfolios | Cormorant Garamond + Satoshi | Soft Ivory `#FAF9F6` / Card `#F3EFE6` | Deep Noir (`#18181B`) |
<!-- row:archetype=solar-minimal -->| **12** | **Solar Minimal** | Climate tech, renewable platforms, biology tools | Outfit + Source Sans 3 | Sage Off-White `#F4F6F2` / Leaf Tint `#E8EDE3` | Forest Viridian (`#15803D`) |

- **Selected Archetype**: `{{archetype_name}}`
- **Active Macrostructure**: `{{macrostructure_name}}` (Options: *Asymmetric Split-Masthead* | *Data-Dense Cockpit* | *Editorial Dossier* | *Interactive Playground* | *Stepped Narrative* | *Minimalist Utility*)

<!-- START FOUNDATION:layout-model-by-task -->
### 1.05 🧭 Task-First Layout Model & Two-Hypothesis Rule (Anti-UI-Slop)
Never default to a card grid or Bento layout when a task-specific workspace primitive fits better:
1. **Select Layout by Primary Task**:
   - *Scan & Compare Multi-Attribute Records*: **Data Table** (sticky header, `tabular-nums`, sort carets; never card soup).
   - *Simultaneous Context & Detail Editing*: **Split View / Master-Detail** or **Canvas + Inspector Rail**.
   - *Sequential Triage & Action Rows*: **Compact Action List / Band** (grouped by whitespace $\ge 2\times$ intra-group gap, not boxed cards).
   - *High-Velocity Power Operations*: **Command Surface + Keyboard First** (`0ms` open/close animation).
   - *Chronological / Audit Streams*: **Vertical Timeline Rail**.
   - *Heterogeneous Feature Overview (Marketing/Onboarding Only)*: **Asymmetric Bento Mosaic**.
2. **Prevent Container Fatigue**: Group related elements via spatial proximity ($2\times$ outer gap vs inner gap) and typographic hierarchy first; use bordered cards only when an interactive boundary, comparison, or elevation layer is functionally required. Never separate the label, value, and context of one logical entity into unrelated containers.
3. **Two-Hypothesis Exploration (`Alt A` vs `Alt B`)**: The first layout idea is a local maximum. Before coding a primary screen, formulate two structurally distinct hypotheses holding content and tokens constant:
   - `Alt A (Structural Rearrangement)`: Optimizes hierarchy and eliminates dead space/container fatigue within the current flow.
   - `Alt B (First-Principles Task Flow)`: Rebuilds the screen around the fewest user moves to complete the primary job.
<!-- END FOUNDATION:layout-model-by-task -->

### 1.1 🌟 The Signature Soul Component
Every project MUST specify and implement at least **one bespoke interactive domain control or visual affordance** unique to this product's domain identity (e.g., a tactile rotary gain meter with physical detents, a custom timeline waveform cue scrubber, an obsidian crystallite texture toggle, or a tactile hardware dial).
- **Signature Component Name**: `{{signature_component_name}}`
- **Domain Metaphor / Physics**: `{{signature_component_metaphor}}`
- **Interactive Affordance**: `{{signature_component_interaction}}`

---

## Colors

<!-- START FOUNDATION:wcag-contrast-law -->
*Interfaces must satisfy dual contrast compliance: WCAG 2.1 AA ($\ge 4.5:1$ body, $\ge 3:1$ large) AND APCA ($|L_c| \ge 75$ body text, $|L_c| \ge 45$ large headings and interactive UI controls).*

- **Perceptual Uniformity (`OKLCH`)**: Palettes are calibrated in `oklch(L C H)` so shifting Hue preserves identical perceived Lightness ($L$) and Chroma ($C$) without Abney-effect hue shifts.
- **Dark Mode Luminance Ladder & Anti-Halation**:
  - Drops shadows fail on dark themes; depth MUST follow $\text{Luminance}(\text{Base}) < \text{Luminance}(\text{Card}) < \text{Luminance}(\text{Modal})$.
  - Forbid pure `#000000` canvas with `#FFFFFF` text ($21:1$ contrast triggers astigmatism halation); use tinted dark surfaces (`#0D0F12`, `oklch(0.14 0.02 H)`) with softened light foregrounds (`#EAEAFB`).
  - Desaturate dark mode accents by $15\%\text{–}25\%$ to eliminate optical vibration.
- **Directional Lighting ($135^\circ$) & Materiality**:
  - Extruded buttons carry top-left highlight border + bottom-right shadow. Recessed inputs carry top-left inner shadow.
  - Large blurs or dark gradients layer an SVG `<feTurbulence type="fractalNoise">` grain texture (`opacity: 0.04`) to prevent 8-bit banding.
- **Contrast Floor**: Body text must achieve APCA $|L_c| \ge 75$ and WCAG AA $\ge 4.5:1$. Large text ($\ge 18\text{pt}$ or bold $\ge 14\text{pt}$) must achieve APCA $|L_c| \ge 45$ and WCAG AA $\ge 3.0:1$.
- **Accent Footprint Law**: `brand_accent` must occupy $\le 5\%$ of the total viewport area. Do not paint large card backgrounds with accent colors.
<!-- END FOUNDATION:wcag-contrast-law -->

---

## Typography

- **Display Face**: `"{{display_font}}"`, sans-serif / serif (Always upright roman; no fake italic headers).
- **Body Face**: `"{{body_font}}"`, sans-serif (16px base, line-height 1.5).
- **Code / Telemetry**: `"{{mono_font}}"`, monospace (Numbers tabular-lining; `font-variant-numeric: tabular-nums`).
- **Reading Measure Clamping**: All prose containers MUST be bounded between `45ch` and `75ch` (`max-width: 68ch`).
- **The 2+1 Font Rule**: Maximum 3 font families on the entire page (`display`, `body`, and at most 1 `outlier` for wordmark/mono).

---

## Layout & Spacing

No arbitrary unscale pixels (`17px`, `23px`). All dimensions bind to this modular 8pt cadence ladder:

```css
--space-3xs: 2px;
--space-2xs: 4px;
--space-xs:  8px;
--space-sm:  12px;
--space-md:  16px;
--space-lg:  24px;
--space-xl:  32px;
--space-2xl: 48px;
--space-3xl: 64px;
--space-4xl: 96px;
--space-5xl: 128px;
```

---

## Elevation & Depth

Depth is expressed through layered surface tones and subtle elevation shadows:

| Level | Surface Token | Shadow Token | Visual Role |
| :--- | :--- | :--- | :--- |
| **Level 0 (Canvas)** | `colors.canvas` | `elevation.none` | Base background layer; zero shadow |
| **Level 1 (Card / Panel)** | `colors.surface` | `elevation.sm` | Content cards, data rows, sidebar columns |
| **Level 2 (Popover / Flyout)** | `colors.surface` | `elevation.md` | Dropdown menus, tooltips, floating command bars |
| **Level 3 (Modal / Sheet)** | `colors.surface` | `elevation.lg` | Centered modal dialogs, slide-in side sheets |
| **Level 4 (Alert / Toast)** | `colors.surface` | `elevation.xl` | System alert overlays, floating notification toasts |

- **Hairline Rule**: Shadows MUST be paired with a subtle `1px` border (`colors.surface_border`) on dark themes to guarantee layer separation.

<!-- START FOUNDATION:surface-optical-geometry -->
### Surface Craft: Concentric Radii, Optical Alignment, Shadow-Borders & Image Outlines
1. **Concentric Border Radius**: When nesting rounded elements with padding $\le 24\text{px}$, enforce `outerRadius = innerRadius + padding` (e.g., `rounded-2xl` `16px` outer card with `p-2` `8px` padding requires `rounded-lg` `8px` inner child).
2. **Optical Over Geometric Alignment**:
   - *Buttons with Text + Trailing/Leading Icon*: Reduce padding on the icon side by `2px` (`padding-inline-start: 16px; padding-inline-end: 14px` or `ps-4 pe-3.5`).
   - *Triangular / Asymmetric Glyphs (Play, Caret, Star)*: Shift play triangles `+2px` horizontally (`translateX(2px)`) to align visual center with geometric center.
3. **Shadows for Elevation vs. Borders for Structure**:
   - Use multi-layer transparent `box-shadow` for card/button depth (`--shadow-border: 0 0 0 1px oklch(0 0 0 / 0.06), 0 1px 2px -1px oklch(0 0 0 / 0.06), 0 2px 4px 0 oklch(0 0 0 / 0.04)` in light mode; `0 0 0 1px oklch(1 0 0 / 0.08)` in dark mode).
   - Keep `1px` solid borders strictly for structural dividers (`border-b`), table cell boundaries, and form input outlines.
4. **Neutral Image Outlines**: Apply a `1px` inner outline to images (`outline: 1px solid oklch(0 0 0 / 0.1); outline-offset: -1px` in light mode; `oklch(1 0 0 / 0.1)` in dark mode; Tailwind: `outline outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10`). Never use tinted palette grays (`slate`/`zinc`) on image edges.
5. **Tiered Brand Surface Contrast**: When stacking multiple brand-tinted background layers in dark mode, maintain $\ge 3.0:1$ non-text contrast between adjacent surface tiers.
<!-- END FOUNDATION:surface-optical-geometry -->

---

## Shapes

Corner radii establish the physical language of components across the product:

| Token | Dimension | Applied UI Roles | Rationale |
| :--- | :--- | :--- | :--- |
| `none` | `0px` | Data tables, code blocks, flat dividers, brutalist frames | Strict geometric precision |
| `xs` | `2px` | Status badges, hairline indicators, micro-tags | Sharp, subtle softening |
| `sm` | `4px` | Inputs, dropdown menu items, small tooltips, buttons | Compact interactive targets |
| `md` | `8px` | Standard cards, panels, popover menus, dialog boxes | Default component container radius |
| `lg` | `12px` | Large modal dialogs, elevated feature callouts | Distinct visual grouping |
| `xl` | `16px` | App shells, floating bottom sheets, hero cards | Generous modern container bounds |
| `full` | `9999px` | Avatars, pill tags, segmented switches, toggle pills | Fully circular or pill-shaped elements |

---

## Components

Standard styles for atom components within this design system:

### Buttons
- **Primary Button**: High contrast action element utilizing `colors.primary` with `colors.bg` text and `rounded.md`.
- **Secondary Button**: Outlined or soft surface element with subtle `colors.surface_border`.
- **States**: Every button must implement the 8-state contract (Default, Hover, Focus-Visible, Active, Disabled, Loading, Empty, Error).

### Input Fields
- Interactive inputs utilize `colors.surface` with `10px 14px` padding and `rounded.md`.
- Active focus requires a high-contrast 2px ring with 2px offset.

### Cards & Surfaces
- Structural containers use `colors.surface` with `rounded.lg`, `24px` internal padding, and Level 1 elevation paired with a 1px border.

---

## Do's and Don'ts

<!-- START FOUNDATION:constraint-matrix -->
Direct operational rules to prevent AI visual drift and template slop:

| Domain | ✅ DO | ❌ DON'T |
| :--- | :--- | :--- |
| **Colors** | Use semantic token variables (`colors.surface`, `colors.brand_accent`). | Hardcode raw arbitrary hex codes (`#17293a`) in component markup. |
| **Accent Footprint** | Restrict accent color to primary action buttons and focused states ($\le 5\%$). | Paint entire card backgrounds, table rows, or full-width headers with accent. |
| **Typography** | Clamp all paragraph and article text containers between `45ch` and `75ch`. | Allow prose text to stretch edge-to-edge across wide 1440px+ viewports. |
| **Numbers & Data** | Apply `font-variant-numeric: tabular-nums` to financial data, counters, and telemetry. | Use proportional figures that jitter or misalign in data tables. |
| **Spacing** | Snap all layout paddings, gaps, and margins strictly to the 8pt modular grid. | Invent ad-hoc arbitrary values like `margin: 13px; padding: 27px;`. |
| **Elevation** | Pair soft box-shadows with a `1px` structural hairline border on dark surfaces. | Use muddy, heavy black drop-shadows without surface border definition. |
| **Shapes** | Use consistent corner radius tokens across identical component tiers (`rounded.md`). | Mix sharp 0px corners, 6px corners, and pill buttons on the same surface. |
| **Motion** | Use fast `150ms–250ms` transitions with `cubic-bezier` easing curves. | Apply sluggish `>500ms` animations or bouncy gimmicks on routine UI clicks. |
| **Icons** | Standardize on one icon library (Lucide or Phosphor) with uniform `1.5px` stroke. | Mix filled, outline, multi-color, and mismatched icon libraries on one page. |
<!-- END FOUNDATION:constraint-matrix -->

---

## 🎛️ Liveliness Dials & Pre-Emit Critique

Score planned output 1–5 across the 6 axes. Any score < 3 triggers revision pass before rendering:

| Axis | Meaning | Threshold Target |
| :--- | :--- | :--- |
| **Philosophy** | Is there an authentic position the page takes, or is it a generic boilerplate? | Score >= 4 |
| **Hierarchy** | Can an eye distinguish primary, secondary, and tertiary weight in 2 seconds? | Score >= 4 |
| **Execution** | Are hairline borders, focus rings, contrast, and radius tokens exact? | Score >= 4 |
| **Specificity** | Does this interface strictly reflect this domain brief, avoiding AI templates? | Score >= 4 |
| **Restraint** | Is every non-functional gradient, excessive pill-button, and decorative fluff pruned? | Score >= 4 |
| **Variety** | Does this layout break alignment with previous project views (asymmetric spans, off-axis CTA)? | Score >= 4 |

---

## ⚡ Motion & Micro-Interactions

<!-- START FOUNDATION:four-gate-motion -->
Every candidate animation must pass the **4-Gate Motion Filter** before implementation:
1. **Gate 1 — Frequency Tier**:
   - `100+ times/day` (Command palettes, keyboard shortcuts, core nav, focus jumps): **0ms — Reject animation completely.**
   - `Tens of times/day` (Hover states, toggles, list traversal): `100ms–160ms` subtle compositor transition only.
   - `Occasional` (Modals, drawers, toasts, popovers): `150ms–300ms` standard spatial transition (`transform-origin` anchored to trigger).
   - `Rare / First-Time` (Onboarding, initial empty state, milestone completion): `300ms–400ms` split-and-stagger (`~80ms–100ms` delay).
2. **Gate 2 — Named Purpose**: Must serve *Feedback*, *Spatial Consistency* (exit along entry vector), *State Indication*, *Bridge for Teleporting Content*, *Explanation*, or *Rare Delight*. Never animate functional charts/data being read.
3. **Gate 3 — Interruptibility & Exact Recipes**:
   - Use **CSS transitions** (never keyframes) for interactive state changes so mid-flight reversal retargets smoothly. Never use `transition: all` or `will-change: all`.
   - **Scale on Press**: Use `active:not-disabled:scale-[0.96]` (`150ms ease-out`, never `< 0.95` and never bouncy elastic curves); expose a `static` prop to disable press scaling on high-frequency or toolbar controls.
   - **Contextual Icon Swap**: Animate icon state changes with `scale(0.25 -> 1)`, `opacity(0 -> 1)`, and `filter: blur(4px -> 0px)` (`duration: 300ms`, `bounce: 0`, `cubic-bezier(0.2, 0, 0, 1)`). Set `initial={false}` on `AnimatePresence` so default icons never animate on initial page load.
   - **Exit Subtlety**: Exits use shorter duration (`150ms`) and small fixed `translateY(-12px)` rather than full-height collapse.
4. **Gate 4 — Opt-In Reduced Motion**: Wrap motion in `@media (prefers-reduced-motion: no-preference)` or replace slides/scales with gentle opacity crossfades under `prefers-reduced-motion: reduce`.
<!-- END FOUNDATION:four-gate-motion -->

---

## 🎯 Iconography Standards

- **Standard Icon Pack**: Lucide Icons or Phosphor Icons (One optical strategy per surface; never mix libraries).
- **Match Stroke Width to Adjacent Text Weight (24px Grid)**:
  - Regular (`400`, `14–16px` text): `1.5px` stroke.
  - Medium / Semibold (`500–600` text): `2.0px` stroke.
  - Bold (`700` or standalone emphasis): `2.5px` stroke.
- **State & Asset Hygiene**: Single SVG with `currentColor` (strip hardcoded hex fills). Default state uses **Outline** variant; active/selected state uses **Fill** variant. Test legibility at `16px` render grid.
- **RTL Directionality (`dir="rtl"`)**: Mirror directional navigation arrows, chevrons, text-alignment glyphs, and send icons (`rtl:-scale-x-100`); NEVER flip brand logos, checkmarks, clocks/physical objects, or media playback controls.

---

## 🧱 The 8-State Control & 6-Family Screen State Machine Contract

<!-- START FOUNDATION:eight-state-contract -->
### A. Interactive Control 8-State Contract
Every interactive control (button, input, select, row) must provide explicit styling for all 8 states:
1. **Default**: Crisp baseline token geometry (`>= 44x44px` touch / `>= 40x40px` desktop hit target; `16px` minimum mobile input font size to prevent iOS Safari zoom).
2. **Hover**: Purposeful single-property transition (`@media (hover: hover) and (pointer: fine)` gated; NO universal `scale-105`).
3. **Focus-Visible**: Instant `2px` high-contrast ring with `2px` offset (`:focus-visible`, never bare `:focus` or `outline: none`; must not be obscured by sticky headers per WCAG 2.4.11).
4. **Active / Pressed**: `scale(0.96)` (`150ms ease-out`, disabled via `static` prop when needed).
5. **Disabled**: Reduced opacity (`0.4–0.5`) AND clear explanation of *why* when non-obvious (prefer keeping Submit enabled and validating on submit to focus the first error).
6. **Loading**: Inline spinner or skeleton matching layout geometry; `aria-busy="true"`.
7. **Empty**: Orientation + concrete next action (never a bare `"No results"` shrug).
8. **Error**: Instruction-first copy adjacent to the failing field (`aria-invalid="true"`, `aria-describedby`); zero blame or `"Oops!"`.

### B. Screen-Level 6-Family State Machine (`UI State Expander`)
A screen is a state machine, not a static poster. Every feature view must account for:
1. **Data States**: `loading` (skeleton when layout matters), `first-time-empty` (explain value + primary create CTA), `filtered-to-empty` (name the query + `"Clear filters"` button), `no-permission-empty`, `populated`, `partial-data` (graceful degradation when 1 sub-request or image fails), `stale`, `optimistic-updating`.
2. **Interaction States**: `default`, `hover`, `focus-visible`, `active`, `disabled-with-reason`, `selected`, `expanded/collapsed`, `dragging` (must include non-drag keyboard/click alternative per WCAG 2.5.7).
3. **Form States**: `placeholder-as-example-only` (persistent visible `<label>` required), `editing`, `valid`, `invalid-instructional`, `auto-filled` (never block password/OTP paste per WCAG 3.3.8), `submitting`, `submit-failed-recoverable`.
4. **Content States (Production Gremlins)**: Very long names/emails/URLs (`overflow-wrap: break-word`, `line-clamp` + tooltip access), `0` value, `1` item, `1,000+` items, localized string expansion (+30–50% width, logical CSS properties `margin-inline-start`).
5. **System States**: `offline`, `timeout`, `rate-limited`, `session-expired`, `maintenance`.
6. **Recovery States**: `retry`, `undo`, `restore-draft`, `reconnected-sync`.
<!-- END FOUNDATION:eight-state-contract -->

---

## 🎨 Palette Rotation Pool (Anti-Monoculture Sets)

To prevent repetitive warm beige/brass/espresso monoculture across consumer and craft briefs, rotate among these production-tested alternatives:

| Palette Set | Canvas & Surface | Primary Text | Accent & Intent | Rationale & Scene |
| :--- | :--- | :--- | :--- | :--- |
<!-- row:palette=cold-luxury -->| **Cold Luxury** | Silver-Grey `#F1F5F9` / Smoke `#E2E8F0` | Obsidian `#0F172A` | Mirror Chrome (`#64748B`) | High-end technical hardware, precision tools, automotive |
<!-- row:palette=deep-forest -->| **Deep Forest** | Bone White `#FDFBF7` / Muted Sage `#E9EFE6` | Deep Pine `#064E3B` | Raw Amber (`#D97706`) | Outdoor heritage, biological tools, climate technology |
<!-- row:palette=black-and-tan -->| **Black & Tan** | Clean Cream `#FAF7F2` / Sand `#EFE9DF` | True Off-Black `#121212`| Warm Tan (`#C28854`) | High-contrast editorial, modern fashion, studio agency |
<!-- row:palette=cobalt-and-cream -->| **Cobalt & Cream** | Light Cream `#FDFCE8` / Soft Mist `#F1F5F9` | Charcoal `#1E293B` | Deep Cobalt (`#1D4ED8`) | Modern fintech, verified commerce, legal platforms |
<!-- row:palette=terracotta-and-slate -->| **Terracotta + Slate**| Slate Canvas `#F8FAFC` / Cool Grey `#EEF2F6` | Dark Slate `#1E293B` | Warm Terracotta (`#C2410C`) | Craft physical goods, ceramics, culinary platforms |

*Rule*: Never ship the identical warm-craft palette twice in consecutive sprints. Pick a new set and lock it across the entire page.

---

## 📦 Design System Selection Protocol

Before authoring custom CSS or inventing ad-hoc component libraries, identify whether the surface demands an official enterprise design system:

| Context / Brief Intent | Mandatory Package | Architectural Rationale |
| :--- | :--- | :--- |
<!-- row:stack=fluent -->| **Microsoft / Enterprise B2B SaaS** | `@fluentui/react-components` | Native Fluent design tokens, verified accessibility, Windows native feel |
<!-- row:stack=carbon -->| **IBM / Data-Dense Operational Suites** | `@carbon/react` + `@carbon/styles` | High-density data grids, battle-tested accessibility |
<!-- row:stack=polaris -->| **E-Commerce Merchant Surfaces** | `@shopify/polaris` | Expected merchant UX patterns, Shopify admin compliance |
<!-- row:stack=primer -->| **GitHub / Devtool Integrations** | `@primer/react` or `@primer/react-brand` | Authentic GitHub devtool identity, Primer tokens |
<!-- row:stack=radix -->| **Modern Component-Owned React App** | `@radix-ui/themes` or `shadcn/ui` | Fully accessible headless primitives, customized token ownership |
<!-- row:stack=tailwind -->| **Tailwind-Native SaaS Marketing** | Tailwind CSS v4 utilities + Motion | Unopinionated performance, native CSS variables |

---

## 👤 UX Flows & Brand Voice

- **User Persona**: `{{primary_persona}}`
- **Key Navigation Patterns**: `{{nav_patterns}}` (e.g., Sidebar Master-Detail | Command Palette + Canvas | Stepped Wizard)
- **Communication Style / Brand Voice**: `{{brand_voice}}` (e.g., Technical & terse | Friendly & conversational | Academic gravitas)

---

## 🧭 Systemic UX & Anti-Dark-Pattern Ethics Checklist

Before finalizing any screen design, verify these interaction principles:

1. **Observe, Oppose, Upscale**: Cut unnecessary steps, modals, and friction points by $50\%$ compared to legacy flows.
2. **Non-Modal Contextual Overlays**: Use semi-transparent side drawers or inline panels instead of disruptive screen-blocking popups.
3. **Direct Spatial / Timeline Scrubbing**: Replace abstract numeric inputs (e.g., `ms` offsets) with direct draggable timeline blocks or spatial scrubbers.
4. **De-Frankensteining**: Maintain a single consolidated icon library and unified primary + context menu structure.
5. **Flattened Persistent Filters**: Keep filter chips visible and sticky; give users granular control over feed tags and collections.
6. **Thumb-Zone Mobile Ergonomics**: Place primary search and core actions within natural thumb reach ($\ge 48\text{px}$ touch targets at the bottom viewport).
7. **Anti-Dark Patterns**: Zero visual interference on cancel/unsubscribe buttons, zero confirmshaming copy, zero button-swapping traps.
