# VOLUME IX: DARWINIAN EVOLUTION LIFECYCLE — Self-Learning & Adaptation

---

## Chapter 22: Friction Mining & Automated Post-Mortems

The `.agents` infrastructure enforces an automated learning loop to prevent recurring engineering errors. When an agent encounters failures during execution, it does not discard the diagnostic context; it mines the friction event.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Execution Failure Event                         │
│           (Exit Code > 0, Broken Assertion, Circuit Breaker)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   1. Friction Mining & Root-Cause                      │
│        Captures exact terminal output, stack trace, and context        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   2. Memory Journaling (LEARNINGS.md)                  │
│   Appends structured YAML entry (issue, root_cause, solution, warning) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   3. Darwinian Evolution Heartbeat                     │
│  `pre-agent-wake.py` checks unreviewed entries (threshold >= 3)        │
│  Flags `"evolution_overdue": true` in `.orion/working/context.json`    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   4. Self-Evolve Synthesis Loop                        │
│   Agent activates `self-evolve` skill to synthesize preventive rules   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   5. Security Sandbox & Promotion Gate                 │
│  `orion.py scan security` validates Risk Score <= 20                   │
│  Human operator approves promotion into permanent rules or GEMINI.md   │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 22.1. Structure of `LEARNINGS.md`
Each post-mortem entry is recorded in human-readable Markdown section format:
```markdown
## YYYY-MM-DD — <Failure Summary or Issue Title>

**Root Cause**: <Detailed explanation of the failure mechanism and trigger condition>

**Fix Applied**:
1. <Remediation step 1>
2. <Remediation step 2>

**Self-Evolve Rule**: <Actionable imperative rule to prevent pattern recurrence>
```

---

## Chapter 23: Evolution Heartbeat & The Self-Evolve Cycle

### 23.1. The Darwinian Heartbeat
During the pre-invocation sequence, `hooks/pre-agent-wake.py` counts unprocessed entries in `LEARNINGS.md`:
- If `unprocessed_learnings >= 3`, the hook injects `"evolution_overdue": true` into `.orion/working/context.json`.
- Upon bootstrap, the agent inspects this flag and executes `.agents/skills/self-evolve/SKILL.md` before starting new feature development.

### 23.2. Core Rule Immutability & Security Sandbox
To prevent adversarial drift or hallucinated policy changes:
- **Core Immutability**: `rules/core-guardrails.md` is strictly immutable. Automated modifications via `self-evolve` are forbidden.
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
This merges hardened rules and canons back to the master `_foundation` hub, enabling continuous evolution across the entire organization.
