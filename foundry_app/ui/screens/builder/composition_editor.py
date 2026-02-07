"""Composition Editor: power-edit the project spec (composition.yml) with
synchronized form and YAML views, plus validation and computed outputs in the
inspector panel."""

from __future__ import annotations

from pathlib import Path

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    PersonaSelection,
    ProjectIdentity,
    StackOverrides,
    StackSelection,
    TeamConfig,
)
from foundry_app.io.composition_io import load_composition, save_composition
from foundry_app.services.validator import run_pre_generation_validation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_STRICTNESS_OPTIONS = ["light", "standard", "strict"]
_POSTURE_OPTIONS = ["baseline", "hardened", "regulated"]
_HOOK_MODE_OPTIONS = ["enforcing", "advisory"]


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape HTML entities in text for safe display."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Inspector panel: computed outputs + validation results
# ---------------------------------------------------------------------------

class _InspectorPanel(QWidget):
    """Right-hand inspector showing computed outputs and validation warnings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel("<b>Composition Inspector</b>")
        layout.addWidget(title)

        self._browser = QTextBrowser()
        self._browser.setOpenExternalLinks(False)
        layout.addWidget(self._browser, stretch=1)

    def set_html(self, html: str) -> None:
        self._browser.setHtml(html)

    def clear(self) -> None:
        self._browser.clear()


# ---------------------------------------------------------------------------
# Form view: structured editing of each composition section
# ---------------------------------------------------------------------------

class _FormView(QScrollArea):
    """Scrollable form with grouped sections matching the CompositionSpec."""

    def __init__(self, library_index: LibraryIndex | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._library_index = library_index
        self.setWidgetResizable(True)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(8, 8, 8, 8)

        self._build_project_section()
        self._build_stacks_section()
        self._build_stack_overrides_section()
        self._build_team_section()
        self._build_hooks_section()
        self._build_generation_section()

        self._layout.addStretch()
        self.setWidget(container)

    # -- Project Identity --------------------------------------------------

    def _build_project_section(self) -> None:
        group = QGroupBox("Project Identity")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Name:"))
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("My Awesome Project")
        row.addWidget(self.project_name, stretch=1)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Slug:"))
        self.project_slug = QLineEdit()
        self.project_slug.setPlaceholderText("my-awesome-project")
        row.addWidget(self.project_slug, stretch=1)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Output Root:"))
        self.output_root = QLineEdit()
        self.output_root.setPlaceholderText("./generated-projects")
        # Load workspace_root from settings as default
        from foundry_app.core.settings import load_settings as _load_settings
        _ws_root = _load_settings().workspace_root or "./generated-projects"
        self.output_root.setText(_ws_root)
        row.addWidget(self.output_root, stretch=1)
        layout.addLayout(row)

        row = QHBoxLayout()
        row.addWidget(QLabel("Output Folder:"))
        self.output_folder = QLineEdit()
        self.output_folder.setPlaceholderText("(defaults to slug)")
        row.addWidget(self.output_folder, stretch=1)
        layout.addLayout(row)

        self._layout.addWidget(group)

    # -- Stacks ------------------------------------------------------------

    def _build_stacks_section(self) -> None:
        group = QGroupBox("Stacks")
        layout = QVBoxLayout(group)

        self.stacks_table = QTableWidget(0, 2)
        self.stacks_table.setHorizontalHeaderLabels(["Stack ID", "Order"])
        self.stacks_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.stacks_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.stacks_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.stacks_table, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_add_stack = QPushButton("Add Stack")
        self._btn_add_stack.clicked.connect(self._on_add_stack)
        btn_row.addWidget(self._btn_add_stack)

        self._btn_remove_stack = QPushButton("Remove Stack")
        self._btn_remove_stack.clicked.connect(self._on_remove_stack)
        btn_row.addWidget(self._btn_remove_stack)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._layout.addWidget(group)

    def _on_add_stack(self) -> None:
        row = self.stacks_table.rowCount()
        self.stacks_table.insertRow(row)

        # Stack ID: combo if library available, otherwise editable text
        if self._library_index and self._library_index.stacks:
            combo = QComboBox()
            for entry in self._library_index.stacks:
                combo.addItem(entry.id)
            self.stacks_table.setCellWidget(row, 0, combo)
        else:
            self.stacks_table.setItem(row, 0, QTableWidgetItem(""))

        # Order: spin box defaulting to (row + 1) * 10
        spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(9999)
        spin.setValue((row + 1) * 10)
        self.stacks_table.setCellWidget(row, 1, spin)

    def _on_remove_stack(self) -> None:
        row = self.stacks_table.currentRow()
        if row >= 0:
            self.stacks_table.removeRow(row)

    def _get_existing_stack_ids(self) -> set[str]:
        ids: set[str] = set()
        for r in range(self.stacks_table.rowCount()):
            widget = self.stacks_table.cellWidget(r, 0)
            if isinstance(widget, QComboBox):
                ids.add(widget.currentText())
            else:
                item = self.stacks_table.item(r, 0)
                if item:
                    ids.add(item.text())
        return ids

    # -- Stack Overrides ---------------------------------------------------

    def _build_stack_overrides_section(self) -> None:
        group = QGroupBox("Stack Overrides")
        layout = QVBoxLayout(group)

        layout.addWidget(QLabel("Notes (Markdown):"))
        self.overrides_notes = QPlainTextEdit()
        self.overrides_notes.setPlaceholderText(
            "Optional markdown notes on stack customization..."
        )
        self.overrides_notes.setMaximumHeight(120)
        layout.addWidget(self.overrides_notes)

        self._layout.addWidget(group)

    # -- Team Personas -----------------------------------------------------

    def _build_team_section(self) -> None:
        group = QGroupBox("Team Personas")
        layout = QVBoxLayout(group)

        self.personas_table = QTableWidget(0, 4)
        self.personas_table.setHorizontalHeaderLabels(
            ["Persona ID", "Agent", "Templates", "Strictness"]
        )
        self.personas_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in (1, 2, 3):
            self.personas_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.personas_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.personas_table, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_add_persona = QPushButton("Add Persona")
        self._btn_add_persona.clicked.connect(self._on_add_persona)
        btn_row.addWidget(self._btn_add_persona)

        self._btn_remove_persona = QPushButton("Remove Persona")
        self._btn_remove_persona.clicked.connect(self._on_remove_persona)
        btn_row.addWidget(self._btn_remove_persona)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._layout.addWidget(group)

    def _on_add_persona(self) -> None:
        row = self.personas_table.rowCount()
        self.personas_table.insertRow(row)

        # Persona ID: combo if library available
        if self._library_index and self._library_index.personas:
            combo = QComboBox()
            for entry in self._library_index.personas:
                combo.addItem(entry.id)
            self.personas_table.setCellWidget(row, 0, combo)
        else:
            self.personas_table.setItem(row, 0, QTableWidgetItem(""))

        # Agent checkbox
        agent_widget = QWidget()
        agent_layout = QHBoxLayout(agent_widget)
        agent_layout.setContentsMargins(0, 0, 0, 0)
        agent_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        agent_cb = QCheckBox()
        agent_cb.setChecked(True)
        agent_layout.addWidget(agent_cb)
        self.personas_table.setCellWidget(row, 1, agent_widget)

        # Templates checkbox
        tpl_widget = QWidget()
        tpl_layout = QHBoxLayout(tpl_widget)
        tpl_layout.setContentsMargins(0, 0, 0, 0)
        tpl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tpl_cb = QCheckBox()
        tpl_cb.setChecked(True)
        tpl_layout.addWidget(tpl_cb)
        self.personas_table.setCellWidget(row, 2, tpl_widget)

        # Strictness combo
        strictness_combo = QComboBox()
        strictness_combo.addItems(_STRICTNESS_OPTIONS)
        strictness_combo.setCurrentText("standard")
        self.personas_table.setCellWidget(row, 3, strictness_combo)

    def _on_remove_persona(self) -> None:
        row = self.personas_table.currentRow()
        if row >= 0:
            self.personas_table.removeRow(row)

    # -- Hooks -------------------------------------------------------------

    def _build_hooks_section(self) -> None:
        group = QGroupBox("Hooks")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Posture:"))
        self.hooks_posture = QComboBox()
        self.hooks_posture.addItems(_POSTURE_OPTIONS)
        self.hooks_posture.setCurrentText("baseline")
        row.addWidget(self.hooks_posture)
        row.addStretch()
        layout.addLayout(row)

        layout.addWidget(QLabel("Hook Packs:"))
        self.hooks_table = QTableWidget(0, 3)
        self.hooks_table.setHorizontalHeaderLabels(["Pack ID", "Enabled", "Mode"])
        self.hooks_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for col in (1, 2):
            self.hooks_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
        self.hooks_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.hooks_table, stretch=1)

        btn_row = QHBoxLayout()
        self._btn_add_hook = QPushButton("Add Hook Pack")
        self._btn_add_hook.clicked.connect(self._on_add_hook)
        btn_row.addWidget(self._btn_add_hook)

        self._btn_remove_hook = QPushButton("Remove Hook Pack")
        self._btn_remove_hook.clicked.connect(self._on_remove_hook)
        btn_row.addWidget(self._btn_remove_hook)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._layout.addWidget(group)

    def _on_add_hook(self) -> None:
        row = self.hooks_table.rowCount()
        self.hooks_table.insertRow(row)

        # Hook Pack ID: combo if library available
        if self._library_index and self._library_index.hooks:
            combo = QComboBox()
            for entry in self._library_index.hooks:
                combo.addItem(entry.id)
            self.hooks_table.setCellWidget(row, 0, combo)
        else:
            self.hooks_table.setItem(row, 0, QTableWidgetItem(""))

        # Enabled checkbox
        enabled_widget = QWidget()
        enabled_layout = QHBoxLayout(enabled_widget)
        enabled_layout.setContentsMargins(0, 0, 0, 0)
        enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        enabled_cb = QCheckBox()
        enabled_cb.setChecked(True)
        enabled_layout.addWidget(enabled_cb)
        self.hooks_table.setCellWidget(row, 1, enabled_widget)

        # Mode combo
        mode_combo = QComboBox()
        mode_combo.addItems(_HOOK_MODE_OPTIONS)
        mode_combo.setCurrentText("enforcing")
        self.hooks_table.setCellWidget(row, 2, mode_combo)

    def _on_remove_hook(self) -> None:
        row = self.hooks_table.currentRow()
        if row >= 0:
            self.hooks_table.removeRow(row)

    # -- Generation Options ------------------------------------------------

    def _build_generation_section(self) -> None:
        group = QGroupBox("Generation Options")
        layout = QVBoxLayout(group)

        self.gen_seed_tasks = QCheckBox("Seed tasks")
        self.gen_seed_tasks.setChecked(True)
        layout.addWidget(self.gen_seed_tasks)

        self.gen_write_manifest = QCheckBox("Write manifest")
        self.gen_write_manifest.setChecked(True)
        layout.addWidget(self.gen_write_manifest)

        self.gen_write_diff_report = QCheckBox("Write diff report")
        self.gen_write_diff_report.setChecked(False)
        layout.addWidget(self.gen_write_diff_report)

        self._layout.addWidget(group)

    # -- Read/write composition from/to form fields ------------------------

    def get_composition(self) -> CompositionSpec:
        """Build a CompositionSpec from the current form state."""
        project = ProjectIdentity(
            name=self.project_name.text().strip(),
            slug=self.project_slug.text().strip(),
            output_root=self.output_root.text().strip() or "./generated-projects",
            output_folder=self.output_folder.text().strip(),
        )

        stacks: list[StackSelection] = []
        for r in range(self.stacks_table.rowCount()):
            stack_id = self._read_cell_text(self.stacks_table, r, 0)
            order_widget = self.stacks_table.cellWidget(r, 1)
            order = order_widget.value() if isinstance(order_widget, QSpinBox) else 10
            if stack_id:
                stacks.append(StackSelection(id=stack_id, order=order))

        stack_overrides = StackOverrides(
            notes_md=self.overrides_notes.toPlainText()
        )

        personas: list[PersonaSelection] = []
        for r in range(self.personas_table.rowCount()):
            persona_id = self._read_cell_text(self.personas_table, r, 0)
            if not persona_id:
                continue

            agent_cb = self._find_checkbox_in_cell(self.personas_table, r, 1)
            tpl_cb = self._find_checkbox_in_cell(self.personas_table, r, 2)
            strictness_widget = self.personas_table.cellWidget(r, 3)

            personas.append(PersonaSelection(
                id=persona_id,
                include_agent=agent_cb.isChecked() if agent_cb else True,
                include_templates=tpl_cb.isChecked() if tpl_cb else True,
                strictness=(
                    strictness_widget.currentText()
                    if isinstance(strictness_widget, QComboBox)
                    else "standard"
                ),
            ))

        packs: list[HookPackSelection] = []
        for r in range(self.hooks_table.rowCount()):
            pack_id = self._read_cell_text(self.hooks_table, r, 0)
            if not pack_id:
                continue

            enabled_cb = self._find_checkbox_in_cell(self.hooks_table, r, 1)
            mode_widget = self.hooks_table.cellWidget(r, 2)

            packs.append(HookPackSelection(
                id=pack_id,
                enabled=enabled_cb.isChecked() if enabled_cb else True,
                mode=(
                    mode_widget.currentText()
                    if isinstance(mode_widget, QComboBox)
                    else "enforcing"
                ),
            ))

        hooks = HooksConfig(
            posture=self.hooks_posture.currentText(),
            packs=packs,
        )

        generation = GenerationOptions(
            seed_tasks=self.gen_seed_tasks.isChecked(),
            write_manifest=self.gen_write_manifest.isChecked(),
            write_diff_report=self.gen_write_diff_report.isChecked(),
        )

        return CompositionSpec(
            project=project,
            stacks=stacks,
            stack_overrides=stack_overrides,
            team=TeamConfig(personas=personas),
            hooks=hooks,
            generation=generation,
        )

    def set_composition(self, spec: CompositionSpec) -> None:
        """Populate form fields from a CompositionSpec."""
        # Project Identity
        self.project_name.setText(spec.project.name)
        self.project_slug.setText(spec.project.slug)
        self.output_root.setText(spec.project.output_root)
        self.output_folder.setText(spec.project.output_folder)

        # Stacks
        self.stacks_table.setRowCount(0)
        for stack in spec.stacks:
            row = self.stacks_table.rowCount()
            self.stacks_table.insertRow(row)

            if self._library_index and self._library_index.stacks:
                combo = QComboBox()
                for entry in self._library_index.stacks:
                    combo.addItem(entry.id)
                # Set to the stack id, or add it if not found
                idx = combo.findText(stack.id)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.addItem(stack.id)
                    combo.setCurrentText(stack.id)
                self.stacks_table.setCellWidget(row, 0, combo)
            else:
                self.stacks_table.setItem(row, 0, QTableWidgetItem(stack.id))

            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(9999)
            spin.setValue(stack.order)
            self.stacks_table.setCellWidget(row, 1, spin)

        # Stack Overrides
        self.overrides_notes.setPlainText(spec.stack_overrides.notes_md)

        # Team Personas
        self.personas_table.setRowCount(0)
        for persona in spec.team.personas:
            row = self.personas_table.rowCount()
            self.personas_table.insertRow(row)

            if self._library_index and self._library_index.personas:
                combo = QComboBox()
                for entry in self._library_index.personas:
                    combo.addItem(entry.id)
                idx = combo.findText(persona.id)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.addItem(persona.id)
                    combo.setCurrentText(persona.id)
                self.personas_table.setCellWidget(row, 0, combo)
            else:
                self.personas_table.setItem(row, 0, QTableWidgetItem(persona.id))

            # Agent checkbox
            agent_widget = QWidget()
            agent_layout = QHBoxLayout(agent_widget)
            agent_layout.setContentsMargins(0, 0, 0, 0)
            agent_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            agent_cb = QCheckBox()
            agent_cb.setChecked(persona.include_agent)
            agent_layout.addWidget(agent_cb)
            self.personas_table.setCellWidget(row, 1, agent_widget)

            # Templates checkbox
            tpl_widget = QWidget()
            tpl_layout = QHBoxLayout(tpl_widget)
            tpl_layout.setContentsMargins(0, 0, 0, 0)
            tpl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tpl_cb = QCheckBox()
            tpl_cb.setChecked(persona.include_templates)
            tpl_layout.addWidget(tpl_cb)
            self.personas_table.setCellWidget(row, 2, tpl_widget)

            # Strictness
            strictness_combo = QComboBox()
            strictness_combo.addItems(_STRICTNESS_OPTIONS)
            strictness_combo.setCurrentText(persona.strictness)
            self.personas_table.setCellWidget(row, 3, strictness_combo)

        # Hooks
        self.hooks_posture.setCurrentText(spec.hooks.posture)
        self.hooks_table.setRowCount(0)
        for pack in spec.hooks.packs:
            row = self.hooks_table.rowCount()
            self.hooks_table.insertRow(row)

            if self._library_index and self._library_index.hooks:
                combo = QComboBox()
                for entry in self._library_index.hooks:
                    combo.addItem(entry.id)
                idx = combo.findText(pack.id)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.addItem(pack.id)
                    combo.setCurrentText(pack.id)
                self.hooks_table.setCellWidget(row, 0, combo)
            else:
                self.hooks_table.setItem(row, 0, QTableWidgetItem(pack.id))

            # Enabled checkbox
            enabled_widget = QWidget()
            enabled_layout = QHBoxLayout(enabled_widget)
            enabled_layout.setContentsMargins(0, 0, 0, 0)
            enabled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            enabled_cb = QCheckBox()
            enabled_cb.setChecked(pack.enabled)
            enabled_layout.addWidget(enabled_cb)
            self.hooks_table.setCellWidget(row, 1, enabled_widget)

            # Mode combo
            mode_combo = QComboBox()
            mode_combo.addItems(_HOOK_MODE_OPTIONS)
            mode_combo.setCurrentText(pack.mode)
            self.hooks_table.setCellWidget(row, 2, mode_combo)

        # Generation Options
        self.gen_seed_tasks.setChecked(spec.generation.seed_tasks)
        self.gen_write_manifest.setChecked(spec.generation.write_manifest)
        self.gen_write_diff_report.setChecked(spec.generation.write_diff_report)

    # -- Helpers -----------------------------------------------------------

    @staticmethod
    def _read_cell_text(table: QTableWidget, row: int, col: int) -> str:
        """Read text from a table cell, handling both QTableWidgetItem and QComboBox."""
        widget = table.cellWidget(row, col)
        if isinstance(widget, QComboBox):
            return widget.currentText()
        item = table.item(row, col)
        if item is not None:
            return item.text().strip()
        return ""

    @staticmethod
    def _find_checkbox_in_cell(table: QTableWidget, row: int, col: int) -> QCheckBox | None:
        """Find the QCheckBox inside a cell widget container."""
        widget = table.cellWidget(row, col)
        if widget is None:
            return None
        # The checkbox is wrapped in a QWidget with a layout
        for child in widget.findChildren(QCheckBox):
            return child
        return None


# ---------------------------------------------------------------------------
# YAML view: raw text editor
# ---------------------------------------------------------------------------

class _YamlView(QWidget):
    """Raw YAML text editor for the composition spec."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setPlaceholderText(
            "# composition.yml\n# Load a file or switch from the Form tab to populate."
        )
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.editor)

    def get_yaml_text(self) -> str:
        return self.editor.toPlainText()

    def set_yaml_text(self, text: str) -> None:
        self.editor.setPlainText(text)


# ---------------------------------------------------------------------------
# Main widget: CompositionEditor
# ---------------------------------------------------------------------------

class CompositionEditor(QWidget):
    """Power editor for the project spec (composition.yml) with synchronized
    form and YAML views, toolbar actions, and inspector integration.

    Parameters
    ----------
    library_root:
        Path to the ai-team-library root, or None if no library is loaded.
    library_index:
        Pre-built LibraryIndex, or None.
    inspector_stack:
        The inspector pane's QStackedWidget for showing computed outputs
        and validation results.
    """

    def __init__(
        self,
        library_root: Path | None,
        library_index: LibraryIndex | None,
        inspector_stack: QStackedWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._library_root = library_root
        self._library_index = library_index
        self._inspector_stack = inspector_stack
        self._file_path: Path | None = None
        self._syncing = False  # guard against re-entrant sync

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # -- Toolbar -------------------------------------------------------
        toolbar = QToolBar()
        toolbar.setMovable(False)

        self._action_load = toolbar.addAction("Load")
        self._action_load.setToolTip("Load a composition.yml file")
        self._action_load.triggered.connect(self._on_load)

        self._action_save = toolbar.addAction("Save")
        self._action_save.setToolTip("Save to the loaded path (or prompt for path)")
        self._action_save.triggered.connect(self._on_save)

        toolbar.addSeparator()

        self._action_validate = toolbar.addAction("Validate")
        self._action_validate.setToolTip(
            "Run pre-generation validation and show results in the inspector"
        )
        self._action_validate.triggered.connect(self._on_validate)

        toolbar.addSeparator()

        self._action_sync = toolbar.addAction("Sync Views")
        self._action_sync.setToolTip(
            "Manually synchronize the form and YAML views"
        )
        self._action_sync.triggered.connect(self._on_sync_views)

        outer.addWidget(toolbar)

        # -- Tab widget: Form + YAML views ---------------------------------
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._form_view = _FormView(self._library_index)
        self._tabs.addTab(self._form_view, "Form")

        self._yaml_view = _YamlView()
        self._tabs.addTab(self._yaml_view, "YAML")

        outer.addWidget(self._tabs, stretch=1)

        # -- Inspector panel (added to the shared inspector stack) ---------
        self._inspector_panel = _InspectorPanel()
        self._inspector_stack.addWidget(self._inspector_panel)

    # ------------------------------------------------------------------
    # Tab switching: synchronize views
    # ------------------------------------------------------------------

    def _on_tab_changed(self, index: int) -> None:
        """Synchronize data when switching between tabs."""
        if self._syncing:
            return

        self._syncing = True
        try:
            if index == 0:
                # Switching TO form: parse YAML and populate form
                self._yaml_to_form()
            elif index == 1:
                # Switching TO YAML: build spec from form and dump
                self._form_to_yaml()
        finally:
            self._syncing = False

    def _form_to_yaml(self) -> None:
        """Build CompositionSpec from the form and write it to the YAML editor."""
        try:
            spec = self._form_view.get_composition()
            data = spec.model_dump()
            yaml_text = yaml.dump(data, default_flow_style=False, sort_keys=False)
            self._yaml_view.set_yaml_text(yaml_text)
        except (ValueError, yaml.YAMLError) as exc:
            QMessageBox.warning(
                self,
                "Sync Error",
                f"Could not convert form data to YAML:\n\n{exc}",
            )

    def _yaml_to_form(self) -> None:
        """Parse the YAML editor text and populate the form."""
        yaml_text = self._yaml_view.get_yaml_text().strip()
        if not yaml_text:
            return

        try:
            data = yaml.safe_load(yaml_text)
            if not isinstance(data, dict):
                QMessageBox.warning(
                    self,
                    "Parse Error",
                    "YAML content is not a valid mapping. Form was not updated.",
                )
                return
            spec = CompositionSpec.model_validate(data)
            self._form_view.set_composition(spec)
        except yaml.YAMLError as exc:
            QMessageBox.warning(
                self,
                "YAML Parse Error",
                f"Could not parse YAML:\n\n{exc}",
            )
        except (ValueError, KeyError) as exc:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"YAML parsed but failed CompositionSpec validation:\n\n{exc}",
            )

    def _on_sync_views(self) -> None:
        """Manually sync: whichever tab is active is the source of truth."""
        if self._syncing:
            return

        self._syncing = True
        try:
            current = self._tabs.currentIndex()
            if current == 0:
                # Form is active -> push to YAML
                self._form_to_yaml()
            else:
                # YAML is active -> push to form
                self._yaml_to_form()
        finally:
            self._syncing = False

    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        """Open a file dialog and load a composition.yml."""
        start_dir = str(self._library_root) if self._library_root else str(Path.home())
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Composition File",
            start_dir,
            "YAML Files (*.yml *.yaml);;All Files (*)",
        )
        if not path:
            return

        file_path = Path(path)
        try:
            spec = load_composition(file_path)
        except (OSError, yaml.YAMLError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load composition file:\n{file_path}\n\n{exc}",
            )
            return

        self._file_path = file_path

        # Populate both views
        self._syncing = True
        try:
            self._form_view.set_composition(spec)
            data = spec.model_dump()
            yaml_text = yaml.dump(data, default_flow_style=False, sort_keys=False)
            self._yaml_view.set_yaml_text(yaml_text)
        finally:
            self._syncing = False

        # Switch to form view after loading
        self._tabs.setCurrentIndex(0)

        # Update inspector with computed outputs
        self._update_inspector(spec)

    def _on_save(self) -> None:
        """Save the composition to the loaded path, or prompt if none."""
        # Build spec from the currently active view
        try:
            spec = self._get_current_spec()
        except (ValueError, yaml.YAMLError) as exc:
            QMessageBox.warning(
                self,
                "Save Error",
                f"Could not build composition from current state:\n\n{exc}",
            )
            return

        if self._file_path is None:
            start_dir = str(self._library_root) if self._library_root else str(Path.home())
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Composition File",
                start_dir,
                "YAML Files (*.yml *.yaml);;All Files (*)",
            )
            if not path:
                return
            self._file_path = Path(path)

        try:
            save_composition(spec, self._file_path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save composition file:\n{self._file_path}\n\n{exc}",
            )
            return

        # Sync both views after saving
        self._syncing = True
        try:
            self._form_view.set_composition(spec)
            data = spec.model_dump()
            yaml_text = yaml.dump(data, default_flow_style=False, sort_keys=False)
            self._yaml_view.set_yaml_text(yaml_text)
        finally:
            self._syncing = False

    def _on_validate(self) -> None:
        """Run pre-generation validation and display results in the inspector."""
        try:
            spec = self._get_current_spec()
        except (ValueError, yaml.YAMLError) as exc:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Could not build composition from current state:\n\n{exc}",
            )
            return

        self._update_inspector(spec, run_validation=True)

    # ------------------------------------------------------------------
    # Inspector updates
    # ------------------------------------------------------------------

    def _update_inspector(
        self,
        spec: CompositionSpec,
        run_validation: bool = False,
    ) -> None:
        """Update the inspector panel with computed outputs and optional validation."""
        lines: list[str] = []

        # -- Computed outputs: resolved templates per persona ---------------
        lines.append("<h3>Computed Outputs</h3>")

        if spec.team.personas:
            for persona in spec.team.personas:
                lines.append(f"<h4>Persona: {_esc(persona.id)}</h4>")

                # Look up templates from the library index
                if self._library_index:
                    entry = next(
                        (p for p in self._library_index.personas if p.id == persona.id),
                        None,
                    )
                    if entry is not None:
                        if entry.templates:
                            lines.append("<b>Templates:</b><ul>")
                            for tpl in entry.templates:
                                lines.append(f"<li>{_esc(tpl)}</li>")
                            lines.append("</ul>")
                        else:
                            lines.append(
                                "<i>No templates found for this persona.</i><br>"
                            )

                        if entry.files:
                            lines.append("<b>Files:</b><ul>")
                            for f in entry.files:
                                lines.append(f"<li>{_esc(f)}</li>")
                            lines.append("</ul>")
                    else:
                        lines.append(
                            f"<p style='color:#c62828;'>Persona '{_esc(persona.id)}' "
                            f"not found in library index.</p>"
                        )
                else:
                    lines.append("<i>No library loaded.</i><br>")
        else:
            lines.append("<i>No personas configured.</i><br>")

        # -- Resolved stack files -------------------------------------------
        if spec.stacks:
            lines.append("<h3>Stack Files</h3>")
            for stack in spec.stacks:
                lines.append(f"<h4>Stack: {_esc(stack.id)} (order {stack.order})</h4>")

                if self._library_index:
                    entry = next(
                        (s for s in self._library_index.stacks if s.id == stack.id),
                        None,
                    )
                    if entry is not None:
                        if entry.files:
                            lines.append("<ul>")
                            for f in entry.files:
                                lines.append(f"<li>{_esc(f)}</li>")
                            lines.append("</ul>")
                        else:
                            lines.append(
                                "<i>No files found for this stack.</i><br>"
                            )
                    else:
                        lines.append(
                            f"<p style='color:#c62828;'>Stack '{_esc(stack.id)}' "
                            f"not found in library index.</p>"
                        )
                else:
                    lines.append("<i>No library loaded.</i><br>")

        # -- Validation results (if requested) ------------------------------
        if run_validation:
            lines.append("<hr>")
            lines.append("<h3>Validation Results</h3>")

            if self._library_root is None:
                lines.append(
                    "<p style='color:#c62828;'><b>Error:</b> "
                    "No library root set. Cannot run validation.</p>"
                )
            else:
                try:
                    result = run_pre_generation_validation(spec, self._library_root)

                    if result.errors:
                        for err in result.errors:
                            lines.append(
                                f"<p style='color:#c62828; margin:2px 0;'>"
                                f"<b>Error:</b> {_esc(err)}</p>"
                            )
                    if result.warnings:
                        for warn in result.warnings:
                            lines.append(
                                f"<p style='color:#e65100; margin:2px 0;'>"
                                f"<b>Warning:</b> {_esc(warn)}</p>"
                            )
                    if result.is_valid and not result.warnings:
                        lines.append(
                            "<p style='color:#2e7d32;'>"
                            "<b>All checks passed.</b></p>"
                        )
                    elif result.is_valid:
                        lines.append(
                            "<p style='color:#2e7d32;'>"
                            "<b>Validation passed with warnings.</b></p>"
                        )
                except (OSError, ValueError) as exc:
                    lines.append(
                        f"<p style='color:#c62828;'><b>Validation error:</b> "
                        f"{_esc(str(exc))}</p>"
                    )

        self._inspector_panel.set_html("\n".join(lines))
        self._inspector_stack.setCurrentWidget(self._inspector_panel)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_current_spec(self) -> CompositionSpec:
        """Build a CompositionSpec from whichever view is currently active."""
        current = self._tabs.currentIndex()
        if current == 1:
            # YAML tab is active: parse from YAML
            yaml_text = self._yaml_view.get_yaml_text().strip()
            if not yaml_text:
                raise ValueError("YAML editor is empty.")
            data = yaml.safe_load(yaml_text)
            if not isinstance(data, dict):
                raise ValueError("YAML content is not a valid mapping.")
            return CompositionSpec.model_validate(data)
        else:
            # Form tab is active (or default)
            return self._form_view.get_composition()
