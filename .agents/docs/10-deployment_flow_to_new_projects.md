# VOLUME X: DEPLOYMENT FLOW TO NEW PROJECTS — Spoke Architecture

---

## Chapter 25: Pre-Flight Verification & Requirements Intake

Deploying the `.agents` foundation into a new or existing target codebase follows a strict 5-step operational pipeline to prevent repository corruption and index bloat.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Spoke Deployment Pipeline                       │
├─────────┬───────────────────────────┬──────────────────────────────────┤
│ Step 1  │ Pre-Flight Diagnostics    │ `orion.py preflight`             │
│ Step 2  │ Stack Identification      │ Determine framework and language │
│ Step 3  │ Gitignore Verification    │ Block build artifacts & secrets  │
│ Step 4  │ Scaffold & Resolution     │ `orion.py foundation deploy`     │
│ Step 5  │ Controlled Local Ingest   │ Safe targeted knowledge ingest   │
└─────────┴───────────────────────────┴──────────────────────────────────┘
```

---

### 25.1. Step 1: Pre-Flight Environment Diagnostics
Before initiating file copying or scaffolding, execute pre-flight checks in the host environment:
```bash
python .agents/scripts/orion.py preflight
```
The preflight script verifies:
- Python $\ge$ 3.10 runtime environment.
- SQLite3 with FTS5 module compilation.
- Cargo Rust `rtk` binary availability (or sets graceful fallback).
- Local Ollama service reachability (`http://127.0.0.1:11434`).

---

### 25.2. Step 2: Stack & Architecture Identification
Identify the target codebase configuration:
- Framework: `flutter`, `react`, `nextjs`, `python`, or `custom`.
- Language: `dart`, `typescript`, `python`, etc.
- Target AI IDEs: `gemini`, `cursor`, `claude`, `copilot`, `windsurf`, or `all` (19 supported IDE platforms).

If `.project_manifest.json` does not exist in the target directory, prompt the developer using native interactive questions.

---

### 25.3. Step 3: Gitignore Pre-Flight Gate
Scaffolding into a repository without proper ignore rules will cause the local RAG engine to index massive binary trees and sensitive keys. Ensure the target `.gitignore` contains:
```gitignore
# Dependencies & Build Artefacts
node_modules/
build/
.dart_tool/
dist/
target/

# Local Orion & Scratch State
.orion/orion.db*
.orion/working/
.agents/working/
*.pyc
__pycache__/

# Secrets & Environment Keys
.env*
*.pem
*.key
```

---

## Chapter 26: Scaffolding Execution & Placeholder Resolution

### 26.1. Deploying to Single or Multiple IDEs
Execute the modular foundation deployment command:

```bash
# Deploy to Gemini / Antigravity default:
python .agents/scripts/orion.py foundation deploy \
  --target /path/to/target_repo \
  --framework flutter \
  --language dart

# Deploy to multiple IDE environments:
python .agents/scripts/orion.py foundation deploy \
  --target /path/to/target_repo \
  --framework react \
  --language typescript \
  --ai cursor,claude,copilot

# Deploy with all 19 supported IDE adapters:
python .agents/scripts/orion.py foundation deploy \
  --target /path/to/target_repo \
  --framework react \
  --language typescript \
  --ai all
```

### 26.2. Dynamic Placeholder Resolution & Dependency-Aware Stack Resolver
During deployment, `commands/foundation.py` inspects the target project's actual manifests (`pubspec.yaml`, `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`) rather than copying static framework assumptions:
1. **Isolated Target Manifest Resolution (`effective_manifest`)**: Target project stack detection runs against an isolated manifest dictionary so spoke deployments never inherit the hub repository's own `.project_manifest.json`.
2. **Dependency-Aware Python Profiling (`_read_python_deps` & `_python_profile`)**: Parses `pyproject.toml` and `requirements*.txt` to classify Python projects into:
   - **`fastapi`**: Detected when `fastapi`, `starlette`, `litestar`, `flask`, or `django` is present.
   - **`pydantic`**: Detected when `pydantic`, `SQLAlchemy`, `sqlmodel`, or `msgspec` is present without a web framework.
   - **`stdlib`**: Pure Python CLI/library/tooling projects (`Zero-Pip` / `stdlib`, `dataclasses`, `unittest`, `sqlite3`) — preventing false `FastAPI` or `SQLAlchemy` claims in generated `BLUEPRINT.md`, `ARCHITECTURE.md`, and `MEMORY.md` context files.
3. **UI vs. Headless Detection (`_detect_ui_project`)**: Automatically suppresses `STYLE_GUIDE.md` generation for headless CLI, backend, and library repositories unless a frontend directory or UI framework is detected.
4. **Dual-Tier Canon Pruning (`prune_unmatched_canons`)**: Removes unselected framework directories in `.agents/canons/ecosystems/` and prunes unmatched cheat-sheets in `.agents/canons/micro/` (preserving only the target stack's micro-canons, e.g., keeping `python.md` on Python targets while removing `flutter.md`, `pubspec.md`, `react.md`, and `supabase.md`).
5. **Template Placeholder Substitution**:
   - `{{PROJECT_NAME}}`: Name of the target directory.
   - `{{FRAMEWORK}}` & `{{LANGUAGE}}`: Detected or explicitly passed target stack.
   - `{{API_STYLE}}`, `{{VALIDATION_ENGINE}}`, `{{DATABASE_ENGINE}}`, `{{STATE_STRATEGY}}`: Dynamically populated from the resolved stack profile.
   - `{{FOUNDATION_PATH}}`: Reference to the parent framework repository for upstream syncing.

### 26.3. 2-Step Non-Interactive Diagnostic Inspector (`orion.py setup --inspect --json`) & 6 Power-Features
For automated IDE onboarding (`DEPLOY_ME.md`), `orion.py setup --inspect --json` probes system RAM/VRAM, CPU cores, installed CLI binaries (`rtk`, `sg`, `bun`, `ollama`), and workspace stack in a single non-interactive JSON payload, then provisions up to 6 optional **Orion Power-Features** via `--features`:
- **`graph-db`**: Initializes `.orion/orion.db` (21-table SQLite WAL + FTS5 + Louvain GraphRAG schema).
- **`second-brain`**: Generates the 4-note executive developer briefing (`00-Home`, `01-Architecture-Map`, `02-Tech-Debt-Radar`, `03-Session-Timeline`).
- **`vault`**: Exports an Obsidian-compatible knowledge graph vault to `.orion/export/vault/`.
- **`design-md`**: Scaffolds `context/DESIGN.md` with locked visual tokens and WCAG contrast rules for UI projects.
- **`security-baseline`**: Generates `.agents/.security-baseline.json` to lock current AST security findings.
- **`pack-hybrid`**: Generates balanced `.orion/bundles/hybrid/` context bundles alongside `00_GEMINI_WEB_AUDIT_PROMPT.txt`.

### 26.4. The 19-Platform Universal IDE Manifest Matrix (`core/platform_manifests.py`)
`orion.py foundation deploy --ai <targets|all>` compiles native instruction files, rule adapters, and `PreToolUse` / wake hooks (`hooks.json`) across **19 AI coding platforms**:

| Platform ID | IDE / Agent Host | Generated Native Artifact(s) |
|:---|:---|:---|
| `gemini` | Google Antigravity / Gemini CLI | `AGENTS.md`, `GEMINI.md`, `.gemini/settings.json` |
| `claude` | Anthropic Claude Code | `CLAUDE.md`, `.claude/settings.local.json` (`PreToolUse` + `SessionStart` hooks) |
| `cursor` | Cursor IDE | `.cursor/rules/orion-foundation.mdc`, `.cursor/hooks.json` |
| `windsurf` | Codeium Windsurf | `.windsurfrules`, `.windsurf/rules/orion.md` |
| `copilot` | GitHub Copilot | `.github/copilot-instructions.md`, `.github/instructions/` |
| `cline` | Cline (VS Code) | `.clinerules/01-orion-foundation.md` |
| `roocode` | Roo Code | `.roo/rules/01-orion-foundation.md` |
| `kilocode` | Kilo Code | `.kilocode/rules/orion-foundation.md` |
| `zed` | Zed Editor | `.rules` |
| `aider` | Aider CLI | `.aider.conf.yml` (`read: [AGENTS.md]`) |
| `continue` | Continue.dev | `.continue/rules/orion-foundation.md` |
| `trae` | ByteDance Trae IDE | `.trae/rules/project_rules.md` |
| `junie` | JetBrains Junie | `.junie/guidelines.md` |
| `kiro` | AWS Kiro IDE | `.kiro/steering/orion-foundation.md` |
| `codex` | OpenAI Codex CLI | `AGENTS.md` |
| `opencode` | OpenCode CLI | `AGENTS.md`, `.opencode/config.json` |
| `amp` | Sourcegraph Amp | `AGENT.md` |
| `goose` | Block Goose | `.goosehints` |
| `pearai` | PearAI | `.pearai/rules/orion-foundation.md` |

---

## Chapter 27: Safe Knowledge Ingestion & Bidirectional Sync

### 27.1. Safe Targeted Ingestion
Once files are scaffolded, seed the local `.orion/orion.db` database:
```bash
python .agents/scripts/orion.py orion_ops ingest \
  .agents/rules .agents/skills .agents/canons context/
```

> [!CAUTION]
> **STRICTLY FORBIDDEN**: Running `orion_ops ingest .` or `orion_ops ingest` without arguments. Ingesting the root directory indiscriminately attempts to parse binary assets, lock the SQLite database, and inflate the index with irrelevant build logs.

---

### 27.2. Bidirectional Knowledge Synchronization

```
┌────────────────────────────────────────────────────────┐
│               Master Hub (Framework Repo)              │
└──────────────┬──────────────────────────▲──────────────┘
               │                          │
  foundation   │                          │  push-upstream
   sync-ai     │                          │  (evolved rules)
               ▼                          │
┌─────────────────────────────────────────┴──────────────┐
│             Target Spoke (Active Project)              │
└────────────────────────────────────────────────────────┘
```

#### Sync Downward (Hub to Spoke)
When the master Foundation framework is updated with new skills or security patches:
```bash
python .agents/scripts/orion.py foundation sync-ai --target /path/to/spoke_project
```

#### Push Upward (Spoke to Hub)
When a spoke project discovers bug patterns, resolves edge cases, or refines canons, push those improvements back to the central repository:
```bash
python .agents/scripts/orion.py foundation push-upstream --source /path/to/spoke_project
```

---

### 27.3. Sovereign Surgical Upstream Upgrade (`orion upgrade`)

When a spoke project needs to pull core engine and framework improvements from the Upstream Hub without clobbering local custom configuration, use the sovereign surgical upgrade engine:

```bash
# Preview changes safely without modifying disk
python .agents/scripts/orion.py upgrade --check

# Execute surgical upgrade from upstream git repository or local hub
python .agents/scripts/orion.py upgrade --source https://github.com/Echo-Scion/portable-brainvibing.git
```

**Key Architectural Invariants**:
1. **Sacred File Shield**: Strictly prevents any mutation to sovereign downstream assets (`context/**`, `.orion/**`, `.agents/working/`, local project canons, and custom rule additions).
2. **Surgical BIOS Splicing**: Merges upstream guardrails into `AGENTS.md` and `GEMINI.md` while preserving custom `## PROJECT-SPECIFIC MANDATES` intact.
3. **Atomic Two-Phase Rollback**: Stages files in memory and temporary buffers, runs `verify_agents`, and automatically rolls back if any gate fails (`Exit Code != 0`).
