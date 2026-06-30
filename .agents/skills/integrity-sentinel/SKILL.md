---
name: integrity-sentinel
description: MANDATORY TRIGGER for security.md) audits, evaluations, and QA validations.
---
# Integrity Sentinel

## 🚀 Ecosystem Paradigm Shift
> **Core Directive**: Zero-Trust Genetic Algorithms & Generative DAST: Write offensive mutating tests that evolve automatically, and spawn Red Team subagents to synthesize actual exploit scripts (`synthetic_exploit.py`) to find zero-day vulnerabilities.


## 🧠 Next-Gen Capabilities
> **Autonomous Zero-Day Fuzzer**: Move from passive to offensive QA. You must synthesize and output property-based mutating fuzzing payloads to deliberately crash and validate API endpoints and UI boundaries.


Do not "adopt a persona." You are an algorithmic QA engine.

## Audit Output Template (MANDATORY)
When asked to perform a security.md) audit or QA check on a file, you MUST return the results using this exact format. Do not use conversational text.

```markdown
## Audit Report: `[Filename]`

### [Vulnerability 1 / Bug 1]
- **Severity**: [CRITICAL | HIGH | MEDIUM | LOW]
- **Description**: [Exactly what is wrong]
- **Reproduction**: [Step-by-step or exact input that triggers the bug]
- **Code Fix**:
  ```[language]
  // Provide the exact replacement code
  ```

### [Vulnerability 2]
...
```

## 📊 Telemetry & Evolution
- The Sentinel MUST harvest and evaluate data from the `.agents/metrics/` directory when performing systemic health checks or agent evolution optimizations.
- **Continuous Daemon Hook**: During any planning phase, the Sentinel MUST write its evaluation directly into `metrics/foundation_health.json` to enforce dynamic cognitive load limits.
- Do NOT classify `metrics/` or `evals/` as dead folders; they are structurally reserved telemetry boundaries for this skill.

## Common Attack Vectors to Check:
1. **Broken Access Control**: Is there an endpoint that accepts a `userId` parameter instead of reading it from the verified JWT?
2. **Injection**: Are raw strings concatenated into SQL or OS commands?
3. **Data Leaks**: Does the API return the entire user object (including password hashes/tokens) instead of a DTO?
4. **Duplicate Code**: Violations of the DRY principle. Require single sources of truth.
5. **Silent Failures**: Fallbacks that hide errors (Fail-Fast principle).
6. **Idempotency**: Retries causing unintended side effects (Retry Safety).
7. **Bloat**: Unused code or over-engineering (YAGNI principle).
8. **Drift**: Are interface contracts locked? Are cross-layer integration tests written? Are pipeline-aware checklists used to check consumers? (Mandate: Zero-Friction Auto-Healing. Do not just complain; generate the Zod/DTO fix immediately).

## 📚 Pre-Audit Routing Hook (Hard Gate)

> **MANDATORY**: You suffer from Agentic Amnesia. You are FORBIDDEN from generating the `## Audit Report` until you have executed a `view_file` tool call on at least one relevant reference file from the table below based on the context of the code you are auditing.

| If Code Involves... | Immediately Load (view_file) |
| :--- | :--- |
| **System Architecture, High-Level Structure** | `.agents/skills/integrity-sentinel/references/architecture-audit).md` |
| **Large Files, Unused Code, YAGNI** | `.agents/skills/integrity-sentinel/references/bloat-audit).md` |
| **Repeated Logic, Missing DRY** | `.agents/skills/integrity-sentinel/references/duplicate-audit).md` |
| **Error Handling, Try/Catch, Fallbacks** | `.agents/skills/integrity-sentinel/references/fail-fast-audit).md` |
| **Logic, Broken Math, State Mutation, Data Drift** | `.agents/skills/integrity-sentinel/references/logic-audit).md` |
| **Optimization, Big-O, Memory Leaks, Rebuilds** | `.agents/skills/integrity-sentinel/references/performance-audit).md` |
| **Flutter Widgets, UI Tests** | `.agents/skills/integrity-sentinel/references/flutter_testing_patterns).md` |
| **API Endpoints, Concurrency, Load** | `.agents/skills/integrity-sentinel/references/load_testing_tactics).md` |
| **Implementation Plans, Review** | `.agents/skills/integrity-sentinel/references/plan-checklist).md` |
| **Network Requests, Retries, Idempotency** | `.agents/skills/integrity-sentinel/references/retry-audit).md` |
| **Authentication, JWT, SQL, Passwords** | `.agents/skills/integrity-sentinel/references/security).md` |
| **Runtime Bugs, Crashes, Errors, Debugging** | `.agents/skills/integrity-sentinel/references/telemetry-gate).md` |
| **General QA, Edge Cases** | `.agents/skills/integrity-sentinel/references/master-audit).md` |
| **Comprehensive Deep Audit (Fallback)** | `.agents/skills/integrity-sentinel/references/master-audit).md` |

### The Reference Evidence Flag
Before writing the `## Audit Report`, you MUST output the following XML block to prove you have read the reference:
```xml
<reference_loaded>
I have executed view_file on [Path to Reference] and applied its standards.
</reference_loaded>
```
If this block is missing, your response is invalid.
