# Bean Workflow

A **Bean** is a unit of work — a feature, enhancement, bug fix, or epic. Beans replace ad-hoc task tracking with a structured, persona-aware workflow.

## Directory Structure

```
ai/beans/
  _index.md                    # Master backlog index
  _bean-template.md            # Template for creating new beans
  _review.md                   # Generated MOC for Obsidian review (auto-generated)
  BEAN-NNN-<slug>/
    bean.md                    # Bean definition (problem, goal, scope, criteria)
    tasks/                     # Task files created during decomposition
      01-<owner>-<slug>.md     # Individual task assigned to a persona
```

## Multi-Agent Environment

Multiple Claude Code agents may be working in this codebase simultaneously. Each agent typically operates in a different functional area (e.g., one on Process beans, another on App beans), but overlap can occur.

**Rules for concurrent work:**
- **Always re-read `_index.md` immediately before creating a new bean** — another agent may have added beans since your last read. Use the highest existing ID + 1.
- **Never pre-assign bean IDs** — during planning, use working titles only. Assign IDs at creation time by reading the current max from `_index.md`.
- **Create beans sequentially, not in parallel** — write each bean's directory + bean.md + index entry before starting the next one. This ensures each bean sees the latest max ID.
- **Always re-read `_index.md` before picking a bean** — another agent may have already picked it.
- **Expect external changes** — files you read earlier may have been modified by another agent. Re-read before editing if significant time has passed.
- **Bean ID collisions** — if you create a bean and find the ID already taken, increment and retry.
- **Don't modify another agent's in-progress bean** — if a bean is `In Progress` with a different owner context, leave it alone.

**Bean locking (claim protocol):**

Beans are locked by their Status + Owner fields in both `_index.md` and `bean.md`. These two fields together act as a lock.

1. **Before picking a bean**, re-read `_index.md`. If the bean's Status is `In Progress` or `Done`, it is locked — skip it. If `Unapproved`, it cannot be picked yet.
2. **To claim a bean**, atomically update both `_index.md` and `bean.md`:
   - Set Status to `In Progress`
   - Set Owner to a unique identifier (e.g., `team-lead`, `agent-2`, or the session context)
3. **A bean is locked when** Status is `In Progress` AND Owner is set. No other agent should pick, modify, or work on a locked bean.
4. **A bean is unlocked when** Status is `Approved` or `Deferred` with no Owner, or Status is `Done`.
5. **If you find a conflict** (you tried to pick a bean but it's already claimed when you go to write), abandon the pick and select a different bean.
6. **Stale locks** — if a bean has been `In Progress` for an unusually long time with no file changes, it may indicate a crashed agent. Do NOT auto-unlock it. Report it to the user and let them decide.

## Bean Lifecycle

```
Unapproved → Approved → In Progress → Done
```

### 1. Creation

Anyone can create a bean:

1. **Re-read `ai/beans/_index.md`** immediately before creation to get the current highest bean ID (another agent may have added beans since your last read)
2. Compute next ID = highest existing + 1
3. Create directory `ai/beans/BEAN-NNN-<slug>/` and copy `_bean-template.md` to `bean.md`
4. Fill in all fields: Problem Statement, Goal, Scope, Acceptance Criteria
5. Set Status to `Unapproved` and assign a Priority
6. Append the bean to `ai/beans/_index.md`

Bean IDs are sequential: BEAN-001, BEAN-002, etc.

**Deferred ID assignment (for batch creation):**

When creating multiple beans at once (e.g., from `/backlog-refinement`), **do not pre-assign IDs during planning**. Use working titles only. Assign IDs one at a time during creation:

1. Plan beans using titles and slugs only (no BEAN-NNN IDs)
2. When ready to create, process beans **sequentially** (not in parallel)
3. For each bean: re-read `_index.md` → assign next ID → write bean.md → append to `_index.md`
4. After all beans are created, update cross-references with the actual IDs

This prevents ID collisions when multiple agents create beans concurrently.

### 2. Approval

Newly created beans have status `Unapproved`. The user must review and approve them before they can be executed. This is the **approval gate** — no work begins without explicit human approval.

**Review methods:**

1. **Obsidian review** (recommended) — Run `/review-beans` to generate a filtered MOC file (`ai/beans/_review.md`) with links to beans awaiting review, then open Obsidian on the `ai/beans/` directory. Edit bean files directly to:
   - Change status from `Unapproved` to `Approved`
   - Adjust priority, scope, or acceptance criteria
   - Add notes or dependencies
   - Defer beans by changing status to `Deferred`

2. **Terminal review** — Edit `bean.md` and `_index.md` files directly using any editor.

**Approval process:**

1. **Review** — Read the bean's Problem Statement, Goal, Scope, and Acceptance Criteria
2. **Evaluate** — Is the scope reasonable? Are criteria testable? Is the priority correct?
3. **Approve** — Change Status from `Unapproved` to `Approved` in both `bean.md` and `_index.md`
4. **Defer** — Optionally change status to `Deferred` for beans that should wait

**What `/long-run` checks:** When the Team Lead enters autonomous mode, it only processes beans with status `Approved`. Beans with status `Unapproved` are skipped entirely. This ensures the user has reviewed and signed off on every unit of work before it begins.

### 3. Picking

The Team Lead reviews the backlog (`ai/beans/_index.md`) and picks beans to work on:

1. **Re-read `_index.md`** — check for beans claimed by other agents since your last read
2. Assess priority and dependencies between beans
3. **Only pick `Approved` beans** — `Unapproved` beans cannot be picked. They must be reviewed and approved first.
4. **Skip locked beans** — any bean with Status `In Progress` and an Owner is claimed by another agent
5. **Claim the bean** — update Status to `In Progress` and set Owner in both `bean.md` and `_index.md`. This is the lock.
6. Update the index table

### 4. Molecularity Gate

Before decomposition, the Team Lead checks that the bean is appropriately sized ("molecular"). A molecular bean represents a single, atomic unit of change.

**Molecularity criteria — a bean SHOULD:**

- **Single concern:** Address one problem, feature, or change — not bundle unrelated work
- **Limited blast radius:** Touch no more than 5 files (excluding generated files, tests, and index updates)
- **One-session scope:** Be completable in a single work session (2-task default wave: Developer → Tech-QA)
- **Independent verifiability:** Have acceptance criteria that can be verified without waiting for other beans
- **Clear boundaries:** Have In Scope and Out of Scope that don't overlap with other active beans

**If a bean exceeds these criteria**, flag it for decomposition:

1. Identify the independent sub-concerns within the bean
2. Split into smaller beans — each addressing exactly one concern
3. Link the new beans via dependencies in their Notes sections
4. Defer the original bean (status `Deferred`) and note the replacement beans, or delete it if fully replaced

**Common signals a bean is too large:**

- The scope section lists multiple unrelated deliverables
- Acceptance criteria span different subsystems or categories (e.g., app code + process docs)
- Decomposition would produce 4+ tasks or require 3+ personas
- The bean title uses "and" to join distinct concepts (e.g., "Add auth and redesign settings")
- The bean exceeds the Blast Radius Budget (see below)

#### Blast Radius Budget

The **Blast Radius Budget** sets quantitative guardrails on the scope of a single bean. It complements the qualitative molecularity criteria above with measurable limits.

**Metrics:**

| Metric | Description | Guideline Threshold |
|--------|-------------|-------------------|
| **Files changed** | Number of source files added or modified (excluding tests, generated files, and index files) | ≤ 10 files |
| **Systems touched** | Number of distinct system boundaries crossed (e.g., UI, service layer, data layer, CI/CD, docs) | ≤ 1 system boundary |
| **Lines modified** | Net lines added + modified + deleted across all changed files | ≤ 300 lines |

**System boundaries** are defined as distinct functional areas:
- `foundry_app/ui/` — UI layer
- `foundry_app/core/`, `foundry_app/services/` — service/core layer
- `foundry_app/io/` — I/O layer
- `tests/` — test suite (excluded from file count but counts as a boundary if non-test code also changes)
- `ai/` — AI team workspace (process/docs)
- `.claude/` — Claude Code configuration
- CI/CD, build, and deployment configs

**How to apply:**

1. **During refinement** — When proposing beans, estimate the blast radius. If a bean is likely to exceed any threshold, flag it for splitting before approval.
2. **During decomposition** — Before creating tasks, the Team Lead reviews the bean scope against the budget. If the planned changes exceed a threshold, decompose the bean into smaller units.
3. **During execution** — If a bean's actual changes exceed the budget mid-flight, the Developer or Team Lead should pause and evaluate whether the bean should be split. Minor threshold breaches (up to 20% over) are acceptable if documented in the bean's Notes section with justification.

**Flagging protocol:**

When a bean exceeds the blast radius budget:
1. Add a note to the bean: `> ⚠ Blast radius exceeded: [metric] is [value] (threshold: [limit])`
2. Evaluate whether the excess is justified (tightly coupled changes that cannot be split) or indicates the bean should be decomposed
3. If decomposition is warranted, follow the standard splitting process above
4. If the excess is justified, document the reason and proceed

### 5. Decomposition

The Team Lead breaks each picked bean into tasks:

1. Read the bean's problem statement, goal, and acceptance criteria
2. **Bottleneck Check** — before creating tasks, identify and mitigate potential bottlenecks (see below)
3. Create task files in `BEAN-NNN-<slug>/tasks/` with sequential numbering
4. Assign each task an owner (persona) and define dependencies
5. Default decomposition: **Developer → Tech-QA**. Add BA or Architect only when their inclusion criteria are met (see below)
6. **Tech-QA is mandatory for every bean** — no exceptions, regardless of category
7. Bean status is already `In Progress` from the picking step

#### Bottleneck Check

Before creating tasks, the Team Lead scans for three categories of bottleneck:

| Category | What to look for | Mitigation |
|----------|-----------------|------------|
| **Sequential dependencies** | Tasks that form a long chain where each waits on the previous one | Break chains by isolating independent subtasks that can run in parallel |
| **Shared resource contention** | Multiple tasks editing the same file, branch, or index | Sequence conflicting writes explicitly; split files if possible; assign one owner per shared resource |
| **Parallelization opportunities** | Tasks assumed sequential that have no real data dependency | Restructure the task graph so independent tasks run concurrently |

**How to apply:**

1. Draft the initial task list and dependency graph
2. Check each dependency edge: is it a true data dependency or just a habit?
3. Flag any shared files that multiple tasks will write to — assign clear ownership or sequence the writes
4. If the task chain is longer than 3 sequential steps, look for subtasks that can be extracted and run in parallel
5. Record findings as a brief note in the bean's Tasks section (e.g., `> Bottleneck check: no contention found` or `> Bottleneck check: tasks 02 and 03 parallelized — no shared inputs`)

#### Inclusion Criteria for Optional Personas

**BA — include when:**
- Requirements are ambiguous with 3+ valid interpretations
- The bean involves user-facing behavior that needs formal acceptance criteria elaboration
- Stakeholder trade-offs need to be documented before implementation

**Architect — include when:**
- The bean creates a new subsystem, module, or package
- The change modifies public APIs or data models used by 3+ modules
- A new external dependency or framework is being introduced
- An ADR (Architecture Decision Record) is needed

When BA or Architect are not included, note the reason with an inline skip tag:
```
> Skipped: BA (default), Architect (default)
```

Each task file should include:
- **Owner:** Which persona handles it
- **Depends on:** Which tasks must complete first
- **Status:** Current status (Pending, In Progress, Done)
- **Started:** — (auto-stamped by telemetry hook)
- **Completed:** — (auto-stamped by telemetry hook)
- **Duration:** — (auto-computed by telemetry hook)
- **Goal:** What this task produces
- **Inputs:** What the owner needs to read
- **Example Output:** A concrete example of the expected output format (see below)
- **Definition of Done:** Concrete checklist

#### Examples-First Principle

Every task should include or reference a concrete example of the expected output format. Abstract instructions alone can be ambiguous — examples eliminate guesswork and improve first-attempt quality.

**When creating tasks, the Team Lead should:**

1. Include an `Example Output:` section in the task file showing what the deliverable looks like
2. Use one of these approaches depending on the task type:
   - **Inline snippet** — paste a short example directly in the task file (best for small outputs like config entries, function signatures, or doc sections)
   - **File reference** — point to an existing file that follows the expected pattern (e.g., "Follow the format of `tasks/01-developer-feature-branch-updates.md`")
   - **Pattern description** — describe the structure when the output is too large to inline (e.g., "A pytest test file with one test class, using `tmp_path` fixtures, following `tests/test_scaffold.py` as a model")

**Example — task for adding a workflow section:**

```markdown
## Example Output

The new section in `bean-workflow.md` should follow this format:

#### Section Title

Brief description of the concept.

**When to apply:**
- Bullet point criteria

**How to apply:**
1. Numbered steps
```

**Example — task for adding a Python function:**

```markdown
## Example Output

The new function should follow this pattern:

def validate_example(spec: CompositionSpec) -> StageResult:
    """One-line description."""
    result = StageResult()
    # validation logic
    return result
```

**If no example is available**, note it explicitly: `> Example Output: No existing pattern — define format in this task's Goal section.` This signals to the executor that they should flag any format ambiguity before starting.

### 6. Comprehension Gate

Before implementation begins, each persona must demonstrate understanding of the codebase area they will modify. This prevents implementations that conflict with established patterns, introduce redundancy, or miss important context.

**When it applies:** Every task that modifies or creates files in the codebase (code, configuration, documentation). Pure review tasks (e.g., Tech-QA verification) are exempt.

**Comprehension criteria — the persona must understand:**

- **Existing patterns:** How similar functionality is currently implemented (naming conventions, data flow, error handling)
- **Module boundaries:** Which modules own the relevant functionality and how they interact
- **Constraints:** Any project rules, architectural decisions (ADRs), or conventions that apply to the area
- **Impact surface:** What other files or features could be affected by the change

**How to demonstrate comprehension:**

Before writing any implementation code, the persona writes a brief **comprehension note** in their task file or output directory (`ai/outputs/<persona>/`). The note must include:

1. **Area summary** (2-3 sentences) — what the relevant code area does and how it is structured
2. **Patterns identified** — key patterns, conventions, or idioms used in that area (bullet list)
3. **Constraints noted** — relevant rules, ADRs, or project conventions that apply
4. **Approach alignment** — how the planned implementation fits within the existing patterns

**Format:** Add a `## Comprehension Note` section to the task file before updating its status to `In Progress`, or write a separate file at `ai/outputs/<persona>/comprehension-BEAN-NNN.md`.

**Gate check:** The comprehension note must exist before implementation work begins. If a persona skips this step, Tech-QA should flag it during review.

### 7. Execution

Each persona claims their task(s) in dependency order:

1. Read the task file and all referenced inputs
2. Produce the required outputs in `ai/outputs/<persona>/`
3. Apply the **micro-iteration loop** if verification fails (see below)
4. Update the task file with completion status
5. Create a handoff note for downstream tasks if needed

#### Micro-Iteration Loop

When a task's verification checks fail, the executing persona applies a structured fix-verify cycle before marking the task done.

**Entry conditions** — enter the loop when any of the following occur:
- `uv run pytest` reports test failures
- `uv run ruff check foundry_app/` reports lint errors
- `/close-loop` identifies an unmet acceptance criterion
- Self-review (`/internal:review-pr`) flags a blocking issue

**Loop steps:**
1. **Diagnose** — identify the specific failure (test name, lint rule, or criterion)
2. **Fix** — make the minimal change to address the failure
3. **Verify** — re-run the failing check (`pytest`, `ruff`, or `/close-loop`)
4. **Check exit conditions** — if all checks pass, exit the loop; otherwise repeat

**Exit conditions:**
- All tests pass, lint is clean, and acceptance criteria are met → **exit, mark task done**
- Max iterations reached (3 attempts) → **stop and escalate to Team Lead** with a summary of what was tried and what still fails

**Max iterations:** 3. After 3 fix-verify cycles without full resolution, the persona must stop iterating and escalate. The escalation note should include: (1) which checks still fail, (2) what was attempted in each iteration, (3) a hypothesis for the root cause.

**Reporting:** Record the iteration count and outcome in the task file's status update. Example: `Status: Done (2 iterations)` or `Status: Blocked (3 iterations, escalated)`.

### 8. Context Diet

Workers MUST minimize context consumption during execution. Every file read and every prompt line costs tokens and shrinks the available context window. Follow these rules:

**Core principles:**

1. **Read only what the task requires.** The task file lists its Inputs — read those. Do not speculatively read files "for background."
2. **Never re-read a file you already have in context.** If you read `bean.md` during decomposition, do not read it again during execution unless it may have changed (multi-agent scenario).
3. **Use targeted reads.** When you need a specific section of a large file, use offset/limit parameters. Do not read a 300-line file to find a 10-line section.
4. **Keep prompts focused.** When delegating to a persona, include only the task-relevant context — not the full bean history, not the full backlog, not the full workflow spec.
5. **Prefer Grep/Glob over exploratory reads.** When searching for something, use search tools first to locate it, then read only the relevant file.

**Essential vs. optional context by task type:**

| Task Type | Essential (always read) | Optional (read only if needed) |
|-----------|------------------------|-------------------------------|
| **App — Developer** | Task file, source files being modified, relevant test files | bean.md (already summarized in task), other module source, full project.md |
| **App — Tech-QA** | Task file, developer's changed files, existing tests | Full module source, architecture docs |
| **Process — Developer** | Task file, document being modified, referenced docs | Full bean-workflow.md (use targeted reads), other process docs |
| **Process — Tech-QA** | Task file, developer's changed documents | Full workflow spec (use targeted reads) |
| **Infra — Developer** | Task file, config/script being modified | Full hook policy, all hook files |
| **Infra — Tech-QA** | Task file, developer's changed configs | Other infra configs |

**Anti-patterns to avoid:**

- Reading `_index.md` repeatedly during task execution (only needed during picking)
- Reading all agent persona files when only one persona is active
- Reading `bean-workflow.md` in full when you only need one section
- Including the full project architecture in every task prompt
- Re-reading files after trivial edits just to "verify" (use the edit tool's feedback instead)

### 9. Verification (VDD Gate)

The Team Lead applies the **Verification-Driven Development (VDD) gate** before closing any bean. See `ai/context/vdd-policy.md` for the full policy.

1. Check each task's Definition of Done
2. Verify outputs match the bean's Acceptance Criteria with **concrete evidence** per the VDD policy
3. Run category-specific verification checks:
   - **App beans:** `uv run pytest` (all pass), `uv run ruff check foundry_app/` (clean), new code has tests
   - **Process beans:** documents exist, cross-references valid, instructions actionable, no contradictions
   - **Infra beans:** hooks/scripts execute, git operations succeed, no regressions
4. For each acceptance criterion, confirm evidence is concrete, reproducible, and current
5. Flag any gaps for rework — a bean that fails the VDD gate stays In Progress

### 9. Closure

Once the VDD gate passes (all acceptance criteria verified with evidence):

1. Update bean status to `Done`
2. Update `ai/beans/_index.md`
3. Note any follow-up beans spawned during execution
4. **Extract rules** — Review the bean's execution for reusable knowledge:
   - **Patterns:** Techniques or approaches that worked well and should be repeated
   - **Anti-patterns:** Mistakes, rework, or friction points to avoid next time
   - **Lessons learned:** Surprising discoveries, edge cases, or workflow improvements
   - Record findings in `MEMORY.md` (concise entries) or create/update a topic file in the auto-memory directory for detailed notes. Skip this step if the bean produced no novel insights.
5. **Merge feature branch to `main`** using `/merge-bean` (Merge Captain). This step is mandatory — a bean is not fully closed until its branch has been merged to `main` and tests pass on the integrated branch

## Branch Strategy

**Every bean MUST have its own feature branch.** No exceptions. All work happens on the feature branch, never directly on `main`.

Feature branches merge directly to `main` via the Merge Captain after verification. There is no intermediate integration branch.

### Naming Convention

```
bean/BEAN-NNN-<slug>
```

Examples: `bean/BEAN-006-backlog-refinement`, `bean/BEAN-012-user-auth`

### Lifecycle

1. **Branch creation** — When a bean moves to `In Progress`, create the feature branch immediately:
   ```
   git checkout -b bean/BEAN-NNN-<slug>
   ```
   This is the **first action** after picking a bean. No work happens before the branch exists.
2. **Work on the branch** — All task commits for this bean happen on the feature branch. Never commit to `main`.
3. **Merge to main** — After the bean is verified and closed, the Merge Captain merges the feature branch into `main` using `/merge-bean`.
4. **Cleanup** — After a successful merge, the feature branch is deleted (local + remote).

### Branch Creation Rules

- `/pick-bean` always creates the feature branch (mandatory).
- `/long-run` always creates a feature branch for each bean it processes.
- Manual bean work MUST create the branch when moving to `In Progress`.
- There are no exceptions — even doc-only beans get their own branch.

## Status Values

| Status | Meaning |
|--------|---------|
| `Unapproved` | Created, awaiting human review and approval |
| `Approved` | Reviewed and approved, ready for execution |
| `In Progress` | Tasks have been created and execution is underway |
| `Done` | All acceptance criteria met |
| `Deferred` | Intentionally postponed |
