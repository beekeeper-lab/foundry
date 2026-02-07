# Task 02: Source Directory Design Spec

| Field | Value |
|-------|-------|
| **Owner** | architect |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Design the model change, service change, and UI change for configurable source directories. Produce a design spec and ADR.

## Inputs

- `ai/beans/BEAN-004-safety-source-dirs/bean.md` — problem statement
- `ai/outputs/ba/bean-004-source-dirs-requirements.md` — refined requirements from BA
- `foundry_app/core/models.py` — FileSystemPolicy, SafetyConfig models
- `foundry_app/services/safety.py` — safety_to_settings_json() function
- `foundry_app/ui/screens/builder/wizard_pages/safety_page.py` — SafetyPage class

## Acceptance Criteria

- [ ] Design spec covers: model field name/type, safety service changes, wizard UI changes
- [ ] ADR written via `/new-adr` documenting the field naming and default behavior decision
- [ ] Backward compatibility addressed: existing compositions without the field still work
- [ ] Output written to `ai/outputs/architect/bean-004-source-dirs-design.md`

## Definition of Done

Design spec and ADR exist. Developer can implement from the spec without architectural ambiguity.
