# Deploy Production & Environment Readiness Checklist

## 0. PRE-FLIGHT (MANDATORY GATE)
Do NOT proceed to deployment steps until all these automated checks return [PASS]. Run these commands directly:

```pwsh
# 1. Secret Leak Check
python .agents/canons/global/harnesses/secrets_scan_verifier.py --path .

# 2. Migration Safety Check (if applying DB changes)
python .agents/canons/global/harnesses/migration_verifier.py --file supabase/migrations/<latest_migration.sql>
```

## 0.5. SUPREME COURT CONSENSUS
- **MANDATORY**: Before deploying, coordinate consensus across domain specialists:
  1. `view_file .agents/skills/integrity-sentinel/SKILL.md`: Votes on Security/Race conditions.
  2. `view_file .agents/skills/project-architect/SKILL.md`: Votes on Architectural integrity.
  3. `view_file .agents/skills/cost-optimizer/SKILL.md`: Votes on Financial blast-radius.
- If ANY subagent issues a `VETO`, abort deployment immediately and fix the flagged issue.

## 1. PREPARATION COMMANDS
Execute these checks in the terminal:

- [ ] **Dependency Audit**: Execute audit command resolved from `.agents/canons/ecosystems/<stack>/ecosystem.json` (e.g., `npm audit`, `pip-audit`, `flutter pub outdated`).
- [ ] **Type & Lint Check**: Execute lint command resolved from `.agents/canons/ecosystems/<stack>/ecosystem.json` (e.g., `npm run lint`, `dart analyze`, `flake8`). Must return Exit Code 0.
- [ ] **Automated Test Suite (MANDATORY)**: Execute test suite resolved from `.agents/canons/ecosystems/<stack>/ecosystem.json` (e.g., `flutter test`, `npm test`, `pytest`). Must return Exit Code 0 with zero failures before proceeding.

## 2. PRODUCTION ENVIRONMENT CONFIGURATION
- Verify `NODE_ENV=production` or `DEBUG=False` in the production `.env` (NOT local).
- Ensure CORS origins are strictly limited to your production domain (no `*`).

## 3. FINAL DEPLOYMENT
Only execute the deployment command (e.g., `npm run build`, `firebase deploy`, `vercel --prod`) IF all pre-flight commands above returned a clean exit code (0).
