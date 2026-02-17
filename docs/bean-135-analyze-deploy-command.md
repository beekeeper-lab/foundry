# BEAN-135: Deploy Command Analysis

**Skill file:** `.claude/skills/deploy/SKILL.md` (152 lines)
**Date:** 2026-02-16
**Analyst:** developer (Process analysis bean)

---

## 1. Overview

The `/deploy` skill promotes code between branches via pull requests. It is the promotion gate in the three-tier deployment model:

```
feature branch → test → main
```

Two modes:
- **`/deploy`** (default) — Promotes `test` → `main`. Full release with branch cleanup.
- **`/deploy test`** — Promotes current branch → `test`. Integration deploy for feature branches.

The skill creates a PR, runs quality gates, merges the PR, and cleans up — all after a single user approval.

---

## 2. Branch Resolution Logic

The skill's most nuanced logic is determining the source branch. Four cases are defined:

| Target | Current Branch | Source Branch | Use Case |
|--------|---------------|---------------|----------|
| `main` (default) | any | `test` | Release: promote integration to production |
| `test` | feature branch | current branch | Integration: merge feature into test |
| `test` | `main` (ahead of origin) | auto-created `deploy/YYYY-MM-DD` | Staging: detach local-only commits |
| `test` | `main` (matches origin) | — (abort) | Nothing to deploy |

### Staging Branch Logic (Case 3)

When on `main` with local-only commits and deploying to `test`:

1. Check `git log origin/main..main` — if empty, abort ("nothing to deploy")
2. Create staging branch `deploy/YYYY-MM-DD` (with `-2`, `-3` suffix on collision)
3. `git checkout -b <staging>` from current HEAD
4. `git branch -f main origin/main` — resets local main ref to match remote
5. Deploy the staging branch into test

**Key invariant preserved:** Only feature/staging branches flow into `test`; only `test` flows into `main`. Main is never pushed directly into test.

**Analysis:** This is a well-thought-out design. The staging branch mechanism avoids breaking the directional flow invariant while handling the edge case of "I committed to main locally and want to deploy those commits." The `branch -f` reset is safe because we've already checked out the staging branch.

---

## 3. Five-Phase Process Flow

### Phase 1: Preparation (Steps 1-5)

```
Start
  │
  ├─ Save current branch
  ├─ Check git status --porcelain
  │   ├─ Clean → continue
  │   └─ Dirty → prompt: Commit / Stash / Abort
  │       ├─ Commit → stage all, commit, continue
  │       ├─ Stash → git stash --include-untracked, continue
  │       └─ Abort → exit
  │
  ├─ Resolve source/target (see Branch Resolution)
  ├─ Push source to remote
  └─ Verify source is ahead of target
      └─ Not ahead → "Nothing to deploy", exit
```

**Decision points:** 2 (dirty working tree handling, ahead-of-target check)

### Phase 2: Quality Gate (Steps 6-7)

```
  ├─ uv run pytest
  │   ├─ Pass → record count, continue
  │   └─ Fail → report, restore stash, return to branch, exit
  │
  └─ uv run ruff check foundry_app/
      └─ Record result (does not block — only reported)
```

**Decision points:** 1 (test pass/fail)

**Note:** Ruff violations are reported but do not block deployment. This is a deliberate choice — lint warnings don't prevent release, but test failures do.

### Phase 3: Build Release Notes (Steps 8-9)

```
  ├─ Parse git log for BEAN-NNN: messages
  ├─ Cross-reference with ai/beans/_index.md for titles
  └─ Count merged bean/* branches (main deploy only)
```

**Decision points:** 0 (informational)

### Phase 4: User Approval (Steps 10-11) — SINGLE PROMPT

```
  ├─ Present deploy summary (beans, tests, ruff, branch cleanup)
  └─ Ask once:
      ├─ Target main: "go" / "go with tag" / "abort"
      └─ Target test: "go" / "abort"
```

**Decision points:** 1 (go/abort, with optional tag for main)

**This is the ONLY user interaction.** Everything after "go" runs unattended.

### Phase 5: Execute (Steps 12-21) — FULLY AUTOMATED

```
  ├─ gh pr create --base <target> --head <source>
  ├─ gh pr merge <pr-number> --merge
  ├─ [main only] git tag + push tags (if requested)
  ├─ [main only] Delete local bean/* branches merged into main
  ├─ [main only] Delete remote bean/* branches
  ├─ [staging] Delete staging branch (local + remote)
  ├─ Checkout target, pull latest
  ├─ Return to original branch (or main if staging was used)
  ├─ Restore stash (if applicable)
  └─ Report: PR URL, merge commit, beans deployed, branches deleted
```

**Decision points:** 0 (fully automated post-approval)

---

## 4. Error Conditions and Recovery

| Error | Phase | Recovery | Stash Restored? | Returns to Branch? |
|-------|-------|----------|-----------------|---------------------|
| Nothing to deploy | 1 | Report and exit | Yes | Yes |
| Tests fail | 2 | Report failures, stop | Yes | Yes |
| PR create fails | 5 | Report, suggest `gh auth status` | Unclear | Unclear |
| PR merge fails | 5 | Report, suggest branch protection/conflicts | Unclear | Unclear |
| User aborts | 4 | Clean exit | Yes | Yes |
| Staging branch reset fails | 1 | Abort, leave staging for manual cleanup | Yes | No (on staging) |
| Command blocked (sandbox) | Any | Print command for manual execution, continue | N/A | N/A |

### Recovery Gap Analysis

**Well-handled:**
- Pre-execution failures (phases 1-2) have clean recovery: stash is restored, user returns to original branch
- The "nothing to deploy" case is caught early in two places (staging check and ahead-of-target check)
- Sandbox blocking is handled gracefully with manual fallback

**Potential gaps:**
- Phase 5 errors (PR create/merge fail) don't explicitly mention stash restoration or branch return. If `gh pr create` fails mid-execution, the user may be left on the wrong branch with a stash still applied.
- No rollback mechanism if the PR is created but merge fails (orphaned PR left open)
- No retry logic for transient `gh` failures (network timeouts)

---

## 5. Relationship to Other Skills

### Upstream: `/merge-bean`
- `/merge-bean` merges feature branches into `test` (direct git merge, no PR)
- `/deploy test` also merges into `test`, but via PR
- These are complementary: merge-bean is for individual beans; deploy-test is for explicit promotion with a PR record

### Downstream: Bean Workflow
- `bean-workflow.md` references `/deploy` as the promotion gate from `test` → `main`
- The three-tier model is: bean work → merge-bean to test → deploy to main

### Branch Cleanup Scope
- `/merge-bean` deletes the single feature branch it merges
- `/deploy` (to main) bulk-deletes ALL merged bean/* branches — local and remote
- This is the "sweep" operation that cleans up after multiple beans are integrated

---

## 6. Design Strengths

1. **Single approval gate.** The "ask once, then run" pattern minimizes user interruption during what could be a 10+ step operation. This is a strong UX choice.

2. **Staging branch invariant.** The `deploy/YYYY-MM-DD` mechanism elegantly preserves the directional flow invariant without forcing users to manually create branches when they've accidentally committed to main.

3. **PR-based promotion.** Using PRs (not direct pushes) for both test and main deploys creates an audit trail and enables future CI integration.

4. **Dirty working tree handling.** The three-option prompt (commit/stash/abort) is user-friendly and avoids silent data loss.

5. **Merge strategy.** Using `--merge` (not squash/rebase) preserves commit history, which is important for the bean telemetry and traceability model.

6. **Branch cleanup separation.** Only main deploys trigger bulk cleanup, which is correct — feature branches may still need rework after test integration.

---

## 7. Risks and Concerns

1. **Phase 5 atomicity.** Steps 12-21 are treated as a single uninterruptible block, but any step can fail. There's no transaction-like rollback. A failure at step 15 (branch deletion) leaves the system in a partially-cleaned state. This is acceptable given the operations are idempotent, but could confuse users.

2. **Stale branch deletion.** Step 15 uses `git branch -D` (force delete) for "stale/orphaned" branches of Done beans. The criteria for "stale" aren't defined in the skill — this relies on the executor's judgment.

3. **No dry-run mode.** There's no way to preview what the deploy would do without actually executing it. The summary in Phase 4 partially serves this purpose, but it doesn't show the exact git commands.

4. **Ruff is non-blocking.** Lint violations are reported but don't prevent deployment. This is intentional but means lint debt can accumulate on main.

5. **Tag collision.** The skill doesn't check if a tag already exists before attempting `git tag <version>`. If the tag exists, the command will fail mid-execution.

6. **Concurrent deploy safety.** If two agents run `/deploy` simultaneously (one to test, one to main), the branch state could become inconsistent. No locking mechanism exists.

---

## 8. Improvement Opportunities

### Quick Wins
- **Add tag existence check** before attempting to create a tag (prevents Phase 5 mid-execution failure)
- **Explicit stash/branch recovery in Phase 5 errors** — ensure the error table documents restoration for all failure modes
- **Define "stale branch" criteria** — e.g., "branches whose bean status is Done in _index.md"

### Medium Effort
- **Dry-run mode** (`/deploy --dry-run`) — show the summary and planned commands without executing
- **Phase 5 checkpoint logging** — write a deploy log file so partial failures can be resumed or diagnosed
- **Add ruff-blocking option** — allow `/deploy --strict` to fail on lint violations

### Larger Enhancements
- **Deploy lock** — a lightweight file-based lock to prevent concurrent deploys
- **Rollback skill** — a `/rollback` companion that can revert a deploy (revert merge commit, reopen PR)
- **CI integration** — replace the local `uv run pytest` with a CI check on the PR, enabling deploy from any machine

---

## 9. Metrics

| Metric | Value |
|--------|-------|
| **Total lines** | 152 |
| **Phases** | 5 |
| **Steps** | 21 |
| **Decision points** | 4 (dirty tree, test pass, ahead check, go/abort) |
| **User prompts** | 1 (+ optional dirty tree prompt) |
| **Error conditions** | 7 documented |
| **Branch resolution cases** | 4 |
| **External tool dependencies** | `git`, `gh`, `uv run pytest`, `uv run ruff` |

---

## 10. Summary

The deploy skill is well-designed for its purpose: a reliable, low-friction promotion gate with strong UX (single approval). The staging branch mechanism is particularly clever. The main areas for improvement are Phase 5 error recovery (making it more robust to partial failures) and adding safety checks for edge cases (tag collision, concurrent deploys). The skill's 152-line specification is thorough and unambiguous, making it one of the best-documented skills in the toolkit.
