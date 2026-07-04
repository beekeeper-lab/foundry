---
id: fastapi
category: Frameworks
entry: true
last-reviewed: 2026-07
---

# FastAPI Conventions

## Category

Frameworks

Non-negotiable defaults for building HTTP APIs with FastAPI in the
Pydantic v2 era. These conventions target FastAPI 0.115+ and assume the
Python pack's baseline (uv, ruff, pytest, `src/` layout). Depth lives in
the sibling files: `testing.md`, `security.md`, `architecture.md`.

## Defaults

| Concern | Default |
|---------|---------|
| Python version | 3.11+ (floor; pin minor in `.python-version`) |
| FastAPI version | >= 0.115 (Annotated DI, Pydantic-model query/form params) |
| Pydantic | v2 only (`pydantic>=2`); `pydantic-settings` for config |
| Project layout | `src/` layout; routers / services / repositories split |
| App construction | App factory (`create_app()`) + `lifespan` context manager |
| Dependency injection | `Annotated[T, Depends(...)]` aliases in a `dependencies.py` module |
| Async posture | `async def` only with async libraries; plain `def` for blocking code |
| Settings | `BaseSettings` loaded once, injected via a dependency |
| Server | `uvicorn` (dev), `uvicorn` workers behind a process manager (prod) |
| Test client | `httpx.AsyncClient` + `ASGITransport`; `TestClient` for sync-only suites |
| Lint / format | `ruff` check + format (see python pack) |
| API docs | OpenAPI enabled in non-prod; every route has `response_model` + tags |

## 1. App Structure & Routers

- Use an **app factory**: `create_app() -> FastAPI` builds the app,
  registers routers, exception handlers, and middleware. No module-level
  `app = FastAPI()` with import-time side effects — factories make tests
  and multi-config deploys trivial.
- One `APIRouter` per resource (`routers/orders.py`, `routers/users.py`),
  each with a `prefix` and `tags` set at include time in the factory, not
  scattered per-route.
- Routes are thin: parse/validate via Pydantic, call a service function,
  translate domain results/errors to HTTP. No business logic in route
  bodies. See `architecture.md` for the full layering contract.
- Declare `status_code` explicitly on non-200 routes (`201` for creates,
  `204` for deletes with no body).

## 2. Dependency Injection

- Use `Annotated` dependency aliases — declare once, reuse everywhere:

  ```python
  SettingsDep = Annotated[Settings, Depends(get_settings)]
  SessionDep = Annotated[AsyncSession, Depends(get_session)]
  CurrentUser = Annotated[User, Depends(get_current_user)]
  ```

- Dependencies that own resources use `yield` (open/close a session,
  acquire/release a connection). Cleanup after `yield` runs even when the
  request raises.
- Cache pure, request-independent dependencies: `get_settings` is a
  `@lru_cache` function so `Settings` is constructed once per process.
- Never instantiate services, sessions, or clients inside route bodies —
  everything a route needs arrives through its signature. That is what
  makes `app.dependency_overrides` work in tests (see `testing.md`).
- Auth is a dependency, not a decorator or middleware check per route
  (see `security.md`).

## 3. Async / Sync Discipline

- `async def` routes and dependencies **only** when every awaited call is
  genuinely async (httpx, asyncpg/SQLAlchemy async, aioboto3...).
- A blocking call (requests, plain SQLAlchemy, file I/O, CPU-heavy work)
  inside an `async def` route **blocks the entire event loop** — every
  in-flight request stalls. This is the number-one FastAPI production
  incident.
- Plain `def` routes are fine: FastAPI runs them in a threadpool. A sync
  route that blocks hurts only its own thread.
- Do not mix: pick async or sync per dependency chain. An async route
  calling a sync ORM session is a bug even when it "works" locally.
- Offload unavoidable blocking work from async code with
  `run_in_threadpool` (from `starlette.concurrency`), or make the route
  `def`.

## 4. Pydantic v2 Models & Settings

- Separate model families per resource: `OrderCreate` (input),
  `OrderRead` (output, set as `response_model`), `OrderUpdate` (partial,
  all-optional). Never expose ORM/entity classes directly on the wire.
- Use v2 idioms only: `model_config = ConfigDict(...)`,
  `model_validate()`, `model_dump()`, `field_validator` /
  `model_validator`. No v1 `class Config`, `.dict()`, `.parse_obj()`,
  `@validator` — mixing eras breaks under upgrade.
- Output models that read from ORM objects set
  `model_config = ConfigDict(from_attributes=True)` (v1's `orm_mode`).
- Settings via `pydantic-settings`:

  ```python
  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
      database_url: PostgresDsn
      secret_key: SecretStr
      debug: bool = False
  ```

  One `Settings` class, loaded through a cached dependency. No
  `os.environ[...]` reads scattered through the codebase. Secrets are
  `SecretStr` so they never repr into logs.
- Constrain fields at the model (`Field(ge=1, max_length=200)`,
  `Literal[...]`, enums) — validation errors then return structured 422s
  for free instead of ad-hoc `if` checks returning 400s.

## 5. Error Handling

- Domain code raises **domain exceptions** (`OrderNotFoundError`), never
  `HTTPException`. Services must not import from `fastapi`.
- Register exception handlers in the factory that map domain exceptions
  to HTTP responses. One mapping, applied everywhere:

  ```python
  @app.exception_handler(NotFoundError)
  async def not_found(request: Request, exc: NotFoundError) -> JSONResponse:
      return JSONResponse(status_code=404, content={"detail": str(exc)})
  ```

- `HTTPException` is acceptable only in the routing/dependency layer for
  purely HTTP concerns (401/403 from auth dependencies).
- Use one error envelope shape across the API (FastAPI's `{"detail": ...}`
  is fine — keep it consistent, and document non-2xx responses in
  `responses={...}` for routes where clients must branch on them).
- Never return 200 with an error payload. Never swallow exceptions in
  routes — let the handler layer or the framework's 500 path log them.

## 6. Testing

- Default client: `httpx.AsyncClient` with `ASGITransport` against the
  factory-built app — no server process, real middleware and DI:

  ```python
  transport = ASGITransport(app=create_app())
  async with AsyncClient(transport=transport, base_url="http://test") as client:
      resp = await client.get("/orders/1")
  ```

- Replace real infrastructure with `app.dependency_overrides[dep] = fake`
  — never monkeypatch route internals.
- Test through the HTTP boundary for behavior (status codes, envelopes,
  validation errors); test services directly for business-logic branches.
- Full patterns — fixtures, async config, override hygiene, factories —
  in `testing.md`.

## Do / Don't

- **Do** build the app in a factory and manage startup/shutdown with a
  `lifespan` context manager — `@app.on_event` is deprecated.
- **Do** set `response_model` (or a return annotation) on every route so
  responses are filtered and documented.
- **Do** use `Annotated` dependency aliases; one definition per
  dependency, imported everywhere.
- **Do** keep routers thin and services framework-free.
- **Don't** call blocking I/O inside `async def` — it freezes the event
  loop for all requests.
- **Don't** raise `HTTPException` from services or import FastAPI below
  the routing layer.
- **Don't** mix Pydantic v1 and v2 idioms (`.dict()`, `class Config`,
  `@validator`) in a v2 codebase.
- **Don't** read `os.environ` outside `Settings`; don't construct
  `Settings()` at import time in library modules.
- **Don't** expose ORM entities as response bodies — always a dedicated
  `Read` model.

## Common Pitfalls

1. **Blocking call in an async route.** `requests.get()` or a sync DB
   session inside `async def` stalls every concurrent request. Symptom:
   p99 latency explodes under mild load. Fix: async client, or make the
   route `def`.
2. **Mutable default in a dependency or model** (`items: list = []`) —
   shared across requests. Use `Field(default_factory=list)`.
3. **Import-time app construction.** `app = FastAPI()` at module scope
   with side effects (DB connect, settings read) makes tests order-
   dependent and breaks multi-environment config. Use the factory.
4. **Forgetting `from_attributes=True`** on read models fed from ORM
   objects — `model_validate(entity)` raises at runtime, often only in
   the one route nobody tested.
5. **`dependency_overrides` leaking between tests** because a test forgot
   to clear them. Always set and clear via fixture (see `testing.md`).
6. **v1/v2 Pydantic mixing after an upgrade** — `.dict()` still works
   with deprecation warnings until it doesn't; `@validator` semantics
   differ from `field_validator`. Sweep the codebase once, fully.
7. **Auth checked in middleware by path prefix** instead of dependencies —
   new routes silently ship unauthenticated. Dependencies fail closed
   (see `security.md`).

## Checklist

- [ ] `create_app()` factory; no import-time side effects
- [ ] `lifespan` context manager for startup/shutdown (no `on_event`)
- [ ] One `APIRouter` per resource, prefix + tags set at include time
- [ ] `Annotated` dependency aliases in a single `dependencies.py`
- [ ] Yield dependencies for every owned resource (sessions, clients)
- [ ] No blocking calls in any `async def` path
- [ ] Pydantic v2 idioms only; `Create`/`Read`/`Update` model split
- [ ] `pydantic-settings` `Settings` with `SecretStr` secrets, cached dep
- [ ] Domain exceptions + registered handlers; no `HTTPException` in services
- [ ] `response_model` and explicit `status_code` on every route
- [ ] Tests use `ASGITransport` client + `dependency_overrides`
- [ ] Auth enforced via dependencies, fail-closed (see `security.md`)
