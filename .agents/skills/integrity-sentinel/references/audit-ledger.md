---
name: audit-ledger
description: Formal protocol for maintaining an AUDIT_STATE and Ledger across long-running or multi-session codebase audits.
---

# AUDIT STATE & LEDGER PROTOCOL

This workflow provides a standardized approach for conducting deep, multi-phase audits across a codebase. Without a ledger and persistent state, AI agents lose context, repeat work, or hallucinate progress across chat boundaries.

## 1. The Core Concept

When an audit is too large to complete in a single prompt or session, you MUST decouple the **findings** (Ledger) from the **current execution progress** (Audit State). 

1. **The Ledger (`00-ledger.md`)**: A master checklist of all discovered vulnerabilities, tech debt, and missing features. It is the single source of truth for what needs fixing.
2. **The Audit State (`AUDIT_STATE.md`)**: A tracking document that records exactly which phase the audit is currently in, what files have been scanned, and what the immediate next step is.

## 2. Directory Structure

Place these tracking files in an isolated directory that is ignored by standard context ingest (e.g., `.orion/working/audit/` or `.agents/archive/prompts/` if managing the foundation).

```
.orion/working/audit/
├── 00-ledger.md       # The master checklist of findings
└── AUDIT_STATE.md     # The current progress pointer
```

## 3. The Ledger Format (`00-ledger.md`)

Use a strict, ID-based format. Never use checkboxes for findings. Use explicit status labels to prevent LLM hallucinations.

**Status Labels:**
- `[OPEN]`: Newly discovered, not yet addressed.
- `[IMPLEMENTATION]`: Code has been written, but not yet verified.
- `[FIXED]`: Code written, tested, and strictly verified (Exit Code 0).
- `[REGRESSION]`: A previously fixed item broke again.
- `[REFUTED]`: Finding was a false positive or hallucination.

**Example Format:**
```markdown
## Security [01]
- S1 [OPEN]: Hardcoded JWT secret in `auth.ts`.
- S2 [FIXED]: SQL Injection vulnerability in `getUser()`.

## Logic [02]
- L1 [IMPLEMENTATION]: Missing transaction wrapper in `checkout`.
```

## 4. The Audit State Format (`AUDIT_STATE.md`)

This file prevents agents from re-scanning the same files. It MUST be updated at the end of every agent turn during an active audit.

**Example Format:**
```markdown
# AUDIT STATE

**Current Phase:** 3 (Deep Logic Analysis)
**Target Directory:** `src/services/`
**Files Scanned So Far:**
- `src/services/auth.ts`
- `src/services/billing.ts`

**Current Focus:** `src/services/inventory.ts`
**Next Action:** Run `grep_search` to find database write calls in inventory service, log any missing transactions to `00-ledger.md`.
```

## 5. Execution Rules

1. **Idempotency**: Always read `AUDIT_STATE.md` at the start of a session to know where to resume.
2. **Decoupled Fixing**: Never fix bugs *during* the discovery phase. Log them to the Ledger as `[OPEN]`. Wait until discovery is 100% complete before moving to the resolution phase.
3. **Verification First**: Never mark an item `[FIXED]` without mechanical proof. Route fixes through `/audit-and-test` (Strict TDD: Red -> Green -> Refactor) to capture passing test proof (Exit Code 0).
4. **Fused Workflow**: When fixing items from the Ledger, `/audit-and-test` automatically hooks into `AUDIT_STATE.md` and `00-ledger.md` without requiring separate invocations.
