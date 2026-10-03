# 🧭 Context Atlas: Scionlog & Orion Foundation

Welcome to the central [[knowledge]] repository for **Scionlog & Orion Foundation** (Portable Brainvibing).

This directory houses the human- and AI-readable business, product, creative, and technical [[knowledge]]. It is organized according to the **4 Lean Pillars** architectural standard.

---

## 🏛️ The 4 Lean Pillars

```text
context/
├── AGENT_IDENTITY.md         # Neuro-cognitive traits, identity, and evolution ledger
├── README.md                 # Master Context Atlas (this file)
├── 00_Strategy/
│   └── BLUEPRINT.md          # [MASTER] Vision, problem discovery, market dynamics, and scope
├── 01_Product/
│   └── ROADMAP.md            # [MASTER] Product roadmap, viability scorecard, milestones, and anti-goals
├── 02_Creative/
│   └── STYLE_GUIDE.md        # [MASTER] Visual aesthetic, CLI formatting, Telegram alerts, and tone
└── 03_Tech/
    └── ARCHITECTURE.md       # [MASTER] System components, data pipelines, SQLite schema, and security
```

---

## ⚡ JIT (Just-In-Time) Expansion Protocol

To prevent context bloat, only the **4 Master Files** exist initially. When deep focus is required for a specific sub-domain, create the granular detail file using the official prefixes defined in `.agents/templates/PROJECT_SCAFFOLD.template.md`:

| Pillar | Sub-Domain Focus | Allowed Prefixes | Examples |
| :--- | :--- | :--- | :--- |
| **`00_Strategy/`** | Idea, Validation, Scaling | `Idea_`, `Valid_`, `Scale_` | `Idea_Market_Research.md`, `Valid_Demand_Testing.md` |
| **`01_Product/`** | Planning, Launch, Growth, Rev | `Plan_`, `Launch_`, `Acq_`, `Rev_`, `Data_`, `Ret_` | `Plan_MVP_Scope.md`, `Rev_Pricing_Strategy.md` |
| **`02_Creative/`** | Design, UX, Tokens | `Design_` | `Design_Design_System.md`, `Design_UX_Flows.md` |
| **`03_Tech/`** | Dev, Infra, Testing | `Dev_`, `Infra_`, `Test_` | `Dev_Database.md`, `Infra_CI_CD.md`, `Test_Unit_Testing.md` |

---

## 🔗 Bi-Directional Neuro-Link
- **Working Context Buffer**: `.orion/working/context.json`
- **Machine RAG Graph**: `.orion/orion.db` (Indexed via `python .agents/scripts/orion.py orion_ops ingest context/`)
- **Agent Rules & Protocols**: `.agents/rules/`
