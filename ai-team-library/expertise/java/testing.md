# Java Testing

Testing strategy, patterns, and tooling for Java applications with Spring Boot.
Covers unit tests, integration tests, slice tests, and test data management.

---

## Defaults

| Concern             | Default Choice                       | Override Requires |
|---------------------|--------------------------------------|-------------------|
| Test Framework      | JUnit 5 (Jupiter)                    | Never             |
| Mocking             | Mockito                              | ADR               |
| Assertions          | AssertJ                              | ADR               |
| Integration Infra   | Testcontainers                       | ADR               |
| Slice Tests         | `@WebMvcTest`, `@DataJpaTest`        | --                |
| Coverage Tool       | JaCoCo                               | ADR               |
| Coverage Threshold  | 80 % lines, branch preferred         | Never lower       |

### Alternatives

| Primary        | Alternative          | When                                  |
|----------------|----------------------|---------------------------------------|
| Mockito        | Mockito + MockK      | Kotlin modules in the project         |
| AssertJ        | Hamcrest             | Legacy test suites, not worth migrating |
| Testcontainers | Embedded H2          | Never for integration -- H2 hides DB-specific bugs |
| JaCoCo         | IntelliJ built-in    | Local dev only, not CI                |

---

## Unit Tests

Unit tests verify services and domain logic in isolation. Dependencies are
mocked with Mockito.

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PricingService pricingService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void calculatesOrderTotalWithDiscount() {
        when(pricingService.getDiscount("VIP")).thenReturn(new Discount(10));
        when(orderRepository.findById("ORD-1"))
            .thenReturn(Optional.of(new Order("ORD-1", 100_00)));

        var result = orderService.calculateTotal("ORD-1", "VIP");

        assertThat(result.total()).isEqualTo(90_00);
        assertThat(result.discount()).isEqualTo(10_00);
    }

    @Test
    void throwsNotFoundWhenOrderMissing() {
        when(orderRepository.findById("ORD-X")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.calculateTotal("ORD-X", "VIP"))
            .isInstanceOf(OrderNotFoundException.class)
            .hasMessageContaining("ORD-X");
    }
}
```

**Rules:**
- Use `@ExtendWith(MockitoExtension.class)`, not `@SpringBootTest`, for unit
  tests. Spring context startup is unnecessary and slow.
- Use `@InjectMocks` + `@Mock` for constructor-injected dependencies.
- One logical assertion per test. Multiple `assertThat` calls that verify a
  single outcome are fine.
- Test method names describe the behavior: `calculatesOrderTotalWithDiscount`.

---

## Integration Tests (Testcontainers)

Integration tests boot the full Spring context against real infrastructure.

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class OrderControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createsOrderAndReturns201() throws Exception {
        mockMvc.perform(post("/v1/orders")
                .contentType("application/json")
                .content("""
                    {"productId": "P-1", "quantity": 2}
                    """))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.productId").value("P-1"))
            .andExpect(jsonPath("$.quantity").value(2));
    }

    @Test
    void returnsBadRequestForInvalidInput() throws Exception {
        mockMvc.perform(post("/v1/orders")
                .contentType("application/json")
                .content("{}"))
            .andExpect(status().isBadRequest());
    }
}
```

**Rules:**
- Never use H2 for integration tests. Use Testcontainers with the production
  database engine (Postgres, MySQL, etc.).
- Use `@DynamicPropertySource` to wire container URLs into Spring config.
- Use `@Sql` or repository setup in `@BeforeEach` to prepare test data.
- Clean state between tests with `@Transactional` (auto-rollback) or truncation.

---

## Slice Tests

| Annotation        | What It Tests                | Loads              |
|-------------------|------------------------------|--------------------|
| `@WebMvcTest`     | Controllers + validation     | MVC layer only     |
| `@DataJpaTest`    | Repositories + queries       | JPA layer only     |
| `@JsonTest`       | JSON serialization/deser     | Jackson only       |

Use slice tests for fast, focused feedback. They are faster than full
`@SpringBootTest` and catch most regressions.

---

## Do / Don't

### Do
- Use AssertJ fluent assertions over JUnit's `assertEquals`.
- Name test methods as behavior descriptions, not `testXxx`.
- Test error paths (exceptions, 400s, 404s) as thoroughly as success paths.
- Use `@ParameterizedTest` with `@CsvSource` or `@MethodSource` for data-driven tests.
- Run tests in CI on every push; a failing test blocks merge.
- Pin Testcontainer image tags for reproducibility.

### Don't
- Use `@SpringBootTest` for unit tests -- it is slow and unnecessary.
- Use H2 as a stand-in for Postgres/MySQL -- SQL dialect differences hide bugs.
- Share mutable state across tests without resetting in `@BeforeEach`.
- Write tests that depend on execution order.
- Ignore flaky tests -- fix them immediately or quarantine with a tracking issue.
- Mock the class under test. Mock only its dependencies.

---

## Common Pitfalls

1. **Slow test suites from `@SpringBootTest` overuse** -- Every
   `@SpringBootTest` starts a new application context unless cached. Use slice
   tests and unit tests for the majority of coverage.
2. **Test pollution via shared `static` state** -- Static fields survive across
   tests in the same JVM. Avoid mutable statics; use `@BeforeEach` resets.
3. **Missing `@Transactional` on integration tests** -- Without it, test data
   persists across tests, causing order-dependent failures.
4. **Mocking concrete classes** -- Mockito creates subclass proxies for
   concrete classes, which breaks with `final` classes. Mock interfaces or
   use `mockito-inline`.
5. **Brittle JSON assertions** -- Asserting on the entire JSON string breaks
   when any field is added. Use `jsonPath` or `assertThat` on deserialized
   objects.
6. **Ignoring test output** -- Warnings like "No tests found" or "Context
   failed to load" are real problems, not noise.

---

## Checklist

- [ ] Unit tests cover new/changed service and domain logic.
- [ ] Integration tests cover new/changed endpoints (success + error paths).
- [ ] Slice tests used for controller validation and repository query logic.
- [ ] `@SpringBootTest` used only for full integration scenarios.
- [ ] Testcontainer images pinned to specific tags (e.g., `postgres:16-alpine`).
- [ ] `@BeforeEach` resets shared state; no test-order dependencies.
- [ ] Coverage meets or exceeds 80 % lines; branch coverage reviewed.
- [ ] No skipped tests (`@Disabled`) without a linked tracking issue.
- [ ] Test method names describe behavior, not implementation.
- [ ] CI runs all tests on every push; failures block merge.
