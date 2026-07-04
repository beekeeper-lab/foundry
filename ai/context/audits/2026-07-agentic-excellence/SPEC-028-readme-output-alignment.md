# SPEC-028: Align README and sample projects with actual output

- **Priority:** P2
- **Effort:** S
- **Area:** docs
- **Depends on:** best done after SPEC-001, 004, 006, 013 land (regeneration step)
- **Status:** Proposed

## Problem

The root README's "Generated Project Structure" section materially over-describes what Foundry emits: it names context files, task layouts, manifests, and sub-agent behavior that do not exist in the actual output. The checked-in sample projects are ~7 weeks stale and showcase known bugs (an empty `settings.json`). A reader following the README will look for files that aren't there; a prospect evaluating the samples sees a degraded product. For each mismatch we must decide whether the README or the generator is wrong, fix accordingly, and then keep the samples continuously honest.

## Evidence

- README claims `ai/context/project.md`, `expertise.md`, `decisions.md`; actual generated tree has `ai/context/bean-workflow.md` + `project-charter.md` (verified in `generated-projects/small-python-team/ai/context/`).
- README says the manifest lives at `ai/generated/manifest.json`; `generator._write_manifest_file` writes project-root `manifest.json` (`foundry_app/services/generator.py:530`).
- README says seeded tasks land in `ai/tasks/seeded-tasks.md` with "wave-based dependency model … parallel lanes"; actual: `ai/tasks/` is empty and tasks live under `ai/beans/BEAN-001-bootstrap/tasks/NN-*.md` as flat per-persona lists (`foundry_app/services/seeder.py`).
- README says `ai/outputs/<role>/README.md`; actual outputs contain persona template files (`adr.md`, `test-plan.md`), no README.
- README "Component Roles" says `.claude/agents/` files load as sub-agent definitions — false until SPEC-001 (no frontmatter).
- Samples stale: `generated-projects/small-python-team/manifest.json` and `drill-deck-base` manifests carry `run_id` 20260512/20260523 (~7 weeks before 2026-07-03).
- `generated-projects/small-python-team/.claude/settings.json` is `{"hooks": {"PreToolUse": [], "PostToolUse": []}}` — the SPEC-004 hook-policy no-op, shipped as the flagship example.

## Proposed change

1. **Adjudicate each mismatch (README-bug vs generator-bug):**
   - `ai/context/*` filenames, manifest location, outputs contents → **README is wrong**; rewrite to match reality.
   - Seeded-task "wave-based dependency lanes" → **README is wrong today**; describe the actual starter-bean flow (ADR-004). If wave lanes are still wanted, that is a new feature bean, not a doc fix.
   - Sub-agent loading claim → **generator is wrong**; fixed by SPEC-001. Keep the README claim and mark it gated on SPEC-001 landing first.
   - Empty `settings.json` in samples → **generator is wrong**; fixed by SPEC-004.
2. **Rewrite the README "Generated Project Structure" section** from a freshly generated project tree (post-fix), not from memory. Include the root `manifest.json` and root `.mcp.json` (if SPEC-022 has landed) placements.
3. **Regenerate both sample projects** (`small-python-team`, `drill-deck-base`) after Wave-1/2 specs (001, 004, 006, 013) merge, and commit the refreshed trees.
4. **Add a freshness gate:** a CI job (or `make check-samples` target) that runs `foundry-cli generate examples/small-python-team.yml --library ai-team-library` into a temp dir and diffs against `generated-projects/small-python-team/` (excluding volatile fields: `run_id`, timestamps). Failing diff = samples or docs are stale.

## Out of scope

- Fixing the generator defects themselves (SPEC-001/004/006/013).
- Marketing/overview sections of the README (only the structure/behavior claims audited here).
- `docs/` deep-dives (touch only if they repeat the same structure claims).

## Acceptance criteria

- [ ] `manual:` every path named in README "Generated Project Structure" exists in a freshly generated `small-python-team` output, and every top-level generated path is documented.
- [ ] `file-contains:` `generated-projects/small-python-team/.claude/settings.json` contains at least one non-empty hook array (post-SPEC-004 regeneration).
- [ ] `manual:` sample manifests carry a regeneration `run_id` dated after this spec's implementation.
- [ ] `test:` the sample-freshness check exists and passes in CI (and demonstrably fails when a sample file is hand-edited).
- [ ] `manual:` README no longer claims wave-based task lanes or `ai/generated/manifest.json`.

## Files to touch

- `README.md` (Generated Project Structure, Component Roles sections)
- `generated-projects/small-python-team/**`, `generated-projects/drill-deck-base/**` (regenerated)
- CI config / `Makefile` or `scripts/check-samples.sh` (freshness gate)
