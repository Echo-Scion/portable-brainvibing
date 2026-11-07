# 🌐 Native Platform Superpowers & JIT Playbook

This reference guides AI agents and developers in utilizing native platform-specific commands, slash tools, and IDE capabilities across supported environments.

---

## 1. Google Antigravity Superpowers

When operating inside Google Antigravity, the host environment provides specialized native slash commands that automate complex multi-turn workflows:

| Slash Command | Best-Fit Scenario | Proactive Trigger in `🔮 NEXT TASK` |
| :--- | :--- | :--- |
| **`/plan`** | Complex features, architectural changes, or multi-file refactors | Recommend before editing code when blast radius > 3 files |
| **`/grill-me`** | Ambiguous requirements, 50/50 forks, architectural trade-offs | Recommend when user proposal has multiple viable branches |
| **`/teamwork`** | Massive projects benefiting from concurrent autonomous subagents | Recommend when tasks can be partitioned across independent worktrees |
| **`/boost`** | Hard bugs, complex math/algorithms, deep code review | Recommend during Strike-2 debugging or complex systems engineering |
| **`/schedule`** | Autonomous cron jobs or delayed wakeup timers | Recommend when user requests recurring polling or delayed checks |
| **`/goal`** | Unattended long-running tasks | Recommend when user asks for overnight or end-to-end task completion |
| **`/browser`** | Web interactions, DOM inspection, scraping | Recommend when web UI testing or live external docs are needed |
| **`/compact`** | Context bloat eviction | Recommend when conversation context window exceeds 80k tokens |
| **`/learn`** | Reflection and persistent memory extraction | Recommend after resolving recurring bugs or when user corrects agent |
| **`/automation`**| Scheduled background automations | Recommend when user wants to author a standing cron routine |

---

## 2. CLI Capability Scanning

Run the unified scanner anytime to inspect active platform tools:

```pwsh
# Markdown cheat sheet of active host superpowers
python .agents/scripts/orion.py env --platform

# Machine-readable environment payload
python .agents/scripts/orion.py env --json
```

---

## 3. Proactive Playbook Trigger Invariant

Agents MUST NOT wait for the user to guess slash commands. If a turn qualifies:
- **Complex multi-file scope?** Suggest `/plan` in `🔮 NEXT TASK`.
- **Ambiguous fork?** Suggest `/grill-me` in `🔮 NEXT TASK`.
- **Concurrent multi-subagent scope?** Suggest `/teamwork` in `🔮 NEXT TASK`.
- **Deep reasoning or tough bug?** Suggest `/boost` in `🔮 NEXT TASK`.
