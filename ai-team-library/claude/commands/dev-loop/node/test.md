# /test Command

Run the project's JavaScript/TypeScript test suite.

## Usage

```
/test [path] [--watch]
```

- `path` -- Optional file or directory to scope the run.
- `--watch` -- Re-run tests on file changes (if the runner supports it).

## Process

1. **Detect runner** — Read the `scripts.test` field in `package.json` (commonly `vitest`, `jest`, or `node --test`).
2. **Run** — `npm test` (or `pnpm test` / `yarn test` based on lockfile).
3. **Report** — Surface failures with file path, line number, and the assertion message.

## Examples

```
/test
/test src/auth/
/test --watch
```

## Notes

This command **invokes** the user-configured test runner declared in `package.json`. It does not install or configure it.
