# The AI Brain: Understanding the `.agents` Ecosystem

Welcome to the layman's guide for the **Portable Brainvibing Infrastructure** (v0.0.1). 

If you are a project manager, a beginner developer, or simply someone trying to understand how this system works, this guide is for you. We will avoid complex jargon and explain how all these folders and files connect together to form a structured workflow.

---

## 1. The Core Problem: AI "Attention Decay"

Imagine you hire a lightning-fast assistant named AI. On the first day, you hand them a 100-page rulebook and say, "Build an app, and follow every rule in this book."

For the first few hours, the assistant is flawless. But after reading thousands of lines of code, the assistant starts losing track. They forget the rules from page 1, begin guessing how things should be done, and make security mistakes. 

In the AI world, this is called **Attention Decay** (or Context Degradation). AI lacks "willpower" and "discipline". If you leave an AI alone in a massive project, its output quality will eventually drop.

**The Solution?** We stop relying solely on text prompts. Instead, we build an automated **Factory Conveyor Belt**. We force the AI onto a track using Python validation scripts and strict checklists.

---

## 2. Anatomy of the Brain (How It All Connects)

The `.agents` directory is not just a folder of text prompts. Every folder acts as an interdependent component.

Here is how the components are connected:

### 🚪 1. The Front Door (Master BIOS: `GEMINI.md` / `CLAUDE.md`)
When you send a message, the AI is forced to read the Master BIOS file sitting at the root of your project first. This file acts as the ultimate bouncer. It intercepts your prompt and commands the AI: *"Before you answer this user, you MUST run our Python scripts to fetch the rules."*

### 📡 2. The Telepathic Bridge (`orion_mcp.py`)
Modern AI IDEs (like Cursor, Antigravity, or Claude Desktop) don't need to type commands blindly into a terminal anymore. They use the **Model Context Protocol (MCP)**. The `orion_mcp.py` server acts as a telepathic adapter, exposing all 14 internal tools natively to the AI as JSON interfaces. This eliminates fragile CLI parsing.

### 🧠 3. The Memory Lobe (`.orion/` & LightRAG)
Feeding the AI everything at once causes Attention Decay. 
The `.orion` folder is the brain's long-term memory vault. It uses **SQLite FTS5**. To prevent the database from bloating, it uses a **Universal AST Ingestion** engine that compresses source code into lightweight structural blueprints before saving them. This creates a fast local filing cabinet storing the context of your app, the architecture blueprints, and the history of recent tasks.

### ⚡ 4. The Central Nervous System (`scripts/`)
These are automatic Python scripts running in the background. The AI doesn't just read text; it triggers these scripts via a unified CLI (`orion.py`) or MCP to do the heavy lifting.
- When the AI needs a memory from `.orion`, it runs **`orion.py brain sync`**. This script searches the `.orion` vault and hands the exact memory to the AI.
- When the AI goes to sleep (ends the session), it runs **`orion.py nano`**. This script uses a tiny, local AI model (Ollama) to compress the day's work into short memories inside `.orion.db`.

### ⚖️ 5. The Rules Library (`rules/`)
Once the AI has its memory, it must check the laws. The `rules/` folder contains absolute constraints.
- **`core-guardrails.md`**: Enforces evidence contracts and formatting mandates.
- **`security-guardrails.md`**: Warns the AI to avoid leaving API passwords in the code.
- **`tier-execution-protocol.md`**: Forces the AI to categorize your task as BUDGET or PREMIUM before it consumes tokens.

### 🎭 6. The Persona Hats (`skills/`)
The AI cannot be an expert at everything simultaneously. The `skills/` folder contains specific uniforms.
- If you ask the AI to design a database, it puts on the **`project-architect`** hat.
- If you ask it to style a button, it puts on the **`ui-finish`** hat.
- Each hat limits what the AI focuses on, ensuring clarity.

### 🛤️ 7. The Conveyor Belts (`workflows/`)
Once the AI has its Memory, its Rules, and its Hat, it needs a roadmap. The `workflows/` folder contains Standard Operating Procedures (SOPs).
- **`app-lifecycle.md`**: How to build an app from scratch.
- **`session-offload.md`**: How to clean up context before concluding a session.

### 📚 8. The Machine Manuals (`canons/`)
If the AI is building a Flutter app, it needs the manual for Flutter. The `canons/` folder contains specific rules for specific frameworks, ensuring the AI doesn't accidentally use Python logic inside a Flutter app.

---

## 3. The Synapse Sequence: A Prompt's Journey

To understand their interconnectedness, let's trace a single prompt:

**Step 1: You type "Build a login page for our Flutter app."**
1. **The Interception**: The `GEMINI.md` (Master BIOS) intercepts your message instantly. It orders the AI: *"Do not write code yet. You must run the `orion.py brain sync` command."*
2. **The Omni-Buffer Sync**: Before responding, a background hook writes the exact file you are looking at and any errors on your screen into `context.json`. The AI reads this magically to gain spatial awareness without asking you to copy-paste.
3. **The Memory Retrieval**: The AI runs `python .agents/scripts/orion.py brain sync` (or calls the MCP Tool). This searches the `.orion.db` vault, pulls out previous login rules, and injects them back into the AI's short-term memory.
4. **The Persona Selection**: The AI routes itself to `skills/frontend-experience/SKILL.md` to adopt the mindset of a UI designer.
5. **The Law Check**: The AI's internal logic forces it to read `rules/core-guardrails.md` and `canons/ecosystems/flutter/flutter-ui-patterns.md`. 
6. **The Execution Belt**: The AI opens `workflows/app-lifecycle.md` and creates the login files.
7. **The Sentinel Audit**: Before finalizing, the AI puts on the `skills/integrity-sentinel` hat. It runs `python .agents/scripts/orion.py preflight`. The script scans the new code to ensure no hardcoded passwords exist.
8. **The Compression**: You say, "Good job, we're done." The AI opens `workflows/session-offload.md`. It triggers `orion.py nano` and `orion.py compress`. The local model compresses the task into a log and stores it in `.orion.db`. 

---

## 4. The Darwinian Evolution Loop (Evolution 2.0)

This system is designed to learn and mutate autonomously. Humans make mistakes and forget; AI models make mistakes and repeat them. 

To solve this, we implemented a deterministic, mechanical **Evolution Loop**:
1. **The Heartbeat Cron**: The Omni-Buffer hook continuously scans for unhandled terminal errors. If failures cross a threshold, it injects an `evolution_overdue` flag into the context, *mechanically forcing* the AI to evolve before answering the user.
2. **Friction Miner**: A pure Python script scans system memory for repeated patterns (`<friction-data>`), ensuring that if a bug happens 3 times, a new rule is synthesized.
3. **Canary Deploy & Fitness Scoring**: When a rule or skill is evolved, the system does not blindly overwrite V1. It creates a V2 fork and runs `python .agents/scripts/orion.py evolve bench` to grade the new rule against a 249-line test suite (using deterministic assertions or NanoBrain). It only promotes V2 if `fitness(V2) >= fitness(V1)`.
4. **The Evolution Ledger**: Every mutation is permanently recorded in an append-only `EVOLUTION_LOG.jsonl` (a git-blame for AI), and a unique `.genome.json` fingerprint allows intelligent auto-merging of rules across different projects.

---

## 5. The Advanced Vision (Unlimited Hardware Budget)

The `.agents` ecosystem is currently highly restricted to operate cleanly on minimal hardware (optimizing for API tokens and using 0.5B parameter background models).

However, if you possess **unlimited budget and compute** (massive local LLMs, 128GB+ RAM, multiple high-end GPUs), the ecosystem transforms:

### 1. Local Swarm Scaling
The `auto_delegate.py` script currently runs tasks sequentially. With massive compute, it could spawn 5 to 10 parallel background agents (each backed by a local 70B parameter model). You could assign an entire feature, and the swarm would develop the Database, the Backend API, and the Frontend UI simultaneously in absolute isolation.

### 2. Continuous Graph Indexing
Instead of waiting for `orion.py brain sync` to trigger manually, a heavy workstation could run a background daemon that continuously indexes every Abstract Syntax Tree (AST) node, every file change, and every terminal log into `.orion.db` in real-time, providing the AI with sub-second, perfect spatial awareness of the entire codebase.

### 3. Visual & Latency-Free Audits
With a local Vision Language Model (VLM) running entirely in VRAM, the `ui-finish` skill wouldn't just read code; it would visually render the UI, compare it to Figma designs pixel-by-pixel, and self-correct CSS padding iteratively at 100+ tokens per second.

---

## 6. Deep Dive Directory & File Map

### `rules/` (The Absolute Laws)
*   **`RULES_INDEX.md`**: The central registry of all foundational constraints.
*   **`core-guardrails.md`**: Enforces evidence contracts and memory recall protocols.
*   **`security-guardrails.md`**: Enforces strict Red Team testing.
*   **`tier-execution-protocol.md`**: Categorizes tasks into BUDGET, STANDARD, or PREMIUM.
*   **`context-standards.md`**: Enforces the 82-file naming registry.
*   **`prerequisites.md`**: The Graceful Fallback mapping for zero-crash operations.

### `scripts/` (The Automation Nervous System)
We use a **Modular CLI** architecture. `orion.py` routes commands to specific modules in `scripts/commands/`.
*   **`orion.py deploy`**: Syncs the Brain into new target apps.
*   **`orion_mcp.py`**: The 14-Tool JSON-RPC Native Server for IDE integrations.
*   **`orion.py orion_ops`**: Computes hashes, dedups memories, and handles SQLite FTS5 ingestion.
*   **`orion.py brain sync`**: Uses SQLite FTS5 to search the `.orion` vault.
*   **`orion.py swarm`**: Sleep-State Delegation Engine for executing complex bash loops.
*   **`orion.py nano`**: The local LLM memory compressor.
*   **`orion.py compress`**: Lexical Token Clipper ("Caveman compression").
*   **`orion.py preflight`**: Ecosystem Diagnostics and linting.
*   **`orion.py scan`**: Structural code maps and token consumption audits.
*   **`orion.py verify`**: The Mechanical Integrity Checker.

### `skills/` (The Specialized Personas)
*   **Architects**: `saas-strategist`, `project-architect`.
*   **Engineering**: `backend-orchestrator`, `data-logic`, `api-contract`.
*   **Frontend**: `frontend-experience`, `ui-finish`, `palette`.
*   **Operations**: `integrity-sentinel`, `project-operator`, `cost-optimizer`.
*   **Tokens**: `caveman` and `caveman-compress`.

### `workflows/` (The Standard Operating Procedures)
*   **`app-lifecycle.md`**: Project inception to final build.
*   **`audit-and-test.md`**: Strict TDD loop.
*   **`session-offload.md`**: The shutdown procedure.
*   **`self-evolve.md`**: Post-task reflection loop.

### `canons/` (Framework Specific Manuals)
*   **`ecosystems/flutter/`**: Specific rules for Flutter apps.
*   **`ecosystems/react/`**: Specific rules for React web apps.
*   **`global/harnesses/`**: Physical checks like `secrets_scan_verifier.py`.
