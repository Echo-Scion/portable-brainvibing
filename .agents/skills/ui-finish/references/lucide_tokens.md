# 🔣 Iconography & Lucide Token Contracts

> **Origin**: Sovereign Cross-Platform Iconography Standard.
> **Purpose**: Standardized vector iconography token mapping across Flutter, Jetpack Compose, and React frontends.

---

## 1. Icon Geometry & Stroke Metrics

- **Base Bounding Box**: `24px x 24px` (viewBox: `0 0 24 24`).
- **Stroke Width**:
  - Dense Desktop / Tables: `1.5px`
  - Standard Mobile & Web: `2.0px`
  - Emphasized / Hero Badges: `2.5px`
- **Line Join & Cap**: `stroke-linecap="round" stroke-linejoin="round"`.
- **Fill Protocol**: `fill="none"` by default. Icons are stroke-based line drawings.

---

## 2. Standard Semantic Token Mapping

| Intent / Action | Lucide Token | Flutter Equivalent | Jetpack Compose Equivalent |
| :--- | :--- | :--- | :--- |
| **Search / Query** | `search` | `LucideIcons.search` | `Icons.Outlined.Search` |
| **Filter / Refine** | `filter` | `LucideIcons.filter` | `Icons.Outlined.FilterList` |
| **Settings / Config** | `settings` | `LucideIcons.settings` | `Icons.Outlined.Settings` |
| **Alert / Warning** | `alert-triangle` | `LucideIcons.alertTriangle` | `Icons.Outlined.Warning` |
| **Success / Verified** | `check-circle-2` | `LucideIcons.checkCircle2` | `Icons.Outlined.CheckCircle` |
| **Error / Failed** | `x-circle` | `LucideIcons.xCircle` | `Icons.Outlined.ErrorOutline` |
| **Delete / Destroy** | `trash-2` | `LucideIcons.trash2` | `Icons.Outlined.Delete` |
| **Copy to Clipboard** | `copy` | `LucideIcons.copy` | `Icons.Outlined.ContentCopy` |
| **External Link** | `external-link` | `LucideIcons.externalLink` | `Icons.Outlined.OpenInNew` |
| **Terminal / CLI** | `terminal` | `LucideIcons.terminal` | `Icons.Outlined.Terminal` |

---

## 3. Aesthetic Restraint Invariants

- **Never Use Icons Decoratively without Meaning**: Every icon must either perform an interactive action or convey an unambiguous status change.
- **Never Mix Filled and Outlined Icon Sets**: Maintain a uniform 100% outlined stroke style across the entire application interface.
- **Strict Sizing Scale**:
  - `size-3` (`12px`): Dense inline status dots.
  - `size-4` (`16px`): Standard inline buttons, table row actions, input prefixes.
  - `size-5` (`20px`): Navigation bar items, card header icons.
  - `size-8` (`32px`): Empty state illustrations, modal header alerts.
