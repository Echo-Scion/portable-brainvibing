---
name: auto-context
description: Organic Business Rule Extraction from Conversations
activation: Called automatically during /session-offload, or manually via /auto-context.md
---

# /auto-context.md (Conversational Context Extraction)

This workflow is the bridge between human conversation and the **25-File Golden Ratio `context/` matrix**. It extracts business logic, architectural decisions, and domain rules from recent chats and automatically injects them into the correct context files (never modifying `context/VISION.md`).

## 1. Context Harvest (Read Phase)
- **Review Working Memory**: Analyze the contents of `.orion/working/handoff.md` and the recent transcript logs.
- **Identify Knowledge**: Look for explicit business rules, workflow exceptions, logic constraints, or architectural decisions stated by the user. Do not extract trivial debugging steps.
- **Example Targets**: 
  - *"Only superadmins can bypass the payment gateway."*
  - *"We decided to use Redis for this cache instead of local state."*

## 2. Structural Routing (Map Phase)
For each extracted piece of knowledge, determine its proper destination within the **25-File Golden Ratio structure** (never modifying `context/VISION.md`):
- **00_Strategy**: `BLUEPRINT.md`, `MEMORY.md`, `PERSONAS_AND_MARKET.md`, `ACQUISITION_AND_GROWTH.md`, `MONETIZATION_AND_PRICING.md`, `RETENTION_AND_LEGAL.md`.
- **01_Product**: `ROADMAP.md`, `PRD_CORE_FEATURES.md`, `USER_JOURNEYS_AND_FLOWS.md`, `ANALYTICS_AND_METRICS.md`, `INTEGRATIONS_AND_WEBHOOKS.md`, `FEEDBACK_AND_BACKLOG.md`.
- **02_Creative**: `STYLE_GUIDE.md`, `UI_COMPONENTS_AND_PATTERNS.md`, `UX_AND_ACCESSIBILITY.md`, `BRAND_VOICE_AND_COPY.md`, `VISUAL_ASSETS_AND_MEDIA.md`.
- **03_Tech**: `ARCHITECTURE.md`, `DATABASE_AND_STORAGE.md`, `API_AND_CONTRACTS.md`, `STATE_AND_DOMAIN_LOGIC.md`, `SECURITY_AND_AUTH.md`, `INFRA_AND_DEVOPS.md`.

*If the target file does not exist, the Agent MUST execute the `write_to_file` tool to create it inside the matching categorized folder.*

## 3. Injection (Write Phase)
- **Action**: Use your `replace_file_content` or `write_to_file` tools to inject the knowledge into the file.
- **Format Constraint**: If the file contains a `<!-- LEGACY MERGE START -->` or `<!-- CONVERSATION MERGE START -->` marker, insert the new knowledge below it. Use clear bullet points and specify the date of extraction.

Example Format:
```markdown
### Extracted from Session: YYYY-MM-DD
- **Rule**: Only superadmins can bypass the payment gateway.
```

## 4. Semantic Commit (Ingest Phase)
You MUST execute the Orion Ingestion script immediately after modifying the context files so the Brain Graph indexes the new knowledge.
- **Command**: `python .agents/scripts/orion.py orion_ops ingest <path_to_modified_context_file>`

## 5. Closure
Provide a terse summary of exactly what rules were extracted and which files were updated.
