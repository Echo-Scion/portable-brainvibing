# Architectural Standards, Strata Gates & Blueprint Review Pipeline

> **Core Law**: Every system architecture must enforce strict tier separation across the 5 canonical strata, align with the 25-File Golden Ratio Registry in `context/`, and survive the 5-Stage Blueprint Review Pipeline before code generation.

---

## 1. 🏛️ 5-Tier Canonical Strata & Structural Gates

System architecture must enforce unidirectional dependency flow across the canonical 5 tiers:

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
   - **FORBIDDEN**: Direct UI rendering, bypassing domain contracts, or creating DB schemas inside state handlers.
5. **Presentation & Design System (`5_presentation`)**:
   - Screens, views, widgets, and design system tokens following 5-State Visual Coverage.
   - **FORBIDDEN**: Raw database queries (SQL) or direct HTTP calls bypassing state controllers.

---

## 2. 🗺️ 25-File Golden Ratio Context Mapping (DNA Alignment)

Architectural specifications must reside strictly within the 4 Lean Pillars of `context/`—never invent arbitrary subdirectories (e.g. `context/03_Tech/designs/` is strictly prohibited by `verify_agents.py`):

- **High-Level Blueprint**: `context/00_Strategy/BLUEPRINT.md` (Master vision, market problem, peak experience).
- **Technical Architecture**: `context/03_Tech/ARCHITECTURE.md` (Master tech stack, component topology, cut list).
- **Granular Facet Registries** (JIT generated only when needed):
  - Persistence & Tables: `context/03_Tech/DATABASE_AND_STORAGE.md`
  - Endpoints & Schemas: `context/03_Tech/API_AND_CONTRACTS.md`
  - Logic & State Machines: `context/03_Tech/STATE_AND_DOMAIN_LOGIC.md`
  - Authentication & RLS: `context/03_Tech/SECURITY_AND_AUTH.md`
  - Deployment & CI/CD: `context/03_Tech/INFRA_AND_DEVOPS.md`

---

## 3. 🔭 Scope Split (`MacroSpan` vs `BentoSpan`)

To prevent altitude drops (getting lost in loop variables during system review) and split-brain reviews:
- **`MacroSpan` (High-Altitude Architecture)**: Covers component boundaries, contracts, data flow, and failure topologies. Audited against MVC simplicity and YAGNI. Code-level implementation details are forbidden in this span.
- **`BentoSpan` (Execution-Altitude Task Cards)**: Covers exact file targets, symbol signatures, state transformations, and verification assertions. Audited against the Stage 5 Zero-Decision Check.

---

## 4. ⚡ The 5-Stage Blueprint Review Pipeline (5-Stage Architecture Gate)

Before finalizing any technical specification or generating execution task cards:

1. **Stage 1: High-Level Simplicity & Reuse Check (MVC / YAGNI)**:
   - *Context Sufficiency*: Is the core motivation and objective clear?
   - *Root Problem Focus*: Does this solve the root architectural defect rather than patching symptoms?
   - *Codebase Reuse*: Search the repository to reuse existing utilities and services before inventing new ones.
   - *YAGNI & Anti-Weeds*: Reject speculative abstractions and premature optimizations.
2. **Stage 2: Paraphrase & Comprehension Check**:
   - The reviewing agent must paraphrase in its own words: (a) *What this proposes*, and (b) *How the existing system works, per this plan*.
   - If the paraphrase cannot be constructed or is rejected as inaccurate, the plan fails as an automatic 🔴 **Blocker**.
3. **Stage 3: Triad Stress-Test**:
   - Probe failure modes across the Triad: Boundary & Malformed Input, Resource & Concurrency, Silent Failure & Masked Fallback.
4. **Stage 4: Post-Review Bloat Check (CRITICAL ANTI-BLOAT)**:
   - When findings from Stages 2 and 3 are addressed, agents frequently inject defensive bloat, unnecessary wrapper layers, and speculative configurability.
   - Stage 4 re-audits all changes introduced during review, ruthlessly pruning newly added bloat back to Minimum Viable Complexity before code generation.
5. **Stage 5: Zero-Decision Check (Implementation Readiness)**:
   - Verify that zero architectural or design decisions remain for the implementer. All column types, endpoint routes, library choices, and edge-case fallbacks must be predetermined.

---

## 5. 🛠️ Master Blueprint Construction Protocol

**Execution Pipeline**:
1. **Diagnostic Extraction**: Identify core domain state invariants (entities, volumes, timestamp bounds).
2. **Scaffold Directory Topology**: Load `.agents/templates/PROJECT_SCAFFOLD.template.md`.
3. **Define Immutable Domain Models**: Leaf DTOs in `1_contracts` $\to$ pure domain in `2_domain` $\to$ reactive providers in `4_state`.
4. **Structural Verification**: Evaluate plan against the 8 pillars in `references/structural_pillars.md`.

---

## 6. ⚠️ Architectural Breach Resolution

- **Boundary Violation**: If requirements force presentation components to access raw database clients, reject and route through a repository contract in `3_services`.
- **State Ambiguity**: If state exists across multiple competing sources of truth, halt blueprinting until a single authoritative owner is assigned in `4_state`.
