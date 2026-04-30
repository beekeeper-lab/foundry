# /format Command

Format JavaScript/TypeScript source files according to the project's style.

## Usage

```
/format [path] [--check]
```

- `path` -- Optional file or directory (default: `src/`).
- `--check` -- Report formatting drift without writing changes.

## Examples

```
/format
/format src/components/
/format --check
```

## Notes

This command **invokes** the user-configured formatter — read from `scripts.format` in `package.json` (commonly `prettier`). Uses `npm run format` (or equivalent); passes `--check` if requested. Config in `.prettierrc.*` or equivalent. No paired skill.
