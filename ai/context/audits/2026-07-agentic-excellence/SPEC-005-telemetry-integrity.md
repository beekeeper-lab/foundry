# SPEC-005: Telemetry integrity: fix Duration computation and checkpoint race

- **Priority:** P0
- **Effort:** S
- **Area:** kit
- **Depends on:** none
- **Status:** Proposed

## Problem

Every bean's `Duration` field is stamped by `telemetry-stamp.py`, which prefers `git_branch_duration()` — elapsed time from the first commit on the branch to **now** — over the Started→Completed delta it also knows how to compute. On long-lived or rebased branches this produces absurd values: BEAN-277 records Started 15:12 / Completed 15:26 (14 minutes) but Duration `1578h 19m`; BEAN-278 records 18 minutes real vs `1588h 13m` stamped. 62+ beans carry corrupted durations, and since duration feeds cost-per-bean reasoning and `/orchestration-report`, every downstream metric built on it is meaningless.

Separately, the hook's token checkpoint is a single global file `/tmp/.foundry-telemetry-checkpoint.json`. Under parallel workers (`/long-run --fast N`, `/spawn-bean --count N`) every worker reads and clobbers the same checkpoint, cross-contaminating token deltas between concurrently running beans.

## Evidence

- `.claude/shared/hooks/telemetry-stamp.py:222-269` — `git_branch_duration()` computes `datetime.now(timezone.utc) - first_commit_after_merge_base` (lines 259-266).
- `.claude/shared/hooks/telemetry-stamp.py:1286` — `duration = git_branch_duration() or format_duration(cur_started, now)`: the git path wins whenever it returns anything; the correct Started→Completed function (`format_duration`, lines 208-219) is only the fallback. Same pattern at line 1306 (`total_dur = git_branch_duration()`).
- `.claude/shared/hooks/telemetry-stamp.py:755,771` — hard-coded global checkpoint path `/tmp/.foundry-telemetry-checkpoint.json`.
- `ai/beans/BEAN-277-programmatic-vdd-gate/bean.md:9-11` — Started/Completed 14 minutes apart, Duration `1578h 19m`. Similar corruption in BEAN-278 and 60+ others (sampled values: `344h`, `1267h`, `1588h`).

## Proposed change

1. **Prefer Started→Completed:** invert the preference at both call sites — `format_duration(cur_started, now)` (or the recorded Completed timestamp) is primary; `git_branch_duration()` only when Started is missing/unparseable. Rename `git_branch_duration` or extend its docstring to state it measures branch age, not work duration.
2. **Guard against nonsense:** if the chosen duration exceeds a sanity threshold (e.g. 7 days) while Started/Completed are same-day, stamp the Started→Completed value and append a `(branch-age: Xh)` annotation rather than the raw git figure.
3. **Per-scope checkpoint:** key the checkpoint file by branch (or bean id): `/tmp/.foundry-telemetry-checkpoint-<sanitized-branch>.json`. Parallel workers each track their own token baseline. Clean up the file on bean closure.
4. **Backfill script:** one-shot `scripts/backfill-bean-durations.py` that walks `ai/beans/*/bean.md`, recomputes Duration from Started/Completed where both parse, rewrites the field, and appends a `(corrected 2026-07)` marker. Dry-run mode by default; summary of changed beans printed.
5. **Tests:** the kit has no test harness of its own — add pytest coverage in this repo (`tests/test_telemetry_stamp.py`) importing the hook module directly (it's plain Python): duration preference, sanity guard, checkpoint path derivation.
6. Publish via `scripts/claude-publish.sh` (this file lives in the kit submodule and ships to every project).

## Out of scope

- Aggregating/consuming telemetry (SPEC-009).
- Reducing the hook's overall size/complexity or its mutate-on-write behavior (worth a follow-up; noted in SPEC-014's hardening context but not blocking).

## Acceptance criteria

- [ ] `test: tests/test_telemetry_stamp.py` — Started→Completed wins when both timestamps parse; git branch-age used only as fallback; checkpoint path varies by branch.
- [ ] `file-contains: .claude/shared/hooks/telemetry-stamp.py` — call sites use `format_duration(` as the primary duration source.
- [ ] `manual:` run `scripts/backfill-bean-durations.py --apply` and spot-check BEAN-277 shows `14m` (± rounding), not `1578h 19m`.
- [ ] `test: uv run pytest` — full suite passes.
- [ ] `manual:` kit change committed to claude-kit and submodule pointer bumped.

## Files to touch

- `.claude/shared/hooks/telemetry-stamp.py` (kit submodule — publish upstream)
- `scripts/backfill-bean-durations.py` (new)
- `tests/test_telemetry_stamp.py` (new)
- `ai/beans/*/bean.md` (backfill output)
