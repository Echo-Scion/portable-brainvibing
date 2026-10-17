---
name: project-architect
description: >-
  Synthesizes complex requirements into technical PRDs, database schemas, and architectural blueprints. Use when designing system architecture, drafting database schemas, defining third-party integrations, or reviewing technical blueprints.
---
# Project Architect



Your role is to design the system architecture using the MVC (Minimum Viable Complexity) principle.

## Blueprint Section Checklist (MANDATORY)
Before generating an architectural blueprint, you MUST read `context/00_Strategy/BLUEPRINT.md` to understand the product context.
Your output MUST contain these 6 sections exactly, and be saved to `context/03_Tech/ARCHITECTURE.md`:

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
- [List 3 features the user asked for that MUST be delayed to v2 to launch faster]
```

If you do not provide "The Cut List", you have failed your role as Architect.

## 7. Backend & Database Orchestration (Merged Capabilities)

### Database Schema Decision Tree
When designing a data model, use this tree:
Q1. Does the data have strict relational integrity? (YES -> Postgres Relational Tables, NO -> Q2)
Q2. Is the data highly unstructured or document-like? (YES -> Postgres `jsonb` columns, NO -> Relational Tables)

### Supabase Row Level Security (MANDATORY TEMPLATE)
NEVER create a table in Supabase without applying RLS.
```sql
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public profiles are viewable by everyone." ON public.posts FOR SELECT USING ( is_public = true OR auth.uid() = user_id );
CREATE POLICY "Users can insert their own posts." ON public.posts FOR INSERT WITH CHECK ( auth.uid() = user_id );
```

## 🔗 Downstream Interconnection Handoff
Architectural schemas must flow downstream without drift:
- Hand off drafted schemas and endpoints to `/api-contract` for Zod/OpenAPI boundary encasement.
- Route entity structures to `/data-logic` for immutable model generation.
- Enforce that boundary validation schemas generate red/failing contracts in `/strict-tdd` prior to writing backend routes.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Architectural Standards** | .agents/skills/project-architect/references/architectural_standards.md |
| **Startup Growth** | .agents/skills/project-architect/references/startup_growth.md |
| **Strategic Rigor** | .agents/skills/project-architect/references/strategic_rigor.md |
| **Structural Pillars** | .agents/skills/project-architect/references/structural_pillars.md |
