# /lint Command

Run the JavaScript/TypeScript linter against the project.

## Usage

```
/lint [path] [--fix]
```

- `path` -- Optional file or directory (default: `src/`).
- `--fix` -- Apply safe autofixes.

## Process

1. **Detect tool** — Read the `scripts.lint` field in `package.json` (commonly `eslint`).
2. **Run** — `npm run lint` (or `pnpm run lint` / `yarn lint`); pass `-- --fix` if requested.
3. **Report** — Print violations grouped by rule; exit non-zero on errors.

## Examples

```
/lint
/lint src/components/
/lint --fix
```

## Notes

This command **invokes** the user-configured linter (config in `eslint.config.js` / `.eslintrc.*`). It does not install or configure ESLint.
