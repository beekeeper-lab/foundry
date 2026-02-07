# Hardening

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
