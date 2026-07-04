---
id: frontend-build-tooling
category: Architecture & Patterns
entry: true
last-reviewed: 2026-07
---

# Frontend Build Tooling Conventions

## Category
Architecture & Patterns

These conventions cover JavaScript/TypeScript bundling, tree-shaking, code
splitting, and monorepo build orchestration. Vite is the default bundler and
Turborepo the default monorepo orchestrator; deviations require an ADR.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| Bundler | Vite 6.x (Rollup prod builds, esbuild dev) | Webpack 5 (existing complex pipelines); Rollup (library builds); Rspack/Turbopack |
| Module format | ESM for app code; ESM + CJS output for libraries | — |
| Build target | `es2022` | `@vitejs/plugin-legacy` only for browsers older than 2 years |
| Code splitting | Dynamic `import()` at route and feature level | `manualChunks` for vendor grouping |
| Tree-shaking | `"sideEffects": false` in every `package.json` (or list side-effect files) | — |
| Source maps | Enabled in production (`build.sourcemap: true`) | — |
| Monorepo orchestrator | Turborepo | Nx (generators, plugins, affected analysis); Bazel (1000+ packages) |
| Package manager | pnpm workspaces, strict mode | npm/Yarn workspaces for minimal needs |
| Workspace layout | `apps/` (deployables) + `packages/` (shared libs) | — |
| Versioning | Changesets for published shared packages | — |
| Caching | Remote cache (Vercel or self-hosted) for CI and cross-developer sharing | — |

---

## 1. Bundling and Tree-Shaking

- Set `"sideEffects": false` in every `package.json` — its absence is the single
  most common reason for bloated bundles (bundlers assume every module has side
  effects and skip tree-shaking).
- Import narrowly: `import { debounce } from "lodash-es"`, never a whole
  library. No `require()` in application code — it prevents tree-shaking.
- Prefer ESM-first dependencies; CJS modules cannot be statically analyzed.
- Avoid barrel files re-exporting large module counts unless `sideEffects` is
  verifiably false; prefer direct path imports (`@ui/Button`).
- Set explicit `build.target`; output filenames must include content hashes
  (`[name].[hash].js`) for cache busting.

Full detail: `bundlers.md`

---

## 2. Code Splitting

- Split at route level (`React.lazy` + `Suspense`) and load heavy feature
  modules on demand via dynamic `import()`.
- Aim for chunks between 20 KB and 200 KB gzipped — over-splitting causes
  waterfall requests; use `manualChunks` to group related vendor code.
- Never disable code splitting to "simplify" deployment.
- Analyze bundles regularly with `rollup-plugin-visualizer` or
  `vite-bundle-analyzer`.

Full detail: `bundlers.md` (Code Splitting Patterns, Webpack baseline for legacy projects)

---

## 3. Monorepo Structure

- Layout: `apps/` for deployable applications, `packages/` for shared
  libraries; each workspace owns its `package.json`, `tsconfig.json`, and tests.
- Keep shared packages small and focused — one concern per package. Split
  dumping-ground `utils` packages by domain.
- Extract shared ESLint/TypeScript/Prettier configs into `packages/config-*`
  and extend them everywhere.
- No circular dependencies between workspaces — verify with `turbo ls
  --affected` or `nx graph` after adding cross-package imports.
- Use TypeScript project references alongside the orchestrator for fast
  cross-package type-checking.

Full detail: `monorepo-tooling.md`

---

## 4. Task Orchestration and Caching

- Define explicit `inputs` and `outputs` for every task in `turbo.json`;
  without them every change rebuilds everything.
- Use `dependsOn: ["^build"]` so dependencies build before dependents.
- Enable remote caching in CI; never cache tasks with non-deterministic
  outputs — list environment inputs in `globalDependencies`.
- CI installs with `--frozen-lockfile` to catch dependency drift.
- Pin workspace protocol versions (`workspace:^1.0.0`) for published packages,
  not `*`.

Full detail: `monorepo-tooling.md` (Turborepo and Nx baselines)

---

## Do / Don't

**Do:**
- Run the production build in CI on every PR — dev (esbuild) and prod (Rollup)
  behave differently around CJS and circular dependencies.
- Enable production source maps for error tracking.
- Use pnpm strict mode to catch undeclared (phantom) dependencies.
- Review bundle-analyzer output when adding significant dependencies.

**Don't:**
- Put application logic in Vite/Webpack config files.
- Use `eval()` or `new Function()` — breaks CSP and defeats minification.
- Rely on hoisting for imports a package doesn't declare.
- Put all code in one package — shared code between apps belongs in `packages/`.

---

## Common Pitfalls

1. **Missing `sideEffects` field** — bundlers conservatively skip tree-shaking;
   this alone can double bundle size.
2. **Barrel file bloat** — one import from a 200-component re-export pulls in
   everything when side-effect freedom can't be proven.
3. **Dev/prod divergence** — code that works under esbuild dev fails under
   Rollup production builds; catch it in CI.
4. **Phantom dependencies** — undeclared imports work locally via hoisting,
   fail in CI; use strict pnpm + `eslint-plugin-import`.
5. **Cache poisoning** — task output depends on env vars not in the cache key;
   list them in `globalDependencies` or per-task `inputs`.
6. **Unbounded task graphs** — no `inputs`/`outputs` means zero cache hits and
   full rebuilds on every change.

---

## Checklist

- [ ] Vite configured with explicit `build.target` and production source maps
- [ ] `"sideEffects"` set correctly in every `package.json`
- [ ] Dynamic `import()` for routes and heavy features; chunks 20-200 KB gzipped
- [ ] Content hashes in output filenames; no `require()` in app source
- [ ] Bundle analyzer reviewed; production build runs in CI on every PR
- [ ] `apps/` + `packages/` layout; shared configs in `packages/config-*`
- [ ] `turbo.json` tasks have explicit `inputs`/`outputs` and `dependsOn: ["^build"]`
- [ ] Remote caching enabled; no non-deterministic cached tasks
- [ ] CI uses `--frozen-lockfile`; no circular workspace dependencies
- [ ] Changesets configured if shared packages are published
