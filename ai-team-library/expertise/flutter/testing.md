# Flutter Testing Conventions

## Testing Pyramid

| Layer             | Tool                          | Scope                              | Speed     |
|-------------------|-------------------------------|------------------------------------|-----------|
| Unit              | `flutter_test` + `mocktail`   | Providers, use cases, repositories | Fast      |
| Widget            | `flutter_test`                | Individual widgets, screens        | Fast      |
| Integration       | `integration_test`            | Full app flows on real device/emu  | Slow      |
| Golden            | `flutter_test` (matchesGoldenFile) | Visual regression snapshots   | Fast      |

---

## Unit Tests

Test providers, use cases, and repositories in isolation.

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:riverpod/riverpod.dart';

class MockOrderRepository extends Mock implements OrderRepository {}

void main() {
  late MockOrderRepository mockRepo;
  late ProviderContainer container;

  setUp(() {
    mockRepo = MockOrderRepository();
    container = ProviderContainer(
      overrides: [
        orderRepositoryProvider.overrideWithValue(mockRepo),
      ],
    );
  });

  tearDown(() => container.dispose());

  test('should return order when found', () async {
    final expected = Order(id: '1', customerId: 'c1', items: [], status: OrderStatus.pending, createdAt: DateTime.now());
    when(() => mockRepo.getOrder('1')).thenAnswer((_) async => expected);

    final result = await container.read(orderProvider('1').future);

    expect(result, equals(expected));
    verify(() => mockRepo.getOrder('1')).called(1);
  });
}
```

### Rules

- One test file per source file. Mirror the `lib/` directory structure in `test/`.
- Use `mocktail` for mocking. Create mock classes extending `Mock`.
- Use `ProviderContainer` with `overrides` to test Riverpod providers in isolation.
- Test behavior, not implementation. Assert on outputs and side effects, not
  internal state.
- Use `setUp` and `tearDown` for shared setup. Dispose containers in `tearDown`.
- Name tests as sentences: `'should return order when found'`.
- Group related tests with `group()`.

---

## Widget Tests

Test widget rendering, user interaction, and integration with providers.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

void main() {
  testWidgets('displays order details when loaded', (tester) async {
    final order = Order(
      id: '1',
      customerId: 'c1',
      items: [OrderItem(productId: 'p1', name: 'Widget', quantity: 2, price: 9.99)],
      status: OrderStatus.pending,
      createdAt: DateTime(2024, 1, 15),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          orderProvider('1').overrideWith((_) => Future.value(order)),
        ],
        child: const MaterialApp(
          home: OrderDetailScreen(orderId: '1'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Widget'), findsOneWidget);
    expect(find.text('Pending'), findsOneWidget);
  });

  testWidgets('shows error state on failure', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          orderProvider('1').overrideWith(
            (_) => Future.error(const ServerFailure('Not found')),
          ),
        ],
        child: const MaterialApp(
          home: OrderDetailScreen(orderId: '1'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Not found'), findsOneWidget);
  });

  testWidgets('navigates to detail on tap', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [/* ... */],
        child: MaterialApp.router(routerConfig: testRouter),
      ),
    );

    await tester.pumpAndSettle();
    await tester.tap(find.text('Order #1'));
    await tester.pumpAndSettle();

    expect(find.byType(OrderDetailScreen), findsOneWidget);
  });
}
```

### Rules

- Wrap widgets in `ProviderScope` with overrides — never depend on real backends.
- Wrap widgets in `MaterialApp` (or `MaterialApp.router` for navigation tests)
  to provide `Theme`, `MediaQuery`, and `Navigator`.
- Use `tester.pumpAndSettle()` after actions that trigger animations or async
  provider updates.
- Find widgets by `find.text()`, `find.byType()`, `find.byKey()`. Prefer
  `find.text` and `find.byKey` over `find.byType` for specificity.
- Test user interactions: `tester.tap()`, `tester.enterText()`, `tester.drag()`.
- Test loading, data, and error states for every async screen.

---

## Integration Tests

Test full user flows on a real device or emulator.

```dart
// integration_test/checkout_flow_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('complete checkout flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Browse products
    await tester.tap(find.text('Products'));
    await tester.pumpAndSettle();

    // Add to cart
    await tester.tap(find.byKey(const Key('add-to-cart-p1')));
    await tester.pumpAndSettle();

    // Go to cart
    await tester.tap(find.byIcon(Icons.shopping_cart));
    await tester.pumpAndSettle();

    expect(find.text('1 item'), findsOneWidget);

    // Checkout
    await tester.tap(find.text('Checkout'));
    await tester.pumpAndSettle();

    expect(find.text('Order confirmed'), findsOneWidget);
  });
}
```

### Rules

- Integration tests live in `integration_test/` at the project root.
- Cover critical user journeys: onboarding, login, core transactions.
- Keep the number of integration tests small — they are slow and brittle.
- Use `find.byKey()` with explicit `Key` values for stable element identification.
- Run on both iOS and Android before release:
  `flutter test integration_test --device-id=<device>`.

---

## Golden Tests

Catch visual regressions with snapshot comparisons.

```dart
testWidgets('order card matches golden', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [/* ... */],
      child: const MaterialApp(
        home: Scaffold(body: OrderCard(order: testOrder)),
      ),
    ),
  );
  await tester.pumpAndSettle();

  await expectLater(
    find.byType(OrderCard),
    matchesGoldenFile('goldens/order_card.png'),
  );
});
```

### Rules

- Store golden files in `test/goldens/` with descriptive names.
- Update goldens explicitly: `flutter test --update-goldens`.
- Run golden tests on CI with a consistent platform (Linux) to avoid
  platform-specific rendering differences.
- Use `materialAppWrapper` or equivalent to ensure consistent theme and locale.

---

## Test Helpers

Create shared test utilities in `test/helpers/`.

```dart
// test/helpers/pump_app.dart
extension PumpApp on WidgetTester {
  Future<void> pumpApp(
    Widget widget, {
    List<Override> overrides = const [],
    GoRouter? router,
  }) async {
    await pumpWidget(
      ProviderScope(
        overrides: overrides,
        child: router != null
            ? MaterialApp.router(routerConfig: router)
            : MaterialApp(home: widget),
      ),
    );
  }
}

// test/helpers/fakes.dart
class FakeOrder {
  static Order create({
    String id = '1',
    String customerId = 'c1',
    OrderStatus status = OrderStatus.pending,
  }) =>
      Order(
        id: id,
        customerId: customerId,
        items: const [],
        status: status,
        createdAt: DateTime(2024, 1, 15),
      );
}
```

### Rules

- Use extension methods on `WidgetTester` for common pump patterns.
- Use factory classes (`FakeOrder.create()`) for test data with sensible defaults.
- Register fallback values for `mocktail` in `setUpAll`:
  `registerFallbackValue(const CreateOrderRequest(...))`.
- Never share mutable state between tests. Create fresh mocks in `setUp`.

---

## Coverage

- Target 80%+ line coverage for `lib/features/` and `lib/core/`.
- Run coverage: `flutter test --coverage`.
- View report: `genhtml coverage/lcov.info -o coverage/html`.
- Exclude generated files (`*.g.dart`, `*.freezed.dart`) from coverage reports
  in `pubspec.yaml` or CI configuration.
- CI must fail if coverage drops below threshold.
