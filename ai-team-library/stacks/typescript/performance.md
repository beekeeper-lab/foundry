# TypeScript Performance

TypeScript performance covers two distinct concerns: compile-time performance
(how fast `tsc` checks your code) and runtime performance (how efficiently the
emitted JavaScript executes). Both matter. A slow type checker kills developer
productivity; slow runtime code kills user experience.

---

## Defaults

- **Compile-time:** Incremental builds (`"incremental": true`), project references for monorepos.
- **Runtime:** Measure before optimizing. Use native APIs over utility libraries.
- **Bundling:** Tree-shaking-friendly ESM exports. No side-effect-heavy barrel files.
- **Profiling:** `tsc --generateTrace` for type-checking bottlenecks; Node `--prof` or Chrome DevTools for runtime.
- **Budget:** `tsc` full build < 30 seconds; incremental rebuild < 5 seconds.

### Alternatives

| Default              | Alternative          | When to consider                       |
|----------------------|----------------------|----------------------------------------|
| `tsc` incremental    | `tsc --build`        | Monorepo with project references       |
| `tsc` for checking   | `oxc` / `stc`        | Experimental; faster type checking     |
| Vite for bundling    | esbuild standalone   | Non-browser target, simpler setup      |

---

## Compile-Time Performance

### Enable Incremental Builds

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": "./dist/.tsbuildinfo"
  }
}
```

Incremental builds reuse the previous compilation's dependency graph and only
recheck changed files. This typically reduces rebuild time by 60-80%.

### Project References for Monorepos

```jsonc
// tsconfig.json (root)
{
  "references": [
    { "path": "./packages/shared" },
    { "path": "./packages/api" },
    { "path": "./packages/web" }
  ]
}

// packages/shared/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "outDir": "./dist",
    "declaration": true
  }
}
```

- Each package compiles independently, enabling parallel checking.
- Use `tsc --build` to compile the dependency graph in order.
- `composite: true` is required for referenced projects.

### Avoiding Type-Check Bottlenecks

```ts
// Slow: deeply nested conditional types
type DeepResolve<T> = T extends Promise<infer U>
  ? DeepResolve<U>
  : T extends object
    ? { [K in keyof T]: DeepResolve<T[K]> }
    : T;

// Better: limit recursion depth or simplify the type
type ResolvePromise<T> = T extends Promise<infer U> ? U : T;
```

**Common bottlenecks:**

- Deeply nested conditional and mapped types (recursive types with no base case limit).
- Large union types (500+ members).
- Complex `infer` chains.
- Barrel files that re-export hundreds of modules.

Use `tsc --generateTrace ./trace` and load the trace in Chrome DevTools
(`chrome://tracing`) to identify slow types.

---

## Runtime Performance

### Prefer Native APIs

```ts
// Slow: importing lodash for a simple operation
import { uniq } from "lodash";
const unique = uniq(items);

// Fast: native Set (zero dependencies, tree-shakes perfectly)
const unique = [...new Set(items)];

// Slow: lodash.cloneDeep for flat objects
import { cloneDeep } from "lodash";
const copy = cloneDeep(config);

// Fast: structuredClone (native, handles most cases)
const copy = structuredClone(config);
```

**Prefer native over library:**

- `Array.prototype.map/filter/reduce` over lodash equivalents.
- `structuredClone()` over `lodash.cloneDeep`.
- `Object.groupBy()` (ES2024) over `lodash.groupBy`.
- `Set` / `Map` over object-based lookups for frequent membership checks.

### Avoid Unnecessary Object Allocation

```ts
// Bad: creates a new object on every iteration
function processItems(items: Item[]): ProcessedItem[] {
  return items.map((item) => ({
    ...item,                    // spreading every property
    displayName: item.name,     // could just read item.name directly
  }));
}

// Better: transform only what you need
function processItems(items: Item[]): ProcessedItem[] {
  return items.map((item) => ({
    id: item.id,
    displayName: item.name,
    total: item.price * item.quantity,
  }));
}
```

---

## Tree Shaking and Bundle Size

### Write Tree-Shakeable Exports

```ts
// Good: named exports -- bundler can eliminate unused ones
export function formatDate(d: Date): string { /* ... */ }
export function formatCurrency(n: number): string { /* ... */ }

// Bad: namespace object -- bundler cannot tree-shake individual functions
const utils = { formatDate, formatCurrency };
export default utils;
```

### Barrel File Discipline

Large barrel files (`index.ts` that re-export everything) defeat tree shaking
and slow down type checking.

```ts
// Bad: re-exporting the entire module tree
export * from "./components";
export * from "./hooks";
export * from "./utils";
export * from "./types";

// Good: explicit, curated public API
export { Button } from "./components/Button";
export { useAuth } from "./hooks/useAuth";
export type { User, Order } from "./types";
```

---

## Do / Don't

### Do

- Enable `incremental: true` in every `tsconfig.json`.
- Use project references in monorepos for parallel type checking.
- Use `tsc --generateTrace` to find type-checking bottlenecks.
- Prefer native APIs (`Set`, `Map`, `structuredClone`, `Object.groupBy`) over utility libraries.
- Write named ESM exports for tree shaking.
- Profile runtime code with real data before optimizing.

### Don't

- Don't write recursive conditional types without a depth limit.
- Don't use `export *` in barrel files. Curate the public API explicitly.
- Don't import full utility libraries (`lodash`, `moment`) when a native API or smaller package exists.
- Don't optimize before measuring. Run `tsc --generateTrace` for compile time and a profiler for runtime.
- Don't create large union types (500+ members). Use a `Record` or `Map` instead.
- Don't use `JSON.parse(JSON.stringify(obj))` for cloning. Use `structuredClone`.

---

## Common Pitfalls

1. **Barrel file explosion.** A root `index.ts` that does `export *` from 50
   modules forces the type checker to evaluate everything on every import. Keep
   barrel files small and explicit.
2. **Recursive types without limits.** A type like `DeepPartial<T>` that
   recurses into nested objects can cause the type checker to hang on deeply
   nested types. Add a depth limit.
3. **Importing lodash without cherry-picking.** `import { uniq } from "lodash"`
   pulls the entire library if the bundler is not configured for tree shaking.
   Use `lodash-es` with direct imports or prefer native alternatives.
4. **Missing incremental builds.** Without `incremental: true`, every `tsc` run
   rechecks the entire project. This wastes minutes on large codebases.
5. **Over-abstracted generic types.** Complex generics that infer through
   multiple layers slow down type checking and produce unreadable error messages.
   Simplify or add explicit type annotations.

---

## Checklist

Before merging performance-related changes:

- [ ] `incremental: true` enabled in `tsconfig.json`
- [ ] Monorepo uses project references with `composite: true`
- [ ] No recursive types without depth limits
- [ ] Barrel files export a curated API (no `export *` on large modules)
- [ ] Native APIs preferred over utility library equivalents
- [ ] Named exports used (not default namespace objects)
- [ ] `tsc --generateTrace` run for any type-heavy changes
- [ ] No full-library imports where tree-shakeable alternatives exist
- [ ] `tsc` full build completes in < 30 seconds
- [ ] Runtime hot paths profiled with real data before optimization
