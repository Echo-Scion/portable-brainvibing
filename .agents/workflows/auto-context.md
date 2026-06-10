---
description: Organic Business Rule Extraction from Conversations
activation: Called automatically during /session-offload, or manually via /auto-context
---

# /auto-context (Conversational Context Extraction)

This workflow is the bridge between human conversation and the structural 82-file `context/` matrix. It extracts business logic, architectural decisions, and domain rules from recent chats and automatically injects them into the correct context files.

## 1. Context Harvest (Read Phase)
- **Review Working Memory**: Analyze the contents of `.orion/working/handoff.md` and the recent transcript logs.
- **Identify Knowledge**: Look for explicit business rules, workflow exceptions, logic constraints, or architectural decisions stated by the user. Do not extract trivial debugging steps.
- **Example Targets**: 
  - *"Only superadmins can bypass the payment gateway."*
  - *"We decided to use Redis for this cache instead of local state."*

## 2. Structural Routing (Map Phase)
For each extracted piece of knowledge, determine its proper destination within the 82-file structure.
- **00_Strategy**: Business goals, user personas, revenue logic.
- **01_Product**: User roles, feature requirements, UI/UX specs.
- **02_Creative**: Color themes, typography, tone of voice.
- **03_Tech**: Architecture, data schemas, API contracts, dependencies.

*If the target file does not exist, use your `write_to_file` tool to create it inside the appropriate folder.*

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
