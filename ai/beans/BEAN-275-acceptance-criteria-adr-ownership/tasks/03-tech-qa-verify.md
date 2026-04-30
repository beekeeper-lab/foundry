# Task 03: Verify BEAN-275 — Partition Tests, Grep Sweep, AC Verdict

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 02 |
| **Status** | Done |
| **Started** | 2026-04-30 15:04 |
| **Completed** | 2026-04-30 15:10 |
| **Duration** | 6m |

## Goal

Add focused tests that lock in the partition cleanliness of the new
Scope Boundaries subsections, run the full suite + lint, sweep BEAN-275's
seven Acceptance Criteria, and produce a structured pass/fail report.

Tests to add (location: `tests/`, follow the project's existing module /
class naming conventions):

1. **Subsection presence** — Each of the five library persona files
   (`ai-team-library/personas/<role>/persona.md`) contains a non-empty
   `## Scope Boundaries` subsection.
2. **Kit subsection presence** — Each of the five kit agent files
   (`.claude/shared/agents/<role>.md`) contains a non-empty
   `## Scope Boundaries` subsection (or whichever heading depth the kit
   files use — match Developer's actual choice).
3. **AC ownership rule present** — Each of the five Scope Boundaries
   subsections names *who owns acceptance-criteria* in a way consistent
   with BA's policy (BA when on wave; Team-Lead default; others verify).
4. **ADR-vs-dev-decision rule present** — The Architect, Developer, and
   Team-Lead Scope Boundaries subsections reference the blast-radius
   rule. (BA and Tech-QA may reference the rule lightly or not at all
   depending on BA's text — match BA's intent.)
5. **No contradictions** — Grep the five library files + five kit files
   for "acceptance criteria" and assert no line says a non-owner
   *authors* AC. (Build a small list of forbidden phrases, e.g.
   "Developer writes acceptance criteria", "Tech-QA defines acceptance
   criteria", and assert none are present.)
6. **Bean template heading subnote** — `ai/beans/_bean-template.md`'s
   `## Acceptance Criteria` section carries the "Authored by: BA (when
   activated) | Team-Lead (default)" subnote.
7. **Partition cleanliness** — Build a small structural test that loads
   the five Scope Boundaries subsections, normalizes them, and asserts
   no two subsections claim ownership of the same artifact (
   `acceptance-criteria` is owned by exactly one role per wave config —
   the partition lives in BA's policy text; this test enforces it).

Then run:
- `uv run pytest` — no regressions.
- `uv run ruff check foundry_app/` — clean.

Sweep BEAN-275's seven Acceptance Criteria. Write a structured pass/fail
report to `ai/outputs/tech-qa/BEAN-275-vdd.md`. Format: a table with one
row per AC, columns: AC text, Status (Pass / Gap), Evidence. Gaps under a
"Gaps" heading at the top.

Don't commit — Team-Lead batches the commit after the wave.

## Inputs

- `ai/outputs/ba/BEAN-275-policy.md` — BA's authored sections (oracle for the tests)
- `ai-team-library/personas/ba/persona.md` — verify subsection present
- `ai-team-library/personas/architect/persona.md` — verify subsection present
- `ai-team-library/personas/developer/persona.md` — verify subsection present
- `ai-team-library/personas/tech-qa/persona.md` — verify subsection present
- `ai-team-library/personas/team-lead/persona.md` — verify subsection present
- `.claude/shared/agents/ba.md` — verify subsection present
- `.claude/shared/agents/architect.md` — verify subsection present
- `.claude/shared/agents/developer.md` — verify subsection present
- `.claude/shared/agents/tech-qa.md` — verify subsection present
- `.claude/shared/agents/team-lead.md` — verify subsection present
- `ai/beans/_bean-template.md` — verify subnote present
- `tests/` — directory for new tests; match existing module / class style

## Acceptance Criteria

- [ ] New tests added under `tests/` and pass.
- [ ] `uv run pytest` is green (no regressions).
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] Grep sweep finds zero contradictions of the AC ownership rule.
- [ ] `ai/outputs/tech-qa/BEAN-275-vdd.md` exists with a row per AC,
      Pass with concrete evidence (or Gap with remediation note).

## Definition of Done

- Tests + VDD report committed-ready (Team-Lead will batch).
- Bean can be safely marked Done by Team-Lead solely from the VDD
  report's evidence.
