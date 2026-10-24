# VOLUME VI: PROCEDURAL PLAYBOOKS & SOPS — Operational Procedures

---

## Chapter 13: Modular Standard Operating Procedures (SOPs)

In the `.agents` ecosystem, procedural workflows are organized according to the **Full Lifecycle State Machine Pipeline**. Rather than drifting as loose, unmaintained scripts, every SOP is bound directly to a parent Skill or Tier-3 Reference, maintaining a strict context boundary (< 7KB per procedure).

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Full Lifecycle Pipeline (Phases 0-6)                 │
├─────────┬───────────────────────────┬──────────────────────────────────┤
│ Phase   │ Stage Name                │ Primary SOP / Playbook           │
├─────────┼───────────────────────────┼──────────────────────────────────┤
│ Phase 0 │ State Initialization      │ `app-lifecycle`, `project-init`  │
│ Phase 1 │ Strategy & Viability      │ `saas-strategist`, `auto-context`│
│ Phase 2 │ Architecture & Contracts  │ `project-architect`, `api-contr` │
│ Phase 3 │ TDD Construction          │ `strict-tdd`, `app-builder`      │
│ Phase 4 │ UI & Aesthetic Polish     │ `ui-finish`, `palette`           │
│ Phase 5 │ Security & Audit Gates    │ `integrity-sentinel`, `code-rev` │
│ Phase 6 │ Offload & Lifecycle Sync  │ `session-offload`, `self-evolve` │
└─────────┴───────────────────────────┴──────────────────────────────────┘
```

---

## Chapter 14: The 18 Canonical Operating Procedures

### 14.1. Lifecycle & Scaffolding SOPs
1. **`app-lifecycle` (`/app-lifecycle`)**: Master Full Lifecycle Pipeline. Evaluates project maturity and orchestrates phased progression through the state machine.
2. **`project-init` (`/project-init`)**: Greenfield Scaffolding Engine. Enforces 3-question requirements intake and constructs the 4 lean pillars in `context/` (`BLUEPRINT.md`, `ROADMAP.md`, `STYLE_GUIDE.md`, `ARCHITECTURE.md`).
3. **`project-migrate` (`/project-migrate`)**: Brownfield & Legacy Onboarding. Safely embeds `.agents` infrastructure into existing codebases without disrupting active builds or production code.
4. **`app-builder` (`/app-builder`)**: Surgical Feature Construction. Shape Spec → Bento-Box UI Design → Immutable Data Models → Adversarial Verification.
5. **`feature-sunset` (`/feature-sunset`)**: Phased Deprecation & Sunset. Dual-write transition → Telemetry deprecation notice → Systematic dead code removal.

### 14.2. Verification & Quality Sentinel SOPs
6. **`audit-vectors` (`/integrity-sentinel`)**: Consolidated Diagnostic Matrix. Executes structured scans across Architecture, Bloat, Duplication, Fail-Fast, Logic, Performance, and Retry behaviors.
7. **`strict-tdd` (`/strict-tdd`)**: Strict Test-Driven Development Loop. Enforces RED-GREEN-REFACTOR cycle with mechanical rollback (`git stash`) if implementation precedes failing tests (`Exit Code > 0`).
8. **`systematic-debugging` (`/systematic-debugging`)**: 4-Phase Root Cause Protocol. Investigation → Pattern Analysis → Hypothesis Testing → Surgical Fix with 3-attempt circuit breaker.
9. **`code-review` (`/code-review`)**: Adversarial PR Review. OWASP checks, mutation audits, temporal edge-case simulation, and Lessword formatting (`🔴 bug:`, `🟡 risk:`, `🔵 nit:`, `❓ q:`).
10. **`audit-ledger` (`/audit-ledger`)**: Multi-Session Audit Ledger. Manages persistent tracking of findings and remediations across extended refactoring initiatives.

### 14.3. Knowledge & Cognitive Memory SOPs
11. **`auto-context` (`/auto-context`)**: Conversational Business Rule Extraction. Captures user design feedback and architectural decisions, updating `context/` markdown files.
12. **`knowledge-extraction` (`/knowledge-extraction`)**: Semantic Graph Triplet Extraction. Parses code syntax, extracts 3–5 structural triplets `(Subject, Predicate, Object)`, and inserts them into `orion.db`.
13. **`orion-ops` (`/orion-ops`)**: Local Knowledge Base Administration. Initializes `.orion/`, rebuilds FTS5 indexes, validates database schemas, and runs graph maintenance.

### 14.4. Operations, Evolution & Session SOPs
14. **`prod-deploy` (`/prod-deploy`)**: Production Deployment Readiness. Pre-flight verification of environment variables, minification, secrets scanning, and rollback procedures.
15. **`self-evolve` (`/self-evolve`)**: Deterministic Self-Learning Loop. Error extraction → Append to `LEARNINGS.md` → Darwinian A/B evaluation → Promotion to permanent rules.
16. **`session-offload` (`/session-offload`)**: Clean Session Shutdown. Temporary file eviction, gated auto-commits, episodic journal writing, and handoff persistence (`handoff.md`).
17. **`temporal-pulse` (`/temporal-pulse`)**: Activity-Based Temporal Synthesis. Evaluates memory consolidation across Session Pulses, Milestone Syntheses (every 5 sessions), and Epoch Consolidations (every 4 milestones).
18. **`lessword-compress` (`/lessword`)**: Deterministic Context & Memory Compression. Token reduction protocol, AST skeletal hollowing, and Shannon Surprisal filtering for LLM context optimization.
