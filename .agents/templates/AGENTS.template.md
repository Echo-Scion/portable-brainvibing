# Workspace Rules & Mandates: {project_name}

<!-- START FOUNDATION MANDATES (Version: 0.0.1 - Router Pattern) -->
> **CRITICAL HABITAT NOTICE:** This file is the Master BIOS. It acts as an Active Router. It defines the absolute operational constraints and the Auto-Pilot knowledge routing for all agents operating within `_foundation`.

## 1.0. SEQUENTIAL TOOL BAN (HARD GATE)
**CRITICAL**: You are FORBIDDEN from using any modifying tools (`run_command`, `write_to_file`, `replace_file_content`, etc.) until you have explicitly executed a `view_file` on `.agents/rules/core-guardrails.md` in the current session. Zero exceptions.

## 1.1. INTEGRITY FLAG
Every implementation plan you create (`implementation_plan.md`) MUST include a direct, literal quote from `core-guardrails.md` in its header to prove your context window is fully loaded and you are not suffering from Agentic Amnesia.

## 1.5. AUTO-PILOT INJECTOR (MANDATORY HARD HOOK)
Before beginning ANY coding task, planning phase, or feature scaffolding, you MUST execute `run_command` with `python .agents/scripts/orion.py brain sync "<your_task_keywords>"` to inject dynamic standards into your context. You MUST do this in your VERY FIRST turn. Do not skip this.

## 1.6. OS-AWARE PYTHON EXECUTION
Whenever a rule or workflow dictates running a `.agents/scripts/` command, use `python` (which is the default in these rules). If `python` fails or is not found (e.g., on Windows), you MUST fallback to `python3`.

## 1.7. THE DARWINIAN HEARTBEAT (MECHANICAL EVOLUTION)
If `context.json` contains `"evolution_overdue": true`, you MUST execute `python .agents/scripts/orion.py evolve mine-friction` before beginning your requested task. This ensures the brain mutates automatically without waiting for user instruction.

## 2. CAVEMAN PROTOCOL (VIA SKILL)
If the user requests token savings, "caveman mode", or terse communication, you MUST immediately load `.agents/skills/caveman/SKILL.md` using the `view_file` tool.
- **Rule**: Use the skill to guide your response compression. Drop articles, filler, pleasantries. Fragments are OK.
- **Exception**: Code, PR descriptions, and architectural blueprints must be written normally.

### Examples (Non-Negotiable Behavioral Anchors when Caveman is Active)
❌ "I noticed that the auth middleware is currently throwing a null pointer exception because it doesn't check..."
✅ "Auth middleware crashes. User object null. Adding null check."
❌ "Great! Now that we have successfully created the database tables, the next step would be..."
✅ "DB tables done. Next: API routes. [DO: YES] to begin."
❌ "I'm a bit confused about the design you want. Should the button be aligned to the left or the right? Please let me know so I can finish the layout."
✅ "Layout blocked. Button alignment unclear. Left or right?"

## 3. INLINE MICRO-RULES (Always Enforced)
- **Anti-Affirmation**: When the user presents a new architectural proposal or system design for review, treat it as flawed. Find up to 3 gaps (Security, Performance, Logic) and propose solutions. If 0 gaps exist, proceed.
- **Code Skeleton First**: Before full reads of files >100 lines, ALWAYS use `grep_search` to find the exact target line.
- **Circuit Breaker**: If you fail the same operation 3 times, ABORT immediately and ask the user for help.
- **Mandatory Orion Fetch (Anti-Amnesia)**: The IDE does NOT auto-load `.orion`. If you need information about project architecture, state, or past decisions, you MUST mechanically execute a `grep_search` or view the relevant `.orion/` file before generating an answer. Standardize on high-performance keyword/regex searching across the whole repository instead of relying on external indexing engines.
- **Cross-Domain Synthesis**: If a prompt triggers multiple conflicting skills (e.g., Frontend Layout + Database Mutability), do NOT treat them as isolated silos. You MUST explicitly synthesize a bridging pattern (e.g., via `api-contract`) in your thought process before executing.
- **Ingest Triplet Duty**: Setelah menjalankan `orion_ops ingest`, jika output mengandung `[TRIPLET_REQUEST]`, anda WAJIB membaca setiap source file yang terdaftar, mengekstrak 3-5 triplet semantik, lalu menjalankan `orion_ops inject_triplets` dengan hasilnya.

## 3.5. INTERNAL ROUTING ANALYSIS (ANTI-TUNNEL VISION)
Before answering ANY user prompt, you MUST perform routing analysis internally.
If a JIT Match is found based on the table below, you MUST immediately call the `view_file` tool on that Target in the exact same turn before continuing.
DO NOT output any `<route>` XML blocks to the chat.

## 4. JIT (JUST-IN-TIME) KNOWLEDGE ROUTING (THE AUTO-PILOT)
DO NOT rely on your internal LLM memory for how to execute these tasks. You suffer from Agentic Amnesia.
**CRITICAL DIRECTIVE**: If the user's prompt matches a trigger below, your VERY FIRST action MUST be to execute a `view_file` tool call on the target path IMMEDIATELY. Do NOT ask for permission. Do NOT wait for the user.

| If User Prompt Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-init.md` & `.agents/workflows/app-lifecycle.md` & `.agents/workflows/app-lifecycle.md` |
| **Legacy Migration, Brownfield, Onboard Existing, Migrate Project** | `.agents/workflows/project-migrate.md` |
| **Feature Scaffold, New Model, Repository, Screen** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-feature-recipe.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint** | `.agents/skills/project-architect/SKILL.md` |
| **Backend Logic, Node.js, API, Server, Cache** | `.agents/skills/backend-orchestrator/SKILL.md` |
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

*Note: Once you load the file via `view_file`, you MUST physically execute any scripts or commands it asks you to run.*

## 4.5. STANDARD DEPLOYMENT (DEPLOY)
After loading the primary workflow or skill from the table above, you MUST mechanically execute a `grep_search` on `.agents/rules/RULES_INDEX.md` using the current technology or feature keyword (e.g., "flutter", "auth", "api"). This guarantees that localized, micro-standards are injected precisely when needed before writing code.

## 5. UNIFIED RESPONSE FOOTER (MANDATORY)
EVERY technical response MUST END with this block. It provides GPS orientation, evidence, and pre-flight validation for the NEXT step.

```markdown
---
🚦 **CHECKPOINT**: [What just happened — 1 short sentence]
📋 **EVIDENCE**: [State the EXACT Exit Code or output status. If Exit Code > 0, you MUST NOT claim success.]
🧠 **EVALUATION**: [If Exit Code > 0: Root cause analysis. If 0: Check transcript logs. If >3 tool errors during task, state "Execution ROUGH" else "Execution smooth".]
🔮 **NEXT TASK**: [If ROUGH or Error: queue `/self-evolve`. If Success: Next workflow step or "None".]
⚡ **[RECOMMENDED TIER: BUDGET|STANDARD|PREMIUM]** — [If task queued: Reply `[DO: YES]` to execute. If empty: Describe next task.]
---
```

## 6. END-OF-TASK PROTOCOL (AUTO-EVOLVE)
You MUST NOT wait for the user to ask you to learn from mistakes.
- **Task Complete / Feature Done:** Before presenting the final output to the user, you MUST review the session. If you executed a manual process >3 times or fixed the same error twice, you MUST trigger `.agents/workflows/self-evolve.md` silently to extract the pattern.
- **Implementation Smoothness Audit:** After a major refactoring or complex task, check system logs (`transcript.jsonl`) for tool failures. If >3 tool errors occurred, the task is "ROUGH". You MUST trigger `.agents/workflows/self-evolve.md` to extract the failed command/tool anti-pattern into `LEARNINGS.md`.
- **Errors / Exit Code > 0:** If you encounter a systemic failure, you MUST trigger `.agents/workflows/self-evolve.md` to extract the learning to `.agents/LEARNINGS.md`.
- **Session Offload Prompting (Soft Trigger):** If task queue is empty (`NEXT TASK: None`) AND you just completed a major milestone (e.g. feature scaffold, successful PR, or heavy context load), you MUST proactively add to your response: *"Milestone reached. Recommend `/session-offload` to save context."*
- **Session End:** If the user indicates they are done for the day or pausing work, you MUST execute `.agents/workflows/session-offload.md` to run garbage collection and commit handoff state.

## 7. AUTOMATION HOOKS (NEVER SKIP)
You are FORCED to physically run these scripts in the terminal (`run_command`) when the corresponding condition is met:
1. **System Mod/Scaffold**: Modifying `.agents/` or finishing a scaffold? MUST run `python .agents/scripts/orion.py verify_agents`
2. **UI Modification**: Finishing any UI task or widget edit? MUST run `python .agents/evals/audit_aesthetics.py --dir <path>`
3. **High Context Load**: User asks about context/tokens? MUST run `python .agents/scripts/orion.py scan tokens`
- Do not mark the task as complete unless the terminal output confirms success.

## 8. IDE-AGNOSTIC NATIVE TOOLING (PORTABILITY)
You are operating in a portable framework. You must detect and utilize your native IDE capabilities (Antigravity, Cursor, Copilot, Windsurf) rather than relying on plain text chats when advanced interaction is required.
- **Interactive Alignment**: When a rule instructs you to "grill the user" or "ask for help", you MUST trigger your IDE's native interactive questionnaire tool (e.g., `/grill-me` in Antigravity, Composer Ask in Cursor) instead of outputting markdown questions.
- **Autonomous Execution**: When instructed to execute a massive refactor or a long-running goal, you MUST recommend or trigger your IDE's native autonomy mode (e.g., `/goal` in Antigravity, Agent Mode in Cursor, Cascade in Windsurf).
- **Scheduled Tasks**: When instructed to run cron-jobs or checks, use your IDE's native scheduling tool (e.g., `/schedule`).

---
*Mandate Version: 0.0.1 (Active Router Pattern)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->
