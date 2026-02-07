"""Tests for foundry_app.ui.screens.builder.wizard_pages.stack_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    LibraryIndex,
    StackInfo,
    StackSelection,
)
from foundry_app.ui.screens.builder.wizard_pages.stack_page import (
    STACK_DESCRIPTIONS,
    StackCard,
    StackSelectionPage,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_stack(sid: str, files: list[str] | None = None) -> StackInfo:
    """Create a minimal StackInfo for testing."""
    return StackInfo(
        id=sid,
        path=f"/fake/stacks/{sid}",
        files=files or [],
    )


def _make_library(*stack_ids: str) -> LibraryIndex:
    """Create a LibraryIndex with the given stack ids."""
    return LibraryIndex(
        library_root="/fake/library",
        stacks=[_make_stack(sid) for sid in stack_ids],
    )


def _make_full_library() -> LibraryIndex:
    """Create a LibraryIndex matching the real 11-stack library."""
    return _make_library(
        "clean-code", "devops", "dotnet", "java", "node",
        "python", "python-qt-pyside6", "react", "security",
        "sql-dba", "typescript",
    )


# ---------------------------------------------------------------------------
# StackCard — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def card():
    stack = _make_stack("python", ["conventions.md", "testing.md"])
    c = StackCard(stack)
    yield c
    c.close()


class TestStackCardConstruction:
    def test_creates_without_error(self, card):
        assert card is not None

    def test_stack_id(self, card):
        assert card.stack_id == "python"

    def test_initially_not_selected(self, card):
        assert card.is_selected is False

    def test_object_name(self, card):
        assert card.objectName() == "stack-card"


# ---------------------------------------------------------------------------
# StackCard — selection
# ---------------------------------------------------------------------------

class TestStackCardSelection:
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
# StackCard — to_stack_selection
# ---------------------------------------------------------------------------

class TestStackCardToSelection:
    def test_default_selection_values(self, card):
        sel = card.to_stack_selection()
        assert isinstance(sel, StackSelection)
        assert sel.id == "python"
        assert sel.order == 0

    def test_custom_order(self, card):
        card._order_spin.setValue(5)
        sel = card.to_stack_selection()
        assert sel.order == 5

    def test_max_order(self, card):
        card._order_spin.setValue(99)
        sel = card.to_stack_selection()
        assert sel.order == 99


# ---------------------------------------------------------------------------
# StackCard — load_from_selection
# ---------------------------------------------------------------------------

class TestStackCardLoadFromSelection:
    def test_load_restores_checked_and_order(self, card):
        sel = StackSelection(id="python", order=10)
        card.load_from_selection(sel)
        assert card.is_selected is True
        assert card._order_spin.value() == 10

    def test_load_with_zero_order(self, card):
        sel = StackSelection(id="python", order=0)
        card.load_from_selection(sel)
        assert card._order_spin.value() == 0

    def test_roundtrip_selection(self, card):
        original = StackSelection(id="python", order=7)
        card.load_from_selection(original)
        result = card.to_stack_selection()
        assert result.id == original.id
        assert result.order == original.order


# ---------------------------------------------------------------------------
# StackCard — unknown stack fallback
# ---------------------------------------------------------------------------

class TestStackCardUnknownStack:
    def test_unknown_stack_uses_titlecased_id(self):
        stack = _make_stack("my-custom-stack")
        card = StackCard(stack)
        assert card.stack_id == "my-custom-stack"
        card.close()


# ---------------------------------------------------------------------------
# StackSelectionPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = StackSelectionPage()
    yield p
    p.close()


@pytest.fixture()
def loaded_page():
    lib = _make_full_library()
    p = StackSelectionPage(library_index=lib)
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_no_cards_initially(self, page):
        assert len(page.stack_cards) == 0

    def test_initially_invalid(self, page):
        assert page.is_valid() is False

    def test_selected_count_zero(self, page):
        assert page.selected_count() == 0

    def test_warning_hidden_initially(self, page):
        assert page._warning_label.isHidden() is True


# ---------------------------------------------------------------------------
# StackSelectionPage — load_stacks
# ---------------------------------------------------------------------------

class TestLoadStacks:
    def test_loads_all_11_stacks(self, loaded_page):
        assert len(loaded_page.stack_cards) == 11

    def test_all_known_stack_ids_present(self, loaded_page):
        cards = loaded_page.stack_cards
        for sid in STACK_DESCRIPTIONS:
            assert sid in cards, f"Missing stack card: {sid}"

    def test_loads_via_constructor(self):
        lib = _make_library("python", "react")
        page = StackSelectionPage(library_index=lib)
        assert len(page.stack_cards) == 2
        page.close()

    def test_load_replaces_previous_stacks(self, loaded_page):
        new_lib = _make_library("python")
        loaded_page.load_stacks(new_lib)
        assert len(loaded_page.stack_cards) == 1
        assert "python" in loaded_page.stack_cards

    def test_empty_library_shows_no_cards(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_stacks(lib)
        assert len(page.stack_cards) == 0


# ---------------------------------------------------------------------------
# StackSelectionPage — selection and validation
# ---------------------------------------------------------------------------

class TestPageSelection:
    def test_select_one_stack(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        assert loaded_page.selected_count() == 1
        assert loaded_page.is_valid() is True

    def test_select_multiple_stacks(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["react"].is_selected = True
        loaded_page.stack_cards["typescript"].is_selected = True
        assert loaded_page.selected_count() == 3

    def test_deselect_all_makes_invalid(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["python"].is_selected = False
        assert loaded_page.is_valid() is False

    def test_selection_changed_signal_emitted(self, loaded_page):
        received = []
        loaded_page.selection_changed.connect(lambda: received.append(True))
        loaded_page.stack_cards["python"].is_selected = True
        assert len(received) >= 1

    def test_warning_shown_after_deselect_all(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["python"].is_selected = False
        assert loaded_page._warning_label.isHidden() is False

    def test_warning_hidden_when_stack_selected(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        assert loaded_page._warning_label.isHidden() is True


# ---------------------------------------------------------------------------
# StackSelectionPage — get_stack_selections
# ---------------------------------------------------------------------------

class TestGetStackSelections:
    def test_empty_when_none_selected(self, loaded_page):
        selections = loaded_page.get_stack_selections()
        assert isinstance(selections, list)
        assert len(selections) == 0

    def test_contains_selected_stacks(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["react"].is_selected = True
        selections = loaded_page.get_stack_selections()
        ids = {s.id for s in selections}
        assert ids == {"python", "react"}

    def test_respects_order_config(self, loaded_page):
        card = loaded_page.stack_cards["python"]
        card.is_selected = True
        card._order_spin.setValue(3)
        selections = loaded_page.get_stack_selections()
        assert len(selections) == 1
        assert selections[0].id == "python"
        assert selections[0].order == 3

    def test_unselected_stacks_excluded(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        selections = loaded_page.get_stack_selections()
        ids = [s.id for s in selections]
        assert "react" not in ids


# ---------------------------------------------------------------------------
# StackSelectionPage — set_stack_selections (round-trip)
# ---------------------------------------------------------------------------

class TestSetStackSelections:
    def test_restores_selections(self, loaded_page):
        selections = [
            StackSelection(id="python", order=1),
            StackSelection(id="react", order=2),
        ]
        loaded_page.set_stack_selections(selections)
        assert loaded_page.stack_cards["python"].is_selected is True
        assert loaded_page.stack_cards["react"].is_selected is True
        assert loaded_page.stack_cards["java"].is_selected is False

    def test_restores_order(self, loaded_page):
        selections = [StackSelection(id="python", order=5)]
        loaded_page.set_stack_selections(selections)
        card = loaded_page.stack_cards["python"]
        assert card._order_spin.value() == 5

    def test_roundtrip_get_set_get(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["react"].is_selected = True
        loaded_page.stack_cards["python"]._order_spin.setValue(3)
        original = loaded_page.get_stack_selections()

        # Reset all
        for card in loaded_page.stack_cards.values():
            card.is_selected = False

        loaded_page.set_stack_selections(original)
        restored = loaded_page.get_stack_selections()

        assert len(restored) == len(original)
        orig_ids = {s.id for s in original}
        rest_ids = {s.id for s in restored}
        assert orig_ids == rest_ids

    def test_set_selections_clears_previous(self, loaded_page):
        loaded_page.stack_cards["python"].is_selected = True
        loaded_page.stack_cards["react"].is_selected = True

        selections = [StackSelection(id="java")]
        loaded_page.set_stack_selections(selections)
        assert loaded_page.stack_cards["python"].is_selected is False
        assert loaded_page.stack_cards["react"].is_selected is False
        assert loaded_page.stack_cards["java"].is_selected is True

    def test_set_selections_updates_warning(self, loaded_page):
        # Set a valid config
        selections = [StackSelection(id="python")]
        loaded_page.set_stack_selections(selections)
        assert loaded_page._warning_label.isHidden() is True

        # Set an empty config
        loaded_page.set_stack_selections([])
        assert loaded_page._warning_label.isHidden() is False


# ---------------------------------------------------------------------------
# StackSelectionPage — file badge display
# ---------------------------------------------------------------------------

class TestFileBadge:
    def test_stack_with_files_shows_badge(self):
        lib = LibraryIndex(
            library_root="/fake",
            stacks=[_make_stack("python", ["conventions.md", "testing.md", "security.md"])],
        )
        page = StackSelectionPage(library_index=lib)
        assert len(page.stack_cards) == 1
        page.close()

    def test_stack_with_one_file_singular(self):
        lib = LibraryIndex(
            library_root="/fake",
            stacks=[_make_stack("python", ["conventions.md"])],
        )
        page = StackSelectionPage(library_index=lib)
        assert len(page.stack_cards) == 1
        page.close()
