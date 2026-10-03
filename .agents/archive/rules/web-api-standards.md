---
description: UI/UX best practices, responsive layout, and API client contract enforcement.
activation: always on
---

# WEB & API STANDARDS

## Web UI Standards
# Web Development Standards (Antigravity)

## 1. Security (Concrete Implementation)

### Content Security Policy (CSP)
You MUST include a CSP header in the web server response or `<meta>` tag in HTML.
**Pattern:**
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://trusted.cdn.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;">
```

### XSS Protection
Never use `dangerouslySetInnerHTML` in React or `innerHTML` in Vanilla JS without sanitizing first.
**Pattern:**
```javascript
// DO:
element.textContent = userInput;
// DONT:
element.innerHTML = userInput; // XSS Vector
```

## 2. Component Harmony (The 4-State Map)

Every UI component that fetches data MUST explicitly handle these 4 states. Do not write the success path only.

```tsx
// MANDATORY 4-STATE PATTERN
function UserProfile({ userId }) {
  const { data, isLoading, error } = useUserData(userId);

  // State 1: Loading
  if (isLoading) return <SkeletonLoader />;
  
  // State 2: Error
  if (error) return <ErrorMessage message={error.message} />;
  
  // State 3: Empty
  if (!data) return <EmptyState icon="user" text="User not found" />;
  
  // State 4: Success
  return <ProfileCard user={data} />;
}
```

## 3. Static Analysis (ESLint)
Ensure strict typing and linting. Always fix lint errors before committing.
If lint rules are missing, enforce this baseline:
- `@typescript-eslint/no-explicit-any`: `error`
- `react-hooks/exhaustive-deps`: `error`

## 4. API Safety (Zod)
See `web-api-standards.md` for the mandatory Zod schema validation pattern for all incoming request payloads.

## API Connector Protocols
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

