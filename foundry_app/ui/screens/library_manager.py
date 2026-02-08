"""Library Manager screen — tree-based browser for exploring the library structure."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

logger = logging.getLogger(__name__)

# Catppuccin Mocha
_BG = "#1e1e2e"
_SURFACE = "#313244"
_TEXT = "#cdd6f4"
_SUBTEXT = "#6c7086"
_ACCENT = "#cba6f7"

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
        self.setStyleSheet(f"background-color: {_BG};")
        self._library_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Library Manager")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_TEXT};")
        layout.addWidget(title)

        subtitle = QLabel("Browse the library hierarchy and edit file contents.")
        subtitle.setStyleSheet(f"color: {_SUBTEXT}; font-size: 14px;")
        layout.addWidget(subtitle)

        # Splitter: tree (left) + editor (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {_SURFACE};
                width: 2px;
            }}
        """)

        # Tree view
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                font-size: 13px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px 8px;
            }}
            QTreeWidget::item:selected {{
                background-color: {_BG};
                color: {_ACCENT};
            }}
            QTreeWidget::branch {{
                background-color: {_SURFACE};
            }}
        """)
        self._tree.currentItemChanged.connect(self._on_item_selected)
        splitter.addWidget(self._tree)

        # Editor pane (replaces the old read-only preview)
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(4)

        self._file_label = QLabel("")
        self._file_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
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
        self._empty_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 14px;")
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
