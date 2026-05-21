# 📋 Templates & Scaffolding Index

This directory contains the master blueprints and boilerplates for the **Portable Brainvibing** infrastructure. These files are used to ensure structural consistency when initializing new projects or promoting new features.

## 🏛️ Core Master Templates
These are used for the main 4-Pillar Master files in the `context/` directory.

| Template | Target File | Purpose |
| :--- | :--- | :--- |
| [BLUEPRINT.template.md](BLUEPRINT.template.md) | `00_Strategy/BLUEPRINT.md` | Strategic system design and vision. |
| [ROADMAP.template.md](ROADMAP.template.md) | `01_Product/ROADMAP.md` | Feature planning and milestones. |
| [STYLE_GUIDE.template.md](STYLE_GUIDE.template.md) | `02_Creative/STYLE_GUIDE.md` | UI/UX tokens and flows. |
| [ARCHITECTURE.template.md](ARCHITECTURE.template.md) | `03_Tech/ARCHITECTURE.md` | System stack and patterns. |

## 🛠️ Operational Templates
Templates for day-to-day agent operations and task management.

| Template | Purpose |
| :--- | :--- |
| [AGENTS.template.md](AGENTS.template.md) | Multi-AI instruction generator (DRY source). |
| [ATOMIC_TASK.template.md](ATOMIC_TASK.template.md) | Blueprint for breaking down complex tasks. |
| [SESSION_HANDOFF.template.md](SESSION_HANDOFF.template.md) | Format for cross-session context persistence. |
| [PROJECT_BRIEF.template.md](PROJECT_BRIEF.template.md) | Intake schema for new project requirements. |

## 🧩 Extension Templates
For developers to extend the ecosystem.

| Template | Purpose |
| :--- | :--- |
| [custom-agent.template.md](custom-agent.template.md) | Scaffold for new specialized Copilot agents. |
| [custom-rule.template.md](custom-rule.template.md) | Scaffold for new behavioral rules. |

## 🧠 Knowledge & Memory Templates
Templates for specialized SaaS knowledge and episodic memory.

| Template | Purpose |
| :--- | :--- |


| [MEMORY.template.md](MEMORY.template.md) | Core decision tracking and friction logging. |
| [WIKI_SCHEMA.template.md](WIKI_SCHEMA.template.md) | Configuration for the `.wiki/` graph. |

## 📖 Reference Docs (Static)
| File | Purpose |
| :--- | :--- |


| [github-native-structure.md](github-native-structure.md) | Canonical GitHub folder structure guide. |
| [startup_knowledge_base.md](startup_knowledge_base.md) | Domain-specific instructions for auto-population. |

---
*Policy: If a template is added, it MUST be indexed here to prevent it from being flagged as unreferenced (Ghost Token).*
