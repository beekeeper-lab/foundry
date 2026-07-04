"""Tests for write_permissions — posture-derived settings.local.json (SPEC-016)."""

import json
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    HooksConfig,
    Posture,
    ProjectIdentity,
    SafetyConfig,
)
from foundry_app.services.safety_writer import write_permissions


def _spec(posture: Posture = Posture.BASELINE, **kwargs) -> CompositionSpec:
    return CompositionSpec(
        project=ProjectIdentity(name="Test", slug="test"),
        hooks=HooksConfig(posture=posture),
        **kwargs,
    )


def _perms(output: Path) -> dict:
    data = json.loads(
        (output / ".claude" / "settings.local.json").read_text(encoding="utf-8")
    )
    return data["permissions"]


class TestPostureDifferentiation:
    def test_three_postures_differ_and_nest(self, tmp_path: Path):
        """hardened deny ⊇ baseline deny; regulated deny ⊇ hardened deny —
        and each posture adds something."""
        denies = {}
        for posture in (Posture.BASELINE, Posture.HARDENED, Posture.REGULATED):
            out = tmp_path / posture.value
            write_permissions(_spec(posture), out)
            denies[posture] = set(_perms(out)["deny"])

        assert denies[Posture.BASELINE] < denies[Posture.HARDENED]
        assert denies[Posture.HARDENED] < denies[Posture.REGULATED]

    def test_baseline_covers_core_protections(self, tmp_path: Path):
        write_permissions(_spec(), tmp_path)
        deny = _perms(tmp_path)["deny"]
        assert "Bash(git push origin main:*)" in deny
        assert "Bash(git push --force:*)" in deny
        assert "Read(./.env)" in deny

    def test_regulated_blocks_deploy_branches(self, tmp_path: Path):
        write_permissions(_spec(Posture.REGULATED), tmp_path)
        deny = _perms(tmp_path)["deny"]
        assert "Bash(git push origin test:*)" in deny
        assert "Bash(git push origin prod:*)" in deny


class TestBaseOverlay:
    def test_library_base_rules_survive(self, tmp_path: Path):
        claude = tmp_path / ".claude"
        claude.mkdir()
        base = {
            "permissions": {
                "allow": ["Read(**)"],
                "deny": ["Bash(git push * main)"],
            },
            "defaultMode": "acceptEdits",
        }
        (claude / "settings.local.json").write_text(json.dumps(base))

        write_permissions(_spec(), tmp_path)
        data = json.loads((claude / "settings.local.json").read_text())
        assert "Read(**)" in data["permissions"]["allow"]
        assert "Bash(git push * main)" in data["permissions"]["deny"]
        assert data["defaultMode"] == "acceptEdits"
        # Derived rules were added on top.
        assert "Bash(git push origin main:*)" in data["permissions"]["deny"]

    def test_idempotent(self, tmp_path: Path):
        write_permissions(_spec(), tmp_path)
        first = _perms(tmp_path)
        write_permissions(_spec(), tmp_path)
        assert _perms(tmp_path) == first


class TestEffectiveSafety:
    def test_explicit_safety_wins(self, tmp_path: Path):
        spec = _spec(safety=SafetyConfig.permissive_safety())
        write_permissions(spec, tmp_path)
        deny = _perms(tmp_path)["deny"]
        # Permissive: no protected branches, force push allowed, no secret
        # blocking — the branch/force rules must not appear.
        assert not any("git push origin main" in r for r in deny)
        assert not any("--force" in r for r in deny)

    def test_fallback_matches_posture(self):
        assert (
            _spec(Posture.REGULATED).effective_safety().git.protected_branches
            == SafetyConfig.regulated_safety().git.protected_branches
        )
        assert _spec().effective_safety() == SafetyConfig.baseline_safety()
