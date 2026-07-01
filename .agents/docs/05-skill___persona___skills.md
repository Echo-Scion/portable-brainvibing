# VOLUME V: SKILL / PERSONA (`skills/`) — 16 Specializations

---

## Chapter 10: Skill Concept
Each skill is a "hat" worn by the AI. When loaded, the skill limits the AI's focus to a specific domain and enforces a specific mindset. Each skill folder contains `SKILL.md` (mandatory instructions) and optionally `references/` (in-depth supporting documents).

### 10.1. `ai-engineer`
**Domain:** Mitigating the probabilistic nature of LLMs.
**Content:** Assertion matrix, Confidence Gates, anti-hallucination. Used when the agent modifies the `.agents` folder itself.

### 10.2. `api-contract`
**Domain:** Client/server interface contracts.
**Content:** OpenAPI specifications, Zod validation, API safety patterns.
**Reference:** `references/api_safety_patterns.md`.

### 10.3. `brain-graph`
**Domain:** Operating `orion.db` and local RAG.
**Content:** FTS5 querying, triplet injection, SQLite maintenance.

### 10.4. `caveman`
**Domain:** Ultra-terse communication compression.
**Content:** 6 intensity levels. Supports `wenyan` (classical Chinese variant).

### 10.5. `caveman-compress`
**Domain:** `.md` file compression.
**Content:** Reads markdown files and replaces them with terse versions via regex. Saves a `.original.md` backup.

### 10.6. `cost-optimizer`
**Domain:** Token and cloud budget management.
**Content:** Routing cheap models (Haiku) for simple tasks, expensive models (Opus) for complex tasks.

### 10.7. `data-logic`
**Domain:** Data immutability.
**Content:** Forbids global state, Redux/Zustand patterns, pure functions, DTOs must not be mutated.

### 10.8. `frontend-experience`
**Domain:** UI/UX debugging.
**Content:** Fixing excessive re-renders, DOM infinite loops, React/Flutter state synchronization.
**Reference:** `references/ux-designer.md`.

### 10.9. `integrity-sentinel`
**Domain:** Red Team & Automated QA.
**Content:** Architecture audit, bloat audit, duplicate audit, fail-fast audit, logic audit, performance audit, retry audit, load testing.
**References:** 11 sub-documents: `architecture-audit.md`, `bloat-audit.md`, `duplicate-audit.md`, `fail-fast-audit.md`, `flutter_testing_patterns.md`, `load_testing_tactics.md`, `logic-audit.md`, `master-audit.md`, `performance-audit.md`, `plan-checklist.md`, `retry-audit.md`, `telemetry-gate.md`.

### 10.10. `meta-agent-admin`
**Domain:** Architect of the `.agents` system itself.
**Content:** Ecosystem evolution, rule creation, routing integrity.
**References:** `agent-architect.md`, `agent-evolution.md`, `context-manager.md`, `knowledge.md`, `loop_design_patterns.md`, `system-admin.md`, `tech-writer.md`.

### 10.11. `palette`
**Domain:** Micro-aesthetics & accessibility.
**Content:** CSS tokens, smooth animations, ARIA labels, glassmorphism, color harmony, keyboard navigation.

### 10.12. `project-architect`
**Domain:** High-scale PRD & Blueprints, and Master backend architect.
**Content:** Translating user ideas into technical documents before code is written, Node.js memory leak management, connection pooling, SQL optimization, database indexing.
**References:** `architectural_standards.md`, `startup_growth.md`, `strategic_rigor.md`, `structural_pillars.md`, `backend-architect.md`, `backend-optimizer.md`, `cache-optimizer.md`, `db-expert.md`, `enterprise_patterns.md`, `node_performance_tuning.md`, `postgres_patterns.md`.

### 10.13. `project-operator`
**Domain:** DevOps & resilience.
**Content:** Dockerfiles, CI/CD pipelines, Nginx, chaos engineering.
**References:** `chaos-engineer.md`, `release-manager.md`.

### 10.14. `saas-strategist`
**Domain:** SaaS business strategy.
**Content:** Viability analysis, monetization, growth, viral content.
**References:** `saas-growth.md`, `saas-viability.md`, `technical_content.md`, `viral_growth.md`.

### 10.15. `ui-finish`
**Domain:** Premium UI final polish.
**Content:** Empty states, loading spinners, error boundaries, Liquid Glass widgets.
**Reference:** `visual_engineering.md`.

---

