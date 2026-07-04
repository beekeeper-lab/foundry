# BEAN-295 VDD Report — Web and Backend Framework Expertise Packs

| Field | Value |
|-------|-------|
| **Bean** | BEAN-295 |
| **Date** | 2026-07-03 |
| **Verifier** | tech-qa |

**Verdict:** PASS

## Acceptance Criteria

| # | Criterion | Evidence type | Result | Evidence |
|---|-----------|---------------|--------|----------|
| 1 | FastAPI pack exists with frontmatter | file: `ai-team-library/expertise/fastapi/conventions.md` | PASS | File exists; frontmatter `id: fastapi`, `category: Frameworks`, `entry: true`, `last-reviewed: 2026-07` |
| 2 | Next.js pack exists with frontmatter | file: `ai-team-library/expertise/nextjs/conventions.md` | PASS | File exists; frontmatter `id: nextjs`, `category: Frameworks`, `applies_to: [developer, tech-qa, architect, code-quality-reviewer]`, `entry: true`, `last-reviewed: 2026-07` |
| 3 | Frontmatter contract holds | test: `tests/test_reference_integrity.py` | PASS | `uv run pytest tests/test_reference_integrity.py tests/test_library_indexer.py -q` → 69 passed |
| 4 | All tests pass | test: `tests/` | PASS | `QT_QPA_PLATFORM=offscreen uv run pytest -q` → **2567 passed, 4 warnings in 15.20s** |

## Programmatic Gate

`foundry-cli vdd 295 --manual pass` run 2026-07-03; aggregate verdict **PASS**
(machine report at `ai/outputs/tech-qa/vdd-295.md`). Note: the gate must be
run with `QT_QPA_PLATFORM=offscreen` — without it, the full-suite criterion
aborts with pytest exit 134 (Qt cannot open a display headless). See Notes.

Lint: `uv run ruff check foundry_app/` → "All checks passed!"

## Schema Adherence (SPEC-019 authoring contract)

All four packs verified against the pack authoring contract in
`ai-team-library/README.md` (§Expertise, SPEC-019).

| Pack | Files | Frontmatter (entry file) | Canonical sections | Siblings frontmatter-free |
|------|-------|--------------------------|--------------------|---------------------------|
| fastapi | conventions.md + testing.md, security.md, architecture.md (4) | id matches dir, category Frameworks, entry true, last-reviewed 2026-07 | Category, Defaults table, §1-6 numbered, Do/Don't, Common Pitfalls, Checklist | yes |
| nextjs | conventions.md + testing.md, performance.md, deployment.md (4) | id matches dir, category Frameworks, applies_to (4 personas), entry true, last-reviewed 2026-07 | Category, Applies To, Defaults table, §1-6 numbered, Do/Don't, Common Pitfalls, Checklist | yes |
| vue | conventions.md + testing.md, architecture.md (3) | id matches dir, category Frameworks, applies_to (3 personas), entry true, last-reviewed 2026-07 | Category, Defaults table, §1-6 numbered, Do/Don't, Common Pitfalls, Checklist | yes |
| spring-boot | conventions.md + testing.md, security.md, observability.md (4) | id matches dir, category Frameworks, entry true, last-reviewed 2026-07 | Category, Defaults table, §1-6 numbered, Do/Don't, Common Pitfalls, Checklist | yes |

### Content spot-checks

- **Rules are concrete**, not filler: e.g. fastapi mandates app-factory +
  `Annotated` DI aliases with explicit `status_code` on non-200 routes; vue's
  pitfalls cover reactivity loss via `reactive()` destructuring and
  `storeToRefs()`; spring-boot bans `open-in-view` default and self-invoked
  `@Transactional` calls.
- **Defaults tables are decision-dense** (concern → default, with override
  path where relevant; spring-boot adds an explicit "Override Requires" column).
- **Version claims are conservative**: FastAPI >= 0.115, Next.js 14+ targeting
  15.x behavior, Vue 3.4+, Spring Boot 3.x / Java 21 LTS floor. No claims
  beyond the knowledge horizon.
- **Scope discipline**: nextjs and spring-boot explicitly defer generic
  guidance to the `react` / `java` packs instead of duplicating it, matching
  the SPEC-020 conflict-precedence model.

## Test Run

| Command | Result |
|---------|--------|
| `QT_QPA_PLATFORM=offscreen uv run pytest -q` | 2567 passed, 4 warnings, 15.20s |
| `uv run pytest tests/test_reference_integrity.py tests/test_library_indexer.py -q` | 69 passed |
| `uv run ruff check foundry_app/` | clean |

## Notes

- Minor: the `foundry-cli vdd` gate runs the full suite without setting
  `QT_QPA_PLATFORM`, so on headless machines it reports a spurious FAIL
  (exit 134) unless the caller exports `QT_QPA_PLATFORM=offscreen`. Not a
  BEAN-295 defect; consider a follow-up bean to set the env var inside the
  vdd runner.
- Minor wording nit: fastapi's numbered-section heading style uses `&`
  ("App Structure & Routers") where other packs spell "and" — cosmetic only.

**Recommendation:** GO — bean ready for merge.
