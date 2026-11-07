# Style & Ergonomics Guide: {{project_name}}

<!-- START FOUNDATION:style-palette -->
## 🎨 Visual Identity & Terminal Palette
- **Primary Palette**: {{primary_palette}}
- **Typography / Monospace**: {{typography_stack}}
- **Core Aesthetics**: {{visual_aesthetic_keywords}}
<!-- END FOUNDATION:style-palette -->

<!-- START FOUNDATION:style-principles -->
## 🧩 Interface Principles (UI & CLI)
- **Layout / Command Philosophy**: {{layout_approach}}
- **Component / Standard Stream**: {{ui_kit_reference}}
<!-- END FOUNDATION:style-principles -->

<!-- START FOUNDATION:style-personas -->
## 👤 User & Consumer Personas
- **Primary Target**: {{primary_persona}}
- **Navigation & Access Patterns**: {{nav_patterns}}
<!-- END FOUNDATION:style-personas -->

<!-- START FOUNDATION:style-tone -->
## 📝 Tone, UX Writing & Localization Contract (`Balise UX Writing`)
- **Communication Style**: {{brand_voice}}
- **Stake-Adapted Tone Matrix**:
  - *Onboarding, Success, First-Time Empty*: Warm, encouraging, orienting.
  - *Routine Actions, Settings, Navigation*: Neutral, minimal, scannable.
  - *Validation Errors & Destructive Confirmations*: Calm, plain, instructional, zero playfulness (never `"Oops!"` or exclamation marks).
  - *Data Loss, Billing, Security & Consent*: Serious, explicit about scope and reversibility.
- **Action & Control Copy Rules**:
  - **Verb-First Buttons**: Start every button with a specific verb (`"Create project"`, `"Save draft"`, never `"OK"` or `"Let's go"`).
  - **Destructive Consequence Confirmation**: Confirmation dialogs must repeat the exact consequence (`"Delete project"` / `"Cancel"`, never bare `"Yes"` / `"No"`).
  - **Self-Describing Links**: Write `"Read the billing docs"`, never `"Click here"` or bare `"Learn more"`.
  - **One Capitalization Policy**: Enforce **Sentence case** across all headings, buttons, and labels for localization safety and reading calm.
  - **State Truthfulness**: Distinguish *Saved*, *Sent*, *Queued*, *Processed*, and *Published*; never imply completion before backend confirmation.
  - **Localization & i18n Safety**: Never concatenate sentence fragments around variables (`"You have " + n + " items"`); use complete plural-aware templates and logical CSS properties (`padding-inline-start`).
<!-- END FOUNDATION:style-tone -->

<!-- START FOUNDATION:style-responsive-priority -->
## 📱 Responsive Priority & Desktop-to-Mobile Transformation Contract
Adapt by task priority rather than mechanically shrinking desktop layouts:
1. **Typography & Rhythm Scaling**: Scale display headings down 30–40% on mobile (`64px -> 36px`, `48px -> 30px`) while keeping body copy at `16px` (`>= 15px` floor) and form inputs at `16px` (`text-base sm:text-sm`) to prevent iOS auto-zoom. Reduce vertical section padding by 40–50% while preserving relative hierarchy.
2. **Navigation Adaptation**: Convert horizontal desktop bars into either a `56px` Bottom Tab Bar (for apps with 3–5 primary destinations) or a `64px` Top Bar + Full-Screen/Sheet Mobile Menu (`56px` row height).
3. **Data Table & Pricing Reflow**:
   - *Tables $\le 6$ simple columns*: Transform rows into stacked key-value cards on mobile.
   - *Dense numeric tables $> 6$ columns*: Horizontal scroll container with the first identifier column pinned.
   - *Pricing grids*: Stack vertically with the recommended plan placed **first** (not buried in the middle).
4. **Touch Ergonomics**: Enforce $\ge 44\times 44\text{px}$ hit targets with $\ge 8\text{px}$ gap between adjacent targets; convert sticky desktop sidebar CTAs into a sticky bottom bar above the mobile safe area.
<!-- END FOUNDATION:style-responsive-priority -->
