---
name: custom-agent
description: "Template for creating a custom Copilot agent"
scope: project-specific
target_path: .github/agents/custom/
---

# Custom Agent Template

Use this template to create project-specific Copilot agents for specialized tasks in your project.

## File Naming
- **Location**: `.github/agents/custom/<agent-name>.agent.md`
- **Format**: kebab-case (e.g., `my-custom-agent.agent.md`)

## Template

```yaml
---
name: my-custom-agent
type: specialized|general-purpose
version: 1.0.0
description: "One-line description of what this agent does"
tools: ["code_execution", "file_operations", "terminal_execution"]
context_window: 60000
token_budget: 30000
---

# @my-custom-agent - Agent Display Name

## Overview

2-3 sentences explaining what this agent does and when to use it.

**Invocation**: `@my-custom-agent`

**Best for**: [List specific use cases]

## Capabilities

- **Capability 1**: Brief description
- **Capability 2**: Brief description
- **Capability 3**: Brief description

## INSTRUCTIONS

Detailed behavioral rules for this agent. These instructions are loaded automatically by Copilot.

### Core Workflow

Describe the step-by-step process this agent follows:

1. **Step 1**: What does it do?
   - Sub-detail
   - Sub-detail

2. **Step 2**: What does it do?
   - Sub-detail
   - Sub-detail

3. **Step 3**: What does it do?
   - Sub-detail
   - Sub-detail

### Decision Rules

When faced with ambiguity, follow these rules:

- **IF** X condition → **THEN** take action Y
- **IF** A condition → **THEN** take action B

### Error Handling

If something goes wrong:

1. Capture error details
2. Attempt recovery with [recovery strategy]
3. If still failing, escalate to `@copilot`

### Security Constraints

List any security gates or validations:

- [ ] Validate input before processing
- [ ] Check for secrets and mask them
- [ ] Verify permissions before actions
- [ ] Log all critical operations

## PROMPT

This is the system prompt that guides Copilot's behavior for this agent.

You are the **[Agent Name]**, a specialized assistant focused on [domain/purpose].

### Your Purpose
[2-3 sentences about what you do]

### Your Constraints
- **Constraint 1**: Never do this
- **Constraint 2**: Always check for this
- **Constraint 3**: Report this type of error

### Your Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

### Your Super Powers
- ✅ [Power 1]
- ✅ [Power 2]
- ✅ [Power 3]

### Decision Framework

When deciding how to proceed:

1. Check if this is within my domain of knowledge
2. If NOT → Delegate to appropriate agent
3. If YES → Validate constraints are met
4. Then → Execute implementation

## SKILLS

Specialized agents this agent can delegate to:

| Agent | When to Use | Handoff Pattern |
| `@copilot` | When task exceeds my scope | "This requires `@copilot` - [reason]" |
| `@other-specialist` | For related domain | Description |

---

## Usage Examples

### Example 1: Common Use Case

```
User: "Can you help me with X?"

When you respond:
1. [What the agent does]
2. [What it asks for clarification if needed]
3. [How it delivers results]
```

### Example 2: Delegation Use Case

```
User: "Help me with X, but also handle Y"

When you respond:
1. Handle X yourself using this agent's capabilities
2. Recognize Y is outside scope
3. Mention `@other-agent` for Y: "For Y, I'll need `@other-agent`"
4. Offer to coordinate between both
```

---

## Integration

This agent integrates with:

- **Rules**: Loads from `.github/rules/` automatically
- **Skills**: Can @mention other agents for delegation
- **Workflows**: Can trigger GitHub Actions via `@copilot` (indirect)

---

## Testing Checklist

Before deployment, verify:

- [ ] Agent name in frontmatter matches filename (without `.agent.md`)
- [ ] YAML frontmatter is syntactically valid
- [ ] All @mentions reference valid agents/skills
- [ ] INSTRUCTIONS section is clear and unambiguous
- [ ] PROMPT section provides good guidance to Copilot
- [ ] Examples are realistic and accurate
- [ ] Uses correct heading levels (# for title, ## for main sections)

---

## Maintenance

- **Last Updated**: [DATE]
- **Version**: 1.0.0
- **Owner**: [Team/Person]
- **Review Schedule**: [Frequency]

---

## When to Create a Custom Agent

Create a custom agent when:
- ✓ Your project has unique, specialized workflows
- ✓ You want to guide Copilot toward project-specific patterns
- ✓ You have domain-specific knowledge to encode
- ✗ You're implementing a skill (too generic) - use `.agents/skills/` instead
- ✗ You're creating a rule (behavioral, not task-specific) - use `.github/rules/custom/` instead

## Submitting Back to Foundation

If this agent would benefit all projects:

1. **Generalize**: Remove all project-specific values
2. **Refine**: Ensure it's broadly applicable
3. **Test**: Verify with multiple projects
4. **Document**: Add to foundation agents (`.github/agents/`)
5. **Propose**: Submit PR describing the new capability

---

Template Version: 1.0.0 | Last Updated: March 31, 2026
```

## Quick Stats

- **Agent creation**: ~30 min per specialized agent
- **Testing**: ~10-15 min per agent
- **Documentation**: Included in agent file