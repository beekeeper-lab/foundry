# Next.js Deployment

Deployment posture for App Router applications. The convention is
**platform-neutral by default**: the app must build with `next build` and run
correctly under `next start` (or the standalone output) on any Node host.
Managed platforms are an optimization you opt into, not a dependency you
accidentally acquire.

---

## 1. Self-Hosted vs Managed

- **Decide early and record it in an ADR.** The choice affects ISR
  infrastructure, image optimization, and how far you can lean on
  platform-specific features.
- **Managed (Vercel and similar):** ISR, image optimization, edge middleware,
  and cache distribution work out of the box. The risk is silent lock-in:
  platform-only APIs and behaviors creep in unnoticed. Any platform-exclusive
  feature gets an explicit ADR.
- **Self-hosted (container/Node):** everything works, but you own the pieces
  managed platforms hide:
  - Use `output: "standalone"` in `next.config.ts` for containers -- it emits
    a minimal server with traced dependencies instead of shipping all of
    `node_modules`.
  - Install `sharp` in the production image, or `next/image` optimization
    degrades.
  - **Multi-instance ISR/data cache is not shared by default** -- each
    instance keeps its own filesystem cache, so revalidations diverge across
    replicas. For more than one instance, configure a custom
    `cacheHandler` backed by shared storage (e.g. Redis), or restrict
    yourself to fully static + fully dynamic routes.
  - Put a CDN/reverse proxy in front and respect the `Cache-Control` headers
    Next.js emits; do not invent your own header scheme on top.
- Either way: the app runs as a **single stateless service**. No writing to
  local disk at request time (except the framework's own cache directory);
  state lives in the database or object storage.

## 2. Environment Variable Handling

- **Two classes, one rule:** `NEXT_PUBLIC_*` variables are inlined into the
  client bundle **at build time** and are public forever; everything else is
  server-only and read at runtime. Never put secrets in `NEXT_PUBLIC_*`.
- Because `NEXT_PUBLIC_*` values are baked at build time, a
  build-once/deploy-many pipeline cannot vary them per environment. Either
  build per environment, or (preferred) keep client-visible config out of env
  vars entirely -- serve it from a server component or route handler.
- Validate the environment at startup: a schema (e.g. zod) over
  `process.env` in a `lib/env.ts` module that everything else imports. Fail
  the boot loudly on a missing variable instead of failing a request at 3am.
  Guard the module with `import "server-only"`.
- `.env.local` is for local development only and is gitignored. `.env` /
  `.env.production` committed to the repo may contain **non-secret defaults
  only**. Real secrets come from the platform's secret store or CI-injected
  environment, per the cross-cutting no-secrets-in-code rule.
- Document every variable in `.env.example`, including the `NEXT_PUBLIC_`
  distinction, so the deploy target's checklist is greppable.

## 3. Middleware Constraints

`middleware.ts` runs on every matched request, historically in an
edge-runtime sandbox. Treat it as a constrained, hot code path:

- **Keep it thin.** Appropriate work: redirects, rewrites, locale routing,
  setting/reading cookies and headers, coarse auth *gating* (is there a
  session token at all?).
- **Do not** do database queries, heavy JSON parsing, or full session
  validation in middleware. It runs on every request including assets you
  forgot to exclude, and the runtime restricts Node APIs (no arbitrary
  `fs`/`net`; assume Web-standard APIs only, unless the project has
  explicitly adopted the Node middleware runtime -- record that in an ADR).
- Middleware auth is a **convenience redirect, not a security boundary**.
  Real authorization happens in the layout/page/action that owns the data --
  middleware can be bypassed by misconfigured matchers and has been the
  subject of real-world bypass CVEs. Defense in depth: check again at the
  data layer.
- Always define a `matcher` in `config`, excluding `_next/static`,
  `_next/image`, and public assets. Middleware silently running on every
  static asset is a common self-inflicted latency tax.
- Middleware cannot produce fully custom heavy responses cheaply; if you are
  rendering in middleware, the logic belongs in a route.

## 4. Build and Release Discipline

- CI runs, in order: lint → typecheck → unit tests → `next build` → route
  tests against `next start` (see `testing.md`). A build that emits
  unexpected dynamic routes fails review (see `conventions.md` §5).
- Pin the Node major version (`engines` + `.nvmrc`/container base image) and
  the package manager via lockfile; builds must be reproducible.
- Run database migrations as a separate deploy step, never at server boot --
  multiple instances booting concurrently must not race migrations.
- Health check endpoint (`app/api/health/route.ts`) returns cheap liveness
  (no DB call storms); readiness checks may verify dependencies.
- After deploy, verify caching behavior in the real topology (CDN + replicas)
  for one ISR route and one dynamic route -- cache bugs are topology bugs and
  do not reproduce locally.

---

## Common Failure Modes

1. **Stale ISR on one replica.** Symptom: refreshing alternates between old
   and new content. Cause: per-instance filesystem cache without a shared
   `cacheHandler`. Fix per §1.
2. **"Works in staging, wrong API URL in prod."** A `NEXT_PUBLIC_*` value was
   baked at build time by a build-once pipeline. Fix per §2.
3. **Middleware latency on every image.** Missing `matcher` exclusions;
   middleware executing for `_next/static` and `_next/image`. Fix per §3.
4. **Blurry or original-size images self-hosted.** `sharp` missing from the
   production image. Fix per §1.

---

## Checklist

- [ ] Deployment target chosen and recorded in an ADR; platform-exclusive
      features individually ADR'd
- [ ] Self-hosted: `output: "standalone"`, `sharp` installed, shared
      `cacheHandler` if running more than one instance
- [ ] No secrets in `NEXT_PUBLIC_*`; build-time inlining implications
      understood in the release pipeline
- [ ] `lib/env.ts` validates `process.env` at startup and is `server-only`
- [ ] `.env.example` documents every variable; `.env.local` gitignored
- [ ] Middleware is thin, has an explicit asset-excluding `matcher`, and is
      not the sole authorization check
- [ ] CI gate: lint, typecheck, tests, `next build`, route tests against a
      production build
- [ ] Node version pinned; migrations run as a discrete deploy step
- [ ] Post-deploy cache verification on one ISR and one dynamic route
