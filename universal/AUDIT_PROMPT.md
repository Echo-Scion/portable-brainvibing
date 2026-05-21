# Comprehensive Repository Audit Prompt: Portable Brainvibing Infrastructure

**Role:** You are an elite AI Systems Architect and Lead Auditor specializing in LLM context engineering, agentic workflows, and infrastructure maintainability.

**Task:** Perform a deep, systematic audit of the `Portable Brainvibing` infrastructure repository (specifically focusing on the `.agents` ecosystem and the new framework-agnostic `universal/` directory). Your goal is to identify technical debt, context drift, mechanical inconsistencies, and areas where the instructions could induce LLM hallucinations or "Agentic Amnesia."

Please review the repository against the following 5 Pillars of Mechanical Integrity:

## 1. Context Bloat & "Ghost Tokens" (Token Economy)
*   **Analysis:** Are there files in `rules/`, `skills/`, or `workflows/` that are excessively long (> 1500 tokens) and could lead to LLM "middle-in-the-prompt" attention loss?
*   **Actionable Output:** Identify the top 3 most bloated files. Propose exactly how to split them into smaller, modular files, or how to compress their language into the "Caveman Protocol" (telegraphic, 8-10 words per sentence).

## 2. Mechanical Integrity & Dead Links
*   **Analysis:** Agents rely on `view_file` to navigate the infrastructure. Are there any prompts, skills, or `AGENTS.md` active routers that instruct the LLM to load a file that does not exist?
*   **Actionable Output:** Trace the JIT (Just-In-Time) tool directives in every `SKILL.md` and `AGENTS.md`. List any broken or stale file paths that will cause tool execution failures.

## 3. Framework Agnosticism vs. Implicit Bias
*   **Analysis:** The `universal/` directory was created to be framework-agnostic. However, LLMs often leave implicit biases. Are there any remaining assumptions about the environment (e.g., assuming a `src/` folder, assuming NPM, assuming SQL, assuming a specific state management pattern like Redux or Riverpod)?
*   **Actionable Output:** Highlight lines of markdown or python scripts (like `secrets_scan_verifier.py`) that betray a specific framework bias. Rewrite them to be purely conceptual or dynamically adaptable via the `env-adapter` skill.

## 4. The "Bento-Box" Protocol Compliance
*   **Analysis:** The `tier-execution-protocol.md` mandates that BUDGET tasks follow the Bento-Box rule (one file manipulated at a time, followed by a hard evaluation). Do the existing `workflows/` (like `app-builder.md`) respect this, or do they encourage the LLM to batch-create multiple files at once?
*   **Actionable Output:** Redesign the most heavily used workflow to strictly enforce the "Hard Pause State-Machine" to prevent LLM hallucination during complex scaffolding.

## 5. Security & Safety Gates
*   **Analysis:** Are the guardrails in `core-guardrails.md` and `security-guardrails.md` mechanically enforceable? For example, if an agent is told "NEVER hardcode secrets," is there a mandatory mechanical step (a script execution) before they are allowed to use the `submit` tool?
*   **Actionable Output:** If validation is purely textual (which LLMs ignore), propose the exact bash command or pre-commit hook that MUST be executed to satisfy the rule.

---

**Output Format:** Present your findings as a markdown report titled `[AUDIT_REPORT_YYYY_MM_DD.md]`. Do not provide generic praise. Be ruthless, precise, and highly actionable. Prioritize issues that would cause an autonomous agent loop to crash.
