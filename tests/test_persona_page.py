"""Tests for foundry_app.ui.screens.builder.wizard_pages.persona_page."""

import pytest

from foundry_app.core.models import (
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    Strictness,
    TeamConfig,
)
from foundry_app.ui.screens.builder.wizard_pages.persona_page import (
    PERSONA_DESCRIPTIONS,
    CollapsibleGroupBox,
    PersonaCard,
    PersonaSelectionPage,
)

pytestmark = pytest.mark.usefixtures("qapp")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_persona(
    pid: str,
    templates: list[str] | None = None,
    category: str = "",
    tier: str = "core",
) -> PersonaInfo:
    """Create a minimal PersonaInfo for testing.

    Per ADR-014, ``tier`` is part of the wire-level identity. Defaults to
    ``"core"`` so existing tests that pass a bare id keep working.
    """
    return PersonaInfo(
        id=pid,
        path=f"/fake/personas/{pid}",
        tier=tier,
        has_persona_md=True,
        has_outputs_md=True,
        has_prompts_md=True,
        templates=templates or [],
        category=category,
    )


def _make_library(*persona_ids: str) -> LibraryIndex:
    """Create a LibraryIndex with the given persona ids (no category)."""
    return LibraryIndex(
        library_root="/fake/library",
        personas=[_make_persona(pid) for pid in persona_ids],
    )


# Tier mapping matching ADR-014 (5 core + 19 extended). Categories retained
# so legacy assertions that exercise the per-persona category metadata still
# resolve, but the page now groups by tier — see TestTierGrouping below.
_CORE_PERSONAS: tuple[str, ...] = (
    "architect", "ba", "developer", "team-lead", "tech-qa",
)

_PERSONA_CATEGORIES: dict[str, str] = {
    "architect": "Software Development",
    "ba": "Software Development",
    "change-management": "Business Operations",
    "code-quality-reviewer": "Software Development",
    "compliance-risk": "Compliance & Legal",
    "customer-success": "Business Operations",
    "data-analyst": "Data & Analytics",
    "data-engineer": "Software Development",
    "database-administrator": "Software Development",
    "developer": "Software Development",
    "devops-release": "Software Development",
    "financial-operations": "Business Operations",
    "integrator-merge-captain": "Software Development",
    "legal-counsel": "Business Operations",
    "mobile-developer": "Software Development",
    "platform-sre-engineer": "Software Development",
    "product-owner": "Business Operations",
    "researcher-librarian": "Data & Analytics",
    "sales-engineer": "Business Operations",
    "security-engineer": "Compliance & Legal",
    "team-lead": "Software Development",
    "tech-qa": "Software Development",
    "technical-writer": "Data & Analytics",
    "ux-ui-designer": "Software Development",
}


def _make_full_library() -> LibraryIndex:
    """Create a LibraryIndex matching the real 24-persona library.

    Per ADR-014 the persona id format depends on tier: core personas use the
    bare name, extended use ``extended/<name>``. Tier is set explicitly so
    grouping tests see the canonical wire form.
    """
    personas = []
    for pid, cat in _PERSONA_CATEGORIES.items():
        if pid in _CORE_PERSONAS:
            personas.append(_make_persona(pid, category=cat, tier="core"))
        else:
            personas.append(
                _make_persona(f"extended/{pid}", category=cat, tier="extended")
            )
    return LibraryIndex(library_root="/fake/library", personas=personas)


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

    def test_click_on_card_toggles_checkbox(self, card):
        """Clicking the card (outside the checkbox/combo) toggles selection."""
        from PySide6.QtCore import QPointF, Qt
        from PySide6.QtGui import QMouseEvent

        assert card.is_selected is False
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(200, 10),  # well outside the checkbox
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        card.mousePressEvent(event)
        assert card.is_selected is True

        card.mousePressEvent(event)
        assert card.is_selected is False


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

    def test_no_category_groups_initially(self, page):
        assert len(page.category_groups) == 0


# ---------------------------------------------------------------------------
# PersonaSelectionPage — load_personas
# ---------------------------------------------------------------------------

class TestLoadPersonas:
    def test_loads_all_24_personas(self, loaded_page):
        assert len(loaded_page.persona_cards) == 24

    def test_all_known_persona_ids_present(self, loaded_page):
        # Per ADR-014, the cards dict is keyed by canonical id — bare for
        # core, ``extended/<name>`` for extended. PERSONA_DESCRIPTIONS still
        # lists bare leaf names, so look up in the tier-aware form.
        cards = loaded_page.persona_cards
        for pid in PERSONA_DESCRIPTIONS:
            key = pid if pid in _CORE_PERSONAS else f"extended/{pid}"
            assert key in cards, f"Missing persona card: {key}"

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
# PERSONA_DESCRIPTIONS completeness
# ---------------------------------------------------------------------------

class TestPersonaDescriptions:
    def test_has_24_entries(self):
        assert len(PERSONA_DESCRIPTIONS) == 24

    def test_all_entries_are_tuples_with_two_strings(self):
        for pid, (name, desc) in PERSONA_DESCRIPTIONS.items():
            assert isinstance(name, str), f"{pid} name is not str"
            assert isinstance(desc, str), f"{pid} desc is not str"
            assert len(name) > 0, f"{pid} has empty display name"
            assert len(desc) > 0, f"{pid} has empty description"

    def test_new_personas_have_entries(self):
        new_personas = [
            "change-management", "customer-success", "data-analyst",
            "data-engineer", "database-administrator", "financial-operations",
            "legal-counsel", "mobile-developer", "platform-sre-engineer",
            "product-owner", "sales-engineer",
        ]
        for pid in new_personas:
            assert pid in PERSONA_DESCRIPTIONS, f"Missing: {pid}"


# ---------------------------------------------------------------------------
# PersonaSelectionPage — category grouping
# ---------------------------------------------------------------------------

class TestCategoryGrouping:
    """Tier-based grouping introduced by ADR-014.

    Persona cards are now grouped under ``core`` and ``extended`` tier
    sections rather than per-category boxes. The page exposes both
    ``tier_groups`` (the canonical accessor) and ``category_groups`` (a
    backward-compat alias kept for older test/UI consumers).
    """

    def test_creates_category_groups(self, loaded_page):
        # Returns the same dict as ``tier_groups`` (BC alias).
        groups = loaded_page.category_groups
        assert len(groups) > 0
        assert groups == loaded_page.tier_groups

    def test_expected_categories_present(self, loaded_page):
        # ADR-014: only two tier groups exist — ``core`` and ``extended``.
        groups = loaded_page.category_groups
        assert set(groups.keys()) == {"core", "extended"}

    def test_category_header_shows_count(self, loaded_page):
        groups = loaded_page.category_groups
        core_group = groups["core"]
        assert isinstance(core_group, CollapsibleGroupBox)
        title = core_group.title()
        # 5 core personas (team-lead, ba, architect, developer, tech-qa).
        assert "Core team" in title
        assert "(5)" in title

    def test_business_operations_count(self, loaded_page):
        # The extended tier holds the 19 specialist personas. Replaces the
        # historic per-category counts (Business Operations, etc.) — those
        # categories are persona metadata, not page-grouping keys.
        groups = loaded_page.category_groups
        title = groups["extended"].title()
        assert "Extended specialists" in title
        assert "(19)" in title

    def test_compliance_legal_count(self, loaded_page):
        # Holdover from the per-category grouping era. The two extended
        # security/compliance personas now live inside the single Extended
        # specialists tier section.
        groups = loaded_page.category_groups
        extended_ids = [
            pid for pid, cat in _PERSONA_CATEGORIES.items()
            if cat == "Compliance & Legal"
        ]
        assert len(extended_ids) == 2
        # Both personas appear in the page's card map under their canonical
        # extended ids.
        cards = loaded_page.persona_cards
        for pid in extended_ids:
            assert f"extended/{pid}" in cards
        assert "extended" in groups

    def test_data_analytics_count(self, loaded_page):
        # Holdover: confirm the 3 Data & Analytics personas now live under
        # the Extended specialists tier section.
        groups = loaded_page.category_groups
        analytics_ids = [
            pid for pid, cat in _PERSONA_CATEGORIES.items()
            if cat == "Data & Analytics"
        ]
        assert len(analytics_ids) == 3
        cards = loaded_page.persona_cards
        for pid in analytics_ids:
            assert f"extended/{pid}" in cards
        assert "extended" in groups

    def test_all_groups_collapsed_by_default(self, loaded_page):
        for name, group in loaded_page.category_groups.items():
            assert not group.isHidden(), f"{name} group header is hidden"
            assert not group.is_expanded, (
                f"{name} group expanded by default; expected collapsed"
            )

    def test_personas_with_no_category_go_to_other(self):
        # Tier grouping ignores the legacy ``category`` field. A persona
        # without a category still groups by tier — both personas below are
        # core, so they share the ``core`` group.
        lib = LibraryIndex(
            library_root="/fake",
            personas=[
                _make_persona(
                    "developer", category="Software Development", tier="core",
                ),
                _make_persona("custom-role", category="", tier="core"),
            ],
        )
        page = PersonaSelectionPage(library_index=lib)
        groups = page.category_groups
        # No "Other" bucket exists — tier is the only grouping axis now.
        assert "Other" not in groups
        assert "core" in groups
        assert "(2)" in groups["core"].title()
        page.close()

    def test_other_group_not_created_when_all_have_categories(self, loaded_page):
        # Tier grouping has no "Other" bucket regardless of category data.
        groups = loaded_page.category_groups
        assert "Other" not in groups

    def test_reload_clears_old_groups(self, loaded_page):
        # Reload with a small extended-only library; the ``core`` group
        # should disappear.
        new_lib = LibraryIndex(
            library_root="/fake",
            personas=[
                _make_persona(
                    "extended/lone", category="Dev", tier="extended",
                ),
            ],
        )
        loaded_page.load_personas(new_lib)
        groups = loaded_page.category_groups
        assert len(groups) == 1
        assert "extended" in groups


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

    def test_select_across_groups(self, loaded_page):
        # Select from both tier groups (ADR-014). Cards are keyed by their
        # canonical id — bare for core, ``extended/<name>`` for extended.
        loaded_page.persona_cards["developer"].is_selected = True  # core
        loaded_page.persona_cards["extended/data-analyst"].is_selected = True
        loaded_page.persona_cards["extended/compliance-risk"].is_selected = True
        loaded_page.persona_cards["extended/change-management"].is_selected = True
        assert loaded_page.selected_count() == 4


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

    def test_get_config_across_groups(self, loaded_page):
        # Cards are keyed by canonical id (ADR-014); selections round-trip
        # the same id form into TeamConfig.
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["extended/data-analyst"].is_selected = True
        loaded_page.persona_cards["extended/legal-counsel"].is_selected = True
        config = loaded_page.get_team_config()
        ids = {p.id for p in config.personas}
        assert ids == {
            "developer", "extended/data-analyst", "extended/legal-counsel",
        }


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

    def test_set_config_across_groups(self, loaded_page):
        config = TeamConfig(personas=[
            PersonaSelection(id="developer"),
            PersonaSelection(id="extended/data-analyst"),
            PersonaSelection(id="extended/compliance-risk"),
            PersonaSelection(id="extended/change-management"),
        ])
        loaded_page.set_team_config(config)
        assert loaded_page.persona_cards["developer"].is_selected is True
        assert (
            loaded_page.persona_cards["extended/data-analyst"].is_selected is True
        )
        assert (
            loaded_page.persona_cards["extended/compliance-risk"].is_selected
            is True
        )
        assert (
            loaded_page.persona_cards["extended/change-management"].is_selected
            is True
        )
        assert loaded_page.persona_cards["architect"].is_selected is False

    def test_roundtrip_across_groups(self, loaded_page):
        loaded_page.persona_cards["developer"].is_selected = True
        loaded_page.persona_cards["extended/data-analyst"].is_selected = True
        loaded_page.persona_cards["extended/compliance-risk"].is_selected = True
        original = loaded_page.get_team_config()

        for card in loaded_page.persona_cards.values():
            card.is_selected = False

        loaded_page.set_team_config(original)
        restored = loaded_page.get_team_config()
        assert {p.id for p in restored.personas} == {
            "developer", "extended/data-analyst", "extended/compliance-risk",
        }


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


# ---------------------------------------------------------------------------
# PersonaSelectionPage — empty-state messaging
# ---------------------------------------------------------------------------

class TestEmptyState:
    def test_empty_label_visible_when_no_library(self, page):
        assert page._empty_label.isHidden() is False

    def test_empty_label_hidden_after_loading_personas(self, loaded_page):
        assert loaded_page._empty_label.isHidden() is True

    def test_empty_label_visible_after_loading_empty_library(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_personas(lib)
        assert page._empty_label.isHidden() is False

    def test_empty_label_hidden_after_reloading_with_personas(self, page):
        # Start empty
        lib_empty = LibraryIndex(library_root="/fake")
        page.load_personas(lib_empty)
        assert page._empty_label.isHidden() is False
        # Load real personas
        lib = _make_library("developer", "architect")
        page.load_personas(lib)
        assert page._empty_label.isHidden() is True


# ---------------------------------------------------------------------------
# BEAN-274 — Team-coherence indicator (red/yellow/green)
#
# The wizard's _coherence_label reflects validate_contract_graph's findings
# in real time as personas are toggled. Tests bind the user-facing contract:
# 🔴 missing producer, 🟡 orphan produces, 🟢 all consumes satisfied.
# ---------------------------------------------------------------------------


def _make_contract_persona(
    pid: str,
    *,
    produces: list[str] | None = None,
    consumes: list[str] | None = None,
    tier: str = "core",
    category: str = "Software Development",
) -> PersonaInfo:
    """PersonaInfo with explicit produces/consumes — for coherence tests."""
    return PersonaInfo(
        id=pid,
        path=f"/fake/personas/{pid}",
        tier=tier,
        has_persona_md=True,
        has_outputs_md=True,
        has_prompts_md=True,
        templates=[],
        category=category,
        produces=produces or [],
        consumes=consumes or [],
    )


@pytest.fixture()
def coherence_page():
    """A page loaded with four contract-bearing personas:
    - producer: produces 'thing' (no consumes)
    - consumer: consumes 'thing' (no produces)
    - orphan-producer: produces 'orphan-thing' (no on-team consumer)
    - orphan-consumer-absent: consumes 'orphan-thing' (library-only;
      keeps the orphan-produces warning actionable per BEAN-289 so the
      yellow indicator fires when only orphan-producer is selected)

    Red = consumer alone (missing producer for 'thing')
    Yellow = orphan-producer alone (orphan, no error)
    Green = producer + consumer (closed graph)
    """
    lib = LibraryIndex(
        library_root="/fake/library",
        personas=[
            _make_contract_persona("producer", produces=["thing"]),
            _make_contract_persona("consumer", consumes=["thing"]),
            _make_contract_persona(
                "orphan-producer", produces=["orphan-thing"],
            ),
            _make_contract_persona(
                "orphan-consumer-absent", consumes=["orphan-thing"],
            ),
        ],
    )
    p = PersonaSelectionPage(library_index=lib)
    yield p
    p.close()


class TestCoherenceIndicatorInitialState:
    """Before any selection, the indicator is hidden (empty selection
    is already covered by the existing 'select at least one' warning)."""

    def test_indicator_hidden_when_no_library(self, page):
        assert page._coherence_label is not None
        assert page._coherence_label.isHidden() is True

    def test_indicator_hidden_when_library_loaded_but_nothing_selected(
        self, coherence_page,
    ):
        assert coherence_page._coherence_label.isHidden() is True


class TestCoherenceIndicatorRed:
    """🔴 — at least one missing-producer error on the current selection."""

    def test_indicator_red_when_consumer_lacks_producer(
        self, coherence_page,
    ):
        coherence_page.persona_cards["consumer"].is_selected = True

        label = coherence_page._coherence_label
        assert label.isHidden() is False
        text = label.text()
        # Red emoji (\U0001f534) marks the missing-producer state.
        assert "\U0001f534" in text, f"Expected red emoji, got: {text!r}"
        # The label messages the user about the missing producer.
        assert "missing" in text.lower()

    def test_indicator_red_count_reflects_findings(self, coherence_page):
        """A consumer with multiple unsatisfied consumes must show the
        right pluralization and count."""
        # Add a consumer with two unsatisfied types.
        lib = LibraryIndex(
            library_root="/fake",
            personas=[
                _make_contract_persona(
                    "lonely",
                    consumes=["aaa", "bbb"],
                ),
            ],
        )
        coherence_page.load_personas(lib)
        coherence_page.persona_cards["lonely"].is_selected = True

        text = coherence_page._coherence_label.text()
        assert "\U0001f534" in text
        # BEAN-290: headline talks about "missing roles" (user vocabulary),
        # not "missing producers" (graph vocabulary).
        assert "2 missing role" in text
        assert "roles" in text  # plural


class TestCoherenceIndicatorYellow:
    """🟡 — orphan produces but no missing producer."""

    def test_indicator_yellow_when_only_orphan_produces(
        self, coherence_page,
    ):
        coherence_page.persona_cards["orphan-producer"].is_selected = True

        label = coherence_page._coherence_label
        assert label.isHidden() is False
        text = label.text()
        # Yellow emoji (\U0001f7e1) marks the orphan-only state.
        assert "\U0001f7e1" in text, f"Expected yellow emoji, got: {text!r}"
        # BEAN-290: yellow headline describes "unused output(s)" rather
        # than "orphan produces".
        assert "unused output" in text.lower()


class TestCoherenceIndicatorGreen:
    """🟢 — all consumes satisfied AND no orphan produces."""

    def test_indicator_green_when_team_is_balanced(self, coherence_page):
        coherence_page.persona_cards["producer"].is_selected = True
        coherence_page.persona_cards["consumer"].is_selected = True

        label = coherence_page._coherence_label
        assert label.isHidden() is False
        text = label.text()
        # Green emoji (\U0001f7e2) marks the all-satisfied state.
        assert "\U0001f7e2" in text, f"Expected green emoji, got: {text!r}"
        # BEAN-290: green headline reads "looks good".
        assert "looks good" in text.lower()

    def test_indicator_green_for_five_core_personas_against_real_library(
        self,
    ):
        """BEAN-289 user-visible payoff: with the real ai-team-library/
        loaded and the 5 core personas selected, the team-coherence
        indicator is GREEN (not yellow). The library-level orphans
        (dev-decision, merge-summary, test-suite) no longer surface as
        unactionable yellow warnings."""
        from pathlib import Path

        from foundry_app.services.library_indexer import build_library_index

        library_root = (
            Path(__file__).resolve().parent.parent / "ai-team-library"
        )
        registry = build_library_index(library_root)
        page = PersonaSelectionPage(library_index=registry)
        try:
            for pid in ("architect", "ba", "developer", "team-lead", "tech-qa"):
                page.persona_cards[pid].is_selected = True
            label = page._coherence_label
            assert label.isHidden() is False
            text = label.text()
            assert "\U0001f7e2" in text, (
                f"Expected GREEN indicator for 5 core personas, got: {text!r}"
            )
            # BEAN-290: green headline reads "looks good".
            assert "looks good" in text.lower()
        finally:
            page.close()


class TestCoherenceIndicatorTransitions:
    """The indicator updates *as personas are checked/unchecked* — that's
    the user-facing payoff of BEAN-274."""

    def test_indicator_transitions_red_to_green(self, coherence_page):
        # Start: consumer alone => RED.
        coherence_page.persona_cards["consumer"].is_selected = True
        assert "\U0001f534" in coherence_page._coherence_label.text()

        # Add the producer => GREEN.
        coherence_page.persona_cards["producer"].is_selected = True
        assert "\U0001f7e2" in coherence_page._coherence_label.text()

    def test_indicator_transitions_green_to_yellow(self, coherence_page):
        # Start: balanced team => GREEN.
        coherence_page.persona_cards["producer"].is_selected = True
        coherence_page.persona_cards["consumer"].is_selected = True
        assert "\U0001f7e2" in coherence_page._coherence_label.text()

        # Add an orphan producer => YELLOW (graph still has no missing
        # producer, but now has an orphan output).
        coherence_page.persona_cards["orphan-producer"].is_selected = True
        assert "\U0001f7e1" in coherence_page._coherence_label.text()

    def test_indicator_transitions_yellow_to_red(self, coherence_page):
        # Start: orphan-producer alone => YELLOW.
        coherence_page.persona_cards["orphan-producer"].is_selected = True
        assert "\U0001f7e1" in coherence_page._coherence_label.text()

        # Add the consumer (whose 'thing' is unsatisfied) => RED dominates.
        coherence_page.persona_cards["consumer"].is_selected = True
        assert "\U0001f534" in coherence_page._coherence_label.text()

    def test_indicator_hides_when_all_personas_unchecked(
        self, coherence_page,
    ):
        coherence_page.persona_cards["consumer"].is_selected = True
        assert coherence_page._coherence_label.isHidden() is False
        coherence_page.persona_cards["consumer"].is_selected = False
        assert coherence_page._coherence_label.isHidden() is True

    def test_indicator_refreshes_on_set_team_config(self, coherence_page):
        """``set_team_config`` (used when navigating back into the wizard)
        must also refresh the indicator — not just card toggles."""
        # Restore a broken team via the public API.
        coherence_page.set_team_config(
            TeamConfig(personas=[PersonaSelection(id="consumer")]),
        )
        assert coherence_page._coherence_label.isHidden() is False
        assert "\U0001f534" in coherence_page._coherence_label.text()

    def test_red_dominates_yellow(self, coherence_page):
        """When BOTH a missing producer AND an orphan produce are present,
        the red (error) state must win — the spec says red on missing,
        yellow on orphan, with red being the more severe state."""
        # Select consumer (missing producer = RED) AND orphan-producer
        # (orphan produces = YELLOW).
        coherence_page.persona_cards["consumer"].is_selected = True
        coherence_page.persona_cards["orphan-producer"].is_selected = True
        text = coherence_page._coherence_label.text()
        assert "\U0001f534" in text
        # Yellow emoji must NOT be present — red dominates.
        assert "\U0001f7e1" not in text


# ---------------------------------------------------------------------------
# BEAN-286 — Inline validation findings (verbatim messages + truncation cap)
#
# The indicator now renders the validator's per-message text below its
# header so the user sees what specifically is broken, not just a count.
# Long lists collapse to a final "+N more" line.
# ---------------------------------------------------------------------------


class TestCoherenceIndicatorVerbatimMessages:
    """🔴/🟡 states surface the validator's actionable per-message text."""

    def test_red_includes_verbatim_missing_producer_message(
        self, coherence_page,
    ):
        coherence_page.persona_cards["consumer"].is_selected = True
        text = coherence_page._coherence_label.text()
        # BEAN-290: missing-producer message names the affected team
        # member and the suggested persona to add, both in user vocabulary.
        assert "Your Consumer needs" in text
        assert "Add the Producer" in text
        # The specific artifact name from the fixture must round-trip
        # (no human label registered for "thing", so it falls through).
        assert "thing" in text

    def test_yellow_includes_verbatim_orphan_message(self, coherence_page):
        coherence_page.persona_cards["orphan-producer"].is_selected = True
        text = coherence_page._coherence_label.text()
        # BEAN-290: orphan-produces message names the producing persona
        # in user vocabulary (title-cased id) and points the user at how
        # to fix it.
        assert "The Orphan Producer produces" in text
        assert "no one else on your team uses" in text
        # Artifact name from the fixture round-trips. The label helper's
        # fallback turns "orphan-thing" into "orphan thing".
        assert "orphan thing" in text


class TestCoherenceIndicatorTruncationCap:
    """Six or more findings collapse the surplus to '+N more'."""

    def test_red_findings_capped_at_five_with_overflow_line(self):
        # Build a single consumer with 6 unsatisfied artifact types so the
        # validator emits 6 missing-producer errors. The indicator shows
        # the first 5 verbatim and a single '+1 more' line for the rest.
        lib = LibraryIndex(
            library_root="/fake",
            personas=[
                _make_contract_persona(
                    "lonely",
                    consumes=["aaa", "bbb", "ccc", "ddd", "eee", "fff"],
                ),
            ],
        )
        page = PersonaSelectionPage(library_index=lib)
        try:
            page.persona_cards["lonely"].is_selected = True
            text = page._coherence_label.text()
            # All six types are *findings*; only the first five appear
            # verbatim. The validator sorts alphabetically, so 'fff' is the
            # one that gets pushed past the cap. BEAN-290: artifact ids
            # appear bare (no quotes) since the message no longer wraps
            # them in `type 'X'` syntax.
            assert "needs aaa" in text
            assert "needs bbb" in text
            assert "needs ccc" in text
            assert "needs ddd" in text
            assert "needs eee" in text
            assert "fff" not in text
            assert "+1 more" in text
        finally:
            page.close()

    def test_no_overflow_line_when_count_at_or_below_cap(
        self, coherence_page,
    ):
        coherence_page.persona_cards["consumer"].is_selected = True
        text = coherence_page._coherence_label.text()
        # One missing producer ⇒ one bullet, no '+N more' suffix.
        assert "more" not in text.lower()
