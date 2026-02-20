# Go Testing

Testing strategy, patterns, and tooling for Go applications. Covers unit tests,
integration tests, table-driven tests, benchmarks, fuzzing, and test data
management.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| Test Framework       | `testing` (stdlib)                   | Never             |
| Assertions           | `testing` + `testify/assert`         | ADR               |
| Mocking              | Interfaces + hand-written mocks      | ADR               |
| Integration Infra    | `testcontainers-go`                  | ADR               |
| HTTP Testing         | `net/http/httptest`                  | Never             |
| Race Detection       | `go test -race`                      | Never             |
| Fuzzing              | `testing.F` (stdlib, Go 1.18+)      | Never             |
| Coverage Tool        | `go test -coverprofile`              | Never             |
| Coverage Threshold   | 80% lines                            | Never lower       |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| Hand-written mocks   | `mockgen` (gomock)   | Many interfaces to mock               |
| `testify/assert`     | `is` / `qt`          | Minimal dependency preference         |
| `testcontainers-go`  | Docker Compose       | Complex multi-service setups          |
| `go test -cover`     | `gocov` + `gocov-html` | Richer HTML coverage reports       |

---

## Table-Driven Tests

Table-driven tests are the standard Go pattern for testing functions with
multiple input/output cases.

```go
func TestParseAmount(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    int64
        wantErr bool
    }{
        {name: "valid dollars", input: "42.00", want: 4200},
        {name: "valid cents", input: "0.99", want: 99},
        {name: "no decimal", input: "100", want: 10000},
        {name: "negative", input: "-5.00", want: -500},
        {name: "empty string", input: "", wantErr: true},
        {name: "not a number", input: "abc", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseAmount(tt.input)
            if tt.wantErr {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got != tt.want {
                t.Errorf("ParseAmount(%q) = %d, want %d", tt.input, got, tt.want)
            }
        })
    }
}
```

**Rules:**
- Use `t.Run(name, func)` subtests for each case. This enables selective
  execution (`go test -run TestParseAmount/valid_dollars`).
- Name test cases descriptively: `"returns error for empty input"`, not
  `"test1"`.
- Keep test logic inside the loop body minimal. Extract helpers for complex
  assertions.
- Use `t.Helper()` in test helper functions so failure messages report the
  caller's line number.

---

## Unit Tests

Unit tests verify services and domain logic in isolation. Dependencies are
replaced with interface-based mocks.

```go
// Define the interface at the consumer.
type OrderRepository interface {
    FindByID(ctx context.Context, id string) (Order, error)
    Save(ctx context.Context, order Order) error
}

// Hand-written mock for testing.
type mockOrderRepo struct {
    findByIDFn func(ctx context.Context, id string) (Order, error)
    saveFn     func(ctx context.Context, order Order) error
}

func (m *mockOrderRepo) FindByID(ctx context.Context, id string) (Order, error) {
    return m.findByIDFn(ctx, id)
}

func (m *mockOrderRepo) Save(ctx context.Context, order Order) error {
    return m.saveFn(ctx, order)
}

func TestOrderService_CalculateTotal(t *testing.T) {
    repo := &mockOrderRepo{
        findByIDFn: func(_ context.Context, id string) (Order, error) {
            if id == "ORD-1" {
                return Order{ID: "ORD-1", Amount: 10000}, nil
            }
            return Order{}, ErrNotFound
        },
    }

    svc := NewOrderService(repo)

    t.Run("calculates total with discount", func(t *testing.T) {
        total, err := svc.CalculateTotal(context.Background(), "ORD-1", 10)
        if err != nil {
            t.Fatalf("unexpected error: %v", err)
        }
        if total != 9000 {
            t.Errorf("got %d, want 9000", total)
        }
    })

    t.Run("returns error for missing order", func(t *testing.T) {
        _, err := svc.CalculateTotal(context.Background(), "ORD-X", 10)
        if !errors.Is(err, ErrNotFound) {
            t.Errorf("got %v, want ErrNotFound", err)
        }
    })
}
```

**Rules:**
- Define interfaces at the consumer (the service), not the implementor (the
  repository).
- Hand-written mocks with function fields are simple and sufficient for most
  cases.
- Use `context.Background()` in tests unless testing cancellation behavior.
- Test both success and error paths for every public function.

---

## Integration Tests (testcontainers-go)

Integration tests run against real infrastructure using testcontainers.

```go
//go:build integration

package repository_test

import (
    "context"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestOrderRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test in short mode")
    }

    ctx := context.Background()

    pgContainer, err := postgres.Run(ctx, "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        t.Fatalf("failed to start postgres: %v", err)
    }
    t.Cleanup(func() { pgContainer.Terminate(ctx) })

    connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
    if err != nil {
        t.Fatalf("failed to get connection string: %v", err)
    }

    repo := NewPostgresOrderRepo(connStr)

    t.Run("saves and retrieves order", func(t *testing.T) {
        order := Order{ID: "ORD-1", Amount: 5000}
        if err := repo.Save(ctx, order); err != nil {
            t.Fatalf("save failed: %v", err)
        }

        got, err := repo.FindByID(ctx, "ORD-1")
        if err != nil {
            t.Fatalf("find failed: %v", err)
        }
        if got.Amount != 5000 {
            t.Errorf("amount = %d, want 5000", got.Amount)
        }
    })
}
```

**Rules:**
- Use build tags (`//go:build integration`) to separate integration tests from
  unit tests.
- Use `testing.Short()` as a secondary skip mechanism for `go test -short`.
- Use `t.Cleanup()` to tear down containers. It runs even if the test fails.
- Pin container image tags for reproducibility (`postgres:16-alpine`, not
  `postgres:latest`).
- Never use SQLite as a stand-in for Postgres in integration tests.

---

## HTTP Handler Tests

```go
func TestOrderHandler_Create(t *testing.T) {
    svc := &mockOrderService{
        createFn: func(_ context.Context, req CreateOrderRequest) (Order, error) {
            return Order{ID: "ORD-1", ProductID: req.ProductID, Quantity: req.Quantity}, nil
        },
    }
    handler := NewOrderHandler(svc)

    body := strings.NewReader(`{"product_id": "P-1", "quantity": 2}`)
    req := httptest.NewRequest(http.MethodPost, "/v1/orders", body)
    req.Header.Set("Content-Type", "application/json")
    rec := httptest.NewRecorder()

    handler.Create(rec, req)

    if rec.Code != http.StatusCreated {
        t.Errorf("status = %d, want %d", rec.Code, http.StatusCreated)
    }

    var resp Order
    if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
        t.Fatalf("decode response: %v", err)
    }
    if resp.ProductID != "P-1" {
        t.Errorf("product_id = %q, want %q", resp.ProductID, "P-1")
    }
}
```

**Rules:**
- Use `httptest.NewRequest` and `httptest.NewRecorder` for handler tests.
- Test status codes, response bodies, and headers.
- Mock the service layer, not the HTTP layer.
- Test error responses (400, 404, 500) as thoroughly as success responses.

---

## Benchmarks and Fuzzing

```go
// Benchmark
func BenchmarkParseAmount(b *testing.B) {
    for b.Loop() {
        ParseAmount("42.99")
    }
}

// Fuzz test (Go 1.18+)
func FuzzParseAmount(f *testing.F) {
    f.Add("42.00")
    f.Add("0.99")
    f.Add("")

    f.Fuzz(func(t *testing.T, input string) {
        _, err := ParseAmount(input)
        if err != nil {
            t.Skip() // Invalid input is expected; skip, don't fail.
        }
    })
}
```

**Rules:**
- Write benchmarks for performance-critical code paths (serialization, hashing,
  hot loops).
- Use `b.Loop()` (Go 1.24+) or `b.N` for benchmark iterations.
- Run benchmarks with `go test -bench=. -benchmem` to include allocation stats.
- Use fuzz tests for parsers, deserializers, and any function that processes
  untrusted input.
- Seed the fuzz corpus with representative valid and invalid inputs.

---

## Do / Don't

### Do
- Use table-driven tests for all functions with multiple input/output cases.
- Use `t.Run()` subtests for descriptive test names and selective execution.
- Use `t.Helper()` in test helper functions.
- Use `t.Parallel()` for independent tests to speed up the suite.
- Run `go test -race` in CI on every push.
- Use `testdata/` directories for fixture files (ignored by the Go tool).
- Test error messages and error types, not just "an error occurred".

### Don't
- Use `assert` libraries as a crutch -- `if got != want` is clear and idiomatic.
- Skip error path tests. Error paths are where bugs hide.
- Use `time.Sleep` in tests. Use channels, `sync.WaitGroup`, or context
  cancellation for synchronization.
- Test private functions directly. Test the public API; private functions are
  implementation details.
- Share mutable state across parallel subtests without synchronization.
- Use `os.Setenv` in parallel tests -- environment is process-global.

---

## Common Pitfalls

1. **Flaky tests from shared state** -- Tests that modify package-level
   variables or shared resources fail intermittently. Use `t.Parallel()` only
   when state is isolated.
2. **Missing `t.Helper()` in helpers** -- Without it, test failures report the
   helper's line number, not the caller's. Always call `t.Helper()` as the
   first line.
3. **Race conditions in tests** -- Parallel subtests accessing shared variables
   without locks. Run `go test -race` to catch these.
4. **Test setup in `init()`** -- `init()` runs for all tests, not just the ones
   that need the setup. Use `TestMain` or per-test setup.
5. **Ignoring `t.Cleanup()`** -- Manual cleanup in `defer` doesn't compose
   well. `t.Cleanup()` runs after the test and all its subtests complete.
6. **Testing implementation, not behavior** -- Tests that assert on internal
   function calls rather than observable outputs break on every refactor.
7. **Benchmarks that optimize away** -- The compiler may eliminate dead code in
   benchmarks. Assign results to a package-level `sink` variable or use
   `b.Loop()` which prevents elimination.

---

## Checklist

- [ ] Unit tests cover new/changed service and domain logic.
- [ ] Table-driven tests used for multi-case functions.
- [ ] Integration tests cover new/changed endpoints (success + error paths).
- [ ] Integration tests use `testcontainers-go` with pinned image tags.
- [ ] `go test -race` enabled in CI; no data races.
- [ ] `go test -short` skips integration tests for fast local feedback.
- [ ] Coverage meets or exceeds 80% lines (`go test -coverprofile`).
- [ ] Benchmarks written for performance-critical paths.
- [ ] Fuzz tests written for parsers and input processors.
- [ ] `t.Helper()` called in all test helper functions.
- [ ] `t.Parallel()` used for independent tests.
- [ ] No `time.Sleep` in tests; proper synchronization used.
- [ ] Test method names describe behavior, not implementation.
