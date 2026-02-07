# TASK-002: Implement asset_copier.py service

| Field | Value |
|-------|-------|
| **Task ID** | TASK-002 |
| **Bean** | BEAN-028 |
| **Owner** | developer |
| **Priority** | 2 |
| **Status** | Pending |
| **Depends On** | TASK-001 |

## Description

Implement `foundry_app/services/asset_copier.py` with a `copy_assets()` function that:

1. Copies persona templates from `library/personas/<id>/templates/` to `output/ai/outputs/<id>/` when `include_templates=True`
2. Copies commands from `library/claude/commands/` to `output/.claude/commands/`
3. Copies hooks from `library/claude/hooks/` to `output/.claude/hooks/`
4. Returns `StageResult` with relative paths in `wrote` and any warnings

Follow the scaffold service pattern. Use `shutil.copy2` for file copying. Handle overlay-safe behavior (skip identical files, warn on conflicts).

## Acceptance Criteria

- [ ] `foundry_app/services/asset_copier.py` exists with `copy_assets()` function
- [ ] Persona templates copied when `include_templates=True`
- [ ] Templates skipped when `include_templates=False`
- [ ] Commands always copied from library
- [ ] Hooks always copied from library
- [ ] Returns `StageResult` with relative paths
- [ ] Overlay-safe: identical files skipped, conflicts warned
- [ ] Missing template directories handled gracefully
- [ ] Logging follows scaffold service pattern (INFO for copies, DEBUG for skips)
