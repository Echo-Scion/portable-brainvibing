# Architectural Standards & Structural Gates

Provides architectural layer definitions, separation-of-concerns invariants, and concrete blueprint validation.

## 🏛️ Layered Structural Gates
Every system architecture must enforce clear boundary separation:

1. **Domain Invariant Layer (`domain/`)**:
   - Pure entities, value objects, and business rules.
   - **FORBIDDEN**: Importing UI frameworks, database drivers, or HTTP network clients.
2. **Application & State Layer (`application/` or `providers/`)**:
   - Orchestrates workflows, coordinates repositories, manages reactive state.
   - **FORBIDDEN**: Direct DOM/UI manipulation or raw database SQL inside state handlers.
3. **Infrastructure & Data Layer (`infrastructure/` or `repositories/`)**:
   - Implements data persistence, network transport, and device APIs.
   - Adheres strictly to contracts defined in the Domain layer.

## 🛠️ Master Blueprint Construction Protocol
**Scenario**: "I want to build an application for tracking daily water intake."
**Execution Pipeline**:
1. **Diagnostic Extraction**: Identify the core domain state invariants (e.g. daily intake target, logged volumes, timestamp bounds).
2. **Scaffold Directory Topology**: Load `.agents/templates/PROJECT_SCAFFOLD.template.md`.
3. **Define Immutable Domain Models**:
   - Path: `lib/features/hydration/domain/models/intake.dart` -> Define immutable DTO.
   - Path: `lib/features/hydration/presentation/providers/intake_provider.dart` -> Define reactive state manager.
4. **Structural Verification**: Evaluate plan against the 8 pillars in `references/structural_pillars.md`.

## ⚠️ Architectural Breach Resolution
- **Boundary Violation**: If requirements force presentation components to access raw database clients, reject and route through a repository contract.
- **State Ambiguity**: If state exists across multiple competing sources of truth, halt blueprinting until a single authoritative owner is assigned.

