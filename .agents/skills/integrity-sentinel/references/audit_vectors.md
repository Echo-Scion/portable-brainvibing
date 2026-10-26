# Unified Audit Vectors Matrix (The Core Diagnostic Vectors)

> "Every changed line must trace directly to user intent." — Section 1 (Core Guardrails)

This document consolidates the 9 primary static and semantic audit vectors into a single, cohesive evaluation matrix. When conducting quality assurance or deep code review, evaluate the target codebase against these vectors sequentially while enforcing the **Calibration & Anti-Moving-Goalposts Clauses**:
- **Materiality Threshold**: Flag findings ONLY when proven to cause runtime failures (`Exception`/`Crash`), data/state corruption, exploitable security vulnerabilities, or non-functional empty stubs. Do not flag minor stylistic variations.
- **Intentional Architecture Exemption**: Defensive fallbacks inside `except ImportError:` blocks and standalone hook scripts (`hooks/`) with local helpers (`_atomic_write_text`, `_log_telemetry`) are NOT DRY violations. Documented retrieval-only modes are NOT shallow shims.
- **Convergence Guarantee**: When all mechanical gates pass (`Exit Code 0`) and zero material bugs exist, conclude with zero findings rather than inventing microscopic nitpicks.

---

## Vector 1: Architecture & High-Level System Mapping
*Goal: Understand core boundaries, data flows, and risk zones before micro-auditing.*

### Inspection Rubric:
1. **Entry Points & Flows**: Map user interaction -> API/Controller -> Service -> Data Persistence.
2. **Outside Services**: Identify external dependencies (payment gateways, third-party APIs, auth providers).
3. **Boundary Coupling & 5-Tier Directed Dependency Laws**: Check if layers violate separation of concerns and single-direction dependency flow:
   - Tier 1 (`1_contracts` / Primitives) MUST NOT import upwards from higher tiers (`2_data`, `3_services`, `4_state`, `5_presentation`).
   - Tier 5 (`5_presentation` / UI) MUST NOT bypass Tier 4 (`4_state`) to invoke Tier 3 (`3_services`) or database models directly.
   - Core execution spine files MUST preserve strict layer isolation.
4. **Output Shape**: Produce a high-level summary of architecture, main pieces, and high-risk hotspots without overwhelming line numbers.

---

## Vector 2: Logic, Semantics & Mathematical Safety
*Goal: Uncover deep runtime flaws, numerical hazards, and state mutations that linters miss.*

### Inspection Rubric:
1. **Math & Precision**:
   - Denominators must be checked for zero before division.
   - Use `Decimal` or scaled integers for currency, financial values, or exact measurements (never raw floating point `double`/`float`).
   - Validate array and slice boundaries to prevent off-by-one errors.
2. **State & Concurrency**:
   - Forbid unsynchronized mutation of shared state across threads or async routines.
   - Guard against race conditions where execution order is assumed rather than guaranteed.
   - Ensure `try/catch` or recovery blocks do not leave state partially updated (orphaned state).
3. **Data Drift & Drift Resilience**:
   - Detect stale caching without automatic invalidation hooks.
   - Flag silent serialization drops where DTO parsers omit required fields or choke on unexpected nulls.

---

## Vector 3: Fail-Fast & Silent Failure Elimination
*Goal: Ensure failures are explicit and audible; eliminate swallowed exceptions and deceptive fallbacks.*

### Inspection Rubric:
1. **Swallowed Exceptions**:
   - Forbid empty catch blocks (`catch (e) {}` or `except: pass`) in core execution paths.
   - Forbid catching an error and converting it to a fake success response.
2. **Deceptive Fallbacks**:
   - If an environment variable or critical credential is missing (e.g., payment secret, DB URI), the application must crash immediately on startup rather than defaulting to mock or dummy data in production.
3. **Empty/Null Returns as Errors**:
   - Return explicit `Result<T, E>`, `Either`, or throw typed domain errors rather than returning `null` or `""` to signal catastrophic failure.
4. **Background Failures**:
   - Background jobs or async tasks must capture exceptions into structured telemetry rather than failing silently into the void.

---

## Vector 4: Duplication & Single Source of Truth (DRY)
*Goal: Eliminate fragmented constants, schema drift, and duplicated domain logic.*

### Inspection Rubric:
1. **Config & Environment**: Consolidate repeated `process.env` or configuration lookups into centralized typed configs.
2. **Design Tokens**: Enforce hex colors, spacing, and typography to reference the design system token registry.
3. **Business Constants**: Eliminate magic numbers and hardcoded price, limit, or threshold literals.
4. **Validation Logic**: Ensure validation schemas (email, tax ID, phone, password) reside in a single canonical validator.
5. **Defensive Isolation Exemption**: Fallback functions inside `except ImportError:` blocks and self-contained helpers in single-file hooks (`hooks/pre-agent-wake.py`) exist for process isolation and MUST NOT be flagged as DRY violations.

---

## Vector 5: Bloat, Dead Code & YAGNI Enforcement
*Goal: Purge speculative abstractions, single-use helpers, and abandoned rewrite remnants.*

### Inspection Rubric:
1. **Unused Code**: Identify functions, types, and imports that have zero references across the repository.
2. **Single-Use Helpers**: Inline helpers that were created under speculative "future reusability" but are only called from one location.
3. **Defensive Over-Validation**: Flag defensive checks validating data that was already strictly verified by the preceding contract layer.
4. **Middleman Code**: Eliminate functions or classes that merely forward arguments to another function without adding domain logic.
5. **Abandoned Feature Flags**: Flag permanent flags or conditionals left active from past rewrites.

---

## Vector 6: Idempotency & Retry Safety
*Goal: Ensure multiple execution triggers do not result in duplicate side-effects.*

### Inspection Rubric:
1. **External Webhooks**: Stripe, GitHub, messaging, or payment webhooks must implement idempotency keys or transaction logs.
2. **User Side-Effects**: Actions triggering emails, SMS, push notifications, or credit grants must be idempotent.
3. **Database Mutations**: Prefer upserts (`INSERT ... ON CONFLICT DO UPDATE`) over naive inserts for sync or retryable pipelines.
4. **UI Debounce/Disable**: Action buttons triggering financial or critical mutations must disable immediately upon click and require idempotency tokens.

---

## Vector 7: Performance, Algorithmic Complexity & Leaks
*Goal: Eradicate silent latency degradations, memory accumulation, and wasteful re-computations.*

### Inspection Rubric:
1. **Algorithmic Traps**:
   - Detect nested loops leading to $O(N^2)$ execution over dynamic inputs.
   - Replace linear searches (`list.contains`) with set/map lookups $O(1)$.
2. **Memory Hygiene**:
   - Guarantee all streams, sockets, listeners, and file handles have verified teardown hooks (`dispose()`, `close()`).
   - Check that event listeners or subscribers are not registered inside repeat render or build cycles.
3. **UI & Rendering Bottlenecks**:
   - Enforce localized state updates instead of full-screen widget tree rebuilds.
   - Enforce `const` constructors on static UI trees.
   - Avoid performing synchronous parsing or heavy transformations inside render/build loops.

---

## Vector 8: Spec-to-Code Parity & Anti-Cosplay Gate (LLM Scaffold Detection)
*Goal: Detect fake implementations, regex-as-AST cosplay, ungrounded spec claims, and shallow tests.*

### Inspection Rubric:
1. **Dependency Truth Check**:
   - Inspect project manifests (`package.json`, `pubspec.yaml`, `pyproject.toml`).
   - Verify every library or parser claimed in `ARCHITECTURE.md`, `BLUEPRINT.md`, or `README.md` is actually installed and actively imported in `src/`.
   - Never accept documentation claims or `epistemic_status: AST_VERIFIED` tags at face value without source code verification.
2. **Parser Authenticity Check**:
   - Inspect files named `*Parser*`, `*Converter*`, `*Analyzer*`, `*Reader*`, or `*Reconstructor*`.
   - Verify whether modules parse syntax using legitimate AST parsers, compiler interfaces, or robust state machines rather than brittle single-line regex `.match()` heuristics.
3. **Exhaustive IR / AST Switch Check**:
   - Compare union type contracts (e.g. `WidgetType` in `types.ts` or AST Node variants) against `switch (node.type)` in the code generator.
   - Every defined union variant MUST emit a real widget/code structure rather than falling through to dummy stubs (`SizedBox.shrink()`, empty comments, or unhandled no-ops).
4. **Pipeline End-to-End Trace**:
   - Trace extraction and decompilation outputs (e.g. `.ipa`, `.dex`, `jadx`, `arsc`, `sqlite`).
   - Verify that extracted assets and sources are consumed and transformed by subsequent pipeline steps rather than dropped into dead-end directories.
5. **Shallow Test Detection**:
   - Reject unit tests that assert code generator or transpiler outputs using only shallow substring checks (`assert.ok(code.includes(...))`) without syntax, AST, or target compiler validation.

---

## Vector 9: Cross-Boundary Persistence, IPC & System Permission Safety
*Goal: Prevent silent runtime failures, state desynchronization, and permission traps across native mobile daemons, shared preferences, and UI capability toggles.*

### Inspection Rubric:
1. **Shared Preferences Binding Parity**:
   - Check that native listeners (`OnSharedPreferenceChangeListener`) bind unconditionally to `"FlutterSharedPreferences"` (`Context.MODE_PRIVATE`) and do NOT conditionally fallback based on initial empty file state (`all.isEmpty()`).
2. **Collection Serialization Parity**:
   - For collections shared across Flutter and native daemons, confirm that Flutter uses explicit JSON strings (`jsonEncode(list)`) rather than `setStringList` (which introduces unparseable Base64 prefix headers in native readers).
3. **UI Permission & Capability Gates**:
   - Inspect all UI switches controlling system-level capabilities (`AccessibilityService`, `SYSTEM_ALERT_WINDOW`, `WRITE_SETTINGS`, `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`).
   - Confirm that the UI queries active service status via `MethodChannel` before toggling, prompts with educational rationale on failure, and validates state upon app resume.
4. **Overlay Lifecycle & Orientation Resilience**:
   - For floating overlays and system window managers, verify that `onConfigurationChanged` handles display metrics shifts without throwing floating coordinates off-screen.
   - Confirm that repeatable actions (volume/brightness) do NOT dismiss overlay menus prematurely.
5. **Clean-Room Dependency Hygiene**:
   - Check build manifests for residual native UI/navigation bloatware (`androidx.navigation`, `constraintlayout`, `viewBinding`, unreferenced styles) that was replaced by cross-platform views.
