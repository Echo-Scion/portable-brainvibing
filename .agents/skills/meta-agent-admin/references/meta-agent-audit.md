# 🛡️ Meta-Agent & Foundation Infrastructure Audit Protocol (v2.0 — Calibrated & Convergent)

> **Purpose**: Algorithmic self-audit protocol for the `.agents/` ecosystem, CLI tools, hooks, local graph databases, templates, and agentic workflows. Codified from the Calibrated Principal Systems, Anti-Cosplay Architecture & Deterministic Zero-Trust Scoring Audit (v2.0).

---

## 0. Pre-Audit Mechanical Gates (Run First)

Before performing any static or architectural analysis, execute these commands via terminal:
```bash
python .agents/scripts/orion.py verify
python .agents/scripts/orion.py preflight
python .agents/scripts/orion.py instruction-lint --strict
pytest .agents/scripts/tests
```
- **Rule**: If any gate fails (Exit Code > 0), the Agent MUST halt immediately and report findings as CRITICAL regressions.

---

## 1. Epistemology, Calibration & Anti-Moving-Goalposts Clauses (Non-Negotiable)

The Agent MUST apply a calibrated, evidence-bound auditor posture to prevent unbounded fault-finding loops:

1. **Empirical AST Grounding**: Verify claims in `README.md`, `docs/`, and docstrings against AST implementations and active end-to-end execution paths.
2. **Zero-Tunnel Vision (End-to-End Call Graph Tracing)**: Trace SQLite tables, classes, functions, constants, and CLI subcommands from producer to consumer. Unconsumed items accessed only in tests are classified as dead bloat.
3. **Anti-Frankenstein Mandate (SSOT)**: Hunt genuine duplicate subsystems across modules while respecting intentional defensive fallbacks.
4. **No Hand-Waving Scores (Strict Ledger Math)**: Estimated or subjective scoring is forbidden. Every point deduction MUST cite `file:line`, prove a material defect, and map to the exact tariff in § 2.
5. **Calibration Clause 1 — Materiality Threshold (Ambang Materialitas)**:
   - The Agent MUST deduct points ONLY when a finding is proven to cause: (a) runtime failure (`Exception`/`Crash`), (b) data or state corruption, (c) an exploitable security vulnerability, or (d) a primary feature that is completely non-functional (empty stub).
   - The Agent MUST NOT deduct points for minor stylistic variations, defensive fallbacks inside `except ImportError:` blocks, or self-contained helpers in single-file hooks (`pre-agent-wake.py`).
6. **Calibration Clause 2 — Intentional Architecture Exemption (Pengecualian Desain Sengaja)**:
   - Fallback functions inside `except ImportError:` blocks and standalone hook scripts (`hooks/`) that include local `_atomic_write_text` or `_log_telemetry` for process isolation are NOT DRY violations (`[DUPLICATE SUBSYSTEM]`).
   - Retrieval-only modes (without an active LLM generator) that evaluate relevance are NOT `[SHALLOW SHIM]` when documented explicitly.
7. **Calibration Clause 3 — Convergence Guarantee (Jaminan Konvergensi 100/100)**:
   - The Agent is NOT evaluated by the quantity of microscopic faults it invents. When all 8 Mechanical Gates (`verify_agents.py`, `instruction-lint`, `context-lint`, `scan security`, `pytest`/`unittest`) pass with `Exit Code 0` factually in the AST and zero active runtime or mathematical bugs exist, the Agent MUST award **100/100**.

---

## 2. Deterministic 100-Point Locked Ledger (v2.0)

Scoring starts at **100 Points** across 7 Audit Vectors. Deduct points mechanically ONLY for findings that cross the **Materiality Threshold (§ 1.5)**. Minimum score per vector is `0`.

### Vector A: Algorithmic Honesty & Anti-Cosplay (Max 20 Pts)
Compares claims in `README.md`, `docs/`, and docstrings against actual code AST implementations.
- **Deduction Tariffs**:
  - `-10 Pts` / incident `[CRITICAL COSPLAY]`: Claiming advanced algorithms or subsystems (e.g., Shannon Surprisal `fts5vocab`, DSPy Compiler, Tree-sitter CST, Hermetic OS Sandbox, Neural Cross-Encoder) that resolve to `pass`, hardcoded lists, naive substring matching, or unisolated commands.
  - `-5 Pts` / incident `[SHALLOW SHIM]`: Functions claiming structural/AST processing that rely on fragile shallow regexes causing runtime false positives/negatives, or ignore critical arguments (e.g., accepting `preserve_code=True` or `db_path` but ignoring them). *(Exemption: Documented retrieval-only modes are NOT shallow shims).*
  - `-3 Pts` / incident `[DOC-CODE DRIFT]`: Material discrepancies between documented behavior and actual code runtime, or broken references to non-existent files.
- **Criteria for 20/20**:
  1. All claims in documentation have equivalent mathematical or structural implementations in code.
  2. Technical limits (e.g., ephemeral workspace runner vs kernel sandbox) are stated explicitly in docstrings and documentation.
  3. 0 ignored function parameters and 0 references to missing files.

### Vector B: Architectural Cohesion & Anti-Frankenstein / DRY (Max 15 Pts)
Detects material logic overlap, function duplication, and redundant schemas from multi-repo merges.
- **Deduction Tariffs**:
  - `-6 Pts` / incident `[DUPLICATE SUBSYSTEM]`: Multiple primary classes, functions, or tables in different modules performing identical core tasks outside of defensive import fallbacks. *(Exemption: `except ImportError:` fallbacks and standalone `hooks/` isolation helpers are exempt).*
  - `-5 Pts` / incident `[REDUNDANT I/O OR DOUBLE-WRITE]`: Writing identical data twice to different tables, or duplicating an open database into `:memory:` to run an existing algorithm.
  - `-2 Pts` / incident `[DEAD SYMBOL / CONSTANT]`: Orphaned functions, global variables, or regexes retained in a file after logic migration.
- **Criteria for 15/15**:
  1. Single Source of Truth (SSOT) for canonical primitives in `core/`.
  2. Modules import shared primitives from `core/` (with optional `except ImportError:` resilience permitted).
  3. 0 double-writes to SQLite and 0 duplicate `:memory:` replications.

### Vector C: Execution Pipeline Cleanliness & Zero Dead Bloat (Max 15 Pts)
Tracks Producer-Consumer links across database tables, classes, and CLI commands.
- **Deduction Tariffs**:
  - `-5 Pts` / incident `[ORPHANED TABLE / SCHEMA]`: SQLite tables or columns created via `CREATE TABLE` that are never written to or read by active CLI or hook workflows.
  - `-4 Pts` / incident `[GHOST CLI DISPATCH]`: CLI subcommands or flags registered in the dispatcher that invoke missing modules, raise `NotImplementedError`, or fail at runtime.
  - `-3 Pts` / incident `[DEAD SUBSYSTEM / HARNESS]`: Utility files unreferenced by any active entrypoint, hook, verifier, or evaluation suite.
- **Criteria for 15/15**:
  1. All registered SQLite tables and columns have active read-write pipelines.
  2. All CLI subcommands and flags in `orion.py` map to active, working functions.
  3. All helper scripts in `.agents/scripts/` have active consumers.

### Vector D: Mathematical & Algorithmic Integrity (Max 15 Pts)
Verifies formal correctness of mathematical formulas and data structures.
- **Deduction Tariffs**:
  - `-7 Pts` / incident `[MATH / FORMULA BUG]`: Formula errors (e.g., missing $2m$ denominator in Louvain modularity, division by zero without epsilon, inverted or unscaled IDF calculations, or surprisal formulas violating probability laws).
  - `-4 Pts` / incident `[ALGORITHMIC COMPLEXITY REGRESSION]`: Algorithmic regressions where an expected $O(V+E)$ or $O(N)$ operation scales to $O(N^2)$ due to expensive un-cached computations in per-item loops.
  - `-2 Pts` / incident `[INCORRECT EDGE BOUNDARY]`: Off-by-one errors or line-slicing boundaries that omit the final line or record.
- **Criteria for 15/15**:
  1. Mathematical implementations (Louvain Modularity, Shannon Surprisal, TF-IDF, Cosine Similarity) match academic specifications.
  2. Zero computational complexity regressions in graph or traversal loops.
  3. Symbol and skeleton parsers cover file end boundaries accurately.

### Vector E: Concurrency Resilience & Zero-State Sabotage (Max 15 Pts)
Assesses background processes, atomic I/O operations, and preservation of user workspace state.
- **Deduction Tariffs**:
  - `-8 Pts` / incident `[DESTRUCTIVE WORKING TREE SABOTAGE]`: Hooks or scripts unilaterally altering git working state (e.g., silent `git stash`, unbacked `git checkout -- .`, or `git clean -f`).
  - `-5 Pts` / incident `[RACE CONDITION / LOCK LEAK]`: Lockfiles lacking process liveness verification (PID check), causing zombie deadlocks upon unexpected process termination.
  - `-3 Pts` / incident `[NON-ATOMIC FILE WRITE]`: Direct overwrites of critical state files in primary execution paths without atomic patterns (`.tmp.{pid}.{uuid}` with `os.replace`).
- **Criteria for 15/15**:
  1. Zero destructive manipulation of git working trees; hooks inspect or warn without overwriting uncommitted code.
  2. Concurrency lockfiles include active PID checks and stale lock reclamation.
  3. Runtime state persistence uses atomic temporary file substitution.

### Vector F: Instruction Language Quality & Agentic Safety (Max 10 Pts)
Validates agent instructions against deterministic quality and AST security standards.
- **Deduction Tariffs**:
  - `-4 Pts` / incident `[FUZZY INSTRUCTION / COLD DRIFT]`: Systemic failure of `instruction-lint --strict` due to ambiguous directives lacking observable acceptance criteria or explicit modality (`MUST`/`MAY`).
  - `-3 Pts` / incident `[AST VULNERABILITY / INJECTION]`: Exploitable security vulnerabilities allowing shell command injection or unsafe deserialization.
  - `-2 Pts` / incident `[SILENT EXCEPTION SWALLOW]`: Unhandled `except Exception: pass` blocks in core execution paths lacking telemetry logging or error context.
- **Criteria for 10/10**:
  1. Rules and skills pass `instruction-lint --strict` with 0 errors and 0 warnings.
  2. Zero active AST security vulnerabilities detected by `orion.py scan security`.
  3. Caught exceptions in primary execution paths record structured telemetry.

### Vector G: Operational Ergonomics, Storage SLA & Frontier Developer Experience (Max 10 Pts)
Evaluates real-world runtime overhead, negative storage bloat, cross-shell portability, and cognitive burden.
- **Deduction Tariffs**:
  - `-5 Pts` / incident `[REDUNDANT STORAGE / RUNAWAY BLOAT]`: Generating redundant mirror files (e.g. raw markdown notes mirroring SQLite tables) or `.orion/` storage exceeding the 50-file lean ceiling without automated garbage collection.
  - `-3 Pts` / incident `[SHELL COMPATIBILITY BREAK]`: Chained shell commands (e.g., `&&` in quickstarts or deployment scripts) that cause fatal syntax crashes in native Windows PowerShell.
  - `-2 Pts` / incident `[PROGRESSIVE DISCLOSURE VIOLATION]`: Rules or skills forcing upfront recursive reading of secondary references/canons before primary task execution, exhausting agent context tokens.
- **Criteria for 10/10**:
  1. Active `.orion/` storage contains $\le 50$ files with zero redundant vault mirror directories.
  2. Documentation quickstarts run cleanly across Windows PowerShell, CMD, Bash, and Zsh without `&&` chaining syntax failures.
  3. Skills strictly follow Antigravity Progressive Disclosure with secondary references loaded only on-demand.

---

### Hard Score Ceilings & Convergence Guarantee
- If any material finding incurs `[CRITICAL COSPLAY]` or `[DESTRUCTIVE STATE]`, the total score MUST NOT exceed **60/100**.
- If any material finding incurs `[MATH BUG]` or `[RACE CONDITION]`, the total score MUST NOT exceed **80/100**.
- **Anti-Cliff Convergence Rule**: Stylistic observations, intentional `except ImportError:` fallbacks, and self-contained hook helpers carry **0 Pts penalty** and MUST NOT trigger any score cap. When all Mechanical Gates pass with `Exit Code 0` and zero material runtime/mathematical defects exist across Vectors A–G, the final score MUST be **100/100**.

---

## 3. The 14 Core Infrastructure Audit Vectors

When auditing the agent infrastructure, the Agent MUST evaluate code against these 14 vectors (subject to the Materiality Threshold and Intentional Architecture Exemptions in § 1):

### Vector 1: Regression Invariants
- Verify that historical bug fixes remain intact.
- Ensure automated test harnesses and verifiers remain active.

### Vector 2: Hooks & Concurrency Safety
- Background hooks MUST verify PID liveness using `os.kill(pid, 0)` or equivalent process table checks.
- Omni-Buffer (`context.json`) MUST reject data older than 5 minutes (`300,000 ms`).
- Hooks MUST avoid recursive self-invocation loops.

### Vector 3: Ingest, Linkify & Graph Integrity
- Regex substitutions in `commands/reflexion.py` MUST escape special characters (`[`, `]`, `(`, `)`) to prevent wikilink corruption.
- SQLite FTS5 synchronization routines MUST maintain consistency between `pages` and `pages_fts`.
- Edge deletion MUST NOT cascade into deleting referenced shared entity nodes.

### Vector 4: Verifiers & Security Harnesses
- Verifiers MUST use `os.path.normpath` and relative paths, avoiding unvalidated basename fallbacks.
- Verifiers MUST return non-zero exit codes on structural failures.
- Preflight audits MUST prevent secrets, API keys, or private `.env` files from repository tracking.

### Vector 5: Database Schema & CLI Runtime
- Schema migrations MUST handle missing columns automatically in `pages` and `edges`.
- CLI entrypoints MUST configure UTF-8 stdout/stderr streams on Windows platforms.

### Vector 6: Hub-Spoke Sync & Templates
- `push-upstream` MUST check placeholder sets (`{{...}}`) to prevent overwriting hub templates with spoke-resolved assets unless forced.
- Path resolution in `foundation.py` MUST resolve to `.agents/`.
- Template deployments MUST provide defaults for all standard variables.
- Seed routines MUST instantiate all 4 Lean Pillar anchors (`BLUEPRINT.md`, `ROADMAP.md`, `STYLE_GUIDE.md`, `ARCHITECTURE.md`).

### Vector 7: DevSecOps Scripts & CLI Dispatchers
- Every CLI subcommand in `orion.py` MUST map to an imported, callable handler.
- Scripts MUST trap operational errors and exit with code 1, emitting diagnostic logs.

### Vector 8: Rules, Contradictions & Token Economics
- Active rules MUST NOT contain conflicting directives.
- File-reading routines MUST inspect bounded ranges instead of reading large files sequentially.
- Direct CLI string replacements (`sed`, `awk`, `python -c`) on source files are forbidden.

### Vector 9: Skills & Workflows Integrity
- JIT routing targets in `AGENTS.md §4`, `AGENTS_INDEX.md`, and `SKILL.md` MUST exist on disk.
- Skill files MUST supply valid YAML frontmatter with `name` and `description`.
- Workflow routines MUST remain idempotent across repeated runs.

### Vector 10: Darwinian Evolution & Genome Integrity
- Upstream synchronization of `.genome.json` MUST perform a set union of evolved assets and take the maximum evolution count.
- Consumer project assets MUST NOT leak into foundation genome files.

### Vector 11: Semantic Fact-Checking & Anti-Hallucination
- Documentation MUST NOT claim third-party libraries or research architectures unless implemented in codebase AST.
- Multi-environment claims MUST be grounded in verifiable test telemetry.
- Documented CLI commands MUST exist as registered subcommands.

### Vector 12: End-to-End Pipeline Cohesion
- SQLite tables and columns MUST have active producer and consumer execution paths.
- Graph relations in `edges` MUST be traversed during knowledge retrieval.

### Vector 13: Version Synchronization & Release Harmonization
- `VERSION` MUST match across `CHANGELOG.md`, `README.md`, `AGENTS.md`, and configuration rules.
- Verification scripts MUST enforce version consistency before release.

### Vector 14: Multi-System Matrix & Severity Scoring
Classify material findings according to four severity tiers:
- **CRITICAL**: Data loss, infinite loops, template pollution, core crash (`NameError`/`Exception`), ungrounded external dependencies.
- **HIGH**: Broken routing targets, unvalidated path fallbacks, silent failure masking in primary logic, schema drift, ghost pipelines, version drift.
- **MEDIUM**: Stream encoding errors, fragile relative paths, unmapped template variables.
- **LOW**: Non-penalized informational notes (0 Pts deduction).

---

## 4. Mandatory Reporting Format (Phase-by-Phase Actionable Remediation Plan)

When an audit is executed, the Agent MUST deliver the report using this exact structure to ensure machine-executable clarity:

### 1. TABEL BUKU BESAR PENILAIAN (LEDGER MATH)
A structured table showing:
| Vektor Audit | Bobot Maksimal | Penalti Material Terbukti | Skor Akhir | Status |
| :--- | :---: | :---: | :---: | :---: |
| Vektor A: Kejujuran Algoritmik & Anti-Cosplay | 20 | 0 | 20 | PASS |
| Vektor B: Kohesi Arsitektur & Anti-Frankenstein | 15 | 0 | 15 | PASS |
| Vektor C: Kebersihan Pipa Eksekusi & Zero Dead Bloat | 15 | 0 | 15 | PASS |
| Vektor D: Integritas Matematis & Algoritmik | 15 | 0 | 15 | PASS |
| Vektor E: Ketahanan Konkurensi & Zero-State Sabotage | 15 | 0 | 15 | PASS |
| Vektor F: Kualitas Instruksi & Keamanan Agentik | 10 | 0 | 10 | PASS |
| Vektor G: Ergonomi Operasional & SLA Penyimpanan | 10 | 0 | 10 | PASS |
| **TOTAL SKOR AKHIR** | **100** | **0** | **100** | **100% PRODUCTION READY** |

### 2. MATRIKS KEJUJURAN ARSITEKTUR (CLAIM VS CODE AST TRUTH)
A table contrasting claims against actual AST implementations:
| Fitur / Algoritma | Klaim Dokumentasi | Realitas Kode AST | Lokasi Berkas & Simbol | Status |
| :--- | :--- | :--- | :--- | :---: |

### 3. ACTIONABLE REMEDIATION PLAN (PHASE-BY-PHASE FOR AI EXECUTION)
If zero material findings exist, the Agent MUST state: `ZERO MATERIAL DEFECTS CONFIRMED: 100/100 PRODUCTION READY. No remediation plan required.`

If material defects exist, the Agent MUST organize tasks into 4 topological dependency phases:
- **Phase 1: Foundation Primitives & Import Integrity** (Kernel primitives in `core/`, import cleanup, atomic write patterns)
- **Phase 2: Core Domain Logic & Mathematical Safety** (Formulas for Shannon/Louvain/IDF, graph traversals, concurrency)
- **Phase 3: Gateway, Dispatcher & Manifest Harmonization** (CLI router `orion.py`, help groups, documentation metrics)
- **Phase 4: Mechanical Verification & End-to-End Evidence** (Running the 8 verification gates and test suites)

Every remediation task MUST be formatted as an **AI Execution Action Card**:
```markdown
### Task [PHASE].[NUMBER]: [Brief Action Title]
- **Target File**: `relative/path/to/file.py`
- **Target Span / Symbol**: Lines X-Y or function `func_name()`
- **Defect Category & Penalty**: `[PENALTY_CODE]` (-X Pts)
- **Root Cause**: [Concise 1-sentence explanation of the runtime or AST defect]
- **Prerequisite Imports**: [Explicit symbols required at the top of the file]
- **Exact Drop-In Code Replacement**:
  ```python
  # Complete, production-ready replacement code block without dummy placeholders
  ```
- **Verification Gate**:
  ```bash
  # Exact terminal command to mechanically verify this fix (Exit Code 0 required)
  ```
```

### 4. EXECUTIVE TO-DO CHECKLIST
An interactive task checklist (`[ ]`) summarizing all Phase 1–4 action items for sequential progress tracking.
