# Analysis: Long Run Command (`/long-run`)

**Bean:** BEAN-132 | **Date:** 2026-02-16 | **Analyst:** Developer

---

## 1. Overview

The `/long-run` command is the Foundry AI team's autonomous backlog processor. It reads the bean backlog, selects the highest-priority actionable bean, decomposes it into tasks, executes the full team wave (BA → Architect → Developer → Tech QA), verifies acceptance criteria, commits, merges, and loops until the backlog is empty.

**Two modes:**
- **Sequential** (default) — processes one bean at a time in a single Claude session
- **Parallel** (`fast N`) — spawns up to N tmux workers, each processing a bean in an isolated git worktree

**Source file:** `.claude/skills/long-run/SKILL.md` (281 lines)

---

## 2. Phase-by-Phase Analysis — Sequential Mode

### Phase 0: Branch Prerequisite & Mode Detection

**What it does:** Ensures the agent is on the `test` branch with a clean working tree. If on `main` with clean tree, auto-checkouts `test`. Detects parallel mode via the `fast` input.

**Assessment:**
- Sound gate — prevents accidental commits to `main`.
- The auto-checkout from `main` to `test` is a convenience that reduces friction for first-time use.
- The dirty-tree check is essential since `/long-run` creates branches and commits.

**Observation:** The skill does not check for stale local state (e.g., local `test` being behind `origin/test`). A `git pull` before starting would prevent merge conflicts later in Phase 5.5.

### Phase 0.5: Trello Sync

**What it does:** Invokes `/trello-load` to import cards from Trello's Sprint_Backlog list as `Approved` beans. Best-effort — failures don't block the run.

**Assessment:**
- Good design: making Trello sync optional and best-effort prevents a third-party service from blocking autonomous operation.
- The one-way flow (Trello → beans) is simple and predictable. Bidirectional sync would add substantial complexity.
- Cards are created with `Approved` status, which means they bypass the human approval gate. This is acceptable because the human approved them in Trello, but it's worth noting the implicit trust transfer.

### Phase 1: Backlog Assessment

**What it does:** Parses `_index.md`, filters for `Approved` beans, applies optional category filter, checks stop condition.

**Assessment:**
- Clean filtering logic: explicitly lists exclusion reasons (Done, Deferred, Unapproved, blocked by dependencies, locked by another agent).
- The category filter (`App`, `Process`, `Infra`) is a useful scoping mechanism for targeted runs.
- The stop condition with category-aware messaging is well thought out.

**Observation:** The "locked by another agent" check depends on the Owner field in `_index.md`. If a previous agent crashed without cleaning up its lock, the bean stays stuck. The skill references this in the bean-workflow docs ("stale locks") but `/long-run` itself doesn't attempt detection — the user must manually intervene.

### Phase 2: Bean Selection

**What it does:** Reads each candidate bean's `bean.md`, applies selection heuristics (priority → dependencies → logical order → ID), announces selection.

**Assessment:**
- The four-tier heuristic is well-ordered and practical. Priority-first is the right default.
- "Logical order" (infrastructure before features, data models before UI) requires the agent to understand inter-bean relationships that may not be explicitly stated — this is inherently fuzzy.
- The announcement format (Header Block + Task Progress Table from the communication template) provides good observability.

**Observation:** The heuristic is deterministic enough for most cases, but when multiple beans have equal priority and no explicit dependencies, the agent must infer "logical order" from bean content. This is the weakest selection criterion and could lead to suboptimal ordering. Consider adding an explicit `depends_on` field to `bean.md` metadata to make dependencies machine-readable.

### Phase 3: Bean Execution

**What it does:** Updates bean status to In Progress, ensures `test` branch exists, creates feature branch, decomposes into tasks, updates bean task table.

**Assessment:**
- The feature branch creation is mandatory and correctly enforced. The "resume" path (checkout existing branch) handles interrupted runs gracefully.
- Task decomposition follows the standard wave pattern with clear file naming: `NN-<owner>-<slug>.md`.
- The mandatory Tech QA rule for `App` and `Infra` beans is an important quality gate — the Team Lead is explicitly prohibited from self-verifying Developer work.
- BA and Architect can be skipped with documented reasons — good flexibility for simple beans.

**Observation:** Step 8 ("Ensure test branch exists") is redundant — Phase 0 already ensures the agent is on `test`. The branch must already exist. This step would only matter if `/long-run` is invoked in an unusual way.

### Phase 4: Wave Execution

**What it does:** Executes tasks in dependency order, records timestamps, runs `/close-loop` telemetry, reprints progress table after each status change.

**Assessment:**
- The telemetry integration (Started/Completed timestamps, duration computation, token self-report) provides valuable project metrics.
- Reprinting the header + task table after each status change keeps the tmux pane scannable — good UX for long-running sessions.
- The "skip inapplicable roles" guidance reinforces Phase 3's decomposition rules with an explicit note that Tech QA must never be skipped for App/Infra beans.

**Observation:** The phrase "prompt for token self-report" in step 12 implies the agent asks itself for token counts. This is inherently inaccurate — Claude doesn't have precise token counters. The BEAN-121 (Token Usage Capture via JSONL Parsing) provides a more reliable mechanism, but the skill text hasn't been updated to reference it.

### Phase 5: Verification & Closure

**What it does:** Checks every acceptance criterion, runs tests and lint for code beans, closes bean as Done, commits on feature branch.

**Assessment:**
- Running both `uv run pytest` and `uv run ruff check` before closure is essential and correctly specified.
- The commit message format (`BEAN-NNN: <bean title>`) is simple and grep-friendly.
- The note that "The orchestrator updates `_index.md` after the merge" correctly separates concerns between the worker (owns `bean.md`) and the orchestrator (owns `_index.md`).

### Phase 5.5: Merge Captain

**What it does:** Executes `/merge-bean` to merge feature branch into `test`, updates `_index.md`, moves Trello card to Completed list.

**Assessment:**
- The merge-then-update-index sequence is correct. Index should only reflect Done after a successful merge.
- The conflict handling (report, abort, leave bean on feature branch, stop loop) is conservative and safe — no auto-resolution.
- The Trello card movement logic is well-specified: reads the Trello metadata section, uses the Card ID for a direct API call, best-effort.

**Observation:** Step 17b has detailed Trello logic (7 sub-steps) that is essentially duplicated in the parallel mode (Phase 5, step 12). This could be extracted into a shared reference to avoid drift.

### Phase 6: Loop

**What it does:** Returns to Phase 1. If no actionable beans remain, reports final summary with the `test` branch warning.

**Assessment:**
- The loop structure is clean. The "return to Phase 1" ensures the backlog is re-read each iteration, picking up any beans that became unblocked.
- The final message (`Work is on the test branch. Run /deploy to promote to main.`) is a critical reminder — without it, users might forget that work hasn't reached `main`.

---

## 3. Parallel Mode Analysis

### Architecture

The parallel mode transforms `/long-run` from a single-agent loop into a multi-agent orchestration system:

- **Main window** = orchestrator (reads backlog, selects beans, spawns workers, monitors dashboard, handles merges)
- **Child windows/panes** = workers (each processes one bean in an isolated git worktree)

Communication is file-based: workers write to `/tmp/foundry-worker-BEAN-NNN.status`, the orchestrator reads these files every ~30 seconds.

### Strengths

1. **Git worktree isolation** — Each worker gets its own directory (`/tmp/foundry-worktree-BEAN-NNN`) with its own branch. No file conflicts, no branch collisions. This is the right architectural choice.

2. **Pre-assignment eliminates races** — The orchestrator selects and assigns all beans before spawning workers. No two workers compete for the same bean.

3. **Centralized merging** — Workers do NOT merge. The orchestrator handles all merges sequentially. This avoids the problem where multiple workers would need to checkout `test` simultaneously (impossible with shared git state).

4. **Auto-submit and auto-close** — Workers pass the prompt as a positional argument to `claude`, so they start immediately. Windows/panes close when claude exits. No manual cleanup.

5. **Dashboard monitoring** — The status file protocol gives the orchestrator real-time visibility without polling workers directly. The progress bar UI with emoji status indicators is compact and informative.

6. **Dynamic replacement** — When a worker finishes, the orchestrator can spawn a replacement for the next bean. The pool stays full until the backlog is exhausted.

### Weaknesses and Risks

1. **Status file reliability** — Workers must remember to update their status file at every transition. If a worker crashes between updates, the status file shows stale data. The 5-minute staleness check helps, but a worker that crashes immediately after writing "running" will appear healthy for 5 minutes.

2. **No heartbeat mechanism** — The system relies on timestamp staleness for liveness detection. A more robust approach would be periodic heartbeat writes (e.g., every 60 seconds) so the orchestrator can distinguish "busy but alive" from "dead."

3. **Merge serialization bottleneck** — All merges go through the orchestrator sequentially. If workers complete beans faster than the orchestrator can merge them, completed beans queue up. This is unlikely with 3-5 workers but could matter at higher parallelism.

4. **Worktree cleanup on crash** — If the orchestrator crashes, worktrees and status files are left behind in `/tmp/`. The skill mentions `git worktree prune` in cleanup but doesn't handle the case where the orchestrator itself fails mid-run.

5. **`_index.md` contention** — The orchestrator is the sole writer of `_index.md`, which is correct. But the sequential commit-push cycle for index updates means the orchestrator does: `update index → commit → push → spawn next worker`. If the push fails (e.g., another repo pushes to `test`), the index and the actual bean state diverge.

6. **No worker-to-orchestrator error escalation** — When a worker hits `status: error`, the orchestrator reports it in the dashboard but doesn't take corrective action. The failed bean stays In Progress indefinitely until a human intervenes.

---

## 4. Dependency Map

### Skills Invoked

| Skill | Phase | Purpose | Required |
|-------|-------|---------|----------|
| `/trello-load` | 0.5 | Import sprint backlog from Trello | No (best-effort) |
| `/pick-bean` | 3 (implicit) | Claim bean, create branch | Yes (logic inlined) |
| `/close-loop` | 4 | Record telemetry after each task | Yes |
| `/merge-bean` | 5.5 | Merge feature branch to test | Yes |
| `/deploy` | Referenced | Promote test to main (user action) | No (post-run) |
| `/spawn-bean` | Parallel | Worker spawning protocol reference | Yes (parallel only) |

### Files Read/Written

| File | Access | Phase |
|------|--------|-------|
| `ai/beans/_index.md` | Read + Write | 1, 3, 5.5, 6 |
| `ai/beans/BEAN-NNN-<slug>/bean.md` | Read + Write | 2, 3, 4, 5 |
| `ai/beans/BEAN-NNN-<slug>/tasks/*.md` | Write | 3, 4 |
| `ai/context/bean-workflow.md` | Read | Reference |
| `ai/outputs/<persona>/*` | Write | 4 |
| `/tmp/foundry-worker-BEAN-NNN.status` | Write (worker) / Read (orchestrator) | Parallel |

### External Dependencies

| Dependency | Required | Failure Impact |
|------------|----------|----------------|
| Git repository (clean state) | Yes | Blocks start |
| `test` branch | Yes (auto-created) | Minor friction |
| `uv run pytest` | Yes (code beans) | Blocks closure |
| `uv run ruff check` | Yes (code beans) | Blocks closure |
| Trello MCP server | No | Skips sync |
| `tmux` | Yes (parallel only) | Blocks parallel mode |
| `claude` CLI | Yes (parallel only) | Blocks worker spawn |

---

## 5. Error Handling Assessment

The skill defines 8 named error conditions:

| Error | Handling Quality | Notes |
|-------|-----------------|-------|
| `EmptyBacklog` | Good | Clean exit with report |
| `NoActionableBeans` | Good | Summary of remaining beans by status |
| `TaskFailure` | Adequate | Stops loop, leaves bean In Progress. Could provide more guidance on recovery. |
| `TestFailure` | Good | "Attempt to fix; if unresolvable, report and stop" — gives the agent latitude to self-correct |
| `CommitFailure` | Adequate | Reports and stops. No retry logic. |
| `MergeConflict` | Good | Reports conflicting files, aborts merge, preserves feature branch. Conservative and safe. |
| `NotInTmux` | Good | Clear error message with resolution steps |
| `WorkerFailure` | Good | Other workers continue. Failed bean stays In Progress. |

**Gap:** No error condition for "git push fails during index update" or "worktree creation fails." These are infrastructure failures that could leave the system in an inconsistent state.

---

## 6. Strengths

1. **Comprehensive lifecycle coverage** — The skill handles the entire bean lifecycle from backlog assessment to merge, with no gaps in the happy path.

2. **Two operating modes from one skill** — Sequential and parallel modes share the same lifecycle phases, minimizing concept divergence. The parallel mode adds orchestration on top rather than reimplementing the lifecycle.

3. **Conservative error handling** — The skill favors stopping over guessing. Merge conflicts abort rather than auto-resolve. Test failures stop the loop. This prevents cascading damage.

4. **Good observability** — The communication template (header block + task table + work log + completion summary) makes long-running sessions inspectable at a glance.

5. **Category filtering** — The ability to scope runs to `App`, `Process`, or `Infra` beans allows targeted processing without manual bean selection.

6. **Trello integration is optional** — The best-effort design for Trello sync means the core workflow is independent of external services.

7. **Clear separation of concerns** — Workers own their `bean.md`, the orchestrator owns `_index.md`. Workers don't merge; the orchestrator handles merges.

8. **Feature branch discipline** — Every bean gets its own branch, merged via `--no-ff`. The git history is clean and traceable.

---

## 7. Weaknesses

1. **Document length and complexity** — At 281 lines, the skill file is the longest in the system. The parallel mode nearly doubles the document. This makes the skill hard to modify safely — a change in one mode may need a corresponding change in the other.

2. **Implicit dependency on bean-workflow.md** — The skill references lifecycle concepts (locking, claim protocol, stale locks) defined in `bean-workflow.md` but doesn't link to them inline. An agent that reads only the skill file may miss important constraints.

3. **Token self-report inaccuracy** — Phase 4 references "prompt for token self-report" which is unreliable. The system has since added JSONL-based token capture (BEAN-121), but the skill text still references the old approach.

4. **No pull-before-start** — Phase 0 checks the branch but doesn't pull. If local `test` is behind `origin/test`, the first merge in Phase 5.5 may conflict unnecessarily.

5. **Duplicated Trello logic** — Steps 17b (sequential) and the parallel Phase 5 step 12 both describe the Trello card movement logic in detail. Changes to one must be manually mirrored in the other.

6. **No resume capability** — If `/long-run` is interrupted mid-bean, there's no built-in way to resume from where it left off. The bean stays In Progress, and a re-run will skip it (since it's locked). The user must manually reset the bean to Approved or manually complete it.

7. **Stale lock problem** — A crashed agent leaves beans In Progress with no automatic recovery. The skill defers to the user ("Do NOT auto-unlock it. Report it to the user.") which is safe but means crashed runs require manual intervention.

8. **Phase numbering drift** — Phase 0, 0.5, 1, 2, 3, 4, 5, 5.5, 6 — the half-steps indicate features bolted on after initial design. While functional, the numbering suggests the document would benefit from a structural pass.

---

## 8. Improvement Recommendations

### High Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 1 | **Add `git pull origin test` to Phase 0** | Prevents unnecessary merge conflicts from stale local state. One line of git, high impact. |
| 2 | **Update token capture reference** | Replace "prompt for token self-report" with reference to JSONL-based capture (BEAN-121). Avoids confusion about how telemetry works. |
| 3 | **Extract Trello card-move logic** | Define the Trello completion logic once (perhaps in `/merge-bean` or a shared section) and reference it from both sequential and parallel modes. Eliminates duplication drift risk. |

### Medium Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 4 | **Add resume capability** | When `/long-run` starts and finds a bean In Progress owned by `team-lead`, offer to resume it instead of skipping. Check for existing task files and completed tasks. |
| 5 | **Add worker heartbeat** | In parallel mode, have workers update their status file timestamp every 60 seconds (even when idle), so the orchestrator can reliably detect dead workers vs. busy workers. |
| 6 | **Renumber phases cleanly** | Reorganize from 0/0.5/1-6 to clean 1-8 numbering. This is cosmetic but improves readability and makes the document easier to reference in other skills. |
| 7 | **Add explicit `depends_on` to bean metadata** | Make inter-bean dependencies machine-readable instead of requiring the agent to infer them from prose. Strengthens Phase 2 selection heuristics. |

### Low Priority

| # | Recommendation | Rationale |
|---|---------------|-----------|
| 8 | **Add worktree cleanup on startup** | At the start of parallel mode, prune any stale worktrees from a previous crashed run. `git worktree prune` is safe and idempotent. |
| 9 | **Add push-retry for index updates** | When the orchestrator's `git push` fails for `_index.md` updates, pull and retry once (similar to `/merge-bean`'s push retry). |
| 10 | **Document max parallelism guidance** | The spawn-bean command mentions "3-5 recommended" but `/long-run` doesn't. Add a note about practical limits (API rate limits, system resources). |

---

## 9. Comparison with Related Skills

| Aspect | `/long-run` | `/spawn-bean` | `/pick-bean` |
|--------|-------------|---------------|--------------|
| Bean selection | Inline heuristic | Pre-assigned or auto-pick | User-specified |
| Branch creation | Inline | Worktree-based | Inline |
| Merging | Inline (calls `/merge-bean`) | Orchestrator merges | Not handled |
| `_index.md` writes | Yes (sequential) / Orchestrator only (parallel) | Orchestrator only | Yes |
| Trello integration | Yes (sync + completion) | No | No |
| Telemetry | Yes (`/close-loop`) | Delegated to workers | No |

**Observation:** `/long-run` in sequential mode inlines most of `/pick-bean`'s logic (steps 7-9) rather than invoking it. This creates a maintenance risk — changes to the pick logic must be reflected in both places. In parallel mode, the spawn-bean prompt tells workers to use `/pick-bean` directly, which is cleaner.

---

## 10. Summary

The `/long-run` command is a well-designed autonomous backlog processor that successfully handles both sequential and parallel bean processing. Its core strengths are conservative error handling, good observability, and clean separation between worker and orchestrator responsibilities.

The main areas for improvement are:
1. **Freshness** — Pull `test` before starting; update telemetry references to current mechanism.
2. **Deduplication** — Trello logic and pick-bean logic are partially duplicated across modes and skills.
3. **Resilience** — Add resume capability, worker heartbeats, and stale worktree cleanup to handle crash recovery gracefully.
4. **Readability** — Renumber phases cleanly and cross-link to dependency documents.

None of these are urgent — the command works well in production today. They represent incremental improvements that would make the skill more maintainable and resilient as the team scales.
