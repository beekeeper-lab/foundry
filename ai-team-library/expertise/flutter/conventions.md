# Flutter Stack Conventions

## Category
Frameworks

Non-negotiable defaults for Flutter applications on this team. Targets Flutter 3.x
with Dart 3.x, Material 3 design, and Riverpod for state management. Covers mobile
(iOS/Android), web, and desktop targets. Deviations require an ADR with justification.
"I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Flutter Version      | 3.x (latest stable channel)            | ADR               |
| Dart Version         | 3.x (bundled with Flutter)             | ADR               |
| State Management     | Riverpod 2.x (`riverpod_generator`)    | ADR               |
| Navigation           | GoRouter                                | ADR               |
| Design System        | Material 3 with custom `ThemeData`     | ADR               |
| HTTP Client          | `dio` with interceptors                | ADR               |
| Local Storage        | `drift` (SQLite) for structured data, `shared_preferences` for key-value | ADR |
| Serialization        | `freezed` + `json_serializable`        | ADR               |
| DI / Service Locator | Riverpod providers (no `get_it`)       | Never             |
| Linting              | `flutter_lints` (official) + custom `analysis_options.yaml` | Never |
| Formatting           | `dart format` (built-in)               | Never             |
| Testing (unit)       | `flutter_test` + `mocktail`            | ADR               |
| Testing (widget)     | `flutter_test` widget tests            | ADR               |
| Testing (integration)| `integration_test` package             | ADR               |
| Build Runner         | `build_runner` for code generation     | Never             |

### Alternatives

| Primary              | Alternative              | When                                    |
|----------------------|--------------------------|-----------------------------------------|
| Riverpod             | Bloc / Cubit             | Team has existing Bloc expertise        |
| GoRouter             | auto_route               | Complex nested navigation with guards   |
| `dio`                | `http` package           | Simple apps with no interceptor needs   |
| `drift`              | `hive` / `isar`          | NoSQL use case, simpler schema          |
| `freezed`            | Manual `copyWith` + `==` | Very few model classes, avoiding codegen |
| Material 3           | Cupertino widgets        | iOS-only app requiring native feel      |
| `mocktail`           | `mockito`                | Team already uses mockito               |

---

## Project Structure

```
project-root/
  lib/
    main.dart                    # Entry point, ProviderScope, app configuration
    app/
      app.dart                   # MaterialApp.router setup, theme, localization
      router.dart                # GoRouter configuration and route definitions
    features/                    # Feature modules (self-contained verticals)
      <feature_name>/
        data/
          datasources/           # Remote and local data sources
          models/                # Data transfer objects (freezed classes)
          repositories/          # Repository implementations
        domain/
          entities/              # Domain entities (freezed classes)
          repositories/          # Repository interfaces (abstract classes)
          usecases/              # Use cases (single-responsibility)
        presentation/
          providers/             # Riverpod providers for this feature
          screens/               # Screen widgets
          widgets/               # Widgets scoped to this feature
    core/
      constants/                 # App-wide constants
      errors/                    # Failure and exception classes
      extensions/                # Dart extension methods
      theme/                     # ThemeData, ColorScheme, TextTheme
      utils/                     # Pure utility functions (no Flutter imports)
      widgets/                   # Shared reusable widgets
    l10n/                        # Localization ARB files
  test/
    features/                    # Mirror lib/features structure
    core/                        # Mirror lib/core structure
    helpers/                     # Test utilities, pump helpers, fakes
  integration_test/              # Integration tests
  assets/
    images/
    fonts/
    icons/
  pubspec.yaml
  analysis_options.yaml
  build.yaml                     # build_runner configuration
```

**Rules:**
- Organize by feature, not by layer. `features/checkout/` over
  `data/repositories/checkout_repository.dart`.
- Each feature has its own `data/`, `domain/`, and `presentation/` layers.
  Cross-feature imports go through the `domain/` layer only.
- Shared widgets live in `core/widgets/` only when used by two or more features.
  Do not preemptively generalize.
- Entry point (`main.dart`) does only three things: initialize bindings, set up
  error handling, run the app inside `ProviderScope`.
- No business logic in widgets. Widgets read state from providers and dispatch
  events. Logic lives in providers, use cases, or repositories.

---

## Widget Patterns

### StatelessWidget First

Default to `StatelessWidget`. Only use `StatefulWidget` when managing lifecycle
callbacks (`initState`, `dispose`) or animation controllers. Riverpod's
`ConsumerWidget` replaces most `StatefulWidget` use cases.

```dart
// Good: ConsumerWidget for state from providers
class OrderSummary extends ConsumerWidget {
  const OrderSummary({super.key, required this.orderId});

  final String orderId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final order = ref.watch(orderProvider(orderId));
    return order.when(
      data: (data) => OrderCard(order: data),
      loading: () => const CircularProgressIndicator(),
      error: (err, stack) => ErrorDisplay(message: err.toString()),
    );
  }
}
```

### Widget Decomposition

- Extract widgets into their own classes when they exceed ~40 lines or when they
  represent a reusable concept.
- Prefer composition over inheritance. Use `const` constructors wherever possible.
- Never use helper methods that return widgets (`Widget _buildHeader()`). Extract
  a separate widget class instead — this preserves the widget tree identity and
  avoids unnecessary rebuilds.

```dart
// Bad: helper method returning widget
class OrderScreen extends StatelessWidget {
  Widget _buildHeader() => const Text('Orders'); // Don't do this

  @override
  Widget build(BuildContext context) => _buildHeader();
}

// Good: extracted widget
class OrderHeader extends StatelessWidget {
  const OrderHeader({super.key});

  @override
  Widget build(BuildContext context) => const Text('Orders');
}
```

### Keys

- Provide explicit `Key` values on widgets in lists (`ListView.builder`) and
  when the widget tree can reorder.
- Use `ValueKey` with a stable identifier (database ID), not the list index.

---

## State Management (Riverpod)

### Provider Types

```dart
// Simple computed value
@riverpod
int cartItemCount(Ref ref) {
  final cart = ref.watch(cartProvider);
  return cart.items.length;
}

// Async data fetching
@riverpod
Future<Order> order(Ref ref, String orderId) async {
  final repo = ref.watch(orderRepositoryProvider);
  return repo.getOrder(orderId);
}

// Stateful notifier for mutable state
@riverpod
class CartNotifier extends _$CartNotifier {
  @override
  Cart build() => const Cart.empty();

  void addItem(Product product) {
    state = state.copyWith(
      items: [...state.items, CartItem(product: product, quantity: 1)],
    );
  }

  void removeItem(String productId) {
    state = state.copyWith(
      items: state.items.where((i) => i.product.id != productId).toList(),
    );
  }
}
```

### Rules

- Use `riverpod_generator` with code generation. Do not write providers manually.
- Use `ref.watch` in `build` methods for reactive rebuilds. Use `ref.read` in
  callbacks and event handlers only.
- Never use `ref.watch` outside of `build` — it causes subtle bugs.
- Providers are the single source of truth. Widgets are stateless renderers of
  provider state.
- Use `AsyncValue` (`.when`, `.whenData`, `.hasError`) for loading/error states.
  Never manually track loading booleans.
- Use `autoDispose` (default with generator) to clean up state when no longer
  watched. Override with `keepAlive` only when caching is explicitly needed.
- Avoid deeply nested provider dependencies. If a provider chain exceeds three
  levels, refactor.

---

## Navigation (GoRouter)

```dart
final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isLoggedIn = // check auth state
    if (!isLoggedIn && !state.matchedLocation.startsWith('/login')) {
      return '/login';
    }
    return null;
  },
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'orders/:orderId',
          builder: (context, state) {
            final orderId = state.pathParameters['orderId']!;
            return OrderDetailScreen(orderId: orderId);
          },
        ),
      ],
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
  ],
);
```

**Rules:**
- Define all routes in a single `router.dart` file. No scattered route definitions.
- Use path parameters for resource identification (`/orders/:orderId`), query
  parameters for optional filters (`/orders?status=pending`).
- Use `context.go()` for navigation that replaces the stack (e.g., after login).
  Use `context.push()` for navigation that adds to the stack.
- Implement `redirect` for auth guards. Do not gate navigation inside widgets.
- Use typed route parameters with `$extra` for passing complex objects only when
  deep linking is not required.
- Keep the navigation tree shallow. Avoid nesting routes more than three levels.

---

## Data Layer

### Repository Pattern

```dart
// Domain layer: abstract interface
abstract class OrderRepository {
  Future<Order> getOrder(String id);
  Future<List<Order>> getOrders({OrderStatus? status});
  Future<Order> createOrder(CreateOrderRequest request);
}

// Data layer: implementation
class OrderRepositoryImpl implements OrderRepository {
  OrderRepositoryImpl({required this.remoteDataSource, required this.localDataSource});

  final OrderRemoteDataSource remoteDataSource;
  final OrderLocalDataSource localDataSource;

  @override
  Future<Order> getOrder(String id) async {
    try {
      final dto = await remoteDataSource.fetchOrder(id);
      final order = dto.toDomain();
      await localDataSource.cacheOrder(order);
      return order;
    } on DioException {
      final cached = await localDataSource.getCachedOrder(id);
      if (cached != null) return cached;
      rethrow;
    }
  }
}

// Riverpod provider
@riverpod
OrderRepository orderRepository(Ref ref) {
  return OrderRepositoryImpl(
    remoteDataSource: ref.watch(orderRemoteDataSourceProvider),
    localDataSource: ref.watch(orderLocalDataSourceProvider),
  );
}
```

**Rules:**
- Repositories abstract data access. The domain layer defines the interface, the
  data layer provides the implementation.
- Data sources handle raw API calls and local database queries. Repositories
  coordinate between data sources and map DTOs to domain entities.
- Use `freezed` for both DTOs and domain entities. DTOs have `fromJson`/`toJson`,
  domain entities do not.
- Never expose `Dio`, `Response`, or data-layer types to the presentation layer.
- Handle errors in repositories. Convert exceptions to typed failures.

### Freezed Models

```dart
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

@freezed
class OrderDto with _$OrderDto {
  const factory OrderDto({
    required String id,
    @JsonKey(name: 'customer_id') required String customerId,
    required List<OrderItemDto> items,
    required String status,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _OrderDto;

  factory OrderDto.fromJson(Map<String, dynamic> json) =>
      _$OrderDtoFromJson(json);
}

extension OrderDtoMapper on OrderDto {
  Order toDomain() => Order(
    id: id,
    customerId: customerId,
    items: items.map((i) => i.toDomain()).toList(),
    status: OrderStatus.values.byName(status),
    createdAt: createdAt,
  );
}
```

---

## Theming

```dart
class AppTheme {
  static ThemeData light() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF1A73E8),
      brightness: Brightness.light,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: _textTheme,
      appBarTheme: AppBarTheme(
        centerTitle: false,
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
      ),
    );
  }

  static ThemeData dark() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF1A73E8),
      brightness: Brightness.dark,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: _textTheme,
    );
  }

  static const _textTheme = TextTheme(
    headlineLarge: TextStyle(fontWeight: FontWeight.w700),
    titleMedium: TextStyle(fontWeight: FontWeight.w600),
  );
}
```

**Rules:**
- Define themes in `core/theme/`. Never hardcode colors, font sizes, or spacing
  in widgets.
- Use `Theme.of(context).colorScheme` and `Theme.of(context).textTheme` to
  access theme values. Never reference color constants directly in widgets.
- Use `ColorScheme.fromSeed` for Material 3 dynamic color generation.
- Support both light and dark themes from day one.
- Use `MediaQuery` and `LayoutBuilder` for responsive layouts, not hardcoded
  breakpoints.

---

## Error Handling

```dart
// Typed failure hierarchy
sealed class Failure {
  const Failure(this.message);
  final String message;
}

class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'Network error']);
}

class ServerFailure extends Failure {
  const ServerFailure(super.message);
}

class CacheFailure extends Failure {
  const CacheFailure([super.message = 'Cache error']);
}

// Either-style result using freezed
@freezed
class Result<T> with _$Result<T> {
  const factory Result.success(T data) = Success<T>;
  const factory Result.failure(Failure failure) = ResultFailure<T>;
}
```

**Rules:**
- Use sealed classes for failure types. Never throw raw exceptions across
  layer boundaries.
- Catch exceptions at the repository level and convert to typed failures.
- Use `AsyncValue` from Riverpod for presentation-layer error handling.
- Log errors with context (operation, parameters) but never log secrets or PII.
- Show user-friendly error messages. Map `Failure` types to localized strings
  in the presentation layer.

---

## Naming Conventions

| Element              | Convention         | Example                        |
|----------------------|--------------------|--------------------------------|
| Files                | `snake_case`       | `order_repository.dart`        |
| Classes              | `PascalCase`       | `OrderRepository`              |
| Functions/methods    | `camelCase`        | `getOrderById()`               |
| Variables            | `camelCase`        | `orderTotal`                   |
| Constants            | `camelCase`        | `defaultTimeout`               |
| Enums                | `PascalCase.camelCase` | `OrderStatus.pending`      |
| Extensions           | `PascalCase`       | `StringExtensions`             |
| Providers            | `camelCase + Provider` | `orderRepositoryProvider`  |
| Private members      | `_` prefix         | `_internalState`               |
| Typedefs             | `PascalCase`       | `JsonMap`                      |
| Named parameters     | `camelCase`        | `{required String orderId}`    |
| Test descriptions    | Sentence case      | `'should return order when found'` |

**Rules:**
- Follow official Dart style guide (dart.dev/effective-dart/style).
- One public class per file. File name matches the class in `snake_case`.
- Use `part` directives only for generated files (`.g.dart`, `.freezed.dart`).
- Prefix private members with `_`. No public fields that should be private.
- Widget files are named after the widget: `order_card.dart` for `OrderCard`.

---

## Do / Don't

### Do
- Use `const` constructors on all widgets and objects that support it.
- Use `freezed` for immutable data classes with `copyWith` and equality.
- Use Riverpod code generation (`@riverpod` annotation) for all providers.
- Use `ref.watch` in `build`, `ref.read` in callbacks.
- Use GoRouter for declarative, deep-linkable navigation.
- Use `AsyncValue.when` for loading/error/data states.
- Use `Theme.of(context)` for all visual properties.
- Use `dart format` and enforce it in CI.
- Use `const` wherever Dart allows it — widgets, constructors, collections.
- Extract widgets into classes, not helper methods.
- Separate DTOs from domain entities with explicit mapping.

### Don't
- Don't use `setState` when Riverpod can manage the state.
- Don't use `BuildContext` across async gaps — it may be unmounted.
- Don't use `get_it` or other service locators — Riverpod is the DI solution.
- Don't write manual providers — use `riverpod_generator`.
- Don't use `print()` for logging — use a proper logger (`logger` package).
- Don't hardcode strings — use `l10n` for user-facing text.
- Don't use `dynamic` types. Use `Object?` and type-check.
- Don't use `!` (null assertion) without a preceding null check. Prefer `?.` or
  pattern matching.
- Don't nest `Builder` widgets to work around `BuildContext` issues — restructure
  the widget tree instead.
- Don't use mutable state in providers — use `copyWith` on immutable objects.
- Don't import `dart:io` in code that targets web — use conditional imports.

---

## Common Pitfalls

1. **Helper methods returning widgets.** `Widget _buildHeader()` bypasses the
   widget tree identity system. Flutter cannot diff helper-method results
   efficiently — it rebuilds the entire subtree every time. Extract a separate
   `StatelessWidget` instead.
2. **Using `BuildContext` after `await`.** After an async gap, the widget may
   have been unmounted. Check `context.mounted` before using context, or
   restructure to avoid the pattern entirely.
3. **Missing `const` constructors.** Without `const`, Flutter creates new widget
   instances every rebuild, defeating tree diffing. Add `const` to every
   constructor and instantiation site that allows it.
4. **Provider spaghetti.** Deeply chained providers (A watches B watches C
   watches D) are hard to debug and cause cascading rebuilds. Keep dependency
   chains to three levels or fewer.
5. **Forgetting `build_runner`.** After modifying `freezed` or `riverpod`
   annotated classes, `dart run build_runner build` must be run. Stale generated
   files cause confusing type errors.
6. **Blocking the UI thread with `compute`.** `Isolate.run` (Dart 3+) is
   preferred over `compute` for running expensive work off the main isolate.
   But most JSON parsing and list operations do not need isolates — profile
   before optimizing.
7. **Platform-specific imports on web.** Importing `dart:io` in code that runs
   on Flutter Web causes compilation failures. Use conditional imports
   (`import 'stub.dart' if (dart.library.io) 'io_impl.dart'`).
8. **Oversized widgets.** A single `build` method with 200+ lines of nested
   widgets is unreadable and defeats Flutter's efficient rebuild system. Break
   it into focused child widgets with `const` constructors.
9. **Not disposing controllers.** `TextEditingController`, `AnimationController`,
   `ScrollController`, and `FocusNode` must be disposed in `dispose()`. Failing
   to do so leaks memory and listeners.
10. **Ignoring `analysis_options.yaml`.** Suppressing lint warnings instead of
    fixing them masks real issues. Treat all lints as errors in CI.

---

## Checklist

Before merging any Flutter PR, verify:

- [ ] `dart format` applied; CI rejects unformatted code
- [ ] `flutter analyze` passes with zero warnings
- [ ] All generated files up to date (`dart run build_runner build --delete-conflicting-outputs`)
- [ ] `const` used on all constructors and instantiations that allow it
- [ ] No helper methods returning widgets — extracted as separate widget classes
- [ ] State managed through Riverpod providers, not `setState` (unless lifecycle-specific)
- [ ] `ref.watch` used only in `build`; `ref.read` used in callbacks
- [ ] `AsyncValue.when` used for loading/error/data — no manual loading booleans
- [ ] `BuildContext` not used after `await` without `mounted` check
- [ ] Navigation uses GoRouter; no `Navigator.push` calls
- [ ] Colors and text styles come from `Theme.of(context)` — no hardcoded values
- [ ] User-facing strings use `l10n` — no hardcoded text
- [ ] DTOs and domain entities are separate `freezed` classes with explicit mapping
- [ ] Controllers disposed in `dispose()` method
- [ ] Unit tests cover providers and use cases
- [ ] Widget tests cover critical UI behavior
- [ ] No `dart:io` imports in code that targets web
- [ ] No `dynamic` types — `Object?` with type checks used instead
- [ ] `pubspec.lock` committed
