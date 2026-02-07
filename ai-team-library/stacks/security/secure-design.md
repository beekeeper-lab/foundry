# Secure Design Principles

Foundational security principles applied during architecture and design.
Security is a design constraint, not a feature bolted on after development.

---

## Defaults

- **Reference framework:** OWASP ASVS (Application Security Verification Standard)
  Level 2 as the minimum for all production applications.
- **Design posture:** Defense in depth. No single control is trusted to be sufficient.
- **Trust model:** Zero trust. Every request is authenticated and authorized regardless
  of network origin.
- **Data classification:** All data is classified (public, internal, confidential,
  restricted) before storage or transmission decisions are made.

---

## Core Principles

### Defense in Depth
Layer multiple independent controls so that a failure in one does not compromise the
system. Authentication at the gateway does not eliminate the need for authorization
checks in the service.

### Least Privilege
Every component, user, and service account receives the minimum permissions required
to perform its function. Permissions are granted explicitly, never by default.

### Fail Secure
When a component fails, it denies access rather than granting it. A crashed
authorization service means requests are rejected, not allowed through.

### Secure by Default
The default configuration is the secure configuration. Features that weaken security
(CORS wildcards, debug endpoints, verbose errors) must be explicitly opted into and
documented.

### Separation of Duties
No single role can perform a sensitive operation end-to-end. Code authors cannot
approve their own pull requests. Deploy pipelines require a separate approver.

---

## Do / Don't

- **Do** authenticate every API endpoint. Unauthenticated endpoints are explicitly
  documented and approved.
- **Do** validate all input at the boundary. Trust nothing from the client.
- **Do** encrypt data in transit (TLS 1.2+) and at rest (AES-256 or equivalent).
- **Do** return generic error messages to clients. Internal details go to logs only.
- **Do** use parameterized queries for all database access. No string concatenation.
- **Don't** implement custom cryptography. Use established libraries (libsodium, etc.).
- **Don't** store secrets in application code, config files, or environment variable
  defaults.
- **Don't** expose stack traces, database errors, or internal paths in API responses.
- **Don't** rely on client-side validation for security. It is a UX convenience only.
- **Don't** disable security controls for convenience in production.

---

## Common Pitfalls

1. **Implicit trust between internal services.** "It's behind the firewall" is not
   a security control. Solution: mutual TLS or JWT validation between all services.
2. **Authorization at the API gateway only.** The gateway checks authentication, but
   individual services skip authorization. Solution: each service enforces its own
   authorization rules.
3. **Verbose error messages in production.** Stack traces in API responses reveal
   internal architecture. Solution: structured error responses with correlation IDs.
   Details in server-side logs only.
4. **Shared service accounts.** Multiple applications use the same database credentials.
   A breach in one compromises all. Solution: per-service credentials with minimal
   permissions.
5. **Security reviewed only before launch.** Design flaws found late are expensive to
   fix. Solution: threat modeling during design, security review in every PR.

---

## Input Validation Pattern

```python
# Validate at the boundary, reject early
from pydantic import BaseModel, Field, field_validator
import re

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str = Field(max_length=254)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must be alphanumeric")
        return v

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()
```

---

## Secure Error Response Pattern

```python
# Return safe errors to clients, log details internally
import uuid
import structlog

logger = structlog.get_logger()

def handle_error(exc: Exception) -> dict:
    correlation_id = str(uuid.uuid4())
    logger.error(
        "unhandled_exception",
        correlation_id=correlation_id,
        error_type=type(exc).__name__,
        error_detail=str(exc),  # internal log only
    )
    # Client sees correlation ID, not the exception details
    return {
        "error": "An internal error occurred.",
        "correlation_id": correlation_id,
    }
```

---

## Alternatives

| Framework          | When to consider                                 |
|--------------------|--------------------------------------------------|
| OWASP ASVS L1     | Low-risk internal tools                          |
| OWASP ASVS L3     | Financial, healthcare, or high-compliance apps   |
| NIST 800-53       | US federal compliance requirements               |
| CIS Benchmarks    | Infrastructure-level hardening baselines         |

---

## Checklist

- [ ] All endpoints require authentication (exceptions are documented and approved)
- [ ] Authorization is enforced at the service level, not just the gateway
- [ ] All input is validated at system boundaries using allowlists
- [ ] Data is encrypted in transit (TLS 1.2+) and at rest
- [ ] Error responses do not leak internal details (stack traces, SQL errors, paths)
- [ ] Database queries use parameterized statements -- no string concatenation
- [ ] Service-to-service communication uses mutual TLS or signed tokens
- [ ] Each service has its own credentials with least-privilege permissions
- [ ] Data classification is documented for all stored data
- [ ] Security review is part of the PR process, not a one-time gate
