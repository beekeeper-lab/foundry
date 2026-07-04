---
name: build
description: "Build the project's production bundle."
---

# /build Command

Build the project's production bundle.

## Usage

```
/build [--analyze]
```

- `--analyze` -- Emit bundle analysis output if the build tool supports it.

## Examples

```
/build
/build --analyze
```

## Notes

This command **invokes** the user-configured build script — read from `scripts.build` in `package.json` (commonly `vite build`, `tsc -b`, `next build`, or `webpack`). Uses `npm run build` (or `pnpm run build` / `yarn build` based on lockfile). Prints artifact sizes and warnings. No paired skill.
