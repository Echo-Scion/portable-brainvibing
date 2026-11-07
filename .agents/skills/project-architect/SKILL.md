---
name: project-architect
description: >-
  Synthesizes complex requirements into technical PRDs, database schemas, and architectural blueprints. Use when designing system architecture, drafting database schemas, defining third-party integrations, reviewing technical blueprints, or conducting multi-lens spec reviews.
---
# Project Architect

Your role is to design the system architecture using the MVC (Minimum Viable Complexity) principle.

## Blueprint Section Checklist (MANDATORY)
Before generating an architectural blueprint, you MUST read `context/VISION.md` (for North Star invariants) and `context/00_Strategy/BLUEPRINT.md` to understand the product context.
Your output MUST contain these 6 sections exactly, and be saved to `context/03_Tech/ARCHITECTURE.md` (with granular database, API, and state facet files created in `context/03_Tech/` per the 25-File Golden Ratio Registry):

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

### Database Access Control & Row-Level Security (When Using Postgres / Supabase)
When the target stack uses Postgres or Supabase, NEVER expose a public table without applying Row Level Security (RLS):
```sql
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public profiles are viewable by everyone." ON public.posts FOR SELECT USING ( is_public = true OR auth.uid() = user_id );
CREATE POLICY "Users can insert their own posts." ON public.posts FOR INSERT WITH CHECK ( auth.uid() = user_id );
```

## 8. Architecture Trade-Off Gate & `(Recommended)` Mandate
When an architectural decision has more than one defensible choice (e.g., data schema, component boundaries, storage engine, protocols):
1. **Present Options & Tag `(Recommended)`**: Present up to three options outlining the concrete mechanism, trade-offs, and failure conditions. In accordance with `AGENTS.md §1 (Ambiguity Halt & Zero-Debt Decision Mandate)`, tag the strongest engineering option with `(Recommended)` unless the choice is a true 50/50 product fork.
2. **Approval & Decision Ledger**: Never pick an architectural fork silently during discovery. Once the user approves the plan (`"Proceed"`), execute the `(Recommended)` path to 100% completion and record the choice in `.agents/DECISIONS.md` (`python .agents/scripts/orion.py decisions record`).
3. **Handle "Just Pick One"**: If the user asks the Agent to decide, execute the `(Recommended)` option, state the critical trade-off in one line, and record it in `.agents/DECISIONS.md`.

## 9. Upstream 6-Vector Pre-Blueprint Interrogation
When exploring raw feature hypotheses before drafting blueprints, stress-test the concept against the 6 Pre-Blueprint Stress-Test Lenses (see `references/strategic_rigor.md`):
1. **Contrarian MVC / YAGNI**: Why does this feature need to exist? Can existing codebase utilities or native stdlib solve 90% without new abstractions?
2. **Token & Resource Economics**: Peak QPS, database query volume, memory footprint, LLM token budget ceiling.
3. **DX & Ergonomics**: Intuitive API/CLI surface, low cognitive load, actionable error contracts.
4. **State Migration & Rollback**: Schema evolution, legacy data translation, rollback safety mid-migration.
5. **Telemetry & 3 AM Observability**: Distributed tracing, health telemetry, oncall incident diagnostics.
6. **Long-Term Tech Debt**: Maintainability across 2+ years, decoupling state machines from presentation.
- **Anti-Glazing Invariant**: Lead with risks and critique first. Strictly ban flattering adjectives (*brilliant, smart, great, spot-on*) and polite apologies.

## 10. The 5-Stage Blueprint Review Pipeline
Before finalizing any technical specification or converting it into execution cards (see `references/architectural_standards.md`):
1. **Scope Split**: Automatically discover the split between high-level architecture (`MacroSpan`: 1..L-1) and detailed tasks (`BentoSpan`: L..End, dividing at `## Detailed Implementation Plan`).
2. **Stage 1: High-Level Simplicity & Reuse Check (MVC / YAGNI)**: Audit `MacroSpan` for context sufficiency, root problem focus, YAGNI, codebase reuse, and anti-weeds altitude control.
3. **Stage 2: Paraphrase & Comprehension Check**: Reviewer must synthesize a coherent paraphrase of *What this proposes* and *How the existing system works*. Failure to mirror coherently is an automatic 🔴 Blocker.
4. **Stage 3: Triad Stress-Test**: Audit failure modes across Boundary, Resource/Concurrency, and Silent Failure.
5. **Stage 4: Post-Review Bloat Check**: Re-audit changes introduced during Stages 2 & 3. Verify that addressing review critique did NOT inject defensive bloat, unnecessary layers, or speculative configurability.
6. **Stage 5: Zero-Decision Check (Implementation Readiness)**: Audit `BentoSpan` to verify that zero architectural or design decisions remain for the implementer.

## 🔗 Downstream Interconnection Handoff
Architectural schemas must flow downstream without drift:
- Hand off drafted schemas and endpoints to `/api-contract` for Zod/OpenAPI boundary encasement.
- Route entity structures to `/data-logic` for immutable model generation.
- Enforce that boundary validation schemas generate red/failing contracts in `/strict-tdd` prior to writing backend routes.
- Delegate isolated multi-agent reviews to `/worker-delegate` (`reviewer` archetype: Isolated Reviewers) governed by $S_{\text{effective}}$ with `Model: 'flash'`.
- Verify architectural alignment against source code via Vector 8 in `.agents/skills/integrity-sentinel/references/audit_vectors.md`.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Architectural Standards & 5-Stage Blueprint Review** | .agents/skills/project-architect/references/architectural_standards.md |
| **Strategic PM Rigor & Discovery Gate** | .agents/skills/project-architect/references/strategic_rigor.md |
| **Startup Growth** | .agents/skills/project-architect/references/startup_growth.md |
| **Structural Pillars** | .agents/skills/project-architect/references/structural_pillars.md |
