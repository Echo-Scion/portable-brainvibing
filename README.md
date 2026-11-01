<div align="center">

# 🧠 Portable Brainvibing (`.agents`)

### Turnkey Auto-Vibe Coding Brain & Cognitive Runtime for Autonomous AI Agents

<p align="center">
  <b>Turn probabilistic coding AIs into deterministic, self-verifying software engineers.</b><br>
  Deploy across separate workspace-level brain, local, zero-pip, zero runtime.
</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/version-v0.0.4-blue.svg?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/core-Python%203.10%2B%20Stdlib-brightgreen.svg?style=flat-square" alt="Core"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/database-SQLite3%20WAL-informational.svg?style=flat-square" alt="Database"></a>
  <a href="PREREQUISITES.md"><img src="https://img.shields.io/badge/dependencies-Zero%20Pip-critical.svg?style=flat-square" alt="Zero-Pip"></a>
  <a href="#-quickstart"><img src="https://img.shields.io/badge/deployment-Multi--Platform-orange.svg?style=flat-square" alt="Platforms"></a>
  <a href="https://github.com/Echo-Scion"><img src="https://img.shields.io/badge/author-Echo--Scion-purple.svg?style=flat-square" alt="Author"></a>
</p>

> ⚠️ **Warning**: Being tested only on personal workflows; this project is currently in active development and has not yet been used to build any production project.
>
> 🛑 **Notice**: 100% AI-generated slop, side project for personal use. AI-audited with Gemini 4 Argon. Sources/origins are unknown; if any rights are offended, please remind me and it will be removed/addressed promptly.

<p align="center">
  <a href="#-quickstart"><b>Quickstart</b></a> •
  <a href="#-whats-inside-agents-the-6-core-features"><b>Core Features</b></a> •
  <a href="#-the-four-anchored-pillars"><b>4 Pillars</b></a> •
  <a href="#-essential-cli-commands-orionpy"><b>CLI Commands</b></a> •
  <a href="CHANGELOG.md"><b>Changelog</b></a>
</p>

</div>

---

### 🛡️ Provenance & Operational Baseline

| Dimension | Specification |
| :--- | :--- |
| **Primary Runtime** | Being tested only on **Google Antigravity IDE**, **Android Studio**, and **VS Code**. |
| **Self-Hosted Engineering** | Constructed and maintained using `.agents` itself under AI pair-programming and automated verification gates. |
| **Adversarial Verification** | AI-audited with **Gemini 4 Argon** and multi-model frontier reviews to verify AST integrity, eliminate dead abstractions, and close concurrency hazards. |
| **Modular Gateway CLI** | Unified `orion.py` dispatcher routing across 9 focused CLI engines (`brain.py`, `bento_slicer.py`, `compact.py`, `rag.py`, `vault.py`, `foundation.py`, `state_machine.py`, `reflexion.py`, `verify_agents.py`). |
| **Air-Gapped Sovereignty** | Zero background daemons, zero external cloud telemetry, zero socket listeners, and zero mandatory `pip` packages. |

---

<a id="-whats-inside-agents-the-6-core-features"></a>
## 🛠️ What's Inside `.agents` (The 6 Core Subsystems)

Every subsystem addresses a specific failure mode of standard AI coding through a single zero-dependency CLI entry point: `python .agents/scripts/orion.py <command>`.

### 1. 🧠 Hybrid Memory & GraphRAG (`brain.py`, `rag.py`)
* **Problem**: AI agents forget context between sessions or hallucinate from outdated architectural decisions.
* **How it Works**: Combines SQLite3 FTS5 lexical search, local vector embeddings, and entity relationship graphs without cloud dependencies. Automatically filters out superseded historical decisions, exports an Obsidian second-brain vault, and discovers multi-project star repositories via Constellation.
* 📖 *Deep Dive: [.agents/docs/03-local_rag_brain.md](.agents/docs/03-local_rag_brain.md)*

### 2. 🍱 Bento Task Slicer (`bento_slicer.py`)
* **Problem**: Models easily lose track of complex multi-file plans, skip intermediate edits, or hallucinate line numbers.
* **How it Works**: Slices implementation plans into atomic, single-step cards (`ACTIVE_TASK.md`) ordered by architectural dependency. Re-anchors line numbers on disk and mechanically verifies file mutations before advancing.
* 📖 *Deep Dive: [.agents/docs/06-workflow___sop.md](.agents/docs/06-workflow___sop.md)*

### 3. 🔍 AST Code Intelligence & Quality Gates (`scanner.py`, `verify_agents.py`)
* **Problem**: Reading large files in full burns token context, while unverified changes introduce security flaws and regressions.
* **How it Works**: Extracts PageRank-ranked AST skeletons so models read only relevant symbol spans. Runs delta-scoped mutation tests on git diffs and enforces an 8-gate mechanical integrity audit.
* 📖 *Deep Dive: [.agents/docs/07-python_scripts___scripts.md](.agents/docs/07-python_scripts___scripts.md)*

### 4. 📦 Universal Project DNA & Polyglot Versioning (`core/dna.py`, `utils/packer.py`)
* **Problem**: Large codebases exceed web context windows, and versioning drifts between manifests, code, and documentation.
* **How it Works**: Partitions polyglot codebases into balanced Markdown bundles for web LLM audits. Dynamically synchronizes SemVer across manifests (`package.json`, `pubspec.yaml`, `Cargo.toml`, etc.), unconventional files (`version.txt`, `Makefile`), and README badges (`orion dna bump`), while purifying AI writing tells.
* 📖 *Deep Dive: [.agents/docs/02-system_architecture.md](.agents/docs/02-system_architecture.md)*

### 5. 🛡️ State Recovery & Latency-Optimized Hooks (`state_machine.py`, `capabilities.py`)
* **Problem**: IDE restarts wipe in-progress context, failing tool loops waste tokens, and constant state rewrites invalidate prompt caches.
* **How it Works**: Preserves editor context across restarts with a 5-minute hash gate protecting LLM prompt-cache hits. Intercepts failing tool loops with a 3-strike circuit breaker and provides Git-bound checkpoints for instant rollback.
* 📖 *Deep Dive: [.agents/docs/02-system_architecture.md](.agents/docs/02-system_architecture.md)*

### 6. 🧬 Habit Observation, Canons & Design Standards (`reflexion.py`, `ui-finish`)
* **Problem**: Agents repeat identical mistakes across sessions and produce generic, robotic UI layouts.
* **How it Works**: Captures runtime friction into an observation ledger, automatically escalating repeat mistakes into Tier-0 mechanical barriers. Provides production framework canons (Flutter, React, Python) paired with Google Labs `design.md` W3C DTCG design tokens and canonical UI component taxonomies.
* 📖 *Deep Dive: [.agents/docs/09-darwinian_evolution_lifecycle.md](.agents/docs/09-darwinian_evolution_lifecycle.md)*

---

<a id="-the-four-anchored-pillars"></a>
## 🏛️ The Four (4) Anchored Pillars & Hybrid Cognition

`.agents` separates mechanical computation from cognitive reasoning across a 4-tier hybrid model (Tier 0: Deterministic Python/Rust/SQLite stdlib $\to$ Tier 1: Local Neural Coprocessor $\to$ Tier 2: Frontier Cloud LLMs $\to$ Tier 3: Human Operator). Frontier models architect systems and invariant guards, while local tools and on-device models handle zero-cost iteration and mechanical verification.

The runtime works out-of-the-box with **only Python 3.10+**. Optional native binaries unlock hardware acceleration and fall back to pure Python stdlib when absent:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            Master BIOS (AGENTS.md)                         │
│        33-Row JIT Knowledge Router • Iron Evidence Law • Lessword Mode     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                      Unified CLI Gateway (orion.py)                        │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│ PILLAR 1 (Floor) │ PILLAR 2 (Rust)  │ PILLAR 3 (Local) │ PILLAR 4 (JS/TS)  │
│ Python 3.10+     │ rtk + ast-grep   │ Ollama/llama.cpp │ Bun Runtime       │
│ Stdlib & SQLite3 │ difft + gitleaks │ Neural Embeddings│ Biome Formatter   │
│ WAL Architecture │ jujutsu (jj VCS) │ Triplet Miner    │ Fast TS & MCP     │
├──────────────────┼──────────────────┼──────────────────┼───────────────────┤
│  ALWAYS ACTIVE   │ Fallback: Python │ Fallback: SQLite │ Fallback: Host    │
│  Zero pip deps   │ difflib+re+stash │ FTS5 Porter BM25 │ runner / Node/Py  │
└──────────────────┴─────────┬────────┴──────────────────┴───────────────────┘
                             │ Accelerated by
┌────────────────────────────▼───────────────────────────────────────────────┐
│ TIER 2: Optional Ephemeral Accelerators (~/.agents/cache/venv & PATH)      │
│ • sqlite-vec (SIMD Vector KNN)       • model2vec (Static CPU Embeddings)   │
│ • tokenizers (Exact Rust BPE)        • duckdb (Stateless In-Memory OLAP)   │
│ • orjson (Fast SIMD JSON)            • rapidfuzz (Fast C++ Levenshtein)    │
│ • tree-sitter (Concrete Syntax Tree) • difftastic / gitleaks / jujutsu     │
│ Strictly isolated in user home cache; zero host workspace contamination.   │
└────────────────────────────────────────────────────────────────────────────┘
```

Check your machine's active pillars and Tier 2 accelerators at any time:
```bash
python .agents/scripts/orion.py doctor
python .agents/scripts/orion.py preflight --pillars
```

---

<a id="-quickstart"></a>
## 🚀 Quickstart & Hub-and-Spoke Topology

`.agents` operates in a **Hub-and-Spoke** topology: the **Upstream Hub** (`<foundation_path>`) develops and validates master templates/scripts, while **Downstream Spokes** (your application repositories) consume `.agents/` and push evolved patterns back upstream.

### 1. Operating in a Downstream Spoke Project (Your App)

#### Step A: Install `.agents` into your project
```bash
# Option 1: Clone directly as .agents
git clone https://github.com/Echo-Scion/portable-brainvibing.git .agents

# Option 2: Deploy from a local Upstream Hub on your machine
python /path/to/<foundation_path>/.agents/scripts/orion.py deploy --target <project_path>
```

#### Step B: Run Setup (Human vs AI Agent)
* **For Humans (Interactive Terminal Wizard)**:
  ```bash
  python .agents/scripts/orion.py setup
  ```
* **For AI Agents in Chat (Headless Mode — `isatty() == False`)**:
  ```bash
  python .agents/scripts/orion.py setup --inspect --json
  python .agents/scripts/orion.py setup --yes --enable graph-db,second-brain,vault
  ```
* **Fast Health Check**:
  ```bash
  python .agents/scripts/orion.py doctor
  ```

#### Step C: Surgically Upgrading Downstream Spokes
Keep downstream spoke projects synchronized with upstream framework updates without clobbering sovereign assets (`context/**`, `.orion/**`, local rules/skills, and `## PROJECT-SPECIFIC MANDATES`):
```bash
# Preview changes safely without modifying disk
python .agents/scripts/orion.py upgrade --check

# Execute surgical upgrade from upstream GitHub repository or local path
python .agents/scripts/orion.py upgrade --source https://github.com/Echo-Scion/portable-brainvibing.git
```

### 2. Operating in the Upstream Foundation Hub (`<foundation_path>`)
```bash
# Verify Hub mechanical & architectural integrity
python .agents/scripts/orion.py verify

# Deploy updated Foundation to a downstream spoke project
python .agents/scripts/orion.py deploy --target <project_path>

# Sync hardened rules/canons from a spoke back to the Hub
python .agents/scripts/orion.py foundation push-upstream --project <project_path>
```

---

<a id="-essential-cli-commands-orionpy"></a>
## 💻 Essential CLI Commands (`orion.py`)

```bash
# --- Bento Task Slicer (Sequential Execution Harness for Budget/Standard Models) ---
python .agents/scripts/orion.py bento init plan.md          # Slice plan into topological tasks & emit ACTIVE_TASK.md
python .agents/scripts/orion.py bento next --verify         # Verify disk patch + run gate + advance to next task
python .agents/scripts/orion.py bento status                # Inspect task progress across T0-T5 strata

# --- Code Intelligence & Context Mapping ---
python .agents/scripts/orion.py scan map src/               # Extract [Lstart-Lend] AST skeletons
python .agents/scripts/orion.py repomap --budget 1500        # PageRank-ranked core symbols within token budget
python .agents/scripts/orion.py scan tokens                 # Audit largest token-consuming files

# --- Knowledge Graph, Hybrid RAG, Constellation & Observational Memory ---
python .agents/scripts/orion.py brain sync "auth token flow" # Hybrid FTS5 + Vector + 1-Hop + Louvain RAG
python .agents/scripts/orion.py brain recall O1             # Expand raw recall turns behind anchor [O1]
python .agents/scripts/orion.py brain rollover              # Trigger zero-LLM generational memory rollover
python .agents/scripts/orion.py graph path UserAuth TokenStore # Shortest BFS dependency path between entities
python .agents/scripts/orion.py brain export-vault          # Export Obsidian Vault to .orion/export/vault/
python .agents/scripts/orion.py constellation status        # Discover sibling spoke projects & living DNA scorecards
python .agents/scripts/orion.py constellation sync          # Export supervisory multi-project knowledge mesh to constellation/

# --- Habit Observation & Self-Evolution ---
python .agents/scripts/orion.py observe "fix" --target rules # Record friction or pattern in OBSERVATIONS.md
python .agents/scripts/orion.py resolve 12 --status actioned # Resolve & archive completed observation #12
python .agents/scripts/orion.py consolidate session         # Run Temporal Pulse session synthesis & habit mining

# --- Quality, Security & Architecture Gates ---
python .agents/scripts/orion.py verify                      # Run 8-gate mechanical, ceiling & portability audit
python .agents/scripts/orion.py dna audit                   # Audit 5-tier architecture compliance & layer leaks
python .agents/scripts/orion.py scan security .             # AST vulnerability, secret & Trojan Unicode scan
python .agents/scripts/orion.py adversarial mutate <f> --diff # Delta-scoped AST mutation testing on git diff
python .agents/scripts/orion.py eval --dir src/             # Audit UI tokens, 8pt grid & prose anti-slop

# --- Universal Project DNA SemVer & Context Packaging ---
python .agents/scripts/orion.py dna semver                  # Dynamic polyglot SemVer impact radar (5-Tier strata)
python .agents/scripts/orion.py dna bump --auto             # Atomic release bump across manifests, build codes & sinks
python .agents/scripts/orion.py pack [arch|hybrid|full|pr]  # Export codebase into <=10 balanced Markdown bundles

# --- Foundation Hub-and-Spoke & Upstream Upgrade ---
python .agents/scripts/orion.py upgrade --check            # Preview upstream engine updates without writing to disk
python .agents/scripts/orion.py upgrade                    # Surgically update framework while shielding sovereign state
python .agents/scripts/orion.py deploy --target <dir>      # Deploy complete foundation to target repository
```

---

## 🎖️ Credits & Architectural Inspirations

`.agents` is architected with a strict **100% Zero-Pip Floor Sovereignty** invariant (pure Python 3.10+ stdlib & SQLite3 WAL), drawing conceptual inspiration and optional execution acceleration from outstanding open-source projects:

* **Conceptual Inspirations**: [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (CLI proxy noise filtering), [caveman](https://github.com/Echo-Scion/caveman) (high-density communication evolved into `lessword`), [ast-grep](https://github.com/ast-grep/ast-grep) (structural CST search), [paul-gauthier/aider](https://github.com/paul-gauthier/aider) (PageRank repo-map packing), [microsoft/graphrag](https://github.com/microsoft/graphrag) & [graphify](https://github.com/Echo-Scion/graphify) (community clustering + entity graph retrieval), [Obsidian](https://obsidian.md) (wikilink graph interoperability), [The Component Gallery](https://component.gallery/) (canonical UI component taxonomy by Iain Bean), and Google DeepMind AutoHarness (deterministic action-verification gates).
* **Anchored Pillars & Accelerators**:
  - **Pillar 2 (Rust)**: [rtk](https://github.com/rtk-ai/rtk) (CLI proxy), [ast-grep](https://github.com/ast-grep/ast-grep) (structural search), [difftastic](https://github.com/Wilfred/difftastic) (syntax diffing), [gitleaks](https://github.com/gitleaks/gitleaks) (secret scanning), and [jujutsu (`jj`)](https://github.com/martinvonz/jj) (anonymous working-copy VCS).
  - **Pillar 3 (Local)**: [Ollama](https://github.com/ollama/ollama) and [llama.cpp](https://github.com/ggerganov/llama.cpp) (local neural coprocessing and background embeddings).
  - **Pillar 4 (JS/TS)**: [Bun](https://github.com/oven-sh/bun) and [Biome](https://github.com/biomejs/biome) (fast JS/TS runtime, MCP server spawning, and web linting).
  - **Tier 2 Accelerators**: [sqlite-vec](https://github.com/asg017/sqlite-vec) (KNN vector search), [model2vec](https://github.com/MinishLab/model2vec) (static CPU embeddings), [tokenizers](https://github.com/huggingface/tokenizers) (BPE counting), [duckdb](https://github.com/duckdb/duckdb) (in-memory OLAP), [orjson](https://github.com/ijl/orjson) (fast JSON), [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz) (Levenshtein matching), and [tree-sitter](https://github.com/tree-sitter/tree-sitter) (concrete syntax trees).

---

## 👥 Contributors

* [@Echo-Scion](https://github.com/Echo-Scion) — Core maintainer & architecture
* **Google Gemini** (AI Pair Programmer) — Architecture drafting, test generation & refactoring

---

## 📄 License

Distributed under the [MIT License](LICENSE).
