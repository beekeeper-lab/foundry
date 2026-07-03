# SPEC-004: Hook generation reconciliation: hook-policy no-op, settings.json overwrite, render validation

- **Priority:** P0
- **Effort:** M
- **Area:** pipeline
- **Depends on:** none
- **Status:** Proposed

## Problem

The hook generation path silently degrades generated projects in three compounding ways.

First, `hook-policy` — the pack selected by the flagship examples (`small-python-team`, `foundry-dogfood`) — has no entry in `safety_writer._HOOK_PACK_REGISTRY`, so `_build_hooks` logs "Unknown hook pack" and skips it. Second, any explicit `hooks.packs` list *replaces* the stack-aware defaults rather than extending them, so selecting extra packs costs you the baseline ones: `drill-deck-base` selected `hook-policy, pre-commit-lint, security-scan` and lost `git-commit-branch` — its generated `settings.json` has no protected-branch guard despite `posture: baseline`. Net result for `small-python-team`: an essentially empty `settings.json` (`{"hooks":{"PreToolUse":[],"PostToolUse":[]}}`) from a composition that asked for hardened hooks.

Third, the write order destroys good input: the asset copier first copies the library's `claude/settings/settings.json` (which wires branch protection, `validate-task-inputs.py`, and `telemetry-stamp.py`), then generation stage 7 (`write_safety`) overwrites `.claude/settings.json` with the registry-derived hooks-only file — and the hook *scripts* the library settings referenced are never copied. The validator blesses all of this: it checks a selected pack exists in the library index (`hook-policy.md` exists as a doc, so it passes) but never that the pack renders any hooks.

## Evidence

- `foundry_app/services/safety_writer.py:394-398` — unknown pack → `logger.warning(...); continue` (silent at generation-result level).
- `foundry_app/services/safety_writer.py:43-188` — `_HOOK_PACK_REGISTRY` contents; no `hook-policy` key.
- `foundry_app/services/safety_writer.py:351-360` — `if spec.hooks.packs:` uses explicit list exclusively; stack-aware defaults only when the list is empty.
- `foundry_app/services/generator.py:350-351` — Stage 7 `write_safety` runs after Stage 4 asset copy; `write_safety` writes `.claude/settings.json` wholesale.
- `examples/small-python-team.yml`, `examples/foundry-dogfood.yml:54-66` — both select `hook-policy`.
- `generated-projects/small-python-team/.claude/settings.json` — empty hooks arrays; `generated-projects/drill-deck-base/.claude/settings.json` — no branch guard.
- `ai-team-library/claude/settings/settings.json` — the richer, discarded hook wiring.
- `foundry_app/services/validator.py` (`_check_hook_packs`) — existence check only.

## Proposed change

1. **Registry entry for `hook-policy`:** define it in `_HOOK_PACK_REGISTRY` as the meta-pack it's documented to be — at minimum the branch-protection PreToolUse guard plus `validate-task-inputs.py` wiring — or, if it is truly only documentation, remove it from the examples and make selecting it a validation ERROR. Pick one; the current half-state is the bug.
2. **Explicit packs extend, don't replace:** in `_resolve_packs`, union explicit selections with the posture's base pack set (`_stack_aware_default_packs`). Provide an explicit opt-out (`hooks.replace_defaults: true`) for the rare composition that genuinely wants replacement, and emit a WARNING listing dropped base packs when it's used.
3. **Merge, don't overwrite, settings.json:** `write_safety` must read an existing `.claude/settings.json` (from asset copy) and deep-merge hook entries (dedup by `(event, matcher, command)`), preserving non-hook keys. The library-sourced hooks survive; registry hooks add to them.
4. **Copy referenced hook scripts:** any `command` in the merged settings referencing `.claude/hooks/<script>` must have that script copied into the generated project (extend asset_copier's hooks stage); fail the stage with a warning if the script can't be found.
5. **Validator render check:** after pack resolution, ERROR when a selected, enabled pack resolves to zero hook entries (`hook-pack-renders-nothing`), and WARNING when explicit packs drop a posture base pack (pre-change behavior detection).
6. **Regenerate the sample projects** so `small-python-team` demonstrably ships branch protection + task-input validation.

## Out of scope

- Making the documented-but-unwired quality-gate hook packs real (SPEC-015).
- SafetyConfig → permissions derivation (SPEC-016).
- Kit-side hook script hardening (SPEC-014).

## Acceptance criteria

- [ ] `test: tests/test_safety_writer.py` — (a) `hook-policy` renders non-empty hooks (or is rejected by the validator, per decision in step 1); (b) explicit packs union with posture base packs; (c) settings merge preserves pre-existing hook entries and dedups.
- [ ] `test: tests/test_validator.py` — zero-render pack selection yields ERROR.
- [ ] `file-contains: generated-projects/small-python-team/.claude/settings.json` — a PreToolUse branch-protection entry after regeneration.
- [ ] `file-contains: generated-projects/drill-deck-base/.claude/settings.json` — branch guard present alongside the ruff and secret-scan hooks.
- [ ] `test: uv run pytest` — full suite passes.

## Files to touch

- `foundry_app/services/safety_writer.py`
- `foundry_app/services/asset_copier.py` (hook-script copying)
- `foundry_app/services/validator.py`
- `foundry_app/core/models.py` (optional `hooks.replace_defaults` flag)
- `tests/test_safety_writer.py`, `tests/test_validator.py`
- `generated-projects/*` (regenerated), `examples/*.yml` (if `hook-policy` is retired)
