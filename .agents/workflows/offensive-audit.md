---
description: "Iterative Audit-Then-Patch Loop with Isolated Subagent Orchestration, Target Finder Integration, and Mandatory Attack Vectors."
---

# 🔍 Sequential Offensive Deep Audit Workflow

**Objective:** Execution mandate for applying the `offensive-audit-protocol` rules safely, deterministically, and iteratively across the codebase without suffering from LLM cognitive fatigue, context degradation, or lazy checklist generation.

---

## 1. The Orchestration & Execution Loop (Execution Mandate)

To prevent *Illusion of Execution* (guessing files) and *Context Window Degradation* (getting lazy over a long chat history), the audit loop MUST be executed using the following strict 3-step automation:

### Step 1: Deterministic Target Discovery
Before auditing, you MUST identify the actual, existing files to scan. Do **not** guess or assume filenames.
1. Run the target finder script in the workspace directory to get a JSON or plaintext list of real files:
   ```powershell
   python .agents/scripts/find_audit_targets.py <TARGET_DIRECTORY>
   ```
2. Parse the output. If the list is empty or the directory is invalid, stop and report immediately.

### Step 2: Isolated Subagent Delegation (Per File)
For every file in the target list, you **MUST NOT** audit it in the primary chat history. Instead, you **MUST** spawn a clean, dedicated sub-agent for each file.
1. Prepare the Subagent prompt. The prompt must be structured as:
   - **System Prompt**: Set the role to `"Lead Quant Security Auditor"` and load the full contents of `.agents/rules/offensive-audit-protocol.md`.
   - **Task**: "Audit the following file according to the protocol rules. Fill out the Per-File Audit Checklist completely without omitting any points or summarizing. Do not cut corners."
   - **Target File**: Inject the path and absolute content of the file.
2. Call the `invoke_subagent` tool with the role `"File Auditor: [Filename]"` and the prepared prompt.
3. Wait for the subagent's response. The subagent will run with a pristine context window, guaranteeing 100% focus and zero shortcutting (*Lazy Generation*).

### Step 3: Synthesis & Iterative Patch Loop
1. **Consolidate Results**: Review all individual subagent reports. Compile a unified Audit Report.
2. **User Confirmation**: If critical bugs are found, STOP and await instruction. If NO bugs are found, proceed.
3. **Patch Phase**: Implement surgical, deterministic fixes for identified vulnerabilities.
4. **Validation**: Run the tests. Once verified, move to the next set of findings.

---

## 2. Mandatory Attack Vectors & Temporal Simulations

When auditing (and within the subagent prompt), you MUST actively stress-test the target file using these specific scenarios:

* **Temporal Simulation (T=0s, T=15s, T=30s) & Collisions:** Simulate split-second collisions between components (e.g., Webhook listeners and DB Sync). Example: T=0s user deletes account, T=15s scheduled cron attempts to read user data, T=30s cache invalidates.
* **Precision Truncation / Edge Maths:** Check for division by zero or precision loss in analytics/pricing math. What if a floating-point calculation drops sub-decimals or divides by zero?
* **Systemic Failure Cascades / API Rate Limits:** Check if 429 errors block the entire event loop. What if a 3rd-party API returns `Retry-After: 3600`? Does the entire thread hang for an hour? What if large JSON payloads are not garbage collected, causing an OOM kill?
* **Orphaned Promises:** Hunt for floating Promises or unawaited async calls in background loops that swallow errors silently.
* **Data Poisoning / Malformed Inputs:** What if a user submits a massive payload or an unexpected array? Does an edge case return `NaN` or `null`, poisoning downstream logic?
* **Type Coercion:** What if an external API returns a number as a string `"10"`? Does the math concatenate strings instead of multiplying?
* **State Inversion / Race Conditions:** If boolean states flip instantly (e.g., active -> suspended -> active), does the state management or hedging logic break?

---

## 3. Audit Checklists

### A. The Plan Checklist

Every plan or logic execution must pass these 5 checks:

1. [ ] KISS
2. [ ] YAGNI
3. [ ] DRY
4. [ ] Fail-fast
5. [ ] Retry-safe

### B. Per-File Audit Checklist (Pipeline-Aware)

Each sub-agent MUST output this exact 12-point block for the file it audits:

* [ ] **1. PURPOSE** — What is the main function of this file? (1 sentence)
* [ ] **2. PIPELINE** — How does this file connect to the larger flow (Data -> Risk -> Exec -> Learn)?
* [ ] **3. IMPORTS** — Which files are imported? (list)
* [ ] **4. CONSUMERS** — Which files import from this file? (Trace explicitly via grep before proceeding)
* [ ] **5. TEMPORAL** — Does this file survive a T=0s, T=15s, T=30s state-machine-collision?
* [ ] **6. LOGIC BUGS** — Are there mathematical flaws, missing edge cases (NaN, Sub-Penny), or zero divisions?
* [ ] **7. PERF BUGS** — Are there memory leaks (Pandas), N+1 DB queries, or heavy synchronous blocking?
* [ ] **8. SEC BUGS** — Are there API key leaks, missing input validations, or unprotected type coercions?
* [ ] **9. CONC BUGS** — Is there mutable shared state, race conditions, or un-safeguarded DB writes?
* [ ] **10. CROSS-FILE** - If this file's output changes shape, will downstream consumers crash?
* [ ] **11. FAIL-FAST** — Are there any silent catch/swallow errors? (CRITICAL)
* [ ] **12. FINDING** — Bugs/smells/improvements found based on the categories above.