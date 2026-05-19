---
description: "Iterative Audit-Then-Patch Loop, Mandatory Attack Vectors & Temporal Simulations, and Audit Checklists."
---

# 🔍 Sequential Offensive Deep Audit Workflow

**Objective:** Execution mandate for applying the `offensive-audit-protocol` rules safely and iteratively across the codebase.

## 1. The Iterative Audit-Then-Patch Loop (Execution Mandate)

You MUST NOT skip ahead. You MUST follow this exact lifecycle for EVERY Phase:

* **Audit Phase:** Identify vulnerabilities using Temporal Simulation and State-Machine Emulation.
* **User Confirmation:** If a critical bug is found, STOP and await instruction. If NO bugs are found, explicitly state "Phase X PASSED" and IMMEDIATELY proceed to Phase X+1.
* **Patch Phase:** Implement surgical fixes for all identified vulnerabilities in that Phase.
* **Validation:** Verify the fix. Only move to the next phase after implementation is complete.
* **Self-Evolution (Phase 9):** If you reach the end and NO code was patched (everything passed), output `[SYSTEM_MATURITY_REACHED]` and stop. If patches were applied, generate new, RARE BUT PLAUSIBLE simulation targets for the next round and restart at Phase 1.

## 2. Mandatory Attack Vectors & Temporal Simulations

When auditing, you MUST actively try to break the code using these specific scenarios:

* **Temporal Simulation (T=0s, T=15s, T=30s) & Collisions:** Simulate split-second collisions between components (e.g., Webhook listeners and DB Sync). Example: T=0s user deletes account, T=15s scheduled cron attempts to read user data, T=30s cache invalidates.
* **Precision Truncation / Edge Maths:** Check for division by zero or precision loss in analytics/pricing math. What if a floating-point calculation drops sub-decimals or divides by zero?
* **Systemic Failure Cascades / API Rate Limits:** Check if 429 errors block the entire event loop. What if a 3rd-party API returns `Retry-After: 3600`? Does the entire thread hang for an hour? What if large JSON payloads are not garbage collected, causing an OOM kill?
* **Orphaned Promises:** Hunt for floating Promises or unawaited async calls in background loops that swallow errors silently.
* **Data Poisoning / Malformed Inputs:** What if a user submits a massive payload or an unexpected array? Does an edge case return `NaN` or `null`, poisoning downstream logic?
* **Type Coercion:** What if an external API returns a number as a string `"10"`? Does the math concatenate strings instead of multiplying?
* **State Inversion / Race Conditions:** If boolean states flip instantly (e.g., active -> suspended -> active), does the state management or hedging logic break?

## 3. Audit Checklists

### A. The Plan Checklist

Every plan or logic execution must pass these 5 checks:

1. [ ] KISS
2. [ ] YAGNI
3. [ ] DRY
4. [ ] Fail-fast
5. [ ] Retry-safe

### B. Per-File Audit Checklist (Pipeline-Aware)

For every file read, the AI MUST output:

* [ ] **1. PURPOSE** — What is the main function of this file? (1 sentence)
* [ ] **2. PIPELINE** — How does this file connect to the larger flow (Data -> Risk -> Exec -> Learn)?
* [ ] **3. IMPORTS** — Which files are imported? (list)
* [ ] **4. CONSUMERS** — Which files import from this file? (Trace explicitly via grep before proceeding)
* [ ] **5. TEMPORAL** — Does this file survive a T=0s, T=15s, T=30s state-machine collision?
* [ ] **6. LOGIC BUGS** — Are there mathematical flaws, missing edge cases (NaN, Sub-Penny), or zero divisions?
* [ ] **7. PERF BUGS** — Are there memory leaks (Pandas), N+1 DB queries, or heavy synchronous blocking?
* [ ] **8. SEC BUGS** — Are there API key leaks, missing input validations, or unprotected type coercions?
* [ ] **9. CONC BUGS** — Is there mutable shared state, race conditions, or un-safeguarded DB writes?
* [ ] **10. CROSS-FILE** - If this file's output changes shape, will downstream consumers crash?
* [ ] **11. FAIL-FAST** — Are there any silent catch/swallow errors? (CRITICAL)
* [ ] **12. FINDING** — Bugs/smells/improvements found based on the categories above.