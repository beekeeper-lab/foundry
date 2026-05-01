# Task 01 — Developer: Author the data-scientist persona

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-291 / 01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 16:52 |
| **Completed** | 2026-05-01 17:00 |
| **Duration** | 8m |

## Goal

Create a complete `data-scientist` persona at the extended tier whose
files match the shape and depth of `data-analyst` and `data-engineer`,
update the data-analyst hand-off section to defer modeling/stats work
to the new persona, and update `ai-team-library/README.md` to reflect
the 25-persona total.

## Inputs

- `ai/beans/BEAN-291-data-scientist-persona/bean.md` — full positioning
  brief: mission, scope (in/out), activation triggers seed list, the
  four required output/template artifacts, persona id and display name
  conventions, and the symmetric hand-off requirement with data-analyst.
- `ai-team-library/personas/extended/data-analyst/` — sibling reference
  for file shape (`persona.md`, `outputs.md`, `prompts.md`, `templates/`)
  and tone.
- `ai-team-library/personas/extended/data-engineer/` — second sibling
  reference for tone consistency.
- `ai-team-library/README.md` — persona table + count to update.

## Acceptance Criteria

- [ ] `ai-team-library/personas/extended/data-scientist/persona.md`
      exists with sections (in order): Category, Mission, Scope (Does /
      Does not), Activated When, Operating Principles, Inputs I Expect,
      Outputs I Produce, Definition of Done, Quality Bar, Collaboration
      & Handoffs (table), Escalation Triggers, Anti-Patterns, Tone &
      Communication, Safety & Constraints. Section names match
      data-analyst exactly (Tech-QA will diff section headers).
- [ ] Hand-off section explicitly names **Data Analyst** as the owner
      of BI/KPI/dashboard work (the symmetric back-reference).
- [ ] `outputs.md` exists with at least four output specs:
      `model-card`, `experiment-design`, `analysis-notebook`,
      `statistical-report`. Each spec follows the data-analyst
      `outputs.md` shape (purpose, when produced, contents, quality
      bar).
- [ ] `prompts.md` exists with at least four task-mode prompts
      covering: exploratory analysis, hypothesis test, model
      selection, result reporting. Each prompt mirrors the
      data-analyst `prompts.md` template form.
- [ ] `templates/model-card.md`, `templates/experiment-design.md`,
      `templates/analysis-notebook.md`, `templates/statistical-report.md`
      exist. Each ~80–120 lines, structured like the data-analyst
      templates (frontmatter, sections, placeholder fields,
      definition-of-done checklist).
- [ ] `ai-team-library/personas/extended/data-analyst/persona.md` —
      Hand-off / Collaboration table updated to defer
      modeling/statistical-test design/ML to **Data Scientist**.
- [ ] `ai-team-library/README.md` — persona table includes a row for
      `data-scientist`; the documented persona count moves from 24 →
      25 wherever it appears.
- [ ] Re-run the library indexer programmatically to confirm the new
      persona is discovered:
      ```
      uv run python -c "
      from pathlib import Path
      from foundry_app.services.library_indexer import build_library_index
      idx = build_library_index(Path('ai-team-library'))
      assert any(p.id == 'extended/data-scientist' for p in idx.personas), 'not indexed'
      print('persona count:', len(idx.personas))
      "
      ```
- [ ] `uv run pytest` — all tests pass.
- [ ] `uv run ruff check foundry_app/` — clean (no app code touched, but
      sanity-check the gate).

## Definition of Done

- All persona files exist and are content-complete (no `TODO`, no
  placeholder `[fill in]` text left).
- The new persona has the same structural shape as data-analyst (a
  diff of section headers shows zero differences).
- Status updated to Done; the telemetry hook stamps Completed/Duration.
