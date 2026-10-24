# VOLUME II: SYSTEM ARCHITECTURE — Anatomy of `.agents`

---

## Chapter 2: Active Router — Master BIOS (`AGENTS.md`)

The `AGENTS.md` file (with host adapter aliases such as `GEMINI.md` and `CLAUDE.md`) at the repository root serves as the **Master BIOS** and **Active Router** for all cognitive operations within the workspace.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Prompt / Task Goal                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│           AGENTS.md (§1.5 Bootstrap & §3.5 Routing Analysis)           │
│  1. Checks `.orion/working/ACTIVE_TASK.md` (Bento Single-Task Gate)    │
│  2. Matches prompt against §4 JIT Table → Executes view_file on Target │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
┌───────────────────────────────┐               ┌───────────────────────┐
│     Core Guardrails Check     │               │   Orion Context Sync  │
│  - Evidence Mandate           │               │  `brain sync <query>` │
│  - Circuit Breaker (3 fails)  │               │  Injects 1-hop graph  │
│  - Zero Contiguous Paging     │               │  and vector nodes     │
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
│  🚦 CHECKPOINT • 📋 EVIDENCE • ⚡ RECOMMENDED TIER • 🔮 NEXT TASK       │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 2.1. Core Guardrails & Behavioral Mandates (§1)
- **Evidence Mandate**: Never claim success without verifiable proof. `Exit Code 0` is required, but agents must verify stdout/stderr assertions, test counts, and state transitions to prevent masked failures.
- **Circuit Breaker**: If any specific tool call or test fails 3 times consecutively, STOP calling tools immediately. Output root-cause error analysis and request operator intervention.
- **Code Skeleton First (Zero Contiguous Paging)**: Files $\le 350$ lines may be read directly. For files $> 350$ lines, agents must run `python .agents/scripts/orion.py scan map <file>` first to obtain exact `[Lstart-Lend]` symbol spans before reading targeted blocks.
- **No Raw CLI Patching**: Forbidden from editing source code via terminal strings (`python -c`, `sed`, `awk`). All modifications must route through native IDE file editing tools.
- **Surgical Diff Mandate**: Modify only code strictly required by the prompt. Never delete pre-existing comments, dead code, or alter adjacent formatting.
- **Code Authenticity**: Forbidden from introducing empty catch blocks (`catch (e) {}`), simulated latency (`setTimeout`/`sleep`), or synthetic mock APIs into production paths.

---

### 2.2. Session Bootstrap & JIT Knowledge Routing (§1.5 & §4)

During session bootstrap, if `.orion/working/ACTIVE_TASK.md` exists, the agent reads it first and executes only that single atomic Bento task before running `python .agents/scripts/orion.py bento next --verify`.

To prevent context bloat, agents do not preload all rules. When a prompt matches a recognized trigger, the agent loads the corresponding target immediately in the first turn:

| If User Prompt Relates To... | Immediately Load (view_file / Read) |
| :--- | :--- |
| **Setup .agents, Onboard Workspace, Doctor Check, Install Pillars, Activate Obsidian Vault / Second Brain** | `.agents/DEPLOY_ME.md` |
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/skills/app-lifecycle/references/project-init.md` |
| **Legacy Migration, Brownfield, Onboard Existing, Migrate Project** | `.agents/skills/app-lifecycle/references/project-migrate.md` |
| **Feature Scaffold, App Builder, New Model, Repository, Screen, End-to-End Feature Creation** | `.agents/skills/app-lifecycle/references/app-builder.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint, Backend Logic, Node.js, API, Server, Cache** | `.agents/skills/project-architect/SKILL.md` |
| **Frontend UI, Layout, Aesthetics, Visual Craft, Animations, Code Comment Hygiene** | `.agents/skills/ui-finish/SKILL.md` |
| **Security Audit, QA, Testing, Bugs, Validation (App Code)** | `.agents/skills/integrity-sentinel/SKILL.md` |
| **Data Immutability, State Management, Transformers** | `.agents/skills/data-logic/SKILL.md` |
| **API Contracts, Zod, Schemas, Request Validation** | `.agents/skills/api-contract/SKILL.md` |
| **Orion, Knowledge Base, Ingest, Lint, Cross-reference** | `.agents/skills/brain-graph/SKILL.md` |
| **Debugging, Errors, Crashes, Runtime Issues** | `.agents/skills/frontend-experience/SKILL.md` & `.agents/skills/systematic-debugging/SKILL.md` |
| **Deployment, Build, Release, CI/CD, DevOps** | `.agents/skills/project-operator/SKILL.md` |
| **Performance, Latency, Speed, Optimization** | `.agents/rules/performance-optimization.md` & `.agents/skills/cost-optimizer/SKILL.md` |
| **Cost Analysis, Token Budget, LLM Costs** | `python .agents/scripts/orion.py scan tokens` (Run it!) & `.agents/skills/cost-optimizer/SKILL.md` |
| **meta-agent-admin, /meta-agent-admin, Audit .agents, Ecosystem Audit, Foundation Review, Template Health, System Mod, Rules** | `.agents/AGENTS_INDEX.md` & `.agents/skills/meta-agent-admin/SKILL.md` |
| **Code Review, PR Review (App Code)** | `.agents/skills/code-review/SKILL.md` |
| **Token Reduction, Compression, Lessword Mode** | `.agents/skills/lessword/SKILL.md` & `.agents/skills/lessword/references/lessword-compress.md` |
| **Accessibility, A11y, Micro-interactions, Web UX** | `.agents/skills/palette/SKILL.md` |
| **Session End, Handoff, Context Eviction** | `.agents/skills/session-offload/SKILL.md` |
| **Test-Driven Development (TDD), Writing Tests** | `.agents/skills/strict-tdd/SKILL.md` |
| **Full Lifecycle Pipeline, State Machine** | `.agents/skills/app-lifecycle/SKILL.md` |
| **Feature Deprecation, Sunset Code, Dead Code Purge** | `.agents/skills/app-lifecycle/references/feature-sunset.md` |
| **Agent Self-Learning, Reflection, Pattern Synthesis, Harness, Autoharness, /learn** | `.agents/skills/self-evolve/SKILL.md` |
| **Agent Identity, Onboarding, Personality, Bootstrap** | `context/AGENT_IDENTITY.md` (or `.agents/templates/agent-identity-template.md` if uninitialized) |
| **Temporal Pulse, Daily Summary, Weekly Synthesis** | `.agents/skills/self-evolve/references/temporal-pulse.md` |
| **Worker Delegation, Sub-agent, Task Splitting** | `.agents/skills/worker-delegate/SKILL.md` |
| **AI Engineering, Model Drift, Probabilistic Traits** | `.agents/skills/ai-engineer/SKILL.md` |
| **Codebase Audit, Audit Ledger, Multi-Session Audit** | `.agents/skills/integrity-sentinel/references/audit-ledger.md` |
| **Audit Vectors, Deep Diagnostic Matrix, Logic/Fail-Fast/Bloat/DRY** | `.agents/skills/integrity-sentinel/references/audit_vectors.md` |
| **Business Rule Extraction, Conversational Context** | `.agents/skills/session-offload/references/auto-context.md` |
| **Knowledge Extraction, Graph Triplet Ingestion** | `.agents/skills/brain-graph/references/knowledge-extraction.md` |
| **Documentation, Copywriting, Readme, PR Description, Anti-Slop, Prose** | `.agents/rules/prose-authenticity.md` |

---

### 2.3. Unified Response Footer & Manual Model Routing (§5)

Every delivered response terminates with a standardized footer that advises the operator which model tier (`BUDGET`, `STANDARD`, or `PREMIUM`) to select for the upcoming `NEXT TASK` (omitting `RECOMMENDED TIER` only when `NEXT TASK` is `"None"`):

**Conversational / Q&A Turn (3 lines):**
```markdown
🚦 **CHECKPOINT**: [Brief summary of the answer or explanation]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next step or "None"]
```

**Standard / Execution / Planning Turn (4 lines):**
```markdown
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [Exit Code X, test status, or verified mechanical state]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Immediate next workflow step or /slash-command]
```

**Premium / Deep Architectural Turn (5 lines):**
```markdown
🚦 **CHECKPOINT**: [Brief summary of what was accomplished]
📋 **EVIDENCE**: [State the EXACT Exit Code or output status. If Exit Code > 0, do NOT claim success.]
🧠 **EVALUATION**: [Execution smooth | Execution rough: brief root-cause / error analysis]
⚡ **RECOMMENDED TIER**: [BUDGET (Flash/Haiku) | STANDARD (Pro/Sonnet) | PREMIUM (Thinking/Opus)] — [1-phrase reason for NEXT TASK]
🔮 **NEXT TASK**: [Next workflow step. MUST include a /slash-command recommendation if applicable, e.g. /integrity-sentinel]
```

---

## Chapter 3: Cache-Aware Omni-Buffer & Execution State Synchronization

### 3.1. The Cache-Aware Omni-Buffer (`.orion/working/context.json`)
The pre-invocation hook (`hooks/pre-agent-wake.py`) evaluates editor state, active Bento tasks, and observation digests before the agent processes a turn:
```json
{
  "timestamp_ms": 1776180000000,
  "structural_hash": "9c4b1e8a7f0d2c3b",
  "active_file": "lib/src/auth/auth_service.dart",
  "terminal_error": "",
  "user_intent": "",
  "ide_source": "antigravity",
  "evolution_overdue": false,
  "unprocessed_learnings": 1,
  "active_bento_task": {
    "task_id": "2.1",
    "title": "Add Post-Condition Disk Mutation Gate",
    "target_file": ".agents/scripts/commands/bento_slicer.py"
  },
  "temporal_gap_marker": null
}
```

- **5-Minute Prompt-Cache Preservation Gate**: Regenerating `context.json` with a fresh timestamp on every turn invalidates prefix KV prompt caches in LLM hosts. `pre-agent-wake.py` computes a SHA-256 `structural_hash` over `active_file`, `terminal_error`, `active_bento_task`, and `evolution_overdue`. If the previous write occurred $< 300$ seconds ago and `structural_hash` is unchanged, the hook skips rewriting `context.json` and exits in $< 5$ms.
- **Temporal Gap Marker**: When an idle gap $\ge 300$ seconds occurs, the hook emits `"temporal_gap_marker": "[IDLE GAP: Xm elapsed since last turn]"` so the agent re-verifies external state assumptions.
- **Darwinian Evolution Flag**: If `unprocessed_learnings >= 3` or open observations exceed threshold, the hook flags `"evolution_overdue": true`.

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

### 6.4. Zero-Escape Bento Task Slicer (`commands/bento_slicer.py`)
To prevent Budget and Standard models in IDE chat sessions from skipping multi-file tasks or hallucinating line offsets:
- **Topological Blast-Radius Sorting ($T_0 \to T_5$) & Bottom-Up File Ordering**: `orion.py bento init <plan.md>` parses implementation plans into atomic tasks, splits multi-pair cards into sub-tasks (`1.1a`, `1.1b`), checks `TTP-*` finding coverage, sorts tasks by architectural tier, and orders same-file edits from highest line number to lowest.
- **Live AST Anchor Recalibration & Whitespace Alignment**: Before rendering `.orion/working/ACTIVE_TASK.md`, the engine locates the exact `SEARCH` block on disk, populates `## 3. Verbatim SEARCH Block` with the exact disk window (`raw_window`), and shifts `## 4. Exact Drop-In REPLACE Block` by the exact leading whitespace delta.
- **Post-Condition Disk Mutation Gate**: `orion.py bento next --verify` inspects the target file on disk before running tests. If the `SEARCH` block is still unpatched and `REPLACE` is absent, progression is rejected with `Exit Code 2 ([BENTO NO-OP REJECTED])`. Multi-line verification commands execute sequentially.

### 6.5. Modular Gateway CLI Architecture (`commands/`)
The CLI execution layer in `.agents/scripts/commands/` is organized into 9 focused Gateway CLI engines routed through `orion.py`:
- **`commands/brain.py`**: Unified cognitive facade, Ollama hardware discovery (`NanoBrain`), rule matrix compilation, and contradiction management.
- **`commands/bento_slicer.py`**: Topological Bento task slicer, live AST anchor recalibrator, disk indentation aligner, and post-condition disk mutation gate (`bento init|next|status|reset`).
- **`commands/compact.py`**: 5-tier context compaction (`lite`, `stream`, `full`, `aggressive`, `ultra`, `pipeline`), stream elision, and Lessword protocol execution.
- **`commands/rag.py`**: Local hybrid retrieval combining SQLite FTS5 BM25, packed float32 vector embeddings, 1-hop graph neighbor expansion, and `superseded_by` filtering.
- **`commands/vault.py`**: Obsidian-compatible graph vault export and 4-note Second Brain briefing generation.
- **`commands/foundation.py`**: Interactive setup wizard, 4-pillar capability doctor, Hub-and-Spoke deployment (`deploy`, `sync-ai`, `push-upstream`), and project initialization.
- **`commands/state_machine.py`**: Formal state machine (`fsm`), Git-bound checkpoint rollback, and budget telemetry.
- **`commands/reflexion.py`**: 5-status Observation Ledger (`OBSERVATIONS.md`), Temporal Pulse consolidation, operator habit mining, and wikilink injection.
- **`commands/verify_agents.py`**: 8-gate mechanical verifier, structural ceiling gatekeeper (`core_max_lines`), preflight auditor, and delta-scoped AST mutation engine.

### 6.6. Universal Project DNA & Multi-Workspace Packer Engine (`utils/packer.py`)
To enable multi-model frontier code audits without file upload limit friction or context explosion:
- **Monorepo & Polyglot Discovery**: Recursively detects polyglot manifests across root and nested sub-containers (`apps/`, `packages/`, `services/`, `modules/`, etc.).
- **5-Tier Architectural Taxonomy**: Classifies application files into architectural strata: `contracts` (DTOs, schemas), `domain` (models, entities, usecases), `services` (clients, network, database), `state` (blocs, controllers, stores), and `presentation` (views, screens, components).
- **Dynamic Graph Topology Clustering (`graph_topology`)**: Groups codebase volume organically using PageRank architectural centrality and AST import graph cohesion, preventing arbitrary bucket collapses and sub-clustering native packages (e.g. JVM/Android namespaces).
- **Cross-Bundle Import Router**: Identifies cross-bundle dependencies across standard source roots (`src/`, `lib/`, `app/`, `packages/`) while preserving multi-segment paths (e.g. `lib/main`, `ir/types`) with $O(1)$ object-identity caching.
- **Polyglot Static Audit Radar**: Evaluates execution sinks (`eval`, `exec`, `spawn`, `execAsync`, `MethodChannel`) and broad/silent catches (`catch {}`) across 10+ languages, surfacing a pre-audit radar in Bundle 01.
- **Interactive 4-Turn Phased Audit Playbook**: Auto-generates `00_GEMINI_WEB_AUDIT_PROMPT.txt` tailored to the repository, orchestrating a 4-turn audit protocol (Architecture/Contracts → Core Services/Logic → Presentation/Bridges → Verification/Hardening) with signature preservation mandates.
- **Large Static JSON Schema Sampling (`shrink_json`)**: Compresses massive JSON catalogs (>350 lines) into representative schema samples with sample items, saving 35k–40k tokens on raw data blobs.
- **Adversarial Forensic Hardening (DEFECT-01 to DEFECT-11 & F-01 to F-08)**:
  - *Prompt-in-Data Shield*: Unconditionally escapes prompt injection tags across all lines including code fences.
  - *Safe Polyglot I/O*: Reads files via `read_text_safe()` with `utf-8-sig` and `utf-16` fallback, eliminating BOM corruption.
  - *Single Root BIOS Deduplication*: Bundles only the canonical `AGENTS.md`, dropping duplicate aliases (`GEMINI.md`) in host app packages.
  - *DSL & Precondition Filtering*: Excludes Kotlin/Java preconditions (`require`, `check`) and scope functions (`let`, `run`, `apply`) from matching as function declarations.
  - *CLI Entrypoint Preservation*: Preserves executable entrypoints in `bin/` (e.g. `bin/flutterin.mjs`).
  - *Symlink Loop Protection*: Enforces realpath containment and disables recursive symlink traversal.
- **Balanced Subtree Bin-Packing**: Uses `balance_into_k_bundles()` with an overflow penalty to partition repository volume into at most 10 balanced Markdown files (`.md`) across isolated tier subfolders (`.orion/bundles/{arch,hybrid,full}/`).
