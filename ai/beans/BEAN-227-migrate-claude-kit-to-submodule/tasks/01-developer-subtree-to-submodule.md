# Task 01: Remove Subtree, Add Submodule, Create Link Script

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Remove the git subtree integration, add `.claude/kit` as a submodule, create the `claude-link.sh` assembly script, and establish the `.claude/local/` directory for project-specific assets.

## Inputs

- `ai/outputs/architect/claude-kit-submodule-spec.md` — target architecture
- Current `.claude/` directory contents
- Upstream claude-kit repo structure (`.claude/shared/{agents,commands,skills,hooks,settings.json}`)

## Acceptance Criteria

- [ ] `claude-kit` git remote removed
- [ ] `.claude/kit` exists as a git submodule
- [ ] `.gitmodules` correctly references `.claude/kit`
- [ ] `.claude/local/` directories created for project-specific assets
- [ ] `scripts/claude-link.sh` creates assembly symlinks
- [ ] `.claude/{commands,skills,agents}` contain working symlinks to kit content
- [ ] `.claude/hooks` symlinked to kit hooks
- [ ] `.claude/settings.json` updated for correct hook paths

## Definition of Done

- `git submodule update --init --recursive` restores `.claude/kit` from scratch
- `scripts/claude-link.sh` is idempotent and executable
- All symlinks resolve correctly
