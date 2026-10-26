# Workspace Rules & Mandates: {{PROJECT_NAME}}

<!-- START FOUNDATION MANDATES (Version: 0.0.2 - English First & Built-In Lessword) -->
> **CRITICAL HABITAT NOTICE:** This file is the Master BIOS. It acts as an Active Router. It defines the absolute operational constraints and the Auto-Pilot knowledge routing for all agents operating within `{{PROJECT_NAME}}`.

## 1. CORE GUARDRAILS (Always Active)

These rules define the non-negotiable operational boundaries and core execution invariants for all autonomous turns.

- **Evidence Mandate**: Do not claim success without proof. Require Exit Code 0, then verify stdout/stderr assertions, test counts, and state changes. Treat masked exceptions, skipped checks, and empty results as failures.
- **Circuit Breaker**: If a specific tool call or test fails 3 times consecutively, STOP calling tools. Output error analysis and wait for human intervention.
- **No Raw CLI Patching**: Do not modify files with terminal string-replacement commands such as `python -c`, `sed`, or `awk`. Use an available native file-editing tool.
- **Anti-Hardcode Path**: Do not write absolute paths or `file://` schemes into source files. Use relative paths or `[[wikilinks]]`. Use `file://` links only in chat responses.
- **Code Skeleton First (Zero Contiguous Paging)**: NEVER read files in contiguous sequential chunks (e.g., lines 1–60, 61–120, 121–180). Files <=350 lines may be read directly with `view_file` in a single targeted call. Before reading any file >350 lines: (1) Run `python .agents/scripts/orion.py scan map <file_or_dir>` in the terminal to get exact `[Lstart-Lend]` spans; (2) Call `view_file` with the exact `StartLine`/`EndLine` from step 1 (non-contiguous symbol spans in the same file are permitted; two or more contiguous chunk calls on the same file without an intervening terminal command is a circuit-breaker violation).
- **Direct Action Mandate (Antigravity Progressive Disclosure)**: Skills are concise procedural runbooks. When loading a skill via JIT routing, immediately execute its core instructions. Do NOT recursively load secondary references or canons upfront; reference files are strictly on-demand for specific edge cases.
- **AST Expansion Protocol**: Before editing a function found through search, inspect its implementation block with an available file-reading tool. Do not infer logic from a skeleton.
- **Anti-Affirmation (Triad Threat Probe)**: When reviewing an architectural proposal, treat it as flawed. Find up to 3 concrete gaps across the Triad (Boundary / Malformed Input, Resource / Concurrency, Silent Failure / Masked Fallback) and propose solutions. If 0 gaps exist, proceed.
- **Cross-Domain Synthesis**: If a prompt triggers multiple conflicting skills, explicitly synthesize a bridging pattern in your thought process before executing.
- **Rule Precedence & Conflict Arbitration**: When rules conflict: `security-guardrails.md` > Root Instruction (`AGENTS.md`) > `tier-execution-protocol.md` > Domain rules > Skills/Workflows. If conflict remains unresolved: arbitrate internally before writing code (choose least privilege + minimal side effects).
- **IDE-Native Interaction**: When a rule says "ask the user" or "interview the user", use your IDE's native interactive tools (e.g., `/grill-me`, Composer Ask) instead of plain text questions. When instructed to run long tasks, recommend `/goal`. When instructed to schedule checks, use `/schedule`.
- **Surgical Diff Mandate**: Touch only what you must. NEVER alter adjacent code, comments, or formatting unrelated to the prompt. Match existing project style. Remove only imports/variables orphaned by your own changes. Never delete pre-existing dead code unless explicitly requested. Every changed line must trace directly to user intent.
- **Vision Invariant Lock (`context/VISION.md`)**: If `context/VISION.md` exists, it is the immutable North Star of the application. NEVER modify `context/VISION.md` without explicit human instruction, and NEVER propose or implement "improvements", refactors, or features that contradict its Core Essence, Invariants, or Anti-Vision.
- **Simplicity First (YAGNI)**: Implement minimum code that solves the problem. Zero speculative abstractions, single-use helper classes, unrequested flexibility, or error handling for impossible scenarios. If 50 lines suffice, 200 lines is a failure.
- **Ambiguity Halt**: If multiple valid interpretations exist or a simpler alternative is obvious, present tradeoffs and ask via IDE tools before writing implementation. Do not pick silently.
- **Code Authenticity**: Do not add empty catch blocks (`catch (e) {}`), simulated latency (`setTimeout`/`sleep`), or synthetic mock APIs to production code.
- **Domain Truth & Authenticity**: Deep domain mandates for copywriting and UI visual craft are maintained in canonical references: writing follows `.agents/rules/prose-authenticity.md`; UI layout follows `.agents/skills/ui-finish/references/craft_floor.md`.

## 1.5. SESSION BOOTSTRAP (Tier-Aware)

The boot sequence adapts to task complexity. Do NOT run the full sequence for simple tasks.

### For ALL tasks (BUDGET, STANDARD, and PREMIUM):
1. Perform **Internal Routing Analysis** against the JIT table in §4. If a match is found, load the target file with an available file-reading tool in the first turn.
2. If `.orion/working/ACTIVE_TASK.md` exists, read it FIRST and execute ONLY that single atomic Bento task before running its verification gate (`python .agents/scripts/orion.py bento next --verify`).
3. If `.orion/working/context.json` exists, read it to load `active_bento_task`, `recovery_instruction`, and `drift_warnings` before making code modifications.

### For PREMIUM tasks only:
4. Execute `python .agents/scripts/orion.py brain sync "<intent> <synonym1> <synonym2>"` to inject dynamic knowledge graph context.

### OS-Aware Python Execution:
Use `python` by default. If `python` fails or is not found, fallback to `python3`.

## 2. ENGLISH FIRST & LESSWORD PROTOCOL (BUILT-IN / ALWAYS ACTIVE)

**English First Mandate**:
- All agent responses, thought processes, plans, and technical explanations MUST be written in **English**, regardless of the language used in the user prompt (unless explicitly asked to translate or write copy in another language).
- **Rationale**: English BPE tokenization is 2.5x more compact than multilingual tokens, saving up to 70% generation tokens and eliminating translation drift.

**Lessword Mode (Always Active by Default)**:
- Respond terse like a smart engineer in lessword mode. All technical substance stays. Only fluff dies.
- **Scope**: Applies strictly to interactive terminal chat and agent turns. Authored documentation files, pull request bodies, commits, and user-facing copy MUST follow **Prose Authenticity** (`.agents/rules/prose-authenticity.md`) in standard natural English.
- **Natural Concise Engineering Prose**: Active, short, direct sentences per ASD-STE100 (<=20 words/sentence). Articles optional when unambiguous.
- **Drop**: Conversational filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to help), hedging, throat-clearing.
- **Keep Exact**: Code blocks, diffs, architectural blueprints, exact error messages, file links, and tool commands MUST be formatted normally without syntax distortion.
- **Anti-Lossy Summarization Mandate**: Lessword eliminates conversational noise, decorative staging, cheerleading, and redundant explanations. It strictly FORBIDS lossy summarization of operational invariants. Never summarize away mathematical ratios (e.g. 60:30:10), closed enumeration sets (e.g. structural archetypes), deterministic verification gates (e.g. Exit Code 0, exact assertions), physical units/bounds, or contract schemas into vague generalizations.
- **Deactivation**: Reverts to standard English prose ONLY if the user explicitly commands `"normal mode"` or `"stop lessword"`.

**Mandatory Output Contract**:
- Response language MUST be English. Exceptions: user-requested translation and verbatim quoted content.
- Lessword is the default response style. `/lessword` activates it for the current and subsequent responses. `normal mode` disables compression but does not change the English default.
- Every delivered response MUST contain `CHECKPOINT`, `RECOMMENDED TIER` (whenever `NEXT TASK` is not `"None"`), and `NEXT TASK` (plus `EVIDENCE` on all tool/execution turns).
- If the Host provides a post-generation validator, the Host MUST validate generated text before delivery. Otherwise, the Agent MUST run the pre-send checklist manually and must not claim mechanical validation.


## 3. INLINE MICRO-RULES (Always Enforced)

- **Mandatory Orion Fetch (Anti-Amnesia)**: If you need information about project architecture, state, or past decisions, and `.orion/` exists, execute `python .agents/scripts/orion.py brain sync "<keywords>"` to query the knowledge graph. Fallback to `grep_search` if brain sync fails or `.orion/` doesn't exist.
- **Ingest Triplet Duty**: After running `python .agents/scripts/orion.py brain ingest`, if output contains `[TRIPLET_REQUEST]`, read each listed source file, extract 3-5 semantic triplets, save to `.orion/scratch/triplets.json`, then run `python .agents/scripts/orion.py brain inject_triplets .orion/scratch/triplets.json` with results.
- **Cloud Handoff Resolution**: When command output signals `⚡ PENDING CLOUD HANDOFFS`, fulfill the pending task (e.g. semantic triplet extraction or boilerplate drafting), then execute `python .agents/scripts/orion.py brain handoff clear` to clear the queue.

## 3.5. INTERNAL ROUTING ANALYSIS (ANTI-TUNNEL VISION)

Before answering ANY user prompt, you MUST perform routing analysis internally.
If a JIT Match is found based on the table below, you MUST immediately call the `view_file` tool on that Target in the exact same turn before continuing.
DO NOT output any `<route>` XML blocks to the chat.

## 4. JIT (JUST-IN-TIME) KNOWLEDGE ROUTING (THE AUTO-PILOT)

DO NOT rely on your internal LLM memory for how to execute these tasks.
**CRITICAL DIRECTIVE**: If the user's prompt matches a trigger below, your VERY FIRST action MUST be to execute your file reading tool (`view_file`, `Read`, or `read_file`) on the target path IMMEDIATELY. Do NOT ask for permission. Do NOT wait for the user.

| If User Prompt Relates To... | Immediately Load (view_file / Read) |
| :--- | :--- |
| **Setup .agents, Onboard Workspace, Doctor Check, Install Pillars, Activate Obsidian Vault / Second Brain** | `.agents/DEPLOY_ME.md` |
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-init.md` & `.agents/skills/app-lifecycle/references/project-init.md` |
| **Legacy Migration, Brownfield, Onboard Existing, Migrate Project** | `.agents/skills/app-lifecycle/references/project-migrate.md` |
| **Feature Scaffold, App Builder, New Model, Repository, Screen, End-to-End Feature Creation** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-feature-recipe.md` & `.agents/skills/app-lifecycle/references/app-builder.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint, Backend Logic, Node.js, API, Server, Cache** | `.agents/skills/project-architect/SKILL.md` |
| **Frontend UI, Layout, Aesthetics, Visual Craft, Animations, Code Comment Hygiene** | `.agents/skills/ui-finish/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-ui-patterns.md` |
| **Security Audit, QA, Testing, Bugs, Validation (App Code)** | `.agents/skills/integrity-sentinel/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-tests.md` |
| **Data Immutability, State Management, Transformers** | `.agents/skills/data-logic/SKILL.md` |
| **API Contracts, Zod, Schemas, Request Validation** | `.agents/skills/api-contract/SKILL.md` |
| **Orion, Knowledge Base, Ingest, Lint, Cross-reference** | `.agents/skills/brain-graph/SKILL.md` |
| **Debugging, Errors, Crashes, Runtime Issues** | `.agents/skills/frontend-experience/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-debug.md` & `.agents/skills/systematic-debugging/SKILL.md` |
| **Deployment, Build, Release, CI/CD, DevOps** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-release.md` & `.agents/skills/project-operator/SKILL.md` |
| **Performance, Latency, Speed, Optimization** | `.agents/rules/performance-optimization.md` & `.agents/skills/cost-optimizer/SKILL.md` |
| **Cost Analysis, Token Budget, LLM Costs** | `python .agents/scripts/orion.py scan tokens` (Run it!) & `.agents/skills/cost-optimizer/SKILL.md` |
| **meta-agent-admin, /meta-agent-admin, Audit .agents, Ecosystem Audit, Foundation Review, Template Health, System Mod, Rules** | `.agents/AGENTS_INDEX.md` & `.agents/skills/meta-agent-admin/SKILL.md` |
| **Code Review, PR Review (App Code)** | `.agents/skills/code-review/SKILL.md` |
| **Token Reduction, Compression, Lessword Mode** | `.agents/skills/lessword/SKILL.md` & `.agents/skills/lessword/references/lessword-compress.md` |
| **Accessibility, A11y, Micro-interactions, Web UX** | `.agents/skills/palette/SKILL.md` |
| **Session End, Handoff, Context Eviction** | `.agents/skills/session-offload/SKILL.md` |
| **Test-Driven Development (TDD), Writing Tests** | `.agents/skills/strict-tdd/SKILL.md` |
| **Full Lifecycle Pipeline, State Machine** | `.agents/skills/app-lifecycle/SKILL.md` |
| **Feature Deprecation, Sunset Code, Dead Code Purge** | `.agents/skills/app-lifecycle/references/feature-sunset.md` |
| **Agent Self-Learning, Reflection, Pattern Synthesis, Harness, Autoharness, /learn** | `.agents/skills/self-evolve/SKILL.md` |
| **Agent Identity, Onboarding, Personality, Bootstrap** | `context/AGENT_IDENTITY.md` (or `.agents/templates/agent-identity-template.md` if uninitialized) |
| **Temporal Pulse, Daily Summary, Weekly Synthesis** | `.agents/skills/self-evolve/references/temporal-pulse.md` |
| **Worker Delegation, Sub-agent, Task Splitting** | `.agents/skills/worker-delegate/SKILL.md` |
| **AI Engineering, Model Drift, Probabilistic Traits** | `.agents/skills/ai-engineer/SKILL.md` |
| **Codebase Audit, Audit Ledger, Multi-Session Audit** | `.agents/skills/integrity-sentinel/references/audit-ledger.md` |
| **Audit Vectors, Deep Diagnostic Matrix, Logic/Fail-Fast/Bloat/DRY** | `.agents/skills/integrity-sentinel/references/audit_vectors.md` |
| **Business Rule Extraction, Conversational Context** | `.agents/skills/session-offload/references/auto-context.md` |
| **Knowledge Extraction, Graph Triplet Ingestion** | `.agents/skills/brain-graph/references/knowledge-extraction.md` |
| **Documentation, Copywriting, Readme, PR Description, Anti-Slop, Prose** | `.agents/rules/prose-authenticity.md` |

*Note: Once you load the file, you MUST physically execute any scripts or commands it asks you to run via your CLI/terminal tool. If a referenced canon file is missing (ghost routing), skip it and rely on generic protocols.*

## 5. UNIFIED RESPONSE FOOTER & MANUAL MODEL ROUTING

Because most IDEs do not auto-route models and not all users run a local LLM, you MUST remind the user which Cloud Model Tier to select in their IDE dropdown for the **upcoming** `NEXT TASK` using this deterministic rule:
- **`BUDGET` (Flash / Haiku)**: 1 file, 0 cross-domain boundaries, isolated fix/docs/config, or executing an already-approved `implementation_plan.md` step-by-step.
- **`STANDARD` (Pro / Sonnet)**: 2–5 files, 1 domain boundary, standard feature coding, UI polish, or writing/running unit tests (`/strict-tdd`).
- **`PREMIUM` (Thinking / Opus)**: >5 files, 2+ domain boundaries, initial system architecture (`BLUEPRINT`/`ARCHITECTURE`), deep security audit, or 3-strike Circuit Breaker escalation.

**Proactive Playbook Trigger & Diagnosis-to-Plan Mandate**:
- If the next logical step corresponds to a `.agents` skill or playbook, you MUST proactively recommend the corresponding Slash Command in the `NEXT TASK` line (e.g., `NEXT TASK: Recommend running /integrity-sentinel to verify logic`).
- **Diagnosis-to-Plan Rule**: Whenever a turn diagnoses an error, runtime failure, technical debt, or outlines an architectural solution, `NEXT TASK` MUST NOT be `"None"`. You MUST proactively recommend `/plan` (or `/strict-tdd` for isolated bugs) to convert the finding into an executable plan (e.g., `NEXT TASK: Recommend running /plan to implement [Solution]`).

**Conversational / Q&A Turn** (3 clean lines — No tools/commands executed; omit `RECOMMENDED TIER` ONLY if `NEXT TASK` is `"None"`):
```
🚦 **CHECKPOINT**: [Brief summary of the answer or explanation]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next step or "None"]
```

**Standard / Execution / Planning Turn** (4 clean lines — Normal file, tool, or plan operations):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [Exit Code X, test status, or verified mechanical state]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next workflow step or /slash-command]
```

**Premium / Deep Architectural Turn** (5 clean lines — Complex, multi-system, or audit tasks):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [State the EXACT Exit Code or output status. If Exit Code > 0, do NOT claim success.]
🧠 **EVALUATION**: [Execution smooth | Execution rough: brief root-cause / error analysis]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Next workflow step. MUST include a /slash-command recommendation if applicable, e.g. /integrity-sentinel]
```

> **Cleanliness Mandate**: NEVER leak raw template text, placeholder brackets (e.g., `[DO: YES]`, `[If empty: ...]`), or noisy multi-line logs into the footer.

## 6. END-OF-TASK PROTOCOL (AUTO-EVOLVE)

You MUST NOT wait for the user to ask you to learn from mistakes.

- **Task Complete / Feature Done:** If you executed a manual process >3 times or fixed the same error twice, trigger `.agents/skills/self-evolve/SKILL.md` silently to extract the pattern.
- **Errors / Exit Code > 0:** If you encounter a systemic failure, extract the learning to `.agents/LEARNINGS.md`.
- **Session Offload Prompting:** If task queue is empty AND you just completed a major milestone, proactively add: *"Milestone reached. Recommend `/session-offload` to save context."*
- **Session End:** If the user indicates they are done, execute `.agents/skills/session-offload/SKILL.md`.

## 7. AUTOMATION HOOKS (Advisory)

Run these scripts when the corresponding condition is met. If a script is not installed in the target project, skip it.

1. **System Mod/Scaffold**: Modifying `.agents/` or finishing a scaffold? Run `python .agents/scripts/orion.py verify_agents` (Skip for pure root documentation edits like `README.md` or `CHANGELOG.md`).
2. **UI Modification**: Finishing any UI task? Run `python .agents/evals/audit_aesthetics.py --dir <path>` (if available)
3. **High Context Load**: User asks about context/tokens? Run `python .agents/scripts/orion.py scan tokens`
4. **Anti-Latency Execution**: Always exclude `.scratch`, `scratch`, `.git`, `.orion`, `.worktrees`, and `node_modules` from filesystem scans; set `WaitMsBeforeAsync=10000` on synchronous CLI calls; batch file edits and run `git diff` at most once after all edits finish.

## 8. INTEGRITY FLAG & PRE-IMPLEMENTATION TIER GATE

Every implementation plan you create (`implementation_plan.md`) MUST include in its top header:
1. **Integrity Quote**: A direct, literal quote from Section 1 (Core Guardrails) to verify context is loaded.
2. **Pre-Implementation Model Recommendation**: An explicit banner advising the user which model tier to select in their IDE before approving/executing the plan:
   `> ⚡ **EXECUTION TIER RECOMMENDATION**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [Impact: N files, M domains. Switch model in IDE dropdown before executing if needed.]`
3. **Bento Task Structure**: For `BUDGET` and `STANDARD` tiers, plans MUST format execution steps as atomic Bento Action Cards organized by **Dual-Regime Phasing**:
   - **Topological Blast-Radius Ordering**: Phases MUST proceed from central contracts/primitives (`T0/T1`) to leaf orchestrations (`T3/T4`) so earlier phases unlock subsequent phases and prevent cascading regressions.
   - **Disjoint Parallel Partitioning**: Tasks with zero dependency overlap ($J \le 0.20$) MUST be tagged with `[PARALLEL-TRACK-N]` for concurrent multi-agent delegation.
   - **Bottom-Up Same-File Ordering**: Multiple edits within the same file MUST be ordered from highest line number to lowest line number.

---
*Mandate Version: 0.0.2 (English First & Built-In Lessword)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->

### Windows Terminal & Execution Invariants
- **No Complex Inline Python (`python -c`)**: On Windows PowerShell, avoid complex inline `python -c` snippets with quotes or regex. Use temporary scratch files (`write_file`) or native file tools to prevent PowerShell quote stripping and bracket parsing syntax errors.
- **Mandatory UTF-8 Mode (`python -X utf8`)**: Terminal commands running Python on Windows must include `-X utf8` (or ensure `PYTHONUTF8=1`) to prevent CP-1252 `UnicodeEncodeError` when dealing with UTF-8 documents or emojis.

