# BEAN-044: Splash Screen & Branded Backgrounds

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-044 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Foundry launches directly into the main window with no splash screen or branded visual identity. Empty screens (History with no past runs, Export with no projects) show plain text placeholders. The app feels utilitarian and unfinished. A branded splash image has been provided — a dark circuit board network design with a golden spark that matches the Catppuccin Mocha theme — but there's no mechanism to display it.

## Goal

Integrate the provided splash image (`foundry-splash.png`) into the application as a startup splash screen and as branded backgrounds for empty/welcome states. The app should feel polished and visually cohesive from the moment it launches.

## Scope

### In Scope
- Copy the source image (`/home/gregg/Downloads/Industrial blueprint network design.png`) to `resources/images/foundry-splash.png`
- **Startup splash screen**: Implement a QSplashScreen shown during app initialization in `main.py`, with the Foundry name and version overlaid on the image. Dismiss when the main window is ready.
- **Welcome/empty state on Builder screen**: Display the splash image as a hero background when no project is in progress (before the wizard starts), with a "Create New Project" call-to-action overlaid
- **Empty state on History screen**: Show the splash image (scaled/dimmed) with a message like "No generation history yet" when no past runs exist
- **Empty state on Export screen**: Show the splash image with "No projects to export" when the workspace is empty
- Update `pyproject.toml` to include `resources/images/` in package data so the image ships with the wheel
- Ensure image path resolves correctly at runtime (source and installed package)
- Image scaling/cropping to fit different widget sizes using `Qt.KeepAspectRatioByExpanding` or similar

### Out of Scope
- Application window icon / taskbar icon (covered by BEAN-043)
- About dialog logo (covered by BEAN-043)
- Animated splash screen or progress bar during startup
- Multiple splash image variants (light theme, seasonal, etc.)
- Image editing or modification (use the provided image as-is)

## Acceptance Criteria

- [ ] `resources/images/foundry-splash.png` exists in the repository
- [ ] App shows a QSplashScreen with the image, app name, and version during startup
- [ ] Splash screen dismisses automatically when the main window is shown
- [ ] Builder screen displays the splash image as a welcome hero when no wizard is active
- [ ] History screen displays a branded empty state when no generation runs exist
- [ ] Export screen displays a branded empty state when no projects are available
- [ ] Image scales gracefully across different window sizes without distortion
- [ ] Overlaid text (app name, messages) is legible against the image (use semi-transparent overlay or text shadow)
- [ ] `pyproject.toml` includes `resources/images/` in package data
- [ ] Image path resolves correctly from both `uv run foundry` and installed package
- [ ] All existing tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Source image: `/home/gregg/Downloads/Industrial blueprint network design.png`
- Target location: `resources/images/foundry-splash.png`
- The image is a dark blue circuit board / network design with a golden spark in the center — matches the Catppuccin Mocha dark theme (background `#1e1e2e`, surface `#313244`).
- BEAN-043 (Add Application Logo) handles the small icon use case. This bean handles the large splash/background use case. They are independent.
- For text legibility over the image, consider a semi-transparent dark overlay (`rgba(30, 30, 46, 0.6)`) behind text, or use text with a subtle drop shadow.
- QSplashScreen is straightforward in PySide6: `splash = QSplashScreen(QPixmap(path))`, `splash.show()`, `splash.finish(main_window)`.
- For empty states, consider a reusable `BrandedEmptyState` widget that takes a message string and displays it over a scaled/dimmed version of the splash image.
