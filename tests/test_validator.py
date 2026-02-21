"""Tests for foundry_app.services.validator — pre-generation validation."""

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseInfo,
    ExpertiseSelection,
    HookPackInfo,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    Severity,
    Strictness,
    TeamConfig,
    ValidationResult,
)
from foundry_app.services.validator import run_pre_generation_validation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_library(**kwargs) -> LibraryIndex:
    """Build a LibraryIndex with sensible defaults."""
    defaults = dict(
        library_root="/fake/library",
        personas=[
            PersonaInfo(id="developer", path="/fake/library/personas/developer",
                        has_persona_md=True, has_outputs_md=True, has_prompts_md=True,
                        templates=["task.md"]),
            PersonaInfo(id="architect", path="/fake/library/personas/architect",
                        has_persona_md=True),
            PersonaInfo(id="tech-qa", path="/fake/library/personas/tech-qa",
                        has_persona_md=True),
        ],
        expertise=[
            ExpertiseInfo(id="python", path="/fake/library/stacks/python",
                      files=["conventions.md", "tools.md", "patterns.md"]),
            ExpertiseInfo(id="react", path="/fake/library/stacks/react",
                      files=["conventions.md"]),
        ],
        hook_packs=[
            HookPackInfo(id="pre-commit-lint", path="/fake/library/claude/hooks/pre-commit-lint.md",
                         files=["pre-commit-lint.md"]),
            HookPackInfo(id="security-scan", path="/fake/library/claude/hooks/security-scan.md",
                         files=["security-scan.md"]),
        ],
    )
    defaults.update(kwargs)
    return LibraryIndex(**defaults)


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


# ---------------------------------------------------------------------------
# Valid composition — no issues expected
# ---------------------------------------------------------------------------


class TestValidComposition:

    def test_valid_spec_passes(self):
        result = run_pre_generation_validation(_make_spec(), _make_library())
        assert result.is_valid
        assert result.errors == []

    def test_valid_spec_with_multiple_personas_and_expertise(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python"), ExpertiseSelection(id="react")],
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="architect"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid

    def test_valid_spec_with_hook_packs(self):
        spec = _make_spec(
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid


# ---------------------------------------------------------------------------
# Missing references — errors expected
# ---------------------------------------------------------------------------


class TestMissingReferences:

    def test_missing_persona_is_error(self):
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-persona"
        assert "nonexistent" in result.errors[0].message

    def test_missing_expertise_is_error(self):
        spec = _make_spec(expertise=[ExpertiseSelection(id="cobol")])
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-expertise"
        assert "cobol" in result.errors[0].message

    def test_missing_hook_pack_is_error(self):
        spec = _make_spec(
            hooks=HooksConfig(packs=[HookPackSelection(id="nonexistent-hook")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert result.errors[0].code == "missing-hook-pack"

    def test_multiple_missing_references(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="cobol")],
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
            hooks=HooksConfig(packs=[HookPackSelection(id="bad-hook")]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        error_codes = {e.code for e in result.errors}
        assert "missing-persona" in error_codes
        assert "missing-expertise" in error_codes
        assert "missing-hook-pack" in error_codes


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


class TestWarnings:

    def test_no_personas_is_warning(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid  # warnings don't block
        assert any(m.code == "no-personas" for m in result.warnings)

    def test_persona_without_persona_md_is_warning(self):
        library = _make_library(personas=[
            PersonaInfo(id="bare", path="/fake/library/personas/bare",
                        has_persona_md=False),
        ])
        spec = _make_spec(team=TeamConfig(personas=[PersonaSelection(id="bare")]))
        result = run_pre_generation_validation(spec, library)
        assert result.is_valid
        assert any(m.code == "persona-no-persona-md" for m in result.warnings)

    def test_expertise_with_no_files_is_warning(self):
        library = _make_library(expertise=[
            ExpertiseInfo(id="empty-stack", path="/fake/library/stacks/empty-stack", files=[]),
        ])
        spec = _make_spec(expertise=[ExpertiseSelection(id="empty-stack")])
        result = run_pre_generation_validation(spec, library)
        assert result.is_valid
        assert any(m.code == "expertise-no-files" for m in result.warnings)

    def test_duplicate_persona_is_warning(self):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="developer"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "duplicate-persona" for m in result.warnings)

    def test_duplicate_expertise_is_warning(self):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python"), ExpertiseSelection(id="python")],
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "duplicate-expertise" for m in result.warnings)


# ---------------------------------------------------------------------------
# Info messages
# ---------------------------------------------------------------------------


class TestInfoMessages:

    def test_no_expertise_is_info(self):
        spec = _make_spec(expertise=[])
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        assert any(m.code == "no-expertise" for m in result.infos)


# ---------------------------------------------------------------------------
# Strictness levels
# ---------------------------------------------------------------------------


class TestStrictnessLight:

    def test_warnings_become_info_in_light_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.LIGHT,
        )
        assert result.is_valid
        assert result.warnings == []
        # "no-personas" should now be info, not warning
        assert any(m.code == "no-personas" for m in result.infos)

    def test_errors_remain_errors_in_light_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[PersonaSelection(id="missing")]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.LIGHT,
        )
        assert not result.is_valid
        assert result.errors[0].code == "missing-persona"


class TestStrictnessStandard:

    def test_standard_is_default(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert any(m.severity == Severity.WARNING for m in result.messages)

    def test_standard_keeps_warnings_as_warnings(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STANDARD,
        )
        assert any(m.code == "no-personas" and m.severity == Severity.WARNING
                    for m in result.messages)


class TestStrictnessStrict:

    def test_warnings_become_errors_in_strict_mode(self):
        spec = _make_spec(team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STRICT,
        )
        assert not result.is_valid
        assert any(m.code == "no-personas" for m in result.errors)
        assert result.warnings == []

    def test_info_stays_info_in_strict_mode(self):
        spec = _make_spec(expertise=[])
        result = run_pre_generation_validation(
            spec, _make_library(), strictness=Strictness.STRICT,
        )
        assert any(m.code == "no-expertise" and m.severity == Severity.INFO
                    for m in result.messages)


# ---------------------------------------------------------------------------
# ValidationResult model
# ---------------------------------------------------------------------------


class TestValidationResultModel:

    def test_empty_result_is_valid(self):
        result = ValidationResult()
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []
        assert result.infos == []

    def test_result_categorizes_messages(self):
        from foundry_app.core.models import ValidationMessage
        result = ValidationResult(messages=[
            ValidationMessage(severity=Severity.ERROR, code="e1", message="err"),
            ValidationMessage(severity=Severity.WARNING, code="w1", message="warn"),
            ValidationMessage(severity=Severity.INFO, code="i1", message="info"),
        ])
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.infos) == 1
        assert not result.is_valid


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_empty_library_all_references_fail(self):
        library = LibraryIndex(library_root="/empty")
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python")],
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = run_pre_generation_validation(spec, library)
        assert not result.is_valid
        assert len(result.errors) == 3

    def test_minimal_spec_no_team_no_expertise(self):
        spec = _make_spec(expertise=[], team=TeamConfig(personas=[]))
        result = run_pre_generation_validation(spec, _make_library())
        assert result.is_valid
        # Should have info about no expertise and warning about no personas
        codes = {m.code for m in result.messages}
        assert "no-expertise" in codes
        assert "no-personas" in codes

    def test_mixed_valid_and_invalid_personas(self):
        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
                PersonaSelection(id="nonexistent"),
            ]),
        )
        result = run_pre_generation_validation(spec, _make_library())
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].code == "missing-persona"
