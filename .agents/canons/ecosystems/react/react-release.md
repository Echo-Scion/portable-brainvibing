---
description: Concrete steps to build and release a React / Next.js application to production.
ecosystem: react
---

# Workflow: React Production Release (`/react-release`)

Follow these concrete steps when the user asks to prepare, build, or deploy a React application to production.

## 1. Pre-Flight Verification Gate
Execute these mechanical verification commands. If any check exits with non-zero code, STOP immediately:

```bash
# 1. Typecheck entire codebase without emitting JS
npx tsc --noEmit

# 2. Strict linter audit
npm run lint

# 3. Unit and integration test suite
npm test -- --run

# 4. Dependency security audit
npm audit --audit-level=high
```

## 2. Production Build Execution
Run the hermetic production build command:

```bash
npm run build
```
*Output: `.next/` (for Next.js) or `dist/` / `build/` (for Vite/CRA)*

### Post-Build Checks:
- Verify stdout contains zero unhandled bundle errors or circular chunk warnings.
- Check bundle size report to ensure no single client chunk exceeds 500 kB uncompressed.

## 3. Deployment Targets

### Target A: Vercel / Netlify
1. If connected via Git: Push clean release commit to `main` branch.
2. If CLI deployment:
   ```bash
   npx vercel --prod
   # or
   npx netlify deploy --prod
   ```

### Target B: Dockerized Container (Node.js Alpine)
Ensure standalone output is enabled in `next.config.js` (`output: "standalone"`):
```bash
docker build -t app:latest .
docker run -p 3000:3000 app:latest
```
