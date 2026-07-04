# ADR-014: Extended-Persona Reference Syntax in `composition.yml`

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-271 |
| **Deciders** | Architect |

## Context

BEAN-271 splits `ai-team-library/personas/` into two on-disk tiers:

- `ai-team-library/personas/core/` — the 5 personas every team includes by default (team-lead, ba, architect, developer, tech-qa).
- `ai-team-library/personas/extended/` — the 19 specialist personas that are opt-in per composition.

Today every `personas[].id` in `composition.yml` is a bare directory name (`developer`, `security-engineer`) and `_scan_personas` in `foundry_app/services/library_indexer.py` walks one flat directory. After the reorg, `_scan_personas` must recurse into two subdirectories and `composition.yml` needs a stable convention for naming an extended persona. Two finalist syntaxes were on the table:

- **A. Tier-prefixed extended refs.** Core stays bare (`developer`); extended is qualified (`extended/security-engineer`). The loader's resolution rule is "lookup `id` in core when bare, in extended when prefixed." Names cannot collide because the namespace is explicit.
- **B. Bare names with implicit two-directory scan.** Every persona is referenced by its bare name (`security-engineer`). The loader scans both subdirectories, builds a single `id → path` map, and errors at index time if any `id` appears in both tiers.

The clean-break decision in the bean (Notes, 2026-04-28) means the syntax we pick is the only one that will ship — there is no shim to hide it. The contract this ADR locks is the one Developer (Task 02) implements and Tech-QA (Task 03) tests.

## Decision

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

## Consequences

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

## Alternatives Rejected

1. **Option B — bare names with implicit two-directory scan.** Rejected: the syntax hides which tier a persona belongs to at the call site, so a `composition.yml` reviewer must consult the library to learn whether `code-quality-reviewer` is core or extended. Collision detection at index-time addresses one sub-problem (duplicate names) but does not address the readability problem that motivated the tiering. Tier is information the reader needs; encoding it inline is cheaper than chasing it down.
2. **A `tier:` field on each persona entry** (`- id: security-engineer\n  tier: extended`). Rejected: doubles the line count and creates a second source of truth for the same fact (the directory layout already says where the persona lives). The `id` string already has spare bits — use them.
3. **A separate top-level `extended:` block in `composition.yml`** (mirror of `team.personas:` but for the extended tier). Rejected: forks the schema. Two iteration paths in the compiler, two validator branches, two wizard pages. Tier is a property of the persona reference, not a property of the team.
4. **Allow `core/<name>` as an alias for `<name>`.** Rejected: gives the user two ways to spell the same thing. One spelling per persona; bare for core, prefixed for extended.

## Migration Impact (`examples/*.yml`)

| File | Personas referenced | Edits required |
|------|---------------------|----------------|
| `examples/small-python-team.yml` | team-lead, developer, tech-qa, code-quality-reviewer | **1 edit.** `code-quality-reviewer` → `extended/code-quality-reviewer`. |
| `examples/foundry-dogfood.yml` | team-lead, architect, developer, tech-qa, code-quality-reviewer, technical-writer, ux-ui-designer | **3 edits.** `code-quality-reviewer`, `technical-writer`, `ux-ui-designer` each gain the `extended/` prefix. |
| `examples/full-stack-web.yml` | team-lead, ba, architect, developer, tech-qa, code-quality-reviewer, devops-release, security-engineer, technical-writer | **4 edits.** `code-quality-reviewer`, `devops-release`, `security-engineer`, `technical-writer` each gain the `extended/` prefix. |
| `examples/security-focused.yml` | team-lead, architect, developer, tech-qa, security-engineer, compliance-risk, devops-release | **3 edits.** `security-engineer`, `compliance-risk`, `devops-release` each gain the `extended/` prefix. |

Total: **11 line edits across 4 files**. Developer (Task 02) makes these edits as part of the file-reorg landing so the examples remain end-to-end runnable. Tech-QA (Task 03) verifies each example loads and compiles after the migration.

## Reversibility

Reversible at low cost while no third-party `composition.yml` files exist in the wild. Rollback path: revert the file reorg in `ai-team-library/personas/`, restore `_scan_personas` to its single-directory form, drop the `tier` field from `PersonaInfo`, and strip `extended/` prefixes from the four example compositions. After external consumers adopt the syntax, rollback requires a coordinated update across those repos — same cost-class as any naming-convention change.
