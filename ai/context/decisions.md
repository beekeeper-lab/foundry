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
| **Bean** | BEAN-251, BEAN-253 |
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
       "generate-audio",
       "generate-image",
       "generate-screen",
   )
   ```

   This is the authoritative list. A skill name is in the registry iff
   the canonical copy of that skill lives at
   `<claude_kit_root>/skills/<name>/`. The registry started with two
   entries (`generate-image`, `generate-screen`); BEAN-281 added
   `_media_lib` (the shared helper package for env discovery, narration
   normalization + hashing, and cost summaries used by the media skills);
   BEAN-283 added `generate-audio` (ElevenLabs narration generator).
   Future media skills append here. Adding to the registry requires only
   editing this tuple — no schema change, no validator change.

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

---

## ADR-010: Multi-Provider Image Generation Routing

| Field | Value |
|-------|-------|
| **Date** | 2026-04-29 |
| **Status** | Accepted |
| **Bean** | BEAN-282 |
| **Deciders** | Architect |

### Context

The current `generate-image` skill (`.claude/shared/skills/generate-image/`)
is a single-shot CLI wrapper around Google's Gemini Nano Banana models.
It is sufficient for ad-hoc one-off assets — an icon for a screen, a
hero image for a marketing page — and the existing `generate-screen`
skill consumes it in exactly that mode.

It is **not** sufficient for any portfolio-style project. Both the
Stonewaters `Course_Material` reference (18 illustrated, narrated HTML
courses) and any future Foundry-generated portfolio project need to
generate hundreds of images per project from a reviewed plan markdown,
re-runnable, idempotent against on-disk state, with auditable
sidecars. The plan-driven workflow is documented in
`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md`
under "Image-generation skill"; the canonical implementation lives in
`Course_Material/Git_Fundamentals/scripts/generate_images.py` and
carries hard-won knowledge (rate-limit constant, 429 retry-with-
`retryDelay`, frontmatter parser, dispatch regex).

Two further forces shape this ADR:

1. **Visible style drift at the seam.** Gemini and OpenAI image
   models produce recognizably different illustrations even at
   matched prompts and quality. Mixing providers within a single
   project is the most visible quality bug — readers see the seam.
   The provider choice must therefore be locked **per project**,
   not per image.
2. **Independent provider quotas.** Gemini's free tier enforces a
   per-minute and per-24-hour cap; OpenAI's image generation can hit
   a dashboard "billing hard limit" mid-batch. When one provider is
   throttled, work routed to the other keeps moving — but only if
   the routing is documented in a per-project frontmatter line that
   the generator script honors deterministically.

The rewrite preserves single-shot mode (`--prompt "..."`) so
`generate-screen` and any ad-hoc consumer keeps working without
modification, and adds plan-driven mode (`--plan IMAGE-PLAN.md`) as
the primary surface. The single-shot/plan-driven duality is the
shape of the rewrite; multi-provider routing is the contract this
ADR locks down.

### Decision

Six concrete commitments. The Developer task (BEAN-282 task 02)
implements directly against this list.

**1. Plan-driven mode is the primary mode; single-shot mode is
preserved.** The rewritten skill exposes two CLI surfaces:

- `--plan path/to/IMAGE-PLAN.md` — primary mode. Reads frontmatter
  + image entries, skips on disk, supports `--filter <substring>`,
  `--force`, `--dry-run`. This is the mode every portfolio-style
  project uses.
- `--prompt "..."` — preserved single-shot mode for `generate-screen`
  consumers and ad-hoc one-off use. No frontmatter; provider/quality
  come from CLI flags or default.

The two modes share the provider-dispatch and rate-limiter code paths
but differ in input shape (plan vs. one prompt) and looping (many vs.
one). The duality is intentional: single-shot is exactly right for
small dispatches, plan-driven is exactly right for portfolios.

**2. The `Generator:` frontmatter line is the per-project provider
lock.** Tolerant containment dispatch:

- Default (line omitted entirely) → **Gemini**
  `gemini-3-pro-image-preview` (Nanobanana Pro). This preserves the
  current skill's behavior for every plan that does not opt into
  OpenAI.
- Any value containing the substring `openai` **OR** `gpt-image`
  (case-insensitive) → **OpenAI**.
- The OpenAI model name is extracted from the same string with the
  regex `gpt-image-[\d.]+`. If no match, fall back to the OpenAI
  default model (commitment 3).

The containment check is deliberately tolerant so all of
`openai-gpt-image-1.5`, `openai-gpt-image-2`, `gpt-image-1.5`,
`gpt-image-2`, and a leading marketing-name prefix (e.g.
`OpenAI gpt-image-2`) route correctly. Anything not matching
`openai`/`gpt-image` routes to Gemini — no auto-pick, no
heuristic, no implicit OpenAI selection.

**3. OpenAI default is `gpt-image-2` with automatic fallback to
`gpt-image-1.5` on the org-verification error.** When the resolved
OpenAI model is `gpt-image-2` and the API returns the
org-verification error (the OpenAI dashboard requires verifying the
org before `gpt-image-2` is callable), the script:

- Prints a one-line warning to stderr — single line, mentions both
  the verification requirement and the fallback that just happened
  (e.g. `WARNING: gpt-image-2 requires OpenAI org verification; falling back to gpt-image-1.5 for this run. Verify your org at platform.openai.com to use gpt-image-2.`).
- Retries the same request against `gpt-image-1.5`.
- Records `fallback_used: true` in the sidecar JSON.

On the OpenAI `billing hard limit` error the script **fails fast**
with a clear message and does not retry. The hard limit is exactly
that — quota is gone for the period; retrying just burns time and
prints the same error N times. The user's correct response is to
raise the dashboard cap or wait for the next billing period; the
script's job is to surface that decision quickly.

The `gpt-image-2` default tracks user direction: ship the newest
model on by default, fall back gracefully when verification has not
yet been completed, surface the verification requirement so the user
can fix it. Shipping with `gpt-image-1.5` as the default would hide
the upgrade path; the fallback handles unverified orgs cleanly.

**4. Unified `--quality low|medium|high` flag, default `high`.** A
single user-facing knob across both providers. Plan frontmatter
`Quality:` overrides the CLI default; CLI flag overrides nothing
about the plan (the plan is the contract).

Mapping table — verbatim:

| `--quality` | OpenAI gpt-image-2 / 1.5 | Gemini |
|---|---|---|
| `low` | `low` | `nanobanana2` |
| `medium` | `medium` | `nanobanana2` |
| `high` | `high` | `nanobanana-pro` (default) |

Two notes on the table:

- OpenAI's quality tokens (`low` / `medium` / `high`) pass through
  unchanged to the OpenAI Images API.
- Gemini exposes two model slots — the faster, cheaper `nanobanana2`
  and the higher-fidelity `nanobanana-pro`. `low` and `medium`
  collapse onto `nanobanana2` because Gemini's lower-quality models
  do not have the same tier granularity as OpenAI; only `high` walks
  up to `nanobanana-pro`.

The unified flag is the *user-facing* knob. The
provider-specific arg names (`quality=high` for OpenAI, model
selection for Gemini) live behind the dispatcher; no caller of the
skill needs to know the difference.

**5. Rate limiter — provider-specific.**

- **Gemini:** hard-paced at ~18 req/min via the in-script constant
  `MIN_INTERVAL_SECONDS = 60.0 / 18`. Gemini's per-minute ceiling is
  20; the 18 target leaves headroom. On 429, the script reads
  `retryDelay` from the Gemini error body and sleeps that long
  before retrying (default `MAX_RETRIES_ON_429 = 3` per request,
  matching the canonical implementation). The constant is not
  configurable — it is a property of the Gemini quota, not a tunable.
- **OpenAI:** the script respects the 429 `retry-after` header when
  present and retries within the same per-request retry budget. On
  the `billing hard limit` error, **fail fast** — do not retry, do
  not enter a retry loop, do not pace. Print the error and exit the
  current run with a clear message so the user knows why work
  stopped. The hard limit is hard; further attempts only delay the
  inevitable failure.

**6. Sidecar JSON next to each PNG — required fields.** Every
successful generation writes a JSON sidecar with the same basename as
the PNG (`<slug>.png` ↔ `<slug>.json`). The sidecar **must** include:

- `timestamp` (ISO 8601, UTC)
- `provider` (`gemini` or `openai`)
- `model` (resolved model name, e.g. `gemini-3-pro-image-preview` or
  `gpt-image-1.5`)
- `quality` (OpenAI only — `low` / `medium` / `high`)
- `size` (OpenAI only — e.g. `1536x1024`)
- `prompt` (the **assembled prompt as sent**, not the raw plan
  description — this is what reproduces the image)
- `output_file` (basename of the PNG)
- `generation_time_ms` (wall-clock time from request to response)
- `usage` (Gemini only — `prompt_tokens` / `candidates_tokens` /
  `total_tokens`; OpenAI's image API does not return token usage)
- `fallback_used` (boolean — true when `gpt-image-2` was requested
  and the script fell back to `gpt-image-1.5`; false otherwise)
- `negative_constraints` (the parsed `Avoid:` list, possibly empty)

The exact JSON shape (key order, optional helper fields, additional
provenance like `assembled_prompt` vs. `prompt`) lives in code
(`generate_image.py`); this ADR documents the *required* fields, not
the exact serialized structure. Adding fields is non-breaking;
removing or renaming any of the listed required fields requires a
follow-up ADR.

### Cost table location

The cost-per-image rates documented in
`AGENTIC-MEDIA-SKILLS.md` (Gemini per-token pricing, OpenAI per
quality+size combo) are baked into a constant table inside
`generate_image.py`. The end-of-run summary prints provider, image
count, and estimated cost computed from that table. **Provider
prices change. The cost table in `generate_image.py` is the
load-bearing version.** When rates change, update the script, not
this ADR and not the bean. Docs that reference cost rates link to
the script's table rather than restating the numbers.

This rule mirrors what `AGENTIC-MEDIA-SKILLS.md` already says about
its reference implementation. We restate it here so the rule is part
of the architecture record, not a footnote.

### One-provider-per-project rule

**Hard rule, not a recommendation: a project commits to one provider
for the life of the project.** The `Generator:` frontmatter line is
the lock. Switching providers mid-project means committing to
**regenerating every image** in that project — half-converted plans
are not supported and will produce visible style drift at the seam.

This is non-negotiable. Style drift between Gemini and OpenAI within
one project is the most visible quality bug in any portfolio-style
output. The skill enforces the rule by reading `Generator:` once per
plan and applying it uniformly; it does not support per-image
provider override (commitment 2 above forbids it). When a user
changes `Generator:` in a plan, the correct response is `--force`
and a re-run, not a partial regeneration.

### Failover use case

Gemini and OpenAI quotas are independent: Gemini has its own
per-minute and per-24-hour limits; OpenAI has its own dashboard-set
billing hard limit. When one provider is throttled or capped,
projects routed to the other keep working.

Documenting the routing in plan frontmatter (commitment 2) makes
this failover **deliberate strategy**, not ad-hoc. When planning a
portfolio of projects, intentionally split the routing so a
quota event on one provider does not block all work. "Today is a
Gemini day, advance Gemini-routed projects; OpenAI is blocked
until next billing period" is a coherent operating mode only when
each project's provider is recorded in writing. This ADR makes
that recording the contract.

### Consequences

**Positive:**

- **Multi-provider portfolios are tractable.** A user can run 18
  projects with some routed to Gemini, some to OpenAI, and pace
  them independently against each provider's quota.
- **Dispatch is one regex and one containment check.** No new
  configuration surface, no per-call provider negotiation.
  Frontmatter line in, provider out.
- **Cost is predictable per project.** End-of-run summary plus the
  one-provider-per-project rule means a project's spend is bounded
  by its image count times the in-script rate for the resolved
  provider/model/quality combo.
- **The single-shot path stays simple.** `generate-screen` and
  ad-hoc callers do not learn anything about plans, frontmatter, or
  failover; the new shape is strictly additive.
- **Sidecars are auditable.** Six months later a regeneration can
  read the sidecar's `prompt` and `model` and reproduce the exact
  request, even if the plan has been edited.

**Negative:**

- **Regex tolerance must stay honest.** As OpenAI ships new image
  models (`gpt-image-3`, `gpt-image-2.1`, etc.), the regex
  `gpt-image-[\d.]+` and the containment check must continue to
  match. Adding a regex test for each new model when it lands is the
  Tech-QA expectation; failing to do so means the new model name
  routes to the OpenAI default fallback silently.
- **Cost table needs maintenance.** Provider prices change; the
  in-script table must be updated when they do. The ADR
  intentionally does not embed numbers — but the maintenance burden
  is real and falls on whoever ships the rate change.
- **The fallback warning is one line.** A user running a 200-image
  batch will see one fallback line and may scroll past it. We
  accept this — louder warnings are noisier and the sidecar's
  `fallback_used` field is the durable record.
- **OpenAI org verification is a manual step.** Until the user
  verifies their OpenAI org, every `gpt-image-2` request falls back
  to `gpt-image-1.5`. The fallback ships value immediately; the
  one-line warning surfaces the unlock path.

### Alternatives Considered

1. **Per-image provider override (e.g. an `Image N:`-level
   `Generator:` field).** Rejected. Invites style drift within a
   single project — the exact failure mode the one-provider-per-
   project rule prevents. The visible-seam quality bug is the
   reason this ADR exists; per-image overrides would re-introduce
   it.
2. **Auto-pick provider from the `--quality` flag (e.g. `low`
   always means OpenAI low, `high` always means Gemini Pro).**
   Rejected. Removes the per-project lock and defeats the purpose
   of the `Generator:` frontmatter line. Quality is a user-facing
   knob *within* a chosen provider; it must not double as a
   provider selector. Coupling quality and provider also makes the
   failover use case incoherent — a user "running OpenAI today"
   could no longer ask for `high` without flipping the project's
   provider.
3. **Ship with OpenAI off until org verification is complete.**
   Rejected. `gpt-image-1.5` works today without verification;
   keeping OpenAI off entirely would deny that value. The
   `gpt-image-2` → `gpt-image-1.5` fallback handles the unverified
   case gracefully and prints the unlock path, so users get value
   immediately and can verify their org when convenient.
4. **Configure provider in CLI flags rather than plan frontmatter.**
   Rejected. CLI flags travel with the invocation, not the
   project. A plan re-run six months later with a different flag
   accidentally produces a different-style image — the seam bug
   again. Frontmatter travels with the project markdown and is
   reviewable in version control; the CLI default just supplies a
   value when the plan does not.
5. **Use a config file (`.image-generator-config.toml`) instead of
   plan frontmatter.** Rejected. Adds a second file to keep in
   sync with the plan, and the plan markdown is already the
   single source of truth for "what should exist." Embedding the
   provider in the plan keeps every project self-describing in one
   reviewable file.

### Reversibility

The dispatch contract is the load-bearing piece. Adding a new
recognized substring (e.g. a third provider's namespace) is
additive and backwards-compatible — existing plans keep routing
correctly. Changing the meaning of an existing substring (e.g.
having `gpt-image` route somewhere other than OpenAI) would
invalidate every project's frontmatter and is the only edit that
requires a follow-up ADR.

The required-fields list for sidecars is similarly load-bearing:
adding a field is non-breaking; removing or renaming a field
requires the follow-up. The exact JSON shape lives in code and
can churn freely without a new ADR, as long as the required
fields keep their current semantics.

## ADR-011: Audio Generation Skill Design (ElevenLabs Narration)

| Field | Value |
|-------|-------|
| **Date** | 2026-04-29 |
| **Status** | Accepted |
| **Bean** | BEAN-283 |
| **Deciders** | Architect |

### Context

The ClaudeKit `.claude/shared/skills/` directory has no audio
generation skill today. The Stonewaters portfolio (18 illustrated,
narrated HTML courses) and any future Foundry-generated portfolio
project needs to turn thousands of short narration paragraphs into
ElevenLabs MP3s — re-runnable, idempotent against on-disk state,
auditable via per-source manifests, and cheap enough to pace
against the ElevenLabs Pro cap (500K credits/month at $100).

The reference design lives in
`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md`
under "Audio-generation skill." The canonical implementation is
`Course_Material/Git_Fundamentals/scripts/generate_narration.py`
(274 lines), which carries production knowledge: the inline
`> 🎙️` blockquote scanner, the markdown-stripping regex order,
the per-source manifest shape, and the orphan-cleanup rule. ADR-009
established ClaudeKit as the canonical home for cross-project
skills; ADR-010 set the precedent for plan-driven, sidecar-driven
media skills routed via plan frontmatter. This ADR continues that
pattern for narration audio.

Three forces shape the contract:

1. **Two surfaces, one source of truth.** Narration text appears in
   two places in the portfolio: inline as `> 🎙️` blockquotes in
   source markdown (the rendered course), and consolidated in
   `NARRATION-PLAN.md` as a reviewer-friendly enumeration. The
   source markdown is what the build pipeline renders; the plan is
   a human review surface. Picking the plan as the source of truth
   would force a manual sync step every time the source markdown
   changes. The inline blocks must be the contract; the plan
   markdown is informational.
2. **Cross-system content-hash dedup.** A narration block that
   appears in three places (e.g. an intro paragraph reused in a
   crash course and a recap page) must render with one MP3 across
   all three. Build pipelines content-hash the *stripped* narration
   text and look up MP3s in a portfolio-wide index. For that lookup
   to hit, the audio generator must store the same stripped text in
   its manifest that the build pipeline hashes — bit-for-bit. BEAN-281
   established `_media_lib.text.normalize_narration_text` and
   `_media_lib.text.hash_text` as the portable contract, with a
   regex-order contract test preventing accidental drift. This skill
   delegates stripping to that module rather than re-implementing it.
3. **Cloned voice IDs are project preference, not kit assets.** The
   Stonewaters Purdue grad courses use a cloned voice ID
   (`s6d7r1gfIA8ArVv5Vocl`, Gregg Reed). ClaudeKit ships to every
   consumer; baking that ID into a kit-shipped voice map would leak
   one user's voice clone into every downstream project. Per user
   direction, cloned voice IDs live in user project plans/env, not
   in committed kit code.

The skill belongs in `.claude/shared/skills/generate-audio/` and is
distributed via the ClaudeKit asset list (`_KIT_DISTRIBUTED_SKILLS`,
BEAN-280) so subtree-mode and library-copy-mode generated projects
both receive it.

### Decision

Six concrete commitments. The Developer task (BEAN-283 task 02)
implements directly against this list.

**1. Inline `> 🎙️` blockquote = the contract; `NARRATION-PLAN.md`
is review surface only.** Source markdown is the source of truth.
The generator scans configured source files for blockquoted lines
beginning with the studio-microphone emoji (🎙️) and treats each
contiguous blockquoted run as one narration block. Default source
glob is `module-*.md` under the project's source directory; `--all`
widens to every `*.md` in that directory (crash courses, references,
auxiliary files).

`NARRATION-PLAN.md`, when present, is parsed for `Voice:` and
`Model:` frontmatter only — informational, not authoritative. CLI
flags override frontmatter. The plan is never the source of which
blocks exist; that's always the source markdown. The plan can carry
per-block character counts so a reviewer can answer "what does the
rest of this course cost" in one line, but the generator does not
read those counts to decide what to generate.

**2. Per-source-file manifest at `audio/<source-stem>/manifest.json`,
schema `{index, module, audio_file, text, size_bytes}`.** One
manifest per source file, written as a JSON array of records. Fields:

- `index` — 1-based block number; matches the `NN_` prefix on the
  MP3 filename (e.g. `01_module-00-intro.mp3` → `index: 1`).
- `module` — the source-file stem (e.g. `module-00-intro`).
- `audio_file` — the MP3 basename, relative to the manifest's
  directory.
- `text` — **the stripped narration text** that was sent to
  ElevenLabs. Not the raw blockquote. Not the source markdown. The
  exact characters that traveled to the API. This is what the build
  pipeline content-hashes for cross-page dedup; bit-for-bit fidelity
  with what was sent is the contract (commitment 5).
- `size_bytes` — the MP3 file size in bytes; used for sanity checks
  and the end-of-run summary.

The manifest is authoritative for "what should exist in this
directory." When the manifest is rewritten, MP3s whose blocks no
longer exist in source are removed (orphan cleanup).

**3. Pre-send stripping uses `_media_lib.text.normalize_narration_text`
from BEAN-281 — no re-implementation.** ElevenLabs literally
pronounces markdown markers ("star star" for `**bold**`), so every
block is normalized before the API call. The generator imports and
calls `normalize_narration_text` from
`.claude/shared/skills/_media_lib/text.py`. The regex application
order (blockquote → mic emoji → HTML tags → bold → italic → code →
link → whitespace collapse) is locked in by the BEAN-281 contract
test; both this skill and any downstream build pipeline that hashes
narration text MUST use that function verbatim. If the regex order
ever changes, both consumers move in lockstep — but the contract
test catches accidental drift either way.

The `text` field stored in the manifest (commitment 2) is exactly
the output of `normalize_narration_text` applied to the captured
blockquote — the same string that was sent to ElevenLabs.

**4. Voice routing — default `rachel`; voice map for stock names;
unknown values pass through as raw IDs; `--voice` overrides; no
cloned voice IDs in committed code.**

- **Default voice:** `rachel`, ElevenLabs voice ID
  `21m00Tcm4TlvDq8ikWAM`.
- **Voice map** (kit-shipped, generic only): `rachel`, `drew`,
  `paul`, `sarah`, `emily`, `charlie`, `george`, `matilda` — names
  that exist in any ElevenLabs account's default voice library and
  the corresponding stock voice IDs. The exact map lives in
  `generate_audio.py`; this ADR fixes the *policy* (stock names
  only), not the exact list, and additions to the stock-name map
  are non-breaking.
- **Passthrough rule:** any `--voice` value not present in the map
  is passed to ElevenLabs as a raw voice ID. This works for two
  cases: (a) a name the user has registered in their own voice
  library, and (b) a raw voice ID string. The script does not
  validate; ElevenLabs validates and returns a clear error if the
  ID is unknown.
- **`--voice <name-or-id>`** is the runtime override. `Voice:`
  frontmatter in `NARRATION-PLAN.md` is informational only.
- **No cloned voice IDs in committed code.** Cloned voices are
  per-project preferences (e.g. the Stonewaters Purdue cloned
  voice). They live in user project plans/env/CLAUDE.md, not in
  the kit's voice map. The generator never auto-discovers cloned
  voices; the user passes them via `--voice <id>` or records them
  in a per-project plan/env file outside the kit.

**5. ElevenLabs default model `eleven_multilingual_v2`; `--model`
overrides; plan frontmatter `Model:` is informational.** The
default tracks the canonical reference implementation and is the
production-tested choice across the Stonewaters portfolio. CLI
`--model` is the runtime override. `Model:` lines in
`NARRATION-PLAN.md` are read for human review but do not bind the
generator — CLI flags win, mirroring the voice-routing rule
(commitment 4) and ADR-010's plan-vs-flag convention.

**6. Skip-on-disk modes — five behaviors, deterministic.**

- **Missing MP3 → generate.** The default. Walk every block in
  every selected source file; if the target MP3 path doesn't
  exist, generate it. This is what makes incremental authoring
  cheap: add one new `> 🎙️` block, re-run, only that one block
  is generated.
- **`--regenerate-changed` → regenerate when stripped text differs
  from manifest.** Compares the current normalized text for each
  block against the manifest's stored `text` field. If they differ,
  regenerate. The comparison hits exactly the right cases because
  both sides are post-stripping (commitment 2 + commitment 3); a
  whitespace-only edit in source markdown collapses to the same
  normalized text and does not trigger regeneration.
- **`--force` → regenerate everything for the run.** Bypasses both
  the missing-file check and the changed-text check. Used when a
  voice or model change requires re-rendering the full set.
- **`--dry-run` → walk the plan, print what would happen, no API
  calls.** Always run dry-run first on a fresh plan or after a
  bulk edit; ElevenLabs spend is irreversible and a 200-block
  course at 600 chars/block is 120K credits (~$24 at the Pro rate
  amortization).
- **`--all` → include auxiliary source files** (crash courses,
  references — every `*.md`) instead of the default `module-*.md`
  glob. Default scope keeps casual re-runs from accidentally
  re-narrating reference material.

These five modes are mutually composable: `--dry-run --force` is a
preview of a full regen; `--dry-run --all --regenerate-changed` is
"what would change across the whole project including auxiliaries."

### Orphan cleanup

When the manifest is rewritten, the generator removes MP3s in
`audio/<source-stem>/` whose `audio_file` names no longer appear in
the new manifest's expected set. The manifest is the only durable
record of "what should exist in this directory" — orphan MP3s are
files whose source `> 🎙️` blocks have been deleted or renumbered,
and leaving them on disk would cause stale audio to be embedded in
rebuilt HTML.

Cleanup runs only on real generation runs, never under `--dry-run`
(dry-run makes no on-disk changes). It runs even when nothing was
generated this pass — re-running on a source file with one block
deleted will rewrite the manifest and remove the orphaned MP3 even
though no new audio was generated.

### Cost discipline

ElevenLabs `eleven_multilingual_v2` is **1 credit per character**.
Pro plan = 500K credits/month at $100. A 30-module intern course
at 8 blocks × 300 chars = ~72K credits ≈ 14% of monthly cap. A
33-module graduate course at 13 blocks × 600 chars = ~257K credits
≈ 50% of monthly cap.

Every run prints a character-count summary at the end:
total characters sent across the run = total credits spent.
Implementation: sum the character counts of every block actually
sent to ElevenLabs in the run (not skipped, not dry-run-previewed)
and print the total before exit. Plan-aware extension: when the
generator was invoked against a project containing
`NARRATION-PLAN.md`, the summary may also print remaining-credit
math from the plan's per-block counts ("this run: X credits;
remaining in plan: Y credits"). The plan-aware extension is
optional polish; the run-total is mandatory.

This is not optional. ElevenLabs spend is the second most
irreversible cost in the agentic-media stack (behind only OpenAI
image batches). The character-count summary is the user's pacing
signal; without it, a 500K-cap user can burn the month's budget on
a single bad invocation. Cost rates change; the credit-per-character
constant lives in `generate_audio.py` and is the load-bearing
version, mirroring ADR-010's cost-table-in-script rule.

### Content-hash dedup contract

The manifest's `text` field MUST be the stripped narration —
exactly the output of
`_media_lib.text.normalize_narration_text(raw_blockquote)` and
exactly what was sent to ElevenLabs. Any downstream build pipeline
that wants to dedupe MP3s across pages — Foundry-generated builds,
the Stonewaters `build_course.py`, or any future consumer —
content-hashes the manifest's `text` via
`_media_lib.text.hash_text` and uses the resulting sha256 as the
cache key.

**Bit-for-bit hash compatibility is required.** The contract is
portable across systems and shipped artifacts; substituting md5,
re-implementing the normalization, or ordering the regexes
differently will desync the cache and force every previously
generated MP3 to be re-narrated. The BEAN-281 contract test
(`tests/test_media_lib.py`) defends the regex order. Downstream
consumers MUST import `hash_text` from `_media_lib.text`, not
re-implement it.

The build pipeline use case is *not* implemented in this skill
(out of scope per the bean — that's a build-time concern; Foundry
itself does not ship a build pipeline). What this ADR locks down
is the *contract* the audio generator honors so that downstream
build pipelines can rely on it.

### Consequences

**Positive:**

- **Cost is predictable per character.** Every block has a known
  cost in credits = its character count. End-of-run summary makes
  spend visible; plan-tracked per-block counts make pacing tractable
  against the monthly cap.
- **Portable dedup.** Same `_media_lib.text.hash_text` across the
  audio generator and any build pipeline means a narration block
  reused in three pages costs one ElevenLabs call. Position-based
  matching is intentionally avoided — it would break the moment
  source files were reordered.
- **Failover when ElevenLabs hits its monthly cap.** When credits
  are exhausted, non-audio courses keep advancing. Plan-first +
  per-source-file manifests + orphan cleanup mean partial work is
  recoverable: when credits return, re-running the generator
  picks up exactly where it left off.
- **No leaked voice clones.** Kit-shipped code carries only generic
  voice names. User project plans carry the cloned IDs. The kit
  ships to every consumer; the user-specific voices stay
  user-specific.
- **Skip-on-disk + content-aware regen are deterministic.** The
  five-mode matrix (missing/regenerate-changed/force/dry-run/all)
  covers every authoring workflow without overlapping behaviors.

**Negative:**

- **Regex order is a cross-system contract.** Changing the regex
  application order in `_media_lib.text.normalize_narration_text`
  changes the hash for every previously stored manifest entry —
  invalidating the audio generator's `--regenerate-changed`
  comparisons and every downstream build pipeline's content-hash
  cache simultaneously. The BEAN-281 contract test guards the order;
  any deliberate change requires coordinated rollouts across the
  generator and every consuming build pipeline. We accept this
  cost — the alternative (per-consumer normalization) would
  guarantee divergent hashes and silent dedup misses.
- **Voice-passthrough trusts the user.** Unknown `--voice` values
  go to ElevenLabs unvalidated. A typo'd voice name produces an
  ElevenLabs error mid-run. We accept this — validating against
  the user's voice library would require an extra API call per run
  and would not cover the cloned-voice case (where the ID is
  meant to look unfamiliar to the kit).
- **Orphan cleanup is silent on dry-run.** A user inspecting a
  dry-run won't see "this MP3 would be removed." The summary lines
  list generation actions; orphan removal is implicit on real runs.
  We accept this for simplicity; the manifest diff is the durable
  record of what changed.
- **Plan frontmatter is informational, not authoritative.** A user
  who carefully writes `Voice:` in `NARRATION-PLAN.md` and then
  forgets `--voice` on the CLI will get the default voice. The
  CLI-wins rule mirrors the rest of the kit (ADR-010) but it does
  surprise occasional users. The first-line summary that the
  generator prints includes the resolved voice and model so the
  surprise is visible in real time.

### Alternatives Considered

1. **Plan markdown as source of truth instead of inline `> 🎙️`
   blocks.** Rejected. The source markdown stays in sync with the
   rendered HTML output by construction — every edit to the
   narration is visible in the same file the build pipeline reads.
   Treating `NARRATION-PLAN.md` as the source forces a manual sync
   step every time the source markdown changes, and that sync step
   is exactly the kind of human chore that goes stale. The plan as
   review surface (rather than source) keeps reviewers' workflows
   intact without making the plan a write-back blocker.
2. **Position-based MP3 reuse instead of content-hash dedup.**
   Rejected. Position-based matching ("block 3 of file X is the
   same MP3 as block 3 of file Y") breaks the moment any source
   file is reordered, split, or merged. Content-hash dedup is
   robust to reordering by construction: the same stripped text
   produces the same sha256 regardless of where it appears.
3. **Inline cloned voice IDs in the kit-shipped voice map.**
   Rejected. The voice map is shipped to every ClaudeKit consumer;
   baking a per-user cloned voice ID into it leaks that user's
   voice clone into every downstream project. Cloned voices are
   per-project preferences and live in user project
   plans/env/CLAUDE.md, never in the kit.
4. **No stripping before send to ElevenLabs.** Rejected.
   ElevenLabs literally pronounces markdown markers ("star star"
   for `**bold**`); this is the day-one bug every shipped TTS
   agent gets wrong. Stripping is mandatory. Re-implementing the
   stripping in this skill (rather than delegating to
   `_media_lib.text.normalize_narration_text`) is also rejected —
   it would diverge from the BEAN-281 contract test and risk
   desyncing the cross-system content hash.
5. **A separate per-block sidecar JSON (one file per MP3) instead
   of a per-source-file manifest array.** Rejected. The audio
   skill's atomic unit is a *source file* — one MP3 per block,
   collated by source. A per-source manifest matches the natural
   grouping (regenerate-changed compares old vs. new for the same
   source file; orphan cleanup operates on the source-file
   directory). Per-block sidecars would scatter that bookkeeping
   across hundreds of files and force the generator to re-walk all
   sidecars to compute the per-source view. The image skill's
   per-PNG sidecar (ADR-010) is the right shape for *that* skill
   because images don't share a natural source-file grouping; for
   audio, the source file is the unit.

### Reversibility

The manifest schema (`{index, module, audio_file, text,
size_bytes}`) is the load-bearing piece. **Adding a field is
non-breaking** — readers ignore unknown fields; old manifests are
forward-compatible. **Removing or renaming any of the five named
fields requires a follow-up ADR**, because both the audio
generator's `--regenerate-changed` lookup and every downstream
build pipeline's content-hash index depend on the exact field
names.

The voice-routing policy (default rachel; stock names only in the
kit map; passthrough for unknown values; no cloned voices) is
similarly load-bearing. Adding a new stock name is non-breaking;
removing rachel as default or admitting cloned voice IDs to the
committed map requires a follow-up ADR.

The `eleven_multilingual_v2` default model and the
1-credit-per-character cost rate live in code, not in this ADR —
they can change without a new ADR as long as the *policy* (default
present, CLI override available, cost printed every run) holds.

---

## ADR-012: Per-Expertise Persona Relevance for Compile-Time Filtering

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-259 |
| **Deciders** | Architect |

### Context

External audit (2026-04-17): every persona's compiled member prompt receives every selected expertise verbatim. The DevOps-Release agent's prompt contains `tsconfig.json` strict-mode detail; the UX/UI Designer's prompt contains `ruff` formatter defaults. This inflates context, dilutes role focus, and only gets worse as the expertise library grows. Today the join is unconditional: `compile_project` calls `_compile_persona_section` and `_compile_expertise_section` independently, the agent_writer joins all expertise highlights into every agent file (`expertise_sections` is shared across the per-persona loop), and the library has no metadata describing which expertise belongs with which persona.

Two candidate mechanisms were considered:

- **(A) Per-expertise persona relevance** — each expertise declares the personas it applies to.
- **(B) Per-persona expertise category filter** — each persona declares which expertise categories it wants (`Languages`, `Infrastructure & Platforms`, …).

Categories already exist on expertise (`## Category` heading, parsed by `library_indexer._parse_expertise_category`), so (B) would reuse existing metadata. But categories are coarse: `python` and `typescript` share `Languages`, yet DevOps-Release cares about Python's `pyproject.toml`/lockfile content while wanting nothing to do with TypeScript's `tsconfig.json`. Sub-categorising would re-create the per-pair granularity that (A) provides directly.

### Decision

**Mechanism A — per-expertise persona relevance.** Each expertise's primary markdown file declares the personas it applies to in an `## Applies To` section; the compiler and agent_writer filter expertise per persona at emit time. **Rationale (developer can quote):** *the author of an expertise file already knows its audience, and locality wins — adding a new expertise is one file change in one place, not a sweep across every persona.*

**Metadata schema.** A new `## Applies To` section on each expertise's primary markdown file (`conventions.md`, or the alphabetically-first `*.md` for multi-file packs like `accessibility-compliance/`). Same parser shape as `## Category` and `## Conflicts With` (ADR-005): a markdown heading followed by a bulleted list of persona IDs.

```markdown
## Applies To

- developer
- tech-qa
- architect
```

`ExpertiseInfo` gains `applies_to: list[str]` (default `[]`). The library indexer parses the section into that field. **The default when the section is absent or empty is "applies to every persona"** — this preserves today's behavior for any composition or library file without the new metadata. Unknown persona IDs in the list are dropped with a warning at index time (mirrors the `Persona '<id>' not found` warning shape already in `compiler.py`).

### Filter Contract

The filter operates on the **full expertise content** that gets joined to per-persona prompts. Specifically:

1. **`compiler._compile_persona_section`** — when assembling a persona's member prompt at `ai/generated/members/<persona>.md`, only expertise whose `applies_to` is empty *or* contains this persona ID contributes content. (Today the persona section does not in fact embed expertise content; this clause is a forward-compat hook for if it ever does — a no-op until then.)
2. **`agent_writer.write_agents`** — `expertise_sections` is no longer pre-computed once and shared. It is recomputed inside the per-persona loop, filtered by `applies_to`, before being passed to the Jinja template. This is the load-bearing change: today every agent file embeds every expertise's `Defaults` highlights; after BEAN-259, an agent file only embeds expertise whose `applies_to` matches.
3. **Lean CLAUDE.md (`_build_lean_claude_md`)** — **unfiltered**. The Tech Stack table continues to list every emitted expertise; that table is project-level scope, not persona-level scope, and removing entries would break the cross-reference contract (`ai/generated/expertise/<id>.md`).
4. **`ai/generated/expertise/<id>.md`** — **unfiltered**. The full expertise file is always written so any persona that needs to read it can. The filter only governs *which expertise gets inlined into a persona's prompt*, not which expertise gets emitted as a standalone file.

A new helper `compiler._expertise_applies_to(persona_id, expertise_info) -> bool` encapsulates the rule: returns `True` when `applies_to` is empty or `persona_id in applies_to`. Both call sites use it; tests target it directly.

### Test Cases

The implementation must satisfy at minimum these assertions:

1. **DevOps-Release / React+TS composition**: the generated `.claude/agents/devops-release.md` and `ai/generated/members/devops-release.md` contain no `tsconfig` substring (case-insensitive) and no React-specific content.
2. **UX/UI Designer / same composition**: the corresponding agent and member files contain no `ruff` substring and no Python-specific content.
3. **Developer / same composition**: the corresponding agent and member files contain both `tsconfig` and `ruff` (Developer is in `applies_to` for both).
4. **Backward-compat — empty metadata**: an expertise file with no `## Applies To` section produces the same agent/member output for every persona as before BEAN-259 (byte-equal on a regression fixture, modulo any unrelated changes).
5. **Backward-compat — empty list**: an expertise file with `## Applies To` present but no bullets is treated identically to "section absent" (apply to all).
6. **Unknown persona ID**: `applies_to: [bogus-persona]` raises an indexer warning and is treated as if the ID were not present (i.e., for a real persona, that persona is *not* matched by the bogus entry).
7. **Lean CLAUDE.md unaffected**: the Tech Stack table in `CLAUDE.md` lists every emitted expertise regardless of `applies_to`.
8. **Standalone expertise files unaffected**: `ai/generated/expertise/<id>.md` is written for every emitted expertise regardless of `applies_to`.

### Consequences

**Positive:**
- Per-persona prompts shrink in proportion to how narrow the persona is. DevOps-Release and UX/UI Designer benefit most; Developer is unaffected by design.
- The metadata lives next to the content it scopes — a library author adding a new expertise edits one file.
- Backward-compatible by construction: existing library files (none of which have `## Applies To` today) continue to produce identical output until the metadata is added.
- The filter helper is a pure function over `(persona_id, ExpertiseInfo)`, trivially unit-testable in isolation.

**Negative:**
- Curating `applies_to` lists is ongoing library-author work. Mitigated by the empty-default rule (forgetting to add the section is a no-op, not a regression).
- A persona–expertise pair can drift if the persona's role changes but the expertise's `applies_to` is not revisited. Acceptable; this is the same drift risk as `## Conflicts With` (ADR-005).

### Reversibility

Fully reversible. Rollback path: delete the `## Applies To` parsing in `library_indexer.py`, drop the `ExpertiseInfo.applies_to` field, and remove the `_expertise_applies_to` calls in `agent_writer.py` and `compiler.py`. Library `## Applies To` sections become inert text (the indexer ignores unknown sections today). No on-disk schema migration is needed: composition specs and generated projects are unaffected.

### Alternatives Rejected

1. **Mechanism B — per-persona expertise-category filter:** Rejected. Categories are coarse (`Languages` covers both Python and TypeScript), so DevOps-Release would either get both or neither — neither matches the audit's complaint. Refining the taxonomy with sub-categories adds a second metadata surface to maintain *and* still places the declaration far from the content being filtered.
2. **Front-matter YAML on persona/expertise files:** Rejected. The library has never used YAML front-matter; existing metadata (`## Category`, `## Conflicts With`) lives in markdown sections parsed by the indexer. Adding a third precedent for the same kind of metadata would fragment the parser.
3. **Separate `_index.yml` in `ai-team-library/expertise/`:** Rejected. Centralized metadata invites drift between the index and the file it describes; the ADR-005 precedent (declarations live with the thing being declared) applies here too.
4. **Runtime filtering at agent-load time:** Out of scope per the bean (compile-time filter only). Runtime tailoring is BEAN-240's territory.

---

## ADR-013: Persona Produces/Consumes Contracts — Format, Registry, Loader, and Compiler Emission

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-273 |
| **Deciders** | Architect |

### Context

BEAN-273 introduces machine-readable produces/consumes contracts to every core persona, plus a registry of artifact types they reference. This ADR locks four structural choices the rest of BEAN-273 (Developer task 03) and downstream beans (BEAN-274 contract-graph validator, BEAN-276 per-edge handoff schemas) will depend on. BA's task 01 deliverable (`ai/outputs/ba/BEAN-273-artifact-types.md`) supplies the registry content and the per-persona contract payloads; this ADR commits to the on-disk shape, the loader integration, and the compiler emission shape so Developer can implement without further design questions.

The bean Notes recommended YAML frontmatter on `persona.md`. ADR-012 rejected YAML frontmatter for a similar metadata case ("The library has never used YAML front-matter; … adding a third precedent for the same kind of metadata would fragment the parser"). That precedent forces a re-evaluation here.

### Decision

**1. Contract location on personas — sibling `contracts.yml` next to `persona.md`.** Each core persona directory grows one new file, `ai-team-library/personas/<id>/contracts.yml`, holding `produces:` and `consumes:` arrays of artifact-type names. **Rationale:** YAML frontmatter would create a third metadata format on `persona.md` (alongside the existing `## Category` markdown section and the per-expertise `## Applies To` markdown section in ADR-012), fragmenting the parser ADR-012 explicitly preserved. A sibling YAML file keeps `persona.md` pure markdown for human readers, parses with the existing PyYAML dependency in three lines, and follows the ADR-005 / ADR-012 "metadata lives next to its thing" principle. The trade-off — one extra file per persona — is small and consistent with the existing per-persona directory layout (`persona.md`, `outputs.md`, `prompts.md`, `templates/`).

**2. Registry location — `ai-team-library/contracts/artifact-types.yml`.** Confirmed as the canonical path; a new top-level `contracts/` directory is added to the library. **Rationale:** `personas/` describes *who*, `templates/` (per-persona) describes *what to write*, and `workflows/` describes *how the team flows*. Artifact types are a cross-cutting glossary owned by no single persona — they belong in their own top-level slot. Nesting under `personas/` would imply persona ownership; nesting under `templates/` would imply per-template scope; nesting under `workflows/` would imply per-workflow scope. None of those frames fit. A top-level `contracts/` directory makes future siblings (e.g. `handoff-schemas.yml` for BEAN-276) a natural addition without re-rooting paths.

**3. Loader integration — extend `foundry_app/services/library_indexer.py`.** A new `contracts_loader.py` module is rejected. **Rationale:** the indexer already walks every persona directory once (`_scan_personas`) and every category/applies-to file once. Adding the contracts read inline costs one additional `path.read_text` call per persona inside the existing loop and one new top-level `_load_artifact_type_registry(library_root / "contracts" / "artifact-types.yml")` call inside `build_library_index`. The blast radius is two new helpers and two new fields on existing models (`PersonaInfo.produces`, `PersonaInfo.consumes`, plus a new `LibraryIndex.artifact_types` list of `ArtifactTypeInfo`). A separate `contracts_loader.py` would duplicate the directory walk, duplicate caller wiring (`generator.py` would need to call two loaders and reconcile two return shapes), and introduce a parallel error-reporting code path. Rejected.

**4. Compiler emission shape — flat `contracts:` block at the bottom of generated `ai/team/composition.yml`.** The shape is frozen as:

```yaml
contracts:
  personas:
    - id: ba
      produces: [user-story, acceptance-criteria, scope-definition, risk-register, handoff-packet]
      consumes: [bean-spec, scope-definition]
    - id: developer
      produces: [code-change, dev-decision, handoff-packet]
      consumes: [task-spec, user-story, acceptance-criteria, design-spec, adr]
    # … one entry per persona on the team
  artifact-types:
    - name: user-story
      format: markdown
      template-path: personas/ba/templates/user-story.md
    - name: code-change
      format: markdown
      template-path: personas/developer/templates/pr-description.md
    # … one entry per artifact type referenced by any persona on the team
```

**Rationale:** this is a flat, addressable, read-once view of the team's contract graph. `personas:` is a list (ordered) so consumers can iterate. `artifact-types:` is a flat reference list — only types actually referenced by a persona on the team appear, so the block stays small (~10-15 entries) and self-contained for BEAN-274's validator. Each artifact-type entry carries `format` and `template-path` (the two registry fields the validator needs). `description` and `required-fields` from the source registry are intentionally omitted at emit time — they live in the library's `artifact-types.yml` for authoring and can be reloaded by tooling that needs them, but they would bloat every generated `composition.yml` without value to the validator.

The block is appended **after** the existing `orchestration:` policy block emitted by `scaffold.py` (`_ORCHESTRATION_YAML_BLOCK`), and emission is gated on `spec.team.personas` being non-empty — same condition the orchestration block already implicitly relies on.

### Ambiguity Resolutions (from BA's task 01 writeup)

- **`acceptance-criteria` dual producer (BA + Team-Lead).** Both personas keep the type in their `produces:`. The contract-graph view treats the registry-side declaration as legal; the per-bean *active-producer* selection rule is "BA wins when on the wave, Team-Lead is fallback." The loader and compiler do **not** special-case this type — they emit both producers in `contracts.personas[].produces`. BEAN-274's validator codifies the active-producer pick; BEAN-275 codifies the prose policy. This ADR records the structural rule only.
- **`dev-decision` has no declared consumer.** The loader treats dangling produced types as **legal but warned**: `library_indexer` logs `"Artifact type '<name>' produced by '<persona>' has no declared consumer"` at INFO level (not WARNING — it is a real signal but not an error, and Team-Lead reviews `dev-decision` content via `merge-summary` synthesis at bean-close). Handoffs for dangling types are not required.
- **`risk-register` shared by BA + Architect.** Keep one registry entry with two producers, mirroring the `acceptance-criteria` pattern. Defer split into `requirements-risks` / `design-risks` to a later bean if the validator can't disambiguate. Confirmed.
- **`handoff-packet` produced by every persona.** Keep flat repetition — every persona's `produces:` lists `handoff-packet`. Confirmed. A "produced-by-everyone" tag would add a second emission code path for one type; the cost (five extra string entries across five personas) is below the threshold where a special case earns its keep.

### Consequences

**Positive:**
- The persona markdown stays clean and human-readable; no new parser is needed for the contract data (PyYAML already in deps).
- Loader extension is two helpers and two fields — small blast radius, single point of failure, single point of test.
- The frozen `composition.yml` shape gives BEAN-274 a stable target. Validator authors can write tests against canned `composition.yml` fixtures without coordinating with this bean.
- The flat reference list of artifact-types in the emitted block keeps generated projects self-describing without re-reading the library at runtime.
- Adding a new persona to a team is one new `contracts.yml` plus one entry in `composition.yml.contracts.personas` — the artifact-types list rebuilds automatically at compile time.

**Negative:**
- One extra file per persona (`contracts.yml`) — visible cost in the persona directory listing. Mitigated by the file being short (≈10 lines per persona) and self-explanatory.
- The dual-producer `acceptance-criteria` model means BEAN-274 must implement an "active producer" rule rather than a simpler "exactly one producer" check. Acceptable; the rule is short and well-scoped.
- The `contracts.yml` files are an additional surface kit-distribution must keep in sync if the library is mirrored across projects. Existing kit-sync paths already copy whole persona directories, so this is mechanical.

### Alternatives Rejected

1. **YAML frontmatter at the top of `persona.md`** (the bean Notes' recommendation). Rejected for the same reason ADR-012 rejected frontmatter on expertise files: the library's existing convention is markdown-section metadata (`## Category`, `## Conflicts With`, `## Applies To`), and adding a third metadata format fragments the parser. The bean Notes invited a concrete reason; ADR-012 supplies one.
2. **A new `## Contracts` markdown section inside `persona.md`.** Rejected because YAML inside a fenced markdown block requires a custom parser (find the heading, find the fence, slice the body, hand off to PyYAML). The sibling-file approach is parseable in three lines (`yaml.safe_load(path.read_text())`).
3. **A new `foundry_app/services/contracts_loader.py` module.** Rejected — see Decision 3. The indexer already walks the persona tree once; piggy-backing is cheaper than a parallel walker.
4. **Single registry-side definition with `produces-by:` / `consumes-by:` pointers** (instead of duplicating onto each persona). Rejected — the locality argument from ADR-012 holds: a new persona's contract belongs in that persona's directory, not in a centralized registry. Maintainers adding a persona edit the persona's own files.
5. **Embedding the full registry (`description`, `required-fields`, etc.) in every emitted `composition.yml`.** Rejected — bloats the generated file with duplicated data the validator does not consume. The library's `artifact-types.yml` is the source of truth; BEAN-274's validator can reload it from `library_root` (or from the library copy bundled into the generated project) when it needs the deeper schema.

### Reversibility

Fully reversible. Rollback path: delete `ai-team-library/contracts/`, delete each persona's `contracts.yml`, drop the `produces`/`consumes` fields and `ArtifactTypeInfo` model, drop the loader helpers, and remove the `contracts:` block emission in `scaffold.py`. Generated projects with the old shape continue to work — the validator (BEAN-274) is the first consumer of this contract data, and it will not exist until after this bean lands.

## ADR-014: Extended-Persona Reference Syntax in `composition.yml`

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-271 |
| **Deciders** | Architect |

### Context

BEAN-271 splits `ai-team-library/personas/` into two on-disk tiers:

- `ai-team-library/personas/core/` — the 5 personas every team includes by default (team-lead, ba, architect, developer, tech-qa).
- `ai-team-library/personas/extended/` — the 19 specialist personas that are opt-in per composition.

Today every `personas[].id` in `composition.yml` is a bare directory name (`developer`, `security-engineer`) and `_scan_personas` in `foundry_app/services/library_indexer.py` walks one flat directory. After the reorg, `_scan_personas` must recurse into two subdirectories and `composition.yml` needs a stable convention for naming an extended persona. Two finalist syntaxes were on the table:

- **A. Tier-prefixed extended refs.** Core stays bare (`developer`); extended is qualified (`extended/security-engineer`). The loader's resolution rule is "lookup `id` in core when bare, in extended when prefixed." Names cannot collide because the namespace is explicit.
- **B. Bare names with implicit two-directory scan.** Every persona is referenced by its bare name (`security-engineer`). The loader scans both subdirectories, builds a single `id → path` map, and errors at index time if any `id` appears in both tiers.

The clean-break decision in the bean (Notes, 2026-04-28) means the syntax we pick is the only one that will ship — there is no shim to hide it. The contract this ADR locks is the one Developer (Task 02) implements and Tech-QA (Task 03) tests.

### Decision

**Extended personas are referenced with a `extended/` tier prefix; core personas are referenced bare.**

```yaml
team:
  personas:
    - id: developer                       # core — bare
    - id: tech-qa                         # core — bare
    - id: extended/security-engineer      # extended — tier-prefixed
    - id: extended/code-quality-reviewer  # extended — tier-prefixed
```

This is **Option A**. Option B is rejected (see Alternatives).

#### Loader behavior (`_scan_personas`)

`_scan_personas(personas_dir, …)` is updated as follows:

1. **Discovery.** Iterate `personas_dir / "core"` and `personas_dir / "extended"` in that fixed order (sorted within each subdir). Skip non-directories. Each subdir is required to exist; if either is missing, log a warning and treat that tier as empty (matches the existing missing-`personas/` behavior).
2. **Canonical id.** Each `PersonaInfo.id` carries the **reference form** the user writes in `composition.yml`:
   - core personas: bare directory name (e.g. `developer`)
   - extended personas: `extended/<dirname>` (e.g. `extended/security-engineer`)
   `PersonaInfo.tier` is set to `"core"` or `"extended"` per the source subdir, matching the field BEAN-271 adds to the model.
3. **Resolution at composition load time.** The compiler (and any other consumer) looks up a `composition.yml` `id` against `LibraryIndex.personas` by exact match on `PersonaInfo.id`. No fuzzy match, no fallback across tiers — the prefix is part of the identity for extended.
4. **Error message — unknown id.** When a `composition.yml` references an `id` not in the index, the loader/compiler emits exactly:

   ```
   Unknown persona '<id>' in composition.yml. Core personas (bare names): <core-list>. Extended personas (tier-prefixed): <extended-list>.
   ```

   `<core-list>` and `<extended-list>` are alphabetized, comma-separated id lists pulled from the live index, so the message stays accurate as personas are added.
5. **Error message — wrong-tier reference.** When a user writes `security-engineer` (bare) but the persona lives in `extended/`, or writes `extended/developer` when the persona lives in `core/`, the message is:

   ```
   Persona '<input>' not found at expected tier. Did you mean '<correct-form>'? Extended personas must be referenced as 'extended/<name>'; core personas use the bare name.
   ```

   The detector for this case is "the trailing path segment exists in the *other* tier and the user's prefix disagrees." This catches the most common migration mistake (an old composition that names an extended persona without the prefix) and points the user at the exact fix without making them re-read the docs.
6. **Reserved namespace.** The `extended/` token is the only tier prefix the loader recognizes. Any other slash-bearing id (`vendor/foo`, `core/developer`) is treated as unknown and falls through to the message in #4. `core/<name>` is *not* an alias for `<name>` — core is bare, period. This keeps the grammar minimal: one prefix, one tier.

The Library Manager's "Add Persona" UI (out of scope for this bean, in scope for a follow-up) defaults new personas into `extended/` since the core five are a closed set. This default reinforces, rather than complicates, the syntax decision: a UI-created persona is automatically referenced as `extended/<id>` everywhere.

### Consequences

**Positive:**
- A `composition.yml` reader can tell at a glance which personas are core team and which are opt-in specialists. The tier is part of the wire format, not metadata recovered from a separate file.
- Adding a 6th persona to `extended/` with the same trailing name as a future core persona is a non-event — there is no global namespace to collide in.
- The error messages are deterministic and include the exact remediation token (`extended/<name>`), so the migration mistake is self-correcting.
- The parser is trivial: a single `str.startswith("extended/")` test plus a string slice. No regex, no resolution table.
- Aligns with how the existing kit references nested resources (`shared/skills/<name>`, `local/<name>`) — slash-separated paths already mean "namespace" elsewhere in the project.

**Negative:**
- Existing `composition.yml` files that name an extended persona must be edited (see Migration). The clean-break stance in the bean accepts this cost.
- The extended ids are longer (`extended/security-engineer` vs. `security-engineer`), adding ~9 characters per line in the YAML. Acceptable — `composition.yml` is authored once per project and read by humans rarely.
- Two namespaces means two listings in error output. The error message handles this by labeling each list explicitly.

### Alternatives Rejected

1. **Option B — bare names with implicit two-directory scan.** Rejected: the syntax hides which tier a persona belongs to at the call site, so a `composition.yml` reviewer must consult the library to learn whether `code-quality-reviewer` is core or extended. Collision detection at index-time addresses one sub-problem (duplicate names) but does not address the readability problem that motivated the tiering. Tier is information the reader needs; encoding it inline is cheaper than chasing it down.
2. **A `tier:` field on each persona entry** (`- id: security-engineer\n  tier: extended`). Rejected: doubles the line count and creates a second source of truth for the same fact (the directory layout already says where the persona lives). The `id` string already has spare bits — use them.
3. **A separate top-level `extended:` block in `composition.yml`** (mirror of `team.personas:` but for the extended tier). Rejected: forks the schema. Two iteration paths in the compiler, two validator branches, two wizard pages. Tier is a property of the persona reference, not a property of the team.
4. **Allow `core/<name>` as an alias for `<name>`.** Rejected: gives the user two ways to spell the same thing. One spelling per persona; bare for core, prefixed for extended.

### Migration Impact (`examples/*.yml`)

| File | Personas referenced | Edits required |
|------|---------------------|----------------|
| `examples/small-python-team.yml` | team-lead, developer, tech-qa, code-quality-reviewer | **1 edit.** `code-quality-reviewer` → `extended/code-quality-reviewer`. |
| `examples/foundry-dogfood.yml` | team-lead, architect, developer, tech-qa, code-quality-reviewer, technical-writer, ux-ui-designer | **3 edits.** `code-quality-reviewer`, `technical-writer`, `ux-ui-designer` each gain the `extended/` prefix. |
| `examples/full-stack-web.yml` | team-lead, ba, architect, developer, tech-qa, code-quality-reviewer, devops-release, security-engineer, technical-writer | **4 edits.** `code-quality-reviewer`, `devops-release`, `security-engineer`, `technical-writer` each gain the `extended/` prefix. |
| `examples/security-focused.yml` | team-lead, architect, developer, tech-qa, security-engineer, compliance-risk, devops-release | **3 edits.** `security-engineer`, `compliance-risk`, `devops-release` each gain the `extended/` prefix. |

Total: **11 line edits across 4 files**. Developer (Task 02) makes these edits as part of the file-reorg landing so the examples remain end-to-end runnable. Tech-QA (Task 03) verifies each example loads and compiles after the migration.

### Reversibility

Reversible at low cost while no third-party `composition.yml` files exist in the wild. Rollback path: revert the file reorg in `ai-team-library/personas/`, restore `_scan_personas` to its single-directory form, drop the `tier` field from `PersonaInfo`, and strip `extended/` prefixes from the four example compositions. After external consumers adopt the syntax, rollback requires a coordinated update across those repos — same cost-class as any naming-convention change.
