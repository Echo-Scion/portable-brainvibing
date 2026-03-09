---
name: react-init
description: Scaffolding and initialization protocol for React and Next.js applications.
activation: manual
---

# React / Next.js Project Initialization Protocol

Follow this workflow when scaffolding a new React web application.

## 1. Project Scaffolding
Prefer Vite with TypeScript for client-side single page applications, or Next.js for hybrid/SSR web applications:
```bash
# Option A: Vite + React + TypeScript
npm create vite@latest <project_name> -- --template react-ts
cd <project_name>
npm install

# Option B: Next.js (App Router + TypeScript + Tailwind)
npx create-next-app@latest <project_name> --typescript --tailwind --eslint --app --src-dir
```

## 2. Directory Structure (Feature-First)
```text
src/
├── app/ or routes/       # Pages and route handlers
├── components/          # Reusable shared UI primitives (Button, Modal, Input)
├── features/            # Domain features (e.g. auth, dashboard, billing)
│   └── <feature_name>/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       └── types/
├── hooks/               # Global reusable React hooks
├── lib/                 # Utility functions and API clients
└── styles/              # Global CSS and design tokens
```

## 3. Essential Tooling Setup
- Package Manager: `npm` or `pnpm`
- Linting: ESLint with `@typescript-eslint`
- Formatting: Prettier
- Unit Testing: `vitest` + `@testing-library/react`
