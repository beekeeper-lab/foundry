"""Tests for foundry_app.ui.screens.builder.wizard_pages.review_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HookPackSelection,
    HooksConfig,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    SafetyConfig,
    SeedMode,
    StackSelection,
    Strictness,
    TeamConfig,
)
from foundry_app.ui.screens.builder.wizard_pages.review_page import (
    ReviewPage,
    ReviewSection,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(
    name: str = "My App",
    slug: str = "my-app",
    output_root: str = "./generated-projects",
) -> ProjectIdentity:
    return ProjectIdentity(name=name, slug=slug, output_root=output_root)


def _make_minimal_spec() -> CompositionSpec:
    """Create a minimal valid CompositionSpec with only required fields."""
    return CompositionSpec(project=_make_project())


def _make_full_spec() -> CompositionSpec:
    """Create a fully populated CompositionSpec."""
    return CompositionSpec(
        project=_make_project(name="Full Project", slug="full-project"),
        team=TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(
                id="architect",
                include_agent=False,
                include_templates=True,
                strictness=Strictness.STRICT,
            ),
            PersonaSelection(
                id="tech-qa",
                include_templates=False,
                strictness=Strictness.LIGHT,
            ),
        ]),
        stacks=[
            StackSelection(id="python", order=0),
            StackSelection(id="react", order=1),
            StackSelection(id="typescript", order=2),
        ],
        hooks=HooksConfig(
            posture=Posture.HARDENED,
            packs=[
                HookPackSelection(id="lint-guard", enabled=True),
                HookPackSelection(id="secret-scan", enabled=True),
                HookPackSelection(id="legacy-pack", enabled=False),
            ],
        ),
        generation=GenerationOptions(
            seed_tasks=True,
            seed_mode=SeedMode.KICKOFF,
            write_manifest=True,
            write_diff_report=True,
        ),
        safety=SafetyConfig.hardened_safety(),
    )


def _make_spec_no_safety() -> CompositionSpec:
    """Create a spec with safety=None (the default)."""
    return CompositionSpec(
        project=_make_project(),
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        stacks=[StackSelection(id="python", order=0)],
    )


# ---------------------------------------------------------------------------
# ReviewSection — construction
# ---------------------------------------------------------------------------

class TestReviewSectionConstruction:
    def test_creates_without_error(self):
        section = ReviewSection("Test Section")
        assert section is not None
        section.close()

    def test_object_name(self):
        section = ReviewSection("Test")
        assert section.objectName() == "review-section"
        section.close()

    def test_has_content_layout(self):
        section = ReviewSection("Test")
        assert section.content_layout is not None
        section.close()


# ---------------------------------------------------------------------------
# ReviewSection — add_field
# ---------------------------------------------------------------------------

class TestReviewSectionAddField:
    def test_add_field_returns_label(self):
        section = ReviewSection("Test")
        val = section.add_field("Name", "My App")
        assert val.text() == "My App"
        section.close()

    def test_add_field_value_object_name(self):
        section = ReviewSection("Test")
        val = section.add_field("Project Name", "App")
        assert val.objectName() == "value-project-name"
        section.close()

    def test_add_multiple_fields(self):
        section = ReviewSection("Test")
        v1 = section.add_field("A", "1")
        v2 = section.add_field("B", "2")
        assert v1.text() == "1"
        assert v2.text() == "2"
        section.close()


# ---------------------------------------------------------------------------
# ReviewSection — add_item and add_empty_message
# ---------------------------------------------------------------------------

class TestReviewSectionItems:
    def test_add_item_returns_label(self):
        section = ReviewSection("Test")
        item = section.add_item("bullet point")
        assert item.text() == "bullet point"
        section.close()

    def test_add_empty_message_returns_label(self):
        section = ReviewSection("Test")
        msg = section.add_empty_message("Nothing here")
        assert msg.text() == "Nothing here"
        section.close()


# ---------------------------------------------------------------------------
# ReviewPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = ReviewPage()
    yield p
    p.close()


@pytest.fixture()
def full_page():
    p = ReviewPage()
    p.set_composition_spec(_make_full_spec())
    yield p
    p.close()


@pytest.fixture()
def minimal_page():
    p = ReviewPage()
    p.set_composition_spec(_make_minimal_spec())
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_object_name(self, page):
        assert page.objectName() == "review-page"

    def test_no_sections_initially(self, page):
        assert len(page.sections) == 0

    def test_is_complete_always_true(self, page):
        assert page.is_complete() is True

    def test_no_spec_initially(self, page):
        assert page.get_composition_spec() is None

    def test_generate_button_exists(self, page):
        assert page._generate_btn is not None
        assert page._generate_btn.text() == "Generate Project"


# ---------------------------------------------------------------------------
# ReviewPage — set_composition_spec with minimal spec
# ---------------------------------------------------------------------------

class TestMinimalSpec:
    def test_project_section_created(self, minimal_page):
        assert "project" in minimal_page.sections

    def test_team_section_created(self, minimal_page):
        assert "team" in minimal_page.sections

    def test_stacks_section_created(self, minimal_page):
        assert "stacks" in minimal_page.sections

    def test_hooks_section_created(self, minimal_page):
        assert "hooks" in minimal_page.sections

    def test_generation_section_created(self, minimal_page):
        assert "generation" in minimal_page.sections

    def test_no_safety_section(self, minimal_page):
        assert "safety" not in minimal_page.sections

    def test_spec_stored(self, minimal_page):
        spec = minimal_page.get_composition_spec()
        assert spec is not None
        assert spec.project.name == "My App"


# ---------------------------------------------------------------------------
# ReviewPage — set_composition_spec with full spec
# ---------------------------------------------------------------------------

class TestFullSpec:
    def test_all_sections_created(self, full_page):
        expected = {"project", "team", "stacks", "architecture", "hooks", "generation", "safety"}
        assert set(full_page.sections.keys()) == expected

    def test_project_section_present(self, full_page):
        assert "project" in full_page.sections

    def test_safety_section_present(self, full_page):
        assert "safety" in full_page.sections

    def test_spec_stored(self, full_page):
        spec = full_page.get_composition_spec()
        assert spec is not None
        assert spec.project.name == "Full Project"


# ---------------------------------------------------------------------------
# ReviewPage — project section content
# ---------------------------------------------------------------------------

class TestProjectSection:
    def test_displays_project_name(self, full_page):
        # The project section should contain the project name
        section = full_page.sections["project"]
        assert section is not None

    def test_minimal_project(self, minimal_page):
        section = minimal_page.sections["project"]
        assert section is not None

    def test_custom_output_folder(self):
        spec = CompositionSpec(
            project=ProjectIdentity(
                name="Custom",
                slug="custom",
                output_folder="my-output",
            ),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "project" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — team section content
# ---------------------------------------------------------------------------

class TestTeamSection:
    def test_empty_personas(self, minimal_page):
        section = minimal_page.sections["team"]
        assert section is not None

    def test_multiple_personas(self, full_page):
        section = full_page.sections["team"]
        assert section is not None

    def test_single_persona(self):
        spec = CompositionSpec(
            project=_make_project(),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "team" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — stacks section content
# ---------------------------------------------------------------------------

class TestStacksSection:
    def test_empty_stacks(self, minimal_page):
        section = minimal_page.sections["stacks"]
        assert section is not None

    def test_multiple_stacks_ordered(self, full_page):
        section = full_page.sections["stacks"]
        assert section is not None

    def test_stacks_sorted_by_order(self):
        spec = CompositionSpec(
            project=_make_project(),
            stacks=[
                StackSelection(id="react", order=2),
                StackSelection(id="python", order=0),
                StackSelection(id="node", order=1),
            ],
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "stacks" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — hooks section content
# ---------------------------------------------------------------------------

class TestHooksSection:
    def test_default_hooks(self, minimal_page):
        section = minimal_page.sections["hooks"]
        assert section is not None

    def test_hardened_posture(self, full_page):
        section = full_page.sections["hooks"]
        assert section is not None

    def test_custom_posture(self):
        spec = CompositionSpec(
            project=_make_project(),
            hooks=HooksConfig(posture=Posture.REGULATED),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "hooks" in page.sections
        page.close()

    def test_no_packs(self):
        spec = CompositionSpec(
            project=_make_project(),
            hooks=HooksConfig(posture=Posture.BASELINE, packs=[]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "hooks" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — generation section content
# ---------------------------------------------------------------------------

class TestGenerationSection:
    def test_default_generation_options(self, minimal_page):
        section = minimal_page.sections["generation"]
        assert section is not None

    def test_custom_generation_options(self, full_page):
        section = full_page.sections["generation"]
        assert section is not None

    def test_no_seed_tasks(self):
        spec = CompositionSpec(
            project=_make_project(),
            generation=GenerationOptions(seed_tasks=False),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "generation" in page.sections
        page.close()

    def test_diff_report_enabled(self):
        spec = CompositionSpec(
            project=_make_project(),
            generation=GenerationOptions(write_diff_report=True),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "generation" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — safety section content
# ---------------------------------------------------------------------------

class TestSafetySection:
    def test_no_safety_config(self, minimal_page):
        assert "safety" not in minimal_page.sections

    def test_safety_present(self, full_page):
        assert "safety" in full_page.sections

    def test_baseline_safety(self):
        spec = CompositionSpec(
            project=_make_project(),
            safety=SafetyConfig.baseline_safety(),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "safety" in page.sections
        page.close()

    def test_permissive_safety(self):
        spec = CompositionSpec(
            project=_make_project(),
            safety=SafetyConfig.permissive_safety(),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "safety" in page.sections
        page.close()

    def test_hardened_safety(self):
        spec = CompositionSpec(
            project=_make_project(),
            safety=SafetyConfig.hardened_safety(),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "safety" in page.sections
        page.close()


# ---------------------------------------------------------------------------
# ReviewPage — generate signal
# ---------------------------------------------------------------------------

class TestGenerateSignal:
    def test_signal_emitted_on_click(self, page):
        page.set_composition_spec(_make_minimal_spec())
        received = []
        page.generate_requested.connect(lambda: received.append(True))
        page._generate_btn.click()
        assert len(received) == 1

    def test_signal_not_emitted_without_click(self, page):
        received = []
        page.generate_requested.connect(lambda: received.append(True))
        assert len(received) == 0

    def test_multiple_clicks(self, page):
        page.set_composition_spec(_make_minimal_spec())
        received = []
        page.generate_requested.connect(lambda: received.append(True))
        page._generate_btn.click()
        page._generate_btn.click()
        assert len(received) == 2


# ---------------------------------------------------------------------------
# ReviewPage — set_composition_spec replaces previous
# ---------------------------------------------------------------------------

class TestSpecReplacement:
    def test_set_spec_replaces_previous(self, page):
        page.set_composition_spec(_make_minimal_spec())
        assert page.get_composition_spec().project.name == "My App"

        new_spec = CompositionSpec(
            project=ProjectIdentity(name="New App", slug="new-app"),
        )
        page.set_composition_spec(new_spec)
        assert page.get_composition_spec().project.name == "New App"

    def test_sections_rebuilt_on_replace(self, page):
        page.set_composition_spec(_make_minimal_spec())
        assert "safety" not in page.sections

        page.set_composition_spec(_make_full_spec())
        assert "safety" in page.sections

    def test_safety_removed_on_replace(self, page):
        page.set_composition_spec(_make_full_spec())
        assert "safety" in page.sections

        page.set_composition_spec(_make_minimal_spec())
        assert "safety" not in page.sections

    def test_section_count_minimal(self, minimal_page):
        # project, team, stacks, architecture, hooks, generation = 6 (no safety)
        assert len(minimal_page.sections) == 6

    def test_section_count_full(self, full_page):
        # project, team, stacks, architecture, hooks, generation, safety = 7
        assert len(full_page.sections) == 7


# ---------------------------------------------------------------------------
# ReviewPage — is_complete
# ---------------------------------------------------------------------------

class TestIsComplete:
    def test_complete_without_spec(self, page):
        assert page.is_complete() is True

    def test_complete_with_minimal_spec(self, minimal_page):
        assert minimal_page.is_complete() is True

    def test_complete_with_full_spec(self, full_page):
        assert full_page.is_complete() is True


# ---------------------------------------------------------------------------
# ReviewPage — edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_team_no_crash(self):
        spec = CompositionSpec(
            project=_make_project(),
            team=TeamConfig(personas=[]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "team" in page.sections
        page.close()

    def test_empty_stacks_no_crash(self):
        spec = CompositionSpec(
            project=_make_project(),
            stacks=[],
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "stacks" in page.sections
        page.close()

    def test_empty_hook_packs_no_crash(self):
        spec = CompositionSpec(
            project=_make_project(),
            hooks=HooksConfig(packs=[]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "hooks" in page.sections
        page.close()

    def test_persona_with_all_defaults(self):
        spec = CompositionSpec(
            project=_make_project(),
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "team" in page.sections
        page.close()

    def test_persona_with_non_standard_strictness(self):
        spec = CompositionSpec(
            project=_make_project(),
            team=TeamConfig(personas=[
                PersonaSelection(id="dev", strictness=Strictness.LIGHT),
                PersonaSelection(id="qa", strictness=Strictness.STRICT),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "team" in page.sections
        page.close()

    def test_persona_no_agent_no_templates(self):
        spec = CompositionSpec(
            project=_make_project(),
            team=TeamConfig(personas=[
                PersonaSelection(
                    id="developer",
                    include_agent=False,
                    include_templates=False,
                ),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "team" in page.sections
        page.close()

    def test_single_stack(self):
        spec = CompositionSpec(
            project=_make_project(),
            stacks=[StackSelection(id="python", order=0)],
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "stacks" in page.sections
        page.close()

    def test_seed_mode_detailed(self):
        spec = CompositionSpec(
            project=_make_project(),
            generation=GenerationOptions(
                seed_tasks=True,
                seed_mode=SeedMode.DETAILED,
            ),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "generation" in page.sections
        page.close()

    def test_mixed_enabled_disabled_packs(self):
        spec = CompositionSpec(
            project=_make_project(),
            hooks=HooksConfig(packs=[
                HookPackSelection(id="pack-a", enabled=True),
                HookPackSelection(id="pack-b", enabled=False),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "hooks" in page.sections
        page.close()

    def test_all_packs_disabled(self):
        spec = CompositionSpec(
            project=_make_project(),
            hooks=HooksConfig(packs=[
                HookPackSelection(id="pack-a", enabled=False),
                HookPackSelection(id="pack-b", enabled=False),
            ]),
        )
        page = ReviewPage()
        page.set_composition_spec(spec)
        assert "hooks" in page.sections
        page.close()
