# Task 01: Create All Shell Scripts and Documentation

| Field | Value |
|-------|-------|
| **Task** | 01-developer-create-scripts |
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-22 02:50 |
| **Completed** | 2026-02-22 02:51 |
| **Duration** | 1m |

## Goal

Create the four deliverables: `scripts/githooks/post-checkout`, `scripts/claude-sync.sh`, `scripts/claude-publish.sh`, and `docs/claude-kit.md`. All scripts must support dual-pattern detection (submodule at `.claude/kit/` vs subtree at `.claude/`) and use relative paths.

## Inputs

- Bean scope and acceptance criteria in `bean.md`
- Existing `.claude/` directory structure (subtree pattern)
- Existing `docs/` directory
- CLAUDE.md subtree instructions (for reference)

## Acceptance Criteria

- [ ] `scripts/githooks/post-checkout` created, executable, fires only on branch checkouts (flag=1)
- [ ] Hook detects submodule vs subtree mode via path checks
- [ ] Hook self-heals `.claude/kit` in submodule mode; warns in subtree mode
- [ ] Hook calls `scripts/claude-sync.sh` if available and executable
- [ ] `scripts/claude-sync.sh` created, executable, installs hooks from `scripts/githooks/` into `.git/hooks/`
- [ ] claude-sync.sh syncs `.claude/` per detected mode (submodule update or subtree pull)
- [ ] `scripts/claude-publish.sh` created, executable, pushes `.claude/` first then main repo
- [ ] claude-publish.sh aborts main push on `.claude/` push failure
- [ ] claude-publish.sh prints clear success/failure messages
- [ ] `docs/claude-kit.md` documents both patterns and the two-commit workflow
- [ ] All scripts pass `bash -n` syntax check
- [ ] All scripts use relative paths only
- [ ] Post-checkout hook installed into `.git/hooks/post-checkout` immediately

## Definition of Done

All four files exist, are executable (scripts), pass syntax check, and the post-checkout hook is active in `.git/hooks/`.
