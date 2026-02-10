"""Tests for foundry_app.ui.screens.builder.wizard_pages.hook_safety_page."""

import pytest
from PySide6.QtWidgets import QApplication

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
from foundry_app.ui.screens.builder.wizard_pages.hook_safety_page import (
    HOOK_PACK_DESCRIPTIONS,
    HookPackCard,
    HookSafetyPage,
    SafetyPolicySection,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pack(pid: str, files: list[str] | None = None) -> HookPackInfo:
    """Create a minimal HookPackInfo for testing."""
    return HookPackInfo(
        id=pid,
        path=f"/fake/hooks/{pid}",
        files=files or [],
    )


def _make_library(*pack_ids: str) -> LibraryIndex:
    """Create a LibraryIndex with the given hook pack ids."""
    return LibraryIndex(
        library_root="/fake/library",
        hook_packs=[_make_pack(pid) for pid in pack_ids],
    )


def _make_full_library() -> LibraryIndex:
    """Create a LibraryIndex matching the real hook packs."""
    return _make_library(
        "pre-commit-lint", "post-task-qa", "security-scan", "compliance-gate",
    )


def _make_library_with_files() -> LibraryIndex:
    """Create a LibraryIndex where packs have hook files."""
    return LibraryIndex(
        library_root="/fake/library",
        hook_packs=[
            _make_pack("pre-commit-lint", ["lint-check.md", "format-check.md"]),
            _make_pack("security-scan", ["secret-scan.md"]),
            _make_pack("compliance-gate", []),
        ],
    )


# ---------------------------------------------------------------------------
# HookPackCard — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def card():
    pack = _make_pack("pre-commit-lint", ["lint-check.md", "format-check.md"])
    c = HookPackCard(pack)
    yield c
    c.close()


class TestHookPackCardConstruction:
    def test_creates_without_error(self, card):
        assert card is not None

    def test_pack_id(self, card):
        assert card.pack_id == "pre-commit-lint"

    def test_initially_enabled(self, card):
        assert card.is_enabled is True

    def test_object_name(self, card):
        assert card.objectName() == "hook-card"

    def test_file_count(self, card):
        assert card.file_count == 2

    def test_initial_mode_is_enforcing(self, card):
        assert card.mode == HookMode.ENFORCING


# ---------------------------------------------------------------------------
# HookPackCard — enable/disable
# ---------------------------------------------------------------------------

class TestHookPackCardToggle:
    def test_disable_via_property(self, card):
        card.is_enabled = False
        assert card.is_enabled is False

    def test_enable_via_property(self, card):
        card.is_enabled = False
        card.is_enabled = True
        assert card.is_enabled is True

    def test_toggled_signal_emitted_on_disable(self, card):
        received = []
        card.toggled.connect(lambda pid, checked: received.append((pid, checked)))
        card.is_enabled = False
        assert len(received) == 1
        assert received[0] == ("pre-commit-lint", False)

    def test_toggled_signal_emitted_on_enable(self, card):
        card.is_enabled = False
        received = []
        card.toggled.connect(lambda pid, checked: received.append((pid, checked)))
        card.is_enabled = True
        assert len(received) == 1
        assert received[0] == ("pre-commit-lint", True)


# ---------------------------------------------------------------------------
# HookPackCard — mode
# ---------------------------------------------------------------------------

class TestHookPackCardMode:
    def test_set_mode_permissive(self, card):
        card.mode = HookMode.PERMISSIVE
        assert card.mode == HookMode.PERMISSIVE

    def test_set_mode_disabled(self, card):
        card.mode = HookMode.DISABLED
        assert card.mode == HookMode.DISABLED

    def test_set_mode_enforcing(self, card):
        card.mode = HookMode.DISABLED
        card.mode = HookMode.ENFORCING
        assert card.mode == HookMode.ENFORCING

    def test_mode_change_emits_toggled_signal(self, card):
        received = []
        card.toggled.connect(lambda pid, checked: received.append((pid, checked)))
        card.mode = HookMode.PERMISSIVE
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# HookPackCard — to_hook_pack_selection
# ---------------------------------------------------------------------------

class TestHookPackCardToSelection:
    def test_default_selection_values(self, card):
        sel = card.to_hook_pack_selection()
        assert isinstance(sel, HookPackSelection)
        assert sel.id == "pre-commit-lint"
        assert sel.enabled is True
        assert sel.mode == HookMode.ENFORCING

    def test_disabled_selection(self, card):
        card.is_enabled = False
        card.mode = HookMode.PERMISSIVE
        sel = card.to_hook_pack_selection()
        assert sel.enabled is False
        assert sel.mode == HookMode.PERMISSIVE


# ---------------------------------------------------------------------------
# HookPackCard — load_from_selection
# ---------------------------------------------------------------------------

class TestHookPackCardLoadFromSelection:
    def test_load_restores_enabled_state(self, card):
        sel = HookPackSelection(id="pre-commit-lint", enabled=False, mode=HookMode.ENFORCING)
        card.load_from_selection(sel)
        assert card.is_enabled is False

    def test_load_restores_mode(self, card):
        sel = HookPackSelection(id="pre-commit-lint", enabled=True, mode=HookMode.PERMISSIVE)
        card.load_from_selection(sel)
        assert card.mode == HookMode.PERMISSIVE

    def test_roundtrip_selection(self, card):
        original = HookPackSelection(
            id="pre-commit-lint", enabled=False, mode=HookMode.DISABLED,
        )
        card.load_from_selection(original)
        result = card.to_hook_pack_selection()
        assert result.id == original.id
        assert result.enabled == original.enabled
        assert result.mode == original.mode


# ---------------------------------------------------------------------------
# HookPackCard — unknown pack fallback
# ---------------------------------------------------------------------------

class TestHookPackCardUnknownPack:
    def test_unknown_pack_uses_titlecased_id(self):
        pack = _make_pack("custom-hook")
        card = HookPackCard(pack)
        assert card.pack_id == "custom-hook"
        card.close()


# ---------------------------------------------------------------------------
# SafetyPolicySection — construction and toggles
# ---------------------------------------------------------------------------

@pytest.fixture()
def section():
    sec = SafetyPolicySection("Test Section")
    sec.add_toggle("flag_a", "Flag A", default=True)
    sec.add_toggle("flag_b", "Flag B", default=False)
    yield sec
    sec.close()


class TestSafetyPolicySectionConstruction:
    def test_creates_without_error(self, section):
        assert section is not None

    def test_title(self, section):
        assert section.title == "Test Section"

    def test_object_name(self, section):
        assert section.objectName() == "safety-section"

    def test_toggle_count(self, section):
        assert len(section.toggles) == 2


class TestSafetyPolicySectionToggles:
    def test_get_default_true(self, section):
        assert section.get_toggle("flag_a") is True

    def test_get_default_false(self, section):
        assert section.get_toggle("flag_b") is False

    def test_set_toggle(self, section):
        section.set_toggle("flag_a", False)
        assert section.get_toggle("flag_a") is False

    def test_get_unknown_key_returns_false(self, section):
        assert section.get_toggle("nonexistent") is False

    def test_set_unknown_key_no_error(self, section):
        section.set_toggle("nonexistent", True)  # should be no-op

    def test_changed_signal_emitted(self, section):
        received = []
        section.changed.connect(lambda: received.append(True))
        section.set_toggle("flag_a", False)
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# HookSafetyPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = HookSafetyPage()
    yield p
    p.close()


@pytest.fixture()
def loaded_page():
    lib = _make_full_library()
    p = HookSafetyPage(library_index=lib)
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_no_cards_initially(self, page):
        assert len(page.hook_cards) == 0

    def test_always_valid(self, page):
        assert page.is_valid() is True

    def test_default_posture_is_baseline(self, page):
        assert page.posture == Posture.BASELINE

    def test_has_six_safety_sections(self, page):
        assert len(page.safety_sections) == 6

    def test_safety_section_keys(self, page):
        expected = {"git", "shell", "filesystem", "network", "secrets", "destructive_ops"}
        assert set(page.safety_sections.keys()) == expected


# ---------------------------------------------------------------------------
# HookSafetyPage — load_hook_packs
# ---------------------------------------------------------------------------

class TestLoadHookPacks:
    def test_loads_all_packs(self, loaded_page):
        assert len(loaded_page.hook_cards) == 4

    def test_all_pack_ids_present(self, loaded_page):
        expected = {"pre-commit-lint", "post-task-qa", "security-scan", "compliance-gate"}
        assert set(loaded_page.hook_cards.keys()) == expected

    def test_loads_via_constructor(self):
        lib = _make_library("pre-commit-lint", "security-scan")
        page = HookSafetyPage(library_index=lib)
        assert len(page.hook_cards) == 2
        page.close()

    def test_load_replaces_previous_packs(self, loaded_page):
        new_lib = _make_library("pre-commit-lint")
        loaded_page.load_hook_packs(new_lib)
        assert len(loaded_page.hook_cards) == 1
        assert "pre-commit-lint" in loaded_page.hook_cards

    def test_empty_library_shows_no_cards(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_hook_packs(lib)
        assert len(page.hook_cards) == 0


# ---------------------------------------------------------------------------
# HookSafetyPage — posture
# ---------------------------------------------------------------------------

class TestPosture:
    def test_set_posture_hardened(self, page):
        page.posture = Posture.HARDENED
        assert page.posture == Posture.HARDENED

    def test_set_posture_regulated(self, page):
        page.posture = Posture.REGULATED
        assert page.posture == Posture.REGULATED

    def test_posture_change_emits_signal(self, page):
        received = []
        page.selection_changed.connect(lambda: received.append(True))
        page.posture = Posture.HARDENED
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# HookSafetyPage — get_hooks_config
# ---------------------------------------------------------------------------

class TestGetHooksConfig:
    def test_returns_hooks_config(self, loaded_page):
        config = loaded_page.get_hooks_config()
        assert isinstance(config, HooksConfig)

    def test_default_posture(self, loaded_page):
        config = loaded_page.get_hooks_config()
        assert config.posture == Posture.BASELINE

    def test_pack_count_matches_cards(self, loaded_page):
        config = loaded_page.get_hooks_config()
        assert len(config.packs) == 4

    def test_all_packs_enabled_by_default(self, loaded_page):
        config = loaded_page.get_hooks_config()
        assert all(p.enabled for p in config.packs)

    def test_all_packs_enforcing_by_default(self, loaded_page):
        config = loaded_page.get_hooks_config()
        assert all(p.mode == HookMode.ENFORCING for p in config.packs)

    def test_empty_page_has_empty_packs(self, page):
        config = page.get_hooks_config()
        assert len(config.packs) == 0

    def test_disabled_pack_reflected(self, loaded_page):
        loaded_page.hook_cards["security-scan"].is_enabled = False
        config = loaded_page.get_hooks_config()
        pack = next(p for p in config.packs if p.id == "security-scan")
        assert pack.enabled is False

    def test_mode_change_reflected(self, loaded_page):
        loaded_page.hook_cards["pre-commit-lint"].mode = HookMode.PERMISSIVE
        config = loaded_page.get_hooks_config()
        pack = next(p for p in config.packs if p.id == "pre-commit-lint")
        assert pack.mode == HookMode.PERMISSIVE


# ---------------------------------------------------------------------------
# HookSafetyPage — set_hooks_config
# ---------------------------------------------------------------------------

class TestSetHooksConfig:
    def test_restores_posture(self, loaded_page):
        config = HooksConfig(
            posture=Posture.REGULATED,
            packs=[HookPackSelection(id="pre-commit-lint", enabled=True, mode=HookMode.ENFORCING)],
        )
        loaded_page.set_hooks_config(config)
        assert loaded_page.posture == Posture.REGULATED

    def test_restores_pack_enabled_state(self, loaded_page):
        config = HooksConfig(
            posture=Posture.BASELINE,
            packs=[
                HookPackSelection(id="pre-commit-lint", enabled=False, mode=HookMode.ENFORCING),
                HookPackSelection(id="security-scan", enabled=True, mode=HookMode.PERMISSIVE),
            ],
        )
        loaded_page.set_hooks_config(config)
        assert loaded_page.hook_cards["pre-commit-lint"].is_enabled is False
        assert loaded_page.hook_cards["security-scan"].mode == HookMode.PERMISSIVE

    def test_missing_packs_reset_to_defaults(self, loaded_page):
        config = HooksConfig(
            posture=Posture.BASELINE,
            packs=[HookPackSelection(id="pre-commit-lint", enabled=True, mode=HookMode.ENFORCING)],
        )
        loaded_page.hook_cards["security-scan"].is_enabled = False
        loaded_page.set_hooks_config(config)
        # security-scan not in config packs → reset to defaults
        assert loaded_page.hook_cards["security-scan"].is_enabled is True
        assert loaded_page.hook_cards["security-scan"].mode == HookMode.ENFORCING

    def test_roundtrip_get_set_get(self, loaded_page):
        # Modify some state
        loaded_page.posture = Posture.HARDENED
        loaded_page.hook_cards["post-task-qa"].is_enabled = False
        loaded_page.hook_cards["pre-commit-lint"].mode = HookMode.DISABLED

        original = loaded_page.get_hooks_config()
        loaded_page.set_hooks_config(original)
        restored = loaded_page.get_hooks_config()

        assert restored.posture == original.posture
        for orig_pack in original.packs:
            rest_pack = next(p for p in restored.packs if p.id == orig_pack.id)
            assert rest_pack.enabled == orig_pack.enabled
            assert rest_pack.mode == orig_pack.mode


# ---------------------------------------------------------------------------
# HookSafetyPage — safety presets
# ---------------------------------------------------------------------------

class TestSafetyPresets:
    def test_permissive_preset(self, page):
        page._apply_permissive()
        config = page.get_safety_config()
        assert config.git.allow_force_push is True
        assert config.git.allow_branch_delete is True
        assert config.filesystem.allow_delete is True
        assert config.secrets.scan_for_secrets is False
        assert config.destructive_ops.allow_destructive is True
        assert config.destructive_ops.require_confirmation is False

    def test_baseline_preset(self, page):
        # First set to permissive, then baseline
        page._apply_permissive()
        page._apply_baseline()
        config = page.get_safety_config()
        assert config.git.allow_push is True
        assert config.git.allow_force_push is False
        assert config.filesystem.allow_delete is False
        assert config.secrets.scan_for_secrets is True
        assert config.destructive_ops.allow_destructive is False

    def test_hardened_preset(self, page):
        page._apply_hardened()
        config = page.get_safety_config()
        assert config.git.allow_force_push is False
        assert config.git.allow_branch_delete is False
        assert config.filesystem.allow_delete is False
        assert config.secrets.scan_for_secrets is True
        assert config.secrets.block_on_secret is True
        assert config.destructive_ops.allow_destructive is False
        assert config.destructive_ops.require_confirmation is True


# ---------------------------------------------------------------------------
# HookSafetyPage — get_safety_config
# ---------------------------------------------------------------------------

class TestGetSafetyConfig:
    def test_returns_safety_config(self, page):
        config = page.get_safety_config()
        assert isinstance(config, SafetyConfig)

    def test_default_git_policy(self, page):
        config = page.get_safety_config()
        assert config.git.allow_push is True
        assert config.git.allow_force_push is False
        assert config.git.allow_branch_delete is False

    def test_default_shell_policy(self, page):
        config = page.get_safety_config()
        assert config.shell.allow_shell is True

    def test_default_filesystem_policy(self, page):
        config = page.get_safety_config()
        assert config.filesystem.allow_write is True
        assert config.filesystem.allow_delete is False

    def test_default_network_policy(self, page):
        config = page.get_safety_config()
        assert config.network.allow_network is True

    def test_default_secrets_policy(self, page):
        config = page.get_safety_config()
        assert config.secrets.scan_for_secrets is True
        assert config.secrets.block_on_secret is True

    def test_default_destructive_ops_policy(self, page):
        config = page.get_safety_config()
        assert config.destructive_ops.allow_destructive is False
        assert config.destructive_ops.require_confirmation is True

    def test_toggle_changes_reflected(self, page):
        page._safety_sections["git"].set_toggle("allow_force_push", True)
        config = page.get_safety_config()
        assert config.git.allow_force_push is True


# ---------------------------------------------------------------------------
# HookSafetyPage — set_safety_config
# ---------------------------------------------------------------------------

class TestSetSafetyConfig:
    def test_restores_git_policy(self, page):
        config = SafetyConfig(
            git=GitPolicy(allow_push=False, allow_force_push=True, allow_branch_delete=True),
        )
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.git.allow_push is False
        assert result.git.allow_force_push is True
        assert result.git.allow_branch_delete is True

    def test_restores_shell_policy(self, page):
        config = SafetyConfig(shell=ShellPolicy(allow_shell=False))
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.shell.allow_shell is False

    def test_restores_filesystem_policy(self, page):
        config = SafetyConfig(
            filesystem=FileSystemPolicy(allow_write=False, allow_delete=True),
        )
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.filesystem.allow_write is False
        assert result.filesystem.allow_delete is True

    def test_restores_network_policy(self, page):
        config = SafetyConfig(network=NetworkPolicy(allow_network=False))
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.network.allow_network is False

    def test_restores_secrets_policy(self, page):
        config = SafetyConfig(
            secrets=SecretPolicy(scan_for_secrets=False, block_on_secret=False),
        )
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.secrets.scan_for_secrets is False
        assert result.secrets.block_on_secret is False

    def test_restores_destructive_ops_policy(self, page):
        config = SafetyConfig(
            destructive_ops=DestructiveOpsPolicy(
                allow_destructive=True, require_confirmation=False,
            ),
        )
        page.set_safety_config(config)
        result = page.get_safety_config()
        assert result.destructive_ops.allow_destructive is True
        assert result.destructive_ops.require_confirmation is False

    def test_roundtrip_get_set_get(self, page):
        page._apply_hardened()
        original = page.get_safety_config()

        page._apply_permissive()  # change to something different
        page.set_safety_config(original)
        restored = page.get_safety_config()

        assert restored.git.allow_push == original.git.allow_push
        assert restored.git.allow_force_push == original.git.allow_force_push
        assert restored.shell.allow_shell == original.shell.allow_shell
        assert restored.filesystem.allow_delete == original.filesystem.allow_delete
        assert restored.secrets.scan_for_secrets == original.secrets.scan_for_secrets
        assert restored.destructive_ops.allow_destructive == (
            original.destructive_ops.allow_destructive
        )


# ---------------------------------------------------------------------------
# HookSafetyPage — selection_changed signal
# ---------------------------------------------------------------------------

class TestSelectionChangedSignal:
    def test_emitted_on_card_toggle(self, loaded_page):
        received = []
        loaded_page.selection_changed.connect(lambda: received.append(True))
        loaded_page.hook_cards["pre-commit-lint"].is_enabled = False
        assert len(received) >= 1

    def test_emitted_on_posture_change(self, page):
        received = []
        page.selection_changed.connect(lambda: received.append(True))
        page.posture = Posture.HARDENED
        assert len(received) >= 1

    def test_emitted_on_safety_toggle(self, page):
        received = []
        page.selection_changed.connect(lambda: received.append(True))
        page._safety_sections["git"].set_toggle("allow_force_push", True)
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# HookSafetyPage — is_valid always True
# ---------------------------------------------------------------------------

class TestIsValid:
    def test_valid_empty(self, page):
        assert page.is_valid() is True

    def test_valid_with_packs(self, loaded_page):
        assert loaded_page.is_valid() is True

    def test_valid_all_disabled(self, loaded_page):
        for card in loaded_page.hook_cards.values():
            card.is_enabled = False
        assert loaded_page.is_valid() is True


# ---------------------------------------------------------------------------
# HookSafetyPage — file count badge
# ---------------------------------------------------------------------------

class TestFileBadge:
    def test_pack_with_files_shows_count(self):
        lib = _make_library_with_files()
        page = HookSafetyPage(library_index=lib)
        assert page.hook_cards["pre-commit-lint"].file_count == 2
        assert page.hook_cards["security-scan"].file_count == 1
        assert page.hook_cards["compliance-gate"].file_count == 0
        page.close()


# ---------------------------------------------------------------------------
# HOOK_PACK_DESCRIPTIONS completeness
# ---------------------------------------------------------------------------

class TestHookPackDescriptions:
    def test_known_packs_have_descriptions(self):
        expected = {"pre-commit-lint", "post-task-qa", "security-scan",
                    "compliance-gate", "hook-policy"}
        assert set(HOOK_PACK_DESCRIPTIONS.keys()) == expected

    def test_descriptions_are_tuples(self):
        for pid, desc in HOOK_PACK_DESCRIPTIONS.items():
            assert isinstance(desc, tuple), f"{pid} description is not a tuple"
            assert len(desc) == 2, f"{pid} description tuple has {len(desc)} elements"

    def test_descriptions_have_nonempty_values(self):
        for pid, (name, desc) in HOOK_PACK_DESCRIPTIONS.items():
            assert len(name) > 0, f"{pid} has empty display name"
            assert len(desc) > 0, f"{pid} has empty description"


# ---------------------------------------------------------------------------
# HookSafetyPage — empty-state messaging
# ---------------------------------------------------------------------------

class TestHookEmptyState:
    def test_empty_label_visible_when_no_library(self, page):
        assert page._hook_empty_label.isHidden() is False

    def test_empty_label_hidden_after_loading_packs(self):
        lib = _make_full_library()
        p = HookSafetyPage(library_index=lib)
        assert p._hook_empty_label.isHidden() is True
        p.close()

    def test_empty_label_visible_after_loading_empty_library(self, page):
        lib = LibraryIndex(library_root="/fake")
        page.load_hook_packs(lib)
        assert page._hook_empty_label.isHidden() is False

    def test_empty_label_hidden_after_reloading_with_packs(self, page):
        lib_empty = LibraryIndex(library_root="/fake")
        page.load_hook_packs(lib_empty)
        assert page._hook_empty_label.isHidden() is False
        lib = _make_library("pre-commit-lint", "security-scan")
        page.load_hook_packs(lib)
        assert page._hook_empty_label.isHidden() is True
