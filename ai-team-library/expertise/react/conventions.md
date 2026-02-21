# React Stack Conventions

These conventions apply to all React projects on this team. They are opinionated
by design -- consistency across the codebase matters more than individual
preference. Deviations require an ADR with justification.

---

## Defaults

- **Framework:** React 18+ with functional components only.
- **Build tool:** Vite with SWC for transforms.
- **Language:** TypeScript in strict mode. No `.js`/`.jsx` files in `src/`.
- **Styling:** CSS Modules + design tokens. Tailwind only via ADR.
- **State:** Local state first, TanStack Query for server state, Zustand for complex client state.
- **Testing:** Vitest + Testing Library (unit/component), Playwright (e2e).
- **Linting:** ESLint with `eslint-plugin-react-hooks` and `eslint-plugin-jsx-a11y`.
- **Formatting:** Prettier with project-level config committed to the repo.
- **Package manager:** pnpm (lockfile committed).

---

## 1. Project Structure

```
project-root/
  src/
    app/                    # App shell: routing, providers, global layout
      routes/               # Route-level components (one dir per route)
    features/               # Feature modules (self-contained verticals)
      <feature-name>/
        components/         # Components scoped to this feature
        hooks/              # Hooks scoped to this feature
        api.ts              # API calls for this feature
        types.ts            # Types scoped to this feature
        index.ts            # Public API of the feature
    components/             # Shared, reusable UI components
      ui/                   # Primitives (Button, Input, Modal, etc.)
      layout/               # Layout components (Sidebar, Header, etc.)
    hooks/                  # Shared custom hooks
    lib/                    # Utilities, constants, helpers (no React)
    types/                  # Shared TypeScript types and interfaces
  tests/
    e2e/                    # End-to-end tests (Playwright)
  public/                   # Static assets
  index.html
  tsconfig.json
  vite.config.ts
```

**Rules:**
- Organize by feature, not by file type. `features/checkout/` over
  `components/CheckoutForm` + `hooks/useCheckout` + `api/checkout`.
- A feature's `index.ts` is its public API. Other features import from the
  index, never from internal paths.
- Shared components live in `components/` only when used by two or more features.
  Do not preemptively generalize.

---

## 2. Component Patterns

### Functional Components Only

Class components are not used. All components are function components.

```tsx
// Good
export function OrderSummary({ orderId }: OrderSummaryProps) {
  // ...
}

// Also acceptable: arrow function for simple components
export const Badge = ({ label }: BadgeProps) => (
  <span className="badge">{label}</span>
);
```

### Component File Convention

One component per file. The file name matches the component name in PascalCase.

```
Button.tsx         -> export function Button(...)
OrderSummary.tsx   -> export function OrderSummary(...)
```

Co-locate the component's types, styles, and tests:

```
OrderSummary/
  OrderSummary.tsx
  OrderSummary.test.tsx
  OrderSummary.module.css   (if using CSS modules)
  types.ts                  (if types are complex)
```

### Props

- Define props as a named type (not inline), suffixed with `Props`.
- Use destructuring in the function signature.
- Default values go in the destructuring, not `defaultProps`.

```tsx
type ButtonProps = {
  variant: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  children: React.ReactNode;
  onClick: () => void;
};

export function Button({
  variant,
  size = "md",
  disabled = false,
  children,
  onClick,
}: ButtonProps) {
  // ...
}
```

---

## 3. Hooks

- Prefix custom hooks with `use`.
- Extract logic into custom hooks when a component exceeds ~50 lines of
  non-JSX logic, or when logic is reused.
- Hooks must not have side effects beyond what React expects (`useEffect`,
  `useMemo`, etc.). A hook named `useOrderData` fetches data; it does not
  also submit forms.
- Keep dependency arrays explicit and correct. Never use `// eslint-disable`
  to suppress exhaustive-deps warnings -- fix the dependency or restructure.

---

## 4. State Management

**Hierarchy (use the simplest option that works):**

1. **Local state** (`useState`) -- default for component-scoped state.
2. **Derived state** -- compute from existing state/props. Do not store
   computed values in state.
3. **Lifted state** -- share between siblings by lifting to the nearest common
   parent.
4. **Context** (`useContext`) -- for genuinely global, low-frequency state
   (theme, auth, locale). Not for high-frequency updates.
5. **External store** (Zustand or TanStack Query) -- for server cache or
   complex client state that multiple features need.

**Rules:**
- Do not reach for a global store before exhausting local and lifted state.
- TanStack Query (React Query) is the default for server state (fetching,
  caching, synchronization). Do not hand-roll fetch-in-useEffect patterns.
- Zustand is the default for client-only global state if Context is
  insufficient. Redux is not used unless the project already has it.

---

## 5. Styling

**Approach: CSS Modules + design tokens.**

- Use CSS Modules (`.module.css`) for component-scoped styles.
- Shared design tokens (colors, spacing, typography) live in
  `src/lib/tokens.css` as CSS custom properties.
- Utility classes are acceptable from Tailwind only if the team has adopted it
  via ADR. Do not mix Tailwind and CSS Modules in the same project.
- No inline styles except for truly dynamic values (e.g., calculated widths).
- No CSS-in-JS libraries (styled-components, Emotion) -- they add runtime cost
  and bundle size without sufficient benefit.

---

## 6. File Naming

| Element            | Convention        | Example                  |
|--------------------|-------------------|--------------------------|
| Components         | `PascalCase.tsx`  | `OrderSummary.tsx`       |
| Hooks              | `camelCase.ts`    | `useOrderData.ts`        |
| Utilities          | `camelCase.ts`    | `formatCurrency.ts`      |
| Types              | `camelCase.ts`    | `types.ts`, `order.ts`   |
| Tests              | `*.test.tsx`      | `OrderSummary.test.tsx`  |
| CSS Modules        | `*.module.css`    | `OrderSummary.module.css`|
| Constants          | `camelCase.ts`    | `routes.ts`              |

---

## 7. Testing

**Tools: Vitest (unit/component), Playwright (e2e).**

### Unit and Component Tests

- Test behavior, not implementation. "When the user clicks Submit, the form
  calls onSubmit with the form data" -- not "the handleClick function sets
  state to X."
- Use `@testing-library/react`. Do not use Enzyme.
- Query elements by role, label, or text -- never by class name or test ID
  unless no accessible query exists.
- Each component test file lives next to the component it tests.

### End-to-End Tests

- E2E tests live in `tests/e2e/` and cover critical user journeys.
- E2E tests run against a real (or realistically stubbed) backend.
- Keep E2E tests to the minimum set that catches integration failures unit
  tests cannot. They are expensive to maintain -- do not duplicate unit test
  coverage.

---

## 8. Accessibility

**Standard: WCAG 2.1 Level AA. This is not optional.**

- Every interactive element is keyboard-accessible.
- Every image has meaningful `alt` text (or `alt=""` for decorative images).
- Form inputs have associated `<label>` elements (not just placeholder text).
- Color contrast meets AA ratios (4.5:1 for normal text, 3:1 for large text).
- Use semantic HTML elements (`<button>`, `<nav>`, `<main>`, `<section>`)
  instead of `<div>` with click handlers.
- Run `axe-core` in CI. Accessibility violations fail the build.

---

## 9. Performance

- **Lazy-load routes** with `React.lazy` and `Suspense`. The initial bundle
  should contain only the shell and the first route.
- **Memoize expensive computations** with `useMemo`. Do not memoize everything
  -- measure first.
- **Avoid unnecessary re-renders.** Use React DevTools Profiler to identify
  components that render too often. Lift state down (closer to where it is
  used) before reaching for `React.memo`.
- **Image optimization.** Use responsive `srcSet`, lazy loading (`loading="lazy"`),
  and modern formats (WebP/AVIF).
- **Bundle analysis.** Run `vite-plugin-visualizer` before every release. No
  single third-party dependency should exceed 50KB gzipped without an ADR
  justifying it.

---

## 10. TypeScript

- **Strict mode enabled.** `"strict": true` in `tsconfig.json`. No exceptions.
- Use `type` over `interface` unless you need declaration merging (rare).
- No `any`. Use `unknown` and narrow with type guards.
- API response types are generated from the backend schema (OpenAPI codegen)
  or manually defined in `features/<feature>/types.ts`.
- Discriminated unions over optional properties for variant types.

```tsx
// Good: discriminated union
type Result =
  | { status: "success"; data: Order }
  | { status: "error"; message: string };

// Bad: optional properties
type Result = {
  status: string;
  data?: Order;
  message?: string;
};
```

---

## Do / Don't

### Do

- Use named exports. Default exports make refactoring harder.
- Co-locate files that change together (component + test + styles).
- Use `React.lazy` for every route-level component.
- Derive state from props/other state instead of syncing with `useEffect`.
- Use `key` props that are stable and unique (database IDs, not array indices).

### Don't

- Don't use `useEffect` for data fetching -- use TanStack Query.
- Don't suppress ESLint warnings with `eslint-disable`. Fix the root cause.
- Don't nest ternaries in JSX -- extract to a variable or a helper component.
- Don't pass entire objects as props when only a primitive is needed.
- Don't use `index` as `key` in lists that can reorder.
- Don't import from another feature's internal paths -- only from its `index.ts`.

---

## Common Pitfalls

1. **Stale closures in useEffect.** Forgetting a dependency causes the callback
   to capture an old value. Always trust the exhaustive-deps lint rule.
2. **Storing derived state.** Putting `filteredItems` in `useState` when it can
   be computed from `items` and `filter` during render. This creates sync bugs.
3. **Over-abstracting too early.** Creating a `<GenericDataTable>` before you
   have three tables. Start concrete; generalize when a third use case appears.
4. **Prop drilling avoidance reflex.** Reaching for Context or Zustand when
   passing a prop through two levels is perfectly fine and more explicit.
5. **Giant useEffect blocks.** A single `useEffect` that handles subscription,
   data fetching, and DOM manipulation. Split into focused effects.
6. **Misusing useMemo/useCallback everywhere.** Memoization has a cost. Only
   use it when profiling shows a measurable benefit.

---

## Checklist

Before merging any React PR, verify:

- [ ] Components are functional (no class components)
- [ ] Props use a named `*Props` type with destructuring
- [ ] No `any` types -- `unknown` with narrowing instead
- [ ] Custom hooks are prefixed with `use` and have a single responsibility
- [ ] State lives at the lowest necessary level
- [ ] Server state uses TanStack Query, not `useEffect` + `fetch`
- [ ] All interactive elements are keyboard-accessible
- [ ] Tests use Testing Library queries (role, label, text) -- no test IDs unless required
- [ ] No ESLint warnings suppressed without an accompanying comment explaining why
- [ ] Route-level components are lazy-loaded
- [ ] Feature modules export only through `index.ts`
- [ ] Bundle size checked with `vite-plugin-visualizer`
- [ ] CSS Modules used for styling (no inline styles, no CSS-in-JS)
