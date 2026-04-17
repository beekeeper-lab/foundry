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

