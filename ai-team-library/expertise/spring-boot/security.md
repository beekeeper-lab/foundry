# Spring Boot Security

Spring Security 6 conventions for Boot 3.x services. Cross-cutting rules (no
secrets in code, validate at boundaries) come from the shared rules and the
`java` pack; this file covers the Spring Security specifics.

---

## 1. Baseline: Lambda DSL, No Deprecated Idioms

Spring Security 6 removed `WebSecurityConfigurerAdapter` and the chained
`and()` style. Configuration is a `SecurityFilterChain` bean using the lambda
DSL — anything else in new code is a review reject.

```java
@Configuration
@EnableWebSecurity
class SecurityConfig {

    @Bean
    SecurityFilterChain apiSecurity(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(CsrfConfigurer::disable);   // stateless token API only — see §3
        return http.build();
    }
}
```

**Rules:**
- Deny by default: end every rule chain with `.anyRequest().authenticated()`
  (or `.denyAll()` for internal-only chains). Never leave a chain that falls
  through to permit.
- Order matters: `requestMatchers` are evaluated top-down — most specific
  first. Multiple `SecurityFilterChain` beans need explicit `@Order` and a
  `securityMatcher` each.
- `permitAll()` entries are an auditable allowlist: health probes, docs if
  public, nothing else without review.

---

## 2. OAuth2 Resource Server

Default posture for service APIs: stateless JWT validation via
`spring-boot-starter-oauth2-resource-server`.

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://idp.example.com/realms/app
```

- `issuer-uri` gives discovery-based key rotation; do not pin `jwk-set-uri`
  unless the IdP lacks discovery.
- Validate audience explicitly — issuer alone accepts any token that IdP
  minted for any service. Add an audience validator via a
  `JwtDecoder`/`JwtAuthenticationConverter` customization.
- Map claims to authorities in one `JwtAuthenticationConverter` bean; do not
  parse claims ad hoc in controllers. Controllers receive identity via
  `@AuthenticationPrincipal Jwt jwt` or a mapped principal type.
- The service validates tokens; it does not do login flows. Interactive login
  (`oauth2Login`) belongs to the frontend/BFF, not the resource server.
- Opaque tokens (introspection) only when the IdP cannot issue JWTs — it adds
  a network call per request; record the choice in an ADR.

---

## 3. Sessions and CSRF

- Token-authenticated APIs are `STATELESS` and may disable CSRF — the two go
  together. If any endpoint uses cookie-based sessions, CSRF protection stays
  on for those endpoints; do not disable it globally "because it broke a
  test".
- Browser-facing apps set the standard response-header baseline (Spring
  Security's defaults are good: keep `X-Content-Type-Options`, frame options,
  HSTS behind TLS). CORS is configured centrally via a
  `CorsConfigurationSource` bean with an explicit origin allowlist — never
  `*` with credentials.

---

## 4. Method Security

URL rules gate the perimeter; method security enforces domain-level rules
where the data lives.

```java
@Configuration
@EnableMethodSecurity   // prePostEnabled = true by default
class MethodSecurityConfig {}

@Service
class OrderService {
    @PreAuthorize("hasRole('ADMIN') or #ownerId == authentication.name")
    OrderDetails find(String ownerId, String orderId) { ... }
}
```

- Use `@PreAuthorize`/`@PostAuthorize`; the legacy `@Secured` and JSR-250
  annotations are less expressive — pick one style and it is `@PreAuthorize`.
- Annotate the service layer, not controllers: other entry points (listeners,
  schedulers) then get the same enforcement.
- Method security uses the same proxy mechanism as `@Transactional` — the
  self-invocation pitfall from `conventions.md` applies: internal `this.`
  calls bypass the check.
- Keep SpEL expressions short; complex authorization logic goes into a named
  bean (`@PreAuthorize("@orderAuth.canView(#orderId)")`) that can be unit
  tested.

---

## 5. Secrets and Testing Security

- Secrets arrive via environment variables or a secret manager integration —
  never in `application.yml`, never in the image. `.env`-style files are
  local-dev only and gitignored.
- Test the security config like production code:
  - `@WebMvcTest` + `@WithMockUser` (or `SecurityMockMvcRequestPostProcessors.jwt()`
    for resource servers) to pin per-endpoint rules: anonymous → 401,
    wrong role → 403, correct role → 2xx.
  - One test asserts the unauthenticated status for every new endpoint —
    the cheapest regression guard against an accidental `permitAll`.
  - Method-security rules get unit tests through the proxied bean, including
    the ownership branch of the SpEL expression.

---

## Checklist

- [ ] Single-source `SecurityFilterChain` beans with lambda DSL; no deprecated adapter code.
- [ ] Deny by default; `permitAll()` list is minimal and reviewed.
- [ ] JWT resource server with `issuer-uri` and an explicit audience validator.
- [ ] Claims-to-authorities mapping centralized in one converter bean.
- [ ] Stateless sessions + CSRF disabled only together, only for token APIs.
- [ ] CORS via central config with explicit origins; no wildcard with credentials.
- [ ] `@EnableMethodSecurity` with `@PreAuthorize` at the service layer; complex rules in testable beans.
- [ ] No secrets in config files or images; env/secret-manager only.
- [ ] Security tests pin 401/403/2xx per endpoint and method-security branches.
