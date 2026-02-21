# Kotlin Testing

Testing strategy, patterns, and tooling for Kotlin applications. Covers unit
tests, integration tests, coroutine testing, Android UI testing, and test
data management.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| Test Framework       | JUnit 5 + kotlin-test                | ADR               |
| Assertions           | kotlin-test assertions + AssertJ     | ADR               |
| Mocking              | MockK                                | ADR               |
| Coroutine Testing    | kotlinx-coroutines-test              | Never             |
| Integration Infra    | Testcontainers                       | ADR               |
| HTTP Testing         | MockMvc / WebTestClient              | ADR               |
| Android UI Testing   | Compose Testing + Espresso           | ADR               |
| Android Unit Testing | Robolectric                          | ADR               |
| Coverage Tool        | JaCoCo                               | Never             |
| Coverage Threshold   | 80% lines                            | Never lower       |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| MockK                | Mockito-Kotlin       | Team already using Mockito            |
| JUnit 5              | Kotest               | Prefer spec-style / property-based testing |
| AssertJ              | Strikt / Hamcrest    | Kotlin-idiomatic assertions preferred |
| Testcontainers       | Docker Compose       | Complex multi-service setups          |
| Robolectric          | Instrumented tests   | Need real Android framework behavior  |

---

## Unit Tests

```kotlin
class OrderServiceTest {
    private val repository = mockk<OrderRepository>()
    private val service = OrderService(repository)

    @Test
    fun `calculates total with discount`() {
        // Given
        val order = Order(id = "ORD-1", amount = BigDecimal("100.00"))
        coEvery { repository.findById("ORD-1") } returns order

        // When
        val total = runTest { service.calculateTotal("ORD-1", discountPercent = 10) }

        // Then
        assertThat(total).isEqualByComparingTo(BigDecimal("90.00"))
        coVerify(exactly = 1) { repository.findById("ORD-1") }
    }

    @Test
    fun `throws NotFound when order is missing`() {
        coEvery { repository.findById(any()) } returns null

        assertThrows<DomainError.NotFound> {
            runTest { service.calculateTotal("ORD-X", discountPercent = 10) }
        }
    }
}
```

**Rules:**
- Use backtick-quoted test method names for readability:
  `` `returns 404 when order not found`() ``.
- Use Given/When/Then structure within each test.
- Use MockK for mocking. Use `coEvery` / `coVerify` for suspend functions.
- Test both success and error paths for every public function.
- Keep tests focused: one assertion concept per test method.

---

## Coroutine Testing

```kotlin
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.UnconfinedTestDispatcher

class OrderProcessorTest {
    @Test
    fun `processes all orders concurrently`() = runTest {
        val processor = OrderProcessor(
            dispatcher = UnconfinedTestDispatcher(testScheduler)
        )

        val results = processor.processBatch(listOf("ORD-1", "ORD-2", "ORD-3"))
        advanceUntilIdle()

        assertThat(results).hasSize(3)
        assertThat(results).allMatch { it.status == "PROCESSED" }
    }

    @Test
    fun `cancels processing on timeout`() = runTest {
        val processor = OrderProcessor(
            dispatcher = UnconfinedTestDispatcher(testScheduler)
        )

        assertThrows<TimeoutCancellationException> {
            withTimeout(100) {
                processor.processSlowOrder("ORD-1")
            }
        }
    }
}

// Testing Flow emissions
class OrderFlowTest {
    @Test
    fun `emits orders in sequence`() = runTest {
        val flow = orderService.observeOrders()

        val emissions = flow.take(3).toList()

        assertThat(emissions).hasSize(3)
        assertThat(emissions.map { it.id }).containsExactly("ORD-1", "ORD-2", "ORD-3")
    }

    @Test
    fun `turbine - emits loading then content`() = runTest {
        viewModel.uiState.test {
            assertThat(awaitItem()).isInstanceOf(UiState.Loading::class.java)
            assertThat(awaitItem()).isInstanceOf(UiState.Content::class.java)
            cancelAndConsumeRemainingEvents()
        }
    }
}
```

**Rules:**
- Use `runTest` from kotlinx-coroutines-test for all coroutine tests. It
  auto-advances virtual time.
- Inject `TestDispatcher` into classes under test instead of hardcoding
  dispatchers.
- Use `UnconfinedTestDispatcher` for eager execution in simple tests.
  Use `StandardTestDispatcher` when you need to control timing.
- Use `advanceUntilIdle()` to process all pending coroutines.
- Use Turbine (`app.cash.turbine`) for testing `Flow` emissions.
- Test cancellation behavior explicitly with `withTimeout` or `cancel()`.

---

## Integration Tests (Spring Boot + Testcontainers)

```kotlin
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {
    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:16-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test")

        @JvmStatic
        @DynamicPropertySource
        fun configureProperties(registry: DynamicPropertyRegistry) {
            registry.add("spring.datasource.url", postgres::getJdbcUrl)
            registry.add("spring.datasource.username", postgres::getUsername)
            registry.add("spring.datasource.password", postgres::getPassword)
        }
    }

    @Autowired
    lateinit var webTestClient: WebTestClient

    @Test
    fun `creates and retrieves order`() {
        val createRequest = CreateOrderRequest(
            productId = "P-1",
            quantity = 2,
            customerId = "C-1",
        )

        val location = webTestClient.post()
            .uri("/api/orders")
            .bodyValue(createRequest)
            .exchange()
            .expectStatus().isCreated
            .returnResult<Unit>()
            .responseHeaders.location

        webTestClient.get()
            .uri(location!!)
            .exchange()
            .expectStatus().isOk
            .expectBody()
            .jsonPath("$.productId").isEqualTo("P-1")
            .jsonPath("$.quantity").isEqualTo(2)
    }
}
```

**Rules:**
- Use `@Testcontainers` with `@Container` for infrastructure dependencies.
- Pin container image tags for reproducibility (`postgres:16-alpine`, not
  `postgres:latest`).
- Use `@DynamicPropertySource` to inject container connection details.
- Use `WebTestClient` for reactive / coroutine endpoints; `MockMvc` for
  traditional servlet endpoints.
- Test error responses (400, 404, 500) as thoroughly as success responses.
- Never use H2 as a stand-in for PostgreSQL in integration tests.

---

## Android Testing

```kotlin
// ViewModel unit test with coroutines
@OptIn(ExperimentalCoroutinesApi::class)
class OrderViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val repository = mockk<OrderRepository>()
    private val viewModel = OrderViewModel(repository)

    @Test
    fun `loads orders on init`() = runTest {
        coEvery { repository.getOrders() } returns listOf(testOrder)

        viewModel.uiState.test {
            assertThat(awaitItem()).isInstanceOf(UiState.Loading::class.java)
            val content = awaitItem() as UiState.Content
            assertThat(content.orders).hasSize(1)
        }
    }
}

// MainDispatcherRule for replacing Main dispatcher in tests
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Compose UI test
class OrderScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `displays order list`() {
        composeTestRule.setContent {
            OrderScreen(orders = listOf(testOrder))
        }

        composeTestRule.onNodeWithText("Order #ORD-1").assertIsDisplayed()
        composeTestRule.onNodeWithText("$100.00").assertIsDisplayed()
    }
}
```

**Rules:**
- Use `MainDispatcherRule` to replace `Dispatchers.Main` in unit tests.
- Test ViewModels as unit tests with MockK and `runTest`.
- Test Compose UI with `createComposeRule()` and semantic matchers.
- Use Robolectric for tests that need Android framework classes without an
  emulator.
- Use instrumented tests (`androidTest/`) only for tests that need real device
  behavior.

---

## Test Data and Fixtures

```kotlin
// Object mothers for test data
object OrderFixtures {
    fun anOrder(
        id: String = "ORD-1",
        amount: BigDecimal = BigDecimal("100.00"),
        status: OrderStatus = OrderStatus.PENDING,
        customerId: String = "C-1",
    ) = Order(id = id, amount = amount, status = status, customerId = customerId)

    fun aCreateRequest(
        productId: String = "P-1",
        quantity: Int = 1,
        customerId: String = "C-1",
    ) = CreateOrderRequest(productId = productId, quantity = quantity, customerId = customerId)
}

// Usage in tests
val order = OrderFixtures.anOrder(status = OrderStatus.COMPLETED)
val request = OrderFixtures.aCreateRequest(quantity = 5)
```

**Rules:**
- Use object mothers (factory functions with defaults) for test data. Avoid
  constructing test objects inline in every test.
- Use named parameters to override only what matters for each test case.
- Keep fixture files in a `fixture/` package parallel to test code.
- Never use random data in assertions. Tests must be deterministic.

---

## Do / Don't

### Do
- Use backtick-quoted test method names for readability.
- Use `runTest` for all coroutine tests.
- Use MockK with `coEvery` / `coVerify` for suspending function mocks.
- Use Turbine for testing `Flow` emissions.
- Inject `TestDispatcher` into classes that use dispatchers.
- Use Testcontainers for integration tests with real databases.
- Use object mothers with default parameters for test data.
- Test error paths as thoroughly as success paths.

### Don't
- Use `runBlocking` in tests. Use `runTest` which controls virtual time.
- Use `Thread.sleep` in tests. Use `advanceTimeBy` or `advanceUntilIdle`.
- Test private functions directly. Test the public API.
- Share mutable state across tests without proper isolation.
- Use H2 as a stand-in for PostgreSQL in integration tests.
- Use `Dispatchers.Main` in unit tests without `MainDispatcherRule`.
- Mock data classes. They are value types; construct real instances.
- Over-mock: if a dependency is simple and deterministic, use the real
  implementation.

---

## Common Pitfalls

1. **Using `runBlocking` instead of `runTest`** -- `runBlocking` blocks the
   thread and doesn't advance virtual time. `runTest` handles coroutine
   timing, delay skipping, and uncaught exception detection.
2. **Missing `MainDispatcherRule`** -- Tests that use `Dispatchers.Main`
   (e.g., ViewModel tests) fail without replacing the Main dispatcher.
   Always use `MainDispatcherRule` with `UnconfinedTestDispatcher`.
3. **Flaky tests from shared mutable state** -- Singletons or shared `mockk`
   instances carry state between tests. Use `clearAllMocks()` in `@BeforeEach`
   or create fresh mocks per test.
4. **Not testing cancellation** -- Coroutines can be cancelled at any
   suspension point. Test that your code handles `CancellationException`
   correctly (cleanup runs, resources released).
5. **Testing Flow without Turbine** -- Collecting a `Flow` with `toList()`
   in tests can hang if the flow never completes. Turbine provides structured
   assertion APIs with timeouts.
6. **Mocking data classes** -- MockK can mock data classes but it breaks
   `equals`, `hashCode`, and `copy`. Construct real instances instead.
7. **Integration test pollution** -- Tests that don't clean up database state
   affect subsequent tests. Use `@Transactional` (rolls back after each test)
   or truncate tables in `@BeforeEach`.

---

## Checklist

- [ ] Unit tests cover new/changed service and domain logic.
- [ ] Backtick-quoted test method names describe behavior.
- [ ] `runTest` used for all coroutine tests (not `runBlocking`).
- [ ] MockK used with `coEvery` / `coVerify` for suspend functions.
- [ ] `TestDispatcher` injected into classes under test.
- [ ] `MainDispatcherRule` used for tests involving `Dispatchers.Main`.
- [ ] Flow emissions tested with Turbine.
- [ ] Integration tests use Testcontainers with pinned image tags.
- [ ] Integration tests clean up state (`@Transactional` or truncation).
- [ ] Coverage meets or exceeds 80% lines (JaCoCo).
- [ ] Test fixtures use object mothers with default parameters.
- [ ] Error paths and cancellation behavior tested.
- [ ] No `Thread.sleep` in tests; virtual time used.
- [ ] Android: Compose UI tests use `createComposeRule()` with semantic matchers.
