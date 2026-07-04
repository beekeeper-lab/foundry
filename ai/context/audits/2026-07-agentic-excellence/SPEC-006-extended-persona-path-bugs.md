# SPEC-006: Fix extended-persona path bugs in compiler and agent writer

- **Priority:** P0
- **Effort:** S
- **Area:** pipeline
- **Depends on:** none
- **Status:** Proposed

## Problem

ADR-014 introduced tiered persona ids (`extended/<name>`), and the scaffolder/compiler correctly flatten them with `_persona_dirname` when creating directories and filenames. But the *link-emitting* sites still use the raw persona id, so every project that includes an extended persona ships broken pointers in two places: the CLAUDE.md Team table links to `.claude/agents/extended/<name>.md` and `ai/generated/members/extended/<name>.md` (actual files are flat), and each extended agent file's own body points its Output directory at `ai/outputs/extended/<name>/` and its "Full compiled prompt" at `ai/generated/members/extended/<name>.md` — neither exists. In `drill-deck-base`, all five extended-persona rows have dead links in both columns.

A smaller library defect rides along: `tech-qa/persona.md` has two `## Scope Boundaries` headings and orders `## Activated When` before Scope Boundaries — the inverse of its four core peers. Any tooling that dedupes or keys on heading text (the pipeline doc explicitly flags duplicate headings) can trip on it.

## Evidence

- `foundry_app/services/compiler.py:580-585` — Team table rows interpolate raw `pid` into both link columns.
- `foundry_app/services/agent_writer.py:283` — context passes `"persona_id": persona_sel.id` (raw, tiered) into the template.
- `foundry_app/templates/agent.md.j2:5,27` — `ai/outputs/{{ persona_id }}/` and `ai/generated/members/{{ persona_id }}.md`.
- `foundry_app/services/agent_writer.py:290-292` — by contrast, the *filename* correctly uses `_persona_dirname(persona_sel.id)`; the flat-dir convention is established, the body just disagrees with it.
- `generated-projects/drill-deck-base/CLAUDE.md:40-44` — links to `.claude/agents/extended/mobile-developer.md` etc.; on-disk files are flat.
- `ai-team-library/personas/core/tech-qa/persona.md:30,46,68` — `## Activated When` at 30, `## Scope Boundaries` at 46, second `## Scope Boundaries (AC and ADR/dev-decision)` at 68; peers order Scope Boundaries (~30) then Activated When (~60).

## Proposed change

1. In `compiler.py` Team-table construction, resolve link paths with the same flattening used at write time — pass or compute `_persona_dirname(pid)` for both the agent and member columns (display name unchanged).
2. In `agent_writer.write_agents`, add `"persona_dirname": _persona_dirname(persona_sel.id)` to the context; change `agent.md.j2` lines 5 and 27 to use it. Keep `persona_id` available if anything else needs the tiered id.
3. Audit the remaining emit sites for the same class of bug: scaffold's `ai/outputs/` creation, member-file writing in `compiler.py` (`ai/generated/members/`), and the generated `composition.yml` contracts block — confirm each is flat-consistent; fix any stragglers.
4. **Regression test:** add a generation test that composes a team including at least one `extended/` persona, generates to a temp dir, extracts every relative link/backtick path from the emitted CLAUDE.md and agent files, and asserts each resolves to an existing file/directory. This catches the whole bug class, not just today's instances.
5. Library fix: restructure `tech-qa/persona.md` to the peer order (Scope Boundaries then Activated When) and merge/rename the duplicate heading (e.g. second one becomes `## Scope Boundaries — AC vs ADR ownership` or folds into the first as a subsection `### AC and ADR/dev-decision ownership`).
6. Regenerate both sample projects.

## Out of scope

- Frontmatter in agent files (SPEC-001) — coordinate, both touch `agent.md.j2`.
- Broader dangling-reference sweep in kit/library prose (SPEC-007).

## Acceptance criteria

- [ ] `test: tests/test_generation_links.py` — every path emitted in CLAUDE.md and `.claude/agents/*.md` for an extended-persona composition resolves on disk.
- [ ] `file-contains: generated-projects/drill-deck-base/CLAUDE.md` — Team table links use `.claude/agents/mobile-developer.md` (no `extended/` segment).
- [ ] `file-contains: generated-projects/drill-deck-base/.claude/agents/code-quality-reviewer.md` — Output directory reads `ai/outputs/code-quality-reviewer/` (flat).
- [ ] `file-contains: ai-team-library/personas/core/tech-qa/persona.md` — exactly one `## Scope Boundaries` H2.
- [ ] `test: uv run pytest` — full suite passes.

## Files to touch

- `foundry_app/services/compiler.py`
- `foundry_app/services/agent_writer.py`
- `foundry_app/templates/agent.md.j2`
- `ai-team-library/personas/core/tech-qa/persona.md` (library-change approval)
- `tests/test_generation_links.py` (new)
- `generated-projects/*` (regenerated)
