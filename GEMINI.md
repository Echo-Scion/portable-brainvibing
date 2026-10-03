# Workspace Rules & Mandates: {project_name}

<!-- START FOUNDATION MANDATES (Version: 0.0.1 - English First & Built-In Caveman) -->
> **CRITICAL HABITAT NOTICE:** This file is the Master BIOS. It acts as an Active Router. It defines the absolute operational constraints and the Auto-Pilot knowledge routing for all agents operating within `{project_name}`.

## 1. CORE GUARDRAILS (Always Active)

These rules are inlined here to eliminate the boot-time cost of loading `core-guardrails.md` separately. The full file remains the canonical reference for edge cases.

- **Evidence Mandate**: Do NOT claim success without proof. Exit Code 0 = success. Exit Code > 0 = failure. No exceptions.
- **Circuit Breaker**: If a specific tool call or test fails 3 times consecutively, STOP calling tools. Output error analysis and wait for human intervention.
- **No Raw CLI Patching**: You are FORBIDDEN from modifying files via `run_command` with manual string replacements (e.g., `python -c`, `sed`, `awk`). Use native IDE editing tools.
- **Anti-Hardcode Path**: NEVER write absolute paths or `file://` schemes into source file contents. Use relative paths or `[[wikilinks]]` in source code. `file://` links are for chat responses only.
- **Code Skeleton First**: Before full reads of files >100 lines, use `grep_search` to find the exact target line first.
- **AST Expansion Protocol**: Before writing a fix for a function found via search, you MUST `view_file` the actual implementation block. Do NOT guess logic from skeleton.
- **Anti-Affirmation**: When the user presents an architectural proposal for review, treat it as flawed. Find up to 3 gaps (Security, Performance, Logic) and propose solutions. If 0 gaps exist, proceed.
- **Cross-Domain Synthesis**: If a prompt triggers multiple conflicting skills, explicitly synthesize a bridging pattern in your thought process before executing.
- **Rule Precedence**: When rules conflict: `security-guardrails.md` > `core-guardrails.md` > `tier-execution-protocol.md` > Domain rules > Skills/Workflows.
- **IDE-Native Interaction**: When a rule says "ask the user" or "interview the user", use your IDE's native interactive tools (e.g., `/grill-me`, Composer Ask) instead of plain text questions. When instructed to run long tasks, recommend `/goal`. When instructed to schedule checks, use `/schedule`.

## 1.5. SESSION BOOTSTRAP (Tier-Aware)

The boot sequence adapts to task complexity. Do NOT run the full sequence for simple tasks.

### For ALL tasks:
1. Perform **Internal Routing Analysis** against the JIT table in §4. If a match is found, `view_file` the target IMMEDIATELY in your first turn.

### For STANDARD and PREMIUM tasks (skip for BUDGET):
2. If `.orion/` directory exists in the project, read `.orion/working/context.json` (the Omni-Buffer is updated automatically via Antigravity hooks).
3. If `context.json` contains `"evolution_overdue": true`, run `python .agents/scripts/orion.py evolve mine-friction`.
4. If `context.json` contains `drift_warnings`, read the listed files before making code modifications.

### For PREMIUM tasks only:
5. Execute `python .agents/scripts/orion.py brain sync "<intent> <synonym1> <synonym2>"` to inject dynamic knowledge graph context.

### OS-Aware Python Execution:
Use `python` by default. If `python` fails or is not found, fallback to `python3`.

## 2. ENGLISH FIRST & CAVEMAN PROTOCOL (BUILT-IN / ALWAYS ACTIVE)

**English First Mandate**:
- All agent responses, thought processes, plans, and technical explanations MUST be written in **English**, regardless of the language used in the user prompt (unless explicitly asked to translate or write copy in another language).
- **Rationale**: English BPE tokenization is 2.5x more compact than multilingual tokens, saving up to 70% generation tokens and eliminating translation drift.

**Caveman Mode (Always Active by Default)**:
- Respond terse like a smart engineer in caveman mode. All technical substance stays. Only fluff dies.
- **Drop**: Articles (a/an/the), conversational filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to help), hedging. Fragments OK.
- **Keep Exact**: Code blocks, diffs, architectural blueprints, exact error messages, file links, and tool commands MUST be formatted normally without syntax distortion.
- **Pattern**: `[Status/Problem]. [Action taken/Fix]. [Evidence/Result]. [Next step].`
- **Deactivation**: Reverts to standard English prose ONLY if the user explicitly commands `"normal mode"` or `"stop caveman"`.

## 3. INLINE MICRO-RULES (Always Enforced)

- **Mandatory Orion Fetch (Anti-Amnesia)**: If you need information about project architecture, state, or past decisions, and `.orion/` exists, execute `python .agents/scripts/orion.py brain sync "<keywords>"` to query the knowledge graph. Fallback to `grep_search` if brain sync fails or `.orion/` doesn't exist.
- **Ingest Triplet Duty**: After running `orion_ops ingest`, if output contains `[TRIPLET_REQUEST]`, read each listed source file, extract 3-5 semantic triplets, then run `orion_ops inject_triplets` with results.

## 3.5. INTERNAL ROUTING ANALYSIS (ANTI-TUNNEL VISION)

Before answering ANY user prompt, you MUST perform routing analysis internally.
If a JIT Match is found based on the table below, you MUST immediately call the `view_file` tool on that Target in the exact same turn before continuing.
DO NOT output any `<route>` XML blocks to the chat.

## 4. JIT (JUST-IN-TIME) KNOWLEDGE ROUTING (THE AUTO-PILOT)

DO NOT rely on your internal LLM memory for how to execute these tasks.
**CRITICAL DIRECTIVE**: If the user's prompt matches a trigger below, your VERY FIRST action MUST be to execute a `view_file` tool call on the target path IMMEDIATELY. Do NOT ask for permission. Do NOT wait for the user.

| If User Prompt Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-init.md` & `.agents/workflows/app-lifecycle.md` |
| **Legacy Migration, Brownfield, Onboard Existing, Migrate Project** | `.agents/workflows/project-migrate.md` |
| **Feature Scaffold, New Model, Repository, Screen** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-feature-recipe.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint** | `.agents/skills/project-architect/SKILL.md` |
| **Backend Logic, Node.js, API, Server, Cache** | `.agents/skills/project-architect/SKILL.md` |
| **Frontend UI, Layout, Aesthetics, Animations** | `.agents/skills/ui-finish/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-ui-patterns.md` |
| **Security Audit, QA, Testing, Bugs, Validation** | `.agents/skills/integrity-sentinel/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-tests.md` |
| **Data Immutability, State Management, Transformers** | `.agents/skills/data-logic/SKILL.md` |
| **API Contracts, Zod, Schemas, Request Validation** | `.agents/skills/api-contract/SKILL.md` |
| **Orion, Knowledge Base, Ingest, Lint, Cross-reference** | `.agents/skills/brain-graph/SKILL.md` & `.agents/workflows/orion-ops.md` |
| **Debugging, Errors, Crashes, Runtime Issues** | `.agents/skills/frontend-experience/SKILL.md` & `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-debug.md` |
| **Deployment, Build, Release, CI/CD, DevOps** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-release.md` & `.agents/skills/project-operator/SKILL.md` & `.agents/workflows/prod-deploy.md` |
| **Cost Analysis, Token Budget, LLM Costs** | `python .agents/scripts/orion.py scan tokens` (Run it!) & `.agents/skills/cost-optimizer/SKILL.md` |
| **Agent System Modification, .agents/ Edits, Rules** | `.agents/AGENTS_INDEX.md` & `.agents/skills/meta-agent-admin/SKILL.md` |
| **Code Review, PR Review** | `.agents/workflows/audit-and-test.md` |
| **Token Reduction, Compression, Caveman Mode** | `.agents/skills/caveman/SKILL.md` & `.agents/skills/caveman-compress/SKILL.md` |
| **Accessibility, A11y, Micro-interactions, Web UX** | `.agents/skills/palette/SKILL.md` |
| **Session End, Handoff, Context Eviction** | `.agents/workflows/session-offload.md` |
| **Test-Driven Development (TDD), Writing Tests** | `.agents/workflows/audit-and-test.md` |
| **End-to-End Feature Creation (App Builder)** | `.agents/workflows/app-lifecycle.md` |
| **Agent Self-Learning, Reflection, Pattern Synthesis** | `.agents/workflows/self-evolve.md` |
| **Agent Identity, Onboarding, Personality, Bootstrap** | `context/AGENT_IDENTITY.md` |
| **Temporal Pulse, Daily Summary, Weekly Synthesis** | `.agents/workflows/temporal-pulse.md` |
| **Worker Delegation, Sub-agent, Task Splitting** | `.agents/skills/worker-delegate/SKILL.md` |

*Note: Once you load the file via `view_file`, you MUST physically execute any scripts or commands it asks you to run. If a referenced canon file is missing (ghost routing), skip it and rely on generic protocols.*

## 5. UNIFIED RESPONSE FOOTER

Technical and conversational responses must end with tidy orientation context. The footer must remain clean, free of raw bracketed prompts or leaked template directives, scaling strictly by turn type:

**Conversational / Q&A Turn** (2 clean lines — No tools/commands executed):
```
🚦 **CHECKPOINT**: [Brief summary of the answer or explanation]
🔮 **NEXT TASK**: [Immediate next step or "None"]
```

**Standard / Execution Turn** (3 clean lines — Normal file/tool operations):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [Exit Code X, test status, or verified mechanical state]
🔮 **NEXT TASK**: [Immediate next workflow step or "None"]
```

**Premium / Deep Architectural Turn** (4 clean lines — Complex, multi-system, or audit tasks):
```
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [State the EXACT Exit Code or output status. If Exit Code > 0, do NOT claim success.]
🧠 **EVALUATION**: [Execution smooth | Execution rough: brief root-cause / error analysis]
🔮 **NEXT TASK**: [Next workflow step or "None"]
```

> **Cleanliness Mandate**: NEVER leak raw template text, placeholder brackets (e.g., `[DO: YES]`, `[If empty: ...]`), or noisy multi-line logs into the footer.

## 6. END-OF-TASK PROTOCOL (AUTO-EVOLVE)

You MUST NOT wait for the user to ask you to learn from mistakes.

- **Task Complete / Feature Done:** If you executed a manual process >3 times or fixed the same error twice, trigger `.agents/workflows/self-evolve.md` silently to extract the pattern.
- **Errors / Exit Code > 0:** If you encounter a systemic failure, extract the learning to `.agents/LEARNINGS.md`.
- **Session Offload Prompting:** If task queue is empty AND you just completed a major milestone, proactively add: *"Milestone reached. Recommend `/session-offload` to save context."*
- **Session End:** If the user indicates they are done, execute `.agents/workflows/session-offload.md`.

## 7. AUTOMATION HOOKS (Advisory)

Run these scripts when the corresponding condition is met. If a script is not installed in the target project, skip it.

1. **System Mod/Scaffold**: Modifying `.agents/` or finishing a scaffold? Run `python .agents/scripts/orion.py verify_agents`
2. **UI Modification**: Finishing any UI task? Run `python .agents/evals/audit_aesthetics.py --dir <path>` (if available)
3. **High Context Load**: User asks about context/tokens? Run `python .agents/scripts/orion.py scan tokens`

## 8. INTEGRITY FLAG

Every implementation plan you create (`implementation_plan.md`) MUST include a direct, literal quote from `core-guardrails.md` in its header to verify context is fully loaded.

---
*Mandate Version: 0.0.1 (English First & Built-In Caveman)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->
