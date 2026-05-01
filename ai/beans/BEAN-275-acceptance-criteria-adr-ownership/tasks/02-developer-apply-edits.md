# Task 02: Apply Scope Boundaries Edits to Personas, Kit, and Bean Template

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-30 11:12 |
| **Completed** | 2026-04-30 11:35 |
| **Duration** | 23m |

## Goal

Apply BA's `BEAN-275-policy.md` deliverable as concrete edits across the
library, the Foundry kit submodule, and the bean template.

Edits required:

1. **Library persona files** — Add the BA-authored `## Scope Boundaries`
   subsection to each of the five core persona files. Place it after the
   existing top-level scope/responsibilities section but before any
   "Workflow" / "Outputs" / "Rules" sections. Match the file's existing
   heading depth and style.
   - `ai-team-library/personas/ba/persona.md`
   - `ai-team-library/personas/architect/persona.md`
   - `ai-team-library/personas/developer/persona.md`
   - `ai-team-library/personas/tech-qa/persona.md`
   - `ai-team-library/personas/team-lead/persona.md`

2. **Foundry kit agent files** — The kit lives at `.claude/shared/`,
   which is a git submodule. The kit's agent files
   (`.claude/shared/agents/<role>.md`) are separate from the library's
   `persona.md` files. Apply the *same* Scope Boundaries content
   (rephrased to fit each kit file's structure as needed — kit files use
   "## Your Team", "## Operating Principles" etc.; insert as
   `## Scope Boundaries` near the bottom, before `## Outputs` /
   `## Rules`).
   - `.claude/shared/agents/ba.md`
   - `.claude/shared/agents/architect.md`
   - `.claude/shared/agents/developer.md`
   - `.claude/shared/agents/tech-qa.md`
   - `.claude/shared/agents/team-lead.md`

   Submodule workflow:
   - `cd .claude/shared`
   - The submodule is in detached HEAD. Create a working branch:
     `git checkout -b kit/BEAN-275-scope-boundaries`
   - Make the five file edits.
   - Commit with message `BEAN-275: add Scope Boundaries subsections`.
   - Push: `git push -u origin kit/BEAN-275-scope-boundaries`.
   - Then **also fast-forward `main` of the kit** so the parent repo
     does not point at a feature-branch tip. The kit's policy is "main
     is the integration branch" — so merge the working branch into the
     kit's `main` and push that:
     `git checkout main && git pull && git merge --no-ff kit/BEAN-275-scope-boundaries && git push origin main`
   - Then return to the parent repo's worktree
     (`cd ../..`) and stage the new submodule pointer:
     `git add .claude/shared` (the parent records the kit's new commit).

3. **Team-Lead orchestration update** — Apply BA's prose addition to
   `ai-team-library/personas/team-lead/persona.md` AND
   `.claude/shared/agents/team-lead.md`. Insert in the relevant
   orchestration / participation section.

4. **Bean template heading update** — Apply BA's exact before/after to
   `ai/beans/_bean-template.md`'s `## Acceptance Criteria` heading.

5. **Idempotency check** — A grep of the five library + five kit files
   for "acceptance criteria" must NOT find any prose that contradicts
   the new ownership rule (e.g., "Developer writes acceptance criteria"
   would contradict). If you find a contradiction, fix the wording in
   the same edit pass.

Constraints:
- No code change in `foundry_app/`. This is a pure documentation /
  policy bean. Do not run `uv run pytest` or modify tests — that is
  Tech-QA's job (Task 03).
- Run `uv run ruff check foundry_app/` only as a sanity check that
  nothing broke (you are not editing Python; this should be a no-op).
- Don't commit on the parent branch — Team-Lead batches the parent
  commit. The submodule commit + push is your responsibility.
- Don't update extended persona files (out of scope per bean).

## Inputs

- `ai/outputs/ba/BEAN-275-policy.md` — BA's authored sections (paste these in)
- `ai-team-library/personas/ba/persona.md` — target file
- `ai-team-library/personas/architect/persona.md` — target file
- `ai-team-library/personas/developer/persona.md` — target file
- `ai-team-library/personas/tech-qa/persona.md` — target file
- `ai-team-library/personas/team-lead/persona.md` — target file
- `.claude/shared/agents/ba.md` — kit target (submodule)
- `.claude/shared/agents/architect.md` — kit target (submodule)
- `.claude/shared/agents/developer.md` — kit target (submodule)
- `.claude/shared/agents/tech-qa.md` — kit target (submodule)
- `.claude/shared/agents/team-lead.md` — kit target (submodule)
- `ai/beans/_bean-template.md` — bean template
- `ai/context/decisions.md` — ADR-013 (read for context only — do not edit)

## Acceptance Criteria

- [ ] Five library persona files contain a non-empty `## Scope
      Boundaries` subsection matching BA's text.
- [ ] Five kit agent files contain a non-empty `## Scope Boundaries`
      subsection matching BA's text (allowing structural rephrasing per
      file's existing pattern).
- [ ] Team-Lead orchestration text references AC owner per wave
      configuration and the ADR-threshold escalation path in both
      library and kit.
- [ ] Bean template AC heading carries BA's "Authored by: ..."
      subnote.
- [ ] Submodule branch `kit/BEAN-275-scope-boundaries` is pushed AND
      kit `main` is updated and pushed.
- [ ] Parent repo's `.claude/shared` pointer is staged (not committed
      yet — Team-Lead handles parent commit).
- [ ] `uv run ruff check foundry_app/` is clean (sanity).

## Definition of Done

- All eleven files (5 library + 5 kit + 1 bean template) edited.
- Submodule pushed.
- Parent repo's submodule pointer staged.
- Tech-QA can verify by reading the eleven files and grepping for
  "acceptance criteria" without finding a contradiction.
