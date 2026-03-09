# 📐 Bento Grids & Asymmetric Macrostructures

Avoid the generic 3-card layout trap (`grid-cols-1 md:grid-cols-3`). High-taste interfaces employ asymmetric bento arrangements, visual pacing, and structural variety.

---

## 1. Bento Grid Principles

A bento grid organizes heterogeneous features into an interconnected typographic mosaic.

- **Rule 1: Exact Cell Count & Purpose**:
  - Every cell must serve a distinct purpose (Hero Showcase, Metric Counter, Interactive Widget, Workflow Graphic). Never pad empty cells with placeholder icons.
- **Rule 2: Visual Anchor (Hero Cell)**:
  - Exactly ONE cell must act as the primary visual anchor, taking $\ge 50\%$ width or spanning multiple rows (`col-span-1 md:col-span-2 row-span-2`).
- **Rule 3: Internal Asymmetry**:
  - Adjacent cells must vary in content density. A text-dense list cell should sit next to a visual or interactive canvas cell.
- **Rule 4: Outer Boundary Alignment**:
  - While internal cell sizes vary, the outer bounding perimeter of the bento grid must align cleanly to the page grid.

---

## 2. Canonical Bento Layout Blueprints

### Blueprint A: The 4-Cell Asymmetric Mosaic (Most Popular for SaaS)
```text
┌───────────────────────────┬─────────────┐
│                           │   Cell 2    │
│          Cell 1           │  (Compact   │
│       (Hero Showcase      │   Metric)   │
│         col-span-2        ├─────────────┤
│         row-span-2)       │   Cell 3    │
│                           │ (Key Feature│
├─────────────┬─────────────┤   Widget)   │
│   Cell 4    │   Cell 5    │             │
│ (Testimonial│(Integration └─────────────┤
│   Snippet)  │   Logos)                  │
└─────────────┴───────────────────────────┘
```

**Tailwind CSS Code:**
```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 p-4">
  <!-- Cell 1: Anchor (2 cols, 2 rows) -->
  <div class="md:col-span-2 md:row-span-2 rounded-2xl p-8 bg-zinc-900 border border-zinc-800 flex flex-col justify-between">
    <div class="space-y-2">
      <span class="text-xs font-mono uppercase tracking-wider text-accent">Core Engine</span>
      <h3 class="text-2xl font-bold text-white">Full-Spectrum Observability</h3>
      <p class="text-zinc-400 max-w-md">Real-time distributed telemetry with zero sampling overhead.</p>
    </div>
    <!-- Interactive or visual canvas slot -->
    <div class="mt-8 h-48 rounded-xl bg-zinc-950/60 border border-zinc-800/80 p-4">...</div>
  </div>

  <!-- Cell 2: Stat Callout -->
  <div class="rounded-2xl p-6 bg-zinc-900 border border-zinc-800 flex flex-col justify-between">
    <span class="text-xs font-mono text-zinc-500 uppercase">Latency Floor</span>
    <div class="text-4xl font-extrabold text-white font-mono my-2">< 12ms</div>
    <p class="text-xs text-zinc-400">P99 globally across 24 edge regions.</p>
  </div>

  <!-- Cell 3: Feature Trigger -->
  <div class="rounded-2xl p-6 bg-zinc-900 border border-zinc-800 flex flex-col justify-between">
    <span class="text-xs font-mono text-zinc-500 uppercase">Auto-Reversion</span>
    <p class="text-sm text-zinc-300 mt-2">Zero-touch rollback upon anomaly detection.</p>
  </div>
</div>
```

---

## 3. Responsive Fallback Strategy

Bento grids must reflow gracefully on smaller screens without breaking typography:

1. **Mobile (`< 768px`)**: Collapse into a single-column stacked feed (`grid-cols-1`). Reset all `col-span-2` and `row-span-2` to default `col-span-1`.
2. **Tablet (`768px - 1024px`)**: Use a 2-column balanced grid (`md:grid-cols-2`).
3. **Desktop (`> 1024px`)**: Expand into the full authored 3-column or 4-column asymmetric bento mosaic (`lg:grid-cols-3` or `lg:grid-cols-4`).

---

## 4. Anti-Slop Layout Checklist
- [ ] No two consecutive sections use identical grid structures.
- [ ] Hero section fits within standard viewport (`min-h-[90vh] md:min-h-[100dvh]`).
- [ ] Top padding on heroes capped at `pt-20` to `pt-24` (prevents endless empty space).
- [ ] Bento cells contain real semantic data, not generic decorative gradients.
- [ ] Grid gaps maintain proportional scale (`gap-4` to `gap-6`).
