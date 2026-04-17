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

## ADR-004: Declarative `Conflicts With` in Hook Pack Metadata

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
