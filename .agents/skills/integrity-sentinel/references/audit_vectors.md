# Unified Audit Vectors Matrix (The Core Diagnostic Vectors)

> "Every changed line must trace directly to user intent." — `.agents/rules/core-guardrails.md`

This document consolidates the 7 primary static and semantic audit vectors into a single, cohesive evaluation matrix. When conducting quality assurance or deep code review, evaluate the target codebase against these vectors sequentially while enforcing the **Calibration & Anti-Moving-Goalposts Clauses**:
- **Materiality Threshold**: Flag findings ONLY when proven to cause runtime failures (`Exception`/`Crash`), data/state corruption, exploitable security vulnerabilities, or non-functional empty stubs. Do not flag minor stylistic variations.
- **Intentional Architecture Exemption**: Defensive fallbacks inside `except ImportError:` blocks and standalone hook scripts (`hooks/`) with local helpers (`_atomic_write_text`, `_log_telemetry`) are NOT DRY violations. Documented retrieval-only modes are NOT shallow shims.
- **Convergence Guarantee**: When all mechanical gates pass (`Exit Code 0`) and zero material bugs exist, conclude with zero findings rather than inventing microscopic nitpicks.

---

## Vector 1: Architecture & High-Level System Mapping
*Goal: Understand core boundaries, data flows, and risk zones before micro-auditing.*

### Inspection Rubric:
1. **Entry Points & Flows**: Map user interaction -> API/Controller -> Service -> Data Persistence.
2. **Outside Services**: Identify external dependencies (payment gateways, third-party APIs, auth providers).
3. **Boundary Coupling**: Check if layers violate separation of concerns (e.g., UI directly executing SQL or querying persistence models).
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
