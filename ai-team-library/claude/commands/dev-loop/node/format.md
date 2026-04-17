# /format Command

Format JavaScript/TypeScript source files according to the project's style.

## Usage

```
/format [path] [--check]
```

- `path` -- Optional file or directory (default: `src/`).
- `--check` -- Report formatting drift without writing changes.

## Process

1. **Detect tool** — Read the `scripts.format` field in `package.json` (commonly `prettier`).
2. **Run** — `npm run format` (or equivalent); pass `--check` if requested.
3. **Report** — Print the list of files changed (or that would change in `--check` mode).

## Examples

```
/format
/format src/components/
/format --check
```

## Notes

This command **invokes** the user-configured formatter (config in `.prettierrc.*` or equivalent). It does not install or configure it.
