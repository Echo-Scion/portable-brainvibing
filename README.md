# Portable Brainvibing — AI-Surgical Infrastructure

> **v1.4.0 — Autonomous Pipeline & Flutter Recipes**

A plug-and-play `.agents` ecosystem that turns any AI coding assistant into a **precision instrument** instead of a generic chatbot. Works identically across Gemini, Claude, Cursor, Windsurf, Copilot, and Cline via a Single Source of Truth (`AGENTS.template.md`).

---

## The Problem

AI coding assistants ignore rules written as prohibitions ("Don't commit secrets"). They hallucinate syntax, skip error states, and forget instructions placed deep in secondary files. Generic "system prompts" do not change model behavior — they're cosmetic. Furthermore, when executing complex tasks, they suffer from **Attention Decay** and forget what step they are on.

## The Solution

This foundation replaces **prohibitions** with **algorithms**, and introduces an **Autonomous Pipeline Architecture** to keep the AI focused:

| Traditional Prompt | This Foundation |
| :--- | :--- |
| "Don't commit API keys" | `python secrets_scan_verifier.py` → `[PASS]` or `[FAIL]` with file:line |
| "Act like an elite architect" | Mandatory 6-section Blueprint Template (fill it or task fails) |
| "Remember the plan" | **State Machine Persistence** (`.wiki/task.md`) checks off tasks automatically |
| "What should we do next?" | **Auto-Chain Triggers** in the footer queue the exact next command |
| "Be concise" | Caveman Protocol with built-in behavioral anchors in the Master BIOS |

---

## Prerequisites & Dependencies

To unlock the full potential of the Autonomous Pipeline, ensure the following tools are installed on your host machine:

- **Python 3.10+**: Required for the verification harnesses and `.agents/scripts/` automation.
- **MCP Servers (Optional but Recommended)**: The ecosystem supports MCPs (Model Context Protocol) for external tools like Github, Supabase, and Dart-MCP to augment agent workflows.
- **Node.js (NPM)**: Required to install QMD for semantic memory search.
  - Install QMD: `npm install -g @tobilu/qmd`
- **Rust (Cargo)**: Required for RTK (Rust Token Killer) for massive token savings on terminal outputs.
  - Install RTK: `cargo install rtk`

---

## Quick Start

### 1. Deploy to a New Project
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/your/project
```
*(This uses `AGENTS.template.md` to instantly generate `GEMINI.md`, `CLAUDE.md`, and Copilot configs in the target project).*

### 2. Verify Integrity
```bash
python .agents/scripts/verify_agents.py
```

### 3. Start Coding
The AI will automatically pick up the root instructions and begin following the JIT routing table, loading skills on-demand.

---

## Architecture

```
.agents/
├── canons/              # Immutable laws (architecture + harnesses + Flutter recipes)
├── rules/               # Algorithmic guardrails (e.g., 3-Tier Execution, Security)
├── skills/              # Domain expertise with mandatory output templates
├── workflows/           # Step-by-step pipelines with Auto-Chain Triggers
├── scripts/             # Runnable Python utilities (Deployment, Verification)
├── templates/           # Single AGENTS.template.md (100% DRY multi-AI deployment)
├── docs/                # Human-readable deployment manuals
└── evals/               # AI compliance benchmarks
```

---

## Key Features

### 🧠 JIT Auto-Pilot Router
The root Master BIOS acts as an **Active Router**. The AI only loads the skill/workflow it needs based on keyword triggers (e.g., "Start a project" → `flutter-init.md`) — preventing token bloat from reading everything upfront.

### 🏭 Autonomous Pipeline (The Conveyor Belt)
Inspired by multi-agent frameworks, this architecture wires single-agent interactions into a continuous loop:
- **Output-as-Input**: Skills don't run in a vacuum. The Strategist writes to `.wiki/CONTEXT.md`, and the Architect is forced to read it before generating `.wiki/BLUEPRINT.md`.
- **State Machine**: Workflows automatically generate and maintain `.wiki/task.md`, checking off `[/]` and `[x]` to prevent attention decay.
- **Auto-Chain Triggers**: The AI never ends a response with a generic question. The Unified Footer forces it to queue the exact terminal command needed for the next step.

### 🔧 Python Verification Harnesses
External enforcement via runnable scripts, not "AI willpower":
- **`secrets_scan_verifier.py`** — Regex-based scan for API keys, tokens, passwords
- **`migration_verifier.py`** — Blocks `DROP TABLE`, `TRUNCATE`, open RLS policies
- **`verify_agents.py`** — Master integrity checker for the `.agents` ecosystem

### ⚖️ 3-Tier Reasoning Model
We use a streamlined tier system to route processing power:
- **BUDGET**: Simple fixes, atomic reads.
- **STANDARD**: Multi-file edits, standard UI components.
- **PREMIUM**: Core architecture, security audits, complex state management.

### 🗣️ Multi-AI Support (100% DRY)
A single `AGENTS.template.md` deploys consistent rules across 6 AI assistants: Gemini, Claude, Cursor, Windsurf, Copilot, and Cline.

---

## Scripts Reference

| Script | Purpose |
| :--- | :--- |
| `verify_agents.py` | Master integrity checker (broken links, frontmatter, compliance) |
| `deploy_foundation.py` | Deploy `.agents` to any project using the DRY template |
| `code_map.py` | AST skeleton map (~300 tokens vs ~5000 for full read) |
| `token_audit.py` | Find files exceeding 500-line ghost token limit |
| `compress_memory.py` | Compress memory files to save input tokens |
| `sync_ai_configs.py` | Sync AI configs after foundation updates |
| `bootstrap_wiki.py` | Initializes the `.wiki/` infrastructure for memory persistence |

---

## Changelog

| Version | Date | Notes |
| :--- | :--- | :--- |
| **1.4.0** | 2026-05-20 | Autonomous Pipeline Injection, Unified Footer, 3-Tier Model, Flutter Recipes, DRY Templates |
| **1.3.0** | 2026-04-18 | RTK, QMD, Caveman adoption |
| **1.2.0** | 2026-03-26 | 10 Prompt Patterns, Root GEMINI.md |
| **1.1.0** | 2026-03-20 | 4-pillar structure, 82-file SaaS mapping |
| **1.0.0** | 2026-03-19 | Clean Reset |

---

## External References & Credits
This foundation is heavily inspired by and integrates principles from several open-source projects:
- **[MetaGPT](https://github.com/geekan/MetaGPT)**: The inspiration for the Conveyor Belt architecture, Output-as-Input mechanisms, and State Machine persistence.
- **[rtk-ai/rtk](https://github.com/rtk-ai/rtk)**: (Active Binary) Utilized to compress and filter verbose terminal outputs.
- **[tobi/qmd](https://github.com/tobi/qmd)**: (Native Engine) Powers the local semantic search for dynamic context discovery.
- **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)**: (Active Skill) Provides the telegraphic communication protocol for 75% output reduction.
- **[drona23/claude-token-efficient](https://github.com/drona23/claude-token-efficient)**: (Rules) Integrated into core mandates for terse response patterns.
- **[nadimtuhin/claude-token-optimizer](https://github.com/nadimtuhin/claude-token-optimizer)**: (Templates) Optimized project setup patterns in `.agents/templates`.
- **[alexgreensh/token-optimizer](https://github.com/alexgreensh/token-optimizer)**: (Logic Ported) Powers the `token_audit.py` for ghost token detection.
- **[tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph)**: (Logic Ported) Powers the `code_map.py` for structural code skeleton mapping.

---

## License

MIT
