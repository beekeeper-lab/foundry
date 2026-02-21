# /deploy Command

Validates the `main` branch, runs tests, and creates a version tag. With trunk-based development, all work is already on `main` via feature branch merges — deploy simply tags a release point.

## Usage

```
/deploy [--tag <version>]
```

- `--tag <version>` -- Optional. Tag the current commit with a version (e.g., `v1.2.0`). If omitted, auto-generates from date: `deploy-YYYY-MM-DD`.

| Command | What It Does |
|---------|-------------|
| `/deploy` | Validate main, run tests, tag with date-based label |
| `/deploy --tag v2.0.0` | Validate main, run tests, tag with version |

## Process

1. **Ensure on `main` branch** — Run `git branch --show-current`. If not on `main`, display error and stop.
2. **Check for uncommitted changes** — if dirty, prompt: **Commit** (stage + commit), **Stash** (stash, restore at end), or **Abort**
3. **Pull latest** — `git pull origin main`
4. **Run tests** (`uv run pytest`) and **ruff** (`uv run ruff check`) — stop if they fail
5. **Build release notes** from bean commits since the last deploy tag in `git log <last-tag>..HEAD`
6. **One approval prompt** — user says "go", or "abort"
7. **Tag** — Create annotated tag: `git tag -a <version> -m "Deploy: <date> — <bean list>"`
8. **Push tag** — `git push origin <version>`
9. **Clean up** — Delete merged feature branches (local + remote) that are fully merged into `main`
10. **Report** — Tag name, commit hash, beans deployed, branches deleted

## Examples

```
/deploy              # Validate and tag with date-based label
/deploy --tag v2.0.0 # Validate and tag with version number
```

**Approval prompt:**
```
===================================================
DEPLOY: Tag main as deploy-2026-02-21
===================================================

Beans since last deploy: BEAN-029, BEAN-030, BEAN-033
Tests: 750 passed, 0 failed
Ruff: clean

Post-tag: 3 merged feature branches will be deleted

On "go": create tag, push it, delete branches,
restore working tree. No further prompts.
===================================================
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Not on main | Switch to main and retry |
| Nothing to deploy | No new commits since last tag — report and exit |
| Tests fail | Report failures, stop. Fix on a feature branch first. |
| Tag already exists | Report error, suggest a different tag name |
| Uncommitted changes | Prompted to commit, stash, or abort before proceeding |
| User aborts | Restore stash, return to original state |
| Command blocked by sandbox | Prints exact command for manual execution, continues |
