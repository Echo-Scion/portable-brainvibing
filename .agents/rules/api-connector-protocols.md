---
activation: model_decision
description: Concrete API communication contracts, Zod validation snippets, and error response standards.

version: 3.0.0
last_updated: 2026-05-20
---

# API Connector & Integrity Protocols

Generic advice like "use JSON" is obsolete. Follow these concrete algorithmic patterns.

## 1. Request Validation (Zod Schema Mandate)

NEVER trust the incoming request body (`req.body` or `Event`). You MUST define a Zod/Freezed schema and parse it strictly before any business logic executes.

✅ **Zod (TypeScript/Node):**
```typescript
import { z } from "zod";

// 1. Define schema
const UpdateUserSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18).optional(),
});

// 2. Parse strictly inside the handler
export async function handler(req: Request) {
  const parseResult = UpdateUserSchema.safeParse(await req.json());
  if (!parseResult.success) {
    return new Response(JSON.stringify({
      error: "VALIDATION_FAILED",
      details: parseResult.error.flatten()
    }), { status: 400 });
  }
  const data = parseResult.data; // Safe to use
  // ... business logic ...
}
```

## 2. API Response Contract Template

Every API endpoint you write MUST conform to this exact JSON structure:

✅ **Success (200/201):**
```json
{
  "success": true,
  "data": { "id": "123", "name": "System" },
  "meta": { "pagination": { "page": 1, "total": 1 } } // Optional
}
```

❌ **Error (400/401/403/500):**
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with ID 123 does not exist.",
    "details": null
  }
}
```
*Rule: Do not leak stack traces or internal DB errors (e.g., Postgres `23505`) to the client.*

## 3. Idempotency Pattern

For critical operations (payments, state changes), you MUST require an `Idempotency-Key` header and implement a check-then-act lock.

**Algorithm:**
1. Read `Idempotency-Key` from header.
2. Query DB: `SELECT response FROM idempotency_store WHERE key = ?`
3. If exists, return cached `response`.
4. If not exists, begin transaction -> process -> save response -> commit.