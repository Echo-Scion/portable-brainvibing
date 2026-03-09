# VOLUME II: SYSTEM ARCHITECTURE — Anatomy of `.agents`

---

## Chapter 2: Active Router — Master BIOS (`GEMINI.md`)

The `GEMINI.md` file (and parallel host adapters such as `CLAUDE.md`) at the repository root serves as the **Master BIOS** and **Active Router** for all cognitive operations within the workspace.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Prompt / Task Goal                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                GEMINI.md (§3.5 Internal Routing Analysis)              │
│  Matches prompt against §4 JIT Table → Executes view_file on Target   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────┐
│     Core Guardrails Check     │               │   Orion Context Sync  │
│  - Evidence Mandate           │               │  `brain sync <query>` │
│  - Circuit Breaker (3 fails)  │               │  Injects 1-hop graph  │
│  - Sequential Tool Ban        │               │  and vector nodes     │
└───────────────┬───────────────┘               └───────────┬───────────┘
                │                                           │
                └───────────────────────┬───────────────────┘
                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│               Task Execution via Strict TDD / Lessword                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Unified Response Footer (§5)                      │
│   🚦 CHECKPOINT  •  📋 EVIDENCE  •  🧠 EVALUATION  •  🔮 NEXT TASK     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1. Core Guardrails & Behavioral Mandates (§1)
- **Evidence Mandate**: Never claim success without verifiable proof. `Exit Code 0` is required, but agents must verify stdout/stderr assertions, test counts, and state transitions to prevent masked failures.
- **Circuit Breaker**: If any specific tool call or test fails 3 times consecutively, STOP calling tools immediately. Output root-cause error analysis and request operator intervention.
- **No Raw CLI Patching**: Forbidden from editing source code via terminal strings (`python -c`, `sed`, `awk`). All modifications must route through native IDE file editing tools.
- **Surgical Diff Mandate**: Modify only code strictly required by the prompt. Never delete pre-existing comments, dead code, or alter adjacent formatting.
- **Code Authenticity**: Forbidden from introducing empty catch blocks (`catch (e) {}`), simulated latency (`setTimeout`/`sleep`), or synthetic mock APIs into production paths.

---

### 2.2. Session Bootstrap & JIT Knowledge Routing (§1.5 & §4)

To prevent context bloat, agents do not preload all rules. When a prompt matches a recognized trigger, the agent must load the corresponding target immediately in the first turn:

| Trigger Domain | Immediate JIT Target |
|:---|:---|
| **Setup .agents, Onboard Workspace, Doctor Check, Install Pillars, Activate Obsidian Vault / Second Brain** | `.agents/DEPLOY_ME.md` |
| **New Project, Init, Scaffold, Greenfield** | `.agents/skills/app-lifecycle/references/project-init.md` |
| **Legacy Migration, Brownfield, Migrate** | `.agents/skills/app-lifecycle/references/project-migrate.md` |
| **Feature Scaffold, New Model, Screen** | `.agents/skills/app-lifecycle/references/app-builder.md` |
| **Business Strategy, Growth, Viability** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema** | `.agents/skills/project-architect/SKILL.md` |
| **Frontend UI, Layout, Aesthetics** | `.agents/skills/ui-finish/SKILL.md` |
| **Security Audit, QA, Testing, Validation** | `.agents/skills/integrity-sentinel/SKILL.md` |
| **Data Immutability, State Management** | `.agents/skills/data-logic/SKILL.md` |
| **API Contracts, Zod, Schemas** | `.agents/skills/api-contract/SKILL.md` |
| **Orion, Knowledge Base, Ingest, Graph** | `.agents/skills/brain-graph/SKILL.md` |
| **Debugging, Errors, Crashes, Runtime** | `.agents/skills/frontend-experience/SKILL.md` & `systematic-debugging/SKILL.md` |
| **Deployment, Build, Release, CI/CD** | `.agents/skills/project-operator/SKILL.md` |
| **Performance, Latency, Speed** | `.agents/rules/performance-optimization.md` |
| **Cost Analysis, Token Budget, LLM Costs** | `.agents/skills/cost-optimizer/SKILL.md` |
| **Audit Vectors, Diagnostic Matrix** | `.agents/skills/integrity-sentinel/references/audit_vectors.md` |
| **Code Review, PR Review** | `.agents/skills/code-review/SKILL.md` |
| **Token Reduction, Lessword Mode** | `.agents/skills/lessword/SKILL.md` |
| **Session End, Handoff, Eviction** | `.agents/skills/session-offload/SKILL.md` |
| **Strict TDD, Writing Tests** | `.agents/skills/strict-tdd/SKILL.md` |
| **Agent Self-Learning, /learn** | `.agents/skills/self-evolve/SKILL.md` |
| **Documentation, Anti-Slop, Prose** | `.agents/rules/prose-authenticity.md` |

---

### 2.3. Unified Response Footer (§5)

Responses terminate with a structured status block tailored to the turn type:

**Conversational / Q&A Turn (2 lines):**
```markdown
🚦 **CHECKPOINT**: [Brief summary of explanation]
🔮 **NEXT TASK**: [Immediate next step or "None"]
```

**Standard Execution Turn (3 lines):**
```markdown
🚦 **CHECKPOINT**: [Summary of action accomplished]
📋 **EVIDENCE**: [Exit Code X, test count, or verified mechanical state]
🔮 **NEXT TASK**: [Immediate next workflow step or "None"]
```

**Premium / Deep Architectural Turn (4 lines):**
```markdown
🚦 **CHECKPOINT**: [Summary of multi-system changes accomplished]
📋 **EVIDENCE**: [Exact Exit Code and output verification status]
🧠 **EVALUATION**: [Execution smooth | Root-cause analysis if errors occurred]
🔮 **NEXT TASK**: [Next workflow step or "None"]
```

**Milestone / Phase-End Turn (4 lines):**
```markdown
🚦 **CHECKPOINT**: [Summary of milestone accomplished]
📋 **EVIDENCE**: [Exit Code X or verified mechanical state]
⚡ **RECOMMENDED TIER**: [BUDGET | STANDARD | PREMIUM]
🔮 **NEXT TASK**: [Next workflow step with recommended /slash-command]
```

---

## Chapter 3: Omni-Buffer & Execution State Synchronization

### 3.1. The Omni-Buffer (`.orion/working/context.json`)
The pre-invocation hook (`hooks/pre-agent-wake.py`) evaluates editor state before the agent processes a user turn, emitting an atomic JSON state file:
```json
{
  "timestamp_ms": 1776180000000,
  "active_file": "lib/src/auth/auth_service.dart",
  "terminal_error": "",
  "user_intent": "",
  "ide_source": "antigravity",
  "evolution_overdue": false,
  "unprocessed_learnings": 1
}
```

- **Stale Data Guard**: If `timestamp_ms` is older than 5 minutes, the agent disregards the buffer and requests direct user clarification.
- **Darwinian Evolution Flag**: If `unprocessed_learnings >= 3`, the hook flags `"evolution_overdue": true`, requiring the agent to review `.agents/skills/self-evolve/SKILL.md`.

### 3.2. Crash-Proof Execution State (`.orion/working/execution_state.json`)
Active task state is tracked through `orion.py fsm` to isolate transient session context from execution workflows. If the host IDE restarts unexpectedly, the hook injects recovery parameters, allowing the agent to resume execution at the exact interrupted step:
- **Git-Bound Checkpoints**: Every state transition captures non-destructive Git tree snapshots (`git stash create` / `git rev-parse HEAD`), stored in `fsm_checkpoints.git_tree_sha`.
- **Atomic Code Rollback**: Running `python .agents/scripts/orion.py fsm rollback --restore-code` restores both SQLite metadata and exact source files to the target checkpoint.

---

## Chapter 4: Cargo Rust Engine (`rtk` + `ast-grep`)

### 4.1. RTK (Rust Token Killer)
Compiled native Rust binary proxying CLI terminal execution. Intercepts stdout/stderr, filtering progress bars, download indicators, and redundant info lines while preserving warnings and failures:
- Eliminates 60–90% of terminal noise tokens.
- Native analytics command: `rtk gain` displays cumulative token savings.
- Direct execution bypass for raw binary inspection: `rtk proxy <cmd>`.

### 4.2. Concrete Syntax Tree Search (`ast-grep`)
Integrated polyglot CST search (`sg`) powered by Tree-sitter. Allows structural code querying and AST rewrites across 20+ programming languages without token-heavy regex parsing.

---

## Chapter 5: The Four (4) Anchored Foundation Pillars

The `.agents` architecture operates on four permanently anchored execution engines designed for zero-daemon, air-gapped sovereignty:

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Four (4) Anchored Pillars                          │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 1. Pure Python 3.10+     │ Primary cognitive orchestrator, SQLite3 WAL │
│    Stdlib (Zero-Pip)     │ FTS5, Louvain community detection, AST      │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 2. Cargo Rust Engine     │ Native rtk token hollowing and ast-grep     │
│    (rtk + ast-grep)      │ structural syntax matching                  │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 3. Universal Local AI    │ Multi-backend neural coprocessor            │
│    (Ollama / llama.cpp)  │ (Ollama, llama-server, LM Studio, vLLM)     │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 4. Bun Static Runtime    │ Zero-install MCP runner (bun x -y),         │
│    Engine (bun)          │ sub-4ms test execution, zero node_modules   │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### Sovereign Zero-Pip Mandate
Core orchestration requires zero external pip packages. All networking utilizes `urllib.request`, database operations utilize standard `sqlite3`, code analysis utilizes `ast`, and mathematical clustering utilizes standard `math` and `collections`. If any external binary is unavailable, the system degrades gracefully to pure Python stdlib fallbacks.

### Zero-Latency Capability Probe (`capabilities.py`)
Hardware and toolchain capability detection is centralized in `core/capabilities.py`. Probe results are cached in `.orion/working/capabilities.json` with a 900-second TTL to eliminate subprocess invocation overhead during agent turns. Inspect active runtime capabilities at any time via:
```bash
python .agents/scripts/orion.py preflight --pillars
```

---

## Chapter 6: Centaur Exoskeleton & Fail-Closed Enforcement Architecture

To guarantee that probabilistic language models operate within deterministic safety boundaries, `.agents` implements a Centaur Exoskeleton architecture that physically separates agent reasoning from execution gates.

### 6.1. Exoskeleton Fail-Closed PreToolUse Interception (`core/capabilities.py`)
The Antigravity `PreToolUse` hook intercepts every tool invocation before execution:
- **Inline Circuit Breaker Evaluation**: The 3-strike circuit breaker in `failures.log` is evaluated directly within the hook execution path.
- **Strict Fail-Closed Contract**: If a stuck loop is detected, the circuit breaker is tripped, or an unhandled hook exception occurs, the hook emits `{"decision": "block", "reason": "..."}` with Exit Code `3`, physically halting execution and forcing human reflection rather than failing open.

### 6.2. Sovereign Sandbox & PEP 578 Syscall Containment (`core/sandbox.py`)
Exploratory and untrusted Python scripts execute within an isolated sandbox environment:
- **Fail-Closed AST Gate**: AST security inspection runs prior to execution. If the security auditor fails to initialize, execution is immediately blocked (Exit Code `126`).
- **PEP 578 Audit Hook**: Runtime audit events intercept destructive filesystem mutations (`os.remove`, `os.unlink`, `os.rmdir`, `os.rename`, `os.replace`, `shutil.rmtree`) and subprocess execution (`os.system`, `subprocess.Popen`) targeting paths outside `_JAIL_ROOT`.

### 6.3. Anti-False-Green TDD State Hardening (`core/capabilities.py`)
State bypasses are locked against accidental or adversarial greenwashing:
- **10-Minute TTL Expiration**: Transient flags such as `.orion/working/adversarial.json` and `TDD_RED` expire after 10 minutes, preventing stale error suppressions.
- **Verified Test Gating**: Failure counters in `failures.log` can only be reset by a verified test suite pass (`Exit Code 0`), preventing benign commands like `git status` from clearing failure streaks.

### 6.4. Deterministic Prompt-in-Data Sandboxing (`utils/packer.py`)
When exporting codebase context bundles for multi-model frontier audits:
- **Tag Breakout Protection**: Literal closing tags (`</artifact>`) within source files are escaped to `&lt;/artifact&gt;`, eliminating XML envelope breakouts.
- **Directive Verb Neutralization**: Imperative action verbs (`Immediately Load`, `Execute view_file ... IMMEDIATELY`) in Markdown tables and bullet lists are neutralized to prevent data from masquerading as system instructions.

### 6.5. Modular Gateway CLI Architecture (`commands/`)
The monolithic `commands/brain.py` (5,211 lines) is decomposed into four focused Gateway CLI engines, maintaining strict sub-500-line modularity targets while preserving full backward compatibility:
- **`commands/compact.py`** (1,582 lines): 5-tier context compaction (`lite`, `stream`, `full`, `aggressive`, `ultra`, `pipeline`), stream elision, and Lessword protocol execution.
- **`commands/rag.py`** (558 lines): Local hybrid retrieval combining SQLite FTS5 BM25, packed float32 vector embeddings, 1-hop graph neighbor expansion, and RAG diagnostic scoring.
- **`commands/vault.py`** (125 lines): Obsidian-compatible graph vault export and 4-note Second Brain briefing generation.
- **`commands/brain.py`** (2,990 lines): Unified cognitive facade, Ollama hardware discovery (`NanoBrain`), rule matrix compilation, and backward-compatible command routing.

### 6.6. Universal Project DNA v2 & Multi-Workspace Packer Engine (`utils/packer.py`)
To enable multi-model frontier code audits without file upload limit friction or context explosion:
- **Monorepo & Polyglot Discovery**: Recursively detects polyglot manifests across root and nested sub-containers (`apps/`, `packages/`, `services/`, `modules/`, etc.).
- **5-Tier Architectural Taxonomy**: Classifies application files into architectural strata: `contracts` (DTOs, schemas), `domain` (models, entities, usecases), `services` (clients, network, database), `state` (blocs, controllers, stores), and `presentation` (views, screens, components).
- **Cross-Bundle Import Router**: Identifies cross-bundle dependencies across standard source roots (`src/`, `lib/`, `app/`, `packages/`) while filtering generic file stems (`index`, `main`, `mod`, `route`).
- **Polyglot Static Audit Radar**: Evaluates execution sinks (`eval`, `exec`, `spawn`, `Process.run`, `Runtime.exec`, `dangerouslySetInnerHTML`) and empty catches (`catch {}`) across 10+ languages, surfacing a pre-audit radar in Bundle 01.
- **Global AST Symbol Compass**: Indexes polyglot declarations (Rust `pub fn`/`struct`, Go `func`/`type`, TypeScript/React `export const ... =>`, Dart/Java classes) for zero-latency lookup.
- **Balanced Subtree Bin-Packing**: Uses `balance_into_k_bundles()` to partition repository volume into at most 10 balanced Markdown files (`.md`) across isolated tier subfolders (`.orion/bundles/{arch,hybrid,full}/`).

