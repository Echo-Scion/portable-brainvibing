# VOLUME IX: DARWINIAN EVOLUTION LIFECYCLE

---

## Chapter 21: Friction Mining

### 21.1. Mechanism
1. AI makes an error → terminal returns Exit Code > 0.
2. Error is written to `LEARNINGS.md` with `[Darwinian Hook]` tag.
3. `pre-agent-wake.py` counts tags. If >= 3: `evolution_overdue = True`.
4. In the next turn, BIOS (`GEMINI.md` §1.7) forces the agent to run `evolve mine-friction`.
5. The agent analyzes error patterns, writes post-mortems, and proposes preventive rules.

### 21.2. Canary Deployment & Fitness Scoring
New rules are not applied immediately. Through `orion.py evolve bench`:
1. **Fork**: `cp SKILL.md SKILL-v2.md`
2. **Benchmark V1**: Test AI with old rules on a dummy task.
3. **Benchmark V2**: Test AI with new rules on the same task.
4. **Fitness Score**: Compare — tokens used, speed, Exit Code.
5. **Promotion**: If `score(V2) >= score(V1)`, merge. If fails, archive (do not delete).

### 21.3. Genomic Ledger
`EVOLUTION_LOG.jsonl` records every mutation permanently. When Foundation is deployed to a new project, this ledger is imported → the AI in the new project immediately inherits all lessons.

---

