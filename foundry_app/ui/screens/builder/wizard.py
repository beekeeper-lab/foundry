"""Project Builder wizard: five-step flow to configure and generate a project."""

from __future__ import annotations

import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HooksConfig,
    LibraryIndex,
    PersonaSelection,
    ProjectIdentity,
    StackOverrides,
    StackSelection,
    TeamConfig,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PAGE_TITLES = [
    "Step 1 of 5 — Project Identity",
    "Step 2 of 5 — Tech Stack",
    "Step 3 of 5 — Team Personas",
    "Step 4 of 5 — Hooks & Policies",
    "Step 5 of 5 — Review & Generate",
]

_STRICTNESS_OPTIONS = ["light", "standard", "strict"]
_POSTURE_OPTIONS = ["baseline", "hardened", "regulated"]


# ---------------------------------------------------------------------------
# Helper: slugify a project name
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    """Convert a human project name to a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


# ---------------------------------------------------------------------------
# Page 1: Identity
# ---------------------------------------------------------------------------

class _IdentityPage(QWidget):
    """Collect project name, slug, output root, and output folder."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Project Name"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Awesome Project")
        self.name_edit.textChanged.connect(self._on_name_changed)
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Project Slug"))
        self.slug_edit = QLineEdit()
        self.slug_edit.setPlaceholderText("my-awesome-project")
        layout.addWidget(self.slug_edit)

        layout.addWidget(QLabel("Output Root Directory"))
        output_row = QHBoxLayout()
        self.output_root_edit = QLineEdit()
        self.output_root_edit.setPlaceholderText("./generated-projects")
        # Load workspace_root from settings as default
        from foundry_app.core.settings import load_settings as _load_settings
        _ws_root = _load_settings().workspace_root or "./generated-projects"
        self.output_root_edit.setText(_ws_root)
        output_row.addWidget(self.output_root_edit)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse)
        output_row.addWidget(self.browse_btn)
        layout.addLayout(output_row)

        layout.addWidget(QLabel("Output Folder Name"))
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setPlaceholderText("(defaults to slug)")
        layout.addWidget(self.output_folder_edit)

        layout.addStretch()

    # -- internal slots --

    def _on_name_changed(self, text: str) -> None:
        self.slug_edit.setText(_slugify(text))

    def _on_browse(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Output Root Directory", str(Path.home())
        )
        if path:
            self.output_root_edit.setText(path)


# ---------------------------------------------------------------------------
# Page 2: Tech Stack
# ---------------------------------------------------------------------------

class _StackPage(QWidget):
    """Select and order tech stacks from the library index."""

    def __init__(self, stack_ids: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Available Stacks (check to include, drag to reorder)"))

        row = QHBoxLayout()

        self.stack_list = QListWidget()
        for sid in stack_ids:
            item = QListWidgetItem(sid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.stack_list.addItem(item)
        row.addWidget(self.stack_list)

        btn_col = QVBoxLayout()
        self.up_btn = QPushButton("Up")
        self.up_btn.clicked.connect(self._move_up)
        btn_col.addWidget(self.up_btn)
        self.down_btn = QPushButton("Down")
        self.down_btn.clicked.connect(self._move_down)
        btn_col.addWidget(self.down_btn)
        btn_col.addStretch()
        row.addLayout(btn_col)

        layout.addLayout(row)

        layout.addWidget(QLabel("Stack Overrides / Notes"))
        self.overrides_edit = QPlainTextEdit()
        self.overrides_edit.setPlaceholderText(
            "Optional markdown notes on stack customization..."
        )
        self.overrides_edit.setMaximumHeight(120)
        layout.addWidget(self.overrides_edit)

        layout.addStretch()

    # -- ordering helpers --

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
        """Return checked stacks in display order."""
        result: list[StackSelection] = []
        order = 0
        for i in range(self.stack_list.count()):
            item = self.stack_list.item(i)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                result.append(StackSelection(id=item.text(), order=order))
                order += 1
        return result


# ---------------------------------------------------------------------------
# Page 3: Team Personas
# ---------------------------------------------------------------------------

class _PersonaRow(QWidget):
    """Inline config for a single persona: agent/templates checkboxes + strictness."""

    def __init__(self, persona_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.persona_id = persona_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        from PySide6.QtWidgets import QCheckBox

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


class _PersonaPage(QWidget):
    """Select personas and configure per-persona options."""

    def __init__(self, persona_ids: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._persona_ids = persona_ids
        self._config_widgets: dict[str, _PersonaRow] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Available Personas (check to include)"))

        self.persona_list = QListWidget()
        for pid in persona_ids:
            item = QListWidgetItem(pid)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.persona_list.addItem(item)
        self.persona_list.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.persona_list)

        # Config area that appears when a persona is checked
        self._config_area = QVBoxLayout()
        config_label = QLabel("Persona Options")
        config_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(config_label)

        self._config_container = QWidget()
        self._config_container.setLayout(self._config_area)
        layout.addWidget(self._config_container)

        layout.addStretch()

    def _on_item_changed(self, item: QListWidgetItem) -> None:
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
        """Return checked personas with their configuration."""
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


# ---------------------------------------------------------------------------
# Page 4: Hooks & Policies
# ---------------------------------------------------------------------------

class _HooksPage(QWidget):
    """Configure hooks posture and generation options."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Security Posture Preset"))
        self.posture_combo = QComboBox()
        self.posture_combo.addItems(_POSTURE_OPTIONS)
        self.posture_combo.setCurrentText("baseline")
        layout.addWidget(self.posture_combo)

        note = QLabel(
            "baseline — sensible defaults for most projects\n"
            "hardened — stricter policies, more guardrails\n"
            "regulated — full audit trail, compliance-oriented"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; margin-top: 8px;")
        layout.addWidget(note)

        # -- Generation Options ------------------------------------------------
        from PySide6.QtWidgets import QCheckBox, QGroupBox

        gen_group = QGroupBox("Generation Options")
        gen_layout = QVBoxLayout(gen_group)

        self.chk_seed_tasks = QCheckBox("Seed initial tasks")
        self.chk_seed_tasks.setChecked(True)
        gen_layout.addWidget(self.chk_seed_tasks)

        self.chk_write_manifest = QCheckBox("Write manifest.json")
        self.chk_write_manifest.setChecked(True)
        gen_layout.addWidget(self.chk_write_manifest)

        self.chk_write_diff_report = QCheckBox("Write diff report")
        self.chk_write_diff_report.setChecked(False)
        gen_layout.addWidget(self.chk_write_diff_report)

        layout.addWidget(gen_group)

        layout.addStretch()


# ---------------------------------------------------------------------------
# Page 5: Review & Generate
# ---------------------------------------------------------------------------

class _ReviewPage(QWidget):
    """Display summary, run validation, and trigger generation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Composition Summary"))

        self.summary_browser = QTextBrowser()
        self.summary_browser.setOpenExternalLinks(False)
        layout.addWidget(self.summary_browser)

        self.validation_browser = QTextBrowser()
        self.validation_browser.setMaximumHeight(160)
        layout.addWidget(self.validation_browser)

    def set_summary(self, html: str) -> None:
        self.summary_browser.setHtml(html)

    def set_validation(self, html: str) -> None:
        self.validation_browser.setHtml(html)


# ---------------------------------------------------------------------------
# Main wizard widget
# ---------------------------------------------------------------------------

class ProjectWizard(QWidget):
    """Five-step project builder wizard.

    Parameters
    ----------
    library_root:
        Path to the ai-team-library root, or None if no library is loaded.
    library_index:
        Pre-built LibraryIndex, or None.
    inspector_stack:
        The inspector pane's QStackedWidget (for future use).
    main_window:
        Reference to MainWindow to call enable_generate / enable_export.
    """

    def __init__(
        self,
        library_root: Path | None,
        library_index: LibraryIndex | None,
        inspector_stack: QStackedWidget,
        main_window: object,
    ) -> None:
        super().__init__()
        self._library_root = library_root
        self._library_index = library_index
        self._inspector_stack = inspector_stack
        self._main_window = main_window

        # Public state: last generated results
        self.last_composition: CompositionSpec | None = None
        self.last_project_path: Path | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # If no library is loaded, show a placeholder and return early
        if self._library_index is None or self._library_root is None:
            placeholder = QLabel("Open a library first to use the Project Builder.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("font-size: 14px; color: #888;")
            outer.addWidget(placeholder)
            return

        # Step title
        self._step_label = QLabel(_PAGE_TITLES[0])
        self._step_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px;")
        outer.addWidget(self._step_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        outer.addWidget(sep)

        # Pages
        self._pages = QStackedWidget()
        self._page_identity = _IdentityPage()
        self._page_stacks = _StackPage(
            [s.id for s in self._library_index.stacks]
        )
        self._page_personas = _PersonaPage(
            [p.id for p in self._library_index.personas]
        )
        self._page_hooks = _HooksPage()
        self._page_review = _ReviewPage()

        self._pages.addWidget(self._page_identity)
        self._pages.addWidget(self._page_stacks)
        self._pages.addWidget(self._page_personas)
        self._pages.addWidget(self._page_hooks)
        self._pages.addWidget(self._page_review)

        outer.addWidget(self._pages, stretch=1)

        # Bottom separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        outer.addWidget(sep2)

        # Navigation buttons
        nav_row = QHBoxLayout()
        nav_row.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.clicked.connect(self._on_back)
        nav_row.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.clicked.connect(self._on_next)
        nav_row.addWidget(self._next_btn)

        self._generate_btn = QPushButton("Generate")
        self._generate_btn.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white; "
            "font-weight: bold; padding: 6px 18px; }"
            "QPushButton:hover { background-color: #388e3c; }"
            "QPushButton:disabled { background-color: #aaa; color: #666; }"
        )
        self._generate_btn.clicked.connect(self._on_generate)
        nav_row.addWidget(self._generate_btn)

        outer.addLayout(nav_row)

        self._update_nav_buttons()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _current_index(self) -> int:
        return self._pages.currentIndex()

    def _page_count(self) -> int:
        return self._pages.count()

    def _update_nav_buttons(self) -> None:
        idx = self._current_index()
        last = self._page_count() - 1

        self._back_btn.setEnabled(idx > 0)
        self._next_btn.setEnabled(idx < last)
        self._next_btn.setVisible(idx < last)
        self._generate_btn.setVisible(idx == last)

        self._step_label.setText(_PAGE_TITLES[idx])

    def _on_back(self) -> None:
        idx = self._current_index()
        if idx > 0:
            self._pages.setCurrentIndex(idx - 1)
            self._update_nav_buttons()

    def _on_next(self) -> None:
        idx = self._current_index()
        if idx < self._page_count() - 1:
            self._pages.setCurrentIndex(idx + 1)
            self._update_nav_buttons()

            # When landing on the review page, refresh summary + validation
            if self._pages.currentIndex() == self._page_count() - 1:
                self._refresh_review()

    # ------------------------------------------------------------------
    # Build CompositionSpec from wizard state
    # ------------------------------------------------------------------

    def _build_composition(self) -> CompositionSpec:
        """Assemble a CompositionSpec from all wizard pages."""
        slug = self._page_identity.slug_edit.text().strip()
        output_folder = self._page_identity.output_folder_edit.text().strip() or slug

        identity = ProjectIdentity(
            name=self._page_identity.name_edit.text().strip(),
            slug=slug,
            output_root=self._page_identity.output_root_edit.text().strip()
            or "./generated-projects",
            output_folder=output_folder,
        )

        stacks = self._page_stacks.selected_stacks()
        overrides = StackOverrides(
            notes_md=self._page_stacks.overrides_edit.toPlainText()
        )

        team = TeamConfig(personas=self._page_personas.selected_personas())

        hooks = HooksConfig(
            posture=self._page_hooks.posture_combo.currentText(),
        )

        generation = GenerationOptions(
            seed_tasks=self._page_hooks.chk_seed_tasks.isChecked(),
            write_manifest=self._page_hooks.chk_write_manifest.isChecked(),
            write_diff_report=self._page_hooks.chk_write_diff_report.isChecked(),
        )

        return CompositionSpec(
            project=identity,
            stacks=stacks,
            stack_overrides=overrides,
            team=team,
            hooks=hooks,
            generation=generation,
        )

    # ------------------------------------------------------------------
    # Review page: summary + validation
    # ------------------------------------------------------------------

    def _refresh_review(self) -> None:
        """Update the review page with current wizard state."""
        composition = self._build_composition()

        # -- Summary HTML --
        lines: list[str] = []
        lines.append("<h3>Project</h3>")
        lines.append(f"<b>Name:</b> {_esc(composition.project.name)}<br>")
        lines.append(f"<b>Slug:</b> {_esc(composition.project.slug)}<br>")
        lines.append(
            f"<b>Output:</b> {_esc(composition.project.output_root)}"
            f"/{_esc(composition.project.output_folder)}<br>"
        )

        lines.append("<h3>Tech Stacks</h3>")
        if composition.stacks:
            lines.append("<ol>")
            for s in composition.stacks:
                lines.append(f"<li>{_esc(s.id)}</li>")
            lines.append("</ol>")
        else:
            lines.append("<i>None selected</i><br>")

        if composition.stack_overrides.notes_md.strip():
            lines.append(
                f"<b>Overrides notes:</b> <pre>{_esc(composition.stack_overrides.notes_md)}</pre>"
            )

        lines.append("<h3>Team Personas</h3>")
        if composition.team.personas:
            lines.append("<ul>")
            for p in composition.team.personas:
                flags = []
                if p.include_agent:
                    flags.append("agent")
                if p.include_templates:
                    flags.append("templates")
                flags.append(f"strictness={p.strictness}")
                lines.append(f"<li><b>{_esc(p.id)}</b> ({', '.join(flags)})</li>")
            lines.append("</ul>")
        else:
            lines.append("<i>None selected</i><br>")

        lines.append("<h3>Hooks &amp; Policies</h3>")
        lines.append(f"<b>Posture:</b> {_esc(composition.hooks.posture)}<br>")

        lines.append("<h3>Generation Options</h3>")
        gen = composition.generation
        lines.append(f"<b>Seed tasks:</b> {'Yes' if gen.seed_tasks else 'No'}<br>")
        lines.append(f"<b>Write manifest:</b> {'Yes' if gen.write_manifest else 'No'}<br>")
        lines.append(f"<b>Write diff report:</b> {'Yes' if gen.write_diff_report else 'No'}<br>")

        self._page_review.set_summary("\n".join(lines))

        # -- Validation --
        assert self._library_root is not None  # guarded in _build_ui
        from foundry_app.core.settings import load_settings
        from foundry_app.services.validator import run_pre_generation_validation

        strictness = load_settings().validation_strictness or "standard"
        result = run_pre_generation_validation(
            composition, self._library_root, strictness
        )

        val_lines: list[str] = []
        if result.errors:
            for err in result.errors:
                val_lines.append(
                    f"<p style='color:#c62828; margin:2px 0;'>"
                    f"<b>Error:</b> {_esc(err)}</p>"
                )
        if result.warnings:
            for warn in result.warnings:
                val_lines.append(
                    f"<p style='color:#f9a825; margin:2px 0;'>"
                    f"<b>Warning:</b> {_esc(warn)}</p>"
                )
        if result.is_valid and not result.warnings:
            val_lines.append(
                "<p style='color:#2e7d32;'><b>All checks passed.</b></p>"
            )
        elif result.is_valid:
            val_lines.append(
                "<p style='color:#2e7d32;'>"
                "<b>Validation passed with warnings.</b></p>"
            )

        self._page_review.set_validation("\n".join(val_lines))

        # Disable generate if validation has errors
        self._generate_btn.setEnabled(result.is_valid)

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def _on_generate(self) -> None:
        """Build the composition and run the generation pipeline."""
        composition = self._build_composition()

        assert self._library_root is not None

        # Determine the output path
        folder = composition.project.output_folder or composition.project.slug
        output_root = Path(composition.project.output_root) / folder

        try:
            from foundry_app.core.settings import load_settings
            from foundry_app.services.generator import generate_project

            strictness = load_settings().validation_strictness or "standard"
            manifest, validation = generate_project(
                composition,
                self._library_root,
                output_root,
                strictness,
            )
        except (OSError, ValueError, KeyError) as exc:
            QMessageBox.critical(
                self,
                "Generation Failed",
                f"An error occurred during generation:\n\n{exc}",
            )
            return

        if not validation.is_valid:
            error_text = "\n".join(f"  - {e}" for e in validation.errors)
            QMessageBox.warning(
                self,
                "Validation Failed",
                f"Pre-generation validation failed:\n\n{error_text}",
            )
            return

        # Count total files written across all stages
        total_files = sum(
            len(stage.wrote) for stage in manifest.stages.values()
        )

        # Store results on the wizard instance
        self.last_composition = composition
        self.last_project_path = output_root
        self.last_composition_path = output_root / "ai" / "team" / "composition.yml"

        # Persist to recent projects
        from foundry_app.core.settings import add_recent_project, load_settings, save_settings
        settings = load_settings()
        settings = add_recent_project(settings, str(output_root))
        save_settings(settings)

        # Enable toolbar actions on the main window
        if hasattr(self._main_window, "enable_generate"):
            self._main_window.enable_generate(True)
        if hasattr(self._main_window, "enable_export"):
            self._main_window.enable_export(True)

        # Build a warning summary if present
        warning_parts: list[str] = []
        if validation.warnings:
            warning_parts.append(
                "\n\nWarnings:\n"
                + "\n".join(f"  - {w}" for w in validation.warnings)
            )
        for stage_name, stage in manifest.stages.items():
            if stage.warnings:
                warning_parts.append(
                    f"\n{stage_name} warnings:\n"
                    + "\n".join(f"  - {w}" for w in stage.warnings)
                )

        QMessageBox.information(
            self,
            "Generation Complete",
            f"Project generated successfully!\n\n"
            f"Output: {output_root}\n"
            f"Files written: {total_files}"
            + ("".join(warning_parts) if warning_parts else ""),
        )

        # Auto-navigate to the generate screen to show results
        if hasattr(self._main_window, "show_screen"):
            self._main_window.show_screen("generate")


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
