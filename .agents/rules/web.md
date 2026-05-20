---
activation: glob
description: Concrete Web Development Standards: Zod, ESLint, CSP, and Component States.
globs: *.ts, *.tsx, *.js, *.jsx, *.html, *.css

version: 3.0.0
last_updated: 2026-05-20
---

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
See `api-connector-protocols.md` for the mandatory Zod schema validation pattern for all incoming request payloads.