---
description: Environment readiness checklist before pushing/deploying to Production.
---

# Deploy Production Workflow

## 0. CONTEXT RETRIEVAL (JIT)
- [ ] Verify protocol compliance and wait for binary confirmations. IF unsure, load `rules/core-guardrails.md`.
- [ ] Activate the `@skills/project-operator` skill for specific CD loops and production readiness checks.
- [ ] **Pre-Deploy Guardrails**: Load `rules/security-guardrails.md` and `rules/git-workflow.md`. Do not deploy if any critical violations exist.


## Steps

- [ ] **1. Environment Variables**: DISABLE `DEBUG` mode (set `NODE_ENV=production` or `DEBUG=False`).
- [ ] **2. Dependency Audit**: Run `npm audit` or equivalent to ensure no CRITICAL vulnerabilities in the lockfile.
- [ ] **3. Database Pre-flight**: Ensure Database schema (migrations via Supabase) is fully executed using `@skills/backend-orchestrator`.
- [ ] **4. Metrics & Logging**: Ensure Application Metrics, Sentry, or Request logging is active in the configuration.
- [ ] **5. Health Checks**: Hit `/health/detailed` to verify connectivity to DB/Cache.

Only proceed with public deployment if all five stages pass.