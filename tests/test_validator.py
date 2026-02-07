"""Tests for foundry_app.services.validator: composition and library checks."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    DestructiveOpsPolicy,
    GitPolicy,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    SafetyConfig,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.validator import (
    run_pre_generation_validation,
    validate_composition,
    validate_safety_config,
)

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def _make_spec(
    personas: list[str] | None = None,
    stacks: list[str] | None = None,
    name: str = "Test",
    slug: str = "test",
) -> CompositionSpec:
    """Helper to build a minimal CompositionSpec."""
    if personas is None:
        personas = ["team-lead", "developer"]
    if stacks is None:
        stacks = ["python"]
    return CompositionSpec(
        project=ProjectIdentity(name=name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=[PersonaSelection(id=pid) for pid in personas]),
        hooks=HooksConfig(),
    )


# -- Full pre-generation validation -------------------------------------------


def test_valid_composition_passes():
    """A well-formed spec with real personas and stacks should pass validation."""
    spec = _make_spec(personas=["team-lead", "developer"], stacks=["python"])
    result = run_pre_generation_validation(spec, LIBRARY_ROOT)
    assert result.is_valid, f"Unexpected errors: {result.errors}"
    assert len(result.errors) == 0


def test_missing_persona_errors():
    """A spec referencing a nonexistent persona should produce errors."""
    spec = _make_spec(personas=["nonexistent-persona"], stacks=["python"])
    result = run_pre_generation_validation(spec, LIBRARY_ROOT)
    assert not result.is_valid
    assert any("nonexistent-persona" in e for e in result.errors)


def test_missing_stack_warns_or_errors():
    """A spec referencing a nonexistent stack should produce errors or warnings."""
    spec = _make_spec(personas=["team-lead"], stacks=["nonexistent-stack"])
    result = run_pre_generation_validation(spec, LIBRARY_ROOT)
    all_messages = result.errors + result.warnings
    assert any("nonexistent-stack" in m for m in all_messages)


def test_empty_team_errors():
    """A spec with no personas should fail validation."""
    spec = _make_spec(personas=[], stacks=["python"])
    result = run_pre_generation_validation(spec, LIBRARY_ROOT)
    assert not result.is_valid
    assert any("persona" in e.lower() for e in result.errors)


# -- validate_composition (structural checks only) ----------------------------


def test_validate_composition_valid():
    """validate_composition accepts a structurally complete spec."""
    spec = _make_spec()
    result = validate_composition(spec)
    assert result.is_valid


def test_validate_composition_empty_team():
    """validate_composition rejects a spec with no personas."""
    spec = _make_spec(personas=[])
    result = validate_composition(spec)
    assert not result.is_valid
    assert any("persona" in e.lower() for e in result.errors)


def test_validate_composition_empty_name():
    """validate_composition rejects a spec with a blank project name."""
    spec = _make_spec(name="", slug="test")
    result = validate_composition(spec)
    assert not result.is_valid
    assert any("name" in e.lower() for e in result.errors)


def test_validate_composition_no_stacks_warns():
    """validate_composition warns (but does not error) when no stacks are selected."""
    spec = _make_spec(stacks=[])
    result = validate_composition(spec)
    # No stacks is a warning, not an error
    assert any("stack" in w.lower() for w in result.warnings)


# -- Strictness modes ---------------------------------------------------------


def test_strictness_light_no_stacks_silent():
    """Light mode suppresses the 'no stacks' warning entirely."""
    spec = _make_spec(stacks=[])
    result = validate_composition(spec, strictness="light")
    assert result.is_valid
    assert not any("stack" in w.lower() for w in result.warnings)


def test_strictness_strict_no_stacks_is_error():
    """Strict mode promotes 'no stacks' from warning to error."""
    spec = _make_spec(stacks=[])
    result = validate_composition(spec, strictness="strict")
    assert not result.is_valid
    assert any("stack" in e.lower() for e in result.errors)


def test_strictness_standard_is_default():
    """Default (standard) gives a warning for no stacks, not an error."""
    spec = _make_spec(stacks=[])
    result = validate_composition(spec)
    assert result.is_valid
    assert any("stack" in w.lower() for w in result.warnings)


def test_strictness_light_skips_template_refs():
    """Light mode skips template reference checks entirely."""
    spec = _make_spec(personas=["team-lead"], stacks=["python"])
    from foundry_app.services.validator import validate_template_references
    result = validate_template_references(spec, LIBRARY_ROOT, strictness="light")
    assert result.is_valid
    assert len(result.warnings) == 0


def test_strictness_propagates_through_full_validation():
    """run_pre_generation_validation passes strictness to sub-validators."""
    spec = _make_spec(personas=["team-lead"], stacks=[])
    # Strict: no stacks becomes an error
    result = run_pre_generation_validation(spec, LIBRARY_ROOT, strictness="strict")
    assert not result.is_valid
    assert any("stack" in e.lower() for e in result.errors)
    # Light: no stacks is silent
    result = run_pre_generation_validation(spec, LIBRARY_ROOT, strictness="light")
    assert result.is_valid


# -- Safety config validation --------------------------------------------------


def test_safety_permissive_warns():
    """validate_safety_config should warn when preset is permissive."""
    spec = _make_spec()
    spec.safety = SafetyConfig(preset="permissive")
    result = validate_safety_config(spec)
    assert result.is_valid  # warnings only, no errors
    assert any("permissive" in w.lower() for w in result.warnings)


def test_safety_contradictory_git_errors():
    """validate_safety_config should error if force-push allowed but push denied."""
    spec = _make_spec()
    spec.safety = SafetyConfig(
        git=GitPolicy(allow_push=False, allow_force_push=True)
    )
    result = validate_safety_config(spec)
    assert not result.is_valid
    assert any("contradictory" in e.lower() for e in result.errors)


def test_safety_all_destructive_warns():
    """validate_safety_config should warn when all destructive ops are allowed."""
    spec = _make_spec()
    spec.safety = SafetyConfig(
        destructive=DestructiveOpsPolicy(
            allow_rm_rf=True,
            allow_reset_hard=True,
            allow_clean=True,
        )
    )
    result = validate_safety_config(spec)
    assert result.is_valid  # warnings only
    assert any("destructive" in w.lower() for w in result.warnings)


def test_safety_baseline_no_warnings():
    """validate_safety_config should not warn for a baseline config."""
    from foundry_app.services.safety import baseline_safety

    spec = _make_spec()
    spec.safety = baseline_safety()
    result = validate_safety_config(spec)
    assert result.is_valid
    assert len(result.warnings) == 0


def test_safety_validation_in_pre_generation():
    """run_pre_generation_validation should include safety validation results."""
    spec = _make_spec(personas=["team-lead"], stacks=["python"])
    spec.safety = SafetyConfig(preset="permissive")
    result = run_pre_generation_validation(spec, LIBRARY_ROOT)
    # Should still pass (safety issues are warnings)
    assert result.is_valid
    assert any("permissive" in w.lower() for w in result.warnings)
