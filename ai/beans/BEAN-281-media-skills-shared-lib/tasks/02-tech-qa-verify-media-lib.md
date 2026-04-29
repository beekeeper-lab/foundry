# Task 02: Verify BEAN-281 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify every BEAN-281 acceptance criterion. Run the full
test suite and lint. Confirm the regex-order contract is locked down.
Sign off or list specific gaps.

## Inputs

- `ai/beans/BEAN-281-media-skills-shared-lib/bean.md` — bean acceptance criteria
- `.claude/shared/skills/_media_lib/` — Developer's new module (env.py, text.py, cost.py, __init__.py)
- `tests/test_media_lib.py` — Developer's new test file
- `foundry_app/services/asset_copier.py` — verify `_media_lib` is in `_KIT_DISTRIBUTED_SKILLS`
- `ai/context/decisions.md` — verify ADR-009 lists `_media_lib` (or the registry it names matches the constant)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_narration.py` — the reference implementation (verify regex order matches verbatim)

CONTEXT DIET: stay within these inputs.

## BEAN-281 Acceptance Criteria

1. `_media_lib/` module exists in `.claude/shared/skills/` with `env.py`, `text.py`, `cost.py`, `__init__.py`.
2. `_media_lib` is added to `_KIT_DISTRIBUTED_SKILLS`.
3. `load_env()` resolves `.env` from cwd → parents → `$HOME`, with existing process env taking precedence.
4. `normalize_narration_text()` reproduces the Stonewaters reference behavior bit-for-bit.
5. `hash_text()` returns `sha256(normalize_narration_text(s))` hex digest.
6. Tests pass (`uv run pytest tests/test_media_lib.py`).
7. All tests pass (`uv run pytest`).
8. Lint clean (`uv run ruff check foundry_app/`).

## Verification Steps

1. **Module presence** — `ls .claude/shared/skills/_media_lib/` shows all four files.
2. **Public surface** — `from _media_lib import load_env, normalize_narration_text, hash_text` works (or equivalent verification through the test file).
3. **Registry** — `grep _media_lib foundry_app/services/asset_copier.py` confirms it's in `_KIT_DISTRIBUTED_SKILLS`.
4. **`load_env` behavior** — read the implementation; confirm walk order, $HOME fallback, no-overwrite-existing-env semantics.
5. **`normalize_narration_text` regex order** — diff the regex order against the Stonewaters reference. They MUST match. If they differ, that's a FAIL.
6. **Regex-order contract test** — confirm a test exists that locks down the regex order. Run it; confirm it passes.
7. **`hash_text`** — confirm it's `sha256` and hex-encoded; confirm a test case matches a known input/output pair from the Stonewaters reference (if any are available; otherwise verify the relationship `hash_text(s) == hashlib.sha256(normalize_narration_text(s).encode("utf-8")).hexdigest()` directly in a spot-check).
8. **Test suite** — `uv run pytest` exits 0; report count and delta from prior baseline (1984).
9. **Module-specific tests** — `uv run pytest tests/test_media_lib.py -v` exits 0; count the assertions covering each regex case.
10. **Lint** — `uv run ruff check foundry_app/` exits 0.
11. **ADR-009** — confirm it mentions `_media_lib` in the registry (or the registry name in the ADR matches the actual constant after the Developer's edit).
12. **Commit message** — confirm `BEAN-281 task 01: ...` style.

## This Task's Acceptance Criteria

- [ ] Every BEAN-281 acceptance criterion verified.
- [ ] Verification report appended to this task file under `## Verification Report`.
- [ ] Pytest count + lint result captured.
- [ ] Regex-order match against Stonewaters reference verified explicitly (the load-bearing contract).
- [ ] Any gaps documented; not silently accepted.

## Definition of Done

- Verification report written.
- Bean is ready to be marked Done by the Team Lead, OR specific gaps are documented.
- Commit message: `BEAN-281 task 02: tech-qa verification`.
