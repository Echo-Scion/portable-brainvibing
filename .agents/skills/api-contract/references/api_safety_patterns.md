# API Safety & Contract Patterns (Node.js + Zod)

## 🛡️ The Strict Contract (Zod)
```typescript
const CreateUserSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3).max(20),
  age: z.coerce.number().min(18).optional(),
}).strict(); // Reject unknown keys

type CreateUser = z.infer<typeof CreateUserSchema>;
```

## 🚨 Standardized Error Responses
```json
{
  "status": 400,
  "errors": [
    { "field": "email", "error": "Must be a valid email address" }
  ]
}
```

## ⚖️ Status Code Precision
- **201 Created**: Successful resource creation.
- **202 Accepted**: Async processing started.
- **409 Conflict**: Resource already exists.
- **422 Unprocessable Entity**: Semantic validation error.

---
*Preserved from Portable Brainvibing Infrastructure*
