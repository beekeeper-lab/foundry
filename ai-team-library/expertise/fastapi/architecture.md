# FastAPI Architecture

Layering, lifecycle, background work, versioning, and OpenAPI discipline
for FastAPI services beyond a handful of routes. Builds on the app
factory and DI conventions in `conventions.md`.

## 1. Layering: Routers → Services → Repositories

```
src/myapp/
  main.py            # create_app(): routers, handlers, middleware, lifespan
  dependencies.py    # Annotated DI aliases (settings, session, current user)
  routers/           # HTTP layer: one APIRouter per resource
  services/          # Business logic: framework-free functions/classes
  repositories/      # Data access: all queries live here
  models/            # Pydantic wire models (Create/Read/Update) + domain types
  db/                # Engine, ORM entities, migrations
```

Contracts between layers:

- **Routers** know HTTP and nothing else: parse via Pydantic, resolve
  dependencies, call one service function, map the result to a response.
  A route body longer than ~15 lines is usually smuggling business logic.
- **Services** know the domain and nothing about HTTP. They must not
  import `fastapi` or `starlette`, must not raise `HTTPException`, and
  take plain arguments or domain objects — not `Request`. This is what
  keeps them unit-testable and reusable from the CLI/worker context.
- **Repositories** own every query. Services call repository methods;
  routers never touch a session directly. Swapping storage or adding
  caching then touches one layer.
- Dependency direction is strictly downward: routers → services →
  repositories. A service importing from `routers/` is an architecture
  bug.
- Small services can start with routers + services and fold repositories
  in later — but the "no HTTP below the router" rule holds from day one;
  it is the cheap rule that keeps the expensive refactor possible.

## 2. Lifespan & Shared Resources

- Startup/shutdown live in a `lifespan` async context manager passed to
  `FastAPI(lifespan=...)`. `@app.on_event("startup")` is deprecated —
  don't write new code with it.

  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      app.state.engine = create_async_engine(settings.database_url)
      app.state.http = httpx.AsyncClient()
      yield
      await app.state.http.aclose()
      await app.state.engine.dispose()
  ```

- Process-wide resources (engine, connection pools, one shared
  `httpx.AsyncClient`) are created in lifespan and reached through
  dependencies that read `app.state` — never created per-request, never
  at import time.
- Everything opened before `yield` is closed after it, in reverse order.
  If a resource has no shutdown story, it will leak in every worker
  recycle.

## 3. Background Work

- `BackgroundTasks` (the dependency) is for **small, fire-and-forget**
  work after the response: send an email, write an audit row. It runs in
  the same process, after the response is sent, with no retry, no
  persistence, and it dies with the worker.
- The moment work needs retries, persistence, scheduling, longer than a
  few seconds of runtime, or survival across deploys — it is a **job
  queue** problem (Celery, arq, Dramatiq, or the platform's queue), not
  `BackgroundTasks`. Enqueue in the route, process in a worker.
- Background functions get plain data (ids, payloads), not ORM instances
  or sessions bound to the finished request — the session is closed by
  the time the task runs. Re-load inside the task.
- Never `asyncio.create_task()` from a route for work that matters:
  unobserved exceptions vanish and graceful shutdown won't wait for it.

## 4. API Versioning

- Version in the path, at the router-mounting level:
  `app.include_router(v1_router, prefix="/api/v1")`. Header-based
  versioning hides the version from logs, caches, and curl — path wins
  on operability.
- Version when you **break** the contract (removing/renaming fields,
  changing semantics), not for additive changes. Adding optional fields
  and new endpoints is not a new version.
- A new version gets new wire models and new routers; it may share
  services. Never fork the service layer per API version — that is how
  business rules diverge silently.
- Keep at most two live versions and publish a sunset date for the old
  one when v-next ships. "We'll deprecate it later" means never.

## 5. OpenAPI Discipline

The generated schema is a **deliverable** — clients and SDK generators
consume it, so treat drift as a defect.

- Every route declares `response_model` (or a precise return
  annotation), `status_code`, and belongs to a tag. Untyped routes
  produce `{}` schemas that poison generated clients.
- Set `summary` (imperative, short) on routes and docstrings for
  descriptions; document non-2xx responses clients must handle via
  `responses={404: {...}, 409: {...}}`.
- Give operations stable ids when clients are generated from the schema
  (a `generate_unique_id_function` producing `{tag}_{route.name}` beats
  the verbose default) — changing an operation id breaks generated SDKs.
- Wire-model changes are contract changes: review the schema diff. Add a
  CI step that exports `app.openapi()` to a committed JSON file and
  fails when it changes without the commit updating it — cheap,
  high-signal drift detection.
- Mark deprecated routes with `deprecated=True` so the schema and docs
  carry the warning, then actually remove them on the published date.

## Pitfalls

1. **Business logic accreting in routes.** Starts as one `if`, ends with
   untestable 80-line route bodies. Enforce the thin-router rule in
   review from the first PR.
2. **Services raising `HTTPException`.** The domain layer now depends on
   the framework, and the same logic can't serve a worker or CLI. Domain
   exceptions + handlers (see `conventions.md` §5).
3. **Per-request `httpx.AsyncClient` or engine.** Connection-pool churn
   and socket exhaustion under load. Create in lifespan, inject via DI.
4. **`BackgroundTasks` used as a job queue.** Deploy restarts silently
   drop the "queued" work. If losing it matters, it needs a real queue.
5. **Passing a request-scoped session into a background task.** The
   session is closed when the task runs; symptoms look like flaky
   `InvalidRequestError`s. Pass ids, re-load in the task.
6. **Versioning by copy-pasting services.** Two v-forks of the pricing
   rules disagree within a quarter. Version wire models and routers;
   share services.
7. **Nobody owns the schema.** Response models drift from reality, and
   the first consumer of the generated SDK finds out. Commit the schema
   export and diff it in CI.
