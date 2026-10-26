# VOLUME VIII: CANONS, TEMPLATES, HOOKS, EVALS, AND ARCHIVES

---

## Chapter 17: Ecosystem Canons (`canons/`)

Canons define framework-specific best practices, architectural standards, and syntactic patterns across verified canon assets:

```
canons/
├── ecosystems/         # Framework-specific production patterns
│   ├── flutter/        # Ecosystem canons (init, debug, release, state-map, ui-patterns, tests, etc.)
│   ├── react/          # Ecosystem canons (init, standards, recipe, ui, tests, debug, release)
│   └── python/         # Ecosystem canons (init, standards, recipe, ui, tests, debug, release)
├── global/             # Cross-framework architectural standards
│   ├── core-architecture.md  # Fundamental principles across all stacks
│   ├── ai_brands.json        # Registry of supported IDE platforms
│   └── harnesses/            # Reusable Code-As-Harness action verifiers
├── micro/              # Compressed cheat-sheets for BUDGET models
│   ├── flutter.md      # Riverpod, Freezed, GoRouter syntax cheat-sheet
│   ├── python.md       # Python 3.10+ stdlib & typing syntax cheat-sheet
│   ├── react.md        # React / Next.js component & hook cheat-sheet
│   ├── pubspec.md      # Flutter pubspec.yaml dependency patterns
│   └── supabase.md     # Supabase security and query patterns
└── local/              # Project-specific custom canon overrides
```

### Core Architecture Principles (`global/core-architecture.md`)
1. **Agent-First Design**: Code and structures optimized for deterministic machine parsing.
2. **Predictable Modularity**: Isolated modules over monolithic structures.
3. **Distributed Context**: Context maintained at root and domain level.
4. **Code-As-Harness**: Verification offloaded to deterministic scripts.
5. **Unidirectional Data Flow**: Immutable state mutations through explicit events/actions.
6. **Strict Verification**: No completion claims without fresh execution evidence.

### 17.1. Code-As-Harness Action Verifiers (`canons/global/harnesses/`)
Following the Harness² (`Code-As-Harness`) methodology, recurring high-risk operations are guarded by standalone Python action verifiers stored in `.agents/canons/global/harnesses/`. Every harness implements `is_legal_action(action: dict, state: dict) -> tuple[bool, str]`:
- **`base_action_verifier.py`**: Reference contract template defining the `is_legal_action` signature, JSON CLI stdin/argv runner, and `--self-test` verification harness.
- **`migration_verifier.py`**: Blocks destructive SQL migrations (`DROP TABLE`, `TRUNCATE`, unguarded `ALTER TABLE ... DROP COLUMN`) unless an explicit rollback migration and backup assertion are present in `state`.
- **`secrets_scan_verifier.py`**: Pre-commit and pre-write action filter that rejects payloads containing high-entropy API keys, PEM private keys, or hardcoded bearer tokens.
- **Automated Synthesis (`HarnessEngine.synthesize_action_verifier`)**: When a new operational failure pattern is promoted, `core/harness/engine.py` synthesizes a new `<slug>_verifier.py`, validates its AST and `is_legal_action` signature, and registers it in `.agents/canons/global/harnesses/`.

---

## Chapter 18: Templates (`templates/`)

Standardized scaffolds for generating new assets and bootstrapping projects across 19 verified templates:

| Template | Scope | Operational Purpose |
|:---|:---|:---|
| `VISION.template.md` | Root North Star | Immutable foundational vision, non-negotiable invariants, and anti-vision filter |
| `AGENTS.template.md` | Root instruction file | Source template for generating canonical `AGENTS.md` and platform adapters (`GEMINI.md`, `CLAUDE.md`) |
| `ANDROID_STUDIO_EXECUTOR.prompt.md` | Sequential Executor | Zero-escape copy-paste system prompt for executing Bento plans in Android Studio / IDE chat |
| `PROJECT_SCAFFOLD.template.md` | Architecture & Blueprint | Master prompt for greenfield project initialization |
| `MEMORY.template.md` | State tracking | SaaS project status, active tasks, and session handoff |
| `TASK_PLANNING.template.md` | Planning checklists | Implementation plans, execution checklists, and atomic Bento sub-tasks |
| `STYLE_GUIDE.template.md` | Design tokens | Visual design system, color palettes, and typographic tokens |
| `DESIGN.template.md` | Visual craft | Master 20+ design archetypes, color palettes, and locked visual tokens |
| `ADR.template.md` | Architectural decisions | Architectural Decision Record standard (Status, Context, Decision, Consequences) |
| `AI_ADAPTER.template.md` | Tool adapters | Lightweight adapters routing external IDEs to canonical AGENTS.md |
| `CURSOR_RULE.template.mdc` | Cursor IDE | Native Cursor project rule adapter |
| `ORION_SCHEMA.template.md` | Knowledge database | SQLite schema definition for `.orion/orion.db` |
| `agent-identity-template.md` | Agent persona | Bootstrap profile for initializing `context/AGENT_IDENTITY.md` |
| `custom-agent.template.md` | New sub-agent | Scaffold for creating new custom agent roles |
| `custom-rule.template.md` | New behavioral rule | Scaffold for creating new behavioral rules |
| `github-native-structure.md` | Version control | Standardized GitHub folder structures and workflows |
| `startup_knowledge_base.md` | Knowledge initialization | Domain knowledge intake guidelines |
| `TEMPLATES.md` | Registry documentation | Master index and specification of all available templates |

---

## Chapter 19: Lifecycle Hooks (`hooks/`)

### 19.1. Pre-Invocation Hook (`pre-agent-wake.py`)
Executed synchronously prior to agent turn execution:
1. Receives invocation parameters: `--active-file`, `--terminal-error`, `--ide-source`, `--user-intent`.
2. Evaluates the **5-Minute SHA-256 Prompt-Cache Preservation Gate**: computes `structural_hash` over `active_file`, `terminal_error`, `active_bento_task`, and `evolution_overdue`. If `< 300` seconds have elapsed since the last write and `structural_hash` matches, skips rewriting `.orion/working/context.json` to preserve LLM KV prompt caches.
3. If state changed or $\ge 300$ seconds elapsed, emits real-time IDE state, `active_bento_task`, `observation_digest`, and `temporal_gap_marker` to `.orion/working/context.json` via atomic file swap (`os.replace`).
4. Evaluates `LEARNINGS.md` and `OBSERVATIONS.md`. If unprocessed learning entries $\ge 3$, sets `"evolution_overdue": true`.
5. Checks for dangling FSM execution state and injects recovery parameters if a prior execution crashed.

### 19.2. Post-Generation Validation
No post-generation hook is currently exposed by this repository's `hooks.json` contract. The response validator remains available for hosts that provide a response-bearing hook:

```bash
python .agents/scripts/orion.py validate-response --file <response-file>
```

Until such a hook exists, validation cannot mechanically block delivery.

### 19.3. Git Post-Commit Hook (`post-commit`)
Executed automatically upon `git commit`:
1. Triggers `python .agents/scripts/orion.py brain sync` in the background.
2. Updates SQLite FTS5 indexes and edge connections without manual developer intervention.

### 19.4. RTK PreToolUse Command Rewriter (`rtk-pre-tool.py`) & Cross-OS Shims (`run-hook.cmd` / `run-hook.sh`)
- **`hooks/rtk-pre-tool.py`**: Intercepts `Bash` / terminal tool calls on supported IDE hosts (`Claude Code`, `Cursor`, `Cline`, `Windsurf`, `Antigravity`). When `rtk` (Rust Token Killer) is installed on `PATH`, the hook transparently rewrites high-noise developer commands (`git status`, `git diff`, `git log`, `cargo test`, `npm test`, `pytest`, `flutter test`) to `rtk <cmd>`, cutting terminal stdout token volume by 60–90% while leaving raw pipes, redirects, and unsupported commands untouched.
- **`hooks/run-hook.cmd` & `hooks/run-hook.sh`**: Cross-platform shell wrappers that resolve `python` vs `python3` with `-X utf8` (`PYTHONUTF8=1`) so `hooks.json` definitions work identically across Windows PowerShell/CMD, macOS, and Linux.

---

## Chapter 20: Automated Evaluators (`evals/`)

The `.agents/evals/` directory houses 3 deterministic verification engines (66 KB total) alongside `evals.json`:

### 20.1. Aesthetic & Anti-Slop Evaluator (`evals/audit_aesthetics.py`)
Automated gatekeeper for UI craft and prose authenticity across Flutter, React, HTML/CSS, and Markdown:
- **WCAG 2.1 AA Luminance & Contrast Math**: Computes relative luminance $L = 0.2126 R + 0.7152 G + 0.0722 B$ and contrast ratios $(L_1 + 0.05) / (L_2 + 0.05)$ to flag text/surface pairs below `4.5:1` (`3.0:1` for large text).
- **Generic Color & Inline Style Check**: Detects un-tokenized raw color literals (`Colors.red`, `Colors.blue`, raw hex) and non-tokenized inline style declarations.
- **Animation Primitives**: Verifies that interactive UI components include motion primitives (`AnimatedContainer`, `framer-motion`, `transition-colors`).
- **54-Pattern Anti-Slop Prose Scanner**: Scans documentation and UI copy against the banned AI tell catalog in `rules/prose-authenticity.md`.
- Returns `Exit Code 1` on critical aesthetic violations, halting execution gates.

### 20.2. Deterministic Assertion Engine (`evals/assertion_engine.py`)
Contract evaluation engine (23 KB) that scores agent outputs and skill benchmark runs against structured criteria in `evals/evals.json`:
- **Multi-Modal Assertions**: Evaluates `contains`, `not_contains`, `regex_match`, `ast_valid`, `json_schema`, `exit_code`, `line_count_max`, and `file_exists` assertions without LLM-as-a-Judge variance.
- **Pass-Rate Aggregation**: Produces per-skill and per-tier pass/fail matrices with exact failure diffs for regression tracking.

### 20.3. Post-Action Consequence Verifier (`evals/consequence_verifier.py`)
To eliminate **False-Green Tests** (tests that execute a click or function call and pass solely because no exception was thrown), `ConsequenceVerifier` (24 KB) enforces positive post-action verification across 4 concrete dimensions:
1. **DOM / Widget Tree Mutation (`dom_widget`)**: Verifies that an interaction actually mounted, unmounted, or mutated target widget/DOM nodes rather than firing a no-op handler.
2. **State & Database Persistence (`state_db`)**: Verifies that state stores, SQLite tables, or repository states reflect expected post-mutation invariants.
3. **Network & IPC Contract (`network_ipc`)**: Validates outbound request payloads, status codes, or IPC channel messages against schema expectations.
4. **Visual & Layout Geometry (`visual_layout`)**: Checks bounding-box constraints, render overflow flags (`RenderFlex overflowed`), and visibility states.

### 20.4. Benchmark Configurations (`evals/evals.json`)
Evaluation matrices and benchmark configurations for assessing agentic reasoning performance, assertion pass rates, and model tier routing.

---

## Chapter 21: Archive & Root Metadata Files

### 21.1. Archive (`archive/`)
Preserves architectural history and legacy implementations:
- `archive/workflows/`: 18 legacy procedural workflows preserved for historical reference following their consolidation into Skill Tier-3 References.
- `archive/orion_mcp.py`: Experimental legacy MCP server implementation.

### 21.2. Root Metadata Files
- **`AGENTS_INDEX.md`**: Master index mapping all rules, skills, workflows, and canons.
- **`DEPLOY_ME.md`**: Plug-and-play instructions for deploying Foundation to new spoke projects.
- **`OBSERVATIONS.md` & `OBSERVATIONS.archive.md`**: Active 5-status Habit Observation ledger and cold archive for actioned/superseded observations.
- **`LEARNINGS.md`**: Collective experiential memory storing structured post-mortems.
- **`EVOLUTION_LOG.jsonl`**: Append-only genomic ledger recording mutations and fitness deltas.
- **`.pack.json`**: Pinned file inclusion and token budget manifest for Digestpack (`orion.py pack`).
- **`.genome.json`**: Compact genomic signature imported during spoke deployments.
- **`.project_manifest.json`**: Spoke metadata defining stack, language, and project identity.
- **`.deployed_ais`**: Registry of configured AI IDE adapters.
