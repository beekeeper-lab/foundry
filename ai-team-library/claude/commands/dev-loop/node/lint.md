# /lint Command

Run the JavaScript/TypeScript linter against the project.

## Usage

```
/lint [path] [--fix]
```

- `path` -- Optional file or directory (default: `src/`).
- `--fix` -- Apply safe autofixes.

## Examples

```
/lint
/lint src/components/
/lint --fix
```

## Notes

This command **invokes** the user-configured linter — read from `scripts.lint` in `package.json` (commonly `eslint`). Uses `npm run lint` (or `pnpm run lint` / `yarn lint`); passes `-- --fix` if requested. Config in `eslint.config.js` / `.eslintrc.*`. No paired skill.
