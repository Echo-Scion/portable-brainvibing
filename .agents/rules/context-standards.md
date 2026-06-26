---
description: Context scoping boundaries and 82-file registry enforcement rules.
activation: always on
---

# Context Standards & Scoping Boundaries

## 1. Environment Boundary Check (Scope Guard)

> **Context/82-File Mandate Isolation**: Before creating context files or enforcing the "82-File Mandate", you **MUST** verify the current environment.
> 1. The 82-file mapping can be applied to tooling/infrastructure repositories (where the tooling itself is the "product"). If a project does not require SaaS documentation, it may simply omit the `context/` directory.
> 2. The 82-file SaaS naming policy applies EXACTLY AND ONLY to Target Deployment Projects (SaaS apps). Enforcing them within `.agents/` or foundation directories is a strict protocol violation.

## 2. Context Length Caps

> **AST Hollowing (Zero-Body Protocol)**: You are STRICTLY FORBIDDEN from using the native `view_file` tool on source code files larger than 100 lines for discovery. 
> - You MUST use `run_command` with `rtk read <path/to/file> --level aggressive` to view the AST skeleton first without burning tokens.
> - Never blindly dump full context of multiple large files into your context window. Use Orion graph search and targeted grep limits.
