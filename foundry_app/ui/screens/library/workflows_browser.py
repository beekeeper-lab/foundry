"""Workflows browser screen: browse, create, delete, and edit workflow markdown files."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import LibraryIndex
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

_WORKFLOWS_REL_DIR = Path("workflows")


class WorkflowsBrowser(QWidget):
    """Browse and edit workflow files from the library workflows directory."""

    def __init__(
        self,
        library_root: Path,
        library_index: LibraryIndex,
        inspector_stack: QStackedWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library_root = library_root
        self._library_index = library_index
        self._inspector_stack = inspector_stack
        self._editors: dict[str, MarkdownEditor] = {}
        self._build_ui()
        self._populate_workflow_list()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Workflows"))

        # --- Filter ---
        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("Filter workflows...")
        self._filter_edit.setClearButtonEnabled(True)
        self._filter_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_edit)

        # --- Workflow list ---
        self._workflow_list = QListWidget()
        self._workflow_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._workflow_list.currentItemChanged.connect(self._on_workflow_selected)
        layout.addWidget(self._workflow_list, stretch=1)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self._btn_new = QPushButton("New Workflow")
        self._btn_new.clicked.connect(self._on_new_workflow)
        btn_row.addWidget(self._btn_new)

        self._btn_delete = QPushButton("Delete Workflow")
        self._btn_delete.clicked.connect(self._on_delete_workflow)
        self._btn_delete.setEnabled(False)
        btn_row.addWidget(self._btn_delete)
        layout.addLayout(btn_row)

    # -- Data population -------------------------------------------------------

    def _populate_workflow_list(self) -> None:
        self._workflow_list.clear()
        workflows_dir = self._library_root / _WORKFLOWS_REL_DIR
        if not workflows_dir.is_dir():
            self._btn_delete.setEnabled(False)
            return

        for md_file in sorted(workflows_dir.glob("*.md")):
            item = QListWidgetItem(md_file.name)
            item.setData(Qt.ItemDataRole.UserRole, md_file)
            self._workflow_list.addItem(item)
        self._btn_delete.setEnabled(False)

    def _apply_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._workflow_list.count()):
            item = self._workflow_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    # -- Slots -----------------------------------------------------------------

    def _on_workflow_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            self._btn_delete.setEnabled(False)
            return

        self._btn_delete.setEnabled(True)
        workflow_file: Path = current.data(Qt.ItemDataRole.UserRole)
        self._open_in_inspector(workflow_file)

    def _open_in_inspector(self, file_path: Path) -> None:
        key = str(file_path)
        if key not in self._editors:
            editor = MarkdownEditor()
            self._editors[key] = editor
            self._inspector_stack.addWidget(editor)
        editor = self._editors[key]
        editor.load_file(file_path)
        self._inspector_stack.setCurrentWidget(editor)

    # -- New / Delete ----------------------------------------------------------

    def _on_new_workflow(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Workflow", "Workflow name (file name without .md):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        workflows_dir = self._library_root / _WORKFLOWS_REL_DIR
        workflow_file = workflows_dir / f"{name}.md"
        if workflow_file.exists():
            QMessageBox.warning(
                self,
                "Already Exists",
                f"A workflow named '{name}' already exists.",
            )
            return

        # Ensure the workflows directory exists
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create skeleton workflow file
        workflow_file.write_text(
            f"# {name}\n\n"
            f"## Overview\n\n"
            f"Describe the purpose of this workflow.\n\n"
            f"## Steps\n\n"
            f"1. First step\n"
            f"2. Second step\n"
            f"3. Third step\n"
        )

        self._populate_workflow_list()

    def _on_delete_workflow(self) -> None:
        current = self._workflow_list.currentItem()
        if current is None:
            return

        workflow_file: Path = current.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Delete Workflow",
            f"Delete workflow '{workflow_file.name}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if workflow_file.is_file():
            workflow_file.unlink()

        # Remove any open editor that pointed to this file
        key = str(workflow_file)
        if key in self._editors:
            widget = self._editors.pop(key)
            self._inspector_stack.removeWidget(widget)
            widget.deleteLater()

        self._populate_workflow_list()
