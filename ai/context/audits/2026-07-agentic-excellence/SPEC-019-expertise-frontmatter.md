# SPEC-019: Expertise pack frontmatter and structural normalization

- **Priority:** P2
- **Effort:** M
- **Area:** expertise
- **Depends on:** SPEC-003 (expertise compile contract / entry-file restructure)
- **Status:** Proposed

## Problem

None of the 184 expertise files carries frontmatter. All pack metadata is **scraped from prose headings**: the indexer looks for a `## Category` heading (in `conventions.md` or the first alphabetical file) and a `## Applies To` heading. This is fragile — renaming or reordering a heading silently changes indexed metadata — and inconsistently used: only 5 of 42 packs declare `## Applies To`, the entry-file convention splits 23/19 between `conventions.md` and domain-named files, and there is no versioning or review-date signal anywhere. ADR-012's persona-scoped expertise filtering has no scoping data for 37 packs. The pack-authoring contract is undocumented and unenforced, which is exactly how half the library became silently dead (SPEC-003).

## Evidence

- `grep -rl '^---' ai-team-library/expertise/ --include='*.md'` → 0 of 184 files have frontmatter.
- `foundry_app/services/library_indexer.py:333-375` — `## Category` and `## Applies To` heading-scraping (docstrings at `:337`, `:359` confirm the mechanism).
- `## Applies To` present in only 5 packs (`python`, `r`, `react`, `typescript`, `accessibility-compliance`); the compiler treats empty applies-to as "applies to everyone", making the 5 the anomaly.
- Entry-file split: 23 packs use `conventions.md`, 19 use domain-named first files (`core-services.md`, `privacy-security-rules.md`, …) — the root cause of SPEC-003's dead packs.
- `ai-team-library/README.md:70` asserts "Each expertise directory contains a `conventions.md` file" — false for 19 packs; nothing enforces it.
- `foundry_app/services/compiler.py:393` — ADR-012 relevance filtering hook point that lacks data for 37 packs.

## Proposed change

1. **Define a frontmatter schema** for expertise files and document it in `ai-team-library/README.md`:

   ```yaml
   ---
   id: python                # pack id (entry file only)
   category: Software Development
   applies_to: [developer, tech-qa, architect]   # empty/omitted = all personas
   entry: true               # exactly one file per pack
   role: reference           # entry | reference (siblings)
   last_reviewed: 2026-07    # YYYY-MM
   ---
   ```

   Sibling files carry the minimal `{role: reference, last_reviewed}`; only the entry file carries pack-level metadata.
2. **Indexer:** `library_indexer.py` parses frontmatter first and falls back to the existing heading-scrape (so unmigrated third-party packs keep working); emit a deprecation warning on fallback.
3. **Validator:** new checks — `expertise-missing-frontmatter` (WARNING during migration, ERROR once migration lands), `expertise-no-entry-file` (ERROR; supersedes/joins SPEC-003's check), `expertise-multiple-entry-files` (ERROR), `applies_to` ids must be known personas (WARNING).
4. **Migration:** script-assisted pass adding frontmatter to all 184 files; `category` lifted from the existing `## Category` heading (heading may then be deleted from the body — one source of truth); `applies_to` populated for the 42 packs using the ADR-012 relevance table where it exists, else left empty (= all).
5. **Compiler:** read `applies_to` from the index (not the heading) in `_expertise_applies_to`; no behavior change for empty values.
6. Keep the schema deliberately small — no abstract taxonomy fields until something consumes them.

## Out of scope

- Making dead packs compile (SPEC-003 — this spec assumes its entry-file restructure and adds the metadata layer on top).
- Refreshing stale content or reconciling contradictions (SPEC-020).
- Frontmatter for personas/skills/commands (SPEC-002 covers the kit; personas are compiled, not discovered).

## Acceptance criteria

- [ ] `file-contains:` `ai-team-library/README.md` documents the frontmatter schema with all six fields.
- [ ] `test:` every file under `ai-team-library/expertise/` parses with valid frontmatter; exactly one `entry: true` per pack (new validator test, `uv run pytest`).
- [ ] `test:` indexer prefers frontmatter over headings when both present and disagree.
- [ ] `test:` heading-scrape fallback still indexes a frontmatter-less pack and logs a deprecation warning.
- [ ] `test:` validator errors on a pack with zero or two `entry: true` files.
- [ ] `lint:` `uv run ruff check foundry_app/` passes.
- [ ] `manual:` `foundry-cli generate examples/small-python-team.yml --library ai-team-library` produces output identical to pre-migration (metadata change is behavior-neutral for already-live packs).

## Files to touch

- `ai-team-library/expertise/**/*.md` (all 184 — mechanical frontmatter addition)
- `ai-team-library/README.md`
- `foundry_app/services/library_indexer.py`, `validator.py`, `compiler.py`
- `scripts/` (one-shot migration script, may be deleted after)
- `tests/test_library_indexer.py`, `tests/test_validator.py`
