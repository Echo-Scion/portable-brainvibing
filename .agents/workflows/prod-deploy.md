---
description: Environment readiness checklist before pushing/deploying to Production.
---

# Deploy Production Workflow

## 0. PRE-FLIGHT (MANDATORY GATE)
Do NOT proceed to deployment steps until all these automated checks return [PASS]. Run these commands directly:

```bash
# 1. Secret Leak Check
if [ -f .agents/canons/global/harnesses/secrets_scan_verifier.py ]; then python .agents/canons/global/harnesses/secrets_scan_verifier.py --path .; else grep -rE "(sk-|BEGIN PRIVATE KEY)" --exclude-dir=".git" .; fi

# 2. Migration Safety Check (if applying DB changes)
python .agents/canons/global/harnesses/migration_verifier.py --file supabase/migrations/<latest_migration.sql>
```

## 0.5. SUPREME COURT CONSENSUS
- **MANDATORY**: Before deploying, You MUST execute `view_file .agents/skills/project-operator/SKILL).md` NOW to coordinate the deployment:
  1. `view_file .agents/skills/integrity-sentinel/SKILL).md`: Votes on Security/Race conditions.
  2. `view_file .agents/skills/project-architect/SKILL).md`: Votes on Architectural integrity.
  3. `view_file .agents/skills/cost-optimizer/SKILL).md`: Votes on Financial blast-radius.
- If ANY subagent issues a `VETO`, abort deployment immediately and fix the flagged issue.

## 1. PREPARATION COMMANDS
Execute these checks in the terminal:

- [ ] **Dependency Audit**: Execute the appropriate command for your tech stack (e.g., `npm audit`, `pip-audit`, `flutter pub outdated`).

- [ ] **Type & Lint Check**: Execute the appropriate lint command for your tech stack (e.g., `npm run lint`, `dart analyze`, `flake8`).

## 2. PRODUCTION ENVIRONMENT CONFIGURATION
- Verify `NODE_ENV=production` or `DEBUG=False` in the production `.env` (NOT local).
- Ensure CORS origins are strictly limited to your production domain (no `*`).

## 3. FINAL DEPLOYMENT
Only execute the deployment command (e.g., `npm run build`, `firebase deploy`, `vercel --prod`) IF all pre-flight commands above returned a clean exit code (0).
