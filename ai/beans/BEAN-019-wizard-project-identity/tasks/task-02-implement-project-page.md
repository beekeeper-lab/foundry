# Task 02: Implement project identity page

| Field | Value |
|-------|-------|
| Owner | developer |
| Status | Pending |
| Depends On | task-01 |

## Description

Create `foundry_app/ui/screens/builder/wizard_pages/project_page.py` with a `ProjectPage` QWidget class that:
- Provides a project name input (required)
- Provides a tagline input (optional)
- Auto-generates and displays a slug (read-only) from the project name
- Validates that name is non-empty before allowing progression
- Returns data as a ProjectIdentity model
- Follows the Catppuccin dark theme from MainWindow

## Acceptance Criteria

- [ ] ProjectPage renders name, tagline, and slug fields
- [ ] Slug auto-updates when name changes
- [ ] `is_complete()` returns False when name is empty
- [ ] `get_data()` returns a valid ProjectIdentity
