---
description: Standard React feature architecture using TypeScript, Zod, TanStack Query, and Zustand.
ecosystem: react
---

# React Feature Recipe

When generating a new React/Next.js feature, ALWAYS follow this 4-layer vertical slice pattern. Do not invent custom state hierarchies.

## 1. Domain Schema Layer (`src/features/[name]/types/schema.ts`)
Always validate API contracts and domain models with Zod:

```typescript
import { z } from "zod";

export const ItemSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1, "Title is required").max(120),
  isCompleted: z.boolean().default(false),
  createdAt: z.string().datetime(),
});

export type Item = z.infer<typeof ItemSchema>;
export const CreateItemInputSchema = ItemSchema.omit({ id: true, createdAt: true });
export type CreateItemInput = z.infer<typeof CreateItemInputSchema>;
```

## 2. Server State Layer (`src/features/[name]/api/use-items.ts`)
Use TanStack Query for server synchronization and caching:

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Item, ItemSchema, CreateItemInput } from "../types/schema";

const ITEM_QUERY_KEY = ["items"] as const;

export function useItems() {
  return useQuery({
    queryKey: ITEM_QUERY_KEY,
    queryFn: async (): Promise<Item[]> => {
      const res = await fetch("/api/items");
      if (!res.ok) throw new Error(`Failed to fetch items: ${res.statusText}`);
      const data = await res.json();
      return z.array(ItemSchema).parse(data);
    },
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateItemInput): Promise<Item> => {
      const res = await fetch("/api/items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      if (!res.ok) throw new Error("Failed to create item");
      return ItemSchema.parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ITEM_QUERY_KEY });
    },
  });
}
```

## 3. Client State Layer (`src/features/[name]/model/use-item-store.ts`)
Use Zustand for purely local/ephemeral client state:

```typescript
import { create } from "zustand";

interface ItemFilterState {
  filter: "all" | "active" | "completed";
  searchQuery: string;
  setFilter: (filter: "all" | "active" | "completed") => void;
  setSearchQuery: (query: string) => void;
}

export const useItemStore = create<ItemFilterState>((set) => ({
  filter: "all",
  searchQuery: "",
  setFilter: (filter) => set({ filter }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
}));
```

## 4. Presentation Component Layer (`src/features/[name]/components/item-list.tsx`)
Implement the 4-state contract (Loading, Empty, Error, Success):

```tsx
import React from "react";
import { useItems } from "../api/use-items";

export function ItemList() {
  const { data: items, isLoading, isError, error, refetch } = useItems();

  if (isLoading) {
    return (
      <div className="space-y-2 p-4" aria-busy="true">
        <div className="h-8 w-full animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
        <div className="h-8 w-3/4 animate-pulse rounded bg-slate-200 dark:bg-slate-800" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded border border-red-200 bg-red-50 p-4 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-200" role="alert">
        <p className="font-medium">Failed to load items</p>
        <p className="text-sm">{error instanceof Error ? error.message : "Unknown error"}</p>
        <button
          onClick={() => refetch()}
          className="mt-2 rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 dark:text-slate-400">
        <p className="text-base font-medium">No items found</p>
        <p className="text-sm">Create your first item to get started.</p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-200 dark:divide-slate-800">
      {items.map((item) => (
        <li key={item.id} className="flex items-center justify-between py-3">
          <span className={item.isCompleted ? "line-through text-slate-400" : ""}>{item.title}</span>
        </li>
      ))}
    </ul>
  );
}
```
