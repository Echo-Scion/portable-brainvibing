<div align="center">

# 🧠 Portable Brainvibing (`.agents`)

### Turnkey Auto-Vibe Coding Brain & Cognitive Runtime for Autonomous AI Agents

<p align="center">
  <b>Turn probabilistic coding AIs into deterministic, self-verifying software engineers.</b><br>
  Deploy across seperate workspace level brain, local, zero-pip, zero runetime.
</p>

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/version-v0.0.1-blue.svg?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/core-Python%203.10%2B%20Stdlib-brightgreen.svg?style=flat-square" alt="Core"></a>
  <a href="#-the-four-anchored-pillars"><img src="https://img.shields.io/badge/database-SQLite3%20WAL-informational.svg?style=flat-square" alt="Database"></a>
  <a href="PREREQUISITES.md"><img src="https://img.shields.io/badge/dependencies-Zero%20Pip-critical.svg?style=flat-square" alt="Zero-Pip"></a>
  <a href="#-quickstart"><img src="https://img.shields.io/badge/deployment-Multi--Platform-orange.svg?style=flat-square" alt="Platforms"></a>
  <a href="https://github.com/Echo-Scion"><img src="https://img.shields.io/badge/author-Echo--Scion-purple.svg?style=flat-square" alt="Author"></a>
</p>

> ⚠️ **Status**: Untested in creating any project or app yet

<p align="center">
  <a href="#-quickstart"><b>Quickstart</b></a> •
  <a href="#-whats-inside-agents-the-6-core-features"><b>Core Features</b></a> •
  <a href="#-the-four-anchored-pillars"><b>4 Pillars</b></a> •
  <a href="#-essential-cli-commands-orionpy"><b>CLI Commands</b></a> •
  <a href="#-dual-tier-repository-architecture"><b>Architecture</b></a> •
  <a href="CHANGELOG.md"><b>Changelog</b></a>
</p>

```bash
# 1. Clone runtime into .agents
git clone https://github.com/Echo-Scion/portable-brainvibing.git .agents

# 2. Interactive Setup Wizard (Auto-detects hardware, stack, local LLMs & optional features)
python .agents/scripts/orion.py setup
```

</div>

---

### 🛡️ Provenance, Runtime Verification & Audit Baseline

| Dimension | Specification & Verification Details |
| :--- | :--- |
| **Primary Runtime** | Only being tested on **Google Antigravity IDE** and **VS Code**. |
| **Hybrid Cognition** | 4-Tier Cognition Model: Deterministic Python/Rust/SQLite stdlib (Tier 0) + Local Neural NanoBrain (Tier 1: Ollama embeddings & structured triplet extraction) + Frontier Cloud LLMs (Tier 2: Gemini/Claude deep reasoning) + Human-in-the-loop (Tier 3). |
| **Mechanical Proportionality** | Deterministic algorithms handle exact computation (AST skeletons, PageRank centrality, bin-packing, secret scrubbing, static radars, test mutations, file/import graph routing), offloading mechanical burdens so frontier models focus cognitive tokens on architectural judgment. |
| **Universal Project DNA v2** | Monorepo and polyglot container discovery (`apps/`, `packages/`, `services/`), universal 5-tier taxonomy (`contracts`, `domain`, `services`, `state`, `presentation`), polyglot static audit radar, cross-bundle import routing, and balanced bin-packing via `orion pack` and `tools/digestpack`. |
| **Pair-Engineering** | 100% of architecture, kernel scripts, and rules are synthesized via *AI Pair-Programming* under *Self-Hosting* principles (AI uses `.agents` to construct and maintain `.agents` itself). |
| **Adversarial Audit** | Independently audited using **Gemini 2.5 Pro & Claude Opus** to map AST integrity, eliminate dead abstractions, isolate race conditions. |
| **Centaur Architecture** | Fail-closed `PreToolUse` hook (Exit Code 3), PEP 578 syscall containment in `SovereignSandbox`, anti-false-green test state gating, and XML artifact breakout protection. |
| **Modular Gateway CLI** | Monolithic `brain.py` decomposed into 8 dedicated Gateway CLI engines (`brain.py`, `compact.py`, `rag.py`, `vault.py`, `foundation.py`, `state_machine.py`, `reflexion.py`, `verify_agents.py`) with unified facade routing. |
| **Air-Gapped Safety** | Zero background daemons, zero cloud telemetry, zero socket listeners, local. |

---

## ⚡ Why Standard AI Coding Fails (And How `.agents` Fixes It)

| Default AI Coding Failure | Deterministic Mitigation in `.agents` |
| :--- | :--- |
| **Mechanical vs Cognitive Overload**: AI models burn context parsing raw directories, tracking imports, and computing dependencies, causing attention fatigue. | **Universal Project DNA v2 & Digestpack**: Deterministic bin-packing (`balance_into_k_bundles()`), cross-bundle import routing, and polyglot static audit radar deliver pre-digested context packets under the strict 10-bundle ceiling. |
| **Hallucinated "Done!" Claims**: AI claims tests pass without running them or masks errors with `catch (e) {}`. | **Iron Evidence Law & Response Validator**: Requires `Exit Code 0` + verified state-delta assertions. Cross-checks claims against `.orion/working/failures.log`. |
| **Sequential File Paging (Token Bleed)**: AI reads 2,000-line files in 50-line chunks, burning context and losing focus. | **AST Skeleton First & Orion Topology Map**: `orion.py scan map` extracts exact `[Lstart-Lend]` symbol spans and PageRank-ranked core modules before reading. |
| **Untested Implementation Bloat**: AI writes 300 lines of feature code before writing a single test. | **Strict TDD Gate & Delta Mutation Testing**: Enforces `RED -> GREEN -> REFACTOR` cycles and runs AST mutations strictly on `git diff` lines. |
| **Runaway Guessing Loops**: AI repeats the same broken command 10 times when stuck. | **3-Attempt Circuit Breaker & Fail-Closed Gate**: Tracks action-observation trajectories, halting tool execution after 3 consecutive failures via a fail-closed `PreToolUse` hook (Exit Code 3). |
| **Untrusted Execution Risk & Sandbox Escapes**: Exploratory scripts delete files or execute arbitrary subprocesses. | **Sovereign Sandbox & PEP 578 Syscall Jail**: AST-gated execution intercepting filesystem mutations (`os.remove`, `rmdir`, `rename`, `shutil.rmtree`) and blocking child processes outside `_JAIL_ROOT`. |
| **Prompt-in-Data Bleed & Breakout**: Code containing closing tags or imperative instructions manipulates the audit prompt. | **Deterministic Artifact Sandboxing**: Escapes `</artifact>` closing tags into `&lt;/artifact&gt;` and neutralizes directive verbs across markdown tables and bullet lists in context packages. |
| **Context Window Exhaustion**: Verbose compiler logs, progress bars, and chatbot pleasantries flood the prompt. | **3-Tier Orion Compactor & Lessword Mode**: Strips ANSI/log noise via Rust `rtk` or native Python shapers, cutting prose and payload tokens by 15%–85% across unified tiers (`lite`, `full`, `ultra`). |
| **Cross-Session Amnesia**: AI forgets architectural decisions, broken dependencies, and past bugs on restart. | **Dual-Horizon SQLite Graph Memory & Active Cache**: Combines FTS5 BM25, local vector embeddings, 1-hop dependency edges, and Louvain community clusters. |
| **Generic "AI Slop" UI & Prose**: AI generates purple-gradient clichés, broken contrast, and robotic buzzwords. | **Mechanical Aesthetic & Anti-Slop Gates**: `audit_aesthetics.py` enforces WCAG 2.x contrast math, 8pt spacing grids, and bans 54 AI writing tells. |

---

## 🛠️ What's Inside `.agents` (The 6 Core Features)

Everything runs through a single zero-dependency CLI command: `python .agents/scripts/orion.py <command>`.

### 1. 🧠 Smart Project Memory (`brain.py`, `rag.py`, `vault.py`, `memory.py`)
* **Remembers Decisions Across Sessions**: Saves your architectural choices, database schemas, and past bug fixes in local SQLite so the AI never forgets context when you reopen your editor.
* **Smart Code Search**: Finds relevant files by analyzing function calls, relationships, and code imports—not just basic text matching.
* **Auto-Generated Knowledge Vault**: Automatically builds an Obsidian-compatible markdown map (`.orion/vault/`) showing how files and modules connect.

### 2. 🔍 Smart Code Analysis & Security (`scanner.py`, `security.py`, `sandbox.py`, `verify_agents.py`)
* **Token-Efficient Code Outline**: Scans symbols across your repository and sends only high-priority outlines to the AI, saving context budget (`orion.py repomap`).
* **Multi-Language Vulnerability Scanner**: Detects SQL injections, hardcoded API secrets, command injection, and invisible Unicode attacks in Python, Dart, TypeScript, Rust, Go, and Kotlin.
* **Hermetic Sovereign Sandbox**: Runs exploratory scripts in an AST-gated PEP 578 audit jail that intercepts destructive filesystem mutations and blocks unvetted subprocess execution.
* **Test Sensitivity Verification**: Tests the quality of your test suite by making small surgical mutations to modified lines (`git diff`) and confirming tests actually fail.

### 3. 📦 Universal Project DNA Packer & Token Reducer (`packer.py`, `capabilities.py`, `compact.py`, `brain.py`)
* **Universal Project DNA v2**: Recursively discovers polyglot monorepo containers (`apps/`, `packages/`, `services/`, `modules/`), applies a clean 5-tier architectural taxonomy (`contracts`, `domain`, `services`, `state`, `presentation`), and traces cross-bundle imports with generic stem filtering.
* **Polyglot Static Audit Radar**: Pre-computes dangerous execution sinks (`eval`, `exec`, `Process.run`, `dangerouslySetInnerHTML`) and empty catch blocks across 10+ languages directly into Bundle 01.
* **Universal 10-Bundle Ceiling**: Uses `balance_into_k_bundles()` to partition any repository into at most 10 Markdown files (`.md`) across three isolated audit tiers (`arch/`, `hybrid/`, `full/`), bypassing upload limits in Gemini Web Chat, Claude Projects, and ChatGPT without context bleed.
* **Standalone Digestpack CLI**: Maintained as an internal Orion command (`orion.py pack`) and a standalone zero-pip utility in `tools/digestpack/` for external multi-model audit workflows.
* **Lessword Mode**: Cuts verbose chatbot filler while keeping code, terminal commands, and technical substance 100% exact.
* **Terminal Log Cleaner**: Automatically strips noisy progress bars, ANSI color codes, and repetitive stack trace frames before sending them to the model, saving 35%–80% in token costs.

### 4. 🛡️ Crash-Proof State Recovery (`state_machine.py`, `pre-agent-wake.py`)
* **Instant Session Recovery**: Automatically snapshots active work and tasks to local SQLite (`git stash create`). If your IDE crashes or reboots, the agent resumes right where it left off.
* **Live Context Synchronizer**: Automatically caches the active file, git status, and terminal errors into `.orion/working/context.json` so the AI has full context the moment it wakes up.

### 5. 🧬 Self-Learning & Skill Manager (`core/harness/`, `reflexion.py`)
* **Learns From Terminal Errors**: When a command or test fails 3 times, the agent stops guessing, diagnoses the root cause, and logs the lesson to `LEARNINGS.md`.
* **Automatic Skill Lifecycle**: Safely protects core project skills while evaluating new agent-created skills, retiring unused ones so your prompt never gets bloated.

### 6. 🎨 Production Canons & Multi-Platform Deployment (`foundation.py`, `audit_aesthetics.py`)
* **Ready-to-Use Framework Best Practices**: Includes built-in best practice cheat-sheets for **Flutter**, **React / Next.js**, **Python**, and **Supabase**.
* **Multi-Platform Deployment in 1 Command**: Generates and syncs instruction files, hooks, and manifests across supported AI platforms and editors in a single command.
* **Accessibility & UI Polish Auditor**: Checks color contrast (WCAG standards), spacing grids, and component interaction states.

---

## 🏛️ The Four (4) Anchored Pillars & Graceful Fallback

The engine runs out-of-the-box with **only Python 3.10+**. Optional native binaries unlock hardware-accelerated capabilities and automatically fall back to pure Python stdlib when absent:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            Master BIOS (AGENTS.md)                         │
│        35-Row JIT Knowledge Router • Iron Evidence Law • Lessword Mode     │
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

## 🚀 Quickstart & Architecture Topology

`.agents` follows a **Hub-and-Spoke** topology. Understand which environment you are operating in:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UPSTREAM FOUNDATION HUB (_foundation)                │
│   • Master template authoring, engine dev, canons & evals              │
│   • CLI: python .agents/scripts/orion.py foundation deploy --target <dir>│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │  1. Deploy / Update
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 DOWNSTREAM SPOKE WORKSPACE (Your App Repo)             │
│   • Your actual product (Flutter, React, Python, Rust, Go, etc.)       │
│   • Consumes .agents/ as a modular submodule or copied engine          │
│   • CLI (Human): python .agents/scripts/orion.py setup                 │
│   • CLI (Agent): python .agents/scripts/orion.py setup --yes           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │  2. Sync Back Inventions / Rules
                                    ▼
       python .agents/scripts/orion.py foundation push-upstream --project .
```

---

### 1. Operating in a Downstream Spoke Project (Your App)

When you are inside your application repository (e.g., `my-mobile-app/` or `saas-backend/`):

#### Step A: Get `.agents` into your project
```bash
# Option 1: Git Submodule / Clone directly as .agents
git clone https://github.com/Echo-Scion/portable-brainvibing.git .agents

# Option 2: Or deploy from a local Upstream Hub on your laptop:
python /path/to/_foundation/.agents/scripts/orion.py foundation deploy --target .
```

#### Step B: Run Setup (Human vs AI Agent)

* **For Humans (Interactive Terminal TUI Wizard)**:
  ```bash
  python .agents/scripts/orion.py setup
  ```
  Guides you step-by-step through laptop diagnostic, hardware tier detection, local model discovery, and lets you toggle optional power-features with interactive keypresses.

* **For AI Agents in Chat (Headless / Zero-Guessing)**:
  AI agents calling tools have no interactive keyboard stream (`sys.stdin.isatty() == False`). Agents MUST run in headless mode:
  ```bash
  # Step 1: Agent inspects workspace & hardware facts as JSON:
  python .agents/scripts/orion.py setup --inspect --json

  # Step 2: Agent executes unattended setup with selected features:
  python .agents/scripts/orion.py setup --yes --enable graph-db,second-brain,vault
  ```

* **Fast Doctor Health Check**:
  ```bash
  python .agents/scripts/orion.py doctor
  ```

---

### 2. Operating in the Upstream Foundation Hub (`_foundation`)

When you are working directly inside the master framework source repository (`_foundation`):

* **Verify Hub Health**: `python .agents/scripts/orion.py doctor` or `python .agents/scripts/orion.py verify_agents`
* **Deploy Foundation to an External Project**:
  ```bash
  python .agents/scripts/orion.py foundation deploy --target "C:/Projects/my-app"
  ```
* **Sync Improvements from an App Back Upstream to Hub**:
  ```bash
  python .agents/scripts/orion.py foundation push-upstream --project "C:/Projects/my-app"
  ```

### 2. Essential CLI Commands (`orion.py`)

```bash
# --- Code Intelligence & Context Mapping ---
python .agents/scripts/orion.py scan map src/               # Extract [Lstart-Lend] AST skeletons
python .agents/scripts/orion.py repomap --budget 1500        # PageRank-ranked God Nodes within token budget
python .agents/scripts/orion.py scan tokens                 # Audit largest token-consuming files

# --- Knowledge Graph & Hybrid RAG ---
python .agents/scripts/orion.py brain sync "auth token flow" # Hybrid FTS5 + Vector + 1-Hop + Louvain RAG
python .agents/scripts/orion.py graph path UserAuth TokenStore # Find shortest BFS path between entities
python .agents/scripts/orion.py brain export-vault          # Export interactive Obsidian Vault to .orion/vault/
python .agents/scripts/orion.py memory second-brain         # Build 4-note cold-start architecture briefing

# --- Quality, Security & Mutation Gates ---
python .agents/scripts/orion.py verify                      # Run 8-gate mechanical & portability audit
python .agents/scripts/orion.py scan security .             # AST vulnerability, secret & Trojan Unicode scan
python .agents/scripts/orion.py adversarial mutate <f> --diff # Delta-scoped AST mutation testing on git diff
python .agents/scripts/orion.py eval --dir src/             # Audit UI tokens, 8pt grid & prose anti-slop
python .agents/scripts/orion.py contrast "#F3F4F6" "#0D0F12" # Verify WCAG 2.x AA/AAA contrast ratio

# --- Token Compaction & Self-Evolution ---
python .agents/scripts/orion.py compact full <file>         # 3-tier unified context compaction (lite, full, ultra)
python .agents/scripts/orion.py harness status              # Inspect autonomous skill staging & lifecycle
python .agents/scripts/orion.py consolidate session         # Generate Temporal Pulse session synthesis
# --- Universal Project DNA Context Packaging (Digestpack) ---
python .agents/scripts/orion.py pack                          # Smart Auto-Vibe: auto-detects staged changes, diff, or clean audit
python .agents/scripts/orion.py pack arch                     # Tier 1: 10 Macro AST skeleton bundles (~60k-100k tokens)
python .agents/scripts/orion.py pack hybrid                   # Tier 2: 10 Balanced production bundles (~350k-400k tokens)
python .agents/scripts/orion.py pack full                     # Tier 3: 10 Zero-truncation complete codebase bundles (~500k tokens)
python .agents/scripts/orion.py pack pr                       # Scopes strictly to staged PR changes with review template
python .agents/scripts/orion.py pack stats                    # Breakdown of files & token volume by extension
python .agents/scripts/orion.py pack <git-url>                # Shallow clone, skeletonize, and ingest remote repo
```

---

## 📂 Dual-Tier Repository Architecture

```plaintext
.agents/
├── AGENTS_INDEX.md           # Master directory of all rules, skills, canons, and scripts
├── DEPLOY_ME.md              # Automated agentic onboarding & spoke deployment protocol
├── hooks.json                # PreToolUse (RTK proxy) & PreInvocation (Omni-Buffer) hooks
├── scripts/
│   ├── orion.py              # Unified zero-pip CLI dispatcher & span tracer
│   ├── core/                 # 8 Kernel Primitives (capabilities, db, memory, orion_graph, paths, sandbox, scanner, security)
│   │   └── harness/          # Sovereign Self-Learning Skill Harness (admission, capture, curator, engine, lifecycle, staging)
│   ├── commands/             # 8 Modular Gateway Engines (brain, compact, foundation, rag, reflexion, state_machine, vault, verify_agents)
│   ├── utils/packer.py       # Universal 10-bundle repository context exporter
│   └── tests/                # Contract & regression test suites
├── rules/                    # 14 Behavioral & Security Laws (core-guardrails, prose-authenticity, fsm-protocol, etc.)
├── skills/                   # 21 Public Domain Skills + 51 Tier-3 Reference Playbooks
├── canons/                   # Ecosystem Recipes (Flutter, React, Python) & ≤50-line Micro-Canons
├── templates/                # 16 Project & IDE Adapter Scaffolds (AGENTS, DESIGN, ADR, CURSOR_RULE)
├── hooks/pre-agent-wake.py   # Synchronous IDE state & JIT skill router hook
├── evals/                    # Deterministic Assertion Engine & WCAG/Aesthetic Auditor
└── docs/                     # 12-Volume Master Technical Encyclopedia (00-intro to 11-glossary)
```

---

## 📚 12-Volume Technical Encyclopedia

Deep-dive specifications are maintained in [`.agents/docs/`](.agents/docs/00-intro.md):

* [Vol I: Theoretical Foundation](.agents/docs/01-theoretical_foundation.md): 6 structural LLM failure modes & deterministic mitigations.
* [Vol II: System Architecture](.agents/docs/02-system_architecture.md): Master BIOS, Omni-Buffer, and the 4 Anchored Pillars.
* [Vol III: Local RAG Brain](.agents/docs/03-local_rag_brain.md): SQLite3 WAL schema, Dual-Level GraphRAG, and Louvain clustering.
* [Vol IV: Rule Library](.agents/docs/04-rule_library___rules.md): Precedence hierarchy, offensive security, and anti-slop prose laws.
* [Vol V: Domain Skills](.agents/docs/05-skill___persona___skills.md): 3-Tier progressive disclosure across 21 engineering personas.
* [Vol VI: Lifecycle Playbooks](.agents/docs/06-workflow___sop.md): Phases 0–6 State Machine & 18 Standard Operating Procedures.
* [Vol VII: Execution Engine](.agents/docs/07-python_scripts___scripts.md): Complete `orion.py` CLI architecture.
* [Vol VIII: Canons, Templates & Evals](.agents/docs/08-canons__templates__hooks__evals__and_archives.md): Stack canons, hooks, and aesthetic verifiers.
* [Vol IX: Darwinian Evolution](.agents/docs/09-darwinian_evolution_lifecycle.md): Friction mining, 4-tuple invariants, and genomic ledger.
* [Vol X: Spoke Deployment](.agents/docs/10-deployment_flow_to_new_projects.md): Multi-IDE adapter synchronization & hub-and-spoke flow.
* [Vol XI: Complete Glossary](.agents/docs/11-complete_glossary.md): Canonical definitions of all architectural terms.

---

## 🤝 Architectural Inspirations & Minimal Lineage

While `.agents` is implemented natively in pure Python 3.10+ Standard Library and SQLite3 WAL without third-party pip dependencies, its architecture builds upon pioneering concepts:

* **CLI Interception & Terminal Noise Reduction**: Inspired by [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (process-level proxying & token savings).
* **AST Structural Matching**: Inspired by [ast-grep](https://github.com/ast-grep/ast-grep) (polyglot syntax-tree pattern matching).
* **Codebase Centrality & Outline Packing**: Inspired by [paul-gauthier/aider](https://github.com/paul-gauthier/aider) (PageRank symbol graph & token-budget knapsack packing).
* **Hierarchical Graph Memory**: Inspired by [microsoft/graphrag](https://github.com/microsoft/graphrag) (combining community clusters with fine-grained entity relations).
* **Action-Harness & Skill Verification**: Inspired by the Google DeepMind AutoHarness methodology (programmatic validation gates for autonomous agents).

---

## 📄 License

Distributed under the [MIT License](LICENSE).