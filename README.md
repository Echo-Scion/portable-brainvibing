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

# 2. Deploy to current workspace or target app repository
python .agents/scripts/orion.py foundation deploy --target <path_to_app_repo>
```

</div>

---

> ### 🛡️ Provenance, Runtime Verification & Audit Baseline
>
> | Dimension | Specification & Verification Details |
> | :--- | :--- |
> | **Primary Runtime** | Tested on **Google Antigravity IDE** and **VS Code**. |
> | **Pair-Engineering** | 100% of architecture, kernel scripts, and rules are synthesized via *AI Pair-Programming* under *Self-Hosting* principles (AI uses `.agents` to construct and maintain `.agents` itself). |
> | **Adversarial Audit** | Independently audited using **Gemini 4 Argon** to map AST integrity, eliminate dead abstractions, isolate race conditions. |
> | **Air-Gapped Safety** | Zero background daemons, zero cloud telemetry, zero socket listeners, local. |

---

## ⚡ Why Standard AI Coding Fails (And How `.agents` Fixes It)

| Default AI Coding Failure | Deterministic Mitigation in `.agents` |
| :--- | :--- |
| **Hallucinated "Done!" Claims**: AI claims tests pass without running them or masks errors with `catch (e) {}`. | **Iron Evidence Law & Response Validator**: Requires `Exit Code 0` + verified state-delta assertions. Cross-checks claims against `.orion/working/failures.log`. |
| **Sequential File Paging (Token Bleed)**: AI reads 2,000-line files in 50-line chunks, burning context and losing focus. | **AST Skeleton First & Orion Topology Map**: `orion.py scan map` extracts exact `[Lstart-Lend]` symbol spans and PageRank-ranked core modules before reading. |
| **Untested Implementation Bloat**: AI writes 300 lines of feature code before writing a single test. | **Strict TDD Gate & Delta Mutation Testing**: Enforces `RED -> GREEN -> REFACTOR` cycles and runs AST mutations strictly on `git diff` lines. |
| **Runaway Guessing Loops**: AI repeats the same broken command 10 times when stuck. | **3-Attempt Circuit Breaker**: Tracks action-observation trajectories and halts tool execution after 3 consecutive failures or cyclical loops. |
| **Context Window Exhaustion**: Verbose compiler logs, progress bars, and chatbot pleasantries flood the prompt. | **5-Tier Orion Compactor & Lessword Mode**: Strips ANSI/log noise via Rust `rtk` or native Python shapers, cutting prose and payload tokens by 35%–90%. |
| **Cross-Session Amnesia**: AI forgets architectural decisions, broken dependencies, and past bugs on restart. | **Dual-Horizon SQLite Graph Memory & Active Cache**: Combines FTS5 BM25, local vector embeddings, 1-hop dependency edges, and Louvain community clusters. |
| **Generic "AI Slop" UI & Prose**: AI generates purple-gradient clichés, broken contrast, and robotic buzzwords. | **Mechanical Aesthetic & Anti-Slop Gates**: `audit_aesthetics.py` enforces WCAG 2.x contrast math, 8pt spacing grids, and bans 54 AI writing tells. |

---

## 🛠️ What's Inside `.agents` (The 6 Core Features)

Everything runs through a single zero-dependency CLI command: `python .agents/scripts/orion.py <command>`.

### 1. 🧠 Smart Project Memory (`brain.py`, `memory.py`)
* **Remembers Decisions Across Sessions**: Saves your architectural choices, database schemas, and past bug fixes in local SQLite so the AI never forgets context when you reopen your editor.
* **Smart Code Search**: Finds relevant files by analyzing function calls, relationships, and code imports—not just basic text matching.
* **Auto-Generated Knowledge Vault**: Automatically builds an Obsidian-compatible markdown map (`.orion/vault/`) showing how files and modules connect.

### 2. 🔍 Smart Code Analysis & Security (`scanner.py`, `security.py`, `verify_agents.py`)
* **Token-Efficient Code Outline**: Scans symbols across your repository and sends only high-priority outlines to the AI, saving context budget (`orion.py repomap`).
* **Multi-Language Vulnerability Scanner**: Detects SQL injections, hardcoded API secrets, command injection, and invisible Unicode attacks in Python, Dart, TypeScript, Rust, Go, and Kotlin.
* **Test Sensitivity Verification**: Tests the quality of your test suite by making small surgical mutations to modified lines (`git diff`) and confirming tests actually fail.

### 3. ✂️ Token Noise Reducer (`capabilities.py`, `brain.py`)
* **Lessword Mode**: Cuts verbose chatbot filler ("Sure! I would be happy to help with...") while keeping all code, terminal commands, and technical substance 100% exact.
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
│                      Master BIOS (AGENTS.md / GEMINI.md)                   │
│        35-Row JIT Knowledge Router • Iron Evidence Law • Lessword Mode     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                      Unified CLI Gateway (orion.py)                        │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│ PILLAR 1 (Floor) │ PILLAR 2 (Rust)  │ PILLAR 3 (Local) │ PILLAR 4 (JS/TS)  │
│ Python 3.10+     │ rtk + ast-grep   │ Ollama Daemon    │ Bun Runtime       │
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

## 🚀 Quickstart

### 1. Deploy into Any Project (Greenfield or Existing)

Clone into your project root as `.agents`:
```bash
git clone https://github.com/Echo-Scion/portable-brainvibing.git .agents
```

Then choose how you want to deploy:

#### Option A: One-Command CLI Deploy
Auto-detects your stack (Flutter, React, Python, Rust, Go) and deploys configurations across supported AI platforms:
```bash
# Deploy to current repository:
python .agents/scripts/orion.py foundation deploy --target .

# Or deploy to an external target application repository:
python .agents/scripts/orion.py foundation deploy --target <path_to_app_repo>
```

#### Option B: AI Agent Prompt (Plug & Play)
If you prefer your AI agent to configure the project directly, prompt your AI:
> **Copy-Paste Prompt for your AI:**  
> *"Read `.agents/DEPLOY_ME.md` and deploy the foundation to this project."*

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
python .agents/scripts/orion.py compact pipeline <file>     # 5-tier deterministic context compaction
python .agents/scripts/orion.py harness status              # Inspect autonomous skill staging & lifecycle
python .agents/scripts/orion.py consolidate session         # Generate Temporal Pulse session synthesis
# --- Seamless Vibe Context Packaging (Auto-Intent) ---
python .agents/scripts/orion.py pack                          # Smart Auto-Vibe: auto-detects staged changes, diff, or clean audit
python .agents/scripts/orion.py pack audit                    # 10 domain bundles with AST skeletonization (~80% token savings)
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
│   ├── commands/             # 5 Gateway Engines (brain, foundation, reflexion, state_machine, verify_agents)
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