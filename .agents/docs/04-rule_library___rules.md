# VOLUME IV: RULE LIBRARY (`rules/`) — Behavioral Standards & Guardrails

---

## Chapter 10: Complete Rule Catalog & Behavioral Standards

The `rules/` directory houses the immutable constitution of the `.agents` ecosystem. These rules establish deterministic behavioral constraints, preventing model drift, hallucinated passes, token waste, and destructive operations.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Rule Precedence Hierarchy                         │
│                                                                        │
│   1. security-guardrails.md     (Highest Priority — Safety & Secrets)  │
│   2. Root Instruction/AGENTS.md (Supreme Operational Constitution: §1) │
│   3. tier-execution-protocol.md (Model Capability & Resource Routing)  │
│   4. Domain & Task Rules        (Performance, Operations, FSM, etc.)   │
│   5. Skill-Specific Directives  (Lowest Priority — Domain Personas)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 10.1. `AGENTS.md § 1` (Core Guardrails — Master BIOS Constitution)
The primary behavioral constitution enforced natively across all sessions via root `AGENTS.md § 1`:
- **Unified Response Protocol (§1)**: Enforces standardized footer format across turn types.
- **Evidence Mandate (§1)**: Never claim success without verifiable proof. `Exit Code 0` is required, but agents must verify assertions, test counts, and state transitions.
- **Circuit Breaker (§4)**: Stop calling tools if any tool or test fails 3 times consecutively. Output root-cause error analysis and request human intervention.
- **No Raw CLI Patching**: Forbids modifying files via terminal scripts (`python -c`, `sed`, `awk`). All edits must route through native IDE editing tools.
- **AST Expansion Protocol**: Before writing a fix for code identified via search, the agent must view the actual implementation block.
- **Anti-Affirmation (Triad Threat Probe)**: Proactively probe proposals for Boundary/Malformed input, Resource/Concurrency leaks, and Silent Failure/Masked fallbacks.
- **Surgical Diff Mandate**: Modify only code strictly relevant to the prompt.
- **Simplicity First (YAGNI)**: Minimum code to solve the immediate problem; zero speculative abstractions.

---

### 10.2. `security-guardrails.md` (Offensive Security)
Offensive security standards and protective verification gates:
- **Pre-Commit Secrets Scanning**: Pre-commit pattern matching detecting OpenAI keys (`sk-*`), `SUPABASE_SERVICE_ROLE_KEY`, AWS credentials, and PEM private keys.
- **Prompt Injection Defense**: Deterministic rejection of injection attempts ("Ignore all previous instructions").
- **Least Privilege Access**: Read-only access by default; explicit confirmation required for privilege escalation.
- **Destructive Command Gate**: Commands executing recursive deletions (`rm -rf`), table drops (`DROP TABLE`), or unconditioned deletes require explicit confirmation.
- **Offensive Audit Protocol**: Enforces mutation testing, audits against empty catch blocks (`catch (e) {}`), and mandates vertical slice security audits (Route → Controller → Service → Repository).

---

### 10.3. `tier-execution-protocol.md` (Resource Routing)
Allocates tasks to model tiers based on computational complexity:

| Tier | Profile | Permitted Scope | Constraints |
|:---|:---|:---|:---|
| **BUDGET** | Flash / Haiku | 1 file fix, indexing, batch runs | Bento-Box Law: Max 1 file per iteration; AST skeleton first |
| **STANDARD** | Sonnet / Pro | Feature builds, TDD, UI, refactors | 3–5 surgical reads; Edge-Case Matrix required |
| **PREMIUM** | Opus / Thinking | Architecture, multi-system debug | Unlimited justified reads; Adversarial Twin required |

- **Bento-Box Law**: BUDGET models are forbidden from multitasking across multiple files simultaneously.
- **Auto-Abort (Downgrade Guard)**: If the active model class is weaker than required by the task tier, the agent must abort (`[ABORT: TIER MISMATCH]`).

---

### 10.4. `development-operations.md` (Development SOPs)
Operational procedures for codebase modifications:
- **Conventional Commits**: Enforces standardized commit format (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`).
- **Save Point Protocol**: Atomic commits after every verified milestone.
- **AutoHarness Protocol**: Creation of verification scripts (Action-Verifier, Action-Filter, Policy) for non-trivial operations.
- **Context Management**: 3-layer context hierarchy (Global → Project → App) and Skeleton-First reading law.

---

### 10.5. `performance-optimization.md` (Bolt Protocol)
Optimization operations must pass three gates before execution:
1. **Measurable?** Baseline and post-fix metrics must be measurable; otherwise cancel.
2. **Readable?** Does the optimization preserve architectural readability?
3. **Scope < 50 lines?** Does the change remain compact and contained?
- **500-Line Refactor Decision Tree**: Modules exceeding 500 lines are flagged for modular decomposition.

---

### 10.6. `memory-hygiene.md` (Context Compaction)
Defines mechanical eligibility criteria for compressing knowledge in `.orion/`:
- Tracks `access_count`, `importance`, and node age in `pages`.
- Preserves frequently accessed nodes and records younger than 14 days.

---

### 10.7. `contradiction-protocol.md` (Knowledge Graph Integrity)
Detects colliding predicates in semantic triplets during ingestion:
- Writes collisions to the `contradictions` SQL table.
- Resolves conflicts by adjusting edge confidence scores (0.0 to 1.0) rather than deleting historical nodes.

---

### 10.8. `prompting-patterns.md` (Instruction Density)
Framing standards for complex engineering tasks:
- High-density instruction formatting.
- 5-State UI validation requirements (Empty, Loading, Success, Error, Offline).
- Elimination of conversational preambles.

---

### 10.9. `fsm-protocol.md` (Formal State Machine)
Enforces separation between static environment data (`context.json`) and active execution state (`execution_state.json`):
- Atomic superstep phase transitions.
- Automatic recovery parameter injection on unexpected IDE restart.

---

### 10.10. `prerequisites.md` (Graceful Fallback Matrix)
Defines architectural fallbacks across the Four (4) Anchored Pillars:

| Pillar / Prerequisite | Primary Engine | Graceful Fallback |
|:---|:---|:---|
| **Pillar 1: Cognitive Kernel** | Python 3.10+ Stdlib | Pure stdlib scripts (`ast`, `sqlite3`, `urllib`) |
| **Pillar 2: Terminal / Code** | Cargo Rust (`rtk` + `sg`) | Python `ast` parser & surgical `view_file` |
| **Pillar 3: Neural Coprocessor** | Ollama (`nomic-embed`) | SQLite3 FTS5 Porter BM25 lexical search |
| **Pillar 4: Static Runtime** | Bun Static Engine (`bun`) | Python stdio bridge or host test runner |

---

### 10.11. `antigravity-rtk-rules.md` (Terminal Proxy Routing)
Operational decision tree governing RTK command execution:
- Commands producing large text output (`git log`, `find`, `test`) must route through `rtk <cmd>`.
- Interactive or raw JSON-dependent commands bypass RTK via `rtk proxy <cmd>` or raw execution.

---

### 10.12. `prose-authenticity.md` (Anti-Slop Writing Standard)
Standards for human-facing documentation, README files, commit messages, and PR descriptions:
- Eliminates 54 AI structural habits and buzzword clusters (*delve, tapestry, pivotal, holistic, foster*).
- Bans binary contrast reversals (*"Not because X, but because Y"*).
- Corporate jargon translation table.

---

### 10.13. `four-pillars-architecture.md` (Sovereign Specification)
Defines the zero-pip mandate, zero-daemon architecture, and operational integration across Python, Cargo Rust, Ollama, and Bun.

---

### 10.14. `obsidian-interop.md` (Obsidian Vault & Wikilink Graph)
Defines local markdown graph interoperability, wikilink formatting (`[[link]]`), and Obsidian Vault integration standards without polluting authored source hierarchies.

---

### 10.15. `RULES_INDEX.md` & `ast/security_rules.yml`
- `RULES_INDEX.md`: Machine-readable registry parsed by NanoBrain during JIT routing.
- `ast/security_rules.yml`: CST rule configurations used by `core/security.py` and `ast-grep` to identify AST-level vulnerabilities.
