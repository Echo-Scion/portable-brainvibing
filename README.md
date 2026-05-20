# Portable Brainvibing — AI-Surgical Infrastructure

> **v3.0.0 — Algorithmic Upgrade**

A plug-and-play `.agents` ecosystem that turns any AI coding assistant into a **precision instrument** instead of a generic chatbot. Works with Gemini, Claude, Cursor, Windsurf, Copilot, and Cline.

---

## The Problem

AI coding assistants ignore rules written as prohibitions ("Don't commit secrets"). They hallucinate syntax, skip error states, and forget instructions placed deep in secondary files. Generic "system prompts" do not change model behavior — they're cosmetic.

## The Solution

This foundation replaces **prohibitions** with **algorithms**:

| Traditional Prompt | This Foundation |
| :--- | :--- |
| "Don't commit API keys" | `python secrets_scan_verifier.py` → `[PASS]` or `[FAIL]` with file:line |
| "Act like an elite architect" | Mandatory 6-section Blueprint Template (fill it or task fails) |
| "Be concise" | Caveman Protocol with 3 Before/After transformation examples |
| "Use the right model" | Auto-Router Decision Tree that predicts the optimal model tier |

---

## Quick Start

### 1. Deploy to a New Project
```bash
python .agents/scripts/deploy_foundation.py --target /path/to/your/project
```

### 2. Verify Integrity
```bash
python .agents/scripts/verify_agents.py
```

### 3. Start Coding
The AI will automatically pick up `GEMINI.md` (or `CLAUDE.md`, `.cursorrules`, etc.) and begin following the JIT routing table, loading skills on-demand.

---

## Architecture

```
.agents/
├── canons/              # Immutable laws (architecture + harnesses)
│   ├── global/          # Core architecture + Python verification harnesses
│   │   └── harnesses/   # secrets_scan_verifier.py, migration_verifier.py
│   └── micro/           # Budget-model cheat sheets (Flutter, Supabase, Git)
├── rules/               # Algorithmic guardrails & decision trees (17 files)
├── skills/              # Domain expertise with mandatory output templates (15 skills)
├── workflows/           # Step-by-step pipelines with exact commands (10 workflows)
├── scripts/             # Runnable Python utilities (13 scripts)
├── templates/           # Multi-AI config templates (Gemini, Claude, Cursor, etc.)
├── docs/                # Human-readable deployment manuals
└── evals/               # AI compliance benchmarks
```

---

## Key Features

### 🧠 JIT Auto-Pilot Router
The root `GEMINI.md` acts as an **Active Router**. The AI only loads the skill/rule it needs based on keyword triggers — no token bloat from reading 59 files upfront.

### 🔧 Python Verification Harnesses
External enforcement via runnable scripts, not "AI willpower":
- **`secrets_scan_verifier.py`** — Regex-based scan for API keys, tokens, passwords
- **`migration_verifier.py`** — Blocks `DROP TABLE`, `TRUNCATE`, open RLS policies
- **`verify_agents.py`** — Master integrity checker for the `.agents` ecosystem

### 📋 Mandatory Output Templates
Every skill forces the AI to fill a concrete template:
- **Project Architect** → 6-section Blueprint with "The Cut List"
- **Integrity Sentinel** → Audit Report (Severity + Reproduction + Code Fix)
- **SaaS Strategist** → Context File + Viability Scorecard
- **API Contract** → Zod Schemas for Auth, Pagination, Strict Updates

### 🌳 Decision Trees (Not Opinions)
Rules use branching logic instead of generic advice:
- File > 500 lines? → Mandatory refactor
- Data changes < 1x/min? → Cache it
- Command outputs text stream? → Use RTK proxy

### 🗣️ Multi-AI Support
Deploy consistent rules across 6 AI assistants:

| AI | Config File | Format |
|---|---|---|
| Gemini | `GEMINI.md` | Markdown |
| Claude | `CLAUDE.md` | Markdown |
| Cursor | `.cursorrules` | Rules |
| Windsurf | `.windsurfrules` | Rules |
| Copilot | `.github/copilot-instructions.md` | Markdown |
| Cline | `.clinerules` | Rules |

---

## Philosophy

This ecosystem treats the AI as a **statistical model**, not a human employee.

- ❌ "Don't be lazy" → AI has no concept of laziness
- ✅ `Decision Tree + Output Template + Python Harness` → Mechanically enforced

See [EXPLAIN.md](EXPLAIN.md) for the full ecosystem guide with file-by-file documentation.

---

## Scripts Reference

| Script | Purpose |
| :--- | :--- |
| `verify_agents.py` | Master integrity checker (broken links, frontmatter, compliance) |
| `deploy_foundation.py` | Deploy `.agents` to any project |
| `code_map.py` | AST skeleton map (~300 tokens vs ~5000 for full read) |
| `token_audit.py` | Find files exceeding 500-line ghost token limit |
| `compress_memory.py` | Compress memory files to save input tokens |
| `sync_ai_configs.py` | Sync AI configs after foundation updates |

---

## Changelog

| Version | Date | Notes |
| :--- | :--- | :--- |
| **3.0.0** | 2026-05-20 | Algorithmic Upgrade: Decision Trees, Output Templates, Python harnesses, JIT Router, predictive Binary Oratory |
| **1.3.0** | 2026-04-18 | RTK, QMD, Caveman adoption |
| **1.2.0** | 2026-03-26 | 10 Prompt Patterns, Root GEMINI.md |
| **1.1.0** | 2026-03-20 | 4-pillar structure, 82-file SaaS mapping |
| **1.0.0** | 2026-03-19 | Clean Reset |

---

## License

MIT
