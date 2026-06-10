---
description: Master index for all foundation rules.
activation: always on
---

# 📚 Rules Index

This directory contains the core behavioral and operational constraints for the `_foundation` ecosystem. These files enforce how the AI plans, writes code, manages state, and performs tests.

## Core Rules

| File | Purpose |
| :--- | :--- |
| `core-guardrails.md` | **(START HERE)** The master AI behavioral protocol and operation constraints. |
| `ai-engineering-standards.md` | Concrete engineering algorithms to mitigate fundamental AI traits (Probabilistic nature, GIGO, Black Box). |
| `tier-execution-protocol.md` | Execution depth per tier (Budget/Standard/Premium) and reasoning standards. |
| `security-guardrails.md` | Absolute security constraints, offensive zero-trust audits, and Red Team exploit generation. |
| `web-api-standards.md` | Frontend UI/UX constraints (Liquid Glass) and strict backend data contracts (Zod, OpenAPI). |
| `development-operations.md` | Git workflows, PR reviews, Auto-Harness validation pipelines, and Context Management. |
| `antigravity-rtk-rules.md` | Rules for interacting with the RTK context proxy. |
| `performance-optimization.md` | Decision trees for performance optimization, token usage, and Bolt-level speed enforcement. |

---
*Policy: If a new rule is added, it MUST be indexed here and MUST include a frontmatter with `description` and `activation` tags.*
