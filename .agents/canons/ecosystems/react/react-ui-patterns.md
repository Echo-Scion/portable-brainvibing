---
description: React UI patterns, Tailwind contracts, 8-state interactive controls, and re-render prevention.
ecosystem: react
---

# React UI Patterns & Restrained Craft

## 1. Surface Philosophy (Solid over Trend-Stacking)
- **Primary Surfaces**: Restrict backgrounds to solid neutral tokens (`bg-white dark:bg-slate-950`).
- **Subtle Borders**: 1px subtle separation (`border border-slate-200 dark:border-slate-800`).
- **Restrained Shadows**: Soft minimal elevation (`shadow-sm`, never heavy colored glows).
- **Glassmorphism**: Forbidden on primary panels. Permitted exclusively as backdrop blur on fixed navbar or modal overlays with `backdrop-blur-md bg-white/80 dark:bg-slate-950/80`.

## 2. Interactive Control 8-State Contract
Every interactive control (button, input, selection row) must handle all 8 states:

```tsx
import React from "react";

interface ActionButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
}

export function ActionButton({ children, isLoading, disabled, className, ...props }: ActionButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      className={`
        inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium
        transition-colors duration-150 ease-in-out
        /* 1. Default */
        bg-slate-900 text-white dark:bg-slate-50 dark:text-slate-900
        /* 2. Hover */
        hover:bg-slate-800 dark:hover:bg-slate-200
        /* 3. Focus-visible */
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 dark:focus-visible:ring-slate-300
        /* 4. Active */
        active:scale-[0.98]
        /* 5. Disabled */
        disabled:pointer-events-none disabled:opacity-50
        /* 6. Loading */
        ${isLoading ? "cursor-wait opacity-80" : ""}
        ${className ?? ""}
      `}
      {...props}
    >
      {isLoading ? (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
}
```

## 3. Re-Render Prevention Rules
1. **Selective Zustand Subscription**: Always select atomic slices:
   ```typescript
   // Correct: only re-renders when count changes
   const count = useStore((state) => state.count);
   // Forbidden: re-renders on any state mutation
   const { count } = useStore();
   ```
2. **Stable Callbacks**: Pass callbacks wrapped in `useCallback` when passing to memoized children or list items.
3. **Compound Children over Prop Drilling**: Prefer `children` composition over heavy config objects to leverage React's bailout optimization.
