# Task 01: Design and Implement Technology Stack Page

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-021-T01 |
| **Owner** | developer |
| **Status** | Pending |
| **Depends On** | — |

## Description

Create `foundry_app/ui/screens/builder/wizard_pages/stack_page.py` following the same card-based UI pattern as the persona page (BEAN-020). The page displays all available stacks from the LibraryIndex, allows multi-select via checkboxes, and supports reordering selected stacks.

## Deliverables

1. **StackCard widget** — individual card for each stack:
   - Checkbox for selection/deselection
   - Stack name (human-readable, derived from id)
   - Description of the stack's purpose
   - File count badge showing number of convention files
   - Visual highlight when selected (consistent with PersonaCard)

2. **StackSelectionPage widget** — wizard page container:
   - Heading and subtitle explaining the purpose
   - Scrollable area with StackCard instances
   - Move up/down buttons for reordering selected stacks
   - Warning label when no stacks are selected
   - `selection_changed` signal for wizard navigation
   - `load_stacks(library_index)` to populate from LibraryIndex
   - `get_stack_selections()` returning list[StackSelection]
   - `set_stack_selections()` for restoring state (back navigation)
   - `is_valid()` returning True when at least one stack selected

3. **Stack descriptions dictionary** — human-readable names and descriptions for all 11 stacks

4. **Catppuccin theme** — consistent with project_page.py and persona_page.py styling

## Acceptance Criteria

- All library stacks appear as cards in the scrollable area
- Each stack card shows name, description, and file count
- User can select/deselect stacks via checkbox
- At least one stack must be selected for validation to pass
- Selections are returned as list[StackSelection] with correct order values
- State can be saved and restored via get/set methods
- Visual feedback on card selection (border highlight)
