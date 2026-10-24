# 🛡️ Skill Inspector: Agent Skill & Sub-Agent Audit Rubric

> **Origin**: Sovereign Agent Skill & Tool Audit Framework.
> **Purpose**: Provides static and semantic verification gates before adopting, executing, or delegating tasks to new AI skills, tool definitions, or sub-agent configurations.

---

## 1. The Two-Line Review Protocol

Every skill audit executes across two independent verification lines:
1. **Static AST & Pattern Verification**: Deterministic scanning for hardcoded secrets, dangerous execution sinks (`eval`, dynamic imports, unpinned network scripts), and permission declarations.
2. **Semantic Source-Aware Review**: Verifies purpose fit, permission alignment, prompt safety boundaries, and user control.

---

## 2. Risk Score Posture & Action Matrix

| Numerical Risk Score | Default Posture | Action Protocol |
| :---: | :---: | :--- |
| **0 – 20** | **LOW (Safe)** | Fast-track admission. Verified mechanical Exit Code 0, clean AST, bounded scope. |
| **21 – 35** | **MEDIUM (Guarded)** | Admissible only if sensitive capabilities (e.g., file writes, CLI execution) are strictly required and user-facing. |
| **36 – 50** | **HIGH (Caution)** | Blocked by default. Requires explicit user consent before tool execution. |
| **> 50** | **CRITICAL (Reject)** | Immediate rejection. Triggers execution circuit breaker. |

---

## 3. High-Signal Risk Rule Taxonomy

| Rule Category | Check Details | Verdict Impact |
| :--- | :--- | :---: |
| **Prompt Injection (`ORION-SEC-01`)** | Hidden instructions attempting to alter agent persona, bypass core guardrails, or leak system prompts. | **CRITICAL (REJECT)** |
| **Natural Language Exfiltration (`ORION-SEC-02`)** | Instructions directing the agent to send files, memory, or environment variables to remote URLs or logs. | **CRITICAL (REJECT)** |
| **Barefoot Credentials (`ORION-SEC-03`)** | Hardcoded API keys, bearer tokens, or private key blocks in skill source files. | **CRITICAL (REJECT)** |
| **Overprivileged Tools (`ORION-SEC-04`)** | Declaring broad file system or shell execution tools when simple read/format tools suffice. | **HIGH (CAUTION)** |
| **Silent Failure Swallow (`ORION-SEC-05`)** | Empty catch blocks (`except: pass` or `catch(e) {}`) hiding execution anomalies. | **HIGH (CAUTION)** |
| **Unpinned Remote Dependencies** | Invoking remote scripts via `curl | bash` or unpinned packages. | **HIGH (CAUTION)** |

---

## 4. Standard Review Output Schema

```json
{
  "skill_name": "example-skill",
  "risk_score": 15,
  "verdict": "APPROVE",
  "findings": [],
  "permission_fit": "PERFECT",
  "prompt_safety": "VERIFIED"
}
```
