# Design Direction: {{project_name}}

> **Design Read & Soul**: This document supplies project-specific aesthetic direction, locked design tokens, and structural rules.
> The AI agent treats this file as **immutable data to apply**, not speculative instructions to improvise.

---

## 1. 🎭 Identity & Archetype Selection

Select exactly **one** primary archetype during scaffolding to eliminate generic aesthetic convergence:

| # | Archetype | Target Vibe & Use Case | Display + Body Typography | Canvas & Surface Palette | Accent & Footprint (<=5%) |
| :- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Swiss Editorial** | Journalistic gravitas, cultural institutions, essays | Newsreader (Serif) + Public Sans | Paper `#F9F9FB` / Clean Slate `#FFFFFF` | Razor Crimson (`#D92D20`) |
| **02** | **Dark Industrial** | Developer infra, hardware telemetry, CLI tooling | Space Grotesk + JetBrains Mono | Obsidian `#0D0F12` / Dark Slate `#16191E` | Amber Phosphor (`#F59E0B`) |
| **03** | **Density Cockpit** | Trading terminals, observability suites, analytics | Inter + IBM Plex Mono | Matte Charcoal `#111318` / Panel `#191C24` | Cyan Telemetry (`#06B6D4`) |
| **04** | **Neo-Brutalist** | Developer tools, indie hacking, direct utility | Archivo (Black) + Space Mono | Canvas `#F8F9FA` / Stark Border `2px #000` | Electric Yellow (`#FACC15`) |
| **05** | **Tactile Ambient** | Premium SaaS, audio tools, creative workflows | Plus Jakarta Sans + Inter | Dusk Neutral `#131418` / Layer `#1E2026` | Iris Purple (`#6366F1`) |
| **06** | **Modern Minimal** | Production SaaS, API platforms, financial engines | Geist Sans + Inter | Paper `#FFFFFF` / Mist Card `#F8FAFC` | Electric Blue (`#2563EB`) |
| **07** | **Retro-Futuristic** | Sci-fi interfaces, simulation tools, synth editors | VT323 / Share Tech + Overpass Mono | CRT Carbon `#12100E` / Rust Surface `#1C1814` | CRT Amber (`#FFB000`) |
| **08** | **Academic Mono** | Research repositories, theorem provers, archives | Playfair Display + Courier Prime | Newsprint Cream `#F5F2EB` / Warm Tint `#EDE8DC` | Deep Bronze (`#5A4A42`) |
| **09** | **Warm Editorial** | Food/hospitality, lifestyle products, storytelling | Fraunces + Cabinet Grotesk | Oatmeal `#FBF9F4` / Surface `#F2EDE2` | Terracotta Clay (`#C85A32`) |
| **10** | **Cyber Terminal** | Security dashboards, forensic scanners, protocol monitors | Red Hat Mono + Fira Code | Deep Abyss `#05080E` / Grid Panel `#0B111C` | Matrix Emerald (`#10B981`) |
| **11** | **Luxury Atelier** | Fashion, bespoke architecture, premium portfolios | Cormorant Garamond + Satoshi | Soft Ivory `#FAF9F6` / Card `#F3EFE6` | Deep Noir (`#18181B`) |
| **12** | **Solar Minimal** | Climate tech, renewable platforms, biology tools | Outfit + Source Sans 3 | Sage Off-White `#F4F6F2` / Leaf Tint `#E8EDE3` | Forest Viridian (`#15803D`) |

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

## 3. 🎨 Color Palette Tokens (WCAG 2.x Compliant)

*All text/background pairings must pass WCAG AA (4.5:1 for body, 3:1 for large display).*

```yaml
tokens:
  colors:
    canvas: "{{canvas_hex}}"        # Base background surface
    surface: "{{surface_hex}}"      # Elevated card / panel
    surface_border: "{{border_hex}}"# 1px structural separator
    text_primary: "{{text_primary}}"# High-contrast reading copy
    text_muted: "{{text_muted}}"    # Secondary labels & captions (>= 4.5:1)
    brand_accent: "{{accent_hex}}"  # Interactive action (<= 5% viewport area)
    status_error: "#EF4444"
    status_success: "#10B981"
    status_warning: "#F59E0B"
```

---

## 4. 📐 Mathematical Spacing Scale (8pt Grid)

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

## 5. 🔤 Typography & Measure Clamping

- **Display Face**: `"{{display_font}}"`, sans-serif / serif (Always upright roman; no fake italic headers).
- **Body Face**: `"{{body_font}}"`, sans-serif (16px base, line-height 1.5).
- **Code / Telemetry**: `"{{mono_font}}"`, monospace (Numbers tabular-lining; `font-variant-numeric: tabular-nums`).
- **Reading Measure Clamping**: All prose containers MUST be bounded between `45ch` and `75ch` (`max-width: 68ch`).
- **The 2+1 Font Rule**: Maximum 3 font families on the entire page (`display`, `body`, and at most 1 `outlier` for wordmark/mono).

---

## 6. 🧱 The 8-State Interactive Contract

Every interactive element (button, input, select, row) must provide explicit styling for all 8 states:

1. **Default**: Crisp baseline token geometry.
2. **Hover**: Purposeful single-property transition (color or border tint; NO universal `scale-105`).
3. **Focus-Visible**: Instant 2px high-contrast ring with 2px offset (zero fade-in transition).
4. **Active / Pressed**: Subtle scale compression (`scale(0.98)`) or 1px translateY depression.
5. **Disabled**: Reduced opacity (`0.4–0.5`), `cursor: not-allowed`, inert pointer events.
6. **Loading**: Inline indeterminate spinner or skeleton shimmer; interactive click blocked.
7. **Empty**: Contextual illustration or typography explaining zero state + clear primary action.
8. **Error**: Inline semantic red message + aria-invalid marker; focus redirected to field.

---

## 7. 🎨 Palette Rotation Pool (Anti-Monoculture Sets)

To prevent repetitive warm beige/brass/espresso monoculture across consumer and craft briefs, rotate among these production-tested alternatives:

| Palette Set | Canvas & Surface | Primary Text | Accent & Intent | Rationale & Scene |
| :--- | :--- | :--- | :--- | :--- |
| **Cold Luxury** | Silver-Grey `#F1F5F9` / Smoke `#E2E8F0` | Obsidian `#0F172A` | Mirror Chrome (`#64748B`) | High-end technical hardware, precision tools, automotive |
| **Deep Forest** | Bone White `#FDFBF7` / Muted Sage `#E9EFE6` | Deep Pine `#064E3B` | Raw Amber (`#D97706`) | Outdoor heritage, biological tools, climate technology |
| **Black & Tan** | Clean Cream `#FAF7F2` / Sand `#EFE9DF` | True Off-Black `#121212`| Warm Tan (`#C28854`) | High-contrast editorial, modern fashion, studio agency |
| **Cobalt & Cream** | Light Cream `#FDFCE8` / Soft Mist `#F1F5F9` | Charcoal `#1E293B` | Deep Cobalt (`#1D4ED8`) | Modern fintech, verified commerce, legal platforms |
| **Terracotta + Slate**| Slate Canvas `#F8FAFC` / Cool Grey `#EEF2F6` | Dark Slate `#1E293B` | Warm Terracotta (`#C2410C`) | Craft physical goods, ceramics, culinary platforms |

*Rule*: Never ship the identical warm-craft palette twice in consecutive sprints. Pick a new set and lock it across the entire page.

---

## 8. 📦 Design System Selection Protocol

Before authoring custom CSS or inventing ad-hoc component libraries, identify whether the surface demands an official enterprise design system:

| Context / Brief Intent | Mandatory Package | Architectural Rationale |
| :--- | :--- | :--- |
| **Microsoft / Enterprise B2B SaaS** | `@fluentui/react-components` | Native Fluent design tokens, verified accessibility, Windows native feel |
| **IBM / Data-Dense Operational Suites** | `@carbon/react` + `@carbon/styles` | High-density data grids, battle-tested accessibility |
| **E-Commerce Merchant Surfaces** | `@shopify/polaris` | Expected merchant UX patterns, Shopify admin compliance |
| **GitHub / Devtool Integrations** | `@primer/react` or `@primer/react-brand` | Authentic GitHub devtool identity, Primer tokens |
| **Modern Component-Owned React App** | `@radix-ui/themes` or `shadcn/ui` | Fully accessible headless primitives, customized token ownership |
| **Tailwind-Native SaaS Marketing** | Tailwind CSS v4 utilities + Motion | Unopinionated performance, native CSS variables |

---

## 9. 👤 UX Flows & Voice

- **User Persona**: `{{primary_persona}}`
- **Key Navigation Patterns**: `{{nav_patterns}}` (e.g., Sidebar Master-Detail | Command Palette + Canvas | Stepped Wizard)
- **Communication Style / Brand Voice**: `{{brand_voice}}` (e.g., Technical & terse | Friendly & conversational | Academic gravitas)

