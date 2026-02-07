# Python Security

Security practices for Python projects including dependency auditing, secrets
management, input validation, and common vulnerability prevention.

---

## Defaults

| Concern              | Default Tool / Approach            |
|----------------------|------------------------------------|
| Dependency audit     | `pip-audit`                        |
| Static analysis      | `bandit` (via ruff `S` rules)      |
| Secrets detection    | `detect-secrets` (pre-commit)      |
| Input validation     | `pydantic` (strict mode)           |
| Secrets management   | Environment variables + vault      |
| HTTP client          | `httpx` (timeout defaults set)     |
| Password hashing     | `argon2-cffi`                      |
| Cryptography         | `cryptography` (never roll your own) |

### Alternatives

- **`safety`** -- alternative to `pip-audit`; commercial product with a free
  tier. `pip-audit` uses the same PyPI advisory database and is fully open.
- **`semgrep`** -- more powerful static analysis with custom rules. Use it for
  team-specific security patterns beyond what ruff/bandit cover.
- **`trufflehog`** -- git history secrets scanner. Use alongside
  `detect-secrets` for repos with long history.

---

## Dependency Auditing

Run `pip-audit` in CI on every build. It checks installed packages against
the PyPI advisory database (and optionally the OSV database).

```bash
# Audit current environment
pip-audit

# Audit from requirements/lock file
pip-audit -r requirements.lock

# Strict mode: fail on any warning (not just known vulnerabilities)
pip-audit --strict
```

```toml
# pyproject.toml -- include in dev dependencies
[project.optional-dependencies]
dev = [
    "pip-audit>=2.7",
    # ...
]
```

Automate with a weekly scheduled CI job in addition to per-PR checks. New
CVEs appear between commits.

---

## Secrets Management

**Rule: No secrets in code, config files, or environment variable defaults.**

```python
# BAD -- hardcoded secret
API_KEY = "sk-live-abc123"

# BAD -- default value leaks in non-production
API_KEY = os.getenv("API_KEY", "sk-live-abc123")

# GOOD -- fail fast if not configured
API_KEY = os.environ["API_KEY"]

# BETTER -- validated via pydantic settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str  # No default; startup fails if missing
    database_url: str
    debug: bool = False

    model_config = {"env_prefix": "APP_"}
```

**Pre-commit hook to prevent accidental commits:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

Generate the baseline once: `detect-secrets scan > .secrets.baseline`.
Review and update it when legitimate secrets patterns change.

---

## Input Validation

Never trust external input. Use Pydantic in strict mode to validate and
coerce at the boundary.

```python
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CreateOrderRequest(BaseModel):
    """Validated request for creating an order."""

    model_config = {"strict": True}

    customer_id: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    quantity: int = Field(ge=1, le=10_000)
    email: str = Field(max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()
```

Key principles:
- Validate at the boundary (API handler, CLI parser, file reader).
- Reject by default; explicitly allow known-good patterns.
- Use `Field` constraints (`min_length`, `ge`, `pattern`) over custom validators
  when possible.

---

## SQL Injection Prevention

Always use parameterized queries. Never build SQL with string formatting.

```python
# BAD -- SQL injection via string formatting
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# GOOD -- parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# GOOD -- SQLAlchemy ORM (parameterized by default)
user = session.query(User).filter(User.id == user_id).first()
```

If you use raw SQL anywhere, wrap it in a dedicated repository function that
enforces parameterization. Never pass raw SQL strings through multiple layers.

---

## Safe HTTP Clients

Always set timeouts. A missing timeout can hang your service indefinitely.

```python
import httpx

# GOOD -- explicit timeouts
client = httpx.Client(
    timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
    follow_redirects=True,
    max_redirects=5,
)

# BAD -- no timeout (blocks forever on unresponsive server)
response = httpx.get("https://api.example.com/data")
```

For `requests`, the same applies: always pass `timeout=`.

---

## Path Traversal Prevention

Never construct file paths from user input without sanitization.

```python
from pathlib import Path

UPLOAD_DIR = Path("/var/app/uploads")

def safe_file_path(user_filename: str) -> Path:
    """Resolve a user-provided filename safely within UPLOAD_DIR."""
    # Resolve to absolute, then verify it's within the allowed directory
    candidate = (UPLOAD_DIR / user_filename).resolve()
    if not candidate.is_relative_to(UPLOAD_DIR):
        raise ValueError("Path traversal attempt detected")
    return candidate
```

---

## Do / Don't

**Do:**
- Run `pip-audit` in CI on every PR and on a weekly schedule.
- Use `detect-secrets` as a pre-commit hook.
- Validate all external input with Pydantic strict mode at the boundary.
- Set explicit timeouts on every HTTP client.
- Use parameterized queries for all database access.
- Use `os.environ["KEY"]` (KeyError on missing) instead of `os.getenv("KEY")`.
- Hash passwords with `argon2-cffi`, never MD5/SHA for passwords.
- Use `secrets.token_urlsafe()` for generating tokens, not `random`.

**Don't:**
- Hardcode secrets, API keys, or database passwords in source code.
- Use `os.getenv()` with a secret as the default value.
- Build SQL with f-strings, `.format()`, or `%` string interpolation.
- Use `pickle` or `eval()` on untrusted input (arbitrary code execution).
- Disable SSL verification (`verify=False`) in production HTTP clients.
- Use `random` for security-sensitive values -- use `secrets` module instead.
- Roll your own cryptography -- use the `cryptography` library.
- Log secrets, tokens, passwords, or unmasked PII.

---

## Common Pitfalls

1. **Using `os.getenv()` with a fallback secret.** `os.getenv("KEY", "default")`
   means the app runs with "default" as the actual key in any environment
   where the variable is not set. Use `os.environ["KEY"]` to fail fast.

2. **`pickle.loads()` on untrusted data.** Pickle executes arbitrary Python
   during deserialization. Use JSON, MessagePack, or Protobuf for untrusted
   data. If you must use pickle, restrict it with `RestrictedUnpickler`.

3. **Missing timeouts on HTTP clients.** Without a timeout, a single slow
   upstream service can exhaust your connection pool and cascade into a full
   outage.

4. **Trusting `Content-Type` headers.** An attacker can send a JPEG with a
   `.py` extension or vice versa. Validate file contents, not just headers
   or extensions.

5. **Logging full request bodies.** Audit your structured logs to ensure they
   do not capture passwords, tokens, or PII in keyword arguments. Use
   allowlist-based logging for sensitive endpoints.

6. **Not running `pip-audit` on a schedule.** New CVEs appear between commits.
   A weekly CI job catches vulnerabilities in transitive dependencies that
   your lock file pins.

7. **Using `random` for tokens or session IDs.** The `random` module is
   predictable. Use `secrets.token_urlsafe(32)` for anything security-sensitive.

---

## Checklist

- [ ] `pip-audit` runs in CI on every PR (and weekly scheduled job)
- [ ] `detect-secrets` configured as a pre-commit hook with baseline file
- [ ] No hardcoded secrets in source code, config files, or env defaults
- [ ] All secrets loaded via `os.environ["KEY"]` or Pydantic `BaseSettings`
- [ ] All external input validated with Pydantic strict mode at the boundary
- [ ] All SQL uses parameterized queries (no string interpolation)
- [ ] All HTTP clients have explicit connect/read/write timeouts
- [ ] File path construction from user input uses `.resolve()` + `is_relative_to()`
- [ ] `secrets` module used for token generation (not `random`)
- [ ] `argon2-cffi` used for password hashing (not MD5/SHA)
- [ ] No `pickle.loads()` or `eval()` on untrusted input
- [ ] SSL verification enabled on all production HTTP clients
- [ ] Structured logs reviewed to confirm no secrets or PII are logged
- [ ] `bandit` rules enabled in ruff (`S` ruleset) and passing in CI
