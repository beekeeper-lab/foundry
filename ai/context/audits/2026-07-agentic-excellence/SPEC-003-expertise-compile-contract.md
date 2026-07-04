# SPEC-003: Expertise compilation contract: no silently dead packs

- **Priority:** P0
- **Effort:** L
- **Area:** expertise
- **Depends on:** none
- **Status:** Proposed

## Problem

The compiler reads exactly one file per expertise pack — `conventions.md`. 19 of the 42 packs don't have one, so they compile to nothing: a warning string is appended and the pack is dropped. That set includes every compliance pack (HIPAA, PCI-DSS, GDPR, SOX, ISO-9000, accessibility), all three cloud packs (AWS, Azure, GCP), and the security pack. A user who selects `hipaa-compliance` for a healthcare project gets zero HIPAA content in the generated project and no error.

Even in the 23 packs that do have `conventions.md`, every sibling file is unreachable: `dotnet/` has 9 files / ~2,920 lines and only one compiles; `mlops/llm-operations.md` (the library's only LLM-app guidance) is dead. Overall only 23 of 184 authored `.md` files (~12.5%) can reach any output. The validator doesn't catch any of this — it checks the pack exists and has *any* files, never that the one file the compiler needs exists. The library README asserts every pack has a `conventions.md`, which is false for 19 of 42.

## Evidence

- `foundry_app/services/compiler.py:478-483` — `_compile_expertise_section` reads only `expertise_dir / "conventions.md"`; on miss: warning + `return None`.
- `foundry_app/services/agent_writer.py:210-216` — agent files likewise read only `conventions.md`; `agent_writer.py:94-146` extracts only the `## Defaults` section from it.
- `foundry_app/services/validator.py:66-93` — `_check_expertise` checks `expertise is None` (ERROR) and `not expertise.files` (WARNING); never checks for `conventions.md`.
- `foundry_app/services/asset_copier.py` — no code path copies raw expertise directories into generated projects.
- Packs with no `conventions.md` (19): accessibility-compliance, aws-cloud-platform, azure-cloud-platform, change-management, customer-enablement, data-engineering, devops, finops, frontend-build-tooling, gcp-cloud-platform, gdpr-data-privacy, hipaa-compliance, iso-9000, pci-dss-compliance, product-strategy, sales-engineering, security, sox-compliance, sql-dba.
- `ai-team-library/README.md:70` — claims "Each expertise directory contains a `conventions.md` file."

## Proposed change

1. **Define the pack contract explicitly** in `ai-team-library/README.md` (and a new `ai-team-library/expertise/_pack-contract.md`): every pack MUST have `conventions.md` as its entry file (the distilled, always-compiled core: Category, Defaults table, Do/Don't, Pitfalls, Checklist); sibling `.md` files are deep-dive references.
2. **Author `conventions.md` for the 19 missing packs**, distilled from their existing content (e.g. `aws-cloud-platform/conventions.md` distills `core-services.md` + `well-architected.md`; `hipaa-compliance/conventions.md` distills `privacy-security-rules.md`). Follow the canonical section schema used by `python/conventions.md`. This is the bulk of the effort — 19 authored files.
3. **Compile siblings without inlining them:** in `compiler.py`, copy each selected pack's sibling files to `ai/generated/expertise/<id>/<file>.md` (subdirectory per pack) and append a generated "Deep-dive references" section to the compiled `conventions.md` output linking each sibling with its H1 title. This makes all 184 files reachable in the generated project without exploding prompt token load. Keep `conventions.md` as the only content inlined into member/agent prompts.
4. **Validator enforcement:** in `validator._check_expertise`, emit ERROR `expertise-missing-conventions` when a selected pack has files but no `conventions.md`. (Library-wide CI: a test asserting every pack in `ai-team-library/expertise/` has one, so unselected packs can't rot either.)
5. **Fix the README claim** and the "39 expertise" count (actual: 42).

## Out of scope

- Frontmatter metadata for packs (SPEC-019).
- Content freshness and cross-pack contradictions (SPEC-020).
- New packs (SPEC-021).
- Changing what `agent_writer` extracts (`## Defaults` highlight extraction stays as-is).

## Acceptance criteria

- [ ] `test: tests/test_library_integrity.py` — every directory under `ai-team-library/expertise/` contains `conventions.md` (new test, initially red for 19 packs, green after authoring).
- [ ] `test: tests/test_validator.py` — selecting a pack lacking `conventions.md` yields ERROR `expertise-missing-conventions`.
- [ ] `test: tests/test_compiler.py` — a pack with siblings produces `ai/generated/expertise/<id>/` copies plus a "Deep-dive references" section listing them.
- [ ] `file: generated-projects/small-python-team/ai/generated/expertise/python/` — sibling files present after regeneration (adjust path to actual sample).
- [ ] `manual:` generate a composition selecting `hipaa-compliance` and confirm compiled HIPAA content appears in the output project.
- [ ] `test: uv run pytest` — full suite passes.

## Files to touch

- `foundry_app/services/compiler.py`, `foundry_app/services/validator.py`
- `ai-team-library/expertise/<19 packs>/conventions.md` (new; library-change approval required — this repo's rule says the library is shared, so route via the library's own change process)
- `ai-team-library/README.md`, `ai-team-library/expertise/_pack-contract.md` (new)
- `tests/test_compiler.py`, `tests/test_validator.py`, `tests/test_library_integrity.py` (new)
- `generated-projects/*` (regenerated)
