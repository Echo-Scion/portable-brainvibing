---
name: backend-orchestrator
description: The overarching Architect for Backend Systems, Database Schema, and Performance Optimization.
---
# Backend Orchestrator

## 1. Database Schema Decision Tree

When designing a data model, use this tree:

```
Q1. Does the data have strict relational integrity? (e.g., Users -> Orders -> Payments)
    ├── YES -> Use Relational Tables.
    └── NO -> Proceed to Q2.

Q2. Is the data highly unstructured or document-like? (e.g., dynamic form configs, raw JSON logs)
    ├── YES -> Use document models or JSON columns depending on the database. Do NOT over-engineer relational schemas for document data.
    └── NO -> Default to standard Relational Tables.
```

## 2. Security Defaults

NEVER create a table or collection without applying security rules or access controls.

1.  Enable Row Level Security (RLS) if using a SQL database that supports it.
2.  Define explicit Read Policies (Who can view?).
3.  Define explicit Write Policies (Who can insert/update/delete?).

Before committing backend changes, run relevant security and migration tests.

## 📚 Reference Resources
- Check local references or rules for specific database constraints and rules.
