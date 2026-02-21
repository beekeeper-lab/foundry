# Frontend Bundlers

Standards for JavaScript/TypeScript bundling, tree-shaking, and code splitting.
Vite is the default bundler for new projects. Deviations require an ADR.

---

## Defaults

- **Bundler:** Vite 6.x (uses Rollup for production builds, esbuild for dev transforms).
- **Module format:** ESM for application code. Output both ESM and CJS for libraries.
- **Tree-shaking:** Enabled by default — mark packages `"sideEffects": false` in
  `package.json` unless they contain global CSS or polyfills.
- **Code splitting:** Use dynamic `import()` for route-level and feature-level splits.
  Vite handles chunk splitting automatically via Rollup's `manualChunks`.
- **Target:** `es2022` for modern browsers. Use `@vitejs/plugin-legacy` only when
  supporting browsers older than 2 years.
- **Dev server:** Vite's native ESM dev server with HMR. No bundling in development.

```typescript
// vite.config.ts — production-ready baseline
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "es2022",
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
        },
      },
    },
  },
});
```

---

## Do / Don't

- **Do** use Vite for new SPAs, SSR apps, and library builds.
- **Do** set `"sideEffects": false` (or list specific side-effect files) in every
  `package.json` to enable aggressive tree-shaking.
- **Do** use dynamic `import()` for routes and heavy feature modules to enable
  automatic code splitting.
- **Do** enable source maps in production for error tracking (`build.sourcemap: true`).
- **Do** analyze bundle size regularly with `rollup-plugin-visualizer` or
  `vite-bundle-analyzer`.
- **Do** set explicit `build.target` to avoid shipping unnecessary polyfills.
- **Don't** import entire libraries when you only need a few functions.
  `import { debounce } from "lodash-es"` not `import _ from "lodash"`.
- **Don't** use `require()` in application code — it prevents tree-shaking.
- **Don't** disable code splitting to "simplify" deployment. The performance cost
  far outweighs the convenience.
- **Don't** put application logic in Vite/Webpack config files.
- **Don't** use `eval()` or `new Function()` — it breaks CSP and defeats minification.
- **Don't** rely on barrel files (`index.ts` re-exports) in large codebases — they
  can defeat tree-shaking if the bundler cannot prove exports are side-effect-free.

---

## Common Pitfalls

1. **Barrel file bloat.** A single `import { Button } from "@ui"` that re-exports 200
   components pulls in every component if tree-shaking cannot eliminate side effects.
   Use direct path imports (`@ui/Button`) or verify `sideEffects: false` is set.
2. **Missing `sideEffects` field.** Without it, bundlers conservatively assume every
   module has side effects and skip tree-shaking. This is the single most common
   reason for bloated bundles.
3. **CJS dependencies breaking tree-shaking.** CommonJS modules cannot be statically
   analyzed. Prefer ESM-first packages. Use `vite-plugin-commonjs` or bundle-time
   conversion only as a last resort.
4. **Over-splitting.** Too many tiny chunks cause waterfall requests. Aim for chunks
   between 20 KB and 200 KB gzipped. Use `manualChunks` to group related vendor code.
5. **Dev/prod divergence.** Vite uses esbuild in dev and Rollup in production. Code
   that works in dev can fail in production due to Rollup's stricter handling of CJS
   and circular dependencies. Run production builds in CI on every PR.
6. **Unoptimized images and assets.** Bundlers handle JS well but images need separate
   optimization. Use `vite-plugin-imagemin` or a CDN-based image pipeline.
7. **Ignoring chunk hash invalidation.** Ensure output filenames include content hashes
   (`[name].[hash].js`) so browsers cache aggressively but invalidate on changes.

---

## Webpack Configuration (Legacy Projects)

For existing projects on Webpack 5 that cannot migrate to Vite immediately:

```javascript
// webpack.config.js — production baseline
const path = require("path");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");

module.exports = {
  mode: "production",
  entry: "./src/index.tsx",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].[contenthash].js",
    chunkFilename: "[name].[contenthash].js",
    clean: true,
  },
  optimization: {
    splitChunks: {
      chunks: "all",
      maxSize: 200_000, // bytes — target ~200 KB per chunk
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendor",
          chunks: "all",
        },
      },
    },
    usedExports: true,    // tree-shaking: mark unused exports
    sideEffects: true,    // tree-shaking: respect sideEffects field
    minimize: true,
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
  plugins: [
    // Run with ANALYZE=true to inspect bundle
    ...(process.env.ANALYZE ? [new BundleAnalyzerPlugin()] : []),
  ],
};
```

---

## Code Splitting Patterns

```typescript
// Route-level splitting with React.lazy
import { lazy, Suspense } from "react";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

```typescript
// Feature-level splitting — load heavy modules on demand
async function exportReport(data: ReportData) {
  const { generatePDF } = await import("./utils/pdf-generator");
  return generatePDF(data);
}
```

```typescript
// Prefetching critical routes for perceived performance
// Vite supports link preload hints automatically for dynamic imports.
// For manual control:
function prefetchRoute(path: string) {
  const link = document.createElement("link");
  link.rel = "modulepreload";
  link.href = path;
  document.head.appendChild(link);
}
```

---

## Alternatives

| Bundler   | When to Consider                                                  |
|-----------|-------------------------------------------------------------------|
| Webpack 5 | Existing large projects with complex loader pipelines             |
| esbuild   | Build tooling, dev-only transforms, or extreme speed requirements |
| Rollup    | Library builds requiring clean ESM output with minimal overhead   |
| Parcel    | Zero-config prototyping or small projects                         |
| Rspack    | Webpack-compatible projects that need faster builds (Rust-based)  |
| Turbopack | Next.js projects (integrated with Next.js 15+)                    |

---

## Checklist

- [ ] Vite (or chosen bundler) configured with explicit `build.target`
- [ ] `"sideEffects": false` set in `package.json` (or side-effect files listed)
- [ ] Dynamic `import()` used for route-level code splitting
- [ ] Output filenames include content hashes for cache busting
- [ ] Source maps enabled for production error tracking
- [ ] Bundle analyzer run and results reviewed (no unexpected large chunks)
- [ ] No `require()` calls in application source code
- [ ] Vendor chunks separated from application code
- [ ] Production build runs in CI on every pull request
- [ ] Chunk sizes are between 20 KB and 200 KB gzipped
- [ ] Images and static assets have a separate optimization pipeline
- [ ] No barrel files re-exporting more than 20 modules without `sideEffects: false`
