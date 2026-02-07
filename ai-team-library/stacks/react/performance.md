# React Performance

Performance in React is about shipping less code, rendering less often, and
keeping the main thread unblocked. Measure before optimizing -- premature
optimization adds complexity without measurable benefit.

---

## Defaults

- **Bundle tool:** Vite with code splitting enabled by default.
- **Bundle analysis:** `vite-plugin-visualizer` run before every release.
- **Profiling:** React DevTools Profiler for render analysis.
- **Lazy loading:** `React.lazy` + `Suspense` for all route-level components.
- **Image optimization:** Responsive `srcSet`, `loading="lazy"`, WebP/AVIF.
- **Performance budget:** No single third-party dependency > 50KB gzipped without an ADR.

### Alternatives

| Default                    | Alternative              | When to consider                    |
|----------------------------|--------------------------|-------------------------------------|
| `vite-plugin-visualizer`   | `webpack-bundle-analyzer`| Webpack-based project               |
| React DevTools Profiler    | `why-did-you-render`     | Need automated re-render detection  |
| `React.lazy`               | `@loadable/component`    | SSR with code splitting             |

---

## Code Splitting and Lazy Loading

Split the bundle at route boundaries. The initial load should include only the
app shell and the first route.

```tsx
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

const Dashboard = lazy(() => import("./features/dashboard/DashboardPage"));
const Settings = lazy(() => import("./features/settings/SettingsPage"));
const OrderDetail = lazy(() => import("./features/orders/OrderDetailPage"));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
      </Routes>
    </Suspense>
  );
}
```

**Rules:**

- Every route-level component uses `React.lazy`.
- Use a meaningful fallback (`<PageSkeleton />`) instead of a spinner when possible.
- Heavy feature-internal components (rich text editors, chart libraries) can also
  be lazy-loaded within a feature.

---

## Memoization

Memoization is a tool, not a default. Incorrect or excessive memoization adds
memory overhead and hides structural problems.

### useMemo -- Expensive Computations

```tsx
import { useMemo } from "react";

function ReportTable({ transactions }: { transactions: Transaction[] }) {
  // Good: expensive filtering/sorting computed once per input change
  const summary = useMemo(
    () => computeFinancialSummary(transactions),
    [transactions],
  );

  return <Table data={summary} />;
}
```

### React.memo -- Preventing Child Re-renders

```tsx
import { memo } from "react";

// Good: pure presentational component that receives stable props
const ExpensiveChart = memo(function ExpensiveChart({ data }: ChartProps) {
  return <canvas>{/* complex D3 rendering */}</canvas>;
});
```

**When NOT to memoize:**

- The component is cheap to render (simple text, a few DOM elements).
- Props change on every render anyway (new object/array references).
- You have not measured a performance problem.

---

## Avoiding Unnecessary Re-renders

The most effective optimization is structural: keep state close to where it is
used so that state changes affect the smallest possible subtree.

```tsx
// Bad: entire page re-renders when the search query changes
function Page() {
  const [query, setQuery] = useState("");
  return (
    <div>
      <SearchBox query={query} onChange={setQuery} />
      <ExpensiveHeader />       {/* re-renders unnecessarily */}
      <ExpensiveSidebar />      {/* re-renders unnecessarily */}
      <SearchResults query={query} />
    </div>
  );
}

// Good: extract the stateful part into its own component
function Page() {
  return (
    <div>
      <SearchSection />         {/* state is scoped here */}
      <ExpensiveHeader />       {/* not affected by search state */}
      <ExpensiveSidebar />      {/* not affected by search state */}
    </div>
  );
}

function SearchSection() {
  const [query, setQuery] = useState("");
  return (
    <>
      <SearchBox query={query} onChange={setQuery} />
      <SearchResults query={query} />
    </>
  );
}
```

---

## List Virtualization

For lists with hundreds or thousands of items, render only the visible rows.

```tsx
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef } from "react";

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
  });

  return (
    <div ref={parentRef} style={{ height: "400px", overflow: "auto" }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: "relative" }}>
        {virtualizer.getVirtualItems().map((vRow) => (
          <div
            key={vRow.key}
            style={{
              position: "absolute",
              top: 0,
              transform: `translateY(${vRow.start}px)`,
              height: `${vRow.size}px`,
              width: "100%",
            }}
          >
            {items[vRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

- Use `@tanstack/react-virtual` for virtualizing lists and grids.
- Consider virtualization when lists exceed ~100 items.

---

## Image Optimization

- Use responsive images with `srcSet` and `sizes`.
- Set `loading="lazy"` on below-the-fold images.
- Prefer WebP/AVIF formats with `<picture>` fallbacks.
- Set explicit `width` and `height` to prevent layout shift (CLS).

```tsx
<img
  src="/images/hero.webp"
  srcSet="/images/hero-400.webp 400w, /images/hero-800.webp 800w"
  sizes="(max-width: 600px) 400px, 800px"
  loading="lazy"
  width={800}
  height={450}
  alt="Product showcase"
/>
```

---

## Bundle Analysis

Run `vite-plugin-visualizer` before every release to identify oversized
dependencies.

```ts
// vite.config.ts
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  plugins: [
    react(),
    visualizer({ filename: "bundle-report.html", open: false }),
  ],
});
```

**Budget rules:**

- No single dependency > 50KB gzipped without an ADR.
- Total initial JS bundle < 200KB gzipped (app code + framework).
- Monitor bundle size in CI with `bundlesize` or equivalent.

---

## Do / Don't

### Do

- Measure with React DevTools Profiler and Lighthouse before optimizing.
- Lazy-load every route-level component with `React.lazy`.
- Keep state as close to its consumers as possible.
- Virtualize long lists (100+ items).
- Set explicit image dimensions to prevent layout shift.
- Run bundle analysis before every release.

### Don't

- Don't wrap every component in `React.memo`. Measure first.
- Don't create new objects or arrays in JSX props on every render if the child is memoized.
- Don't use `useMemo` for trivial computations (string concatenation, simple filters on small arrays).
- Don't load the entire icon library when you need five icons -- use tree-shakeable imports.
- Don't import heavy libraries (moment.js, lodash full) when smaller alternatives exist (date-fns, lodash-es with cherry-picking).

---

## Common Pitfalls

1. **Memoizing everything.** `useMemo` and `React.memo` have overhead (memory
   for cached values, shallow comparisons). Only memoize when profiling shows
   a measurable problem.
2. **Unstable references defeating memo.** Passing `style={{ color: "red" }}`
   as a prop creates a new object every render, making `React.memo` useless.
   Hoist the object or use `useMemo`.
3. **Loading the entire bundle upfront.** Not using `React.lazy` means every
   route's code is in the initial bundle, even if the user never visits it.
4. **Giant context providers.** A single context with many values causes every
   consumer to re-render when any value changes. Split into focused contexts.
5. **Layout shift from images.** Images without explicit `width`/`height` cause
   content to jump as they load, hurting Cumulative Layout Shift (CLS) scores.

---

## Checklist

Before merging performance-related changes:

- [ ] Route-level components are lazy-loaded with `React.lazy` + `Suspense`
- [ ] State is scoped to the smallest necessary subtree
- [ ] `useMemo` / `React.memo` used only where profiling shows a benefit
- [ ] Long lists (100+ items) use virtualization
- [ ] Images have explicit `width`, `height`, `loading="lazy"`, and responsive `srcSet`
- [ ] Bundle analysis run and no dependency exceeds 50KB gzipped without ADR
- [ ] Initial JS bundle < 200KB gzipped
- [ ] No full-library imports where tree-shakeable alternatives exist
- [ ] React DevTools Profiler shows no unnecessary re-renders on critical paths
- [ ] Lighthouse Performance score >= 90 on representative pages
