# VOLUME VIII: CANONS, TEMPLATES, HOOKS, EVALS, AND ARCHIVES

---

## Chapter 13: Ecosystem Canons (`canons/`)

### 13.1. 4-Layer Structure
```
canons/
├── ecosystems/         # Framework-specific
│   ├── flutter/        # 16 canon files (init, debug, release, state-map, ui-patterns, tests, etc.)
│   ├── react/          # 2 canon files (init, standards)
│   └── python/         # 2 canon files (init, standards)
├── global/             # Cross-framework
│   ├── core-architecture.md  # Constitution of all projects
│   ├── ai_brands.json        # Registry of supported IDEs
│   └── harnesses/            # Reusable verification scripts (action verifier, migration verifier, secrets scan)
├── local/              # Project-specific (empty in _foundation)
└── micro/              # Cheat-sheets for BUDGET models
    ├── pubspec.md      # Summary of Flutter pubspec.yaml
    └── supabase.md     # Summary of Supabase patterns
```

### 13.2. `global/core-architecture.md` — 6 Core Principles
1. **Agent-First Design**: Code must be easy for AI to parse.
2. **Predictable Modularity**: Isolated modules > monoliths.
3. **Distributed Context**: Context at root AND app-level.
4. **Code-As-Harness**: Offload validations to verifier scripts.
5. **Unidirectional Data Flow**: Immutable state, mutations via actions/events.
6. **Strict Verification**: No features completed without mechanical verification.

## Chapter 14: Templates (`templates/`)

### 14.1. 11 Template Files

| Template | Target | Purpose |
|:--|:--|:--|
| `AGENTS.template.md` | Root project (`GEMINI.md`/`CLAUDE.md`) | Multi-AI instruction generator (DRY source) |
| `PROJECT_SCAFFOLD.template.md` | Architecture & Blueprint | Master prompt for scaffolding new projects + 82-file mapping |
| `MEMORY.template.md` | State tracking | SaaS state tracking & session handoff |
| `TASK_PLANNING.template.md` | Checklists | Execution, roadmap, atomic tasks |
| `STYLE_GUIDE.template.md` | UI/UX tokens | Visual style guide |
| `ORION_SCHEMA.template.md` | `.orion/` configuration | Graph schema |
| `custom-agent.template.md` | New agent | Scaffold for custom AI agent |
| `custom-rule.template.md` | New rule | Scaffold for behavioral rule |
| `github-native-structure.md` | GitHub | Canonical GitHub folder structure guide |
| `startup_knowledge_base.md` | Knowledge | Auto-populating instructions for SaaS domains |

## Chapter 15: Hooks (`hooks/`)

### 15.1. `pre-agent-wake.py`
**Omni-Buffer Hook.** Called by IDE before AI starts its turn. Functions:
1. Receives arguments `--active-file`, `--terminal-error`, `--ide-source`, `--user-intent`.
2. Writes state to `context.json` atomically (temp file → `os.replace`).
3. Checks `LEARNINGS.md` for `[Darwinian Hook]` tags. If >= 3, sets `evolution_overdue = True`.
4. Automatically spawns `orion.py evolve mine-friction` in the background.

### 15.2. `post-commit` (Git Hook)
**Proactive Synchronization.** Automatically triggered by Git upon every commit. Functions:
1. Runs `python .agents/scripts/orion.py brain sync`.
2. Ensures the AI's contextual knowledge base and Graph representation are updated asynchronously without developer friction.

## Chapter 16: Evaluators (`evals/`)

### 16.1. `audit_aesthetics.py`
**CI/CD Gatekeeper for Aesthetics.** Scans `.dart`, `.tsx`, `.jsx`, `.css` files:
- **Check 1**: Detects generic colors (`Colors.red`, `Colors.blue`). Error: must use design tokens.
- **Check 2**: Detects inline style with generic colors. Error.
- **Check 3**: If > 5 raw hex codes, warning: extract to semantic tokens.
- **Check 4**: If file is a UI component but NO animation primitives are used (`AnimatedContainer`, `framer-motion`, `transition-all`), warning: add micro-interactions.

Exit Code 1 = fail → agent is forbidden from proceeding without fixes.

### 16.2. `evals.json`
Benchmark/evaluation configuration for testing AI models.

## Chapter 17: Documentation (`docs/`)

### 17.1. `versioning-changelog-guide.md`
Automated versioning pipeline: Semantic Versioning (`MAJOR.MINOR.PATCH`), automatic CHANGELOG, sanitizing sensitive files before distribution, blacklisting files that must not be synced.

### 17.2. `workflows_guide.md`
Brief guide on how to use workflows.

### 17.3. `MULTI_AI_DEPLOYMENT.md` (181 bytes)
Notes on deploying to multiple IDEs simultaneously.

## Chapter 18: Metrics (`metrics/`)
Contains `README.md` and `eval_workspace/` — workspace to run model performance evaluations.

## Chapter 19: Archive (`archive/`)
Contains `README.md` and `orion_mcp.py` — MCP server implementation for Orion (legacy/experimental).

## Chapter 20: Root `.agents` Files

### 20.1. `AGENTS_INDEX.md`
Master map listing all Rules, Skills, Workflows, and Canons with relative paths.

### 20.2. `DEPLOY_ME.md`
Plug-and-play instructions to deploy Foundation to a new project. Covers:
- Mandatory Q&A (framework, language).
- Gitignore pre-flight.
- Execution command: `python .agents/scripts/orion.py foundation deploy --target ... --framework ... --language ...`
- Safe Auto-Ingest (strictly forbidden to ingest the root directory).

### 20.3. `LEARNINGS.md`
**Collective memory.** YAML format per entry: `date`, `task_id`, `tier`, `severity`, `issue`, `root_cause`, `solution`, `debt_warning`. Contains real post-mortems (VRAM OOM, workflow violations, smart ingest architecture).

### 20.4. `EVOLUTION_LOG.jsonl`
Append-only genomic ledger. Each mutation, bug fix, and extracted pattern is written as a JSON line:
```json
{
  "timestamp": "2026-06-12T14:30:00Z",
  "mutation": "Banned usage of generic 'any' type in TS DTOs.",
  "friction_source": "Runtime crash on malformed JSON payload.",
  "fitness_delta": "+15%",
  "genome_hash": "a1b2c3d4e5"
}
```

### 20.5. `.genome.json` (139 bytes)
Genomic fingerprint that can be imported to a new project so the AI immediately inherits past lessons.

### 20.6. `.project_manifest.json` (70 bytes)
Project metadata: framework, language, project name.

### 20.7. `.deployed_ais` (414 bytes)
Registry of IDEs that have received Foundation deployment.

### 20.8. `.foundation_path` (47 bytes)
Absolute path to the `_foundation` repo. Used by deployment scripts.

---

