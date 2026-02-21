# Node.js Stack Conventions

These conventions are non-negotiable defaults for Node.js server-side
applications on this team. Deviations require an ADR with justification.
"I prefer it differently" is not justification.

---

## 1. Project Structure

```
project-root/
  src/
    index.ts                # Entry point (server bootstrap)
    config/
      index.ts              # Configuration loading, env var mapping
      schema.ts             # Config validation schema (Zod)
    routes/                 # Route definitions (one file per resource)
    handlers/               # Request handlers (business logic entry points)
    services/               # Business logic (stateless, framework-agnostic)
    repositories/           # Data access layer
    middleware/              # Express/Fastify middleware
    models/                 # Domain types and interfaces
    utils/                  # Pure utility functions (no business logic)
    errors/                 # Custom error classes
  tests/
    unit/                   # Mirror src/ structure
    integration/            # Tests requiring running services
    fixtures/               # Shared test data
    helpers/                # Test utility functions
  package.json
  tsconfig.json
  .nvmrc                    # Pin the Node.js major version (e.g., 22)
  .env.example              # Documented env var template (no real values)
  README.md
```

**Rules:**
- Use `src/` layout. All application code lives under `src/`.
- Separate routes from handlers. Routes define HTTP concerns (method, path,
  middleware chain). Handlers contain the logic.
- One repository per data store entity. Repositories return domain types, not
  raw database rows.
- Monorepos use npm workspaces with independent `package.json` files per
  package.

---

## 2. Language and Runtime

**TypeScript is mandatory.** No plain JavaScript files in `src/`.

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "sourceMap": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

**Rules:**
- `strict: true` is required. No exceptions.
- `noUncheckedIndexedAccess: true` prevents silent undefined from array/object
  access.
- No `any`. Use `unknown` and narrow with type guards. Every `any` requires a
  justifying comment.
- Pin Node.js version in `.nvmrc`. CI and local development must use the same
  major version.

---

## 3. Framework

**Default: Fastify.** Express is acceptable for existing projects, but new
projects use Fastify for its built-in schema validation, logging, and
performance.

**Rules:**
- Register routes as plugins for encapsulation.
- Use Fastify's schema-based validation (JSON Schema or Typebox) for all
  request inputs. Do not validate manually in handlers.
- Do not use `app.use()` for global middleware unless it genuinely applies to
  every route (e.g., request ID, CORS).
- Register error handlers centrally. Individual routes do not catch and format
  their own errors.

---

## 4. Formatting and Linting

**Tools: ESLint + Prettier.**

```jsonc
// .eslintrc.cjs (key rules)
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/no-floating-promises": "error",
    "no-console": "error"
  }
}
```

**Rules:**
- Prettier handles all formatting. Do not configure ESLint formatting rules.
- `no-console: error`. Use a structured logger, never `console.log` in
  production code.
- `no-floating-promises: error`. Every promise must be awaited, returned, or
  explicitly voided.
- Format on save in your editor. CI rejects unformatted code.

---

## 5. Naming Conventions

| Element          | Convention        | Example                     |
|------------------|-------------------|-----------------------------|
| Files            | `kebab-case.ts`   | `order-service.ts`          |
| Classes          | `PascalCase`      | `OrderService`              |
| Functions        | `camelCase`       | `calculateTotal`            |
| Constants        | `UPPER_SNAKE`     | `MAX_RETRY_COUNT`           |
| Interfaces       | `PascalCase`      | `OrderRepository`           |
| Type aliases     | `PascalCase`      | `CreateOrderInput`          |
| Enum members     | `PascalCase`      | `OrderStatus.Completed`     |
| Environment vars | `UPPER_SNAKE`     | `DATABASE_URL`              |

Do not prefix interfaces with `I`. Do not suffix types with `Type`. The name
should describe the concept, not the TypeScript construct.

---

## 6. Dependency Management

**Tool: npm** (with lockfile).

**Rules:**
- Commit `package-lock.json`. Always.
- Use exact versions for direct dependencies (`--save-exact`).
- Audit dependencies weekly: `npm audit`. Critical and High vulnerabilities
  block deployment.
- Keep `devDependencies` separate. Build tooling, test frameworks, and type
  packages belong in `devDependencies`.
- No global package installations. Use `npx` for one-off CLI tools.
- Evaluate every new dependency: does it justify the supply chain risk? If the
  functionality is achievable in under 50 lines, write it yourself.

---

## 7. Configuration and Environment

**Tool: Zod for validation.**

```typescript
import { z } from "zod";

const configSchema = z.object({
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

export const config = configSchema.parse(process.env);
```

**Rules:**
- Validate all environment variables at startup. Fail fast with a clear error
  message if required variables are missing.
- Never access `process.env` directly outside the config module.
- Maintain `.env.example` with every variable documented (description, type,
  whether required, default value). Never commit `.env` files.
- Do not use different config loading mechanisms per environment. One config
  module, one validation schema, environment-specific values come from the
  environment.

---

## 8. Logging

**Tool: Pino** (Fastify's default, or standalone for Express).

```typescript
import pino from "pino";

const logger = pino({
  level: config.LOG_LEVEL,
  formatters: {
    level: (label) => ({ level: label }),
  },
});

// Good: structured, context-rich
logger.info({ orderId, total, durationMs: elapsed }, "order_processed");

// Bad: unstructured string interpolation
logger.info(`Processed order ${orderId} for $${total}`);
```

**Rules:**
- Every log entry uses a static event message with variable data as properties.
- Log levels: `debug` for developer diagnostics, `info` for operational events,
  `warn` for recoverable problems, `error` for failures requiring attention.
- Never log secrets, tokens, passwords, or full PII.
- Include a request ID in all log entries for distributed tracing. Use Fastify's
  built-in request ID or add middleware for Express.
- JSON output in production. Pretty-print in development only.

---

## 9. Error Handling

```typescript
// Base application error
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly isOperational: boolean = true,
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Specific errors
export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} '${id}' not found`, "NOT_FOUND", 404);
  }
}
```

**Rules:**
- Define a base `AppError` class. All application errors inherit from it.
- Distinguish operational errors (expected failures: bad input, missing
  resource) from programmer errors (bugs: null reference, type mismatch).
- Catch specific errors. Never use bare `catch (e)` without rethrowing
  unknown errors.
- Centralized error handler formats the response and logs the error. Individual
  handlers do not format error responses.
- Async errors must be caught. Use `no-floating-promises` ESLint rule and
  Fastify's built-in async error handling.

---

## 10. Testing

**Framework: Vitest** (default) or Jest (for existing projects).

**Rules:**
- Test file naming: `<module-name>.test.ts`, co-located or in `tests/unit/`.
- Use `describe` blocks to group related tests. Use `it` or `test` with
  descriptive names: `it("returns 404 when order does not exist")`.
- Unit tests mock external dependencies (databases, HTTP clients) using
  dependency injection, not module mocking.
- Integration tests use Testcontainers for databases and external services.
  Never mock the database in integration tests.
- Aim for 80% line coverage minimum on new code. Branch coverage is the
  more meaningful metric.
- Tests run in CI on every push. A failing test blocks merge.
- Use `supertest` or Fastify's `.inject()` for HTTP endpoint testing.

---

## 11. CI/CD Patterns

**Pipeline stages (in order):**

1. **Install** -- `npm ci` (not `npm install`). Uses lockfile exactly.
2. **Lint** -- ESLint + Prettier check. Fail on any violation.
3. **Type Check** -- `tsc --noEmit`. Fail on any error.
4. **Unit Tests** -- Vitest or Jest. Fail on any failure or coverage below
   threshold.
5. **Integration Tests** -- Run against containerized dependencies. Fail on any
   failure.
6. **Build** -- Compile TypeScript to JavaScript. Verify the build succeeds.
7. **Security Scan** -- `npm audit --audit-level=high`. Fail on Critical or
   High.
8. **Deploy** -- Only after all previous stages pass.

**Rules:**
- CI uses the same Node.js version pinned in `.nvmrc`.
- No `--force` or `--legacy-peer-deps` in CI. Dependency conflicts are resolved
  in `package.json`, not papered over in the install command.
- Build artifacts (the `dist/` directory) are the deployment unit. Never deploy
  source TypeScript.

---

## Defaults

| Concern              | Default Choice            | Override Requires |
|----------------------|---------------------------|-------------------|
| Language             | TypeScript (strict)       | ADR               |
| Framework            | Fastify                   | ADR               |
| Logger               | Pino (JSON)               | ADR               |
| Validation           | Zod (config), Typebox/JSON Schema (routes) | ADR |
| Test Runner          | Vitest                    | ADR               |
| Linter / Formatter   | ESLint + Prettier         | Never             |
| Package Manager      | npm (lockfile committed)  | ADR               |
| Node Version Pinning | `.nvmrc` (LTS major)     | Never             |
| Module System        | ESM (`"type": "module"`)  | ADR               |
| Error Base Class     | `AppError` (see sec. 9)   | Never             |

---

## Do / Don't

### Do
- Pin exact dependency versions with `--save-exact`.
- Validate every environment variable at startup via Zod.
- Use structured logging (Pino) with static event messages and data-as-properties.
- Separate routes from handlers; keep handlers thin, push logic to services.
- Use `npm ci` in CI -- never `npm install`.
- Catch errors centrally; let individual handlers throw domain errors.
- Write integration tests against real dependencies using Testcontainers.
- Keep `.env.example` in sync with every env var the app reads.

### Don't
- Use `any`. Prefer `unknown` with narrowing.
- Use `console.log` in production code. Use the structured logger.
- Install packages globally. Use `npx` for one-off CLIs.
- Mock the database in integration tests.
- Use `--force` or `--legacy-peer-deps` to paper over dependency conflicts.
- Access `process.env` outside the config module.
- Use barrel files (`index.ts` re-exporting everything) unless the package is
  a public library -- they defeat tree-shaking and slow IDE indexing.
- Commit `.env` files. Ever.

---

## Common Pitfalls

1. **Unhandled promise rejections** -- A single forgotten `await` can crash the
   process in Node 22+. The `no-floating-promises` ESLint rule is your safety
   net; never disable it.
2. **Event-loop blocking** -- CPU-intensive synchronous work (JSON parsing large
   payloads, crypto) blocks all requests. Offload to worker threads or a queue.
3. **Memory leaks from closures** -- Closures capturing request-scoped data
   inside long-lived event listeners will leak. Use `WeakRef` or detach
   listeners explicitly.
4. **Implicit `undefined` from index access** -- Without
   `noUncheckedIndexedAccess`, `arr[0]` is typed as `T` instead of
   `T | undefined`. This hides real bugs.
5. **Lockfile drift** -- Running `npm install` on CI instead of `npm ci` lets
   the lockfile silently change, producing unreproducible builds.
6. **Over-mocking** -- Mocking every dependency in unit tests creates tests that
   pass even when the real code is broken. Prefer thin integration tests with
   `.inject()` / Testcontainers.
7. **Ignoring backpressure** -- Piping streams without honoring backpressure
   causes unbounded memory growth. Use `pipeline()` from `node:stream/promises`.

---

## Checklist

Use this checklist before opening a pull request on any Node.js service.

- [ ] `npm ci` installs cleanly with no warnings.
- [ ] `tsc --noEmit` reports zero errors.
- [ ] ESLint + Prettier pass with zero violations.
- [ ] No `any` types introduced (or each has a justifying comment).
- [ ] Every new env var is validated in `config/schema.ts` and documented in `.env.example`.
- [ ] New routes have request schema validation (Typebox / JSON Schema).
- [ ] Structured log entries use static messages with data-as-properties.
- [ ] Unit tests added/updated for changed business logic (>=80 % branch coverage).
- [ ] Integration tests cover new endpoints end-to-end.
- [ ] `npm audit` shows no Critical or High vulnerabilities.
- [ ] No secrets, tokens, or PII in logs or committed files.
- [ ] Error paths return the standard `AppError` JSON shape.
- [ ] `.nvmrc` matches the CI Node.js version.
