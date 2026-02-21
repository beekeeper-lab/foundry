# React Testing

Testing strategy and patterns for React applications. Tests exist to catch
regressions and document behavior -- not to achieve arbitrary coverage numbers.
Every test should describe a user-visible behavior or a critical integration
boundary.

---

## Defaults

- **Unit / Component tests:** Vitest + `@testing-library/react`.
- **End-to-end tests:** Playwright.
- **Assertion library:** Vitest built-in (`expect`) + `@testing-library/jest-dom` matchers.
- **Mocking:** Vitest `vi.mock()` for modules; MSW (Mock Service Worker) for network requests.
- **Coverage target:** 80% line coverage on business logic; no hard target on UI components.
- **CI gate:** All tests must pass. Flaky tests are deleted or fixed within 48 hours.

### Alternatives

| Default           | Alternative        | When to consider                        |
|-------------------|--------------------|-----------------------------------------|
| Vitest            | Jest               | Existing Jest codebase; migration not worth it |
| Playwright        | Cypress            | Team already proficient; simpler setup  |
| MSW               | Nock               | Node-only test environment              |

---

## Test Organization

```
src/
  features/
    checkout/
      CheckoutForm.tsx
      CheckoutForm.test.tsx       # Component test, co-located
      hooks/
        useCheckout.ts
        useCheckout.test.ts       # Hook test, co-located
tests/
  e2e/
    checkout.spec.ts              # E2E journey test
  setup.ts                        # Global test setup (MSW, cleanup)
```

- Co-locate unit/component tests next to the source file.
- E2E tests live in `tests/e2e/`, named by user journey.
- Shared test utilities (render wrappers, factories) live in `tests/helpers/`.

---

## Component Testing Patterns

### Render and Assert

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { CheckoutForm } from "./CheckoutForm";

describe("CheckoutForm", () => {
  it("calls onSubmit with the entered email when submitted", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(<CheckoutForm onSubmit={handleSubmit} />);

    await user.type(screen.getByRole("textbox", { name: /email/i }), "a@b.com");
    await user.click(screen.getByRole("button", { name: /place order/i }));

    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ email: "a@b.com" }),
    );
  });

  it("disables the submit button while loading", () => {
    render(<CheckoutForm onSubmit={vi.fn()} isLoading />);

    expect(screen.getByRole("button", { name: /place order/i })).toBeDisabled();
  });
});
```

### Testing Hooks with `renderHook`

```tsx
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { useDebounce } from "./useDebounce";

describe("useDebounce", () => {
  it("returns the debounced value after the delay", async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: "hello" } },
    );

    rerender({ value: "world" });
    expect(result.current).toBe("hello"); // not yet updated

    await waitFor(() => {
      expect(result.current).toBe("world");
    });
  });
});
```

---

## Mocking Network Requests with MSW

```tsx
// tests/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/orders/:id", ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      status: "confirmed",
      total: 42.0,
    });
  }),
];

// tests/setup.ts
import { setupServer } from "msw/node";
import { handlers } from "./mocks/handlers";

export const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

- Use MSW instead of mocking `fetch` directly. MSW intercepts at the network
  level and works with any HTTP client.
- Set `onUnhandledRequest: "error"` so unmocked requests fail loudly.

---

## E2E Testing with Playwright

```ts
// tests/e2e/checkout.spec.ts
import { test, expect } from "@playwright/test";

test("user completes a checkout", async ({ page }) => {
  await page.goto("/products/widget-a");
  await page.getByRole("button", { name: /add to cart/i }).click();
  await page.getByRole("link", { name: /cart/i }).click();
  await page.getByRole("button", { name: /checkout/i }).click();

  await page.getByLabel(/email/i).fill("buyer@example.com");
  await page.getByRole("button", { name: /place order/i }).click();

  await expect(page.getByText(/order confirmed/i)).toBeVisible();
});
```

- E2E tests cover critical user journeys only. Do not replicate unit test
  coverage.
- Use accessible locators (`getByRole`, `getByLabel`) consistently.
- Run E2E in CI against a preview deployment, not localhost.

---

## Do / Don't

### Do

- Query by accessible role, label, or text (`getByRole`, `getByLabelText`, `getByText`).
- Use `userEvent` over `fireEvent` -- it simulates real user interactions (focus, keystrokes, blur).
- Test error states and loading states, not just the happy path.
- Use factories or builders for test data instead of copy-pasting objects.
- Clean up after each test (Testing Library does this automatically with `cleanup`).

### Don't

- Don't test implementation details (internal state, private methods, specific CSS classes).
- Don't use `getByTestId` unless no accessible query is possible.
- Don't mock child components in component tests unless they have expensive side effects.
- Don't write E2E tests for form validation -- unit tests cover that faster.
- Don't use `waitFor` with assertions that will never become true -- add a timeout message.
- Don't snapshot-test component trees. Snapshots are brittle and provide low signal.

---

## Common Pitfalls

1. **Testing the framework, not your code.** Asserting that `useState` works
   or that React renders children. Test your logic and behavior.
2. **Wrapping every render in `act()` manually.** Testing Library's `render`,
   `userEvent`, and `waitFor` already handle `act` batching.
3. **Overly specific assertions.** `toHaveTextContent("Total: $42.00")` breaks
   when formatting changes. Prefer `toHaveTextContent(/\$42/)` for resilience.
4. **Skipping the unhappy path.** Network errors, empty states, and permission
   denials are where bugs hide. Write tests for them.
5. **Flaky async tests.** Not waiting for elements to appear before asserting.
   Always use `findBy*` or `waitFor` for async content.

---

## Checklist

Before merging test changes:

- [ ] Tests describe user-visible behavior, not implementation details
- [ ] Queries use accessible selectors (`getByRole`, `getByLabelText`, `getByText`)
- [ ] `userEvent` is used instead of `fireEvent`
- [ ] Network requests are mocked with MSW, not `vi.mock("fetch")`
- [ ] Error and loading states have test coverage
- [ ] No snapshot tests on component trees
- [ ] E2E tests cover only critical journeys (not duplicating unit tests)
- [ ] All tests pass locally before pushing
- [ ] No `test.skip` or `test.todo` without an accompanying issue ticket
- [ ] Test data uses factories, not hardcoded inline objects
