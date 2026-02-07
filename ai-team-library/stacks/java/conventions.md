# Java Stack Conventions

Non-negotiable defaults for Java server-side applications on this team.
Targets modern Java (17+ / 21+ where virtual threads are available) with
Spring Boot as the default framework. Deviations require an ADR with
justification. "I prefer it differently" is not justification.

---

## Defaults

| Concern              | Default Choice                       | Override Requires |
|----------------------|--------------------------------------|-------------------|
| Java Version         | 21 LTS (virtual threads enabled)     | ADR               |
| Framework            | Spring Boot 3.x                      | ADR               |
| Build Tool           | Gradle (Kotlin DSL) or Maven         | ADR               |
| Formatter            | google-java-format                   | Never             |
| Linter               | Error Prone + SpotBugs               | ADR               |
| Logging              | SLF4J + Logback                      | Never             |
| DI                   | Constructor injection (Spring)       | Never             |
| Config               | `application.yml` + `@ConfigurationProperties` | ADR    |
| HTTP Client          | `RestClient` (Spring 6.1+) / `WebClient` | ADR          |
| Module System        | Multi-module Gradle/Maven project    | ADR               |

---

## Project Structure

```
project-root/
  src/
    main/
      java/com/example/orders/
        OrdersApplication.java        # @SpringBootApplication entry point
        config/                        # @Configuration, @ConfigurationProperties
        controller/                    # @RestController (thin, delegates to service)
        service/                       # Business logic (framework-agnostic)
        repository/                    # Data access (Spring Data / JDBC)
        model/
          entity/                      # JPA entities / DB-mapped records
          dto/                         # Request/response DTOs (records)
        exception/                     # Custom exceptions + @ControllerAdvice
        util/                          # Pure utility classes (no business logic)
      resources/
        application.yml
        application-dev.yml
        application-prod.yml
    test/
      java/com/example/orders/
        unit/                          # Mirror main structure
        integration/                   # @SpringBootTest with Testcontainers
        fixture/                       # Shared test data builders
  build.gradle.kts (or pom.xml)
  .editorconfig
  README.md
```

**Rules:**
- Controllers are thin: validate input, call service, return response. No
  business logic in controllers.
- Services are framework-agnostic. They accept and return domain types, not
  HTTP request/response objects.
- DTOs are Java `record` types (immutable, concise). Never expose JPA entities
  directly in API responses.
- One `@ControllerAdvice` handles all exception-to-HTTP mapping centrally.

---

## Formatting and Static Analysis

```kotlin
// build.gradle.kts
plugins {
    id("com.diffplug.spotless") version "6.25.0"
    id("net.ltgt.errorprone") version "4.0.1"
}

spotless {
    java {
        googleJavaFormat("1.22.0")
        removeUnusedImports()
        trimTrailingWhitespace()
    }
}

dependencies {
    errorprone("com.google.errorprone:error_prone_core:2.28.0")
}
```

**Rules:**
- `google-java-format` is the only formatter. No team-specific overrides.
- Error Prone runs on every build. New warnings break the build.
- Spotless check runs in CI. Unformatted code is rejected.
- Use `@SuppressWarnings` with a comment only when the warning is a false
  positive.

---

## Naming Conventions

| Element          | Convention      | Example                        |
|------------------|-----------------|--------------------------------|
| Packages         | `lowercase`     | `com.example.orders.service`   |
| Classes          | `PascalCase`    | `OrderService`                 |
| Methods          | `camelCase`     | `calculateTotal()`             |
| Constants        | `UPPER_SNAKE`   | `MAX_RETRY_COUNT`              |
| Local variables  | `camelCase`     | `orderTotal`                   |
| DTOs (records)   | `PascalCase`    | `CreateOrderRequest`           |
| Test methods     | `camelCase`     | `returnsNotFoundWhenMissing()` |

---

## Logging

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public Order process(String orderId) {
        log.info("order_processing_started orderId={}", orderId);
        // ... business logic ...
        log.info("order_processing_completed orderId={} durationMs={}", orderId, elapsed);
        return order;
    }
}
```

**Rules:**
- Use SLF4J parameterized logging (`{}` placeholders). Never string-concatenate
  log messages.
- Use static event-name prefixed messages with key=value structured context.
- Log levels: `DEBUG` for developer diagnostics, `INFO` for operational events,
  `WARN` for recoverable problems, `ERROR` for failures requiring attention.
- Never log secrets, tokens, passwords, or full PII.
- Configure JSON output in production (Logstash encoder), human-readable in dev.

---

## Do / Don't

### Do
- Use Java records for DTOs, value objects, and configuration properties.
- Prefer constructor injection; mark classes `final` where possible.
- Use `Optional` for return types that may be absent. Never use `null` to signal
  "not found".
- Validate inputs with Bean Validation annotations (`@NotNull`, `@Size`, `@Valid`).
- Write tests first or alongside the implementation, never as an afterthought.
- Keep methods short (< 20 lines). Extract named methods for readability.
- Use `try-with-resources` for all closeable resources.

### Don't
- Use field injection (`@Autowired` on fields). Always use constructor injection.
- Expose JPA entities in API responses. Map to DTOs.
- Catch `Exception` or `Throwable` broadly. Catch specific exception types.
- Use `System.out.println`. Use the SLF4J logger.
- Suppress warnings without a justifying comment.
- Use raw types (`List` instead of `List<Order>`).
- Put business logic in controllers or repositories.

---

## Common Pitfalls

1. **N+1 queries** -- Lazy-loaded JPA relationships trigger a query per item.
   Use `@EntityGraph` or `JOIN FETCH` in JPQL to batch-load associations.
2. **Missing `@Transactional` boundaries** -- Service methods that modify
   multiple entities without `@Transactional` risk partial writes. Annotate
   at the service layer, not the repository layer.
3. **Blocking virtual threads** -- `synchronized` blocks and `ReentrantLock`
   pin virtual threads to carrier threads. Use `java.util.concurrent.locks.Lock`
   with `tryLock()` or redesign for non-blocking.
4. **Configuration drift** -- Hardcoded values instead of externalized config.
   Use `@ConfigurationProperties` with validation for all tunable parameters.
5. **Ignoring `equals`/`hashCode` on entities** -- JPA entities used in `Set`
   or `Map` without proper `equals`/`hashCode` cause subtle bugs. Implement
   based on business key, not database ID.
6. **Over-injecting** -- A class with 8+ constructor parameters signals too many
   responsibilities. Split the class.

---

## Checklist

- [ ] Java 21 LTS targeted in `build.gradle.kts` / `pom.xml`.
- [ ] `google-java-format` applied via Spotless; CI rejects unformatted code.
- [ ] Error Prone enabled; no new warnings introduced.
- [ ] All DTOs are Java `record` types; no JPA entities in API responses.
- [ ] Constructor injection only; no `@Autowired` on fields.
- [ ] SLF4J parameterized logging; no string concatenation in log calls.
- [ ] Bean Validation annotations on all request DTOs (`@Valid` in controller).
- [ ] `@ControllerAdvice` maps exceptions to RFC 7807 Problem Details.
- [ ] `@Transactional` on service methods that modify data.
- [ ] No secrets in source code, logs, or committed config files.
- [ ] `.editorconfig` committed and consistent across the team.
