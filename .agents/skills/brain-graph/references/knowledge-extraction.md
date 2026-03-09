---
name: knowledge-extraction
description: IDE Agent workflow for extracting graph triplets (Subject, Predicate, Object) from raw code sources.
activation: Triggered automatically by the [TRIPLET_REQUEST] directive during orion_ops ingest.
---

# Knowledge Graph Extraction & Entity Resolution Workflow

You have been invoked because a recent ingestion operation generated a `[TRIPLET_REQUEST]`.
This directive requires semantic relationships (triplets) and normalized entity definitions to be mapped into the knowledge graph (`orion.db`), providing persistent, structured memory across project sessions.

---

## 1. Dual-Level Graph Architecture

The knowledge graph serves two distinct retrieval tiers:

1. **Low-Level Precision Retrieval (Local Subgraphs)**:
   - Targets specific entities, methods, interface contracts, and direct 1-hop / 2-hop dependencies.
   - Example query: *"What does `SecurityAuditor` call when validating AST nodes?"*
   - Requires: Atomic, unambiguous entity names and explicit predicate verbs.

2. **High-Level Global Synthesis (Community & Theme Clusters)**:
   - Targets overarching subsystems, cross-cutting architectural policies, and data flow pipelines.
   - Example query: *"How does error telemetry propagate from presentation to storage?"*
   - Requires: Consistent entity typing, normalized relationships, and cohesive entity descriptions.

---

## 2. Canonical Entity Typing & Naming Protocol

To prevent graph fragmentation (e.g., fractured duplicate nodes for `AuthService`, `auth_service`, and `authenticationService`), enforce strict normalization:

### 2.1 Entity Type Guidance
Classify every extracted entity into one of these canonical categories:

| Entity Type | Definition & Scope | Example |
| :--- | :--- | :--- |
| **Component** | UI widgets, presentation views, rendering blocks | `NavBar`, `UserProfileCard` |
| **Service** | Domain logic orchestrators, API clients, controllers | `AuthService`, `PaymentGateway` |
| **Interface** | Contracts, abstract base classes, protocol definitions | `RepositoryContract`, `SecurityVisitor` |
| **Schema** | Immutable DTOs, data transfer models, database tables | `UserRecord`, `TransactionPayload` |
| **Config** | Environment variables, project settings, manifest files | `AppConfig`, `SecurityBaseline` |
| **Event** | Domain events, state transitions, messaging payloads | `UserLoggedIn`, `SessionEvicted` |
| **Concept** | Architectural patterns, operational policies, algorithms | `StrictTDD`, `EvidenceQuad` |

### 2.2 Canonical Naming Rules
1. **TitleCase Normalization**: Normalize case-insensitive identifiers into TitleCase (e.g., `TokenRefresher`, not `token_refresher` or `tokenRefresher`).
2. **Strip File Extensions & Syntax**: Never name an entity after its raw filename or syntax punctuation (e.g., use `AuthService`, NOT `auth_service.py` or `<AuthService/>`).
3. **Third-Person Grounding**: Never use pronouns (`this file`, `our service`, `we`, `the script`). Always state the fully qualified entity noun.

---

## 3. Relationship Decomposition & Edge Deduplication

### 3.1 Binary Decomposition of N-ary Relationships
If source text describes an interaction among >2 entities, decompose it into atomic binary pairs:
- *Raw text*: "`AuthService` validates `Credentials` using `TokenEncoder` and writes to `SessionStore`."
- *Decomposed Triplets*:
  1. `AuthService` -> `VALIDATES` -> `Credentials`
  2. `AuthService` -> `USES` -> `TokenEncoder`
  3. `AuthService` -> `WRITES_TO` -> `SessionStore`

### 3.2 Canonical Predicate Verbs
Standardize predicate relationships using uppercase active verbs:
- Structural: `IMPLEMENTS`, `EXTENDS`, `CONTAINS`, `DEPENDS_ON`
- Behavioral: `CALLS`, `DISPATCHES`, `MUTATES`, `VALIDATES`, `EMITS`
- Data Flow: `READS_FROM`, `WRITES_TO`, `TRANSFORMS`, `PRODUCES`

### 3.3 Undirected & Bidirectional Edge Deduplication
- For reciprocal relationships (e.g., `PEERS_WITH`, `EQUIVALENT_TO`), treat edges as undirected.
- Do NOT emit swapped duplicate pairs (`A -> PEERS_WITH -> B` and `B -> PEERS_WITH -> A`). Emit only one canonical pair sorted alphabetically by subject name (`A` -> `PEERS_WITH` -> `B`).

---

## 4. Multi-Source Entity Description Reconciliation

When multiple files mention the same entity, follow this reconciliation loop:
1. **Additive Union**: Combine distinct responsibilities into a single comprehensive description.
2. **Conflict Resolution**: If two files describe conflicting states (e.g., deprecated legacy interface vs modern v2 interface):
   - Explicitly note both perspectives with state markers: `[Current: Uses async dispatch] / [Legacy: Synchronous fallback]`.
   - Never overwrite active production behavior with speculative comments.

---

## 5. Execution Protocol (Handling `[TRIPLET_REQUEST]`)

1. **Read Source Files**: 
   Use an available file-reading tool to scan files listed in the `[TRIPLET_REQUEST]` output.

2. **Extract Semantic Triplets**:
   For each source file, extract 3–5 high-signal relationships adhering to the canonical typing and naming rules above.

3. **Format JSON Array**:
   ```json
   [
     {
       "s": "AuthService",
       "p": "DEPENDS_ON",
       "o": "JwtToken",
       "src": "src/services/auth.py",
       "desc": "Validates inbound user credentials and issues signed JWT bearer tokens."
     },
     {
       "s": "UserController",
       "p": "CALLS",
       "o": "AuthService",
       "src": "src/controllers/user.py",
       "desc": "Invokes authentication verification before granting access to user profile mutations."
     }
   ]
   ```

4. **Inject into Graph**:
   Write the JSON array to `.orion/scratch/triplets.json` using `write_to_file`.
   Then execute the terminal command:
   ```pwsh
   python .agents/scripts/orion.py orion_ops inject_triplets .orion/scratch/triplets.json
   ```

5. **Completion Verification**:
   Verify terminal output reports: `[SUCCESS] Injected X triplets into orion.db.`.
