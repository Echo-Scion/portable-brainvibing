---
description: Environment readiness checklist before pushing/deploying to Production.
---

# Deploy Production Workflow

## 0. PRE-FLIGHT (MANDATORY GATE)
Do NOT proceed to deployment steps until all these automated checks return [PASS]. Run these commands directly:

```bash
# 1. Secret Leak Check
python .agents/canons/global/harnesses/secrets_scan_verifier.py --path .

# 2. Migration Safety Check (if applying DB changes)
python .agents/canons/global/harnesses/migration_verifier.py --file supabase/migrations/<latest_migration.sql>
```

## 1. PREPARATION COMMANDS
Execute these checks in the terminal:

- [ ] **Dependency Audit**:
```bash
# Node
npm audit --audit-level=critical
# OR Dart/Flutter
dart pub outdated --dependency-overrides
```

- [ ] **Type & Lint Check**:
```bash
# Node/TS
npx tsc --noEmit && npm run lint
# OR Dart/Flutter
dart analyze --fatal-warnings
```

## 2. PRODUCTION ENVIRONMENT CONFIGURATION
- Verify `NODE_ENV=production` or `DEBUG=False` in the production `.env` (NOT local).
- Ensure CORS origins are strictly limited to your production domain (no `*`).

## 3. FINAL DEPLOYMENT
Only execute the deployment command (e.g., `npm run build`, `firebase deploy`, `vercel --prod`) IF all pre-flight commands above returned a clean exit code (0).