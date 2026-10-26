# Architectural Standards & Structural Gates

Provides architectural layer definitions, separation-of-concerns invariants, and concrete blueprint validation.

## 🏛️ 5-Tier Canonical Strata & Structural Gates
Every system architecture must enforce clear boundary separation across the canonical 5 tiers:

1. **Contracts & Immutable Models (`1_contracts`)**:
   - Pure leaf definitions: DTO interfaces, serialization schemas (Zod, Freezed, Pydantic), and database models.
   - **FORBIDDEN**: Importing presentation, state, domain, or infrastructure services.
2. **Pure Domain Logic & Use Cases (`2_domain`)**:
   - Pure entities, value objects, interactors, and business rules.
   - **FORBIDDEN**: Importing UI presentation widgets, state controllers, or network/database drivers.
3. **Persistence Adapters & Services (`3_services`)**:
   - Implements data persistence (SQLite, Drift, Prisma), HTTP/gRPC transport, and device APIs.
   - **FORBIDDEN**: Importing UI widgets or state controllers.
4. **Unidirectional State Orchestration (`4_state`)**:
   - Manages reactive state providers, notifiers, BLoCs, and controllers.
   - **FORBIDDEN**: Direct UI rendering, bypassing domain contracts, or database schema creation inside state handlers.
5. **Presentation & Design System (`5_presentation`)**:
   - Screens, views, widgets, and design system tokens following 5-State Visual Coverage.
   - **FORBIDDEN**: Raw database queries (SQL) or direct HTTP calls bypassing state controllers.

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
