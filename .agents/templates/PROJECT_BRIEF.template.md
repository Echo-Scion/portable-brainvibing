---
description: Schema definition for the core $PROJECT_BRIEF object holding intake parameters
---

# PROJECT BRIEF SCHEMA

During `/project-init` (Step 0 Intake), the agent MUST compile the user's answers into this JSON schema. **Crucially, the AI must then perform a "Deepening Phase" to infer the architectural slots needed for the Blueprint.**

```json
{
  "project_info": {
    "name": "Project Name",
    "tagline": "A short, one-sentence description",
    "monetization": "e.g., SaaS, B2B",
    "persona": "Target user description"
  },
  "technical_info": {
    "stack": "Primary languages/frameworks",
    "detected_state": "fresh | legacy | blueprint",
    "features": ["Core features list"],
    "token_optimization": "Strategies for lean context (e.g., telegraphic, symbol-only)"
  },
  "inferred_logic": {
    "etymology": "Derived meaning of the project name",
    "trinity_keywords": ["3 core values inferred from brief"],
    "dual_lens_concept": "The two primary user perspectives",
    "wow_moment": "The first 30 seconds experience",
    "architectural_risks": ["Potential technical debt or scale issues"],
    "structural_pillars": ["How it maps to the 8 pillars of Tier-S"]
  }
}
```