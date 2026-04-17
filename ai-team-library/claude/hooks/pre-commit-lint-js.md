# Hook Pack: Pre-Commit Lint (JS / TypeScript)

## Category
code-quality

## Purpose

Enforces JavaScript / TypeScript code quality before every commit. Replaces
the Python-oriented `pre-commit-lint` pack on projects whose primary stack is
React, TypeScript, Node, React Native, or general frontend build tooling.

## Hooks

| Hook Name | Trigger | Check | Pass Criteria | Fail Action |
|-----------|---------|-------|---------------|-------------|
| `format-check` | `pre-commit` | `prettier --check` on staged files | Zero formatting violations | Block commit; list files needing formatting |
| `lint-check` | `pre-commit` | `eslint` on staged files | Zero error-severity findings | Block commit; list violations |
| `type-check` | `pre-commit` | `tsc --noEmit` | No new type errors introduced | Block commit; list type errors |

## Configuration

- **Default mode:** enforcing
- **Timeout:** 60 seconds per hook (type-check: 180 seconds for large codebases)
- **Customization:** Projects may disable individual hooks via composition spec.
  A JS-only project without TypeScript should drop `type-check`.

## Posture Compatibility

| Posture | Included | Default Mode |
|---------|----------|--------------|
| `baseline` | Yes | enforcing |
| `hardened` | Yes | enforcing |
| `regulated` | Yes | enforcing |

## Stack Signals

Added by default when the composition includes any of:
`react`, `typescript`, `node`, `react-native`, `frontend-build-tooling`.
