# 📜 Scripts & Automation Index

This directory contains global utilities and automation scripts for the **Portable Brainvibing** infrastructure.

## 🛠️ Global Utility Scripts

| Script | Purpose | Availability |
| :--- | :--- | :--- |
| [verify_agents.py](file:///<ROOT>/.agents/scripts/verify_agents.py) | Scans for broken links/headers (Mechanical Audit). | **PORTABLE** |
| [context_naming_lint.py](file:///<ROOT>/.agents/scripts/context_naming_lint.py) | Validates `context/` naming against 82-file registry + required master anchors. | **PORTABLE** |
| [sync_ai_configs.py](file:///<ROOT>/.agents/scripts/sync_ai_configs.py) | Synchronizes AI mandates across deployed config files (`GEMINI.md`, etc.). | **PORTABLE** |
| [track_budget.py](file:///<ROOT>/.agents/scripts/track_budget.py) | Tracks and reports "Small Model Superiority" KPIs and budget telemetry. | **PORTABLE** |
| [token_audit.py](file:///<ROOT>/.agents/scripts/token_audit.py) | Ghost Token Auditor (detects memory bloat, redundancy, and RTK savings). | **PORTABLE** |
| [code_map.py](file:///<ROOT>/.agents/scripts/code_map.py) | Structural Code Mapper (generates lightweight skeleton of the codebase). | **PORTABLE** |
| [deploy_foundation.py](file:///<ROOT>/.agents/scripts/deploy_foundation.py) | Physically deploys/syncs Foundation to a local project. | **PORTABLE** |

## 📐 Organization Policy

1.  **Global Scripts**: Place in `.agents/scripts/`. These should be generic enough to run from the root.
2.  **Module Scripts**: Place in `/<module_name>/scripts/` (e.g., `MainSystem/scripts/`).
3.  **Output Files**: Scripts should NEVER write persistent logs or reports to the root. Use a `logs/` folder or system-specific temp directories.