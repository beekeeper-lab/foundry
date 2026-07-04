# Vue Architecture

Structural conventions for Vue 3 applications: how to organize code as the
app grows, how to layer composables, and when server-side rendering or Nuxt
is actually warranted. Companion to `conventions.md`.

---

## Feature Folders

Organize by feature, not by file type. Type-based folders (`components/`,
`composables/`, `stores/` at the top level) scale badly: every feature change
touches four distant directories.

```
src/
  app/                    # App shell: router, plugin setup, global styles
    router.ts
    main.ts
  shared/                 # Genuinely cross-feature code
    components/           # Design-system-ish primitives (BaseButton, AppModal)
    composables/          # useDebounce, useLocalStorage, ...
    api/                  # HTTP client setup, interceptors
  features/
    orders/
      components/         # Feature-private components
      composables/        # useOrderSearch, useOrderTotals
      stores/             # orders store(s)
      api.ts              # Feature's API calls, typed request/response
      types.ts
      index.ts            # Public surface of the feature
    auth/
      ...
  views/                  # Route targets; thin wiring of features to routes
```

**Rules:**

- A feature's internals are private. Other features import only from its
  `index.ts`. Enforce with an ESLint import-boundary rule if the team is
  larger than two or three people.
- `shared/` is for code with **three or more** consumers. Two features
  sharing something is a coincidence; three is an abstraction.
- Views stay thin: resolve route params, pick feature components, own
  page-level loading/error states. Business logic lives in the feature.
- Cross-feature communication goes through Pinia stores or explicit
  function calls on a feature's public surface — never deep imports.

---

## Composable Layering

Composables are the primary unit of logic reuse. Keep three layers distinct:

1. **Utility composables** (`shared/composables/`): framework-adjacent,
   domain-free — `useDebouncedRef`, `useEventListener`, `useMediaQuery`.
   These are candidates for replacement by VueUse; check there before
   writing your own.
2. **Data composables** (feature-level): wrap API access and expose
   `{ data, error, isLoading, refresh }`-shaped state. If the project uses
   a query library (Pinia Colada, TanStack Query), this layer is thin
   wrappers around it with typed keys.
3. **Feature/workflow composables**: orchestrate the above plus stores into
   one screen-sized concern — `useCheckoutFlow`, `useOrderFilters`.

**Rules:**

- Dependencies point downward only: workflow → data → utility. A utility
  composable must never import a store.
- One composable, one concern. When `useOrders` grows pagination, filtering,
  and selection, split it; compose the pieces in the workflow layer.
- Components consume composables; composables do not know which component
  hosts them. No DOM selectors, no template refs passed implicitly — accept
  refs as arguments.
- Prefer composables over mixins (never), over renderless components
  (rarely needed now), and over utility classes with reactive members.

---

## State Placement

Decision ladder — use the lowest rung that works:

1. **Local `ref` in the component** — default.
2. **Lifted to the parent / props+emits** — two sibling components share it.
3. **Composable with shared instance or provide/inject** — a subtree shares it.
4. **Pinia store** — shared across routes or unrelated trees, or must
   survive navigation.
5. **URL (route query/params)** — state the user should be able to
   bookmark, share, or restore on reload: filters, tabs, pagination.

Server cache (fetched entities) is its own category: keep it in the data
composable layer or a query library, keyed and invalidated there. Copying
server data into Pinia by hand creates two sources of truth and stale bugs.

---

## When Nuxt Is (and Isn't) Warranted

Choose based on rendering and infrastructure needs, not fashion.

**Plain Vue + Vite (SPA) is the default when:**

- The app sits behind a login (dashboards, admin tools, internal apps) —
  SEO is irrelevant and first-paint SSR buys little.
- You deploy as static assets to a CDN and want the simplest possible
  operational model (no Node server to run, patch, and scale).
- The team is small and the app is one of several services; fewer moving
  parts wins.

**Nuxt is warranted when:**

- Public content where SEO and social-share previews matter (marketing,
  e-commerce, docs, blogs) — SSR/SSG is the point, and hand-rolling Vue SSR
  is a project in itself.
- You want file-based routing, layouts, data-fetching conventions
  (`useFetch`/`useAsyncData`), and server routes (`server/api/`) as an
  integrated, documented whole rather than assembling them.
- Mixed rendering per route (static marketing pages + dynamic app) via
  route rules.

**Anti-signals:** adopting Nuxt "for structure" on an auth-walled SPA adds a
server runtime, hydration complexity, and a framework upgrade treadmill for
no user-visible benefit. Conversely, bolting SSR onto a mature SPA later is
far more expensive than starting with Nuxt — decide at project start.

---

## SSR Considerations

If you do render on the server (Nuxt or custom):

- **No shared mutable module state.** A module-level singleton (including a
  bare Pinia store instance created at import time) is shared across
  requests on the server and leaks one user's data to another. Create app,
  router, and Pinia instances per request; Nuxt does this for you.
- **Guard browser APIs.** `window`, `document`, `localStorage` do not exist
  on the server. Touch them only inside `onMounted`, event handlers, or
  behind an environment check (`import.meta.client` in Nuxt).
- **Hydration mismatches are bugs, not warnings.** Anything
  non-deterministic between server and client render — dates formatted in
  the user's locale, random IDs, feature flags resolved differently — must
  be deferred to client-only rendering (`<ClientOnly>`) or made
  deterministic (`useId()` for IDs).
- **Serialize state once.** Fetch on the server, transfer via the payload
  (Nuxt's `useAsyncData` handles this), and do not re-fetch on hydration.
- Side-effectful composables must be SSR-safe: register cleanup, no timers
  started at the module top level, no fetches outside the framework's
  data-fetching hooks.

---

## Checklist

- [ ] Code organized by feature; features expose an `index.ts` public surface
- [ ] `shared/` contains only code with 3+ consumers
- [ ] Views are thin route-wiring; business logic lives in features
- [ ] Composables layered utility → data → workflow, dependencies downward
- [ ] Server cache lives in the data layer, not hand-copied into Pinia
- [ ] Bookmarkable UI state (filters, tabs, pages) lives in the URL
- [ ] SPA-vs-Nuxt decision recorded in an ADR with the rendering rationale
- [ ] If SSR: no request-shared singletons, browser APIs guarded, zero
      hydration warnings in CI
