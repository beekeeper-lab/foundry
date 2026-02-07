# Python Testing

Testing strategy, frameworks, and patterns for Python projects including unit,
integration, property-based, and snapshot testing.

---

## Defaults

| Concern              | Default Tool / Approach            |
|----------------------|------------------------------------|
| Test framework       | `pytest`                           |
| Coverage             | `pytest-cov` (branch coverage)     |
| Mocking              | `unittest.mock` (stdlib)           |
| Property-based       | `hypothesis`                       |
| Integration fixtures | `testcontainers`                   |
| Snapshot testing     | `syrupy`                           |
| Async testing        | `pytest-asyncio`                   |
| Markers              | `pytest.mark.slow`, `pytest.mark.integration` |

### Alternatives

- **`ward`** -- expressive test framework; smaller ecosystem than pytest.
- **`nox`** / **`tox`** -- multi-environment test runners; use when you need
  to verify across Python versions. `nox` preferred for its Python-native config.
- **`factory_boy`** -- model factories; useful if you have complex ORM models.

---

## Project Layout

```
tests/
  conftest.py             # Shared fixtures, pytest plugins
  unit/
    test_services.py      # Mirrors src/<pkg>/services.py
    test_models.py
  integration/
    test_repository.py    # Tests against real DB via testcontainers
    conftest.py           # Integration-specific fixtures (containers, etc.)
```

Tests mirror the `src/` package structure. Each test file is named
`test_<module>.py`. Never put tests inside the `src/` package.

---

## Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow (deselect with -m 'not slow')",
    "integration: requires external services",
]
```

Run fast unit tests during development; full suite in CI:

```bash
# Fast feedback (skip slow + integration)
pytest -m "not slow and not integration"

# Full CI run
pytest
```

---

## Writing Tests

### Unit Test Example

```python
from __future__ import annotations

import pytest
from my_app.services.pricing import calculate_discount


class TestCalculateDiscount:
    """Tests for the calculate_discount function."""

    def test_no_discount_below_threshold(self) -> None:
        result = calculate_discount(total=49.99, tier="standard")
        assert result.discount == 0.0
        assert result.final_total == 49.99

    def test_percentage_discount_applied(self) -> None:
        result = calculate_discount(total=100.00, tier="premium")
        assert result.discount == pytest.approx(15.0)
        assert result.final_total == pytest.approx(85.0)

    def test_negative_total_raises(self) -> None:
        with pytest.raises(ValueError, match="total must be non-negative"):
            calculate_discount(total=-1.0, tier="standard")
```

### Fixture Example

```python
# tests/conftest.py
from __future__ import annotations

import pytest
from my_app.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Return test-specific settings with safe defaults."""
    return Settings(
        database_url="sqlite:///:memory:",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def service(settings: Settings) -> OrderService:
    """Provide a fully wired OrderService for unit tests."""
    repo = InMemoryOrderRepository()
    return OrderService(repo=repo, settings=settings)
```

### Integration Test with Testcontainers

```python
import pytest
from testcontainers.postgres import PostgresContainer

from my_app.repositories.order_repo import OrderRepository


@pytest.fixture(scope="module")
def pg_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture
def repo(pg_container) -> OrderRepository:
    url = pg_container.get_connection_url()
    return OrderRepository(database_url=url)


@pytest.mark.integration
def test_save_and_retrieve_order(repo: OrderRepository) -> None:
    order = repo.save(Order(customer_id="cust-1", total=99.99))
    retrieved = repo.get(order.id)
    assert retrieved.customer_id == "cust-1"
```

### Property-Based Test with Hypothesis

```python
from hypothesis import given, strategies as st
from my_app.services.pricing import calculate_discount


@given(total=st.floats(min_value=0, max_value=1_000_000, allow_nan=False))
def test_discount_never_exceeds_total(total: float) -> None:
    result = calculate_discount(total=total, tier="premium")
    assert 0 <= result.discount <= total
    assert result.final_total >= 0
```

---

## Do / Don't

**Do:**
- Use `pytest.approx()` for floating-point comparisons.
- Use fixtures for setup; avoid `setUp`/`tearDown` methods.
- Mark slow tests with `@pytest.mark.slow` to keep the fast loop fast.
- Use `testcontainers` for integration tests against real databases.
- Use `hypothesis` for any function with numeric or string input ranges.
- Name test classes `Test<Unit>` and test functions `test_<behavior>`.
- Scope expensive fixtures (`scope="module"` or `scope="session"`) appropriately.

**Don't:**
- Mock everything -- mocking the thing you are testing proves nothing.
- Use `unittest.TestCase` -- plain functions/classes with pytest are simpler.
- Put test utilities in `src/` -- keep them in `tests/` or `conftest.py`.
- Assert on implementation details (private methods, call counts) when you
  can assert on observable behavior instead.
- Use `time.sleep()` in tests -- use polling/retries or event-based waits.
- Skip writing integration tests because "unit tests are enough."

---

## Common Pitfalls

1. **Forgetting `--strict-markers`.** Without it, a typo in `@pytest.mark.solw`
   silently creates a new marker instead of failing. Always enable strict mode.

2. **Over-mocking.** If your test has more `patch()` calls than assertions,
   you are testing the mocking framework, not your code. Push I/O to the edges
   and test pure logic directly.

3. **Module-scoped fixtures that mutate state.** A fixture with
   `scope="module"` is shared across tests in the file. If one test mutates the
   fixture's return value, later tests see corrupted state. Use `scope="module"`
   only for read-only resources (containers, connections).

4. **Not testing the sad path.** Happy-path-only tests give false confidence.
   Every function that raises exceptions needs a test that triggers each one.

5. **Asserting on log output instead of return values.** If the only way to
   verify behavior is by reading logs, the function's API is too opaque.
   Refactor to return a result object.

6. **Flaky integration tests.** Tests that depend on timing, network, or
   execution order will fail randomly. Use deterministic container startup
   checks and idempotent setup.

---

## Checklist

- [ ] `pytest` configured in `pyproject.toml` with `--strict-markers` and `--strict-config`
- [ ] Coverage gate set: `--cov-fail-under=80` with branch coverage enabled
- [ ] Test directory mirrors `src/` package structure
- [ ] Shared fixtures in `conftest.py`, not duplicated across test files
- [ ] Slow tests marked with `@pytest.mark.slow`
- [ ] Integration tests marked with `@pytest.mark.integration`
- [ ] Integration tests use `testcontainers` (not mocked storage)
- [ ] At least one `hypothesis` property test for numeric/string logic
- [ ] No `time.sleep()` in tests -- use polling or event waits
- [ ] CI runs full suite; local dev can skip slow/integration with `-m`
- [ ] Every public exception path has a corresponding test
- [ ] No `unittest.TestCase` -- use plain pytest functions/classes
