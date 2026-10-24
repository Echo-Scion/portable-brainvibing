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
