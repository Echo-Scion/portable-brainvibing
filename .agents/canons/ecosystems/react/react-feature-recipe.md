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
Implement the 6-Family State Machine (Loading Skeleton, Instructional Error + Retry, First-Time Empty vs. Filtered-to-Empty, and Truncation-Safe Populated View):

```tsx
import React from "react";
import { useItems } from "../api/use-items";
import { useItemStore } from "../model/use-item-store";

export function ItemList({ onCreateFirst }: { onCreateFirst?: () => void }) {
  const { data: items, isLoading, isError, error, refetch } = useItems();
  const filter = useItemStore((s) => s.filter);
  const searchQuery = useItemStore((s) => s.searchQuery);
  const setFilter = useItemStore((s) => s.setFilter);
  const setSearchQuery = useItemStore((s) => s.setSearchQuery);

  if (isLoading) {
    return (
      <div className="space-y-2 p-4" aria-busy="true" aria-label="Loading items">
        <div className="h-10 w-full animate-pulse rounded-md bg-slate-200 dark:bg-slate-800" />
        <div className="h-10 w-3/4 animate-pulse rounded-md bg-slate-200 dark:bg-slate-800" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-900 dark:border-red-900/60 dark:bg-red-950/50 dark:text-red-200" role="alert">
        <p className="font-medium">Unable to load items</p>
        <p className="mt-1 text-sm">{error instanceof Error ? error.message : "Check your connection and try again."}</p>
        <button
          type="button"
          onClick={() => refetch()}
          className="mt-3 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white transition-colors duration-150 hover:bg-red-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-600 focus-visible:ring-offset-2"
        >
          Retry loading items
        </button>
      </div>
    );
  }

  // First-Time Empty State: orientation + single clear next action
  if (!items || items.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 p-8 text-center dark:border-slate-800">
        <p className="font-medium text-slate-900 dark:text-slate-100">No items yet</p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Items keep your team deliverables and milestones organized in one place.
        </p>
        {onCreateFirst ? (
          <button
            type="button"
            onClick={onCreateFirst}
            className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-transform duration-150 ease-out active:scale-[0.96] dark:bg-slate-50 dark:text-slate-900"
          >
            Create item
          </button>
        ) : null}
      </div>
    );
  }

  const visibleItems = items.filter((item) => {
    const matchesStatus =
      filter === "all" || (filter === "completed" ? item.isCompleted : !item.isCompleted);
    const matchesQuery =
      !searchQuery.trim() || item.title.toLowerCase().includes(searchQuery.trim().toLowerCase());
    return matchesStatus && matchesQuery;
  });

  // Filtered-to-Empty State: name the active filter/query and offer an immediate exit
  if (visibleItems.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 p-8 text-center dark:border-slate-800">
        <p className="font-medium text-slate-900 dark:text-slate-100">
          {searchQuery.trim() ? `No results for "${searchQuery.trim()}"` : `No ${filter} items`}
        </p>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Try a different search term or reset your active filters.
        </p>
        <button
          type="button"
          onClick={() => {
            setFilter("all");
            setSearchQuery("");
          }}
          className="mt-4 rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          Clear filters
        </button>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-200 dark:divide-slate-800">
      {visibleItems.map((item) => (
        <li key={item.id} className="flex items-center justify-between gap-4 py-3 px-4">
          <span
            title={item.title}
            className={`min-w-0 truncate ${item.isCompleted ? "line-through text-slate-400" : "text-slate-900 dark:text-slate-100"}`}
          >
            {item.title}
          </span>
        </li>
      ))}
    </ul>
  );
}
```
