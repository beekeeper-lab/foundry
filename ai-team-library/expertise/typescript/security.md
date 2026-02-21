# TypeScript Security

TypeScript's type system catches many categories of bugs at compile time, but
security requires runtime enforcement too. Types disappear at runtime -- every
external boundary needs validation, and every trust assumption needs
justification.

---

## Defaults

- **Runtime validation:** Zod at every external data boundary (API, file I/O, env vars).
- **No `any`:** Eliminates the most common escape hatch for unsafe operations.
- **Dependency auditing:** `pnpm audit` in CI; critical/high findings block the build.
- **Linting:** `@typescript-eslint/no-unsafe-*` rules enabled.
- **Environment variables:** Validated with Zod at startup, not accessed with raw `process.env`.
- **Input sanitization:** Server-side validation for all user input, regardless of client types.

### Alternatives

| Default        | Alternative     | When to consider                      |
|----------------|-----------------|---------------------------------------|
| Zod            | Valibot         | Bundle size critical (browser)        |
| `pnpm audit`   | Snyk / Socket  | Need supply chain analysis            |
| ESLint TS      | Biome           | Faster linting, simpler config        |

---

## Validate at Boundaries

Types do not exist at runtime. Every point where external data enters the
application is a trust boundary that requires runtime validation.

```ts
import { z } from "zod";

// 1. Define schema as the single source of truth
const OrderSchema = z.object({
  id: z.string().uuid(),
  customerId: z.string().min(1),
  items: z.array(
    z.object({
      productId: z.string(),
      quantity: z.number().int().positive(),
    }),
  ),
  total: z.number().nonnegative(),
});

type Order = z.infer<typeof OrderSchema>;

// 2. Validate at the boundary
async function handleCreateOrder(req: Request): Promise<Order> {
  const body: unknown = await req.json();
  return OrderSchema.parse(body); // throws ZodError if invalid
}
```

**Boundaries that require validation:**

- API request/response bodies.
- URL parameters and query strings.
- Environment variables.
- File contents (JSON, YAML, CSV).
- WebSocket messages.
- Third-party SDK return values.

---

## Environment Variable Validation

Validate all environment variables at application startup. Fail fast with a
clear error message.

```ts
// src/config.ts
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  DATABASE_URL: z.string().url(),
  API_SECRET: z.string().min(32),
  PORT: z.coerce.number().int().positive().default(3000),
});

// Validate once at startup -- crash immediately if invalid
export const env = EnvSchema.parse(process.env);

// Usage elsewhere: fully typed, guaranteed valid
// import { env } from "./config";
// env.DATABASE_URL -- string, validated as URL
```

Never access `process.env` directly outside `config.ts`. The `env` object is
the single typed entry point.

---

## Preventing Type Assertion Abuse

Type assertions (`as`) bypass the compiler without runtime checks. Restrict
their use.

```ts
// Bad: assertion without validation -- runtime crash waiting to happen
const user = response.data as User;

// Good: validate, then the type is narrowed safely
const user = UserSchema.parse(response.data);

// Acceptable: controlled branding (documented exception)
function createUserId(raw: string): UserId {
  // Validated upstream; branded for type safety
  return raw as UserId;
}
```

**ESLint rules to enforce:**

- `@typescript-eslint/no-unsafe-assignment` -- flags `any` flowing into typed variables.
- `@typescript-eslint/no-unsafe-member-access` -- flags property access on `any`.
- `@typescript-eslint/no-explicit-any` -- flags `any` annotations.
- `@typescript-eslint/consistent-type-assertions` -- restricts `as` usage.

---

## Dependency Security

- Run `pnpm audit` in CI. Critical and high findings are build blockers.
- Pin dependencies via lockfile (`pnpm-lock.yaml` committed).
- Review new dependencies before adding: maintainer reputation, download count,
  last publish date, known vulnerabilities.
- Prefer smaller, focused packages over large utility libraries.
- Use `pnpm licenses list` to audit license compliance.

---

## Prototype Pollution Defense

JavaScript objects are vulnerable to prototype pollution through `__proto__` and
`constructor.prototype` manipulation. TypeScript types do not prevent this.

```ts
// Bad: spreading unknown input directly
function mergeConfig(base: Config, overrides: unknown): Config {
  return { ...base, ...(overrides as Partial<Config>) }; // unsafe
}

// Good: validate overrides with Zod first
const ConfigOverrideSchema = z.object({
  timeout: z.number().optional(),
  retries: z.number().int().optional(),
}).strict(); // .strict() rejects unknown keys

function mergeConfig(base: Config, overrides: unknown): Config {
  const validated = ConfigOverrideSchema.parse(overrides);
  return { ...base, ...validated };
}
```

- Use `.strict()` on Zod schemas to reject unexpected keys.
- Use `Object.create(null)` for dictionaries that should not inherit from `Object.prototype`.
- Never use `JSON.parse` on untrusted input without schema validation.

---

## Do / Don't

### Do

- Validate all external data with Zod at the boundary where it enters.
- Validate environment variables once at startup and export a typed `env` object.
- Enable `@typescript-eslint/no-unsafe-*` ESLint rules.
- Run `pnpm audit` in CI and block on critical/high findings.
- Use `.strict()` on Zod schemas that process user input.
- Fail fast with descriptive errors when validation fails.

### Don't

- Don't use `as` to cast external data to a type without validation.
- Don't access `process.env` directly -- go through the validated `env` config.
- Don't use `any` as a workaround for complex types. Use `unknown` and narrow.
- Don't trust client-side TypeScript types on the server. Types are erased at runtime.
- Don't use `eval()`, `new Function()`, or `vm.runInNewContext()` with user input.
- Don't spread untrusted objects without validation (prototype pollution risk).

---

## Common Pitfalls

1. **Trusting `as` for safety.** `data as User` compiles but performs zero
   runtime checks. The app crashes when a field is missing or the wrong type.
2. **Raw `process.env` access.** `process.env.PORT` is `string | undefined`.
   Without validation, you get silent `undefined` bugs or crashes.
3. **Forgetting server-side validation.** TypeScript on the client gives a false
   sense of security. The server must validate independently because HTTP
   requests can be crafted without the client.
4. **Stale lockfile.** Not committing `pnpm-lock.yaml` means different
   environments resolve different dependency versions, some of which may be
   compromised.
5. **Over-permissive Zod schemas.** Using `z.object({}).passthrough()` on user
   input lets unexpected keys through, enabling prototype pollution or data
   injection.

---

## Checklist

Before deploying TypeScript applications:

- [ ] All external data boundaries validate with Zod (API, file, env, WebSocket)
- [ ] Environment variables validated at startup via a typed `env` config
- [ ] No `any` types in the codebase
- [ ] No `as` assertions on external data (only at controlled branding points)
- [ ] `@typescript-eslint/no-unsafe-*` rules enabled and passing
- [ ] `pnpm audit` passes with no critical or high findings
- [ ] Lockfile (`pnpm-lock.yaml`) committed and reviewed
- [ ] Zod schemas use `.strict()` for user-facing input
- [ ] No `eval()`, `new Function()`, or dynamic code execution with user input
- [ ] Server-side validation exists independently of client-side types
