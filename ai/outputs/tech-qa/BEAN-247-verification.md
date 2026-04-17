# BEAN-247 — Tech-QA Verification

## Scope

Verify that the compiler no longer lists expertise in the generated
`CLAUDE.md` when the expertise's source file was not emitted, while still
surfacing the missing-source warning.

## Test Runs

- `uv run pytest` — 1811 passed, 0 failed.
- `uv run ruff check foundry_app/` — clean.
- New unit tests in `tests/test_compiler.py`:
  - `test_missing_expertise_excluded_from_claude_md`
  - `test_all_expertise_references_in_claude_md_exist_on_disk`
- New integration test in `tests/test_generator.py`:
  - `TestGenerationSelfConsistency::test_claude_md_expertise_references_exist_on_disk`
- Updated: `test_claude_md_contains_expertise_content` now only asserts
  reference presence for expertise whose source file was emitted.

## Manual Verification

Regenerated `examples/small-python-team.yml`:

- `ai/generated/expertise/` on disk: `python.md` only.
- `CLAUDE.md` Tech Stack references: `python.md` only.
- No reference to `ai/generated/expertise/clean-code.md`.
- Pipeline still emits warning: `Expertise 'clean-code' missing conventions.md`.

## Conclusion

Acceptance criteria satisfied. Generated project no longer ships with a
broken internal expertise reference.
