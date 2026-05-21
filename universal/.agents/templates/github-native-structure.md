---
name: github-native-structure
description: "Template for GitHub native stack directory structure"
scope: deployment
target_path: .github/
---

# GitHub Native Stack - Directory Structure Template

This template defines the complete `.github/` directory structure that will be created when deploying the Agent Foundation to a new project.

## Directory Tree

```
.github/
├── agents/                          # Native Copilot agent configurations
│   ├── copilot.agent.md            # Primary general-purpose agent (required)
│   ├── foundation-deployer.agent.md# Deployment specialist agent (required)
│   ├── integrity-auditor.agent.md  # Security/QA specialist agent (required)
│   ├── README.md                   # Agents documentation (required)
│   └── custom/                     # Project-specific custom agents (optional)
│       └── .gitkeep
│
├── rules/                           # Behavioral rules for agents
│   ├── _index.md                   # Navigation index (required)
│   ├── agent-core.md               # Core behavioral mandates (required)
│   ├── tier-execution.md           # Tier-based execution protocols (required)
│   ├── security-gates.md           # Pre-deployment security validation (required)
│   ├── context-standards.md        # Context hierarchy & memory management (required)
│   └── custom/                     # Project-specific custom rules (optional)
│       └── .gitkeep
│
├── workflows/                       # GitHub Actions automation hooks
│   ├── verify-agents.yml           # Verify structural integrity (required)
│   ├── deploy-foundation.yml       # Deploy foundation to new projects (required)
│   ├── check-staleness.yml         # Detect stale/deprecated files (required)
│   ├── publish-foundation.yml      # Sync to portable brainvibing (required)
│   └── custom/                     # Project-specific custom workflows (optional)
│       └── .gitkeep
│
├── ARCHITECTURE.md                 # GitHub native stack architecture (required)
├── README.md                       # Entry point & navigation (required)
└── .copilot-memory.md             # Session-scoped memory (optional, auto-created)
```

## File Deployment Checklist

### Required Core Files (MUST be deployed)
- [ ] `.github/agents/copilot.agent.md`
- [ ] `.github/agents/foundation-deployer.agent.md`
- [ ] `.github/agents/integrity-auditor.agent.md`
- [ ] `.github/agents/README.md`
- [ ] `.github/rules/_index.md`
- [ ] `.github/rules/agent-core.md`
- [ ] `.github/rules/tier-execution.md`
- [ ] `.github/rules/security-gates.md`
- [ ] `.github/rules/context-standards.md`
- [ ] `.github/workflows/verify-agents.yml`
- [ ] `.github/workflows/deploy-foundation.yml`
- [ ] `.github/workflows/check-staleness.yml`
- [ ] `.github/workflows/publish-foundation.yml`
- [ ] `.github/ARCHITECTURE.md`
- [ ] `.github/README.md`

### Optional Directories (auto-created if missing)
- [ ] `.github/agents/custom/`
- [ ] `.github/rules/custom/`
- [ ] `.github/workflows/custom/`

## Post-Deployment Structure

After deployment, structure should be:

```
project-root/
├── .github/
│   ├── agents/
│   ├── rules/
│   ├── workflows/
│   ├── ARCHITECTURE.md
│   └── README.md
│
├── .agents/                     # Also deployed alongside
│   ├── rules/
│   ├── skills/
│   ├── workflows/
│   ├── scripts/
│   ├── templates/
│   └── workspace_map.md
│
└── context/ (optional, user creates)
    ├── 00_Strategy/
    ├── 01_Product/
    ├── 02_Creative/
    └── 03_Tech/
```

## Integration Points

### Copilot Integration
- Agents in `.github/agents/` automatically discoverable
- Rules in `.github/rules/` loaded by agents at runtime
- Workflows trigger on specified GitHub events

### Skill Integration
- `.github/agents/` reference `.agents/skills/` via skill names
- Agents delegate to skills via @mention pattern (e.g., `@project-architect`)

### Context Integration
- Project-specific context stored in `context/` (separate from foundation)
- Foundation remains clean and updateable
- Custom rules/agents go in `.github/` (versioned separately)

---

**Usage**: Deploy using `.agents/scripts/deploy_foundation.py --target <path>`