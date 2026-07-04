# Next.js Testing

Testing strategy for App Router applications. Tooling and general philosophy
(Testing Library queries, behavior-over-implementation, e2e minimalism)
inherit from the `react` pack; this file covers what Next.js changes: async
Server Components do not fit the classic component-test harness, and the
interesting failures live at the route level.

---

## 1. The Layered Strategy

Server Components broke the assumption that everything is unit-testable with
a JSDOM render. Split coverage by layer instead of forcing one tool to do
everything:

| Layer | What | Tool |
|-------|------|------|
| Logic | Data layer, services, validation schemas, utils | Unit tests (Vitest/Jest) |
| Client components | Interactive leaves marked `"use client"` | Testing Library (per `react` pack) |
| Server Components + routes | Rendering, data flow, cache/auth behavior | Playwright against a running app |
| Server Actions | Parse → authorize → mutate → revalidate | Unit test the extracted logic + e2e the form flow |

The center of gravity moves **down** (more logic tests, because the
conventions push logic into a framework-free `lib/`) and **up** (more
route-level tests), with a thinner component-test middle than a SPA.

## 2. Testing Client Components

- Client components (`"use client"`) test exactly as the `react` pack
  prescribes: Testing Library, accessible queries, behavior assertions.
- Mock Next.js hooks at the module boundary when the component uses them:
  `useRouter`, `usePathname`, `useSearchParams` from `next/navigation`.
  Keep a shared test helper that provides a router mock so individual tests
  do not hand-roll it.
- `next/image` and `next/link` render fine in JSDOM; do not mock them unless
  a specific assertion requires it.
- If a client component is hard to test because it receives complex
  server-fetched props, that is a design smell -- the props contract should
  be plain serializable data you can construct in a test.

## 3. Server Component Testing Constraints

Know the constraint before choosing a tool:

- **Async Server Components cannot be reliably rendered by Testing Library in
  JSDOM.** `render(<AsyncPage />)` on an `async` component is not a supported
  pattern; treat any local workaround as throwaway.
- Consequences for design:
  - Keep Server Components thin: fetch, transform, delegate to presentational
    components. The presentational components (sync, prop-driven) are
    unit-testable; the data functions are unit-testable; the thin async glue
    is covered at the route level.
  - **Do not chase unit coverage of async Server Components.** A passing
    contrived unit test of one proves little; the real risks (cache posture,
    auth, streaming) only exist in a running app.
- Sync (non-async) Server Components without server-only imports can be
  rendered with Testing Library like any component -- that is fine.

## 4. Route-Level Testing with Playwright

When the project has Playwright (per the `react` pack default), route tests
are the primary safety net for server behavior:

- Run against a real build when verifying caching/rendering behavior
  (`next build && next start`); `next dev` differs materially (no full route
  cache, dev-only recompiles). CI route tests run against the production
  build.
- Cover per critical route:
  - The page renders with real (seeded) data -- assert on visible content,
    not implementation.
  - Streaming: fallback appears, then resolves (assert final state; assert
    fallback only where the skeleton is a product requirement).
  - Auth: unauthenticated access redirects; wrong-tenant access 404s/403s.
  - Mutations: submit the real form → assert the UI reflects the write
    (this exercises the Server Action *and* its revalidation in one test).
- Stub external third-party APIs at the network edge (route handler test
  doubles or a mock server); use a real database seeded per test run, per the
  `react` pack's e2e realism rule.
- Keep the suite small and journey-shaped. Route tests are the expensive
  tier; they exist to catch integration failures, not to re-prove component
  logic.

## 5. Testing Server Actions and Route Handlers

- Structure actions so the testable part is a plain function: the action
  parses/authorizes, then calls a service function in `lib/`. Unit test the
  service function and the validation schema directly.
- Direct invocation of a server action in a unit test works for pure
  parse/branch logic, but `revalidatePath`/`redirect`/`cookies` require
  mocking `next/cache` / `next/navigation` -- acceptable for edge-case
  matrices, but the happy path belongs in a Playwright form-submission test.
- Route handlers (`app/api/*/route.ts`) are functions taking a `Request`:
  unit test them by constructing `Request` objects and asserting on the
  `Response` -- status codes, error shapes, auth rejection. No server needed.

## 6. What Not to Do

- Don't mock `fetch` globally to force async Server Components through JSDOM.
  You end up testing your mocks.
- Don't assert on caching behavior from `next dev` runs.
- Don't write an e2e test per component state -- that matrix belongs in
  component/unit tests.
- Don't let route tests share mutable seed data; parallel workers will
  flake. Seed per test or per worker.

---

## Checklist

- [ ] Data layer and validation schemas have direct unit tests (no Next.js
      runtime needed)
- [ ] Client components tested per `react` pack, with shared
      `next/navigation` mocks
- [ ] Async Server Components kept thin; their presentational children are
      unit-tested, their behavior route-tested
- [ ] Playwright route tests exist for critical journeys: render, auth,
      streaming resolution, form mutation + revalidation
- [ ] Route tests in CI run against `next build && next start`, not dev mode
- [ ] Server Actions delegate to unit-tested service functions; happy path
      covered by a real form submission test
- [ ] Route handlers unit-tested via `Request`/`Response`
- [ ] External APIs stubbed; database real and seeded per test run
