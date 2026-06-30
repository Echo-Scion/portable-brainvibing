# Architectural Standards & Examples (Legacy Deep-Dive)

## 📖 Chapter Guidelines (Soul & Hand)
- **Chapters 1-4 (The Soul)**: Focus on narrative, philosophy, and user psychology. Do not skip the "Diagnostic Extraction."
- **Chapters 5-7 (The Hand)**: Focus on technical implementation, file paths, and dependency mapping.

## 🛠️ Master Blueprint Examples
**Scenario**: "I want to build a Flutter app for tracking my daily water intake."
**Expected Output**:
1. **Diagnostic Extraction**: Identify "Inconsistent hydration tracking" as the core pain point.
2. **Scaffolding**: Load `.agents/templates/PROJECT_SCAFFOLD.template.md`.
3. **Planning (Chapter 8)**: 
   - Path: `lib/features/hydration/domain/models/intake.dart` -> Define immutable `@freezed` model.
   - Path: `lib/features/hydration/presentation/providers/intake_provider.dart` -> Define StateNotifier.
4. **Validation**: Check against the 8 Pillars in `references/structural_pillars.md`.

## ⚠️ Troubleshooting Details
- **Blueprint feels generic**: Stop. Re-read the guidelines for Chapters 1-4. Ask the user about the project's "Soul."
- **Structural breach**: If requirements violate "Single Source of Truth," explicitly warn the user before proceeding.

---
*Preserved from Portable Brainvibing Infrastructure*
