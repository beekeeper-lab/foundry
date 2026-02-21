# /git-status Command

Show the sync status of local branches against their remote counterparts, focused on `main` and `test`.

## Usage

```
/git-status
```

## Process

1. **Fetch latest refs** — Run `git fetch origin` to get up-to-date remote refs without changing any local branches.
2. **Current branch** — Run `git branch --show-current` and report it.
3. **Working tree status** — Run `git status --short`. If clean, report "Clean". If dirty, list the changed files.
4. **Compare `main`** — Run `git rev-list --left-right --count origin/main...main`.
   - Parse the output as `<behind>\t<ahead>`.
   - Report: "main: N ahead, M behind origin/main" (or "in sync" if both are 0).
5. **Compare `test`** — Run `git rev-list --left-right --count origin/test...test`.
   - Same format as above.
   - If the local `test` branch doesn't exist, report "test: no local branch (remote exists at `<short-hash>`)".
6. **Compare `main` vs `test`** — Run `git rev-list --left-right --count origin/test...origin/main`.
   - Report: "origin/main is N commits ahead of origin/test" (or "in sync" if both are 0).
   - This shows whether a `/deploy` (test → main promotion) is needed or if there's unreleased work on `test`.

## Output Format

```
Git Status
──────────
Branch:    main
Working tree: Clean

main       ✓ In sync with origin/main
test       ✓ In sync with origin/test
main↔test  origin/main is 2 commits ahead of origin/test

```

Use ✓ for in-sync and ⚠ for out-of-sync. Keep the output concise — no extra explanation needed unless something is wrong.
