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
