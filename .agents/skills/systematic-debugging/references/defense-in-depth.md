# 4-Layer Defense-in-Depth Validation Protocol

> **Core Principle**: When fixing a defect caused by invalid data or unexpected state, adding validation at a single site is fragile. Validate at EVERY architectural layer the data traverses to make the bug structurally impossible.

---

## The Four (4) Validation Layers

```
Layer 1: Entry Point Validation      (Reject malformed input at boundary)
                 │
                 ▼
Layer 2: Business Logic Validation   (Enforce domain invariant consistency)
                 │
                 ▼
Layer 3: Environment Test Guards     (Refuse destructive actions outside sandbox)
                 │
                 ▼
Layer 4: Forensic Instrumentation    (Emit structured audit logging)
```

### Layer 1: Entry Point Boundary Validation
- Validate argument presence, type constraints, and non-empty strings before dispatching to internal methods.
- Example: Reject empty workspace paths or malformed JSON payloads at CLI / API routers.

### Layer 2: Business Logic & Domain Invariants
- Assert that the operation makes sense within the current domain state.
- Example: Ensure target workspace exists and contains valid manifests before scheduling builds.

### Layer 3: Environment & Sandbox Guards
- Prevent dangerous operations in testing or staging environments.
- Example: Refuse `git init`, destructive file writes, or table drops outside temporary directories (`tempfile.gettempdir()`) when running under test suites.

### Layer 4: Forensic Instrumentation
- Emit structured log telemetry capturing caller context before executing critical sinks.
- Example: Log execution parameters, timestamps, and caller signatures to enable 3 AM incident triage.

---

## The Verification Gate
When reporting a fix for a data-integrity bug:
1. Map all checkpoints the corrupted data traversed.
2. Confirm that defensive assertions exist at least across Layers 1, 2, and 3.
3. Test each layer independently (verify that bypassing Layer 1 still causes Layer 2 or 3 to catch the defect).
