# React Security

Security in React applications requires defense in depth: framework-level
protections, secure coding patterns, dependency hygiene, and server-side
enforcement. Client-side security is a complement to -- never a replacement
for -- server-side validation and authorization.

---

## Defaults

- **XSS prevention:** Rely on React's automatic JSX escaping. Never bypass it.
- **Content Security Policy (CSP):** Enforce a strict CSP header on every deployment.
- **Dependency auditing:** `pnpm audit` runs in CI; critical/high vulnerabilities block the build.
- **Secrets management:** No secrets in client-side code. Environment variables prefixed with `VITE_` are public.
- **Authentication tokens:** Store in `httpOnly` cookies, not `localStorage`.
- **Linting:** `eslint-plugin-security` enabled for server-adjacent code.

### Alternatives

| Default               | Alternative            | When to consider                    |
|-----------------------|------------------------|-------------------------------------|
| `pnpm audit`          | Snyk / Socket          | Need deeper supply-chain analysis   |
| `httpOnly` cookies    | Token in memory        | Short-lived SPA with no refresh     |
| CSP via headers       | CSP via `<meta>` tag   | No control over server headers      |

---

## XSS Prevention

React escapes JSX expressions by default. The primary risk is bypassing that
protection.

```tsx
// Safe: React escapes the value automatically
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}</h1>;
}

// DANGEROUS: bypasses React's escaping -- XSS vulnerability
function RawContent({ html }: { html: string }) {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
```

**Rules for `dangerouslySetInnerHTML`:**

- Requires security review and an inline comment explaining why it is necessary.
- The HTML must be sanitized server-side or with DOMPurify before rendering.
- Never pass user input directly.

```tsx
import DOMPurify from "dompurify";

function SanitizedContent({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, { ALLOWED_TAGS: ["b", "i", "a", "p"] });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

---

## Content Security Policy

Configure CSP headers on the server or CDN. A minimal strict policy:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

- Do not use `'unsafe-eval'`. If a library requires it, find an alternative.
- `'unsafe-inline'` for styles is acceptable with CSS Modules; prefer a nonce-based
  approach if the infrastructure supports it.
- `frame-ancestors 'none'` prevents clickjacking.

---

## Secrets and Environment Variables

- **Vite exposes all `VITE_` variables to the client bundle.** They are not secret.
- Never store API keys, database credentials, or tokens in `VITE_` variables.
- Use server-side proxies or BFF (Backend For Frontend) patterns to keep secrets
  on the server.

```
# .env -- safe: only VITE_ vars are bundled
VITE_API_BASE_URL=https://api.example.com   # OK: public URL
DATABASE_URL=postgres://...                   # OK: not exposed to client
VITE_SECRET_KEY=abc123                        # WRONG: exposed to anyone
```

---

## Authentication and Token Handling

- Store authentication tokens in `httpOnly`, `Secure`, `SameSite=Strict` cookies.
- Never store tokens in `localStorage` or `sessionStorage` -- both are accessible
  to XSS attacks.
- Short-lived access tokens + server-side refresh tokens.
- Log out: clear the cookie server-side and invalidate the session.

---

## Dependency Security

- Run `pnpm audit` in CI. Critical and high severity vulnerabilities fail the build.
- Pin exact dependency versions in `pnpm-lock.yaml` (committed to the repo).
- Review new dependencies before adding: check download count, maintenance
  activity, and known vulnerabilities.
- Limit the dependency tree. Fewer dependencies = smaller attack surface.

---

## URL and Navigation Safety

- Validate all URLs before rendering as `href`. Reject `javascript:` schemes.
- Use `rel="noopener noreferrer"` on external links with `target="_blank"`.

```tsx
function SafeLink({ href, children }: { href: string; children: React.ReactNode }) {
  const isSafe = /^https?:\/\//.test(href);
  if (!isSafe) return <span>{children}</span>;
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}
```

---

## Do / Don't

### Do

- Trust React's default escaping for dynamic content.
- Sanitize with DOMPurify if you must render raw HTML.
- Enforce a strict CSP header on every environment.
- Store tokens in `httpOnly` cookies.
- Run `pnpm audit` in CI and treat high/critical findings as blockers.
- Validate and sanitize all user input on the server, regardless of client validation.

### Don't

- Don't use `dangerouslySetInnerHTML` without DOMPurify and a security review.
- Don't store secrets in `VITE_` environment variables.
- Don't store auth tokens in `localStorage` or `sessionStorage`.
- Don't use `eval()`, `new Function()`, or `'unsafe-eval'` in CSP.
- Don't trust client-side validation alone -- always validate on the server.
- Don't allow `javascript:` URLs in `href` attributes.

---

## Common Pitfalls

1. **Assuming React prevents all XSS.** React escapes JSX expressions but
   `dangerouslySetInnerHTML`, `href="javascript:..."`, and server-rendered
   HTML are all escape hatches that bypass protection.
2. **Leaking secrets through `VITE_` variables.** Everything prefixed with
   `VITE_` is embedded in the client bundle and visible to anyone.
3. **Storing tokens in localStorage.** Any XSS vulnerability gives an attacker
   full access to the token. `httpOnly` cookies are not accessible to JavaScript.
4. **Ignoring dependency vulnerabilities.** A single compromised transitive
   dependency can inject malicious code. Audit regularly.
5. **Missing CSP headers.** Without CSP, an XSS vulnerability can load and
   execute arbitrary external scripts.

---

## Checklist

Before deploying any React application:

- [ ] No `dangerouslySetInnerHTML` without DOMPurify sanitization and code review
- [ ] CSP headers configured and tested (no `unsafe-eval`)
- [ ] No secrets in `VITE_` environment variables
- [ ] Auth tokens stored in `httpOnly` / `Secure` / `SameSite=Strict` cookies
- [ ] `pnpm audit` passes with no critical or high vulnerabilities
- [ ] External links use `rel="noopener noreferrer"`
- [ ] No `javascript:` URLs accepted in `href` attributes
- [ ] Server-side validation enforced for all user input
- [ ] Dependency lockfile committed and reviewed for unexpected changes
- [ ] Security review completed for any new third-party dependencies
