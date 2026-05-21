---
description: Mandatory security rules and validations (No Secrets, Secure Headers, Input Parsing).
activation: glob
globs: *

version: 3.0.0
last_updated: 2026-05-20
---

# 🛡️ Universal Security Guardrails

## 1. Absolute Directives (Zero Exceptions)

1. **NO HARDCODED SECRETS**: You MUST NEVER hardcode API keys, service roles, database credentials, or environment variables in application code.
2. **NO BLIND EXECUTION**: You MUST NEVER suggest or execute shell commands involving `curl | bash` without first writing the script to a file and auditing it.

## 2. Mandatory Pre-Commit Mechanical Checks

Before concluding any task that modifies configuration, authentication logic, or initialization files, you **MUST** run the Mechanical Sentinel.

**How to run it:**
```bash
# To scan the whole project:
python .agents/canons/global/harnesses/secrets_scan_verifier.py

# To scan a specific file:
python .agents/canons/global/harnesses/secrets_scan_verifier.py --file <path_to_file>
```
If the script returns `[FATAL]`, you MUST remove the secret, replace it with an environment variable reference, and re-run the script until it returns `[PASS]`.

## 3. Database Security Defenses

When implementing backend architecture or database schemas:

1. **Enforce Access Control**: Never expose direct database connections to the client without an access control layer (e.g., Row Level Security or a secure API layer).
2. **Sanitize Inputs**: Always use parameterized queries or an ORM/Query Builder. NEVER construct raw SQL strings via concatenation (`SELECT * FROM users WHERE name = '` + userInput + `'`).
3. **Least Privilege**: Always configure database connections using roles with the absolute minimum privileges required for the specific service.

## 4. Frontend Security Defenses

When modifying frontend logic or UI:

1. **Output Encoding**: Assume all user-provided data is malicious. Always encode data before rendering it in the UI to prevent XSS (Cross-Site Scripting). Do not bypass framework safety mechanisms (e.g., avoid `dangerouslySetInnerHTML` in React, or equivalent features in other frameworks, unless absolutely necessary and coupled with a sanitizer).
2. **Secure State Transfer**: Never store sensitive data (tokens, PII) in insecure local storage (like `localStorage` in web) if secure alternatives exist (like `HttpOnly` cookies or encrypted platform storage).

## 5. Network Security Defaults
1. **HTTPS Everywhere**: Never make an HTTP request; enforce HTTPS.
2. **CORS/CSP**: Configure strict Cross-Origin Resource Sharing (CORS) and Content Security Policy (CSP) headers on the server to restrict where resources can be loaded from.
