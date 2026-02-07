"""Persona browser screen: browse, create, delete personas and edit their files."""

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
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import LibraryIndex, PersonaIndexEntry
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

_PERSONA_SKELETON_FILES = ["persona.md", "outputs.md", "prompts.md"]


class PersonaBrowser(QWidget):
    """Browse personas from the library index and open their files for editing."""

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
        self._populate_persona_list()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left panel: persona list with filter and action buttons ---
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)

        left_layout.addWidget(QLabel("Personas"))

        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("Filter personas...")
        self._filter_edit.setClearButtonEnabled(True)
        self._filter_edit.textChanged.connect(self._apply_filter)
        left_layout.addWidget(self._filter_edit)

        self._persona_list = QListWidget()
        self._persona_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._persona_list.currentItemChanged.connect(self._on_persona_selected)
        left_layout.addWidget(self._persona_list, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_new = QPushButton("New Persona")
        self._btn_new.clicked.connect(self._on_new_persona)
        btn_row.addWidget(self._btn_new)

        self._btn_delete = QPushButton("Delete Persona")
        self._btn_delete.clicked.connect(self._on_delete_persona)
        self._btn_delete.setEnabled(False)
        btn_row.addWidget(self._btn_delete)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left)

        # --- Right panel: file list for the selected persona ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 4, 4, 4)

        self._files_header = QLabel("Select a persona to see its files")
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

    def _populate_persona_list(self) -> None:
        self._persona_list.clear()
        for persona in self._library_index.personas:
            item = QListWidgetItem(persona.id)
            item.setData(Qt.ItemDataRole.UserRole, persona)
            self._persona_list.addItem(item)

    def _apply_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._persona_list.count()):
            item = self._persona_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    # -- Slots -----------------------------------------------------------------

    def _on_persona_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        self._file_list.clear()
        if current is None:
            self._files_header.setText("Select a persona to see its files")
            self._btn_delete.setEnabled(False)
            return

        persona: PersonaIndexEntry = current.data(Qt.ItemDataRole.UserRole)
        self._files_header.setText(f"Files in {persona.id}")
        self._btn_delete.setEnabled(True)

        # Top-level files
        for filename in persona.files:
            fi = QListWidgetItem(filename)
            fi.setData(
                Qt.ItemDataRole.UserRole,
                self._library_root / persona.path / filename,
            )
            self._file_list.addItem(fi)

        # Templates (nested under templates/)
        for tpl_name in persona.templates:
            fi = QListWidgetItem(f"templates/{tpl_name}")
            fi.setData(
                Qt.ItemDataRole.UserRole,
                self._library_root / persona.path / "templates" / tpl_name,
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

    # -- New / Delete ----------------------------------------------------------

    def _on_new_persona(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Persona", "Persona ID (folder name):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        persona_dir = self._library_root / "personas" / name
        if persona_dir.exists():
            QMessageBox.warning(
                self,
                "Already Exists",
                f"A persona named '{name}' already exists.",
            )
            return

        # Create directory structure
        persona_dir.mkdir(parents=True, exist_ok=True)
        (persona_dir / "templates").mkdir(exist_ok=True)

        # Create skeleton markdown files
        for filename in _PERSONA_SKELETON_FILES:
            filepath = persona_dir / filename
            filepath.write_text(f"# {name} — {filepath.stem}\n")

        # Rebuild index from the library index model
        self._library_index = LibraryIndex.from_library_path(self._library_root)
        self._populate_persona_list()

    def _on_delete_persona(self) -> None:
        current = self._persona_list.currentItem()
        if current is None:
            return

        persona: PersonaIndexEntry = current.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Delete Persona",
            f"Delete persona '{persona.id}' and all its files?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        import shutil

        persona_path = self._library_root / persona.path
        if persona_path.is_dir():
            shutil.rmtree(persona_path)

        # Remove any open editors that pointed into this persona
        prefix = str(persona_path)
        keys_to_remove = [k for k in self._editors if k.startswith(prefix)]
        for key in keys_to_remove:
            widget = self._editors.pop(key)
            self._inspector_stack.removeWidget(widget)
            widget.deleteLater()

        self._library_index = LibraryIndex.from_library_path(self._library_root)
        self._populate_persona_list()
        self._file_list.clear()
        self._files_header.setText("Select a persona to see its files")
