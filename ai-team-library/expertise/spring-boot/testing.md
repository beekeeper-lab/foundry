# Spring Boot Testing

How to test Spring Boot services without a minutes-long suite. The core rule:
**the amount of Spring context a test boots must be proportional to what it
verifies.** Most tests need no context at all.

---

## 1. The Test Pyramid, Boot Edition

| Layer | Tool | Spring context | Share of suite |
|-------|------|----------------|----------------|
| Domain / service logic | Plain JUnit 5 + Mockito | None | Most |
| Web layer | `@WebMvcTest` + MockMvc | Web slice only | Some |
| Persistence | `@DataJpaTest` / `@JdbcTest` + Testcontainers | Data slice only | Some |
| Wiring / end-to-end | `@SpringBootTest` + Testcontainers | Full | Few |

- Services use constructor injection (see `conventions.md`), so unit tests
  are `new OrderService(mockRepo, fixedClock)` — no runner, no context,
  sub-millisecond.
- Reserve `@SpringBootTest` for verifying that the application actually wires
  and for a small set of end-to-end smoke flows. It is not the default test
  annotation.

---

## 2. Slice Tests

### Web slice: `@WebMvcTest`

Boots controllers, converters, validation, and your `@RestControllerAdvice` —
nothing else. Mock the service boundary.

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvc mvc;
    @MockitoBean OrderService orderService;

    @Test
    void returnsProblemDetailWhenMissing() throws Exception {
        when(orderService.find("42")).thenThrow(new OrderNotFoundException("42"));
        mvc.perform(get("/api/v1/orders/42"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.status").value(404));
    }
}
```

- Use `@MockitoBean` (Boot 3.4+; replaces the deprecated `@MockBean`).
- Assert the error contract here — status codes and ProblemDetail shape are
  web-slice behavior, not service behavior.
- On the reactive stack, the equivalent is `@WebFluxTest` + `WebTestClient`.
  `WebTestClient` also works against a running server in `@SpringBootTest`
  with `webEnvironment = RANDOM_PORT`.

### Persistence slice: `@DataJpaTest` / `@JdbcTest`

- Test custom queries, mappings, and projections — not Spring Data's own CRUD.
- Run against the real database engine via Testcontainers, never H2: dialect
  differences make H2 green/prod red a recurring failure mode.
- `@DataJpaTest` is transactional-with-rollback by default; remember flushes
  (`TestEntityManager.flush()`) when asserting constraint violations.

---

## 3. Testcontainers

- Add `@ServiceConnection` on the container field (Boot 3.1+) and Boot wires
  the datasource/broker connection automatically — no
  `@DynamicPropertySource` boilerplate for supported types.

```java
@Testcontainers
@DataJpaTest(properties = "spring.jpa.hibernate.ddl-auto=validate")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class OrderRepositoryTest {
    @Container @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
}
```

- Make containers `static` so they are shared across test methods; reuse one
  container per suite rather than one per class where startup cost matters.
- Run Flyway migrations in the container (`ddl-auto: validate`) so tests also
  verify the migration chain.
- Local dev bonus: a `@TestConfiguration` with `@ServiceConnection` beans plus
  `./gradlew bootTestRun` gives a full local stack with zero installed
  infrastructure.

---

## 4. Full-Context Tests

- One `@SpringBootTest(webEnvironment = RANDOM_PORT)` smoke class that boots
  the app against Testcontainers and exercises 2-3 critical flows
  end-to-end over HTTP (`TestRestTemplate` or `WebTestClient`).
- Context caching: Spring caches contexts keyed by configuration. Every
  distinct combination of `properties`, `@MockitoBean`, `@ActiveProfiles`,
  or `@DirtiesContext` forces a new boot. Standardize on a small number of
  test configurations and the suite pays boot cost once, not per class.
- `@DirtiesContext` is a smell; find and fix the state leak instead.
- Use a dedicated `test` profile for test-only overrides; never point tests
  at shared/dev infrastructure.

---

## 5. What to Assert

- **Behavior through the boundary**, not interactions: prefer asserting the
  HTTP response / persisted row over `verify(...)` call counts.
- **The error contract**: every custom exception mapped in the advice has a
  slice test pinning status + ProblemDetail fields.
- **Config binding**: one test binds each `@ConfigurationProperties` record
  from sample YAML and asserts validation failures for missing values.
- **Query counts** for hot read paths: assert statement counts (Hibernate
  statistics or a proxy datasource) to lock out N+1 regressions.

---

## Checklist

- [ ] Service logic covered by plain JUnit tests with no Spring context.
- [ ] Controllers + advice covered by `@WebMvcTest` with `@MockitoBean`.
- [ ] Custom queries covered by `@DataJpaTest`/`@JdbcTest` on the real engine.
- [ ] Testcontainers with `@ServiceConnection`; no H2 stand-ins.
- [ ] Flyway migrations exercised in tests (`ddl-auto: validate`).
- [ ] Exactly one full `@SpringBootTest` smoke configuration; context cache hits high.
- [ ] No `@DirtiesContext` without a justifying comment.
- [ ] ProblemDetail error contract pinned by tests per exception type.
