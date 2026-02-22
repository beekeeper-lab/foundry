# Task 03: Verify Migration

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01, 02 |
| **Status** | Done |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Verify all acceptance criteria: symlinks resolve, commands/skills/agents/hooks are discoverable, scripts work, documentation is accurate.

## Inputs

- Bean acceptance criteria
- `.claude/` directory post-migration
- `scripts/claude-link.sh`, `claude-sync.sh`, `claude-publish.sh`
- `.gitmodules`

## Acceptance Criteria

- [ ] All symlinks in `.claude/{commands,skills,agents,hooks}` resolve to real files
- [ ] `.gitmodules` correctly references `.claude/kit`
- [ ] `settings.json` hook paths are valid
- [ ] `scripts/claude-link.sh` is idempotent (run twice, same result)
- [ ] `scripts/claude-sync.sh` runs without error
- [ ] No subtree references remain in active documentation
- [ ] Tests still pass (`uv run pytest`)

## Definition of Done

- All checks pass with concrete evidence documented
