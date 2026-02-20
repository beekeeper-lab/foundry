# Task 01: Add Changes Section to Template and Merge Workflow

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:19 |
| **Completed** | 2026-02-20 20:20 |
| **Duration** | 1m |

## Goal

Add a `## Changes` section placeholder to the bean template, and update the merge-bean workflow to populate it with a git diff summary when a bean is completed.

## Inputs

- `ai/beans/_bean-template.md` — current template (already in context)
- `.claude/skills/internal/merge-bean/SKILL.md` — merge workflow (already in context)
- `.claude/commands/internal/merge-bean.md` — merge command doc (already in context)

## Implementation

1. **Bean template** (`ai/beans/_bean-template.md`): Add a `## Changes` section between `## Notes` and `## Trello` with a placeholder indicating it will be auto-populated.

2. **Merge-bean SKILL.md** (`.claude/skills/internal/merge-bean/SKILL.md`): Add a new step in Phase 1 (after telemetry aggregation, before branch derivation) that:
   - Runs `git diff --stat main...HEAD` (or the target branch base) to get file-level change summary
   - Parses the output to build a markdown table of files changed with +/- line counts
   - Writes the result into the bean's `## Changes` section in `bean.md`
   - Commits the updated `bean.md` before proceeding to merge

3. **Merge-bean command doc** (`.claude/commands/internal/merge-bean.md`): Update the Process section to mention the Changes section population step.

## Example Output

The `## Changes` section placeholder in the template:

```markdown
## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |
```

The populated Changes section after merge:

```markdown
## Changes

| File | Lines |
|------|-------|
| `foundry_app/core/validator.py` | +25 −3 |
| `tests/test_validator.py` | +40 −0 |
| **Total** | **+65 −3** |
```

The new step in merge-bean SKILL.md:

```markdown
### Phase 1.5: Populate Changes Section

4. **Generate change summary** — On the feature branch, run `git diff --stat <target>...HEAD` to get the file-level diff summary.
5. **Write Changes section** — Parse the diff stat output and populate the `## Changes` section in `bean.md` with a markdown table listing each file and its +/- line counts.
6. **Commit changes** — `git add bean.md && git commit -m "Populate Changes section"`.
```

## Definition of Done

- [ ] `_bean-template.md` has a `## Changes` section placeholder
- [ ] merge-bean SKILL.md describes the step that populates the Changes section
- [ ] merge-bean command doc mentions the Changes step
- [ ] Changes section format includes file paths and +/- line counts
