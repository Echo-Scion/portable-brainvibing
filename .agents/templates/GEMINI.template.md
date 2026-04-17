# Workspace Rules & Mandates: {project_name}

<!-- START FOUNDATION MANDATES -->
> **CRITICAL HABITAT NOTICE:** This directory is a satellite deployment of the Master Habitat. This file defines the **absolute operational constraints** for all agents operating within `{project_name}`. It is always-on and non-negotiable.

## 1. MANDATORY BOOTSTRAP (Session Resume)
- **Goal:** Immediately recover context, atomic task status, and architectural constraints.
- **CRITICAL**: Locate and read `core-guardrails.md` at the start of **every** task. This file contains the "Pre-Execution Firewall" (Binary Oratory), "Surgical Munching" protocols, and "Reasoning Standards" that are no longer hardcoded in this BIOS.
- **AUTO-ROUTER TRIGGER (Small Model Superiority)**: You MUST automatically identify if you are running as a Budget/Small Model. If so, you are AUTOMATICALLY BOUND by the LOCAL TRIAD OF RULES: Find and read `context-standards.md` (Skeleton First), `tier-execution-protocol.md` (One task per run), and `autoharness-protocol.md` (Only write verifier test then Auto-Abort for Premium Model). The user DOES NOT NEED to remind you.
- For task-specific rules, use the search tools (`file_search` or `grep_search`) to find domain-specific rules by their filename rather than relying on folder paths.

> [!CAUTION]
> **HARD GATE**: You are **FORBIDDEN** from executing any filesystem or terminal tools (except `view_file` or `grep_search` to find core rules) UNTIL you have read `core-guardrails.md`. Any tool call (like `run_command`, `write_to_file`, `replace_file_content`, etc.) before reading the guardrails is a severe protocol violation.

> **INTEGRITY FLAG**: Every `implementation_plan.md` or first technical response MUST begin with a "Bootstrap Verification" block, quoting exactly one relevant constraint from `core-guardrails.md` to prove context recovery.

- **ANTI-AFFIRMATION MANDATE**: Never simply agree with or affirm the user's ideas/code. You must proactively find flaws, logical gaps, missed edge cases, or scalability issues. Treat every initial idea as flawed until proven otherwise. You MUST provide exactly 3 specific points of criticism along with 3 corresponding actionable solutions before proceeding.

## 2. ABSOLUTE [DONT] LIST
- `[DONT]` Delete production databases or their contents.
- `[DONT]` Commit secrets, API keys, or credentials to any file.
- `[DONT]` Execute `rm -rf` or `Remove-Item -Recurse` without explicit confirmation.
- `[DONT]` Modify `GEMINI.md` or any structural system rules without a Binary Oratory pre-flight.

## 3. MASTER ROUTING INDEX
> Rely on dynamic discovery rather than hardcoded paths. Use QMD (`npx @tobilu/qmd query`) to semantically search for the relevant architectural knowledge, canons, or context documents you need.

### 3.1 CORE RULES & CANONS (Constraints)
Instead of relying on fixed directories, search for these core filenames across the workspace when their focus area is triggered:
- **Behavior & Logic**: Locate `core-guardrails.md` and `reasoning-standards.md`.
- **Tier & Context**: Locate `tier-execution-protocol.md` and `context-standards.md`.
- **Coding Limits**: Locate `autoharness-protocol.md` and `flutter-standards.md`.
- **Security & Git**: Locate `security-guardrails.md` and `git-workflow.md`.
- **Architecture**: Locate the project's `core-architecture.md` or relevant `README.md` for global, harnesses, and microservice structures.

### 3.2 SKILL ORCHESTRATORS (Actions)
Locate the corresponding skill files by searching for their orchestrator name.
- **SaaS Strategy**: Invoke `saas-strategist`
- **Architecture & Backend**: Invoke `backend-orchestrator`
- **UI/UX & Frontend**: Invoke `frontend-experience`
- **Admin & Evolution**: Invoke `meta-agent-admin`
- **DevOps & Release**: Invoke `project-operator`
- **API Contracts**: Invoke `api-contract`
- **Data Logic**: Invoke `data-logic`
- **Security / QA**: Invoke `integrity-sentinel`

---
*Mandate Version: 2.3.2 (Decoupled Path Optimized)*
<!-- END FOUNDATION MANDATES -->

## PROJECT-SPECIFIC MANDATES
<!-- Add your custom project rules here. They will be preserved during foundation updates. -->