# Accessibility Contracts & Inclusive Engineering Standards

> **Mandate**: Interfaces must be fully operable by keyboard, screen reader, and assistive technologies out of the box, fulfilling WCAG 2.1 AA criteria without superficial cosmetic overrides.

---

## 1. Accessible Names (Priority 1)

Every interactive control must have a machine-readable accessible name computed by the browser's accessibility tree:

1. **Icon-Only Buttons & Controls**:
   - FORBIDDEN: `<button><SearchIcon /></button>` with no text.
   - MANDATORY: Add `aria-label="Search documents"` or wrap an invisible text element `<span className="sr-only">Search documents</span>`.
2. **Decorative vs Informative Icons**:
   - Decorative icons accompanying visible text must be hidden from screen readers: `<FileIcon aria-hidden="true" /> <span>Files</span>`.
   - Standalone icons carrying state (e.g. status badge) must have a tooltip or screen-reader text: `<span className="sr-only">Warning: disk space low</span>`.
3. **Form Fields**:
   - Every `<input>`, `<select>`, and `<textarea>` must be linked to a `<label>` using matching `id` and `htmlFor` (or `for`):
     ```html
     <label htmlFor="user-email">Email Address</label>
     <input id="user-email" type="email" name="email" required />
     ```
   - If a visual label cannot be placed, provide an explicit `aria-label="Email Address"`.
4. **Meaningful Anchor Text**:
   - Never use "click here", "read more", or raw URLs as link text.
   - Good: `<a href="/pricing">View Enterprise Pricing tiers</a>`.

---

## 2. Keyboard Access & Focus Order (Priority 2)

1. **No Unreachable Controls**:
   - All interactive elements must be reachable in sequential reading order via `Tab` / `Shift+Tab`.
   - NEVER assign `tabindex` greater than 0 (`tabindex="1"` is forbidden because it breaks predictable DOM focus order). Use `tabindex="0"` to make a custom element focusable, or `tabindex="-1"` for programmatically focusable containers.
2. **Native Semantics Over Synthetic Role Hacks**:
   - Prefer native `<button>`, `<a>`, `<input>` elements.
   - If a non-interactive element (`div`, `span`) must handle interaction, it MUST implement:
     - `role="button"`
     - `tabindex="0"`
     - Keyboard event listeners for both `Enter` and `Space` (`key === 'Enter' || key === ' '`).
3. **High-Contrast Visible Focus Rings**:
   - NEVER set `outline: none` or `outline: 0` without providing a high-contrast replacement.
   - Use `:focus-visible` to target keyboard users without showing rings on mouse click:
     ```css
     :focus-visible {
       outline: 2px solid var(--focus-ring-color, #2563eb);
       outline-offset: 2px;
     }
     ```
4. **Dismissal via Escape Key**:
   - Any modal, drawer, popover, or dropdown overlay must close immediately when the user presses `Escape`.

---

## 3. Focus Trapping & Dialog Contracts (Priority 3)

When a modal dialog or drawer is opened:
1. **Focus Trap**: Keyboard focus must be trapped strictly within the active dialog. Pressing `Tab` on the last focusable element must cycle back to the first focusable element.
2. **Initial Focus**: Move focus deliberately to the first interactive field, primary action, or dialog container with `tabindex="-1"`.
3. **Focus Restoration**: When the dialog closes, focus MUST return automatically to the trigger element that opened it.
4. **Body Scroll Lock**: Lock window scroll while modal is active without causing layout shift (`overflow: hidden; padding-right: [scrollbar-width]`).

---

## 4. Form Validation & Dynamic State Announcements

1. **Inline Field Errors**:
   - Associate error messages directly with the erroneous input using `aria-describedby`:
     ```html
     <input
       id="username"
       type="text"
       aria-invalid="true"
       aria-describedby="username-error"
     />
     <p id="username-error" role="alert" className="text-sm text-red-600">
       Username must be at least 3 characters.
     </p>
     ```
2. **Live Announcements**:
   - Use `aria-live="polite"` for non-disruptive dynamic updates (e.g. search result count changes).
   - Use `role="alert"` / `aria-live="assertive"` sparingly, reserved only for critical errors requiring immediate operator attention.
3. **Async / Loading States**:
   - Active data-fetching regions must announce busy state via `aria-busy="true"`.
   - Buttons undergoing async action must maintain dimensions, set `disabled`, and announce status (e.g. `aria-label="Saving changes, please wait..."`).

---

## 5. Visual Contrast & Physical Ergonomics

1. **WCAG 2.1 AA Contrast Ratios**:
   - Normal text (`< 18pt` or `< 14pt bold`): Minimum `4.5:1`.
   - Large text (`>= 18pt` or `>= 14pt bold`): Minimum `3.0:1`.
   - Essential UI components and graphical objects: Minimum `3.0:1` against adjacent background.
2. **Touch Target Dimensions**:
   - Minimum target bounding box on touch interfaces: `44x44px` (iOS standard) or `48x48px` (Android standard).
   - Use padding on small icons to expand the hit area without distorting icon geometry.
