"""Tests for foundry_app.services.asset_copier: copy skills, commands, hooks."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import HookPackSelection, HooksConfig
from foundry_app.services.asset_copier import (
    copy_commands,
    copy_skills,
    write_hooks_config,
)

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


# -- copy_skills ---------------------------------------------------------------


def test_copy_skills_creates_core_skills(tmp_path: Path):
    """copy_skills should copy core skill directories into .claude/skills/."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    result = copy_skills(LIBRARY_ROOT, project_dir, persona_ids=["developer"])

    skills_dir = project_dir / ".claude" / "skills"
    assert skills_dir.is_dir()
    # Core skills should be present
    assert (skills_dir / "compile-team").is_dir()
    assert (skills_dir / "seed-tasks").is_dir()
    assert (skills_dir / "new-work").is_dir()
    assert (skills_dir / "handoff").is_dir()
    assert (skills_dir / "validate-config").is_dir()
    assert len(result.wrote) > 0


def test_copy_skills_includes_persona_specific(tmp_path: Path):
    """copy_skills for developer should include review-pr skill."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    copy_skills(LIBRARY_ROOT, project_dir, persona_ids=["developer"])

    skills_dir = project_dir / ".claude" / "skills"
    assert (skills_dir / "review-pr").is_dir()


def test_copy_skills_architect_gets_adr(tmp_path: Path):
    """copy_skills for architect should include new-adr skill."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    copy_skills(LIBRARY_ROOT, project_dir, persona_ids=["architect"])

    skills_dir = project_dir / ".claude" / "skills"
    assert (skills_dir / "new-adr").is_dir()
    assert (skills_dir / "scaffold-project").is_dir()


def test_copy_skills_multiple_personas(tmp_path: Path):
    """copy_skills for multiple personas should include all relevant skills."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    copy_skills(
        LIBRARY_ROOT, project_dir,
        persona_ids=["developer", "architect", "security-engineer"],
    )

    skills_dir = project_dir / ".claude" / "skills"
    assert (skills_dir / "review-pr").is_dir()
    assert (skills_dir / "new-adr").is_dir()
    assert (skills_dir / "threat-model").is_dir()


def test_copy_skills_unknown_persona_no_crash(tmp_path: Path):
    """copy_skills with an unknown persona should not crash."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    result = copy_skills(LIBRARY_ROOT, project_dir, persona_ids=["unknown-ghost"])

    # Should still have core skills
    assert len(result.wrote) > 0


def test_copy_skills_empty_personas(tmp_path: Path):
    """copy_skills with empty personas should still copy core skills."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    result = copy_skills(LIBRARY_ROOT, project_dir, persona_ids=[])

    skills_dir = project_dir / ".claude" / "skills"
    assert (skills_dir / "compile-team").is_dir()
    assert len(result.wrote) > 0


# -- copy_commands -------------------------------------------------------------


def test_copy_commands_creates_core_commands(tmp_path: Path):
    """copy_commands should copy core command files into .claude/commands/."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    result = copy_commands(LIBRARY_ROOT, project_dir, persona_ids=["developer"])

    commands_dir = project_dir / ".claude" / "commands"
    assert commands_dir.is_dir()
    assert (commands_dir / "compile-team.md").is_file()
    assert (commands_dir / "seed-tasks.md").is_file()
    assert (commands_dir / "new-work.md").is_file()
    assert (commands_dir / "handoff.md").is_file()
    assert (commands_dir / "status-report.md").is_file()
    assert len(result.wrote) > 0


def test_copy_commands_includes_persona_specific(tmp_path: Path):
    """copy_commands for developer should include review-pr command."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    copy_commands(LIBRARY_ROOT, project_dir, persona_ids=["developer"])

    commands_dir = project_dir / ".claude" / "commands"
    assert (commands_dir / "review-pr.md").is_file()


def test_copy_commands_ba_gets_notes_to_stories(tmp_path: Path):
    """copy_commands for ba should include notes-to-stories command."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    copy_commands(LIBRARY_ROOT, project_dir, persona_ids=["ba"])

    commands_dir = project_dir / ".claude" / "commands"
    assert (commands_dir / "notes-to-stories.md").is_file()


def test_copy_commands_wrote_paths_are_relative(tmp_path: Path):
    """All paths in result.wrote should be relative (no leading '/')."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    result = copy_commands(LIBRARY_ROOT, project_dir, persona_ids=["developer"])

    for path_str in result.wrote:
        assert not path_str.startswith("/"), f"Expected relative path: {path_str}"


# -- write_hooks_config --------------------------------------------------------


def test_write_hooks_copies_enabled_packs(tmp_path: Path):
    """write_hooks_config should copy enabled hook pack docs."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    hooks = HooksConfig(
        packs=[
            HookPackSelection(id="pre-commit-lint", enabled=True),
            HookPackSelection(id="security-scan", enabled=True),
        ]
    )

    result = write_hooks_config(LIBRARY_ROOT, project_dir, hooks)

    hooks_dir = project_dir / ".claude" / "hooks"
    assert (hooks_dir / "pre-commit-lint.md").is_file()
    assert (hooks_dir / "security-scan.md").is_file()
    assert len(result.wrote) >= 2


def test_write_hooks_skips_disabled_packs(tmp_path: Path):
    """write_hooks_config should skip disabled hook packs."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    hooks = HooksConfig(
        packs=[
            HookPackSelection(id="pre-commit-lint", enabled=False),
        ]
    )

    write_hooks_config(LIBRARY_ROOT, project_dir, hooks)

    hooks_dir = project_dir / ".claude" / "hooks"
    assert not (hooks_dir / "pre-commit-lint.md").exists()


def test_write_hooks_always_copies_hook_policy(tmp_path: Path):
    """write_hooks_config should always copy hook-policy.md if it exists."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    hooks = HooksConfig(packs=[])

    write_hooks_config(LIBRARY_ROOT, project_dir, hooks)

    hooks_dir = project_dir / ".claude" / "hooks"
    assert (hooks_dir / "hook-policy.md").is_file()


def test_write_hooks_warns_on_missing_pack(tmp_path: Path):
    """write_hooks_config should warn when a pack doesn't exist in the library."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    hooks = HooksConfig(
        packs=[
            HookPackSelection(id="nonexistent-pack", enabled=True),
        ]
    )

    result = write_hooks_config(LIBRARY_ROOT, project_dir, hooks)

    assert len(result.warnings) > 0
    assert any("nonexistent-pack" in w for w in result.warnings)
