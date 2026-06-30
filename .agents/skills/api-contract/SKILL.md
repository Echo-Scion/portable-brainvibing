---
name: api-contract
description: Employ this skill to define strict request/response data contracts and safety layers (OpenAPI, Zod).
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

## 📚 Mandatory Knowledge Routing (JIT References)
*If your current task intersects with these domains, you MUST execute iew_file on the target BEFORE writing code:*

| If User Prompt/Task Relates To... | Immediately Load (view_file) |
| :--- | :--- |
| **Api Safety Patterns** | references/[[api_safety_patterns]]) |
