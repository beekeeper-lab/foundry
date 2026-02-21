# Java Security

Security practices for Java applications with Spring Boot, covering input
validation, authentication, dependency management, and common vulnerability
prevention.

---

## Defaults

| Concern               | Default Choice                          | Override Requires |
|-----------------------|-----------------------------------------|-------------------|
| Auth Framework        | Spring Security                         | ADR               |
| Input Validation      | Bean Validation (`jakarta.validation`)  | Never             |
| Password Hashing      | BCrypt (`BCryptPasswordEncoder`)        | ADR               |
| JWT                   | `spring-security-oauth2-resource-server` | ADR              |
| Secrets Management    | Environment variables / Vault           | ADR               |
| Dependency Scanning   | OWASP Dependency-Check (Gradle/Maven)   | Never             |
| SAST                  | SpotBugs + Find Security Bugs           | ADR               |
| HTTPS                 | Enforced in all environments            | Never             |

### Alternatives

| Primary                 | Alternative            | Notes                       |
|-------------------------|------------------------|-----------------------------|
| Spring Security         | Apache Shiro           | Non-Spring projects only    |
| BCrypt                  | Argon2 / SCrypt        | Higher security, more CPU   |
| OWASP Dependency-Check  | Snyk / Trivy           | Deeper analysis, paid tiers |
| Find Security Bugs      | Semgrep                | More rules, CI-friendly     |

---

## Input Validation

Validate at the API boundary. Never trust client data.

```java
// DTO with Bean Validation constraints
public record CreateUserRequest(
    @NotBlank @Email @Size(max = 254)
    String email,

    @NotBlank @Size(min = 1, max = 200)
    String name,

    @NotNull
    Role role
) {}

// Controller applies @Valid
@RestController
@RequestMapping("/v1/users")
public class UserController {

    private final UserService userService;

    UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse create(@Valid @RequestBody CreateUserRequest request) {
        return userService.create(request);
    }
}
```

**Rules:**
- Every request DTO carries Bean Validation annotations.
- Controllers annotate `@RequestBody` with `@Valid`. Validation errors are
  mapped to 400 responses by `@ControllerAdvice`.
- Set `@Size(max = ...)` on every string field. Unbounded strings are a DoS
  vector.
- Use `@Pattern` sparingly. Prefer semantic annotations (`@Email`, `@URL`).

---

## Authentication and Authorization

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable()) // Stateless API, JWT-only
            .sessionManagement(sm -> sm.sessionCreationPolicy(STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

**Rules:**
- Disable CSRF for stateless JWT APIs. Enable it for session-based apps.
- Use `STATELESS` session policy for APIs; never store auth state server-side.
- Default-deny: `anyRequest().authenticated()`. Whitelist only public endpoints.
- Use method-level security (`@PreAuthorize`) for fine-grained access control.
- BCrypt cost factor >= 12. Adjust based on acceptable login latency.

---

## Do / Don't

### Do
- Run OWASP Dependency-Check in CI; block deployment on Critical/High CVEs.
- Use parameterized queries (Spring Data, `JdbcTemplate` with `?`). Never
  concatenate SQL strings.
- Return generic error messages to clients (`"Unauthorized"`), not stack traces.
- Externalize secrets via environment variables or HashiCorp Vault.
- Enable HTTPS and set `Strict-Transport-Security` header.
- Review dependency updates in every PR (check `gradle.lockfile` / `pom.xml` diffs).
- Use `@PreAuthorize` for role/permission checks, not manual `if` blocks.

### Don't
- Log secrets, tokens, passwords, or full PII.
- Use `MD5` or `SHA-1` for password hashing or integrity checks.
- Disable CSRF protection on session-based applications.
- Use `@PermitAll` as a shortcut when you are unsure about access rules.
- Store passwords in plaintext or reversible encryption.
- Expose Spring Actuator endpoints publicly (except `/health`).
- Trust `X-Forwarded-For` without configuring a trusted proxy list.

---

## Common Pitfalls

1. **SQL injection via string concatenation** -- Using `"SELECT * FROM users
   WHERE name = '" + name + "'"` is exploitable. Always use parameterized
   queries or Spring Data derived methods.
2. **Mass assignment** -- Binding request JSON directly to JPA entities lets
   attackers set fields like `role` or `isAdmin`. Use DTOs and map explicitly.
3. **Exposing Actuator endpoints** -- `/actuator/env`, `/actuator/beans`, and
   `/actuator/heapdump` leak internals. Secure all except `/health` and
   `/info`.
4. **Insecure deserialization** -- Using `ObjectInputStream` on untrusted data
   allows remote code execution. Never deserialize untrusted Java objects. Use
   JSON with Jackson.
5. **Missing CORS configuration** -- Spring Security defaults to no CORS, which
   blocks legitimate frontends. Configure an explicit origin allowlist.
6. **Weak JWT validation** -- Not verifying `iss`, `aud`, and `exp` claims
   allows token reuse across services. Configure all claims in the resource
   server.
7. **Dependency confusion** -- Internal packages with the same name as public
   Maven Central packages. Use a unique group ID and configure repository
   priority.

---

## Checklist

- [ ] Spring Security configured with default-deny (`anyRequest().authenticated()`).
- [ ] CSRF disabled only for stateless JWT APIs; enabled for session-based apps.
- [ ] All request DTOs validated with `@Valid` + Bean Validation annotations.
- [ ] All string fields have `@Size(max = ...)` constraints.
- [ ] SQL queries use parameterized bindings (no string concatenation).
- [ ] Passwords hashed with BCrypt (cost >= 12) or Argon2.
- [ ] JWT `iss`, `aud`, and `exp` claims validated.
- [ ] OWASP Dependency-Check runs in CI; Critical/High CVEs block deployment.
- [ ] Spring Actuator endpoints secured (only `/health` public).
- [ ] No secrets in source code, logs, or committed config files.
- [ ] CORS configured with explicit origin allowlist.
- [ ] HTTPS enforced; `Strict-Transport-Security` header set.
