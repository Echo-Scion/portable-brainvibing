# 60 FPS Motion Performance & Compositor Contracts

> **Mandate**: Animations must run on the GPU compositor thread at steady 60 FPS without layout thrashing, main-thread blocking, or excessive layer memory promotion.

---

## 1. The Three Rendering Phases Glossary

| Phase | Affected Properties | Cost & Performance Profile |
| :--- | :--- | :--- |
| **Composite** | `transform` (`translate`, `scale`, `rotate`), `opacity` | **Optimal (60 FPS GPU)**: Handled directly by GPU compositor thread without triggering layout or repaint. |
| **Paint** | `background-color`, `border-color`, `color`, `box-shadow`, `filter` | **Medium**: Repaints pixels into bitmap layers. Acceptable for isolated elements; avoid continuous loops on large surfaces. |
| **Layout** | `width`, `height`, `top`, `left`, `bottom`, `right`, `margin`, `padding`, `gap`, `flex`, `grid` | **Severe Hazard (Reflow)**: Recalculates page geometry, thrashing the entire DOM tree and causing dropped frames (jank). |

---

## 2. Critical "Never" Patterns (Zero-Jank Rules)

1. **Never Animate Layout Properties Continuously**:
   - FORBIDDEN: `transition: width 300ms`, `transition: height 300ms`, `transition: all 200ms`, `top: 10px -> 50px`.
   - MANDATORY: Use `transform: translateY(...)` or `transform: scale(...)`. For height expansion (accordions/dropdowns), use grid rows (`grid-template-rows: 0fr -> 1fr`) or CSS transform scale.
2. **Never Interleave DOM Reads and Writes (Layout Thrashing)**:
   - Reading geometry properties (`offsetHeight`, `clientHeight`, `getBoundingClientRect()`, `scrollTop`) immediately forces a synchronous layout calculation if a preceding write occurred.
   - MANDATORY: Batch all layout reads first, compute transforms, then batch all DOM writes in a single `requestAnimationFrame` callback.
3. **Never Drive Animations via Scroll Polling**:
   - FORBIDDEN: `window.addEventListener('scroll', () => { el.style.transform = ... })` without throttling or off-thread binding.
   - MANDATORY: Use CSS Scroll Timelines (`animation-timeline: scroll()`) or View Timelines (`animation-timeline: view()`). Fallback to `IntersectionObserver` to toggle CSS classes or pause off-screen animations.
4. **Never Run Unbounded `requestAnimationFrame` Loops**:
   - Loops must have an explicit stop condition when reaching terminal state or when element exits viewport.
5. **Never Use Unbounded `will-change: all`**:
   - FORBIDDEN: Blanket `will-change: transform` on static CSS classes across hundreds of cards. This causes GPU memory exhaustion (layer explosion).
   - MANDATORY: Apply `will-change: transform, opacity` surgically during `:hover` or just prior to active animation initiation, and remove it upon transition end.

---

## 3. High-Craft Motion Architectural Patterns

### A. The FLIP Technique (First, Last, Invert, Play)
When an element must transition between two layout positions:
1. **First**: Record initial bounding box (`el.getBoundingClientRect()`).
2. **Last**: Apply the new layout/state class and record final bounding box.
3. **Invert**: Invert delta via GPU transform: `deltaX = first.left - last.left`, `deltaY = first.top - last.top`, `deltaW = first.width / last.width`. Apply `transform: translate(deltaX, deltaY) scale(deltaW)`.
4. **Play**: Clear the transform with a transition to smoothly animate from inverted state to final natural state on the compositor thread.

### B. View & Scroll Timeline Declarations
For scroll-linked reveals, avoid JavaScript scroll event handlers:
```css
@keyframes reveal-card {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.timeline-reveal {
  animation: reveal-card linear both;
  animation-timeline: view();
  animation-range: entry 10% cover 30%;
}
```

### C. Reduced-Motion Contract (Accessibility Compliance)
Every animated surface must provide a clean fallback for users with vestibular or motion sensitivities:
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 4. Interaction Timing Budget

- **Immediate Micro-interactions (Click / Press / Hover)**: `<= 150ms`, `cubic-bezier(0.16, 1, 0.3, 1)` or `ease-out`.
- **Surface Entrances (Modals / Drawers / Toasts)**: `180ms – 240ms`, `ease-out`.
- **Exits & Dismissals**: `120ms – 160ms` (exits must always be faster than entrances to feel responsive).
- **Zero-Bouncy Defaults**: No dramatic overshoot curves (`cubic-bezier(..., 1.5)`) on productivity UI surfaces. Reserve subtle spring dynamics strictly for tactile mobile toggles or game interfaces.
