---
name: "{{project_name}}"
version: "1.0.0"
description: "Design system specification, visual tokens, and constraints for {{project_name}}"
tokens:
  colors:
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
    fonts:
      display: "{{display_font}}"
      body: "{{body_font}}"
      mono: "{{mono_font}}"
    sizes:
      xs: "12px"
      sm: "14px"
      base: "16px"
      lg: "18px"
      xl: "20px"
      "2xl": "24px"
      "3xl": "30px"
      "4xl": "36px"
    weights:
      normal: 400
      medium: 500
      semibold: 600
      bold: 700
    line_heights:
      tight: 1.25
      snug: 1.375
      normal: 1.5
      relaxed: 1.625
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

## 1. 🎭 Identity & Archetype Selection

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

---

## 2. 🎛️ Liveliness Dials & Pre-Emit Critique

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

## 3. 🎨 Color Palette & Contrast Hierarchy (WCAG 2.1 AA)

<!-- START FOUNDATION:wcag-contrast-law -->
*All text/background pairings must pass WCAG AA (4.5:1 for body, 3:1 for large display).*

```yaml
tokens:
  colors:
    canvas: "{{canvas_hex}}"        # Base background surface
    surface: "{{surface_hex}}"      # Elevated card / panel
    surface_border: "{{border_hex}}"# 1px structural separator
    text_primary: "{{text_primary}}"# High-contrast reading copy (>= 4.5:1)
    text_muted: "{{text_muted}}"    # Secondary labels & captions (>= 4.5:1)
    brand_accent: "{{accent_hex}}"  # Interactive action (<= 5% viewport area)
    status_error: "#EF4444"
    status_success: "#10B981"
    status_warning: "#F59E0B"
    status_info: "#3B82F6"
```

- **Contrast Floor**: Body text must achieve $\ge 4.5:1$ against its background surface. Large text ($\ge 18\text{pt}$ or bold $\ge 14\text{pt}$) must achieve $\ge 3.0:1$.
- **Accent Footprint Law**: `brand_accent` must occupy $\le 5\%$ of the total viewport area. Do not paint large card backgrounds with accent colors.
<!-- END FOUNDATION:wcag-contrast-law -->

---

## 4. 📐 Spacing Scale & 8pt Grid Cadence

No arbitrary unscale pixels (`17px`, `23px`). All dimensions bind to this modular ladder:

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

## 5. 🔲 Shape & Corner Radii (`rounded`)

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

## 6. 🏛️ Elevation, Depth & Layer Hierarchy (`elevation`)

Depth is expressed through layered surface tones and subtle elevation shadows:

| Level | Surface Token | Shadow Token | Visual Role |
| :--- | :--- | :--- | :--- |
| **Level 0 (Canvas)** | `colors.canvas` | `elevation.none` | Base background layer; zero shadow |
| **Level 1 (Card / Panel)** | `colors.surface` | `elevation.sm` | Content cards, data rows, sidebar columns |
| **Level 2 (Popover / Flyout)** | `colors.surface` | `elevation.md` | Dropdown menus, tooltips, floating command bars |
| **Level 3 (Modal / Sheet)** | `colors.surface` | `elevation.lg` | Centered modal dialogs, slide-in side sheets |
| **Level 4 (Alert / Toast)** | `colors.surface` | `elevation.xl` | System alert overlays, floating notification toasts |

- **Hairline Rule**: Shadows MUST be paired with a subtle `1px` border (`colors.surface_border`) on dark themes to guarantee layer separation.

---

## 7. 🔤 Typography & Measure Clamping

- **Display Face**: `"{{display_font}}"`, sans-serif / serif (Always upright roman; no fake italic headers).
- **Body Face**: `"{{body_font}}"`, sans-serif (16px base, line-height 1.5).
- **Code / Telemetry**: `"{{mono_font}}"`, monospace (Numbers tabular-lining; `font-variant-numeric: tabular-nums`).
- **Reading Measure Clamping**: All prose containers MUST be bounded between `45ch` and `75ch` (`max-width: 68ch`).
- **The 2+1 Font Rule**: Maximum 3 font families on the entire page (`display`, `body`, and at most 1 `outlier` for wordmark/mono).

---

## 8. ⚡ Motion, Transitions & Micro-Interactions (`motion`)

Animations must feel snappy, physical, and restrained:

| Intent | Duration | Easing Curve | Use Case |
| :--- | :--- | :--- | :--- |
| **Micro-feedback** | `75ms` (`instant`) | `easing.default` | Active click/press depression, toggle switch |
| **Interactive State**| `150ms` (`fast`) | `easing.out` | Hover color/border shift, tooltip fade |
| **Layout / Expansion**| `250ms` (`normal`) | `easing.default` | Accordion fold, dropdown expansion, tab slide |
| **Modal / Dialog** | `250ms` (`normal`) | `easing.out` | Modal fade & scale-in (`scale(0.96) -> scale(1)`) |
| **Deliberate Reveal** | `400ms` (`deliberate`) | `easing.out` | Page route transition, hero section entrance |

- **Accessibility Mandate**: Respect user motion preferences:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

---

## 9. 🎯 Iconography Standards

- **Standard Icon Pack**: Lucide Icons or Phosphor Icons (Pick one library, never mix multiple icon styles).
- **Sizing Grid**:
  - `16px` (`size-4`): Compact inline badges, input field adornments, table row actions.
  - `20px` (`size-5`): Standard button icons, navigation list items, tab headers.
  - `24px` (`size-6`): Hero feature highlights, empty state visual anchors, page titles.
- **Stroke Uniformity**: Consistent `1.5px` stroke weight across all icons (or `2px` for bold/compact). Never mix thin and thick icons.
- **Alignment**: Center icon optical bounds vertically with adjacent typography.

---

## 10. 🧱 The 8-State Interactive Contract

<!-- START FOUNDATION:eight-state-contract -->
Every interactive element (button, input, select, row) must provide explicit styling for all 8 states:

1. **Default**: Crisp baseline token geometry.
2. **Hover**: Purposeful single-property transition (color or border tint; NO universal `scale-105`).
3. **Focus-Visible**: Instant 2px high-contrast ring with 2px offset (zero fade-in transition).
4. **Active / Pressed**: Subtle scale compression (`scale(0.98)`) or 1px translateY depression.
5. **Disabled**: Reduced opacity (`0.4–0.5`), `cursor: not-allowed`, inert pointer events.
6. **Loading**: Inline indeterminate spinner or skeleton shimmer; interactive click blocked.
7. **Empty**: Contextual illustration or typography explaining zero state + clear primary action.
8. **Error**: Inline semantic red message + aria-invalid marker; focus redirected to field.
<!-- END FOUNDATION:eight-state-contract -->

---

## 11. 🎨 Palette Rotation Pool (Anti-Monoculture Sets)

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

## 12. 📦 Design System Selection Protocol

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

## 13. 🚫 Do's and Don'ts (Agent Behavioral Constraint Matrix)

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

## 14. 👤 UX Flows & Brand Voice

- **User Persona**: `{{primary_persona}}`
- **Key Navigation Patterns**: `{{nav_patterns}}` (e.g., Sidebar Master-Detail | Command Palette + Canvas | Stepped Wizard)
- **Communication Style / Brand Voice**: `{{brand_voice}}` (e.g., Technical & terse | Friendly & conversational | Academic gravitas)
