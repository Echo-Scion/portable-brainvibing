# AI Brain: Main Encyclopedia of the `.agents` & `.orion` Ecosystem
# (Portable Brainvibing Infrastructure v0.0.3)

> **Complete Technical Encyclopedia.** Every architectural pillar, deterministic guardrail, local RAG component, script cluster, and operational skill is documented with technical precision and exact code examples.

---

## 1. Executive Summary & Architectural Synthesis

The `.agents` infrastructure is an agentic engineering engine designed to convert probabilistic Large Language Models (LLMs) into reliable, deterministic software delivery agents. 

Rather than relying on ad-hoc prompts or bloated external frameworks, `.agents` consolidates structural patterns across developer-tooling, formal verification, and cognitive memory into a cohesive, zero-daemon framework:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Master BIOS (AGENTS.md)                         │
│     JIT Knowledge Router • Evidence Mandate • Sequential Tool Ban      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│ Rule Library │             │ Domain Skill │             │  Execution   │
│  (`rules/`)  │             │ (`skills/`)  │             │   Scripts    │
│  13 Active   │             │  21 Domain   │             │ (`scripts/`) │
│  Standards   │             │ (+1 Internal)│             │  5 Clusters  │
└──────┬───────┘             └──────┬───────┘             └──────┬───────┘
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   The Four (4) Anchored Pillars                        │
│  1. Pure Python 3.10+ Stdlib   •  2. Cargo Rust Engine (rtk + sg)      │
│  3. Ollama Coprocessor         •  4. Bun Static Runtime (bun)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Orion Knowledge Graph (.orion/)                     │
│   SQLite3 WAL • FTS5 BM25 • Dual-Level GraphRAG • Observational Memory │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Architecture Highlights
- **Four Anchored Pillars (Zero-Pip Floor)**: Runs out-of-the-box on pure Python 3.10+ standard library (`ast`, `re`, `sqlite3`, `hashlib`, `urllib`). Optional native accelerators unlock hardware performance and degrade gracefully when absent: Cargo Rust (`rtk` terminal proxy + `ast-grep` CST matcher), local neural coprocessors (`Ollama`, `llama-server`, `LM Studio`, `vLLM`), and the `Bun` static TypeScript/MCP runtime.
- **Master BIOS & 33-Row JIT Knowledge Router (`AGENTS.md`)**: Dynamic Just-In-Time (JIT) skill and canon dispatch that loads only domain-relevant runbooks on demand, preventing prompt saturation and "Lost in the Middle" attention decay across 19 supported AI IDEs and CLIs.
- **Dual-Level GraphRAG & 3-Tier Observational Memory (`orion.db`)**: Combines SQLite3 WAL FTS5 Porter BM25 lexical search, packed `float32` vector embeddings, 1-hop entity-relation traversal, and pure-Python Louvain modularity community clustering. Raw session turns (`recall_turns`) compress into anchored observations (`[O1]`–`[On]`) and roll over into `memory_generations` via zero-LLM Shannon Surprisal scoring with `superseded_by` anti-flashback filtering.
- **Sovereign Skill Harness & Code-As-Harness (`core/harness/`)**: In-tree implementation of the *Agent = Model + Execution Harness* architecture. Governs skill staging (`staging.py`), 14-gate admission promotion (`admission.py`), opportunity-relative lifecycle archival (`lifecycle.py`), prefix cluster curation (`curator.py`), quantum tool telemetry (`capture.py`), and programmatic synthesis of `is_legal_action` verification scripts (`engine.py`).
- **Living Architectural DNA & Epigenetic Linter (`core/dna.py`)**: Sequences any repository into 6 architectural strata ($T_0 \to T_5$), discovers brownfield folder naming conventions via Epigenetic Aliases without forcing directory renames, and audits directional import violations to compute a deterministic `dna_compliance_score` (0–100).
- **Zero-Escape Bento Task Slicer (`commands/bento_slicer.py`)**: Decomposes multi-file implementation plans into single atomic task sheets (`.orion/working/ACTIVE_TASK.md`) sorted by topological blast-radius ($T_0 \to T_5$) and bottom-up line order. Recalibrates live disk line spans, auto-aligns indentation deltas, and enforces a Post-Condition Disk Mutation Gate (`Exit Code 2` on no-op skips).
- **Cache-Aware Crash-Proof State Machine (`pre-agent-wake.py`, `state_machine.py`)**: Separates static editor context (`context.json`, guarded by a 5-minute SHA-256 structural hash gate to preserve LLM KV prompt caches) from transactional workflow execution (`execution_state.json` with Git-bound tree checkpoints for atomic code rollback).
- **Centaur Exoskeleton & Fail-Closed Interception (`capabilities.py`, `sandbox.py`, `db.py`)**: Enforces a 3-strike `PreToolUse` circuit breaker (`Exit Code 3`), a PEP 578 syscall-jailed Python sandbox (`Exit Code 126`), and `@mechanical_catch` post-condition decorators that trap silent semantic failures and deep-copy mutable fallbacks.
- **Universal Context Packer & Digestpack (`utils/packer.py`)**: Clusters polyglot monorepos using PageRank centrality and AST import cohesion into at most 10 balanced Markdown bundles (`.orion/bundles/{arch,hybrid,full}/`), embedding a Cross-Bundle Import Router, Pre-Audit Static Risk Radar, Prompt-in-Data XML breakout shield, and a 4-turn Gemini Web Audit Playbook.
- **Consequence-Driven Evals & 8-Gate Mechanical Verifier (`evals/`, `verify_agents.py`)**: Prevents "False Green" tests via `ConsequenceVerifier` (checking DOM/Widget, State/DB, Network/IPC, and Layout geometry consequences), `AssertionEngine`, `audit_aesthetics.py` (WCAG 2.1 AA contrast math & 54-pattern anti-slop prose scanner), and an 8-gate repository verifier (`orion.py verify`) backed by 26 automated test suites.

---

## 2. Complete System Inventory (Physical Baseline)

| Subsystem | Physical Path | Verified Inventory & Scope |
|:---|:---|:---|
| **Root BIOS & Index** | `AGENTS.md`, `.agents/AGENTS_INDEX.md` | 33-row JIT Router, Iron Evidence Law, Lessword Mode, Unified Footer |
| **Rule Library** | `.agents/rules/*.md` | 13 Active Standards + `RULES_INDEX.md` + `ast/security_rules.yml` |
| **Domain Skills** | `.agents/skills/*/SKILL.md` | 21 Public Domain Skills (+1 Internal) & 51 Tier-3 Reference Runbooks |
| **Gateway CLI Engines** | `.agents/scripts/commands/*.py` | 9 Modular Engines (`brain`, `bento_slicer`, `compact`, `rag`, `vault`, `foundation`, `state_machine`, `reflexion`, `verify_agents`) |
| **Core Kernel Modules** | `.agents/scripts/core/*.py` | 10 Core Modules (`db`, `memory`, `capabilities`, `dna`, `orion_graph`, `scanner`, `security`, `sandbox`, `paths`, `platform_manifests`) |
| **Sovereign Skill Harness** | `.agents/scripts/core/harness/*.py` | 6 Harness Modules (`engine`, `admission`, `capture`, `staging`, `lifecycle`, `curator`) |
| **Context Packer** | `.agents/scripts/utils/packer.py` | Polyglot DNA Discovery, PageRank Clustering, 10-Bundle Bin-Packer |
| **Automated Evaluators** | `.agents/evals/*.py` | 3 Evaluators (`audit_aesthetics.py`, `assertion_engine.py`, `consequence_verifier.py`) + `evals.json` |
| **Lifecycle Hooks** | `.agents/hooks/*` | `pre-agent-wake.py`, `rtk-pre-tool.py`, `run-hook.cmd`, `run-hook.sh` |
| **Ecosystem Canons** | `.agents/canons/**` | 48 Verified Canons across `ecosystems/` (`flutter`, `python`, `react`, `ast-grep`, `bun`, `obsidian`, `rtk`), `global/` (with 3 action verifiers), and `micro/` |
| **Scaffold Templates** | `.agents/templates/*` | 19 Templates (`VISION`, `AGENTS`, `PROJECT_SCAFFOLD`, `MEMORY`, `DESIGN`, etc.) |
| **SQLite Knowledge Store** | `.orion/orion.db` | 18 Relational Tables + 3 FTS5 Virtual Tables + 2 Compatibility Views (`nodes`, `edges`) |
| **Automated Test Suites** | `.agents/scripts/tests/test_*.py` | 26 Unittest Contract Suites verifying all core engines and safety gates |

---

## 3. Table of Contents

| Volume | Title | Core Focus & Audited Subsystems |
|:---|:---|:---|
| [Volume I](01-theoretical_foundation.md) | Theoretical Foundation | 8 root LLM failure modes, deterministic mitigations, and 4-Tier Hybrid Cognition |
| [Volume II](02-system_architecture.md) | System Architecture | Master BIOS, Omni-Buffer, Living DNA (`dna.py`), Bento Slicer, Exoskeleton & Packer |
| [Volume III](03-local_rag_brain.md) | Local RAG Brain (`.orion/`) | Complete 21-table SQLite3 WAL schema, Dual-Level Louvain GraphRAG & Generational Rollover |
| [Volume IV](04-rule_library___rules.md) | Rule Library (`rules/`) | Complete catalog of 13 behavioral laws, precedence hierarchy, and AST security rules |
| [Volume V](05-skill___persona___skills.md) | Skill & Persona (`skills/`) | 3-Tier Progressive Disclosure, 21 public domain skills (+1 internal), and 51 references |
| [Volume VI](06-workflow___sop.md) | Procedural Playbooks & SOPs | Full Lifecycle State Machine (Phases 0–6) and 18 canonical operating procedures |
| [Volume VII](07-python_scripts___scripts.md) | Execution Engine (`scripts/`) | Complete module-by-module reference for `core/`, `core/harness/`, `commands/`, `verify_agents` 8 Gates & 26 Test Suites |
| [Volume VIII](08-canons__templates__hooks__evals__and_archives.md) | Canons, Templates, Hooks & Evals | 48 Canons, Code-As-Harness verifiers, 19 Templates, Hooks, and 3 Evaluation Engines (`evals/`) |
| [Volume IX](09-darwinian_evolution_lifecycle.md) | Darwinian Evolution & Harness | Sovereign Skill Harness (`core/harness/`), 14 Admission Gates, Observation Ledger, Barrier Escalation & Reflexion Auto-Heal |
| [Volume X](10-deployment_flow_to_new_projects.md) | Spoke Deployment Flow | 19-Platform IDE Manifest Matrix, Dependency-Aware Stack Resolver, Non-Interactive Setup & Bidirectional Sync |
| [Volume XI](11-complete_glossary.md) | Complete Glossary | Canonical engineering definitions for all mechanisms, algorithms, and contracts |
