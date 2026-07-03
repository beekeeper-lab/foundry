# Hardening

## Category
Compliance & Governance

Checklists and standards for hardening applications, APIs, and infrastructure.
Hardening reduces the attack surface by disabling what is not needed and
strengthening what remains.

---

## Defaults

- **TLS:** TLS 1.2 minimum. TLS 1.3 preferred. No SSL, no TLS 1.0/1.1.
- **HTTP security headers:** Applied at the reverse proxy or API gateway level.
  Enforced in CI via header-check tests.
- **Dependencies:** No known Critical/High CVEs in production dependencies.
  Scanned daily.
- **Attack surface:** Debug endpoints, admin panels, and development tools are
  disabled in production. Verified by automated checks.

---

## HTTP Security Headers

Every HTTP response from a production service must include these headers:

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store
```

```python
# FastAPI middleware example
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; object-src 'none'"
        return response
```

---

## Do / Don't

- **Do** enforce HTTPS everywhere. Redirect HTTP to HTTPS at the load balancer.
- **Do** set secure cookie attributes: `Secure`, `HttpOnly`, `SameSite=Lax` (or
  `Strict`), and appropriate `Path`/`Domain` scope.
- **Do** apply rate limiting on authentication endpoints (login, password reset,
  token refresh).
- **Do** disable directory listing on web servers and object storage buckets.
- **Do** remove default accounts, sample applications, and server version banners.
- **Do** pin dependency versions and use lock files with hash verification.
- **Don't** expose debug endpoints (`/debug`, `/metrics`, `/swagger`) without
  authentication in production.
- **Don't** use wildcard CORS (`Access-Control-Allow-Origin: *`) for authenticated APIs.
- **Don't** allow `GET` requests to perform state-changing operations.
- **Don't** trust the `Content-Type` header from clients. Validate the actual content.
- **Don't** leave default TLS certificates or self-signed certs in production.

---

## Common Pitfalls

1. **CORS misconfiguration.** Reflecting the `Origin` header back without validation
   effectively makes CORS a wildcard. Solution: maintain an explicit allowlist of
   permitted origins.
2. **Missing rate limiting.** Login endpoint allows unlimited attempts, enabling
   credential stuffing. Solution: rate limit by IP and by account. Lock accounts
   after N failed attempts.
3. **Stale dependencies.** The app ships with a 2-year-old version of a framework
   that has 15 known CVEs. Solution: automated dependency updates (Dependabot/Renovate)
   with CI verification.
4. **Overly permissive CSP.** `Content-Security-Policy: default-src *` or
   `unsafe-inline` `unsafe-eval` defeats the purpose. Solution: start strict,
   loosen only with documented justification. Use nonces for inline scripts.
5. **Debug mode in production.** Framework debug mode exposes stack traces, environment
   variables, and sometimes a code execution shell. Solution: CI check that verifies
   debug flags are false in production config.

---

## Input Validation Hardening

```python
# Defense against common injection patterns
import bleach
import re

def sanitize_html_input(raw: str) -> str:
    """Strip all HTML tags except a safe allowlist."""
    return bleach.clean(raw, tags=["b", "i", "em", "strong"], strip=True)

def validate_redirect_url(url: str, allowed_hosts: list[str]) -> str:
    """Prevent open redirect by validating against allowed hosts."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.hostname not in allowed_hosts:
        raise ValueError(f"Redirect to {parsed.hostname} is not allowed")
    if parsed.scheme not in ("https",):
        raise ValueError("Only HTTPS redirects are allowed")
    return url
```

---

## Dependency Hardening

```yaml
# Renovate config for automated dependency updates
# renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "vulnerabilityAlerts": {
    "enabled": true,
    "labels": ["security"]
  },
  "packageRules": [
    {
      "matchUpdateTypes": ["patch"],
      "automerge": true
    }
  ]
}
```

```bash
# Verify dependency integrity with hash checking
pip install --require-hashes -r requirements.lock
npm ci --ignore-scripts  # install without running postinstall scripts
```

---

## TLS Configuration

Recommended cipher suite order (test with `testssl.sh` or SSL Labs):

```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-RSA-AES128-GCM-SHA256
```

Disable: SSLv3, TLS 1.0, TLS 1.1, RC4, 3DES, CBC-mode ciphers, RSA key exchange.

---

## Alternatives

| Tool               | When to consider                                  |
|--------------------|---------------------------------------------------|
| ModSecurity (WAF)  | Application-level firewall rules                  |
| Cloudflare WAF     | Edge-level protection, managed rules              |
| Dependabot         | GitHub-native dependency updates (simpler config) |
| Renovate           | Multi-platform, more flexible update policies     |
| testssl.sh         | CLI tool for testing TLS configuration            |

---

## Checklist

- [ ] TLS 1.2+ enforced. TLS 1.0/1.1 and SSL disabled
- [ ] All HTTP security headers are present and correctly configured
- [ ] HSTS is enabled with a max-age of at least 1 year
- [ ] Cookies use `Secure`, `HttpOnly`, and `SameSite` attributes
- [ ] CORS is configured with an explicit origin allowlist (no wildcards)
- [ ] Rate limiting is applied to authentication and sensitive endpoints
- [ ] Debug mode is disabled in production (verified by CI)
- [ ] Server version banners and default pages are removed
- [ ] Dependencies are scanned daily; no Critical/High CVEs in production
- [ ] Automated dependency update tool is configured and running
- [ ] Input validation rejects unexpected content types and encodings
- [ ] Open redirect protection is in place for all redirect endpoints
- [ ] CSP is configured without `unsafe-inline` or `unsafe-eval`

---

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

---

# Security Testing

Standards for integrating security testing into the development lifecycle.
Security testing is continuous, automated, and part of the pipeline -- not a
periodic manual exercise.

---

## Defaults

- **SAST (Static Application Security Testing):** Runs on every PR. Blocks merge on
  Critical/High findings.
- **SCA (Software Composition Analysis):** Runs on every PR and on a daily schedule
  for new CVE disclosures.
- **DAST (Dynamic Application Security Testing):** Runs against staging after every
  deployment.
- **Secret scanning:** Pre-commit hook + CI pipeline check.
- **Baseline:** OWASP Top 10 coverage as the minimum for all testing tools.

---

## Testing Types

### SAST -- Find Bugs in Your Code
Static analysis scans source code for vulnerabilities without executing it. Catches
SQL injection, XSS, insecure deserialization, hardcoded secrets.

```yaml
# GitHub Actions SAST example with Semgrep
- name: SAST scan
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/security-audit
```

### SCA -- Find Bugs in Your Dependencies
Scans dependency manifests and lock files against CVE databases. Most exploited
vulnerabilities come from known CVEs in third-party libraries.

```yaml
# GitHub Actions SCA example
- name: Dependency audit
  run: |
    # Python
    pip-audit --require-hashes -r requirements.lock

    # Node
    npm audit --audit-level=high

    # General (Trivy)
    trivy fs --severity HIGH,CRITICAL --exit-code 1 .
```

### DAST -- Find Bugs at Runtime
Dynamic analysis tests a running application by sending malicious requests. Catches
issues that static analysis misses: misconfigured headers, authentication bypasses,
CORS issues.

```yaml
# DAST with OWASP ZAP against staging
- name: DAST scan
  uses: zaproxy/action-full-scan@v0.9.0
  with:
    target: "https://staging.example.com"
    rules_file_name: "zap-rules.tsv"
    allow_issue_writing: false
```

---

## Do / Don't

- **Do** run SAST and SCA on every PR. Fast feedback prevents security debt.
- **Do** tune SAST rules to reduce false positives. A noisy scanner gets ignored.
- **Do** fail the build on Critical and High severity findings.
- **Do** maintain a suppression file for acknowledged false positives, with
  justification and expiry date for each suppression.
- **Do** run dependency scans on a schedule (daily) to catch newly disclosed CVEs.
- **Don't** treat security testing as a replacement for secure design. Testing finds
  bugs; design prevents categories of bugs.
- **Don't** suppress findings without a documented justification and review.
- **Don't** run DAST against production unless you have explicit authorization and
  controls in place.
- **Don't** rely on a single tool. SAST, SCA, and DAST find different classes of bugs.
- **Don't** ignore Medium findings indefinitely. Triage and schedule them.

---

## Common Pitfalls

1. **Scanner overload.** Three SAST tools, two SCA tools, all dumping hundreds of
   findings. Nobody reads any of them. Solution: pick one tool per category. Tune
   it. Own the output.
2. **False positive fatigue.** Developers suppress all findings because 80% are false
   positives. Solution: invest time in custom rules and suppressions. A well-tuned
   scanner with 20 real findings beats a default scanner with 500 noise findings.
3. **SCA findings with no upgrade path.** A critical CVE in a dependency, but the
   fix requires a major version bump that breaks your code. Solution: track these
   as tech debt with a remediation deadline. Consider patching or replacing the
   dependency.
4. **DAST runs too slow for CI.** A full DAST scan takes 2 hours and blocks deploys.
   Solution: run a baseline (fast) scan in CI and a full scan nightly or weekly.
5. **No triage process.** Findings accumulate in a dashboard nobody checks. Solution:
   security findings go through the same triage and sprint planning as bugs.

---

## Recommended Tool Stack

| Category          | Primary tool  | Alternatives                          |
|-------------------|---------------|---------------------------------------|
| SAST              | Semgrep       | CodeQL, SonarQube, Snyk Code          |
| SCA               | Trivy         | Snyk, Dependabot, pip-audit, npm audit|
| DAST              | OWASP ZAP     | Burp Suite, Nuclei                    |
| Secret scanning   | Gitleaks      | TruffleHog, git-secrets               |
| Container scanning| Trivy         | Grype, Snyk Container                 |

---

## Triage Severity Matrix

| Scanner severity | Response time       | Action                              |
|-----------------|---------------------|-------------------------------------|
| Critical        | Block merge / 24h   | Fix immediately or revert the change|
| High            | Block merge / 7 days| Fix in current sprint               |
| Medium          | 30 days             | Schedule in backlog                 |
| Low             | 90 days             | Address opportunistically           |

---

## Checklist

- [ ] SAST runs on every PR and blocks merge on Critical/High
- [ ] SCA runs on every PR and on a daily schedule
- [ ] DAST runs against staging after each deployment
- [ ] Secret scanning runs as a pre-commit hook and in CI
- [ ] Container images are scanned before deployment
- [ ] False positive suppressions include justification and expiry dates
- [ ] Security findings feed into the team's triage and sprint planning
- [ ] SAST rules are tuned to the project (custom rules where needed)
- [ ] A dependency update strategy exists for CVE remediation
- [ ] Quarterly review of scanner effectiveness (false positive rate, missed findings)

---

# Threat Modeling

Standards for identifying, analyzing, and mitigating threats during design.
Threat modeling happens before code is written, not after a breach.

---

## Defaults

- **Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure,
  Denial of Service, Elevation of Privilege).
- **When:** Every new feature, every new service, every significant architecture change.
- **Participants:** Architect, lead developer, security engineer. Product owner for
  risk acceptance decisions.
- **Output:** Threat model document stored alongside the design doc in the repo.
  Each threat has a severity, mitigation, and owner.

---

## STRIDE Categories

| Category               | Threat question                                     | Typical mitigation           |
|------------------------|-----------------------------------------------------|------------------------------|
| **S**poofing           | Can an attacker pretend to be another user/service?  | Authentication, mTLS         |
| **T**ampering          | Can data be modified in transit or at rest?           | Integrity checks, signatures |
| **R**epudiation        | Can an actor deny performing an action?              | Audit logging, non-repudiation|
| **I**nformation Disclosure | Can sensitive data be exposed?                   | Encryption, access controls  |
| **D**enial of Service  | Can the system be made unavailable?                  | Rate limiting, scaling       |
| **E**levation of Privilege | Can a user gain unauthorized access?             | Authorization, least privilege|

---

## Do / Don't

- **Do** create a data flow diagram (DFD) before applying STRIDE. You cannot threat
  model what you cannot see.
- **Do** enumerate trust boundaries. Every point where data crosses a boundary is an
  attack surface.
- **Do** assign a severity to each threat (Critical, High, Medium, Low) using impact
  and likelihood.
- **Do** track mitigations as actionable work items, not vague statements.
- **Do** review the threat model when the architecture changes.
- **Don't** threat model in a vacuum. Include developers who know the system internals.
- **Don't** accept risk without explicit sign-off from a product owner or security lead.
- **Don't** treat threat modeling as a one-time ceremony. Update it as the system evolves.
- **Don't** model only external threats. Insider threats and supply chain attacks matter.

---

## Common Pitfalls

1. **Analysis paralysis.** The team models every conceivable threat and never ships.
   Solution: focus on the top 10 threats by severity. Iterate in later sessions.
2. **DFD is too abstract.** A single box labeled "backend" hides all the interesting
   attack surface. Solution: decompose to the level of individual services, data stores,
   and external integrations.
3. **Mitigations are "we'll fix it later."** Threats are identified but never addressed.
   Solution: every mitigation becomes a tracked ticket with a sprint assignment.
4. **No follow-up.** The model is created once and forgotten. A new API endpoint is
   added six months later with no threat review. Solution: make threat model updates
   a required checklist item for architecture changes.
5. **Confusing threats with vulnerabilities.** A threat is what an attacker wants to
   do. A vulnerability is a weakness they exploit. Keep them separate in your model.

---

## Threat Modeling Process

### Step 1: Draw the Data Flow Diagram

```
  [User Browser]
       |
       | HTTPS (TLS 1.3)
       v
  [API Gateway]  ---- trust boundary ----
       |
       | JWT (internal)
       v
  [Order Service] ----> [Database]
       |                    ^
       | gRPC (mTLS)        | encrypted at rest
       v                    |
  [Payment Service] ----> [Audit Log]
       |
       | HTTPS
       v
  [External Payment Provider]  ---- trust boundary ----
```

### Step 2: Apply STRIDE to Each Element

```markdown
## Threat: Spoofed API requests (Spoofing)
- **Target:** API Gateway
- **Attack:** Attacker forges JWT tokens to impersonate users.
- **Severity:** Critical
- **Mitigation:** Validate JWT signature with RS256. Verify issuer, audience,
  and expiry. Reject tokens signed with "none" algorithm.
- **Owner:** @backend-team
- **Status:** Mitigated (JWT validation middleware deployed)

## Threat: Tampered order data (Tampering)
- **Target:** Order Service -> Database
- **Attack:** SQL injection modifies order totals.
- **Severity:** High
- **Mitigation:** Parameterized queries for all database access. ORM-only
  data access layer. No raw SQL.
- **Owner:** @backend-team
- **Status:** Mitigated (ORM enforced, raw SQL blocked by linter rule)
```

### Step 3: Prioritize and Track

Rank threats by `impact x likelihood`. Critical and High threats must be mitigated
before the feature launches. Medium threats are tracked for the next iteration.

---

## Threat Model Document Template

```markdown
# Threat Model: [Feature/Service Name]
**Date:** YYYY-MM-DD
**Participants:** [names]
**Status:** Draft | Reviewed | Accepted

## System Overview
[Brief description and link to architecture diagram]

## Data Flow Diagram
[Embed or link to DFD]

## Trust Boundaries
1. External internet -> API Gateway
2. API Gateway -> Internal services
3. Internal services -> External providers

## Threats
| ID  | Category | Description         | Severity | Mitigation       | Owner | Status    |
|-----|----------|---------------------|----------|------------------|-------|-----------|
| T01 | Spoofing | Forged JWT tokens   | Critical | JWT RS256 validation | @team | Mitigated |
| T02 | Tampering| SQL injection       | High     | Parameterized queries | @team | Mitigated |

## Accepted Risks
[List any threats accepted with justification and sign-off]
```

---

## Alternatives

| Methodology       | When to consider                                    |
|-------------------|-----------------------------------------------------|
| PASTA             | Risk-centric, business-impact focused modeling      |
| Attack Trees      | Analyzing a specific, known attack goal in depth    |
| LINDDUN           | Privacy-focused threat modeling                     |
| VAST              | Scaling threat modeling across large organizations  |

---

## Checklist

- [ ] Data flow diagram is created before threat analysis begins
- [ ] Trust boundaries are explicitly identified and labeled
- [ ] STRIDE is applied to each component and data flow
- [ ] Each threat has severity, mitigation, owner, and status
- [ ] Critical and High threats are mitigated before feature launch
- [ ] Risk acceptance decisions have explicit sign-off
- [ ] Threat model is stored in the repository alongside design docs
- [ ] Threat model is reviewed when architecture changes
- [ ] Mitigations are tracked as work items with sprint assignments
- [ ] The team reviews the threat model at least once per quarter
