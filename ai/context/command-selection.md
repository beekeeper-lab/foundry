# Command and Skill Selection Rules

How `foundry_app/services/asset_copier.py` decides which `.claude/commands/` and `.claude/skills/` entries land in a generated project.

## TL;DR

| Rule | Behavior |
|------|----------|
| Default commands/skills | Copied unconditionally (workflow, ops, backlog tooling). |
| Dev-loop commands (`/test`, `/build`, `/lint`, `/format`, `/dev`) | Stack-aware — one set is selected based on the project's expertise. |
| Governance commands/skills (`/threat-model`, `/risk-liability`, `/ip-licensing`, `/contract-review`, `/regulatory-assessment`, `/legal-drafting`) | Gated — copied only when an unlocking persona is on the team. |

## Dev-loop command selection

Dev-loop command sources live under `ai-team-library/claude/commands/dev-loop/<stack>/`. The copier picks **the first stack** matched by the project's expertise (in declared order) and flattens that set into `.claude/commands/`.

Mapping (`_DEV_LOOP_STACK_BY_EXPERTISE` in `asset_copier.py`):

| Expertise id | Dev-loop stack |
|--------------|----------------|
| `python` | `python` |
| `python-qt-pyside6` | `python` |
| `node` | `node` |
| `react` | `node` |
| `typescript` | `node` |
| `react-native` | `node` |
| `frontend-build-tooling` | `node` |

If no selected expertise has a mapping, no dev-loop commands are copied.

The dev-loop commands **invoke** the user's configured tooling — they do not install or scaffold it. A Python `/test` calls `pytest`; a Node `/test` calls whatever `package.json`'s `scripts.test` resolves to.

## Governance gating

Governance commands and skills are sensitive: they ship only when the team has a persona who would actually use them. This prevents a small Python project from receiving `/ip-licensing` and `/contract-review` by default.

### Commands (`_GOVERNANCE_COMMANDS`)

| Command file | Unlocked when team includes |
|--------------|------------------------------|
| `threat-model.md` | `security-engineer` |
| `risk-liability.md` | `legal-counsel` or `compliance-risk` |

### Skills (`_GOVERNANCE_SKILLS`)

| Skill | Unlocked when team includes |
|-------|------------------------------|
| `threat-model` | `security-engineer` |
| `risk-liability` | `legal-counsel` or `compliance-risk` |
| `ip-licensing` | `legal-counsel` |
| `contract-review` | `legal-counsel` |
| `regulatory-assessment` | `legal-counsel` or `compliance-risk` |
| `legal-drafting` | `legal-counsel` |

## How to extend

- **Add a new dev-loop stack:** create `ai-team-library/claude/commands/dev-loop/<stack>/` with the five commands and add the `expertise_id → stack` rows to `_DEV_LOOP_STACK_BY_EXPERTISE`.
- **Gate a new command/skill:** add an entry to `_GOVERNANCE_COMMANDS` (filename) or `_GOVERNANCE_SKILLS` (skill id / file stem) with the set of unlocking persona ids.

## Related

- BEAN-256 — initial implementation.
- BEAN-255 — hook selection (parallel pattern for hooks).
