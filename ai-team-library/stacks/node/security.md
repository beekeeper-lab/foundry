# Node.js Security

Security practices for Node.js applications covering input validation,
dependency hygiene, HTTP hardening, authentication, and secrets management.

---

## Defaults

| Concern               | Default Choice                   | Override Requires |
|-----------------------|----------------------------------|-------------------|
| Input Validation      | Zod (body), Typebox (route schema) | ADR             |
| HTTP Hardening        | `@fastify/helmet` / `helmet`     | Never             |
| Rate Limiting         | `@fastify/rate-limit`            | ADR               |
| Auth Tokens           | JWT (`RS256`) via `@fastify/jwt`  | ADR               |
| Secrets Storage       | Environment variables (validated) | ADR               |
| Dependency Auditing   | `npm audit` (CI-integrated)      | Never             |
| CORS                  | `@fastify/cors` with allowlist   | Never             |

### Alternatives

| Primary               | Alternative              | Notes                          |
|-----------------------|--------------------------|--------------------------------|
| `@fastify/helmet`     | `helmet` (Express)       | Same headers, different API    |
| `@fastify/rate-limit`  | `express-rate-limit`     | Express equivalent             |
| `@fastify/jwt`        | `jose` library           | Framework-agnostic JWT         |
| `npm audit`           | Snyk / Socket            | Deeper analysis, paid tiers    |

---

## Input Validation

Never trust client input. Validate at the boundary and work with typed,
validated data everywhere else.

```typescript
// Route-level validation (Fastify + Typebox)
import { Type, Static } from "@sinclair/typebox";

const CreateUserBody = Type.Object({
  email: Type.String({ format: "email", maxLength: 254 }),
  name: Type.String({ minLength: 1, maxLength: 200 }),
  role: Type.Union([Type.Literal("admin"), Type.Literal("member")]),
});
type CreateUserBody = Static<typeof CreateUserBody>;

app.post<{ Body: CreateUserBody }>("/users", {
  schema: { body: CreateUserBody },
  handler: async (request, reply) => {
    // request.body is validated and typed -- safe to use
    const user = await userService.create(request.body);
    reply.code(201).send(user);
  },
});
```

**Rules:**
- Validate on ingress, not in business logic.
- Set `maxLength` on every string field. Unbounded strings are a DoS vector.
- Use `format` constraints (`email`, `uri`, `uuid`) rather than raw regex.
- Reject unexpected fields: Typebox strips additional properties by default.

---

## HTTP Hardening

```typescript
// src/plugins/security.ts
import helmet from "@fastify/helmet";
import rateLimit from "@fastify/rate-limit";
import cors from "@fastify/cors";

export async function registerSecurity(app: FastifyInstance): Promise<void> {
  // Security headers (CSP, X-Frame-Options, etc.)
  await app.register(helmet, {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
      },
    },
  });

  // Rate limiting -- 100 requests per minute per IP
  await app.register(rateLimit, {
    max: 100,
    timeWindow: "1 minute",
    keyGenerator: (request) => request.ip,
  });

  // CORS -- explicit origin allowlist
  await app.register(cors, {
    origin: ["https://app.example.com"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  });
}
```

---

## Do / Don't

### Do
- Run `npm audit` in CI; block deployment on Critical and High findings.
- Set `sameSite: "strict"` and `httpOnly: true` on all cookies.
- Use parameterized queries / ORM bindings for all database access.
- Rotate secrets regularly; never hardcode them in source code.
- Return generic error messages to clients (`"Unauthorized"`), not internal details.
- Enforce HTTPS everywhere; set `Strict-Transport-Security` header.
- Pin dependency versions with `--save-exact` and review lockfile diffs in PRs.
- Apply the principle of least privilege to service accounts and API keys.

### Don't
- Log secrets, tokens, API keys, passwords, or full PII.
- Use `eval()`, `new Function()`, or `vm.runInNewContext()` with user input.
- Disable TLS certificate verification (`NODE_TLS_REJECT_UNAUTHORIZED=0`).
- Trust `X-Forwarded-For` without configuring a trusted proxy chain.
- Use `MD5` or `SHA1` for password hashing. Use `bcrypt` or `argon2`.
- Accept file uploads without size limits, type validation, and virus scanning.
- Store JWTs in `localStorage`. Use `httpOnly` cookies.
- Use wildcard CORS (`*`) in production.

---

## Common Pitfalls

1. **Prototype pollution** -- Deep-merge libraries and `JSON.parse` of
   untrusted data can inject `__proto__` properties. Use `Object.create(null)`
   for lookup maps and validate input shapes with Zod/Typebox.
2. **ReDoS (Regular Expression DoS)** -- Complex regexes with nested quantifiers
   can hang the event loop. Use `safe-regex` to lint custom patterns, or prefer
   schema `format` validators.
3. **Insecure JWT defaults** -- `HS256` with a weak secret is trivially
   forgeable. Use `RS256` with a rotated key pair. Always verify `iss` and `aud`
   claims.
4. **Missing rate limits on auth endpoints** -- Login and token-refresh endpoints
   without rate limiting invite credential stuffing. Apply stricter limits
   (e.g., 10/min) on auth routes.
5. **Dependency supply-chain attacks** -- Typosquatted packages, compromised
   maintainer accounts, and install scripts. Pin exact versions, audit lockfile
   diffs, and use `npm audit signatures`.
6. **Path traversal in file operations** -- User-controlled file paths without
   sanitization allow reading `/etc/passwd`. Use `path.resolve()` and verify
   the result stays within the expected root directory.

---

## Checklist

- [ ] `@fastify/helmet` (or `helmet`) registered with CSP configured.
- [ ] Rate limiting applied globally and with stricter limits on auth endpoints.
- [ ] CORS configured with an explicit origin allowlist (no `*` in production).
- [ ] All request inputs validated at the route schema level.
- [ ] All string fields have `maxLength` constraints.
- [ ] Database queries use parameterized bindings (no string concatenation).
- [ ] JWTs use `RS256`; `iss` and `aud` claims validated.
- [ ] Cookies set `httpOnly`, `secure`, `sameSite: "strict"`.
- [ ] `npm audit` runs in CI and blocks on Critical/High findings.
- [ ] No secrets in source code, logs, or error responses.
- [ ] File upload endpoints enforce size limits and content-type validation.
- [ ] Lockfile diffs reviewed in every PR for unexpected dependency changes.
