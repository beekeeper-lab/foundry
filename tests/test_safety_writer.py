"""Tests for foundry_app.services.safety_writer — safety config generation."""

import json
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    HooksConfig,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    SafetyConfig,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.safety_writer import write_safety


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        stacks=[StackSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _read_settings(output: Path) -> dict:
    """Read and parse the generated settings.json."""
    return json.loads(
        (output / ".claude" / "settings.json").read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# Basic generation
# ---------------------------------------------------------------------------


class TestBasicGeneration:

    def test_creates_settings_file(self, tmp_path: Path):
        result = write_safety(_make_spec(), tmp_path)
        assert (tmp_path / ".claude" / "settings.json").is_file()
        assert ".claude/settings.json" in result.wrote

    def test_creates_claude_directory(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        assert (tmp_path / ".claude").is_dir()

    def test_returns_stage_result(self, tmp_path: Path):
        result = write_safety(_make_spec(), tmp_path)
        assert len(result.wrote) == 1
        assert result.warnings == []

    def test_settings_is_valid_json(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        data = _read_settings(tmp_path)
        assert isinstance(data, dict)

    def test_settings_has_safety_key(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        data = _read_settings(tmp_path)
        assert "safety" in data

    def test_output_dir_accepts_string(self, tmp_path: Path):
        result = write_safety(_make_spec(), str(tmp_path))
        assert len(result.wrote) == 1


# ---------------------------------------------------------------------------
# Posture modes
# ---------------------------------------------------------------------------


class TestBaselinePosture:

    def test_baseline_uses_defaults(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        safety = data["safety"]
        assert safety["git"]["allow_push"] is True
        assert safety["git"]["allow_force_push"] is False

    def test_baseline_allows_shell(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["shell"]["allow_shell"] is True


class TestHardenedPosture:

    def test_hardened_blocks_force_push(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["git"]["allow_force_push"] is False

    def test_hardened_blocks_branch_delete(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["git"]["allow_branch_delete"] is False

    def test_hardened_has_blocked_commands(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["safety"]["shell"]["blocked_commands"]) > 0

    def test_hardened_scans_for_secrets(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["secrets"]["scan_for_secrets"] is True
        assert data["safety"]["secrets"]["block_on_secret"] is True

    def test_hardened_blocks_destructive_ops(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["destructive_ops"]["allow_destructive"] is False

    def test_hardened_has_protected_branches(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        branches = data["safety"]["git"]["protected_branches"]
        assert "main" in branches
        assert "master" in branches


class TestRegulatedPosture:

    def test_regulated_uses_hardened_base(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.REGULATED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["git"]["allow_force_push"] is False
        assert data["safety"]["destructive_ops"]["allow_destructive"] is False


# ---------------------------------------------------------------------------
# Inline safety overrides
# ---------------------------------------------------------------------------


class TestInlineOverrides:

    def test_inline_safety_overrides_posture(self, tmp_path: Path):
        custom = SafetyConfig.permissive_safety()
        spec = _make_spec(
            hooks=HooksConfig(posture=Posture.HARDENED),
            safety=custom,
        )
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        # Permissive allows force push, even though posture is hardened
        assert data["safety"]["git"]["allow_force_push"] is True

    def test_inline_safety_allows_destructive(self, tmp_path: Path):
        custom = SafetyConfig.permissive_safety()
        spec = _make_spec(safety=custom)
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert data["safety"]["destructive_ops"]["allow_destructive"] is True


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_existing_claude_dir_not_error(self, tmp_path: Path):
        (tmp_path / ".claude").mkdir()
        result = write_safety(_make_spec(), tmp_path)
        assert len(result.wrote) == 1

    def test_overwrites_existing_settings(self, tmp_path: Path):
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "settings.json").write_text("{}")
        result = write_safety(_make_spec(), tmp_path)
        assert len(result.wrote) == 1
        data = _read_settings(tmp_path)
        assert "safety" in data

    def test_json_is_pretty_printed(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        raw = (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
        assert "\n" in raw
        assert "  " in raw

    def test_json_ends_with_newline(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        raw = (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
        assert raw.endswith("\n")

    def test_default_posture_is_baseline(self, tmp_path: Path):
        spec = _make_spec()
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        # Baseline defaults: allow_push=True, allow_force_push=False
        assert data["safety"]["git"]["allow_push"] is True
        assert data["safety"]["git"]["allow_force_push"] is False
