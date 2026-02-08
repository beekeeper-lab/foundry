# BEAN-043: Add Application Logo

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-043 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Foundry has no application icon or logo. The `resources/icons/` directory exists as an empty placeholder (only `.gitkeep`). The application uses the default Qt/platform window icon, making it harder to identify in the taskbar and giving it an unfinished appearance. A custom logo graphic has been provided and needs to be integrated as the application's visual identity.

## Goal

Add the provided logo graphic to the project, wire it up as the application's window icon (taskbar, window decoration, Alt-Tab), and display it in the About dialog. The application should have a consistent visual identity across all places where an icon is shown.

## Scope

### In Scope
- Copy the source graphic (`/home/gregg/Downloads/ChatGPT Image Feb 7, 2026, 07_50_27 PM.png`) into `resources/icons/foundry-logo.png`
- Set the application window icon in `foundry_app/main.py` using `QApplication.setWindowIcon()` with `QIcon`
- Display the logo in the About dialog (`_show_about()` in `main_window.py`)
- Ensure the icon file is packaged in the wheel by updating `pyproject.toml` package data configuration
- Resolve the icon path correctly at runtime (relative to package or using `importlib.resources` / `pathlib`)

### Out of Scope
- Generating multiple icon sizes (32x32, 64x64, etc.) — use original PNG as-is, Qt handles scaling
- Creating a `.ico` file for Windows
- Creating a `.desktop` file for Linux
- Creating a macOS `.icns` file
- Modifying the sidebar or other UI elements to show the logo

## Acceptance Criteria

- [ ] `resources/icons/foundry-logo.png` exists in the repository
- [ ] Application window shows the Foundry logo in the title bar and taskbar
- [ ] About dialog displays the logo image
- [ ] Icon path resolves correctly whether running from source (`uv run foundry`) or installed package
- [ ] `pyproject.toml` includes the resources directory in package data so the icon ships with the wheel
- [ ] No new dependencies introduced (uses only PySide6 built-in `QIcon`/`QPixmap`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Generate logo PNG to `resources/icons/foundry-logo.png` | developer | | Done |
| 2 | Update `pyproject.toml` to include `resources/icons` in package data | developer | 1 | Done |
| 3 | Add `setWindowIcon()` call in `foundry_app/main.py` | developer | 1 | Done |
| 4 | Add logo to About dialog in `main_window.py` | developer | 1 | Done |
| 5 | Run tests and lint | tech-qa | 2,3,4 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Source image: `/home/gregg/Downloads/ChatGPT Image Feb 7, 2026, 07_50_27 PM.png`
- Target location: `resources/icons/foundry-logo.png`
- The `resources/icons/` directory already exists with a `.gitkeep`
- Currently `main.py` only calls `app.setApplicationName("Foundry")` and `app.setOrganizationName("Foundry")` — no icon is set
- BEAN-036 (Update About Dialog Text) should incorporate the logo when implementing the About dialog update — this bean should be done first
- For runtime path resolution, use `Path(__file__).parent.parent / "resources" / "icons" / "foundry-logo.png"` or similar relative-to-package approach
