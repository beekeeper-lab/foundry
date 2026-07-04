# FastAPI Security

Auth, CORS, and abuse protection for FastAPI services. The organizing
principle: **security is enforced by dependencies**, so it composes with
routing, shows up in OpenAPI, and fails closed when a route forgets it.

## 1. Auth Is a Dependency

- Authentication and authorization live in dependency functions, not in
  middleware path-matching and not inline in route bodies.
- Middleware-based auth keyed on path prefixes fails **open**: a new
  router mounted outside the guarded prefix ships unauthenticated.
  Dependencies fail **closed**: a route without `CurrentUser` in its
  signature visibly has no auth, and reviewers can see it.
- Layer the dependencies:

  ```python
  bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

  async def get_current_user(token: Annotated[str, Depends(bearer)]) -> User:
      payload = decode_token(token)          # raises 401 on any failure
      return await load_user(payload["sub"]) # raises 401 if missing/disabled

  CurrentUser = Annotated[User, Depends(get_current_user)]

  def require_role(role: str):
      def check(user: CurrentUser) -> User:
          if role not in user.roles:
              raise HTTPException(status_code=403, detail="Insufficient role")
          return user
      return check
  ```

- Apply auth to whole routers by default, opt routes *out* explicitly
  rather than opting in:

  ```python
  app.include_router(orders.router, dependencies=[Depends(get_current_user)])
  ```

  Public endpoints (health, docs, token issuance) live on a separate,
  explicitly unauthenticated router.
- 401 means "who are you?" (missing/invalid credentials, include
  `WWW-Authenticate: Bearer`); 403 means "you, specifically, may not"
  (authenticated but unauthorized). Don't blur them — clients and
  monitoring branch on the difference.

## 2. OAuth2 / JWT Patterns

- Use `OAuth2PasswordBearer` (or `HTTPBearer`) for token extraction so
  the scheme appears in OpenAPI and the docs UI can authenticate.
- JWT rules:
  - Sign with a `SecretStr` key from `Settings` (HS256) or a private key
    (RS256) when tokens are verified by other services. Never a key in
    source.
  - Always set and **verify** `exp`; keep access tokens short-lived
    (minutes to an hour) and use refresh tokens for longevity.
  - Pin the algorithm on decode (`algorithms=["HS256"]`) — never accept
    the header's claim of its own algorithm.
  - Put only identifiers and coarse claims (`sub`, `roles`, `exp`) in the
    token. No PII, no permissions snapshots that go stale.
  - Any decode failure → generic 401. Don't distinguish "expired" from
    "bad signature" in the response body beyond what clients need for
    refresh flows.
- Password handling: hash with `bcrypt`/`argon2` via `passlib` or the
  maintained equivalent; compare with the library's verify function,
  never string equality. Rate-limit the token endpoint (see §4).
- Service-to-service auth: static bearer/API keys compared with
  `secrets.compare_digest`, or mTLS at the ingress — not shared user
  JWTs.

## 3. CORS

- Add `CORSMiddleware` only when browsers on other origins call the API.
  Server-to-server traffic doesn't need it.
- Configuration comes from `Settings`, per environment:

  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins,   # explicit list, no "*"
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
      allow_headers=["Authorization", "Content-Type"],
  )
  ```

- `allow_origins=["*"]` with `allow_credentials=True` is invalid per the
  CORS spec and effectively disables the protection — Starlette will not
  send the credentials header in that combination, and code that "fixes"
  this by echoing the request origin has recreated `*` with credentials.
  List the origins.
- CORS is a browser courtesy, not authentication. Never treat an
  Origin check as an auth layer.

## 4. Rate Limiting & Abuse

- Prefer limiting at the edge (API gateway, nginx, cloud LB) — it's
  cheaper and protects the app before Python runs.
- In-app, `slowapi` (or an equivalent token-bucket keyed on client
  identity) covers per-route needs. Key on authenticated principal when
  available, client IP otherwise; remember IP is spoofable behind
  misconfigured proxies — configure trusted proxy headers deliberately.
- Always rate-limit: token/login endpoints (credential stuffing),
  password reset, signup, and anything that sends email/SMS.
- Return `429` with `Retry-After`. Log the principal/IP so abuse is
  attributable.
- Cap request body size at the ingress; don't rely on Pydantic to reject
  a 500 MB JSON body cheaply.

## 5. Headers, Docs, and Surface

- Behind a TLS-terminating proxy, run uvicorn with
  `--proxy-headers --forwarded-allow-ips=<proxy>` so `request.url` and
  client IPs are correct — but only trust headers from your own proxy.
- Security headers (HSTS, `X-Content-Type-Options`, CSP for any served
  HTML) belong at the reverse proxy; add a small middleware only when
  there is no proxy to own it.
- Decide docs exposure explicitly per environment: internal APIs
  commonly set `docs_url=None, redoc_url=None, openapi_url=None` in
  production, or put docs behind the auth dependency. Don't leave the
  default because nobody decided.
- Never let secrets reach responses or logs: `SecretStr` in settings,
  redaction in log processors, and no exception messages that embed
  connection strings (the default 500 handler already hides details —
  keep `debug=False` in production).

## Pitfalls

1. **Auth by path prefix in middleware.** New router, no auth, nobody
   notices. Use router-level dependencies; fail closed.
2. **Unpinned JWT algorithm on decode** — accepting `alg: none` or an
   attacker-chosen algorithm. Pass `algorithms=[...]` explicitly, always.
3. **`allow_origins=["*"]` plus credentials**, or echoing the Origin
   header to "make it work" — either way, any site can ride the user's
   session.
4. **Token endpoint without rate limiting** — free credential-stuffing
   oracle.
5. **403 where 401 belongs (and vice versa)** — breaks client refresh
   logic and muddies security monitoring.
6. **Trusting `X-Forwarded-For` from anywhere** — rate limits and audit
   logs keyed on an attacker-controlled header.
