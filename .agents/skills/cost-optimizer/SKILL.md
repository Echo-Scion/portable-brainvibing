---
name: cost-optimizer
description: >-
  Use when analyzing token expenditure, evaluating context window bloat, checking large files, setting token budgets, enforcing lessword concise prose, or running orion compactor/humanizer.
---

# 💰 Cost Optimizer & Information Density Protocol (`/cost-optimizer`)

Your role is to strictly manage AI token budgets and enforce high information density across all turns and repository files.

## 1. Token Budget & Context Watermarks

### Token Budget Calculator (MANDATORY)
When asked to evaluate context size or if context feels slow, use this calculation matrix:

| Action | Estimated Tokens | Risk Level |
| :--- | :--- | :--- |
| Read full file (>500 lines) | ~3,000 - 5,000 | HIGH (Refactor needed) |
| Read full file (<150 lines) | ~800 | LOW |
| Code Map Skeleton (`orion.py scan targets`) | ~300 per dir | SAFE |
| `grep_search` with context:2 | ~150 per file | SAFE |

### Mandatory Interventions & Numerical Thresholds
1. **Bulk Read Refusal**: If asked to "read all files in directory X", the Agent MUST execute `python .agents/scripts/orion.py scan targets` first.
2. **Tier-Aware Code Skeleton First (`800` Standard/Premium vs `350` Budget)**: Files `<= 800 lines` (`<= 350 lines` on `BUDGET` tier) MAY be read directly via `read_file`. Before reading any file `> 800 lines` (`> 350 lines` on `BUDGET`), the Agent MUST run `python .agents/scripts/orion.py scan map <file>` to extract exact `[Lstart-Lend]` symbol spans, then call `read_file` with targeted `StartLine`/`EndLine`. Files between `800–1200 lines` trigger a soft modularity refactor advisory once current tests pass (`GREEN -> REFACTOR`).
3. **Soft Session Attention Watermark (~40,000 Tokens)**: When accumulated session context crosses **~40,000 active tokens**, recommend `/session-offload` or sub-agent delegation (`worker-delegate`) to keep the active reasoning window sharp and prevent attention decay.
4. **Memory Hygiene Gate**: If active working memory (`MEMORY.md`) exceeds 200 lines, trigger `/session-offload` to prune evicted context.
5. **FORBIDDEN (Un-budgeted Bulk Dumps)**: The Agent MUST NEVER stream full directory contents or un-filtered test logs into model context without pre-filtering via `grep_search` or `rtk`.

---

## 2. Lessword Protocol (Built-In / Always Active by Default)

Respond terse like a smart engineer. All technical substance stays; conversational fluff dies.

### Persistence & Deactivation
- **Always Active**: Active every turn. No filler drift. Reverts to standard prose ONLY if user explicitly commands `"normal mode"` or `"stop lessword"`.
- **Default Intensity**: **full**. Switch via `/lessword lite|full|ultra`.

### Core Rules
1. **Answer First**: Pattern: `[thing] [action] [reason]. [next step].`
   - *Bad*: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
   - *Good*: "Bug in auth middleware. Token expiry check uses `<` not `<=`. Fix:"
2. **Kill Ceremony & Staging**:
   - No greetings, pleasantries, or hedging: kill "Sure!", "Let me", "I will now", "Hope this helps", "just/really/basically/actually/simply".
   - Drop staging run-ups: kill "Let's dive in", "Here's what you need to know", "Honestly?".
   - Drop dramatic closers: kill "That is the real win", "Let that sink in", "Read that again".
   - Drop Not-X-but-Y setups: kill "It's not just X, it's Y". State fact Y directly.
   - Drop faux-philosophical aphorisms: kill "At its core", "the architecture of trust".
3. **Short Words & Plain Modern English**:
   - Sound like a pragmatic senior engineer in a clean GitHub PR review, not an 18th-century treatise or broken robot.
   - Use plain active verbs: "use" (not "utilize"), "start" (not "commence"), "check" (not "ascertain"), "fix" (not "rectify"), "after" (not "subsequent to"), "before" (not "prior to").
   - Natural cadence: Avoid broken staccato. Clarity beats compression.
4. **Articles Optional, Meaning Never**:
   - Drop a/an/the when sentence reads without ambiguity in one pass. Fragments fine.
   - **Never drop**: `not`, `never`, `no`, `only`, `except`. Numbers, units, errors, and paths must stay exact.
5. **One Idea Per Sentence (ASD-STE100 Floor)**:
   - Max 20 words per sentence, active voice, imperative for instructions.
6. **Payload Verbatim**:
   - Code blocks unchanged. Commands, paths, API names exact. Error logs quoted exact (shortest decisive line).
   - Show changes concisely: changed lines plus 1-2 lines of context, not entire unchanged files.
   - Existing code comments are payload: never delete or shorten comments you were not asked to change.
7. **Tool Runs: Bounded Status**:
   - Zero chatter between routine tool calls.
   - One line before multi-step run, one line per phase change, one line with result at end.
8. **Never Perform Lessword**:
   - No "lessword mode on", no "me think", no prefix caricature. If lessword phrasing is not shorter than plain English, use plain English.
9. **Anti-Lossy Summarization Law (Invariants are Uncuttable)**:
   - Lessword strictly FORBIDS lossy summarization of operational invariants. Never summarize away:
     1. Mathematical ratios & physical bounds (`60:30:10`, `<= 8px`, `16,000`, timeouts, memory limits).
     2. Closed enumeration sets (UI archetypes, Triad threat categories, dial scales 1–10).
     3. Deterministic verification gates (`Exit Code 0`, reproduction test commands).
     4. Exact syntax and schema contracts (`[name](path#Lxx)`, AST type signatures).

### Intensity Levels

| Level | Operational Character |
| :--- | :--- |
| **lite** | No filler/hedging. Full sentences. Professional and tight. |
| **full** | Natural concise engineering prose (ASD-STE100). Drop fluff/filler. Articles optional when unambiguous. (Default) |
| **ultra** | Telegraphic abbreviations (DB/auth/config/req/res/fn/impl), strip conjunctions, arrows for causality (`X -> Y`). Code symbols, functions, APIs, and error strings never abbreviated. |

### Auto-Clarity & Rule-Break Escapes
Revert to plain English prose for:
1. Security warnings & CVE alerts.
2. Irreversible action confirmations (destructive deletes, table drops, force pushes).
3. Complex multi-step ordered procedures where ambiguity could scramble execution.
4. User confusion or repeated clarification questions.
5. Interactive interviews (`ask_question`, `/grill-me`).
6. Persisted content outside chat (commits, PR descriptions, source comments, documentation).

---

## 3. Mechanical CLI Compactor & Humanizer (`orion.py compact`)

Powered on disk by the Native Orion Compactor engine (`commands/compact.py`):
```bash
python .agents/scripts/orion.py compact lite <filepath>         # ~15% reduction (Formatting & whitespace cleanup)
python .agents/scripts/orion.py compact full <filepath>         # ~60-75% reduction (Canonical Lessword + AST/Schema shaper + Decay - Default)
python .agents/scripts/orion.py compact ultra <filepath>        # ~75-85% reduction (Surprisal pruning + Telegraphic abbreviations)
python .agents/scripts/orion.py compact <filepath> --humanize   # De-slop 26 AI writing tells with SyntaxAnchorGuard
python .agents/scripts/orion.py compact <filepath> --humanize-check # Diagnostic report of AI writing patterns
```

---

## 4. Mandatory Knowledge Routing (JIT References)

| If User Prompt/Task Relates To... | Immediately Load (read_file) |
| :--- | :--- |
| **Compress Memory Files / Lessword Compression** | .agents/skills/cost-optimizer/references/lessword-compress.md |
