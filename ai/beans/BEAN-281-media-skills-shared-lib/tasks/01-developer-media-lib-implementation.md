# Task 01: Implement `_media_lib` Shared Library + Tests

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Build the `_media_lib` shared library at
`.claude/shared/skills/_media_lib/`. Three modules + package init:

- `env.py` — `.env` walker (cwd → parents → `$HOME`, first found wins; existing process env always wins over `.env` values).
- `text.py` — `normalize_narration_text()` (strip markdown markers, HTML tags, `🎙️` emoji, leading `> ` blockquote markers; collapse whitespace) and `hash_text()` (sha256 hex of normalized text).
- `cost.py` — small helpers for cost-table lookups + per-run cost summaries (used by both image and audio generators with their own cost tables).
- `__init__.py` — re-export the public surface.

The portability contract for `normalize_narration_text` and `hash_text` is load-bearing: a downstream build pipeline must produce the same hash for the same input. Capture this contract as a docstring on `normalize_narration_text` listing the regex order (verbatim from the Stonewaters reference), and lock the order in with tests that fail if the order changes.

Add `_media_lib` to `_KIT_DISTRIBUTED_SKILLS` in `foundry_app/services/asset_copier.py` so library-copy-mode projects receive it.

## Inputs

- `ai/beans/BEAN-281-media-skills-shared-lib/bean.md` — full scope and acceptance criteria
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_narration.py` — canonical implementation of the stripping regexes (port the order verbatim; this is the load-bearing contract)
- `foundry_app/services/asset_copier.py` — registry to extend with `"_media_lib"`
- `tests/` — directory for the new test file (`tests/test_media_lib.py` or wherever pattern matches)
- `.claude/shared/skills/_media_lib/` — destination (does not exist yet; create the directory)

CONTEXT DIET: stay within these inputs. Don't speculatively browse the rest of the kit.

## Changes Required

1. **Create `.claude/shared/skills/_media_lib/`** directory with:
   - `__init__.py` — re-export `load_env`, `normalize_narration_text`, `hash_text`, and the cost helpers.
   - `env.py` — `load_env(start: Path | None = None) -> dict[str, str]`. Walks `start or Path.cwd()` → all parents → `Path.home()` looking for a `.env` file. First found wins. Parses `KEY=VALUE` lines (one per line, ignore blanks and `#` comments, support quoted values). Returns dict of newly-set keys. Existing `os.environ` keys are NEVER overwritten. Use `python-dotenv` if available; else inline parser.
   - `text.py`:
     - `normalize_narration_text(text: str) -> str` — apply regexes in this exact order (the contract; document in the docstring):
       1. Strip leading `> ` blockquote markers (line by line).
       2. Strip the 🎙️ emoji (and any leading whitespace after it).
       3. Strip HTML tags (`<[^>]+>`).
       4. `**bold**` → `bold`
       5. `*italic*` → `italic`
       6. `` `code` `` → `code`
       7. `[label](url)` → `label`
       8. Collapse runs of whitespace (including newlines) to single spaces, then strip.
     - `hash_text(text: str) -> str` — `hashlib.sha256(normalize_narration_text(text).encode("utf-8")).hexdigest()`. Module docstring or function docstring must state explicitly that downstream consumers must use these functions verbatim or hashes will diverge.
   - `cost.py` — minimal:
     - `format_cost_summary(per_item_costs: list[float], label: str = "items") -> str` returning a one-line summary like `"42 items, total $5.46"`.
     - Other helpers if obviously needed by the surface; keep this file small.
2. **Tests** at `tests/test_media_lib.py`:
   - **env**: `load_env` finds nearest `.env` walking up; respects `$HOME` fallback; does not overwrite existing `os.environ`; handles quoted values; ignores blank/comment lines. (~5 tests)
   - **text normalization**: each regex case in isolation (bold, italic, code, link, emoji, blockquote, HTML, whitespace), plus a combined fixture matching the Stonewaters reference behavior. ~9 tests.
   - **regex-order contract test**: assert that a specific ambiguous input (e.g., a `**bold link [text](url)**`) produces the exact expected output. If the regex order changes, this test fails. ~1 test.
   - **hash stability**: same input → same hash; trivially-different markdown (e.g., `**foo**` vs `foo`) → same hash; semantically-different text → different hash; non-ASCII unicode round-trips correctly. ~4 tests.
3. **Add `"_media_lib"` to `_KIT_DISTRIBUTED_SKILLS`** in `foundry_app/services/asset_copier.py`. Update the inline comment if appropriate.
4. **Update ADR-009** in `ai/context/decisions.md` to add `_media_lib` to the named registry list (if it lists names; verify and update if needed).

## Acceptance Criteria

- [ ] `_media_lib/` module exists in `.claude/shared/skills/` with `env.py`, `text.py`, `cost.py`, `__init__.py`.
- [ ] `_media_lib` is added to `_KIT_DISTRIBUTED_SKILLS` so library-copy-mode projects receive it.
- [ ] `load_env()` resolves `.env` from cwd → parents → `$HOME`, with existing process env taking precedence.
- [ ] `normalize_narration_text()` reproduces the Stonewaters reference behavior bit-for-bit on the test cases ported from `Course_Material/Git_Fundamentals/scripts/generate_narration.py`.
- [ ] `hash_text()` returns `sha256(normalize_narration_text(s))` hex digest.
- [ ] Tests pass (`uv run pytest tests/test_media_lib.py`).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- All files created on the feature branch.
- Tests pass; lint clean.
- Regex-order docstring + locked-down test exist on `normalize_narration_text` to prevent future drift.
- Commit message: `BEAN-281 task 01: _media_lib shared library + tests`.
