# Task 02: Implement Persona Tiering — File Reorg, Indexer, Model, Compiler, Wizard, Examples

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-30 23:42 |
| **Completed** | 2026-04-30 23:56 |
| **Duration** | 14m |

## Goal

Implement the tiering scheme decided by ADR-014 (Task 01). Move the 24
persona directories into `core/` and `extended/`, teach the indexer and
compiler about the tier, gate default emission to core, update the
wizard UI to group by tier, and update example compositions and the
library README. The Library Manager UI's persona-create flow should
default new personas into `extended/`.

## Inputs

- `ai/beans/BEAN-271-library-persona-tiering/bean.md` — bean spec.
  Read the **Scope — In Scope** list and the **Acceptance Criteria**
  section.
- `ai/context/decisions.md` — **ADR-014** (the syntax decision from
  Task 01). Implement exactly what the ADR specifies.
- `ai-team-library/personas/` — current flat layout of 24 directories.
  Core 5: `team-lead, ba, architect, developer, tech-qa`. Extended 19:
  everything else.
- `foundry_app/core/models.py` — `PersonaInfo` (line 546). Add
  `tier: Literal["core", "extended"]`.
- `foundry_app/services/library_indexer.py` — `_scan_personas`
  (line 219). Update to scan both `core/` and `extended/` subdirs and
  set `tier` on each `PersonaInfo`.
- `foundry_app/services/compiler.py` — review how
  `spec.team.personas` is consumed (line 682+). The default composition
  (no `personas:` block) must produce a project containing only `tier=core`.
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` —
  group personas into two collapsible sections labeled **"Core team"**
  and **"Extended specialists"** with brief explainer text.
- `foundry_app/ui/screens/library_manager.py` (line 1017,
  `target_dir = self._library_root / rel_path`) — for new personas
  created via the UI, target `personas/extended/<name>/` (core is a
  fixed set; users don't add to it).
- `examples/foundry-dogfood.yml`, `examples/full-stack-web.yml`,
  `examples/security-focused.yml`, `examples/small-python-team.yml` —
  rewrite extended-persona references in the syntax ADR-014 specifies.
- `ai-team-library/README.md` (line 16, line 125) — update persona
  table to mark each persona's tier; update the "Add a persona"
  instructions for the new layout.
- `ai-team-library/workflows/foundry-pipeline.md` (line 100) — update
  "Adding a persona" instructions.

## Acceptance Criteria

- [ ] `ai-team-library/personas/core/` contains exactly: `team-lead`,
      `ba`, `architect`, `developer`, `tech-qa` (full directory contents
      moved with `git mv`).
- [ ] `ai-team-library/personas/extended/` contains the remaining 19
      personas (full contents moved with `git mv`).
- [ ] `PersonaInfo.tier` field exists and is set correctly by
      `_scan_personas` for every persona.
- [ ] Default composition (no `personas:` block) generates a project
      containing only the 5 core personas.
- [ ] A composition that explicitly references an extended persona
      (in the ADR-014 syntax) generates the right project.
- [ ] If a composition references an unknown or wrong-tier persona,
      the compiler errors with the message specified in ADR-014.
- [ ] Wizard's persona selection page renders two clearly-labeled
      groups ("Core team", "Extended specialists").
- [ ] Library Manager UI's "Add Persona" creates new personas under
      `personas/extended/`.
- [ ] All 4 example compositions in `examples/` updated to use
      ADR-014 syntax for their extended-persona references; at least
      one example references an extended persona to exercise the path.
- [ ] `ai-team-library/README.md` persona table marks each persona's
      tier and instructions reflect the new layout.
- [ ] `ai-team-library/workflows/foundry-pipeline.md` updated for the
      new layout.
- [ ] Lint clean: `uv run ruff check foundry_app/`.
- [ ] Tests pass for all files you touched (Tech-QA owns the broader
      regression sweep in Task 03 — but if your edits clearly break a
      test, fix it here).

## Definition of Done

- All persona dirs moved with `git mv` (preserves history).
- All listed code/config/doc files updated.
- Lint clean.
- Status set to `Done`.

## Notes

**Use `git mv`, not `mv`.** Preserves history across the rename.
Example: `git mv ai-team-library/personas/team-lead ai-team-library/personas/core/team-lead`.

**`tests/` will break temporarily.** Fixtures in `test_validator.py`,
`test_agent_writer.py`, and `test_persona_contracts.py` reference
`personas/<id>` paths. **Do not fix them in this task** — Tech-QA
(Task 03) owns the test sweep. But ensure your code changes don't
break tests that aren't path-dependent.

**Defer scope:** Do not edit persona content, do not refactor unrelated
code, do not add new personas. The bean explicitly excludes content
edits.
