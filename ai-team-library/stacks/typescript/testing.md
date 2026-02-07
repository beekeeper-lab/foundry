# TypeScript Testing

Testing TypeScript code effectively means leveraging the type system in tests,
ensuring type-safe mocks, and validating behavior at type boundaries. The type
system catches shape errors at compile time; tests catch logic errors at runtime.

---

## Defaults

- **Test runner:** Vitest (ESM-native, TypeScript-native, fast).
- **Assertion style:** Vitest built-in `expect` with strict equality.
- **Mocking:** Vitest `vi.mock()` and `vi.fn()` with typed signatures.
- **Runtime validation tests:** Test Zod schemas against valid and invalid payloads.
- **Coverage:** 80% line coverage on business logic. No hard target on type utilities.
- **CI gate:** All tests pass. Type checking (`tsc --noEmit`) runs as a separate CI step.

### Alternatives

| Default  | Alternative | When to consider                         |
|----------|-------------|------------------------------------------|
| Vitest   | Jest        | Existing Jest setup; migration not worth it |
| Vitest   | Node test   | Zero-dependency requirement, Node >= 20  |

---

## Test File Organization

```
src/
  features/
    orders/
      orderUtils.ts
      orderUtils.test.ts        # Co-located unit test
      types.ts
  lib/
    validation.ts
    validation.test.ts          # Co-located unit test
tests/
  integration/                  # Cross-module integration tests
  helpers/
    factories.ts                # Typed test data factories
```

- Co-locate unit tests next to source files.
- Integration tests that span modules live in `tests/integration/`.
- Test data factories live in `tests/helpers/` and return fully typed objects.

---

## Type-Safe Test Factories

Create typed factories to avoid duplicating test data and to keep tests resilient
to type changes.

```ts
// tests/helpers/factories.ts
import type { User, Order } from "../../src/features/orders/types";

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: "u-001",
    name: "Test User",
    email: "test@example.com",
    role: "member",
    ...overrides,
  };
}

export function buildOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: "o-001",
    userId: "u-001",
    status: "pending",
    items: [],
    total: 0,
    ...overrides,
  };
}
```

```ts
// Usage in tests
import { buildUser } from "../helpers/factories";

it("formats the user greeting", () => {
  const user = buildUser({ name: "Alice" });
  expect(formatGreeting(user)).toBe("Hello, Alice!");
});
```

When the `User` type adds a required field, the factory breaks at compile time,
forcing you to update it once (not in every test).

---

## Type-Safe Mocking

Use typed function mocks to ensure mocks match the real signature.

```ts
import { vi, describe, it, expect } from "vitest";
import type { OrderRepository } from "./orderRepository";

// Type-safe mock: matches the real function signature
const mockFindById = vi.fn<Parameters<OrderRepository["findById"]>, ReturnType<OrderRepository["findById"]>>();

// Or use satisfies for an object mock
const mockRepo = {
  findById: vi.fn(),
  save: vi.fn(),
} satisfies Record<keyof OrderRepository, ReturnType<typeof vi.fn>>;

describe("OrderService", () => {
  it("returns the order when found", async () => {
    mockRepo.findById.mockResolvedValue(buildOrder({ id: "o-42" }));

    const service = new OrderService(mockRepo);
    const order = await service.getOrder("o-42");

    expect(order.id).toBe("o-42");
    expect(mockRepo.findById).toHaveBeenCalledWith("o-42");
  });
});
```

---

## Testing Zod Schemas

Zod schemas are a critical boundary -- test them with both valid and invalid
payloads.

```ts
import { describe, it, expect } from "vitest";
import { UserSchema } from "./schemas";

describe("UserSchema", () => {
  it("parses a valid user", () => {
    const input = { id: "550e8400-e29b-41d4-a716-446655440000", name: "Alice", email: "a@b.com", role: "admin" };
    const result = UserSchema.safeParse(input);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.name).toBe("Alice");
    }
  });

  it("rejects a user with an invalid email", () => {
    const input = { id: "550e8400-e29b-41d4-a716-446655440000", name: "Alice", email: "not-an-email", role: "admin" };
    const result = UserSchema.safeParse(input);

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain("email");
    }
  });

  it("rejects unknown roles", () => {
    const input = { id: "550e8400-e29b-41d4-a716-446655440000", name: "Alice", email: "a@b.com", role: "superadmin" };
    const result = UserSchema.safeParse(input);

    expect(result.success).toBe(false);
  });
});
```

---

## Testing Discriminated Unions

Ensure every branch of a discriminated union is tested.

```ts
import { describe, it, expect } from "vitest";

type Result = { status: "ok"; value: number } | { status: "error"; message: string };

function describeResult(r: Result): string {
  switch (r.status) {
    case "ok":
      return `Value: ${r.value}`;
    case "error":
      return `Error: ${r.message}`;
  }
}

describe("describeResult", () => {
  it("describes the ok variant", () => {
    expect(describeResult({ status: "ok", value: 42 })).toBe("Value: 42");
  });

  it("describes the error variant", () => {
    expect(describeResult({ status: "error", message: "fail" })).toBe("Error: fail");
  });
});
```

---

## Do / Don't

### Do

- Use typed factories for test data. Update the factory when types change.
- Test Zod schemas with valid, invalid, and edge-case payloads.
- Run `tsc --noEmit` in CI as a separate step from tests.
- Use `satisfies` to type-check mock objects against real interfaces.
- Test every variant of a discriminated union.

### Don't

- Don't use `as any` in tests to bypass type errors. Fix the type or the test.
- Don't test TypeScript utility types at runtime -- they exist only at compile time.
- Don't skip schema validation tests because "the type system covers it." Types
  don't exist at runtime; schemas do.
- Don't write tests that only assert `typeof x === "object"`. Assert the specific shape.
- Don't mock implementations you don't own. Wrap third-party libraries and mock the wrapper.

---

## Common Pitfalls

1. **`as any` in tests.** Tests silently pass with the wrong shape, then the
   real code fails at runtime. Use factories and proper types.
2. **Not testing the sad path of schemas.** Validating that a schema accepts
   correct data is half the job. Test that it rejects malformed data.
3. **Mocks drifting from real interfaces.** An untyped mock passes tests even
   after the real interface changes. Use `satisfies` or typed mocks.
4. **Testing types at runtime.** Writing `expect(typeof result).toBe("object")`
   when you should be using a type guard or Zod parse. The type system handles
   compile-time; tests handle runtime behavior.
5. **Ignoring `tsc` errors in CI.** Tests pass because Vitest transpiles without
   type checking. A separate `tsc --noEmit` step catches type errors that tests miss.

---

## Checklist

Before merging test changes:

- [ ] Test data uses typed factories, not inline object literals
- [ ] Mocks are typed with `satisfies` or explicit generic parameters
- [ ] Zod schemas tested with valid, invalid, and edge-case inputs
- [ ] Every variant of discriminated unions has a test case
- [ ] No `as any` in test files (search for it)
- [ ] `tsc --noEmit` runs as a separate CI step alongside tests
- [ ] Coverage meets 80% threshold on business logic modules
- [ ] Integration tests exist for cross-module interactions
- [ ] Test file co-located with source file (`*.test.ts` next to `*.ts`)
- [ ] Factories updated when source types change
