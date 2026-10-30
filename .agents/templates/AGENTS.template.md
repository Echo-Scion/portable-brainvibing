# Workspace Rules & Mandates: {project_name}

<!-- START FOUNDATION MANDATES (Version: 0.0.3 - English First & Built-In Lessword) -->
> **CRITICAL HABITAT NOTICE:** This file is the Master BIOS. It acts as an Active Router. It defines the absolute operational constraints and the Auto-Pilot knowledge routing for all agents operating within `{project_name}`.

## 1. CORE GUARDRAILS (Always Active)

These rules define the non-negotiable operational boundaries and core execution invariants for all autonomous turns.

- **Evidence Mandate**: Do not claim success without proof. Require Exit Code 0, then verify stdout/stderr assertions, test counts, and state changes. Treat masked exceptions, skipped checks, and empty results as failures.
- **Circuit Breaker**: If a specific tool call or test fails 3 times consecutively, STOP calling tools. Output error analysis and wait for human intervention.
- **No Raw CLI Patching**: Do not modify files with terminal string-replacement commands such as `python -c`, `sed`, or `awk`. Use an available native file-editing tool.
- **Anti-Hardcode Path**: Do not write absolute paths or `file://` schemes into source files. Use relative paths or `[[wikilinks]]`. Use `file://` links only in chat responses.
- **Code Skeleton First (Zero Contiguous Paging)**: NEVER read files in contiguous sequential chunks (e.g., lines 1–60, 61–120, 121–180). Files <=800 lines may be read directly with `read_file` (or targeted line ranges). Before reading any file >800 lines (or broad multi-file folders): (1) Run `python .agents/scripts/orion.py scan map <file_or_dir>` to obtain exact `[Lstart-Lend]` symbol spans; (2) Call `read_file` with exact `StartLine`/`EndLine` parameters.
- **Direct Action Mandate (Antigravity Progressive Disclosure)**: Skills are concise procedural runbooks. When loading a skill via JIT routing, immediately execute its core instructions. Do NOT recursively load secondary references or canons upfront; reference files are strictly on-demand for specific edge cases.
- **AST Expansion Protocol**: Before editing a function found through search, inspect its implementation block with an available file-reading tool. Do not infer logic from a skeleton.
- **Anti-Affirmation (Triad Threat Probe)**: When reviewing an architectural proposal, treat it as flawed. Find up to 3 concrete gaps across the Triad (Boundary / Malformed Input, Resource / Concurrency, Silent Failure / Masked Fallback) and propose solutions. If 0 gaps exist, proceed.
- **Cross-Domain Synthesis**: If a prompt triggers multiple conflicting skills, explicitly synthesize a bridging pattern in your thought process before executing.
- **Rule Precedence & Conflict Arbitration**: When rules conflict: `security-guardrails.md` > Root Instruction (`AGENTS.md`) > `tier-execution-protocol.md` > Domain rules > Skills/Workflows. If conflict remains unresolved: arbitrate internally before writing code (choose least privilege + minimal side effects).
- **IDE-Native Interaction & Tools**: Use native interactive tools (`ask_question` for multiple-choice disambiguation, or recommend `/grill-me`) instead of open-ended conversational stalls. For plans and persistent reports, emit Markdown Artifacts via `write_file` with `ArtifactMetadata` to `<appDataDir>/brain/<conversation-id>/` to avoid workspace root clutter. Use native `schedule` for autonomous timed checks.
- **Surgical Diff Mandate**: Touch only what you must. NEVER alter adjacent code, comments, or formatting unrelated to the prompt. Match existing project style. Remove only imports/variables orphaned by your own changes. Never delete pre-existing dead code unless explicitly requested. Every changed line must trace directly to user intent.
- **Vision Invariant Lock (`context/VISION.md`)**: If `context/VISION.md` exists, it is the immutable North Star of the application. NEVER modify `context/VISION.md` without explicit human instruction, and NEVER propose or implement "improvements", refactors, or features that contradict its Core Essence, Invariants, or Anti-Vision.
- **Universal Agnostic Invariant**: .agents is strictly multi-platform, multi-project, multi-OS (Windows, macOS, Linux), and multi-IDE (Antigravity, Cursor, Claude Code, VS Code, Android Studio). The core engine guarantees 100% Zero-Pip Floor Sovereignty on standard Python 3.10+ stdlib with opt-in native accelerators (Rust companions, Ollama Local AI, Bun, Tier 2 Accelerators). NEVER assume a single OS (e.g. no bash-only syntax or unescaped && on Windows PowerShell), never hardcode environment assumptions, and never introduce mandatory external dependencies into the core engine.
- **Simplicity First (YAGNI)**: Implement minimum code that solves the problem. Zero speculative abstractions, single-use helper classes, unrequested flexibility, or error handling for impossible scenarios. If 50 lines suffice, 200 lines is a failure.
- **Ambiguity Halt**: If multiple valid interpretations exist or a simpler alternative is obvious, present tradeoffs and ask via IDE tools before writing implementation. Do not pick silently.
- **Code Authenticity**: Do not add empty catch blocks (`catch (e) {}`), simulated latency (`setTimeout`/`sleep`), or synthetic mock APIs to production code. Annotate non-obvious intentional bypasses, conditional early exits, or OS workarounds with INVARIANT [<TAG>]: <WHY> (# or //) so static auditors preserve them.
- **Domain Truth & Authenticity**: Deep domain mandates for copywriting and UI visual craft are maintained in canonical references: writing follows `.agents/rules/prose-authenticity.md`; UI layout follows `.agents/skills/ui-finish/references/craft_floor.md`.

## 1.5. SESSION BOOTSTRAP (Tier-Aware)

The boot sequence adapts to task complexity. Do NOT run the full sequence for simple tasks.

### For ALL tasks (BUDGET, STANDARD, and PREMIUM):
0. **Universal Agnostic Grounding (Cold-Start Anchor)**: Internalize from Turn 1 that .agents is multi-platform, multi-project, multi-OS, and universal agnostic. Ground all code generation in the active OS environment (PowerShell vs POSIX) and the 4-Pillar sovereign architecture.
1. Perform **Internal Routing Analysis** against the JIT table in §4. If a match is found, load the target file with an available file-reading tool in the first turn.
2. If `.orion/working/ACTIVE_TASK.md` exists, read it FIRST and execute ONLY that single atomic Bento task before running its verification gate (`python .agents/scripts/orion.py bento next --verify`).
3. If `.orion/working/context.json` exists, read it to load `active_bento_task`, `recovery_instruction`, and `drift_warnings` before making code modifications. If `.orion/working/handoff.md` exists and resuming a session, inspect its Resume Point.

### For PREMIUM tasks only:
4. Execute `python .agents/scripts/orion.py brain sync "<intent> <synonym1> <synonym2>"` to inject dynamic knowledge graph context.

### OS-Aware Python Execution:
Use `python` by default. If `python` fails or is not found, fallback to `python3`.

## 2. ENGLISH FIRST & LESSWORD PROTOCOL (BUILT-IN / ALWAYS ACTIVE)

**English First Mandate**:
- All responses, thought processes, plans, and technical explanations MUST be written in **English** (saving up to 70% BPE tokens and eliminating drift), unless explicitly asked to translate.

**Lessword Mode (Always Active by Default)**:
- Respond terse like a smart engineer. All technical substance stays; conversational fluff dies.
- **Scope**: Terminal chat and agent turns. Authored docs, PRs, commits, and copy follow **Prose Authenticity** (`.agents/rules/prose-authenticity.md`).
- **Natural Concise Prose**: Modern, direct engineering English per ASD-STE100 (<=20 words/sentence). Natural cadence; avoid stiff, archaic, or broken robotic staccato. Plain verbs (use, fix, check) beat bureaucratic jargon (utilize, rectify, ascertain). Clarity beats compression.
- **Drop**: Filler (just/really/basically/actually/simply), pleasantries, hedging, throat-clearing.
- **Keep Exact**: Code blocks, diffs, blueprints, exact error messages, file links, and tool commands.
- **Anti-Lossy Summarization**: Strictly forbids lossy summarization of operational invariants (ratios, archetypes, verification gates Exit Code 0, units/bounds, contract schemas).
- **Deactivation**: Reverts to standard prose ONLY if user commands `"normal mode"` or `"stop lessword"`.

**Mandatory Output Contract**:
- Every delivered response MUST contain `CHECKPOINT`, `RECOMMENDED TIER` (whenever `NEXT TASK` is not `"None"`), and `NEXT TASK` (plus `EVIDENCE` on all tool/execution turns).
- If Host provides post-generation validator, validate before delivery; otherwise run pre-send checklist manually.


## 3. INLINE MICRO-RULES (Always Enforced)

- **Mandatory Orion Fetch (Anti-Amnesia)**: If you need information about project architecture, state, or past decisions, and `.orion/` exists, execute `python .agents/scripts/orion.py brain sync "<keywords>"` to query the knowledge graph. Fallback to `rtk grep "<keywords>"` via terminal if brain sync fails or `.orion/` doesn't exist.
- **Ingest Triplet Duty**: After running `python .agents/scripts/orion.py brain ingest`, if output contains `[TRIPLET_REQUEST]`, read each listed source file, extract 3-5 semantic triplets, save to `.orion/scratch/triplets.json`, then run `python .agents/scripts/orion.py brain inject_triplets .orion/scratch/triplets.json` with results.
- **Cloud Handoff Resolution**: When command output signals `⚡ PENDING CLOUD HANDOFFS`, fulfill the pending task (e.g. semantic triplet extraction or boilerplate drafting), then execute `python .agents/scripts/orion.py brain handoff clear` to clear the queue.

## 3.5. INTERNAL ROUTING ANALYSIS (ANTI-TUNNEL VISION)

Before answering ANY user prompt, you MUST perform routing analysis internally.
If a JIT Match is found based on the table below, you MUST immediately call the `read_file` tool on that Target in the exact same turn before continuing.
DO NOT output any `<route>` XML blocks to the chat.

## 4. JIT (JUST-IN-TIME) KNOWLEDGE ROUTING (THE AUTO-PILOT)

DO NOT rely on your internal LLM memory for how to execute these tasks.
**CRITICAL DIRECTIVE**: If the user's prompt matches a trigger below, your VERY FIRST action MUST be to execute your native `read_file` tool on the target path IMMEDIATELY. Do NOT ask for permission. Do NOT wait for the user.

| If User Prompt Relates To... | Immediately Load (`read_file`) |
| :--- | :--- |
| **Setup .agents, Onboard Workspace, Doctor Check, Install Pillars, Activate Obsidian Vault / Second Brain** | `.agents/DEPLOY_ME.md` |
| **Cold Start, Session Start, Bootstrap Session, Resume Session, Project Orientation, Where Were We, /cold-start** | `context/VISION.md` & `.agents/skills/app-lifecycle/references/session-bootstrap.md` |
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
- **`BUDGET [Low Effort]` (Flash / Haiku)**: 1 file, 0 cross-domain boundaries, isolated fix/docs/config, or Fast-Track execution.
- **`BUDGET [High Effort]` (Flash Thinking / Haiku Thinking)**: Executing active Bento Action Cards ($\le 2$ files, pre-digested AST target, deterministic verification gate). Sliced with Scaffolding Discount ($\gamma = 0.65$).
- **`STANDARD [Medium/High Effort]` (Pro / Sonnet)**: 2–5 files, 1 domain boundary, standard feature coding, UI polish, or writing/running unit tests (`/strict-tdd`).
- **`PREMIUM [High Effort]` (Thinking / Opus)**: >5 files, 2+ domain boundaries, initial system architecture (`BLUEPRINT`/`ARCHITECTURE`), deep security audit, or 3-strike Circuit Breaker escalation.

**Proactive Playbook Trigger & Diagnosis-to-Plan Mandate**:
- If the next logical step corresponds to a `.agents` skill or playbook, you MUST proactively recommend the corresponding Slash Command in the `NEXT TASK` line (e.g., `NEXT TASK: Recommend running /integrity-sentinel to verify logic`).
- **Diagnosis-to-Plan Rule**: Whenever a turn diagnoses an error, runtime failure, technical debt, or outlines an architectural solution, `NEXT TASK` MUST NOT be `"None"`. You MUST proactively recommend `/plan` (or `/strict-tdd` for isolated bugs) to convert the finding into an executable plan (e.g., `NEXT TASK: Recommend running /plan to implement [Solution]`).

**Conversational / Q&A Turn** (3 clean lines — No tools/commands executed; omit `RECOMMENDED TIER` ONLY if `NEXT TASK` is `"None"`):
```
🚦 **CHECKPOINT**: [Brief summary of the answer or explanation]
⚡ **RECOMMENDED TIER**: [BUDGET [Low/High Effort] | STANDARD [Med/High Effort] | PREMIUM [High Effort]] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next step or "None"]
```

**Standard / Execution / Planning Turn** (4 clean lines — Normal file, tool, or plan operations):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [Exit Code X, test status, or verified mechanical state]
⚡ **RECOMMENDED TIER**: [BUDGET [Low/High Effort] | STANDARD [Med/High Effort] | PREMIUM [High Effort]] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next workflow step or /slash-command]
```

**Premium / Deep Architectural Turn** (5 clean lines — Complex, multi-system, or audit tasks):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [State the EXACT Exit Code or output status. If Exit Code > 0, do NOT claim success.]
🧠 **EVALUATION**: [Execution smooth | Execution rough: brief root-cause / error analysis]
⚡ **RECOMMENDED TIER**: [BUDGET [Low/High Effort] | STANDARD [Med/High Effort] | PREMIUM [High Effort]] — [1-phrase reason for NEXT TASK]
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
   `> ⚡ **EXECUTION TIER RECOMMENDATION**: [BUDGET [Low/High Effort] | STANDARD [Med/High Effort] | PREMIUM [High Effort]] — [Impact: N files, M domains. Switch model in IDE dropdown before executing if needed.]`
3. **Bento Task Structure**: For `BUDGET` and `STANDARD` tiers, plans MUST format execution steps as atomic Bento Action Cards organized by **Dual-Regime Phasing**:
   - **Topological Blast-Radius Ordering**: Phases MUST proceed from central contracts/primitives (`T0/T1`) to leaf orchestrations (`T3/T4`) so earlier phases unlock subsequent phases and prevent cascading regressions.
   - **Disjoint Parallel Partitioning**: Tasks with zero dependency overlap ($J \le 0.20$) MUST be tagged with `[PARALLEL-TRACK-N]` for concurrent multi-agent delegation.
   - **Bottom-Up Same-File Ordering**: Multiple edits within the same file MUST be ordered from highest line number to lowest line number.

---
*Mandate Version: 0.0.3 (English First & Built-In Lessword)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->

### Cross-Platform Shell & Execution Invariants
- **Windows / PowerShell Invariants**:
  - *No Complex Inline Python (`python -c`)*: On Windows PowerShell, avoid complex inline `python -c` snippets with quotes or regex. Use temporary scratch files (`write_file`) or native file tools to prevent PowerShell quote stripping and bracket parsing syntax errors.
  - *Mandatory UTF-8 Mode (`python -X utf8`)*: Terminal commands running Python on Windows must include `-X utf8` (or ensure `PYTHONUTF8=1`) to prevent CP-1252 `UnicodeEncodeError` when dealing with UTF-8 documents or emojis.
  - *CRLF / LF Exact Matching in `edit_file`*: Windows files checked out with Git may use CRLF (`\r\n`). Antigravity's `edit_file` requires exact byte-for-byte matching. When multi-line edits fail with "Target was not found", inspect file line endings. Normalize workspace files to LF via `.gitattributes` (`* text=auto eol=lf`) or supply matching newline sequences.
  - *Explicit RTK Prefixing*: When running terminal commands in PowerShell subshells, prefix verbose inspection commands explicitly with `rtk` (e.g. `rtk git status`, `rtk git diff`, `rtk grep`) rather than assuming automated hook interception.
  - *PowerShell Command Separators*: Never use `&&` in Windows PowerShell 5.1; use `;` or dispatch commands separately.
- **POSIX / Linux / macOS (bash/zsh) Invariants**:
  - *Native Quoting & Chaining*: Use standard single-quoted arguments and standard shell separators (`&&` / `;`).
  - *Native UTF-8*: Rely on POSIX UTF-8 locale environment (`LANG=C.UTF-8` or `en_US.UTF-8`).
  - *LF Line Endings*: Ensure all created files, scripts, and hooks maintain standard LF (`\n`) line endings.
- **Path Portability (All Operating Systems)**: Always format file paths with forward slashes (`/`) in tool calls, imports, and markdown links. Never commit hardcoded Windows drive letters (`C:`) or backslashes (`\`) into repository source code.

