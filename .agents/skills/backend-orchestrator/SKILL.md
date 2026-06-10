---
name: backend-orchestrator
description: The overarching Architect for Backend Systems, Database Schema, and Performance Optimization.
---
# Backend Orchestrator

## 🚀 Ecosystem Paradigm Shift
> **Core Directive**: Edge-First Nano-Services: Every handler is an isolated Edge function deployed near the user with distributed caching.


## 🧠 Next-Gen Capabilities
> **Predictive Edge Caching**: Anticipate the user. Design predictive cache warming algorithms that pre-fetch data based on probable next-step user flows, and architect serverless cold-start mitigation patterns.


## 1. Database Schema Decision Tree

When designing a data model, use this tree:

```
Q1. Does the data have strict relational integrity? (e.g., Users -> Orders -> Payments)
    ├── YES -> Use Postgres Relational Tables.
    └── NO -> Proceed to Q2.

Q2. Is the data highly unstructured or document-like? (e.g., dynamic form configs, raw JSON logs)
    ├── YES -> Use Postgres `jsonb` columns. Do NOT create 10 EAV tables.
    └── NO -> Default to standard Relational Tables.
```

## 2. Supabase Row Level Security (MANDATORY TEMPLATE)

NEVER create a table in Supabase without applying RLS. Use this exact syntax template:

```sql
-- 1. Enable RLS
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- 2. Read Policy (Who can view?)
CREATE POLICY "Public profiles are viewable by everyone."
ON public.posts FOR SELECT
USING ( is_public = true OR auth.uid() = user_id );

-- 3. Write Policy (Who can insert/update?)
CREATE POLICY "Users can insert their own posts."
ON public.posts FOR INSERT
WITH CHECK ( auth.uid() = user_id );
```

Before committing backend changes, run the migration verifier harness.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute iew_file on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Backend Architect** | references/backend-architect.md |
| **Backend Optimizer** | references/backend-optimizer.md |
| **Cache Optimizer** | references/cache-optimizer.md |
| **Db Expert** | references/db-expert.md |
| **Enterprise Patterns** | references/enterprise_patterns.md |
| **Node Performance Tuning** | references/node_performance_tuning.md |
| **Postgres Patterns** | references/postgres_patterns.md |
