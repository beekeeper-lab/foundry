# Task 4: Author the `spring-boot` expertise pack: Spring Boot 3.x (Java 21 era): project layout, configuration, dependency injection, data/JPA discipline, testing (slices vs @SpringBootTest), actuator/observability.

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Dependencies** | — |
| **Status** | Done |

## Objective

Author the `spring-boot` expertise pack: Spring Boot 3.x (Java 21 era): project layout, configuration, dependency injection, data/JPA discipline, testing (slices vs @SpringBootTest), actuator/observability.

## Inputs

- ai-team-library/expertise/python/conventions.md — canonical pack schema reference
- ai-team-library/README.md — pack authoring contract (frontmatter, SPEC-019)
- ai-team-library/expertise/llm-applications/conventions.md — recent example of an authored (not distilled) pack

## Acceptance Criteria

- [ ] (file:ai-team-library/expertise/spring-boot/conventions.md) Entry file exists with frontmatter
- [ ] (file-contains:ai-team-library/expertise/spring-boot/conventions.md::## Defaults) Canonical schema followed
- [ ] 2-4 sibling deep-dive files authored

## Comprehension Note

Followed the canonical pack schema from `expertise/python/conventions.md` (frontmatter → `# <Name> Conventions` → `## Category` → `## Defaults` table → numbered sections → Do/Don't → Common Pitfalls → Checklist). Composed with `expertise/java/conventions.md`: generic Java guidance (formatting, naming, SLF4J logging, records-for-DTOs, entity-exposure rules) is referenced, not duplicated; this pack covers only Spring-Boot-specific concerns. Siblings (`testing.md`, `observability.md`, `security.md`) carry no frontmatter, matching the sibling-file convention. Grounded in Boot 3.4-era practice with conservative version claims (`@MockitoBean` 3.4+, `@ServiceConnection` 3.1+, `JdbcClient` 3.2+).

## Telemetry

| Field | Value |
|-------|-------|
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
