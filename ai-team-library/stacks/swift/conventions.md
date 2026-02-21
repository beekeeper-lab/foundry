# Swift Stack Conventions

Non-negotiable defaults for Swift projects on this team. Targets Swift 6.0+ with
iOS/macOS native development using SwiftUI, structured concurrency, and ARC memory
management. Deviations require an ADR with justification. "I prefer it differently"
is not justification.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| Swift Version        | 6.0+ (latest stable)                 | ADR               |
| Platform             | iOS 17+ / macOS 14+                  | ADR               |
| UI Framework         | SwiftUI                               | ADR               |
| Build System         | Xcode + Swift Package Manager (SPM)  | Never             |
| Concurrency          | Swift structured concurrency (`async/await`, actors) | ADR |
| Reactive Framework   | Observation framework (`@Observable`) | ADR               |
| Networking           | `URLSession` + `async/await`         | ADR               |
| Persistence          | SwiftData                             | ADR               |
| Dependency Injection | Constructor injection (no framework)  | Never             |
| Formatter            | `swift-format`                        | Never             |
| Linter               | SwiftLint                             | ADR               |
| Testing              | Swift Testing framework + XCTest      | Never             |

### Alternatives

| Primary              | Alternative              | When                                    |
|----------------------|--------------------------|-----------------------------------------|
| SwiftUI              | UIKit / AppKit           | Complex custom views, legacy support    |
| `@Observable`        | Combine                  | Complex event streams, backpressure     |
| SwiftData            | Core Data / GRDB / Realm | Complex migration needs, cross-platform |
| `URLSession`         | Alamofire                | Complex auth flows, retry policies      |
| `swift-format`       | Custom rules             | Team has established different style     |
| Swift Testing        | XCTest only              | UI testing, performance testing         |
| SPM                  | CocoaPods / Carthage     | Dependencies not available via SPM      |
| Structured concurrency | GCD / OperationQueue  | Interop with legacy Objective-C code    |

---

## Project Structure

```
ProjectName/
  App/
    ProjectNameApp.swift         # @main entry point, app configuration
    ContentView.swift            # Root view
  Features/
    Orders/
      OrderListView.swift        # SwiftUI view (presentation only)
      OrderDetailView.swift
      OrderViewModel.swift       # @Observable view model (presentation logic)
      OrderService.swift         # Business logic (no UI dependency)
      OrderRepository.swift      # Data access (network, database)
    Settings/
      SettingsView.swift
      SettingsViewModel.swift
  Core/
    Models/
      Order.swift                # Domain types, value objects
      User.swift
    Networking/
      APIClient.swift            # URLSession wrapper, endpoint definitions
      APIError.swift             # Typed network errors
    Persistence/
      DataStore.swift            # SwiftData model container setup
    Extensions/
      Date+Formatting.swift      # Small, focused extensions
  Resources/
    Assets.xcassets
    Localizable.xcstrings
  Tests/
    OrderServiceTests.swift
    OrderViewModelTests.swift
    OrderRepositoryTests.swift
  UITests/
    OrderFlowUITests.swift
  Package.swift                  # SPM dependencies (or .xcodeproj)
```

**Rules:**
- Feature folders group related views, view models, services, and repositories
  together. This keeps related code close and makes features easy to find.
- Views are thin: they bind to view model state and dispatch actions. No business
  logic, no network calls, no database queries in views.
- View models are `@Observable` classes that own presentation logic. They call
  services for business operations.
- Services contain business logic and are independent of UI framework. They accept
  and return domain types, not SwiftUI types.
- Repositories handle data access (network, database, file system). Services call
  repositories, never views directly.
- The `Core/` folder contains shared infrastructure used across features.
- One `@main` entry point in `App/`. It configures the dependency graph and
  presents the root view.

---

## Memory Management (ARC)

Swift uses Automatic Reference Counting (ARC), not garbage collection. Understanding
reference cycles is critical to preventing memory leaks.

```swift
// Good: weak reference breaks retain cycle in closures
class OrderViewModel: Observable {
    private let service: OrderService

    func loadOrders() {
        Task { [weak self] in
            guard let self else { return }
            let orders = try await service.fetchOrders()
            self.orders = orders
        }
    }
}

// Good: unowned when lifetime is guaranteed
class OrderDetailView {
    unowned let coordinator: AppCoordinator  // coordinator always outlives this view
}

// Bad: strong reference cycle
class Parent {
    var child: Child?
}
class Child {
    var parent: Parent?  // retain cycle — use weak or unowned
}
```

**Rules:**
- Use `weak` references for delegates, closures capturing `self`, and parent
  references in child objects. Default to `weak` when unsure.
- Use `unowned` only when the referenced object is guaranteed to outlive the
  referencing object. If in doubt, use `weak`.
- Capture `[weak self]` in escaping closures and `Task` blocks. Always guard-let
  `self` immediately after.
- Use `Instruments > Leaks` and `Memory Graph Debugger` in Xcode to detect retain
  cycles during development.
- Value types (`struct`, `enum`) do not participate in ARC. Prefer structs for
  data models to avoid reference cycle concerns entirely.
- Never store closures as stored properties on the object they capture without
  breaking the cycle with `[weak self]` or `[unowned self]`.

---

## Concurrency (async/await and Actors)

Swift's structured concurrency model replaces GCD and completion handlers with
compile-time-checked async code.

```swift
// Async function with structured concurrency
func fetchOrderDetails(id: String) async throws -> OrderDetails {
    async let order = apiClient.fetchOrder(id: id)
    async let reviews = apiClient.fetchReviews(orderId: id)

    return try await OrderDetails(
        order: order,
        reviews: reviews
    )
}

// Actor for thread-safe mutable state
actor OrderCache {
    private var cache: [String: Order] = [:]

    func get(_ id: String) -> Order? {
        cache[id]
    }

    func set(_ id: String, order: Order) {
        cache[id] = order
    }
}

// TaskGroup for dynamic fan-out
func processOrders(_ ids: [String]) async throws -> [Order] {
    try await withThrowingTaskGroup(of: Order.self) { group in
        for id in ids {
            group.addTask {
                try await self.fetchOrder(id: id)
            }
        }
        var results: [Order] = []
        for try await order in group {
            results.append(order)
        }
        return results
    }
}
```

**Rules:**
- Use `async/await` for all asynchronous work. Do not use completion handlers in
  new code.
- Use `async let` for concurrent operations that can run in parallel within the
  same scope.
- Use `TaskGroup` for dynamic fan-out where the number of concurrent operations
  is determined at runtime.
- Use `actor` types to protect shared mutable state. Actors serialize access
  automatically, eliminating data races.
- Mark view models as `@MainActor` to ensure UI state updates happen on the main
  thread. Use `@MainActor` on any type that touches UI state.
- Use `Task { }` to bridge from synchronous to asynchronous code. Always store
  the task handle if cancellation is needed.
- Use `Task.checkCancellation()` or `Task.isCancelled` in long-running operations
  to support cooperative cancellation.
- Never use `Task.detached` unless you specifically need to opt out of the current
  actor context. Prefer structured `Task { }` blocks.
- Enable strict concurrency checking (`-strict-concurrency=complete`) in build
  settings. Fix all warnings — they become errors in Swift 6.

---

## SwiftUI Patterns

```swift
// Observable view model (Swift 5.9+ Observation framework)
@Observable
class OrderListViewModel {
    var orders: [Order] = []
    var isLoading = false
    var error: Error?

    private let service: OrderService

    init(service: OrderService) {
        self.service = service
    }

    func loadOrders() async {
        isLoading = true
        defer { isLoading = false }
        do {
            orders = try await service.fetchOrders()
        } catch {
            self.error = error
        }
    }
}

// SwiftUI view — thin, declarative, no business logic
struct OrderListView: View {
    @State private var viewModel: OrderListViewModel

    init(service: OrderService) {
        _viewModel = State(initialValue: OrderListViewModel(service: service))
    }

    var body: some View {
        List(viewModel.orders) { order in
            OrderRow(order: order)
        }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
        .task {
            await viewModel.loadOrders()
        }
    }
}
```

**Rules:**
- Use `@Observable` (Observation framework) instead of `ObservableObject` /
  `@Published` for new code. It has better performance and simpler syntax.
- Use `@State` for view-local state that the view owns. Use `@Environment` for
  dependencies injected from parent views.
- Use `.task { }` modifier for async work tied to view lifecycle. It automatically
  cancels when the view disappears.
- Keep views small and composable. Extract reusable subviews as separate structs.
- Use `@Bindable` to create bindings from `@Observable` objects in SwiftUI views.
- Never perform side effects in `body`. Use `.task`, `.onAppear`, or explicit
  user actions.
- Use `@Environment(\.dismiss)` for navigation, not manual state flags.

---

## Error Handling

```swift
// Define typed errors for domain operations
enum OrderError: LocalizedError {
    case notFound(id: String)
    case paymentDeclined(reason: String)
    case networkUnavailable

    var errorDescription: String? {
        switch self {
        case .notFound(let id):
            return "Order \(id) not found"
        case .paymentDeclined(let reason):
            return "Payment declined: \(reason)"
        case .networkUnavailable:
            return "Network unavailable"
        }
    }
}

// Typed throws (Swift 6.0+)
func fetchOrder(id: String) throws(OrderError) -> Order {
    guard let order = cache[id] else {
        throw .notFound(id: id)
    }
    return order
}

// Propagate with try, handle at the boundary
func loadOrders() async {
    do {
        orders = try await service.fetchOrders()
    } catch let error as OrderError {
        self.error = error
    } catch {
        self.error = OrderError.networkUnavailable
    }
}
```

**Rules:**
- Define domain-specific error enums conforming to `LocalizedError` for every
  module that can fail.
- Use typed throws (`throws(MyError)`) in Swift 6.0+ for functions with known
  error types.
- Propagate errors with `try` and `throws`. Handle errors at the presentation
  boundary, not deep in business logic.
- Never use `try!` in production code. It crashes on error.
- Use `try?` only when the error is genuinely ignorable (e.g., optional cache lookup).
- Use `Result<T, E>` for values that carry errors across async boundaries or
  stored properties. Prefer `throws` for synchronous function signatures.
- Provide user-facing error messages via `LocalizedError.errorDescription`.
  Log technical details separately.

---

## Naming Conventions

| Element              | Convention         | Example                       |
|----------------------|--------------------|-------------------------------|
| Types / Structs      | `PascalCase`       | `OrderService`                |
| Protocols            | `PascalCase`       | `OrderFetching`, `Identifiable` |
| Functions / Methods  | `camelCase`        | `fetchOrders()`, `placeOrder(_:)` |
| Properties           | `camelCase`        | `orderCount`, `isLoading`     |
| Constants            | `camelCase`        | `let maxRetryCount = 3`       |
| Enum cases           | `camelCase`        | `OrderStatus.pending`         |
| Type parameters      | Single uppercase   | `T`, `Element`, `Key`         |
| Protocols (capability) | `-able`/`-ing`/`-ible` | `Codable`, `Sendable`, `Loading` |
| Bool properties      | `is`/`has`/`should` prefix | `isLoading`, `hasError`  |
| Factory methods      | `make` prefix      | `makeOrderService()`          |

**Rules:**
- Follow the [Swift API Design Guidelines](https://swift.org/documentation/api-design-guidelines/).
  Name methods for their side effects: mutating verbs (`sort()`), non-mutating
  nouns (`sorted()`).
- Use argument labels to clarify the role of each parameter:
  `move(from: a, to: b)`, not `move(a, b)`.
- Omit the first argument label when the method name includes the parameter's
  role: `addSubview(_ view:)`, `contains(_ element:)`.
- Acronyms follow Swift convention: uppercase when at the start (`URLSession`),
  lowercase within (`urlSession`).
- Protocol names describe capability (`Equatable`, `Sendable`) or role
  (`OrderFetching`, `DataStoring`). Do not use `I` prefix or `Protocol` suffix.
- Use `typealias` sparingly. It obscures types more than it helps unless the
  aliased type is genuinely complex.

---

## Logging

```swift
import OSLog

extension Logger {
    static let orders = Logger(subsystem: "com.company.app", category: "orders")
    static let network = Logger(subsystem: "com.company.app", category: "network")
}

// Use structured logging with privacy annotations
func processOrder(_ order: Order) {
    Logger.orders.info("Processing order \(order.id)")
    Logger.orders.debug("Order total: \(order.total, privacy: .private)")

    do {
        try validate(order)
        Logger.orders.info("Order \(order.id) validated successfully")
    } catch {
        Logger.orders.error("Order validation failed: \(error.localizedDescription)")
    }
}
```

**Rules:**
- Use `os.Logger` (OSLog) for structured logging. Do not use `print()` or
  `NSLog()` for operational messages.
- Define static `Logger` instances per subsystem/category for consistent filtering.
- Use log levels: `debug` for developer diagnostics, `info` for operational events,
  `notice` for noteworthy conditions, `error` for failures, `fault` for bugs.
- Use `privacy: .private` for sensitive data (PII, tokens, financial amounts).
  OSLog redacts private values in release builds.
- Never log secrets, tokens, passwords, or full PII without privacy annotation.
- Use `signpost` for performance instrumentation of critical operations.

---

## Do / Don't

### Do
- Use `struct` for data models. Value types avoid reference cycle issues and are
  `Sendable` by default.
- Use `async/await` for all asynchronous work. Structured concurrency is checked
  at compile time.
- Use `actor` for shared mutable state. Actors prevent data races.
- Mark UI-touching code with `@MainActor`. SwiftUI views are implicitly main-actor.
- Use `[weak self]` in escaping closures and Task blocks to prevent retain cycles.
- Use `@Observable` for view models. It tracks property access automatically.
- Use `.task { }` for async work tied to view lifecycle.
- Use `swift-format` and SwiftLint on every commit. CI rejects violations.
- Conform types to `Sendable` when they cross actor boundaries.
- Use `guard` for early returns to reduce nesting.

### Don't
- Use `class` when `struct` suffices. Classes introduce ARC overhead and reference
  cycle risks.
- Use `force unwrap` (`!`) in production code. It crashes on `nil`.
- Use implicitly unwrapped optionals (`String!`) except for `@IBOutlet` in legacy
  UIKit code.
- Use `DispatchQueue` / GCD in new code. Use structured concurrency.
- Use `ObservableObject` / `@Published` in new code. Use `@Observable`.
- Use `AnyView` for type erasure. It defeats SwiftUI's diffing. Use `@ViewBuilder`
  or `some View` returns.
- Use singletons for dependency injection. Pass dependencies through constructors
  or `@Environment`.
- Ignore `Sendable` warnings. They indicate potential data races that Swift 6
  will enforce as errors.
- Use `Any` or `AnyObject` when a protocol or generic would be more precise.
- Nest more than 3 levels of closures or control flow. Extract into named methods.

---

## Common Pitfalls

1. **Retain cycles in closures** — Capturing `self` strongly in escaping closures
   (completion handlers, `Task` blocks, `NotificationCenter` observers) causes
   memory leaks. Always use `[weak self]` and guard-let immediately. Use
   Instruments > Leaks regularly.

2. **Blocking the main thread** — Performing synchronous I/O, heavy computation,
   or `Thread.sleep` on the main thread freezes the UI. Use `async/await` with
   proper actor isolation. Use `Task.detached` or `spawn_blocking` patterns for
   CPU-intensive work.

3. **Missing `@MainActor` on UI state** — Updating UI state from a background
   context causes runtime warnings or crashes. Mark view models with `@MainActor`
   or use `await MainActor.run { }` when updating UI properties.

4. **Force unwrapping optionals** — Using `!` on a `nil` value crashes the app
   immediately. Use `guard let`, `if let`, optional chaining (`?.`), or the
   nil-coalescing operator (`??`) instead. Reserve `!` for `@IBOutlet` only.

5. **Ignoring `Sendable` conformance** — Types passed across actor boundaries
   must conform to `Sendable`. Ignoring compiler warnings leads to data races
   that Swift 6 strict concurrency will reject. Fix warnings now.

6. **Overusing `@State` for complex state** — `@State` is for simple, view-owned
   values. Complex state with business logic belongs in an `@Observable` view
   model. Putting logic in `@State` makes it untestable.

7. **Not cancelling Tasks** — `Task` blocks started in `onAppear` or button
   handlers continue running even after the view disappears if not cancelled.
   Use `.task { }` modifier (auto-cancels) or store and cancel `Task` handles
   manually.

---

## Checklist

- [ ] Swift 6.0+ targeted; strict concurrency checking enabled (`-strict-concurrency=complete`)
- [ ] `swift-format` applied; CI rejects unformatted code
- [ ] SwiftLint runs in CI; no new warnings introduced
- [ ] `@Observable` used for view models; no `ObservableObject` in new code
- [ ] `async/await` used for all async work; no completion handlers in new code
- [ ] `actor` used for shared mutable state; no manual locking
- [ ] `@MainActor` applied to all UI-state-mutating types
- [ ] `[weak self]` used in all escaping closures and Task blocks
- [ ] No `force unwrap` (`!`) in production code paths
- [ ] No `try!` in production code paths
- [ ] All error types conform to `LocalizedError` with descriptive messages
- [ ] `Sendable` conformance verified for all types crossing actor boundaries
- [ ] `os.Logger` used for structured logging; no `print()` statements
- [ ] Instruments > Leaks run during development; no retain cycles detected
- [ ] Struct preferred over class for data models
- [ ] `.task { }` modifier used for view-lifecycle-bound async work
- [ ] No secrets in source code, logs, or committed config files
