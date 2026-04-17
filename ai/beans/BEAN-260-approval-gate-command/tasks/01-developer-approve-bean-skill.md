# Task 01 — Developer: Approve-Bean Skill, Command, Validator, and Workflow Docs

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Implement the `/internal:approve-bean NNN` skill and command that gates the `Unapproved → Approved` transition behind a criteria check. Add a matching Python validator helper so the rules are pytest-testable. Document the approval gate in `ai/context/bean-workflow.md`.

## Inputs

- `ai/beans/BEAN-260-approval-gate-command/bean.md` (this bean)
- `ai/beans/_bean-template.md` (reference for required fields)
- `.claude/shared/skills/internal/new-bean/SKILL.md` (pattern for an internal bean-manipulation skill)
- `.claude/shared/commands/internal/new-bean.md` (pattern for a command doc)
- `ai/context/bean-workflow.md` (existing workflow doc — section §2 Approval will gain a "Approval Gate" subsection)
- `foundry_app/services/validator.py` (pattern for a service-layer validator)

## Required Changes

1. **`foundry_app/services/bean_approval.py`** (new)
   - Export `ApprovalCheck` dataclass with fields: `ok: bool`, `missing: list[str]`, `bean_id: str | None`.
   - Export `check_bean_approvable(bean_path: Path) -> ApprovalCheck`.
   - Parse `bean.md` markdown:
     - Metadata table: read **Bean ID**, **Priority**, **Category**.
     - Sections: confirm `## Problem Statement`, `## Goal`, `## Scope`, `## Acceptance Criteria` each have at least one non-blank, non-placeholder content line.
   - Missing-field rule: a field is "missing" if absent, blank, the template placeholder (e.g. `BEAN-NNN`, `YYYY-MM-DD`, `(App | Process | Infra)`, `Medium` is OK but `—` is missing, `What problem does this bean solve?` is placeholder), or only contains the template example lines (e.g. `- Item 1`, `- Item 2`, `- Criterion 1`, `- Criterion 2`).
   - Return `ApprovalCheck(ok=True, missing=[], bean_id=...)` when all fields present; otherwise `ok=False` with a list of human-readable names like `"Problem Statement"`, `"Scope (In Scope list empty or placeholder)"`.

2. **`.claude/local/skills/internal/approve-bean/SKILL.md`** (new)
   - Section structure mirrors `.claude/shared/skills/internal/new-bean/SKILL.md`: Description, Trigger, Inputs, Process, Outputs, Quality Criteria, Error Conditions, Dependencies.
   - Document the validator algorithm and point to `foundry_app/services/bean_approval.py` for test coverage.
   - Process: resolve bean dir from `NNN` → run `check_bean_approvable` → on failure, print missing fields and exit with actionable message → on success, update Status to `Approved` in both `bean.md` and `_index.md`, commit with message `Approve BEAN-NNN: <title>[; rationale: <text>]`.

3. **`.claude/local/commands/internal/approve-bean.md`** (new)
   - Short command doc (follow `.claude/shared/commands/internal/new-bean.md` format): Purpose, Usage, Inputs, Process, Output, Error Handling, Examples.
   - Invocation: `/internal:approve-bean NNN [--rationale "<text>"]`.

4. **`ai/context/bean-workflow.md`** (modify)
   - Add an `#### Approval Gate` section inside `### 2. Approval` containing:
     - The approval checklist (Problem Statement, Goal, Scope, Acceptance Criteria, Priority, Category all populated).
     - The command entry point: `/internal:approve-bean NNN`.
     - Audit trail note: approver identity comes from git commit author; rationale passes via `--rationale`.
     - Failure handling: command refuses approval and lists missing fields.

## Acceptance Criteria

- [ ] `foundry_app/services/bean_approval.py` exists with `check_bean_approvable()` and `ApprovalCheck`.
- [ ] `.claude/local/skills/internal/approve-bean/SKILL.md` exists and references the validator.
- [ ] `.claude/local/commands/internal/approve-bean.md` exists with Usage / Process / Examples sections.
- [ ] `ai/context/bean-workflow.md` has a new `#### Approval Gate` subsection under `### 2. Approval`.
- [ ] Ruff clean: `uv run ruff check foundry_app/`.

## Example Output

`ApprovalCheck` signature follows the `StageResult` dataclass pattern already used in `foundry_app/core/models.py`:

```python
@dataclass
class ApprovalCheck:
    ok: bool
    missing: list[str]
    bean_id: str | None
```
