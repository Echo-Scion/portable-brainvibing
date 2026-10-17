# 🏛️ Domain Capability Index & Multi-Discipline Taxonomy Registry

This document serves as the master engineering taxonomy and domain capability registry for the agent ecosystem. It provides a structured, multi-discipline index of proven architectural patterns, negative constraints, and verification protocols across 12 core software disciplines.

---

## 1. Quality Benchmark & Admission Standards

Every capability pattern, skill, or synthesized procedure must satisfy these four fundamental quality gates before adoption:

| Benchmark Dimension | Engineering Requirement | Failure Condition |
| :--- | :--- | :--- |
| **1. Signal-to-Noise Ratio** | Terse, actionable operational steps. Free of conversational fluff, buzzwords, or tautological commentary. | Generic advice, placeholder steps, or marketing filler. |
| **2. Progressive Disclosure** | Strict 3-tier layering: Metadata (<100 tokens), Body (<500 lines), References (loaded on demand). | Monolithic files dumping unneeded domain docs into early context turns. |
| **3. Machine Portability** | Zero absolute paths, user-specific home directory references, or compiled external C++ daemon dependencies. | Path hardcoding (`/Users/foo/`), unportable wheels, or background daemon requirements. |
| **4. Deterministic Verification** | Every domain pattern must pair with a verifiable mechanical command (`Exit Code 0 = Pass`, `Exit Code > 0 = Fail`). | Subjective or unprovable success claims without execution evidence. |

---

## 2. The 12-Discipline Capability Taxonomy

```
DOMAIN CAPABILITY TAXONOMY
├── 01. Systems & Backend Engineering
├── 02. Frontend & Visual Craft
├── 03. Security, Hardening & Static AST
├── 04. DevOps, Release & Infrastructure
├── 05. AI, ML & Graph Engineering
├── 06. Quality Assurance & Testing Discipline
├── 07. Data Integrity & State Architecture
├── 08. API Contracts & Protocol Bridges
├── 09. Meta-Tooling & Agent Orchestration
├── 10. Memory, Compaction & Context Optimization
├── 11. Performance & Algorithmic Scalability
└── 12. Product Lifecycle & SWE Governance
```

---

### Discipline 01: Systems & Backend Engineering
- **Domain Scope**: Scalable server applications, asynchronous job queues, database connectivity, and resilient distributed subsystems.
- **Core Responsibilities**:
  - Implement idempotent request handling with idempotency keys.
  - Enforce bounded connection pooling and timeout budgets on all external calls.
  - Design transactional boundary commits (Unit of Work pattern).
  - Structure structured logging with trace IDs and context propagation.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER execute unbounded queries (`SELECT *`) without pagination and limit clauses.
  - NEVER swallow connection teardown errors or leave dangling sockets.
  - NEVER perform blocking network I/O inside tight CPU loops or transaction locks.
- **Standard Verification Protocol**:
  ```bash
  python -m unittest discover tests/backend/ -v
  ```

---

### Discipline 02: Frontend & Visual Craft
- **Domain Scope**: Restrained ergonomic user interfaces, design token governance, micro-interactions, and accessibility (a11y).
- **Core Responsibilities**:
  - Enforce mathematical 8pt spatial rhythm (`space-1` through `space-8`) and locked design tokens.
  - Guarantee 8 interaction states: Default, Hover, Active, Focus-Visible, Disabled, Loading, Empty, and Error.
  - Ensure strict WCAG 2.1 AA luminance contrast ratios (4.5:1 text, 3:1 graphical elements).
  - Structure semantic HTML with proper landmark roles, ARIA attributes, and keyboard navigation.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER invent arbitrary inline hex colors, loose pixel margins, or saturated gradient glows.
  - NEVER draw synthetic OS browser chrome, fake mobile bezels, or artificial terminal wrappers.
  - NEVER use italicized emphasis words inside display headings (`<h1>` through `<h3>`).
- **Standard Verification Protocol**:
  ```bash
  python .agents/evals/audit_aesthetics.py --dir src/
  ```

---

### Discipline 03: Security, Hardening & Static AST
- **Domain Scope**: Offensive security auditing, static code analysis, vulnerability remediation, and secret containment.
- **Core Responsibilities**:
  - Inspect AST syntax trees for dangerous calls (`eval`, `exec`, `pty.spawn`, `posix_spawn`).
  - Scan for 22+ credential harvesting keys (`AWS_SECRET_ACCESS_KEY`, `DATABASE_URL`, `TOKEN`).
  - Prevent insecure deserialization (`pickle.loads`, `yaml.unsafe_load`, `marshal.loads`).
  - Detect Unicode Trojan Source attacks (Directional formatting characters, BiDi overrides).
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER concatenate raw user strings into SQL queries or shell execution strings.
  - NEVER commit credentials, private keys, or API tokens into source control.
  - NEVER rely on client-side authentication checks without server-side validation.
- **Standard Verification Protocol**:
  ```bash
  python .agents/scripts/orion.py scan security .agents
  ```

---

### Discipline 04: DevOps, Release & Infrastructure
- **Domain Scope**: Continuous integration, hermetic build environments, reproducible deployments, and configuration management.
- **Core Responsibilities**:
  - Enforce declarative, deterministic infrastructure configurations.
  - Structure multi-stage isolated builds with minimal runtime image footprint.
  - Verify zero-downtime rolling update mechanics and atomic rollback triggers.
  - Maintain clean separation between static build assets and dynamic runtime configuration.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER run containers or server processes with root permissions.
  - NEVER mutate running production infrastructure via ad-hoc interactive SSH commands.
  - NEVER deploy without clean git working tree state and verified cryptographic hashes.
- **Standard Verification Protocol**:
  ```bash
  git status --porcelain && python .agents/scripts/orion.py verify_agents
  ```

---

### Discipline 05: AI, ML & Graph Engineering
- **Domain Scope**: Retrieval-Augmented Generation (RAG), GraphRAG knowledge bases, deterministic prompt construction, and model evaluation.
- **Core Responsibilities**:
  - Design semantic knowledge graphs with typed triplets `(Subject, Predicate, Object)`.
  - Maintain bidirectional entity linking with strict contradiction detection.
  - Structure evaluation harnesses testing for hallucinations, boundary bypasses, and drift.
  - Ground LLM outputs using explicit context injection and strict schema extraction.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER pass unvalidated LLM output directly to raw shell executors or database write queries.
  - NEVER rely on model internal parameters for changing project business rules.
  - NEVER leak internal prompt templates or system directives in customer-facing error traces.
- **Standard Verification Protocol**:
  ```bash
  python .agents/scripts/orion.py brain sync "verification"
  ```

---

### Discipline 06: Quality Assurance & Testing Discipline
- **Domain Scope**: Test-Driven Development (TDD), Doubt-Driven Development (DDD), property-based testing, and regression suites.
- **Core Responsibilities**:
  - Execute strict Red-Green-Refactor cycles: verify failing test (Exit Code > 0) BEFORE writing code.
  - Apply 4-phase systematic debugging: Root cause investigation -> Pattern analysis -> Single hypothesis -> Surgical fix.
  - Enforce 3-attempt circuit breaker: halt immediately upon 3 consecutive test failures to prevent thrashing.
  - Implement adversarial doubt probes targeting unstated assumptions, concurrency, and error boundaries.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER claim success without verifiable execution logs showing Exit Code 0.
  - NEVER write implementation code before a verified failing test reproduces the bug.
  - NEVER bundle refactoring, formatting cleanup, or speculative tweaks during bug fixes.
- **Standard Verification Protocol**:
  ```bash
  python -m pytest --maxfail=1 -q
  ```

---

### Discipline 07: Data Integrity & State Architecture
- **Domain Scope**: Immutable state modeling, transactional integrity, Data Transfer Objects (DTOs), and transformation pipelines.
- **Core Responsibilities**:
  - Design data structures with immutability by default (frozen dataclasses, read-only types).
  - Separate external transport models (DTOs) from internal domain entities.
  - Structure unidirectional state flow with explicit action dispatch and pure reducers.
  - Validate all data at runtime ingress boundaries using strict schemas.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER perform in-place mutation of shared memory state across concurrent tasks.
  - NEVER allow implicit type coercion across data transformation boundaries.
  - NEVER bypass DTO validation when parsing external webhook or socket payloads.
- **Standard Verification Protocol**:
  ```bash
  python -m unittest tests/data/
  ```

---

### Discipline 08: API Contracts & Protocol Bridges
- **Domain Scope**: Specification-First Architecture, OpenAPI/JSON Schema definitions, RPC bridges, and Model Context Protocol (MCP).
- **Core Responsibilities**:
  - Author formal specifications (`api-spec.json`, OpenAPI) before generating implementation stubs.
  - Enforce JSON-RPC 2.0 contracts for tool call protocols (`stdio` and HTTP transport).
  - Guarantee backward compatibility with explicit semantic versioning (`v1`, `v2`).
  - Return standardized error envelopes with machine-readable error codes and safe descriptions.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER introduce breaking schema modifications without deprecation notices.
  - NEVER return raw internal stack traces or database schema errors in client API responses.
  - NEVER emit untyped JSON responses with unpredictable dynamic key structures.
- **Standard Verification Protocol**:
  ```bash
  python -c "import json; [json.loads(open(f).read()) for f in ['api-spec.json'] if __import__('os').path.exists(f)]"
  ```

---

### Discipline 09: Meta-Tooling & Agent Orchestration
- **Domain Scope**: Skill authoring engines, progressive disclosure loading, multi-agent delegation, and operational discernment.
- **Core Responsibilities**:
  - Author modular skills following the 3-tier progressive context disclosure hierarchy.
  - Enforce Operational Discernment Thresholds: autonomous action bias vs. mandatory human alignment gates.
  - Dispatch subagent worker tasks with strict boundary specifications and non-colliding worktrees.
  - Apply the Principle of Lack of Surprise: zero hidden side-effects or obfuscated scripts.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER allow skills to exceed 500 lines in their primary `SKILL.md` body.
  - NEVER ask the user trivial questions for routine, non-destructive, reversible diagnostics.
  - NEVER execute destructive actions (dropping tables, force push, uncommitted file deletion) without explicit human confirmation.
- **Standard Verification Protocol**:
  ```bash
  python .agents/scripts/orion.py verify_agents
  ```

---

### Discipline 10: Memory, Compaction & Context Optimization
- **Domain Scope**: Episodic memory distillation, session handoff state, transcript parsing, and token economics.
- **Core Responsibilities**:
  - Parse multi-turn conversation transcripts using pure Python standard library to extract high-signal observations.
  - Tag episodic observations with standardized prefixes: `[decision]`, `[bugfix]`, `[feature]`, `[refactor]`, `[discovery]`, `[security_alert]`, `[sensitive]`, `[open_loop]`.
  - Compile session pulses, milestone syntheses, and epoch consolidations based on project activity.
  - Enforce context budget limits by offloading stale state to persistent markdown handoffs.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER rely on heavy background daemon servers (Docker containers, cloud vector stores) for local memory persistence.
  - NEVER lose active work context across session boundaries; always write `.orion/working/handoff.md`.
  - NEVER bloat root system prompts with unbounded historical transcripts.
- **Standard Verification Protocol**:
  ```bash
  python .agents/scripts/orion.py consolidate session
  ```

---

### Discipline 11: Performance & Algorithmic Scalability
- **Domain Scope**: Algorithmic complexity bounds, memory footprint control, latency minimization, and token budgeting.
- **Core Responsibilities**:
  - Audit Big-O computational complexity to prevent quadratic loops (`O(N^2)`) on large collections.
  - Minimize token consumption using Lessword mode and targeted AST grep searches before full file reads.
  - Implement memoization and caching with bounded LRU eviction policies.
  - Profile bottleneck operations with deterministic wall-clock and CPU measurement hooks.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER perform repeated full-directory scans inside tight recursive loops.
  - NEVER leave unbounded in-memory caches without TTL or max-size constraints.
  - NEVER consume premium token tiers for simple, low-entropy formatting or lint tasks.
- **Standard Verification Protocol**:
  ```bash
  python -m timeit -s "import time" "time.sleep(0.001)"
  ```

---

### Discipline 12: Product Lifecycle & SWE Governance
- **Domain Scope**: Architecture Decision Records (ADRs), Specification-Driven Development, feature sunsetting, and code hygiene.
- **Core Responsibilities**:
  - Document every major structural pivot in standard Architecture Decision Records (`.agents/templates/ADR.template.md`).
  - Execute phased feature deprecation: Announce -> Soft Deprecate -> Hard Deprecate -> Remove.
  - Maintain code comment hygiene: explain invariants, non-obvious algorithms, and edge cases (no tautological syntax restatement).
  - Synchronize workspace documentation with actual code reality on every session milestone.
- **Key Negative Constraints (Anti-Patterns)**:
  - NEVER delete deprecated APIs in a single breaking release without a transition cycle.
  - NEVER insert decorative ASCII banners, boxes, or decorative emoji into source code files.
  - NEVER claim feature completion without updating corresponding architecture documentation.
- **Standard Verification Protocol**:
  ```bash
  git diff --check
  ```

---

## 3. Just-In-Time (JIT) Skill Synthesis Protocol

When an agent encounters a novel or highly specialized technical domain not directly covered by an installed skill in `.agents/skills/`:

1. **Locate Discipline Archetype**: Match the user's intent to one of the 12 disciplines above.
2. **Inherit Constraints**: Adopt the discipline's Core Responsibilities and Negative Constraints.
3. **Establish Verification Command**: Define the exact mechanical command (`Exit Code 0`) that will prove correctness before writing code.
4. **Author Ephemeral Scaffold**: If the domain recurs >3 times in a session, trigger `/self-evolve` to promote the synthesized pattern into a permanent skill using the Skill Creator Engine.
