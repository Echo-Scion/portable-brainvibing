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
  static?: boolean; // Disable press scale on high-frequency (100+/day) toolbar controls
  hasTrailingIcon?: boolean; // Optical alignment: pe-3.5 vs ps-4
}

export function ActionButton({
  children,
  isLoading,
  disabled,
  static: isStatic = false,
  hasTrailingIcon = false,
  className,
  ...props
}: ActionButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      className={`
        inline-flex min-h-[40px] items-center justify-center gap-2 rounded-md text-sm font-medium
        ${hasTrailingIcon ? "ps-4 pe-3.5" : "px-4"} py-2
        transition-[transform,background-color,box-shadow] duration-150 ease-out
        /* 1. Default */
        bg-slate-900 text-white dark:bg-slate-50 dark:text-slate-900
        /* 2. Hover */
        hover:bg-slate-800 dark:hover:bg-slate-200
        /* 3. Focus-visible (2px ring + 2px offset) */
        focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 dark:focus-visible:ring-slate-300
        /* 4. Active (0.96 scale unless static or disabled) */
        ${!isStatic ? "active:enabled:scale-[0.96]" : ""}
        /* 5. Disabled */
        disabled:pointer-events-none disabled:opacity-50
        /* 6. Loading */
        ${isLoading ? "cursor-wait opacity-80" : ""}
        ${className ?? ""}
      `}
      {...props}
    >
      {isLoading ? (
        <span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
}
```

## 2.5. High-Craft Surface, Image & Contextual Icon Recipes
1. **Concentric Nested Surfaces (`outerRadius = innerRadius + padding`)**:
   ```tsx
   <div className="rounded-2xl p-2 shadow-[0_0_0_1px_oklch(0_0_0/0.06),0_1px_2px_-1px_oklch(0_0_0/0.06)] dark:shadow-[0_0_0_1px_oklch(1_0_0/0.08)]">
     <div className="rounded-lg bg-slate-50 p-4 dark:bg-slate-900">{/* 16px outer - 8px pad = 8px inner */}</div>
   </div>
   ```
2. **Neutral Image Inner Outline (Never Tinted Slate/Zinc)**:
   ```tsx
   <img src={src} alt={alt} className="rounded-lg outline outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10" />
   ```
3. **Zero-Dependency Contextual Icon Crossfade (`scale 0.25 -> 1`, `blur 4px -> 0`, `bounce 0`)**:
   ```tsx
   export function StatefulIconSwap({ isActive, ActiveIcon, InactiveIcon }: { isActive: boolean; ActiveIcon: React.FC; InactiveIcon: React.FC }) {
     return (
       <span className="relative inline-flex size-4 items-center justify-center" aria-hidden="true">
         <span className={`absolute inset-0 flex items-center justify-center transition-[opacity,filter,transform] duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${isActive ? "scale-100 opacity-100 blur-0" : "scale-[0.25] opacity-0 blur-[4px]"}`}>
           <ActiveIcon />
         </span>
         <span className={`flex items-center justify-center transition-[opacity,filter,transform] duration-300 ease-[cubic-bezier(0.2,0,0,1)] ${isActive ? "scale-[0.25] opacity-0 blur-[4px]" : "scale-100 opacity-100 blur-0"}`}>
           <InactiveIcon />
         </span>
       </span>
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
