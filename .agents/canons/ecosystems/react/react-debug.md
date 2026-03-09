---
description: Systematic debugging workflows for React and Next.js applications.
ecosystem: react
---

# React Debugging Workflow

Follow this procedure when diagnosing UI rendering glitches, hydration mismatches, or runtime errors.

## 1. Hydration Mismatch Resolution
**Symptom**: `Expected server HTML to contain a matching <div> in <span>` or `Hydration failed because the initial UI does not match that was rendered on the server`.

### Diagnostic Steps:
1. **Invalid DOM Nesting**: Check for `<div>`, `<p>`, or `<h1>` rendered inside `<p>` or `<span>`. Common issue: rich text wrappers.
2. **Browser-Only APIs in Render**: Check for `window`, `localStorage`, `navigator.userAgent`, or `document` called directly during render rather than inside `useEffect`:
   ```tsx
   // Bug:
   const theme = typeof window !== "undefined" ? localStorage.getItem("theme") : "light";
   
   // Fix:
   const [theme, setTheme] = useState("light");
   useEffect(() => {
     setTheme(localStorage.getItem("theme") || "light");
   }, []);
   ```
3. **Date / Time / Randomization**: Non-deterministic values rendered on server vs client. Wrap in dedicated client-only boundary or pass normalized timestamps as server props.

## 2. Unhandled Async & Network Errors
1. Verify all `fetch` calls have an `if (!res.ok) throw new Error(...)` gate before `.json()`.
2. Ensure TanStack Query mutations define an `onError` handler or boundary.
3. Check for unmounted component state updates; use `AbortController` in effects:
   ```typescript
   useEffect(() => {
     const controller = new AbortController();
     fetchData({ signal: controller.signal });
     return () => controller.abort();
   }, []);
   ```

## 3. Render Profiling & Infinite Loops
1. **Dependency Array Audit**: If a `useEffect` loops endlessly, identify object/array literals or inline function definitions inside the dependency array. Wrap in `useMemo` or move outside component.
2. **React StrictMode Double-Invocation**: Expected in development (`process.env.NODE_ENV !== "production"`). Never write side-effects (analytics, charges, mutations) inside render or effect setup without cleanup.
