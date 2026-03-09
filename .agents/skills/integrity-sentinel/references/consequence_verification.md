# Consequence-Driven Runtime Assertion & False Green Prevention

> **Core Principle**: A green test is evidence about the *test*, not about the *application*. Verification requires proving concrete runtime consequences, not observing the mere absence of crashes.

---

## 1. The Five Shapes of False Green Tests

A "false green" occurs when an automated test suite passes with exit code 0 while the underlying feature is non-functional or broken in production.

| Shape | Defect Signature | Why It Passes | How to Eliminate It |
| :--- | :--- | :--- | :--- |
| **1. Absence-Only Assertion** | `expect(err).toBeNull()`, `assert not error` | A dead button or un-wired event handler throws nothing, dispatches nothing, and changes nothing. | Mandate positive consequence assertions: assert state mutation, signal emission, or wire request. |
| **2. Mock Drift / Mock-Only Test** | Test drives a stubbed mock; app runtime drives a real endpoint | Mock returns hardcoded fixture while backend API contract has drifted or changed status codes. | Assert against real wire requests or validate mock signatures against live schema contracts. |
| **3. UI Moved, State Stagnant** | DOM visual toggle changes, but application store/database does not update | Client component toggles local CSS state while backend sync silently fails or was never triggered. | Assert Tier 2 state change: inspect store path or database entity delta alongside UI render. |
| **4. Unconsumed Response** | API returns `200 OK`, but response payload is never parsed or consumed | Network tab shows success, but caller lacks an `await`, ignores returned data, or drops promise. | Assert that state reflects payload content (`verifiedReason: outcome_unread` if response is dropped). |
| **5. Untouched Critical Surfaces** | High unit test coverage percentage, zero end-to-end user journey exercise | 100% of helper functions pass, but integration seam between router, auth, and state is never executed. | Deterministic flow replay across end-to-end journey steps (`FlowSpec`). |

---

## 2. The Three Consequence Tiers

Every meaningful user action produces consequences across three distinct architectural tiers. Validations must assert consequences across at least two tiers to achieve high confidence:

```
+-----------------------------------------------------------+
| TIER 1: Machine Signals & Telemetry                       |
| (Events dispatched, custom bus signals, telemetry pings)  |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| TIER 2: State, Network & Route Deltas                     |
| (Store path mutation, HTTP request + status, URL route)   |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| TIER 3: DOM Existence & Render Consequence                |
| (Rendered text, accessibility attributes, mounted nodes)  |
+-----------------------------------------------------------+
```

### Tier 1: Machine-Level Signal
- **Mechanism**: Event bus emission, telemetry ping, framework dispatch signal.
- **Predicate**: `{ kind: "signal", name: "order.placed", payloadMatches: { ... } }`.
- **Verdict Value**: Proves the event handler actually fired and executed business logic.

### Tier 2: State, Network & Route Delta
- **Mechanism**:
  - **Network**: Concrete HTTP request sent over the wire: `{ kind: "net", method: "POST", urlContains: "/api/checkout", status: 200 }`.
  - **State**: Centralized store (Redux, Zustand, Pinia, Riverpod, SQL DB) path mutated: `{ kind: "state", path: "cart.items", op: "empty" }`.
  - **Route**: URL navigation occurred: `{ kind: "route", path: "/confirmation", queryContains: { id: "..." } }`.
- **Verdict Value**: Proves system state transitioned and external contracts were fulfilled.

### Tier 3: DOM & Render Consequence
- **Mechanism**: Visible text rendered, ARIA role updated, error banner mounted.
- **Predicate**: `{ kind: "dom", selector: "[data-testid='order-summary']", textContains: "Success" }`.
- **Verdict Value**: Proves user perception reflects the state change.

---

## 3. Consequence Predicate Composition

Predicates can be composed to form ironclad assertions:

```json
{
  "kind": "allOf",
  "predicates": [
    { "kind": "net", "method": "POST", "urlContains": "/api/v1/projects", "status": 201 },
    { "kind": "state", "path": "projects.current.id", "notEmpty": true },
    { "kind": "dom", "selector": "[data-testid='project-header']", "textContains": "My New Project" }
  ]
}
```

If the network call returns 201 but the DOM or state does not update, the verdict is `FAIL` with `reason: "contradicted"` (the tiers disagree).

---

## 4. Deterministic Flow Replay (Zero-Model Replay)

Rather than spending LLM tokens re-driving interactive UI journeys on every commit:
1. **Record Once**: Store user journey as a sequence of deterministic steps:
   - `ref`: Element identifier (`data-testid`, semantic role, or unique selector).
   - `action`: `click`, `fill`, `select`, `navigate`.
   - `until`: Expected consequence predicate (Tiers 1–3).
2. **Replay Deterministically**: Run replay engine via `.agents/evals/consequence_verifier.py`.
3. **Verify Verdict**:
   - `PASS`: All steps reached their `until` predicates within timeout.
   - `FAIL`: Step drift (target disappeared) or predicate unsatisfied (`SUCCESS_NOT_MET`).
   - `UNKNOWN`: Missing telemetry or uninstrumented surface.
