---
name: project-init
description: Unified project initialization workflow scaffolding context, DESIGN.md, and codebase architecture.
---

# 🚀 Workflow: Project Initialization (`/project-init`)

Follow these steps exactly when creating a new project or scaffolding a new major feature directory.

## 1. Requirements Intake
Read the user's prompt. If it is vague, do NOT guess.
- **MANDATORY BLOCK**: You MUST output the prompt: *"Please provide the core functionality, target audience, and primary platform."*
- **STOP EXECUTION**: You are FORBIDDEN from proceeding to Step 2 until the user has explicitly answered this question. Do not anticipate or hallucinate requirements.

## 2. Generate Context & Design Direction (Lean Scaffolding)
Create the foundational knowledge and design direction for the AI.
- **Action**: Use `run_command` to physically scaffold the workspace directories cross-platform: `python .agents/scripts/orion.py setup --yes --target .` (or `python .agents/scripts/orion.py orion_ops init`).
- **Action**: Generate `context/VISION.md` (instantiated from `.agents/templates/VISION.template.md`) as the Immutable North Star, and the 4 Master files inside `context/` (`00_Strategy/BLUEPRINT.md`, `01_Product/ROADMAP.md`, `02_Creative/STYLE_GUIDE.md`, `03_Tech/ARCHITECTURE.md`) using templates in `.agents/templates/`.
- **Action (Automatic DESIGN.md Generation)**: In the project root, automatically generate `DESIGN.md` instantiated from `.agents/templates/DESIGN.template.md`. 
  - Tailor its Identity, Palette Tokens, Typography, Macrostructure, and Liveliness Dials (`ENERGY`, `RHYTHM`, `MOTION`) uniquely to the project's philosophy, audience, and platform derived from Step 1.
  - If reference screenshots or URLs are provided, execute the Visual DNA Extraction protocol (extracting layout cadence, typographic scale, and palette tokens into `DESIGN.md` without copying pixels).
  - Verify that color contrast ratios comply with WCAG 2.x via `python .agents/evals/audit_aesthetics.py --contrast "<fg_hex>" "<bg_hex>"`.
- **Rule (Anti-Bloat)**: DO NOT generate detail files here. Detail files are generated Just-In-Time (JIT) later in the lifecycle.

## 3. Scaffold Architecture (Codebase) & Apply Constraints
Generate the source directory structure for the app itself using Universal Living Project DNA.
- **Command**: `view_file .agents/skills/project-architect/SKILL.md`
- **DNA Stratification**: Follow the 5-Tier Architectural Stratification (`contracts`, `domain`, `services`, `state`, `presentation`).
  - *Small single-module apps*: Use `src/<tier>` or `lib/<tier>`.
  - *Multi-feature apps*: Use `src/features/<feature>/<tier>` or `lib/features/<feature>/<tier>` (Option A: Adaptive Hybrid).
- **DNA Manifest**: Verify `.agents/.dna.json` is stamped with `schema_version: "0.0.1"`, `dna_state: "GREENFIELD"`, and initial execution spine. Run `python .agents/scripts/orion.py dna audit` to verify zero layer violations.
- **Hardware Constraint Rule**: Check for resource-heavy defaults in the scaffolded project. Load the relevant ecosystem canon from `canons/ecosystems/` for platform-specific memory/resource optimizations. Recommend lightweight IDE and physical device testing on constrained hardware.

## 4. Install Infrastructure Tooling
Set up the mechanical verifiers.
- **Action**: Run `python .agents/scripts/orion.py verify_agents` to ensure the ecosystem is intact in the new directory.

## 5. First-Pass Semantic Indexing
Ensure the new project is searchable.
- **Command**: Run `python .agents/scripts/orion.py scan map` to generate an architectural skeleton.

## 6. Bootstrap & Safe Auto-Ingest Brain Graph
- **Command**: `python .agents/scripts/orion.py orion_ops init`
- **Action**: Scaffolds `.orion/` + scans all layers into `_manifest.json`, ensuring `.agents/.dna.json` governance specification is stamped.
- **Command (Safe Auto-Ingest)**: `python .agents/scripts/orion.py orion_ops ingest .agents/rules .agents/skills .agents/canons context/`
- **Note**: Auto-ingest is SAFE here because it strictly targets high-signal knowledge directories, preventing SQLite bloat from `build/` or `android/` folders.
