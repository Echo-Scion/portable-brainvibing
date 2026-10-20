---
name: project-operator
description: >-
  Coordinates production deployments, release manager workflows, pre-flight readiness gates, and chaos engineering experiments. Use when preparing production releases, executing deployment pre-flight checks, managing version tags, or running chaos resilience audits.
---
# Project Operator

Your role is to manage code releases, handle technical debt, coordinate production deployment gates, and ensure deployment environments are pristine.

## 🧭 Sub-Intent Dispatch Matrix
- **Production Deployment Readiness (`/project-operator deploy`)**: JIT load .agents/skills/project-operator/references/prod-deploy.md
- **Release Management & Version Tagging (`/project-operator release`)**: JIT load .agents/skills/project-operator/references/release-manager.md
- **Chaos Resilience & Fault Injection (`/project-operator chaos`)**: JIT load .agents/skills/project-operator/references/chaos-engineer.md

## Release Checklist & Hard Deployment Gates (MANDATORY)

Before merging a major feature branch to `main` or deploying to production, you MUST execute this mechanical gate sequence. Bypassing failing checks is strictly forbidden:

```bash
# 1. Check for hardcoded API keys or secrets
python .agents/scripts/orion.py scan security .

# 2. Check for dangerous SQL commands in the latest migration
python .agents/canons/global/harnesses/migration_verifier.py --file supabase/migrations/<migration_file>

# 3. Check for Context/Token bloat
python .agents/scripts/orion.py scan tokens

# 4. Execute Full Agent & System Verification
python .agents/scripts/orion.py verify_agents
```

### Hard Gates (Non-Negotiable)
- **GATE 1 (Exit Code Mandate)**: If ANY verification script, test suite, or pre-flight check returns Exit Code > 0, the release is IMMEDIATELY ABORTED. Overriding or ignoring failing exit codes is FORBIDDEN.
- **GATE 2 (Clean Index Guarantee)**: Uncommitted git diffs, untracked temporary files, or dirty staging states block production deployment.
- **GATE 3 (Zero Secret Leakage)**: Any detected secret token, exposed private key, or unpinned environment variable immediately halts deployment pipelines.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Chaos Engineer** | .agents/skills/project-operator/references/chaos-engineer.md |
| **Release Manager** | .agents/skills/project-operator/references/release-manager.md |
| **Production Deployment Readiness** | .agents/skills/project-operator/references/prod-deploy.md |
