---
id: nextjs
category: Frameworks
applies_to:
  - developer
  - tech-qa
  - architect
  - code-quality-reviewer
entry: true
last-reviewed: 2026-07
---

# Next.js Conventions

## Category
Frameworks

## Applies To

- developer
- tech-qa
- architect
- code-quality-reviewer

These conventions govern Next.js applications in the App Router era (Next.js 14+,
targeting 15.x behavior). They cover what is *specific to Next.js*: routing,
server/client component boundaries, data fetching and caching, server actions,
and rendering strategy. Generic React guidance -- component patterns, hooks,
state management, accessibility, TypeScript style -- is owned by the `react`
pack and is **not** repeated here. When the two packs appear to conflict, the
Next.js-specific rule wins inside `app/`; the React rule wins everywhere else.
Deviations require an ADR with justification.

---

## Defaults

| Concern              | Default                                              |
|----------------------|------------------------------------------------------|
| Router               | App Router (`app/`). Pages Router only for legacy migration, via ADR. |
| Component model      | Server Components by default; `"use client"` only where interaction demands it. |
| Language             | TypeScript strict mode (inherits `react` pack policy). |
| Data fetching        | `fetch`/data access in Server Components; explicit cache posture per call. |
| Caching              | Opt in deliberately. Assume dynamic; add caching where measured, never by accident. |
| Mutations            | Server Actions with validation at the boundary; `revalidatePath`/`revalidateTag` after writes. |
| Styling              | Per `react` pack (CSS Modules + tokens). Tailwind only via ADR. |
| Deployment           | Platform-neutral: build must pass `next build` and run under `next start` or `output: "standalone"`. No Vercel-only APIs without an ADR. |
| Testing              | See `testing.md` in this pack; tooling inherits the `react` pack.  |

---

## 1. Routing and Layouts

- All routes live in `app/`. Use the special files for their intended jobs:
  `page.tsx` (route UI), `layout.tsx` (shared shell, preserves state),
  `template.tsx` (remounts per navigation -- rare, justify in a comment),
  `loading.tsx` (route-level Suspense fallback), `error.tsx` (route-level
  error boundary, must be a client component), `not-found.tsx`.
- The root layout owns `<html>` and `<body>` and global providers. Nested
  layouts own section-scoped chrome only. Do not fetch per-request user data
  in a layout that wraps mostly-static pages -- it forces the whole subtree
  dynamic.
- Use **route groups** `(group)` to organize without affecting URLs, and
  **private folders** `_components/`, `_lib/` to co-locate non-route code
  inside `app/` without creating routes.
- Dynamic segments: `[id]` for single params, `[...slug]` only when the route
  genuinely has variable depth. Type params via the props of `page.tsx`; do
  not parse `window.location`.
- Every route with non-trivial data work gets a `loading.tsx` or an explicit
  `<Suspense>` boundary. A route that can fail gets an `error.tsx`.

## 2. Server vs Client Components

- **Server Components are the default.** Add `"use client"` only for state,
  effects, event handlers, browser APIs, or client-only libraries.
- Push `"use client"` to the **leaves**. Mark the interactive widget, not the
  page. A page-level `"use client"` is a review flag: it drags the entire
  subtree (and its dependencies) into the client bundle.
- Interleave by passing Server Components as `children`/props *into* client
  components -- a client component cannot `import` a server component.
- Server-only code (DB clients, secrets, heavy SDKs) is guarded with
  `import "server-only"` so accidental client imports fail at build time.
- Props crossing the server→client boundary must be serializable. No
  functions, class instances, or Dates-as-Dates without explicit conversion
  (Server Action references are the exception).
- Never read secrets in client components. Only `NEXT_PUBLIC_*` env vars
  exist in the browser; everything else is server-only by design.

## 3. Data Fetching and Caching Discipline

- Fetch in Server Components, as close to where data is used as possible.
  Duplicate `fetch` calls to the same URL are deduplicated per request; wrap
  non-fetch data access (ORM calls) in React `cache()` for the same effect.
- **State every cache decision explicitly.** Every `fetch` carries
  `{ cache: "no-store" }` or `{ next: { revalidate: N, tags: [...] } }` -- do
  not rely on remembered default behavior, which changed across major
  versions (uncached by default in the 15 era).
- Prefer **tag-based revalidation** (`next: { tags }` + `revalidateTag`) over
  time-based when you control the write path. Time-based (`revalidate: N`) is
  for third-party data you cannot invalidate.
- Do not fetch from your own API routes inside Server Components. Call the
  data layer (ORM/service function) directly; route handlers are for
  external/browser consumers.
- Client-side data (polling, infinite scroll, live updates) uses the `react`
  pack's server-state tooling against route handlers -- not `useEffect`+`fetch`.
- Know your dynamic triggers: `cookies()`, `headers()`, `searchParams`, and
  uncached fetches opt a route into dynamic rendering. Isolate them behind
  Suspense boundaries instead of letting one call de-optimize the whole page.

## 4. Server Actions and Mutations

- Mutations go through Server Actions (`"use server"`) invoked from `<form
  action={...}>` or transitions -- not hand-rolled `POST` route handlers,
  unless an external client needs the endpoint.
- **Treat every action as a public, unauthenticated HTTP endpoint.** Re-check
  auth and authorization *inside* the action. Validate all inputs with a
  schema (e.g. zod) at the top; never trust `FormData` shapes.
- After a successful write, call `revalidatePath`/`revalidateTag` (or
  `redirect`) so cached reads reflect the mutation. A mutation without an
  invalidation is a bug until proven otherwise.
- Return typed result objects (`{ ok: true } | { ok: false; errors }`) and
  surface them with `useActionState`; throw only for unexpected failures.
- Keep actions thin: parse → authorize → call service function → invalidate.
  Business logic lives in the service layer where it is unit-testable.

## 5. Rendering Strategy per Route

- Decide per route, and record non-obvious choices in the route's code:
  - **Static** (default for marketing/docs): no dynamic APIs, cached data.
  - **Static + ISR**: `revalidate`/tags for content that changes on publish.
  - **Dynamic**: per-user pages (dashboards, carts) -- accept the render cost,
    stream with Suspense so TTFB stays low.
  - **Partial**: static shell + Suspense-wrapped dynamic islands.
- `generateStaticParams` for known dynamic segments you want prebuilt.
- Verify intent with the `next build` output (route table shows
  static/dynamic per route). A route that unexpectedly flipped to dynamic is
  a regression -- find the trigger, do not shrug.
- Metadata via the Metadata API (`metadata` export / `generateMetadata`), not
  hand-rolled `<head>` tags.

## 6. Project Structure

```
project-root/
  app/                      # Routes only + route-scoped _components/, _lib/
    (marketing)/            # Route group: static/public pages
    (app)/                  # Route group: authenticated product
    api/                    # Route handlers for external/browser consumers
    layout.tsx
  components/               # Shared UI (per react pack: ui/, layout/)
  features/                 # Feature verticals (per react pack)
  lib/                      # Framework-free utilities, data layer, server-only services
  middleware.ts             # Edge middleware: keep it thin (see deployment.md)
  next.config.ts
```

- `app/` holds routing concerns; substantial components and logic live
  outside it in `features/`/`components/`/`lib/` per the `react` pack layout.
- The data layer in `lib/` is framework-free and `server-only` where it
  touches secrets, so it is testable without a running Next.js server.

---

## Do / Don't

**Do:**
- Default to Server Components; add `"use client"` at the leaves only.
- Annotate every fetch with an explicit cache posture.
- Validate and authorize inside every Server Action.
- Revalidate (path or tag) after every mutation.
- Wrap slow/dynamic subtrees in `<Suspense>` with meaningful fallbacks.
- Check the `next build` route table before merging routing/data changes.
- Use `import "server-only"` in modules that must never reach the client.

**Don't:**
- Don't put `"use client"` at the top of a page to "make errors go away."
- Don't fetch your own route handlers from Server Components.
- Don't rely on implicit caching defaults -- they differ across versions.
- Don't read `cookies()`/`headers()` in shared layouts casually; it makes the
  subtree dynamic.
- Don't expose secrets via `NEXT_PUBLIC_*` or client-imported server modules.
- Don't duplicate `react` pack guidance decisions locally -- defer to that pack.

---

## Common Pitfalls

1. **Client-component creep.** One `"use client"` high in the tree silently
   ships the whole subtree to the browser. Audit boundaries in review.
2. **Assumed caching.** Code written against Next 13/14 fetch-caches-by-default
   behavior breaks on 15-era defaults. Explicit posture per call avoids this.
3. **Unvalidated Server Actions.** Actions are network endpoints; skipping
   schema validation + auth inside them is an injection/IDOR waiting to happen.
4. **Mutation without revalidation.** The write succeeds but users see stale
   cached reads and file it as data loss.
5. **Accidental dynamic routes.** A stray `cookies()` call flips a static page
   to per-request rendering; latency and cost jump without any visible diff.
6. **Fetching own API routes server-side.** Adds an HTTP hop, loses types, and
   can deadlock in self-hosted single-process setups. Call the data layer.
7. **Non-serializable props across the boundary.** Passing a Date, Map, or
   function from server to client fails at runtime, not compile time.

---

## Checklist

- [ ] App Router (`app/`) only; no new Pages Router code
- [ ] `"use client"` only at interactive leaves; no page-level client pages
      without justification
- [ ] Every `fetch`/data call has an explicit cache/revalidate posture
- [ ] Server Actions validate inputs (schema) and re-check authorization
- [ ] Every mutation revalidates affected paths/tags or redirects
- [ ] `loading.tsx`/`Suspense` and `error.tsx` on data-bearing routes
- [ ] `server-only` guard on secret-touching modules; no secrets in
      `NEXT_PUBLIC_*`
- [ ] `next build` route table reviewed: each route's static/dynamic status
      is intentional
- [ ] Structure follows §6; generic React concerns follow the `react` pack
- [ ] Deep dives consulted where relevant: `performance.md`, `testing.md`,
      `deployment.md`
