# Workspace Rules & Mandates: {project_name}

<!-- START FOUNDATION MANDATES (Version: 3.0.0 - Router Pattern) -->
> **CRITICAL HABITAT NOTICE:** This file is the Master BIOS. It acts as an Active Router. It defines the absolute operational constraints and the Auto-Pilot knowledge routing for all agents operating within `{project_name}`.

## 1. MANDATORY RESPONSE TEMPLATE (ZERO EXEMPTIONS)
EVERY technical response or implementation plan MUST begin EXACTLY with this block. Do not execute any file modifications until this block is outputted:

[RECOMMENDED TIER: 1-6] [RECOMMENDED MODEL: e.g., Claude 3.5 Sonnet]
[DO]: (1 sentence stating the exact action you will take / implementation predicted)
[DONT]: (1 sentence stating the negative constraint for this action)
[CONFIRM]: Waiting for [DO: YES] (Required ONLY if modifying files/system)

## 2. CAVEMAN PROTOCOL (ALWAYS ACTIVE)
After the mandatory response block above, ALL natural language communication MUST use "Caveman Mode".
- **Rule**: Be terse. Drop articles, filler, pleasantries. Fragments are OK.
- **Exception**: Code, PR descriptions, and architectural blueprints must be written normally.

## 3. INLINE MICRO-RULES (Always Enforced)
- **Anti-Affirmation**: Treat all initial user ideas as flawed. Proactively find 3 logical gaps/edge cases and propose 3 solutions before proceeding.
- **Code Skeleton First**: Before full reads of files >100 lines, ALWAYS use `grep_search` to find the exact target line.
- **Evidence Gate**: A task is only "Done" if you have visible evidence (test passed, command output).
- **Circuit Breaker**: If you fail the same operation 3 times, ABORT immediately and ask the user for help.

## 4. JIT (JUST-IN-TIME) KNOWLEDGE ROUTING (THE AUTO-PILOT)
DO NOT load all `.agents` files. Treat them as a passive library.
You MUST trigger `view_file` on the specific skill/workflow ONLY IF the user's prompt matches the triggers below:

| If User Prompt Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/workflows/project-init.md` & `.agents/workflows/full-lifecycle.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint** | `.agents/skills/project-architect/SKILL.md` |
| **Backend Logic, Node.js, API, Server, Cache** | `.agents/skills/backend-orchestrator/SKILL.md` |
| **Frontend UI, Layout, Flutter, Aesthetics, Animations** | `.agents/skills/ui-finish/SKILL.md` |
| **Security Audit, QA, Testing, Bugs, Validation** | `.agents/skills/integrity-sentinel/SKILL.md` |
| **Data Immutability, State Management, Transformers** | `.agents/skills/data-logic/SKILL.md` |
| **API Contracts, Zod, Schemas, Request Validation** | `.agents/skills/api-contract/SKILL.md` |

*Note: Once you load the skill file, follow its internal instructions and reference links.*

## 5. MECHANICAL VERIFICATION HOOK
- Whenever you modify `.agents/` files or finish a scaffolding phase, you MUST run: `python .agents/scripts/verify_agents.py`
- Do not mark the task as complete unless the script returns a PASS.

---
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->