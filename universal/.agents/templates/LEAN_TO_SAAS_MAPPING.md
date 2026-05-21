# Bi-directional Mapping: Lean (Master) ↔ SaaS (Surgical Detail)

This document defines how the 82 granular SaaS files map to the 4 Lean Master Files.

## 1. Logic: Master vs Surgical Detail
*   **Master Files (Lean)**: High-level overview, index of detail files, and "Atlas" for the project.
*   **Surgical Detail Files (SaaS)**: Deep technical/strategic data for specific sub-domains.

| Lean Master File | SaaS Prefixes (Children) | Integration Method |
| :--- | :--- | :--- |
| **`00_Strategy/BLUEPRINT.md`** | `Idea_`, `Valid_`, `Scale_` | Blueprint contains summaries; Detail files contain execution data. |
| **`01_Product/ROADMAP.md`** | `Plan_`, `Launch_`, `Acq_`, `Dist_`, `Conv_`, `Rev_`, `Data_`, `Ret_`, `Growth_` | Roadmap tracks milestones; Detail files track funnels, metrics, and models. |
| **`02_Creative/STYLE_GUIDE.md`** | `Design_` | Style Guide defines tokens; Detail files contain flows and wireframe specs. |
| **`03_Tech/ARCHITECTURE.md`** | `Dev_`, `Infra_`, `Test_` | Architecture defines system logic; Detail files contain API contracts and DevOps SOPs. |

## 2. Expansion Logic (Lean to SaaS)
When a project "upgrades" to Startup mode:
1.  **Keep Masters**: Master files (`BLUEPRINT`, `ROADMAP`, etc.) remain in place.
2.  **JIT Generation**: AI generates Prefix-based detail files (e.g., `Rev_Pricing_Strategy.md`) only when the task requires it.
3.  **Cross-Linking**: Master files MUST include standard Markdown links (e.g., `[Prefix_Filename.md](./Prefix_Filename.md)`) to their children for navigation.

## 3. Migration (SaaS to Lean)
When "downgrading" or simplifying:
1.  **Condense**: AI reads all Prefix files and summarizes them back into the 4 Master files.

---
*Portable Brainvibing Infrastructure - Unified Context Mapping Protocol*