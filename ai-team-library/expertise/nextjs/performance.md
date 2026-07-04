# Next.js Performance

Next.js-specific performance discipline for App Router applications. Generic
React performance guidance (memoization, re-render hygiene, profiling) lives in
the `react` pack; this file covers what the framework adds: streaming, the
built-in asset optimizers, server/client bundle discipline, and cache
profiling.

---

## 1. Streaming and Suspense

The single biggest App Router performance lever is **not blocking the first
byte on your slowest data source**.

- Give every data-bearing route a `loading.tsx`, or better, wrap individual
  slow subtrees in `<Suspense>` so the static shell streams immediately and
  islands fill in as their data resolves.
- Structure pages as: fast shell (nav, headings, layout) renders
  synchronously; each independent data region gets its own Suspense boundary.
  One boundary around the whole page recreates the blocking behavior you were
  trying to avoid.
- Start fetches early and in parallel: kick off promises before awaiting
  (`const a = getA(); const b = getB(); await Promise.all([a, b])`), or pass
  promises down and resolve them with React's `use()` inside the Suspense
  boundary.
- Sequential awaits in a Server Component are a request waterfall. They are
  invisible in the browser network tab (it is all server time) -- find them in
  code review and server traces.
- Fallbacks must be layout-stable: skeletons sized like the real content, so
  streaming does not cause layout shift.

## 2. Image and Font Optimization

- Use `next/image` for all raster images. It provides sizing (CLS
  prevention), lazy loading, responsive `srcSet`, and format negotiation
  (WebP/AVIF) for free.
  - Always provide real `width`/`height` (or `fill` inside a sized
    container). Missing dimensions reintroduce layout shift.
  - Mark the LCP image (hero) with `priority`; everything below the fold
    stays lazy.
  - Remote images require `remotePatterns` in `next.config.ts` -- keep the
    allowlist tight; it is a security boundary, not just config.
  - Self-hosted deployments must have `sharp` installed or image
    optimization silently degrades (see `deployment.md`).
- Use `next/font` for all fonts. It self-hosts Google/local fonts at build
  time: zero external font requests, automatic `font-display` handling, and
  size-adjusted fallbacks that eliminate font-swap layout shift.
  - Load fonts once in the root layout and expose them as CSS variables.
  - Subset aggressively (`subsets: ["latin"]`); each extra subset is payload.

## 3. Bundle Discipline

Server Components changed the goal: most code should **never ship to the
client at all**.

- The bundle budget applies to client components and their imports. Moving a
  heavy dependency (markdown renderer, syntax highlighter, date library)
  behind the server boundary is usually cheaper than optimizing it.
- Audit what crosses the boundary: a `"use client"` file's entire import
  graph is client-side. One convenience import of a server util file can drag
  a large dependency into the bundle.
- Use `next/dynamic` (with `ssr: false` only when the component genuinely
  cannot render on the server) for heavy, below-the-fold, or
  interaction-gated client widgets: charts, editors, maps, modals.
- Run `@next/bundle-analyzer` before release. Budgets follow the `react`
  pack rule (no single dependency over 50KB gzipped without an ADR), applied
  to **client chunks** -- server-only weight is a build-time concern, not a
  user-facing one.
- Prefer `optimizePackageImports`-friendly imports (named, specific) for icon
  and component libraries; avoid barrel-file imports that defeat tree shaking.

## 4. Cache Profiling and Verification

Caching claims are verified, not assumed.

- **Build time:** read the `next build` route table. Each route is marked
  static, dynamic, or partially prerendered. Diff this against intent on
  every PR that touches data fetching -- an unexpectedly-dynamic route is a
  performance regression.
- **Runtime:** in development, use the fetch logging option
  (`logging.fetches.fullUrl` in `next.config.ts`) to see per-request cache
  hits/misses/skips for every fetch.
- Measure **TTFB per route** in production. Dynamic routes pay server render
  cost on every request; if a dynamic route's data is actually shared across
  users, move it to tag-based ISR and let revalidation do the work.
- Watch revalidation behavior: `revalidateTag` invalidates on the *next*
  request (stale-while-revalidate semantics vary by version). Do not build
  UX that assumes instantaneous global cache purge.
- Router cache (client-side) can make stale data look like a server bug.
  When debugging staleness, distinguish the layers: browser cache → router
  cache → full route cache → data cache → origin.

## 5. Core Web Vitals Guardrails

- **LCP:** hero image via `next/image` + `priority`; no client-side data
  dependency for above-the-fold content on static/ISR routes.
- **CLS:** dimensioned images, `next/font` fallback adjustment, layout-stable
  Suspense skeletons.
- **INP:** keep hydration surface small (fewer/leaner client components);
  avoid synchronous work in top-level client providers.
- Track vitals with `useReportWebVitals` (or the platform's analytics) and
  gate releases on regressions for key routes, not global averages.

---

## Checklist

- [ ] Data-bearing routes stream: `loading.tsx` or granular `<Suspense>`
      boundaries around slow regions
- [ ] No sequential-await waterfalls in Server Components (parallelize or
      pass promises)
- [ ] All raster images use `next/image` with real dimensions; LCP image has
      `priority`
- [ ] Fonts via `next/font` in the root layout; no external font requests
- [ ] Heavy dependencies live server-side or behind `next/dynamic`
- [ ] Bundle analyzed before release; client-chunk budget respected
- [ ] `next build` route table matches rendering intent per route
- [ ] Dev fetch logging used to verify cache hit/miss expectations
- [ ] Web Vitals monitored per key route with regression gating
