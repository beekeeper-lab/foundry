"""Step 2: Team & Stack — side-by-side persona and stack selection."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import PersonaSelection, StackSelection

_STRICTNESS_OPTIONS = ["light", "standard", "strict"]


class _PersonaRow(QWidget):
    """Inline config for a single persona: agent/templates checkboxes + strictness."""

    def __init__(self, persona_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.persona_id = persona_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self.agent_cb = QCheckBox("Agent")
        self.agent_cb.setChecked(True)
        layout.addWidget(self.agent_cb)

        self.templates_cb = QCheckBox("Templates")
        self.templates_cb.setChecked(True)
        layout.addWidget(self.templates_cb)

        layout.addWidget(QLabel("Strictness:"))
        self.strictness_combo = QComboBox()
        self.strictness_combo.addItems(_STRICTNESS_OPTIONS)
        self.strictness_combo.setCurrentText("standard")
        layout.addWidget(self.strictness_combo)

        layout.addStretch()


class TeamStackPage(QWidget):
    """Side-by-side team members and tech stacks selection."""

    def __init__(
        self,
        persona_ids: list[str],
        stack_ids: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._config_widgets: dict[str, _PersonaRow] = {}

        outer = QVBoxLayout(self)
        columns = QHBoxLayout()

        # --- Left column: Personas ---
        left = QVBoxLayout()
        left.addWidget(QLabel("Team Members"))

        self.persona_list = QListWidget()
        for pid in persona_ids:
            item = QListWidgetItem(pid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.persona_list.addItem(item)
        self.persona_list.itemChanged.connect(self._on_persona_changed)
        left.addWidget(self.persona_list)

        # Config area for checked personas
        config_label = QLabel("Persona Options")
        config_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        left.addWidget(config_label)

        self._config_area = QVBoxLayout()
        self._config_container = QWidget()
        self._config_container.setLayout(self._config_area)
        left.addWidget(self._config_container)

        columns.addLayout(left, stretch=1)

        # --- Right column: Stacks ---
        right = QVBoxLayout()
        right.addWidget(QLabel("Tech Stacks"))

        self.stack_list = QListWidget()
        for sid in stack_ids:
            item = QListWidgetItem(sid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.stack_list.addItem(item)
        right.addWidget(self.stack_list)

        # Up/Down buttons for stack ordering
        btn_row = QHBoxLayout()
        self.up_btn = QPushButton("Up")
        self.up_btn.clicked.connect(self._move_up)
        btn_row.addWidget(self.up_btn)
        self.down_btn = QPushButton("Down")
        self.down_btn.clicked.connect(self._move_down)
        btn_row.addWidget(self.down_btn)
        btn_row.addStretch()
        right.addLayout(btn_row)

        right.addWidget(QLabel("Stack Overrides / Notes"))
        self.overrides_edit = QPlainTextEdit()
        self.overrides_edit.setPlaceholderText("Optional notes on stack customization...")
        self.overrides_edit.setMaximumHeight(100)
        right.addWidget(self.overrides_edit)

        columns.addLayout(right, stretch=1)
        outer.addLayout(columns, stretch=1)

    # --- Persona events ---

    def _on_persona_changed(self, item: QListWidgetItem) -> None:
        pid = item.text()
        if item.checkState() == Qt.CheckState.Checked:
            if pid not in self._config_widgets:
                row = _PersonaRow(pid)
                self._config_widgets[pid] = row
                self._config_area.addWidget(row)
            self._config_widgets[pid].setVisible(True)
        else:
            if pid in self._config_widgets:
                self._config_widgets[pid].setVisible(False)

    def selected_personas(self) -> list[PersonaSelection]:
        result: list[PersonaSelection] = []
        for i in range(self.persona_list.count()):
            item = self.persona_list.item(i)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                pid = item.text()
                cfg = self._config_widgets.get(pid)
                if cfg is not None:
                    result.append(
                        PersonaSelection(
                            id=pid,
                            include_agent=cfg.agent_cb.isChecked(),
                            include_templates=cfg.templates_cb.isChecked(),
                            strictness=cfg.strictness_combo.currentText(),
                        )
                    )
                else:
                    result.append(PersonaSelection(id=pid))
        return result

    # --- Stack ordering ---

    def _move_up(self) -> None:
        row = self.stack_list.currentRow()
        if row <= 0:
            return
        item = self.stack_list.takeItem(row)
        self.stack_list.insertItem(row - 1, item)
        self.stack_list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self.stack_list.currentRow()
        if row < 0 or row >= self.stack_list.count() - 1:
            return
        item = self.stack_list.takeItem(row)
        self.stack_list.insertItem(row + 1, item)
        self.stack_list.setCurrentRow(row + 1)

    def selected_stacks(self) -> list[StackSelection]:
        result: list[StackSelection] = []
        order = 0
        for i in range(self.stack_list.count()):
            item = self.stack_list.item(i)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                result.append(StackSelection(id=item.text(), order=order))
                order += 1
        return result
