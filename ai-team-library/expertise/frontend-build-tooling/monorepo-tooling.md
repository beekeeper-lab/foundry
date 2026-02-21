# Monorepo Tooling

Standards for monorepo build orchestration, dependency management, and workspace structure.
Turborepo is the default orchestrator for new monorepos. Deviations require an ADR.

---

## Defaults

- **Orchestrator:** Turborepo — handles task scheduling, caching, and dependency graph.
- **Package manager:** pnpm with workspaces — strict dependency isolation, fast installs,
  content-addressable storage.
- **Workspace layout:** `apps/` for deployable applications, `packages/` for shared
  libraries. Each workspace has its own `package.json`, `tsconfig.json`, and test setup.
- **Task caching:** Remote caching enabled (Vercel Remote Cache or self-hosted) for
  CI and cross-developer cache sharing.
- **Versioning:** Changesets for versioning and publishing shared packages.

```
my-monorepo/
├── apps/
│   ├── web/                # Next.js / Vite app
│   │   ├── package.json
│   │   └── src/
│   └── api/                # Backend service
│       ├── package.json
│       └── src/
├── packages/
│   ├── ui/                 # Shared component library
│   │   ├── package.json
│   │   └── src/
│   ├── config-eslint/      # Shared ESLint config
│   │   └── package.json
│   └── config-typescript/  # Shared tsconfig bases
│       └── package.json
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

---

## Turborepo Configuration

```jsonc
// turbo.json — production-ready baseline
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json", "package.json"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tests/**", "vitest.config.*"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json"]
    }
  }
}
```

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

---

## Nx Configuration (Alternative)

For projects that need advanced dependency graph analysis, generators, or plugin
ecosystems:

```jsonc
// nx.json — baseline configuration
{
  "$schema": "https://nx.dev/reference/nx-json",
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["production", "^production"],
      "cache": true
    },
    "test": {
      "inputs": ["default", "^production"],
      "cache": true
    },
    "lint": {
      "inputs": ["default", "{workspaceRoot}/.eslintrc.json"],
      "cache": true
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "production": [
      "default",
      "!{projectRoot}/tests/**",
      "!{projectRoot}/**/*.spec.*"
    ],
    "sharedGlobals": []
  },
  "defaultBase": "main"
}
```

```jsonc
// project.json — per-project Nx configuration
{
  "name": "web",
  "sourceRoot": "apps/web/src",
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "outputs": ["{options.outputPath}"],
      "options": {
        "outputPath": "dist/apps/web"
      }
    },
    "dev": {
      "executor": "@nx/vite:dev-server",
      "options": {
        "buildTarget": "web:build"
      }
    },
    "test": {
      "executor": "@nx/vite:test",
      "options": {
        "passWithNoTests": true
      }
    }
  }
}
```

---

## Do / Don't

- **Do** define explicit `inputs` and `outputs` for every task in `turbo.json` so
  caching is accurate and effective.
- **Do** use `dependsOn: ["^build"]` to ensure dependencies are built before dependents.
- **Do** enable remote caching in CI to share build artifacts across pipeline runs.
- **Do** use `pnpm` with strict mode (`pnpm-workspace.yaml` + `shamefully-hoist=false`)
  to catch missing dependency declarations.
- **Do** keep shared packages small and focused — one concern per package.
- **Do** use TypeScript project references (`references` in `tsconfig.json`) alongside
  monorepo tooling for fast type-checking across packages.
- **Do** set up a `config-*` package pattern for shared ESLint, TypeScript, and Prettier
  configs.
- **Don't** put all code in a single package. If two apps share code, extract it to
  `packages/`.
- **Don't** allow circular dependencies between workspaces. Use `turbo ls --affected`
  or `nx graph` to visualize the dependency graph and catch cycles.
- **Don't** skip `--frozen-lockfile` in CI — it catches dependency drift.
- **Don't** use `*` workspace protocol versions in production. Pin to specific ranges
  (`workspace:^1.0.0`) for published packages.
- **Don't** cache tasks with non-deterministic outputs (e.g., tasks that read
  environment variables not listed in `globalDependencies`).

---

## Common Pitfalls

1. **Phantom dependencies.** A package imports a module it doesn't declare in its own
   `package.json`, relying on hoisting. Works locally, fails in CI or on another
   machine. Use `pnpm --strict-peer-dependencies` and lint with `eslint-plugin-import`.
2. **Cache poisoning.** Tasks produce different output based on environment variables
   or system state not tracked by the cache key. List all such inputs in
   `globalDependencies` or per-task `inputs`.
3. **Unbounded task graphs.** Running `turbo build` without `inputs`/`outputs` defined
   rebuilds everything on every change. Invest time in accurate task definitions.
4. **Shared config drift.** Each app defines its own ESLint/TypeScript config that
   slowly diverges. Extract shared configs into `packages/config-*` and extend them.
5. **Oversized shared packages.** A `packages/utils` that becomes a dumping ground for
   unrelated code. It forces all consumers to rebuild when anything changes. Split by
   domain: `packages/date-utils`, `packages/string-utils`.
6. **Ignoring the dependency graph.** Adding a dependency between packages without
   updating the orchestrator config leads to build ordering issues. Always verify with
   `turbo ls --affected` or `nx graph` after adding cross-package imports.
7. **Lock file conflicts.** Multiple developers adding dependencies in parallel cause
   constant merge conflicts in `pnpm-lock.yaml`. Rebase frequently and use
   `pnpm install --merge-git-branch-lockfiles` when available.

---

## Workspace Package Management

```jsonc
// Root package.json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "test": "turbo test",
    "typecheck": "turbo typecheck",
    "format": "prettier --write \"**/*.{ts,tsx,md}\""
  },
  "devDependencies": {
    "turbo": "^2.0.0",
    "prettier": "^3.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

```jsonc
// packages/ui/package.json — shared library example
{
  "name": "@repo/ui",
  "version": "0.0.0",
  "private": true,
  "sideEffects": false,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "lint": "eslint . --max-warnings 0",
    "test": "vitest run"
  },
  "devDependencies": {
    "@repo/config-eslint": "workspace:*",
    "@repo/config-typescript": "workspace:*",
    "tsup": "^8.0.0",
    "vitest": "^2.0.0"
  }
}
```

---

## Alternatives

| Tool             | When to Consider                                                    |
|------------------|---------------------------------------------------------------------|
| Nx               | Need generators, plugin ecosystem, or advanced affected analysis    |
| pnpm workspaces  | Simple monorepo without build orchestration (just dependency mgmt)  |
| npm workspaces   | Already on npm, minimal monorepo needs, no caching required         |
| Yarn workspaces  | Existing Yarn projects, need Plug'n'Play for strict isolation       |
| Lerna             | Legacy projects (now wraps Nx under the hood)                      |
| Bazel            | Very large monorepos (1000+ packages) needing hermetic builds       |
| Pants            | Python-heavy monorepos with mixed language support                  |

---

## Checklist

- [ ] Workspace layout follows `apps/` + `packages/` convention
- [ ] `pnpm-workspace.yaml` (or equivalent) defines all workspace paths
- [ ] `turbo.json` (or `nx.json`) defines tasks with explicit `inputs` and `outputs`
- [ ] `dependsOn: ["^build"]` set for tasks that consume built package outputs
- [ ] Remote caching configured for CI builds
- [ ] Shared ESLint, TypeScript, and Prettier configs extracted to `packages/config-*`
- [ ] No circular dependencies in the workspace graph (verified with graph tool)
- [ ] CI runs `--frozen-lockfile` to prevent dependency drift
- [ ] Every workspace package has its own `package.json` with correct dependency declarations
- [ ] `sideEffects` field set in shared library packages for tree-shaking
- [ ] Changesets configured for versioning shared packages (if publishing)
- [ ] Task graph verified after adding new cross-package dependencies
