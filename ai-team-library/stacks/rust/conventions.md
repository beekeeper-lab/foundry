# Rust Stack Conventions

Non-negotiable defaults for Rust projects on this team. Rust's ownership model,
zero-cost abstractions, and memory safety guarantees demand specific conventions
that differ significantly from garbage-collected languages. Deviations require
an ADR with justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                       | Alternatives (ADR Required) |
|----------------------|--------------------------------------|-----------------------------|
| Rust Edition         | 2024 (latest stable)                 | 2021 for legacy codebases   |
| Build Tool           | `cargo`                              | Never                       |
| Formatter            | `rustfmt`                            | Never                       |
| Linter               | `clippy` (pedantic preset)           | Never                       |
| Error Handling       | `thiserror` (libraries), `anyhow` (applications) | `eyre`, `miette`  |
| Async Runtime        | `tokio` (multi-threaded)             | `async-std`, `smol`         |
| Serialization        | `serde` + `serde_json`               | Never                       |
| HTTP Framework       | `axum`                               | `actix-web`, `warp`         |
| Test Framework       | Built-in `#[test]` + `cargo test`    | `nextest` for runner        |
| Logging              | `tracing` (structured)               | `log` + `env_logger`        |
| Dependency Audit     | `cargo-deny` + `cargo-audit`         | Never                       |

---

## 1. Project Structure

```
project-root/
  src/
    main.rs              # Binary entry point (thin: parse args, call run())
    lib.rs               # Library root (public API re-exports)
    config.rs            # Configuration loading (env vars, files)
    error.rs             # Error types (thiserror enums)
    models/              # Domain types and data structures
    services/            # Business logic (stateless functions/structs)
    handlers/            # HTTP handlers / API routes (thin, delegates to services)
    db/                  # Data access layer (queries, connection pool)
  tests/
    integration/         # Integration tests (separate binary targets)
  benches/               # Criterion benchmarks
  Cargo.toml             # Package metadata and dependencies
  Cargo.lock             # Committed for binaries, not for libraries
  rust-toolchain.toml    # Pin toolchain version
  clippy.toml            # Clippy configuration
  .cargo/
    config.toml          # Cargo configuration (linker, target settings)
  README.md
```

**Rules:**
- Binary crates have a thin `main.rs` that calls into `lib.rs`. This makes the
  library testable without running the binary.
- One crate per repository for simple projects. Use a Cargo workspace for
  multi-crate projects.
- Public API surface is controlled through `pub` visibility in `lib.rs`. Do not
  make internal modules `pub` unless they are part of the API.
- Commit `Cargo.lock` for binaries and applications. Do not commit it for
  libraries.

---

## 2. Ownership and Borrowing

Ownership is Rust's core differentiator. These rules prevent fights with the
borrow checker and produce idiomatic code.

- **Prefer borrowing over cloning.** Pass `&T` or `&mut T` unless the function
  needs to own the data. Clone only when ownership transfer is required or the
  cost is measured and acceptable.
- **Use `Cow<'_, str>`** for functions that sometimes need to allocate and
  sometimes do not. Avoid allocating a `String` when a `&str` suffices.
- **Minimize lifetime annotations.** If the compiler can infer lifetimes through
  elision rules, do not annotate them. Explicit lifetimes signal a non-trivial
  relationship.
- **Avoid self-referential structs.** They require `Pin` and are error-prone.
  Restructure data so the reference and the data live in separate structs.
- **Prefer `to_owned()` over `clone()`** when converting borrowed data to owned
  (e.g., `&str` to `String`), as it signals intent more clearly.
- **Use `impl Into<String>` or `impl AsRef<str>`** for function parameters that
  accept both `&str` and `String`, reducing caller friction.

```rust
// Good: borrows when possible, owns when needed
fn process_name(name: &str) -> String {
    name.to_uppercase()
}

// Good: accepts both &str and String
fn set_label(label: impl Into<String>) {
    let _owned: String = label.into();
}

// Bad: unnecessary clone
fn process_name_bad(name: String) -> String {
    name.to_uppercase() // Could have taken &str
}
```

---

## 3. Error Handling

**Libraries use `thiserror`; applications use `anyhow`.** Never use
`unwrap()` or `expect()` in production paths.

```rust
// Library: structured errors with thiserror
use thiserror::Error;

#[derive(Debug, Error)]
pub enum OrderError {
    #[error("order {id} not found")]
    NotFound { id: String },
    #[error("payment declined: {reason}")]
    PaymentDeclined { reason: String },
    #[error("database error")]
    Database(#[from] sqlx::Error),
}

// Application: anyhow for ad-hoc context
use anyhow::{Context, Result};

fn load_config() -> Result<Config> {
    let contents = std::fs::read_to_string("config.toml")
        .context("failed to read config.toml")?;
    let config: Config = toml::from_str(&contents)
        .context("failed to parse config.toml")?;
    Ok(config)
}
```

**Rules:**
- Every public function returns `Result<T, E>` where `E` is a domain-specific
  error type, not `Box<dyn Error>`.
- Use the `?` operator for propagation. Do not write manual `match` on `Result`
  unless you need to handle a specific variant.
- `unwrap()` is only allowed in tests and code paths proven unreachable. Use
  `expect("reason")` with a message explaining why it cannot fail.
- Convert foreign errors with `#[from]` or `.context()`. Do not discard the
  original error.
- Use `Result` for recoverable errors and `panic!` only for programmer bugs
  (invariant violations).

---

## 4. Unsafe Code

**Default: no `unsafe`.** Every `unsafe` block requires justification and a
`// SAFETY:` comment explaining the invariants upheld.

```rust
// SAFETY: `ptr` is non-null and properly aligned because it comes from
// `Vec::as_ptr()` on a non-empty vec, and we hold a shared reference
// to the vec for the lifetime of this access.
unsafe {
    *ptr.add(index)
}
```

**Rules:**
- Audit all `unsafe` blocks during code review. They need the same scrutiny as
  security-sensitive code.
- Prefer safe abstractions from well-audited crates (`bytemuck`, `zerocopy`)
  over hand-written `unsafe`.
- Encapsulate `unsafe` in a safe wrapper with a documented safety contract.
  Callers should not need to reason about memory safety.
- Use `#![deny(unsafe_code)]` at the crate root for crates that should contain
  no `unsafe`. Opt in per-module with `#[allow(unsafe_code)]` only when needed.
- Run `cargo miri test` in CI to detect undefined behavior in `unsafe` code.
- Avoid `unsafe` for performance unless profiling confirms a measurable gain.

---

## 5. Concurrency

Rust's type system prevents data races at compile time, but deadlocks and
logical races remain possible.

```rust
// Good: message passing with channels
use tokio::sync::mpsc;

let (tx, mut rx) = mpsc::channel(100);
tokio::spawn(async move {
    while let Some(msg) = rx.recv().await {
        process(msg).await;
    }
});

// Good: shared state with Arc<Mutex<T>>
use std::sync::Arc;
use tokio::sync::Mutex;

let state = Arc::new(Mutex::new(AppState::default()));
let state_clone = Arc::clone(&state);
tokio::spawn(async move {
    let mut guard = state_clone.lock().await;
    guard.update();
});
```

**Rules:**
- **Prefer message passing** (`mpsc`, `oneshot`, `broadcast` channels) over
  shared state. Channels are easier to reason about and compose.
- **Use `Arc<T>` for shared ownership** across threads. Never use raw pointers
  for cross-thread sharing.
- **Use `tokio::sync::Mutex`** in async code, not `std::sync::Mutex`. Holding a
  `std::sync::Mutex` guard across an `.await` blocks the runtime thread.
- **Keep critical sections short.** Lock, copy the data you need, unlock. Do not
  perform I/O while holding a lock.
- **Use `tokio::spawn`** for CPU-bound work in async contexts via
  `tokio::task::spawn_blocking`. Do not block the async executor.
- **Avoid `Rc<T>`** in multithreaded code. `Rc` is not `Send`; the compiler will
  reject it, but reaching for it signals a design issue.
- **Use `RwLock`** when reads vastly outnumber writes. Default to `Mutex` when
  unsure.

---

## 6. Performance

Rust provides zero-cost abstractions, but idiomatic code still requires
awareness of allocation and copying patterns.

- **Avoid unnecessary allocations.** Reuse buffers, use `&str` instead of
  `String` in read-only contexts, prefer stack-allocated arrays over `Vec` for
  small, fixed-size collections.
- **Use iterators, not index loops.** Iterator chains enable compiler
  optimizations (vectorization, bounds-check elimination) that indexed loops
  prevent.
- **Profile before optimizing.** Use `criterion` for microbenchmarks and
  `cargo flamegraph` for CPU profiling. Do not guess at bottlenecks.
- **Prefer `Vec::with_capacity`** when the size is known or estimable. This
  avoids repeated reallocations.
- **Use `#[inline]` sparingly.** The compiler's inlining heuristics are good.
  Only annotate after benchmarking proves a gain.
- **Avoid `Box<dyn Trait>` in hot paths.** Dynamic dispatch has overhead. Use
  generics (`impl Trait` or `<T: Trait>`) for monomorphized, inlined code.
- **Use `SmallVec` or `ArrayVec`** for collections that are almost always small
  but occasionally need heap allocation.

```rust
// Good: iterator chain, no intermediate allocations
let total: f64 = orders.iter()
    .filter(|o| o.is_active())
    .map(|o| o.total())
    .sum();

// Bad: allocating intermediate Vec unnecessarily
let active: Vec<&Order> = orders.iter().filter(|o| o.is_active()).collect();
let total: f64 = active.iter().map(|o| o.total()).sum();
```

---

## 7. Testing

**Framework: Built-in `#[test]` with `cargo test`. Use `cargo-nextest` for
faster parallel execution.**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calculates_order_total() {
        let order = Order::new(vec![
            LineItem::new("widget", 2, 9.99),
            LineItem::new("gadget", 1, 24.99),
        ]);
        assert_eq!(order.total(), 44.97);
    }

    #[test]
    fn rejects_empty_order() {
        let result = Order::new(vec![]);
        assert!(result.is_err());
    }
}
```

**Rules:**
- Unit tests live in a `#[cfg(test)] mod tests` block inside the module they
  test. Integration tests go in `tests/`.
- Use `assert_eq!`, `assert_ne!`, and `assert!` with descriptive messages.
  Consider `assert_matches!` for enum variant checking.
- Test error paths, not just happy paths. Verify that functions return the
  correct error variant.
- Use `#[should_panic(expected = "...")]` only for tests verifying panic
  behavior. Prefer `Result`-returning tests.
- Use `proptest` or `quickcheck` for property-based testing on parsing,
  serialization, and algorithmic code.
- Integration tests use real dependencies via Docker (testcontainers-rs) or
  in-memory alternatives. Do not mock core infrastructure.
- Benchmark critical paths with `criterion`. Performance regressions are CI
  failures.
- Use `#[ignore]` for slow tests; run them in a separate CI stage.
- Aim for 80%+ line coverage; measure with `cargo-llvm-cov` or `cargo-tarpaulin`.

---

## 8. Naming Conventions

| Element          | Convention      | Example                        |
|------------------|-----------------|--------------------------------|
| Crates           | `kebab-case`    | `order-processing`             |
| Modules          | `snake_case`    | `payment_gateway.rs`           |
| Types / Structs  | `PascalCase`    | `OrderProcessor`               |
| Traits           | `PascalCase`    | `Serializable`, `IntoResponse` |
| Functions        | `snake_case`    | `calculate_total`              |
| Constants        | `UPPER_SNAKE`   | `MAX_RETRY_COUNT`              |
| Enum variants    | `PascalCase`    | `OrderStatus::Pending`         |
| Type parameters  | Single uppercase| `T`, `E`, `K`, `V`            |
| Lifetimes        | Short lowercase | `'a`, `'de`, `'ctx`           |
| Feature flags    | `kebab-case`    | `serde-support`                |

---

## 9. Logging and Observability

**Use `tracing` for structured, span-based logging.**

```rust
use tracing::{info, instrument};

#[instrument(skip(db), fields(order_id = %order_id))]
async fn process_order(order_id: &str, db: &Pool) -> Result<Order> {
    info!("processing order");
    let order = db.get_order(order_id).await?;
    info!(total = order.total(), "order loaded");
    Ok(order)
}
```

**Rules:**
- Use `tracing` spans to create structured context, not string interpolation.
- Log levels: `trace` for verbose diagnostics, `debug` for developer detail,
  `info` for operational events, `warn` for recoverable problems, `error` for
  failures.
- Never log secrets, tokens, or PII. Use `skip` in `#[instrument]` to exclude
  sensitive fields.
- Use `tracing-subscriber` with JSON output in production and human-readable
  output in development.

---

## 10. Dependency Management

```toml
# Cargo.toml
[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }
proptest = "1"
```

**Rules:**
- Pin dependencies with `=` versions in applications. Use semver ranges in
  libraries.
- Run `cargo deny check` in CI to block known-vulnerable or duplicate
  dependencies.
- Run `cargo audit` regularly and in CI to catch advisories.
- Enable only the Cargo features you need. Do not use `features = ["full"]`
  unless you genuinely need every feature.
- Keep `Cargo.lock` committed for binaries. Do not commit it for libraries.
- Audit new dependencies before adding them. Prefer well-maintained crates with
  `unsafe`-free or well-audited `unsafe` usage.

---

## Do / Don't

### Do
- Use `Result<T, E>` for all fallible operations. Propagate with `?`.
- Borrow data (`&T`, `&mut T`) unless the function needs ownership.
- Encapsulate all `unsafe` in safe wrappers with `// SAFETY:` comments.
- Use `clippy::pedantic` and fix all warnings before merging.
- Use `tracing` with spans and structured fields for observability.
- Use `cargo fmt` on every save. CI rejects unformatted code.
- Use `Arc` for shared ownership across threads; prefer channels over mutexes.
- Run `cargo deny check` and `cargo audit` in CI.
- Use `Cow<'_, str>` when a function may or may not allocate.
- Pin your Rust toolchain version in `rust-toolchain.toml`.

### Don't
- Use `unwrap()` or `expect()` in production code paths.
- Use `unsafe` without a `// SAFETY:` comment and code review approval.
- Hold a `std::sync::Mutex` guard across `.await` points.
- Use `clone()` to silence the borrow checker without understanding why.
- Use `Box<dyn Error>` as a public API error type. Define domain errors.
- Block the async executor with synchronous I/O or CPU-heavy computation.
- Use `Rc<T>` in multithreaded code. Use `Arc<T>` instead.
- Ignore `clippy` warnings. Fix them or document a suppression reason.
- Use `println!` for operational output. Use `tracing`.
- Add dependencies without auditing their maintenance status and safety.

---

## Common Pitfalls

1. **Cloning to appease the borrow checker.** New Rust developers scatter
   `.clone()` to make the compiler happy. This masks ownership design issues
   and introduces unnecessary allocations. Restructure data ownership instead.

2. **Holding locks across await points.** Using `std::sync::Mutex` in async code
   and holding the guard across `.await` blocks the runtime thread. Use
   `tokio::sync::Mutex` or restructure to release the lock before awaiting.

3. **Using `unwrap()` in library code.** Libraries must never panic on expected
   input. Return `Result` and let the caller decide how to handle errors.
   `unwrap()` in a library becomes someone else's production crash.

4. **Fighting lifetimes with self-referential structs.** Storing a reference and
   the data it borrows in the same struct requires `Pin` and is fragile.
   Separate the data from the reference, or use indices instead of references.

5. **Ignoring `Send` and `Sync` bounds in async code.** Futures must be `Send`
   to be spawned on a multi-threaded runtime. Using `Rc`, `Cell`, or non-Send
   types inside async functions causes cryptic compiler errors. Use `Arc` and
   `Mutex` instead.

6. **Blocking the async executor.** Calling synchronous I/O or CPU-intensive
   functions inside `async fn` blocks the task scheduler. Use
   `tokio::task::spawn_blocking` for blocking operations.

7. **Over-using `String` where `&str` suffices.** Allocating a `String` for
   every function parameter when a `&str` borrow would work wastes memory and
   CPU. Only take `String` when the function needs ownership.

---

## Checklist

- [ ] `rust-toolchain.toml` pins the Rust edition and toolchain version
- [ ] `rustfmt` configured and enforced in CI (`cargo fmt -- --check`)
- [ ] `clippy::pedantic` enabled; all warnings addressed or documented
- [ ] `#![deny(unsafe_code)]` at crate root; `unsafe` blocks have `// SAFETY:` comments
- [ ] All public functions return `Result<T, E>` with domain-specific error types
- [ ] `thiserror` for library errors; `anyhow` for application errors
- [ ] No `unwrap()` or `expect()` in production code paths
- [ ] `tracing` configured with structured spans (JSON in prod, human-readable in dev)
- [ ] Async code uses `tokio::sync::Mutex`, not `std::sync::Mutex` across awaits
- [ ] Channels preferred over shared state for concurrency
- [ ] `cargo deny check` and `cargo audit` run in CI
- [ ] `Cargo.lock` committed for binaries, not for libraries
- [ ] `cargo test` and `cargo-nextest` pass with 80%+ coverage via `cargo-llvm-cov`
- [ ] `criterion` benchmarks for performance-critical paths
- [ ] No unnecessary `.clone()` calls; ownership model reviewed
- [ ] CI gate runs: `cargo fmt`, `clippy`, `test`, `deny`, `audit`
