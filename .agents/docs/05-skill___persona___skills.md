# VOLUME V: SKILL & PERSONA (`skills/`) — 21 Public Domain Skills (+1 Internal)

---

## Chapter 11: Modular Skill Architecture (3-Tier Progressive Disclosure)

Each skill represents a distinct operational domain worn by the agent. To prevent context window saturation, skills adhere strictly to the **3-Tier Progressive Disclosure** architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        3-Tier Skill Anatomy                            │
├───────────────────┬───────────────────────────────┬────────────────────┤
│ Tier              │ File / Scope                  │ Token Footprint    │
├───────────────────┼───────────────────────────────┼────────────────────┤
│ 1. Metadata       │ YAML frontmatter (name, desc) │ < 100 tokens       │
│ 2. Runbook        │ SKILL.md body                 │ <= core_max_lines  │
│ 3. Deep Knowledge │ references/ & scripts/        │ Loaded on demand   │
└───────────────────┴───────────────────────────────┴────────────────────┘
```

The agent loads Tier 1 during discovery, mounts Tier 2 when activated via JIT routing, and accesses Tier 3 references only when navigating specific edge cases or executing specialized playbooks. Each `SKILL.md` declares a `core_max_lines` frontmatter ceiling (default 200 lines) enforced by `verify_agents.py`.

---

## Chapter 12: Complete Catalog of 21 Public Domain Skills

### 12.1. `ai-engineer`
- **Domain**: Mitigating the probabilistic limitations of LLMs (GIGO, drift, hallucinations, latency).
- **Core Directives**: Assertion matrices, confidence threshold gates, and multi-model fallback pipelines.
- **Trigger**: AI integrations, LLM features, prompt pipelines, ML evaluations.

### 12.2. `api-contract`
- **Domain**: Client/server interface contracts and payload safety.
- **Core Directives**: OpenAPI specifications, Zod/TypeBox validation schemas, and defensive API boundaries.
- **Reference**: `.agents/skills/api-contract/references/api_safety_patterns.md`.

### 12.3. `app-lifecycle`
- **Domain**: Master Full Lifecycle Pipeline & State Machine.
- **Core Directives**: Orchestrates project progression from Phase 0 (State Init) to Phase 6 (Offload).
- **Consolidated References**:
  - `project-init.md`: Greenfield scaffolding engine and 4 lean pillars setup.
  - `project-migrate.md`: Brownfield & legacy onboarding.
  - `app-builder.md`: Surgical feature construction and Bento-Box UI design.
  - `feature-sunset.md`: Phased component deprecation and dead code purging.

### 12.4. `brain-graph`
- **Domain**: Knowledge graph indexing and local RAG operations.
- **Core Directives**: SQLite3 FTS5 queries, triplet ingestion, Louvain community generation, and database maintenance.
- **Reference**: `.agents/skills/brain-graph/references/knowledge-extraction.md` (Semantic Graph Triplet Extraction).

### 12.5. `code-review`
- **Domain**: Adversarial code review and offensive security verification.
- **Core Directives**: OWASP vulnerability audits, algorithmic mutation testing, temporal state simulation, and Lessword review tags (`🔴 bug:`, `🟡 risk:`, `🔵 nit:`, `❓ q:`).

### 12.6. `cost-optimizer`
- **Domain**: Token expenditure and computational budget management.
- **Core Directives**: Model tier routing (BUDGET vs STANDARD vs PREMIUM), context window bloat detection, and Small Model Superiority (SMS) telemetry.

### 12.7. `data-logic`
- **Domain**: Data immutability and unidirectional data flow.
- **Core Directives**: Pure function transformation pipelines, immutable DTO definitions, and prevention of global mutable state.

### 12.8. `frontend-experience`
- **Domain**: Frontend architecture, component lifecycles, and UI state debugging.
- **Core Directives**: 4-state component verification, DOM render loop elimination, and reactive state synchronization.
- **Reference**: `.agents/skills/frontend-experience/references/ux-designer.md`.

### 12.9. `integrity-sentinel`
- **Domain**: Unified Quality Enforcement Hub, Pre-Completion Gatekeeper & QA Sentinel.
- **Core Directives**: Enforces the Iron Evidence Law, coordinates test-driven development, runs regression audits, and guards pre-completion gates.
- **Consolidated References**:
  - `audit_vectors.md`: Consolidated Diagnostic Matrix (merges architecture, bloat, duplicate, fail-fast, logic, performance, and retry audits).
  - `audit-ledger.md`: Multi-session audit state ledger.
  - `load_testing_tactics.md`: Stress testing patterns and concurrency boundaries.
  - `ui_testing_patterns.md`: Cross-framework UI interaction testing.
  - `plan-checklist.md`, `security.md`, `skill_inspector.md`, `telemetry-gate.md`.

### 12.10. `lessword`
- **Domain**: Ultra-terse, high-density communication compression (~75% token reduction).
- **Core Directives**: Drops articles, pleasantries, conversational filler, and hedging. Supports 6 intensity levels (`lite`, `full`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`).
- **Reference**: `.agents/skills/lessword/references/lessword-compress.md`.

### 12.11. `meta-agent-admin`
- **Domain**: AI agent ecosystem architecture, rule creation, and foundation governance.
- **Core Directives**: Rule authoring standards, JIT router integrity, structural line ceiling enforcement (`core_max_lines`), MCP server scaffolding, and ecosystem health audits.
- **References**: `agent-architect.md`, `agent-evolution.md`, `context-manager.md`, `knowledge.md`, `loop_design_patterns.md`, `mcp-builder.md`, `meta-agent-audit.md`, `skills-catalog.md`, `system-admin.md`, `tech-writer.md`.

### 12.12. `palette`
- **Domain**: Web/React micro-interactions, semantic HTML, and accessibility (a11y).
- **Core Directives**: ARIA labels, focus traps, keyboard navigation, color contrast ratios (WCAG AA/AAA), and micro-animations.

### 12.13. `project-architect`
- **Domain**: Technical PRDs, database schema design, and backend system architecture.
- **Core Directives**: High-concurrency system blueprints, connection pooling, SQL query plans, and vertical slice isolation.
- **References**: `architectural_standards.md`, `startup_growth.md`, `strategic_rigor.md`, `structural_pillars.md`.

### 12.14. `project-operator`
- **Domain**: Production release orchestration, CI/CD, and system resilience.
- **Core Directives**: Hermetic build validation, Docker configuration, pre-flight deployment gates, and chaos engineering.
- **References**: `prod-deploy.md`, `release-manager.md`, `chaos-engineer.md`.

### 12.15. `saas-strategist`
- **Domain**: SaaS product viability, growth architecture, and business models.
- **Core Directives**: Product viability scorecards, feature prioritization matrices, monetization structures, and viral loop design.
- **References**: `saas-viability.md`, `saas-growth.md`, `technical_content.md`, `viral_growth.md`.

### 12.16. `self-evolve`
- **Domain**: Post-task reflection, Habit Observation ledger governance, and deterministic learning loop.
- **Core Directives**: 5-status Observation Ledger (`OBSERVATIONS.md` / `OBSERVATIONS.archive.md`), 2nd-violation Tier-0 Barrier Escalation, Operator Habit Mining, and pattern synthesis into permanent rules.
- **References**: `temporal-pulse.md` (Session, Milestone, and Epoch cadences) and `starter-principles.md`.

### 12.17. `session-offload`
- **Domain**: Clean session shutdown, context eviction, and handoff persistence.
- **Core Directives**: Temporary scratchpad deletion, gated auto-commits, episodic memory writing, and `handoff.md` generation.
- **Reference**: `.agents/skills/session-offload/references/auto-context.md` (Conversational Business Rule Extraction).

### 12.18. `strict-tdd`
- **Domain**: Strict Test-Driven Development enforcement.
- **Core Directives**: Mandatory RED-GREEN-REFACTOR cycle with mechanical rollback (`git stash`) if implementation code is written prior to a verified failing test (`Exit Code > 0`).

### 12.19. `systematic-debugging`
- **Domain**: Scientific 4-phase root-cause discipline.
- **Core Directives**: Phase 1 (Root Cause Investigation) → Phase 2 (Differential Pattern Analysis) → Phase 3 (Single Hypothesis Testing) → Phase 4 (Surgical Fix with 3-attempt circuit breaker).

### 12.20. `ui-finish`
- **Domain**: Premium visual aesthetics, restrained design, and UI state polish.
- **Core Directives**: Linear/Raycast design aesthetics, empty state designs, loading skeletons, and design token contracts.
- **Reference**: `.agents/skills/ui-finish/references/visual_engineering.md`.

### 12.21. `worker-delegate`
- **Domain**: Sub-agent task decomposition and asynchronous delegation.
- **Core Directives**: Context-isolating read-only scout, Jaccard dependency overlap gate (`orion.py delegate-check`), patch-spec drafting, and Omni-Buffer (`context.json`) Context Delta auto-ingestion. Stores delegation outputs in `.agents/working/delegations/`.
