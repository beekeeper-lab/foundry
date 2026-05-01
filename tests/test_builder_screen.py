"""Tests for foundry_app.ui.screens.builder_screen.

Focused on BEAN-288 behavior: in-progress detection, start_over reset,
state_changed signal wiring, and Start Over button visibility.
"""

from __future__ import annotations

import pytest

from foundry_app.core.models import LibraryIndex, PersonaInfo
from foundry_app.ui.screens.builder_screen import BuilderScreen

pytestmark = pytest.mark.usefixtures("qapp")


def _make_library() -> LibraryIndex:
    """Library with a single core persona — enough to exercise selection."""
    return LibraryIndex(
        library_root="/fake",
        personas=[
            PersonaInfo(
                id="developer",
                path="/fake/developer",
                tier="core",
                has_persona_md=True,
                has_outputs_md=True,
                has_prompts_md=True,
                templates=[],
                category="",
            ),
        ],
    )


@pytest.fixture()
def builder():
    s = BuilderScreen()
    yield s
    s.close()


@pytest.fixture()
def builder_with_library():
    s = BuilderScreen()
    s.set_library_index(_make_library())
    yield s
    s.close()


# ---------------------------------------------------------------------------
# BEAN-288 — has_in_progress_state()
# ---------------------------------------------------------------------------


class TestHasInProgressStateDefault:
    """Fresh state must report no in-progress work."""

    def test_fresh_builder_is_not_in_progress(self, builder):
        assert builder.has_in_progress_state() is False

    def test_fresh_builder_with_library_is_not_in_progress(
        self, builder_with_library,
    ):
        # Loading a library doesn't count as user input.
        assert builder_with_library.has_in_progress_state() is False


class TestHasInProgressStateTriggers:
    """Each user-input avenue flips the answer to True."""

    def test_in_progress_after_project_name_entered(self, builder):
        builder.project_page.name_edit.setText("my-project")
        assert builder.has_in_progress_state() is True

    def test_in_progress_after_persona_selected(self, builder_with_library):
        builder_with_library.persona_page.persona_cards[
            "developer"
        ].is_selected = True
        assert builder_with_library.has_in_progress_state() is True

    def test_in_progress_when_advanced_past_step_zero(self, builder):
        builder._page_stack.setCurrentIndex(1)
        assert builder.has_in_progress_state() is True

    def test_whitespace_only_name_does_not_count(self, builder):
        builder.project_page.name_edit.setText("   ")
        assert builder.has_in_progress_state() is False


# ---------------------------------------------------------------------------
# BEAN-288 — start_over()
# ---------------------------------------------------------------------------


class TestStartOver:
    """start_over() must clear every page's state and return to step 0."""

    def test_start_over_clears_project_name(self, builder):
        builder.project_page.name_edit.setText("my-project")
        assert builder.has_in_progress_state() is True
        builder.start_over()
        assert builder.project_page.name_edit.text() == ""
        assert builder.has_in_progress_state() is False

    def test_start_over_clears_persona_selection(self, builder_with_library):
        builder_with_library.persona_page.persona_cards[
            "developer"
        ].is_selected = True
        assert builder_with_library.has_in_progress_state() is True

        builder_with_library.start_over()
        assert (
            builder_with_library.persona_page.persona_cards[
                "developer"
            ].is_selected
            is False
        )
        assert builder_with_library.has_in_progress_state() is False

    def test_start_over_returns_to_step_zero(self, builder):
        builder._page_stack.setCurrentIndex(2)
        builder.start_over()
        assert builder.current_step == 0


class TestStartOverButtonVisibility:
    """The button only appears when the user has state worth resetting."""

    def test_start_over_button_hidden_at_fresh_start(self, builder):
        assert builder._start_over_btn.isHidden() is True

    def test_start_over_button_visible_when_state_present(self, builder):
        builder.project_page.name_edit.setText("my-project")
        assert builder._start_over_btn.isHidden() is False

    def test_start_over_button_hidden_after_clicking(self, builder):
        builder.project_page.name_edit.setText("my-project")
        assert builder._start_over_btn.isHidden() is False
        builder._start_over_btn.click()
        assert builder._start_over_btn.isHidden() is True


# ---------------------------------------------------------------------------
# BEAN-288 — state_changed signal
# ---------------------------------------------------------------------------


class TestStateChangedSignal:
    """state_changed fires when the in-progress answer flips."""

    def test_state_changed_fires_on_name_input(self, qtbot=None):
        builder = BuilderScreen()
        try:
            received: list[bool] = []
            builder.state_changed.connect(received.append)
            builder.project_page.name_edit.setText("foo")
            assert True in received
        finally:
            builder.close()

    def test_state_changed_fires_on_persona_select(self):
        builder = BuilderScreen()
        builder.set_library_index(_make_library())
        try:
            received: list[bool] = []
            builder.state_changed.connect(received.append)
            builder.persona_page.persona_cards[
                "developer"
            ].is_selected = True
            assert True in received
        finally:
            builder.close()

    def test_state_changed_fires_back_to_false_on_start_over(self):
        builder = BuilderScreen()
        try:
            builder.project_page.name_edit.setText("foo")
            received: list[bool] = []
            builder.state_changed.connect(received.append)
            builder.start_over()
            assert False in received
        finally:
            builder.close()
