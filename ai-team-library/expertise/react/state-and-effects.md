# React State and Effects

State management and side-effect patterns for React applications. The goal is
predictable data flow: state lives as close to where it is used as possible,
effects are minimal and focused, and server state is delegated to a purpose-built
cache.

---

## Defaults

- **Local state:** `useState` for component-scoped values.
- **Derived state:** Compute during render. Do not store computed values in state.
- **Server state:** TanStack Query (React Query) for fetching, caching, and synchronization.
- **Client global state:** Zustand when Context is insufficient.
- **Side effects:** `useEffect` only for synchronization with external systems.
- **Forms:** React Hook Form or native controlled inputs. No two-way binding libraries.

### Alternatives

| Default            | Alternative      | When to consider                         |
|--------------------|------------------|------------------------------------------|
| TanStack Query     | SWR              | Simpler feature set is sufficient        |
| Zustand            | Jotai            | Prefer atomic state model                |
| Zustand            | Redux Toolkit    | Existing Redux codebase, migration not worth it |
| React Hook Form    | Formik           | Already in use; migration not justified  |

---

## State Hierarchy

Use the simplest option that solves the problem. Escalate only when necessary.

```
1. Local state       (useState)           -- single component
2. Derived state     (computed in render)  -- value computable from other state
3. Lifted state      (prop drilling)       -- shared by siblings
4. Context           (useContext)          -- global, low-frequency (theme, auth)
5. Server cache      (TanStack Query)     -- data from the API
6. Client store      (Zustand)            -- complex cross-feature client state
```

---

## Local and Derived State

```tsx
import { useState } from "react";

function ProductFilter({ products }: { products: Product[] }) {
  const [query, setQuery] = useState("");

  // Good: derived state computed during render, not stored in useState
  const filtered = products.filter((p) =>
    p.name.toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Filter products"
      />
      <ul>
        {filtered.map((p) => (
          <li key={p.id}>{p.name}</li>
        ))}
      </ul>
    </>
  );
}
```

**Anti-pattern: syncing derived state with useEffect.**

```tsx
// Bad: storing derived state and syncing with useEffect
const [filtered, setFiltered] = useState(products);

useEffect(() => {
  setFiltered(products.filter((p) => p.name.includes(query)));
}, [products, query]);
// This causes an unnecessary re-render and creates sync bugs.
```

---

## Server State with TanStack Query

TanStack Query owns all data fetching, caching, background refresh, and error
handling for server data.

```tsx
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchOrders, createOrder } from "./api";

function OrderList() {
  const { data: orders, isLoading, error } = useQuery({
    queryKey: ["orders"],
    queryFn: fetchOrders,
    staleTime: 30_000, // consider fresh for 30 seconds
  });

  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorBanner error={error} />;

  return (
    <>
      <button onClick={() => createMutation.mutate({ item: "widget" })}>
        New Order
      </button>
      <ul>
        {orders.map((o) => (
          <li key={o.id}>{o.item}</li>
        ))}
      </ul>
    </>
  );
}
```

**Rules:**

- Never use `useEffect` + `fetch` for data loading. TanStack Query handles
  loading, error, caching, refetching, and race conditions.
- Define query keys as constants or with a factory to avoid typos.
- Set `staleTime` per query. The default (0) causes a refetch on every mount.
- Use `useMutation` + `invalidateQueries` for write operations.

---

## Client State with Zustand

Use Zustand when multiple features share client-only state that does not come
from the server and Context would cause excessive re-renders.

```tsx
// stores/useNotificationStore.ts
import { create } from "zustand";

type Notification = { id: string; message: string; type: "info" | "error" };

type NotificationStore = {
  notifications: Notification[];
  add: (n: Omit<Notification, "id">) => void;
  dismiss: (id: string) => void;
};

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  add: (n) =>
    set((s) => ({
      notifications: [...s.notifications, { ...n, id: crypto.randomUUID() }],
    })),
  dismiss: (id) =>
    set((s) => ({
      notifications: s.notifications.filter((n) => n.id !== id),
    })),
}));
```

- Keep stores small and focused. One store per domain concern.
- Use selectors to subscribe to only the slice of state a component needs.
- Do not put server data in Zustand -- that belongs in TanStack Query.

---

## Effects: Rules and Patterns

`useEffect` is for synchronizing with external systems (DOM APIs, timers,
subscriptions, browser APIs). It is not for data fetching or derived state.

**Legitimate uses:**

- Subscribing to a WebSocket or EventSource.
- Integrating with a non-React DOM library (e.g., D3, a map widget).
- Setting `document.title`.
- Registering/cleaning up event listeners on `window` or `document`.

**Always return a cleanup function when the effect creates a subscription.**

```tsx
useEffect(() => {
  const controller = new AbortController();

  const eventSource = new EventSource("/api/events");
  eventSource.onmessage = (e) => handleEvent(JSON.parse(e.data));

  return () => {
    eventSource.close();
    controller.abort();
  };
}, []);
```

---

## Do / Don't

### Do

- Derive values during render instead of storing them in state.
- Use TanStack Query for all server data -- fetching, caching, and mutations.
- Keep `useEffect` dependency arrays honest. Fix the dependency, never suppress the lint.
- Return cleanup functions from effects that create subscriptions or timers.
- Use Zustand selectors to avoid unnecessary re-renders.

### Don't

- Don't fetch data in `useEffect`. Use TanStack Query.
- Don't store values in state that can be computed from props or other state.
- Don't use `useEffect` to "sync" two pieces of state. Restructure the state instead.
- Don't put server data in Zustand. TanStack Query is the server cache.
- Don't ignore the exhaustive-deps lint rule.
- Don't use `useRef` to hold mutable state that should trigger re-renders.

---

## Common Pitfalls

1. **useEffect for derived state.** Storing `filteredList` in state and syncing
   it with `useEffect` when `items` or `query` changes. Compute it during render.
2. **Missing cleanup.** An effect subscribes to a WebSocket but never closes it.
   This leaks connections and causes updates on unmounted components.
3. **Stale closures.** An effect captures an old value because a dependency is
   missing. Trust the exhaustive-deps rule.
4. **Data fetching in useEffect.** Hand-rolled fetch logic misses caching, race
   conditions, background refresh, and error retry. Use TanStack Query.
5. **Overusing global state.** Reaching for Zustand or Context when `useState`
   in a parent component would suffice. Start local, escalate only when needed.

---

## Checklist

Before merging state or effect changes:

- [ ] State lives at the lowest necessary level (local before global)
- [ ] No derived values stored in `useState`
- [ ] Server data uses TanStack Query with explicit `staleTime`
- [ ] Query keys follow the project naming convention
- [ ] `useMutation` invalidates relevant queries on success
- [ ] `useEffect` is used only for external system synchronization
- [ ] Every `useEffect` with subscriptions returns a cleanup function
- [ ] Dependency arrays are complete and correct (no lint suppressions)
- [ ] Zustand stores are focused on a single domain concern
- [ ] Components subscribe to the narrowest possible state slice
