# Task 1: Add PERSONA_DESCRIPTIONS and Implement Grouped Layout

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-02-20 21:01 |
| **Completed** | 2026-02-20 21:01 |
| **Duration** | < 1m |

## Description

Update `persona_page.py` to:

1. Add PERSONA_DESCRIPTIONS entries for the 11 new personas: change-management, customer-success, data-analyst, data-engineer, database-administrator, financial-operations, legal-counsel, mobile-developer, platform-sre-engineer, product-owner, sales-engineer

2. Refactor `load_personas()` to group PersonaCards by category:
   - Group personas by `PersonaInfo.category`
   - Each group rendered as a collapsible `QGroupBox` with header showing "Category Name (N)"
   - All groups expanded by default
   - Personas with empty category go in "Other" group at the bottom
   - Maintain alphabetical order within groups
   - Category groups ordered alphabetically, with "Other" last

3. Ensure `get_team_config()` and `set_team_config()` work across groups by iterating all cards in `self._cards` dict.

## Inputs
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`
- `foundry_app/core/models.py` (PersonaInfo.category field)

## Outputs
- Modified `persona_page.py` with grouped layout and complete PERSONA_DESCRIPTIONS

## Acceptance Criteria
- All 24 personas have PERSONA_DESCRIPTIONS entries
- Cards are grouped under collapsible QGroupBox by category
- Category headers show "Name (count)" format
- All groups expanded by default
- Empty/unknown category goes to "Other"
- get_team_config/set_team_config still work correctly