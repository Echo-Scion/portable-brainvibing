---
description: Checklist for reviewing source code quality and security before committing (Code Review).
---

# Code Review Workflow

Before accepting or approving code changes (`git diff --name-only HEAD`), perform a check on each modified file based on the following criteria. **Remember: Maintain the "Caveman" protocol. Be terse and direct, do not use pleasantries or empathy.**

## 0. CONTEXT RETRIEVAL (JIT)
- [ ] Verify Binary Oratory compliance. IF unsure, load `rules/core-guardrails.md`.
- [ ] Invoke `@skills/meta-agent-admin` to properly map code relations.
- [ ] **Git Standards**: Load `rules/git-workflow.md` and enforce rules on all reviewed commits.


## Steps

- [ ] **Step 1:** Load `rules/reasoning-standards.md` for logical checking baseline.
- [ ] **Step 2:** Load `rules/security-guardrails.md` for baseline security compliance. Check for **CRITICAL Security** violations (Block commit immediately):
  - Hardcoded credentials, API keys, JWT secrets, or tokens.
  - SQL injection vulnerabilities (use of string concatenation in queries).
  - XSS vulnerabilities (rendering HTML without sanitization).
  - Missing or weak input validation on client/server-side.
  - Path traversal risks (reading files based on direct user input).
- [ ] **Step 3:** Check for **HIGH Code Quality** violations (Block commit if too many):
  - Functions > 50 lines (request extraction into smaller functions).
  - Files > 500 lines (request splitting — matches Vibecode Hard Cap in `performance-optimization.md`).
  - Nesting depth logic > 4 levels (use early returns / guard clauses).
  - *Silent fail*: Missing error handling (empty catch blocks).
  - Leftover `debugPrint()` from debugging or unclear `TODO/FIXME` items.
- [ ] **Step 4:** Provide **MEDIUM Best Practices** suggestions:
  - Variable mutation present (prioritize immutable patterns / data copying).
  - No unit tests for newly added logic/functions.
  - Missing JSDoc/docstrings for public functions or external APIs.

After the review, generate a clear report containing Severity (CRITICAL/HIGH/MEDIUM), file location & line number, problem description, and direct improvement suggestions. NEVER approve code that violates CRITICAL Security points!