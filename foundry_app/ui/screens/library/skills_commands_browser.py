"""Skills & Commands browser screen: browse and edit Claude command and skill files."""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import LibraryIndex
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

_COMMANDS_REL_DIR = Path("claude") / "commands"
_SKILLS_REL_DIR = Path("claude") / "skills"

_COMMAND_SKELETON = """\
# {name}

## Purpose

Describe what this command does.

## Usage

```
/user:{name}
```

## Steps

1. First step
2. Second step
"""

_SKILL_SKELETON = """\
# {name}

## Description

Describe what this skill provides.

## When to use

Explain the situations where this skill is useful.

## Instructions

Provide detailed instructions for the skill.
"""


class SkillsCommandsBrowser(QWidget):
    """Browse and edit Claude command and skill files from the library."""

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
        self._scan_commands()
        self._scan_skills()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Skills & Commands"))

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, stretch=1)

        # --- Tab 1: Commands ---
        commands_tab = QWidget()
        commands_layout = QVBoxLayout(commands_tab)
        commands_layout.setContentsMargins(4, 4, 4, 4)

        self._cmd_filter = QLineEdit()
        self._cmd_filter.setPlaceholderText("Filter commands...")
        self._cmd_filter.setClearButtonEnabled(True)
        self._cmd_filter.textChanged.connect(self._apply_cmd_filter)
        commands_layout.addWidget(self._cmd_filter)

        self._cmd_list = QListWidget()
        self._cmd_list.currentItemChanged.connect(self._on_command_selected)
        commands_layout.addWidget(self._cmd_list, stretch=1)

        cmd_btn_row = QHBoxLayout()
        self._btn_new_cmd = QPushButton("New Command")
        self._btn_new_cmd.clicked.connect(self._on_new_command)
        cmd_btn_row.addWidget(self._btn_new_cmd)

        self._btn_delete_cmd = QPushButton("Delete Command")
        self._btn_delete_cmd.clicked.connect(self._on_delete_command)
        self._btn_delete_cmd.setEnabled(False)
        cmd_btn_row.addWidget(self._btn_delete_cmd)
        commands_layout.addLayout(cmd_btn_row)

        self._tabs.addTab(commands_tab, "Commands")

        # --- Tab 2: Skills ---
        skills_tab = QWidget()
        skills_layout = QVBoxLayout(skills_tab)
        skills_layout.setContentsMargins(4, 4, 4, 4)

        self._skill_filter = QLineEdit()
        self._skill_filter.setPlaceholderText("Filter skills...")
        self._skill_filter.setClearButtonEnabled(True)
        self._skill_filter.textChanged.connect(self._apply_skill_filter)
        skills_layout.addWidget(self._skill_filter)

        self._skill_list = QListWidget()
        self._skill_list.currentItemChanged.connect(self._on_skill_selected)
        skills_layout.addWidget(self._skill_list, stretch=1)

        skill_btn_row = QHBoxLayout()
        self._btn_new_skill = QPushButton("New Skill")
        self._btn_new_skill.clicked.connect(self._on_new_skill)
        skill_btn_row.addWidget(self._btn_new_skill)

        self._btn_delete_skill = QPushButton("Delete Skill")
        self._btn_delete_skill.clicked.connect(self._on_delete_skill)
        self._btn_delete_skill.setEnabled(False)
        skill_btn_row.addWidget(self._btn_delete_skill)
        skills_layout.addLayout(skill_btn_row)

        self._tabs.addTab(skills_tab, "Skills")

    # -- Data population -------------------------------------------------------

    def _scan_commands(self) -> None:
        """Scan the commands directory and populate the commands list."""
        self._cmd_list.clear()
        self._btn_delete_cmd.setEnabled(False)
        commands_dir = self._library_root / _COMMANDS_REL_DIR
        if not commands_dir.is_dir():
            return
        for md_file in sorted(commands_dir.glob("*.md")):
            item = QListWidgetItem(md_file.stem)
            item.setData(Qt.ItemDataRole.UserRole, md_file)
            self._cmd_list.addItem(item)

    def _scan_skills(self) -> None:
        """Scan the skills directory and populate the skills list."""
        self._skill_list.clear()
        self._btn_delete_skill.setEnabled(False)
        skills_dir = self._library_root / _SKILLS_REL_DIR
        if not skills_dir.is_dir():
            return
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if skill_dir.is_dir() and skill_file.is_file():
                item = QListWidgetItem(skill_dir.name)
                item.setData(Qt.ItemDataRole.UserRole, skill_file)
                self._skill_list.addItem(item)

    # -- Filtering -------------------------------------------------------------

    def _apply_cmd_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._cmd_list.count()):
            item = self._cmd_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    def _apply_skill_filter(self, text: str) -> None:
        text_lower = text.lower()
        for i in range(self._skill_list.count()):
            item = self._skill_list.item(i)
            item.setHidden(text_lower not in item.text().lower())

    # -- Slots -----------------------------------------------------------------

    def _on_command_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            self._btn_delete_cmd.setEnabled(False)
            return
        self._btn_delete_cmd.setEnabled(True)
        file_path: Path = current.data(Qt.ItemDataRole.UserRole)
        self._open_in_inspector(file_path)

    def _on_skill_selected(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if current is None:
            self._btn_delete_skill.setEnabled(False)
            return
        self._btn_delete_skill.setEnabled(True)
        file_path: Path = current.data(Qt.ItemDataRole.UserRole)
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

    # -- New / Delete Commands -------------------------------------------------

    def _on_new_command(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Command", "Command name (without .md):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        commands_dir = self._library_root / _COMMANDS_REL_DIR
        cmd_file = commands_dir / f"{name}.md"
        if cmd_file.exists():
            QMessageBox.warning(
                self,
                "Already Exists",
                f"A command named '{name}' already exists.",
            )
            return

        commands_dir.mkdir(parents=True, exist_ok=True)
        cmd_file.write_text(_COMMAND_SKELETON.format(name=name))
        self._scan_commands()

    def _on_delete_command(self) -> None:
        current = self._cmd_list.currentItem()
        if current is None:
            return

        name = current.text()
        confirm = QMessageBox.question(
            self,
            "Delete Command",
            f"Delete command '{name}' and its file?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        file_path: Path = current.data(Qt.ItemDataRole.UserRole)
        if file_path.is_file():
            file_path.unlink()

        # Remove any cached editor for this file
        key = str(file_path)
        if key in self._editors:
            widget = self._editors.pop(key)
            self._inspector_stack.removeWidget(widget)
            widget.deleteLater()

        self._scan_commands()

    # -- New / Delete Skills ---------------------------------------------------

    def _on_new_skill(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Skill", "Skill name (folder name):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()

        skill_dir = self._library_root / _SKILLS_REL_DIR / name
        if skill_dir.exists():
            QMessageBox.warning(
                self,
                "Already Exists",
                f"A skill named '{name}' already exists.",
            )
            return

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(_SKILL_SKELETON.format(name=name))
        self._scan_skills()

    def _on_delete_skill(self) -> None:
        current = self._skill_list.currentItem()
        if current is None:
            return

        name = current.text()
        confirm = QMessageBox.question(
            self,
            "Delete Skill",
            f"Delete skill '{name}' and its entire directory?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        skill_file: Path = current.data(Qt.ItemDataRole.UserRole)
        skill_dir = skill_file.parent

        if skill_dir.is_dir():
            shutil.rmtree(skill_dir)

        # Remove any cached editors that pointed into this skill directory
        prefix = str(skill_dir)
        keys_to_remove = [k for k in self._editors if k.startswith(prefix)]
        for key in keys_to_remove:
            widget = self._editors.pop(key)
            self._inspector_stack.removeWidget(widget)
            widget.deleteLater()

        self._scan_skills()
