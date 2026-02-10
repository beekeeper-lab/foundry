"""Tests for foundry_app.ui.screens.library_manager — tree browser and editor."""

from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QMessageBox

from foundry_app.ui.screens.library_manager import (
    STARTER_TEMPLATE,
    LibraryManagerScreen,
    _build_file_tree,
    persona_starter_files,
    starter_content,
    validate_asset_name,
)
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_library(root: Path) -> Path:
    """Create a minimal library directory structure for testing."""
    lib = root / "test-library"
    # Personas
    persona_dir = lib / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer persona", encoding="utf-8")
    (persona_dir / "outputs.md").write_text("# Outputs", encoding="utf-8")
    templates_dir = persona_dir / "templates"
    templates_dir.mkdir()
    (templates_dir / "impl.md.j2").write_text("template", encoding="utf-8")

    # Stacks
    stack_dir = lib / "stacks" / "python-fastapi"
    stack_dir.mkdir(parents=True)
    (stack_dir / "stack.md").write_text("# Python + FastAPI", encoding="utf-8")
    (stack_dir / "conventions.md").write_text("# Conventions", encoding="utf-8")
    (stack_dir / "testing.md").write_text("# Testing", encoding="utf-8")

    # Shared Templates
    tpl_dir = lib / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "CLAUDE.md.j2").write_text("# Claude template", encoding="utf-8")
    (tpl_dir / "shared" / "adr.md").parent.mkdir(parents=True, exist_ok=True)
    (tpl_dir / "shared" / "adr.md").write_text("# ADR template", encoding="utf-8")

    # Workflows
    wf_dir = lib / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "default.md").write_text("# Default workflow", encoding="utf-8")

    # Claude assets
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "review-pr.md").write_text("# Review PR", encoding="utf-8")

    skills_dir = lib / "claude" / "skills" / "handoff"
    skills_dir.mkdir(parents=True)
    (skills_dir / "SKILL.md").write_text("# Handoff skill", encoding="utf-8")

    hooks_dir = lib / "claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit-lint.md").write_text("# Lint hook", encoding="utf-8")

    return lib


# ---------------------------------------------------------------------------
# Pure tree building logic
# ---------------------------------------------------------------------------


class TestBuildFileTree:

    def test_empty_dir(self, tmp_path: Path):
        tree = _build_file_tree(tmp_path / "nonexistent")
        assert tree == []

    def test_returns_all_categories(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        assert "Personas" in names
        assert "Stacks" in names
        assert "Shared Templates" in names
        assert "Workflows" in names
        assert "Claude Commands" in names
        assert "Claude Skills" in names
        assert "Claude Hooks" in names

    def test_personas_has_children(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 1
        dev = personas["children"][0]
        assert dev["name"] == "developer"
        # developer dir should have persona.md, outputs.md, and templates/ subdir
        child_names = [c["name"] for c in dev["children"]]
        assert "persona.md" in child_names
        assert "outputs.md" in child_names
        assert "templates" in child_names

    def test_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        persona_md = next(c for c in dev["children"] if c["name"] == "persona.md")
        assert persona_md["path"] is not None
        assert persona_md["path"].endswith("persona.md")

    def test_directory_nodes_have_no_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        dev = personas["children"][0]
        assert dev["path"] is None

    def test_missing_category_dir_gives_empty_children(self, tmp_path: Path):
        lib = tmp_path / "sparse-lib"
        (lib / "personas" / "test").mkdir(parents=True)
        (lib / "personas" / "test" / "persona.md").write_text("hi", encoding="utf-8")
        tree = _build_file_tree(lib)
        stacks = next(c for c in tree if c["name"] == "Stacks")
        assert stacks["children"] == []

    def test_hidden_files_are_skipped(self, tmp_path: Path):
        lib = tmp_path / "lib"
        wf = lib / "workflows"
        wf.mkdir(parents=True)
        (wf / ".hidden").write_text("nope", encoding="utf-8")
        (wf / "visible.md").write_text("yes", encoding="utf-8")
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        names = [c["name"] for c in workflows["children"]]
        assert ".hidden" not in names
        assert "visible.md" in names


# ---------------------------------------------------------------------------
# Screen construction
# ---------------------------------------------------------------------------


class TestScreenConstruction:

    def test_creates_screen(self):
        screen = LibraryManagerScreen()
        assert screen is not None

    def test_has_tree(self):
        screen = LibraryManagerScreen()
        assert screen.tree is not None

    def test_has_editor_widget(self):
        screen = LibraryManagerScreen()
        assert screen.editor_widget is not None
        assert isinstance(screen.editor_widget, MarkdownEditor)

    def test_preview_alias_returns_editor(self):
        screen = LibraryManagerScreen()
        assert screen.preview is screen.editor_widget

    def test_has_file_label(self):
        screen = LibraryManagerScreen()
        assert screen.file_label is not None

    def test_has_empty_label(self):
        screen = LibraryManagerScreen()
        assert screen.empty_label is not None


# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------


class TestLibraryLoading:

    def test_set_library_root(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        assert screen.tree.topLevelItemCount() == 7  # all categories

    def test_nonexistent_root_shows_empty(self, tmp_path: Path):
        screen = LibraryManagerScreen()
        screen.set_library_root(tmp_path / "nonexistent")
        assert screen.tree.topLevelItemCount() == 0
        assert not screen.empty_label.isHidden()

    def test_valid_root_hides_empty_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        assert not screen.empty_label.isVisible()

    def test_tree_has_correct_nesting(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.text(0) == "Personas"
        assert personas_item.childCount() == 1
        dev_item = personas_item.child(0)
        assert dev_item.text(0) == "developer"

    def test_empty_string_root_shows_empty(self):
        screen = LibraryManagerScreen()
        screen.set_library_root("")
        assert screen.tree.topLevelItemCount() == 0

    def test_refresh_updates_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Add a new file
        (lib / "workflows" / "new-workflow.md").write_text("new", encoding="utf-8")
        screen.refresh_tree()
        workflows = None
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                workflows = item
                break
        assert workflows is not None
        assert workflows.childCount() == 2


# ---------------------------------------------------------------------------
# File selection loads into editor
# ---------------------------------------------------------------------------


class TestFileEditing:

    def test_selecting_file_loads_into_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to personas > developer > persona.md
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "persona.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Developer persona" in screen.editor_widget.editor.toPlainText()

    def test_selecting_directory_clears_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select a directory node (category)
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item)
        assert screen.editor_widget.editor.toPlainText() == ""

    def test_file_label_shows_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "persona.md":
                screen.tree.setCurrentItem(child)
                break
        assert "persona.md" in screen.file_label.text()


# ---------------------------------------------------------------------------
# MarkdownEditor widget tests
# ---------------------------------------------------------------------------


class TestMarkdownEditorWidget:

    def test_instantiation(self):
        editor = MarkdownEditor()
        assert editor is not None
        assert editor.dirty is False
        assert editor.file_path is None

    def test_load_content(self):
        editor = MarkdownEditor()
        editor.load_content("# Hello World")
        assert editor.editor.toPlainText() == "# Hello World"
        assert editor.dirty is False

    def test_load_file(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test File\n\nSome content.", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        assert editor.editor.toPlainText() == "# Test File\n\nSome content."
        assert editor.file_path == md_file
        assert editor.dirty is False

    def test_load_nonexistent_file(self, tmp_path: Path):
        editor = MarkdownEditor()
        editor.load_file(tmp_path / "nonexistent.md")
        assert editor.editor.toPlainText() == ""
        assert editor.file_path is None

    def test_dirty_tracking_on_edit(self):
        editor = MarkdownEditor()
        editor.load_content("original")
        assert editor.dirty is False
        editor.editor.setPlainText("modified")
        assert editor.dirty is True

    def test_dirty_false_when_restored_to_original(self):
        editor = MarkdownEditor()
        editor.load_content("original")
        editor.editor.setPlainText("modified")
        assert editor.dirty is True
        editor.editor.setPlainText("original")
        assert editor.dirty is False

    def test_save_writes_to_disk(self, tmp_path: Path):
        md_file = tmp_path / "save-test.md"
        md_file.write_text("before", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        editor.editor.setPlainText("after")
        assert editor.dirty is True
        result = editor.save()
        assert result is True
        assert md_file.read_text(encoding="utf-8") == "after"
        assert editor.dirty is False

    def test_save_without_file_path_returns_false(self):
        editor = MarkdownEditor()
        editor.load_content("content")
        result = editor.save()
        assert result is False

    def test_revert_reloads_from_disk(self, tmp_path: Path):
        md_file = tmp_path / "revert-test.md"
        md_file.write_text("original", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        editor.editor.setPlainText("modified")
        assert editor.dirty is True
        editor.revert()
        assert editor.editor.toPlainText() == "original"
        assert editor.dirty is False

    def test_revert_without_file_restores_saved_content(self):
        editor = MarkdownEditor()
        editor.load_content("initial")
        editor.editor.setPlainText("changed")
        assert editor.dirty is True
        editor.revert()
        assert editor.editor.toPlainText() == "initial"
        assert editor.dirty is False

    def test_clear(self):
        editor = MarkdownEditor()
        editor.load_content("some content", file_path=Path("/tmp/fake.md"))
        editor.clear()
        assert editor.editor.toPlainText() == ""
        assert editor.file_path is None
        assert editor.dirty is False

    def test_save_button_disabled_when_clean(self, tmp_path: Path):
        md_file = tmp_path / "btn-test.md"
        md_file.write_text("content", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        assert not editor.save_button.isEnabled()

    def test_save_button_enabled_when_dirty(self, tmp_path: Path):
        md_file = tmp_path / "btn-test.md"
        md_file.write_text("content", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        editor.editor.setPlainText("changed")
        assert editor.save_button.isEnabled()

    def test_revert_button_disabled_when_clean(self):
        editor = MarkdownEditor()
        editor.load_content("content")
        assert not editor.revert_button.isEnabled()

    def test_revert_button_enabled_when_dirty(self):
        editor = MarkdownEditor()
        editor.load_content("content")
        editor.editor.setPlainText("changed")
        assert editor.revert_button.isEnabled()

    def test_dirty_label_shows_modified(self):
        editor = MarkdownEditor()
        editor.load_content("content")
        assert editor.dirty_label.text() == ""
        editor.editor.setPlainText("changed")
        assert editor.dirty_label.text() == "Modified"

    def test_dirty_label_clears_on_save(self, tmp_path: Path):
        md_file = tmp_path / "label-test.md"
        md_file.write_text("content", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        editor.editor.setPlainText("changed")
        assert editor.dirty_label.text() == "Modified"
        editor.save()
        assert editor.dirty_label.text() == ""

    def test_dirty_changed_signal(self):
        editor = MarkdownEditor()
        editor.load_content("content")
        signals: list[bool] = []
        editor.dirty_changed.connect(signals.append)
        editor.editor.setPlainText("changed")
        assert True in signals

    def test_file_saved_signal(self, tmp_path: Path):
        md_file = tmp_path / "signal-test.md"
        md_file.write_text("content", encoding="utf-8")
        editor = MarkdownEditor()
        editor.load_file(md_file)
        editor.editor.setPlainText("changed")
        saved_paths: list[str] = []
        editor.file_saved.connect(saved_paths.append)
        editor.save()
        assert len(saved_paths) == 1
        assert str(md_file) in saved_paths[0]

    def test_preview_renders_html(self):
        editor = MarkdownEditor()
        editor.load_content("# Heading\n\nParagraph text.")
        # Force immediate preview update (bypass debounce timer)
        editor._update_preview()
        html = editor.preview_pane.toHtml()
        assert "Heading" in html

    def test_load_content_with_file_path(self, tmp_path: Path):
        editor = MarkdownEditor()
        fp = tmp_path / "test.md"
        editor.load_content("content", file_path=fp)
        assert editor.file_path == fp


# ---------------------------------------------------------------------------
# Pure validation and starter content (no Qt needed)
# ---------------------------------------------------------------------------


class TestValidateAssetName:

    def test_valid_names(self):
        assert validate_asset_name("my-command") is None
        assert validate_asset_name("review-pr") is None
        assert validate_asset_name("a") is None
        assert validate_asset_name("123") is None
        assert validate_asset_name("my-hook-2") is None

    def test_empty_name(self):
        assert validate_asset_name("") is not None

    def test_uppercase_rejected(self):
        assert validate_asset_name("MyCommand") is not None

    def test_spaces_rejected(self):
        assert validate_asset_name("my command") is not None

    def test_underscore_rejected(self):
        assert validate_asset_name("my_command") is not None

    def test_leading_hyphen_rejected(self):
        assert validate_asset_name("-bad") is not None

    def test_special_chars_rejected(self):
        assert validate_asset_name("cmd@1") is not None

    def test_too_long(self):
        assert validate_asset_name("a" * 61) is not None
        assert validate_asset_name("a" * 60) is None


class TestStarterContent:

    def test_command_template(self):
        content = starter_content("Claude Commands", "deploy-app")
        assert "/deploy-app" in content
        assert "## Purpose" in content
        assert "## Usage" in content

    def test_skill_template(self):
        content = starter_content("Claude Skills", "code-review")
        assert "Skill: Code Review" in content
        assert "/code-review" in content
        assert "## Trigger" in content

    def test_hook_template(self):
        content = starter_content("Claude Hooks", "security-scan")
        assert "Hook Pack: Security Scan" in content
        assert "## Hooks" in content
        assert "## Posture Compatibility" in content

    def test_workflow_template(self):
        content = starter_content("Workflows", "release-process")
        assert "Release Process" in content
        assert "## Overview" in content


# ---------------------------------------------------------------------------
# Screen CRUD — button state
# ---------------------------------------------------------------------------


class TestButtonState:

    def test_buttons_exist(self):
        screen = LibraryManagerScreen()
        assert screen.new_button is not None
        assert screen.delete_button is not None

    def test_buttons_disabled_initially(self):
        screen = LibraryManagerScreen()
        assert not screen.new_button.isEnabled()
        assert not screen.delete_button.isEnabled()

    def test_new_enabled_for_editable_category(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select the "Workflows" category node
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        assert screen.new_button.isEnabled()

    def test_new_disabled_when_no_selection(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # No item selected — button should be disabled
        screen.tree.setCurrentItem(None)
        assert not screen.new_button.isEnabled()

    def test_delete_enabled_for_file_in_editable_category(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select a hook file
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item.child(0))
                break
        assert screen.delete_button.isEnabled()

    def test_delete_disabled_for_category_node(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        assert not screen.delete_button.isEnabled()


# ---------------------------------------------------------------------------
# Screen CRUD — create operations
# ---------------------------------------------------------------------------

_INPUT_DIALOG = "foundry_app.ui.screens.library_manager.QInputDialog.getText"
_MSG_WARNING = "foundry_app.ui.screens.library_manager.QMessageBox.warning"


class TestCreateAsset:

    def test_create_command(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select Claude Commands category
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("my-new-cmd", True)):
            screen._on_new_asset()
        created = lib / "claude" / "commands" / "my-new-cmd.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "/my-new-cmd" in content

    def test_create_command_auto_selects(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select Claude Commands category
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("my-new-cmd", True)):
            screen._on_new_asset()
        # The new command should be auto-selected in the tree
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "my-new-cmd.md"
        # Its file path should point to the created file
        created = lib / "claude" / "commands" / "my-new-cmd.md"
        assert current.data(0, 0x0100) == str(created)  # Qt.ItemDataRole.UserRole

    def test_create_command_shows_content_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("deploy-app", True)):
            screen._on_new_asset()
        # The editor should show the starter content with the command name
        editor_text = screen.editor_widget.toPlainText()
        assert "/deploy-app" in editor_text

    def test_create_skill(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("my-skill", True)):
            screen._on_new_asset()
        created = lib / "claude" / "skills" / "my-skill" / "SKILL.md"
        assert created.is_file()
        assert "Skill: My Skill" in created.read_text(encoding="utf-8")

    def test_create_hook(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("my-hook", True)):
            screen._on_new_asset()
        created = lib / "claude" / "hooks" / "my-hook.md"
        assert created.is_file()
        assert "Hook Pack:" in created.read_text(encoding="utf-8")

    def test_create_workflow(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("release-notes", True)):
            screen._on_new_asset()
        created = lib / "workflows" / "release-notes.md"
        assert created.is_file()
        assert "Release Notes" in created.read_text(encoding="utf-8")

    def test_create_duplicate_command_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("review-pr", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_duplicate_skill_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("handoff", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_invalid_name_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("Bad Name!", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()
        # No file created
        assert not (lib / "workflows" / "Bad Name!.md").exists()

    def test_create_cancelled_does_nothing(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        before_count = len(list((lib / "workflows").iterdir()))
        with patch(_INPUT_DIALOG, return_value=("", False)):
            screen._on_new_asset()
        assert len(list((lib / "workflows").iterdir())) == before_count

    def test_tree_refreshes_after_create(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Count hooks before
        hooks_item = None
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                hooks_item = item
                break
        before = hooks_item.childCount()
        screen.tree.setCurrentItem(hooks_item)
        with patch(_INPUT_DIALOG, return_value=("new-hook", True)):
            screen._on_new_asset()
        # Re-find after refresh
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                hooks_item = item
                break
        assert hooks_item.childCount() == before + 1

    def test_create_hook_auto_selects_new_item(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("auto-select-hook", True)):
            screen._on_new_asset()
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "auto-select-hook.md"

    def test_create_hook_shows_content_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("editor-hook", True)):
            screen._on_new_asset()
        editor_text = screen.editor_widget.editor.toPlainText()
        assert "Hook Pack: Editor Hook" in editor_text
        assert "## Hooks" in editor_text

    def test_create_hook_duplicate_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("pre-commit-lint", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()


# ---------------------------------------------------------------------------
# Workflow Create — end-to-end (BEAN-094)
# ---------------------------------------------------------------------------


class TestWorkflowCreate:

    def test_create_workflow_file_on_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("deploy-guide", True)):
            screen._on_new_asset()
        created = lib / "workflows" / "deploy-guide.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "# Deploy Guide" in content
        assert "## Overview" in content


# ---------------------------------------------------------------------------
# Skill create — auto-selection and editor integration
# ---------------------------------------------------------------------------


class TestSkillCreateAutoSelect:

    def test_skill_create_auto_selects_new_item(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("deploy-guide", True)):
            screen._on_new_asset()
        created = lib / "workflows" / "deploy-guide.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "# Deploy Guide" in content
        assert "## Overview" in content

    def test_create_workflow_auto_selects_in_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("ci-pipeline", True)):
            screen._on_new_asset()
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "ci-pipeline.md"

    def test_create_workflow_shows_content_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("release-process", True)):
            screen._on_new_asset()
        editor_text = screen.editor_widget.editor.toPlainText()
        assert "# Release Process" in editor_text
        assert "## Overview" in editor_text

    def test_skill_create_shows_content_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("deploy-hook", True)):
            screen._on_new_asset()
        editor_text = screen.editor_widget.editor.toPlainText()
        assert "Skill: Deploy Hook" in editor_text
        assert "/deploy-hook" in editor_text

    def test_create_workflow_tree_shows_new_item(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                before = item.childCount()
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("hotfix-guide", True)):
            screen._on_new_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                assert item.childCount() == before + 1
                child_names = [item.child(j).text(0) for j in range(item.childCount())]
                assert "hotfix-guide.md" in child_names
                break

    def test_skill_create_updates_file_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("deploy-hook", True)):
            screen._on_new_asset()
        assert "SKILL.md" in screen.file_label.text()

    def test_create_duplicate_workflow_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("default", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_workflow_invalid_name_rejected(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        before_count = len(list((lib / "workflows").iterdir()))
        with (
            patch(_INPUT_DIALOG, return_value=("My Workflow!", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()
        assert len(list((lib / "workflows").iterdir())) == before_count

    def test_create_workflow_cancelled_does_nothing(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        before_count = len(list((lib / "workflows").iterdir()))
        with patch(_INPUT_DIALOG, return_value=("", False)):
            screen._on_new_asset()
        assert len(list((lib / "workflows").iterdir())) == before_count

    def test_create_workflow_file_label_shows_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("branching-strategy", True)):
            screen._on_new_asset()
        assert "branching-strategy.md" in screen.file_label.text()

    def test_skill_create_from_existing_skill_node(self, tmp_path: Path):
        """Creating a skill while a sibling skill node is selected."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Select existing skill directory node (handoff)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item.child(0))  # handoff dir
                break
        with patch(_INPUT_DIALOG, return_value=("code-review", True)):
            screen._on_new_asset()
        created = lib / "claude" / "skills" / "code-review" / "SKILL.md"
        assert created.is_file()
        assert "Skill: Code Review" in created.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Screen CRUD — delete operations
# ---------------------------------------------------------------------------

_MSG_QUESTION = "foundry_app.ui.screens.library_manager.QMessageBox.question"


class TestDeleteAsset:

    def test_delete_command_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "commands" / "review-pr.md"
        assert target.is_file()
        # Select the file in the tree
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_hook_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "hooks" / "pre-commit-lint.md"
        assert target.is_file()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Hooks":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_workflow_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "workflows" / "default.md"
        assert target.is_file()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Workflows":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_skill_directory(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "skills" / "handoff"
        assert target.is_dir()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                # Select skill dir node (first child = "handoff" dir)
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_skill_cancelled_keeps_directory(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "skills" / "handoff"
        assert target.is_dir()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_dir()

    def test_delete_skill_confirmation_shows_name(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(
            _MSG_QUESTION, return_value=QMessageBox.StandardButton.No
        ) as mock_q:
            screen._on_delete_asset()
        msg = mock_q.call_args[0][2]
        assert "handoff" in msg

    def test_tree_refreshes_after_skill_delete(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                assert item.childCount() == 1
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                assert item.childCount() == 0
                break

    def test_delete_button_enabled_for_skill_dir(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item.child(0))
                break
        assert screen.delete_button.isEnabled()

    def test_delete_cancelled_keeps_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "claude" / "commands" / "review-pr.md"
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_file()

    def test_tree_refreshes_after_delete(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                assert item.childCount() == 1
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Commands":
                assert item.childCount() == 0
                break



# ---------------------------------------------------------------------------
# Persona starter templates (pure logic, no Qt)
# ---------------------------------------------------------------------------


class TestPersonaStarterFiles:

    def test_returns_three_files(self):
        files = persona_starter_files("my-agent")
        assert set(files.keys()) == {"persona.md", "outputs.md", "prompts.md"}

    def test_persona_md_has_sections(self):
        files = persona_starter_files("data-engineer")
        content = files["persona.md"]
        assert "# Persona: Data Engineer" in content
        assert "## Mission" in content
        assert "## Scope" in content
        assert "## Operating Principles" in content
        assert "## Definition of Done" in content

    def test_outputs_md_has_sections(self):
        files = persona_starter_files("data-engineer")
        content = files["outputs.md"]
        assert "Data Engineer -- Outputs" in content
        assert "## 1. Primary Deliverable" in content

    def test_prompts_md_has_sections(self):
        files = persona_starter_files("data-engineer")
        content = files["prompts.md"]
        assert "Data Engineer -- Prompts" in content
        assert "## Activation Prompt" in content
        assert "## Task Prompts" in content
        assert "## Handoff Prompts" in content


# ---------------------------------------------------------------------------
# Persona CRUD -- create operations
# ---------------------------------------------------------------------------

_INPUT_DIALOG2 = "foundry_app.ui.screens.library_manager.QInputDialog.getText"
_MSG_WARNING2 = "foundry_app.ui.screens.library_manager.QMessageBox.warning"
_MSG_QUESTION2 = "foundry_app.ui.screens.library_manager.QMessageBox.question"


class TestCreatePersona:

    def test_create_persona_creates_directory_structure(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        with patch(_INPUT_DIALOG2, return_value=("my-agent", True)):
            screen._on_new_asset()
        persona_dir = lib / "personas" / "my-agent"
        assert persona_dir.is_dir()
        assert (persona_dir / "persona.md").is_file()
        assert (persona_dir / "outputs.md").is_file()
        assert (persona_dir / "prompts.md").is_file()
        assert (persona_dir / "templates").is_dir()

    def test_create_persona_starter_content(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        with patch(_INPUT_DIALOG2, return_value=("my-agent", True)):
            screen._on_new_asset()
        persona_md = (lib / "personas" / "my-agent" / "persona.md").read_text(
            encoding="utf-8"
        )
        assert "# Persona: My Agent" in persona_md
        assert "## Mission" in persona_md

    def test_create_duplicate_persona_shows_warning(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        with (
            patch(_INPUT_DIALOG2, return_value=("developer", True)),
            patch(_MSG_WARNING2) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_persona_invalid_name_shows_warning(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        with (
            patch(_INPUT_DIALOG2, return_value=("Bad Name!", True)),
            patch(_MSG_WARNING2) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()
        assert not (lib / "personas" / "Bad Name!").exists()

    def test_tree_refreshes_after_persona_create(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.text(0) == "Personas"
        before = personas_item.childCount()
        screen.tree.setCurrentItem(personas_item)
        with patch(_INPUT_DIALOG2, return_value=("new-agent", True)):
            screen._on_new_asset()
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.childCount() == before + 1

    def test_new_persona_auto_selected_in_editor(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        with patch(_INPUT_DIALOG2, return_value=("my-agent", True)):
            screen._on_new_asset()
        # The new persona's persona.md should be loaded in the editor
        editor_text = screen.editor_widget.editor.toPlainText()
        assert "# Persona: My Agent" in editor_text
        assert "persona.md" in screen.file_label.text()


# ---------------------------------------------------------------------------
# Persona CRUD -- delete operations
# ---------------------------------------------------------------------------


class TestDeletePersona:

    def test_delete_persona_directory(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "personas" / "developer"
        assert target.is_dir()
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item.child(0))
        with patch(_MSG_QUESTION2, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_persona_cancelled_keeps_directory(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "personas" / "developer"
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item.child(0))
        with patch(_MSG_QUESTION2, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_dir()

    def test_delete_persona_confirmation_message(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item.child(0))
        with patch(
            _MSG_QUESTION2, return_value=QMessageBox.StandardButton.No
        ) as mock_q:
            screen._on_delete_asset()
        call_args = mock_q.call_args
        msg = call_args[0][2]
        assert "developer" in msg
        assert "all its files" in msg

    def test_tree_refreshes_after_persona_delete(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.childCount() == 1
        screen.tree.setCurrentItem(personas_item.child(0))
        with patch(_MSG_QUESTION2, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        personas_item = screen.tree.topLevelItem(0)
        assert personas_item.childCount() == 0


# ---------------------------------------------------------------------------
# Persona button state
# ---------------------------------------------------------------------------


class TestPersonaButtonState:

    def test_new_enabled_for_personas_category(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        screen.tree.setCurrentItem(screen.tree.topLevelItem(0))
        assert screen.new_button.isEnabled()

    def test_delete_enabled_for_persona_directory(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        screen.tree.setCurrentItem(personas_item.child(0))
        assert screen.delete_button.isEnabled()


# ---------------------------------------------------------------------------
# Persona file editing
# ---------------------------------------------------------------------------


class TestPersonaFileEditing:

    def test_clicking_persona_md_opens_in_editor(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "persona.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Developer persona" in screen.editor_widget.editor.toPlainText()

    def test_clicking_outputs_md_opens_in_editor(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "outputs.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Outputs" in screen.editor_widget.editor.toPlainText()


# ---------------------------------------------------------------------------
# Template starter content (pure logic, no Qt)
# ---------------------------------------------------------------------------


class TestTemplateStarterContent:

    def test_shared_template_content(self):
        content = starter_content("Shared Templates", "risk-log")
        assert "# Risk Log" in content
        assert "## Purpose" in content
        assert "## Checklist" in content
        assert "## Definition of Done" in content

    def test_persona_template_content(self):
        content = starter_content("_persona_template", "code-review")
        assert "# Code Review" in content
        assert "## Purpose" in content

    def test_starter_template_has_metadata_table(self):
        content = starter_content("Shared Templates", "test-plan")
        assert "| **Category** |" in content
        assert "| **Version** |" in content

    def test_starter_template_constant(self):
        assert "## Purpose" in STARTER_TEMPLATE
        assert "## Checklist" in STARTER_TEMPLATE
        assert "## Definition of Done" in STARTER_TEMPLATE


# ---------------------------------------------------------------------------
# Template button state
# ---------------------------------------------------------------------------


class TestTemplateButtonState:

    def test_new_enabled_for_shared_templates_category(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        assert screen.new_button.isEnabled()

    def test_new_enabled_for_shared_template_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                if item.childCount() > 0:
                    screen.tree.setCurrentItem(item.child(0))
                break
        assert screen.new_button.isEnabled()

    def test_delete_enabled_for_shared_template_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                # Find a file child (CLAUDE.md.j2)
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.data(0, 0x0100) is not None:  # Qt.ItemDataRole.UserRole
                        screen.tree.setCurrentItem(child)
                        break
                break
        assert screen.delete_button.isEnabled()

    def test_new_enabled_for_persona_templates_dir(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to Personas > developer > templates
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                screen.tree.setCurrentItem(child)
                break
        assert screen.new_button.isEnabled()

    def test_delete_enabled_for_persona_template_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to Personas > developer > templates > impl.md.j2
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                if child.childCount() > 0:
                    screen.tree.setCurrentItem(child.child(0))
                break
        assert screen.delete_button.isEnabled()


# ---------------------------------------------------------------------------
# Template CRUD — create operations
# ---------------------------------------------------------------------------


class TestCreateTemplate:

    def test_create_shared_template(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("risk-log", True)):
            screen._on_new_asset()
        created = lib / "templates" / "risk-log.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "# Risk Log" in content
        assert "## Purpose" in content

    def test_create_persona_template(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to Personas > developer > templates
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                screen.tree.setCurrentItem(child)
                break
        with patch(_INPUT_DIALOG, return_value=("pr-review", True)):
            screen._on_new_asset()
        created = lib / "personas" / "developer" / "templates" / "pr-review.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "# Pr Review" in content

    def test_create_template_duplicate_shows_warning(self, tmp_path):
        lib = _create_library(tmp_path)
        # Create a template first
        (lib / "templates" / "existing.md").write_text("existing", encoding="utf-8")
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("existing", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_template_invalid_name_shows_warning(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("Bad Name!", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_template_cancelled_does_nothing(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        before_count = len(list((lib / "templates").iterdir()))
        with patch(_INPUT_DIALOG, return_value=("", False)):
            screen._on_new_asset()
        assert len(list((lib / "templates").iterdir())) == before_count

    def test_tree_refreshes_after_template_create(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                before = item.childCount()
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("new-template", True)):
            screen._on_new_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                assert item.childCount() == before + 1
                break

    def test_new_template_auto_selected_after_create(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("auto-select", True)):
            screen._on_new_asset()
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "auto-select.md"
        # Editor should show the starter content
        assert "# Auto Select" in screen.editor_widget.editor.toPlainText()
        assert "## Purpose" in screen.editor_widget.editor.toPlainText()

    def test_new_persona_template_auto_selected_after_create(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                screen.tree.setCurrentItem(child)
                break
        with patch(_INPUT_DIALOG, return_value=("checklist", True)):
            screen._on_new_asset()
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "checklist.md"
        assert "# Checklist" in screen.editor_widget.editor.toPlainText()


# ---------------------------------------------------------------------------
# Template CRUD — delete operations
# ---------------------------------------------------------------------------


class TestDeleteTemplate:

    def test_delete_shared_template_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "templates" / "CLAUDE.md.j2"
        assert target.is_file()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                # Find CLAUDE.md.j2 file
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.text(0) == "CLAUDE.md.j2":
                        screen.tree.setCurrentItem(child)
                        break
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_persona_template_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "personas" / "developer" / "templates" / "impl.md.j2"
        assert target.is_file()
        # Navigate to Personas > developer > templates > impl.md.j2
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                for j in range(child.childCount()):
                    tpl = child.child(j)
                    if tpl.text(0) == "impl.md.j2":
                        screen.tree.setCurrentItem(tpl)
                        break
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_template_cancelled_keeps_file(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "templates" / "CLAUDE.md.j2"
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.text(0) == "CLAUDE.md.j2":
                        screen.tree.setCurrentItem(child)
                        break
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_file()

    def test_tree_refreshes_after_template_delete(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                before = item.childCount()
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.text(0) == "CLAUDE.md.j2":
                        screen.tree.setCurrentItem(child)
                        break
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                assert item.childCount() == before - 1
                break


# ---------------------------------------------------------------------------
# Template visual distinction
# ---------------------------------------------------------------------------


class TestTemplateVisualDistinction:

    def test_shared_template_items_are_italic(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Shared Templates":
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.data(0, 0x0100) is not None:  # file node
                        assert child.font(0).italic(), (
                            f"Shared template file '{child.text(0)}' should be italic"
                        )
                break

    def test_persona_template_items_are_not_italic(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                for j in range(child.childCount()):
                    tpl = child.child(j)
                    assert not tpl.font(0).italic(), (
                        f"Persona template '{tpl.text(0)}' should not be italic"
                    )
                break


# ---------------------------------------------------------------------------
# Stack CRUD — create operations
# ---------------------------------------------------------------------------


class TestStackCreate:

    def test_create_stack_at_category_level(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("rust-actix", True)):
            screen._on_new_asset()
        stack_dir = lib / "stacks" / "rust-actix"
        assert stack_dir.is_dir()
        conv = stack_dir / "conventions.md"
        assert conv.is_file()
        content = conv.read_text(encoding="utf-8")
        assert "Rust Actix Stack Conventions" in content

    def test_create_new_file_from_stack_dir(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                stack_dir_node = item.child(0)  # python-fastapi dir
                screen.tree.setCurrentItem(stack_dir_node.child(0))  # file inside
                break
        with patch(_INPUT_DIALOG, return_value=("security", True)):
            screen._on_new_asset()
        created = lib / "stacks" / "python-fastapi" / "security.md"
        assert created.is_file()
        content = created.read_text(encoding="utf-8")
        assert "# Security" in content
        assert "## Guidelines" in content

    def test_create_new_file_from_file_inside_stack(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                stack_dir = item.child(0)  # python-fastapi
                screen.tree.setCurrentItem(stack_dir.child(0))  # conventions.md
                break
        with patch(_INPUT_DIALOG, return_value=("performance", True)):
            screen._on_new_asset()
        created = lib / "stacks" / "python-fastapi" / "performance.md"
        assert created.is_file()

    def test_create_duplicate_stack_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("python-fastapi", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_duplicate_stack_file_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                stack_dir_node = item.child(0)  # python-fastapi dir
                screen.tree.setCurrentItem(stack_dir_node.child(0))  # file inside
                break
        with (
            patch(_INPUT_DIALOG, return_value=("conventions", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()

    def test_create_stack_invalid_name_shows_warning(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with (
            patch(_INPUT_DIALOG, return_value=("Bad Name!", True)),
            patch(_MSG_WARNING) as mock_warn,
        ):
            screen._on_new_asset()
        mock_warn.assert_called_once()
        assert not (lib / "stacks" / "Bad Name!").exists()

    def test_create_stack_cancelled_does_nothing(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        before_count = len(list((lib / "stacks").iterdir()))
        with patch(_INPUT_DIALOG, return_value=("", False)):
            screen._on_new_asset()
        assert len(list((lib / "stacks").iterdir())) == before_count

    def test_tree_refreshes_after_stack_create(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                before = item.childCount()
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("new-stack", True)):
            screen._on_new_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                assert item.childCount() == before + 1
                break

    def test_new_stack_auto_selected_after_create(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("go-fiber", True)):
            screen._on_new_asset()
        current = screen.tree.currentItem()
        assert current is not None
        assert current.text(0) == "conventions.md"
        expected_path = str(lib / "stacks" / "go-fiber" / "conventions.md")
        assert current.data(0, 0x0100) == expected_path  # Qt.ItemDataRole.UserRole

    def test_new_stack_content_shown_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("go-fiber", True)):
            screen._on_new_asset()
        editor_text = screen.editor_widget.editor.toPlainText()
        assert "Go Fiber Stack Conventions" in editor_text

    def test_new_stack_parent_expanded_in_tree(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        with patch(_INPUT_DIALOG, return_value=("go-fiber", True)):
            screen._on_new_asset()
        # The stack directory node should be expanded
        current = screen.tree.currentItem()
        assert current is not None
        stack_node = current.parent()
        assert stack_node is not None
        assert stack_node.text(0) == "go-fiber"
        assert stack_node.isExpanded()


# ---------------------------------------------------------------------------
# Stack CRUD — delete operations
# ---------------------------------------------------------------------------


class TestStackDelete:

    def test_delete_stack_directory(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "stacks" / "python-fastapi"
        assert target.is_dir()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item.child(0))  # python-fastapi dir
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_stack_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "stacks" / "python-fastapi" / "testing.md"
        assert target.is_file()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                stack_dir = item.child(0)
                for j in range(stack_dir.childCount()):
                    child = stack_dir.child(j)
                    if child.text(0) == "testing.md":
                        screen.tree.setCurrentItem(child)
                        break
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        assert not target.exists()

    def test_delete_stack_cancelled_keeps_dir(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        target = lib / "stacks" / "python-fastapi"
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.No):
            screen._on_delete_asset()
        assert target.is_dir()

    def test_tree_refreshes_after_stack_delete(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                assert item.childCount() == 1
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(_MSG_QUESTION, return_value=QMessageBox.StandardButton.Yes):
            screen._on_delete_asset()
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                assert item.childCount() == 0
                break


# Stack Read — BEAN-085
# ---------------------------------------------------------------------------


class TestStackRead:
    """Verify stack listing in tree and file loading into editor (BEAN-085)."""

    def _find_stacks_item(self, screen):
        """Return the top-level 'Stacks' tree item."""
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                return item
        return None

    def test_stacks_category_lists_all_stacks(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        assert stacks_item is not None
        # _create_library creates one stack: python-fastapi
        assert stacks_item.childCount() == 1
        assert stacks_item.child(0).text(0) == "python-fastapi"

    def test_stacks_category_lists_multiple_stacks(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        # Add a second stack
        second = lib / "stacks" / "rust-actix"
        second.mkdir(parents=True)
        (second / "conventions.md").write_text("# Rust Actix", encoding="utf-8")
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        assert stacks_item.childCount() == 2
        child_names = [stacks_item.child(i).text(0) for i in range(stacks_item.childCount())]
        assert "python-fastapi" in child_names
        assert "rust-actix" in child_names

    def test_stack_directory_shows_nested_files(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        stack_dir_item = stacks_item.child(0)  # python-fastapi
        # _create_library adds stack.md, conventions.md, testing.md
        assert stack_dir_item.childCount() == 3
        file_names = sorted(
            stack_dir_item.child(i).text(0) for i in range(stack_dir_item.childCount())
        )
        assert file_names == ["conventions.md", "stack.md", "testing.md"]

    def test_clicking_stack_file_loads_content_in_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        stack_dir_item = stacks_item.child(0)
        # Find and select stack.md
        for i in range(stack_dir_item.childCount()):
            child = stack_dir_item.child(i)
            if child.text(0) == "stack.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Python + FastAPI" in screen.editor_widget.editor.toPlainText()

    def test_clicking_stack_conventions_loads_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        stack_dir_item = stacks_item.child(0)
        for i in range(stack_dir_item.childCount()):
            child = stack_dir_item.child(i)
            if child.text(0) == "conventions.md":
                screen.tree.setCurrentItem(child)
                break
        assert "Conventions" in screen.editor_widget.editor.toPlainText()

    def test_file_path_label_updates_for_stack_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        stack_dir_item = stacks_item.child(0)
        for i in range(stack_dir_item.childCount()):
            child = stack_dir_item.child(i)
            if child.text(0) == "testing.md":
                screen.tree.setCurrentItem(child)
                break
        label_text = screen.file_label.text()
        assert "testing.md" in label_text
        assert "stacks" in label_text

    def test_selecting_stack_directory_clears_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        # First select a file to load content
        stack_dir_item = stacks_item.child(0)
        screen.tree.setCurrentItem(stack_dir_item.child(0))
        assert screen.editor_widget.editor.toPlainText() != ""
        # Now select the directory node — editor should clear
        screen.tree.setCurrentItem(stack_dir_item)
        assert screen.editor_widget.editor.toPlainText() == ""

    def test_live_preview_renders_stack_markdown(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        stack_dir_item = stacks_item.child(0)
        for i in range(stack_dir_item.childCount()):
            child = stack_dir_item.child(i)
            if child.text(0) == "stack.md":
                screen.tree.setCurrentItem(child)
                break
        # Force preview update (bypass debounce)
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "Python" in html

    def test_empty_stacks_directory_shows_no_children(self, tmp_path: Path):
        lib = tmp_path / "empty-lib"
        (lib / "stacks").mkdir(parents=True)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        stacks_item = self._find_stacks_item(screen)
        assert stacks_item is not None
        assert stacks_item.childCount() == 0

    def test_stack_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks_cat = next(c for c in tree if c["name"] == "Stacks")
        stack_dir = stacks_cat["children"][0]  # python-fastapi
        assert stack_dir["path"] is None  # directory node
        for file_node in stack_dir["children"]:
            assert file_node["path"] is not None
            assert file_node["path"].endswith(".md")

    def test_stack_directory_node_has_no_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        tree = _build_file_tree(lib)
        stacks_cat = next(c for c in tree if c["name"] == "Stacks")
        stack_dir = stacks_cat["children"][0]
        assert stack_dir["name"] == "python-fastapi"
        assert stack_dir["path"] is None


# ---------------------------------------------------------------------------
# Persona Update — end-to-end integration tests (BEAN-083)
# ---------------------------------------------------------------------------


def _select_persona_file(screen, filename="persona.md"):
    """Navigate the tree to Personas > developer > <filename> and select it."""
    personas_item = screen.tree.topLevelItem(0)
    dev_item = personas_item.child(0)
    for i in range(dev_item.childCount()):
        child = dev_item.child(i)
        if child.text(0) == filename:
            screen.tree.setCurrentItem(child)
            return child
    return None


class TestPersonaUpdate:
    """End-to-end tests for persona update: select -> edit -> save -> verify."""

    def test_select_persona_loads_content_into_editor(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        assert "Developer persona" in screen.editor_widget.editor.toPlainText()
        assert screen.editor_widget.file_path is not None

    def test_edit_persona_sets_dirty_state(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        assert screen.editor_widget.dirty is False
        screen.editor_widget.editor.setPlainText("# Updated persona content")
        assert screen.editor_widget.dirty is True

    def test_edit_persona_shows_modified_indicator(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        assert screen.editor_widget.dirty_label.text() == ""
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_save_persona_persists_to_disk(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        new_content = "# Updated Developer\n\nNew mission statement."
        screen.editor_widget.editor.setPlainText(new_content)
        result = screen.editor_widget.save()
        assert result is True
        disk_content = (lib / "personas" / "developer" / "persona.md").read_text(
# ---------------------------------------------------------------------------
# Skill update — end-to-end editing flow (BEAN-103)
# ---------------------------------------------------------------------------


def _select_skill_file(screen: LibraryManagerScreen) -> None:
    """Navigate the tree to Claude Skills > handoff > SKILL.md and select it."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Claude Skills":
            handoff_dir = item.child(0)  # "handoff" directory node
            for j in range(handoff_dir.childCount()):
                child = handoff_dir.child(j)
                if child.text(0) == "SKILL.md":
                    screen.tree.setCurrentItem(child)
                    return
    raise AssertionError("SKILL.md not found in tree")


class TestSkillUpdate:

    def test_selecting_skill_loads_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        assert "Handoff skill" in screen.editor_widget.editor.toPlainText()

    def test_selecting_skill_sets_file_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        assert "SKILL.md" in screen.file_label.text()

    def test_editing_skill_triggers_dirty_state(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        assert screen.editor_widget.dirty is False
        screen.editor_widget.editor.setPlainText("# Updated skill content")
        assert screen.editor_widget.dirty is True
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_save_persists_skill_to_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        new_content = "# Updated Handoff Skill\n\nNew description."
        screen.editor_widget.editor.setPlainText(new_content)
        assert screen.editor_widget.dirty is True
        result = screen.editor_widget.save()
        assert result is True
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""
        # Verify on disk
        disk_content = (lib / "claude" / "skills" / "handoff" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert disk_content == new_content

    def test_save_persona_clears_dirty_state(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.dirty is True
        screen.editor_widget.save()
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""

    def test_save_persona_enables_then_disables_save_button(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.save()
        assert not screen.editor_widget.save_button.isEnabled()

    def test_revert_persona_restores_original_content(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        original = screen.editor_widget.editor.toPlainText()
        screen.editor_widget.editor.setPlainText("# Completely different")
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == original

    def test_revert_persona_clears_dirty_state(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.dirty is True
        screen.editor_widget.revert()
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""

    def test_revert_persona_does_not_alter_disk(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        original_disk = (lib / "personas" / "developer" / "persona.md").read_text(
            encoding="utf-8"
        )
        screen.editor_widget.editor.setPlainText("# Changed")
        screen.editor_widget.revert()
        after_disk = (lib / "personas" / "developer" / "persona.md").read_text(
            encoding="utf-8"
        )
        assert after_disk == original_disk

    def test_preview_updates_during_persona_editing(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        screen.editor_widget.editor.setPlainText("# New Heading\n\nSome body text.")
# ---------------------------------------------------------------------------
# Command update — end-to-end (BEAN-099)
# ---------------------------------------------------------------------------


def _select_command_file(screen: LibraryManagerScreen) -> None:
    """Select the review-pr.md command node in the tree."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Claude Commands":
            screen.tree.setCurrentItem(item.child(0))
            return
    raise AssertionError("Claude Commands category not found")


class TestCommandUpdate:

    def test_select_command_loads_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert "Review PR" in screen.editor_widget.editor.toPlainText()

    def test_select_command_sets_file_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert "review-pr.md" in screen.file_label.text()

    def test_select_command_sets_file_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert screen.editor_widget.file_path is not None
        assert screen.editor_widget.file_path.name == "review-pr.md"

    def test_edit_command_triggers_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert not screen.editor_widget.dirty
        screen.editor_widget.editor.setPlainText("# Updated content")
        assert screen.editor_widget.dirty
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_save_command_persists_to_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        new_content = "# Updated Review PR\n\nNew instructions."
        screen.editor_widget.editor.setPlainText(new_content)
        result = screen.editor_widget.save()
        assert result is True
        on_disk = (lib / "claude" / "commands" / "review-pr.md").read_text(
            encoding="utf-8"
        )
        assert on_disk == new_content

    def test_save_command_clears_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.dirty
        screen.editor_widget.save()
        assert not screen.editor_widget.dirty
        assert screen.editor_widget.dirty_label.text() == ""

    def test_revert_command_restores_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        original = screen.editor_widget.editor.toPlainText()
        screen.editor_widget.editor.setPlainText("# Totally different")
        assert screen.editor_widget.dirty
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == original
        assert not screen.editor_widget.dirty

    def test_revert_command_clears_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        screen.editor_widget.editor.setPlainText("# Changed")
        screen.editor_widget.revert()
        assert not screen.editor_widget.dirty
        assert screen.editor_widget.dirty_label.text() == ""

    def test_preview_updates_during_command_edit(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        screen.editor_widget.editor.setPlainText("# New Heading\n\nParagraph.")
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "New Heading" in html

    def test_update_outputs_md(self, tmp_path):
        """Verify update works for outputs.md within the same persona."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "outputs.md")
        new_content = "# Updated Outputs\n\nDeliverables list."
        screen.editor_widget.editor.setPlainText(new_content)
        screen.editor_widget.save()
        disk = (lib / "personas" / "developer" / "outputs.md").read_text(
            encoding="utf-8"
        )
        assert disk == new_content

    def test_file_label_shows_persona_path(self, tmp_path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        label = screen.file_label.text()
        assert "personas" in label
        assert "developer" in label
        assert "persona.md" in label

    def test_consecutive_saves_accumulate(self, tmp_path):
        """Multiple edits and saves should each persist."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_persona_file(screen, "persona.md")
        target = lib / "personas" / "developer" / "persona.md"
        # First edit and save
        screen.editor_widget.editor.setPlainText("# Version 1")
        screen.editor_widget.save()
        assert target.read_text(encoding="utf-8") == "# Version 1"
        # Second edit and save
        screen.editor_widget.editor.setPlainText("# Version 2")
        screen.editor_widget.save()
        assert target.read_text(encoding="utf-8") == "# Version 2"


# ---------------------------------------------------------------------------
# Stack Update — end-to-end workflow (BEAN-087)
# ---------------------------------------------------------------------------


def _select_stack_file(screen, stack_name: str, file_name: str):
    """Helper: select a file inside a stack directory in the tree."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Stacks":
            for j in range(item.childCount()):
                stack_dir = item.child(j)
                if stack_dir.text(0) == stack_name:
                    for k in range(stack_dir.childCount()):
                        child = stack_dir.child(k)
                        if child.text(0) == file_name:
                            screen.tree.setCurrentItem(child)
                            return child
    return None


class TestStackUpdate:

    def test_selecting_stack_file_loads_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert "Conventions" in screen.editor_widget.editor.toPlainText()

    def test_selecting_stack_file_shows_file_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert "conventions.md" in screen.file_label.text()

    def test_editing_stack_triggers_dirty_state(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert screen.editor_widget.dirty is False
        screen.editor_widget.editor.setPlainText("# Updated conventions")
        assert screen.editor_widget.dirty is True
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_save_stack_persists_to_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        screen.editor_widget.editor.setPlainText("# New conventions content")
        assert screen.editor_widget.dirty is True
        result = screen.editor_widget.save()
        assert result is True
        assert screen.editor_widget.dirty is False
        disk_content = (lib / "stacks" / "python-fastapi" / "conventions.md").read_text(
            encoding="utf-8"
        )
        assert disk_content == "# New conventions content"

    def test_save_clears_dirty_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.dirty_label.text() == "Modified"
        screen.editor_widget.save()
        assert screen.editor_widget.dirty_label.text() == ""

    def test_revert_stack_restores_original(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        original = screen.editor_widget.editor.toPlainText()
        screen.editor_widget.editor.setPlainText("unsaved changes")
    def test_revert_restores_original_skill_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        original = screen.editor_widget.editor.toPlainText()
        screen.editor_widget.editor.setPlainText("# Totally different content")
        assert screen.editor_widget.dirty is True
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == original
        assert screen.editor_widget.dirty is False

    def test_revert_clears_dirty_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.dirty_label.text() == "Modified"
        screen.editor_widget.revert()
        assert screen.editor_widget.dirty_label.text() == ""

    def test_preview_updates_for_stack(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        screen.editor_widget.editor.setPlainText("# Stack Preview Test")
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "Stack Preview Test" in html

    def test_save_button_enabled_when_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.save_button.isEnabled()

    def test_revert_button_enabled_when_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert not screen.editor_widget.revert_button.isEnabled()
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.revert_button.isEnabled()

    def test_update_different_stack_files(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Edit and save stack.md
        _select_stack_file(screen, "python-fastapi", "stack.md")
        screen.editor_widget.editor.setPlainText("# Updated stack")
        screen.editor_widget.save()
        # Edit and save testing.md
        _select_stack_file(screen, "python-fastapi", "testing.md")
        screen.editor_widget.editor.setPlainText("# Updated testing")
        screen.editor_widget.save()
        # Verify both persisted
        assert (lib / "stacks" / "python-fastapi" / "stack.md").read_text(
            encoding="utf-8"
        ) == "# Updated stack"
        assert (lib / "stacks" / "python-fastapi" / "testing.md").read_text(
            encoding="utf-8"
        ) == "# Updated testing"

    def test_switching_stack_files_loads_new_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        assert "Conventions" in screen.editor_widget.editor.toPlainText()
        _select_stack_file(screen, "python-fastapi", "testing.md")
        assert "Testing" in screen.editor_widget.editor.toPlainText()

    def test_dirty_state_resets_on_file_switch(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_stack_file(screen, "python-fastapi", "conventions.md")
        screen.editor_widget.editor.setPlainText("unsaved edits")
        assert screen.editor_widget.dirty is True
        # Switch to a different file — editor reloads, dirty resets
        _select_stack_file(screen, "python-fastapi", "testing.md")
        assert screen.editor_widget.dirty is False


# ---------------------------------------------------------------------------
# Template Update — end-to-end (BEAN-091)
# ---------------------------------------------------------------------------


def _select_shared_template(screen: LibraryManagerScreen, filename: str):
    """Helper: select a file node under the Shared Templates category."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Shared Templates":
            for j in range(item.childCount()):
                child = item.child(j)
                if child.text(0) == filename:
                    screen.tree.setCurrentItem(child)
                    return


# ---------------------------------------------------------------------------
# Workflow Update — BEAN-095
# ---------------------------------------------------------------------------


def _select_workflow_file(screen: LibraryManagerScreen, filename: str = "default.md"):
    """Helper to select a workflow file node in the tree by filename."""
    for i in range(screen.tree.topLevelItemCount()):
        item = screen.tree.topLevelItem(i)
        if item.text(0) == "Workflows":
            for j in range(item.childCount()):
                child = item.child(j)
                if child.text(0) == filename:
                    screen.tree.setCurrentItem(child)
                    return child
            # Check subdirectories too
            for j in range(item.childCount()):
                child = item.child(j)
                if child.data(0, 0x0100) is None:  # directory node
                    for k in range(child.childCount()):
                        sub = child.child(k)
                        if sub.text(0) == filename:
                            screen.tree.setCurrentItem(sub)
                            return sub
    return None


class TestTemplateUpdate:
    """BEAN-091: Verify the template update workflow end-to-end."""

    def test_selecting_shared_template_loads_content(self, tmp_path: Path):
        """AC: Selecting a template loads its content into the editor."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert "Claude template" in screen.editor_widget.editor.toPlainText()

    def test_selecting_shared_template_sets_file_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert screen.editor_widget.file_path is not None
        assert screen.editor_widget.file_path.name == "CLAUDE.md.j2"

    def test_selecting_template_in_subdirectory(self, tmp_path: Path):
        """Templates in subdirectories (e.g. shared/) also load correctly."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "adr.md")
        assert "ADR template" in screen.editor_widget.editor.toPlainText()

    def test_editing_template_triggers_dirty_state(self, tmp_path: Path):
        """AC: Editing text triggers the dirty/modified state indicator."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert screen.editor_widget.dirty is False
        screen.editor_widget.editor.setPlainText("# Modified template")
        assert screen.editor_widget.dirty is True
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_save_persists_template_to_disk(self, tmp_path: Path):
        """AC: Clicking 'Save' persists changes to disk and clears dirty state."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        template_path = lib / "templates" / "CLAUDE.md.j2"
        original = template_path.read_text(encoding="utf-8")
        # Edit
        screen.editor_widget.editor.setPlainText("# Updated template content")
        assert screen.editor_widget.dirty is True
        # Save
        result = screen.editor_widget.save()
        assert result is True
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""
        # Verify disk
        assert template_path.read_text(encoding="utf-8") == "# Updated template content"
        assert template_path.read_text(encoding="utf-8") != original

    def test_save_button_enabled_when_template_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("changed")
    def test_save_button_enabled_when_command_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.dirty_label.text() == ""

    def test_revert_after_disk_change_reads_current_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        screen.editor_widget.editor.setPlainText("unsaved edits")
        # Simulate external edit on disk
        skill_path = lib / "claude" / "skills" / "handoff" / "SKILL.md"
        skill_path.write_text("# Externally modified", encoding="utf-8")
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == "# Externally modified"

    def test_live_preview_updates_on_edit(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        screen.editor_widget.editor.setPlainText("# Preview Test\n\nVisible text.")
        # Force immediate preview update (bypass debounce timer)
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "Preview Test" in html

    def test_save_button_enabled_when_skill_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_skill_file(screen)
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.save_button.isEnabled()

    def test_save_button_disabled_after_save(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        _select_skill_file(screen)
        screen.editor_widget.editor.setPlainText("changed")
        screen.editor_widget.save()
        assert not screen.editor_widget.save_button.isEnabled()

    def test_revert_restores_original_template(self, tmp_path: Path):
        """AC: Clicking 'Revert' restores original content and clears dirty state."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        original = screen.editor_widget.editor.toPlainText()
        # Edit
        screen.editor_widget.editor.setPlainText("# Totally different content")
        assert screen.editor_widget.dirty is True
        # Revert
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == original
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""

    def test_revert_button_enabled_when_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert not screen.editor_widget.revert_button.isEnabled()
        screen.editor_widget.editor.setPlainText("changed")
        assert screen.editor_widget.revert_button.isEnabled()

    def test_revert_button_disabled_after_revert(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        screen.editor_widget.editor.setPlainText("changed")
        screen.editor_widget.revert()
        assert not screen.editor_widget.revert_button.isEnabled()

    def test_preview_updates_on_template_edit(self, tmp_path: Path):
        """AC: The live preview updates in real-time during editing."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        screen.editor_widget.editor.setPlainText("# Preview Heading\n\nSome paragraph.")
        # Force immediate preview update (bypass debounce)
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "Preview Heading" in html

    def test_disk_unchanged_until_save(self, tmp_path: Path):
        """Editing does not write to disk — only explicit save does."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        template_path = lib / "templates" / "CLAUDE.md.j2"
        original = template_path.read_text(encoding="utf-8")
        screen.editor_widget.editor.setPlainText("# Not yet saved")
        # Disk should still have original content
        assert template_path.read_text(encoding="utf-8") == original

    def test_file_saved_signal_emitted_on_template_save(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        screen.editor_widget.editor.setPlainText("changed")
    return None


class TestWorkflowUpdate:

    def test_selecting_workflow_loads_content_into_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert "Default workflow" in screen.editor_widget.editor.toPlainText()

    def test_selecting_workflow_sets_file_path_on_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert screen.editor_widget.file_path is not None
        assert screen.editor_widget.file_path.name == "default.md"

    def test_selecting_workflow_shows_file_label(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert "default.md" in screen.file_label.text()

    def test_editing_workflow_triggers_dirty_state(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert screen.editor_widget.dirty is False
        screen.editor_widget.editor.setPlainText("# Updated workflow")
        assert screen.editor_widget.dirty is True

    def test_editing_workflow_shows_modified_indicator(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert screen.editor_widget.dirty_label.text() == ""
        screen.editor_widget.editor.setPlainText("# Updated workflow")
        assert screen.editor_widget.dirty_label.text() == "Modified"

    def test_saving_workflow_persists_to_disk(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# Updated workflow content")
        result = screen.editor_widget.save()
        assert result is True
        on_disk = (lib / "workflows" / "default.md").read_text(encoding="utf-8")
        assert on_disk == "# Updated workflow content"

    def test_saving_workflow_clears_dirty_state(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# Updated workflow content")
        assert screen.editor_widget.dirty is True
        screen.editor_widget.save()
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""

    def test_saving_workflow_emits_file_saved_signal(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# Updated")
        saved_paths: list[str] = []
        screen.editor_widget.file_saved.connect(saved_paths.append)
        screen.editor_widget.save()
        assert len(saved_paths) == 1
        assert "CLAUDE.md.j2" in saved_paths[0]

    def test_dirty_changed_signal_on_template_edit(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        signals: list[bool] = []
        screen.editor_widget.dirty_changed.connect(signals.append)
        screen.editor_widget.editor.setPlainText("modified")
        assert True in signals

    def test_persona_template_update(self, tmp_path: Path):
        """Persona-level templates can also be edited and saved."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # Navigate to Personas > developer > templates > impl.md.j2
        personas_item = screen.tree.topLevelItem(0)
        dev_item = personas_item.child(0)
        for i in range(dev_item.childCount()):
            child = dev_item.child(i)
            if child.text(0) == "templates":
                for j in range(child.childCount()):
                    tpl = child.child(j)
                    if tpl.text(0) == "impl.md.j2":
                        screen.tree.setCurrentItem(tpl)
                        break
                break
        assert "template" in screen.editor_widget.editor.toPlainText()
        # Edit and save
        screen.editor_widget.editor.setPlainText("# Updated persona template")
        assert screen.editor_widget.dirty is True
        result = screen.editor_widget.save()
        assert result is True
        assert screen.editor_widget.dirty is False
        target = lib / "personas" / "developer" / "templates" / "impl.md.j2"
        assert target.read_text(encoding="utf-8") == "# Updated persona template"

    def test_file_label_shows_template_path(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_shared_template(screen, "CLAUDE.md.j2")
        assert "CLAUDE.md.j2" in screen.file_label.text()
    def test_delete_stack_confirmation_message(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item.child(0))
                break
        with patch(
            _MSG_QUESTION, return_value=QMessageBox.StandardButton.No
        ) as mock_q:
            screen._on_delete_asset()
        call_args = mock_q.call_args
        msg = call_args[0][2]
        assert "python-fastapi" in msg
        assert "all its files" in msg


# ---------------------------------------------------------------------------
# Stack button state
# ---------------------------------------------------------------------------


class TestStackButtonState:

    def test_delete_enabled_for_stack_directory(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item.child(0))
                break
        assert screen.delete_button.isEnabled()

    def test_delete_enabled_for_stack_file(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                stack_dir = item.child(0)
                screen.tree.setCurrentItem(stack_dir.child(0))
                break
        assert screen.delete_button.isEnabled()

    def test_new_enabled_for_stacks_category(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Stacks":
                screen.tree.setCurrentItem(item)
                break
        assert screen.new_button.isEnabled()
        assert "default.md" in saved_paths[0]

    def test_reverting_workflow_restores_original_content(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        original = screen.editor_widget.editor.toPlainText()
        screen.editor_widget.editor.setPlainText("# Modified content")
        screen.editor_widget.revert()
        assert screen.editor_widget.editor.toPlainText() == original

    def test_reverting_workflow_clears_dirty_state(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# Modified content")
        assert screen.editor_widget.dirty is True
        screen.editor_widget.revert()
        assert screen.editor_widget.dirty is False
        assert screen.editor_widget.dirty_label.text() == ""

    def test_workflow_preview_updates_on_edit(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# New Heading\n\nNew paragraph.")
        screen.editor_widget._update_preview()
        html = screen.editor_widget.preview_pane.toHtml()
        assert "New Heading" in html

    def test_save_button_state_tracks_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert not screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.save_button.isEnabled()
        screen.editor_widget.save()
        assert not screen.editor_widget.save_button.isEnabled()

    def test_revert_button_state_tracks_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        assert not screen.editor_widget.revert_button.isEnabled()
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.revert_button.isEnabled()
        screen.editor_widget.revert()
        assert not screen.editor_widget.revert_button.isEnabled()

    def test_workflow_roundtrip_edit_save_reload(self, tmp_path: Path):
        """Full roundtrip: load → edit → save → reload from tree → verify."""
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_workflow_file(screen, "default.md")
        screen.editor_widget.editor.setPlainText("# Fully updated workflow")
        screen.editor_widget.save()
        # Re-select by refreshing tree and selecting again
        screen.refresh_tree()
        _select_workflow_file(screen, "default.md")
        assert screen.editor_widget.editor.toPlainText() == "# Fully updated workflow"
        assert screen.editor_widget.dirty is False
        _select_command_file(screen)
        screen.editor_widget.editor.setPlainText("# Changed")
        screen.editor_widget.save()
        assert not screen.editor_widget.save_button.isEnabled()

    def test_revert_button_enabled_when_command_dirty(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        assert not screen.editor_widget.revert_button.isEnabled()
        screen.editor_widget.editor.setPlainText("# Changed")
        assert screen.editor_widget.revert_button.isEnabled()

    def test_file_saved_signal_emitted(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        screen.editor_widget.editor.setPlainText("# Changed")
        saved: list[str] = []
        screen.editor_widget.file_saved.connect(saved.append)
        screen.editor_widget.save()
        assert len(saved) == 1
        assert "review-pr.md" in saved[0]

    def test_dirty_changed_signal_emitted(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        _select_command_file(screen)
        signals: list[bool] = []
        screen.editor_widget.dirty_changed.connect(signals.append)
        screen.editor_widget.editor.setPlainText("# Changed")
        assert True in signals
    def test_selecting_skill_dir_clears_editor(self, tmp_path: Path):
        lib = _create_library(tmp_path)
        screen = LibraryManagerScreen()
        screen.set_library_root(lib)
        # First select the skill file to load content
        _select_skill_file(screen)
        assert screen.editor_widget.editor.toPlainText() != ""
        # Now select the skill directory node (no file path)
        for i in range(screen.tree.topLevelItemCount()):
            item = screen.tree.topLevelItem(i)
            if item.text(0) == "Claude Skills":
                screen.tree.setCurrentItem(item.child(0))  # handoff dir
                break
        assert screen.editor_widget.editor.toPlainText() == ""
