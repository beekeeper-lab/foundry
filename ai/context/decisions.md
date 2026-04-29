# Architecture Decisions

> Record ADRs here as the project evolves.

---

## ADR-001: Overlay as a Mode of the Existing Generation Pipeline

| Field | Value |
|-------|-------|
| **Date** | 2026-02-07 |
| **Status** | Accepted |
| **Bean** | BEAN-002 |
| **Deciders** | Architect |

### Context

Foundry's generator pipeline produces Claude Code project folders by running six stages in sequence: Validate, Scaffold, Compile, Copy Assets, Seed, Write Manifest. Currently, it only writes to a new/clean output directory. When using Foundry on an existing project (the dogfooding use case), users must generate to a staging directory and manually copy the `.claude/` and `ai/` subtrees into their project root. This is fragile and does not support iterative re-generation (e.g., after adding a persona or changing stacks).

We need a way to write generated files directly into an existing project directory, merging with existing content, detecting conflicts, and supporting dry-run previews.

### Decision

Implement overlay as a **mode of the existing `generate` command**, not as a separate tool or subcommand. The overlay mode uses a **two-phase approach**:

1. **Phase 1:** Run the existing pipeline stages unchanged, writing all files to a temporary directory.
2. **Phase 2:** Compare the temp directory against the target, classify each file (create / unchanged / conflict), and apply the plan.

Key design points:

- **New module `overlay.py`** contains all overlay-specific logic (comparison, plan building, plan application, reporting). Existing stage modules are not modified.
- **`generate_project()`** gains `overlay`, `dry_run`, and `force` keyword parameters.
- **Conflict classification** uses byte-for-byte content comparison. Any file that exists with different content is a conflict. The previous manifest provides advisory provenance context but does not change classification.
- **Sidecar files** (`.foundry-new`) are written alongside conflicting files so users can diff and merge manually.
- **`--force`** overwrites conflicts without writing sidecars.
- **`--dry-run`** produces a categorized report without writing any files to the target.
- **Orphaned files** (in previous manifest but not in current generation) are reported but never automatically deleted.

### Consequences

**Positive:**
- Existing pipeline stages remain unchanged and independently testable.
- Overlay logic is isolated in a single module, easy to test and reason about.
- Two-phase approach eliminates partial-write risk: if generation fails, the target directory is untouched.
- Dry-run is trivially implemented by skipping phase 2's apply step.
- Conservative conflict detection protects user work by default.

**Negative:**
- Two-phase approach requires generating to a temp directory, which doubles disk I/O. For the expected file count (30-80 files, mostly small markdown), this is negligible.
- The return type of `generate_project()` gains a third element, requiring minor updates to existing callers.
- No automatic file merging: users must resolve conflicts manually. Structured merge (especially for `settings.local.json`) is deferred to a future iteration.

### Alternatives Rejected

1. **Separate `overlay` subcommand:** Rejected because overlay _is_ generation with a different write strategy. A separate subcommand would duplicate pipeline orchestration logic.
2. **Modify each stage to check before writing:** Rejected because it scatters overlay conditionals across six modules, making the concern impossible to test in isolation.
3. **Wrap the `_write` helper with a conditional writer:** Partially viable but still requires threading overlay context through every stage call. The two-phase approach is cleaner.

---

## ADR-002: Editable Dirs Field on FileSystemPolicy

| Field | Value |
|-------|-------|
| **Date** | 2026-02-07 |
| **Status** | Accepted |
| **Bean** | BEAN-004 |
| **Deciders** | Architect |

### Context

The safety service hardcodes `Edit(src/**)`, `Edit(tests/**)`, and `Edit(ai/**)` in `safety_to_settings_json()`. Projects with non-standard source directories (e.g. `foundry_app/`, `lib/`, `app/`) must manually fix `settings.local.json` after generation.

### Decision

Add an `editable_dirs: list[str]` field to `FileSystemPolicy` with a default of `["src/**", "tests/**", "ai/**"]`. The safety service iterates this list to generate `Edit()` rules.

**Field name:** `editable_dirs` (not `source_dirs`) because the list includes non-source directories like `tests/**` and `ai/**`.

**Default value:** `["src/**", "tests/**", "ai/**"]` — matches current hardcoded behavior exactly, ensuring zero-effort backward compatibility.

### Consequences

**Positive:**
- Projects with non-standard layouts work out of the box.
- Backward compatible: existing compositions and presets get the same defaults.
- Simple, single-field change with no cascading model restructuring.

**Negative:**
- Users must know their directory layout at composition time (no auto-detection).
- The field name `editable_dirs` could be confused with filesystem deny_patterns. Mitigated by tooltip text in the wizard.

### Alternatives Rejected

1. **`source_dirs` field name:** Rejected because the field covers `tests/**` and `ai/**`, not just source code.
2. **Separate fields for source, test, and AI directories:** Over-engineered. A single list is simpler and more flexible.
3. **Auto-detect from project structure:** Out of scope — generation often happens before the project directory exists.

---

## ADR-003: Project Charter as Scaffolded TODO Template

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-252 |
| **Deciders** | Architect |

### Context

External audit (2026-04-17) flagged that a freshly generated Foundry project has no purpose statement. When `spec.project.description` is empty, the generated README falls back to `"AI-team-backed project for <Name>"` — a single line of generic prose that tells personas nothing about what the project is, who it serves, or what "done" looks like. The audit called this the #1 day-1 blocker: *"Nine personas, zero product. A team with no goal will invent one, inconsistently."*

Two implementation paths were considered:

1. **Scaffold a charter file** — emit `ai/context/project-charter.md` from the scaffold pipeline as a structured TODO template (Purpose / Audience / Success Criteria / Non-Goals / Constraints).
2. **Promote `description` to required** — make `ProjectIdentity.description` mandatory with a minimum length, validated at the wizard and CLI boundaries.

### Decision

Scaffold `ai/context/project-charter.md` as a structured TODO template. The file is emitted by `foundry_app/services/scaffold.py` alongside `README.md`, overlay-safe (only written if missing), with sections for Purpose, Audience, Success Criteria, Non-Goals, and Constraints. If `spec.project.description` is set it is echoed under the title; otherwise a TODO line is shown.

### Consequences

**Positive:**
- Strictly additive — does not break existing wizard flows, CLI invocations, or YAML files in the wild.
- Mirrors the existing README emission pattern (overlay-safe, footer with version+date), so the implementation surface is small and well-precedented.
- The TODO-marked sections are visually loud — personas opening the project see immediately that there is unfilled context to address.
- Composes with future hardening: a follow-up bean can promote `description` to required without contradicting this decision.

**Negative:**
- A charter file with the TODO markers still in place is not enforced — a careless user can ignore it. Mitigated by the `> **Status:** TODO` admonition at the top of the file, which is greppable.
- Adds one more file to the scaffold output (currently ~10 files at the project root level).

### Alternatives Rejected

1. **Promote `description` to required (Option 2):** Larger blast radius — touches the model, validator, wizard, and CLI; breaks existing YAML compositions that rely on the optional default; a one-line description is still terse compared to a five-section charter. Reserved as a possible follow-up if the charter alone proves insufficient.
2. **Embed the charter in `CLAUDE.md`:** CLAUDE.md is already instruction-dense and is regenerated from the spec; mixing user-authored prose into a regenerated file invites overwrite conflicts.
3. **Embed the charter in `README.md`:** README is for humans landing on the repo; the charter is for personas opening the project. Co-locating with `ai/context/project.md` (the architecture/module map) keeps the AI-team-facing context in one place.

---

## ADR-004: Seeded Tasks Flow Through a Starter Bean

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-254 |
| **Deciders** | Architect |

### Context

External audit (2026-04-17) flagged that seeded tasks were orphaned: `ai/tasks/_index.md` listed tasks assigned to personas, but `ai/beans/_index.md` was empty and no task was linked to a bean. The declared unit of work is the bean (per `ai/context/bean-workflow.md`), so tasks that live in `ai/tasks/` bypass the very system that is supposed to track them. A Team Lead's first action on a newly generated project is meant to be *picking a bean* from the backlog — but there was no starter bean for them to pick.

### Decision

The Seeder stage emits a single starter bean, `BEAN-001-bootstrap`, under `ai/beans/`. The bean is created with `Status: Approved` so the Team Lead can claim it immediately. Its `tasks/` directory holds the same set of per-persona tasks the Seeder used to write into `ai/tasks/_index.md`, one task per file, named `NN-<owner>-<slug>.md`. `ai/beans/_index.md` is appended with a BEAN-001 row. The bean's Problem Statement references `ai/context/project-charter.md` (emitted by BEAN-252) when that file is present, falling back to a generic "bootstrap" placeholder otherwise.

`ai/tasks/` remains as an empty scaffold-created directory so downstream library commands that write task files (`seed-tasks`, `new-work`, `release-notes`) still have a target, and so `validate-repo`'s structural path list is unaffected.

### Consequences

**Positive:**
- Seeded work enters through the bean workflow — no orphan tasks.
- Team Lead's day-1 action has a target (`BEAN-001`) that can be picked without any setup.
- Tasks are now first-class bean artifacts, so telemetry, status changes, and outputs all flow through the bean directory contract the rest of the workflow already speaks.
- Strictly additive — no existing generated projects lose files, because the new write location is a parallel tree (`ai/beans/BEAN-001-bootstrap/`).

**Negative:**
- Two task file shapes coexist in the library (the old `ai/tasks/NNN-{slug}.md` layout referenced by `seed-tasks.md` / `new-work.md` commands, and the new bean-scoped `NN-<owner>-<slug>.md` layout). These command docs describe downstream library commands the generated project runs later — they can migrate independently.

### Alternatives Rejected

1. **Leave `ai/tasks/_index.md` as-is:** Does not solve the audit's complaint. Rejected.
2. **Delete `ai/tasks/` entirely:** Larger blast radius — the library's `seed-tasks` / `new-work` / `release-notes` commands reference that path. Keeping the empty directory costs one `mkdir` and preserves the contract.
3. **Emit one starter bean per persona:** Multiplies the backlog with beans that share a single goal (bootstrap). A single bean whose `tasks/` directory enumerates per-persona work mirrors the normal bean → tasks decomposition pattern exactly.

---

## ADR-005: Declarative `Conflicts With` in Hook Pack Metadata

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-262 |
| **Deciders** | Architect |

### Context

External review (2026-04-17) found that `az-read-only` and `az-limited-ops` silently cancel each other when both are selected: the read-only guard blocks every mutating verb while the limited-ops guard is trying to permit deployment verbs. The generator today composes hook packs from whatever the user selects without checking whether any pair is contradictory. Result: a project that *appears* to allow deploys but actually blocks them at every `PreToolUse:Bash` hook — a silent misconfiguration that only surfaces when someone tries to deploy.

The same pattern applies to the AWS pair (`aws-read-only` ⇄ `aws-limited-ops`) and is latent in any future "strict vs. permissive" hook pair that may land in the library.

Two detection strategies were considered:

1. **Declare conflicts in hook pack metadata** — add a `## Conflicts With` section to each hook pack markdown file, parsed by the library indexer and enforced by the pre-generation validator.
2. **Hard-code pairs in `safety_writer.py`** — maintain a Python-side list of conflict pairs next to the existing `_HOOK_PACK_REGISTRY`.

### Decision

Declare conflicts in the hook pack markdown files (Option 1). Each hook pack that conflicts with another lists the conflicting pack id under a `## Conflicts With` section (one id per bullet). The library indexer parses this section into `HookPackInfo.conflicts_with: list[str]`. The pre-generation validator (`foundry_app/services/validator.py`) adds a `_check_hook_conflicts` check that emits a `hook-pack-conflict` **error** when a composition enables both sides of any declared conflict pair.

Conflict declarations are symmetric by convention — each side lists the other — but the validator treats any one-sided declaration as sufficient to flag the pair. This makes the detection robust to declaration drift.

### Consequences

**Positive:**
- Conflict declarations live alongside the behavior they describe (the hook pack markdown), so adding a new conflicting pair is a documentation change, not a Python change.
- The validator surfaces a blocking error with a clear message before any file is written, preventing silent misconfiguration at emit time.
- Extends naturally to future conflict pairs without schema churn.

**Negative:**
- Declaration drift is possible if only one side of a pair is updated. Mitigated by treating one-sided declarations as binding and by covering both sides in tests.
- Pair-level only — does not detect N-way conflict cliques. Acceptable for now; explicitly noted as out-of-scope in the bean.

### Alternatives Rejected

1. **Hard-code pairs in `safety_writer.py` (Option 2):** Keeps Python and markdown out of sync; adding a conflict requires a code change in a file that already holds the hook command strings, bloating an already long module. Rejected because the declaration belongs with the hook pack, not with the emitter.
2. **Runtime detection in the generated project** — have the hooks themselves detect overlap at `PreToolUse` time. Rejected: out of scope per the bean, and detection at generation time is both cheaper and more visible to the author.

---

## ADR-006: Keep Posture Names, Document the Taxonomy Explicitly

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-250 |
| **Deciders** | Architect |

### Context

External review flagged the hook posture taxonomy (`baseline` / `hardened` / `regulated`) as "conceptually muddy": the reviewer observed compositions at `baseline` that appeared to enable multiple git, cloud, compliance, QA, lint, and secret controls, prompting the question "if this is baseline, what does hardened mean?"

The reviewer proposed two resolutions:
1. **Slim** `baseline` so the word matches the posture.
2. **Rename** the levels so the taxonomy is honest about what each level turns on.

Inspecting the code, the current per-posture **base pack set** in `safety_writer._POSTURE_BASE` is already narrow:

| Posture | Base packs (stack-independent) | Base count |
|---------|--------------------------------|------------|
| `baseline` | `git-commit-branch` | 1 |
| `hardened` | `git-commit-branch`, `git-push-feature`, `security-scan` | 3 |
| `regulated` | `git-commit-branch`, `git-push-feature`, `security-scan`, `compliance-gate`, `post-task-qa` | 5 |

Stack-aware layering (BEAN-255) adds at most one lint pack (expertise-driven) and one cloud pack per cloud provider, and cloud packs are only added at `hardened`/`regulated`. So a `baseline` project with Python + AWS gets exactly **two** packs: `git-commit-branch` + `pre-commit-lint`. Not "muddy" in the code — muddy in the **documentation and example compositions**, where the reader cannot infer this without reading `safety_writer.py`.

The reviewer's premise (that `baseline` includes Azure, compliance, QA, secret controls) does not match the base-pack set. It matches what a user sees if they look at the full library of available packs and assume all of them are enabled at `baseline`, or if they look at an example YAML where an explicit `packs:` list overrides stack-aware defaults.

### Decision

**Keep the existing names (`baseline` / `hardened` / `regulated`) and make the taxonomy visible through documentation + a lock-in test.**

Specifically:
1. Add `ai/context/hook-posture.md` that states — for each posture — the **intent**, the **base pack list**, the **default enforcement mode**, and how stack-aware layering adds to it.
2. Expose `posture_base_packs(posture) -> list[str]` as a public helper in `safety_writer.py` so the mapping is importable (for tests, UI surfaces, and future tooling) and no longer buried in a module-private dict.
3. Add a Tech-QA test that asserts `posture_base_packs(Posture.BASELINE|HARDENED|REGULATED)` matches the documented list — so the doc and code cannot drift.

### Rationale — why keep the names

- **The code is not broken; the narration is.** The existing mapping already forms a reasonable ordering (1 → 3 → 5 base packs). Slimming `baseline` further would mean zero base packs, which removes the one guardrail (`git-commit-branch`) every generated project benefits from.
- **Rename has a large blast radius** — every example YAML, every loaded composition, every settings default, every docs reference, every screenshot in flight would change. The bean even calls this out as "visible in every composition YAML."
- **The reviewer's concern is answered by making the taxonomy legible**, not by changing identifiers. A reader who opens `hook-posture.md` can predict the pack count within a reasonable range for each level — which is exactly the bean's stated goal.
- **`regulated` has a distinct meaning** (compliance + post-task-qa) that `hardened` does not capture. Collapsing to a two-level rename would lose that signal.

### Alternatives Rejected

1. **Rename `baseline` → `minimal`, `hardened` → `standard`, `regulated` → `strict` (reviewer's option B).** Rejected: forces migration of every composition YAML, settings key, UI label, and test. The existing names already suggest an ordering once documented. The rename trades a documentation problem for a migration problem.
2. **Slim `baseline` to zero base packs.** Rejected: `git-commit-branch` is the one guardrail we want on by default — it blocks edits on `main` / `master` / `test` / `prod`. Removing it means every new project starts with no safety net.
3. **Collapse to two levels (`standard` / `strict`).** Rejected: `regulated` encodes a compliance-adjacent intent (compliance-gate + post-task-qa) that doesn't fit the `hardened` bucket. Users picking `regulated` are making a different statement than users picking `hardened`.

### Consequences

- `ai/context/hook-posture.md` becomes the canonical reference for the taxonomy. `safety_writer.py` module docstring and `hook-selection.md` link to it.
- A failing lock-in test flags any future silent change to `_POSTURE_BASE` — taxonomy changes must update the doc too.
- No migration aliases are needed — enum values are unchanged.
- If a future bean wants to restructure levels, this ADR is superseded and the rename migration happens then.

---

## ADR-007: Planning-Only Scaffolding — Foundry Does Not Generate App Code

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-253 |
| **Deciders** | Architect |

### Context

External audit (2026-04-17): *"No code scaffolding despite claiming React/TS. No `package.json`, `tsconfig.json`, `vite.config.ts`, `src/`, `.eslintrc`, no lockfile. A Developer cannot run anything on day 1."*

The audit is factually correct: Foundry generates the AI-team scaffold (`.claude/`, `ai/`, `CLAUDE.md`, agent/member files, starter bean, project charter) but not the application-code scaffold (`package.json`, `pyproject.toml`, `src/`, `tsconfig.json`, lockfiles, etc.). A persona opening the generated project cannot run `npm test` or `uv run pytest` until a human initializes the app.

The audit frames this as a bug. We frame it as a scope question: *should* Foundry scaffold app code, and if so, how far should that scope extend? Three stances were considered.

1. **Planning-only** — Foundry scaffolds the AI-team context only; the user initializes their app with the stack-appropriate command (`npm create vite@latest`, `uv init`, `cargo new`, …).
2. **Minimal stub per stack** — Foundry emits a tiny stack-specific skeleton (e.g. `package.json` + `src/index.ts` for React/TS, `pyproject.toml` + module dir for Python) alongside the AI-team scaffold.
3. **Delegate to ecosystem tools** — Foundry shells out to `cookiecutter` / `npm create` / `yo` / … at generation time.

### Decision

**Stance 1 — Planning-only.** Foundry does not scaffold stack-specific app code. The generated `CLAUDE.md` includes a Scope section stating this explicitly; the generated `README.md` points users at `docs/starter-stacks.md` in the Foundry repo, a cheat sheet of canonical init commands per supported expertise. Paired with ADR-relevant work in BEAN-251 (narrow `Edit(ai/**)` permission model), the two decisions produce a single coherent posture: *Foundry manages planning artifacts under `ai/`; humans initialize and implement the app.*

### Consequences

**Positive:**
- Foundry stays small and focused. The unique contribution is the AI team, not a competing starter-template generator.
- Dodges the stack-template treadmill: React/Vite/Next/Vue/Python/Rust/Go each evolve their own canonical generators on their own cadence. Bundling scaffolders means inheriting every one of those churns indefinitely.
- Aligns with the permission model already shipped: the generated `settings.local.json` grants `Edit(ai/**)` only, which is exactly right for a Planning-only scope.
- The reversal direction is cheap: any future bean can add Stance 2 or 3 on top of the existing core without breaking any project generated under Stance 1. Generated output is a strict subset of any future expansion.

**Negative:**
- Day-1 gap: the generated project has no `package.json` or `pyproject.toml`, so a persona cannot "run the app" until a human runs one init command. Mitigated by `docs/starter-stacks.md` and by the README's Getting Started pointer.
- Personas that expect stack-specific files (a test harness, a lint config) must degrade gracefully until the human initializes the app. Expected — this is part of what "Planning-only" means.

### Reversibility

The two directions are asymmetric and this decision chooses the reversible one:

- **Planning-only → scaffolders (reversible).** Any future bean can add stack-specific generation on top of the current core. No existing generated project breaks because the current output is a strict subset of what an expanded Foundry would produce.
- **Scaffolders → Planning-only (irreversible in practice).** Once Foundry ships a `package.json` generator and users depend on it, removing it later deprecates every project that relied on the shipped stub. Either users keep the stale stub or migrate off it — both are support burden.

Choose the reversible direction. The audit's complaint is real, but it does not force scaffolders; it forces *explicitness* about the scope. That is what this ADR and its paired generator changes provide.

### Alternatives Rejected

1. **Stance 2 — Minimal stub per stack:** Rejected. A true minimum-viable stub for a modern stack is never one file (React/TS alone needs `package.json` + `tsconfig.json` + `vite.config.ts` + `index.html` + `src/main.tsx` to boot). Shipping stubs commits Foundry to tracking upstream format changes forever. Once shipped, users depend on the stubs, and removing them later is a breaking change. The surface Foundry would take on is not justified by the audit's complaint.
2. **Stance 3 — Delegate to ecosystem tools:** Rejected. Adds runtime dependencies Foundry does not otherwise need (Node, `cookiecutter`, `yo`). Introduces a new configuration surface in the composition spec (which ecosystem tool per expertise?). Error paths multiply (missing PATH entries, upstream tool version skew). Still coupled to upstream template drift — just laundered through another layer.
3. **Add `spec.generation.scaffold_app_code` toggle:** Rejected. A toggle implies both modes are supported; supporting both means Foundry owns both, which defeats the point of this ADR. A toggle is a commitment, not a hedge.
4. **Retrofit existing generated projects:** Out of scope. This ADR governs new generations; existing projects in the wild are unaffected.

---

## ADR-008: `/spawn-task` Per-Task Dispatch Mechanism

| Field | Value |
|-------|-------|
| **Date** | 2026-04-28 |
| **Status** | Accepted |
| **Bean** | BEAN-270 |
| **Deciders** | Architect |

### Context

Today, "delegation" inside a bean is convention only: the Team-Lead writes
task files to `tasks/NN-<owner>-<slug>.md`, and the same Claude session
plays Developer, then plays Tech-QA. There is no `Agent` tool boundary
between roles. The orchestrator supervises itself, and role baggage,
prior-task context, and unrelated reads accumulate in one window. The
Anthropic supervisor pattern's main benefit — context isolation per
specialist — is forfeited.

`/spawn-bean` already exists, but it dispatches Team-Lead for a *full bean
lifecycle*. There is no command that dispatches a single specialist for a
single task. This ADR fixes the contract for that command — `/spawn-task`
— so the Implementing task (BEAN-270 task 02) can build against a stable
spec.

The decision must answer three questions: (1) how does `/spawn-task` choose
between two execution paths, (2) what does it pass to the chosen path, and
(3) when should it warn the user that they should be using a stronger form
of dispatch.

### Decision

**1. Runtime detection rule.** `/spawn-task` chooses its execution path
from a single environment check:

```
[ -n "$TMUX" ]
```

When `$TMUX` is non-empty, the command runs the **tmux path**: create a
git worktree on the task's bean branch, write a status file at
`/tmp/agentic-task-BEAN-NNN-<task-slug>.status`, open a child tmux window
named `task-NNN-<slug>`, and launch a `claude --dangerously-skip-permissions`
process whose positional argument is the task prompt. This mirrors the
`/spawn-bean` pattern and inherits its watchdog/auto-close behavior.

When `$TMUX` is empty, the command runs the **Agent-tool path**: the
calling Claude session emits a single `Agent(subagent_type=<persona>,
description=..., prompt=<task prompt>)` call. The subagent gets a fresh
context, returns one summary message, and the calling session captures
that summary into the task's Telemetry row. No tmux, no worktree, no
status file.

The detection rule is intentionally one-shot. There is no
`--force-tmux` / `--force-agent` flag. If the user wants the other path,
they enter or exit tmux. Two flags would invite "wrong path because I
forgot the flag" failures; one rule produces deterministic dispatch.

**2. Agent-tool prompt schema.** Whichever path runs, the prompt has the
same five required sections, in this order:

| Section | Content |
|---------|---------|
| **Role** | One line: `You are the <persona> persona. Your job: <one-sentence task goal>.` |
| **Task file** | Absolute path to the task's `NN-<owner>-<slug>.md` file. Worker reads this first. |
| **Inputs** | Verbatim the task's `Inputs:` list (paths, anchors). The worker reads only these. |
| **Acceptance** | Verbatim the task's `Acceptance Criteria` block. |
| **Completion contract** | Three sentences max: (a) flip task Status to `Done` when criteria met, (b) commit on the current branch, (c) exit. |

The persona's own context bundle (`ai-team-library/personas/<persona>/persona.md`)
is referenced by name, not inlined — the worker reads it once on startup.
This keeps the prompt small (no copy-pasted persona body) and lets persona
edits propagate without re-issuing in-flight prompts.

The schema is identical for both paths so reviewers and tooling can audit
dispatch correctness from one rubric, regardless of execution mode.

**3. Reminder-banner heuristic.** When `/spawn-task` runs in the
Agent-tool path (i.e., not in tmux), it prints a one-line reminder iff
either condition holds:

- The task's metadata table has `priority: high` (case-insensitive).
- The task's bean has **≥4 remaining tasks** with status not in `{Done, Skipped}`.

The reminder reads:

```
Tip: tmux + /long-run --fast gives this task an isolated worker context. Consider relaunching there for high-priority or multi-task work.
```

Below either threshold, no banner is emitted — the Agent-tool path is the
right tool for one-off small dispatches and the warning would be noise.
The threshold is intentionally additive (either trigger fires it) and
intentionally generous on the bean side: 4 remaining tasks is the rough
breakpoint where in-process role-switching starts mixing meaningfully
unrelated context for the calling session.

### Out of Scope

- **No agent retry logic.** If the Agent-tool path returns failure, the
  caller (Team-Lead) decides what to do. `/spawn-task` does not loop.
- **No cross-task state.** Each `/spawn-task` invocation is independent.
  Tasks coordinate through committed files, not through `/spawn-task` itself.
- **No replacement for `/spawn-bean`.** `/spawn-bean` keeps its place for
  bean-level dispatch. `/spawn-task` is strictly for individual tasks
  inside an already-claimed bean.
- **No `Inputs:` validation.** That is BEAN-272's responsibility — a
  separate hook integrated into the dispatch path. `/spawn-task` calls
  the validator if it exists; absence is not an error in this bean.
- **No `produces:`/`consumes:` enforcement.** That is BEAN-273's. When
  it lands, it adds a "consumed types as required reading" line under
  the prompt's Inputs section.

### Consequences

**Positive:**

- The supervisor pattern becomes structural rather than aspirational: one
  command produces real isolation (tmux process or fresh subagent context)
  per task.
- Identical prompt schema across paths eliminates dispatch-correctness
  drift. A reviewer can audit one rubric.
- The detection rule is one line of bash and one line of docs. No flag
  surface to keep coherent.

**Negative:**

- Detection is binary — there is no in-between for users who run inside
  `screen`/`zellij`/etc. The reminder banner partially mitigates by
  surfacing the recommended setup; affected users can opt into tmux.
- Two execution paths means two test surfaces. The verification task
  (BEAN-270 task 03) flags the in-tmux path as a manual test until a
  durable harness exists.

### Alternatives Rejected

1. **Single execution path via Agent tool only.** Rejected. The
   Agent-tool path is in-process: subagents share the calling session's
   process and quota. Long-running parallel work (`/long-run --fast N`)
   needs OS-level isolation, which only the tmux path provides.
2. **Single execution path via tmux only.** Rejected. Tmux is a
   prerequisite many invocations don't have (one-off task dispatch from
   an IDE-embedded Claude). Forcing tmux for every dispatch raises the
   activation cost for the simple case.
3. **`--mode=tmux|agent` flag instead of `$TMUX` detection.** Rejected.
   A flag commits the user to remembering it; `$TMUX` is observable
   ground truth and matches "the runtime you are actually in."
4. **Inlined persona context in the prompt.** Rejected. Inlining bloats
   every prompt and stales when the persona file changes. Reference by
   path lets each spawn read the current source.
5. **Always emit the reminder banner outside tmux.** Rejected. For a
   one-task one-bean dispatch, the Agent-tool path is exactly right; a
   blanket reminder trains users to ignore it.

### Reversibility

The schema (sections + order) is the load-bearing piece. Adding sections
later (e.g., a `Consumes:` line when BEAN-273 lands) is additive and
backwards-compatible — workers tolerate trailing content. Reordering or
renaming existing sections would invalidate every cached worker prompt
template; that is the only edit that requires a follow-up bean.

---

## ADR-009: ClaudeKit as Canonical Source for Cross-Project Skills

| Field | Value |
|-------|-------|
| **Date** | 2026-04-29 |
| **Status** | Accepted |
| **Bean** | BEAN-280 |
| **Deciders** | Architect |

### Context

Foundry has two paths for delivering `.claude/` content into a generated
project:

1. **Subtree mode** (`foundry_app/services/subtree_setup.py`) —
   `git subtree add --prefix=.claude <claude_kit_url> main --squash`.
   The generated project receives the full contents of ClaudeKit's
   `.claude/shared/` tree, including everything under `skills/`.
2. **Library-copy mode** (`foundry_app/services/asset_copier.py`) —
   walks `<library_root>/claude/` and copies files into the new
   project's `.claude/`. Skills are sourced from
   `<library_root>/claude/skills/`.

The two paths produce **different skill sets**. The
`generate-image` and `generate-screen` skills live only in
`.claude/shared/skills/` (the ClaudeKit submodule, mounted at
`<foundry_root>/.claude/shared/`). They are **not** present in
`ai-team-library/claude/skills/`. Therefore, today, library-copy-mode
generated projects silently miss `generate-image` and `generate-screen`.
A subtree-mode project gets them; a library-copy-mode project does not.
There is no diagnostic — the omission is invisible until a downstream
persona invokes `/generate-image` and finds nothing.

This is not a one-off oversight. The same shape will repeat for every
future cross-project skill that lives only in the kit (the media skills
proposed in BEAN-282 / BEAN-283 are the next two examples — see
`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md`
for the motivating design). The asset_copier today has no concept of
"this skill lives in the kit, not the library."

The library was originally treated as the canonical source for all
distributable assets, but in practice the kit (`.claude/shared/`) is the
only source that BOTH generation modes have access to: subtree mode
literally pulls ClaudeKit, and library-copy mode runs from a Foundry
checkout that has the ClaudeKit submodule already on disk. The kit is
the natural single source of truth for cross-project skills.

The ai-team-library remains the right home for project-template assets:
commands the generated project's personas invoke (`/new-bean`,
`/handoff`, `/seed-tasks`), hook packs that get bundled into a
generated project's `settings.local.json`, persona templates copied
into `ai/outputs/<persona>/`, and plan skeletons. These are template
inputs that the library *owns* — they are not actively used inside
the Foundry repo itself.

### Decision

**ClaudeKit (`.claude/shared/`) owns cross-project skills. The
ai-team-library owns project-template assets. Both generation modes
resolve cross-project skills from the kit.**

Specifically:

1. **Ownership boundary — ClaudeKit (`.claude/shared/`).**
   Cross-project skills that any generated project might reasonably
   invoke at runtime live here. A skill belongs in the kit when it
   meets all four of:
   - It is **agnostic to the project's stack and personas** (it does
     not assume Python or React; it does not assume a Tech-QA persona
     is on the team).
   - It is **useful in more than one project** generated by Foundry.
   - It is **safe to ship to every project** by default (gating, if
     any, happens via the asset_copier governance maps, not by
     pruning the kit).
   - It is **owned by the kit's release cadence** — updates ship via
     the ClaudeKit submodule, not by editing a library file.

2. **Ownership boundary — `ai-team-library/claude/`.**
   Project-template assets live here:
   - `ai-team-library/claude/commands/` — slash commands a generated
     project's personas invoke (governed by `_GOVERNANCE_COMMANDS` in
     asset_copier).
   - `ai-team-library/claude/hooks/` — hook pack markdown files
     (selected by spec.hooks.packs).
   - `ai-team-library/personas/<persona>/templates/` — persona output
     templates copied to `ai/outputs/<persona>/`.
   - `ai-team-library/process/` — bean and context scaffolding.
   - `ai-team-library/claude/skills/` — **project-template-only
     skills** that the generated project's personas use, but which
     do not need to be available in the Foundry repo itself
     (e.g. `seed-tasks`, `new-bean`, `merge-bean`, `validate-repo`).

3. **Kit-distributed skill registry.** The asset_copier defines a
   module-level constant:

   ```python
   _KIT_DISTRIBUTED_SKILLS: tuple[str, ...] = (
       "_media_lib",
       "generate-image",
       "generate-screen",
   )
   ```

   This is the authoritative list. A skill name is in the registry iff
   the canonical copy of that skill lives at
   `<claude_kit_root>/skills/<name>/`. The registry started with two
   entries (`generate-image`, `generate-screen`); BEAN-281 added
   `_media_lib` (the shared helper package for env discovery, narration
   normalization + hashing, and cost summaries used by the media skills),
   and BEAN-282 / BEAN-283 will append `generate-audio` and any further
   media skills. Adding to the registry requires only editing this
   tuple — no schema change, no validator change.

   Criteria for adding a skill to `_KIT_DISTRIBUTED_SKILLS`:
   - The skill's source files live (or will live) under
     `.claude/shared/skills/<name>/`.
   - The skill meets the four ownership criteria in (1) above.
   - The skill does NOT also exist under
     `ai-team-library/claude/skills/<name>/`. (If it does, that copy
     is removed in the same change that adds the registry entry — no
     two homes.)

4. **Resolution rules for `asset_copier.copy_assets()`.** The
   function gains a new keyword parameter, `claude_kit_root: str |
   Path | None`, defaulting to `<foundry_root>/.claude/shared/` (the
   bundled submodule path resolved relative to the foundry_app package
   root, with a falsy/missing value treated as "kit not available").
   The resolution algorithm is:

   ```
   For each skill the asset_copier would copy:
       skill_name = src_entry.name (or src_entry.stem for flat-file skills)

       if subtree_mode:
           # The subtree already includes .claude/shared/skills/<name>/
           # under .claude/skills/, so skip everything to avoid double-copy.
           # (Existing behavior — unchanged.)
           SKIP all skills

       else:  # library-copy mode
           if skill_name in _KIT_DISTRIBUTED_SKILLS:
               source = <claude_kit_root>/skills/<skill_name>/
               destination = <out_root>/.claude/skills/<skill_name>/
               if source does not exist:
                   warn("kit-distributed skill <name> missing from kit at <path>")
                   continue
               apply existing governance gate (_GOVERNANCE_SKILLS)
               copy source/ → destination/ overlay-safe
           else:
               source = <library_root>/claude/skills/<skill_name>/
               # existing behavior — unchanged
               apply existing governance gate (_GOVERNANCE_SKILLS)
               copy source/ → destination/ overlay-safe
   ```

   Three rules follow from this:

   - **Subtree mode does not consult the registry.** The subtree
     bundles `.claude/shared/` wholesale; trying to also library-copy
     the kit-distributed skills would either be a no-op (identical
     content) or an overlay conflict. The asset_copier's existing
     "skip .claude/ in subtree mode" branch already handles this —
     no change needed for subtree mode.
   - **Library-copy mode iterates the union of skill names** present
     under `<library_root>/claude/skills/` plus the registry. A
     kit-distributed skill name that does not exist in the library
     directory is still copied (sourced from the kit). A skill name
     that exists only in the library and not in the registry copies
     from the library as today.
   - **Governance gates apply equally to both sources.** A skill
     listed in `_GOVERNANCE_SKILLS` is suppressed when no unlocking
     persona is on the team, regardless of whether its source is the
     kit or the library. The current `_GOVERNANCE_SKILLS` map does
     not name any kit-distributed skills, so today's behavior is
     "all kit-distributed skills copy unconditionally in library-copy
     mode" — but the gate is wired in case a future kit-distributed
     skill needs persona gating.

5. **Generator wiring.** `generator.py` resolves the default
   `claude_kit_root` from the foundry_app package root
   (`<foundry_root>/.claude/shared/`) and passes it through to
   `asset_copier.copy_assets()`. Callers (CLI, GUI, tests) may
   override the path. When the resolved path does not exist (e.g.
   the submodule is uninitialized), asset_copier emits a warning per
   missing kit-distributed skill but does not fail generation —
   library-copy-mode generation remains best-effort, matching the
   existing copier's tolerance for missing source directories.

6. **Cross-reference in the library.** A short note is added to the
   `ai-team-library/claude/skills/` directory's structure docs
   stating that cross-project skills are owned by ClaudeKit
   (`.claude/shared/skills/`) and listing the registry as the
   authoritative reference. This is informational — implementers
   should not look at the library directory and assume it is the
   complete skill set for a generated project.

### Consequences

**Positive:**

- **Single source of truth.** Each cross-project skill has exactly
  one home (`.claude/shared/skills/<name>/`). No mirror, no sync
  script, no drift.
- **Subtree mode and library-copy mode converge.** Both modes ship
  the same set of cross-project skills to a generated project.
- **Backfill is automatic.** Once asset_copier consults the registry,
  every library-copy-mode project starts shipping with
  `generate-image` and `generate-screen` — the existing gap closes
  without any per-project migration.
- **Future media skills (BEAN-282, BEAN-283) extend the registry by
  one tuple line each.** No new pipeline wiring per skill.
- **Reviews are local.** A change to a kit-distributed skill is
  reviewed in the ClaudeKit repo. A change to a project-template
  skill is reviewed in the ai-team-library tree. The ownership
  boundary maps to the review boundary.

**Negative:**

- **Skills must be designed kit-first.** A new skill author has to
  decide up front: "is this cross-project (kit) or project-template
  (library)?" The criteria in (1) make the decision concrete, but it
  is one extra question per skill.
- **Project-template-only skills stay in the library.** Skills like
  `seed-tasks`, `new-bean`, `validate-repo` remain library-resident
  because they are inert outside a generated project context. The
  registry's job is to keep that distinction visible — not to
  centralize everything.
- **Resolution adds a branch in asset_copier.** The skill-copy code
  path now consults the registry before resolving a source. This is
  one `if` and a constant lookup; the cost is trivial. Tests cover
  both branches (kit-distributed and library-resident) explicitly.
- **The kit submodule is now load-bearing for library-copy mode.**
  A generated project produced from a Foundry checkout with an
  uninitialized submodule will be missing kit-distributed skills.
  Mitigated by the warning emission and by the existing
  `git submodule update --init --recursive` instruction in
  `CLAUDE.md`.

### Alternatives Considered

1. **Mirror skills into ai-team-library via a sync script.**
   *Rejected.* This is the wrong shape. A sync script creates two
   locations to maintain — the kit and the library — with the
   library copy as a tracked-but-derived artifact. Drift becomes
   possible the first time someone edits the library copy (instead
   of the kit) by mistake; the script must then decide whether to
   overwrite the local edit or preserve it. Either rule produces a
   class of subtle bugs. Worse, the *semantics* are muddied: a reader
   browsing `ai-team-library/claude/skills/` cannot tell which
   entries are owned by the library and which are mirrored from the
   kit. A `## Source: kit` header in each mirrored file would help,
   but at that point the library is just shadowing the kit for no
   benefit. Single-source-of-truth resolution (this ADR's choice)
   eliminates the entire failure mode without adding tooling.

2. **Symlink kit skills into the library directory.**
   *Rejected.* Symlinks survive `git add`, but they break on Windows
   without developer-mode enabled, they break under `pip` and
   `hatchling` source distributions, and they break the existing
   asset_copier's `is_symlink()` warning path (which would either
   need to be relaxed for these specific symlinks — adding policy —
   or the symlinks would be silently skipped). Same drift risk as
   the sync-script alternative if the symlink is ever replaced with
   a regular file. The asset_copier already declines to copy
   symlinks; reversing that decision for one set of files invites
   subtle copy-semantics bugs.

3. **Move the kit-distributed skills into the library and remove
   them from the kit.**
   *Rejected.* Subtree-mode generated projects pull from the kit;
   removing the skills from the kit would regress every
   subtree-mode project. We would also lose the ability to use the
   skills inside the Foundry repo itself — the kit is the only
   `.claude/` Foundry's own Claude sessions can see.

4. **Add a `spec.generation.kit_distributed_skills` field to the
   composition YAML.**
   *Rejected.* User-facing configuration for what is fundamentally
   an internal resolution mechanism. The set of kit-distributed
   skills is determined by where the skill lives, not by a
   per-composition choice. A constant in `asset_copier.py` is the
   correct level of indirection.

5. **Detect kit-distributed skills automatically by scanning
   `<claude_kit_root>/skills/`.**
   *Rejected.* "Everything in the kit is a kit-distributed skill"
   is almost true today, but it makes the asset_copier's behavior
   depend on the contents of an external directory rather than on
   declared intent. A drive-by addition to the kit would silently
   start shipping to every library-copy-mode project. The explicit
   registry is the gate; auto-detection turns the kit into an
   unaudited deploy surface.

### Reversibility

Adding a skill to `_KIT_DISTRIBUTED_SKILLS` is a one-line edit and is
reversible until the skill ships in a Foundry release. After that,
removing a skill from the registry must be paired with either (a)
moving the skill back into the library or (b) accepting that
library-copy-mode projects regenerated against a newer Foundry will
lose the skill. This ADR does not lock the registry — it locks the
*pattern* of having a registry. The contents are expected to grow.
