"""Wizard page 5 — Hook & Safety Configuration.

Allows users to configure hook packs (posture + per-pack enable/mode) and
safety policies (git, shell, filesystem, network, secrets, destructive ops).
Provides preset buttons for quick safety configuration.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    DestructiveOpsPolicy,
    FileSystemPolicy,
    GitPolicy,
    HookMode,
    HookPackInfo,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    NetworkPolicy,
    Posture,
    SafetyConfig,
    SecretPolicy,
    ShellPolicy,
)
from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_SECONDARY_MUTED,
    BG_INSET,
    BG_OVERLAY,
    BG_SURFACE,
    BORDER_DEFAULT,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_SIZE_XS,
    FONT_WEIGHT_BOLD,
    RADIUS_MD,
    RADIUS_SM,
    SPACE_LG,
    SPACE_MD,
    SPACE_SM,
    SPACE_XL,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Human-readable hook pack descriptions (keyed by pack id)
# ---------------------------------------------------------------------------

HOOK_PACK_DESCRIPTIONS: dict[str, tuple[str, str]] = {
    # Code quality
    "pre-commit-lint": ("Pre-Commit Lint", "Linting and formatting checks before code commit"),
    "post-task-qa": ("Post-Task QA", "Output validation after task completion"),
    "security-scan": ("Security Scan", "Security and secret scanning"),
    "compliance-gate": ("Compliance Gate", "Compliance verification"),
    "hook-policy": ("Hook Policy", "Hook policy documentation"),
    # Git workflow
    "git-commit-branch": ("Commit Branch Guard", "Prevent direct commits to protected branches"),
    "git-push-feature": ("Push Feature Branch", "Push feature branch with upstream tracking"),
    "git-generate-pr": ("Generate PR", "Create pull requests via gh CLI"),
    "git-merge-to-test": ("Merge to Test", "Merge approved PRs to test branch"),
    "git-merge-to-prod": ("Merge to Prod", "Merge test to production with safety gates"),
    # Azure CLI
    "az-read-only": ("Az Read-Only", "Allow only read operations on Azure resources"),
    "az-limited-ops": ("Az Limited-Ops", "Allow deploys, block destructive Azure operations"),
}

# Category display names
CATEGORY_LABELS: dict[str, str] = {
    "git": "Git Workflow",
    "az": "Azure CLI",
    "code-quality": "Code Quality",
    "": "Other",
}

# ---------------------------------------------------------------------------
# Stylesheet constants (theme-based)
# ---------------------------------------------------------------------------

CARD_STYLE = f"""
QFrame#hook-card {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_MD}px;
}}
QFrame#hook-card:hover {{
    border-color: {ACCENT_SECONDARY_MUTED};
}}
"""

CARD_SELECTED_BORDER = f"border-color: {ACCENT_PRIMARY};"

SECTION_STYLE = f"""
QFrame#safety-section {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_MD}px;
}}
"""

LABEL_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px; font-weight: {FONT_WEIGHT_BOLD};"
)
DESC_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
CONFIG_LABEL_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
HEADING_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_XL}px; font-weight: {FONT_WEIGHT_BOLD};"
)
SUBHEADING_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
SECTION_HEADING_STYLE = (
    f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_LG}px; font-weight: {FONT_WEIGHT_BOLD};"
)
FILES_STYLE = f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_XS}px; font-style: italic;"
PRESET_BTN_STYLE = f"""
QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM // 2}px {SPACE_MD}px;
    font-size: {FONT_SIZE_SM}px;
}}
QPushButton:hover {{
    background-color: {BG_INSET};
}}
"""

COMBO_STYLE = f"""
QComboBox {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM // 2}px {SPACE_SM}px;
    font-size: {FONT_SIZE_SM}px;
}}
QComboBox:focus {{
    border-color: {ACCENT_PRIMARY};
    border-width: 2px;
}}
QComboBox:hover {{
    border-color: {ACCENT_SECONDARY_MUTED};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: {SPACE_SM}px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_SECONDARY};
    margin-right: {SPACE_SM}px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_OVERLAY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    selection-background-color: {ACCENT_SECONDARY_MUTED};
    selection-color: {TEXT_PRIMARY};
    padding: {SPACE_SM // 2}px;
}}
"""

CHECKBOX_STYLE = f"""
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 3px;
    background-color: {BG_INSET};
}}
QCheckBox::indicator:hover {{
    border-color: {ACCENT_SECONDARY_MUTED};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT_PRIMARY};
    border-color: {ACCENT_PRIMARY_HOVER};
}}
"""


# ---------------------------------------------------------------------------
# HookPackCard — single hook pack row widget
# ---------------------------------------------------------------------------

class HookPackCard(QFrame):
    """A card representing a single hook pack with enable checkbox and mode selector."""

    toggled = Signal(str, bool)  # pack_id, checked

    def __init__(self, pack: HookPackInfo, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pack = pack
        self.setObjectName("hook-card")
        self.setStyleSheet(CARD_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_SM + 2, SPACE_MD, SPACE_SM + 2)
        layout.setSpacing(SPACE_SM + 2)

        # Checkbox
        self._checkbox = QCheckBox()
        self._checkbox.setStyleSheet(CHECKBOX_STYLE)
        self._checkbox.setChecked(True)  # enabled by default
        self._checkbox.stateChanged.connect(self._on_toggled)
        layout.addWidget(self._checkbox)

        # Name and description
        display_name, desc = HOOK_PACK_DESCRIPTIONS.get(
            self._pack.id, (self._pack.id.replace("-", " ").title(), "")
        )

        name_label = QLabel(display_name)
        name_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(name_label)

        desc_label = QLabel(f"— {desc}" if desc else "")
        desc_label.setStyleSheet(DESC_STYLE)
        layout.addWidget(desc_label, stretch=1)

        # File count badge
        file_count = len(self._pack.files)
        if file_count > 0:
            badge = QLabel(f"{file_count} file{'s' if file_count != 1 else ''}")
            badge.setStyleSheet(FILES_STYLE)
            layout.addWidget(badge)

        # Mode selector
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet(CONFIG_LABEL_STYLE)
        layout.addWidget(mode_label)

        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(COMBO_STYLE)
        self._mode_combo.addItems(["enforcing", "permissive", "disabled"])
        self._mode_combo.setCurrentText("enforcing")
        self._mode_combo.setFixedWidth(100)
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        layout.addWidget(self._mode_combo)

    # -- State access -------------------------------------------------------

    @property
    def pack_id(self) -> str:
        return self._pack.id

    @property
    def is_enabled(self) -> bool:
        return self._checkbox.isChecked()

    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        self._checkbox.setChecked(value)

    @property
    def mode(self) -> HookMode:
        return HookMode(self._mode_combo.currentText())

    @mode.setter
    def mode(self, value: HookMode) -> None:
        self._mode_combo.setCurrentText(value.value)

    @property
    def file_count(self) -> int:
        return len(self._pack.files)

    def to_hook_pack_selection(self) -> HookPackSelection:
        """Build a HookPackSelection from the current card state."""
        return HookPackSelection(
            id=self._pack.id,
            category=self._pack.category,
            enabled=self._checkbox.isChecked(),
            mode=self.mode,
        )

    def load_from_selection(self, sel: HookPackSelection) -> None:
        """Restore card state from a HookPackSelection."""
        self._checkbox.setChecked(sel.enabled)
        self._mode_combo.setCurrentText(sel.mode.value)

    # -- Slots --------------------------------------------------------------

    def _on_toggled(self, state: int) -> None:
        checked = state == Qt.CheckState.Checked.value
        self.toggled.emit(self._pack.id, checked)
        if checked:
            self.setStyleSheet(CARD_STYLE + f"QFrame#hook-card {{ {CARD_SELECTED_BORDER} }}")
        else:
            self.setStyleSheet(CARD_STYLE)

    def _on_mode_changed(self, _text: str) -> None:
        self.toggled.emit(self._pack.id, self.is_enabled)


# ---------------------------------------------------------------------------
# SafetyPolicySection — toggle group for one safety domain
# ---------------------------------------------------------------------------

class SafetyPolicySection(QFrame):
    """A collapsible section showing toggles for one safety policy domain."""

    changed = Signal()

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._toggles: dict[str, QCheckBox] = {}
        self.setObjectName("safety-section")
        self.setStyleSheet(SECTION_STYLE)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACE_MD, SPACE_SM + 2, SPACE_MD, SPACE_SM + 2)
        self._layout.setSpacing(SPACE_SM - 2)

        heading = QLabel(title)
        heading.setStyleSheet(SECTION_HEADING_STYLE)
        self._layout.addWidget(heading)

    def add_toggle(self, key: str, label: str, default: bool = True) -> QCheckBox:
        """Add a boolean toggle to this section."""
        row = QHBoxLayout()
        row.setSpacing(SPACE_SM + 2)

        cb = QCheckBox()
        cb.setStyleSheet(CHECKBOX_STYLE)
        cb.setChecked(default)
        cb.stateChanged.connect(lambda _: self.changed.emit())
        row.addWidget(cb)

        lbl = QLabel(label)
        lbl.setStyleSheet(CONFIG_LABEL_STYLE)
        row.addWidget(lbl, stretch=1)

        self._layout.addLayout(row)
        self._toggles[key] = cb
        return cb

    def get_toggle(self, key: str) -> bool:
        """Get the current value of a toggle."""
        if key in self._toggles:
            return self._toggles[key].isChecked()
        return False

    def set_toggle(self, key: str, value: bool) -> None:
        """Set the value of a toggle."""
        if key in self._toggles:
            self._toggles[key].setChecked(value)

    @property
    def toggles(self) -> dict[str, QCheckBox]:
        return dict(self._toggles)

    @property
    def title(self) -> str:
        return self._title


# ---------------------------------------------------------------------------
# HookSafetyPage — wizard page widget
# ---------------------------------------------------------------------------

class HookSafetyPage(QWidget):
    """Wizard page for configuring hook packs and safety policies.

    Emits ``selection_changed`` whenever any configuration changes.
    Call ``get_hooks_config()`` and ``get_safety_config()`` for current state.
    """

    selection_changed = Signal()

    def __init__(
        self,
        library_index: LibraryIndex | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cards: dict[str, HookPackCard] = {}
        self._category_labels: list[QLabel] = []
        self._safety_sections: dict[str, SafetyPolicySection] = {}
        self._build_ui()
        if library_index is not None:
            self.load_hook_packs(library_index)

    # -- UI construction ----------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(SPACE_XL, SPACE_XL - 4, SPACE_XL, SPACE_XL - 4)
        outer.setSpacing(SPACE_MD)

        heading = QLabel("Hook & Safety Configuration")
        heading.setStyleSheet(HEADING_STYLE)
        outer.addWidget(heading)

        subtitle = QLabel(
            "Configure hook packs and safety policies for your project. "
            "Hook packs define automated checks, while safety policies control "
            "what operations are allowed during development."
        )
        subtitle.setStyleSheet(SUBHEADING_STYLE)
        subtitle.setWordWrap(True)
        outer.addWidget(subtitle)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(SPACE_LG)

        # --- Hooks section ---
        self._build_hooks_section()

        # --- Safety section ---
        self._build_safety_section()

        self._content_layout.addStretch(1)
        scroll.setWidget(self._content)
        outer.addWidget(scroll, stretch=1)

    def _build_hooks_section(self) -> None:
        """Build the hooks configuration section."""
        hooks_heading = QLabel("Hook Packs")
        hooks_heading.setStyleSheet(SECTION_HEADING_STYLE)
        self._content_layout.addWidget(hooks_heading)

        # Posture selector row
        posture_row = QHBoxLayout()
        posture_row.setSpacing(SPACE_SM + 2)

        posture_label = QLabel("Safety Posture:")
        posture_label.setStyleSheet(CONFIG_LABEL_STYLE)
        posture_row.addWidget(posture_label)

        self._posture_combo = QComboBox()
        self._posture_combo.setStyleSheet(COMBO_STYLE)
        self._posture_combo.addItems(["baseline", "hardened", "regulated"])
        self._posture_combo.setCurrentText("baseline")
        self._posture_combo.setFixedWidth(130)
        self._posture_combo.currentTextChanged.connect(self._on_posture_changed)
        posture_row.addWidget(self._posture_combo)

        posture_row.addStretch(1)
        self._content_layout.addLayout(posture_row)

        # Empty-state label for hooks (visible until library is loaded)
        self._hook_empty_label = QLabel(
            "No library loaded. Go to Settings and configure your "
            "Library Root to populate this page."
        )
        self._hook_empty_label.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_SM}px;"
        )
        self._hook_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hook_empty_label.setWordWrap(True)
        self._content_layout.addWidget(self._hook_empty_label)

        # Hook card container
        self._hook_card_container = QWidget()
        self._hook_card_layout = QVBoxLayout(self._hook_card_container)
        self._hook_card_layout.setContentsMargins(0, 0, 0, 0)
        self._hook_card_layout.setSpacing(SPACE_SM)
        self._content_layout.addWidget(self._hook_card_container)

    def _build_safety_section(self) -> None:
        """Build the safety policies section with preset buttons and toggles."""
        safety_heading = QLabel("Safety Policies")
        safety_heading.setStyleSheet(SECTION_HEADING_STYLE)
        self._content_layout.addWidget(safety_heading)

        # Preset buttons
        preset_row = QHBoxLayout()
        preset_row.setSpacing(SPACE_SM)

        self._permissive_btn = QPushButton("Permissive")
        self._permissive_btn.setStyleSheet(PRESET_BTN_STYLE)
        self._permissive_btn.clicked.connect(self._apply_permissive)
        preset_row.addWidget(self._permissive_btn)

        self._baseline_btn = QPushButton("Baseline")
        self._baseline_btn.setStyleSheet(PRESET_BTN_STYLE)
        self._baseline_btn.clicked.connect(self._apply_baseline)
        preset_row.addWidget(self._baseline_btn)

        self._hardened_btn = QPushButton("Hardened")
        self._hardened_btn.setStyleSheet(PRESET_BTN_STYLE)
        self._hardened_btn.clicked.connect(self._apply_hardened)
        preset_row.addWidget(self._hardened_btn)

        preset_row.addStretch(1)
        self._content_layout.addLayout(preset_row)

        # Git policy
        git_section = SafetyPolicySection("Git Policy")
        git_section.add_toggle("allow_push", "Allow push", default=True)
        git_section.add_toggle("allow_force_push", "Allow force push", default=False)
        git_section.add_toggle("allow_branch_delete", "Allow branch delete", default=False)
        git_section.changed.connect(self._on_safety_changed)
        self._safety_sections["git"] = git_section
        self._content_layout.addWidget(git_section)

        # Shell policy
        shell_section = SafetyPolicySection("Shell Policy")
        shell_section.add_toggle("allow_shell", "Allow shell commands", default=True)
        shell_section.changed.connect(self._on_safety_changed)
        self._safety_sections["shell"] = shell_section
        self._content_layout.addWidget(shell_section)

        # Filesystem policy
        fs_section = SafetyPolicySection("Filesystem Policy")
        fs_section.add_toggle("allow_write", "Allow file writes", default=True)
        fs_section.add_toggle("allow_delete", "Allow file deletes", default=False)
        fs_section.changed.connect(self._on_safety_changed)
        self._safety_sections["filesystem"] = fs_section
        self._content_layout.addWidget(fs_section)

        # Network policy
        net_section = SafetyPolicySection("Network Policy")
        net_section.add_toggle("allow_network", "Allow network access", default=True)
        net_section.changed.connect(self._on_safety_changed)
        self._safety_sections["network"] = net_section
        self._content_layout.addWidget(net_section)

        # Secrets policy
        secrets_section = SafetyPolicySection("Secrets Policy")
        secrets_section.add_toggle("scan_for_secrets", "Scan for secrets", default=True)
        secrets_section.add_toggle("block_on_secret", "Block on secret found", default=True)
        secrets_section.changed.connect(self._on_safety_changed)
        self._safety_sections["secrets"] = secrets_section
        self._content_layout.addWidget(secrets_section)

        # Destructive ops policy
        destruct_section = SafetyPolicySection("Destructive Operations Policy")
        destruct_section.add_toggle(
            "allow_destructive", "Allow destructive operations", default=False
        )
        destruct_section.add_toggle(
            "require_confirmation", "Require confirmation", default=True
        )
        destruct_section.changed.connect(self._on_safety_changed)
        self._safety_sections["destructive_ops"] = destruct_section
        self._content_layout.addWidget(destruct_section)

    # -- Public API ---------------------------------------------------------

    def load_hook_packs(self, library_index: LibraryIndex) -> None:
        """Populate the hook pack section with packs from a LibraryIndex, grouped by category."""
        # Clear existing cards and category labels
        for card in self._cards.values():
            self._hook_card_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        for widget in self._category_labels:
            self._hook_card_layout.removeWidget(widget)
            widget.deleteLater()
        self._category_labels.clear()

        # Group packs by category
        groups: dict[str, list[HookPackInfo]] = {}
        for pack in library_index.hook_packs:
            cat = pack.category or ""
            groups.setdefault(cat, []).append(pack)

        # Render groups in a stable order
        category_order = ["git", "az", "code-quality", ""]
        for cat in category_order:
            packs = groups.get(cat, [])
            if not packs:
                continue

            # Category heading
            cat_label = CATEGORY_LABELS.get(cat, cat.replace("-", " ").title())
            heading = QLabel(cat_label)
            heading.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: {FONT_SIZE_MD}px; "
                f"font-weight: {FONT_WEIGHT_BOLD}; "
                f"padding-top: {SPACE_SM}px;"
            )
            self._hook_card_layout.addWidget(heading)
            self._category_labels.append(heading)

            for pack in packs:
                card = HookPackCard(pack)
                card.toggled.connect(self._on_card_toggled)
                self._hook_card_layout.addWidget(card)
                self._cards[pack.id] = card

        self._hook_empty_label.setVisible(len(self._cards) == 0)
        logger.info("Loaded %d hook pack cards in %d categories", len(self._cards), len(groups))

    def get_hooks_config(self) -> HooksConfig:
        """Return the current hook configuration."""
        packs = [card.to_hook_pack_selection() for card in self._cards.values()]
        return HooksConfig(
            posture=Posture(self._posture_combo.currentText()),
            packs=packs,
        )

    def set_hooks_config(self, config: HooksConfig) -> None:
        """Restore hook configuration state."""
        self._posture_combo.setCurrentText(config.posture.value)
        pack_map = {p.id: p for p in config.packs}
        for pid, card in self._cards.items():
            if pid in pack_map:
                card.load_from_selection(pack_map[pid])
            else:
                card.is_enabled = True
                card.mode = HookMode.ENFORCING

    def get_safety_config(self) -> SafetyConfig:
        """Return the current safety configuration."""
        git_sec = self._safety_sections["git"]
        shell_sec = self._safety_sections["shell"]
        fs_sec = self._safety_sections["filesystem"]
        net_sec = self._safety_sections["network"]
        secrets_sec = self._safety_sections["secrets"]
        destruct_sec = self._safety_sections["destructive_ops"]

        return SafetyConfig(
            git=GitPolicy(
                allow_push=git_sec.get_toggle("allow_push"),
                allow_force_push=git_sec.get_toggle("allow_force_push"),
                allow_branch_delete=git_sec.get_toggle("allow_branch_delete"),
            ),
            shell=ShellPolicy(
                allow_shell=shell_sec.get_toggle("allow_shell"),
            ),
            filesystem=FileSystemPolicy(
                allow_write=fs_sec.get_toggle("allow_write"),
                allow_delete=fs_sec.get_toggle("allow_delete"),
            ),
            network=NetworkPolicy(
                allow_network=net_sec.get_toggle("allow_network"),
            ),
            secrets=SecretPolicy(
                scan_for_secrets=secrets_sec.get_toggle("scan_for_secrets"),
                block_on_secret=secrets_sec.get_toggle("block_on_secret"),
            ),
            destructive_ops=DestructiveOpsPolicy(
                allow_destructive=destruct_sec.get_toggle("allow_destructive"),
                require_confirmation=destruct_sec.get_toggle("require_confirmation"),
            ),
        )

    def set_safety_config(self, config: SafetyConfig) -> None:
        """Restore safety configuration state."""
        git_sec = self._safety_sections["git"]
        git_sec.set_toggle("allow_push", config.git.allow_push)
        git_sec.set_toggle("allow_force_push", config.git.allow_force_push)
        git_sec.set_toggle("allow_branch_delete", config.git.allow_branch_delete)

        shell_sec = self._safety_sections["shell"]
        shell_sec.set_toggle("allow_shell", config.shell.allow_shell)

        fs_sec = self._safety_sections["filesystem"]
        fs_sec.set_toggle("allow_write", config.filesystem.allow_write)
        fs_sec.set_toggle("allow_delete", config.filesystem.allow_delete)

        net_sec = self._safety_sections["network"]
        net_sec.set_toggle("allow_network", config.network.allow_network)

        secrets_sec = self._safety_sections["secrets"]
        secrets_sec.set_toggle("scan_for_secrets", config.secrets.scan_for_secrets)
        secrets_sec.set_toggle("block_on_secret", config.secrets.block_on_secret)

        destruct_sec = self._safety_sections["destructive_ops"]
        destruct_sec.set_toggle("allow_destructive", config.destructive_ops.allow_destructive)
        destruct_sec.set_toggle(
            "require_confirmation", config.destructive_ops.require_confirmation
        )

    @property
    def posture(self) -> Posture:
        """Get the current posture selection."""
        return Posture(self._posture_combo.currentText())

    @posture.setter
    def posture(self, value: Posture) -> None:
        """Set the posture selection."""
        self._posture_combo.setCurrentText(value.value)

    def is_valid(self) -> bool:
        """Hook & safety page is always valid (sensible defaults exist)."""
        return True

    @property
    def hook_cards(self) -> dict[str, HookPackCard]:
        """Access cards by pack id (for testing)."""
        return dict(self._cards)

    @property
    def safety_sections(self) -> dict[str, SafetyPolicySection]:
        """Access safety sections by domain key (for testing)."""
        return dict(self._safety_sections)

    # -- Slots --------------------------------------------------------------

    def _on_card_toggled(self, pack_id: str, checked: bool) -> None:
        logger.debug("Hook pack %s toggled: %s", pack_id, checked)
        self.selection_changed.emit()

    def _on_posture_changed(self, _text: str) -> None:
        self.selection_changed.emit()

    def _on_safety_changed(self) -> None:
        self.selection_changed.emit()

    def _apply_permissive(self) -> None:
        """Apply permissive safety preset."""
        self.set_safety_config(SafetyConfig.permissive_safety())

    def _apply_baseline(self) -> None:
        """Apply baseline safety preset."""
        self.set_safety_config(SafetyConfig.baseline_safety())

    def _apply_hardened(self) -> None:
        """Apply hardened safety preset."""
        self.set_safety_config(SafetyConfig.hardened_safety())
