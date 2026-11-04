# ⚡ Continuous Execution Protocol: Rulings, Not Stalls

> **Origin**: Sovereign Sub-Agent Execution Protocol.
> **Purpose**: Eliminates conversational stalling, unnecessary check-ins, and artificial "Should I continue?" blockers during multi-step plan execution.

---

## 1. The Core Principle: Continuous Execution

When the user commands **"Execute"** or approves an implementation plan:
- **Execute all plan tasks without stopping**: Do NOT pause between tasks to ask "Should I proceed to step 2?". Complete the work.
- **Rulings, Not Stalls**: A running plan does not park on a human question for minor edge cases or ambiguities. Decide them decisively.
  - Record each decision as: `Ruling: <decision> — <rationale> — <rework cost if wrong>`.
  - Keep going. A wrong ruling costs minor rework that can be reviewed; parking the session costs human time and stalls momentum.

---

## 2. The Four (4) Legitimate Stoppage Conditions

The agent MUST stop and prompt the user ONLY under these four strict conditions:
1. **Irreversible or Destructive Operations**: Deleting uncommitted files, dropping production databases, wiping git history.
2. **Security-Sensitive Actions**: Leaking private keys, bypassing canary guardrails, granting unbounded remote permissions.
3. **Out-of-Worktree Side Effects**: Pushing to shared remote branches, deploying to public production registries without staging gates.
4. **Completely Broken Spec**: The plan is structurally defective and every path forward is blind guesswork.

Outside of these four conditions: **EXECUTE TO COMPLETION.**

---

## 3. Subagent Dispatch Invariant

- Fresh subagents handle isolated units of work (e.g., AST scans, repo mapping, test mutations) without context bleed.
- Parent orchestrator holds the active plan state machine (`fsm transition EXECUTING` $\to$ `VERIFYING` $\to$ `DONE`).
- Narrate at most 1–2 lines between execution steps. The execution evidence and exit codes carry the record.

---

## 4. The 5-Round Bounded Fix Loop

When a subagent task review reports test failures, missing requirements, or Critical/Important findings:

### Triage Routes
- **Minor Findings (`🔵 nit`)**: Never enter the fix loop. Append directly to `.orion/working/audit/00-ledger.md` as `Task <N>: minor (deferred): <finding>`. The final branch review triages them before merge.
- **Plan-Mandated Conflicts**: Weigh the finding against the plan text. If the finding reflects a plan defect, record a ruling before dispatching fixes.

### Fix Rounds (Maximum 5 Rounds)
1. **Rounds 1–3 (Same Implementer Tier)**:
   - Re-dispatch to the implementer tier carrying the exact open findings, brief path, and test logs.
   - The implementer fixes the code, runs the focused test covering amended files, and returns the short contract.
2. **Rounds 4–5 (Capability Bump + Fresh Eyes)**:
   - If the issue survives 3 rounds, the implementer cannot see its own defect.
   - Dispatch to a fresh subagent on a higher model tier (e.g., `BUDGET` $\to$ `STANDARD` or `STANDARD` $\to$ `PREMIUM`) with:
     *"A prior implementer attempted this task 3 times; you own it now. Inspect the report file for what was tried."*
3. **Round 5 Breaker (Controller Adjudication)**:
   - If Round 5 still leaves findings open, stop dispatching. Adjudicate each open finding:
     - *Contestable/Wrong Reviewer*: Park it: `Task <N>: parked — <finding> — Ruling: <why code stands>`.
     - *Real but Non-Blocking*: Park it as deferred.
     - *Real & Load-Bearing*: Decide the smallest surgical change unblocking dependent tasks and carry the ruling forward.
