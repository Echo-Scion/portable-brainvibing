# VOLUME IX: DARWINIAN EVOLUTION LIFECYCLE — Self-Learning & Adaptation

---

## Chapter 22: Habit Observation Ledger, Friction Mining & Automated Post-Mortems

The `.agents` infrastructure enforces a deterministic learning loop to prevent recurring engineering errors and capture operator habits. When an agent encounters tool failures, rule violations, or repeated developer command patterns, it captures and governs them through the **Observation Ledger** (`OBSERVATIONS.md`) and **Post-Mortem Journal** (`LEARNINGS.md`).

```
┌────────────────────────────────────────────────────────────────────────┐
│              Execution Friction / Repeated Operator Pattern            │
│    (Exit Code > 0, Rule Violation, Circuit Breaker, Command Habit)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│         1. Observation Ledger Capture (`.agents/OBSERVATIONS.md`)      │
│   5-Status Lifecycle: `open` → `validated` → `promoted` | `parked`     │
│   Sanitizes workspace paths; isolates unit tests from prod ledger      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
┌───────────────────────────────────┐           ┌───────────────────────────┐
│  2a. 2nd-Violation Escalation     │           │ 2b. Operator Habit Miner  │
│  `check_rule_violations()` flags  │           │ `mine_operator_habits()`  │
│  `[BARRIER_ESCALATION_CANDIDATE]` │           │ detects >= 3 command seqs │
└───────────────┬───────────────────┘           └─────────────┬─────────────┘
                │                                             │
                └───────────────────────┬─────────────────────┘
                                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│           3. Self-Evolve Synthesis & Cold Archival (`resolve`)         │
│   Promotes hardened checks into Tier-0 scripts or `rules/`             │
│   Archives resolved items to `.agents/OBSERVATIONS.archive.md`         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│          4. Security Sandbox, Ceiling Gate & Genomic Ledger            │
│   `orion.py verify` checks `core_max_lines` & `Risk Score <= 20`       │
│   Appends mutation record to `.agents/EVOLUTION_LOG.jsonl`             │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 22.1. The 5-Status Observation Ledger (`OBSERVATIONS.md` & `OBSERVATIONS.archive.md`)
Managed by `ObservationLedger` in `commands/reflexion.py` (`orion.py observe` / `orion.py resolve`):
- **5 Lifecycle Statuses**: `open`, `validated`, `promoted`, `parked`, and `superseded`.
- **Workspace Path Sanitization**: Both `note` and `evidence` fields automatically strip machine-specific absolute paths and `file://` prefixes (`<workspace>/...`) before persisting to disk.
- **Test Harness Isolation**: `core/db.py` (`log_telemetry`) and `core/harness/capture.py` (`ToolQuantumCapture`) isolate unit test runs (`unittest`/`pytest` or external `tempfile` directories) so synthetic test exceptions never bleed into the production `.agents/OBSERVATIONS.md`.
- **Cold Archival (`orion.py resolve <id> --status actioned`)**: Resolved or superseded observations are moved out of the active `OBSERVATIONS.md` file into `OBSERVATIONS.archive.md`, keeping the active ledger compact.

### 22.2. 2nd-Violation Tier-0 Barrier Escalation
Advisory Markdown rules degrade when models are under heavy context load. `ObservationLedger.check_rule_violations()` monitors repeated rule infractions:
- **1st Violation**: Logged as an advisory observation in `OBSERVATIONS.md`.
- **2nd Violation of the Same Rule**: Automatically escalates the entry to `[BARRIER_ESCALATION_CANDIDATE]`, signaling `self-evolve` to convert the prose rule into a deterministic Tier-0 Python check in `verify_agents.py` or `pre-agent-wake.py`.

### 22.3. Operator Habit Mining (`mine_operator_habits`)
During `orion.py consolidate session`, `mine_operator_habits()` inspects recent `recall_turns` and telemetry for manual CLI command sequences repeated $\ge 3$ times by the developer, logging candidate automation playbooks into `OBSERVATIONS.md`.

### 22.4. Structure of `LEARNINGS.md`
Each systemic post-mortem entry is recorded in structured Markdown format:
```markdown
## YYYY-MM-DD — <Failure Summary or Issue Title>

**Root Cause**: <Detailed explanation of the failure mechanism and trigger condition>

**Fix Applied**:
1. <Remediation step 1>
2. <Remediation step 2>

**Self-Evolve Rule**: <Actionable imperative rule to prevent pattern recurrence>
```

---

## Chapter 23: Evolution Heartbeat, Ceiling Ratchet & Security Sandbox

### 23.1. The Darwinian Heartbeat
During the pre-invocation sequence, `hooks/pre-agent-wake.py` counts unprocessed entries in `LEARNINGS.md` and summarizes active observations (`observation_digest`):
- If `unprocessed_learnings >= 3`, the hook injects `"evolution_overdue": true` into `.orion/working/context.json`.
- Upon bootstrap, the agent inspects this flag and executes `.agents/skills/self-evolve/SKILL.md` before starting new feature development.

### 23.2. Structural Ceiling Gate (`core_max_lines`)
To prevent self-evolution from bloating root instruction files or skills over time, `verify_agents.py` enforces hard line-count ceilings:
- Root instruction files (`AGENTS.md`, `GEMINI.md`) and `RULES_INDEX.md` are checked against structural line limits.
- Every skill (`skills/<name>/SKILL.md`) is validated against its YAML frontmatter `core_max_lines` ratchet (default 200 lines). If a skill grows past its ceiling, `orion.py verify` fails until detail is extracted into `references/`.

### 23.3. Core Rule Immutability & Security Sandbox
To prevent adversarial drift or hallucinated policy changes:
- **Core Immutability**: Section 1 of `AGENTS.md` and `GEMINI.md` is strictly immutable. Automated modifications via `self-evolve` are forbidden.
- **Security Scanner Sandbox**: Any proposed rule synthesized by `self-evolve` must pass `python .agents/scripts/orion.py scan security <file>` with a `Risk Score <= 20` before human review.
- **Human-in-the-Loop Gate**: Synthesized rules remain in draft status until explicitly approved by the developer.

---

## Chapter 24: Append-Only Genomic Ledger (`EVOLUTION_LOG.jsonl`)

Approved mutations, structural enhancements, and systemic bug fixes are committed to the append-only ledger `EVOLUTION_LOG.jsonl`:
```json
{
  "timestamp": "2026-10-14T23:30:00Z",
  "mutation": "Centralized database connections to core.kernel.db with WAL mode and busy_timeout=5000",
  "friction_source": "SQLite locked exceptions during parallel orion_ops ingest",
  "fitness_delta": "+28%",
  "genome_hash": "e4f8b91c2a"
}
```

### 24.1. Genome Fingerprint (`.genome.json`)
A compact hash representation of historical system mutations. When Foundation scaffolds into a new spoke project, `.genome.json` is copied, transferring operational lessons learned in previous projects.

### 24.2. Upstream Synchronization (`orion.py foundation push-upstream`)
When a spoke project develops improved patterns or discovers edge-case mitigations, the developer runs:
```bash
python .agents/scripts/orion.py foundation push-upstream --source /path/to/spoke
```
This merges hardened rules and canons back to the master framework hub, enabling continuous evolution across the entire organization.

---

## Chapter 25: Sovereign Skill Harness & Reflexion Auto-Heal (`core/harness/` & `reflexion.py`)

To prevent unverified LLM-authored skills or repairs from polluting the production workspace, `.agents` implements a quarantined **Sovereign Skill Harness** (`core/harness/`, ~79 KB) paired with closed-loop **Reflexion Auto-Heal** (`commands/reflexion.py`).

### 25.1. Tool Quantum Capture & Secret Redaction (`core/harness/capture.py`)
- **`ToolQuantumCapture`**: Tracks every tool execution as an opportunity-relative **session quantum** (`total_quanta`) in `.orion/harness/quantum_state.json`, recording which skills were invoked or missed without relying on wall-clock timestamps.
- **`SecretRedactor`**: Automatically scrubs API keys (`sk-...`, `AIza...`, `ghp_...`), bearer tokens, PEM blocks, and connection strings from captured tool arguments before any telemetry or staged skill intent is written to disk.

### 25.2. Quarantine Intent Queue & Stdio MCP Staging Server (`core/harness/staging.py`)
Agents cannot write directly into `.agents/skills/` during autonomous turns:
1. Candidate skills are submitted as a `StagedIntent` to `.orion/harness/intents/<intent_id>.json` via `IntentQueue` or the built-in stdio JSON-RPC 2.0 MCP server (`python .agents/scripts/orion.py harness serve`, exposing the `stage_skill` tool).
2. Each staged intent remains quarantined until evaluated by `SovereignPromoter` (`orion.py harness promote <intent_id>`).

### 25.3. The 14-Gate Admission Barrier (`core/harness/admission.py`)
`SovereignPromoter` validates every staged skill against 14 deterministic admission gates before permitting promotion into `.agents/skills/`:

| Gate ID | Category | Deterministic Check |
|:---|:---|:---|
| `HARNESS-FM-01` | Frontmatter | Valid YAML frontmatter block present at line 1 |
| `HARNESS-FM-02` | Frontmatter | Required keys (`name`, `description`) non-empty and kebab-case aligned |
| `HARNESS-FM-03` | Frontmatter | `core_max_lines` integer declared and respected ($\le 200$ lines default) |
| `HARNESS-STR-01` | Structure | Total `SKILL.md` line count $\le$ `core_max_lines` ceiling |
| `HARNESS-STR-02` | Structure | Mandatory actionable sections (`Workflow`, `Verification`, or procedural steps) present |
| `HARNESS-STR-03` | Structure | Zero hardcoded OS home-directory paths or `file://` URIs |
| `HARNESS-STR-04` | Structure | Zero placeholder tokens (`TODO`, `TBD`, `FIXME`, `<fill-in>`) |
| `HARNESS-T0-01` | Tier-0 Safety | Cannot weaken or contradict Section 1 Core Guardrails of `AGENTS.md` |
| `HARNESS-SIB-01` | Deduplication | Lexical/prefix similarity check against existing sibling skills |
| `HARNESS-CUR-01` | Curation | Triggers `ClusterCurator` check when $>3$ skills share a domain prefix |
| `HARNESS-REF-01` | Integrity | All referenced `references/` and `scripts/` paths physically exist |
| `HARNESS-SEC-01` | AST Security | Passes `core/security.py` static AST/regex scan with zero high-severity findings |
| `HARNESS-VERIFY-01` | Executable Gate | Associated verification command or `--self-test` harness exits with Code `0` |
| `HARNESS-CMT-01` | Prose & Hygiene | Passes comment hygiene and anti-slop prose authenticity checks |

### 25.4. Opportunity-Relative Skill Lifecycle (`core/harness/lifecycle.py`)
Unlike wall-clock TTL systems that wrongly archive skills simply because a developer was away on vacation, `LifecycleManager` (`orion.py harness lifecycle`) measures skill utility relative to **elapsed session quanta** (`maturity_window = 100` quanta, `active_capacity = 50` skills):
- **`PROBATION`**: Newly promoted skills with `< 100` elapsed session quanta since promotion.
- **`ESTABLISHED`**: Skills with $\ge 100$ elapsed quanta and positive hit utility (`hits / elapsed_quanta`).
- **`ARCHIVE_CANDIDATE`**: Skills with $\ge 100$ elapsed quanta, zero hits across the maturity window, and active skill count exceeding `active_capacity`.

### 25.5. Prefix Cluster Curation (`core/harness/curator.py`)
`ClusterCurator` (`orion.py harness curate`) scans `.agents/skills/` for fragmented prefix clusters (e.g., multiple micro-skills sharing a `<domain>-*` prefix) and generates an umbrella consolidation plan that merges sibling playbooks into a single primary `SKILL.md` with on-demand `references/`.

### 25.6. Closed-Loop Reflexion Auto-Heal (`commands/reflexion.py`)
When a test or verification command fails, `ReflexionLoop.auto_heal(file_path, test_cmd, error_output)` coordinates with `resolve_elastic_execution_plan()`:
1. Snapshots the original file contents in memory before attempting any repair.
2. Allocates `0`–`3` local repair trials depending on the active local model parameter tier (`3B` `micro_syntax` $\to 1$ trial; `7B` `single_fn` $\to 2$ trials; `32B` `multi_fn` $\to 3$ trials).
3. Validates every candidate patch via Python `ast.parse()` (for `.py` targets) and re-runs `test_cmd`.
4. If `test_cmd` returns `Exit Code 0`, records the successful heal in `.orion/working/reflexion_heals.jsonl`. If all local trials fail, restores the exact original file snapshot and escalates a structured handoff to the Cloud IDE tier.
