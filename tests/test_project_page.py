"""Tests for foundry_app.ui.screens.builder.wizard_pages.project_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import ProjectIdentity
from foundry_app.ui.screens.builder.wizard_pages.project_page import (
    ProjectPage,
    _slugify,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# _slugify unit tests
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_simple_name(self):
        assert _slugify("My Project") == "my-project"

    def test_already_slug(self):
        assert _slugify("my-project") == "my-project"

    def test_uppercase(self):
        assert _slugify("MY PROJECT") == "my-project"

    def test_special_characters(self):
        assert _slugify("Hello, World! (v2)") == "hello-world-v2"

    def test_leading_trailing_whitespace(self):
        assert _slugify("  spaces  ") == "spaces"

    def test_leading_hyphens_stripped(self):
        assert _slugify("---leading") == "leading"

    def test_trailing_hyphens_stripped(self):
        assert _slugify("trailing---") == "trailing"

    def test_consecutive_specials_collapsed(self):
        assert _slugify("a   b___c") == "a-b-c"

    def test_empty_string(self):
        assert _slugify("") == ""

    def test_only_special_chars(self):
        assert _slugify("!@#$%") == ""

    def test_numeric_start(self):
        assert _slugify("42 things") == "42-things"

    def test_single_word(self):
        assert _slugify("foundry") == "foundry"


# ---------------------------------------------------------------------------
# Slug auto-generation
# ---------------------------------------------------------------------------


class TestSlugAutoGeneration:
    @pytest.fixture()
    def page(self):
        p = ProjectPage()
        yield p

    def test_slug_updates_on_name_change(self, page):
        page.name_edit.setText("My Awesome Project")
        assert page.slug_edit.text() == "my-awesome-project"

    def test_slug_clears_when_name_cleared(self, page):
        page.name_edit.setText("Something")
        page.name_edit.setText("")
        assert page.slug_edit.text() == ""

    def test_slug_handles_special_chars(self, page):
        page.name_edit.setText("Hello, World! (v2)")
        assert page.slug_edit.text() == "hello-world-v2"

    def test_slug_live_updates(self, page):
        page.name_edit.setText("First")
        assert page.slug_edit.text() == "first"
        page.name_edit.setText("Second Name")
        assert page.slug_edit.text() == "second-name"


# ---------------------------------------------------------------------------
# Validation / completeness
# ---------------------------------------------------------------------------


class TestValidation:
    @pytest.fixture()
    def page(self):
        p = ProjectPage()
        yield p

    def test_incomplete_when_empty(self, page):
        assert not page.is_complete()

    def test_complete_when_name_entered(self, page):
        page.name_edit.setText("Test Project")
        assert page.is_complete()

    def test_incomplete_when_whitespace_only(self, page):
        page.name_edit.setText("   ")
        assert not page.is_complete()

    def test_complete_after_clear_and_retype(self, page):
        page.name_edit.setText("Project")
        page.name_edit.setText("")
        assert not page.is_complete()
        page.name_edit.setText("New Project")
        assert page.is_complete()

    def test_completeness_signal_emitted(self, page):
        signals = []
        page.completeness_changed.connect(lambda v: signals.append(v))
        page.name_edit.setText("Project")
        assert signals == [True]
        page.name_edit.setText("")
        assert signals == [True, False]

    def test_signal_not_emitted_for_same_state(self, page):
        signals = []
        page.completeness_changed.connect(lambda v: signals.append(v))
        page.name_edit.setText("A")
        page.name_edit.setText("AB")
        # Only one True — both states are "complete"
        assert signals == [True]


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------


class TestGetData:
    @pytest.fixture()
    def page(self):
        p = ProjectPage()
        yield p

    def test_get_data_returns_project_identity(self, page):
        page.name_edit.setText("My API")
        data = page.get_data()
        assert isinstance(data, ProjectIdentity)

    def test_get_data_name(self, page):
        page.name_edit.setText("My API")
        data = page.get_data()
        assert data.name == "My API"

    def test_get_data_slug(self, page):
        page.name_edit.setText("My API")
        data = page.get_data()
        assert data.slug == "my-api"

    def test_get_data_strips_whitespace(self, page):
        page.name_edit.setText("  Padded Name  ")
        data = page.get_data()
        assert data.name == "Padded Name"
        assert data.slug == "padded-name"

    def test_get_data_default_output_root(self, page):
        page.name_edit.setText("Test")
        data = page.get_data()
        assert data.output_root == "./generated-projects"


# ---------------------------------------------------------------------------
# set_data (pre-populate from existing identity)
# ---------------------------------------------------------------------------


class TestSetData:
    @pytest.fixture()
    def page(self):
        p = ProjectPage()
        yield p

    def test_set_data_populates_name(self, page):
        identity = ProjectIdentity(name="Existing", slug="existing")
        page.set_data(identity)
        assert page.name_edit.text() == "Existing"

    def test_set_data_generates_slug(self, page):
        identity = ProjectIdentity(name="Existing Project", slug="existing-project")
        page.set_data(identity)
        assert page.slug_edit.text() == "existing-project"

    def test_set_data_makes_page_complete(self, page):
        identity = ProjectIdentity(name="Existing", slug="existing")
        page.set_data(identity)
        assert page.is_complete()
