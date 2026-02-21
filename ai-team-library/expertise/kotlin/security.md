# Kotlin Security

Security practices for Kotlin applications, covering input validation,
authentication, cryptography, dependency management, and common vulnerability
prevention for both server-side (Spring Boot) and Android platforms.

---

## Defaults

| Concern               | Default Choice                           | Override Requires |
|-----------------------|------------------------------------------|-------------------|
| Input Validation      | Bean Validation (`@Valid`, `@NotNull`)   | ADR               |
| Auth Framework        | Spring Security + JWT                    | ADR               |
| TLS                   | TLS 1.2+ enforced                        | Never             |
| Password Hashing      | BCrypt (Spring Security)                 | ADR               |
| Secrets Management    | Environment variables / Vault            | ADR               |
| Dependency Scanning   | OWASP Dependency-Check / Snyk            | Never             |
| SAST                  | detekt security rules + SpotBugs         | ADR               |
| SQL                   | Parameterized queries (Spring Data / JDBI)| Never            |
| Android Secure Storage| EncryptedSharedPreferences / Keystore    | Never             |

### Alternatives

| Primary               | Alternative            | When                               |
|-----------------------|------------------------|------------------------------------|
| Spring Security       | Ktor Authentication    | Using Ktor framework               |
| BCrypt                | Argon2id               | Higher security requirements       |
| OWASP Dep-Check       | Snyk / Trivy           | Container scanning, CI integration |
| Environment vars      | HashiCorp Vault        | Dynamic secrets, rotation          |
| EncryptedSharedPrefs  | Android Keystore       | Cryptographic key material         |

---

## Input Validation

Validate at the API boundary. Never trust client data.

```kotlin
data class CreateUserRequest(
    @field:NotBlank
    @field:Email
    @field:Size(max = 254)
    val email: String,

    @field:NotBlank
    @field:Size(min = 1, max = 200)
    val name: String,

    @field:NotNull
    @field:Pattern(regexp = "^(admin|user|viewer)$")
    val role: String,
)

@RestController
class UserController(private val service: UserService) {
    @PostMapping("/users")
    suspend fun create(@Valid @RequestBody req: CreateUserRequest): ResponseEntity<User> {
        val user = service.create(req)
        return ResponseEntity.status(HttpStatus.CREATED).body(user)
    }
}

// Global exception handler for validation errors
@ControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(ex: MethodArgumentNotValidException): ResponseEntity<ProblemDetail> {
        val detail = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST,
            ex.bindingResult.fieldErrors.joinToString("; ") { "${it.field}: ${it.defaultMessage}" }
        )
        return ResponseEntity.badRequest().body(detail)
    }
}
```

**Rules:**
- Validate all request fields at the controller layer with Bean Validation
  annotations before passing to services.
- Limit string lengths on every field. Unbounded strings are a DoS vector.
- Validate enum values against an allowlist using `@Pattern`, not a denylist.
- Use Kotlin's `require` / `check` for domain-level validation in services.
- Configure Jackson to reject unknown properties
  (`DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES`).

---

## Authentication and Authorization

```kotlin
@Configuration
@EnableWebSecurity
class SecurityConfig {
    @Bean
    fun securityFilterChain(http: HttpSecurity): SecurityFilterChain = http
        .csrf { it.disable() } // Disable for stateless APIs
        .sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }
        .authorizeHttpRequests {
            it.requestMatchers("/actuator/health").permitAll()
            it.requestMatchers("/api/admin/**").hasRole("ADMIN")
            it.anyRequest().authenticated()
        }
        .oauth2ResourceServer { it.jwt { } }
        .build()

    @Bean
    fun jwtDecoder(): JwtDecoder = NimbusJwtDecoder
        .withJwkSetUri("https://auth.example.com/.well-known/jwks.json")
        .build()
        .also {
            it.setJwtValidator(
                DelegatingOAuth2TokenValidator(
                    JwtTimestampValidator(),
                    JwtIssuerValidator("https://auth.example.com"),
                    // Custom audience validator
                    JwtClaimValidator<List<String>>("aud") { aud ->
                        aud.contains("api.example.com")
                    }
                )
            )
        }
}
```

**Rules:**
- Validate JWT `iss`, `aud`, `exp`, and `alg` claims. Never skip validation.
- Default-deny: all endpoints require authentication unless explicitly public.
- Use Spring Security's method-level security (`@PreAuthorize`) for
  fine-grained authorization.
- Return generic error messages to clients. Never expose stack traces, JWT
  details, or internal errors.
- BCrypt cost factor >= 12 for password hashing.
- Android: use BiometricPrompt for local authentication. Never store passwords
  in SharedPreferences.

---

## Cryptography

```kotlin
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

// Generate cryptographically secure random tokens
fun generateToken(byteLength: Int = 32): String {
    val bytes = ByteArray(byteLength)
    SecureRandom().nextBytes(bytes)
    return bytes.joinToString("") { "%02x".format(it) }
}

// Password hashing with Spring Security BCrypt
val encoder = BCryptPasswordEncoder(12) // Cost factor 12

fun hashPassword(password: String): String = encoder.encode(password)

fun checkPassword(rawPassword: String, hashedPassword: String): Boolean =
    encoder.matches(rawPassword, hashedPassword)
```

**Rules:**
- Always use `SecureRandom` for random values, never `java.util.Random` or
  `kotlin.random.Random`.
- Use BCrypt or Argon2id for password hashing. Never MD5, SHA-1, or SHA-256
  for passwords.
- Use SHA-256 for integrity checks (file hashes, checksums), not for passwords.
- Enforce TLS 1.2+ for all network communication.
- Never implement custom cryptographic algorithms.
- Android: use `AndroidKeyStore` for storing cryptographic keys. Never
  hardcode keys in source.

---

## SQL Injection Prevention

```kotlin
// Spring Data — parameterized queries by default
interface OrderRepository : JpaRepository<Order, String> {
    fun findByCustomerId(customerId: String): List<Order>

    @Query("SELECT o FROM Order o WHERE o.status = :status AND o.total > :minTotal")
    fun findByStatusAndMinTotal(status: String, minTotal: BigDecimal): List<Order>
}

// NEVER concatenate user input into queries
// BAD: "SELECT * FROM orders WHERE id = '$id'"
// BAD: @Query("SELECT o FROM Order o WHERE o.id = '${id}'")
```

**Rules:**
- Use Spring Data repository methods or `@Query` with named parameters.
- Never use string interpolation or concatenation to build SQL/JPQL queries.
- For dynamic queries, use `Specification` or `Criteria API` — they use
  parameterized bindings.
- Validate and sanitize identifiers (table/column names) if they must be
  dynamic.
- Use `@Param` annotations for clarity in native queries.

---

## Android-Specific Security

```kotlin
// Encrypted SharedPreferences for sensitive local data
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val securePrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
)

// Certificate pinning with OkHttp
val client = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .build()
    )
    .build()
```

**Rules:**
- Use `EncryptedSharedPreferences` for sensitive data at rest. Never store
  tokens or secrets in plain `SharedPreferences`.
- Use certificate pinning for API communication to prevent MITM attacks.
- Set `android:exported="false"` on components not intended for external use.
- Set `android:allowBackup="false"` to prevent sensitive data in backups.
- Use `ProGuard` / `R8` for code obfuscation in release builds.
- Never log sensitive data in production builds. Use `BuildConfig.DEBUG` guards.

---

## Do / Don't

### Do
- Run OWASP Dependency-Check or Snyk in CI on every push; block deployment on
  known CVEs.
- Validate all request fields with Bean Validation annotations.
- Set timeouts on all HTTP clients (`connectTimeout`, `readTimeout`).
- Use Spring Security method-level authorization (`@PreAuthorize`).
- Pin dependency versions. Review dependency diffs in PRs.
- Set `Content-Type` and security headers (`X-Content-Type-Options`,
  `X-Frame-Options`, `Strict-Transport-Security`) on all responses.
- Use `SecureRandom` for all security-sensitive random values.
- Android: use `EncryptedSharedPreferences` and `AndroidKeyStore`.

### Don't
- Log secrets, tokens, passwords, or full PII.
- Use MD5 or SHA-1 for any security purpose.
- Disable TLS verification in production.
- Use string interpolation to build SQL queries with user input.
- Trust `X-Forwarded-For` without configuring a trusted proxy list.
- Store passwords in plaintext or reversible encryption.
- Android: use plain `SharedPreferences` for tokens or secrets.
- Android: set `android:exported="true"` without intent filters.
- Hardcode API keys or secrets in source code or `BuildConfig`.

---

## Common Pitfalls

1. **SQL injection via string templates** -- Kotlin's string templates
   (`"SELECT * WHERE id = '$id'"`) make SQL injection easy to introduce
   accidentally. Always use parameterized queries or Spring Data methods.
2. **Missing HTTP timeouts** -- Default `OkHttpClient` and `RestClient` with
   zero timeouts allow slowloris attacks and resource exhaustion. Always
   configure `connectTimeout`, `readTimeout`, and `writeTimeout`.
3. **Weak JWT validation** -- Not validating `iss`, `aud`, or `alg` allows
   token forgery. Use Spring Security's `JwtDecoder` with explicit validators.
4. **Using `java.util.Random` for security** -- `java.util.Random` and
   `kotlin.random.Random` are deterministic. Use `SecureRandom` for tokens,
   session IDs, and all security-sensitive values.
5. **Android secrets in source** -- API keys in `BuildConfig`, `strings.xml`,
   or hardcoded constants are extractable from APKs. Use server-side proxying
   or Android Keystore for sensitive credentials.
6. **Exposing actuator endpoints** -- Spring Boot Actuator endpoints
   (`/env`, `/configprops`) leak configuration and secrets. Restrict all
   actuator endpoints except `/health` behind authentication.
7. **Coroutine context loss** -- Security context (e.g., `SecurityContextHolder`)
   is thread-local and lost when switching coroutine dispatchers. Use
   `SecurityContextHolder.setStrategyName(MODE_INHERITABLETHREADLOCAL)` or
   propagate context explicitly with `ReactorContext`.

---

## Checklist

- [ ] All request DTOs validated with Bean Validation annotations (`@Valid`).
- [ ] All string fields have maximum length constraints.
- [ ] SQL queries use parameterized bindings (no string interpolation).
- [ ] JWT validation enforces `alg`, `iss`, `aud`, and `exp` claims.
- [ ] Passwords hashed with BCrypt (cost >= 12) or Argon2id.
- [ ] `SecureRandom` used for all security-sensitive random values.
- [ ] HTTP client and server timeouts configured.
- [ ] OWASP Dependency-Check or Snyk runs in CI; known CVEs block deployment.
- [ ] TLS 1.2+ enforced; no insecure TLS verification in production.
- [ ] No secrets in source code, logs, or committed config files.
- [ ] Security headers set on all HTTP responses.
- [ ] Spring Boot Actuator endpoints restricted behind authentication.
- [ ] Android: `EncryptedSharedPreferences` for sensitive data at rest.
- [ ] Android: certificate pinning configured for API communication.
- [ ] Android: `android:exported="false"` on internal components.
