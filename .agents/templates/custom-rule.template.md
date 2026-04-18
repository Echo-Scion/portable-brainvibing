---
name: custom-rule
description: "Template for creating a custom behavioral rule"
scope: project-specific
target_path: .github/rules/custom/
---

# Custom Rule Template

Use this template to create project-specific behavioral rules. Each rule should focus on ONE behavioral domain specific to your project.

## File Naming
- **Location**: `.github/rules/custom/<rule-name>.md`
- **Format**: kebab-case (e.g., `my-custom-rule.md`)

## Template

```yaml
---
name: my-custom-rule
description: "Brief one-line description of what this rule enforces"
scope: project-specific
applies_to: ["copilot", "cline"]  # Which AI tools this applies to
---

# My Custom Rule Title

## Purpose

One or two sentences explaining why this rule exists and what problem it solves.

## Scope

Describe the extent of this rule:
- What scenarios trigger this rule?
- When should agents follow this rule vs. override it?
- Are there exceptions?

## Core Principles

List the key principles (2-4 main ideas):

1. **Principle 1**: Explanation
2. **Principle 2**: Explanation
3. **Principle 3**: Explanation

## Decision Matrix

Create a decision tree or matrix for applying this rule:

| Scenario | Action | Rationale |
| Scenario 1 | Action A | Because... |
| Scenario 2 | Action B | Because... |

## Implementation

Provide specific, actionable instructions:

### Step 1: Check X
Description of how to check X...

```bash
# Example command or code
```

### Step 2: Do Y
Description of how to do Y...

### Step 3: Verify Z
Description of how to verify Z...

## Anti-Patterns

Common mistakes or things NOT to do:

- ✗ **WRONG**: Description of wrong approach
- ✓ **CORRECT**: Description of correct approach

## Examples

### Example 1: Common Use Case
```
User: "I want to do X"

The agent should:
1. Check rule condition
2. Follow this pattern
3. Verify with this test
```

### Example 2: Edge Case
```
User: "What about edge case Y?"

This rule covers it by:
1. [specific handling]
2. [specific validation]
```

## References

Link to related documentation:
- [Parent Rule](../agent-core.md) — If this rule refines another rule
- [Related Skill](../../agents/skills/skill-name/SKILL.md) — If implemented by a skill
- [Reference Doc](../../ARCHITECTURE.md) — If you're implementing architectural pattern

## Maintenance

- **Last Updated**: [DATE]
- **Review Frequency**: Monthly / Quarterly / As-Needed
- **Owner**: [Team/Person]

---

## When to Create a Custom Rule

Create a custom rule when:
- ✓ You have project-specific behavioral constraints
- ✓ You want to override or extend foundation rules
- ✓ You identify a recurring pattern that should be formalized
- ✗ You're implementing a feature (use skills/workflows instead)
- ✗ You're documenting code (use code comments instead)

## Submitting Back to Foundation

If this rule is valuable for all projects:

1. **Generalize**: Remove project-specific values
2. **Refine**: Ensure it's broadly applicable
3. **Document**: Update examples for general audience
4. **Propose**: Submit PR to foundational rules (`.agents/rules/`)

---

Template Version: 1.0.0 | Last Updated: March 31, 2026
```

This template ensures consistency while allowing project-specific customization.