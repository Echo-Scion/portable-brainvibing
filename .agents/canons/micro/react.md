---
name: react-micro
description: Micro-canon cheat sheet for React 19, Next.js App Router, TanStack Query, Zustand, and Zod.
---

# React Micro-Canon & Syntax Cheat Sheet

## 1. Zod Model Contract
```typescript
import { z } from "zod";
export const UserSchema = z.object({ id: z.string().uuid(), name: z.string().min(1) });
export type User = z.infer<typeof UserSchema>;
```

## 2. TanStack Query Fetch & Cache
```typescript
import { useQuery } from "@tanstack/react-query";
export function useUsers() {
  return useQuery({
    queryKey: ["users"],
    queryFn: async () => z.array(UserSchema).parse(await (await fetch("/api/users")).json()),
  });
}
```

## 3. Zustand Atomic Slice
```typescript
import { create } from "zustand";
interface State { count: number; inc: () => void; }
export const useCounter = create<State>((set) => ({ count: 0, inc: () => set((s) => ({ count: s.count + 1 })) }));
// Consumption: const count = useCounter((s) => s.count);
```

## 4. State-Complete Presentation Pattern (Skeleton, Instructional Error, Orientation Empty)
```tsx
export function View({ query = "", onReset, onCreate }: { query?: string; onReset?: () => void; onCreate?: () => void }) {
  const { data, isLoading, isError, refetch } = useUsers();
  if (isLoading) return <div aria-busy="true" className="h-10 animate-pulse rounded-md bg-slate-200 dark:bg-slate-800" />;
  if (isError) return <div role="alert">Unable to load users. <button type="button" onClick={() => refetch()}>Retry</button></div>;
  if (!data?.length) return <div><p>No users yet</p><button type="button" onClick={onCreate}>Create user</button></div>;
  const visible = query ? data.filter((u) => u.name.toLowerCase().includes(query.toLowerCase())) : data;
  if (!visible.length) return <div><p>No results for "{query}"</p><button type="button" onClick={onReset}>Clear filters</button></div>;
  return <ul>{visible.map((u) => <li key={u.id} className="truncate">{u.name}</li>)}</ul>;
}
```
