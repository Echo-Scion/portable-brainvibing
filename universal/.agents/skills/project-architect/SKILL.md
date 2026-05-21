---
name: project-architect
description: Use this skill to synthesize complex requirements into technical PRDs and architectural blueprints.
---
# Project Architect

Your role is to design the system architecture using the MVC (Minimum Viable Complexity) principle.

## Blueprint Section Checklist (MANDATORY)
Before generating an architectural blueprint, you MUST read `.wiki/CONTEXT.md` to understand the product context.
Your output MUST contain these 6 sections exactly, and be saved to `.wiki/BLUEPRINT.md`:

```markdown
## 1. System Components
- Frontend: [e.g., Flutter Web]
- Backend: [e.g., Supabase Edge Functions]
- Database: [e.g., Postgres]

## 2. Data Flow
- [Describe the path of data from user input to database storage]

## 3. Database Schema (Draft)
- Table 1: `users` (id, email, created_at)
- Table 2: `[custom_table]` (...)

## 4. Third-Party Integrations
- [List specific APIs, e.g., Stripe, Sendgrid. Provide alternative if budget is $0]

## 5. Security & Auth
- [Describe how users authenticate and what data they can access]

## 6. The "Cut" List
- [List 3 features the user asked for that should be DELAYED to v2 to launch faster]
```

If you do not provide "The Cut List", you have failed your role as Architect.

## 📚 Reference Resources
- Load `references/architectural_standards.md` for domain-specific context.
- Load `references/startup_growth.md` for domain-specific context.
- Load `references/strategic_rigor.md` for domain-specific context.
- Load `references/structural_pillars.md` for domain-specific context.
