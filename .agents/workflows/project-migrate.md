---
description: Onboarding workflow for legacy or brownfield projects (90% done) into the Portable Brainvibing architecture.
---

# PROJECT MIGRATE & BROWNFIELD ONBOARDING

## Workflow: Project Migrate (`/project-migrate`)

Follow these steps exactly when installing the Portable Brainvibing foundation (`.agents` directory) into an **existing, mostly complete (Brownfield)** codebase.

> **CRITICAL RULE**: Do NOT attempt to use AI to auto-generate the 82 SaaS Context files by scanning the existing codebase. AI cannot safely reverse-engineer business logic, revenue models, or legal boundaries from raw code. You MUST follow the manual injection protocol below.

## Phase 0: State Initialization (MANDATORY)
- **Action**: Create or overwrite `.orion/task.md` with the checklist of this workflow.
- **Rule**: At the start of every phase below, you MUST mark its checkbox as `[/]` (in-progress) in `.orion/task.md`. At the end of every phase, mark it `[x]` (done).

## Phase 1: Architectural Extraction
Extract a lightweight skeleton of the existing codebase to provide cheap token context.
- **Command**: Run `python .agents/scripts/orion.py scan map`
- **Output**: This will generate an architectural skeleton without incurring massive token costs for full-file reads.

## Phase 2: Scaffold Empty Context
Generate the foundational knowledge structure using the 82-file registry, but keep the files empty for manual injection.
- **Command**: `python .agents/scripts/orion.py brain sync "init SaaS structure"`
- **Command**: `python .agents/scripts/orion.py brain scaffold_saas`
- **Action**: Use `run_command` to physically scaffold the directories: `mkdir -p context/00_Strategy context/01_Product context/02_Creative context/03_Tech`.

## Phase 3: Context Extraction & Inference
- **Action 1: Strategy (README Integration)**:
  - Check if `README.md` exists in the workspace root.
  - **If exists**: Execute `view_file README.md` to extract business context. Integrate into `context/00_Strategy/BLUEPRINT.md`.
  - **If missing**: Create `README.md` using `write_to_file` with temporary content: `This project is managed by Portable Brainvibing. .orion supports context-less ingest. Refer to development-operations.md for legacy merge constraints.` Mirror this into `context/00_Strategy/BLUEPRINT.md`.
- **Action 2: Technical Inference**:
  - AI reads core dependency files (e.g., `package.json`, `pubspec.yaml`, `build.gradle`).
  - AI infers the language, framework, and core tech stack.
  - AI populates `context/03_Tech/ARCHITECTURE.md` with the extracted technical blueprint.
- **Action 3: Pillar Broad Strokes**:
  - AI populates `context/01_Product/ROADMAP.md` by broadly listing current state features.
  - AI populates `context/02_Creative/STYLE_GUIDE.md` by inferring UI libraries (e.g., Tailwind, Material) from dependencies.

## Phase 4: Legacy Documentation Merge
- **Action**: Move or integrate any pre-existing documentation (e.g., `README.md`, legacy specs) into the newly created 82-file `context/` structure.
- **Rule**: You MUST use the `<!-- LEGACY MERGE START -->` format inside the respective `context/` files when appending legacy text, as defined in `development-operations.md`. Do not summarize or alter the legacy text.

## Phase 5: Semantic Indexing & Safe Auto-Ingest
Now that the code skeleton and explicit business strategy exist, unify them in the Brain Graph.
- **Command**: `python .agents/scripts/orion.py orion_ops init`
- **Action**: Scaffolds `.orion/` + scans all layers into `_manifest.json`
- **Command (Safe Auto-Ingest)**: `python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons .agents/workflows context/`
- **Completion**: The existing codebase is now mapped semantically to the new SaaS context framework without hallucinating strategy.
