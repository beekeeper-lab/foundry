# Kotlin Stack Conventions

Non-negotiable defaults for Kotlin applications on this team. Covers both
server-side (Spring Boot / Ktor) and Android development. Targets Kotlin 2.0+
with coroutines as the primary concurrency model. Deviations require an ADR
with justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                         | Override Requires |
|----------------------|----------------------------------------|-------------------|
| Kotlin Version       | 2.0+ (latest stable)                  | ADR               |
| JVM Target           | 21 (server) / per Android minSdk      | ADR               |
| Server Framework     | Spring Boot 3.x with Kotlin support    | ADR               |
| Build Tool           | Gradle (Kotlin DSL)                    | ADR               |
| Formatter            | ktfmt (Google style)                   | Never             |
| Linter               | detekt                                 | ADR               |
| Logging              | SLF4J + Logback (server) / Timber (Android) | ADR          |
| DI                   | Constructor injection (Spring / Hilt)  | ADR               |
| Config               | `application.yml` + `@ConfigurationProperties` | ADR       |
| Serialization        | kotlinx.serialization                  | ADR               |
| Concurrency          | Kotlin Coroutines + Flow               | Never             |
| HTTP Client          | Ktor Client / OkHttp                   | ADR               |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| Spring Boot          | Ktor                 | Lightweight microservices, no Spring ecosystem needed |
| ktfmt                | ktlint               | Team already using ktlint             |
| Hilt (Android)       | Koin                 | Simpler DI without annotation processing |
| kotlinx.serialization| Moshi / Jackson Kotlin | Legacy interop or specific format needs |
| Ktor Client          | Retrofit             | Android with complex API contracts    |
| Logback              | kotlin-logging       | Kotlin-idiomatic wrapper preferred    |

---

## Project Structure (Server — Spring Boot)

```
project-root/
  src/
    main/
      kotlin/com/example/orders/
        OrdersApplication.kt          # @SpringBootApplication entry point
        config/                        # @Configuration, @ConfigurationProperties
        controller/                    # @RestController (thin, delegates to service)
        service/                       # Business logic (suspend functions)
        repository/                    # Data access (Spring Data / R2DBC)
        model/
          entity/                      # JPA entities or R2DBC mappings
          dto/                         # Request/response data classes
        exception/                     # Sealed class hierarchies + @ControllerAdvice
      resources/
        application.yml
        application-dev.yml
        application-prod.yml
    test/
      kotlin/com/example/orders/
        unit/                          # Mirror main structure
        integration/                   # @SpringBootTest with Testcontainers
        fixture/                       # Shared test data builders
  build.gradle.kts
  detekt.yml
  README.md
```

## Project Structure (Android)

```
app/
  src/
    main/
      kotlin/com/example/app/
        di/                            # Hilt modules
        data/
          local/                       # Room DAOs, entities
          remote/                      # Retrofit/Ktor API services
          repository/                  # Repository implementations
        domain/
          model/                       # Domain data classes
          usecase/                     # Use cases (single-responsibility)
          repository/                  # Repository interfaces
        ui/
          feature/                     # One package per feature
            FeatureScreen.kt           # Composable screen
            FeatureViewModel.kt        # ViewModel with StateFlow
            FeatureUiState.kt          # Sealed interface for UI state
        util/                          # Extension functions, helpers
      res/
    test/                              # Unit tests
    androidTest/                       # Instrumented tests
  build.gradle.kts
```

**Rules:**
- Controllers are thin: validate input, call service, return response. No
  business logic in controllers.
- Services use `suspend` functions for all I/O operations.
- DTOs are Kotlin `data class` types. Never expose JPA entities directly in
  API responses.
- Use sealed classes/interfaces for representing fixed hierarchies (errors,
  states, events).
- One `@ControllerAdvice` handles all exception-to-HTTP mapping centrally.
- Android: one ViewModel per screen, UI state modeled as sealed interface.

---

## Null Safety

```kotlin
// Use nullable types explicitly — never use !!
fun findUser(id: String): User? {
    return userRepository.findByIdOrNull(id)
}

// Safe call + Elvis operator for defaults
val displayName = user?.name ?: "Anonymous"

// let for scoped null-safe operations
user?.let { userService.activate(it) }

// Smart cast after null check
fun process(input: Any?) {
    if (input is String) {
        // input is automatically cast to String here
        println(input.length)
    }
}

// require / check for preconditions
fun withdraw(amount: BigDecimal) {
    require(amount > BigDecimal.ZERO) { "Amount must be positive: $amount" }
    check(balance >= amount) { "Insufficient balance" }
    // ...
}
```

**Rules:**
- Never use `!!` (not-null assertion). It throws `NullPointerException` and
  defeats the purpose of null safety. Use `?.`, `?:`, or `let` instead.
- Mark return types as nullable (`?`) when the value may be absent.
- Use `requireNotNull` / `checkNotNull` at boundaries where null indicates a
  programming error.
- Use `require` for argument validation, `check` for state validation.
- Platform types from Java interop are dangerous. Add explicit nullability
  annotations (`@Nullable`/`@NonNull`) on Java APIs consumed from Kotlin.

---

## Data Classes and Sealed Types

```kotlin
// Data class for DTOs and value objects
data class CreateOrderRequest(
    val productId: String,
    val quantity: Int,
    val customerId: String,
)

// Sealed interface for result types
sealed interface OrderResult {
    data class Success(val order: Order) : OrderResult
    data class NotFound(val id: String) : OrderResult
    data class ValidationError(val errors: List<String>) : OrderResult
}

// Sealed class for domain errors
sealed class DomainError(override val message: String) : Exception(message) {
    class NotFound(val id: String) : DomainError("Entity not found: $id")
    class Conflict(val reason: String) : DomainError("Conflict: $reason")
    class Forbidden(val action: String) : DomainError("Forbidden: $action")
}

// when expression is exhaustive on sealed types (no else needed)
fun handle(result: OrderResult): ResponseEntity<*> = when (result) {
    is OrderResult.Success -> ResponseEntity.ok(result.order)
    is OrderResult.NotFound -> ResponseEntity.notFound().build()
    is OrderResult.ValidationError -> ResponseEntity.badRequest().body(result.errors)
}
```

**Rules:**
- Use `data class` for DTOs, value objects, and any type whose identity is
  defined by its properties.
- Use trailing commas in data class constructors and function parameters.
- Use `sealed interface` / `sealed class` for closed type hierarchies. The
  compiler enforces exhaustive `when` expressions.
- Prefer `sealed interface` over `sealed class` when subtypes don't share state.
- Use `copy()` for creating modified copies of data classes. Never mutate.
- Destructure data classes in `when` and `let` for readability.

---

## Coroutines

```kotlin
// Suspend function for sequential async work
suspend fun processOrder(id: String): Order {
    val order = orderRepository.findById(id) // suspends, not blocking
    val enriched = enrichmentService.enrich(order) // sequential
    return orderRepository.save(enriched)
}

// Structured concurrency with coroutineScope
suspend fun fetchDashboard(userId: String): Dashboard = coroutineScope {
    val profile = async { userService.getProfile(userId) }
    val orders = async { orderService.getRecent(userId) }
    val notifications = async { notificationService.getUnread(userId) }

    Dashboard(
        profile = profile.await(),
        orders = orders.await(),
        notifications = notifications.await(),
    )
}

// Flow for reactive streams
fun observeOrders(): Flow<Order> = flow {
    while (currentCoroutineContext().isActive) {
        val orders = orderRepository.findPending()
        orders.forEach { emit(it) }
        delay(1.seconds)
    }
}.flowOn(Dispatchers.IO)
```

**Rules:**
- Use structured concurrency. Never use `GlobalScope`. Launch coroutines within
  a `CoroutineScope` (e.g., `viewModelScope`, `coroutineScope`, or an
  injected scope).
- Use `Dispatchers.IO` for blocking I/O, `Dispatchers.Default` for CPU-bound
  work, `Dispatchers.Main` for UI (Android).
- Use `async`/`await` for concurrent operations within a `coroutineScope`.
- Use `Flow` for cold streams of data, `StateFlow`/`SharedFlow` for hot state.
- Always handle cancellation. Check `isActive` in long-running loops.
- Use `withContext` to switch dispatchers within a suspend function.
- Use `supervisorScope` when child failures should not cancel siblings.

---

## Naming Conventions

| Element              | Convention         | Example                        |
|----------------------|--------------------|--------------------------------|
| Packages             | `lowercase`        | `com.example.orders.service`   |
| Classes              | `PascalCase`       | `OrderService`                 |
| Functions            | `camelCase`        | `calculateTotal()`             |
| Properties           | `camelCase`        | `orderTotal`                   |
| Constants            | `UPPER_SNAKE`      | `MAX_RETRY_COUNT`              |
| Enum entries         | `UPPER_SNAKE`      | `OrderStatus.PENDING`          |
| Type parameters      | Single uppercase   | `T`, `K`, `V`                  |
| Backing properties   | `_` prefix         | `_uiState` / `uiState`        |
| Extension functions  | `camelCase`        | `String.toSlug()`              |
| Test functions       | Backticks allowed  | `` `returns 404 when not found`() `` |

**Rules:**
- Follow official Kotlin coding conventions (kotlinlang.org/docs/coding-conventions.html).
- Use backtick-quoted test method names for readability.
- Acronyms follow PascalCase: `HttpClient`, `JsonParser`, not `HTTPClient`.
- Use `companion object` for factory methods and constants, not top-level functions
  in the same file (unless purely utility).
- Extension functions go in a file named after the type they extend
  (`StringExtensions.kt`).

---

## Logging

```kotlin
import org.slf4j.LoggerFactory

class OrderService(private val repo: OrderRepository) {
    private val log = LoggerFactory.getLogger(javaClass)

    suspend fun process(orderId: String): Order {
        log.info("order_processing_started orderId={}", orderId)
        val order = repo.findById(orderId)
            ?: throw DomainError.NotFound(orderId)
        // ... business logic ...
        log.info("order_processing_completed orderId={} durationMs={}", orderId, elapsed)
        return order
    }
}
```

**Rules:**
- Use SLF4J parameterized logging (`{}` placeholders). Never string-concatenate
  or use string templates in log messages.
- Use static event-name prefixed messages with key=value structured context.
- Log levels: `DEBUG` for developer diagnostics, `INFO` for operational events,
  `WARN` for recoverable problems, `ERROR` for failures requiring attention.
- Never log secrets, tokens, passwords, or full PII.
- Configure JSON output in production (Logstash encoder), human-readable in dev.
- Android: use Timber with a custom tree. Never use `Log.d()` directly.

---

## Do / Don't

### Do
- Use `data class` for DTOs and value objects; use `copy()` for modifications.
- Use `sealed interface` / `sealed class` for closed type hierarchies.
- Use coroutines and `suspend` functions for all asynchronous work.
- Use `?.` (safe call), `?:` (Elvis), and `let` for null handling.
- Use `require` / `check` for precondition validation.
- Use extension functions to add behavior to existing types without inheritance.
- Use `when` expressions exhaustively on sealed types (no `else` branch needed).
- Use trailing commas in multi-line declarations.
- Keep functions short (< 20 lines). Extract named functions for readability.

### Don't
- Use `!!` (not-null assertion). It defeats null safety.
- Use `var` when `val` is sufficient. Default to immutable.
- Use `GlobalScope` for launching coroutines. Use structured concurrency.
- Use `runBlocking` in production code (except at the application entry point or
  in tests). It blocks the calling thread.
- Use Java-style getters/setters. Use Kotlin properties.
- Use `companion object` as a dumping ground. Keep them focused.
- Use `lateinit` for nullable properties. Use `lazy` or nullable types instead.
- Use bare `Thread` or `Executor` when coroutines are available.
- Use `when` with an `else` branch on sealed types (it hides missing cases).

---

## Common Pitfalls

1. **Not-null assertion (`!!`) crashes** -- Using `!!` converts a `KotlinNullPointerException`
   from a compile-time check to a runtime crash. Use `?.`, `?:`, `let`, or
   `requireNotNull` with a meaningful message.
2. **`runBlocking` on the main thread** -- Blocks the entire thread, causing ANR
   on Android or thread starvation on server. Only use at application entry
   points or in test code.
3. **Coroutine leak from `GlobalScope`** -- `GlobalScope` coroutines are not
   cancelled when the calling scope is destroyed. Use `viewModelScope`,
   `lifecycleScope`, or custom `CoroutineScope` tied to a lifecycle.
4. **Data class `equals`/`hashCode` pitfall** -- Data class equality includes
   all constructor parameters. Adding a mutable `var` property to a data class
   constructor changes identity semantics unexpectedly.
5. **Platform type null safety** -- Java methods return platform types (neither
   nullable nor non-null). Assigning a platform type to a non-null Kotlin
   variable crashes at runtime if the value is null. Always add explicit
   null checks at Java interop boundaries.
6. **Sealed `when` with `else`** -- Adding an `else` branch to `when` on a
   sealed type suppresses compiler warnings when new subtypes are added.
   Omit `else` so the compiler forces you to handle new cases.
7. **Mutable collections exposed from data layer** -- Returning `MutableList`
   from a repository allows callers to modify the backing collection. Return
   `List` (read-only interface) and use `toList()` / `toMutableList()` at
   boundaries.

---

## Checklist

- [ ] Kotlin 2.0+ targeted in `build.gradle.kts`.
- [ ] `ktfmt` applied; CI rejects unformatted code.
- [ ] `detekt` runs in CI; no new warnings introduced.
- [ ] No `!!` usage anywhere in the codebase.
- [ ] `val` used by default; `var` only where mutation is required.
- [ ] All DTOs are `data class` types; entities not exposed in API responses.
- [ ] Sealed types used for closed hierarchies; `when` exhaustive without `else`.
- [ ] Coroutines use structured concurrency; no `GlobalScope`.
- [ ] `suspend` functions used for all I/O operations.
- [ ] SLF4J parameterized logging; no string concatenation in log calls.
- [ ] No `runBlocking` in production code (except entry points).
- [ ] Trailing commas used in multi-line declarations.
- [ ] No secrets in source code, logs, or committed config files.
