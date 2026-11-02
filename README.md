<div align="center">

# 🧠 Portable Brainvibing (`.agents`)

### Turnkey Auto-Vibe Coding Brain & Cognitive Runtime for Autonomous AI Agents

<p align="center">
  <b>Turn probabilistic coding AIs into deterministic, self-verifying software engineers.</b><br>
  Deploy across separate workspace-level brain, local, zero-pip, zero runtime.
</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/version-v0.0.5-blue.svg?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/core-Python%203.10%2B%20Stdlib-brightgreen.svg?style=flat-square" alt="Core"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/database-SQLite3%20WAL-informational.svg?style=flat-square" alt="Database"></a>
  <a href="PREREQUISITES.md"><img src="https://img.shields.io/badge/dependencies-Zero%20Pip-critical.svg?style=flat-square" alt="Zero-Pip"></a>
  <a href="#-quickstart"><img src="https://img.shields.io/badge/deployment-Multi--Platform-orange.svg?style=flat-square" alt="Platforms"></a>
  <a href="https://github.com/Echo-Scion"><img src="https://img.shields.io/badge/author-Echo--Scion-purple.svg?style=flat-square" alt="Author"></a>
</p>

> ⚠️ **Status**: Active research and development project; currently tested on personal developer workflows and not yet recommended for production environments.
>
> 💡 **Notice**: Co-developed through human-AI pair programming and audited with automated verification gates and multi-model reviews (Gemini 4 Argon). If any rights or attribution concerns arise, please reach out and they will be addressed promptly.

<p align="center">
  <a href="#-quickstart"><b>Quickstart</b></a> •
  <a href="#-whats-inside-agents-the-8-core-features"><b>Core Features</b></a> •
  <a href="#-the-four-anchored-pillars"><b>4 Pillars</b></a> •
  <a href="#-unified-command--agent-prompt-reference"><b>CLI & Prompts</b></a> •
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

<a id="-whats-inside-agents-the-8-core-features"></a>
## 🛠️ What's Inside `.agents` (The 8 Core Subsystems)

Every subsystem addresses a systemic failure mode of autonomous AI coding through a single zero-dependency CLI entry point: `python .agents/scripts/orion.py <command>`.

### 1. 🧠 Cognitive Memory & Local GraphRAG (`brain.py`, `rag.py`)
* **Problem**: AI agents suffer from episodic amnesia across sessions, hallucinate from superseded architectural decisions, lose contextual continuity as chat history is truncated, and risk leaking sensitive intellectual property when forced to use third-party cloud vector databases.
* **How it Works**: Implements a zero-cloud, 100% local Dual-Level GraphRAG engine combining SQLite3 WAL FTS5 BM25 lexical search, vector similarity, and pure-Python Louvain community clustering. Raw session turns compress into anchored observations (`[O1]`) that roll over into generational memory (`memory_generations`) with Shannon surprisal filtering and `superseded_by` anti-flashback tracking.
* 📖 *Deep Dive: [.agents/docs/03-local_rag_brain.md](.agents/docs/03-local_rag_brain.md)*

### 2. 🌌 Multi-Project Portfolio Mesh (`commands/constellation.py`, `core/spoke_mesh.py`)
* **Problem**: Developers and teams manage multiple interconnected projects, services, or micro-repositories, but AI assistants operate in isolated repository silos—unaware of shared data models, upstream API contracts, or living architectural health across the broader portfolio.
* **How it Works**: Automatically discovers sibling project repositories across a workspace portfolio (the `Constellation` spoke mesh). Tracks individual project health scorecards, validates cross-project architectural boundaries, syncs shared standards without coupling git trees, and projects a unified second-brain knowledge mesh into interoperable Obsidian vaults.
* 📖 *Deep Dive: [.agents/docs/03-local_rag_brain.md](.agents/docs/03-local_rag_brain.md)*

### 3. 🧭 Master BIOS, JIT Router & Communication Protocols (`AGENTS.md`, `rules/`, `lessword`)
* **Problem**: Massive static system prompts trigger "Lost in the Middle" attention degradation, models waste 60%–80% of their output tokens on polite filler and bureaucratic hedging, and behavior diverges wildly across fragmented AI IDEs (Antigravity, Cursor, Claude Code, VS Code).
* **How it Works**: Anchors autonomous behavior in a single Master BIOS (`AGENTS.md`) with a 33-row Just-In-Time (JIT) knowledge router that loads targeted procedural runbooks on Turn 1 and deploys lightweight pointer adapters (`GEMINI.md`, `CLAUDE.md`) across 19 supported AI coding hosts. Enforces the Lessword communication protocol (ASD-STE100 concise engineering English cutting token bloat by ~75%) and mandates a deterministic 4-line Response Footer with explicit model tier recommendations.
* 📖 *Deep Dive: [.agents/docs/04-rule_library___rules.md](.agents/docs/04-rule_library___rules.md)*

### 4. 🧬 Living Architectural DNA & Dynamic SemVer (`core/dna.py`)
* **Problem**: Multi-tier architectures degrade over time through illegal cross-layer imports (e.g. presentation directly querying databases), brownfield codebases resist rigid framework directory renames, and version numbers drift inconsistently across manifests, build codes, badges, and documentation.
* **How it Works**: Continuously classifies repository files into 5 canonical architectural tiers (`contracts`, `domain`, `services`, `state`, `presentation`), blocking upward layer leaks and non-destructively mapping brownfield directory layouts via Epigenetic Aliases. Dynamically calculates polyglot SemVer impact from git diff AST strata and atomically bumps release manifests (`package.json`, `pubspec.yaml`, `Cargo.toml`, Gradle, badges, roadmaps).
* 📖 *Deep Dive: [.agents/docs/02-system_architecture.md](.agents/docs/02-system_architecture.md)*

### 5. 📐 Pre-Implementation Blueprint Rigor (`project-architect`, `integrity-sentinel`)
* **Problem**: Autonomous agents jump straight into writing code before verifying viability, leading to broken assumptions, missing schema contracts, undetected race conditions, and silent regression loops.
* **How it Works**: Enforces pre-implementation rigor through 8 Core Viability Questions, an interactive spec-alignment interview (`/grill-me`), a 5-Stage Blueprint Review Pipeline, isolated reviewer subagents, and automated Spec-to-Code Drift detection that verifies parity between planned contracts and actual AST implementations.
* 📖 *Deep Dive: [.agents/docs/02-system_architecture.md](.agents/docs/02-system_architecture.md)*

### 6. 🍱 Sequential Execution Harness & Bento Task Slicer (`bento_slicer.py`)
* **Problem**: Frontier and budget models lose track of complex multi-file implementation plans, hallucinate outdated line numbers, skip intermediate edits, or corrupt files during large unstructured code generations.
* **How it Works**: Decomposes large plans into atomic, single-step Bento Action Cards (`ACTIVE_TASK.md`) sorted by topological blast-radius ($T_0 \to T_5$) and bottom-up file position. Recalibrates live disk line spans before every modification and enforces a Post-Condition Disk Mutation Gate (`Exit Code 2` on skips) before advancing.
* 📖 *Deep Dive: [.agents/docs/06-workflow___sop.md](.agents/docs/06-workflow___sop.md)*

### 7. 🛡️ Exoskeleton Safety & AST Quality Sentinels (`capabilities.py`, `sandbox.py`, `scanner.py`, `verify_agents.py`)
* **Problem**: Agents get trapped in runaway tool-failure loops, silently mask errors with empty catch blocks, read full bloated files that burn context budgets, and allow hidden credentials or Trojan Unicode to slip into production commits.
* **How it Works**: Enforces a 3-strike `PreToolUse` circuit breaker, a PEP 578 syscall-jailed Python sandbox, and `@mechanical_catch` exception boundaries. Hollows code into PageRank-ranked AST skeletons (`scan map`), runs a Consequence Verifier checking real DOM/widget, database, network, and layout mutations alongside delta-scoped git-diff mutation tests and an 8-gate mechanical repository audit (`orion.py verify`).
* 📖 *Deep Dive: [.agents/docs/07-python_scripts___scripts.md](.agents/docs/07-python_scripts___scripts.md)*

### 8. 🌱 Habit Evolution, Production Canons & Design Craft Floor (`reflexion.py`, `core/harness/`, `ui-finish`)
* **Problem**: Coding models repeat the exact same mistakes across sessions, recurring manual developer workflows go unautomated, generated UIs suffer from generic AI slop and inconsistent spacing, and teams lack verified framework architecture patterns.
* **How it Works**: Intercepts runtime friction into an Observation Ledger, automatically escalating repeat violations into Tier-0 mechanical barriers, while mining recurring CLI sequences into automated workflows. Governs skill lifecycle through an in-tree Sovereign Skill Harness with 14-gate admission promotion. Provides production framework canons (Flutter 120Hz Impeller, React, Python) paired with W3C DTCG design tokens (`DESIGN.md`), 60+ canonical UI primitives, and automated WCAG 2.1 AA aesthetics evaluation (`audit_aesthetics.py`).
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

<a id="-unified-command--agent-prompt-reference"></a>
## 💻 Unified Command & Agent Prompt Reference

You can either run commands directly via the unified `orion.py` CLI or copy-paste natural language prompts directly into your AI coding assistant (Antigravity, Claude Code, Cursor, Copilot, Gemini CLI):

| Domain / Intent | Say This in Chat (AI Prompt) | CLI Command (`orion.py`) |
| :--- | :--- | :--- |
| **New Project Setup** | `"Setup .agents for this new project and start in draft mode"` | `python .agents/scripts/orion.py setup --inspect` |
| **Brownfield Onboarding** | `"Scan my existing codebase, harvest our theme tokens, and setup .agents"` | `python .agents/scripts/orion.py setup` |
| **Health & 4 Pillars Audit** | `"Check .agents health, active pillars, and environment status"` | `python .agents/scripts/orion.py doctor` |
| **Mechanical Repository Audit** | `"Run the 8-gate mechanical, ceiling, and portability audit"` | `python .agents/scripts/orion.py verify` |
| **Project DNA Architecture Audit** | `"Audit our project DNA to verify 5-tier architecture layer boundaries"` | `python .agents/scripts/orion.py dna audit` |
| **Dynamic Polyglot SemVer** | `"Calculate SemVer impact across 5-tier strata and bump manifests"` | `python .agents/scripts/orion.py dna bump --auto` |
| **Bento Task Slicing** | `"Slice implementation plan into topological tasks and emit active card"` | `python .agents/scripts/orion.py bento init plan.md` |
| **Bento Step & Gate Verification** | `"Verify disk mutation, run verification gate, and step to next task"` | `python .agents/scripts/orion.py bento next --verify` |
| **AST Skeleton & Line Mapping** | `"Extract AST skeletons and symbol line spans to inspect without paging"` | `python .agents/scripts/orion.py scan map src/` |
| **PageRank Repo Map** | `"Generate PageRank-ranked core symbols within a 1500-token budget"` | `python .agents/scripts/orion.py repomap --budget 1500` |
| **Token Consumption Audit** | `"Audit repository files to find the largest token-consuming files"` | `python .agents/scripts/orion.py scan tokens` |
| **Cognitive Memory & RAG Search** | `"Sync memory knowledge graph for auth token flow using hybrid RAG"` | `python .agents/scripts/orion.py brain sync "auth token flow"` |
| **Expand Anchor Recall** | `"Expand raw recall turns behind memory anchor O1"` | `python .agents/scripts/orion.py brain recall O1` |
| **Generational Memory Rollover** | `"Trigger zero-LLM generational memory rollover with Shannon surprisal"` | `python .agents/scripts/orion.py brain rollover` |
| **Obsidian Vault Export** | `"Export our local second-brain knowledge graph to Obsidian vault format"` | `python .agents/scripts/orion.py brain export-vault` |
| **Portfolio Mesh Discovery** | `"Discover sibling repositories across the portfolio and audit scorecards"` | `python .agents/scripts/orion.py constellation status` |
| **Portfolio Knowledge Sync** | `"Export cross-project portfolio knowledge mesh across sibling repositories"` | `python .agents/scripts/orion.py constellation sync` |
| **Habit & Friction Observation** | `"Record developer friction or recurring bug pattern in observations"` | `python .agents/scripts/orion.py observe "fix" --target rules` |
| **Temporal Session Synthesis** | `"Run Temporal Pulse session synthesis and mine recurring habits"` | `python .agents/scripts/orion.py consolidate session` |
| **Design Archetype Selection** | `"Lock our design archetype to Dark Industrial and flatten DESIGN.md"` | `python .agents/scripts/orion.py design select dark-industrial` |
| **Design Token Harvesting** | `"Harvest theme tokens from our code and tell me the inferred archetype"` | `python .agents/scripts/orion.py design infer` |
| **UI Aesthetics & Anti-Slop Audit** | `"Audit UI tokens, 8pt spatial grid, and prose anti-slop rules"` | `python .agents/scripts/orion.py eval --dir src/` |
| **AST Security & Secret Scan** | `"Scan codebase for AST vulnerabilities, secrets, and Trojan Unicode"` | `python .agents/scripts/orion.py scan security .` |
| **Delta Mutation Testing** | `"Run delta-scoped AST mutation testing against our recent git diff"` | `python .agents/scripts/orion.py adversarial mutate <f> --diff` |
| **Context Bundling for Web Audits** | `"Pack codebase into at most 10 balanced Markdown bundles for web review"` | `python .agents/scripts/orion.py pack [arch|hybrid|full|pr]` |
| **AI Host Adapters Sync** | `"Generate thin GEMINI.md and CLAUDE.md adapters linked to AGENTS.md"` | `python .agents/scripts/orion.py sync-ai --target . --ai gemini,claude` |
| **Safe Upstream Upgrade** | `"Surgically upgrade .agents from upstream while shielding sovereign state"` | `python .agents/scripts/orion.py upgrade` |
| **Deploy to Downstream Spoke** | `"Deploy complete foundation engine to downstream target repository"` | `python .agents/scripts/orion.py deploy --target <dir>` |

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
