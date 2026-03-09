# ADR-{{NUMBER}}: {{TITLE}}

## Status
{{STATUS: Proposed | Accepted | Superseded by ADR-XXX | Deprecated}}

## Date
{{DATE: YYYY-MM-DD}}

## Context & Problem Statement
[Describe the context and problem statement in 2-4 sentences. What business or technical forces are driving this choice? What constraints exist?]

## Decision Drivers
- [Driver 1: e.g., Low memory footprint on constrained hardware (≤8GB RAM)]
- [Driver 2: e.g., Pure Python 3 standard library portability without external compiled wheels]
- [Driver 3: e.g., Sub-50ms query latency for vector retrieval]
- [Driver 4: e.g., Long-term maintenance cost and deprecation ease]

## Considered Options
1. **Option 1**: {{OPTION_1_NAME}}
2. **Option 2**: {{OPTION_2_NAME}}
3. **Option 3**: {{OPTION_3_NAME}}

## Decision Outcome
Chosen option: **"{{OPTION_NAME}}"**, because [summarize the key justification, alignment with drivers, and expected return on investment].

## Pros and Cons of Considered Options

### {{OPTION_1_NAME}} (Chosen)
- **Good**, because [advantage 1]
- **Good**, because [advantage 2]
- **Bad**, because [drawback or mitigation required]
- **Mitigation**: [how the drawback is handled]

### {{OPTION_2_NAME}}
- **Good**, because [advantage 1]
- **Bad**, because [disqualifying factor or excessive complexity]
- **Verdict**: Rejected because [rationale]

### {{OPTION_3_NAME}}
- **Good**, because [advantage 1]
- **Bad**, because [disqualifying factor or constraint violation]
- **Verdict**: Rejected because [rationale]

## Consequences
- **Positive**:
  - [Benefit 1: e.g., Deterministic reproducibility across all developer machines]
  - [Benefit 2: e.g., Zero cloud daemon operational overhead]
- **Negative / Risks**:
  - [Trade-off 1: e.g., Requires manual schema migration scripts instead of automatic reflection]
  - [Trade-off 2: e.g., Limited throughput under >10,000 req/sec]
- **Neutral**:
  - [Neutral outcome: e.g., Relies on standard JSON format]

## Validation & Compliance Gate
- [ ] **Verification Command**: `[command proving the implementation functions as designed]`
- [ ] **Static/AST Enforcer**: `[linter rule, AST check, or schema validator preventing violation]`
- [ ] **Regression Test**: `[test suite covering the decision invariants]`
