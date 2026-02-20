# Go Stack Conventions

Non-negotiable defaults for Go services on this team. Targets Go 1.22+ with
the standard library as the primary dependency. Deviations require an ADR with
justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| Go Version           | 1.22+ (latest stable)                | ADR               |
| Module System        | Go modules (`go.mod`)                | Never             |
| Formatter            | `gofmt` / `goimports`                | Never             |
| Linter               | `golangci-lint`                      | ADR               |
| Logging              | `log/slog` (structured)              | ADR               |
| HTTP Framework       | `net/http` (stdlib, Go 1.22+ routing)| ADR               |
| Config               | Environment variables + `envconfig`  | ADR               |
| Dependency Injection | Constructor functions (no framework) | Never             |
| Error Handling       | Explicit `error` returns             | Never             |
| Concurrency          | Goroutines + channels + `sync`       | Never             |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| `net/http`           | Chi / Echo / Gin     | Complex routing needs beyond stdlib   |
| `log/slog`           | Zap / Zerolog        | Extreme throughput (>100k msg/s)      |
| `envconfig`          | Viper                | Complex config (files + env + flags)  |
| `golangci-lint`      | `staticcheck` alone  | Minimal CI setup                      |
| `encoding/json`      | `json-iterator`      | Hot-path JSON where stdlib is too slow|

---

## Project Structure

```
project-root/
  cmd/
    server/
      main.go                    # Entry point: config, wiring, server start
  internal/
    config/
      config.go                  # Configuration struct + loading
    handler/
      order.go                   # HTTP handlers (thin, delegates to service)
      order_test.go
    service/
      order.go                   # Business logic (no HTTP dependency)
      order_test.go
    repository/
      order.go                   # Data access (database, external APIs)
      order_test.go
    model/
      order.go                   # Domain types, value objects
    middleware/
      logging.go                 # HTTP middleware (auth, logging, recovery)
  pkg/                           # Public library code (only if needed)
  migrations/
    001_create_orders.sql
  go.mod
  go.sum
  Makefile
  Dockerfile
  README.md
```

**Rules:**
- `cmd/` contains entry points only: parse config, wire dependencies, start
  the server. No business logic.
- `internal/` prevents external imports. All application code lives here.
- Handlers are thin: parse request, call service, write response. No business
  logic in handlers.
- Services accept and return domain types, not `*http.Request` or
  `http.ResponseWriter`.
- `pkg/` is only for code intentionally shared with other modules. Default to
  `internal/`.
- One `main.go` per binary in `cmd/<binary-name>/`.

---

## Error Handling

```go
// Define sentinel errors for known conditions.
var (
    ErrNotFound   = errors.New("not found")
    ErrConflict   = errors.New("conflict")
    ErrForbidden  = errors.New("forbidden")
)

// Wrap errors with context using fmt.Errorf.
func (s *OrderService) GetOrder(ctx context.Context, id string) (Order, error) {
    order, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return Order{}, fmt.Errorf("get order %s: %w", id, err)
    }
    return order, nil
}

// Callers check with errors.Is / errors.As.
order, err := svc.GetOrder(ctx, id)
if errors.Is(err, ErrNotFound) {
    http.Error(w, "order not found", http.StatusNotFound)
    return
}
if err != nil {
    http.Error(w, "internal error", http.StatusInternalServerError)
    return
}
```

**Rules:**
- Always check returned errors. Never use `_` to discard an error.
- Wrap errors with `fmt.Errorf("context: %w", err)` to build a chain.
- Use `errors.Is` and `errors.As` for typed error checks, not string matching.
- Define sentinel errors (`var ErrNotFound = errors.New(...)`) for conditions
  callers need to distinguish.
- Do not use `panic` for expected error conditions. Reserve `panic` for
  programmer bugs (impossible states).
- Return errors; do not log and return. The caller decides how to handle them.

---

## Concurrency

```go
// Fan-out with errgroup for bounded concurrency.
func (s *Service) ProcessBatch(ctx context.Context, ids []string) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // bounded concurrency

    for _, id := range ids {
        g.Go(func() error {
            return s.processOne(ctx, id)
        })
    }
    return g.Wait()
}

// Channel for producer-consumer pipelines.
func generate(ctx context.Context, items []int) <-chan int {
    ch := make(chan int)
    go func() {
        defer close(ch)
        for _, item := range items {
            select {
            case ch <- item:
            case <-ctx.Done():
                return
            }
        }
    }()
    return ch
}
```

**Rules:**
- Always pass `context.Context` as the first parameter to functions that do
  I/O or long-running work. Respect cancellation via `ctx.Done()`.
- Use `errgroup` for fan-out with error propagation. Set concurrency limits
  with `g.SetLimit(n)`.
- Prefer channels for communication, `sync.Mutex` for protecting shared state.
- Never start a goroutine without a plan for how it stops. Use context
  cancellation, `done` channels, or `sync.WaitGroup`.
- Close channels from the sender side only. Never close from the receiver.
- Use `sync.Once` for one-time initialization, not `sync.Mutex` with a flag.

---

## Naming Conventions

| Element              | Convention         | Example                      |
|----------------------|--------------------|------------------------------|
| Packages             | `lowercase`        | `order`, `httputil`          |
| Exported types       | `PascalCase`       | `OrderService`               |
| Unexported types     | `camelCase`        | `orderCache`                 |
| Functions            | `PascalCase`/`camelCase` | `NewOrderService()` / `validate()` |
| Constants            | `PascalCase`       | `MaxRetryCount`              |
| Interfaces           | `-er` suffix       | `Reader`, `Storer`, `Notifier` |
| Test functions       | `Test` prefix      | `TestOrderService_GetOrder`  |
| Acronyms             | All caps           | `HTTPClient`, `userID`       |

**Rules:**
- Package names are singular nouns: `order`, not `orders`.
- No `util`, `common`, `misc` packages. Name packages after what they provide.
- Interface names use `-er` suffix when describing a single behavior: `Reader`,
  `Writer`, `Closer`.
- Getters omit `Get`: use `o.Name()`, not `o.GetName()`.
- Accept interfaces, return structs. This keeps APIs flexible and concrete.
- Acronyms are all-caps in identifiers: `ID`, `HTTP`, `URL`, not `Id`, `Http`.

---

## Logging

```go
import "log/slog"

// Initialize structured logger at startup.
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))
slog.SetDefault(logger)

// Use structured key-value pairs.
slog.Info("order_processing_started",
    "order_id", orderID,
    "customer_id", customerID,
)

// Include errors as structured fields.
slog.Error("order_processing_failed",
    "order_id", orderID,
    "error", err,
)
```

**Rules:**
- Use `log/slog` for structured logging. Never use `fmt.Println` or `log.Printf`
  for operational messages.
- Use JSON handler in production, text handler in development.
- Log levels: `Debug` for developer diagnostics, `Info` for operational events,
  `Warn` for recoverable problems, `Error` for failures requiring attention.
- Use event-name style messages (`order_processing_started`) with key-value
  context.
- Never log secrets, tokens, passwords, or full PII.
- Pass logger via context or constructor injection. Avoid package-level loggers
  in libraries.

---

## Do / Don't

### Do
- Use `context.Context` as the first parameter for all I/O and cancellable work.
- Return errors explicitly; handle every returned error.
- Use `defer` for cleanup (closing files, releasing locks, flushing buffers).
- Keep interfaces small (1-3 methods). Define them at the consumer, not the
  implementor.
- Use table-driven tests for functions with multiple input/output cases.
- Run `gofmt` and `golangci-lint` before every commit.
- Use `go vet` and `race detector` (`go test -race`) in CI.

### Don't
- Use `init()` functions. They create hidden dependencies and initialization
  order problems. Pass dependencies explicitly.
- Use global mutable state. Pass dependencies via constructors.
- Ignore the `context.Context` parameter. Always check `ctx.Err()` in loops and
  pass `ctx` to downstream calls.
- Use bare goroutines without lifecycle management. Leaked goroutines are memory
  leaks.
- Name packages `util`, `helpers`, `common`, or `misc`.
- Return interfaces from constructors. Return concrete types; accept interfaces.
- Use `panic` for error handling in library code.

---

## Common Pitfalls

1. **Goroutine leaks** -- Starting goroutines without a shutdown mechanism
   (context cancellation, done channel, or WaitGroup) causes memory leaks.
   Every goroutine must have a defined exit path.
2. **Nil pointer on interface values** -- A nil pointer stored in an interface
   is not a nil interface. `var err *MyError = nil; var e error = err; e != nil`
   is `true`. Return plain `nil`, not typed nil pointers.
3. **Data races** -- Concurrent access to shared state without synchronization.
   Always run `go test -race` in CI. Use `sync.Mutex` or channels to protect
   shared data.
4. **Deferred close ignoring errors** -- `defer f.Close()` discards the error
   from `Close()`. For writable resources, capture the error:
   `defer func() { err = errors.Join(err, f.Close()) }()`.
5. **Copying sync types** -- `sync.Mutex`, `sync.WaitGroup`, and `sync.Once`
   must not be copied after first use. Pass them by pointer, or embed them in
   a struct that is passed by pointer.
6. **Oversized structs by value** -- Passing large structs by value in hot
   paths causes excessive copying. Use pointer receivers for structs with more
   than a few fields.
7. **Forgetting to drain channels** -- A goroutine blocked on sending to a
   channel that nobody reads is a leak. Always drain or cancel.

---

## Checklist

- [ ] Go 1.22+ targeted in `go.mod`.
- [ ] `gofmt` / `goimports` applied; CI rejects unformatted code.
- [ ] `golangci-lint` runs in CI; no new warnings introduced.
- [ ] All errors checked; no discarded errors (`_`).
- [ ] Errors wrapped with context (`fmt.Errorf("...: %w", err)`).
- [ ] `context.Context` passed as first parameter for I/O functions.
- [ ] All goroutines have a defined shutdown path (context, done channel, WaitGroup).
- [ ] `go test -race` enabled in CI; no data races.
- [ ] `log/slog` used for structured logging; no `fmt.Println` or `log.Printf`.
- [ ] No `init()` functions; dependencies injected via constructors.
- [ ] Interfaces defined at the consumer, not the implementor.
- [ ] No secrets in source code, logs, or committed config files.
