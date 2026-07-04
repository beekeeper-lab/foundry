---
id: dart
category: Languages
entry: true
last-reviewed: 2026-07
---

# Dart Stack Conventions

## Category
Languages

Non-negotiable defaults for Dart projects on this team. Targets Dart 3.x with
sound null safety, pattern matching, and structured concurrency via isolates.
Covers CLI tools, server-side (shelf/dart_frog), and shared packages. Deviations
require an ADR with justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                         | Override Requires |
|----------------------|----------------------------------------|-------------------|
| Dart Version         | 3.x (latest stable)                   | ADR               |
| Null Safety          | Sound null safety (enforced)           | Never             |
| Formatter            | `dart format` (built-in)               | Never             |
| Linter               | `dart analyze` with recommended rules  | ADR               |
| Serialization        | `json_serializable` + `freezed`        | ADR               |
| HTTP Server          | `shelf` + `shelf_router`               | ADR               |
| HTTP Client          | `http` package (simple) / `dio` (complex) | ADR            |
| Testing              | `package:test` + `package:mocktail`    | ADR               |
| Dependency Injection | Constructor injection (no framework)   | ADR               |
| Build Tool           | `dart compile` / `build_runner`        | ADR               |
| Package Manager      | `dart pub` (pubspec.yaml)              | Never             |
| Concurrency          | `async/await` + `Isolate.run`          | Never             |

### Alternatives

| Primary              | Alternative              | When                                    |
|----------------------|--------------------------|-----------------------------------------|
| `shelf`              | `dart_frog`              | Convention-over-configuration preferred |
| `json_serializable`  | `dart_mappable`          | Advanced mapping features needed        |
| `http`               | `dio`                    | Interceptors, request cancellation needed |
| `mocktail`           | `mockito`                | Team already using mockito              |
| `freezed`            | Manual immutable classes | Very few models, avoiding codegen       |
| `Isolate.run`        | `compute` (Flutter)      | Flutter-specific isolate wrapper        |

---

## Project Structure (Package / CLI)

```
project-root/
  lib/
    src/                         # Private implementation (not exported)
      models/                    # Data classes, DTOs
      services/                  # Business logic
      utils/                     # Helpers, extensions
    my_package.dart              # Public barrel export file
  bin/
    main.dart                    # CLI entry point (if executable)
  test/
    src/                         # Mirror lib/src structure
    helpers/                     # Test utilities, fakes
  analysis_options.yaml
  pubspec.yaml
```

## Project Structure (Server)

```
project-root/
  lib/
    src/
      config/                    # Server configuration, env loading
      middleware/                 # Shelf middleware (auth, logging, CORS)
      routes/                    # Route handlers
      models/                    # Request/response DTOs, domain entities
      services/                  # Business logic
      repositories/              # Data access
    server.dart                  # Server bootstrap, pipeline assembly
  bin/
    server.dart                  # Entry point: starts the server
  test/
    routes/                      # Handler tests
    services/                    # Service tests
    integration/                 # Full request/response tests
  analysis_options.yaml
  pubspec.yaml
```

**Rules:**
- Everything under `lib/src/` is private to the package. Only export public API
  through the barrel file (`lib/my_package.dart`).
- One class per file. File name matches the class in `snake_case`.
- Keep `bin/` thin — parse arguments, call into `lib/`.
- Tests mirror the `lib/src/` structure. One test file per source file.

---

## Null Safety

```dart
// Nullable types are explicit
String? findUserName(String id) {
  final user = userStore[id];
  return user?.name;
}

// Null-aware operators
final displayName = user?.name ?? 'Anonymous';

// Pattern matching for null checks (Dart 3+)
switch (user) {
  case User(:final name):
    print('Hello, $name');
  case null:
    print('No user found');
}

// Assertions for values that must not be null
void processOrder(Order? order) {
  if (order case final order?) {
    // order is non-null here
    submit(order);
  } else {
    throw ArgumentError('Order must not be null');
  }
}
```

**Rules:**
- Sound null safety is mandatory. All code compiles with `--sound-null-safety`.
- Use `?` suffix for nullable types. Default to non-nullable.
- Use `?.`, `??`, and `??=` for null-safe access. Never use `!` (null assertion)
  unless the value is provably non-null and a type promotion is not possible.
- Use pattern matching (`case final x?` or `switch`) for null checks when it
  improves readability.
- Validate nullable inputs at system boundaries (API handlers, CLI args).
  Interior code should work with non-nullable types.

---

## Pattern Matching and Records (Dart 3+)

```dart
// Destructuring records
(String, int) parseHeader(String line) {
  final parts = line.split(':');
  return (parts[0].trim(), int.parse(parts[1].trim()));
}

final (name, value) = parseHeader('Content-Length: 42');

// Switch expressions with patterns
String describeStatus(int code) => switch (code) {
  200 => 'OK',
  301 || 302 => 'Redirect',
  404 => 'Not Found',
  >= 500 && < 600 => 'Server Error',
  _ => 'Unknown',
};

// Sealed class exhaustive matching
sealed class Shape {}
class Circle extends Shape { final double radius; Circle(this.radius); }
class Square extends Shape { final double side; Square(this.side); }

double area(Shape shape) => switch (shape) {
  Circle(:final radius) => 3.14159 * radius * radius,
  Square(:final side) => side * side,
};

// If-case for single-pattern checks
if (json case {'name': String name, 'age': int age}) {
  print('$name is $age years old');
}
```

**Rules:**
- Use records for returning multiple values. Prefer named fields for records
  used in public APIs: `({String name, int age})`.
- Use switch expressions (not switch statements) when every branch returns a value.
- Use sealed classes for closed type hierarchies. The compiler enforces exhaustive
  matching — do not add a `default` / `_` case.
- Use if-case for single-pattern matching. Use switch for multiple patterns.
- Destructure objects with named field patterns (`:final fieldName`) for clarity.

---

## Async and Concurrency

```dart
// Async/await for sequential async work
Future<Order> processOrder(String id) async {
  final order = await orderRepository.getById(id);
  final enriched = await enrichmentService.enrich(order);
  return await orderRepository.save(enriched);
}

// Future.wait for concurrent independent work
Future<Dashboard> loadDashboard(String userId) async {
  final results = await Future.wait([
    userService.getProfile(userId),
    orderService.getRecent(userId),
    notificationService.getUnread(userId),
  ]);
  return Dashboard(
    profile: results[0] as UserProfile,
    orders: results[1] as List<Order>,
    notifications: results[2] as List<Notification>,
  );
}

// Streams for reactive data
Stream<Order> watchPendingOrders() async* {
  while (true) {
    final orders = await orderRepository.findPending();
    for (final order in orders) {
      yield order;
    }
    await Future.delayed(const Duration(seconds: 5));
  }
}

// Isolates for CPU-intensive work
Future<List<Order>> parseOrders(String jsonString) async {
  return Isolate.run(() {
    final list = jsonDecode(jsonString) as List;
    return list
        .cast<Map<String, dynamic>>()
        .map(Order.fromJson)
        .toList();
  });
}
```

**Rules:**
- Use `async`/`await` for all asynchronous operations. Never use `.then()` chains.
- Use `Future.wait` for concurrent independent operations.
- Use `Isolate.run` (Dart 3+) for CPU-intensive work. It handles spawning and
  cleanup automatically.
- Use `Stream` and `async*` generators for push-based data.
- Always handle errors in async code. Use try/catch around `await` calls, or
  `.onError` on streams.
- Cancel subscriptions when no longer needed. Store `StreamSubscription` references
  and call `.cancel()` in cleanup.
- Use `Completer` only when bridging callback-based APIs to Futures. Prefer
  `async`/`await` for new code.

---

## Classes and Data Modeling

```dart
// Immutable data class with freezed
@freezed
class Order with _$Order {
  const factory Order({
    required String id,
    required String customerId,
    required List<OrderItem> items,
    required OrderStatus status,
    required DateTime createdAt,
  }) = _Order;
}

// Sealed class for result types
sealed class Result<T> {
  const Result();
}

class Success<T> extends Result<T> {
  const Success(this.value);
  final T value;
}

class Failure<T> extends Result<T> {
  const Failure(this.error);
  final String error;
}

// Extension methods for adding behavior to existing types
extension StringValidation on String {
  bool get isValidEmail => RegExp(r'^[\w.-]+@[\w-]+\.[\w.]+$').hasMatch(this);
  String get capitalized => isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}

// Enums with members (Dart 3+)
enum OrderStatus {
  pending('Pending'),
  processing('Processing'),
  shipped('Shipped'),
  delivered('Delivered');

  const OrderStatus(this.label);
  final String label;
}
```

**Rules:**
- Use `freezed` for immutable data classes with `copyWith`, equality, and
  serialization support.
- Use `sealed class` for closed type hierarchies. The compiler enforces
  exhaustive switch.
- Use extension methods to add behavior to existing types without inheritance.
- Use enhanced enums with members for enums that carry data or behavior.
- Prefer composition over inheritance. Use mixins for shared behavior.
- Use `const` constructors wherever possible.
- Classes that hold no mutable state should be `final` (Dart 3+) to prevent
  subclassing.

---

## Naming Conventions

| Element              | Convention         | Example                        |
|----------------------|--------------------|--------------------------------|
| Files                | `snake_case`       | `order_repository.dart`        |
| Libraries            | `snake_case`       | `library my_package;`          |
| Classes              | `PascalCase`       | `OrderRepository`              |
| Mixins               | `PascalCase`       | `SerializableMixin`            |
| Extensions           | `PascalCase`       | `StringValidation`             |
| Functions/methods    | `camelCase`        | `getOrderById()`               |
| Variables            | `camelCase`        | `orderTotal`                   |
| Constants            | `camelCase`        | `defaultTimeout`               |
| Enums                | `PascalCase.camelCase` | `OrderStatus.pending`      |
| Type parameters      | Single uppercase   | `T`, `K`, `V`                  |
| Private members      | `_` prefix         | `_internalState`               |
| Named parameters     | `camelCase`        | `{required String orderId}`    |
| Test descriptions    | Sentence case      | `'should return order when found'` |

**Rules:**
- Follow official Dart style guide (dart.dev/effective-dart/style).
- One public class per file. File name matches the class in `snake_case`.
- Use `part` directives only for generated files (`.g.dart`, `.freezed.dart`).
- Private members start with `_`. Library-private visibility is the default.
- Constants use `camelCase`, not `UPPER_SNAKE_CASE` (Dart convention).
- Prefix boolean variables and getters with `is`, `has`, `can`, `should`.

---

## Error Handling

```dart
// Typed exception hierarchy
sealed class AppException implements Exception {
  const AppException(this.message);
  final String message;
}

class NotFoundException extends AppException {
  const NotFoundException(String id) : super('Not found: $id');
}

class ValidationException extends AppException {
  const ValidationException(super.message);
  final List<String> errors = const [];
}

// Functional error handling with Result type
Future<Result<Order>> getOrder(String id) async {
  try {
    final order = await repository.findById(id);
    if (order == null) return Failure('Order $id not found');
    return Success(order);
  } on DioException catch (e) {
    return Failure('Network error: ${e.message}');
  }
}
```

**Rules:**
- Use sealed classes for typed exception hierarchies.
- Catch specific exception types, never bare `catch (e)`.
- Convert exceptions to typed results at service boundaries.
- Never swallow exceptions silently. Log or propagate.
- Use `rethrow` (not `throw e`) to preserve the original stack trace.
- Reserve `assert` for development-only invariant checks. It is stripped in
  release builds.

---

## Do / Don't

### Do
- Use `dart format` and enforce it in CI.
- Use `dart analyze` with zero warnings as a CI gate.
- Use `const` on constructors, collections, and widget instances.
- Use pattern matching and records (Dart 3+) for clarity.
- Use `sealed class` for closed type hierarchies with exhaustive matching.
- Use `async`/`await` for all async work — never `.then()` chains.
- Use `Isolate.run` for CPU-intensive computation.
- Use `freezed` for immutable data classes.
- Use extension methods to add behavior to existing types.
- Use named parameters for functions with more than two parameters.
- Use `final` for local variables that are not reassigned.

### Don't
- Don't use `dynamic`. Use `Object?` and type-check.
- Don't use `!` (null assertion) without a preceding null check.
- Don't use `.then()` / `.catchError()` chains — use `async`/`await`.
- Don't use `UPPER_SNAKE_CASE` for constants — Dart uses `camelCase`.
- Don't ignore linter warnings — fix or configure rules in `analysis_options.yaml`.
- Don't use `new` keyword — it is optional and redundant since Dart 2.
- Don't use `part`/`part of` except for generated files.
- Don't use mutable global state. Pass dependencies through constructors.
- Don't use `print()` for logging in production — use a structured logger.
- Don't catch `Exception` broadly — catch specific types.

---

## Common Pitfalls

1. **Null assertion (`!`) crashes.** Using `!` converts a compile-time null check
   into a runtime crash. Use `?.`, `??`, pattern matching, or if-case instead.
2. **Forgetting `build_runner`.** After modifying `freezed` or `json_serializable`
   annotated classes, run `dart run build_runner build`. Stale generated files
   cause confusing type errors.
3. **Using `.then()` chains.** Callback-based futures are harder to read and
   debug than `async`/`await`. Errors propagate differently — `await` surfaces
   them naturally with try/catch.
4. **Mutable global state.** Top-level mutable variables create hidden
   dependencies and make testing impossible. Pass state through constructors or
   use a DI container.
5. **Catching `Exception` broadly.** `catch (e)` or `on Exception` hides bugs.
   Catch specific exception types so unexpected errors propagate.
6. **Ignoring `StreamSubscription` cleanup.** Unsubscribed streams leak memory
   and may fire callbacks on disposed objects. Store subscriptions and cancel
   them in cleanup code.
7. **Not using `const`.** Without `const`, Dart creates new instances at every
   call site. Const objects are canonicalized and reused, improving performance
   and enabling identity-based equality.
8. **Exporting private implementation.** Putting classes directly in `lib/` makes
   them public API. Keep implementation in `lib/src/` and export only the public
   surface through a barrel file.

---

## Checklist

Before merging any Dart PR, verify:

- [ ] `dart format` applied; CI rejects unformatted code
- [ ] `dart analyze` passes with zero warnings
- [ ] Generated files up to date (`dart run build_runner build --delete-conflicting-outputs`)
- [ ] Sound null safety enforced — no `// ignore: ...` for null checks
- [ ] No `dynamic` types — `Object?` with type checks used instead
- [ ] No `!` (null assertion) without provable non-null guarantee
- [ ] `const` used on all constructors and collections that support it
- [ ] `async`/`await` used for all async code — no `.then()` chains
- [ ] Sealed classes used for closed hierarchies; switch is exhaustive without `_`
- [ ] Extension methods used instead of utility classes with static methods
- [ ] Named parameters used for functions with more than two parameters
- [ ] `final` used for local variables that are not reassigned
- [ ] `pubspec.lock` committed for applications, excluded for packages
- [ ] No secrets in source code, logs, or committed config files
