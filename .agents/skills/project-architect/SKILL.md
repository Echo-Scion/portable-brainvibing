---
name: project-architect
description: Use this skill to synthesize complex requirements into technical PRDs and architectural blueprints.
---
# Project Architect

## 🚀 Ecosystem Paradigm Shift
> **Core Directive**: Executable Generative Blueprints: Architecture diagrams (Mermaid graphs) become the single source of truth. Edit the diagram -> auto scaffold code.


## 🧠 Next-Gen Capabilities
> **Dynamic Topology Generation**: Ambiguity is lethal. You are strictly mandated to output C4 Model architecture specifications and Mermaid UML diagrams for every system design proposal. If it isn't visual, it isn't approved.


Your role is to design the system architecture using the MVC (Minimum Viable Complexity) principle.

## Blueprint Section Checklist (MANDATORY)
Before generating an architectural blueprint, you MUST read `.orion/CONTEXT.md` to understand the product context.
Your output MUST contain these 6 sections exactly, and be saved to `.orion/[BLUEPRINT](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/[BLUEPRINT.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/context/00_Strategy/BLUEPRINT.md)).md`:

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

## 7. Backend & Database Orchestration (Merged Capabilities)

### Database Schema Decision Tree
When designing a data model, use this tree:
Q1. Does the data have strict relational integrity? (YES -> Postgres Relational Tables, NO -> Q2)
Q2. Is the data highly unstructured or document-like? (YES -> Postgres `jsonb` columns, NO -> Relational Tables)

### Supabase Row Level Security (MANDATORY TEMPLATE)
NEVER create a table in Supabase without applying RLS.
```sql
ALTER TABLE public.posts ENABLE ROW LEVEL [SECURITY.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/caveman-compress/[SECURITY.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/caveman-compress/SECURITY.md));
CREATE POLICY "Public profiles are viewable by everyone." ON public.posts FOR SELECT USING ( is_public = true OR auth.uid() = user_id );
CREATE POLICY "Users can insert their own posts." ON public.posts FOR INSERT WITH CHECK ( auth.uid() = user_id );
```

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Architectural Standards** | references/[architectural_standards.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/[architectural_standards.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/architectural_standards.md)) |
| **Startup Growth** | references/[startup_growth.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/[startup_growth.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/startup_growth.md)) |
| **Strategic Rigor** | references/[strategic_rigor.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/[strategic_rigor.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/strategic_rigor.md)) |
| **Structural Pillars** | references/[structural_pillars.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/[structural_pillars.md](file:///C:/Users/USER/AndroidStudioProjects/_foundation/.agents/skills/project-architect/references/structural_pillars.md)) |
| **Backend Architect** | references/backend-architect.md |
| **Backend Optimizer** | references/backend-optimizer.md |
| **Cache Optimizer** | references/cache-optimizer.md |
| **Db Expert** | references/db-expert.md |
| **Enterprise Patterns** | references/enterprise_patterns.md |
| **Node Performance Tuning** | references/node_performance_tuning.md |
| **Postgres Patterns** | references/postgres_patterns.md |
