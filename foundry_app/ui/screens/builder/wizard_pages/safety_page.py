"""Step 3: Safety — questionnaire to build SafetyConfig."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import (
    DestructiveOpsPolicy,
    FileSystemPolicy,
    GitPolicy,
    NetworkPolicy,
    SafetyConfig,
    SecretPolicy,
    ShellPolicy,
)
from foundry_app.services.safety import (
    baseline_safety,
    hardened_safety,
    permissive_safety,
)

_PRESET_OPTIONS = ["baseline", "hardened", "permissive", "custom"]

_PRESET_DESCRIPTIONS = {
    "baseline": "Sensible defaults — blocks dangerous ops, allows normal development.",
    "hardened": "Maximum guardrails — restricted by default, ask for everything.",
    "permissive": "Fully open — minimal restrictions, for trusted environments.",
    "custom": "Configure each policy individually below.",
}


class SafetyPage(QWidget):
    """Safety questionnaire with preset selector and per-category checkboxes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # --- Preset selector ---
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Safety Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(_PRESET_OPTIONS)
        self.preset_combo.setCurrentText("baseline")
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_row.addWidget(self.preset_combo)
        preset_row.addStretch()
        layout.addLayout(preset_row)

        self._preset_desc = QLabel(_PRESET_DESCRIPTIONS["baseline"])
        self._preset_desc.setWordWrap(True)
        self._preset_desc.setStyleSheet("color: #666; margin-bottom: 8px;")
        layout.addWidget(self._preset_desc)

        # --- Git policy ---
        git_group = QGroupBox("Git")
        git_layout = QVBoxLayout(git_group)
        self.chk_allow_push = QCheckBox("Allow git push")
        self.chk_allow_push.setChecked(True)
        git_layout.addWidget(self.chk_allow_push)
        self.chk_allow_force_push = QCheckBox("Allow git push --force")
        git_layout.addWidget(self.chk_allow_force_push)
        self.chk_allow_branch_delete = QCheckBox("Allow git branch -D")
        git_layout.addWidget(self.chk_allow_branch_delete)
        layout.addWidget(git_group)

        # --- Shell policy ---
        shell_group = QGroupBox("Shell")
        shell_layout = QVBoxLayout(shell_group)
        self.chk_allow_sudo = QCheckBox("Allow sudo")
        shell_layout.addWidget(self.chk_allow_sudo)
        self.chk_allow_install = QCheckBox("Allow package installation")
        self.chk_allow_install.setChecked(True)
        shell_layout.addWidget(self.chk_allow_install)
        layout.addWidget(shell_group)

        # --- Destructive ops ---
        destructive_group = QGroupBox("Destructive Operations")
        destructive_layout = QVBoxLayout(destructive_group)
        self.chk_allow_rm_rf = QCheckBox("Allow rm -rf")
        destructive_layout.addWidget(self.chk_allow_rm_rf)
        self.chk_allow_reset_hard = QCheckBox("Allow git reset --hard")
        destructive_layout.addWidget(self.chk_allow_reset_hard)
        self.chk_allow_clean = QCheckBox("Allow git clean -f")
        destructive_layout.addWidget(self.chk_allow_clean)
        layout.addWidget(destructive_group)

        # --- Filesystem / Network / Secrets (compact row) ---
        extras_row = QHBoxLayout()

        fs_group = QGroupBox("Filesystem")
        fs_layout = QVBoxLayout(fs_group)
        self.chk_allow_outside = QCheckBox("Allow outside project")
        fs_layout.addWidget(self.chk_allow_outside)
        fs_layout.addWidget(QLabel("Editable directories:"))
        self.txt_editable_dirs = QLineEdit()
        self.txt_editable_dirs.setText("src/**, tests/**, ai/**")
        self.txt_editable_dirs.setPlaceholderText("src/**, tests/**, ai/**")
        self.txt_editable_dirs.setToolTip(
            "Comma-separated glob patterns for directories agents can edit."
        )
        fs_layout.addWidget(self.txt_editable_dirs)
        extras_row.addWidget(fs_group)

        net_group = QGroupBox("Network")
        net_layout = QVBoxLayout(net_group)
        self.chk_allow_network = QCheckBox("Allow network")
        self.chk_allow_network.setChecked(True)
        net_layout.addWidget(self.chk_allow_network)
        self.chk_allow_external_apis = QCheckBox("Allow external APIs")
        self.chk_allow_external_apis.setChecked(True)
        net_layout.addWidget(self.chk_allow_external_apis)
        extras_row.addWidget(net_group)

        secrets_group = QGroupBox("Secrets")
        secrets_layout = QVBoxLayout(secrets_group)
        self.chk_block_env = QCheckBox("Block .env files")
        self.chk_block_env.setChecked(True)
        secrets_layout.addWidget(self.chk_block_env)
        self.chk_block_creds = QCheckBox("Block credentials")
        self.chk_block_creds.setChecked(True)
        secrets_layout.addWidget(self.chk_block_creds)
        extras_row.addWidget(secrets_group)

        layout.addLayout(extras_row)
        layout.addStretch()

        # Store all config groups for enabling/disabling
        self._config_groups = [
            git_group, shell_group, destructive_group,
            fs_group, net_group, secrets_group,
        ]

    def _on_preset_changed(self, preset: str) -> None:
        self._preset_desc.setText(_PRESET_DESCRIPTIONS.get(preset, ""))

        if preset == "custom":
            for g in self._config_groups:
                g.setEnabled(True)
            return

        # Apply the preset values to checkboxes
        if preset == "permissive":
            config = permissive_safety()
        elif preset == "hardened":
            config = hardened_safety()
        else:
            config = baseline_safety()

        self._apply_config(config)

        # Disable individual controls for non-custom presets
        for g in self._config_groups:
            g.setEnabled(False)

    def _apply_config(self, config: SafetyConfig) -> None:
        self.chk_allow_push.setChecked(config.git.allow_push)
        self.chk_allow_force_push.setChecked(config.git.allow_force_push)
        self.chk_allow_branch_delete.setChecked(config.git.allow_branch_delete)
        self.chk_allow_sudo.setChecked(config.shell.allow_sudo)
        self.chk_allow_install.setChecked(config.shell.allow_install)
        self.chk_allow_rm_rf.setChecked(config.destructive.allow_rm_rf)
        self.chk_allow_reset_hard.setChecked(config.destructive.allow_reset_hard)
        self.chk_allow_clean.setChecked(config.destructive.allow_clean)
        self.chk_allow_outside.setChecked(config.filesystem.allow_outside_project)
        self.txt_editable_dirs.setText(", ".join(config.filesystem.editable_dirs))
        self.chk_allow_network.setChecked(config.network.allow_network)
        self.chk_allow_external_apis.setChecked(config.network.allow_external_apis)
        self.chk_block_env.setChecked(config.secrets.block_env_files)
        self.chk_block_creds.setChecked(config.secrets.block_credentials)

    def _parse_editable_dirs(self) -> list[str]:
        """Parse the editable dirs text field into a list of patterns."""
        raw = self.txt_editable_dirs.text().strip()
        if not raw:
            return []
        return [d.strip() for d in raw.split(",") if d.strip()]

    def build_safety_config(self) -> SafetyConfig:
        """Build a SafetyConfig from the current checkbox state."""
        preset = self.preset_combo.currentText()
        return SafetyConfig(
            preset=preset,
            git=GitPolicy(
                allow_push=self.chk_allow_push.isChecked(),
                allow_force_push=self.chk_allow_force_push.isChecked(),
                allow_branch_delete=self.chk_allow_branch_delete.isChecked(),
            ),
            shell=ShellPolicy(
                allow_sudo=self.chk_allow_sudo.isChecked(),
                allow_install=self.chk_allow_install.isChecked(),
            ),
            filesystem=FileSystemPolicy(
                allow_outside_project=self.chk_allow_outside.isChecked(),
                editable_dirs=self._parse_editable_dirs(),
            ),
            network=NetworkPolicy(
                allow_network=self.chk_allow_network.isChecked(),
                allow_external_apis=self.chk_allow_external_apis.isChecked(),
            ),
            secrets=SecretPolicy(
                block_env_files=self.chk_block_env.isChecked(),
                block_credentials=self.chk_block_creds.isChecked(),
            ),
            destructive=DestructiveOpsPolicy(
                allow_rm_rf=self.chk_allow_rm_rf.isChecked(),
                allow_reset_hard=self.chk_allow_reset_hard.isChecked(),
                allow_clean=self.chk_allow_clean.isChecked(),
            ),
        )
