# 🎨 Brief Inference & The Three Dials Engine

> **Origin**: Sovereign UI Aesthetic & Design Philosophy Protocol.
> **Purpose**: Eliminates formulaic AI UI designs (purple mesh gradients, centered dark heroes, 3 equal cards, generic glassmorphism) through contextual brief inference and mathematical configuration dials.

---

## 1. Brief Inference Protocol ("Read the Room")

Before writing a single line of frontend code (Flutter widgets, Jetpack Compose, React TSX, or Tailwind CSS), the agent MUST output a **one-line Design Read**:

> **"Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <design system or aesthetic family>."**

### Signals to Infer
1. **Page Kind**: Landing (SaaS / consumer / agency / event), Dashboard (dense data / analytical), Portfolio (developer / designer), Mobile Screen (Flutter / Android), or Redesign.
2. **Audience Demographics**: Technical B2B procurement vs. design-conscious consumers vs. internal operations.
3. **Reference Signals**: Explicit brands mentioned (Linear, Stripe, Apple, Raycast, Vercel) or competitor URLs.
4. **Quiet Constraints**: WCAG 2.1 AA accessibility, trust-first regulated industries, or high-density cockpit operations.

---

## 2. The Three Dials (Configuration Matrix)

Every layout, motion, and density decision is governed by three locked numerical dials (scale 1–10):

| Dial | Metric | Scale Range | Default Baseline |
| :--- | :--- | :---: | :---: |
| **`DESIGN_VARIANCE`** | Layout Asymmetry & Organic Rhythm | 1 (Perfect Grid Symmetry) $\leftrightarrow$ 10 (Artsy Chaos / Editorial) | **8** |
| **`MOTION_INTENSITY`** | Animation Velocity & Spring Physics | 1 (Completely Static) $\leftrightarrow$ 10 (Cinematic Physics / Keyframes) | **6** |
| **`VISUAL_DENSITY`** | Information Packing & Whitespace | 1 (Art Gallery / Airy Whitespace) $\leftrightarrow$ 10 (Cockpit / Bloomberg Terminal) | **4** |

### Preset Presets by Domain
```
+------------------------------------+----------+--------+---------+
| Target Domain                      | VARIANCE | MOTION | DENSITY |
+------------------------------------+----------+--------+---------+
| Mainstream B2B SaaS                |    7     |   6    |    4    |
| Creative Agency / Studio Portfolio |    9     |   8    |    3    |
| Luxury / Premium Consumer App      |    7     |   6    |    3    |
| Developer Tool / Terminal Utility  |    5     |   4    |    7    |
| Financial / Trading / Analytical   |    3     |   2    |    9    |
| Healthcare / Regulated Public Org  |    3     |   2    |    5    |
+------------------------------------+----------+--------+---------+
```

---

## 3. The Anti-Default Discipline

Strictly forbid default LLM clichés across all UI implementations:
- **No AI-Purple/Indigo Meshes**: Replace with muted neutral backgrounds (`zinc-950`, `slate-950`) or warm earth undertones with deliberate high-contrast semantic accents.
- **No Symmetric Three-Card Grids**: Use asymmetric Bento grids (e.g., 2:1 column ratios, featured hero cards).
- **No Decorative Glassmorphism on Everything**: Use solid, crisp background layers with subtle 1px border strokes (`border-zinc-800/60`).
- **No Infinite Floating Loops**: Micro-interactions must be triggered by user input (hover, tap, active), never continuous unprompted bouncing.
