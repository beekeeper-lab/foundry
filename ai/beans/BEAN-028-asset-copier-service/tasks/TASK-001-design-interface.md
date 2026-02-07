# TASK-001: Design asset copier interface and review models

| Field | Value |
|-------|-------|
| **Task ID** | TASK-001 |
| **Bean** | BEAN-028 |
| **Owner** | architect |
| **Priority** | 1 |
| **Status** | Pending |
| **Depends On** | (none) |

## Description

Review the existing models (`StageResult`, `CompositionSpec`, `LibraryIndex`, `PersonaInfo`) and the scaffold service pattern. Design the `copy_assets()` function signature and document what asset categories are copied (persona templates, commands, hooks). Confirm the overlay-safe behavior pattern.

## Acceptance Criteria

- [ ] Function signature defined: `copy_assets(spec, library_index, library_root, output_dir) -> StageResult`
- [ ] Asset categories documented: persona templates, commands, hooks
- [ ] Overlay behavior specified: skip identical files, warn on conflicts
- [ ] No model changes needed (existing models sufficient)
