# 🧠 Portable Brainvibing — Plug and Play AI Infrastructure

![Foundation CI](https://github.com/Echo-Scion/Portable-Brainvibing/actions/workflows/foundation-ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-v0.0.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![AI Compatible](https://img.shields.io/badge/AI-Gemini%20%7C%20Claude%20%7C%20Copilot%20%7C%20Cursor%20%7C%20Windsurf-orange)

A plug-and-play `.agents` ecosystem that transforms generic AI coding assistants into **deterministic engineering instruments**. This repository contains the **Universal Framework**—a language-agnostic, OS-agnostic blueprint designed to enforce absolute reproducibility and minimize AI hallucination. 

⚠️ WARNING: 100% AI ENGINEERED. UNTESTED. ACTUAL VERSION NEVER 1.0. IT EVOLVE WITH YOU.

---

## 📖 Table of Contents
- [The Core Philosophy](#-the-core-philosophy)
- [Universal Mechanics & Principles](#-universal-mechanics--principles)
- [Autonomous Pipeline Logic](#-autonomous-pipeline-logic)
- [DevSecOps & Algorithmic Governance](#-devsecops--algorithmic-governance)
- [Architecture & Taxonomy](#-architecture--taxonomy)
- [The Advanced Vision (Unbound Hardware)](#-the-advanced-vision-unbound-hardware)
- [Deployment](#-deployment)

---

## 💡 The Core Philosophy
AI coding assistants suffer from three structural flaws when dealing with complex codebases:
1. **Agentic Amnesia**: They forget rules defined earlier in the context window.
2. **Attention Decay**: They lose track of the overarching goal during complex, multi-file tasks.
3. **Token Inefficiency**: They waste context window space explaining basic concepts or reading raw terminal logs.

The Universal Framework mitigates this by replacing **prohibitions** ("Don't do X") with **algorithmic gates**. The AI is physically restricted by Python validation scripts, forced workflows, and strict contextual limits.

---

## ⚙️ Universal Mechanics & Principles

These are the core, framework-agnostic concepts that power this ecosystem:

### 1. 🦍 The Caveman Protocol (Token Optimization)
We structurally ban polite AI fluff. The AI is forced to speak in terse, fragmented "Caveman Mode." 
- **AI before:** *"I apologize for the confusion! Let's go ahead and fix the null pointer issue by adding a check..."*
- **AI now:** `Auth crash. User null. Adding check.` 
*Result: Context windows last longer. Compute cost drops significantly. Logic remains accurate.*

### 2. 🧠 IDE Agent Delegation & Modular CLI (`orion.py`)
Instead of forcing the AI to manually search for rules or parse fragile CLI outputs, the system relies on structured IDE Agent Delegation. Your IDE AI explicitly triggers specialized CLI tools via standard `run_command` protocols. The standard CLI (`orion.py`) acts as the primary interface for both background cron-jobs and human/AI-driven task orchestration.

### 3. 📡 The Omni-Buffer (Context Hook)
To prevent the AI from hallucinating about which file the user is currently looking at, we utilize the `context.json` Omni-Buffer. A background hook silently writes the active IDE tab, cursor position, and any terminal errors to this buffer. The AI reads it magically on its first turn—no manual copy-pasting required.

### 4. ⚔️ Adversarial Twin Protocol (Brute-Force Loops)
The AI is forced into an automated attack/defend cycle:
1. Write implementation code.
2. Write a unit test specifically designed to break the implementation.
3. Mutate the code iteratively until the terminal outputs `Exit Code 0`.
If the AI fails 3 times, the **Circuit Breaker** trips automatically, forcing it to stop wasting tokens and ask for human intervention.

### 5. ✂️ Output Filtering & Universal AST Ingestion
Verbose terminal logs (e.g., `npm install` or `cargo build`) flood the AI's context window.
- **RTK (Rust Token Killer)**: Proxies all terminal commands and strips >80% of log output.
- **Universal AST Parser**: Before saving source code to the `.orion` SQLite database, our parser strips out all comments, white-spaces, and logic blocks, leaving only pure structural footprints. This reduces SQLite database bloat by 90%.

### 6. 🧬 The Self-Evolve Engine (Darwinian Mutation)
The ecosystem learns autonomously through a strictly mechanical evolution loop:
- **Heartbeat Cron**: Forces evolution based on error thresholds, defeating Agentic Amnesia.
- **Fitness Benchmarker**: Forks rules (V1 vs V2) and runs automated `evals.json` to prove V2 is superior before promotion.
- **Evolution Genome**: Every mutation is logged to an append-only JSONL ledger, providing a genetic history of the brain's divergence.

### 7. 🦖 The LightRAG Quad-Core
To bypass heavy vector databases and bloated background daemons, we use a lightweight quad-core setup:
- **SQLite FTS5**: Super lightweight, high-performance local full-text search.
- **Relational Triplet Graph**: Explicit semantic linking of code symbols and files under `.orion/`.
- **Dynamic Local LLM Tiers**: Natively integrated with Ollama. At deployment, users configure their local AI hardware capabilities (`Low`, `Medium`, `High` intelligence). The system dynamically gates features (like code generation vs simple vibe checks) based on this tier to physically prevent Agentic Hallucination, gracefully falling back to Cloud Agents when required.
- **Universal OS-Agnostic Execution**: Every component runs natively via standard `python` without hardcoded aliases, ensuring 100% plug-and-play across Windows, macOS, and Linux virtual environments.

### 8. 🌐 IDE-Agnostic Native Tooling
The framework avoids vendor lock-in by utilizing an abstract tooling policy. Whether running inside Antigravity, Cursor, Copilot, or Windsurf, the AI is instructed to dynamically map abstract workflows ("ask the user", "execute long task") to its specific native slash-commands (like `/grill-me`, `/goal`, or `Composer Ask`).

---

## 🔄 Autonomous Pipeline Logic (Output-as-Input)

Skills and Subagents do not operate in a vacuum. The framework chains them together using a **State Machine**:
- **Strategist** writes `.orion/CONTEXT.md`.
- **Architect** ingests `CONTEXT.md` before generating `.orion/BLUEPRINT.md`.
- **Coder** reads `BLUEPRINT.md` and generates source code.

**The Unified Footer**: Every single AI response must end with a standard footer that automatically queues the exact next terminal command. The AI reads the Exit Code and executes the next state block.

---

## 🛡️ DevSecOps & Algorithmic Governance

We do not trust the AI to implicitly follow prompt rules. The Universal template enforces rules mechanically via Python scripts:

| Traditional Prompt | Universal Framework (Algorithmic Governance) |
| :--- | :--- |
| *"Don't commit API keys"* | **`orion.py preflight`** intercepts and throws `[FAIL]` if regex matches a key. |
| *"Follow the taxonomy"* | **`orion.py context-lint`** crashes if a file is created outside the approved mapping. |
| *"Don't break internal links"* | **`orion.py verify`** acts as a compiler for markdown, verifying all cross-references. |
| *"What file am I looking at?"* | **Omni-Buffer (`context.json`)** intercepts the IDE's state to prevent the AI from modifying the wrong file. |

---

## 🏗️ Architecture & Taxonomy

The ecosystem is split conceptually to allow infinite scaling across any tech stack:

1. **`.agents/`** (The Agnostic Core)
   The baseline truth. Contains the core pipelines, the Caveman Protocol, DevSecOps Python scripts, and the overarching AI logic. 
2. **Project Workspace** (The Inherited Layer)
   The active repository. It inherits the Universal rules but allows injection of specific framework canons (e.g., Flutter UI rules, React testing protocols) without polluting the global workflows.

```text
.agents/
├── canons/              # Immutable structural laws and recipes
├── rules/               # Context-aware guardrails (Security, Execution Tiers)
├── skills/              # Domain expertise triggered by JIT Routing
├── workflows/           # CI pipelines, session handoffs, test loops
├── scripts/             # The Modular CLI Ecosystem (`orion.py`)
├── templates/           # DRY source for generating IDE Master BIOS files
└── metrics/             # Telemetry, evals, and compliance testing
```

---

## 🌌 The Advanced Vision (Unbound Hardware)

The current `.agents` ecosystem is heavily optimized for resource-constrained environments (using Caveman compression, tiny SQLite graphs, and 0.5B parameter background models). 

However, if deployed on a workstation with **unlimited budget and compute** (e.g., 128GB+ RAM, massive VRAM, Dual RTX 4090s), the architecture is designed to scale into a truly autonomous engineering hive:

1. **Massive Local Swarm Concurrency**:
   Instead of using `auto_delegate.py` sequentially, an unbound system could spin up 10-20 local instances of a 70B parameter model (e.g., Llama 3 70B). The Architect skill could deploy isolated worker agents in parallel to build the UI, API, and Database simultaneously, without hitting any cloud API rate limits.
2. **Real-Time Continuous Graph Ingestion**:
   Currently, `.orion` uses SQLite FTS5 triggered on-demand to save compute. With infinite resources, a heavy continuous GraphRAG daemon could map every AST (Abstract Syntax Tree) node, every file change, and every terminal log into `.orion.db` in real-time, providing the AI with sub-second, perfect spatial awareness of the entire codebase.
3. **Zero-Latency Motor Control**:
   Instead of asking for user permission to run commands, a massive local model could run terminal execution evaluations locally at >100 tokens/second, brute-forcing compile errors and resolving dependency hell in seconds.
4. **Local Multi-Modal QA**:
   The `ui-finish` skill could utilize a local Vision Language Model (VLM) running in the background to visually audit UI renderings pixel-by-pixel against Figma blueprints, automatically fixing CSS padding without human oversight.

---

## 🚀 Deployment & Onboarding

The Universal template can be injected into any repository (Node, Rust, Flutter, Python, Go) to align the AI workflow. Instead of setting it up manually, you simply order your AI to do it for you.

### 📌 Prerequisites
- **Python 3.x** must be installed on your machine.
- Work best with **RTK** and **Local LMM for Proxy**
- Your target project must have a basic structure initialized.

### 🤖 How to Deploy (Agentic Installation)
To deploy this foundation into your project, you do **not** need to copy files manually. Just copy the exact prompt below and paste it into your IDE's AI chat (Gemini, Cursor, Copilot, Windsurf, etc.):

> *"Hey AI, please read the deployment manual at `[path-to-foundation]/.agents/DEPLOY_ME.md` and execute the python deployment engine to inject this foundation into my current project."*

👉 **Full Manual:** **[Agentic Deployment Guide (.agents/DEPLOY_ME.md)](.agents/DEPLOY_ME.md)**

*(The deployment process relies on `orion.py foundation deploy` which will automatically handle symlinking, creating `GEMINI.md`, generating `.gitignore`, and performing safe graph ingestion without human intervention).*

---

## 🤝 Credits & External Modules

This foundation synthesizes principles from top open-source optimization tools:
- **[rtk-ai/rtk](https://github.com/rtk-ai/rtk)**: (Active Binary) Compresses and filters verbose terminal output.
- **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)**: (Protocol) Telegraphic communication mapping for token reduction.

---
**License**: MIT

---
**Note**: No longer maintained. Please support with a star! 