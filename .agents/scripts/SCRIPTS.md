#  Scripts & Automation Index

This directory contains global utilities and automation scripts for the **Portable Brainvibing** infrastructure.

## Modular CLI: `orion.py`

This directory uses a **Modular CLI** architecture. Instead of calling individual scripts, use the `orion.py` entrypoint.

| Command | Purpose | Target Script |
| :--- | :--- | :--- |
| `python .agents/scripts/orion.py verify` | Scans for broken links/headers (Mechanical Audit). | `commands/verify_agents.py` |
| `python .agents/scripts/orion.py context-lint` | Validates `context/` naming against registry. | `commands/context_naming_lint.py` |
| `python .agents/scripts/orion.py deploy` | Physically deploys/syncs Foundation to a local project. | `commands/foundation.py` |
| `python .agents/scripts/orion.py push-upstream` | Syncs local agent evolution back to the Foundation. | `commands/foundation.py` |
| `python .agents/scripts/orion.py budget` | Tracks budget and tier telemetry. | `commands/track_budget.py` |
| `python .agents/scripts/orion.py scan tokens` | Ghost Token Auditor (detects memory bloat, RTK savings). | `commands/scanner.py` |
| `python .agents/scripts/orion.py scan map` | Structural Code Mapper (generates lightweight skeleton). | `commands/scanner.py` |
| `python .agents/scripts/orion.py scan targets` | Identifies targets for the Offensive Audit protocol. | `commands/scanner.py` |
| `python .agents/scripts/orion.py preflight` | Pre-flight diagnostic (Self-Healing Routing). | `commands/preflight_check.py` |
| `python .agents/scripts/orion.py compress` | Compresses episodic memory into Caveman format. | `commands/compress_memory.py` |
| `python .agents/scripts/orion.py orion_ops init` | Initializes the `.orion/` infrastructure. | `commands/orion_ops.py` |
| `python .agents/scripts/orion.py orion_ops ingest`| Ingests rules and configs into the `.orion/` graph. | `commands/orion_ops.py` |
| `python .agents/scripts/orion.py amnesia` | Rule eviction mechanism. | `commands/rule_eviction.py` |
| `python .agents/scripts/orion.py swarm` | Multi-Threaded Micro-Fix Swarm. | `commands/auto_delegate.py` |
| `python .agents/scripts/orion.py rtk` | RTK Proxy. | `core/rtk_proxy.py` |

## Organization Policy

1. **Global Entrypoint**: `orion.py` is the only script called directly.
2. **Command Modules**: Placed in `commands/`.
3. **Core Utilities**: Placed in `core/`.
4. **Output Files**: Scripts should NEVER write persistent logs or reports to the root. Use a `logs/` folder or system-specific temp directories.
