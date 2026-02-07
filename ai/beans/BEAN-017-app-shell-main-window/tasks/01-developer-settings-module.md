# Task 01: Settings Module

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Pending |

## Goal

Create `foundry_app/core/settings.py` — a QSettings-backed persistent user preferences module.

## Inputs

- Bean scope: library_root, workspace_root, recent files, window geometry
- PySide6 QSettings API

## Definition of Done

- [ ] `FoundrySettings` class wraps QSettings
- [ ] Persists: library_root, workspace_root, recent_libraries, window geometry
- [ ] Type-safe getters/setters with defaults
- [ ] Works without a running QApplication (for testing)
