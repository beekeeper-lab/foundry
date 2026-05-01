# /dev Command

Start the project's development server with hot reload.

## Usage

```
/dev [args...]
```

- `args` -- Forwarded to the dev server.

## Examples

```
/dev
/dev --host 0.0.0.0
```

## Notes

This command **invokes** the user-configured dev script — read from `scripts.dev` (or `scripts.start`) in `package.json` (commonly `vite`, `next dev`, `webpack serve`). Uses `npm run dev` (or `pnpm dev` / `yarn dev` based on lockfile). Streams the dev server's output, including the local URL. Use `Ctrl+C` to stop. No paired skill.
