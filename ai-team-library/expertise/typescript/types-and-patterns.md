# TypeScript Types and Patterns

Advanced type patterns for building robust, maintainable TypeScript code. These
patterns reduce runtime errors by encoding business rules in the type system.

---

## Defaults

- **Discriminated unions** for variant types (not optional properties).
- **Generics** for reusable data structures and utilities.
- **Type narrowing** via type guards, not type assertions.
- **Runtime validation** with Zod for external data boundaries.
- **Utility types** from the standard library before writing custom ones.

### Alternatives

| Default | Alternative  | When to consider                          |
|---------|------------- |-------------------------------------------|
| Zod     | Valibot      | Smaller bundle size is critical           |
| Zod     | ArkType      | Need better performance on large schemas  |
| Zod     | io-ts        | Functional programming style preferred    |

---

## Discriminated Unions

Model variant types with a shared literal discriminant field. This gives
exhaustive checking in `switch` statements and narrowing in conditionals.

```ts
type ApiResult<T> =
  | { status: "success"; data: T }
  | { status: "error"; code: number; message: string }
  | { status: "loading" };

function renderResult(result: ApiResult<User>) {
  switch (result.status) {
    case "success":
      return `Hello, ${result.data.name}`;
    case "error":
      return `Error ${result.code}: ${result.message}`;
    case "loading":
      return "Loading...";
    default:
      // exhaustive check: this line errors if a variant is unhandled
      const _exhaustive: never = result;
      return _exhaustive;
  }
}
```

**Rules:**

- Always include an exhaustive check (`never` assignment) in switch statements
  over discriminated unions.
- Name the discriminant field consistently across the codebase (`status`, `kind`,
  or `type` -- pick one and stick with it).

---

## Type Narrowing

Narrow `unknown` and union types with type guards rather than type assertions.

### Built-in Narrowing

```ts
function formatValue(value: string | number): string {
  if (typeof value === "string") {
    return value.toUpperCase(); // narrowed to string
  }
  return value.toFixed(2); // narrowed to number
}
```

### Custom Type Guards

```ts
type User = { id: string; name: string; role: "admin" | "member" };

function isUser(data: unknown): data is User {
  return (
    typeof data === "object" &&
    data !== null &&
    "id" in data &&
    "name" in data &&
    "role" in data
  );
}

// Usage
function handleResponse(body: unknown) {
  if (isUser(body)) {
    console.log(body.name); // safely narrowed to User
  }
}
```

For complex shapes, prefer Zod over hand-written type guards (see Runtime
Validation below).

---

## Generics

Use generics for reusable containers and utilities. Keep generic parameters
descriptive and constrained.

```ts
// Good: descriptive parameter with constraint
function groupBy<TItem, TKey extends string>(
  items: TItem[],
  keyFn: (item: TItem) => TKey,
): Record<TKey, TItem[]> {
  const result = {} as Record<TKey, TItem[]>;
  for (const item of items) {
    const key = keyFn(item);
    (result[key] ??= []).push(item);
  }
  return result;
}

// Usage: types are inferred
const grouped = groupBy(users, (u) => u.role);
// typeof grouped: Record<"admin" | "member", User[]>
```

**Rules:**

- Constrain generic parameters (`extends`) when possible.
- Use descriptive names: `TItem` over `T`, `TResponse` over `R`.
- Don't add generics unless the function/type is actually used with multiple types.

---

## Utility Types

Use the standard library utility types before writing custom ones.

| Utility                | Purpose                                          |
|------------------------|--------------------------------------------------|
| `Partial<T>`           | All properties optional                          |
| `Required<T>`          | All properties required                          |
| `Pick<T, K>`           | Subset of properties                             |
| `Omit<T, K>`           | All properties except K                          |
| `Record<K, V>`         | Object with keys K and values V                  |
| `Readonly<T>`          | All properties readonly                          |
| `Extract<T, U>`        | Members of T assignable to U                     |
| `Exclude<T, U>`        | Members of T not assignable to U                 |
| `NonNullable<T>`       | Remove `null` and `undefined`                    |
| `ReturnType<T>`        | Return type of a function type                   |

```ts
// Partial for update payloads
type UserUpdate = Partial<Pick<User, "name" | "email">>;

// Readonly for immutable state
type AppState = Readonly<{
  users: readonly User[];
  currentPage: number;
}>;
```

---

## Runtime Validation with Zod

Type assertions (`as`) do not validate data at runtime. At system boundaries
(API responses, form inputs, file parsing), use Zod to validate and infer types.

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(["admin", "member"]),
});

// Infer the type from the schema -- single source of truth
type User = z.infer<typeof UserSchema>;

// Validate at the boundary
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data: unknown = await response.json();
  return UserSchema.parse(data); // throws ZodError if invalid
}
```

**Rules:**

- Define the Zod schema first, then infer the type. Do not maintain both
  separately.
- Use `.parse()` at system boundaries (API, file I/O, environment variables).
- Use `.safeParse()` when you want to handle errors without exceptions.

---

## Branded / Opaque Types

Prevent accidental mixing of structurally identical types (e.g., `UserId` vs.
`OrderId`) with branded types.

```ts
type Brand<T, B extends string> = T & { readonly __brand: B };

type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;

function createUserId(id: string): UserId {
  return id as UserId; // single controlled assertion point
}

function getUser(id: UserId): User { /* ... */ }

const userId = createUserId("u-123");
const orderId = "o-456" as OrderId;

getUser(userId);   // OK
getUser(orderId);  // Type error: OrderId is not assignable to UserId
```

---

## Do / Don't

### Do

- Use discriminated unions with exhaustive checks for variant types.
- Narrow `unknown` with type guards or Zod, not type assertions.
- Validate external data at system boundaries with Zod schemas.
- Use standard utility types (`Partial`, `Pick`, `Omit`, etc.) before writing custom ones.
- Use branded types when domain IDs must not be mixed.

### Don't

- Don't use `as` to silence the compiler. Fix the type or validate the data.
- Don't hand-write type guards for complex shapes -- use Zod.
- Don't create unnecessary generic abstractions. If a function is only used with
  one type, don't make it generic.
- Don't nest conditional types more than two levels deep. Extract to named types.
- Don't use `object` as a type. Use `Record<string, unknown>` or a specific shape.

---

## Common Pitfalls

1. **Type assertion as validation.** `data as User` compiles but does not check
   the shape. The app crashes at runtime when a field is missing.
2. **Forgetting the exhaustive check.** A `switch` on a discriminated union
   without a `never` default silently ignores new variants added later.
3. **Overly complex mapped types.** Deeply nested conditional and mapped types
   are hard to read and debug. Extract intermediate types with descriptive names.
4. **Duplicate type and schema.** Defining a `type User` and a separate
   `UserSchema` that can drift out of sync. Use `z.infer` to derive one from
   the other.
5. **Using `object` type.** `object` matches arrays, functions, and class
   instances -- almost never what you want. Be specific.

---

## Checklist

Before merging type-heavy changes:

- [ ] Variant types use discriminated unions with exhaustive checks
- [ ] External data boundaries validate with Zod (not `as` assertions)
- [ ] Zod schemas are the single source of truth (types inferred with `z.infer`)
- [ ] Generic parameters have descriptive names and constraints
- [ ] Standard utility types used before custom ones
- [ ] No `as` assertions except at controlled branding points
- [ ] No `object` type (use `Record<string, unknown>` or a specific shape)
- [ ] Custom type guards return `data is T` predicate
- [ ] Complex types are decomposed into named intermediate types
- [ ] Domain IDs use branded types where mixing would cause bugs
