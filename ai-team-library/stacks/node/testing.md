# Node.js Testing

Testing strategy, patterns, and tooling for Node.js applications. Covers unit
tests, integration tests, HTTP endpoint tests, and test data management.

---

## Defaults

| Concern             | Default Choice                 | Override Requires |
|---------------------|--------------------------------|-------------------|
| Test Runner         | Vitest                         | ADR               |
| HTTP Testing        | Fastify `.inject()` / Supertest| ADR               |
| Mocking             | Vitest built-in (`vi.fn()`)    | ADR               |
| Containers          | Testcontainers                 | ADR               |
| Coverage Tool       | `v8` provider (Vitest built-in)| ADR               |
| Coverage Threshold  | 80 % lines, branch preferred   | Never lower       |
| Assertion Style     | `expect` (Vitest native)       | Never             |

### Alternatives

| Primary        | Alternative    | When                                  |
|----------------|----------------|---------------------------------------|
| Vitest         | Jest           | Existing Jest codebase, not worth migrating |
| `.inject()`    | Supertest      | Express projects                      |
| Testcontainers | Docker Compose | Complex multi-service topology        |
| `v8` coverage  | `istanbul`     | Rare edge cases with v8 gaps          |

---

## Unit Tests

Unit tests cover services and utility functions in isolation. External
dependencies (databases, HTTP clients) are injected and stubbed.

```typescript
// src/services/pricing-service.test.ts
import { describe, it, expect, vi } from "vitest";
import { PricingService } from "./pricing-service.js";

describe("PricingService", () => {
  const mockRepo = { findDiscount: vi.fn() };

  it("applies percentage discount to base price", async () => {
    mockRepo.findDiscount.mockResolvedValue({ type: "percent", value: 10 });

    const service = new PricingService(mockRepo);
    const result = await service.calculate("ITEM-1", 100);

    expect(result).toEqual({ base: 100, discount: 10, total: 90 });
    expect(mockRepo.findDiscount).toHaveBeenCalledWith("ITEM-1");
  });

  it("returns full price when no discount exists", async () => {
    mockRepo.findDiscount.mockResolvedValue(null);

    const service = new PricingService(mockRepo);
    const result = await service.calculate("ITEM-2", 50);

    expect(result).toEqual({ base: 50, discount: 0, total: 50 });
  });
});
```

**Rules:**
- Inject dependencies via constructor. Never mock modules with `vi.mock()`
  for business logic dependencies -- it couples tests to file paths.
- Keep tests fast (<5 ms each). Anything slower belongs in integration tests.
- One assertion concept per test. Multiple `expect` calls are fine when they
  verify a single logical outcome.

---

## Integration Tests

Integration tests verify the full request-response cycle against real
infrastructure (databases, caches, queues).

```typescript
// tests/integration/orders.test.ts
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { PostgreSqlContainer } from "@testcontainers/postgresql";
import { buildApp } from "../../src/app.js";

describe("POST /v1/orders", () => {
  let container: Awaited<ReturnType<typeof PostgreSqlContainer.prototype.start>>;
  let app: Awaited<ReturnType<typeof buildApp>>;

  beforeAll(async () => {
    container = await new PostgreSqlContainer().start();
    app = await buildApp({ databaseUrl: container.getConnectionUri() });
    await app.ready();
  }, 30_000);

  afterAll(async () => {
    await app.close();
    await container.stop();
  });

  it("creates an order and returns 201", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/v1/orders",
      payload: { productId: "P-1", quantity: 2 },
    });

    expect(res.statusCode).toBe(201);
    expect(res.json()).toMatchObject({
      id: expect.any(String),
      productId: "P-1",
      quantity: 2,
    });
  });

  it("returns 400 for missing required fields", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/v1/orders",
      payload: {},
    });

    expect(res.statusCode).toBe(400);
  });
});
```

**Rules:**
- Never mock the database in integration tests. Use Testcontainers.
- Set a generous `beforeAll` timeout (30 s) for container startup.
- Clean state between tests with transactions or truncation, not by restarting
  the container.

---

## Do / Don't

### Do
- Name test files `<module>.test.ts`, co-located or in `tests/unit/`.
- Use descriptive test names: `it("returns 404 when order does not exist")`.
- Run tests in CI on every push; a failing test blocks merge.
- Test error paths as thoroughly as success paths.
- Use `vi.useFakeTimers()` for time-dependent logic instead of `setTimeout` hacks.
- Prefer `toMatchObject` over `toEqual` when you only care about a subset of fields.

### Don't
- Use `vi.mock()` for internal modules -- it creates brittle path-coupled tests.
- Share mutable state between tests without resetting in `beforeEach`.
- Write tests that depend on execution order.
- Ignore flaky tests -- fix them immediately or quarantine with a tracking issue.
- Test private methods directly. Test the public API that exercises them.
- Use snapshots for dynamic data (timestamps, UUIDs).

---

## Common Pitfalls

1. **Leaked handles** -- Open database connections or timers prevent Vitest from
   exiting. Use `afterAll` to close everything and run with `--detectOpenHandles`.
2. **Port conflicts** -- Hardcoded ports collide in parallel test suites. Let
   Fastify bind to port `0` or use `.inject()` which skips the network layer.
3. **Flaky container tests** -- Testcontainer startup can be slow on cold pulls.
   Pin container image tags and use a local registry or CI cache.
4. **Over-mocking** -- Mocking every layer means your tests verify mock wiring,
   not behavior. A thin integration test via `.inject()` catches more bugs.
5. **Missing error-path tests** -- Teams test the happy path and skip 400/404/500
   scenarios. Error paths are where most production bugs hide.
6. **Coverage gaming** -- Hitting 80 % by testing trivial getters while ignoring
   complex branching logic. Branch coverage is the meaningful metric.

---

## Checklist

- [ ] Unit tests cover new/changed business logic.
- [ ] Integration tests cover new/changed endpoints (success + error paths).
- [ ] No `vi.mock()` for internal business modules (use dependency injection).
- [ ] `beforeEach` / `afterEach` reset shared state.
- [ ] Tests pass locally **and** in CI with identical results.
- [ ] Coverage meets or exceeds 80 % lines, branch coverage reviewed.
- [ ] No hardcoded ports, timestamps, or random values causing flakiness.
- [ ] Testcontainer images pinned to specific tags.
- [ ] Test names are descriptive and follow the `it("does X when Y")` pattern.
- [ ] No skipped tests (`it.skip`) without a linked tracking issue.
