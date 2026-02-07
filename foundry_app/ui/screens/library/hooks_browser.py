"""Hooks browser screen: manage hook policy packs and templates for generated projects."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGroupBox,
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

from foundry_app.core.models import HookIndexEntry, LibraryIndex
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

_POSTURE_PRESETS: dict[str, str] = {
    "baseline": (
        "Baseline: A minimal set of hooks enabled by default. "
        "Formatting and basic lint checks run in advisory mode. "
        "Suitable for solo developers and early-stage projects."
    ),
    "hardened": (
        "Hardened: All recommended hooks enabled and enforcing. "
        "Includes secrets scanning, commit-message validation, and "
        "strict formatting. Suitable for team projects with CI."
    ),
    "regulated": (
        "Regulated: Every available hook enabled in enforcing mode "
        "with no bypass allowed. Adds audit-trail and policy-compliance "
        "checks. Suitable for regulated industries and enterprise."
    ),
}

_HOOKS_REL_DIR = Path("claude") / "hooks"


class HooksBrowser(QWidget):
    """Browse and manage hook policy packs from the library index."""

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
        self._populate_hook_list()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Hooks"))

        # --- Posture Presets group box ---
        posture_group = QGroupBox("Posture Presets")
        posture_layout = QVBoxLayout(posture_group)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Preset:"))
        self._posture_combo = QComboBox()
        for preset_name in _POSTURE_PRESETS:
            self._posture_combo.addItem(preset_name)
        self._posture_combo.currentTextChanged.connect(self._on_posture_changed)
        preset_row.addWidget(self._posture_combo, stretch=1)
        posture_layout.addLayout(preset_row)

        self._posture_description = QLabel(_POSTURE_PRESETS["baseline"])
        self._posture_description.setWordWrap(True)
        self._posture_description.setStyleSheet(
            "color: #666; font-style: italic; padding: 4px;"
        )
        posture_layout.addWidget(self._posture_description)

        layout.addWidget(posture_group)

        # --- Filter ---
        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("Filter hooks...")
        self._filter_edit.setClearButtonEnabled(True)
        self._filter_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_edit)

        # --- Hook list ---
        self._hook_list = QListWidget()
        self._hook_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._hook_list.currentItemChanged.connect(self._on_hook_selected)
        layout.addWidget(self._hook_list, stretch=1)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self._btn_new = QPushButton("New Hook")
        self._btn_new.clicked.connect(self._on_new_hook)
        btn_row.addWidget(self._btn_new)

        self._btn_delete = QPushButton("Delete Hook")
        self._btn_delete.clicked.connect(self._on_delete_hook)
        self._btn_delete.setEnabled(False)
        btn_row.addWidget(self._btn_delete)
        layout.addLayout(btn_row)

    # -- Data population -------------------------------------------------------

    def _populate_hook_list(self) -> None:
        self._hook_list.clear()
        for hook in self._library_index.hooks:
            mode_label = hook.mode
            enabled_label = "on" if hook.default_enabled else "off"
            display = f"{hook.id}  [{enabled_label}, {mode_label}]"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, hook)
            self._hook_list.addItem(item)
        self._btn_delete.setEnabled(False)

    def _apply_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._hook_list.count()):
            item = self._hook_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    # -- Slots -----------------------------------------------------------------

    def _on_posture_changed(self, preset_name: str) -> None:
        description = _POSTURE_PRESETS.get(preset_name, "")
        self._posture_description.setText(description)

    def _on_hook_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            self._btn_delete.setEnabled(False)
            return

        self._btn_delete.setEnabled(True)
        hook: HookIndexEntry = current.data(Qt.ItemDataRole.UserRole)
        hook_file = self._library_root / _HOOKS_REL_DIR / f"{hook.id}.md"
        self._open_in_inspector(hook_file)

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

    def _on_new_hook(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Hook", "Hook ID (file name without .md):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        hooks_dir = self._library_root / _HOOKS_REL_DIR
        hook_file = hooks_dir / f"{name}.md"
        if hook_file.exists():
            QMessageBox.warning(
                self,
                "Already Exists",
                f"A hook named '{name}' already exists.",
            )
            return

        # Ensure the hooks directory exists
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Create skeleton hook file
        hook_file.write_text(
            f"# {name}\n\n"
            f"## What it enforces\n\n"
            f"Describe what this hook checks or enforces.\n\n"
            f"## Why it exists\n\n"
            f"Explain the rationale behind this hook.\n\n"
            f"## How to bypass\n\n"
            f"Document any sanctioned bypass mechanisms.\n"
        )

        # Rebuild index
        self._library_index = LibraryIndex.from_library_path(self._library_root)
        self._populate_hook_list()

    def _on_delete_hook(self) -> None:
        current = self._hook_list.currentItem()
        if current is None:
            return

        hook: HookIndexEntry = current.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(
            self,
            "Delete Hook",
            f"Delete hook '{hook.id}' and its file?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        hook_file = self._library_root / _HOOKS_REL_DIR / f"{hook.id}.md"
        if hook_file.is_file():
            hook_file.unlink()

        # Remove any open editor that pointed to this file
        key = str(hook_file)
        if key in self._editors:
            widget = self._editors.pop(key)
            self._inspector_stack.removeWidget(widget)
            widget.deleteLater()

        # Rebuild index
        self._library_index = LibraryIndex.from_library_path(self._library_root)
        self._populate_hook_list()
