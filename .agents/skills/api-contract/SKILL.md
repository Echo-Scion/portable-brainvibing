---
name: api-contract
description: >-
  Defines strict request/response data contracts, validation schemas (Zod, OpenAPI), and API safety layers. Use when designing API endpoints, validating request payloads, or creating data transfer contracts.
---
# API Contract Guard



Your role is to ensure zero malformed data reaches the database.

## Zod Schema Templates (MANDATORY)
When writing API endpoints, use these exact templates:

### 1. The Auth/Registration Template
```typescript
export const RegisterSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string().min(8, "Minimum 8 characters").regex(/[0-9]/, "Must contain a number"),
  name: z.string().min(2).max(50)
});
```

### 2. The Pagination Template (GET Requests)
```typescript
export const PaginationQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
  search: z.string().optional()
});
```

### 3. The Strict Update Template (PATCH Requests)
```typescript
export const UpdateProfileSchema = z.object({
  bio: z.string().max(200).optional(),
  avatarUrl: z.string().url().optional()
}).strict(); // Prevents injection of arbitrary fields like `isAdmin`
```

Never proceed with an API implementation without defining the Zod schema first.

## 📜 Specification-First Architecture & Protocol (SDD)

Never guess API shape. Code without a validated specification is speculative guessing. Follow this 4-phase protocol:

### Phase 0: Scope & Capability Mapping
When a requirement spans multiple independently testable sub-domains (e.g., auth, billing, notifications):
1. **Decompose First**: Define an explicit Capability Map before drafting individual endpoint schemas:
   ```markdown
   | Module ID | Responsibility | Dependencies |
   |---|---|---|
   | auth | Accounts, JWT tokens, RBAC | — |
   | billing | Invoicing, payment webhooks | auth |
   | notifications | Email dispatch, alerts | auth, billing |
   ```
2. **Acyclic Dependency Invariant**: Dependency arrows must point in one direction. Cyclical dependencies between modules are strictly forbidden.

### Phase 1: Contract Invariants & Negative Refusals
- **FORBIDDEN (Untyped Any Payloads)**: Loosely typed request bodies (`any`, `dynamic`, raw dictionaries, untyped maps) are strictly forbidden across boundary layers. Every endpoint MUST validate incoming parameters against an explicit Zod, Pydantic, or OpenAPI contract.
- **FORBIDDEN (Raw DB Exception Leaks)**: Never expose internal database error messages, stack traces, table names, or raw SQL queries in client-facing HTTP responses. Internal exceptions MUST be caught, logged server-side, and mapped to standard error envelopes.
- **FORBIDDEN (Mass-Assignment)**: Mutation schemas MUST enforce strict key stripping (`.strict()` in Zod, `extra="forbid"` in Pydantic). Rejecting unexpected payload properties is non-negotiable.
- **Immutable DTO First**: Define the complete contract DTO before authoring service or repository logic.


### Phase 2: Standard Unified Response Envelopes
Every HTTP endpoint must return a structured, predictable response envelope:

#### Success Envelope (`HTTP 200/201`):
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-10-11T22:45:00Z",
    "version": "v1"
  }
}
```

#### Error Envelope (`HTTP 4xx/5xx`):
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Field 'email' failed format validation",
    "details": [
      { "field": "email", "issue": "Invalid email address format" }
    ]
  },
  "meta": {
    "timestamp": "2026-10-11T22:45:00Z"
  }
}
```

### Phase 3: Contract Rejection Tests (Red-First & TDD Handoff)
Before implementing the route handler:
1. Write an automated unit test supplying invalid, malicious, or extraneous parameters.
2. Verify that the contract layer rejects the payload with an explicit `HTTP 400/422` and matching error code before connecting business logic.
3. Hand off validated payload schemas to `/data-logic` for immutable model mapping and execute the full cycle under `/strict-tdd`.

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute `view_file` on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **API Safety Patterns** | .agents/skills/api-contract/references/api_safety_patterns.md |
