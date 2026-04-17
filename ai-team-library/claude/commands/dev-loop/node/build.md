# /build Command

Build the project's production bundle.

## Usage

```
/build [--analyze]
```

- `--analyze` -- Emit bundle analysis output if the build tool supports it.

## Process

1. **Detect script** — Read the `scripts.build` field in `package.json` (commonly `vite build`, `tsc -b`, `next build`, or `webpack`).
2. **Run** — `npm run build` (or `pnpm run build` / `yarn build` based on lockfile).
3. **Report** — Print artifact sizes and any warnings/errors.

## Examples

```
/build
/build --analyze
```

## Notes

This command **invokes** the user-configured build script declared in `package.json`. It does not install or configure it.
