# Security Conventions

## Category
Compliance & Governance

Security is a design constraint, not a feature bolted on after development.
These conventions cover secure design principles, threat modeling, continuous
security testing, and hardening — applied from design through deployment.

---

## Defaults

| Concern              | Default Approach                                        |
|----------------------|---------------------------------------------------------|
| Reference framework  | OWASP ASVS Level 2 minimum for production applications  |
| Design posture       | Defense in depth — no single control trusted alone      |
| Trust model          | Zero trust — every request authenticated and authorized |
| Data classification  | All data classified (public/internal/confidential/restricted) before storage decisions |
| Threat modeling      | STRIDE, for every new feature/service/architecture change |
| SAST                 | Every PR; blocks merge on Critical/High findings        |
| SCA                  | Every PR + daily schedule for new CVE disclosures       |
| DAST                 | Against staging after every deployment                  |
| Secret scanning      | Pre-commit hook + CI pipeline check                     |
| TLS                  | 1.2 minimum, 1.3 preferred; no SSL, no TLS 1.0/1.1      |
| Security headers     | Applied at reverse proxy/gateway; enforced by CI tests  |
| Dependencies         | No known Critical/High CVEs in production; scanned daily |
| Attack surface       | Debug endpoints/admin panels disabled in production, verified by automated checks |

---

## 1. Secure Design Principles

- **Defense in depth.** Layer independent controls; authentication at the
  gateway does not eliminate authorization checks in each service.
- **Least privilege.** Every component, user, and service account gets the
  minimum permissions required — granted explicitly, never by default.
- **Fail secure.** A crashed authorization service means requests are
  rejected, not allowed through.
- **Secure by default.** Features that weaken security (CORS wildcards, debug
  endpoints, verbose errors) are explicitly opted into and documented.
- **Separation of duties.** No single role performs a sensitive operation
  end-to-end; code authors cannot approve their own PRs.

Validate all input at the boundary with allowlists; use parameterized queries
only; encrypt in transit (TLS 1.2+) and at rest (AES-256 or equivalent).
Return generic error messages with correlation IDs — internal details go to
server-side logs only.

Full detail: `secure-design.md`

---

## 2. Threat Modeling

- **Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information
  Disclosure, Denial of Service, Elevation of Privilege).
- **When:** every new feature, new service, and significant architecture
  change — before code is written. Review the model whenever the
  architecture changes.
- **Process:** draw a data flow diagram first (you cannot threat model what
  you cannot see), enumerate trust boundaries, apply STRIDE to each element,
  rank by impact × likelihood.
- **Output:** threat model document stored alongside the design doc in the
  repo. Each threat has severity, mitigation, owner, and status. Mitigations
  become tracked tickets, not vague statements.
- Critical and High threats must be mitigated before feature launch. Risk
  acceptance requires explicit sign-off from a product owner or security lead.

Full detail: `threat-modeling.md`

---

## 3. Security Testing Pipeline

Security testing is continuous, automated, and part of the pipeline — not a
periodic manual exercise. Pick one tool per category and tune it; SAST, SCA,
and DAST find different classes of bugs.

| Category           | Primary tool | Runs                              |
|--------------------|--------------|-----------------------------------|
| SAST               | Semgrep      | Every PR, blocks on Critical/High |
| SCA                | Trivy        | Every PR + daily schedule         |
| DAST               | OWASP ZAP    | Staging after each deployment     |
| Secret scanning    | Gitleaks     | Pre-commit + CI                   |
| Container scanning | Trivy        | Before deployment                 |

Triage: Critical = block merge / fix in 24h; High = block merge / 7 days;
Medium = 30 days; Low = 90 days. Suppressions require documented
justification and an expiry date. Findings feed the same triage and sprint
planning as bugs.

Full detail: `security-testing.md`

---

## 4. Hardening — Headers, TLS, Cookies

Every production HTTP response includes:

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store
```

- Enforce HTTPS everywhere; redirect HTTP at the load balancer. Disable
  SSLv3, TLS 1.0/1.1, RC4, 3DES, CBC-mode ciphers, and RSA key exchange.
  Test with `testssl.sh` or SSL Labs.
- Cookies use `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict`), and scoped
  `Path`/`Domain`.
- CORS uses an explicit origin allowlist — never wildcards for authenticated
  APIs, and never reflect the `Origin` header back unvalidated.
- Rate limit authentication endpoints (login, password reset, token refresh)
  by IP and by account.
- Remove default accounts, sample applications, server version banners, and
  directory listings.

Full detail: `hardening.md`

---

## 5. Dependency and Input Hardening

- Pin dependency versions; use lock files with hash verification
  (`pip install --require-hashes`, `npm ci --ignore-scripts`).
- Run an automated dependency update tool (Renovate or Dependabot) with
  vulnerability alerts enabled and CI verification.
- Sanitize HTML input against a safe tag allowlist; validate redirect URLs
  against an allowed-hosts list (HTTPS only) to prevent open redirects.
- Don't trust the `Content-Type` header from clients — validate actual
  content.

Full detail: `hardening.md`

---

## Do / Don't

**Do:**
- Authenticate every API endpoint; document and approve any exceptions.
- Validate all input at the boundary. Trust nothing from the client.
- Use parameterized queries for all database access. No string concatenation.
- Create a data flow diagram and enumerate trust boundaries before STRIDE.
- Run SAST and SCA on every PR; fail the build on Critical/High findings.
- Tune SAST rules to reduce false positives — a noisy scanner gets ignored.
- Set secure cookie attributes and rate limit authentication endpoints.

**Don't:**
- Implement custom cryptography — use established libraries (libsodium, etc.).
- Store secrets in application code, config files, or env var defaults.
- Expose stack traces, database errors, or internal paths in API responses.
- Rely on client-side validation for security — it is a UX convenience only.
- Suppress scanner findings without documented justification and review.
- Use wildcard CORS for authenticated APIs or allow `GET` to change state.
- Expose debug endpoints (`/debug`, `/metrics`, `/swagger`) unauthenticated
  in production.
- Accept risk without explicit sign-off from a product owner or security lead.

---

## Common Pitfalls

1. **Implicit trust between internal services.** "It's behind the firewall"
   is not a security control. Use mutual TLS or JWT validation between all
   services.

2. **Authorization at the API gateway only.** The gateway authenticates but
   services skip authorization. Each service enforces its own authorization
   rules.

3. **Shared service accounts.** One breached credential compromises every
   app. Per-service credentials with minimal permissions.

4. **CORS misconfiguration.** Reflecting the `Origin` header back without
   validation is effectively a wildcard. Maintain an explicit allowlist.

5. **False positive fatigue.** Developers suppress everything because 80% is
   noise. A well-tuned scanner with 20 real findings beats a default scanner
   with 500 noise findings.

6. **Threat model with no follow-up.** Created once, forgotten; new endpoints
   ship with no threat review. Make threat model updates a required checklist
   item for architecture changes.

7. **Debug mode in production.** Exposes stack traces, environment variables,
   sometimes a code-execution shell. Add a CI check that debug flags are
   false in production config.

---

## Checklist

- [ ] All endpoints require authentication; exceptions documented and approved
- [ ] Authorization enforced at the service level, not just the gateway
- [ ] All input validated at boundaries using allowlists; parameterized queries only
- [ ] Data encrypted in transit (TLS 1.2+) and at rest; data classification documented
- [ ] Error responses leak no internal details; correlation IDs link to server logs
- [ ] Threat model (STRIDE + DFD) exists, is stored in-repo, reviewed on architecture change
- [ ] Critical/High threats mitigated before launch; risk acceptance signed off
- [ ] SAST and SCA run on every PR and block merge on Critical/High
- [ ] DAST runs against staging after each deployment
- [ ] Secret scanning runs pre-commit and in CI; container images scanned before deploy
- [ ] All HTTP security headers present; HSTS max-age ≥ 1 year; strict CSP (no `unsafe-inline`/`unsafe-eval`)
- [ ] Cookies use `Secure`, `HttpOnly`, `SameSite`; CORS uses explicit allowlist
- [ ] Rate limiting on authentication and sensitive endpoints
- [ ] Dependencies scanned daily, no Critical/High CVEs; automated updates configured
- [ ] Debug mode disabled in production, verified by CI
