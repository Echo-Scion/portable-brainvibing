# The Telemetry Gate (Pre-Debug Hard Gate)

Before investigating ANY runtime bug, crash, or unexpected behavior, the agent MUST collect crime scene evidence. No evidence = no investigation.

## Hard Gate Checklist

The following 4 items MUST be present before writing a single line of fix code. If ANY item is missing, **STOP** the debug attempt and request the missing data from the user.

### 1. Error Signal (MANDATORY)
At least ONE of:
- Exact error message or stack trace (copy-pasted, not paraphrased)
- HTTP status code + response body
- Screenshot of the failure state
- Log output from the failing process
- Console error output

**Invalid inputs** (reject these):
- "It doesn't work" → Ask: "What exactly happens? Paste the error message."
- "It crashes" → Ask: "Paste the stack trace or crash log."
- "It's broken" → Ask: "What do you see on screen? What did you expect?"

### 2. Timestamp & Frequency (MANDATORY)
- When did it first occur? (date/time or "always")
- Is it reproducible? ("every time" / "intermittent ~30%" / "happened once")
- Did it work before? If yes, what changed? (deploy, config, dependency update)

### 3. Environment Context (MANDATORY)
- Where: local dev / staging / production / CI
- OS + runtime version (e.g., "Windows 11, Flutter 3.29", "Ubuntu 22, Node 20")
- Relevant config state (DB connected? API keys set? Network accessible?)

### 4. Reproduction Path (MANDATORY — at least attempted)
- Steps the user took to trigger the failure, OR
- "Cannot reproduce — only happens in production" (this IS valid, but changes the investigation strategy to log analysis instead of local debugging)

## Gate Decision Matrix

| Evidence Available | Action |
|:-------------------|:-------|
| All 4 items present | ✅ Proceed to Root Cause Analysis (5-Why Script) |
| 3 of 4 present | ⚠️ Proceed with caution. Document what's missing in the task log. |
| 2 or fewer present | 🛑 STOP. Request missing evidence. Do NOT guess. |
| "Cannot reproduce" declared | 🔍 Switch to Log Analysis mode — request production logs, metrics dashboards, or APM traces instead of local repro. |

## Post-Gate: Investigation Protocol

Once the gate is cleared:

1. **Start from the crash point** — read the stack trace bottom-up. Identify the exact line, exact variable, exact state.
2. **Write a reproduction test** — per `core-guardrails.md §2` (5-Why Script). Must return `Exit Code > 0`.
3. **Trace backwards** — from the crash line, identify every variable assignment and function call that feeds into it.
4. **Identify the delta** — what changed between "it worked" and "it broke"? (commit diff, config change, data migration, dependency bump)
5. **Fix at root cause** — not at symptom. If `user_id` is null at line 89, the fix is wherever `user_id` should have been validated, not a null-check at line 89.

## Anti-Patterns (FORBIDDEN)

- ❌ "Let me look at the code and see what might be wrong" — without evidence, this is guessing.
- ❌ Adding defensive null-checks everywhere "just in case" — this is symptom masking, not root cause fixing.
- ❌ "I think the problem might be..." — without stack trace or reproduction, confidence is too low to act.
- ❌ Skipping the gate because the user seems impatient — silent bugs cost more than delayed fixes.

## Output Format

Before starting debug work, emit this block to prove the gate was satisfied:

```xml
<telemetry_gate>
  <error_signal>[Paste or summarize the exact error]</error_signal>
  <timestamp>[When / frequency]</timestamp>
  <environment>[Where it runs]</environment>
  <reproduction>[Steps or "log analysis mode"]</reproduction>
  <gate_status>[PASS | PARTIAL (missing: X) | FAIL]</gate_status>
</telemetry_gate>
```

If `gate_status` is FAIL, your next action MUST be requesting the missing data. No exceptions.
