# VOLUME VIII: CANONS, TEMPLATES, HOOKS, EVALS, AND ARCHIVES

---

## Chapter 17: Ecosystem Canons (`canons/`)

Canons define framework-specific best practices, architectural standards, and syntactic patterns. They are structured into four layers:

```
canons/
├── ecosystems/         # Framework-specific production patterns
│   ├── flutter/        # 13 canon files (init, debug, release, state-map, ui-patterns, tests, etc.)
│   ├── react/          # Ecosystem canons (init, standards, recipe, ui, tests, debug, release)
│   └── python/         # Ecosystem canons (init, standards, recipe, ui, tests, debug, release)
├── global/             # Cross-framework architectural standards
│   ├── core-architecture.md  # Fundamental principles across all stacks
│   ├── ai_brands.json        # Registry of supported IDE platforms
│   └── harnesses/            # Reusable verification scripts
├── micro/              # Compressed cheat-sheets for BUDGET models
│   ├── flutter.md      # Riverpod 2.x, Freezed, GoRouter syntax cheat-sheet
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

---

## Chapter 18: Templates (`templates/`)

Standardized scaffolds for generating new assets and bootstrapping projects:

| Template | Scope | Operational Purpose |
|:---|:---|:---|
| `AGENTS.template.md` | Root instruction file | Source template for generating `GEMINI.md`, `CLAUDE.md`, or `.cursorrules` |
| `PROJECT_SCAFFOLD.template.md` | Architecture & Blueprint | Master prompt for greenfield project initialization |
| `MEMORY.template.md` | State tracking | SaaS project status, active tasks, and session handoff |
| `TASK_PLANNING.template.md` | Planning checklists | Implementation plans, execution checklists, and atomic sub-tasks |
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
2. Emits real-time IDE state to `.orion/working/context.json` via atomic file swap (`os.replace`).
3. Evaluates `LEARNINGS.md`. If unprocessed learning entries $\ge 3$, sets `"evolution_overdue": true`.
4. Checks for dangling FSM execution state and injects recovery parameters if a prior execution crashed.

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

---

## Chapter 20: Automated Evaluators (`evals/`)

### 20.1. Aesthetic Evaluator (`evals/audit_aesthetics.py`)
Automated gatekeeper for UI quality across Flutter, React, and web components:
- **Generic Color Check**: Detects un-tokenized raw color literals (`Colors.red`, `Colors.blue`, raw hex).
- **Inline Style Check**: Flags non-tokenized inline style declarations.
- **Animation Primitives**: Verifies that interactive UI components include motion primitives (`AnimatedContainer`, `framer-motion`, `transition-colors`).
- Returns `Exit Code 1` on critical aesthetic violations, halting execution gates.

### 20.2. Benchmark Configurations (`evals/evals.json`)
Evaluation matrices and benchmark configurations for assessing agentic reasoning performance and model tier routing.

---

## Chapter 21: Archive & Root Metadata Files

### 21.1. Archive (`archive/`)
Preserves architectural history and legacy implementations:
- `archive/workflows/`: 18 legacy procedural workflows preserved for historical reference following their consolidation into Skill Tier-3 References.
- `archive/orion_mcp.py`: Experimental legacy MCP server implementation.

### 21.2. Root Metadata Files
- **`AGENTS_INDEX.md`**: Master index mapping all rules, skills, workflows, and canons.
- **`DEPLOY_ME.md`**: Plug-and-play instructions for deploying Foundation to new spoke projects.
- **`LEARNINGS.md`**: Collective experiential memory storing structured post-mortems.
- **`EVOLUTION_LOG.jsonl`**: Append-only genomic ledger recording mutations and fitness deltas.
- **`.genome.json`**: Compact genomic signature imported during spoke deployments.
- **`.project_manifest.json`**: Spoke metadata defining stack, language, and project identity.
- **`.deployed_ais`**: Registry of configured AI IDE adapters.
