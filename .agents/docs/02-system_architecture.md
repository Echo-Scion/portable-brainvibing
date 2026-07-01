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

