# FastAPI Testing

How to test a FastAPI service: client setup, dependency overrides, async
configuration, and data factories. Assumes the pytest baseline from the
python pack and the app-factory + DI conventions from `conventions.md`.

## 1. Client Setup

Test against the ASGI app in-process — no server, no ports, real
middleware, real validation, real exception handlers.

**Async client (default):**

```python
import pytest
from httpx import ASGITransport, AsyncClient

from myapp.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

**Sync client (only for fully-sync codebases):**

```python
from fastapi.testclient import TestClient

@pytest.fixture
def client(app):
    with TestClient(app) as c:   # context manager runs lifespan
        yield c
```

Rules:

- The app comes from the **factory**, built fresh per test (or per
  module if construction is expensive and tests don't mutate it).
- Use the client as a context manager. For `TestClient` that is what
  triggers `lifespan`; skipping it means startup code never ran.
- `ASGITransport` does **not** run lifespan by itself. If a test needs
  startup/shutdown behavior, wrap the app with
  `asgi_lifespan.LifespanManager` or use `TestClient` — don't duplicate
  startup logic in fixtures.
- Never hit a live `uvicorn` process from unit/integration tests; that
  belongs to smoke tests only.

## 2. Async Test Configuration

- Install `pytest-asyncio` (or `anyio`); with pytest-asyncio set:

  ```toml
  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  ```

  so `async def test_*` functions and async fixtures just work — no
  per-test `@pytest.mark.asyncio` boilerplate.
- One event loop policy for the whole suite. Loop-scoped resources
  (async engines, connection pools) must be created inside the loop that
  runs the test — a session-scoped async engine with function-scoped
  loops is the classic "attached to a different loop" error. Align the
  fixture's loop scope with the resource's lifetime.
- Don't call `asyncio.run()` inside tests; the plugin owns the loop.

## 3. Dependency Overrides

`app.dependency_overrides` is the seam. Override the dependency
*function object* that routes actually depend on:

```python
from myapp.dependencies import get_session, get_current_user

@pytest.fixture
def app(fake_session):
    app = create_app()
    app.dependency_overrides[get_session] = lambda: fake_session
    yield app
    app.dependency_overrides.clear()
```

Rules:

- **Always clear** overrides in fixture teardown. A leaked override is a
  test-order heisenbug — passing alone, failing in the suite.
- Override at the same granularity production uses. If routes depend on
  `get_current_user`, override that — not the token decoder underneath —
  so auth tests stay independent of the auth backend:

  ```python
  app.dependency_overrides[get_current_user] = lambda: User(id=1, role="admin")
  ```

- Prefer overrides to `monkeypatch` for anything that is already a
  dependency. Monkeypatching module internals couples tests to import
  paths; overrides couple them to the public DI contract.
- Do not override validation-bearing dependencies with permissive fakes
  and then claim the validation is tested. Keep at least one test per
  route family against the real dependency chain.

## 4. Database Fixtures

- Integration tests run against a **real database** (testcontainers or
  docker-compose), per the python pack. SQLite-in-memory is acceptable
  only when production is also SQLite — dialect drift hides bugs.
- Standard shape: session-scoped engine, function-scoped transaction
  that rolls back:

  ```python
  @pytest.fixture
  async def db_session(engine):
      async with engine.connect() as conn:
          trans = await conn.begin()
          session = AsyncSession(bind=conn, expire_on_commit=False)
          yield session
          await session.close()
          await trans.rollback()
  ```

  Then override `get_session` to return this session, so route,
  service, and test all share one transaction and see each other's
  uncommitted data.

## 5. Data Factories

- Use factory functions (or `factory_boy` / `polyfactory`) for request
  payloads and entities, with sensible defaults and keyword overrides:

  ```python
  def order_payload(**overrides) -> dict:
      base = {"sku": "SKU-1", "quantity": 1, "customer_id": 42}
      return {**base, **overrides}

  async def test_rejects_zero_quantity(client):
      resp = await client.post("/orders", json=order_payload(quantity=0))
      assert resp.status_code == 422
  ```

- One factory per wire model, colocated in `tests/factories.py`. Tests
  state only the fields they care about; everything else is factory
  defaults — payload churn then touches one file, not fifty tests.
- Factories return plain dicts for request bodies (what the client
  sends), model instances for service-layer tests.

## 6. What to Assert

- Route tests assert the **HTTP contract**: status code, response
  envelope shape, validation errors (422 body includes the failing
  field), auth failures (401/403), and headers where they matter.
- Don't re-assert business math through HTTP — cover branches in
  service-level tests where setup is cheap, and keep one happy-path and
  one failure-path test per route.
- Assert on parsed JSON, not raw strings: `resp.json()["detail"]`, never
  substring matching on `resp.text`.
- For paginated/list endpoints, assert ordering and page metadata
  explicitly once; other tests may just assert membership.

## Pitfalls

1. **Lifespan never ran.** `TestClient(app)` without the `with` block, or
   `ASGITransport` assumed to run startup. Symptom: "pool is None" only
   in tests.
2. **Loop mismatch.** Session-scoped async fixtures with function-scoped
   event loops → `RuntimeError: attached to a different loop`. Align
   scopes.
3. **Override leakage.** Missing `dependency_overrides.clear()` in
   teardown; failures depend on test order.
4. **Overriding the wrong function.** Overriding `myapp.db.get_session`
   while routes import it via `myapp.dependencies.get_session` — the
   override is keyed by function object, so the wrong import does
   nothing, silently.
5. **Testing FastAPI itself.** Asserting that invalid enum values give
   422 for every single field on every route duplicates the framework's
   guarantees. Test your models' custom validators, not Pydantic's.
