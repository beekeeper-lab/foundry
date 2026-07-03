# SPEC-020: Expertise freshness and cross-pack contradiction pass

- **Priority:** P2
- **Effort:** M
- **Area:** expertise
- **Depends on:** SPEC-019 (for `last_reviewed` frontmatter dates; content fixes can land independently)
- **Status:** Proposed

## Problem

Expertise content ages into agent prompts. Several packs pin dated tool versions, one hardcodes 2025-era model IDs **and per-token prices** that are now wrong, and overlapping packs give guidance that can conflict when co-selected — with no precedence rule for the compiler or the agent to resolve the conflict. Since packs are concatenated verbatim into prompts, every stale line and every unresolved contradiction ships directly into generated teams.

## Evidence

Staleness (as of July 2026):
- `ai-team-library/expertise/mlops/llm-operations.md:40` — default model `claude-sonnet-4-20250514`; `:328-330` — `MODEL_COSTS` table hardcoding `claude-sonnet-4` at $3/$15 and `gpt-4o` at $2.50/$10 per 1M tokens. Model IDs and prices are stale and will keep going stale.
- `ai-team-library/expertise/node/conventions.md:36` — `.nvmrc` example pins Node 22 (Node 24 is current LTS); `:61-62` — `"module": "Node16"` / `"moduleResolution": "Node16"` (current guidance: `NodeNext`/`Bundler`).
- `ai-team-library/expertise/dotnet/` — targets ".NET 8+ / C# 12+" and presents .NET 8 features as new (`IExceptionHandler (.NET 8+)`, `TimeProvider (.NET 8+)`); .NET 10 LTS shipped Nov 2025, .NET 8 leaves support Nov 2026.
- `ai-team-library/expertise/dotnet/unity.md:4,20` — "Unity 2022 LTS+", "Unity 2023+"; Unity 6 is current.
- `ai-team-library/expertise/azure-cloud-platform/core-services.md:100` — ARM `apiVersion: 2023-12-01` example.

Contradiction/overlap:
- `clean-code/conventions.md:45` — constants `UPPER_SNAKE` "(or the language's established idiom)" vs `dart/conventions.md:331` — constants `camelCase`, explicitly "not UPPER_SNAKE_CASE". (Correction to the audit report: clean-code's parenthetical already defers to language idiom, so this is a soft conflict — but no pack or compiler rule states the precedence, so a generated agent sees both flat statements.)
- Duplicated guidance emitted twice when co-selected: error-handling (fail-fast/catch-narrow) in `clean-code/conventions.md:101-119` ≈ `python/conventions.md:235-243` ≈ rust; "80% coverage" repeated in `python`, `rust`, `clean-code`.
- Security truisms ("don't log secrets", "validate at boundaries", "least privilege") spread across 10+ files (`security/`, per-language `*/security.md`, compliance packs) with no single source of truth.

## Proposed change

1. **Kill hardcoded model prices.** In `mlops/llm-operations.md`, delete the `MODEL_COSTS` literal; replace with a pattern: "load rates from config / the provider's pricing page at deploy time" and use current model-family names (Claude Sonnet 4.5 / GPT-5 class) only as *examples* marked as such. (If SPEC-021's LLM pack absorbs this file, do it there instead — coordinate.)
2. **Version refresh pass:** node → Node 24 example + `NodeNext`; dotnet → frame against .NET 10 LTS, drop "(.NET 8+)" novelty markers; unity → Unity 6; azure → current ARM apiVersion. Prefer *floors* ("Node ≥ 22") over point versions wherever possible so content ages slower.
3. **Precedence rule, stated once and compiled in:** add to `ai-team-library/README.md` and `clean-code/conventions.md`: *"When a language/framework pack and a generic practices pack disagree, the more specific pack wins."* Have the compiler emit this one line at the top of the combined expertise section (`foundry_app/services/compiler.py`, expertise assembly) so every generated agent carries the tie-breaker.
4. **Cheap dedupe:** where a generic principle is restated verbatim in a language pack, cut the language-pack copy unless it adds language-specific content (keep `structlog`/`tracing` specifics; cut the restated principle). Target the error-handling and coverage duplications first; do not attempt a full dedupe.
5. **`last_reviewed` stamping:** set `last_reviewed: 2026-07` (per SPEC-019 schema) on every file touched; add a maintenance note in the README that packs older than 12 months should be re-reviewed (advisory; no tooling gate yet).
6. Fold in a light fact-check of the refreshed claims (versions, LTS dates) during implementation — do not trust this spec's dates blindly either.

## Out of scope

- New packs and coverage gaps (SPEC-021).
- Compile-time reachability of dead packs (SPEC-003) — refresh the dead compliance/cloud packs' content only if SPEC-003 has made them live; otherwise sequence after it.
- Frontmatter mechanics (SPEC-019).

## Acceptance criteria

- [ ] `file-contains:` `ai-team-library/expertise/mlops/llm-operations.md` contains no `MODEL_COSTS` literal and no `claude-sonnet-4-20250514`.
- [ ] `file-contains:` `ai-team-library/expertise/node/conventions.md` contains `NodeNext`.
- [ ] `file-contains:` `ai-team-library/README.md` contains the specific-pack-wins precedence rule.
- [ ] `file-contains:` generated combined expertise output includes the precedence line (assert via compiler test).
- [ ] `test:` `uv run pytest` passes (compiler test updated for the precedence header).
- [ ] `manual:` co-select `clean-code` + `dart` in a scratch composition; confirm the compiled output contains the precedence rule adjacent to both packs' constants guidance.
- [ ] `manual:` spot-check refreshed version claims against current upstream docs at implementation time.

## Files to touch

- `ai-team-library/expertise/mlops/llm-operations.md`, `node/conventions.md`, `dotnet/*.md`, `dotnet/unity.md`, `azure-cloud-platform/core-services.md`, `clean-code/conventions.md`, `python/conventions.md`, `rust/conventions.md`
- `ai-team-library/README.md`
- `foundry_app/services/compiler.py` (precedence header line)
- `tests/test_compiler.py`
