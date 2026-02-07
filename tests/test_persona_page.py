"""Tests for foundry_app.ui.screens.builder.wizard_pages.persona_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    Strictness,
    TeamConfig,
)
from foundry_app.ui.screens.builder.wizard_pages.persona_page import (
    PERSONA_DESCRIPTIONS,
    PersonaCard,
    PersonaSelectionPage,
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


def _make_library(*persona_ids: str) -> LibraryIndex:
    """Create a LibraryIndex with the given persona ids."""
    return LibraryIndex(
        library_root="/fake/library",
        personas=[_make_persona(pid) for pid in persona_ids],
    )


def _make_full_library() -> LibraryIndex:
    """Create a LibraryIndex matching the real 13-persona library."""
    return _make_library(
        "architect", "ba", "code-quality-reviewer", "compliance-risk",
        "developer", "devops-release", "integrator-merge-captain",
        "researcher-librarian", "security-engineer", "team-lead",
        "tech-qa", "technical-writer", "ux-ui-designer",
    )


# ---------------------------------------------------------------------------
# PersonaCard — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def card():
    persona = _make_persona("developer", ["impl-plan.md", "pr-desc.md"])
    c = PersonaCard(persona)
    yield c
    c.close()


class TestPersonaCardConstruction:
    def test_creates_without_error(self, card):
        assert card is not None

    def test_persona_id(self, card):
        assert card.persona_id == "developer"

    def test_initially_not_selected(self, card):
        assert card.is_selected is False

    def test_object_name(self, card):
        assert card.objectName() == "persona-card"


# ---------------------------------------------------------------------------
# PersonaCard — selection
# ---------------------------------------------------------------------------

class TestPersonaCardSelection:
    def test_select_via_property(self, card):
        card.is_selected = True
        assert card.is_selected is True

    def test_deselect_via_property(self, card):
        card.is_selected = True
        card.is_selected = False
        assert card.is_selected is False

    def test_toggled_signal_emitted_on_select(self, card):
        received = []
        card.toggled.connect(lambda pid, checked: received.append((pid, checked)))
        card.is_selected = True
        assert len(received) == 1
        assert received[0] == ("developer", True)

    def test_toggled_signal_emitted_on_deselect(self, card):
        card.is_selected = True
        received = []
        card.toggled.connect(lambda pid, checked: received.append((pid, checked)))
        card.is_selected = False
        assert len(received) == 1
        assert received[0] == ("developer", False)


# ---------------------------------------------------------------------------
# PersonaCard — to_persona_selection
# ---------------------------------------------------------------------------

class TestPersonaCardToSelection:
    def test_default_selection_values(self, card):
        sel = card.to_persona_selection()
        assert isinstance(sel, PersonaSelection)
        assert sel.id == "developer"
        assert sel.include_agent is True
        assert sel.include_templates is True
        assert sel.strictness == Strictness.STANDARD

    def test_custom_agent_unchecked(self, card):
        card._agent_check.setChecked(False)
        sel = card.to_persona_selection()
        assert sel.include_agent is False

    def test_custom_templates_unchecked(self, card):
        card._templates_check.setChecked(False)
        sel = card.to_persona_selection()
        assert sel.include_templates is False

    def test_custom_strictness_light(self, card):
        card._strictness_combo.setCurrentText("light")
        sel = card.to_persona_selection()
        assert sel.strictness == Strictness.LIGHT

    def test_custom_strictness_strict(self, card):
        card._strictness_combo.setCurrentText("strict")
        sel = card.to_persona_selection()
        assert sel.strictness == Strictness.STRICT


# ---------------------------------------------------------------------------
# PersonaCard — load_from_selection
# ---------------------------------------------------------------------------

class TestPersonaCardLoadFromSelection:
    def test_load_restores_checked(self, card):
        sel = PersonaSelection(
            id="developer",
            include_agent=False,
            include_templates=False,
            strictness=Strictness.STRICT,
        )
        card.load_from_selection(sel)
        assert card.is_selected is True
        assert card._agent_check.isChecked() is False
        assert card._templates_check.isChecked() is False
        assert card._strictness_combo.currentText() == "strict"

    def test_load_with_light_strictness(self, card):
        sel = PersonaSelection(
            id="developer",
            include_agent=True,
            include_templates=True,
            strictness=Strictness.LIGHT,
        )
        card.load_from_selection(sel)
        assert card._strictness_combo.currentText() == "light"

    def test_roundtrip_selection(self, card):
        original = PersonaSelection(
            id="developer",
            include_agent=False,
            include_templates=True,
            strictness=Strictness.STRICT,
        )
        card.load_from_selection(original)
        result = card.to_persona_selection()
        assert result.id == original.id
        assert result.include_agent == original.include_agent
        assert result.include_templates == original.include_templates
        assert result.strictness == original.strictness


# ---------------------------------------------------------------------------
# PersonaCard — unknown persona fallback
# ---------------------------------------------------------------------------

class TestPersonaCardUnknownPersona:
    def test_unknown_persona_uses_titlecased_id(self):
        persona = _make_persona("custom-role")
        card = PersonaCard(persona)
        assert card.persona_id == "custom-role"
        card.close()


# ---------------------------------------------------------------------------
# PersonaSelectionPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = PersonaSelectionPage()
    yield p
    p.close()


@pytest.fixture()
def loaded_page():
    lib = _make_full_library()
    p = PersonaSelectionPage(library_index=lib)
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_no_cards_initially(self, page):
        assert len(page.persona_cards) == 0

    def test_initially_invalid(self, page):
        assert page.is_valid() is False

    def test_selected_count_zero(self, page):
        assert page.selected_count() == 0

    def test_warning_hidden_initially(self, page):
        assert page._warning_label.isHidden() is True


# ---------------------------------------------------------------------------
# PersonaSelectionPage — load_personas
# ---------------------------------------------------------------------------

class TestLoadPersonas:
    def test_loads_all_13_personas(self, loaded_page):
        assert len(loaded_page.persona_cards) == 13

    def test_all_known_persona_ids_present(self, loaded_page):
        cards = loaded_page.persona_cards
        for pid in PERSONA_DESCRIPTIONS:
            assert pid in cards, f"Missing persona card: {pid}"

    def test_loads_via_constructor(self):
        lib = _make_library("developer", "architect")
        page = PersonaSelectionPage(library_index=lib)
        assert len(page.persona_cards) == 2
        page.close()

    def test_load_replaces_previous_personas(self, loaded_page):
        new_lib = _make_library("developer")
        loaded_page.load_personas(new_lib)
        assert len(loaded_page.persona_cards) == 1
        assert "developer" in loaded_page.persona_cards

    def test_empty_library_shows_no_cards(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_personas(lib)
        assert len(page.persona_cards) == 0


# ---------------------------------------------------------------------------
# PersonaSelectionPage — selection and validation
# ---------------------------------------------------------------------------

class TestPageSelection:
    def test_select_one_persona(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        assert loaded_page.selected_count() == 1
        assert loaded_page.is_valid() is True

    def test_select_multiple_personas(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["architect"].is_selected = True
        loaded_page.persona_cards["tech-qa"].is_selected = True
        assert loaded_page.selected_count() == 3

    def test_deselect_all_makes_invalid(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["developer"].is_selected = False
        assert loaded_page.is_valid() is False

    def test_selection_changed_signal_emitted(self, loaded_page):
        received = []
        loaded_page.selection_changed.connect(lambda: received.append(True))
        loaded_page.persona_cards["developer"].is_selected = True
        assert len(received) >= 1

    def test_warning_shown_after_deselect_all(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["developer"].is_selected = False
        assert loaded_page._warning_label.isHidden() is False

    def test_warning_hidden_when_persona_selected(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        assert loaded_page._warning_label.isHidden() is True


# ---------------------------------------------------------------------------
# PersonaSelectionPage — get_team_config
# ---------------------------------------------------------------------------

class TestGetTeamConfig:
    def test_empty_when_none_selected(self, loaded_page):
        config = loaded_page.get_team_config()
        assert isinstance(config, TeamConfig)
        assert len(config.personas) == 0

    def test_contains_selected_personas(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["architect"].is_selected = True
        config = loaded_page.get_team_config()
        ids = {p.id for p in config.personas}
        assert ids == {"developer", "architect"}

    def test_respects_per_persona_config(self, loaded_page):
        card = loaded_page.persona_cards["developer"]
        card.is_selected = True
        card._agent_check.setChecked(False)
        card._strictness_combo.setCurrentText("strict")
        config = loaded_page.get_team_config()
        sel = config.personas[0]
        assert sel.id == "developer"
        assert sel.include_agent is False
        assert sel.strictness == Strictness.STRICT

    def test_unselected_personas_excluded(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        config = loaded_page.get_team_config()
        ids = [p.id for p in config.personas]
        assert "architect" not in ids


# ---------------------------------------------------------------------------
# PersonaSelectionPage — set_team_config (round-trip)
# ---------------------------------------------------------------------------

class TestSetTeamConfig:
    def test_restores_selections(self, loaded_page):
        config = TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="tech-qa", strictness=Strictness.STRICT),
        ])
        loaded_page.set_team_config(config)
        assert loaded_page.persona_cards["developer"].is_selected is True
        assert loaded_page.persona_cards["tech-qa"].is_selected is True
        assert loaded_page.persona_cards["architect"].is_selected is False

    def test_restores_strictness(self, loaded_page):
        config = TeamConfig(personas=[
            PersonaSelection(id="developer", strictness=Strictness.LIGHT),
        ])
        loaded_page.set_team_config(config)
        card = loaded_page.persona_cards["developer"]
        assert card._strictness_combo.currentText() == "light"

    def test_restores_agent_and_templates(self, loaded_page):
        config = TeamConfig(personas=[
            PersonaSelection(
                id="developer",
                include_agent=False,
                include_templates=False,
            ),
        ])
        loaded_page.set_team_config(config)
        card = loaded_page.persona_cards["developer"]
        assert card._agent_check.isChecked() is False
        assert card._templates_check.isChecked() is False

    def test_roundtrip_get_set_get(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["architect"].is_selected = True
        loaded_page.persona_cards["developer"]._strictness_combo.setCurrentText("strict")
        original = loaded_page.get_team_config()

        # Reset all
        for card in loaded_page.persona_cards.values():
            card.is_selected = False

        loaded_page.set_team_config(original)
        restored = loaded_page.get_team_config()

        assert len(restored.personas) == len(original.personas)
        orig_ids = {p.id for p in original.personas}
        rest_ids = {p.id for p in restored.personas}
        assert orig_ids == rest_ids

    def test_set_config_clears_previous(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["architect"].is_selected = True

        config = TeamConfig(personas=[
            PersonaSelection(id="tech-qa"),
        ])
        loaded_page.set_team_config(config)
        assert loaded_page.persona_cards["developer"].is_selected is False
        assert loaded_page.persona_cards["architect"].is_selected is False
        assert loaded_page.persona_cards["tech-qa"].is_selected is True

    def test_set_config_updates_warning(self, loaded_page):
        # Set a valid config
        config = TeamConfig(personas=[PersonaSelection(id="developer")])
        loaded_page.set_team_config(config)
        assert loaded_page._warning_label.isHidden() is True

        # Set an empty config
        loaded_page.set_team_config(TeamConfig())
        assert loaded_page._warning_label.isHidden() is False


# ---------------------------------------------------------------------------
# PersonaSelectionPage — template badge display
# ---------------------------------------------------------------------------

class TestTemplateBadge:
    def test_persona_with_templates_shows_badge(self):
        lib = LibraryIndex(
            library_root="/fake",
            personas=[_make_persona("developer", ["a.md", "b.md", "c.md"])],
        )
        page = PersonaSelectionPage(library_index=lib)
        assert len(page.persona_cards) == 1
        page.close()

    def test_persona_with_one_template_singular(self):
        lib = LibraryIndex(
            library_root="/fake",
            personas=[_make_persona("developer", ["a.md"])],
        )
        page = PersonaSelectionPage(library_index=lib)
        assert len(page.persona_cards) == 1
        page.close()
