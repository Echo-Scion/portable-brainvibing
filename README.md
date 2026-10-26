<div align="center">

# 🧠 Portable Brainvibing (`.agents`)

### Turnkey Auto-Vibe Coding Brain & Cognitive Runtime for Autonomous AI Agents

<p align="center">
  <b>Turn probabilistic coding AIs into deterministic, self-verifying software engineers.</b><br>
  Deploy across separate workspace-level brain, local, zero-pip, zero runtime.
</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/version-v0.0.2-blue.svg?style=flat-square" alt="Version"></a>
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

Every subsystem addresses a specific failure mode of standard AI coding and runs through a single zero-dependency CLI entry point: `python .agents/scripts/orion.py <command>`.

### 1. 🧠 Dual-Level GraphRAG & Observational Memory (`brain.py`, `rag.py`, `vault.py`, `core/memory.py`)
* **Problem Solved**: Standard AI agents suffer from cross-session amnesia and RAG "flashbacks" where outdated, superseded architectural decisions pollute current retrieval.
* **Hybrid Graph Retrieval**: Combines SQLite3 FTS5 Porter BM25 lexical search, local float32 vector embeddings (`archival_vectors`), 1-hop entity-relation traversal, and pure-Python Louvain modularity community clustering.
* **In-Place Schema Auto-Migration**: Automatically detects and migrates legacy databases in-place, adding `superseded_by` and `generation_id` columns across `pages` and `archival_vectors` tables without data loss.
* **3-Tier Epistemic Compression Funnel**: Progressively distills raw session turns (`recall_turns`) into an active observation ledger with ephemeral anchor IDs (`[O1]`–`[On]`) under a dynamic token budget (`max(3600, total // 2)`), and rolls older generations into a single Head Reflection (`memory_generations`) using zero-LLM Shannon Surprisal scoring.
* **Anti-Flashback Supersession (`superseded_by`)**: Historical records replaced by newer generations are filtered out of default RAG queries while remaining inspectable on demand via `orion.py brain recall <anchor_id>`.
* **Obsidian Second-Brain Export**: Generates an interactive wikilinked vault (`.orion/export/vault/`) and a 4-note cold-start architecture briefing.

### 2. 🍱 Zero-Escape Bento Task Slicer (`bento_slicer.py`)
* **Problem Solved**: Budget and Standard models in IDE chat interfaces frequently lose track of multi-file audit plans, skip middle tasks, hallucinate line numbers after prior edits, or claim completion while leaving patches unapplied.
* **Topological Blast-Radius Sequencing**: Parses multi-step implementation plans into atomic single-task instruction sheets (`.orion/working/ACTIVE_TASK.md`), sorted across architectural strata ($T_0 \to T_5$) and ordered bottom-up (highest line number to lowest) within the same file so edits never invalidate upstream line spans.
* **Live Anchor Recalibration & Indentation Alignment**: Re-locates target symbols on disk right before emitting each task, populates `SEARCH` with the exact byte-for-byte lines on disk, and shifts `REPLACE` indentation to match the file's actual leading whitespace.
* **Post-Condition Disk Mutation Gate**: When advancing via `orion.py bento next --verify`, the engine checks the physical file on disk before running tests. If the `SEARCH` block remains unpatched, it rejects progression (`Exit Code 2: [BENTO NO-OP REJECTED]`), executes all verification commands sequentially, and checks that all `TTP-*` audit findings are covered.

### 3. 🔍 AST Code Intelligence, TDD & Security Sandbox (`scanner.py`, `security.py`, `sandbox.py`, `verify_agents.py`)
* **Problem Solved**: Models burn context reading 2,000-line files in sequential chunks, write untested implementation code, or run untrusted scripts that mutate files outside the workspace.
* **AST Skeleton First & PageRank Repo-Map**: Extracts exact `[Lstart-Lend]` symbol spans (`orion.py scan map`) and PageRank-weighted core modules (`orion.py repomap`) so agents read only targeted functions.
* **Strict TDD & Delta Mutation Testing**: Enforces `RED -> GREEN -> REFACTOR` cycles and runs AST mutations exclusively on `git diff` lines (`orion.py adversarial mutate <file> --diff`) to verify that tests actually catch regressions.
* **Hermetic PEP 578 Sovereign Sandbox**: Executes exploratory scripts inside an AST-gated syscall jail that intercepts filesystem deletions/renames (`os.remove`, `rmdir`, `rename`, `shutil.rmtree`) and blocks subprocess spawning outside `_JAIL_ROOT`.
* **8-Gate Ecosystem Verifier with AST Caching**: Audits link integrity, ghost references, schema parity, polyglot security rules, structural line ceilings (`core_max_lines`), and instruction language hygiene (`orion.py verify`) backed by persistent `(mtime_ns, size)` AST caching.
* **27-Suite Contract Test Matrix**: 210 standard library `unittest` suites in `.agents/scripts/tests/` running full coverage with 100% pass rates.

### 4. 📦 Universal Project DNA, Context Packaging & Humanizer (`utils/packer.py`, `compact.py`, `tools/digestpack/`)
* **Problem Solved**: Uploading large polyglot repositories to web LLMs hits file count limits, truncates critical logic, or triggers prompt-in-data XML breakouts.
* **10-Bundle Ceiling & Topology Clustering**: Partitions any monorepo or polyglot codebase into at most 10 balanced Markdown bundles (`.md`) across `arch`, `hybrid`, and `full` tiers using PageRank centrality and AST import cohesion (`balance_into_k_bundles()`).
* **Pre-Audit Static Radar & 4-Turn Playbook**: Embeds a cross-bundle import router and static risk radar (execution sinks, broad catch blocks) in Bundle 01, paired with an automated 4-turn review prompt (`00_GEMINI_WEB_AUDIT_PROMPT.txt`).
* **Prompt-in-Data Shield**: Escapes literal closing tags (`</artifact>`) and neutralizes control tags (`<system>`, `<prompt_instructions>`) across all lines including code fences.
* **5-Tier Context Compactor & Lessword Protocol**: Compresses terminal streams, AST payloads, and prose by 15%–85% across unified compaction tiers (`lite`, `stream`, `full`, `aggressive`, `ultra`).
* **Prose Authenticity Engine (De-AI Prose Filter)**: Integrated 26-tell AI writing detector based on *Wikipedia: Signs of AI writing* and standard structural prose guidelines (`orion.py compact --humanize` and `--humanize-check`) guarded by syntax anchors so code, paths, and identifiers remain unmodified.

### 5. 🛡️ Cache-Aware State Recovery & Latency-Optimized Hooks (`state_machine.py`, `pre-agent-wake.py`, `capabilities.py`)
* **Problem Solved**: IDE restarts wipe in-progress context, runaway tool loops repeat failing commands, and regenerating state files on every keystroke invalidates LLM KV prompt caches.
* **SHA-256 Cache-Aware Omni-Buffer**: `pre-agent-wake.py` synchronizes active editor state, terminal errors, and active Bento tasks into `.orion/working/context.json`. A 5-minute idle activation gate compares structural SHA-256 hashes (`active_file`, `terminal_error`, `active_bento_task`, `evolution_overdue`) and skips file rewrites on unchanged turns to preserve LLM prompt-cache hits, emitting a `temporal_gap_marker` after idle gaps.
* **Pruned Hook Matchers (Zero Read-Tool Overhead)**: `.agents/hooks.json` matches exclusively against terminal execution (`run_command|execute_command|Bash`), eliminating process startup latency during high-frequency file reads.
* **Git-Bound FSM Checkpoints**: Snapshots working trees (`git stash create`) on state transitions so `orion.py fsm rollback --restore-code` restores both SQLite state and source files after a crash.
* **Fail-Closed PreToolUse Circuit Breaker**: Intercepts IDE tool calls and blocks execution (`Exit Code 3`) after 3 consecutive command/test failures until root-cause analysis is performed.

### 6. 🧬 Habit Observation, Self-Evolution & Telemetry Ledger (`reflexion.py`, `foundation.py`, `core/db.py`)
* **Problem Solved**: Agents repeat identical mistakes across sessions, accumulate bloated skills, and generate generic UI layouts or robotic prose.
* **5-Status Observation Ledger & Barrier Escalation**: Captures tool friction, runtime exceptions, and operator habits into `.agents/OBSERVATIONS.md` (`open`, `validated`, `promoted`, `parked`, `superseded`) with cold archival to `OBSERVATIONS.archive.md`. A 2nd repeated violation of the same rule automatically escalates from an advisory warning to a Tier-0 mechanical gate (`[BARRIER_ESCALATION_CANDIDATE]`).
* **Single-Sink Append-Only Telemetry**: Replaced $\mathcal{O}(N)$ whole-file rewrites with append-only `mechanical_catches.jsonl`, ensuring zero write contention and constant-time persistence.
* **Operator Habit Miner**: Detects recurring manual developer command sequences (`mine_operator_habits`) and proposes reusable workflow automation.
* **Framework Canons & Aesthetic Gatekeeper**: Ships production canons for **Flutter**, **React**, and **Python**, alongside `audit_aesthetics.py` (enforcing WCAG 2.x contrast math and 8pt grids) and `prose-authenticity.md` (banning 54 AI writing tells).

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
│ Stdlib & SQLite3 │ CLI & CST Engine │ Neural Embeddings│ Fast TS & MCP     │
├──────────────────┼──────────────────┼──────────────────┼───────────────────┤
│  ALWAYS ACTIVE   │ Fallback: Python │ Fallback: SQLite │ Fallback: Host    │
│  Zero pip deps   │ stream + ast mod │ FTS5 Porter BM25 │ runner / Node/Py  │
└──────────────────┴──────────────────┴──────────────────┴───────────────────┘
```

Check your machine's active pillars at any time (cached with a 900s TTL in `.orion/working/capabilities.json`):
```bash
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

# --- Knowledge Graph, Hybrid RAG & Observational Memory ---
python .agents/scripts/orion.py brain sync "auth token flow" # Hybrid FTS5 + Vector + 1-Hop + Louvain RAG
python .agents/scripts/orion.py brain recall O1             # Expand raw recall turns behind anchor [O1]
python .agents/scripts/orion.py brain rollover              # Trigger zero-LLM generational memory rollover
python .agents/scripts/orion.py graph path UserAuth TokenStore # Shortest BFS dependency path between entities
python .agents/scripts/orion.py brain export-vault          # Export Obsidian Vault to .orion/export/vault/

# --- Habit Observation & Self-Evolution ---
python .agents/scripts/orion.py observe "fix" --target rules # Record friction or pattern in OBSERVATIONS.md
python .agents/scripts/orion.py resolve 12 --status actioned # Resolve & archive completed observation #12
python .agents/scripts/orion.py consolidate session         # Run Temporal Pulse session synthesis & habit mining

# --- Quality, Security & Mutation Gates ---
python .agents/scripts/orion.py verify                      # Run 8-gate mechanical, ceiling & portability audit
python .agents/scripts/orion.py scan security .             # AST vulnerability, secret & Trojan Unicode scan
python .agents/scripts/orion.py adversarial mutate <f> --diff # Delta-scoped AST mutation testing on git diff
python .agents/scripts/orion.py eval --dir src/             # Audit UI tokens, 8pt grid & prose anti-slop

# --- Universal Project DNA Context Packaging (Digestpack) ---
python .agents/scripts/orion.py pack                        # Auto-detect staged changes, diff, or hybrid pack
python .agents/scripts/orion.py pack arch                   # Tier 1: <=10 Macro AST skeleton bundles
python .agents/scripts/orion.py pack hybrid                 # Tier 2: <=10 Balanced production bundles
python .agents/scripts/orion.py pack full                   # Tier 3: <=10 Complete codebase bundles
python .agents/scripts/orion.py pack pr                     # Scope strictly to staged PR changes
```

---

## 🤝 Architectural Inspirations

Implemented natively in Python 3.10+ Standard Library and SQLite3 WAL without third-party `pip` packages, drawing conceptual inspiration from:
* [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (CLI proxy noise filtering), [caveman](https://github.com/Echo-Scion/caveman) (high-density concise communication; evolved natively into `lessword`), [ast-grep](https://github.com/ast-grep/ast-grep) (Tree-sitter CST matching), [paul-gauthier/aider](https://github.com/paul-gauthier/aider) (PageRank repo-map packing), [microsoft/graphrag](https://github.com/microsoft/graphrag) & [graphify](https://github.com/Echo-Scion/graphify) (hierarchical community clustering + entity graph retrieval), [Obsidian](https://obsidian.md) (wikilink graph interoperability & local second-brain briefing), loop engineering (deterministic state-machine cycles & supervisory feedback), and Google DeepMind AutoHarness (deterministic action-verification gates).

---

## 👥 Contributors

* [@Echo-Scion](https://github.com/Echo-Scion) — Core maintainer & architecture
* **Google Gemini** (AI Pair Programmer) — Architecture drafting, test generation & refactoring

---

## 📄 License

Distributed under the [MIT License](LICENSE).
