"""Library Manager screen — tree-based browser with CRUD for library assets."""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    BG_BASE,
    BG_SURFACE,
    BORDER_DEFAULT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

logger = logging.getLogger(__name__)

# Top-level categories mapped to their directory paths relative to library root.
# Order matters — this is the display order in the tree.
LIBRARY_CATEGORIES: list[tuple[str, str]] = [
    ("Personas", "personas"),
    ("Stacks", "stacks"),
    ("Shared Templates", "templates"),
    ("Workflows", "workflows"),
    ("Claude Commands", "claude/commands"),
    ("Claude Skills", "claude/skills"),
    ("Claude Hooks", "claude/hooks"),
]

# Categories that support create/delete operations, mapped to their rel_path.
_EDITABLE_CATEGORIES: dict[str, str] = {
    "Workflows": "workflows",
    "Claude Commands": "claude/commands",
    "Claude Skills": "claude/skills",
    "Claude Hooks": "claude/hooks",
}

# ---------------------------------------------------------------------------
# Starter templates for new assets
# ---------------------------------------------------------------------------

STARTER_COMMAND = """\
# /{name} Command

## Purpose

Describe what this command does.

## Usage

```
/{name} [arguments]
```

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| | | |

## Process

1. Step one
2. Step two

## Output

Describe the expected output.
"""

STARTER_SKILL = """\
# Skill: {name}

## Description

Describe the skill purpose.

## Trigger

- Invoked by the `/{slug}` slash command.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| | | | |

## Process

1. Step one
2. Step two

## Outputs

Describe the outputs.

## Error Conditions

- Describe error scenarios.
"""

STARTER_HOOK = """\
# Hook Pack: {name}

## Purpose

Describe what this hook pack enforces.

## Hooks

| Hook Name | Trigger | Check | Pass Criteria | Fail Action |
|-----------|---------|-------|---------------|-------------|
| | | | | |

## Configuration

- **Default mode:** enforcing
- **Timeout:** 60 seconds per hook

## Posture Compatibility

| Posture | Included | Default Mode |
|---------|----------|--------------|
| strict | Yes | enforcing |
| standard | Yes | enforcing |
| relaxed | No | — |
"""

STARTER_WORKFLOW = """\
# {name}

## Overview

Describe the workflow or reference document.

## Details

Add content here.
"""

_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def validate_asset_name(name: str) -> str | None:
    """Validate an asset filename (without extension).

    Returns None if valid, or an error message string.
    """
    if not name:
        return "Name cannot be empty."
    if not _FILENAME_RE.match(name):
        return (
            "Use lowercase letters, digits, and hyphens only"
            " (must start with a letter or digit)."
        )
    if len(name) > 60:
        return "Name is too long (max 60 characters)."
    return None


def starter_content(category: str, name: str) -> str:
    """Return starter markdown content for a new asset in the given category."""
    title = name.replace("-", " ").title()
    if category == "Claude Commands":
        return STARTER_COMMAND.format(name=name)
    if category == "Claude Skills":
        return STARTER_SKILL.format(name=title, slug=name)
    if category == "Claude Hooks":
        return STARTER_HOOK.format(name=title)
    return STARTER_WORKFLOW.format(name=title)


# ---------------------------------------------------------------------------
# Pure tree-building logic (testable without Qt)
# ---------------------------------------------------------------------------

def _build_file_tree(library_root: Path) -> list[dict]:
    """Scan a library directory and return a nested structure for the tree.

    Returns a list of category dicts, each with:
        {"name": str, "children": [{"name": str, "path": str|None, "children": [...]}]}

    Leaf nodes with a file path have ``"path"`` set; directories have ``"path": None``.
    """
    if not library_root.is_dir():
        return []

    categories: list[dict] = []
    for display_name, rel_path in LIBRARY_CATEGORIES:
        cat_dir = library_root / rel_path
        if not cat_dir.is_dir():
            categories.append({"name": display_name, "children": []})
            continue

        children = _scan_dir(cat_dir)
        categories.append({"name": display_name, "children": children})

    return categories


def _scan_dir(directory: Path) -> list[dict]:
    """Recursively scan a directory, returning sorted children."""
    children: list[dict] = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            sub_children = _scan_dir(entry)
            children.append({
                "name": entry.name,
                "path": None,
                "children": sub_children,
            })
        elif entry.is_file():
            children.append({
                "name": entry.name,
                "path": str(entry),
                "children": [],
            })
    return children


# ---------------------------------------------------------------------------
# LibraryManagerScreen
# ---------------------------------------------------------------------------

class LibraryManagerScreen(QWidget):
    """Screen for browsing the library structure with a tree and markdown editor pane."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._library_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Library Manager")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Browse the library hierarchy and edit file contents.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(subtitle)

        # Splitter: tree (left) + editor (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {BG_SURFACE};
                width: 2px;
            }}
        """)

        # Left pane: toolbar + tree
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        # Action toolbar for create/delete
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        _btn_style = f"""
            QPushButton {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {BG_BASE};
            }}
            QPushButton:disabled {{
                color: {TEXT_SECONDARY};
            }}
        """

        self._new_btn = QPushButton("New...")
        self._new_btn.setToolTip("Create a new library asset")
        self._new_btn.setStyleSheet(_btn_style)
        self._new_btn.setEnabled(False)
        self._new_btn.clicked.connect(self._on_new_asset)
        toolbar.addWidget(self._new_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setToolTip("Delete the selected library asset")
        self._delete_btn.setStyleSheet(_btn_style)
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete_asset)
        toolbar.addWidget(self._delete_btn)

        toolbar.addStretch()
        left_layout.addLayout(toolbar)

        # Tree view
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: 4px;
                font-size: 13px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px 8px;
            }}
            QTreeWidget::item:selected {{
                background-color: {BG_BASE};
                color: {ACCENT_PRIMARY};
            }}
            QTreeWidget::branch {{
                background-color: {BG_SURFACE};
            }}
        """)
        self._tree.currentItemChanged.connect(self._on_item_selected)
        left_layout.addWidget(self._tree, stretch=1)

        splitter.addWidget(left_pane)

        # Editor pane (replaces the old read-only preview)
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(4)

        self._file_label = QLabel("")
        self._file_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        editor_layout.addWidget(self._file_label)

        self._editor = MarkdownEditor()
        editor_layout.addWidget(self._editor, stretch=1)
        splitter.addWidget(editor_container)

        # Default split: 1/3 tree, 2/3 editor
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

        # Empty state message (shown when no library configured)
        self._empty_label = QLabel(
            "No library path configured.\n\n"
            "Go to Settings to set your library root directory."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        self._empty_label.setWordWrap(True)
        layout.addWidget(self._empty_label)
        self._empty_label.hide()

        self._splitter = splitter

    # -- Public API --------------------------------------------------------

    @property
    def tree(self) -> QTreeWidget:
        return self._tree

    @property
    def editor_widget(self) -> MarkdownEditor:
        """The markdown editor widget."""
        return self._editor

    @property
    def preview(self) -> MarkdownEditor:
        """Backward-compatible alias for the editor widget."""
        return self._editor

    @property
    def file_label(self) -> QLabel:
        return self._file_label

    @property
    def empty_label(self) -> QLabel:
        return self._empty_label

    @property
    def new_button(self) -> QPushButton:
        return self._new_btn

    @property
    def delete_button(self) -> QPushButton:
        return self._delete_btn

    def set_library_root(self, root: str | Path) -> None:
        """Set the library root directory and refresh the tree."""
        self._library_root = Path(root) if root else None
        self.refresh_tree()

    def refresh_tree(self) -> None:
        """Rebuild the tree from the library directory."""
        self._tree.clear()
        self._editor.clear()
        self._file_label.setText("")

        if self._library_root is None or not self._library_root.is_dir():
            self._splitter.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._splitter.show()

        categories = _build_file_tree(self._library_root)
        for cat in categories:
            cat_item = QTreeWidgetItem([cat["name"]])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, None)
            self._tree.addTopLevelItem(cat_item)
            self._add_children(cat_item, cat.get("children", []))

    def showEvent(self, event) -> None:  # noqa: N802
        """Auto-refresh the tree when the screen becomes visible."""
        super().showEvent(event)
        self.refresh_tree()

    # -- Internal ----------------------------------------------------------

    def _add_children(self, parent: QTreeWidgetItem, children: list[dict]) -> None:
        """Recursively add child items to a tree node."""
        for child in children:
            item = QTreeWidgetItem([child["name"]])
            item.setData(0, Qt.ItemDataRole.UserRole, child.get("path"))
            parent.addChild(item)
            self._add_children(item, child.get("children", []))

    def _on_item_selected(self, current: QTreeWidgetItem | None, _prev) -> None:
        """Load the file into the editor when a file node is selected."""
        self._update_button_state(current)

        if current is None:
            self._editor.clear()
            self._file_label.setText("")
            return

        file_path = current.data(0, Qt.ItemDataRole.UserRole)
        if file_path is None:
            self._editor.clear()
            self._file_label.setText("")
            return

        path = Path(file_path)
        if not path.is_file():
            self._editor.load_content("File not found.")
            self._file_label.setText(str(path))
            return

        self._editor.load_file(path)
        self._file_label.setText(str(path))

    def _get_category_for_item(self, item: QTreeWidgetItem | None) -> str | None:
        """Walk up from *item* to the top-level category and return its name."""
        if item is None:
            return None
        node = item
        while node.parent() is not None:
            node = node.parent()
        return node.text(0)

    def _update_button_state(self, item: QTreeWidgetItem | None) -> None:
        """Enable/disable New and Delete based on the selected item."""
        cat = self._get_category_for_item(item)
        editable = cat in _EDITABLE_CATEGORIES
        self._new_btn.setEnabled(editable)

        # Delete is enabled only when a file leaf in an editable category is selected
        has_file = (
            item is not None
            and item.data(0, Qt.ItemDataRole.UserRole) is not None
        )
        # For skills, also allow deleting the skill directory node
        is_skill_dir = (
            cat == "Claude Skills"
            and item is not None
            and item.parent() is not None
            and item.data(0, Qt.ItemDataRole.UserRole) is None
            and item.parent().parent() is None  # direct child of top-level
        )
        self._delete_btn.setEnabled(editable and (has_file or is_skill_dir))

    # -- Create / Delete operations ----------------------------------------

    def _on_new_asset(self) -> None:
        """Prompt user for a name and create a new asset file."""
        item = self._tree.currentItem()
        cat = self._get_category_for_item(item)
        if cat not in _EDITABLE_CATEGORIES or self._library_root is None:
            return

        label = {
            "Workflows": "workflow",
            "Claude Commands": "command",
            "Claude Skills": "skill",
            "Claude Hooks": "hook pack",
        }.get(cat, "file")

        name, ok = QInputDialog.getText(
            self,
            f"New {label.title()}",
            f"Enter {label} name (lowercase, hyphens):",
        )
        if not ok or not name:
            return

        name = name.strip()
        error = validate_asset_name(name)
        if error:
            QMessageBox.warning(self, "Invalid Name", error)
            return

        rel_path = _EDITABLE_CATEGORIES[cat]
        target_dir = self._library_root / rel_path

        if cat == "Claude Skills":
            dest = target_dir / name / "SKILL.md"
            if dest.parent.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"Skill '{name}' already exists."
                )
                return
            dest.parent.mkdir(parents=True, exist_ok=True)
        else:
            dest = target_dir / f"{name}.md"
            if dest.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"File '{name}.md' already exists."
                )
                return
            dest.parent.mkdir(parents=True, exist_ok=True)

        content = starter_content(cat, name)
        dest.write_text(content, encoding="utf-8")
        logger.info("Created %s", dest)
        self.refresh_tree()

    def _on_delete_asset(self) -> None:
        """Delete the selected file (or skill directory) after confirmation."""
        item = self._tree.currentItem()
        if item is None:
            return

        cat = self._get_category_for_item(item)
        if cat not in _EDITABLE_CATEGORIES:
            return

        file_path = item.data(0, Qt.ItemDataRole.UserRole)

        # Skill directory node (no path, direct child of category)
        is_skill_dir = (
            cat == "Claude Skills"
            and file_path is None
            and item.parent() is not None
            and item.parent().parent() is None
        )

        if file_path:
            path = Path(file_path)
            display = path.name
        elif is_skill_dir:
            rel_path = _EDITABLE_CATEGORIES[cat]
            path = self._library_root / rel_path / item.text(0)
            display = item.text(0)
        else:
            return

        answer = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete '{display}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        if path.is_dir():
            shutil.rmtree(path)
            logger.info("Deleted directory %s", path)
        elif path.is_file():
            path.unlink()
            logger.info("Deleted %s", path)

        self.refresh_tree()
