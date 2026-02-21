# Go Security

Security practices for Go applications, covering input validation,
authentication, cryptography, dependency management, and common vulnerability
prevention.

---

## Defaults

| Concern               | Default Choice                          | Override Requires |
|-----------------------|-----------------------------------------|-------------------|
| Input Validation      | Manual validation + `validator`         | ADR               |
| Auth Framework        | Middleware-based JWT validation          | ADR               |
| TLS                   | `crypto/tls` (stdlib), TLS 1.2+        | Never             |
| Password Hashing      | `bcrypt` (`golang.org/x/crypto/bcrypt`) | ADR               |
| Secrets Management    | Environment variables / Vault           | ADR               |
| Dependency Scanning   | `govulncheck`                           | Never             |
| SAST                  | `golangci-lint` security linters        | ADR               |
| HTTPS                 | Enforced in all environments            | Never             |
| SQL                   | Parameterized queries (`database/sql`)  | Never             |

### Alternatives

| Primary              | Alternative            | When                               |
|----------------------|------------------------|------------------------------------|
| `bcrypt`             | `argon2id`             | Higher security, password storage  |
| `govulncheck`       | Snyk / Trivy           | Deeper analysis, container scanning|
| Manual validation    | `ozzo-validation`      | Complex validation chains          |
| Environment vars     | HashiCorp Vault        | Dynamic secrets, rotation          |

---

## Input Validation

Validate at the API boundary. Never trust client data.

```go
type CreateUserRequest struct {
    Email string `json:"email" validate:"required,email,max=254"`
    Name  string `json:"name"  validate:"required,min=1,max=200"`
    Role  string `json:"role"  validate:"required,oneof=admin user viewer"`
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid JSON", http.StatusBadRequest)
        return
    }

    if err := h.validate.Struct(req); err != nil {
        http.Error(w, "validation failed", http.StatusBadRequest)
        return
    }

    // Proceed with validated input...
}
```

**Rules:**
- Validate all request fields at the handler layer before passing to services.
- Limit string lengths on every field. Unbounded strings are a DoS vector.
- Use `io.LimitReader` when reading request bodies to prevent oversized payloads:
  `io.LimitReader(r.Body, 1<<20)` (1 MB).
- Validate enum values against an allowlist, not a denylist.
- Never use `reflect` or dynamic type assertions on untrusted input.

---

## Authentication and Authorization

```go
// JWT middleware using a shared validation function.
func AuthMiddleware(keyFunc jwt.Keyfunc) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            tokenStr := extractBearerToken(r)
            if tokenStr == "" {
                http.Error(w, "unauthorized", http.StatusUnauthorized)
                return
            }

            token, err := jwt.Parse(tokenStr, keyFunc,
                jwt.WithValidMethods([]string{"RS256"}),
                jwt.WithIssuer("https://auth.example.com"),
                jwt.WithAudience("api.example.com"),
            )
            if err != nil || !token.Valid {
                http.Error(w, "unauthorized", http.StatusUnauthorized)
                return
            }

            ctx := context.WithValue(r.Context(), userClaimsKey, token.Claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func extractBearerToken(r *http.Request) string {
    auth := r.Header.Get("Authorization")
    if !strings.HasPrefix(auth, "Bearer ") {
        return ""
    }
    return strings.TrimPrefix(auth, "Bearer ")
}
```

**Rules:**
- Validate JWT `iss`, `aud`, `exp`, and `alg` claims. Never skip validation.
- Restrict `alg` to an explicit allowlist (`RS256`). Never accept `none`.
- Default-deny: all endpoints require authentication unless explicitly public.
- Use context values for passing claims downstream, not global state.
- Return generic error messages (`"unauthorized"`) to clients, never token
  details or stack traces.
- BCrypt cost factor >= 12 for password hashing.

---

## Cryptography

```go
import (
    "crypto/rand"
    "crypto/sha256"
    "encoding/hex"
    "golang.org/x/crypto/bcrypt"
)

// Generate cryptographically secure random tokens.
func generateToken(n int) (string, error) {
    b := make([]byte, n)
    if _, err := rand.Read(b); err != nil {
        return "", fmt.Errorf("generate token: %w", err)
    }
    return hex.EncodeToString(b), nil
}

// Hash passwords with bcrypt.
func hashPassword(password string) (string, error) {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    if err != nil {
        return "", fmt.Errorf("hash password: %w", err)
    }
    return string(hash), nil
}

func checkPassword(hash, password string) bool {
    return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password)) == nil
}
```

**Rules:**
- Always use `crypto/rand` for random values, never `math/rand`.
- Use `bcrypt` or `argon2id` for password hashing. Never `MD5`, `SHA-1`, or
  `SHA-256` for passwords.
- Use `SHA-256` for integrity checks (file hashes, checksums), not for
  passwords.
- Use `crypto/tls` with `MinVersion: tls.VersionTLS12` for TLS configuration.
- Never implement custom cryptographic algorithms.

---

## SQL Injection Prevention

```go
// Always use parameterized queries.
func (r *OrderRepo) FindByID(ctx context.Context, id string) (Order, error) {
    var order Order
    err := r.db.QueryRowContext(ctx,
        "SELECT id, amount, status FROM orders WHERE id = $1", id,
    ).Scan(&order.ID, &order.Amount, &order.Status)
    if errors.Is(err, sql.ErrNoRows) {
        return Order{}, ErrNotFound
    }
    return order, err
}

// NEVER concatenate user input into SQL strings.
// BAD: fmt.Sprintf("SELECT * FROM orders WHERE id = '%s'", id)
```

**Rules:**
- Use `$1`, `$2` (Postgres) or `?` (MySQL) parameterized placeholders.
- Never use `fmt.Sprintf` to build SQL queries with user input.
- Use an ORM or query builder (`sqlc`, `squirrel`) that enforces parameterization.
- Validate and sanitize identifiers (table/column names) if they must be
  dynamic -- they cannot be parameterized.

---

## Do / Don't

### Do
- Run `govulncheck` in CI on every push; block deployment on known CVEs.
- Use `io.LimitReader` on all request body reads.
- Set timeouts on all HTTP clients and servers (`ReadTimeout`, `WriteTimeout`,
  `IdleTimeout`).
- Use `context.Context` for request-scoped cancellation and timeouts.
- Pin dependency versions in `go.sum`. Review `go.sum` diffs in PRs.
- Set `Content-Type` and security headers (`X-Content-Type-Options`,
  `X-Frame-Options`, `Strict-Transport-Security`) on all responses.
- Use `crypto/rand` for all random values in security contexts.

### Don't
- Log secrets, tokens, passwords, or full PII.
- Use `MD5` or `SHA-1` for any security purpose.
- Disable TLS verification (`InsecureSkipVerify: true`) in production.
- Accept `alg: none` in JWT validation.
- Use `fmt.Sprintf` to build SQL queries with user input.
- Trust `X-Forwarded-For` without configuring a trusted proxy list.
- Store passwords in plaintext or reversible encryption.
- Use `os.Getenv` for secrets without validating they are non-empty at startup.

---

## Common Pitfalls

1. **SQL injection via string formatting** -- Using `fmt.Sprintf` to build
   queries with user input is exploitable. Always use parameterized queries
   (`$1`, `?`) or query builders like `sqlc`.
2. **Missing HTTP timeouts** -- `http.Server{}` and `http.Client{}` with zero
   timeouts allow slowloris attacks and resource exhaustion. Always set
   `ReadTimeout`, `WriteTimeout`, and `IdleTimeout`.
3. **Weak JWT validation** -- Not restricting `alg` to an allowlist lets
   attackers forge tokens with `alg: none`. Always use `jwt.WithValidMethods`.
4. **Using `math/rand` for security** -- `math/rand` is deterministic and
   predictable. Use `crypto/rand` for tokens, session IDs, and all
   security-sensitive random values.
5. **Unbounded request bodies** -- Without `io.LimitReader` or
   `http.MaxBytesReader`, attackers can send multi-GB payloads to exhaust
   memory.
6. **Exposing debug endpoints** -- `net/http/pprof` registers handlers on
   `DefaultServeMux` via `init()`. Use a separate mux for debug endpoints and
   bind it to a non-public port.
7. **Dependency confusion** -- Go module paths that don't match the actual
   repository URL. Verify `go.sum` integrity and use `GONOSUMCHECK` only for
   private modules with `GONOSUMDB` and `GOPRIVATE`.

---

## Checklist

- [ ] All request bodies read via `io.LimitReader` or `http.MaxBytesReader`.
- [ ] All string fields validated with maximum length constraints.
- [ ] SQL queries use parameterized bindings (no `fmt.Sprintf` with user input).
- [ ] JWT validation enforces `alg`, `iss`, `aud`, and `exp` claims.
- [ ] Passwords hashed with `bcrypt` (cost >= 12) or `argon2id`.
- [ ] `crypto/rand` used for all security-sensitive random values.
- [ ] HTTP server and client timeouts configured (`ReadTimeout`, `WriteTimeout`).
- [ ] `govulncheck` runs in CI; known CVEs block deployment.
- [ ] TLS 1.2+ enforced; `InsecureSkipVerify` is `false` in production.
- [ ] No secrets in source code, logs, or committed config files.
- [ ] Security headers set on all HTTP responses.
- [ ] `net/http/pprof` not exposed on public-facing ports.
