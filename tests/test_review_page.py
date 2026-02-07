"""Tests for foundry_app.ui.screens.builder.wizard_pages.review_page."""

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from foundry_app.core.models import (
    CompositionSpec,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    Severity,
    StackInfo,
    StackSelection,
    Strictness,
    TeamConfig,
)
from foundry_app.ui.screens.builder.wizard_pages.review_page import (
    SEVERITY_ICONS,
    SEVERITY_STYLES,
    ReviewPage,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_persona(pid: str, templates: list[str] | None = None) -> PersonaInfo:
    """Create a minimal PersonaInfo for testing."""
    return PersonaInfo(
        id=pid,
        path=f"/fake/personas/{pid}",
        has_persona_md=True,
        has_outputs_md=True,
        has_prompts_md=True,
        templates=templates or [],
    )


def _make_stack(sid: str, files: list[str] | None = None) -> StackInfo:
    """Create a minimal StackInfo for testing."""
    return StackInfo(
        id=sid,
        path=f"/fake/stacks/{sid}",
        files=files or ["conventions.md"],
    )


def _make_library(
    persona_ids: list[str] | None = None,
    stack_ids: list[str] | None = None,
) -> LibraryIndex:
    """Create a LibraryIndex with given personas and stacks."""
    return LibraryIndex(
        library_root="/fake/library",
        personas=[_make_persona(pid) for pid in (persona_ids or [])],
        stacks=[_make_stack(sid) for sid in (stack_ids or [])],
    )


def _make_spec(
    name: str = "Test Project",
    slug: str = "test-project",
    persona_ids: list[str] | None = None,
    stack_ids: list[str] | None = None,
    posture: Posture = Posture.BASELINE,
) -> CompositionSpec:
    """Create a minimal CompositionSpec for testing."""
    personas = [PersonaSelection(id=pid) for pid in (persona_ids or [])]
    stacks = [StackSelection(id=sid, order=i) for i, sid in enumerate(stack_ids or [])]
    return CompositionSpec(
        project=ProjectIdentity(name=name, slug=slug),
        team=TeamConfig(personas=personas),
        stacks=stacks,
        hooks=HooksConfig(posture=posture),
    )


def _make_valid_spec_and_library() -> tuple[CompositionSpec, LibraryIndex]:
    """Create a spec + library pair that passes validation."""
    spec = _make_spec(
        persona_ids=["developer", "architect"],
        stack_ids=["python", "react"],
    )
    library = _make_library(
        persona_ids=["developer", "architect", "tech-qa"],
        stack_ids=["python", "react", "typescript"],
    )
    return spec, library


def _find_labels(widget, text_contains: str) -> list[QLabel]:
    """Find all QLabel children whose text contains the given substring."""
    return [
        child for child in widget.findChildren(QLabel)
        if text_contains in child.text()
    ]


# ---------------------------------------------------------------------------
# ReviewPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = ReviewPage()
    yield p
    p.close()


@pytest.fixture()
def loaded_page():
    spec, library = _make_valid_spec_and_library()
    p = ReviewPage()
    p.load_spec(spec, library)
    yield p
    p.close()


class TestConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_spec_initially_none(self, page):
        assert page.spec is None

    def test_library_index_initially_none(self, page):
        assert page.library_index is None

    def test_validation_result_initially_none(self, page):
        assert page.validation_result is None

    def test_initially_invalid(self, page):
        assert page.is_valid() is False

    def test_generate_button_initially_disabled(self, page):
        assert page.generate_button.isEnabled() is False

    def test_has_project_section(self, page):
        assert page.project_section is not None

    def test_has_personas_section(self, page):
        assert page.personas_section is not None

    def test_has_stacks_section(self, page):
        assert page.stacks_section is not None

    def test_has_hooks_section(self, page):
        assert page.hooks_section is not None

    def test_has_validation_section(self, page):
        assert page.validation_section is not None

    def test_generate_button_object_name(self, page):
        assert page.generate_button.objectName() == "generate-btn"


# ---------------------------------------------------------------------------
# ReviewPage — load_spec
# ---------------------------------------------------------------------------

class TestLoadSpec:
    def test_stores_spec(self, loaded_page):
        assert loaded_page.spec is not None
        assert loaded_page.spec.project.name == "Test Project"

    def test_stores_library_index(self, loaded_page):
        assert loaded_page.library_index is not None

    def test_runs_validation(self, loaded_page):
        assert loaded_page.validation_result is not None

    def test_valid_spec_enables_generate(self, loaded_page):
        assert loaded_page.generate_button.isEnabled() is True

    def test_reload_replaces_spec(self, loaded_page):
        new_spec = _make_spec(name="New Project", slug="new-project",
                              persona_ids=["developer"], stack_ids=["python"])
        new_lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        loaded_page.load_spec(new_spec, new_lib)
        assert loaded_page.spec.project.name == "New Project"


# ---------------------------------------------------------------------------
# ReviewPage — project section display
# ---------------------------------------------------------------------------

class TestProjectSection:
    def test_shows_project_name(self, loaded_page):
        labels = _find_labels(loaded_page.project_section, "Test Project")
        assert len(labels) >= 1

    def test_shows_project_slug(self, loaded_page):
        labels = _find_labels(loaded_page.project_section, "test-project")
        assert len(labels) >= 1

    def test_shows_output_path(self, loaded_page):
        labels = _find_labels(loaded_page.project_section, "generated-projects")
        assert len(labels) >= 1

    def test_shows_name_label(self, loaded_page):
        labels = _find_labels(loaded_page.project_section, "Name:")
        assert len(labels) >= 1

    def test_shows_slug_label(self, loaded_page):
        labels = _find_labels(loaded_page.project_section, "Slug:")
        assert len(labels) >= 1


# ---------------------------------------------------------------------------
# ReviewPage — personas section display
# ---------------------------------------------------------------------------

class TestPersonasSection:
    def test_shows_persona_count(self, loaded_page):
        labels = _find_labels(loaded_page.personas_section, "2 personas")
        assert len(labels) >= 1

    def test_shows_developer_persona(self, loaded_page):
        labels = _find_labels(loaded_page.personas_section, "developer")
        assert len(labels) >= 1

    def test_shows_architect_persona(self, loaded_page):
        labels = _find_labels(loaded_page.personas_section, "architect")
        assert len(labels) >= 1

    def test_no_personas_shows_message(self, page):
        spec = _make_spec(persona_ids=[], stack_ids=["python"])
        lib = _make_library(stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.personas_section, "No personas selected")
        assert len(labels) >= 1

    def test_single_persona_singular_count(self, page):
        spec = _make_spec(persona_ids=["developer"], stack_ids=["python"])
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.personas_section, "1 persona")
        assert len(labels) >= 1
        # Ensure it's not "1 personas"
        labels_plural = _find_labels(page.personas_section, "1 personas")
        assert len(labels_plural) == 0

    def test_persona_with_non_standard_config(self, page):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Test", slug="test"),
            team=TeamConfig(personas=[
                PersonaSelection(
                    id="developer",
                    include_agent=False,
                    include_templates=False,
                    strictness=Strictness.STRICT,
                ),
            ]),
            stacks=[StackSelection(id="python", order=0)],
        )
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.personas_section, "no agent")
        assert len(labels) >= 1
        labels = _find_labels(page.personas_section, "no templates")
        assert len(labels) >= 1
        labels = _find_labels(page.personas_section, "strict")
        assert len(labels) >= 1


# ---------------------------------------------------------------------------
# ReviewPage — stacks section display
# ---------------------------------------------------------------------------

class TestStacksSection:
    def test_shows_stack_count(self, loaded_page):
        labels = _find_labels(loaded_page.stacks_section, "2 stacks")
        assert len(labels) >= 1

    def test_shows_python_stack(self, loaded_page):
        labels = _find_labels(loaded_page.stacks_section, "python")
        assert len(labels) >= 1

    def test_shows_react_stack(self, loaded_page):
        labels = _find_labels(loaded_page.stacks_section, "react")
        assert len(labels) >= 1

    def test_stacks_shown_in_order(self, loaded_page):
        labels = _find_labels(loaded_page.stacks_section, "1. python")
        assert len(labels) >= 1
        labels = _find_labels(loaded_page.stacks_section, "2. react")
        assert len(labels) >= 1

    def test_no_stacks_shows_message(self, page):
        spec = _make_spec(persona_ids=["developer"], stack_ids=[])
        lib = _make_library(persona_ids=["developer"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.stacks_section, "No stacks selected")
        assert len(labels) >= 1

    def test_single_stack_singular_count(self, page):
        spec = _make_spec(persona_ids=["developer"], stack_ids=["python"])
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.stacks_section, "1 stack")
        assert len(labels) >= 1
        # Ensure not "1 stacks"
        labels_plural = _find_labels(page.stacks_section, "1 stacks")
        assert len(labels_plural) == 0


# ---------------------------------------------------------------------------
# ReviewPage — hooks section display
# ---------------------------------------------------------------------------

class TestHooksSection:
    def test_shows_posture(self, loaded_page):
        labels = _find_labels(loaded_page.hooks_section, "baseline")
        assert len(labels) >= 1

    def test_shows_posture_label(self, loaded_page):
        labels = _find_labels(loaded_page.hooks_section, "Posture:")
        assert len(labels) >= 1

    def test_no_hook_packs_shows_message(self, loaded_page):
        labels = _find_labels(loaded_page.hooks_section, "No hook packs selected")
        assert len(labels) >= 1

    def test_shows_hook_packs(self, page):
        spec = _make_spec(persona_ids=["developer"], stack_ids=["python"])
        spec.hooks.packs = [
            HookPackSelection(id="safety-baseline", enabled=True),
        ]
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.hooks_section, "safety-baseline")
        assert len(labels) >= 1

    def test_disabled_pack_shows_disabled(self, page):
        spec = _make_spec(persona_ids=["developer"], stack_ids=["python"])
        spec.hooks.packs = [
            HookPackSelection(id="pack-1", enabled=False),
        ]
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.hooks_section, "(disabled)")
        assert len(labels) >= 1

    def test_hardened_posture_displayed(self, page):
        spec = _make_spec(
            persona_ids=["developer"], stack_ids=["python"],
            posture=Posture.HARDENED,
        )
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.hooks_section, "hardened")
        assert len(labels) >= 1


# ---------------------------------------------------------------------------
# ReviewPage — validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_valid_spec_passes(self, loaded_page):
        assert loaded_page.is_valid() is True
        assert loaded_page.validation_result is not None
        assert loaded_page.validation_result.is_valid is True

    def test_valid_spec_shows_all_checks_passed(self, loaded_page):
        labels = _find_labels(loaded_page.validation_section, "All checks passed")
        assert len(labels) >= 1

    def test_missing_persona_shows_error(self, page):
        spec = _make_spec(
            persona_ids=["developer", "nonexistent"],
            stack_ids=["python"],
        )
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        assert page.is_valid() is False
        labels = _find_labels(page.validation_section, "missing-persona")
        assert len(labels) >= 1

    def test_missing_stack_shows_error(self, page):
        spec = _make_spec(
            persona_ids=["developer"],
            stack_ids=["python", "nonexistent"],
        )
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        assert page.is_valid() is False
        labels = _find_labels(page.validation_section, "missing-stack")
        assert len(labels) >= 1

    def test_error_disables_generate_button(self, page):
        spec = _make_spec(
            persona_ids=["nonexistent"],
            stack_ids=["python"],
        )
        lib = _make_library(stack_ids=["python"])
        page.load_spec(spec, lib)
        assert page.generate_button.isEnabled() is False

    def test_warnings_dont_disable_generate(self, page):
        # No personas = warning, but no errors
        spec = _make_spec(persona_ids=[], stack_ids=["python"])
        lib = _make_library(stack_ids=["python"])
        page.load_spec(spec, lib)
        assert page.generate_button.isEnabled() is True

    def test_validation_summary_present(self, loaded_page):
        labels = _find_labels(loaded_page.validation_section, "0 errors")
        assert len(labels) >= 1

    def test_validation_summary_with_errors(self, page):
        spec = _make_spec(
            persona_ids=["nonexistent"],
            stack_ids=["nonexistent"],
        )
        lib = _make_library()
        page.load_spec(spec, lib)
        # Should have errors for missing persona and stack
        result = page.validation_result
        assert result is not None
        assert len(result.errors) >= 2

    def test_reload_reruns_validation(self, loaded_page):
        assert loaded_page.is_valid() is True
        # Load an invalid spec
        spec = _make_spec(persona_ids=["bad"], stack_ids=["python"])
        lib = _make_library(stack_ids=["python"])
        loaded_page.load_spec(spec, lib)
        assert loaded_page.is_valid() is False


# ---------------------------------------------------------------------------
# ReviewPage — generate button
# ---------------------------------------------------------------------------

class TestGenerateButton:
    def test_emits_signal_on_click(self, loaded_page):
        received = []
        loaded_page.generate_requested.connect(lambda: received.append(True))
        loaded_page.generate_button.click()
        assert len(received) == 1

    def test_disabled_button_does_not_emit(self, page):
        received = []
        page.generate_requested.connect(lambda: received.append(True))
        page.generate_button.click()
        assert len(received) == 0

    def test_button_text(self, page):
        assert page.generate_button.text() == "Generate Project"


# ---------------------------------------------------------------------------
# ReviewPage — section refresh on reload
# ---------------------------------------------------------------------------

class TestRefreshOnReload:
    def test_project_section_updates_on_reload(self, loaded_page):
        new_spec = _make_spec(
            name="New Name", slug="new-name",
            persona_ids=["developer"], stack_ids=["python"],
        )
        new_lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        loaded_page.load_spec(new_spec, new_lib)
        labels = _find_labels(loaded_page.project_section, "New Name")
        assert len(labels) >= 1

    def test_personas_section_updates_on_reload(self, loaded_page):
        new_spec = _make_spec(
            persona_ids=["tech-qa"], stack_ids=["python"],
        )
        new_lib = _make_library(persona_ids=["tech-qa"], stack_ids=["python"])
        loaded_page.load_spec(new_spec, new_lib)
        labels = _find_labels(loaded_page.personas_section, "tech-qa")
        assert len(labels) >= 1
        # Old persona should be gone
        dev_labels = _find_labels(loaded_page.personas_section, "developer")
        assert len(dev_labels) == 0

    def test_stacks_section_updates_on_reload(self, loaded_page):
        new_spec = _make_spec(
            persona_ids=["developer"], stack_ids=["typescript"],
        )
        new_lib = _make_library(persona_ids=["developer"], stack_ids=["typescript"])
        loaded_page.load_spec(new_spec, new_lib)
        labels = _find_labels(loaded_page.stacks_section, "typescript")
        assert len(labels) >= 1

    def test_old_project_data_cleared(self, loaded_page):
        # After reload, old data should not be present
        new_spec = _make_spec(
            name="Replacement", slug="replacement",
            persona_ids=["developer"], stack_ids=["python"],
        )
        new_lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        loaded_page.load_spec(new_spec, new_lib)
        old_name = _find_labels(loaded_page.project_section, "Test Project")
        assert len(old_name) == 0


# ---------------------------------------------------------------------------
# ReviewPage — severity styles
# ---------------------------------------------------------------------------

class TestSeverityStyles:
    def test_error_style_exists(self):
        assert Severity.ERROR in SEVERITY_STYLES

    def test_warning_style_exists(self):
        assert Severity.WARNING in SEVERITY_STYLES

    def test_info_style_exists(self):
        assert Severity.INFO in SEVERITY_STYLES

    def test_error_icon_exists(self):
        assert Severity.ERROR in SEVERITY_ICONS

    def test_warning_icon_exists(self):
        assert Severity.WARNING in SEVERITY_ICONS

    def test_info_icon_exists(self):
        assert Severity.INFO in SEVERITY_ICONS


# ---------------------------------------------------------------------------
# ReviewPage — edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_load_none_library_index(self, page):
        """Validation should fail gracefully without library index."""
        # load_spec requires both, but spec and lib can lead to empty validation
        spec = _make_spec(persona_ids=[], stack_ids=[])
        lib = LibraryIndex(library_root="/fake")
        page.load_spec(spec, lib)
        assert page.validation_result is not None

    def test_many_personas(self, page):
        """Page should handle many personas without error."""
        ids = [f"persona-{i}" for i in range(20)]
        spec = _make_spec(persona_ids=ids, stack_ids=[])
        lib = _make_library(persona_ids=ids)
        page.load_spec(spec, lib)
        labels = _find_labels(page.personas_section, "20 personas")
        assert len(labels) >= 1

    def test_many_stacks(self, page):
        """Page should handle many stacks without error."""
        ids = [f"stack-{i}" for i in range(15)]
        spec = _make_spec(persona_ids=[], stack_ids=ids)
        lib = _make_library(stack_ids=ids)
        page.load_spec(spec, lib)
        labels = _find_labels(page.stacks_section, "15 stacks")
        assert len(labels) >= 1

    def test_output_folder_override(self, page):
        """When output_folder is set, it should appear in the output path."""
        spec = CompositionSpec(
            project=ProjectIdentity(
                name="Test", slug="test",
                output_folder="custom-output",
            ),
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            stacks=[StackSelection(id="python", order=0)],
        )
        lib = _make_library(persona_ids=["developer"], stack_ids=["python"])
        page.load_spec(spec, lib)
        labels = _find_labels(page.project_section, "custom-output")
        assert len(labels) >= 1
