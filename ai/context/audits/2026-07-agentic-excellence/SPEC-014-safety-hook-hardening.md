# SPEC-014: Safety hook hardening: false positives, defense in depth, honest claims

- **Priority:** P1
- **Effort:** M
- **Area:** kit
- **Depends on:** none (complements SPEC-004/SPEC-015 hook work)
- **Status:** Proposed

## Problem

The kit's two safety hooks are regex filters over command strings and file paths. As shipped they fail in both directions: they block routine legitimate operations (updating a feature branch from main, writing `.env.example`, cleaning up a scratch file), and they miss trivial variants of exactly the dangerous operations they exist to stop (refspec pushes to main, variable indirection, `bash -c` wrapping). Worse, the kit's CLAUDE.md tells every downstream project these hooks "cannot be bypassed" — a false safety claim that invites over-reliance. The hooks are pure Python functions and currently have zero tests.

## Evidence

False positives:
- `.claude/shared/hooks/bash_safety.py:49` — `git\s+merge\s+.*\s+main([\s;|&]|$)` blocks `git merge origin/main` on a feature branch — the standard way to update a branch, which the kit's own PR workflow requires.
- `bash_safety.py:60-70` — any `rm` not matching the hard-coded safe list (node_modules, dist, `*.log`…) is blocked, including `rm -f scratch.txt`; the "safe" pattern `rm\s+[^-]` ironically allows plain `rm file` but the flagged form `rm -f file` of the same deletion is blocked.
- `.claude/shared/hooks/write_safety.py:70` — `basename.startswith(".env")` blocks `.env.example` / `.env.template` / `.env.sample`, files that are conventionally committed (the Foundry repo itself ships `.env.example`).
- `write_safety.py:41-42` — bare substring `"/etc"` matches any project path containing `/etc` (e.g. `myapp/etc/config.yml`).

Bypasses (all evade the current regexes):
- `git push origin +feature:main` and `git push origin HEAD:main` — refspec forms not matched by `bash_safety.py:45-48`.
- `b=main; git push origin $b`, `git${IFS}push`, multi-line commands, `bash -c "…"`, `eval`, `xargs`.
- `.claude/shared/CLAUDE.md:43` — "These are enforced via `settings.json` PreToolUse hooks and cannot be bypassed." False, per the above.

No tests: `grep -rn bash_safety tests/` → nothing.

## Proposed change

1. **Fix the false positives precisely:**
   - Merge guard: block only `git merge` **while the current branch is main/master** (the hook can run `git branch --show-current`, as the inline settings.json guard already does) — merging *from* main into a feature branch becomes legal.
   - `rm` policy: allow `rm`/`rm -f` of paths inside the repo working tree that are not tracked-sensitive; keep hard blocks for `-r` outside the safe list, `/`, `~`, `$HOME`. Reduce the soft-block to genuinely risky shapes instead of "anything with a flag."
   - `.env` guard: exempt `.env.example|.env.template|.env.sample|.env.dist` (exact-suffix allowlist before the `startswith` check).
   - `/etc` guard: anchor to absolute paths (`normalized_path.startswith("/etc/")` or `== "/etc"`), not substring.
2. **Strengthen matching where cheap (no parser project):** add refspec patterns (`git push … [+]?[^ ]*:(main|master)\b`, `HEAD:main`), and block `git push` with `--force-with-lease` to protected branches. Explicitly do NOT chase shell-metaprogramming completeness — that's what layer 3 is for.
3. **Defense in depth via permissions:** add a `permissions.deny` block to kit `settings.json` for the protected-branch push/force-push shapes and sensitive-file reads, so there are two independent layers (permission rules + hook). Coordinate with SPEC-015 (which adds the missing `permissions` block generally).
4. **Honest documentation:** rewrite `.claude/shared/CLAUDE.md:43` to: hooks are one layer of defense in depth; they block common accidents, not determined evasion; branch protection on the remote (GitHub rules) remains the authoritative guard. Add a short "known limits" section to each hook's docstring.
5. **Unit-test the hook scripts.** Refactor each script's checks into pure functions (`check_command(cmd) -> Verdict`), keep the `main()` stdin wrapper thin, and add a test matrix: every documented block fires; every documented false positive from this spec now passes; every new refspec bypass is caught. These tests live in the kit repo (and run in Foundry's suite via the submodule path).

## Out of scope

- The unwired doc-hooks (`hook-policy.md`, `pre-commit-lint.md`, `post-task-qa.md`) — SPEC-015.
- The generator's hook-pack registry duplication — SPEC-004.
- Sandboxing/containerization strategies.

## Acceptance criteria

- [ ] (test:tests/test_bash_safety.py) Matrix passes: `git merge origin/main` on feature branch ALLOWED; same command on main BLOCKED; `git push origin +f:main`, `HEAD:main` BLOCKED; `rm -f scratch.txt` in-repo ALLOWED; `rm -rf /` BLOCKED
- [ ] (test:tests/test_write_safety.py) `.env.example` ALLOWED; `.env` BLOCKED; `myapp/etc/config.yml` ALLOWED; `/etc/hosts` BLOCKED
- [ ] (file-contains:.claude/shared/settings.json::deny) permissions.deny defense-in-depth entries present
- [ ] (file-contains:.claude/shared/CLAUDE.md::defense in depth) "Cannot be bypassed" claim replaced
- [ ] (lint:.claude/shared/hooks/) Ruff clean on the refactored hooks
- [ ] manual: One week of normal Foundry work produces zero safety-hook false-positive blocks (track via the hooks' stderr messages)

## Files to touch

- `.claude/shared/hooks/bash_safety.py`, `.claude/shared/hooks/write_safety.py` (kit repo — publish via claude-publish flow)
- `.claude/shared/settings.json`, `.claude/shared/CLAUDE.md`
- `tests/test_bash_safety.py`, `tests/test_write_safety.py` (new; location per kit test convention)
