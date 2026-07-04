---
id: spring-boot
category: Frameworks
entry: true
last-reviewed: 2026-07
---

# Spring Boot Conventions

## Category
Frameworks

Non-negotiable defaults for Spring Boot services on this team. This pack
composes with the `java` pack: generic Java guidance (formatting, naming,
logging, records-for-DTOs, exception hygiene) lives in
`expertise/java/conventions.md` and is not repeated here. This pack covers
what is Spring-Boot-specific: application slicing, injection discipline,
configuration, data access, transactions, and the web layer.

Deviations require an ADR with justification.

Sibling deep dives: `testing.md`, `observability.md`, `security.md`.

---

## Defaults

| Concern              | Default Choice                                   | Override Requires |
|----------------------|--------------------------------------------------|-------------------|
| Spring Boot version  | 3.x, current minor (3.4-era); never EOL minors   | ADR               |
| Java version         | 21 LTS floor (matches `java` pack)               | ADR               |
| Build                | Gradle with committed wrapper (`./gradlew`)      | ADR (Maven OK)    |
| Dependency injection | Constructor injection only                       | Never             |
| Configuration        | `@ConfigurationProperties` records over `@Value` | Never             |
| Config format        | `application.yml` + profile-specific overrides   | ADR               |
| Data access          | Spring Data JPA (disciplined) or `JdbcClient`    | ADR               |
| Integration tests    | Testcontainers against real infrastructure      | ADR               |
| Virtual threads      | `spring.threads.virtual.enabled: true` for blocking-IO services | ADR |
| Observability        | Actuator + Micrometer (metrics, health, tracing) | Never             |
| Error responses      | RFC 9457 via `ProblemDetail`                     | ADR               |

---

## 1. Project Layout and Slicing

Follow the package layout in the `java` pack (`config/`, `controller/`,
`service/`, `repository/`, `model/`). Spring-specific rules:

- One `@SpringBootApplication` class at the root package so component scanning
  covers the whole application without explicit `scanBasePackages`.
- Slice by feature when the service grows past a handful of aggregates
  (`orders/`, `billing/`, each with its own controller/service/repository),
  not by ever-deeper technical layers.
- Keep `@Configuration` classes small and topical (`JacksonConfig`,
  `ClockConfig`). No god-config class.
- Auto-configuration is the default; write explicit `@Bean` methods only when
  overriding Boot's opinion, and say why in a comment.
- Package-private visibility is the default for beans. Spring does not need
  `public` classes to inject them; enforce feature-slice boundaries with
  visibility (or ArchUnit tests) rather than convention alone.

---

## 2. Dependency Injection Discipline

- Constructor injection only. Single-constructor classes need no annotation;
  Spring autowires it. Never `@Autowired` on fields or setters.
- Declare dependencies as `private final`; let the constructor be the complete
  list of collaborators. More than ~6 constructor parameters means the class
  has too many responsibilities — split it.
- No `@Lazy`, `ObjectProvider`, or `ApplicationContext` lookups to paper over
  circular dependencies. A cycle is a design error: extract the shared piece.
- Do not inject prototype-scoped beans into singletons and expect fresh
  instances. If you need per-call state, pass it as a method argument.
- `@Component`/`@Service`/`@Repository` on classes Spring manages; plain `new`
  for value objects and domain logic that needs no container involvement.

---

## 3. Configuration and Profiles

- Bind all tunables through `@ConfigurationProperties` records with
  `@Validated` constraints. `@Value` is acceptable only for a single one-off
  scalar; two related values already justify a properties record.

```java
@Validated
@ConfigurationProperties(prefix = "app.orders")
public record OrdersProperties(
    @NotNull Duration paymentTimeout,
    @Min(1) int maxRetries) {}
```

- Register with `@EnableConfigurationProperties(OrdersProperties.class)` or
  `@ConfigurationPropertiesScan`; do not add `@Component` to the record.
- Profiles are for environment shape (`dev`, `prod`, `test`), not feature
  flags. Keep the profile set small; per-developer profiles are forbidden.
- `application.yml` holds safe defaults; environment-specific values come from
  environment variables or an external secret store. Never commit secrets —
  see `security.md`.
- Fail fast: missing required config should stop startup (validation on the
  properties record), not surface as a runtime NPE.

---

## 4. Data Access: JPA Discipline vs JdbcClient

Choose per service, record the choice:

- **Spring Data JPA** when the domain has rich aggregates and you will use its
  change tracking. Discipline is mandatory:
  - Disable open-session-in-view: `spring.jpa.open-in-view: false`. Always.
  - All associations `FetchType.LAZY`; load explicitly with `@EntityGraph` or
    `join fetch` per use case.
  - Repositories return entities to services only; controllers see DTOs
    (records) mapped in the service layer.
  - Use projections (interface or record) for read-heavy queries instead of
    loading full entities.
- **`JdbcClient`** (Boot 3.2+) when access is query-shaped: reporting,
  simple CRUD, batch jobs. Explicit SQL, no proxy magic, no dirty checking.
  Prefer it over raw `JdbcTemplate` for new code.
- Do not mix both styles against the same aggregate in the same service
  without an ADR.
- Schema changes go through a migration tool (Flyway default);
  `spring.jpa.hibernate.ddl-auto` is `validate` (or `none`) everywhere except
  throwaway prototypes.

---

## 5. Transactions

- `@Transactional` belongs on service methods, not repositories or
  controllers. One service method = one unit of work.
- Use `@Transactional(readOnly = true)` for query-only methods; it enables
  driver/ORM optimizations and documents intent.
- Spring's proxy-based AOP means **self-invocation bypasses the transaction**
  (see Common Pitfalls). Calling a `@Transactional` method from another method
  of the same class starts no transaction.
- Keep transactions short: no HTTP calls, message publishing, or file IO
  inside a transaction. Do slow work first or after commit
  (`@TransactionalEventListener(phase = AFTER_COMMIT)`).
- Checked exceptions do not roll back by default. Either use unchecked
  exceptions for failure paths (team default per the `java` pack) or declare
  `rollbackFor` explicitly.

---

## 6. REST Controllers and Error Handling

- Controllers are thin: bind + validate input (`@Valid` on request records),
  call one service method, map to a response DTO. No business logic.
- Version the API in the path (`/api/v1/...`). Return explicit status codes:
  `201` + `Location` for creation, `204` for deletes, never `200` with an
  error body.
- Error handling is centralized in one `@RestControllerAdvice` returning
  RFC 9457 `ProblemDetail`:

```java
@RestControllerAdvice
class ApiExceptionHandler {
    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail handleNotFound(OrderNotFoundException ex) {
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        pd.setProperty("orderId", ex.orderId());
        return pd;
    }
}
```

- Enable `spring.mvc.problemdetails.enabled: true` so framework errors
  (400s, 405s) use the same shape.
- Never leak stack traces, SQL, or internal class names in error responses;
  log the detail server-side with a correlation ID and return a generic
  message for 5xx.

---

## Do / Don't

### Do
- Pin the Boot version via the dependency-management plugin/BOM; upgrade
  minors promptly, majors via ADR.
- Run the app with the Gradle wrapper committed to the repo; CI uses the same
  wrapper.
- Enable virtual threads for servlet-stack services doing blocking IO; avoid
  `synchronized` around IO (pinning) — prefer `ReentrantLock` if you must lock.
- Use `RestClient` for outbound HTTP on the servlet stack (per `java` pack);
  set connect/read timeouts explicitly — defaults are not production-safe.
- Keep startup fail-fast: validated config, migration check, no lazy init in
  production.

### Don't
- Don't use field or setter injection, `@Lazy` cycles, or context lookups.
- Don't sprinkle `@Value` where a `@ConfigurationProperties` record belongs.
- Don't leave `spring.jpa.open-in-view` at its default (`true`).
- Don't expose JPA entities from controllers (see `java` pack) or accept them
  as request bodies.
- Don't call `@Transactional` / `@Cacheable` / `@Async` methods through `this`.
- Don't add starters speculatively; every dependency on the classpath changes
  auto-configuration behavior.

---

## Common Pitfalls

1. **Field injection.** `@Autowired` fields hide dependencies, block `final`,
   and make tests need reflection or a full context. Constructor injection is
   mechanical to migrate to — do it on touch.
2. **Open-session-in-view left enabled.** The default keeps a Hibernate
   session open through view rendering, masking lazy-loading bugs and holding
   DB connections across the whole request. Disable it; fetch what each use
   case needs explicitly.
3. **N+1 queries.** Lazy associations iterated in a loop issue one query per
   row. Detect in tests (assert statement counts with Hibernate statistics or
   a datasource proxy); fix with `@EntityGraph`, `join fetch`, or a
   projection. Do not "fix" with `EAGER`.
4. **`@Transactional` self-invocation.** Proxy-based AOP only intercepts
   external calls. `this.saveAll()` from the same class runs without a
   transaction — silently. Restructure so transactional entry points are
   called from outside the class, or split the class.
5. **Fat `@SpringBootTest` everywhere.** Booting the full context for every
   test makes the suite minutes-slow. Default to slices and plain unit tests;
   see `testing.md`.
6. **Timeouts left at defaults.** Outbound HTTP and pool settings default to
   values that hang under downstream failure. Set explicit connect/read
   timeouts and pool sizes in config, per environment.

---

## Checklist

- [ ] Boot 3.x current minor; Java 21 toolchain; Gradle wrapper committed.
- [ ] Constructor injection only; no `@Autowired` fields anywhere.
- [ ] All tunables in validated `@ConfigurationProperties` records.
- [ ] `spring.jpa.open-in-view: false`; all associations LAZY.
- [ ] Flyway migrations; `ddl-auto: validate` outside prototypes.
- [ ] `@Transactional` at the service layer; no self-invocation of advised methods.
- [ ] One `@RestControllerAdvice` returning `ProblemDetail`; problemdetails enabled.
- [ ] Explicit timeouts on every outbound HTTP client and connection pool.
- [ ] Virtual threads decision recorded (enabled for blocking-IO services).
- [ ] Actuator + Micrometer configured per `observability.md`.
- [ ] Security baseline per `security.md`; test posture per `testing.md`.
