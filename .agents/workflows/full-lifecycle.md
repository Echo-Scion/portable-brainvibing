---
description: Standard workflow for creating new projects or major features (Automated Lifecycle).
---

# 🚀 WORKFLOW: FULL LIFECYCLE (HIGH-DENSITY)

This workflow is the **Master Orchestrator**. It leverages the entire `.agents` ecosystem to build robust, secure, and cost-effective SaaS applications from zero.

## PHASE 0: INGESTION (THE SOUL)
> **Tier**: BUDGET — read-only context loading.
- [ ] **Global Alignment**: Read `canons/global/` and `rules/core-guardrails.md`.
- [ ] **Context Loading**: Read the current `BLUEPRINT.md` (if exists) or the project's intake brief.
- [ ] **Skill Activation**: Identify and activate the necessary specialized skills for the project domain.
- [ ] **Gate 0**: Confirm task tier and active constraints before any file write.

## PHASE 1: STRATEGIC BLUEPRINT (THE BRAIN)
> **Tier**: PREMIUM — architecture and cross-system reasoning. Sequential Thinking mandatory.
- [ ] **Viability Gate & Loop**: Invoke `@skills/saas-strategist` (`saas-viability`). Baseline the idea. If score < 13/15, run the Recursive Viability Engine (Pivot mutable features while locking Vision Invariant) until the score is optimized.
- [ ] **Architectural Design**: Invoke `@skills/project-architect` to synthesize requirements into Chapter 1-7 of the Master Blueprint based on the finalized viability pivot.
- [ ] **Cost Guard**: Invoke `@skills/cost-optimizer` to validate the chosen tech stack and infrastructure for token and cloud efficiency.
- [ ] **Security Blueprint**: Invoke `@skills/integrity-sentinel` to identify potential threat vectors (Auth, Data Leakage, RLS) before code is written.
- [ ] **Socratic Challenge**: AI must present at least TWO architectural risks or trade-offs for user confirmation.
- [ ] **Gate 1**: Do not proceed to scaffolding until the Viability Gate is passed and risks are acknowledged.

## PHASE 2: SCAFFOLDING (THE SKELETON)
> **Tier**: STANDARD — multi-file creation, template population.
- [ ] **Initialize Context**: Run `/project-init`.
- [ ] **Pillar Setup**: Ensure `00_Strategy/`, `01_Product/`, `02_Creative/`, and `03_Tech/` are established.
- [ ] **Master Files**: Populate `BLUEPRINT.md`, `ROADMAP.md`, `STYLE_GUIDE.md`, and `ARCHITECTURE.md` using slot-fill templates.
- [ ] **Gate 2**: Run `python .agents/scripts/verify_agents.py` if `.agents/` was modified during scaffolding.

## PHASE 3: EXECUTION LOOP (THE MUSCLES)
> **Tier**: STANDARD per feature. Escalate to PREMIUM if the feature touches auth, RLS, or global state.
For each feature defined in the Roadmap:
- [ ] **Feature Initiation**: Run `/app-builder`.
- [ ] **Security Implementation**: Invoke `@skills/integrity-sentinel` during API and Database design (Phase B of app-builder).
- [ ] **Evaluation Loop**: Invoke `@skills/integrity-sentinel` to verify that the implementation meets the original prompt requirements without regression.
- [ ] **Gate 3**: Per feature, include one Breaker evidence block (see `reasoning-standards.md`).

## PHASE 4: CERTIFICATION (THE SEAL)
> **Tier**: PREMIUM — exhaustive certification, adversarial testing, final audit.
- [ ] **Quality Assurance**: Invoke `@skills/integrity-sentinel` to perform exhaustive TDD, Widget Testing, and Edge Case verification.
- [ ] **System Audit**: Invoke `@skills/integrity-sentinel` for a final structural and logic certification.
- [ ] **Zero N/A Compliance**: Ensure all context files touched during execution are fully populated and relevant.
- [ ] **Gate 4**: If any certification check fails, status must be `PARTIAL` and release is blocked.

## PHASE 5: MAINTENANCE & SYNC (THE HEALTH)
> **Tier**: BUDGET — deterministic script execution, no reasoning required.
> **Turbo Mode (Exclusive Exemption)**: Scripts in this phase are pre-authorized. They do NOT require `[DO: YES]` confirmation — they touch no source code. This is the ONLY exemption from the Universal Pre-Flight rule.
- [ ] **Semantic Sync**: 
// turbo
Run `@index-project` to update semantic indexing.
- [ ] **Gate 5**: 
// turbo
Re-run `python .agents/scripts/verify_agents.py` and require PASS before closing lifecycle.

---
*Portable Brainvibing Infrastructure - Orchestrated Lifecycle Protocol*