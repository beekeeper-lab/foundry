"""Template browser screen: cross-cut view of all templates across all personas."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import LibraryIndex
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor


def _infer_template_type(filename: str) -> str:
    """Infer a broad category from a template filename.

    Maps filenames like ``bug-report.md`` → ``report``, ``test-plan.md`` → ``test``.
    Rules are ordered most-specific-first so ``test-plan`` matches ``test``
    before the broader ``plan`` rule.
    """
    stem = filename.removesuffix(".md").lower()

    # Ordered rules — first match wins, most specific first
    _RULES: list[tuple[list[str], str]] = [
        (["checklist"], "checklist"),
        (["adr", "decision"], "adr"),
        (["runbook", "rollback", "cutover", "rotation"], "runbook"),
        (["test", "regression", "traceability"], "test"),
        (["bug", "defect", "issue"], "report"),
        (["review", "diff", "comment"], "review"),
        (["spec", "brief", "criteria", "contract"], "spec"),
        (["plan", "matrix", "mapping"], "plan"),
        (["report", "notes", "memo", "log"], "report"),
        (["guide", "readme", "onboarding", "docs", "index", "bibliography"], "docs"),
        (["story", "epic", "stakeholder", "user-flow", "wireframe"], "design"),
    ]
    for keywords, category in _RULES:
        if any(kw in stem for kw in keywords):
            return category
    return "other"


class TemplateBrowser(QWidget):
    """Cross-cut view of every template across all personas in the library."""

    _ALL_PERSONAS = "(All Personas)"
    _ALL_TYPES = "(All Types)"

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

        # Build the flat list of (persona_id, template_name, abs_path, type) once
        self._all_templates: list[tuple[str, str, Path, str]] = []
        for persona in self._library_index.personas:
            for tpl_name in persona.templates:
                abs_path = (
                    self._library_root / persona.path / "templates" / tpl_name
                )
                tpl_type = _infer_template_type(tpl_name)
                self._all_templates.append((persona.id, tpl_name, abs_path, tpl_type))

        self._build_ui()
        self._repopulate_list()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Templates (all personas)"))

        # Filter row
        filter_row = QHBoxLayout()

        filter_row.addWidget(QLabel("Persona:"))
        self._persona_combo = QComboBox()
        self._persona_combo.addItem(self._ALL_PERSONAS)
        persona_ids = sorted({t[0] for t in self._all_templates})
        for pid in persona_ids:
            self._persona_combo.addItem(pid)
        self._persona_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._persona_combo, stretch=1)

        filter_row.addWidget(QLabel("Type:"))
        self._type_combo = QComboBox()
        self._type_combo.addItem(self._ALL_TYPES)
        type_ids = sorted({t[3] for t in self._all_templates})
        for tid in type_ids:
            self._type_combo.addItem(tid)
        self._type_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._type_combo, stretch=1)

        filter_row.addWidget(QLabel("Search:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Filter by template name...")
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.textChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._search_edit, stretch=2)

        layout.addLayout(filter_row)

        # Template list
        self._template_list = QListWidget()
        self._template_list.itemClicked.connect(self._on_template_clicked)
        self._template_list.itemDoubleClicked.connect(self._on_template_clicked)
        layout.addWidget(self._template_list, stretch=1)

    # -- Data population -------------------------------------------------------

    def _repopulate_list(self) -> None:
        """Rebuild the visible list from the full template set."""
        self._template_list.clear()
        for persona_id, tpl_name, abs_path, tpl_type in self._all_templates:
            display = f"{persona_id}/{tpl_name}"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, abs_path)
            # Store persona id and type for filtering
            item.setData(Qt.ItemDataRole.UserRole + 1, persona_id)
            item.setData(Qt.ItemDataRole.UserRole + 2, tpl_type)
            self._template_list.addItem(item)
        self._apply_filters()

    def _on_filter_changed(self) -> None:
        self._apply_filters()

    def _apply_filters(self) -> None:
        selected_persona = self._persona_combo.currentText()
        selected_type = self._type_combo.currentText()
        search_text = self._search_edit.text().lower()

        for i in range(self._template_list.count()):
            item = self._template_list.item(i)
            persona_id: str = item.data(Qt.ItemDataRole.UserRole + 1)
            tpl_type: str = item.data(Qt.ItemDataRole.UserRole + 2)

            # Persona filter
            persona_match = (
                selected_persona == self._ALL_PERSONAS
                or persona_id == selected_persona
            )

            # Type filter
            type_match = (
                selected_type == self._ALL_TYPES
                or tpl_type == selected_type
            )

            # Text search filter (matches against the full display string)
            text_match = search_text in item.text().lower()

            item.setHidden(not (persona_match and type_match and text_match))

    # -- Slots -----------------------------------------------------------------

    def _on_template_clicked(self, item: QListWidgetItem) -> None:
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
