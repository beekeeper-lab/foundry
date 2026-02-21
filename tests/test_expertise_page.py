"""Tests for foundry_app.ui.screens.builder.wizard_pages.expertise_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    ExpertiseInfo,
    ExpertiseSelection,
    LibraryIndex,
)
from foundry_app.ui.screens.builder.wizard_pages.expertise_page import (
    EXPERTISE_DESCRIPTIONS,
    ExpertiseCard,
    ExpertiseSelectionPage,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_expertise(
    sid: str,
    files: list[str] | None = None,
    category: str = "",
) -> ExpertiseInfo:
    """Create a minimal ExpertiseInfo for testing."""
    return ExpertiseInfo(
        id=sid,
        path=f"/fake/expertise/{sid}",
        files=files or [],
        category=category,
    )


def _make_library(*stack_ids: str) -> LibraryIndex:
    """Create a LibraryIndex with the given expertise ids (no categories)."""
    return LibraryIndex(
        library_root="/fake/library",
        expertise=[_make_expertise(sid) for sid in stack_ids],
    )


def _make_categorized_library() -> LibraryIndex:
    """Create a LibraryIndex with categorized expertise for grouped UI tests."""
    return LibraryIndex(
        library_root="/fake/library",
        expertise=[
            _make_expertise("python", category="Languages"),
            _make_expertise("react", category="Languages"),
            _make_expertise("typescript", category="Languages"),
            _make_expertise("clean-code", category="Architecture & Patterns"),
            _make_expertise("microservices", category="Architecture & Patterns"),
            _make_expertise("devops", category="Infrastructure & Platforms"),
            _make_expertise("kubernetes", category="Infrastructure & Platforms"),
            _make_expertise("sql-dba", category="Data & ML"),
            _make_expertise("security", category="Compliance & Governance"),
            _make_expertise("finops", category="Business Practices"),
            _make_expertise("custom-thing"),  # no category -> Other
        ],
    )


def _make_full_library() -> LibraryIndex:
    """Create a LibraryIndex with 11 expertise items for compatibility."""
    return _make_library(
        "clean-code", "devops", "dotnet", "java", "node",
        "python", "python-qt-pyside6", "react", "security",
        "sql-dba", "typescript",
    )


def _make_library_with_files() -> LibraryIndex:
    """Create a LibraryIndex where expertise items have convention files."""
    return LibraryIndex(
        library_root="/fake/library",
        expertise=[
            _make_expertise("python", ["conventions.md", "testing.md", "security.md"]),
            _make_expertise("react", ["conventions.md", "testing.md"]),
            _make_expertise("devops", ["conventions.md"]),
        ],
    )


# ---------------------------------------------------------------------------
# ExpertiseCard — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def card():
    expertise = _make_expertise("python", ["conventions.md", "testing.md", "security.md"])
    c = ExpertiseCard(expertise)
    yield c
    c.close()


class TestExpertiseCardConstruction:
    def test_creates_without_error(self, card):
        assert card is not None

    def test_expertise_id(self, card):
        assert card.expertise_id == "python"

    def test_initially_not_selected(self, card):
        assert card.is_selected is False

    def test_object_name(self, card):
        assert card.objectName() == "expertise-card"

    def test_file_count(self, card):
        assert card.file_count == 3


# ---------------------------------------------------------------------------
# ExpertiseCard — selection
# ---------------------------------------------------------------------------

class TestExpertiseCardSelection:
    def test_select_via_property(self, card):
        card.is_selected = True
        assert card.is_selected is True

    def test_deselect_via_property(self, card):
        card.is_selected = True
        card.is_selected = False
        assert card.is_selected is False

    def test_toggled_signal_emitted_on_select(self, card):
        received = []
        card.toggled.connect(lambda sid, checked: received.append((sid, checked)))
        card.is_selected = True
        assert len(received) == 1
        assert received[0] == ("python", True)

    def test_toggled_signal_emitted_on_deselect(self, card):
        card.is_selected = True
        received = []
        card.toggled.connect(lambda sid, checked: received.append((sid, checked)))
        card.is_selected = False
        assert len(received) == 1
        assert received[0] == ("python", False)


# ---------------------------------------------------------------------------
# ExpertiseCard — to_expertise_selection
# ---------------------------------------------------------------------------

class TestExpertiseCardToSelection:
    def test_default_selection_values(self, card):
        sel = card.to_expertise_selection()
        assert isinstance(sel, ExpertiseSelection)
        assert sel.id == "python"
        assert sel.order == 0

    def test_custom_order(self, card):
        sel = card.to_expertise_selection(order=3)
        assert sel.order == 3


# ---------------------------------------------------------------------------
# ExpertiseCard — load_from_selection
# ---------------------------------------------------------------------------

class TestExpertiseCardLoadFromSelection:
    def test_load_checks_card(self, card):
        sel = ExpertiseSelection(id="python", order=2)
        card.load_from_selection(sel)
        assert card.is_selected is True

    def test_roundtrip_selection(self, card):
        original = ExpertiseSelection(id="python", order=5)
        card.load_from_selection(original)
        result = card.to_expertise_selection(order=5)
        assert result.id == original.id
        assert result.order == original.order


# ---------------------------------------------------------------------------
# ExpertiseCard — unknown expertise fallback
# ---------------------------------------------------------------------------

class TestExpertiseCardUnknownId:
    def test_unknown_expertise_uses_titlecased_id(self):
        expertise = _make_expertise("custom-framework")
        card = ExpertiseCard(expertise)
        assert card.expertise_id == "custom-framework"
        card.close()


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = ExpertiseSelectionPage()
    yield p
    p.close()


@pytest.fixture()
def loaded_page():
    lib = _make_full_library()
    p = ExpertiseSelectionPage(library_index=lib)
    yield p
    p.close()


@pytest.fixture()
def categorized_page():
    lib = _make_categorized_library()
    p = ExpertiseSelectionPage(library_index=lib)
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_no_cards_initially(self, page):
        assert len(page.expertise_cards) == 0

    def test_initially_invalid(self, page):
        assert page.is_valid() is False

    def test_selected_count_zero(self, page):
        assert page.selected_count() == 0

    def test_warning_hidden_initially(self, page):
        # Warning is hidden initially because there are no cards yet
        assert page._warning_label.isHidden() is True

    def test_ordered_ids_empty(self, page):
        assert page.ordered_ids == []


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — load_expertise
# ---------------------------------------------------------------------------

class TestLoadExpertise:
    def test_loads_all_11_expertise(self, loaded_page):
        assert len(loaded_page.expertise_cards) == 11

    def test_loads_via_constructor(self):
        lib = _make_library("python", "react")
        page = ExpertiseSelectionPage(library_index=lib)
        assert len(page.expertise_cards) == 2
        page.close()

    def test_load_replaces_previous_expertise(self, loaded_page):
        new_lib = _make_library("python")
        loaded_page.load_expertise(new_lib)
        assert len(loaded_page.expertise_cards) == 1
        assert "python" in loaded_page.expertise_cards

    def test_empty_library_shows_no_cards(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_expertise(lib)
        assert len(page.expertise_cards) == 0


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — category grouping
# ---------------------------------------------------------------------------

class TestCategoryGrouping:
    def test_items_grouped_by_category(self, categorized_page):
        groups = categorized_page.category_groups
        assert "Languages" in groups
        assert "Architecture & Patterns" in groups
        assert "Infrastructure & Platforms" in groups
        assert "Data & ML" in groups
        assert "Compliance & Governance" in groups
        assert "Business Practices" in groups
        assert "Other" in groups

    def test_category_count_in_title(self, categorized_page):
        groups = categorized_page.category_groups
        assert "Languages (3)" in groups["Languages"].title()
        assert "Architecture & Patterns (2)" in groups["Architecture & Patterns"].title()
        assert "Other (1)" in groups["Other"].title()

    def test_all_cards_accessible(self, categorized_page):
        assert len(categorized_page.expertise_cards) == 11

    def test_uncategorized_items_in_other(self, categorized_page):
        assert "custom-thing" in categorized_page.expertise_cards

    def test_reload_clears_groups(self, categorized_page):
        new_lib = _make_library("python")
        categorized_page.load_expertise(new_lib)
        groups = categorized_page.category_groups
        assert len(groups) == 1
        assert "Other" in groups

    def test_category_groups_sorted_alphabetically(self, categorized_page):
        group_names = list(categorized_page.category_groups.keys())
        # "Other" should be last, rest alphabetical
        non_other = [g for g in group_names if g != "Other"]
        assert non_other == sorted(non_other)
        if "Other" in group_names:
            assert group_names[-1] == "Other"

    def test_selection_works_across_groups(self, categorized_page):
        categorized_page.expertise_cards["python"].is_selected = True
        categorized_page.expertise_cards["devops"].is_selected = True
        categorized_page.expertise_cards["custom-thing"].is_selected = True
        assert categorized_page.selected_count() == 3
        sels = categorized_page.get_expertise_selections()
        ids = {s.id for s in sels}
        assert ids == {"python", "devops", "custom-thing"}

    def test_set_selections_works_across_groups(self, categorized_page):
        selections = [
            ExpertiseSelection(id="python", order=0),
            ExpertiseSelection(id="security", order=1),
            ExpertiseSelection(id="finops", order=2),
        ]
        categorized_page.set_expertise_selections(selections)
        assert categorized_page.expertise_cards["python"].is_selected is True
        assert categorized_page.expertise_cards["security"].is_selected is True
        assert categorized_page.expertise_cards["finops"].is_selected is True
        assert categorized_page.expertise_cards["devops"].is_selected is False


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — selection and validation
# ---------------------------------------------------------------------------

class TestPageSelection:
    def test_select_one_expertise(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        assert loaded_page.selected_count() == 1
        assert loaded_page.is_valid() is True

    def test_select_multiple_expertise(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.expertise_cards["typescript"].is_selected = True
        assert loaded_page.selected_count() == 3

    def test_deselect_all_makes_invalid(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["python"].is_selected = False
        assert loaded_page.is_valid() is False

    def test_selection_changed_signal_emitted(self, loaded_page):
        received = []
        loaded_page.selection_changed.connect(lambda: received.append(True))
        loaded_page.expertise_cards["python"].is_selected = True
        assert len(received) >= 1

    def test_warning_shown_after_deselect_all(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["python"].is_selected = False
        assert loaded_page._warning_label.isHidden() is False

    def test_warning_hidden_when_expertise_selected(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        assert loaded_page._warning_label.isHidden() is True


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — get_expertise_selections
# ---------------------------------------------------------------------------

class TestGetExpertiseSelections:
    def test_empty_when_none_selected(self, loaded_page):
        selections = loaded_page.get_expertise_selections()
        assert isinstance(selections, list)
        assert len(selections) == 0

    def test_contains_selected_expertise(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        selections = loaded_page.get_expertise_selections()
        ids = {s.id for s in selections}
        assert ids == {"python", "react"}

    def test_unselected_expertise_excluded(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        selections = loaded_page.get_expertise_selections()
        ids = [s.id for s in selections]
        assert "react" not in ids

    def test_order_values_assigned(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        selections = loaded_page.get_expertise_selections()
        orders = [s.order for s in selections]
        assert orders == [0, 1]

    def test_selections_are_expertise_selection_objects(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        selections = loaded_page.get_expertise_selections()
        assert all(isinstance(s, ExpertiseSelection) for s in selections)


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — set_expertise_selections (round-trip)
# ---------------------------------------------------------------------------

class TestSetExpertiseSelections:
    def test_restores_selections(self, loaded_page):
        selections = [
            ExpertiseSelection(id="python", order=0),
            ExpertiseSelection(id="react", order=1),
        ]
        loaded_page.set_expertise_selections(selections)
        assert loaded_page.expertise_cards["python"].is_selected is True
        assert loaded_page.expertise_cards["react"].is_selected is True
        assert loaded_page.expertise_cards["java"].is_selected is False

    def test_restores_ordering(self, loaded_page):
        selections = [
            ExpertiseSelection(id="react", order=0),
            ExpertiseSelection(id="python", order=1),
        ]
        loaded_page.set_expertise_selections(selections)
        assert loaded_page.ordered_ids == ["react", "python"]

    def test_set_clears_previous(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["java"].is_selected = True

        selections = [ExpertiseSelection(id="react", order=0)]
        loaded_page.set_expertise_selections(selections)
        assert loaded_page.expertise_cards["python"].is_selected is False
        assert loaded_page.expertise_cards["java"].is_selected is False
        assert loaded_page.expertise_cards["react"].is_selected is True

    def test_set_updates_warning(self, loaded_page):
        # Set a valid selection
        selections = [ExpertiseSelection(id="python", order=0)]
        loaded_page.set_expertise_selections(selections)
        assert loaded_page._warning_label.isHidden() is True

        # Set an empty selection
        loaded_page.set_expertise_selections([])
        assert loaded_page._warning_label.isHidden() is False

    def test_roundtrip_get_set_get(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        original = loaded_page.get_expertise_selections()

        # Reset all
        for card in loaded_page.expertise_cards.values():
            card.is_selected = False

        loaded_page.set_expertise_selections(original)
        restored = loaded_page.get_expertise_selections()

        assert len(restored) == len(original)
        orig_ids = {s.id for s in original}
        rest_ids = {s.id for s in restored}
        assert orig_ids == rest_ids

    def test_ignores_unknown_expertise_ids(self, loaded_page):
        selections = [
            ExpertiseSelection(id="python", order=0),
            ExpertiseSelection(id="nonexistent", order=1),
        ]
        loaded_page.set_expertise_selections(selections)
        assert loaded_page.expertise_cards["python"].is_selected is True
        assert loaded_page.selected_count() == 1


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — ordering
# ---------------------------------------------------------------------------

class TestOrdering:
    def test_selection_order_tracked(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        assert loaded_page.ordered_ids == ["python", "react"]

    def test_deselection_removes_from_order(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.expertise_cards["python"].is_selected = False
        assert loaded_page.ordered_ids == ["react"]

    def test_move_up(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.move_expertise_up("react")
        assert loaded_page.ordered_ids == ["react", "python"]

    def test_move_up_at_top_no_change(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.move_expertise_up("python")
        assert loaded_page.ordered_ids == ["python", "react"]

    def test_move_down(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.move_expertise_down("python")
        assert loaded_page.ordered_ids == ["react", "python"]

    def test_move_down_at_bottom_no_change(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.move_expertise_down("react")
        assert loaded_page.ordered_ids == ["python", "react"]

    def test_move_unselected_expertise_no_error(self, loaded_page):
        loaded_page.move_expertise_up("python")  # not selected, should be no-op
        assert loaded_page.ordered_ids == []

    def test_move_emits_selection_changed(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        received = []
        loaded_page.selection_changed.connect(lambda: received.append(True))
        loaded_page.move_expertise_up("react")
        assert len(received) >= 1

    def test_order_values_in_selections(self, loaded_page):
        loaded_page.expertise_cards["python"].is_selected = True
        loaded_page.expertise_cards["react"].is_selected = True
        loaded_page.expertise_cards["typescript"].is_selected = True
        loaded_page.move_expertise_up("typescript")
        # Order should be: typescript(0), python(1), react(2)
        selections = loaded_page.get_expertise_selections()
        by_id = {s.id: s.order for s in selections}
        assert by_id["typescript"] < by_id["react"]


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — file count badge display
# ---------------------------------------------------------------------------

class TestFileBadge:
    def test_expertise_with_files_shows_count(self):
        lib = _make_library_with_files()
        page = ExpertiseSelectionPage(library_index=lib)
        assert page.expertise_cards["python"].file_count == 3
        assert page.expertise_cards["react"].file_count == 2
        assert page.expertise_cards["devops"].file_count == 1
        page.close()

    def test_expertise_with_no_files(self):
        lib = _make_library("python")
        page = ExpertiseSelectionPage(library_index=lib)
        assert page.expertise_cards["python"].file_count == 0
        page.close()


# ---------------------------------------------------------------------------
# EXPERTISE_DESCRIPTIONS completeness
# ---------------------------------------------------------------------------

class TestExpertiseDescriptions:
    def test_all_39_expertise_have_descriptions(self):
        expected = {
            "accessibility-compliance", "api-design", "aws-cloud-platform",
            "azure-cloud-platform", "business-intelligence", "change-management",
            "clean-code", "customer-enablement", "data-engineering", "devops",
            "dotnet", "event-driven-messaging", "finops", "frontend-build-tooling",
            "gcp-cloud-platform", "gdpr-data-privacy", "go", "hipaa-compliance",
            "iso-9000", "java", "kotlin", "kubernetes", "microservices", "mlops",
            "node", "pci-dss-compliance", "product-strategy", "python",
            "python-qt-pyside6", "react", "react-native", "rust",
            "sales-engineering", "security", "sox-compliance", "sql-dba",
            "swift", "terraform", "typescript",
        }
        assert set(EXPERTISE_DESCRIPTIONS.keys()) == expected

    def test_descriptions_are_tuples(self):
        for sid, desc in EXPERTISE_DESCRIPTIONS.items():
            assert isinstance(desc, tuple), f"{sid} description is not a tuple"
            assert len(desc) == 2, f"{sid} description tuple has {len(desc)} elements"

    def test_descriptions_have_nonempty_values(self):
        for sid, (name, desc) in EXPERTISE_DESCRIPTIONS.items():
            assert len(name) > 0, f"{sid} has empty display name"
            assert len(desc) > 0, f"{sid} has empty description"


# ---------------------------------------------------------------------------
# ExpertiseSelectionPage — empty-state messaging
# ---------------------------------------------------------------------------

class TestEmptyState:
    def test_empty_label_visible_when_no_library(self, page):
        assert page._empty_label.isHidden() is False

    def test_empty_label_hidden_after_loading_expertise(self):
        lib = _make_full_library()
        p = ExpertiseSelectionPage(library_index=lib)
        assert p._empty_label.isHidden() is True
        p.close()

    def test_empty_label_visible_after_loading_empty_library(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_expertise(lib)
        assert page._empty_label.isHidden() is False

    def test_empty_label_hidden_after_reloading_with_expertise(self, page):
        lib_empty = LibraryIndex(library_root="/fake")
        page.load_expertise(lib_empty)
        assert page._empty_label.isHidden() is False
        lib = _make_library("python", "react")
        page.load_expertise(lib)
        assert page._empty_label.isHidden() is True
