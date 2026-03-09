---
name: systematic-debugging
description: >-
  Executes a 4-phase scientific debugging protocol with single hypothesis trees, survivor verification, and circuit breaker. Use when investigating runtime bugs, failing tests, unexpected behaviors, or system crashes before modifying implementation code.
---

# 🌲 Systematic Debugging Protocol (Scientific Root-Cause Discipline)

Use `python .agents/scripts/orion.py sandbox` or `SovereignSandbox.execute_snippet()` for isolated reproduction snippets before modifying production code.

> **The Iron Law**: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.  
> If you have not deterministically proven the root cause, you are FORBIDDEN from modifying implementation code.

Execute these four phases sequentially for ANY bug, test failure, crash, or unexpected behavior:

## Phase 1: Root Cause Investigation
1. **Read Error Messages & Stack Traces Completely**:
   - Note exact file paths, line numbers, and error codes. Do NOT skim or jump to assumptions.
2. **Deterministic Minimal Reproduction (Scratchpad Isolation Gate)**:
   - Formulate exact reproduction steps. Create a standalone reproduction test case in a temporary scratch script (e.g., `scratch/repro_<issue>.<ext>`) or ephemeral test that exits with `Exit Code > 0`.
   - **Zero Production Mutation**: NEVER modify production source code or persistent database tables just to probe or reproduce a bug. Reproduction must remain completely isolated in the scratchpad harness.
3. **Trace Data Flow Backward**:
   - Trace backwards from the symptom or bad value to the exact origin in the call stack. Fix at the source, never at the symptom.
4. **Multi-Component Diagnostic Logging**:
   - When issues span boundaries (API -> Service -> DB, CLI -> Subprocess), add temporary diagnostic logs at each boundary (input data, output data, state). Pinpoint precisely which layer breaks before touching logic.

## Phase 2: Pattern Analysis
1. **Find Working Examples**: Locate similar working implementations in the same codebase.
2. **Differential Analysis**: Compare the working code against the broken code line-by-line. List every difference without assuming "that can't matter."
3. **Dependency & Environment Verification**: Check active configuration, environment variables, and state assumptions.

## Phase 3: Single Hypothesis & Minimal Testing
1. **Formulate Explicit Hypothesis**:
   - Write a single-sentence hypothesis: *"Condition X causes invariant Y to fail because of state Z."*
2. **Minimal Single-Variable Modification**:
   - Test the hypothesis by changing ONE variable at a time.
   - Strictly forbid bundled refactoring, formatting cleanup, or "while I'm here" modifications during debugging.
3. **Evaluate Outcome & Mandatory Rollback**:
   - If reproduction test passes, advance to Phase 4.
   - If test still fails, discard hypothesis immediately.
   - **Mandatory Rollback Gate**: You MUST execute `git stash push --include-untracked -m "debug-hypothesis-rollback" -- <target_file>` to revert modifications non-destructively before testing the next hypothesis. Speculative changes MUST NEVER accumulate across hypotheses (Anti-Shotgun Rule).
   - If 2 consecutive hypotheses fail, document root-cause analysis before attempting Hypothesis 3.

## Phase 4: Implementation, Survivor Verification & Circuit Breaker
1. **Targeted Root Cause Fix**: Apply the surgical fix directly addressing the proven root cause.
2. **Survivor Verification**:
   - Verify reproduction test exits with `Exit Code 0`.
   - Run the full project test suite to prove zero regression (`Exit Code 0`).
3. **The 3-Attempt Circuit Breaker**:
   - If 3 consecutive fix attempts fail, STOP calling tools immediately.
   - Repeated failure indicates an architectural flaw or wrong pattern, NOT a missing tweak.
   - Acknowledge the pattern failure, output error analysis, and consult user before attempting further fixes.

## 🔒 Causal Enforcement (The "No-Fix" Policy)
- **Protocol**:
  1. Write `reproduce_bug.<ext>` or `<feature>_test.<ext>` (e.g. `.py`, `.ts`, `.go`, `.dart`).
  2. Run the script.
  3. If script succeeds (no bug found), STOP fix.
  4. If script fails (bug proven), proceed with implementation.
