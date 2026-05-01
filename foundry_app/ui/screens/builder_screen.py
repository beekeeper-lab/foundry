"""Builder screen — multi-step wizard container for composing a new project."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    LibraryIndex,
)
from foundry_app.ui import theme
from foundry_app.ui.screens.builder.wizard_pages.architecture_page import (
    ArchitectureCloudPage,
)
from foundry_app.ui.screens.builder.wizard_pages.expertise_page import ExpertiseSelectionPage
from foundry_app.ui.screens.builder.wizard_pages.hook_safety_page import HookSafetyPage
from foundry_app.ui.screens.builder.wizard_pages.persona_page import (
    PersonaSelectionPage,
)
from foundry_app.ui.screens.builder.wizard_pages.project_page import ProjectPage
from foundry_app.ui.screens.builder.wizard_pages.review_page import ReviewPage

logger = logging.getLogger(__name__)

# Step definitions: (label, page_factory, requires_library)
_STEPS = [
    ("Project", "project"),
    ("Team", "persona"),
    ("Expertise", "expertise"),
    ("Architecture", "architecture"),
    ("Safety", "hooks"),
    ("Review", "review"),
]


class BuilderScreen(QWidget):
    """Multi-step wizard that assembles a CompositionSpec and triggers generation."""

    generate_requested = Signal(CompositionSpec)
    # BEAN-288: emitted whenever ``has_in_progress_state()`` would change —
    # ``MainWindow`` listens so the sidebar's builder button can flip between
    # "New Project" and "Resume Project".
    state_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._library_index: LibraryIndex | None = None
        self._last_in_progress = False
        self._build_ui()
        self._wire_state_change_signals()
        self._update_nav_state()

    # -- UI construction ---------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Step indicator bar
        self._step_bar = QWidget()
        self._step_bar.setStyleSheet(f"""
            background-color: {theme.BG_INSET};
            border-bottom: 1px solid {theme.BORDER_DEFAULT};
        """)
        step_bar_layout = QHBoxLayout(self._step_bar)
        step_bar_layout.setContentsMargins(
            theme.SPACE_XL, theme.SPACE_SM, theme.SPACE_XL, theme.SPACE_SM,
        )
        step_bar_layout.setSpacing(theme.SPACE_XS)

        self._step_labels: list[QLabel] = []
        for i, (label, _key) in enumerate(_STEPS):
            step_label = QLabel(f"{i + 1}. {label}")
            step_label.setFont(QFont("", theme.FONT_SIZE_SM))
            step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_label.setStyleSheet(f"""
                color: {theme.TEXT_DISABLED};
                padding: {theme.SPACE_XS}px {theme.SPACE_SM}px;
            """)
            step_bar_layout.addWidget(step_label)
            self._step_labels.append(step_label)
            if i < len(_STEPS) - 1:
                sep = QLabel("\u203a")
                sep.setStyleSheet(f"color: {theme.TEXT_DISABLED};")
                sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
                step_bar_layout.addWidget(sep)

        step_bar_layout.addStretch()
        layout.addWidget(self._step_bar)

        # Page stack
        self._page_stack = QStackedWidget()
        self._page_stack.setStyleSheet(f"background-color: {theme.BG_BASE};")
        layout.addWidget(self._page_stack, stretch=1)

        # Create wizard pages
        self._project_page = ProjectPage()
        self._persona_page = PersonaSelectionPage()
        self._expertise_page = ExpertiseSelectionPage()
        self._architecture_page = ArchitectureCloudPage()
        self._hooks_page = HookSafetyPage()
        self._review_page = ReviewPage()

        self._pages: list[QWidget] = [
            self._project_page,
            self._persona_page,
            self._expertise_page,
            self._architecture_page,
            self._hooks_page,
            self._review_page,
        ]

        for page in self._pages:
            self._page_stack.addWidget(page)

        # Connect review page generate signal
        self._review_page.generate_requested.connect(self._on_generate)

        # Connect page validation signals to update Next button state
        self._project_page.completeness_changed.connect(
            lambda _: self._update_next_enabled()
        )
        self._persona_page.selection_changed.connect(self._update_next_enabled)
        self._expertise_page.selection_changed.connect(self._update_next_enabled)

        # Navigation bar
        nav_bar = QWidget()
        nav_bar.setStyleSheet(f"""
            background-color: {theme.BG_INSET};
            border-top: 1px solid {theme.BORDER_DEFAULT};
        """)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(
            theme.SPACE_XL, theme.SPACE_MD, theme.SPACE_XL, theme.SPACE_MD,
        )

        self._back_btn = QPushButton("Back")
        self._back_btn.setStyleSheet(self._nav_button_style())
        self._back_btn.clicked.connect(self._go_back)

        # BEAN-288: explicit reset affordance — visible only when the wizard
        # has accumulated state worth clearing. The current "click somewhere
        # else and come back" path was not discoverable.
        self._start_over_btn = QPushButton("Start Over")
        self._start_over_btn.setToolTip("Reset wizard — clear all selections.")
        self._start_over_btn.setStyleSheet(self._nav_button_style())
        self._start_over_btn.setVisible(False)
        self._start_over_btn.clicked.connect(self.start_over)

        self._next_btn = QPushButton("Next")
        self._next_btn.setStyleSheet(self._primary_button_style())
        self._next_btn.clicked.connect(self._go_next)

        nav_layout.addWidget(self._back_btn)
        nav_layout.addWidget(self._start_over_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self._next_btn)

        layout.addWidget(nav_bar)

    # -- Public API --------------------------------------------------------

    @property
    def current_step(self) -> int:
        return self._page_stack.currentIndex()

    @property
    def page_stack(self) -> QStackedWidget:
        return self._page_stack

    @property
    def project_page(self) -> ProjectPage:
        return self._project_page

    @property
    def persona_page(self) -> PersonaSelectionPage:
        return self._persona_page

    @property
    def expertise_page(self) -> ExpertiseSelectionPage:
        return self._expertise_page

    @property
    def review_page(self) -> ReviewPage:
        return self._review_page

    @property
    def back_button(self) -> QPushButton:
        return self._back_btn

    @property
    def next_button(self) -> QPushButton:
        return self._next_btn

    def set_library_index(self, index: LibraryIndex) -> None:
        """Load library data into pages that need it."""
        self._library_index = index
        self._persona_page.load_personas(index)
        self._expertise_page.load_expertise(index)
        self._hooks_page.load_hook_packs(index)
        logger.info("Library loaded into builder wizard")

    def reset_wizard(self) -> None:
        """Reset to step 0. Selections are preserved (BEAN-288)."""
        self._page_stack.setCurrentIndex(0)
        self._update_nav_state()
        self._emit_state_changed()

    def has_in_progress_state(self) -> bool:
        """Return True when the wizard holds non-default user input.

        BEAN-288: drives the sidebar "New Project" → "Resume Project" flip
        and the visibility of the in-wizard Start Over button. The heuristic
        is intentionally simple — any sign of work-in-progress qualifies:
        a non-empty project name, any selected persona or expertise, or the
        user advanced past step 0.
        """
        if self._page_stack.currentIndex() > 0:
            return True
        if self._project_page.name_edit.text().strip():
            return True
        if any(
            card.is_selected for card in self._persona_page.persona_cards.values()
        ):
            return True
        if self._expertise_page.get_expertise_selections():
            return True
        return False

    def start_over(self) -> None:
        """Clear every page's state and return to step 0 (BEAN-288).

        Distinct from :meth:`reset_wizard` (which is page-index-only). After
        this call ``has_in_progress_state()`` is False.
        """
        self._project_page.name_edit.setText("")
        self._project_page.tagline_edit.setText("")
        self._project_page.slug_edit.setText("")
        for card in self._persona_page.persona_cards.values():
            card.is_selected = False
        for card in self._expertise_page.expertise_cards.values():
            card.is_selected = False
        # Re-load the hooks page from the library if available so its
        # default-conflict resolution (BEAN-286) re-runs from a clean slate.
        if self._library_index is not None:
            self._hooks_page.load_hook_packs(self._library_index)
        self._page_stack.setCurrentIndex(0)
        self._update_nav_state()
        self._emit_state_changed()

    def _wire_state_change_signals(self) -> None:
        """Re-emit ``state_changed`` whenever a page-level signal flips the
        in-progress answer. Keeping this in one place avoids a fan-out of
        ad-hoc wiring across the builder."""
        self._project_page.completeness_changed.connect(
            lambda _checked: self._emit_state_changed()
        )
        self._persona_page.selection_changed.connect(self._emit_state_changed)
        self._expertise_page.selection_changed.connect(self._emit_state_changed)
        self._page_stack.currentChanged.connect(
            lambda _idx: self._emit_state_changed()
        )

    def _emit_state_changed(self) -> None:
        in_progress = self.has_in_progress_state()
        self._start_over_btn.setVisible(in_progress)
        if in_progress != self._last_in_progress:
            self._last_in_progress = in_progress
            self.state_changed.emit(in_progress)

    # -- Navigation --------------------------------------------------------

    def _go_back(self) -> None:
        idx = self._page_stack.currentIndex()
        if idx > 0:
            self._page_stack.setCurrentIndex(idx - 1)
            self._update_nav_state()

    def _go_next(self) -> None:
        idx = self._page_stack.currentIndex()
        if not self._is_current_page_valid():
            return
        if idx < len(self._pages) - 1:
            # If moving to review page, build and set the composition spec
            if idx + 1 == len(self._pages) - 1:
                spec = self._build_composition_spec()
                self._review_page.set_composition_spec(spec)
            self._page_stack.setCurrentIndex(idx + 1)
            self._update_nav_state()

    def _is_current_page_valid(self) -> bool:
        idx = self._page_stack.currentIndex()
        page = self._pages[idx]
        if hasattr(page, "is_complete"):
            return page.is_complete()
        if hasattr(page, "is_valid"):
            return page.is_valid()
        return True

    def _update_next_enabled(self) -> None:
        """Enable/disable Next button based on current page validity."""
        idx = self._page_stack.currentIndex()
        if idx >= len(self._pages) - 1:
            return  # Review page — Next is hidden
        valid = self._is_current_page_valid()
        self._next_btn.setEnabled(valid)

    def _update_nav_state(self) -> None:
        idx = self._page_stack.currentIndex()
        self._back_btn.setVisible(idx > 0)
        # Hide Next on review page (generate button lives there)
        self._next_btn.setVisible(idx < len(self._pages) - 1)
        self._update_next_enabled()

        # Update step indicator styles
        for i, label in enumerate(self._step_labels):
            if i == idx:
                label.setStyleSheet(f"""
                    color: {theme.ACCENT_PRIMARY};
                    font-weight: {theme.FONT_WEIGHT_BOLD};
                    padding: {theme.SPACE_XS}px {theme.SPACE_SM}px;
                    border-bottom: 2px solid {theme.ACCENT_PRIMARY};
                """)
            elif i < idx:
                label.setStyleSheet(f"""
                    color: {theme.TEXT_SECONDARY};
                    padding: {theme.SPACE_XS}px {theme.SPACE_SM}px;
                """)
            else:
                label.setStyleSheet(f"""
                    color: {theme.TEXT_DISABLED};
                    padding: {theme.SPACE_XS}px {theme.SPACE_SM}px;
                """)

    # -- Composition spec building -----------------------------------------

    def _build_composition_spec(self) -> CompositionSpec:
        """Collect data from all wizard pages into a CompositionSpec."""
        project = self._project_page.get_data()
        team = self._persona_page.get_team_config()
        expertise = self._expertise_page.get_expertise_selections()
        architecture = self._architecture_page.get_architecture_config()
        hooks = self._hooks_page.get_hooks_config()
        safety = self._hooks_page.get_safety_config()

        return CompositionSpec(
            project=project,
            team=team,
            expertise=expertise,
            architecture=architecture,
            hooks=hooks,
            safety=safety,
            generation=GenerationOptions(),
        )

    def _on_generate(self) -> None:
        spec = self._review_page.get_composition_spec()
        if spec is not None:
            logger.info("Generate requested for project: %s", spec.project.name)
            self.generate_requested.emit(spec)

    # -- Styles ------------------------------------------------------------

    def _nav_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {theme.BG_SURFACE};
                color: {theme.TEXT_PRIMARY};
                border: 1px solid {theme.BORDER_DEFAULT};
                border-radius: {theme.RADIUS_SM}px;
                padding: {theme.SPACE_SM}px {theme.SPACE_XL}px;
                font-size: {theme.FONT_SIZE_MD}px;
            }}
            QPushButton:hover {{
                background-color: {theme.BG_OVERLAY};
            }}
        """

    def _primary_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {theme.ACCENT_PRIMARY};
                color: {theme.TEXT_ON_ACCENT};
                border: none;
                border-radius: {theme.RADIUS_SM}px;
                padding: {theme.SPACE_SM}px {theme.SPACE_XL}px;
                font-size: {theme.FONT_SIZE_MD}px;
                font-weight: {theme.FONT_WEIGHT_BOLD};
            }}
            QPushButton:hover {{
                background-color: {theme.ACCENT_PRIMARY_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {theme.ACCENT_PRIMARY_MUTED};
                color: {theme.TEXT_DISABLED};
            }}
        """
