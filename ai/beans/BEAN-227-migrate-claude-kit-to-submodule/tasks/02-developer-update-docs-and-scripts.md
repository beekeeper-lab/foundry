# Task 02: Update Documentation and Scripts

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Update CLAUDE.md, docs/claude-kit.md, and lifecycle scripts (claude-sync.sh, claude-publish.sh, post-checkout) to reflect the submodule pattern.

## Inputs

- `CLAUDE.md` — current subtree documentation
- `docs/claude-kit.md` — current deep-dive docs
- `scripts/claude-sync.sh`, `scripts/claude-publish.sh`, `scripts/githooks/post-checkout`

## Acceptance Criteria

- [ ] `CLAUDE.md` documents submodule workflow (not subtree)
- [ ] `docs/claude-kit.md` updated for submodule pattern
- [ ] `scripts/claude-sync.sh` uses submodule update + link rebuild
- [ ] `scripts/claude-publish.sh` pushes submodule correctly
- [ ] `scripts/githooks/post-checkout` initializes submodule on checkout

## Definition of Done

- No references to "subtree" remain in documentation (except historical notes)
- Scripts are executable and handle edge cases (missing submodule, first clone)
