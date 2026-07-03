# SPEC-016: Wire SafetyConfig to generated permissions or remove it

- **Priority:** P1
- **Effort:** M
- **Area:** pipeline
- **Depends on:** none (complements SPEC-004, SPEC-014)
- **Status:** Proposed

## Problem

The composition model has a rich, typed `SafetyConfig` (git policy, filesystem policy, secrets, destructive-command policy, with posture factory methods) that **no service ever reads** — it is dead weight in the schema. Meanwhile the file that actually carries permissions in a generated project, `.claude/settings.local.json`, is a **static verbatim copy** of the library's copy, identical for every project regardless of posture. A `regulated` composition gets exactly the same permission surface as a `baseline` one. The result: Foundry models safety it never applies, and applies safety it never models.

## Evidence

- `foundry_app/core/models.py:334` — `class SafetyConfig`; factories `baseline_safety()` at `:366`, `hardened_safety()` at `:371`. (Note: there is **no** `regulated_safety()` factory even though `Posture.REGULATED` exists at `models.py:31` — the model is incomplete as well as unused.)
- `foundry_app/core/models.py:445` — `CompositionSpec.safety` field, populated from YAML but never consumed: `grep -rn 'spec.safety\|SafetyConfig' foundry_app/services/` returns nothing.
- `foundry_app/services/asset_copier.py:17-21` — `_GLOBAL_ASSET_DIRS` copies `claude/settings` → `.claude` verbatim; both checked-in sample projects (`generated-projects/small-python-team`, `drill-deck-base`) have byte-identical `settings.local.json` despite different postures/teams.
- `safety_writer.py` imports `Posture`/`HookMode`/`HookPackSelection` but not `SafetyConfig` — hooks are posture-aware, permissions are not.

## Proposed change

**Recommendation: wire it, don't delete it.** It is the only path to posture-differentiated permissions, and SPEC-014's defense-in-depth (`permissions.deny` backing up the bypassable regex hooks) needs exactly this mechanism.

1. Add `regulated_safety()` factory to `models.py` completing the posture triple; `CompositionSpec.effective_safety()` returns `spec.safety` if set, else the factory matching `spec.hooks.posture`.
2. New `foundry_app/services/permissions_writer.py` (or a function inside `safety_writer.py`) that renders `.claude/settings.local.json` from `effective_safety()`:
   - **baseline:** `deny`: force-push, `rm -rf /`, push to protected branches, reads of `.env`/`**/credentials*`/`~/.ssh/**`; `allow`: project test/lint/build commands (`uv run pytest*`, `uv run ruff*`, `git status`, `git diff*`, `git log*`).
   - **hardened:** baseline + `deny` network-fetch piped to shell, `git push` outside feature branches; `defaultMode` unchanged.
   - **regulated:** hardened + `defaultMode: "ask"` for `Bash`, deny writes outside the project root, deny `WebFetch` except allow-listed docs domains (field on `SafetyConfig.network`).
   - Each `SafetyConfig` sub-policy maps to concrete rule groups; document the mapping table in the module docstring so it is reviewable in one place.
3. Merge semantics: start from the library's `claude/settings/settings.local.json` as the base, then overlay the derived rules (union of deny lists, union of allow lists, strictest `defaultMode` wins). Never silently drop library rules — this is the permissions analogue of SPEC-004's settings.json fix.
4. Call the writer from `generator.py` as part of the safety stage; record the derived rule count in the manifest.
5. Validator: warn when a composition sets `safety:` fields that the writer does not map (unknown = silently ignored today; must become visible).
6. Tests: golden-file tests for the three postures; a test asserting hardened ⊃ baseline and regulated ⊃ hardened deny sets.

## Out of scope

- Hook-pack rendering and the settings.json overwrite bug (SPEC-004).
- Hardening the hook scripts themselves (SPEC-014).
- New composition knobs for per-persona tool restriction (SPEC-011).

## Acceptance criteria

- [ ] `file:` `foundry_app/services/permissions_writer.py` exists (or `safety_writer.py` gains a documented `write_permissions` entry point).
- [ ] `test:` generating the same team at `baseline`, `hardened`, and `regulated` produces three **different** `settings.local.json` files, each a superset of the previous posture's deny list.
- [ ] `test:` library base rules survive the overlay (no rule present in `ai-team-library/claude/settings/settings.local.json` is absent from generated output).
- [ ] `file-contains:` `foundry_app/core/models.py` contains `def regulated_safety`.
- [ ] `test:` `CompositionSpec.effective_safety()` falls back to the posture factory when `safety:` is omitted.
- [ ] `lint:` `uv run ruff check foundry_app/` passes.
- [ ] `manual:` regenerate `examples/small-python-team.yml` and confirm the emitted permissions match the mapping table.

## Files to touch

- `foundry_app/core/models.py`
- `foundry_app/services/permissions_writer.py` (new) or `safety_writer.py`
- `foundry_app/services/generator.py`, `validator.py`
- `tests/test_permissions_writer.py` (new)
- `generated-projects/` samples (regenerate; with SPEC-028)
