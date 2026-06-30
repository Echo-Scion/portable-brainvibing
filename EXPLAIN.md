# AI Brain: Main Encyclopedia of the `.agents` & `.orion` Ecosystem
# (Portable Brainvibing Infrastructure v0.0.1)

> **This document is a Complete Encyclopedia — not a summary, not a quick guide.** Every file, every concept, every mechanism is explicitly documented along with code examples and architectural rationale. Created to be read from start to finish as an absolute reference.

---

# VOLUME I: THEORETICAL FOUNDATION — Why Does This System Exist?

---

## Chapter 1: Three Fatal Flaws of Large Language Models (LLMs)

The `.agents` system exists because LLMs — however advanced — have three structural vulnerabilities that cannot be resolved with standard prompting. This infrastructure is not just a "collection of rules"; it is a **deterministic correction engine** that transforms a probabilistic chatbot into an engineering instrument.

### 1.1. Context Degradation ("Lost in the Middle")
When LLMs are fed large contexts (>50,000 tokens), their ability to recall instructions in the middle drops drastically. This phenomenon is called "Lost in the Middle" and has been empirically proven by Liu et al. (2023).

**Real-World Scenario:**
You feed a 100-page architecture guide into the AI's context. On page 3, there is Rule #12: *"Do not use `setState`. Always use `Riverpod`."* You then ask the AI to build a Login screen. The AI writes 200+ lines of UI code, and since its attention is focused on the immediate task, the rule on page 3 "evaporates." The AI uses `setState`, immediately polluting the project's architecture. You only notice it 3 days later after 15 other screens have already been built.

**Architectural Solution: Just-In-Time (JIT) Routing**
The `.agents` framework physically prevents loading all rules at once. It uses a dynamic routing table (defined in `GEMINI.md` §4). If the user asks about a "database", only the `project-architect` and `data-logic` rules are loaded. If it's about "UI", only `ui-finish` and `palette` are loaded. This guarantees that the AI's context is always clean, focused, and populated only with relevant information.

### 1.2. IDE Fragmentation (Vendor Lock-In Vulnerability)
Each IDE (Cursor, Windsurf, Copilot, Antigravity) has different AI engines and interactive tools:
- **Cursor**: `Composer Ask`, `Agent Mode`, `Ctrl+K`.
- **Antigravity/Gemini**: `/grill-me`, `/goal`, `/schedule`.
- **Copilot**: `/fix`, `/tests`, Chat variables.
- **Windsurf**: `Cascade`, built-in flow tools.

If a rule is hardcoded as *"Use `/grill-me` when confused"*, when the project is opened in Cursor, that rule becomes a dead instruction. The AI will get confused and might throw an error.

**Solution: IDE-Agnostic Tooling Directives**
Rules are written in abstract language: *"Trigger your native interactive questionnaire tool."* The AI, self-aware of its host IDE, will translate this automatically — to `/grill-me` in Antigravity, `Composer Ask` in Cursor, etc. This is defined in `core-guardrails.md` §1.8 and guarantees full portability.

### 1.3. "Politeness Tax" (Token Inefficiency / Politeness Tax)
Standard AI responses waste many tokens on pleasantries.

| Style | Example | ~Tokens |
|:--|:--|:--|
| Standard | "I apologize for the oversight! You are absolutely right. Let's go ahead and fix the null pointer exception by adding a safety check to the Auth module." | ~35 |
| Caveman | "Auth crash. User null. Adding check." | ~7 |

A 5x difference. If the AI responds 50 times a day for a month: Standard = 35,000 tokens wasted vs Caveman = 7,000 tokens. Saved tokens = extra context space for the actual code.

**Solution: Caveman Protocol** (`skills/caveman/SKILL.md`)
A communication protocol that structurally forbids articles (a, an, the), polite openings, and long narrations. Supports 6 intensity levels: `lite`, `full`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`.

---

# VOLUME II: SYSTEM ARCHITECTURE — Complete Anatomy of `.agents`

---

## Chapter 2: Active Router — Master BIOS (`GEMINI.md`)

The `GEMINI.md` file (or `CLAUDE.md`, depending on the IDE) at the project root acts as the **Active Router** and **Master BIOS** — it is the first thing read by every AI agent when starting a session.

### 2.1. Sequential Tool Ban (Hard Gate — §1.0)
```
CRITICAL: You are FORBIDDEN from using any modifying tools (write_to_file, replace_file_content,
run_command, etc.) until you have explicitly executed a view_file on .agents/rules/core-guardrails.md.
```
This is an absolute mechanical block. The AI is required to read the "master rules" before being allowed to touch any files. Its purpose: to prevent Tunnel Vision and Agentic Amnesia at the beginning of the session.

### 2.2. Integrity Flag (§1.1)
Every implementation plan (`implementation_plan.md`) must include a direct quote from `core-guardrails.md` in its header. This proves that the AI's context is actually loaded, not hallucinated.

### 2.3. Auto-Pilot Injector (§1.5)
Before starting ANY task, the agent is required to run:
```bash
python .agents/scripts/orion.py brain sync "<your_task_keywords>"
```
This injects relevant dynamic standards into the context, ensuring the agent does not work "in the dark."

### 2.4. Darwinian Heartbeat (§1.7)
If `context.json` contains `"evolution_overdue": true`, the agent MUST run:
```bash
python .agents/scripts/orion.py evolve mine-friction
```
This forces the system to evolve from mistakes before working on new tasks.

### 2.5. JIT Knowledge Routing Table (§4)
A complete routing table mapping 20+ user prompt categories to specific target files. Example:

| If User Prompt Relates To... | Immediately Load (view_file) |
|:--|:--|
| **New Project, Init, Scaffold, Start from Scratch** | `.agents/canons/ecosystems/{{FRAMEWORK}}/{{FRAMEWORK}}-init.md` & `.agents/workflows/app-lifecycle.md` |
| **Business Strategy, Growth, Idea Viability, Planning** | `.agents/skills/saas-strategist/SKILL.md` |
| **System Architecture, Database Schema, Blueprint** | `.agents/skills/project-architect/SKILL.md` |
| **Frontend UI, Layout, Aesthetics, Animations** | `.agents/skills/ui-finish/SKILL.md` |
| **Security Audit, QA, Testing, Bugs, Validation** | `.agents/skills/integrity-sentinel/SKILL.md` |
| **Debugging, Errors, Crashes, Runtime Issues** | `.agents/skills/frontend-experience/SKILL.md` |
| **Deployment, Build, Release, CI/CD, DevOps** | `.agents/skills/project-operator/SKILL.md` |
| **Orion, Knowledge Base, Ingest, Lint, Cross-reference** | `.agents/skills/brain-graph/SKILL.md` |
| **Cost Analysis, Token Budget, LLM Costs** | `.agents/skills/cost-optimizer/SKILL.md` |
| **Session End, Handoff, Context Eviction** | `.agents/workflows/session-offload.md` |

### 2.6. Unified Response Footer (§5)
Every technical response MUST end with the navigation block:
```
🚦 CHECKPOINT: [What just happened]
📋 EVIDENCE: [Exit Code or output status]
🧠 EVALUATION: [Root cause analysis if error]
🔮 NEXT TASK: [Next step]
⚡ RECOMMENDED TIER: BUDGET|STANDARD|PREMIUM
```

---

## Chapter 3: Omni-Buffer — IDE Context Synchronization (`.orion/working/context.json`)

### 3.1. Problem Solved
The AI does not know which file the user is currently viewing. If the user says "Fix this file", the AI might edit the wrong file. This is called "spatial hallucination."

### 3.2. Working Mechanism
The hook script `hooks/pre-agent-wake.py` is called by the IDE (or background daemon) before the AI starts its turn. This script writes the IDE state to JSON:
```json
{
  "timestamp_ms": 1718104500000,
  "active_file": "src/auth/middleware.ts",
  "terminal_error": "TypeError: Cannot read properties of undefined (reading 'token')",
  "user_intent": "",
  "ide_source": "antigravity",
  "evolution_overdue": false,
  "unprocessed_learnings": 0
}
```

### 3.3. Stale Data Guard
If the `timestamp_ms` is older than 5 minutes relative to the current system time, the AI must discard that data and ask the user directly. This prevents actions based on expired context.

### 3.4. Autonomic Evolution Hook
In `pre-agent-wake.py` lines 44-70, there is automatic logic: if the number of `[Darwinian Hook]` tags in `LEARNINGS.md` is >= 3, the script will:
1. Mark `evolution_overdue = True`.
2. Automatically spawn `subprocess.Popen` running `orion.py evolve mine-friction` in the background.

Meaning: evolution does not need to wait for a manual command — it happens autonomously.

---

## Chapter 4: Terminal Filtering — RTK (Rust Token Killer)

### 4.1. The Problem
Terminal commands like `npm install` can generate 5,000+ lines of output (progress bars, download logs, info). If the AI reads all of this, its context window immediately explodes.

### 4.2. The Solution
RTK is a Rust binary that proxies terminal commands. `rtk npm install` intercepts output, removes progress bars and `INFO` logs, and only forwards `WARN` and `ERROR` logs. Savings: 60-90% of tokens.

### 4.3. Decision Tree (Mandatory — from `antigravity-rtk-rules.md`)
```
Q1. Does the command generate large text output? (git log, find, grep, docker ps)
    ├── YES → Use rtk <cmd>
    └── NO → Proceed to Q2
Q2. Is the command interactive or does it require raw JSON output?
    ├── YES → Use RAW command (without rtk)
    └── NO → Use rtk <cmd> as default
```

### 4.4. Meta Commands
```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

### 4.5. Fallback (from `prerequisites.md`)
If `rtk` is not available (`command not found`), the agent must degrade to native IDE `grep_search` or `view_file` with a narrow `StartLine`/`EndLine` range. It must not block the task.

---

# VOLUME III: LOCAL RAG BRAIN — Anatomy of `.orion/`

---

## Chapter 5: Directory Structure of `.orion/`

```
.orion/
├── _manifest.json        # Metadata of the entire index (36KB, auto-generated)
├── index.md              # Human-readable index map of all assets (135 entries)
├── log.md                # Episodic log across sessions
├── orion.db              # Main SQLite database (225KB) — the core brain
├── episodic/             # Past session summaries (episodic memory)
├── matrix/               # Compressed YAML matrix of rules
├── sources/              # 118 files (.yml/.md) — processed copies of all assets
└── working/
    └── context.json      # Omni-Buffer (real-time IDE state)
```

### 5.1. `orion.db` — Main SQLite Database
Uses the virtual table **FTS5** (Full Text Search 5) for instant lexical search:
```sql
CREATE VIRTUAL TABLE memories USING fts5(
    id UNINDEXED,
    title,
    content,
    tags
);
```
Every `.agents` file is hashed with SHA-256 before being upserted, preventing duplication. Instant search query without cloud costs:
```sql
SELECT * FROM memories WHERE memories MATCH 'auth OR jwt OR session';
```

### 5.2. `sources/` — 118 Reflection Files
When `orion_ops ingest` is run, every file in `.agents/rules/`, `.agents/skills/`, `.agents/canons/`, and `.agents/workflows/` is processed and saved to the `sources/` folder as structured `.yml` or `.md` files. This folder is the "indexed mirror" of the entire ecosystem.

### 5.3. `matrix/` — YAML Rule Matrix
The YAML version of each rule file. Generated by `compile_rules.py`. Its purpose: so that NanoBrain and Python scripts can parse rules without parsing Markdown manually.

### 5.4. `index.md` — Human Navigation Map
A 135-line file listing every asset in the ecosystem, grouped by layer:
- **Infrastructure Layer**: Canons, rules, skills, workflows.
- **Context Layer**: Business strategy, architecture, roadmap files.
- **Project Docs Layer**: `LEARNINGS.md`.
- **Raw/Source Layer**: Raw Python scripts (harness, compress, etc.).

### 5.5. `_manifest.json` — Machine Metadata
A large JSON file (36KB) storing hash metadata, last processed date, and classification type for each file. Used by `orion_ops.py` to determine if a file has changed since the last ingest.

---

## Chapter 6: Relational Triplet Graph (Preventing Compilation Bugs)

### 6.1. Core Concept
Source code is not just text; it has structural relationships between entities. The system extracts **Semantic Triplets** (Subject - Predicate - Object) from each file:
```json
{
  "subject": "UserController",
  "predicate": "depends_on",
  "object": "AuthService",
  "context": "UserController requires AuthService to validate JWT tokens on line 45."
}
```

### 6.2. Practical Impact
If the AI is asked to refactor `AuthService`, the Triplet Graph immediately issues a warning:
*"UserController depends on AuthService. You MUST update both."*
This eliminates compilation bugs due to blind refactoring.

### 6.3. Triplet Injection
The `knowledge-extraction.md` workflow instructs the AI to:
1. Read a specific source file.
2. Extract 3-5 Semantic Triplets.
3. Run `orion_ops inject_triplets` which executes SQL `INSERT` into the edge table.

---

## Chapter 7: Universal AST Parser (Code Summarizer)

### 7.1. The Problem
Feeding 2,000 lines of code into the AI's context is extremely expensive in terms of tokens. Most lines are comments, whitespace, and repetitive logic blocks that are irrelevant for architectural understanding.

### 7.2. Mechanism
The file `scripts/utils/ast_parser.py` processes the source code and generates a skeleton:

**Original Code (50 lines):**
```python
class AuthService:
    # This function logs the user in
    def login(self, user_id: str):
        print("Logging in...")
        db.connect()
        if not user:
            raise Exception("User not found")
        return True
```

**AST Footprint (2 lines):**
```python
class AuthService:
    def login(self, user_id: str) -> bool: pass
```

Reduction: **~90%** size, with perfect retention of class names, method names, and parameter types. The AI knows the architecture without reading the implementation.

---

## Chapter 8: NanoBrain Intelligence (`qwen2.5:0.5b`)

### 8.1. Description
A super-small quantized LLM model (<500MB) running locally via Ollama. Not a replacement for the large model; it is a cheap pre-processing assistant.

### 8.2. Active Mode (`brain sync`)
When the user types "fix the login", NanoBrain:
1. **Semantic Query Expansion**: Expands "login" → `["auth", "jwt", "session", "oauth"]`.
2. **FTS5 Search**: Runs a query in `orion.db` with the expanded terms. Result: ~20 documents.
3. **Dynamic Rule Filtering**: Reads 20 documents, scoring them YES/NO based on the current context. Only YES documents (~3 documents) are sent to the IDE AI.

This guarantees: the expensive AI models (Claude, Gemini) only receive laser-focused context, not 20 random documents.

### 8.3. Sleep Mode (`nano`)
When the IDE is closed:
1. NanoBrain reads the daily conversation transcript (`transcript.jsonl`).
2. Summarizes what was built that day to ~500 tokens.
3. Extracts new Triplet relations and saves them to `orion.db`.
4. The summary is stored in `episodic/` as a permanent episodic memory.

---

# VOLUME IV: RULE LIBRARY (`rules/`) — 10 Law Files

---

## Chapter 9: Complete List of Rule Files

### 9.1. `core-guardrails.md` (142 lines | 11KB)
**Supreme Law.** Contains 10 sections:
1. **Unified Response Protocol**: Mandatory footer CHECKPOINT/EVIDENCE/EVALUATION/NEXT in every response.
2. **Environment Boundary Check (§1.5)**: Forbids implementing the "82-File Mandate" in the `_foundation` repo.
3. **Native Orion Execution (§1.6)**: Requires using `orion.py`, not external binaries.
4. **Omni-Buffer Context Protocol (§1.7)**: Requires reading `context.json` at the start of the session.
5. **IDE-Agnostic Tooling (§1.8)**: Translates commands to the native tools of each IDE.
6. **Reasoning Standards (§2)**: Plan Protocol, Anti-Laziness Mandate, 5-Why Script, Evidence Mandate.
7. **Edge-Case Tax (§2)**: Mandatory Edge-Case Matrix for STANDARD/PREMIUM tasks.
8. **Circuit Breaker (§4)**: 3 consecutive failures = ABORT and ask for human help.
9. **Rule Precedence (§5)**: Priority order: Security > Core > Tier > Domain > Skills.
10. **Token Efficiency (§9)**: AST Hollowing, Sleep-State Delegation, Anti-Full-Read.

### 9.2. `security-guardrails.md` (168 lines | 9.3KB)
**Security & Offensive Audit Law. Contains:**
- **Pre-Commit Secrets Scan**: Required `grep` commands before every `git commit` to detect OpenAI keys (`sk-*`), `SUPABASE_SERVICE_ROLE_KEY`, PEM private keys.
- **Prompt Injection Defense**: Deterministic algorithm detecting and rejecting malicious instructions ("Ignore previous instructions").
- **Least Privilege**: Required justification for every permission. Default = READ-ONLY.
- **Destructive Command Gate**: `rm -rf`, `DROP TABLE`, `DELETE FROM` without WHERE require `[DO: YES]` confirmation.
- **Offensive Audit Protocol**: AI is forced to act as a "Lead Quant Security Auditor" who:
  - Runs mutation testing (intentionally introducing bugs, ensuring tests catch them).
  - Checks every `catch`/`except` — if there is a silent fail, it is immediately a CRITICAL VULNERABILITY.
  - Audits vertical slices (Route → Controller → Service → Repo), not layer-by-layer.

### 9.3. `tier-execution-protocol.md` (172 lines | 11KB)
**Resource Allocation Engine. Divides tasks into 3 tiers:**

| Tier | Capabilities | Model Profile |
|:--|:--|:--|
| **BUDGET** | Fix 1 file, indexing, batch | Flash/Haiku |
| **STANDARD** | UI, code gen, testing | Sonnet/Pro |
| **PREMIUM** | Architecture, complex debugging | Opus/Thinking |

**Bento-Box Law**: BUDGET models are forbidden from multitasking. Only 1 file per iteration.
**Auto-Abort (Downgrade Guard)**: If the active model is weaker than the target tier, the agent MUST `[ABORT: TIER MISMATCH]`.
**Token Economy**: BUDGET = max 1 file read; STANDARD = 3-5 surgical reads; PREMIUM = unlimited (justified).
**Adversarial Twin Protocol**: Write exploit script → run → log results in XML `<adversarial_attack>`.

### 9.4. `development-operations.md` (155 lines | 9.3KB)
**Development Operations. Contains 3 sub-systems:**
- **Git Workflow**: Commit conventions (`<type>(<scope>): <subject>`), branching (`feat/*`, `fix/*`), Save Point Protocol (commit after every successful sub-step).
- **AutoHarness Protocol**: AI must write automated validation scripts (Harness) for destructive operations. Types: Action-Verifier, Action-Filter, Policy. Required output: `action_id`, `is_legal`, `violated_rule`, `fix_hint`.
- **Context Management**: 3-layer context hierarchy (Global → Project → App), Skeleton-First Law (BUDGET forbidden from full-read), 82-File Mandate (only for target SaaS projects).

### 9.5. `performance-optimization.md` (94 lines | 3.6KB)
**Bolt Protocol. Before any optimization, must pass 3 gates:**
1. Measurable? → If NO, cancel.
2. Readable? → If NO, cancel.
3. Scope < 50 lines? → If NO, cancel.

**500-Line Decision Tree**: Files > 500 lines = MUST refactor.
**Keyword Surgical Loading**: Map (AST) → Search (grep) → Surgical Read (view_file with line range).

### 9.6. `web-api-standards.md` (131 lines | 3.9KB)
**Web & API Standards. Contains:**
- **CSP (Content Security Policy)**: Required meta tag or header.
- **4-State Map**: Every UI component fetching data MUST handle: Loading, Error, Empty, Success.
- **Zod Schema Mandate**: NEVER trust `req.body`. Zod validation is mandatory.
- **API Response Contract**: Standard format `{ success: true/false, data/error: {...} }`.
- **Idempotency Pattern**: Critical operations require `Idempotency-Key` header.

### 9.7. `context-standards.md` (19 lines | 1.2KB)
Context boundary enforcement. Forbids implementing the "82-File Mandate" in the `_foundation` repo. Forces **AST Hollowing** (forbidding `view_file` on files > 100 lines without `rtk read`).

### 9.8. `prerequisites.md` (34 lines | 2.3KB)
**Graceful Fallback Matrix. Defines 4 prerequisites and their fallbacks:**

| Prerequisite | Fallback |
|:--|:--|
| RTK (Rust) | `grep_search` or `view_file` with line range |
| Orion (Python) | Manual `grep_search` on `.orion/` |
| QMD/Ollama | Manual `grep_search` and traversal |
| Subagent Orchestration | Handle in main thread with aggressive `grep_search` |

### 9.9. `antigravity-rtk-rules.md` (54 lines | 1.6KB)
Specific rules for RTK integration in the Antigravity IDE. Decision tree and command examples.

### 9.10. `RULES_INDEX.md` (1.4KB)
Compiled index of all rules. Parsed by NanoBrain for fast filtering during JIT routing.

### 9.11. `rules/local/` (Sub-directory)
Place for project-specific rules that override global rules. Empty in `_foundation`.

---

# VOLUME V: SKILL / PERSONA (`skills/`) — 16 Specializations

---

## Chapter 10: Skill Concept
Each skill is a "hat" worn by the AI. When loaded, the skill limits the AI's focus to a specific domain and enforces a specific mindset. Each skill folder contains `SKILL.md` (mandatory instructions) and optionally `references/` (in-depth supporting documents).

### 10.1. `ai-engineer`
**Domain:** Mitigating the probabilistic nature of LLMs.
**Content:** Assertion matrix, Confidence Gates, anti-hallucination. Used when the agent modifies the `.agents` folder itself.

### 10.2. `api-contract`
**Domain:** Client/server interface contracts.
**Content:** OpenAPI specifications, Zod validation, API safety patterns.
**Reference:** `references/api_safety_patterns.md`.

### 10.3. `brain-graph`
**Domain:** Operating `orion.db` and local RAG.
**Content:** FTS5 querying, triplet injection, SQLite maintenance.

### 10.4. `caveman`
**Domain:** Ultra-terse communication compression.
**Content:** 6 intensity levels. Supports `wenyan` (classical Chinese variant).

### 10.5. `caveman-compress`
**Domain:** `.md` file compression.
**Content:** Reads markdown files and replaces them with terse versions via regex. Saves a `.original.md` backup.
**Supporting scripts:** `scripts/__init__.py`, `scripts/compress.py`, `scripts/detect.py`, `scripts/validate.py`, `scripts/benchmark.py`, `scripts/cli.py`.

### 10.6. `cost-optimizer`
**Domain:** Token and cloud budget management.
**Content:** Routing cheap models (Haiku) for simple tasks, expensive models (Opus) for complex tasks.

### 10.7. `data-logic`
**Domain:** Data immutability.
**Content:** Forbids global state, Redux/Zustand patterns, pure functions, DTOs must not be mutated.

### 10.8. `frontend-experience`
**Domain:** UI/UX debugging.
**Content:** Fixing excessive re-renders, DOM infinite loops, React/Flutter state synchronization.
**Reference:** `references/ux-designer.md`.

### 10.9. `integrity-sentinel`
**Domain:** Red Team & Automated QA.
**Content:** Architecture audit, bloat audit, duplicate audit, fail-fast audit, logic audit, performance audit, retry audit, load testing.
**References:** 11 sub-documents: `architecture-audit.md`, `bloat-audit.md`, `duplicate-audit.md`, `fail-fast-audit.md`, `flutter_testing_patterns.md`, `load_testing_tactics.md`, `logic-audit.md`, `master-audit.md`, `performance-audit.md`, `plan-checklist.md`, `retry-audit.md`, `telemetry-gate.md`.

### 10.10. `meta-agent-admin`
**Domain:** Architect of the `.agents` system itself.
**Content:** Ecosystem evolution, rule creation, routing integrity.
**References:** `agent-architect.md`, `agent-evolution.md`, `context-manager.md`, `knowledge.md`, `loop_design_patterns.md`, `system-admin.md`, `tech-writer.md`.

### 10.11. `palette`
**Domain:** Micro-aesthetics & accessibility.
**Content:** CSS tokens, smooth animations, ARIA labels, glassmorphism, color harmony, keyboard navigation.

### 10.12. `project-architect`
**Domain:** High-scale PRD & Blueprints, and Master backend architect.
**Content:** Translating user ideas into technical documents before code is written, Node.js memory leak management, connection pooling, SQL optimization, database indexing.
**References:** `architectural_standards.md`, `startup_growth.md`, `strategic_rigor.md`, `structural_pillars.md`, `backend-architect.md`, `backend-optimizer.md`, `cache-optimizer.md`, `db-expert.md`, `enterprise_patterns.md`, `node_performance_tuning.md`, `postgres_patterns.md`.

### 10.13. `project-operator`
**Domain:** DevOps & resilience.
**Content:** Dockerfiles, CI/CD pipelines, Nginx, chaos engineering.
**References:** `chaos-engineer.md`, `release-manager.md`.

### 10.14. `saas-strategist`
**Domain:** SaaS business strategy.
**Content:** Viability analysis, monetization, growth, viral content.
**References:** `saas-growth.md`, `saas-viability.md`, `technical_content.md`, `viral_growth.md`.

### 10.15. `ui-finish`
**Domain:** Premium UI final polish.
**Content:** Empty states, loading spinners, error boundaries, Liquid Glass widgets.
**Reference:** `visual_engineering.md`.

---

# VOLUME VI: WORKFLOW / SOP — 10 Standard Operating Procedures

---

## Chapter 11: Complete List of Workflows

### 11.1. `app-lifecycle.md` (11.9KB)
**Mega E2E workflow.** 10 steps:
1. Requirements Intake (Interview).
2. Blueprint Generation.
3. Scaffold Database.
4. API Layer.
5. UI Layer.
6. Integration.
7. Testing.
8. Polish.
9. Pre-Deploy.
10. Launch.

### 11.2. `audit-and-test.md` (6.8KB)
**Strict TDD Loop** (Red → Green → Refactor) + PR Code Review Checklist.

### 11.3. `auto-context.md` (2.4KB)
**Organic Extraction.** If the user repeatedly corrects the AI ("No, I meant X"), the system automatically extracts rule X, formalizes it, and saves it to `orion.db`.

### 11.4. `knowledge-extraction.md` (2KB)
Instructs the AI to read code files, extract 3-5 Semantic Triplets, and run `orion_ops inject_triplets`.

### 11.5. `knowledge-sync.md` (2.5KB)
Internal DevOps: version bumping, integrity verification, Git commits.

### 11.6. `orion-ops.md` (1.8KB)
SOP for rebuilding the FTS5 database, querying the graph, and repairing corrupt SQLite state.

### 11.7. `prod-deploy.md` (1.7KB)
Pre-production checklist: environment variables, minification, security headers.

### 11.8. `project-migrate.md` (3.9KB)
Guide to migrating legacy/brownfield projects to the `.agents` architecture without breaking running systems.

### 11.9. `self-evolve.md` (3.5KB)
**Deterministic Reflection Loop.** 4 phases:
1. **Error Extraction**: Extract error traces to XML.
2. **Memory Write**: Write to `LEARNINGS.md`.
3. **Darwinian A/B Evolution**: Fork rules → Benchmark V1 vs V2 → Promote winner.
4. **Pattern Recognition**: Scan `LEARNINGS.md` for recurring patterns → Synthesize new rules/skills/workflows.

### 11.10. `session-offload.md` (4.7KB)
**Shutdown Sequence.** 5 steps:
1. **Scratchpad Eviction**: Clean temporary files.
2. **Gated Auto-Commit**: Logic Gate → Security Gate → History Gate before committing.
3. **Memory Compression**: `compress_memory` + `nano_compressor` to shrink logs.
4. **Handoff State**: Write `handoff.md` with Resume Point, Technical State, Anti-Goals.
5. **RTK Metrics**: Report token savings for this session.

---

# VOLUME VII: PYTHON SCRIPTS (`scripts/`) — Execution Engine

---

## Chapter 12: Script Architecture

### 12.1. Entry Point: `orion.py` (4.2KB)
The only script called directly. All commands are routed through this modular CLI.

### 12.2. Complete Command Table

| Command | Target Script | Function |
|:--|:--|:--|
| `verify` | `commands/verify_agents.py` (23KB) | Markdown compiler — scans all links, ensures no phantom references |
| `context-lint` | `commands/context_naming_lint.py` (5.6KB) | Validates context file naming against the 82-file registry |
| `deploy` | `commands/foundation.py` (29KB) | Deploys/syncs Foundation to a new project via symlinks |
| `push-upstream` | `commands/foundation.py` | Syncs project evolutions back to master Foundation |
| `budget` | `commands/track_budget.py` (2.3KB) | Tracks budgets and tier telemetry |
| `scan tokens` | `core/scanner.py` (10KB) | Ghost Token Auditor — detects memory bloat |
| `scan map` | `core/scanner.py` | Structural Code Mapper — creates lightweight skeletons |
| `scan targets` | `core/scanner.py` | Identifies targets for Offensive Audit |
| `preflight` | `commands/preflight_check.py` (6.7KB) | Pre-flight diagnostics (Self-Healing Routing) |
| `compress` | `commands/compress_memory.py` (6.3KB) | Compresses episodic memory to Caveman format |
| `orion_ops init` | `commands/orion_ops.py` (35KB) | Initializes the `.orion/` infrastructure |
| `orion_ops ingest` | `commands/orion_ops.py` | Ingests rules and configurations into the graph |
| `linkify` | `commands/linkify.py` | Auto-injects Absolute Native Markdown Links into context files |
| `amnesia` | `commands/rule_eviction.py` (2.2KB) | Rule eviction mechanism (garbage collection) |
| `swarm` | `commands/auto_delegate.py` (4.6KB) | Multi-Thread Micro-Fix (parallel) |
| `rtk` | `core/rtk_proxy.py` (1.7KB) | RTK Proxy |
| `evolve bench` | `commands/evolve.py` (9.6KB) | Benchmarks rule mutations A/B |
| `evolve mine-friction` | `commands/evolve.py` | Mines friction patterns from learnings |

### 12.3. Supporting Utilities

| File | Function |
|:--|:--|
| `utils/ast_parser.py` (4.4KB) | Universal AST Parser — extracts code skeletons |
| `utils/evolution_ledger.py` (2.3KB) | Writes to `EVOLUTION_LOG.jsonl` |
| `commands/brain.py` (19.5KB) | RAG Engine: query expansion, FTS5 search, Ollama filtering |
| `commands/compile_rules.py` (2.8KB) | Compiles Markdown rules → YAML for `matrix/` |
| `commands/nano_compressor.py` (2.8KB) | Ollama connection for NanoBrain compression |
| `commands/scaffold_saas.py` (3.6KB) | SaaS project scaffold generator |

---

# VOLUME VIII: CANONS, TEMPLATES, HOOKS, EVALS, AND ARCHIVES

---

## Chapter 13: Ecosystem Canons (`canons/`)

### 13.1. 4-Layer Structure
```
canons/
├── ecosystems/         # Framework-specific
│   ├── flutter/        # 16 canon files (init, debug, release, state-map, ui-patterns, tests, etc.)
│   ├── react/          # 2 canon files (init, standards)
│   └── python/         # 2 canon files (init, standards)
├── global/             # Cross-framework
│   ├── core-architecture.md  # Constitution of all projects
│   ├── ai_brands.json        # Registry of supported IDEs
│   └── harnesses/            # Reusable verification scripts (action verifier, migration verifier, secrets scan)
├── local/              # Project-specific (empty in _foundation)
└── micro/              # Cheat-sheets for BUDGET models
    ├── pubspec.md      # Summary of Flutter pubspec.yaml
    └── supabase.md     # Summary of Supabase patterns
```

### 13.2. `global/core-architecture.md` — 6 Core Principles
1. **Agent-First Design**: Code must be easy for AI to parse.
2. **Predictable Modularity**: Isolated modules > monoliths.
3. **Distributed Context**: Context at root AND app-level.
4. **Code-As-Harness**: Offload validations to verifier scripts.
5. **Unidirectional Data Flow**: Immutable state, mutations via actions/events.
6. **Strict Verification**: No features completed without mechanical verification.

## Chapter 14: Templates (`templates/`)

### 14.1. 11 Template Files

| Template | Target | Purpose |
|:--|:--|:--|
| `AGENTS.template.md` (12KB) | Root project (`GEMINI.md`/`CLAUDE.md`) | Multi-AI instruction generator (DRY source) |
| `PROJECT_SCAFFOLD.template.md` (10KB) | Architecture & Blueprint | Master prompt for scaffolding new projects + 82-file mapping |
| `MEMORY.template.md` (3.6KB) | State tracking | SaaS state tracking & session handoff |
| `TASK_PLANNING.template.md` (3.9KB) | Checklists | Execution, roadmap, atomic tasks |
| `STYLE_GUIDE.template.md` | UI/UX tokens | Visual style guide |
| `ORION_SCHEMA.template.md` (1KB) | `.orion/` configuration | Graph schema |
| `custom-agent.template.md` (5.4KB) | New agent | Scaffold for custom AI agent |
| `custom-rule.template.md` (3.4KB) | New rule | Scaffold for behavioral rule |
| `github-native-structure.md` (4.6KB) | GitHub | Canonical GitHub folder structure guide |
| `startup_knowledge_base.md` (2.3KB) | Knowledge | Auto-populating instructions for SaaS domains |

## Chapter 15: Hooks (`hooks/`)

### 15.1. `pre-agent-wake.py` (91 lines | 4KB)
**Omni-Buffer Hook.** Called by IDE before AI starts its turn. Functions:
1. Receives arguments `--active-file`, `--terminal-error`, `--ide-source`, `--user-intent`.
2. Writes state to `context.json` atomically (temp file → `os.replace`).
3. Checks `LEARNINGS.md` for `[Darwinian Hook]` tags. If >= 3, sets `evolution_overdue = True`.
4. Automatically spawns `orion.py evolve mine-friction` in the background.

## Chapter 16: Evaluators (`evals/`)

### 16.1. `audit_aesthetics.py` (89 lines | 4.3KB)
**CI/CD Gatekeeper for Aesthetics.** Scans `.dart`, `.tsx`, `.jsx`, `.css` files:
- **Check 1**: Detects generic colors (`Colors.red`, `Colors.blue`). Error: must use design tokens.
- **Check 2**: Detects inline style with generic colors. Error.
- **Check 3**: If > 5 raw hex codes, warning: extract to semantic tokens.
- **Check 4**: If file is a UI component but NO animation primitives are used (`AnimatedContainer`, `framer-motion`, `transition-all`), warning: add micro-interactions.

Exit Code 1 = fail → agent is forbidden from proceeding without fixes.

### 16.2. `evals.json` (9.9KB)
Benchmark/evaluation configuration for testing AI models.

## Chapter 17: Documentation (`docs/`)

### 17.1. `versioning-changelog-guide.md` (280 lines | 6.8KB)
Automated versioning pipeline: Semantic Versioning (`MAJOR.MINOR.PATCH`), automatic CHANGELOG, sanitizing sensitive files before distribution, blacklisting files that must not be synced.

### 17.2. `workflows_guide.md` (1.2KB)
Brief guide on how to use workflows.

### 17.3. `MULTI_AI_DEPLOYMENT.md` (181 bytes)
Notes on deploying to multiple IDEs simultaneously.

## Chapter 18: Metrics (`metrics/`)
Contains `README.md` and `eval_workspace/` — workspace to run model performance evaluations.

## Chapter 19: Archive (`archive/`)
Contains `README.md` and `orion_mcp.py` (10.3KB) — MCP server implementation for Orion (legacy/experimental).

## Chapter 20: Root `.agents` Files

### 20.1. `AGENTS_INDEX.md` (4.7KB)
Master map listing all Rules, Skills, Workflows, and Canons with relative paths.

### 20.2. `DEPLOY_ME.md` (4.3KB)
Plug-and-play instructions to deploy Foundation to a new project. Covers:
- Mandatory Q&A (framework, language).
- Gitignore pre-flight.
- Execution command: `python .agents/scripts/orion.py foundation deploy --target ... --framework ... --language ...`
- Safe Auto-Ingest (strictly forbidden to ingest the root directory).

### 20.3. `LEARNINGS.md` (3.7KB)
**Collective memory.** YAML format per entry: `date`, `task_id`, `tier`, `severity`, `issue`, `root_cause`, `solution`, `debt_warning`. Contains real post-mortems (VRAM OOM, workflow violations, smart ingest architecture).

### 20.4. `EVOLUTION_LOG.jsonl`
Append-only genomic ledger. Each mutation, bug fix, and extracted pattern is written as a JSON line:
```json
{
  "timestamp": "2026-06-12T14:30:00Z",
  "mutation": "Banned usage of generic 'any' type in TS DTOs.",
  "friction_source": "Runtime crash on malformed JSON payload.",
  "fitness_delta": "+15%",
  "genome_hash": "a1b2c3d4e5"
}
```

### 20.5. `.genome.json` (139 bytes)
Genomic fingerprint that can be imported to a new project so the AI immediately inherits past lessons.

### 20.6. `.project_manifest.json` (70 bytes)
Project metadata: framework, language, project name.

### 20.7. `.deployed_ais` (414 bytes)
Registry of IDEs that have received Foundation deployment.

### 20.8. `.foundation_path` (47 bytes)
Absolute path to the `_foundation` repo. Used by deployment scripts.

---

# VOLUME IX: DARWINIAN EVOLUTION LIFECYCLE

---

## Chapter 21: Friction Mining

### 21.1. Mechanism
1. AI makes an error → terminal returns Exit Code > 0.
2. Error is written to `LEARNINGS.md` with `[Darwinian Hook]` tag.
3. `pre-agent-wake.py` counts tags. If >= 3: `evolution_overdue = True`.
4. In the next turn, BIOS (`GEMINI.md` §1.7) forces the agent to run `evolve mine-friction`.
5. The agent analyzes error patterns, writes post-mortems, and proposes preventive rules.

### 21.2. Canary Deployment & Fitness Scoring
New rules are not applied immediately. Through `orion.py evolve bench`:
1. **Fork**: `cp SKILL.md SKILL-v2.md`
2. **Benchmark V1**: Test AI with old rules on a dummy task.
3. **Benchmark V2**: Test AI with new rules on the same task.
4. **Fitness Score**: Compare — tokens used, speed, Exit Code.
5. **Promotion**: If `score(V2) >= score(V1)`, merge. If fails, archive (do not delete).

### 21.3. Genomic Ledger
`EVOLUTION_LOG.jsonl` records every mutation permanently. When Foundation is deployed to a new project, this ledger is imported → the AI in the new project immediately inherits all lessons.

---

# VOLUME X: DEPLOYMENT FLOW TO NEW PROJECTS

---

## Chapter 22: Complete Deployment Procedure

### 22.1. Step 1: Identify Target & Stack
The AI must ask for framework (`react`, `flutter`, `nextjs`, `python`) and language (`typescript`, `dart`, `python`) if `.project_manifest.json` does not exist yet.

### 22.2. Step 2: Gitignore Pre-Flight
The AI must ensure `.gitignore` exists and includes `node_modules`, `build`, `.env*`, etc. This prevents RAG ingest from indexing binary garbage.

### 22.3. Step 3: Execution
```bash
# Deploy to a single IDE (Gemini default)
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework flutter --language dart

# Deploy to multiple IDEs
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai cursor,copilot

# Deploy to all 6 IDEs
python .agents/scripts/orion.py foundation deploy --target /path/to/project --framework react --language typescript --ai all
```

### 22.4. Step 4: Safe Auto-Ingest
```bash
python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/
```
**STRICTLY FORBIDDEN**: `ingest .` or ingest without arguments. This can freeze the system or corrupt the SQLite database.

### 22.5. Step 5: Periodic Sync
```bash
# Sync after Foundation is updated
python .agents/scripts/orion.py foundation sync-ai --target /path/to/project

# Push project improvements back to master Foundation
python .agents/scripts/orion.py foundation push-upstream --source /path/to/project
```

---

# VOLUME XI: COMPLETE GLOSSARY

---

| Term | Definition |
|:--|:--|
| **Agentic Amnesia** | Phenomenon where AI forgets instructions due to excessively large contexts or restarts |
| **AST Hollowing** | Technique of reading only the skeleton of source code, removing detailed implementation |
| **AutoHarness** | Pattern where the AI writes automatic validation scripts to verify its own actions |
| **Bento-Box Law** | Rule stating BUDGET models may only work on 1 file per iteration |
| **Canary Deployment** | Testing new rules in a sandbox before deploying them to production |
| **Caveman Protocol** | Ultra-terse communication mode removing articles and pleasantries |
| **Context Poisoning** | Degradation of AI capabilities due to overly large/irrelevant contexts |
| **Darwinian Heartbeat** | Automatic cron mechanism triggering evolution when errors accumulate |
| **Fitness Score** | Benchmark metric comparing the efficiency of rule V1 vs V2 |
| **FTS5** | Full Text Search 5 — SQLite extension for fast text search |
| **Friction Mining** | Automatic process of extracting error patterns from logs to generate preventive rules |
| **Genome Ledger** | `EVOLUTION_LOG.jsonl` — append-only record of every system mutation |
| **Ghost Token** | File or reference existing in the index but not physically present |
| **Hard Gate** | Mechanical block that cannot be bypassed by the AI (e.g., Sequential Tool Ban) |
| **JIT Routing** | Loading rules/skills dynamically based on prompt keywords |
| **Lost in the Middle** | Phenomenon of AI attention degrading on content in the middle of context |
| **NanoBrain** | Super-small local LLM (qwen2.5:0.5b) for pre-processing and compression |
| **Omni-Buffer** | `context.json` — real-time IDE state synchronization file |
| **RTK** | Rust Token Killer — terminal proxy saving 60-90% of tokens |
| **Skeleton-First Law** | Rule forbidding BUDGET models from reading full files >200 lines |
| **Stale Data Guard** | Mechanism discarding `context.json` data if older than 5 minutes |
| **Semantic Triplet** | `Subject-Predicate-Object` relations extracted from source code |
| **Tier Mismatch** | Condition where the active model is weaker than the tier required for the task |
| **82-File Mandate** | Context naming policy based on 82 standard SaaS file domains |

