# Unified Audit Vectors Matrix (The Core Diagnostic Vectors)

> "Every changed line must trace directly to user intent." — Section 1 (Core Guardrails)

This document consolidates the 12 primary static and semantic audit vectors into a single, cohesive evaluation matrix. When conducting quality assurance or deep code review, evaluate the target codebase against these vectors sequentially while enforcing the **Calibration & Anti-Moving-Goalposts Clauses**:
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
6. **Cross-File Pipeline Contract Exemption**: Functions, parameters, return structures, and exported constants that participate in cross-file pipelines, CLI dispatch (e.g., `CMD_MAP`), or plugin hooks MUST NOT be flagged as dead code or bloat based on single-file or single-bundle analysis. Parameter deletion requires verified 0 references across the entire repository graph.

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

---

## Vector 10: AI, LLM & Agentic Boundary Security
*Goal: Prevent prompt-role confusion, indirect prompt injection, confused deputy tool attacks, and context exfiltration in agentic applications.*
*Runbook Reference: [ai_llm_attacks.md](ai_llm_attacks.md)*

### Inspection Rubric:
1. **Prompt Injection & Delimiter Integrity (`ORION-LLM-01`)**:
   - Audit all pipelines where external documents, RAG chunks, or search outputs are injected into prompt context.
   - Confirm user-controlled text cannot impersonate system delimiters or override core guardrails.
2. **Confused Deputy Tool Dispatches (`ORION-LLM-02`)**:
   - Ensure tool arguments generated by models (`run_command`, `write_file`) are validated with strict schemas before execution.
   - Reject unvalidated string concatenation into shell commands or un-canonicalized file paths.
3. **Context & Persistent Memory Poisoning**:
   - Verify unverified chat cannot insert permanent instructions or false triplets into `.orion/orion.db` or vector stores.
4. **Rendered Output Exfiltration (`ORION-LLM-04`)**:
   - Block markdown image tags with external URLs leaking context parameters (`![exfil](https://.../?token=...)`).
   - Sanitize model-generated HTML/SVG artifacts before mounting in the UI.
5. **MCP & Sub-Agent Boundaries (`ORION-LLM-03`)**:
   - Verify MCP server configurations restrict environment variables and apply least-privilege toolsets.
   - Harmonize with [`skill_inspector.md`](skill_inspector.md) to audit third-party skills before adoption.

---

## Vector 11: Memory Safety & Low-Level Binary Invariants
*Goal: Eliminate buffer overflows, use-after-free, integer allocation wrap-around, and unsafe Rust/FFI violations in native code.*
*Runbook Reference: [memory_safety_and_binary.md](memory_safety_and_binary.md)*

### Inspection Rubric:
1. **Spatial Memory & Slice Bounds (`ORION-MEM-01`)**:
   - Audit array indexing and memory copy operations (`memcpy`, `memmove`).
   - Ensure destination lengths are strictly validated against input lengths prior to copying.
2. **Temporal Safety & Lifecycle (`ORION-MEM-02`)**:
   - Verify pointers are zeroed immediately upon deallocation to eliminate use-after-free.
   - Ensure explicit initialization (`calloc` or zeroing) prevents uninitialized memory reads.
3. **Integer & Allocation Hazards (`ORION-MEM-03`)**:
   - Audit dynamic allocations (`count * size`); mandate overflow-checked arithmetic (`calloc` or `checked_mul`).
   - Check signed/unsigned comparison boundaries (`len < MAX` where `len = -1`).
4. **Unsafe Rust Invariants (`ORION-MEM-04`)**:
   - Every `unsafe { ... }` block MUST be preceded by a verified `// SAFETY:` rationale.
   - Audit raw pointer dereferences for concurrent mutable aliasing.
5. **FFI Seams & Memory Ownership (`ORION-MEM-05`)**:
   - Memory allocated by native runtimes MUST be freed by the origin allocator.
   - Verify struct alignment and field padding match byte-for-byte across host/foreign declarations.

---

## Vector 12: Desktop, Mobile & Local IPC Privilege Isolation
*Goal: Thwart local privilege escalation, deep-link hijacking, world-writable IPC channels, and WebView capability leaks.*
*Runbook Reference: [desktop_mobile_ipc.md](desktop_mobile_ipc.md)*

### Inspection Rubric:
1. **Rejection of Fake Peer Authentication (`ORION-IPC-01`)**:
   - Banned: Process names, bundle IDs, and self-reported sender headers as authenticators.
   - Mandated: OS credentials (`SO_PEERCRED`, Windows token impersonation, Android `Binder.getCallingUid()`).
2. **Deep-Link & Custom Scheme CSRF (`ORION-IPC-02`)**:
   - Forbid deep-link URL schemes (`myapp://...`) from executing unauthenticated state changes.
   - Require verified app links (Android App Links, iOS Universal Links) for OAuth redirects.
3. **Transport Security & DACLs (`ORION-IPC-03`)**:
   - Reject world-writable Named Pipes (`NULL` DACL on Windows) and permissive Unix sockets (`0777`).
   - Confirm Android manifests specify `android:exported="false"` for internal components.
4. **WebView JavaScript Bridge Isolation (`ORION-IPC-04`)**:
   - Restrict `@JavascriptInterface` to safe operations; validate `event.origin` in all `postMessage` handlers.
5. **Account & Session Lifecycle Isolation (`ORION-IPC-05`)**:
   - Verify immediate purge of cached responses, tokens, and encryption keys upon user logout.
