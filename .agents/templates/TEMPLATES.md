# 📋 Templates & Scaffolding Index

This directory contains the master blueprints and boilerplates for the **Portable Brainvibing** infrastructure. 

<template-index>
## 🏛️ Core Master Templates

| Template | Target File | Purpose |
| :--- | :--- | :--- |
| `PROJECT_SCAFFOLD.template.md` | `00_Strategy/BLUEPRINT.md` & `03_Tech/ARCHITECTURE.md` | Unified master generation prompt for new architectures, SaaS domains, and 82-file mapping. |
| `STYLE_GUIDE.template.md` | `02_Creative/STYLE_GUIDE.md` | UI/UX tokens and flows. |
| `DESIGN.template.md` | `DESIGN.md` | Master 20+ design archetypes, color palettes, and locked visual tokens. |
| `AGENTS.template.md` | `.agents/AGENTS_INDEX.md` | Multi-AI instruction generator (DRY source). |
| `AI_ADAPTER.template.md` | Native adapter files | Lightweight adapters that route tools to canonical `AGENTS.md`. |
| `CURSOR_RULE.template.mdc` | `.cursor/rules/portable-brainvibing.mdc` | Native Cursor project rule adapter. |


## 🛠️ Operational & Memory Templates

| Template | Purpose |
| :--- | :--- |
| `TASK_PLANNING.template.md` | Unified Execution Checklists, Roadmaps, Project Briefs, and Atomic Tasks. |
| `MEMORY.template.md` | Unified State Tracking, SaaS Domain Memory, and Session Handoff. |
| `ADR.template.md` | Architectural Decision Record standard (Status, Context, Decision, Consequences). |
| `agent-identity-template.md` | Agent persona, onboarding bootstrap, and cognitive role identity. |

## 🧩 Extension Templates

| Template | Purpose |
| :--- | :--- |
| `custom-agent.template.md` | Scaffold for new specialized Copilot agents. |
| `custom-rule.template.md` | Scaffold for new behavioral rules. |

## 📖 Reference Docs (Static)

| File | Purpose |
| :--- | :--- |
| `github-native-structure.md` | Canonical GitHub folder structure guide. |
| `startup_knowledge_base.md` | Domain-specific instructions for auto-population. |
| `ORION_SCHEMA.template.md` | Configuration for the `.orion/` graph. |

</template-index>

---
*Policy: If a template is added, it MUST be indexed here to prevent it from being flagged as unreferenced (Ghost Token).*
