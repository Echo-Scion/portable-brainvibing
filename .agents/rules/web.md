---
activation: glob
description: Web Development Standards for frontend excellence, API safety, and Node.js logic.
globs: *.ts, *.html, *.css

version: 2.4.0
last_updated: 2026-05-20
---

# Web Development Standards (Antigravity)

## 1. Backend & API (The "Defensive Shell" Principle)
- **Safety Gate**: Use `zod` or equivalent for strict input validation and schema parsing. Never trust raw request bodies.
- **Service Layer Pattern**: Decouple logic from Express/FastAPI routes. Use dedicated Service classes/functions for business logic.
- **Atomic Database Operations**: Use transactions for multi-step database writes to prevent partial data state.
- **API Documentation**: Provide comprehensive documentation for all endpoints (OpenAPI/Swagger).

## 2. Frontend (The "Component Harmony" Principle)
- **Premium Craftsmanship**: Every layout and architecture choice must be intentional. Avoid basic boilerplate; use professional patterns (e.g., compound components, render props).
- **Visual State Mapping**: Every component MUST account for and implement all states: Loading, Empty, Success, and Error.
- **Accessibility (A11y)**: All code MUST be compliant with WCAG 2.1 AA standards. Use semantic HTML, ARIA attributes, and ensure full keyboard navigation support.
- **Type Safety**: Mandatory TypeScript for all React/Angular components.
- **Atomic UI Components**: Keep components small (<150 lines) and focused on a single responsibility.

## 3. Performance & Security
- **Optimization**: Target initial load times under 1.5 seconds. Implement lazy loading for routes and heavy visual assets.
- **Static Analysis**: Enforce strict ESLint/Prettier rules before every commit.
- **Token Hygiene**: Use HttpOnly/Secure cookies for JWT storage. Never store secrets in `localStorage`.
- **Vulnerability Protection**: Protect against common web vulnerabilities (XSS, CSRF, SQL Injection).

## 4. Dependency Management
- **Audit**: Regularly update libraries to include latest security fixes and audit performance impact.
- **Pruning**: Avoid over-reliance on large, monolithic frameworks; prefer modular, tree-shakable libraries.