---
description: Master index linking all components (Rules, Skills, Workflows) of the agent ecosystem.
activation: when navigating the ecosystem or seeking an overview of agent capabilities
---
# 🗺️ AGENTS MASTER INDEX

> **CAVEMAN COMPRESS MODE**: Master map. Directs AI to correct subsystem.

## 1. 📚 RULES (The Core Guardrails)
- **Index**: `.agents/rules/RULES_INDEX.md` (Master index of all standards)
- **Primary Guardrail**: `.agents/rules/core-guardrails.md`
- **Formal State Machine**: `.agents/rules/standards/fsm-protocol.md`
- **Contradiction**: `.agents/rules/contradiction-protocol.md`
- **Memory Hygiene**: `.agents/rules/memory-hygiene.md`

## 2. 🛠️ SKILLS (The Personas & Domains)
*Skills define deep domain knowledge and specialized personas.*

- **ai-engineer**: `.agents/skills/ai-engineer/SKILL.md` (Mitigating probabilistic nature, AI engineering)

- **caveman**: `.agents/skills/caveman/SKILL.md` (Ultra-compressed communication)
- **caveman-compress**: `.agents/skills/caveman-compress/SKILL.md` (Token reduction for docs)
- **cost-optimizer**: `.agents/skills/cost-optimizer/SKILL.md` (Cloud/LLM token budgeting)

- **integrity-sentinel**: `.agents/skills/integrity-sentinel/SKILL.md` (Security audits, QA)
- **brain-graph**: `.agents/skills/brain-graph/SKILL.md` (Brain Graph, Orion, Knowledge base)
- **meta-agent-admin**: `.agents/skills/meta-agent-admin/SKILL.md` (Ecosystem evolution, you are here)

- **project-architect**: `.agents/skills/project-architect/SKILL.md` (System Architecture, Blueprints)
- **project-operator**: `.agents/skills/project-operator/SKILL.md` (Deployments, Release cycles)

- **api-contract**: `.agents/skills/api-contract/SKILL.md` (API Schemas, Zod, Request Validation)
- **data-logic**: `.agents/skills/data-logic/SKILL.md` (Data Immutability, State Management)
- **frontend-experience**: `.agents/skills/frontend-experience/SKILL.md` (Debugging, Errors, Runtime Issues)
- **palette**: `.agents/skills/palette/SKILL.md` (Accessibility, A11y, Micro-interactions)
- **saas-strategist**: `.agents/skills/saas-strategist/SKILL.md` (Business Strategy, Growth, Idea Viability)
- **ui-finish**: `.agents/skills/ui-finish/SKILL.md` (Frontend UI, Layout, Aesthetics, Animations)

## 3. 🚀 WORKFLOWS (The Lifecycle Checklists)
*Workflows define step-by-step procedures.*

- **app-builder**: `.agents/workflows/app-lifecycle.md` (End-to-end feature creation)
- **auto-context**: `.agents/workflows/auto-context.md` (Organic Business Rule Extraction)
- **code-review**: `.agents/workflows/audit-and-test.md` (Source code quality review)
- **full-lifecycle**: `.agents/workflows/app-lifecycle.md` (New project/feature lifecycle)
- **knowledge-sync**: `.agents/workflows/knowledge-sync.md` (Internal foundation doc update & version bump)
- **prod-deploy**: `.agents/workflows/prod-deploy.md` (Environment readiness checklist)
- **project-init**: `.agents/workflows/app-lifecycle.md` (Root/sub-project unified initialization)
- **project-migrate**: `.agents/workflows/project-migrate.md` (Brownfield/Legacy onboarding)
- **self-evolve**: `.agents/workflows/self-evolve.md` (Agent self-learning loop)
- **session-offload**: `.agents/workflows/session-offload.md` (Context eviction, handoff)
- **strict-tdd**: `.agents/workflows/audit-and-test.md` (Test-driven development cycle)
- **orion-ops**: `.agents/workflows/orion-ops.md` (Orion query and linting procedures)

## 4. 🧰 CORE SCRIPTS (The Execution Engine)
*Python scripts that power the ecosystem, triggered by hooks or manual orchestration.*

- **state_machine**: `.agents/scripts/commands/state_machine.py` (FSM Engine)
- **consolidate**: `.agents/scripts/commands/consolidate.py` (Temporal Pulse)
- **contradict**: `.agents/scripts/commands/contradict.py` (Predicate Collision)
- **pre-agent-wake**: `.agents/hooks/pre-agent-wake.py` (Bootstrapper)
- **nano_compressor**: `.agents/scripts/commands/nano_compressor.py` (Memory compression)

