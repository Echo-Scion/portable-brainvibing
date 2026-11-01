# 🏛️ Canonical Component Taxonomy & Design System Primitives

> **Taxonomic Reference**: Structured in alignment with [The Component Gallery](https://component.gallery/) (curated by Iain Bean), indexing ~60 canonical component primitives across 95+ production design systems.
> **Operational Purpose**: Eliminates AI UI slop by providing a standardized, polyglot primitive vocabulary with strict anatomical and accessibility contracts across Web, Flutter, and Android Jetpack Compose.

---

## 1. Taxonomic Framework & Component Anatomy

Every production UI component consists of standard anatomical parts rather than arbitrary nested `<div>` wrappers. When authoring or assembling components, engineers and agents MUST respect canonical anatomy:

- **Root (`<Component.Root>`)**: The outermost container enforcing component bounds, context, and focus management.
- **Trigger (`<Component.Trigger>`)**: The interactive element dispatching the open/toggle/select action.
- **Content (`<Component.Content>`)**: The encapsulated surface containing the component's primary payload.
- **Overlay (`<Component.Overlay>`)**: The backdrop obscuring background content during modal interactions.
- **Portal (`<Component.Portal>`)**: A teleported DOM/layer node rendering over the application tree to avoid z-index clipping.
- **Item / Option (`<Component.Item>`)**: A discrete selectable or actionable row within lists, menus, or grids.
- **Indicator (`<Component.Indicator>`)**: A visible state glyph (check mark, radio dot, sort caret, loading spinner).

---

## 2. The 6 Functional Domains & ~60 Canonical Primitives

```
CANONICAL COMPONENT TAXONOMY (~60 Primitives)
├── 01. Actions & Triggers (5 Primitives)
├── 02. Navigation & Wayfinding (8 Primitives)
├── 03. Forms & Inputs (11 Primitives)
├── 04. Data Display (9 Primitives)
├── 05. Feedback & Overlays (9 Primitives)
└── 06. Layout Primitives (6 Primitives)
```

---

### Domain 01: Actions & Triggers

| Component | Anatomy & Purpose | Accessibility & ARIA Contract | Web / Radix | Flutter (M3) | Android Compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Button** | Root + Label + Leading/Trailing Icon. Initiates immediate action. | `role="button"`, `tabindex="0"`, `aria-disabled="true"`, Space/Enter triggers. | `<button>`, Radix Slot | `FilledButton`, `OutlinedButton`, `TextButton` | `Button`, `OutlinedButton`, `TextButton` |
| **Button Group** | Container grouping adjacent related buttons. | `role="group"`, `aria-label="Action group"`. | Flex row + negative margin borders | `SegmentedButton` | `SingleChoiceSegmentedButtonRow` |
| **Split Button** | Primary action button paired with a dropdown disclosure button. | Primary: `role="button"`. Secondary: `aria-haspopup="menu"`, `aria-expanded`. | Dual button cluster + Radix DropdownMenu | Custom Row (`FilledButton` + `PopupMenuButton`) | Custom Row (`Button` + `IconButton` with `DropdownMenu`) |
| **Dropdown Menu** | Trigger + Content + Item list. Reveals list of actions. | `role="menu"`, `role="menuitem"`, arrow key focus loop, escape key dismiss. | `@radix-ui/react-dropdown-menu` | `PopupMenuButton<T>` | `DropdownMenu`, `DropdownMenuItem` |
| **Action List** | Vertical list of actionable rows with icons and metadata. | `role="menu"` or `role="list"`, `aria-orientation="vertical"`. | `ul.action-list` > `li > button` | `ListView` with `ListTile` | `Column` with `ListItem` / clickable rows |

---

### Domain 02: Navigation & Wayfinding

| Component | Anatomy & Purpose | Accessibility & ARIA Contract | Web / Radix | Flutter (M3) | Android Compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Breadcrumbs** | Ordered hierarchy trail linking parent pages. | `<nav aria-label="Breadcrumb">` + `<ol>`, `aria-current="page"` on leaf. | `nav > ol > li > a` | `Wrap` of breadcrumb chips | `Row` with `Text` links and separators |
| **Header / App Bar** | Top horizontal landmark holding brand, nav, and user actions. | `<header role="banner">`, semantic top-level landmark. | `header.app-bar` | `AppBar`, `SliverAppBar` | `TopAppBar`, `MediumTopAppBar` |
| **Side Navigation / Drawer** | Vertical persistent or dismissible navigation landmark. | `<nav role="navigation">`, `<aside aria-label="Main Navigation">`. | `nav.sidebar` | `NavigationDrawer` | `ModalNavigationDrawer`, `PermanentNavigationDrawer` |
| **Stepper** | Numbered progressive sequence of milestone phases. | `<ol aria-label="Progress">`, `aria-current="step"`, `aria-disabled`. | `ol.stepper` > `li` | `Stepper` | Custom Stepper with `Step` rows |
| **Tabs** | Root + List + Trigger + Content. Switches alternate panels in-place. | `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, arrow key navigation. | `@radix-ui/react-tabs` | `TabBar` + `TabBarView` | `PrimaryTabRow`, `Tab` |
| **Tree View** | Hierarchical expandable tree of nodes. | `role="tree"`, `role="treeitem"`, `aria-expanded`, arrow key navigation. | Custom recursive or Headless Tree | Custom recursive `ExpansionTile` | Custom recursive `Tree` / LazyColumn |
| **Pagination** | Root + Previous + Page Numbers + Next. Navigates page chunks. | `<nav aria-label="Pagination">`, `aria-current="page"`, `aria-disabled="true"`. | `nav > ul > li > a` | Custom row with page buttons | `Pagination` row with item buttons |
| **Skip Link** | First focusable link jumping directly to main content landmark. | `class="sr-only focus:not-sr-only"`, `href="#main-content"`. | `<a href="#main-content">` | `Semantics(label: "Skip to content")` | Accessible action targeting main content focus |

---

### Domain 03: Forms & User Inputs

| Component | Anatomy & Purpose | Accessibility & ARIA Contract | Web / Radix | Flutter (M3) | Android Compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Text Input** | Label + Input + Hint/Error + Clear Button. Captures single-line string. | `<label for="id">`, `aria-invalid="true"`, `aria-describedby="hint-id"`. | `<input type="text">` | `TextField`, `TextFormField` | `TextField`, `OutlinedTextField` |
| **Textarea** | Label + Multiline Input + Character Counter. Captures long prose. | `<label for="id">`, `aria-invalid`, `aria-describedby`. | `<textarea>` | `TextField(maxLines: null)` | `OutlinedTextField(minLines = 3)` |
| **Checkbox** | Root + Check Indicator + Label. Toggles binary opt-in state. | `role="checkbox"`, `aria-checked="true|false|mixed"`, Space toggles. | `@radix-ui/react-checkbox` | `CheckboxListTile` | `Checkbox`, `TriStateCheckbox` |
| **Radio Group** | Root + Radio Items + Labels. Mutually exclusive selection ($\le 4$). | `role="radiogroup"`, `role="radio"`, `aria-checked`, arrow key traversal. | `@radix-ui/react-radio-group` | `RadioGroup` / `RadioListTile` | `RadioButton` in selectable column |
| **Switch / Toggle** | Root + Thumb. Immediate system state toggle (no submit needed). | `role="switch"`, `aria-checked="true|false"`, Space toggles. | `@radix-ui/react-switch` | `SwitchListTile` | `Switch` |
| **Select** | Trigger + Content + Viewport + Item + Indicator. Single option from dropdown. | `role="combobox"`, `aria-expanded`, `aria-haspopup="listbox"`, `aria-controls`. | `@radix-ui/react-select` | `DropdownMenu`, `DropdownButtonFormField` | `ExposedDropdownMenuBox` |
| **Combobox / Autocomplete** | Input + Listbox Popover + Items. Searchable filtered selection. | `role="combobox"`, `aria-autocomplete="list"`, `aria-controls`, `aria-activedescendant`. | Headless Combobox (Radix/Command) | `Autocomplete<T>` | `AutoCompleteTextField` |
| **Range Slider** | Track + Range Fill + Thumb. Selects numeric value on continuous continuum. | `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, arrow adjustment. | `@radix-ui/react-slider` | `Slider`, `RangeSlider` | `Slider`, `RangeSlider` |
| **Date Picker** | Input trigger + Calendar Grid Popover. Selects date or range. | `role="dialog"`, grid: `role="grid"`, `aria-label="Calendar"`, arrow navigation. | Custom Popover + Date-Fns / Radix | `showDatePicker()`, `CalendarDatePicker` | `DatePickerDialog`, `DatePicker` |
| **File Upload** | Dropzone surface + File list + Progress + Remove action. | `<input type="file">`, dropzone: `role="region"`, `aria-label="Dropzone"`. | `<input type="file" class="sr-only">` | Custom Dropzone with `file_picker` | Custom file picker launcher |
| **Pin / OTP Input** | Row of single-character numeric input boxes with auto-advance. | Single hidden input or grouped inputs with `aria-label="Verification digit N"`. | Custom segmented numeric row | `Pinput` package or custom row | Grouped `OutlinedTextField` row |

---

### Domain 04: Data Display & Content Layout

| Component | Anatomy & Purpose | Accessibility & ARIA Contract | Web / Radix | Flutter (M3) | Android Compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Avatar** | Root + Image + Fallback Initials/Icon. Represents person or entity. | `<img alt="Person Name">` or `aria-label="Person Initials"`. | `@radix-ui/react-avatar` | `CircleAvatar` | Image with `CircleShape` clip |
| **Badge / Tag / Chip** | Pill container + Label + Optional Dismiss Icon. Status or metadata. | Non-interactive: `role="status"`. Interactive: `role="button"`, `tabindex="0"`. | `span.badge` | `Badge`, `Chip`, `FilterChip` | `Badge`, `AssistChip`, `FilterChip` |
| **Card** | Surface container grouping related content. | `<article>` or `<div>`, semantic heading inside. Never nested 3 deep. | `article.card` | `Card`, `ElevatedCard` | `Card`, `ElevatedCard` |
| **Data Table / Grid** | Header row + Data rows + Sticky columns + Cell formatters. | `<table>`, `<th>` with `scope="col"`, `aria-sort="ascending|descending"`. | `table.data-table` | `DataTable`, `PaginatedDataTable` | `LazyColumn` with structured row items |
| **Description List** | Pairs of terms (`<dt>`) and definitions (`<dd>`). Key-value metadata. | `<dl>`, `<dt>`, `<dd>`. Never substitute with ad-hoc bold divs. | `<dl class="description-list">` | Custom 2-column key-value list | Column of key-value `ListItem` rows |
| **Empty State** | Illustration / Icon + Headline + Explanatory Prose + Primary CTA. | `role="region"`, `aria-label="Zero state notice"`. | `div.empty-state` | Custom centered Column | Centered `Column` with icon + CTA |
| **Stat Callout (KPI)** | Oversized tabular metric + Label + Trend delta badge. | `<dl>` with `<dt>` label and `<dd>` metric, `font-variant-numeric: tabular-nums`. | `div.stat-callout` | Custom metric `Card` | `Card` with oversized `Text` |
| **Timeline** | Chronological series of event nodes connected by rail lines. | `<ol aria-label="Event history">` + `<li>` nodes. | `ol.timeline` | Custom `CustomPainter` or Column | Column with vertical divider rail |
| **Code Block** | Container + Language Tag + Copy Button + Preformatted code. | `<pre><code>`, copy button: `aria-label="Copy code to clipboard"`. | `pre > code` + Copy button | `HighlightView` or styled Container | `Surface` with `Text` in FontFamily.Monospace |

---

### Domain 05: Feedback, Overlays & Notifications

| Component | Anatomy & Purpose | Accessibility & ARIA Contract | Web / Radix | Flutter (M3) | Android Compose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Modal Dialog** | Root + Portal + Overlay + Content + Title + Close Button. Disruptive task. | `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus trap, escape key dismiss. | `@radix-ui/react-dialog` | `showDialog()` with `AlertDialog` | `Dialog`, `BasicAlertDialog` |
| **Alert Dialog** | Modal confirming destructive or irreversible actions. | `role="alertdialog"`, `aria-modal="true"`, focus locked on cancel button by default. | `@radix-ui/react-alert-dialog` | `AlertDialog` with red action | `AlertDialog` |
| **Sheet / Drawer** | Side-panel overlay sliding from viewport edge. Secondary sub-tasks. | `role="dialog"`, `aria-modal="true"`, focus trap, maintains page context. | `@radix-ui/react-dialog` (side slide) | `showModalBottomSheet()` | `ModalBottomSheet` |
| **Popover** | Trigger + Content + Anchor. Contextual floating menu/details. | `role="dialog"` or `role="region"`, anchored to trigger bounding rect. | `@radix-ui/react-popover` | Custom `OverlayEntry` | `Popup` |
| **Tooltip** | Trigger + Bubble Content. Fleeting explanatory description on hover/focus. | `role="tooltip"`, `id` linked via `aria-describedby` on trigger. | `@radix-ui/react-tooltip` | `Tooltip` | `TooltipBox` |
| **Banner / Callout** | Container + Status Icon + Title + Body copy. Persistent section notice. | `role="status"` or `role="alert"`. | `aside.banner` | `MaterialBanner` | `Surface` with semantic status border |
| **Toast / Snackbar** | Fleeting non-modal notification banner anchored to screen edge. | `role="status"`, `aria-live="polite"` (or `assertive` for critical errors). | `@radix-ui/react-toast` | `ScaffoldMessenger.showSnackBar()` | `SnackbarHost`, `Snackbar` |
| **Progress Bar** | Track + Fill indicator. Quantifies operation progress. | `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`. | `@radix-ui/react-progress` | `LinearProgressIndicator` | `LinearProgressIndicator` |
| **Skeleton Shimmer** | Placeholder shape pulsating with subtle gradient wash during fetch. | `aria-hidden="true"`, parent container marked with `aria-busy="true"`. | `div.skeleton` | Shimmer package / custom shader | Animated brush gradient box |

---

### Domain 06: Layout Primitives

| Component | Purpose & CSS Mapping | Flutter Equivalent | Android Compose Equivalent |
| :--- | :--- | :--- | :--- |
| **Box** | Polymorphic base element for padding, border, and background tokens. | `Container` | `Box` |
| **Stack (VStack / HStack)** | 1-dimensional flex layout managing directional gaps and alignment. | `Column`, `Row` | `Column`, `Row` |
| **Grid** | 2-dimensional grid layout managing column templates and responsive spans. | `GridView`, `Wrap` | `LazyVerticalGrid` |
| **Splitter / Resizable** | Resizable multi-pane container separated by interactive draggable handle. | Custom draggable split view | Two panes with draggable divider |
| **Divider / Separator** | 1px horizontal or vertical hairline dividing unrelated sections. | `Divider`, `VerticalDivider` | `HorizontalDivider`, `VerticalDivider` |
| **Aspect Ratio** | Container locking width-to-height ratio (16:9, 4:3, 1:1) against layout shifts. | `AspectRatio` | `Modifier.aspectRatio()` |

---

## 3. Enforcement & Verification Protocol

When scaffolding or modifying any frontend screen:
1. **Declare Primitives**: Identify every intended UI component by its canonical name from this taxonomy in the implementation plan.
2. **Refuse Ad-Hoc Wrappers**: Banish generic unlabelled `<div>` clickables or pseudo-dialogs.
3. **Audit Against 8 States**: Verify all interactive primitives satisfy the 8-state contract codified in `SKILL.md`.
