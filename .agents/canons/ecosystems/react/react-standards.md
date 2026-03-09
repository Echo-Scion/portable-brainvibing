---
name: react-standards
description: Development standards, state management, and accessibility guidelines for React applications.
activation: glob
globs: *.{tsx,jsx}
---

# React Development Standards & Guidelines

## 1. Component Design & Hooks
- Use pure functional components with TypeScript props interfaces. Avoid `React.FC`.
- Keep components small and focused. Extract business logic into custom hooks (`useFeatureState`).
- Obey the Rules of Hooks: Never call hooks inside loops, conditions, or nested functions.

## 2. State Management Strategy
- Local UI state: Use `useState` or `useReducer`.
- Server cache / remote state: Use `@tanstack/react-query` or SWR. Never store API response caches in global state stores.
- Client global state: Use `zustand` with selective subscription. Avoid giant unmemoized Redux or Context providers.

## 3. Performance & Rendering
- Avoid premature `useMemo` and `useCallback`, but mandate them when passing callbacks to memoized children or in dependency arrays.
- Virtualize long lists using `@tanstack/react-virtual` or `react-window`.
- Code-split routes and heavy dialogs using `React.lazy` and `Suspense`.

## 4. Accessibility (a11y) & HTML Semantics
- Use semantic HTML elements (`<main>`, `<nav>`, `<article>`, `<button>`). Never use `<div onClick=...>` without role, tabIndex, and keyboard handlers.
- Ensure all interactive elements have visible focus rings and accessible labels (`aria-label`).
