---
name: [[knowledge]])-sync.md
description: "Internal workflow to synchronize all foundation [[knowledge]]) files, bump version, and push to origin at the end of a session."
---

# Knowledge & Foundation Sync Workflow

**Purpose**: A dedicated internal checklist to ensure that all master [[knowledge]]) files in the `_foundation` repository are updated, versioned, and pushed to origin after any structural or functional changes. 

> [!WARNING]
> **Version Cap**: Do NOT exceed version `1.0.0` unless explicitly authorized by the Human. All bumps should remain in the `0.x.x` range for beta/internal development.

## 1. Context Assessment
- [ ] Review `.orion/episodic/` handoff files or `git diff` to understand what was changed in the current session.
- [ ] Identify if the change is a **Patch** (bug fixes), **Minor** (new internal features/canons), or **Major** (breaking architectural shifts).

## 2. Version Bump
- [ ] Read the current version from `VERSION`.
- [ ] Calculate the new version according to SemVer (e.g., `0.4.1` -> `0.4.2`).
- [ ] Overwrite `VERSION` with the new version string.
- [ ] **MANDATORY**: You MUST mechanically update the `version:` metadata inside `.agents/rules/core-guardrails.md` and `GEMINI.md` to prevent Version Drift.

## 3. Knowledge Base Hydration
Review and update the following files **only if** the recent changes affect their domain:
- [ ] `CHANGELOG.md`: Add a new version block at the top with date and bullet points of changes.
- [ ] `EXPLAIN.md` / `README.md`: Update if core architecture or user-facing instructions changed.
- [ ] `GEMINI.md`: Update if AI Master BIOS constraints or JIT triggers changed.
- [ ] `PREREQUISITES.md`: Update if new dependencies (e.g., Genkit, Python libraries) were added.
- [ ] `.gitignore` / `CODEOWNERS` / `LICENSE`: Verify if new exclusions or ownership rules apply.
- [ ] `.orion/episodic/handoff_*.md`: Flush short-term episodic memory into handoff state, and archive stale handoffs.

## 4. Ecosystem & Orion Sync
- [ ] If `.agents/` rules or schemas were modified, execute `python .agents/scripts/orion.py verify_agents` to ensure mechanical integrity.
- [ ] Hydrate the internal [[knowledge]]) graph: `python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows`

## 5. Commit & Push
- [ ] Stage all changes: `git add .`
- [ ] Commit with semantic version tag: `git commit -m "chore(docs): sync knowledge.md) base for v<NEW_VERSION>"`
- [ ] Push to remote: `git push origin`

---
🚦 **END OF WORKFLOW**: Reply with the standard checkpoint format confirming the version bump and successful push.
