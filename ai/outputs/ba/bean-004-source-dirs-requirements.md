# BEAN-004: Source Directory Configuration — Requirements

**Author:** BA | **Date:** 2026-02-07 | **Bean:** BEAN-004

## Problem Summary

The safety service (`safety.py:56-59`) hardcodes three `Edit()` rules:
- `Edit(src/**)`
- `Edit(tests/**)`
- `Edit(ai/**)`

Projects that use different source directories (e.g. `foundry_app/`, `lib/`, `app/`) must manually edit `settings.local.json` after generation. This was experienced firsthand during Foundry's own dogfooding setup.

## User Stories

### US-1: Custom source directory

**As a** project creator using a non-standard source directory,
**I want to** specify my source directories in the composition YAML,
**So that** the generated `settings.local.json` has the correct `Edit()` rules.

**Given** a composition YAML with `filesystem.editable_dirs: ["foundry_app/**"]`
**When** I run `foundry-cli generate`
**Then** the generated `settings.local.json` contains `Edit(foundry_app/**)` instead of `Edit(src/**)`

### US-2: Multiple source directories

**As a** project creator with multiple editable directories,
**I want to** list several directories,
**So that** all of them are included as `Edit()` allow rules.

**Given** a composition YAML with `filesystem.editable_dirs: ["src/**", "lib/**", "scripts/**"]`
**When** I run `foundry-cli generate`
**Then** the generated `settings.local.json` contains `Edit(src/**)`, `Edit(lib/**)`, and `Edit(scripts/**)`

### US-3: Default behavior when field is omitted

**As a** project creator using the standard `src/` layout,
**I want to** not have to configure anything,
**So that** the default behavior is unchanged.

**Given** a composition YAML with no `editable_dirs` field
**When** I run `foundry-cli generate`
**Then** the generated `settings.local.json` contains the current defaults: `Edit(src/**)`, `Edit(tests/**)`, `Edit(ai/**)`

### US-4: Wizard UI configuration

**As a** GUI user on the Safety page of the wizard,
**I want to** enter my project's source directories,
**So that** I don't have to edit YAML manually.

**Given** I am on the Safety page of the wizard
**When** I enter `foundry_app/**` in the editable directories field
**Then** the generated composition spec contains `filesystem.editable_dirs: ["foundry_app/**"]`

## Scope Boundary

### In Scope

- New `editable_dirs` field on `FileSystemPolicy` model
- Safety service reads `editable_dirs` to generate `Edit()` rules
- Default value `["src/**", "tests/**", "ai/**"]` when field is omitted (backward compatible)
- Wizard Safety page gains a text input for editable directories (comma-separated or one-per-line)
- YAML round-trip: `editable_dirs` persists through load/save
- Composition examples updated

### Out of Scope

- Auto-detection of source directories by scanning filesystem
- Validation that directories actually exist (generation happens before project exists)
- Per-persona directory restrictions (all members share the same Edit rules)
- Changes to `deny_patterns` behavior (remains unchanged)
- Changes to `Read(**)` rule (always included, not configurable here)

## Edge Cases

| ID | Case | Expected Behavior |
|----|------|-------------------|
| EC-1 | `editable_dirs` is an empty list `[]` | No `Edit()` rules generated (user explicitly wants no edit permissions). Emit a warning. |
| EC-2 | `editable_dirs` omitted from YAML | Falls back to default: `["src/**", "tests/**", "ai/**"]` |
| EC-3 | Single directory `["app/**"]` | One `Edit(app/**)` rule generated |
| EC-4 | Duplicate entries `["src/**", "src/**"]` | Deduplicate — only one `Edit(src/**)` rule |
| EC-5 | Entries with leading/trailing whitespace `[" src/** "]` | Strip whitespace before generating rules |
| EC-6 | Entry without glob pattern `["src"]` | Accept as-is — `Edit(src)` is a valid (if unusual) Claude Code pattern |
| EC-7 | Old composition YAML (no `editable_dirs` field) | Pydantic default applies — backward compatible |
| EC-8 | Wizard user clears the field entirely | Treat as empty list, show warning that no edit permissions will be granted |

## Risks

| ID | Risk | Mitigation |
|----|------|------------|
| R-1 | Users forget to update `editable_dirs` and get `src/**` by default, but their project uses a different layout | Document the field in wizard tooltip/help text; consider a note in generated safety-policy.md |
| R-2 | Breaking change if default shifts from `["src/**", "tests/**", "ai/**"]` | Keep same defaults — this is additive only |

## CLI Interface

No CLI changes needed. The `foundry-cli generate` command already reads the composition YAML, which will now contain `editable_dirs` when configured. The safety service will pick it up automatically.
