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

## §6a Context Diet

Every API turn sends the full conversation context. A 20-turn session at ~250K tokens/turn costs 5M billed input tokens. Context discipline is the single biggest lever for reducing per-bean cost.

**Core rule:** Read only what each task's Inputs list specifies. No speculative reads. Never re-read files already in context. Use targeted reads (offset/limit) for large files.

**Per-category budgets:**

| Category | What to read | What NOT to read |
|----------|-------------|-----------------|
| **Library content** | Template file + target output file only | Full library index, other personas, unrelated expertise files |
| **Process** | Affected doc files (agent .md, skill .md, workflow .md) | Entire codebase, unrelated agent files, full bean history |
| **App** | Affected module + its test file + direct imports | Full service layer, all test files, unrelated UI modules |

**Practical guidelines:**
- Before reading a file, ask: "Does this task's Inputs list reference it?" If no, don't read it.
- Use `Glob` to find files, not `Read` on directories or broad searches.
- For files >200 lines, use `offset` and `limit` to read only the relevant section.
- When running tests, run only the specific test file, not the full suite (unless verifying no regressions).
- Avoid reading `_index.md` repeatedly — once at the start of a bean is enough unless picking a new bean.

**For `/long-run` workers:**
- The orchestrator passes a `CONTEXT DIET` block in the worker prompt.
- Workers must follow it: read only task Inputs, commit after each task, exit on completion.
- Never read the full bean backlog or other beans' files from a worker.

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

## BA Engagement Mode

| Setting | Value |
|---------|-------|
| **BA Mode** | Partial |

**Values:** `Full` or `Partial` (default).

- **Full mode:** BA runs on every bean as the first step in the wave. BA maintains a requirements register at `ai/outputs/ba/requirements-register.md`, analyzes each bean's impact on requirements, updates the register, and hands off relevant requirements to the next persona. Wave order: **BA → [Architect if needed] → Developer → Tech-QA**.
- **Partial mode** (default): BA is engaged only when specific rules are triggered. See "Inclusion Criteria for Optional Personas" below for the numbered rules.

To switch modes, update the `BA Mode` value in the table above.

### Full-Mode BA Workflow

When `BA Mode: Full`, the following steps run at the start of every bean (before any other persona):

1. **Read the bean** — BA reads the bean's Problem Statement, Goal, Scope, and Acceptance Criteria.
2. **Analyze requirements impact** — BA checks the requirements register (`ai/outputs/ba/requirements-register.md`) for affected requirements. Determines if the bean requires new requirements, modifies existing ones, or has no impact.
3. **Update register** — BA adds new requirements or modifies existing entries. Each requirement has: ID, description, source bean, status (Active/Modified/Deprecated), and acceptance criteria.
4. **Handoff** — BA writes a requirements brief to `ai/outputs/ba/` listing the relevant requirements for this bean. The next persona (Architect or Developer) receives this as an input.
5. **Task file** — The Team Lead creates a BA task (numbered 01) for every bean in full mode.

### Requirements Register Format

Location: `ai/outputs/ba/requirements-register.md`

```markdown
| REQ ID | Description | Source Bean | Status | Acceptance Criteria |
|--------|-------------|-------------|--------|---------------------|
| REQ-001 | ... | BEAN-NNN | Active | ... |
```

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

#### Approval Gate

Transitioning a bean from `Unapproved` to `Approved` is a deliberate, validated action. The gate is enforced by the `/internal:approve-bean` command, which refuses to approve beans that still contain template placeholders or empty required fields.

**Entry point:**

```
/internal:approve-bean <NNN> [--rationale "<text>"]
```

**Approval checklist — every field must have real content (not placeholders, not the template's example lines):**

- [ ] **Problem Statement** — states the problem and why it matters.
- [ ] **Goal** — states the desired outcome.
- [ ] **Scope — In Scope** — at least one concrete deliverable (beyond `- Item 1` placeholders).
- [ ] **Acceptance Criteria** — at least one bean-specific criterion beyond the standard `pytest` / `ruff` lines.
- [ ] **Priority** — set to a real value (not the template default cell).
- [ ] **Category** — set to `App`, `Process`, or `Infra` (not the placeholder `(App | Process | Infra)`).

**What happens on success:**

1. `bean.md` Status is set to `Approved`.
2. The matching row in `ai/beans/_index.md` is updated.
3. A single commit captures both file changes. The commit message is `Approve BEAN-NNN: <title>`; when `--rationale` is supplied, it is recorded in the commit body.
4. The commit author is the audit trail for **who approved** (derived from git identity).

**What happens on failure:**

The command prints the list of missing or placeholder fields and exits without modifying any file. No commit is created. The reviewer fixes the flagged fields in `bean.md` and retries.

**Implementation note:** The criteria are encoded in `foundry_app/services/bean_approval.py` (`check_bean_approvable`). The same rules are exercised by `tests/test_bean_approval.py`, so the gate behaves identically whether invoked through the command or the Python helper.

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

**BA — engagement depends on the BA Mode flag** (see "BA Engagement Mode" above).

**Full mode:** BA runs on every bean — no rules to check.

**Partial mode** (default) — include the BA when ANY of these apply:

1. **Requirements ambiguity** — the bean has 3+ valid interpretations of what should be built or how it should behave
2. **User-facing behavior change** — the bean changes how end users interact with the system (new screens, modified workflows, changed defaults, new user-facing concepts)
3. **Multi-stakeholder trade-offs** — the bean involves competing concerns (performance vs usability, security vs convenience) that need documented trade-off analysis
4. **Documentation or specification task** — the bean's primary deliverable is documentation, specifications, or process definitions (BA is better suited than Developer for requirements-heavy writing)
5. **Scope uncertainty** — the bean's In Scope / Out of Scope boundaries are unclear, contentious, or likely to expand during implementation
6. **Cross-bean requirements impact** — the bean may affect requirements or assumptions of 2+ other beans (new constraints, changed interfaces, deprecated behaviors)
7. **New user-facing concept** — the bean introduces a term, workflow, or mental model that users need to understand

**Do NOT engage the BA for (partial mode):** bug fixes with obvious expected behavior, infrastructure/CI/CD changes with no user-facing impact, code refactoring that preserves existing behavior, test-only beans, single-file configuration changes, beans where Problem Statement, Goal, and Acceptance Criteria are already precise and unambiguous.

**When in doubt:** If the bean affects what users see or how they work and you are unsure whether the requirements are clear enough, engage the BA. A lightweight requirements review costs less than rework from misunderstood requirements.

**Architect — include when ANY of these apply:**

1. **New subsystem or module** — creates a new module, service, package, or top-level directory
2. **Refactoring driven by new functionality** — adds features that require restructuring existing code (moving functions between modules, changing class hierarchies, splitting/merging files)
3. **Cross-cutting change** — modifies public APIs, data models, or interfaces used by 3+ modules
4. **New external dependency** — introduces a new third-party library, framework, or external service
5. **Data format or schema change** — changes, creates, or translates between data formats or configuration schemas
6. **Architectural decision with alternatives** — involves a design choice with 2+ reasonable approaches and long-term consequences (triggers an ADR)
7. **Project foundation or scaffold** — sets up initial project structure or establishes foundational patterns for subsequent work
8. **Pipeline or workflow restructuring** — changes execution order, stage boundaries, or data flow of a processing pipeline
9. **Cross-boundary integration** — connects previously independent subsystems or introduces new integration points

**Do NOT engage the Architect for:** single-file bug fixes, UI text/styling changes, adding form elements to existing screens, config value changes, test-only beans, documentation-only beans, routine CRUD following established patterns.

**When in doubt:** If the bean touches 3+ files across different directories and you hesitate, engage the architect. The cost of a lightweight review is low; the cost of unrecorded structural decisions is high.

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
- **Inputs:** What the owner needs to read. **Required and non-empty** — the `validate-task-inputs.py` hook (BEAN-272, library: `ai-team-library/claude/hooks/`) blocks the Status→`In Progress` transition and any `/spawn-task` dispatch when this field is missing, empty, or only contains placeholder values. Escape hatch for genuinely input-less tasks: `Inputs: NONE (justified: <reason of at least 10 chars>)`. Escape-hatch use is counted in the bean's Orchestration Telemetry (BEAN-278) so over-use surfaces.
- **Example Output:** A concrete example of the expected output format (see below)
- **Definition of Done:** Concrete checklist

#### Examples-First Principle (optional)

> **Status (2026-07, SPEC-029):** demoted to optional — 21 of 342 task
> files used it. Include an Example Output when the task's deliverable
> shape is genuinely ambiguous; skip it for routine tasks.

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

### 6. Comprehension Gate (retired as a mandatory step)

> **Status (2026-07, SPEC-029):** retired as written. Across 342 task
> files, 3 carried a Comprehension Note — a ~99% skip rate with no
> enforcement and no observed quality signal. The INTENT survives in
> lighter forms: read the task's Inputs before acting (enforced by
> validate-task-inputs), follow existing patterns (persona operating
> principles), and Tech-QA flags pattern violations at review. A persona
> MAY still write a `## Comprehension Note` for genuinely unfamiliar
> areas; it is no longer required and its absence is not a review flag.

### 7. Execution

Tasks are executed by **specialist workers dispatched via `/spawn-task`** (BEAN-270; ADR-017, superseding ADR-008's tmux transport). The orchestrator does not play the role inline by default. `/spawn-task` issues a background `Agent` call with `subagent_type=<persona>` — with worktree isolation when a wave's tasks run in parallel — under the standard permission mode (never permission-bypass flags). The worker reads only the task's `Inputs:` plus the persona's own context bundle.

In-conversation role-switching (the orchestrator reading the task and executing it itself in the same window) remains a fallback for tiny tasks where dispatch overhead is not justified. It is not the default.

For each task in dependency order:

1. Dispatch with `/spawn-task <task-file>`. The worker:
   1. Reads the task file and all referenced inputs (the `validate-task-inputs.py` hook ensures Inputs is populated before dispatch — BEAN-272).
   2. Produces the required outputs in `ai/outputs/<persona>/`. The artifacts must be the types declared in the persona's `contracts.yml` (`produces:`, BEAN-273).
   3. Applies the **micro-iteration loop** if verification fails (see below).
   4. Updates the task file with completion status.
2. The orchestrator runs `/handoff <from> <to>` to package outputs for the next persona — typed packets per the artifact registry's required fields and any pair-fields extras (BEAN-276). `/handoff` appends a row to `ai/handoffs/_index.md` for traceability and blocks if a required field is missing.

See `ai/context/orchestration-architecture.md` for the model in full.

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

See **§6a Context Diet** near the top of this document — the single canonical statement of the rules (SPEC-029 removed the duplicate copy that lived here).

### Gate Enforcement Status (SPEC-029)

One table, so nobody has to guess which gates are machinery and which are
convention:

| Gate | Enforcement |
|------|-------------|
| Branch protection (no edits on main) | **Hook** (settings.json PreToolUse) |
| Task `Inputs:` present at dispatch | **Hook** (validate-task-inputs.py) |
| Bean Done requires passing VDD report | **Hook** (vdd-gate.py, SPEC-008) |
| Telemetry stamping | **Hook** (telemetry-stamp.py) |
| Format/lint on save | **Hook** (format-on-save.py, non-blocking) |
| Typed handoff packets (/handoff) | Convention (skill prose) — candidate for a future hook |
| Molecularity / Blast-Radius / Bottleneck checks | Convention (Team Lead judgment) |
| Comprehension Gate | **Retired** (see §6) |
| Examples-First | Optional (see Task Specification) |

### 9. Verification (VDD Gate)

The Team Lead applies the **Verification-Driven Development (VDD) gate** before closing any bean. See `ai/context/vdd-policy.md` for the full policy.

The gate is automated via `/vdd <bean-id>` (BEAN-277). The skill parses the bean's Acceptance Criteria checklist, runs each "concrete evidence" check programmatically (evidence-type prefixes: `(test:…)`, `(lint:…)`, `(file:…)`; un-prefixed criteria fall back to manual confirmation), and writes a structured pass/fail report to `ai/outputs/tech-qa/vdd-<bean-id>.md`. `/merge-bean` refuses to merge when the report is missing or shows fail.

Apply the gate as follows:

1. Check each task's Definition of Done
2. Run `/vdd <bean-id>` to produce the structured report
3. The skill runs category-specific verification checks:
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
