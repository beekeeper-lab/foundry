# SPEC-025: claude-sync.sh robustness and portability

- **Priority:** P2
- **Effort:** M
- **Area:** kit
- **Depends on:** none
- **Status:** Proposed

## Problem

`claude-sync.sh` (the kit's sync engine, wrapped by each project's `scripts/claude-sync.sh`) rebuilds the entire `.claude/{agents,commands,skills,hooks}` discovery layer destructively and non-atomically, uses GNU-only tooling, duplicates settings arrays on every re-merge, clobbers projects' own git hooks, symlinks a non-skill helper package as a skill, and never honors local hook overrides because `settings.json` bypasses the symlink layer entirely. Any of these can leave a consuming project with a broken or degraded Claude Code configuration after a routine sync.

## Evidence

All references are to `.claude/shared/scripts/claude-sync.sh` (the project-root `scripts/claude-sync.sh` is a 3-line exec wrapper) and `.claude/shared/settings.json`:

- `:78-90` — `clean_generated()` does `rm -rf "$dir"` then rebuilds. A crash mid-run or two concurrent runs (manual + the post-merge/post-checkout git hooks) leaves the discovery layer empty or half-built.
- `:54` — `realpath --relative-to=` and `:72` `ln -sfn` are GNU coreutils; stock macOS `realpath` lacks `--relative-to`, so the script fails on non-GNU systems the kit claims to support.
- `:303-304` — `deep_merge` concatenates lists (`result[key] + value`); a local `settings.json` carrying hooks/permissions arrays gets its entries appended again on every re-sync → duplicate hook registrations. (Mitigated today only because merge output isn't itself re-read as input; any project committing a merged file regresses.)
- `:363-388` — `install_git_hooks()` unconditionally `cp`s over `post-merge`/`post-checkout` in `$GIT_DIR/hooks`, destroying any project-authored hook. No backup, no chaining.
- `:368` — `project_hooks_src` assigned, never used: project-level githooks are silently not installed despite the comment.
- `:186,201` — `sync_skills()` skips only the dir literally named `internal`, so `skills/_media_lib/` (a Python helper package with no SKILL.md) is symlinked into `.claude/skills/_media_lib` and presented to Claude Code as a skill.
- `.claude/shared/settings.json:18,27,36,47` — hooks are invoked via `$CLAUDE_PROJECT_DIR/.claude/shared/hooks/<name>.py`, a hard path into the submodule. `sync_files "hooks"` (`:399`) dutifully builds `.claude/hooks/` with local-overrides-shared semantics, but nothing reads it — a project dropping an override into `.claude/local/hooks/` is silently ignored.

## Proposed change

1. **Atomic rebuild:** build each generated dir as `<dir>.tmp.$$`, then `rm -rf <dir> && mv <dir>.tmp.$$ <dir>` (or symlink-swap). Add a simple lockfile (`mkdir`-based) so concurrent syncs serialize instead of interleaving.
2. **Portability:** replace `realpath --relative-to` with a POSIX-safe helper (python3 one-liner fallback: `python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))'`). Verify on macOS (BSD userland) in CI or a documented manual check.
3. **Merge dedup:** in `deep_merge`, dedupe list entries by stable identity — for `hooks.*` arrays key on `(matcher, command)`; for permission arrays key on the literal string. Local entries win on conflict.
4. **Git-hook chaining:** before installing, if an existing hook file is present and not kit-generated (detect via a marker comment), rename it to `<name>.local` and generate a kit hook that execs both. Also actually install `project_hooks_src` hooks (or delete the dead code and the claim).
5. **Skip underscore-prefixed dirs** in `sync_skills()` (`[ "${name#_}" = "$name" ] || continue`) so `_media_lib` and future helpers are never exposed as skills.
6. **Honor local hook overrides:** change `settings.json` hook commands to `$CLAUDE_PROJECT_DIR/.claude/hooks/<name>.py` (the synced layer, where local-overrides-shared is already implemented), and keep `sync_files "hooks"` as the resolver. This makes the kit's documented override promise true for hooks.
7. **`--check` mode parity:** extend CI check mode to detect duplicated merged-settings entries and stray underscore skills.

## Out of scope

- Replacing the whole sync/symlink mechanism with plugin distribution (SPEC-026 decides that; this spec keeps current consumers working meanwhile).
- Hook content/behavior changes (SPEC-014, SPEC-015).

## Acceptance criteria

- [ ] `manual:` killing the sync mid-run leaves the previous `.claude/commands/` intact (verify by inserting a sleep and interrupting).
- [ ] `manual:` running sync twice with a local `settings.json` containing a hooks array produces no duplicate hook entries in `.claude/settings.json`.
- [ ] `file:` `.claude/skills/_media_lib` does not exist after sync, while `.claude/skills/generate-image` does.
- [ ] `manual:` a pre-existing user `post-merge` hook still executes after sync installs the kit hook.
- [ ] `file-contains:` `.claude/shared/settings.json` references `.claude/hooks/` (synced layer), not `.claude/shared/hooks/`.
- [ ] `manual:` a file at `.claude/local/hooks/bash_safety.py` is the one executed on the next Bash tool call after sync.
- [ ] `manual:` script passes `bash -n` and ShellCheck with no errors; dead `project_hooks_src` path resolved (used or removed).

## Files to touch

- `.claude/shared/scripts/claude-sync.sh` (kit repo — via kit PR flow)
- `.claude/shared/settings.json` (hook command paths)
- `.claude/shared/scripts/githooks/` (chaining-aware hook templates)
- `.claude/shared/README.md` (override semantics, macOS support note)
