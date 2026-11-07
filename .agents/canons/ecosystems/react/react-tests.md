---
description: React testing recipes with Vitest, React Testing Library, and Playwright.
ecosystem: react
---

# React Test Recipes

Place unit and component tests adjacent to source or in `__tests__/` / `tests/` directory with `.test.tsx` extension.

## 1. Custom Hook Test (Vitest + React Testing Library)

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useItems } from "../api/use-items";
import React from "react";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("useItems", () => {
  it("fetches items successfully", async () => {
    const mockData = [{ id: "123e4567-e89b-12d3-a456-426614174000", title: "Task 1", isCompleted: false, createdAt: new Date().toISOString() }];
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const { result } = renderHook(() => useItems(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].title).toBe("Task 1");
  });
});
```

## 2. Component Integration Test (RTL + user-event)

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { ActionButton } from "../components/action-button";
import React from "react";

describe("ActionButton", () => {
  it("renders with text and triggers click event", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<ActionButton onClick={handleClick}>Submit</ActionButton>);

    const button = screen.getByRole("button", { name: /submit/i });
    expect(button).toBeInTheDocument();

    await user.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("disables interaction when isLoading is true", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<ActionButton isLoading onClick={handleClick}>Submit</ActionButton>);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");

    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });
});
```

## 3. Playwright E2E, State-Transition & Production Gremlin Spec

Always test goal-driven user scenarios across state transitions (Loading -> Populated -> Filtered-to-Empty -> Recovery) and Production Gremlins (120-char unbroken strings, 0 items, keyboard-only navigation):

```typescript
import { test, expect } from "@playwright/test";

test.describe("Goal-Driven Journey, State Transitions & Gremlins", () => {
  test("completes keyboard-only flow, recovers from filtered-empty state, and survives long-text gremlins", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // 1. Keyboard-only modal focus trap & focus restoration (WCAG 2.4.3 / 2.4.7)
    const createTrigger = page.getByRole("button", { name: /^create item$/i });
    await createTrigger.focus();
    await page.keyboard.press("Enter");
    await page.keyboard.press("Escape");
    await expect(createTrigger).toBeFocused();

    // 2. Filtered-to-Empty state recovery transition
    const searchInput = page.getByRole("searchbox");
    await searchInput.fill("nonexistent_gremlin_query_999");
    await expect(page.getByText(/no results for "nonexistent_gremlin_query_999"/i)).toBeVisible();
    await page.getByRole("button", { name: /^clear filters$/i }).click();
    await expect(searchInput).toHaveValue("");
  });
});
```
