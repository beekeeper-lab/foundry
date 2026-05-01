"""Tests for foundry_app.ui.screens.builder.wizard_pages.hook_safety_page."""

import pytest

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

pytestmark = pytest.mark.usefixtures("qapp")


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

    def test_click_on_card_toggles_checkbox(self, card):
        from PySide6.QtCore import QPointF, Qt
        from PySide6.QtGui import QMouseEvent

        assert card.is_enabled is True  # hook packs start enabled
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(200, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        card.mousePressEvent(event)
        assert card.is_enabled is False
        card.mousePressEvent(event)
        assert card.is_enabled is True


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
        expected = {
            "pre-commit-lint", "post-task-qa", "security-scan",
            "compliance-gate", "hook-policy",
            "git-commit-branch", "git-push-feature", "git-generate-pr",
            "git-merge-to-test", "git-merge-to-prod",
            "az-read-only", "az-limited-ops",
        }
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


# ---------------------------------------------------------------------------
# BEAN-286 — Real-time hook-pack conflict indicator + default-load conflict-free
#
# When a user enables two packs that declare a mutual conflict, the page
# should surface that fact at the page itself — not defer it to generation
# time. Defaults must also load conflict-free out of the box.
# ---------------------------------------------------------------------------


def _make_pack_with_conflicts(pid: str, conflicts_with: list[str]) -> HookPackInfo:
    return HookPackInfo(
        id=pid,
        path=f"/fake/hooks/{pid}",
        files=[],
        conflicts_with=conflicts_with,
    )


def _make_conflict_library() -> LibraryIndex:
    """Library with one declared conflict pair: pack-a ↔ pack-b."""
    return LibraryIndex(
        library_root="/fake/library",
        hook_packs=[
            _make_pack_with_conflicts("pack-a", ["pack-b"]),
            _make_pack_with_conflicts("pack-b", ["pack-a"]),
            _make_pack("pack-c"),
        ],
    )


class TestConflictIndicator:
    """Hook Safety page surfaces enabled mutually-exclusive pairs in real time."""

    def test_indicator_hidden_when_no_library(self, page):
        assert page._conflict_label is not None
        assert page._conflict_label.isHidden() is True

    def test_indicator_green_when_no_conflicts(self):
        # pack-a's conflict partner (pack-b) is unchecked by the default-
        # conflict resolver, so on load the indicator is green.
        p = HookSafetyPage(library_index=_make_conflict_library())
        try:
            label = p._conflict_label
            assert label.isHidden() is False
            text = label.text()
            assert "\U0001f7e2" in text
            assert "none" in text.lower()
        finally:
            p.close()

    def test_indicator_red_names_pair_when_both_enabled(self):
        p = HookSafetyPage(library_index=_make_conflict_library())
        try:
            # Manually re-enable the partner that the default-resolver
            # auto-disabled — simulates a user clicking it on.
            p.hook_cards["pack-b"].is_enabled = True
            label = p._conflict_label
            assert label.isHidden() is False
            text = label.text()
            assert "\U0001f534" in text
            assert "pack-a" in text
            assert "pack-b" in text
            assert "mutually exclusive" in text.lower()
        finally:
            p.close()

    def test_indicator_transitions_red_to_green_on_disable(self):
        p = HookSafetyPage(library_index=_make_conflict_library())
        try:
            p.hook_cards["pack-b"].is_enabled = True
            assert "\U0001f534" in p._conflict_label.text()
            # Toggling one pack of the pair off clears the conflict.
            p.hook_cards["pack-b"].is_enabled = False
            text = p._conflict_label.text()
            assert "\U0001f7e2" in text
            assert "\U0001f534" not in text
        finally:
            p.close()

    def test_indicator_handles_one_sided_declaration(self):
        # Only pack-a declares the conflict; pack-b has no list. The
        # detector mirrors validator._check_hook_conflicts, which treats
        # one-sided declarations as binding.
        lib = LibraryIndex(
            library_root="/fake",
            hook_packs=[
                _make_pack_with_conflicts("pack-a", ["pack-b"]),
                _make_pack("pack-b"),
            ],
        )
        p = HookSafetyPage(library_index=lib)
        try:
            p.hook_cards["pack-b"].is_enabled = True
            text = p._conflict_label.text()
            assert "\U0001f534" in text
            assert "pack-a" in text and "pack-b" in text
        finally:
            p.close()


class TestDefaultLoadConflictFree:
    """Defaults must load conflict-free — fixture libraries and the real one."""

    def test_default_load_drops_partner_of_declared_conflict_pair(self):
        p = HookSafetyPage(library_index=_make_conflict_library())
        try:
            # First-wins: pack-a stays on, pack-b is dropped, pack-c stays.
            assert p.hook_cards["pack-a"].is_enabled is True
            assert p.hook_cards["pack-b"].is_enabled is False
            assert p.hook_cards["pack-c"].is_enabled is True
        finally:
            p.close()

    def test_default_load_real_library_is_conflict_free(self):
        """Regression: BEAN-286.

        Out of the box, with the real ``ai-team-library/`` indexed, no two
        enabled hook packs may declare a mutual conflict. This test fails
        before BEAN-286 lands because the page set every pack to enabled
        regardless of conflict declarations.
        """
        from pathlib import Path

        from foundry_app.services.library_indexer import build_library_index
        from foundry_app.services.validator import _check_hook_conflicts

        repo_root = Path(__file__).resolve().parent.parent
        library_root = repo_root / "ai-team-library"
        if not library_root.exists():
            pytest.skip("ai-team-library/ not available in this checkout")

        lib = build_library_index(library_root)

        page = HookSafetyPage(library_index=lib)
        try:
            cfg = page.get_hooks_config()
            from foundry_app.core.models import (
                CompositionSpec,
                ProjectIdentity,
                TeamConfig,
            )

            composition = CompositionSpec(
                project=ProjectIdentity(
                    name="test", slug="test", description="", purpose="t",
                ),
                team=TeamConfig(personas=[]),
                hooks=cfg,
            )
            messages: list = []
            _check_hook_conflicts(composition, lib, messages)
            assert messages == [], (
                f"Default load is not conflict-free: {[m.message for m in messages]}"
            )
        finally:
            page.close()


# ---------------------------------------------------------------------------
# BEAN-293 — Posture-incompatible packs must not ship enabled-by-default
#
# A fresh wizard session at the default ``baseline`` posture must not include
# any pack whose ``Posture Compatibility`` table marks baseline as
# ``Included: No`` (e.g. ``compliance-gate``). Switching posture at runtime
# must re-apply the same filter so the user can't be left with a stale
# enabled pack that fails generation.
# ---------------------------------------------------------------------------


def _make_pack_with_posture(
    pid: str,
    posture_compatibility: dict[str, dict[str, str]],
) -> HookPackInfo:
    return HookPackInfo(
        id=pid,
        path=f"/fake/hooks/{pid}",
        files=[],
        posture_compatibility=posture_compatibility,
    )


def _library_with_compliance_gate_posture() -> LibraryIndex:
    """Library where compliance-gate excludes baseline + hardened."""
    return LibraryIndex(
        library_root="/fake/library",
        hook_packs=[
            _make_pack_with_posture(
                "pre-commit-lint",
                {
                    "baseline": {"included": "Yes", "default_mode": "enforcing"},
                    "hardened": {"included": "Yes", "default_mode": "enforcing"},
                    "regulated": {"included": "Yes", "default_mode": "enforcing"},
                },
            ),
            _make_pack_with_posture(
                "compliance-gate",
                {
                    "baseline": {"included": "No", "default_mode": "—"},
                    "hardened": {"included": "No", "default_mode": "—"},
                    "regulated": {"included": "Yes", "default_mode": "enforcing"},
                },
            ),
        ],
    )


class TestPostureIncompatibleDefaultsFilter:
    """BEAN-293: Posture-incompatible packs are unchecked at default load."""

    def test_compliance_gate_unchecked_at_default_baseline(self):
        """At default baseline, compliance-gate (baseline: No) must be off."""
        lib = _library_with_compliance_gate_posture()
        p = HookSafetyPage(library_index=lib)
        try:
            assert p.posture == Posture.BASELINE
            assert p.hook_cards["compliance-gate"].is_enabled is False
            # Compatible pack remains enabled.
            assert p.hook_cards["pre-commit-lint"].is_enabled is True
        finally:
            p.close()

    def test_pack_without_posture_metadata_not_filtered(self):
        """Older packs (no posture_compatibility) must not crash or change."""
        # Mirrors validator's skip behavior for backward compatibility.
        lib = _make_library("pre-commit-lint", "post-task-qa")
        p = HookSafetyPage(library_index=lib)
        try:
            # Both packs ship enabled-by-default and the filter must not
            # touch them when posture_compatibility is empty.
            assert p.hook_cards["pre-commit-lint"].is_enabled is True
            assert p.hook_cards["post-task-qa"].is_enabled is True
        finally:
            p.close()

    def test_posture_change_with_empty_metadata_does_not_crash(self):
        """BEAN-293 (Tech-QA regression): older-library packs survive
        the posture-change path.

        Developer's ``test_pack_without_posture_metadata_not_filtered``
        covers the ``load_hook_packs`` entry to ``_apply_posture_filter``.
        The ``_on_posture_changed`` entry is the second call site, and
        the AC item asks the page filter to "not crash" on either path
        when ``posture_compatibility`` is empty (mirroring the validator's
        documented backward-compatibility skip). This test pins the
        posture-change path so a future refactor that, say, replaces
        ``not pack.posture_compatibility`` with
        ``pack.posture_compatibility[key]`` is caught here, not in
        production.
        """
        # Library where every pack has empty posture_compatibility (older
        # library shape). _make_library leaves posture_compatibility={}.
        lib = _make_library("pre-commit-lint", "post-task-qa")
        p = HookSafetyPage(library_index=lib)
        try:
            # Posture change (the _on_posture_changed → _apply_posture_filter
            # path) must not crash and must leave card states unchanged.
            p.posture = Posture.HARDENED
            assert p.hook_cards["pre-commit-lint"].is_enabled is True
            assert p.hook_cards["post-task-qa"].is_enabled is True

            p.posture = Posture.REGULATED
            assert p.hook_cards["pre-commit-lint"].is_enabled is True
            assert p.hook_cards["post-task-qa"].is_enabled is True

            p.posture = Posture.BASELINE
            assert p.hook_cards["pre-commit-lint"].is_enabled is True
            assert p.hook_cards["post-task-qa"].is_enabled is True
        finally:
            p.close()

    def test_regulated_to_baseline_unchecks_now_incompatible_pack(self):
        """User switches regulated → baseline; compliance-gate gets unchecked."""
        lib = _library_with_compliance_gate_posture()
        p = HookSafetyPage(library_index=lib)
        try:
            # Bootstrap into a state where compliance-gate is enabled at
            # regulated. We have to construct this manually because the
            # filter purges it at any load that lands at baseline.
            p.posture = Posture.REGULATED
            p.hook_cards["compliance-gate"].is_enabled = True
            assert p.hook_cards["compliance-gate"].is_enabled is True

            # Now switch to baseline — the filter must purge it.
            p.posture = Posture.BASELINE
            assert p.hook_cards["compliance-gate"].is_enabled is False
        finally:
            p.close()

    def test_baseline_to_regulated_does_not_restore_filtered_pack(self):
        """Documented behavior: posture switching purges, never restores.

        Switching `baseline → regulated` after the default-load filter
        unchecked compliance-gate must NOT re-enable it. The user can
        consciously opt in by checking the card. This is the simpler
        behavior — implementing "remember default-on" would require
        per-card state tracking that the bean doesn't warrant.
        """
        lib = _library_with_compliance_gate_posture()
        p = HookSafetyPage(library_index=lib)
        try:
            # At default baseline, compliance-gate was unchecked by the filter.
            assert p.hook_cards["compliance-gate"].is_enabled is False
            # Switch to regulated — pack is now compatible, but stays off.
            p.posture = Posture.REGULATED
            assert p.hook_cards["compliance-gate"].is_enabled is False
        finally:
            p.close()

    def test_set_hooks_config_does_not_apply_posture_filter(self):
        """Saved-state restore is the source of truth; the filter must not run.

        If a user persisted compliance-gate enabled at regulated, then loaded
        the saved composition while the page constructor is at baseline,
        ``set_hooks_config`` must restore the saved selection verbatim — the
        validator will surface the mismatch through its normal error path
        (the user explicitly chose this combination at save time, so the
        restore is faithful, not silently mutated).
        """
        lib = _library_with_compliance_gate_posture()
        p = HookSafetyPage(library_index=lib)
        try:
            # Default load at baseline filtered compliance-gate off.
            assert p.hook_cards["compliance-gate"].is_enabled is False

            # User loads a saved composition that enabled compliance-gate at
            # regulated. set_hooks_config must NOT re-apply the filter.
            saved = HooksConfig(
                posture=Posture.REGULATED,
                packs=[
                    HookPackSelection(
                        id="pre-commit-lint",
                        enabled=True,
                        mode=HookMode.ENFORCING,
                    ),
                    HookPackSelection(
                        id="compliance-gate",
                        enabled=True,
                        mode=HookMode.ENFORCING,
                    ),
                ],
            )
            p.set_hooks_config(saved)
            assert p.posture == Posture.REGULATED
            assert p.hook_cards["compliance-gate"].is_enabled is True
        finally:
            p.close()

    def test_default_load_passes_validator_at_baseline(self):
        """Wizard-default regression: no posture-incompatibility errors."""
        from foundry_app.core.models import (
            CompositionSpec,
            ProjectIdentity,
            TeamConfig,
        )
        from foundry_app.services.validator import (
            _check_hook_posture_compatibility,
        )

        lib = _library_with_compliance_gate_posture()
        p = HookSafetyPage(library_index=lib)
        try:
            cfg = p.get_hooks_config()
            spec = CompositionSpec(
                project=ProjectIdentity(
                    name="test", slug="test", description="", purpose="t",
                ),
                team=TeamConfig(personas=[]),
                hooks=cfg,
            )
            messages: list = []
            _check_hook_posture_compatibility(spec, lib, messages)
            assert messages == [], (
                f"Default load tripped posture validator: "
                f"{[m.message for m in messages]}"
            )
        finally:
            p.close()


class TestPostureIncompatibleRealLibrary:
    """BEAN-293: each posture's default load must validator-clean against the real library."""

    @pytest.mark.parametrize(
        "posture",
        [Posture.BASELINE, Posture.HARDENED, Posture.REGULATED],
    )
    def test_default_load_real_library_no_posture_errors(self, posture):
        """For each posture, defaults at that posture pass validator."""
        from pathlib import Path

        from foundry_app.core.models import (
            CompositionSpec,
            ProjectIdentity,
            TeamConfig,
        )
        from foundry_app.services.library_indexer import build_library_index
        from foundry_app.services.validator import (
            _check_hook_posture_compatibility,
        )

        repo_root = Path(__file__).resolve().parent.parent
        library_root = repo_root / "ai-team-library"
        if not library_root.exists():
            pytest.skip("ai-team-library/ not available in this checkout")

        lib = build_library_index(library_root)

        page = HookSafetyPage(library_index=lib)
        try:
            page.posture = posture
            cfg = page.get_hooks_config()
            spec = CompositionSpec(
                project=ProjectIdentity(
                    name="test", slug="test", description="", purpose="t",
                ),
                team=TeamConfig(personas=[]),
                hooks=cfg,
            )
            messages: list = []
            _check_hook_posture_compatibility(spec, lib, messages)
            assert messages == [], (
                f"Default load at posture={posture.value} tripped "
                f"posture validator: {[m.message for m in messages]}"
            )
        finally:
            page.close()

    def test_default_load_real_library_baseline_unchecks_compliance_gate(self):
        """At baseline against real library, compliance-gate must be off."""
        from pathlib import Path

        from foundry_app.services.library_indexer import build_library_index

        repo_root = Path(__file__).resolve().parent.parent
        library_root = repo_root / "ai-team-library"
        if not library_root.exists():
            pytest.skip("ai-team-library/ not available in this checkout")

        lib = build_library_index(library_root)
        page = HookSafetyPage(library_index=lib)
        try:
            assert page.posture == Posture.BASELINE
            card = page.hook_cards.get("compliance-gate")
            assert card is not None, (
                "Test library should ship a compliance-gate pack"
            )
            assert card.is_enabled is False, (
                "compliance-gate should default-off at baseline"
            )
        finally:
            page.close()

    def test_user_explicit_check_at_baseline_trips_validator(self):
        """BEAN-293 (Tech-QA regression): user opts in to compliance-gate
        at baseline → validator surface still fires.

        Headless substitution for the bean's last (manual) AC item:
        "manually enable ``compliance-gate`` at the default ``baseline``
        posture, click Generate → still fails with the friendly BEAN-290
        message". Loads the **real** library through the **real** page
        (no mocked HookPackInfo — see task Notes), confirms the default
        filter unchecks compliance-gate, then re-enables it
        programmatically and asserts ``run_pre_generation_validation``
        produces a ``hook-pack-posture-incompatible`` ERROR. Proves the
        defaults filter and the validator surface are independent: the
        former runs at the page layer, the latter at composition time.
        """
        from pathlib import Path

        from foundry_app.core.models import (
            CompositionSpec,
            PersonaSelection,
            ProjectIdentity,
            TeamConfig,
        )
        from foundry_app.services.library_indexer import build_library_index
        from foundry_app.services.validator import (
            run_pre_generation_validation,
        )

        repo_root = Path(__file__).resolve().parent.parent
        library_root = repo_root / "ai-team-library"
        if not library_root.exists():
            pytest.skip("ai-team-library/ not available in this checkout")

        lib = build_library_index(library_root)
        page = HookSafetyPage(library_index=lib)
        try:
            # Sanity: defaults filter unchecked compliance-gate at baseline.
            assert page.posture == Posture.BASELINE
            assert page.hook_cards["compliance-gate"].is_enabled is False

            # User explicitly opts in by checking the card.
            page.hook_cards["compliance-gate"].is_enabled = True
            assert page.hook_cards["compliance-gate"].is_enabled is True

            # Build the composition the wizard would assemble.
            cfg = page.get_hooks_config()
            spec = CompositionSpec(
                project=ProjectIdentity(
                    name="test", slug="test", description="", purpose="t",
                ),
                team=TeamConfig(
                    personas=[PersonaSelection(id="developer")],
                ),
                hooks=cfg,
            )

            # Validator surface must surface the mismatch as an ERROR.
            result = run_pre_generation_validation(spec, lib)
            posture_errors = [
                m for m in result.errors
                if m.code == "hook-pack-posture-incompatible"
            ]
            assert len(posture_errors) >= 1, (
                "User-explicit compliance-gate at baseline should ERROR "
                f"via hook-pack-posture-incompatible. Got errors: "
                f"{[(m.code, m.message) for m in result.errors]}"
            )
            # Friendly BEAN-290 message names the pack and posture.
            msg = posture_errors[0].message
            assert "compliance-gate" in msg
            assert "baseline" in msg
        finally:
            page.close()
