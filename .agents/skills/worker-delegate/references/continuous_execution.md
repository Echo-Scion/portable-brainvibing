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
