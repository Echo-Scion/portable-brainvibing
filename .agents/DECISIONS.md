# 🏛️ Architectural Decision Records (.agents/DECISIONS.md)

> Canonical living ledger of design trade-offs and plan resolutions across .agents.
> Maintained automatically via `python .agents/scripts/orion.py decisions`.

| ID | Plan | Topic | Chosen Resolution | Status | Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEC-20261103-01` | `seamless_jit_routing_plan.md` | How should we handle `ai_llm_attacks.md` and `skill_inspe... | `**(Recommended) Option A — Cross-Link + Direct 1-Hop Rout...` | `RESOLVED_RECOMMENDED` | 2026-11-03 |
| `DEC-20261103-02` | `zero_trust_guard_plan.md` | How do you override a false positive (e.g., a legit packa... | `**(Recommended)** Install it yourself in your own termina...` | `RESOLVED_RECOMMENDED` | 2026-11-03 |
| `DEC-20261104-01` | `plan_deferred_design_and_deploy_intake.md` | Default Archetype for Unattended Greenfield | `(Recommended) Option A: Context-aware stack default (mode...` | `RESOLVED_RECOMMENDED` | 2026-11-04 |
| `DEC-20261104-02` | `plan_deferred_design_and_deploy_intake.md` | README.md Overwrite Policy | `(Recommended) Option A: Non-destructive policy (never ove...` | `RESOLVED_RECOMMENDED` | 2026-11-04 |
| `DEC-20261105-01` | `implementation_plan.md` | Dual-Loop Git Strategy & Pragmatic .scratch Policy | `(Recommended) Inner Loop Micro-commits + Outer Loop Trunk Discipline; Native IDE edit first with .scratch as power tool/fallback` | `RESOLVED_RECOMMENDED` | 2026-11-05 |
