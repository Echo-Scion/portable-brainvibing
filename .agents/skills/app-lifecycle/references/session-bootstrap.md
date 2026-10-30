---
name: session-bootstrap
description: Cold-start grounding, environment calibration, and previous handoff resumption workflow.
---

# 🌅 Workflow: Session Cold-Start & Bootstrap (`/cold-start`)

Follow this workflow at the start of a session, when resuming work after an interruption, or when prompted for project orientation.

## 1. Constitutional Grounding (The Immutable North Star)
Internalize the foundational invariants before inspecting or touching code:
- **Universal Agnostic**: `.agents` is 100% agnostic across platforms, repositories, and operating systems.
- **Polyglot Scope**: Works seamlessly across Flutter, React/Web, Android Studio, Python, Go, Rust, and Systems codebases.
- **Multi-OS First**: Never assume POSIX-only. Windows (PowerShell with explicit UTF-8, LF line endings, no `&&`), macOS, and Linux are equally supported.
- **4-Pillar Sovereign Architecture**:
  - Pillar 1 (Core Floor): Python 3.10+ Stdlib (100% Zero-Pip Floor Sovereignty).
  - Pillar 2 (Speed & AST): Rust companions (`rtk`, `ast-grep`, `difftastic`, `gitleaks`, `jj`).
  - Pillar 3 (Intelligence): Local AI (Ollama).
  - Pillar 4 (Web Runtime): Bun.
  - Tier 2 Accelerators: Opt-in, zero-overhead, seamless fallback.
- **Invariant Lock**: `context/VISION.md` is immutable without explicit human instruction. Anti-enterprise-bloat, YAGNI, and Evidence Mandate (Exit Code 0) strictly govern all turns.

## 2. Handoff & Technical State Resumption
Check if a previous session left a handoff note:
- Read `.orion/working/handoff.md` if present:
  - Extract `## 1. Resume Point` to identify immediate next actions.
  - Extract `## 2. Technical State` to detect active files or pending blockers.
  - Extract `## 5. Anti-Goals` to avoid known regressions.
- If `.orion/working/ACTIVE_TASK.md` exists:
  - This is the active Bento card. Execute ONLY this single task before running verification (`python .agents/scripts/orion.py bento next --verify`).

## 3. Toolchain & Environment Sanity Check
Verify the host environment and active pillars:
```bash
python .agents/scripts/orion.py doctor
```
Ensure Exit Code 0 and confirm active pillars and Tier 2 accelerators (e.g. 7/7 Active).

## 4. Git Worktree & Hazard Detection
Inspect working tree status for unstaged changes, branch state, and write hazards:
```bash
rtk git status
```
If uncommitted modifications exist, triage whether to resume them or stash/revert before starting new tasks.

## 5. Synthesize Orientation Output
Output a clean Lessword orientation summary to the user:
1. **Host & Ecosystem**: Detected OS, active shell, project archetype, and pillar readiness.
2. **Current Objective**: Active Bento task or resume point from `handoff.md`.
3. **Execution Tier Recommendation**: Advise user which model tier to use.
4. **Immediate Next Step**: Proactively recommend `/plan` or the specific action to proceed.
