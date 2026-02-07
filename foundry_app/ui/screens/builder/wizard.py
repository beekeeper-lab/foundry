"""Project Builder wizard: four-step flow to configure and generate a project."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HooksConfig,
    LibraryIndex,
    ProjectIdentity,
    StackOverrides,
    TeamConfig,
)
from foundry_app.ui.screens.builder.wizard_pages import (
    ProjectPage,
    ReviewPage,
    SafetyPage,
    TeamStackPage,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PAGE_TITLES = [
    "Step 1 of 4 — Project",
    "Step 2 of 4 — Team & Stack",
    "Step 3 of 4 — Safety",
    "Step 4 of 4 — Review & Generate",
]


# ---------------------------------------------------------------------------
# Main wizard widget
# ---------------------------------------------------------------------------

class ProjectWizard(QWidget):
    """Four-step project builder wizard.

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
        self._page_project = ProjectPage()
        self._page_team_stack = TeamStackPage(
            persona_ids=[p.id for p in self._library_index.personas],
            stack_ids=[s.id for s in self._library_index.stacks],
        )
        self._page_safety = SafetyPage()
        self._page_review = ReviewPage()

        self._pages.addWidget(self._page_project)
        self._pages.addWidget(self._page_team_stack)
        self._pages.addWidget(self._page_safety)
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
        name = self._page_project.name_edit.text().strip()
        slug = self._page_project.slug_edit.text().strip()
        subtitle = self._page_project.subtitle_edit.text().strip()

        # Load output root from settings
        from foundry_app.core.settings import load_settings as _load_settings
        ws_root = _load_settings().workspace_root or "./generated-projects"

        identity = ProjectIdentity(
            name=name,
            slug=slug,
            subtitle=subtitle,
            output_root=ws_root,
            output_folder=slug,
        )

        stacks = self._page_team_stack.selected_stacks()
        overrides = StackOverrides(
            notes_md=self._page_team_stack.overrides_edit.toPlainText()
        )
        team = TeamConfig(personas=self._page_team_stack.selected_personas())
        safety = self._page_safety.build_safety_config()

        # Build generation options from review page
        generation = GenerationOptions(
            seed_tasks=self._page_review.chk_seed_tasks.isChecked(),
            seed_mode=self._page_review.seed_mode,
            write_manifest=self._page_review.chk_write_manifest.isChecked(),
            write_diff_report=self._page_review.chk_write_diff_report.isChecked(),
        )

        return CompositionSpec(
            project=identity,
            stacks=stacks,
            stack_overrides=overrides,
            team=team,
            hooks=HooksConfig(),
            safety=safety,
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
        if composition.project.subtitle:
            lines.append(f"<b>Subtitle:</b> {_esc(composition.project.subtitle)}<br>")
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

        lines.append("<h3>Safety</h3>")
        lines.append(f"<b>Preset:</b> {_esc(composition.safety.preset)}<br>")

        lines.append("<h3>Generation Options</h3>")
        gen = composition.generation
        lines.append(f"<b>Seed tasks:</b> {'Yes' if gen.seed_tasks else 'No'}<br>")
        lines.append(f"<b>Seed mode:</b> {_esc(gen.seed_mode)}<br>")
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
