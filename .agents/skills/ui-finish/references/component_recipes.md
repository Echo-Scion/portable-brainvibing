# 🧱 Production Component Recipes & Architectural Patterns

> **Design Read**: Curated, production-grade layout recipes and structural sketches.
> Supports both **Web (Semantic HTML5 + Vanilla CSS/Tailwind tokens)** and **Flutter (Material 3 + Custom Widgets)**.
> Avoids AI-default tropes (uniform centered grids, purple glow cards, fake browser chrome).

---

## 1. Navigation Architectures

### N1. Floating Detached Pill (Modern Minimal)
*Use When*: Clean modern interfaces where the canvas should flow uninterrupted behind the header.
- **Web Implementation**:
```css
.nav-floating-pill {
  position: fixed;
  top: var(--space-md, 16px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-lg, 24px);
  padding: var(--space-xs, 8px) var(--space-lg, 24px);
  background: rgba(18, 20, 24, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  z-index: 50;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
```
- **Flutter Implementation**:
```dart
ClipRRect(
  borderRadius: BorderRadius.circular(32),
  child: BackdropFilter(
    filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF121418).withOpacity(0.85),
        borderRadius: BorderRadius.circular(32),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [...navItems]),
    ),
  ),
);
```

### N2. Canonical SaaS 3-Section Header
*Use When*: Production platforms requiring clear brand identity, central navigation links, and primary action.
- Wordmark (Left, `font-weight: 700`, line-height: 1)
- Link cluster (Center, `display: flex; gap: 24px`, hover subtle text color transition)
- Action CTA (Right, high-contrast button + optional secondary login link)

---

## 2. Hero Section Archetypes

### H1. Asymmetric Split Diptych (70/30 or 60/40)
*Use When*: Technical products where real code, live metrics, or interactive demo balances headline copy.
- **Rule**: Eyebrow label and CTA break alignment with the headline (eyebrow margin-aligned or numeral-anchored, never 100% centered-everything).
- **Web Skeleton**:
```html
<section class="hero-diptych">
  <div class="hero-diptych__content">
    <div class="hero-diptych__eyebrow">01 — SPECIFICATION FIRST</div>
    <h1 class="hero-diptych__title">Deterministic AI Engineering for Real Systems.</h1>
    <p class="hero-diptych__lede">Eliminating prompt drift with verified AST scanning, local vector memory, and strict verification gates.</p>
    <div class="hero-diptych__actions">
      <button class="btn btn-primary">Initialize Workspace</button>
      <span class="hero-diptych__meta">v1.0.0 · Pure Python stdlib</span>
    </div>
  </div>
  <div class="hero-diptych__capture">
    <!-- Live telemetry or terminal block, NO fake drawn chrome -->
    <pre class="telemetry-block"><code>$ verify_agents --all
[PASS] Security & AST Integrity: 0 vulnerabilities
[PASS] Mechanical link check: 0 broken links</code></pre>
  </div>
</section>
```

### H2. Stat-Led High-Density Cockpit
*Use When*: Observability, analytics, fintech, or developer dashboards.
- Lead with an oversized metric (`font-size: clamp(3rem, 8vw, 6rem)`, `font-variant-numeric: tabular-nums`).
- Qualifier label underneath in small uppercase tracked type (`letter-spacing: 0.05em`).

---

## 3. Feature Blocks & Bento Grids

### F1. The Asymmetric Bento Grid
*Rule*: NEVER emit uniform equal 3-box cards. Vary spans across 1×1, 2×1, 1×2, and 2×2 blocks.
- **Web Skeleton**:
```html
<div class="bento-grid">
  <!-- Hero Tile (2x2 on desktop) -->
  <article class="bento-card bento-card--hero">
    <span class="bento-card__tag">Core Guardrail</span>
    <h3>Evidence Before Claims</h3>
    <p>Every claim requires mechanical verification proof with Exit Code 0.</p>
  </article>
  
  <!-- Narrow Telemetry Tile (1x2) -->
  <article class="bento-card bento-card--tall">
    <span class="bento-card__stat">0 ms</span>
    <p>Local AST execution latency.</p>
  </article>

  <!-- Standard Metric Tile (1x1) -->
  <article class="bento-card">
    <h4>Zero Sidecars</h4>
    <p>Runs cleanly without external daemon processes.</p>
  </article>
</div>
```
- **CSS Grid Layout**:
```css
.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md, 16px);
}
.bento-card--hero {
  grid-column: span 2;
  grid-row: span 2;
}
.bento-card {
  background: var(--surface);
  border: 1px solid var(--surface-border);
  border-radius: var(--radius-md, 8px);
  padding: var(--space-lg, 24px);
  transition: border-color 150ms ease;
}
.bento-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
}
```

### F2. Tabular Spec Sheet
*Use When*: API documentation, hardware specs, enterprise plan comparisons.
- Rows separated by 1px hairline rules (`border-bottom: 1px solid var(--surface-border)`).
- Numerics rendered in monospace font with tabular numerals (`font-variant-numeric: tabular-nums`).
- No bulky card boxes; lead with clean typography and whitespace.

---

## 4. Call-to-Action (CTA) Recipes

### C1. Inline Form as CTA
*Use When*: Fast user conversion without redirecting to a separate blank page.
- Single unified input container:
```html
<form class="inline-cta-form">
  <input type="email" placeholder="developer@company.com" required class="inline-cta-form__input" />
  <button type="submit" class="inline-cta-form__btn">Get Access →</button>
</form>
```
- Continuous 1px border encasing both input and button, preventing disjointed pill gaps.

---

## 5. Footers & Colophons

### FT1. Editorial Colophon Footer
*Use When*: High-craft tools, developer platforms, technical documentation.
- Left column: Masthead wordmark + system version + build hash.
- Center columns: Categorized navigation columns with uppercase muted headers.
- Right column: System status badge (e.g., green dot `All Systems Operational`).
- Bottom row: License, copyright, and keyboard navigation hint (`Press ⌘K for commands`).

---

## 6. Kinetic Choreography & Scroll Patterns

### M1. Canonical Sticky-Stack (Card Stacking on Scroll)
*Use When*: Multi-feature showcases or stepped narratives where cards physically stack and recede into background depth.
*Rule*: Pin at viewport top (`start: "top top"`), pin the outer shell, and tween the inner wrapper to prevent jitter. Always provide accessible non-pin fallback for `prefers-reduced-motion`.

```tsx
"use client";
import React, { useRef, useEffect, useId, type ReactNode } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function StickyStack({ cards }: { cards: ReactNode[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldReduceMotion = useReducedMotion();
  const instanceId = useId().replace(/:/g, "");
  const cardClass = `stack-card-${instanceId}`;
  const innerClass = `stack-inner-${instanceId}`;

  useEffect(() => {
    if (shouldReduceMotion || !containerRef.current || cards.length <= 1) return;

    const ctx = gsap.context(() => {
      const cardElements = gsap.utils.toArray<HTMLElement>(`.${cardClass}`);
      cardElements.forEach((card, i) => {
        if (i === cardElements.length - 1) return;

        ScrollTrigger.create({
          trigger: card,
          start: "top top",
          endTrigger: cardElements[cardElements.length - 1],
          end: "top top",
          pin: true,
          pinSpacing: false,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        });

        const inner = card.querySelector(`.${innerClass}`);
        if (!inner) return;

        gsap.to(inner, {
          scale: 0.92,
          opacity: 0.55,
          ease: "none",
          scrollTrigger: {
            trigger: cardElements[i + 1],
            start: "top bottom",
            end: "top top",
            scrub: true,
            invalidateOnRefresh: true,
          },
        });
      });
    }, containerRef);

    return () => ctx.revert();
  }, [shouldReduceMotion, cards.length, cardClass, innerClass]);

  return (
    <div ref={containerRef} className="relative">
      {cards.map((card, i) => (
        <div
          key={i}
          style={{ zIndex: i + 1 }}
          className={`${cardClass} relative min-h-[100dvh] flex items-center justify-center`}
        >
          <div className={`${innerClass} w-full flex items-center justify-center will-change-transform`}>
            {card}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### M2. Horizontal-Pan (Scrubbed Track Pattern)
*Use When*: Gallery, portfolio showcase, or chronological timeline traveling horizontally as user scrolls vertically.
*Rule*: Function-based distance calculation with `invalidateOnRefresh: true`. Under `prefers-reduced-motion`, degrade gracefully to `overflow-x-auto scroll-smooth snap-x`.

```tsx
"use client";
import React, { useRef, useEffect, type ReactNode } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useReducedMotion } from "motion/react";

gsap.registerPlugin(ScrollTrigger);

export function HorizontalPan({ children }: { children: ReactNode }) {
  const wrapRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const shouldReduceMotion = useReducedMotion();

  useEffect(() => {
    if (shouldReduceMotion || !wrapRef.current || !trackRef.current) return;

    const ctx = gsap.context(() => {
      const getDistance = () =>
        Math.max(0, trackRef.current!.scrollWidth - wrapRef.current!.clientWidth);

      gsap.to(trackRef.current, {
        x: () => -getDistance(),
        ease: "none",
        scrollTrigger: {
          trigger: wrapRef.current,
          start: "top top",
          end: () => `+=${getDistance()}`,
          pin: true,
          scrub: 1,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });
    }, wrapRef);

    return () => ctx.revert();
  }, [shouldReduceMotion]);

  return (
    <section
      ref={wrapRef}
      role="region"
      aria-label="Horizontal content track"
      tabIndex={shouldReduceMotion ? 0 : undefined}
      className={`relative w-full ${shouldReduceMotion ? "overflow-x-auto scroll-smooth" : "overflow-hidden"}`}
    >
      <div
        ref={trackRef}
        className={`flex h-[100dvh] w-max items-center ${shouldReduceMotion ? "snap-x snap-mandatory" : ""}`}
      >
        {children}
      </div>
    </section>
  );
}
```

### M3. Lightweight Scroll-Reveal Stagger (Motion Primitives)
*Use When*: Staggered entry transitions without requiring GSAP ScrollTrigger runtime.

```tsx
"use client";
import React from "react";
import { motion, useReducedMotion } from "motion/react";

export function RevealStagger({ items }: { items: React.ReactNode[] }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={shouldReduceMotion ? false : "hidden"}
      whileInView={shouldReduceMotion ? undefined : "visible"}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ staggerChildren: 0.08 }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {items.map((item, idx) => (
        <motion.div
          key={idx}
          variants={{
            hidden: { opacity: 0, y: 16 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } },
          }}
        >
          {item}
        </motion.div>
      ))}
    </motion.div>
  );
}
```
