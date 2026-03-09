---
name: react-micro
description: Micro-canon cheat sheet for React 19, Next.js App Router, TanStack Query, Zustand, and Zod.
version: 1.0.0
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

## 4. 4-State Presentation Pattern
```tsx
export function View() {
  const { data, isLoading, isError, error } = useUsers();
  if (isLoading) return <div aria-busy="true" className="animate-pulse">Loading...</div>;
  if (isError) return <div role="alert">Error: {(error as Error).message}</div>;
  if (!data?.length) return <div>No records found.</div>;
  return <ul>{data.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
```
