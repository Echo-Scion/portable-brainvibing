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
- Target AI IDEs: `gemini`, `cursor`, `claude`, `copilot`, `windsurf`, or `all`.

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

# Deploy with all 6 supported IDE adapters:
python .agents/scripts/orion.py foundation deploy \
  --target /path/to/target_repo \
  --framework react \
  --language typescript \
  --ai all
```

### 26.2. Dynamic Placeholder Resolution
During deployment, `commands/foundation.py` resolves dynamic placeholders across templates:
- `{{PROJECT_NAME}}`: Name of the target directory.
- `{{FRAMEWORK}}`: Selected framework canon.
- `{{LANGUAGE}}`: Target programming language.
- `{{FOUNDATION_PATH}}`: Absolute reference to the parent `_foundation` repository for upstream syncing.

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
│             Master Hub (_foundation repo)              │
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
