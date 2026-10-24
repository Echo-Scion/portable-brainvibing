---
name: project-migrate
description: Onboarding workflow for legacy or brownfield projects (90% done) into the Portable Brainvibing architecture.
---

# PROJECT MIGRATE & BROWNFIELD ONBOARDING

## Workflow: Project Migrate (`/project-migrate`)

Follow these steps when installing the Portable Brainvibing foundation (`.agents` directory) into an **existing, mostly complete (Brownfield)** codebase or when onboarding reverse-engineered application assets.

> **EPISTEMIC AUTO-CONTEXT PROTOCOL**: Raw source code and reverse-engineered packages (APK, IPA, Web, SQLite, HAR) contain high-fidelity structural facts (AST, database schemas, API routes, permissions, design tokens), but DO NOT contain business strategy or legal terms. Do NOT generate 82 empty or unanchored files. Follow the **3-Tier Epistemic Protocol**:
> 1. `[AST_VERIFIED]`: 100% deterministic facts (schemas, APIs, permissions, colors). Write directly with `needs_human_review: false`.
> 2. `[SDK_INFERRED]`: High-probability functional signals (Stripe/Billing, AdMob, Auth, Analytics). Write with `needs_human_review: true`.
> 3. `[HYPOTHESIS_DRAFT]`: Probabilistic strategy/personas. Bound with warning banners; mandatory human review.
> All auto-extracted content MUST be wrapped inside `<!-- [ORION:AUTO-INFERRED:START] -->` anchors to preserve manual developer edits across re-scans.

## Phase 0: State Initialization (MANDATORY)
- **Action**: Create or overwrite `.orion/task.md` with the checklist of this workflow.
- **Rule**: At the start of every phase below, mark its checkbox as `[/]` (in-progress) in `.orion/task.md`. At the end of every phase, mark it `[x]` (done).

## Phase 0.5: Reverse Engineering Staging (If Applicable)
If onboarding an external binary, decompile target, or foreign repository:
- **Staging Directory**: Place raw inputs in `.scratch/reverse/<target_name>/raw/` (e.g., decompiled manifests, layouts, strings, SQLite, HAR). Never pollute `<src_root>` (e.g. `src/` or `lib/`) or git tracking with raw decompiled dumps.
- **IR Extraction**: Run scanner/ast tools (`python .agents/scripts/orion.py scan map <target_dir>`) to emit structured intermediate AST representations into `.scratch/reverse/<target_name>/ir/`.
- **Phased Porting to 5-Tier Canonical Architecture** (Adapt `<src_root>`: `lib/` for Flutter, `src/` for React/Node/Rust, `app/` for Python, `internal/` for Go):
  1. `<src_root>/contracts/` & `<src_root>/core/{l10n,i18n,locales}/`: Data contracts, DTO interfaces, localization strings, schema definitions.
  2. `<src_root>/domain/`: Pure business models, entities, value objects, and repository interfaces.
  3. `<src_root>/services/`: HTTP/gRPC clients, database drivers, auth adapters, and external integrations.
  4. `<src_root>/state/`: State management (Riverpod/Bloc for Flutter, Zustand/Redux for React, signals/notifiers).
  5. `<src_root>/presentation/`: Screens/views, UI components/widgets, router, and design system tokens.

## Phase 0.6: Clean-Room Workspace & Build Hygiene Gate (MANDATORY for Hybrid/Migrated Apps)
When porting native applications (Android/iOS) to Flutter or modern frameworks:
1. **Prune Native UI & Navigation Bloat**:
   - Strip build dependencies superseded by the cross-platform UI. In Android Gradle (`build.gradle.kts` / `settings.gradle.kts`), immediately remove plugins and dependencies for Jetpack Navigation (`androidx.navigation.safeargs`, `navigation-fragment-ktx`, `navigation-ui-ktx`), `viewBinding = true`, `constraintlayout`, and unused legacy JSON libraries (`gson`).
2. **Purge Orphan Resource Styles & XML**:
   - Inspect `res/values/styles.xml` and `res/values/colors.xml`. Delete styles and themes associated with unported native features (e.g., third-party OEM battery helpers, vendor activity themes) to prevent dead weight and audit drift.
3. **Prevent Split-Brain Workspace Identity**:
   - Immediately align root project identity markers (`README.md`, `package.json`, root scripts, build configs) with `context/00_Strategy/BLUEPRINT.md`. Never allow previous prototype documentation or stale naming to contradict the active architecture blueprint.
4. **Enforce Cross-Boundary Persistence Parity**:
   - Ensure the native background daemon and Flutter settings repository share identical preference filenames (`"FlutterSharedPreferences"`), storage keys, and JSON serialization formats.

## Phase 1: Architectural Extraction
Extract a lightweight skeleton of the existing codebase to provide cheap token context.
- **Command**: Run `python .agents/scripts/orion.py scan map`
- **Output**: Generates an architectural skeleton without incurring massive token costs for full-file reads.

## Phase 1.5: Project DNA Epigenetic Mutation Protocol (`orion.py dna mutate`)
When deploying `.agents` mid-flight into an existing repository or reverse-engineered codebase, you do NOT need to forcefully rewrite all directory structures immediately. The engine uses **Epigenetic Mutation**:

1. **Step 1: Epigenetic Mutation (Zero-Disruption / Recommended)**:
   - **Command**: `python .agents/scripts/orion.py dna mutate --mode epigenetic`
   - Maps pre-existing folders (e.g. `src/models` or `lib/models` -> `1_contracts`, `src/api` or `lib/network` -> `3_services`, `src/store` or `lib/controllers` -> `4_state`, `src/views` or `lib/ui` -> `5_presentation`) inside `.agents/.dna.json` as `epigenetic_aliases`.
   - Leaves physical files completely untouched while granting context packager, packer.py, and AI agents immediate 5-tier understanding.

2. **Step 2: Mutation Plan Inspection**:
   - **Command**: `python .agents/scripts/orion.py dna mutate --mode plan`
   - Generates a dry-run surgical relocation plan showing how non-canonical folders can physically assimilate into standard 5-Tier layout without moving files.

3. **Step 3: Physical Scaffold Mutation (Optional / Controlled)**:
   - **Command**: `python .agents/scripts/orion.py dna mutate --mode scaffold`
   - Safely creates empty canonical 5-tier directory scaffolds (`contracts/`, `domain/`, `services/`, `state/`, `presentation/`) without deleting or overwriting any existing code.

4. **Verification**:
   - **Command**: `python .agents/scripts/orion.py dna audit`
   - Computes DNA compliance score (0-100%) and reports any forbidden cross-layer dependency violations.

## Phase 2: Scaffold Master Context & Signal-Driven Materialization
Generate the foundational knowledge structure using the 82-file registry, practicing **Selective Signal-Driven Materialization**:
- **Rule**: Scaffold ONLY the 4 Master files upfront:
  - `context/00_Strategy/BLUEPRINT.md`
  - `context/01_Product/ROADMAP.md`
  - `context/02_Creative/STYLE_GUIDE.md`
  - `context/03_Tech/ARCHITECTURE.md`
- **Command**: Run `python .agents/scripts/orion.py brain sync "init SaaS structure"`.
- **Action**: Materialize child detail files (e.g., `Dev_Database.md`, `Dev_APIs.md`, `Infra_Security.md`, `Design_Design_System.md`) ONLY when concrete code/asset signals exist. Unmaterialized slots remain documented in master indices without creating 82 empty files.

## Phase 3: Epistemic Context Extraction & Bounded Merging
- **Action 1: Technical & Security Extraction (`[AST_VERIFIED]`)**:
  - Extract database schemas (SQLite, Drift, Prisma) into `context/03_Tech/Dev_Database.md`.
  - Extract API endpoints and payload schemas into `context/03_Tech/Dev_APIs.md`.
  - Extract permissions, network configs, and capabilities into `context/03_Tech/Infra_Security.md`.
  - Wrap sections with `<!-- [ORION:AUTO-INFERRED:START source="..." confidence="AST_VERIFIED"] -->`.
- **Action 2: Creative & Design Tokens (`[AST_VERIFIED]`)**:
  - Extract palette, typography, and component styling into `context/02_Creative/Design_Design_System.md`.
  - Extract screen transition flows into `context/02_Creative/Design_UX_Flows.md`.
- **Action 3: Product & Monetization Signals (`[SDK_INFERRED]`)**:
  - Identify payment/billing SDKs (Stripe, Google Play Billing) -> `context/01_Product/Conv_Pricing_Strategy.md`.
  - Identify analytics/telemetry SDKs (PostHog, Mixpanel, Firebase) -> `context/01_Product/Data_User_Tracking.md`.
  - Set `epistemic_status: SDK_INFERRED` and `needs_human_review: true`.
- **Action 4: Strategic Hypotheses (`[HYPOTHESIS_DRAFT]`)**:
  - Synthesize problem statement and target audience from README and manifest metadata.
  - Set `epistemic_status: HYPOTHESIS_DRAFT` and insert disclaimer banner.

## Phase 4: Legacy Documentation Merge
- **Action**: Move or integrate any pre-existing documentation (e.g., `README.md`, legacy specs) into the newly created `context/` structure.
- **Rule**: Use the `<!-- LEGACY MERGE START -->` format inside the respective `context/` files when appending legacy text. Do not summarize or alter the legacy text.

## Phase 5: Semantic Indexing & Epistemic Ingest
Unify code skeletons, epistemic context, and architecture in the Brain Graph.
- **Command**: `python .agents/scripts/orion.py orion_ops init`
- **Action**: Scaffolds `.orion/` + scans all layers into `_manifest.json`.
- **Command (Epistemic Ingest)**: `python .agents/scripts/orion.py brain ingest context/`
- **Verification**: Verify that `[HYPOTHESIS_DRAFT]` entries are tagged with `confidence = "hypothesis"` in `orion.db`, preventing unverified assumptions from contaminating autonomous code generation.
