# Task 03: Source Directory Implementation

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | 02 |

## Goal

Implement configurable source directories in the model, safety service, CLI, and wizard UI.

## Inputs

- `ai/beans/BEAN-004-safety-source-dirs/bean.md` — problem statement
- `ai/outputs/ba/bean-004-source-dirs-requirements.md` — requirements
- `ai/outputs/architect/bean-004-source-dirs-design.md` — design spec
- `foundry_app/core/models.py` — models to modify
- `foundry_app/services/safety.py` — service to modify
- `foundry_app/ui/screens/builder/wizard_pages/safety_page.py` — UI to modify

## Acceptance Criteria

- [ ] `FileSystemPolicy` (or appropriate model) has a new field for editable directories
- [ ] `safety_to_settings_json()` uses the configured dirs instead of hardcoded `src/**`
- [ ] Default behavior unchanged when field is omitted (falls back to `["src/**"]`)
- [ ] Wizard Safety page has a UI control for entering source directories
- [ ] Existing composition YAMLs without the new field still parse and work
- [ ] Tests written for: custom dirs, default fallback, multiple dirs, empty list, round-trip YAML
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — clean
- [ ] Implementation notes written to `ai/outputs/developer/bean-004-source-dirs-notes.md`

## Definition of Done

Code changes complete, tests pass, lint clean, implementation notes written. Ready for Tech-QA.
