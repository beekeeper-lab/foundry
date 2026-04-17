# /dev Command

Start the project's development server with hot reload.

## Usage

```
/dev [args...]
```

- `args` -- Forwarded to the dev server.

## Process

1. **Detect script** — Read the `scripts.dev` (or `scripts.start`) field in `package.json` (commonly `vite`, `next dev`, `webpack serve`).
2. **Run** — `npm run dev` (or `pnpm dev` / `yarn dev` based on lockfile).
3. **Report** — Stream the dev server's output, including the local URL.

## Examples

```
/dev
/dev --host 0.0.0.0
```

## Notes

This command **invokes** the user-configured dev script declared in `package.json`. It does not install or configure it. Use `Ctrl+C` to stop.
