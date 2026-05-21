# [AUDIT_REPORT_2024_05_21.md]

## 1. Context Bloat & "Ghost Tokens" (Token Economy)
*   **Analysis:** Several core rule files exceed the optimal context window for focused tasks, creating "ghost tokens" that dilute instructions and increase the risk of middle-in-the-prompt attention loss.
*   **Actionable Output:**
    *   **Top 3 Bloated Files:**
        1.  `.agents/rules/context-standards.md` (~1642 words)
        2.  `.agents/rules/core-guardrails.md` (~1456 words)
        3.  `.agents/rules/tier-execution-protocol.md` (~1137 words)
    *   **Resolution Strategy (Modularization & Caveman Protocol):**
        *   Split `context-standards.md` into `context-limits.md` (hard numeric constraints) and `context-routing.md` (navigation rules).
        *   Split `core-guardrails.md` into `guardrails-behavior.md` and `guardrails-code.md`.
        *   Apply "Caveman Protocol" (Telegraphic, 8-10 words per sentence) to the remaining content. Replace verbose explanations with direct commands. For example, instead of "You must ensure that the context window is not overloaded by reading too many files at once," use: "Read one file. Target grep. Save tokens."

## 2. Mechanical Integrity & Dead Links
*   **Analysis:** The `view_file` JIT loading mechanism is central to the architecture, but restructuring has left several broken references.
*   **Actionable Output:**
    *   **Broken/Stale Paths Identified:**
        *   `view_file .agents/canons/micro/flutter.md` referenced in `.agents/rules/flutter-standards.md` (File is missing in the `universal` directory).
        *   `view_file .agents/canons/micro/git-workflow.md` referenced in `universal/.agents/rules/git-workflow.md` (The file exists, but its path may not align if `universal/` is used as the root).
    *   **Resolution:** Implement a mechanical pre-flight script (`verify_links.sh`) to recursively grep for `view_file` commands and assert file existence. Synchronize the `canons/micro/` directory between root and `universal/`.

## 3. Structural Drift & Duplication
*   **Analysis:** The creation of the framework-agnostic `universal/` directory has resulted in structural drift and duplicated logic compared to the root `.agents/`.
*   **Actionable Output:**
    *   **Drift Instances:**
        *   `.agents/workflows/app-builder.md` uses Flutter-specific terminology ("Widget tree"), while `universal/.agents/workflows/app-builder.md` uses generic terms ("Component tree").
        *   Files like `flutter-standards.md` exist in the root but not in `universal`, which is expected, but the universal `app-builder.md` still relies on concepts that require framework-specific logic.
    *   **Resolution:** Consolidate shared logic. Use a templating engine or environment variable injection (via the `env-adapter` skill) to inject framework-specific terms (like "Widget" vs "Component") into a single set of base workflows, rather than maintaining two diverging copies.

## 4. The "Bento-Box" Protocol Compliance
*   **Analysis:** The `tier-execution-protocol.md` mandates the Bento-Box rule for BUDGET tasks (manipulate one file, followed by a hard evaluation). However, heavily used workflows do not strictly enforce this mechanical pause.
*   **Actionable Output:**
    *   **Redesign `app-builder.md`:** The current `app-builder.md` chains multiple UI and Logic tasks sequentially without forcing a mechanical verification stop.
    *   **Resolution:** Inject strict `[HARD PAUSE]` checkpoints into `app-builder.md`. Example redesign for step transitions:
        ```markdown
        ## 2. AESTHETIC DESIGN (LIQUID GLASS)
        - [ ] **Component Blueprint**: Define the Component tree in `STYLE_GUIDE.md`.
        - [ ] **MANDATORY BENTO-BOX PAUSE**: You MUST run UI linting/testing before proceeding to Step 3. Do not batch Step 2 and Step 3 together.
        - [ ] **Auto-Chain Trigger**: Set `NEXT TASK: Execute lint and proceed to data-logic`
        ```

## 5. Security & Safety Gates
*   **Analysis:** `security-guardrails.md` contains strict rules (e.g., "NO HARDCODED SECRETS", "Pre-Commit Secrets Scan"), but relies on textual instruction, which LLMs may skip.
*   **Actionable Output:**
    *   **Enforcement Hook:** Textual validation is insufficient. Create a strict mechanical pre-commit hook that MUST be executed.
    *   **Mandatory Bash Execution:** Agents must be forced to execute this exact bash command before using the `submit` tool:
        ```bash
        grep -rE "(sk-[a-zA-Z0-9]{32,}|SUPABASE_SERVICE_KEY|anon_key|password\s*=\s*['\"][^'\"]+['\"])" --include="*.dart" --include="*.ts" . || echo "[SECRETS CLEAR] Proceed to submit."
        ```
