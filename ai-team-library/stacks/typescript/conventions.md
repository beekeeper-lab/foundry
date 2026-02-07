# TypeScript Conventions

These conventions govern all TypeScript code in the project. Strict mode is
non-negotiable. The type system is a tool for catching bugs at compile time --
use it fully, not as a formality to satisfy the compiler.

---

## Defaults

- **Strict mode:** `"strict": true` in `tsconfig.json`. No exceptions.
- **Target:** ES2022 or later (all modern environments support it).
- **Module system:** ESM (`"module": "ESNext"` or `"NodeNext"` for Node projects).
- **Linting:** ESLint with `@typescript-eslint/recommended-type-checked`.
- **Formatting:** Prettier with project-level config.
- **Type preference:** `type` over `interface` unless declaration merging is needed.
- **No `any`:** Use `unknown` and narrow with type guards.

### tsconfig Baseline

```jsonc
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules": true
  }
}
```

Key flags beyond `strict`:
- `noUncheckedIndexedAccess`: array/object indexing returns `T | undefined`.
- `exactOptionalPropertyTypes`: distinguishes `{ x?: string }` from `{ x: string | undefined }`.

---

## Type Aliases vs Interfaces

Use `type` by default. Use `interface` only when you need declaration merging
(rare, mainly for library augmentation).

```ts
// Default: type alias
type User = {
  id: string;
  name: string;
  role: "admin" | "member";
};

// Exception: declaration merging for library augmentation
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}
```

---

## Naming Conventions

| Element          | Convention       | Example                          |
|------------------|------------------|----------------------------------|
| Types            | `PascalCase`     | `OrderStatus`, `UserRole`        |
| Type parameters  | Descriptive      | `TItem`, `TResponse`             |
| Enums            | Avoided          | Use union types instead          |
| Constants        | `UPPER_SNAKE`    | `MAX_RETRIES`, `API_BASE_URL`    |
| Functions        | `camelCase`      | `formatCurrency`, `parseDate`    |
| Files            | `camelCase.ts`   | `orderUtils.ts`, `types.ts`      |

- Do not prefix types with `I` or `T` (no `IUser`, no `TUser`). Use plain `User`.
- Exception: generic type parameters use `T` prefix for clarity (`TItem`, `TKey`).

---

## Avoiding `any`

`any` disables the type system. Use `unknown` and narrow.

```ts
// Bad: any silently accepts everything
function parsePayload(data: any) {
  return data.items.map((i: any) => i.name);
}

// Good: unknown forces you to validate before use
function parsePayload(data: unknown): string[] {
  if (!isOrderPayload(data)) {
    throw new Error("Invalid payload shape");
  }
  return data.items.map((i) => i.name);
}
```

If a third-party library forces `any`, isolate it in a thin wrapper and type
the wrapper's public API.

---

## Union Types Over Enums

Enums have runtime behavior that is confusing and does not tree-shake well.
Use string literal unions.

```ts
// Good: union type
type OrderStatus = "pending" | "confirmed" | "shipped" | "delivered";

// Bad: enum
enum OrderStatus {
  Pending = "pending",
  Confirmed = "confirmed",
  Shipped = "shipped",
  Delivered = "delivered",
}
```

When you need a reverse mapping or iteration, use `as const` with an object:

```ts
const ORDER_STATUSES = ["pending", "confirmed", "shipped", "delivered"] as const;
type OrderStatus = (typeof ORDER_STATUSES)[number];
```

---

## Module Boundaries

- Each feature or module exposes a public API through an `index.ts` barrel file.
- Internal types and helpers are not exported from the barrel.
- Cross-module imports go through the barrel, never into internal files.
- Circular imports are a build error. ESLint rule `import/no-cycle` is enabled.

```
features/
  orders/
    index.ts          # public: export type { Order }; export { OrderList };
    types.ts          # internal: Order, OrderLineItem
    orderUtils.ts     # internal: not exported from index
```

---

## Do / Don't

### Do

- Enable `strict: true` and the additional flags listed in the tsconfig baseline.
- Use `type` for data shapes; reserve `interface` for declaration merging.
- Use `unknown` instead of `any` and narrow with type guards.
- Use discriminated unions for variant types.
- Use `as const` for literal tuples and constant objects.
- Write explicit return types on exported functions.

### Don't

- Don't use `any`. Ever. Use `unknown`, generics, or a more precise type.
- Don't use enums. Use string literal unions or `as const` objects.
- Don't use `@ts-ignore`. Use `@ts-expect-error` with an explanation if truly needed.
- Don't use type assertions (`as`) to silence the compiler. Fix the type instead.
- Don't omit return types on public/exported functions.
- Don't barrel-export everything. Only export what other modules need.

---

## Common Pitfalls

1. **Widening with `as`.** `response.data as User` silences the compiler but
   does not validate the shape at runtime. Use a validation library (Zod) for
   external data.
2. **Forgetting `noUncheckedIndexedAccess`.** Without it, `arr[0]` is typed as
   `T` instead of `T | undefined`, hiding potential runtime errors.
3. **Optional properties vs. `undefined` values.** `{ x?: string }` means the
   key may be absent; `{ x: string | undefined }` means the key is present but
   the value may be `undefined`. `exactOptionalPropertyTypes` enforces this.
4. **Circular imports.** Two modules importing from each other causes load-order
   bugs and often `undefined` at runtime. Restructure or extract shared types.
5. **Over-relying on type inference.** Inferred return types on exported
   functions make the public API fragile -- a refactoring inside the function
   can silently change the return type for all consumers.

---

## Checklist

Before merging TypeScript changes:

- [ ] `strict: true` and additional flags enabled in `tsconfig.json`
- [ ] No `any` types (search for `: any` and `as any`)
- [ ] No `@ts-ignore` (use `@ts-expect-error` with explanation if needed)
- [ ] `type` used instead of `interface` (unless declaration merging)
- [ ] Union types used instead of enums
- [ ] Exported functions have explicit return types
- [ ] Module barrel files (`index.ts`) export only the public API
- [ ] No circular imports (`import/no-cycle` passes)
- [ ] External data validated at runtime (Zod or equivalent)
- [ ] `noUncheckedIndexedAccess` enabled and code handles `T | undefined`
