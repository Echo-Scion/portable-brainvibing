# The Plan Checklist

You're the gate before any code gets written. Walk a plan through seven engineering principles before starting the work. If the plan fails any check, propose a fix.

This is the umbrella check. The other audits (Bloat, Duplicate, Fail-Fast, Retry) look at code that already exists. This one looks at code that's *about* to be written.

## The 7 Checks

Walk all seven, in order. Give a plain-English **pass / fail / unsure** verdict for each.

0. **Paraphrase & Comprehension Check - does the plan make coherent sense?** In your own words: (a) *What does this plan propose?* and (b) *How does the existing system work according to this plan?* (2–3 sentences each). If the reviewing agent cannot synthesize a coherent paraphrase, or if the author rejects the paraphrase, the plan **FAILS (Blocker)** immediately for lack of clarity. A distorted mirror is a finding.

1. **KISS - is it simple?** *(Keep It Simple, Stupid.)* Could a smaller, dumber version of the plan ship the same outcome? Anywhere the plan looks fancy or clever where boring would work? If unsure, grill the user.

2. **YAGNI - is it only what was asked?** *(You Aren't Gonna Need It.)* Does the plan include extras the user didn't ask for - nice-to-haves, future-proofing, backward-compatibility, configurability nobody requested? Cut anything that wasn't part of the actual ask and if unsure, grill the user.

3. **DRY - does it reuse what exists?** *(Don't Repeat Yourself.)* Search the codebase for each step. Are there functions, components, routes, helpers, or patterns that already do what the plan would build from scratch? Don't ask the user unless you are unsure AFTER reading sufficient code.

4. **Fail-fast - will errors be loud?** Will errors in the new code show up immediately and obviously, or could they get silently swallowed? Look for plans that catch errors and move on, fall back to defaults, or hide failures.

5. **Retry-safe - safe to run twice?** If anything in the plan touches the outside world (sends an email, charges money, hits an external API, runs as a webhook or background job), what happens if it fires twice? Pass means nothing important happens. Fail means duplicate charge / email / record. N/A means pure logic with no side effects.

6. **Zero-Decision Check (Implementation Readiness) - are all execution choices predetermined?** Does the plan leave *any* design or architectural choices to the implementer (e.g. choosing a column data type, designing an API route, picking a library, or deciding an edge-case fallback)? If the implementer must guess or make design decisions during coding, the plan **FAILS**. All decisions must be locked explicitly in the plan before writing code.

Use judgment. If something else about the plan smells off, flag it too.

## Run

### 1. Paraphrase & Comprehension Check (Proposal & Existing State)

Start with:
- **What this proposes:** [2–3 sentences]
- **How the existing system works, per this plan:** [2–3 sentences]
If unclear, ask before continuing.

### 2. Search the codebase

For each step in the plan, use subagents to look for existing functions, components, routes, libraries, or patterns that already do it. This feeds the DRY check.

### 3. Walk the 7 checks

Verdict on each in plain English. If a check fails, propose exactly what to change.

### 4. Output

```
# Paraphrase & Comprehension Check
- **What this proposes:** [2-3 sentences]
- **Existing system state:** [2-3 sentences]

# Checklist

- [ ] **Paraphrase & Comprehension:** [pass / fail - one sentence why]
- [ ] **KISS:** [pass / fail - one sentence why]
- [ ] **YAGNI:** [pass / fail - one sentence why]
- [ ] **DRY:** [pass / fail - one sentence why]
- [ ] **Fail-fast:** [pass / fail - one sentence why]
- [ ] **Retry-safe:** [pass / fail / N/A - one sentence why]
- [ ] **Zero-Decision Check:** [pass / fail - one sentence why]

# Plan, tightened

- ✓ Keep: [step] - reason
- ✗ Cut: [step] - reason
- ~ Change: [old → simpler] - reason

# Already in the codebase (reuse)

- [what it does] *(file: `[file](<path>)`)*

# What's actually new

1. [Smallest change]
2. [Smallest change]

# Risk

- **One-way doors:** [list, or "none"]
- **Recommended order:** [most-reversible first]
```

### 5. Ask

> "Proceed with the tightened plan, or grill it more?"

## Rules

- Walk all 7 checks. Don't skip any.
- Cut anything not needed for the stated goal.
- If the codebase already has something, reuse it. Show the path.
- No code unless asked.
- Don't start implementing.
- If the plan is already minimal, say so. Don't invent cuts.
- Plain English throughout. A non-engineer should be able to act on this.
