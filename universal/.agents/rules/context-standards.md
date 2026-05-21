---
description: Comprehensive rules for Context Management, Context Hierarchy, Token Economy, Skeleton-first loading, and Context Naming Policy (The 82-File Mandate) with QMD Retrieval.
activation: always on

version: 2.4.0
last_updated: 2026-05-20
---

# 1. Context Hierarchy & Resolution Layer
# Rule: Plug & Play Context Hierarchy

This rule defines how the agent resolves and prioritizes rules, skills, and memory in a **Physical Residency** environment (Plug & Play).

## 1. Resolution Layers

The context is resolved in two or three layers depending on project type:

### Standard Project (Single Layer)
| Level | Name | Scope | Location |
| :--- | :--- | :--- | :--- |
| **0** | **Global Foundation** | General AI behavior & standards. | `.agents/rules/` |
| **1** | **Project Local** | Project-specific rules & memory. | `.agents/rules/local/` & `context/` |

### Monorepo Project (Double Lean Layer)
| Level | Name | Scope | Location |
| :--- | :--- | :--- | :--- |
| **0** | **Global Foundation** | General AI behavior & standards. | `.agents/rules/` |
| **1** | **Monorepo Root** | Shared infrastructure, DevOps, & Design. | `/context/` (Root) |
| **2** | **App Local** | Specific business logic & features. | `/apps/[app_name]/context/` |

## 2. Monorepo Context Distribution (Double Lean)

In a monorepo environment, context MUST be distributed to prevent "Context Bloat" and ensure app-specific isolation:

- **Root Context**: Reserved ONLY for global platform infrastructure, monorepo DevOps (e.g., Melos, Docker), and unified design systems.
- **App Context**: Every sub-app MUST maintain its own **4-Pillar Context** folders (`00_Strategy`, `01_Product`, `02_Creative`, `03_Tech`).
- **Distributed SaaS Mapping**: Detailed SaaS context (Idea, Planning, Development, etc.) is stored in the specific app's context directory using the Prefix-Based Registry.

## 3. Plug & Play Residency (Physical)

To ensure 100% IDE compatibility and symbol indexing (Antigravity IDE), this system uses **Physical Residency**:

- **No Symlinks/Junctions**: All rules and skills are physically copied into the project's `.agents/` folder.
- **Self-Contained**: Every project is a standalone "Intelligence Unit" that carries its own brain.
- **IDE Native**: Because files are local, `@` mentions and clickable file links work out-of-the-box.

## 4. Domain Canons (The Truth)

Beyond rules and behaviors, this system uses **Canons** (`canons/`) to store the "Static Truth" of the project:

- **Identity & Philosophy**: Foundational values and aesthetic standards (`canons/global/`).
- **Standard Logic**: Pre-approved architectural patterns for `auth/`, `notifications/`, etc.
- **Lazy-Loading**: The agent MUST lazy-load relevant `.md` files from the `canons/` directory based on the task domain to minimize context usage while maintaining high fidelity to standards.
- **BUDGET Restriction**: `BUDGET` tasks are **prohibited** from loading canons unless the canon is explicitly referenced by name in the user's request. Canons are architectural context; atomic tasks do not require them.

## 5. Override Logic
- **Local Overrides Global**: If a rule exists in `.agents/rules/local/`, it automatically overrides the same rule in `.agents/rules/`.
- **Skill Priority**: The agent always checks for a local version of a skill in `.agents/skills/` before execution.

## 6. Initialization
- **Active Discovery**: At start, the agent checks for the `.agents/` folder in the project root.

# 2. Context Economy (Surgical Munching)
# Context7 Economical Usage

## 1. Resource Management
- Minimize token consumption during context retrieval.
- Prioritize high-value information snippets over full-text reads.
- Reuse context objects efficiently to avoid redundant processing.

## 2. Query Optimization
- Use specific and targeted queries to filter relevant documentation.
- Cache common query results for faster subsequent access.
- Limit the depth of recursive context generation.

## 3. Cost Control
- Monitor usage patterns to identify potential inefficiencies.
- Use lower-tier models for non-critical context processing.
- Periodically review and purge outdated context data.

## 4. Integration Guidelines
- Integrate Context7 seamlessly with existing agent workflows.
- Ensure consistent data formatting for all retrieved context.
- Provide clear error messages when context retrieval fails.

# 3. Context Diet for Budget Models
# Context Diet Protocol (Skeleton-First)

## 1. The Core Problem
Small/Budget Models hallucinate when fed too much raw code. If a model reads an 800-line file just to find one method, its context window gets "poisoned" by irrelevant noise, dropping reasoning accuracy drastically.

## 2. The Skeleton-First Law
If the agent is operating on **[TIER: BUDGET]**, the agent is **STRICTLY PROHIBITED** from using the `view_file` tool on long files (>200 lines) as a first step.

**Circuit Breaker (Strict Parameters):**
The agent MUST automatically reject (Abort) any attempt to use `view_file` on target files (>200 lines) if the `startLine` and `endLine` parameters are missing or cover the entire file.

**Mandatory File Navigation Order:**
1. **Grep/Search Skeleton:** Use `grep_search` to find the target function name, class, or file *header*.
   *Example:* `grep_search` with pattern `class |function |interface ` to get a structural overview.
2. **Targeted Read:** Once the target line is found, the agent may ONLY read that specific block (e.g., lines 45-80) using the line range parameters in `view_file`.
3. **No Blind Full-Reads:** A *blind full-read* without line constraints triggers an immediate block to prevent context poisoning.

## 3. Surgical Munching
Only extract what is absolutely essential for the task. If the task is merely changing a *button* color, reading the *Auth* module is forbidden.

*This rule guarantees that Small Models remain sharp, focused, and undistracted by irrelevant variables.*




# 4. Context Naming Policy (The 82-File Mandate) & QMD Retrieval

> **Scope Guard**: This rule applies ONLY to **target deployment projects** (SaaS apps built using this foundation). It does NOT apply to `_foundation` itself, which is a tooling project. If working within `_foundation/.agents/`, ignore the 82-file mapping requirement.

To prevent architectural drift and naming inconsistency, all files created within the `context/` directory MUST follow a deterministic naming convention.

## 1. The Mapping Requirement (Structural Organization)
- AI **MUST NOT** invent arbitrary file names for context or knowledge items.



## 2. Selection Logic
1. **Direct Match**: If the knowledge fits a specific category (e.g., SEO strategy), use the designated file (e.g., `01_Product/Acq_SEO_Wins.md`).
2. **Expansion Match**: If the knowledge is an expansion of an idea, append it to the relevant existing file rather than creating a "shadow" file.
3. **Zero Creation Tolerance**: The AI **MUST NOT** propose or create new file names. If the knowledge cannot be mapped exactly to one of the 82 files in the baseline, the system MUST return an error and reject the operation. No exceptions.

## 3. Retrieval & Discovery (The QMD Protocol)
- While the 82-File structure enforces **organization and scaffolding**, **retrieval** is managed dynamically via QMD semantic search.
- When you need to read architectural decisions or project context, do NOT guess the path or rely on manual catalogs (`workspace_map.md`). Instead, use QMD (`npx @tobilu/qmd search`) to semantically search for the relevant information.

## 4. Unstructured-to-Surgical (U2S) Mapping
- When a user provides an **Info-Dump** or a **Monolithic Master Blueprint** (single-file specs), the AI **MUST NOT** simply store it as a single file.
- AI MUST taxonomize the input and distribute it across the **82 SaaS Startup Files** baseline.
- **Protocol**:
    1. Parse the dump.
    2. Map snippets to specific domain files (e.g., "we will charge $10" -> `01_Product/Rev_Subscriptions.md`).
    3. Update `00_Strategy/BLUEPRINT.md` as the index.
    4. Interpolate missing details to ensure "Zero N/A" compliance.

## 5. Lean-to-Startup Evolution (Just-In-Time Expansion)
- **Anti-Paralysis**: Do NOT generate all 82 SaaS files upfront. Start with the minimal files needed for the current sprint.

- Even in **Lean** or **Startup** projects, any NEW idea or feature MUST trigger a **Surgical Expansion (JIT)**.
- Instead of creating random files, the AI "promotes" the relevant category from the 82-file baseline.
- *Example*: Adding a "Referral Program" to a project results in the creation of `context/01_Product/Growth_Referral_Programs.md`, initializing that specific file ONLY when needed.

## 6. Monorepo Distribution (Double Lean)
- In a monorepo, context is **split** between the root and the apps.
- **Dynamic Anchor Mapping**: Paths like `apps/[app]/context/` and `packages/[pkg]/context/` are declared as **Valid Base Anchors**. The 82-file *Exact Match* rule applies *relative to these anchors*, not just the workspace root.
- **Discrimination Matrix (Strict Isolation)**:
    - **Root `/context/` ONLY for**: `03_Tech/Infra_*` (Melos, Docker, CI/CD), `02_Creative/Design_Design_System.md` (Global Theme), and `00_Strategy/BLUEPRINT.md` (Main Vision).
    - **App `apps/[app]/context/` ONLY for**: Anything with `01_Product` prefix, app-specific UI/UX, and `03_Tech/Dev_*`.
    - Any attempt to violate this isolation MUST immediately trigger a **Circuit Breaker Error**.
- **The "Bridge Context" Protocol (Cross-Boundary Sync)**: For cross-app features (e.g., frontend + backend), the AI MUST use QMD Semantic Search. DO NOT duplicate context data across silos.

## 7. Safe Context Refactoring (Archivist & Quarantine Protocol)
To prevent accidental data loss ("Lossy Compression Hazard") when cleaning up or migrating malformed context files, the system enforces the following anti-destructive laws:

### 1. The "Quarantine" Rule (Proactive Rejection)

- **Rule**: The AI MUST NOT touch, overwrite, or proactively delete Quarantine files.
- AI must halt context operations targeting those files and instead notify the user about the anomaly to prevent destructive data loss.

### 2. Mandatory "Append-Only" Merging (No Summarization)
- If the AI is specifically tasked to merge a non-standard file into an official 82-file context file, the AI is **FORBIDDEN from paraphrasing or summarizing** the legacy content.
- Legacy text MUST be moved losslessly and appended directly to the bottom of the destination file inside a dedicated comment block, e.g., `<!-- LEGACY MERGE START --> [Original content here] <!-- LEGACY MERGE END -->`.
- *Why?* To ensure specific edge-cases written by the developers are not abstracted away by the LLM.