"""Stack browser screen: browse stacks and edit their files."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import LibraryIndex, StackIndexEntry
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor


class StackBrowser(QWidget):
    """Browse stacks from the library index and open their files for editing."""

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
        self._populate_stack_list()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left panel: stack list with filter ---
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)

        left_layout.addWidget(QLabel("Stacks"))

        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("Filter stacks...")
        self._filter_edit.setClearButtonEnabled(True)
        self._filter_edit.textChanged.connect(self._apply_filter)
        left_layout.addWidget(self._filter_edit)

        self._stack_list = QListWidget()
        self._stack_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._stack_list.currentItemChanged.connect(self._on_stack_selected)
        left_layout.addWidget(self._stack_list, stretch=1)

        splitter.addWidget(left)

        # --- Right panel: file list for the selected stack ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 4, 4, 4)

        self._files_header = QLabel("Select a stack to see its files")
        self._files_header.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(self._files_header)

        self._file_list = QListWidget()
        self._file_list.itemDoubleClicked.connect(self._on_file_clicked)
        self._file_list.itemClicked.connect(self._on_file_clicked)
        right_layout.addWidget(self._file_list, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([260, 340])

        outer.addWidget(splitter)

    # -- Data population -------------------------------------------------------

    def _populate_stack_list(self) -> None:
        self._stack_list.clear()
        for stack in self._library_index.stacks:
            item = QListWidgetItem(stack.id)
            item.setData(Qt.ItemDataRole.UserRole, stack)
            self._stack_list.addItem(item)

    def _apply_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._stack_list.count()):
            item = self._stack_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    # -- Slots -----------------------------------------------------------------

    def _on_stack_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        self._file_list.clear()
        if current is None:
            self._files_header.setText("Select a stack to see its files")
            return

        stack: StackIndexEntry = current.data(Qt.ItemDataRole.UserRole)
        self._files_header.setText(f"Files in {stack.id}")

        for filename in stack.files:
            fi = QListWidgetItem(filename)
            fi.setData(
                Qt.ItemDataRole.UserRole,
                self._library_root / stack.path / filename,
            )
            self._file_list.addItem(fi)

    def _on_file_clicked(self, item: QListWidgetItem) -> None:
        file_path: Path = item.data(Qt.ItemDataRole.UserRole)
        if file_path is None:
            return
        self._open_in_inspector(file_path)

    def _open_in_inspector(self, file_path: Path) -> None:
        key = str(file_path)
        if key not in self._editors:
            editor = MarkdownEditor()
            self._editors[key] = editor
            self._inspector_stack.addWidget(editor)
        editor = self._editors[key]
        editor.load_file(file_path)
        self._inspector_stack.setCurrentWidget(editor)
