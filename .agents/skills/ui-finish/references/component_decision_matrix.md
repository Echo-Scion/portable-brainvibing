# 🧭 Component Decision Matrix & Contextual Selection Trees

> **Operational Mandate**: Eliminates arbitrary component guessing by enforcing deterministic heuristic decision trees matching user intent and design system constraints.
> **Companions**: Pairs with [component_taxonomy.md](component_taxonomy.md) and [craft_floor.md](craft_floor.md).

---

## 1. Overlay & Interruption Triage

Engineers and agents MUST NOT default to generic modal dialogs for every interaction. Select the exact overlay primitive based on cognitive friction:

```
[ User triggers an overlay / sub-task ]
  │
  ├─► Is the action destructive or irreversible?
  │     └─► YES: Use **Alert Dialog** (Focus locked to Cancel by default; assertive ARIA role).
  │
  ├─► Does the task require user concentration and block background page interaction?
  │     ├─► Short, isolated task (<3 form fields, login, confirmation)?
  │     │     └─► YES: Use **Modal Dialog** (Centered, max-w-lg, escape key closes).
  │     │
  │     └─► Deep editing flow or rich preview while preserving background context?
  │           └─► YES: Use **Sheet / Side Drawer** (Right-side slide-over, full height, page context visible).
  │
  ├─► Is the user accessing contextual actions or filters next to a specific trigger?
  │     ├─► Selection list or action menu?
  │     │     └─► YES: Use **Dropdown Menu** (Anchored, keyboard arrow-traversal).
  │     │
  │     └─► Rich contextual card or preview flyout?
  │           └─► YES: Use **Popover** (Anchored, non-modal, auto-repositions).
  │
  ├─► Is this a temporary system feedback event triggered by a background operation?
  │     └─► YES: Use **Toast / Snackbar** (Edge-anchored, auto-dismissing, polite live region).
  │
  └─► Is this a persistent system notification or section warning?
        └─► YES: Use **Banner / Inline Callout** (In-flow surface, semantic status border, actionable retry).
```

---

## 2. Data Display & Layout Triage

Avoid generic card soup. Select the data display primitive that matches the data's structural dimensionality:

```
[ Presenting data to the user ]
  │
  ├─► Is the data homogeneous, tabular, and multi-record?
  │     └─► YES: Use **Data Table / Grid** (Sticky headers, sort carets, tabular-nums, pagination).
  │
  ├─► Is the data a set of object properties or key-value metadata?
  │     └─► YES: Use **Description List** (`<dl>`, `<dt>`, `<dd>` pairs; forbid nested card divs).
  │
  ├─► Is the data a single high-signal quantitative metric?
  │     └─► YES: Use **Stat Callout (KPI)** (Large tabular numeral + small uppercase label + trend badge).
  │
  ├─► Is the data an ordered sequence of historical or chronological events?
  │     └─► YES: Use **Timeline** (Vertical rail line + node milestones + timestamp stamps).
  │
  ├─► Is the dataset currently empty or query result returned 0 items?
  │     └─► YES: Use **Empty State** (MANDATORY: Semantic icon + explanatory heading + clear recovery CTA).
  │
  └─► Are these rich, heterogeneous entities with media and secondary actions?
        └─► YES: Use **Card Grid** (Must use Asymmetric Bento spans, never uniform 3-box clones).
```

---

## 3. Input & Form Control Triage

Eliminate form friction by choosing input primitives that expose appropriate affordances:

```
[ User must supply input or make a choice ]
  │
  ├─► Binary state (On / Off)?
  │     ├─► Takes immediate effect without form submission (e.g. Dark Mode, Auto-Save)?
  │     │     └─► YES: Use **Switch / Toggle**.
  │     │
  │     └─► Part of a batch form requiring explicit submit (e.g. Terms, Filter)?
  │           └─► YES: Use **Checkbox**.
  │
  ├─► Choosing exactly 1 option from a mutually exclusive set?
  │     ├─► 2 to 4 options?
  │     │     └─► YES: Use **Segmented Control** or **Radio Group** (Keep options visible).
  │     │
  │     ├─► 5 to 10 static options?
  │     │     └─► YES: Use **Select (Dropdown)**.
  │     │
  │     └─► > 10 options or searchable dynamic dataset?
  │           └─► YES: Use **Combobox / Autocomplete** (Text input + filtered listbox popover).
  │
  ├─► Continuous numeric adjustment within a known bounded range?
  │     └─► YES: Use **Range Slider** (Includes live value indicator + keyboard step support).
  │
  └─► Long-form unstructured narrative text?
        └─► YES: Use **Textarea** (With bounded resize and accessible character count).
```

---

## 4. Design System Archetype Component Pairing

Components take on different visual treatments and densities based on the active Design System Archetype:

| Design System Archetype | Dominant Component Patterns | Density & Token Rules |
| :--- | :--- | :--- |
| **Linear-Precision** | Command Palette (`Kbd`), Action Lists, Segmented Controls, Sheets, Tabular Status Badges. | `DENSITY: 7-8`. 6px radii, monochromatic borders (`zinc-800`), instant 150ms transitions. |
| **Carbon / Enterprise** | Data Grids with batch action bars, Description Lists, Structured Inline Banners, Tooltips. | `DENSITY: 9`. 0px to 4px radii, strict contrast, zero ambient shadows, tabular numbers. |
| **Polaris / Merchant Ops** | Full-width `Page` headers, `ResourceList`, `SaveBar`, Modal confirmation dialogs, contextual Badges. | `DENSITY: 5-6`. 8px radii, distinct semantic surface tints, explicit primary CTAs. |
| **Apple HIG / Fluid Tactile** | Grouped insets, Segmented Pickers, Sheets with drag handles, spring-action toggles. | `DENSITY: 4`. 12px to 16px radii, generous 44px tap targets, spring physics. |

---

## 5. Anti-Slop Component Selection Refusals

The following anti-patterns represent bad LLM heuristics and are strictly forbidden:

1. **The Modal Reflex**: NEVER spawn a centered modal dialog for secondary editing or browsing workflows that benefit from page context. Use a side `Sheet / Drawer`.
2. **The Card-Soup Trap**: NEVER use generic rounded cards with bold titles for tabular records or key-value settings. Use `Data Table` for records and `Description List` for settings.
3. **The Hidden Dropdown Trap**: NEVER hide $\le 4$ options inside a dropdown `<select>`. Use `Segmented Control` or `Radio Group` so the user sees all options at a glance.
4. **The Ghost Notification**: NEVER use fleeting auto-dismissing `Toast` messages for critical errors that block user workflows. Critical errors require an in-page `Banner` or blocking `Alert Dialog`.
5. **The Bare Icon**: NEVER emit an `IconButton` without either a visible label or an accessible `aria-label` and `Tooltip`.

---

## 6. 6 Systemic UX Redesign Patterns

When building or refactoring complex application views, replace legacy friction points with systemic interaction patterns:

| Pattern | Legacy Anti-Pattern | Systemic UX Solution |
| :--- | :--- | :--- |
| **1. Non-Modal Contextual Overlays** | Centered modal popups blocking main workspace/media while adjusting settings. | Transparent/translucent **Side Drawers / Overlay Panels** allowing live preview and active workspace manipulation. |
| **2. Direct Spatial / Timeline Manipulation** | Abstract millisecond (`ms`) or coordinate inputs forcing trial-and-error guessing. | Direct interactive visual scrubbing (e.g. draggable subtitle/cue blocks on an audio waveform or seek bar). |
| **3. De-Frankensteining (UI Unification)** | Multiple fragmented menus, disparate icon weights, or conflicting light/dark patches. | Single unified Design System contract, consolidated icon sets, and unified primary + context menus. |
| **4. Entity Unification** | Disconnected "Cloud Catalog" vs. "Local Library" items where editing metadata breaks origin links. | Unified data entity model where user edits metadata without severing parent links or breadcrumbs. |
| **5. Flattened Filters & User Agency** | Filters hidden inside multi-level dropdowns that auto-close on each select; forced algorithm feeds. | **Persistent horizontal chip bar**, user-curated feed collections, and visible feed tag customization/muting. |
| **6. Cozy Spatial De-cluttering & Hybrid Bar** | Crowded sidebars with noisy red badges competing for attention simultaneously. | Hover-to-expand compact rails, vertical tabs on wide screens, thumb-zone mobile hitboxes ($\ge 48\text{px}$), and a fast **`Cmd+K` Command Bar**. |

---

## 7. Anti-Dark-Pattern Ethics Gate

Interfaces must respect user autonomy and avoid deceptive patterns:
- **Zero Visual Interference**: Never hide "Cancel", "Downgrade", or "Unsubscribe" actions behind low-contrast washed-out text or misleading styles.
- **Zero Confirmshaming**: Never write manipulative emotional guilt-trip button copy (e.g., "No thanks, I hate saving money").
- **Zero Muscle-Memory Swapping**: Never flip button order (placing destructive confirmation where "Cancel" was on previous steps) to trap accidental clicks.

