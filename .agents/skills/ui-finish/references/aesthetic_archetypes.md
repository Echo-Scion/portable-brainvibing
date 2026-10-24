# 🎨 Aesthetic Archetypes: Production Design Systems

When building modern web and mobile applications, avoid defaulting to generic AI templates (Inter font + slate-900 background + purple blur). Adopt a cohesive, deliberate aesthetic archetype matching the product persona.

---

## 1. Minimalist / Linear-Style (Engineered Precision)

Ideal for developer tools, technical B2B SaaS, and high-velocity workflows.

- **Palette**: Monochromatic neutrals (Deep neutral black `#09090b`, zinc grays `#27272a`, crisp white `#fafafa`). Single sharp accent color (e.g., Electric Orange `#ff5c00` or Linear Indigo `#5e6ad2`).
- **Typography**: Geometric sans (Geist, Inter, SF Pro). Tight tracking (`-0.02em`), compact line-heights, uppercase tracked labels (`tracking-wider text-xs font-mono`).
- **Borders & Radii**: Precision 1px borders (`border-zinc-800`), restrained corner radii (`rounded-md` or `rounded-lg`, 6px–8px).
- **Elevation**: Flat surfaces with subtle 1px border contrast (`bg-zinc-900/50 border border-zinc-800`). No heavy drop shadows.
- **Micro-interactions**: Crisp 100ms–150ms transitions (`transition-colors duration-150`). Subtle keyboard shortcut badges (`<kbd>`).

---

## 2. Neobrutalist / High-Contrast Editorial

Ideal for developer portfolios, creative studios, cultural events, and design tools.

- **Palette**: High-contrast, unblended colors (Pure black `#000000`, paper white `#ffffff`, saturated primary yellow `#ffe600`, neo-green `#23c55e`).
- **Typography**: Heavy grotesque or monospaced display (Space Grotesk, Syne, JetBrains Mono). Large display headings (`text-5xl md:text-7xl font-black`).
- **Borders & Radii**: Hard 2px–3px black borders (`border-2 border-black` or `border-3 border-black`). Zero or minimal radius (`rounded-none` or `rounded-sm`).
- **Elevation**: Hard offset drop shadows with ZERO blur (`shadow-[4px_4px_0px_#000000]` or `shadow-[6px_6px_0px_#000000]`).
- **Interactions**: Button click moves into the shadow (`active:translate-x-1 active:translate-y-1 active:shadow-none`).

---

## 3. Warm Tactile / Organic Soft

Ideal for consumer wellness, note-taking apps, community platforms, and lifestyle products.

- **Palette**: Warm earthen neutrals (Warm cream canvas `#fdfbf7`, soft taupe borders `#e6e2dd`, deep espresso text `#2b2621`). Muted natural accents (Terracotta `#c85a32`, Sage green `#6b8e23`).
- **Typography**: Humanist sans or warm serifs (Newsreader, Fraunces, Source Serif, Plus Jakarta Sans). Generous leading (`leading-relaxed`), relaxed character measure.
- **Borders & Radii**: Fluid organic radii (`rounded-2xl` or `rounded-3xl`, 16px–24px). Soft border tones with slight alpha transparency.
- **Elevation**: Multi-layered ambient diffuse shadows (`shadow-[0_8px_30px_rgb(0,0,0,0.04)]`). Smooth tactile button pills.
- **Interactions**: Springy physics (`transition-all duration-300 ease-out`). Warm hover states with gentle scaling (`hover:scale-[1.01]`).

---

## 4. Cold Luxury / Restrained Dark Mode

Ideal for fintech, luxury consumer products, AI infrastructure, and cryptographic applications.

- **Palette**: Deep slate-black canvas (`#030712`), obsidian card surfaces (`#0b0f19`), cool platinum text (`#f8fafc`), muted silver secondary (`#94a3b8`). Muted cold metallic accents (Cobalt `#2563eb` or Platinum Blue `#38bdf8`).
- **Typography**: Clean neutral sans with deliberate display contrast (Satoshi, General Sans, Instrument Sans). Strict size hierarchy with ample negative space.
- **Borders & Radii**: Ultra-fine semi-transparent borders (`border border-white/10` or `border-slate-800`). Smooth medium radii (`rounded-xl`, 12px).
- **Elevation**: Subtle directional top-lighting (`bg-gradient-to-b from-white/[0.08] to-transparent`). Soft directional blur shadows with zero glow halos.
- **Interactions**: Understated opacity and border shifts (`hover:border-white/25 transition-all duration-200`).

---

## 5. Token Implementation Matrix

| Token Class | Minimalist / Linear | Neobrutalist | Warm Tactile | Cold Luxury |
| :--- | :--- | :--- | :--- | :--- |
| **Border Width** | `border` (1px) | `border-2` (2px) | `border` (1px) | `border` (1px) |
| **Corner Radius** | `rounded-md` (6px) | `rounded-none` (0px) | `rounded-2xl` (16px) | `rounded-xl` (12px) |
| **Shadow** | Subtle / None | `shadow-[4px_4px_0px_#000]` | `shadow-sm` / diffuse | Ambient soft |
| **Font Pairing** | Geist Sans + Mono | Space Grotesk + Mono | Plus Jakarta + Serif | Satoshi + Neutral |
| **Action Motion** | 150ms ease-out | Immediate jump-in | 300ms gentle spring | 200ms smooth fade |
