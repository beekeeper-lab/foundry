# Task 01: ADR — ClaudeKit-Distributed Skills Pattern

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends on** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Record an Architecture Decision Record in `ai/context/decisions.md`
that establishes ClaudeKit (`.claude/shared/`) as the canonical source
of truth for cross-project skills, and `ai-team-library/` as the home
for project-template assets (commands, hooks, persona templates). The
ADR must define the kit-distributed skill registry, the resolution
contract for `asset_copier.copy_assets()`, and the rationale for
preferring single-source-of-truth over a mirroring approach.

The ADR is the contract that BEAN-280's Developer task implements. It
also locks the design that BEAN-281–285 will follow.

## Inputs

- `ai/beans/BEAN-280-claudekit-canonical-skills-distribution/bean.md` — full scope and acceptance criteria for this bean
- `ai/context/decisions.md` — ADR home; match its format and numbering
- `foundry_app/services/asset_copier.py` — existing copier; understand current resolution logic for context
- `foundry_app/services/subtree_setup.py` — existing subtree path; the ADR must explain how it interacts with library-copy mode
- `.claude/shared/skills/` — current contents (the canonical-skills location)
- `ai-team-library/claude/skills/` — current contents (project-template skills)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` — reference design; cite as motivating context

## Changes Required

1. **ADR section** in `ai/context/decisions.md` (next available ADR number) titled
   "ClaudeKit as Canonical Source for Cross-Project Skills". The ADR must contain:
   - **Context** — the dual-distribution problem (subtree mode vs library-copy mode produce different skill sets), with the existing `generate-image` gap as the motivating example.
   - **Decision** — ClaudeKit owns cross-project skills; ai-team-library owns project-template assets. Define both ownership boundaries explicitly.
   - **Kit-distributed skill registry** — the initial list (`generate-image`, `generate-screen`) plus the criteria for adding skills to the registry.
   - **Resolution rules** for `asset_copier.copy_assets()`:
     - Subtree mode: skip kit-distributed skills (subtree already covers them)
     - Library-copy mode: resolve kit-distributed skills from `<claude_kit_root>/skills/<name>/`; resolve all other skills from `<library_root>/claude/skills/<name>/`
   - **Consequences** — what becomes easier (single source of truth, no drift), what becomes harder (skills must be designed kit-first; project-template-only skills stay in ai-team-library).
   - **Alternatives considered** — explicitly reject "mirror skills into ai-team-library via sync script" as the wrong shape (creates two locations to maintain; semantics become muddled).
2. **Cross-reference** — add a one-line entry in `ai-team-library/claude/skills/`'s
   structure docs (or a README in that directory if appropriate) noting that the
   library does not own cross-project skills; those live in ClaudeKit.

## Acceptance Criteria

- [ ] ADR exists in `ai/context/decisions.md` with the structure above.
- [ ] ADR is numbered consecutively with the existing ADRs in the file.
- [ ] Kit-distributed skill registry is named explicitly (matches the constant name the Developer task will introduce: `_KIT_DISTRIBUTED_SKILLS`).
- [ ] Resolution rules are precise enough that an implementer can reproduce the algorithm without further design discussion.
- [ ] "Alternatives considered" section names the mirror-script approach and explains why it was rejected.
- [ ] No code changes in this task — design only.

## Definition of Done

- ADR section appended to `ai/context/decisions.md`.
- The Developer task (02) can read this ADR and implement asset_copier without ambiguity.
- Commit message: `BEAN-280 task 01: ADR for kit-distributed skills pattern`.
