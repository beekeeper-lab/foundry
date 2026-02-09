# BEAN-066: Builder Wizard Screen

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-066 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The Builder tab in the main window shows a BrandedEmptyState placeholder instead of the composition wizard. Four wizard page modules already exist (`project_page.py`, `persona_page.py`, `stack_page.py`, `review_page.py`) plus two more (`architecture_page.py`, `hook_safety_page.py`), but there is no container screen that assembles them into a step-by-step wizard with navigation (Next/Back/Generate). There is also no connection from the wizard's "Generate" action to the GenerationProgressScreen, and no flow from generation completion to the ExportScreen.

## Goal

Create a `BuilderScreen` that assembles the existing wizard pages into a navigable multi-step wizard. Users can step through Project Identity, Team & Stack, Safety, and Review, then click Generate to trigger the generation pipeline. The GenerationProgressScreen shows real-time progress, and on completion the user can export or return to the builder.

## Scope

### In Scope
- Create `foundry_app/ui/screens/builder_screen.py` as the wizard container
- Assemble the existing wizard pages in order: ProjectPage -> PersonaPage -> StackPage -> ArchitecturePage -> HookSafetyPage -> ReviewPage
- Step indicator (breadcrumb or progress dots) showing current position
- Next/Back navigation buttons with validation gates between steps
- "Generate" button on the Review page that builds a CompositionSpec from wizard state
- Transition to GenerationProgressScreen when Generate is clicked
- Pass CompositionSpec to the generator service and show progress
- On generation complete: show summary with "Export" and "Back to Builder" buttons
- Wire the BuilderScreen into main_window.py (replace the Builder placeholder)
- Read library_root and workspace_root from FoundrySettings to configure the wizard
- Add tests for wizard navigation, validation gates, and generation trigger

### Out of Scope
- Modifying the individual wizard page modules (they already work)
- Modifying the generator service (BEAN-032, already complete)
- Styling the wizard (that's the style beans BEAN-048, BEAN-049, etc.)

## Acceptance Criteria

- [ ] Clicking "Builder" in the sidebar shows the wizard with the first page (Project Identity)
- [ ] Next/Back buttons navigate between wizard pages
- [ ] Next button is disabled until the current page's required fields are filled
- [ ] Step indicator shows which page the user is on
- [ ] Review page shows a summary of all selections with a "Generate" button
- [ ] Clicking Generate builds a CompositionSpec and starts the generator
- [ ] GenerationProgressScreen shows pipeline stages and progress
- [ ] On completion, user sees a summary with Export and Back to Builder options
- [ ] Wizard state resets when starting a new composition
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-057 (Settings Screen — Core Paths) for library_root to be configured.
- Depends on BEAN-060 (Wire Screens) for the main_window plumbing pattern.
- The wizard pages are in `foundry_app/ui/screens/builder/wizard_pages/`. Each page is a QWidget with fields and a `get_data()` or similar method.
- GenerationProgressScreen is in `foundry_app/ui/screens/generation_progress.py` — already complete.
- ExportScreen is in `foundry_app/ui/screens/export_screen.py` — already complete.
- The generator orchestrator is in `foundry_app/services/generator.py` — accepts a CompositionSpec and library root path.
- This is the most complex wiring bean because it involves multi-page state management, validation, and the generation pipeline trigger.
