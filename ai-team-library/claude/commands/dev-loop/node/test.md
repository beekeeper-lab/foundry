# /test Command

Run the project's JavaScript/TypeScript test suite.

## Usage

```
/test [path] [--watch]
```

- `path` -- Optional file or directory to scope the run.
- `--watch` -- Re-run tests on file changes (if the runner supports it).

## Examples

```
/test
/test src/auth/
/test --watch
```

## Notes

This command **invokes** the user-configured test runner — read from `scripts.test` in `package.json` (commonly `vitest`, `jest`, or `node --test`). Uses `npm test` (or `pnpm test` / `yarn test` based on lockfile). Surfaces failures with file path, line number, and assertion message. No paired skill.
