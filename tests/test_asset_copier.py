"""Tests for foundry_app.services.asset_copier — library asset copying."""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.asset_copier import copy_assets

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _all_hooks_config() -> HooksConfig:
    """Return a HooksConfig with both test hook packs enabled."""
    return HooksConfig(packs=[
        HookPackSelection(id="pre-commit-lint", enabled=True),
        HookPackSelection(id="security-scan", enabled=True),
    ])


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults.

    NOTE: By default, no hook packs are selected (hooks.packs is empty),
    which means no hooks will be copied.  Pass ``hooks=_all_hooks_config()``
    to enable hook copying in tests that need it.
    """
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _make_library(tmp_path: Path) -> Path:
    """Create a minimal library structure with templates, commands, and hooks."""
    lib = tmp_path / "library"

    # Persona templates
    tpl_dir = lib / "personas" / "developer" / "templates"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "implementation-plan.md").write_text("# Implementation Plan\n")
    (tpl_dir / "pr-description.md").write_text("# PR Description\n")

    # Architect persona (no templates dir)
    (lib / "personas" / "architect").mkdir(parents=True)
    # architect has persona dir but no templates/

    # Commands
    cmd_dir = lib / "claude" / "commands"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "validate-repo.md").write_text("# Validate Repo\n")
    (cmd_dir / "seed-tasks.md").write_text("# Seed Tasks\n")

    # Hooks
    hook_dir = lib / "claude" / "hooks"
    hook_dir.mkdir(parents=True)
    (hook_dir / "pre-commit-lint.md").write_text("# Pre-commit Lint\n")
    (hook_dir / "security-scan.md").write_text("# Security Scan\n")

    # Skills
    skill_dir = lib / "claude" / "skills"
    skill_dir.mkdir(parents=True)
    (skill_dir / "review-pr.md").write_text("# Review PR\n")
    (skill_dir / "deploy.md").write_text("# Deploy\n")

    return lib


def _make_index(lib: Path) -> LibraryIndex:
    """Build a LibraryIndex matching the _make_library layout."""
    return LibraryIndex(
        library_root=str(lib),
        personas=[
            PersonaInfo(
                id="developer",
                path=str(lib / "personas" / "developer"),
                has_persona_md=True,
                templates=["implementation-plan.md", "pr-description.md"],
            ),
            PersonaInfo(
                id="architect",
                path=str(lib / "personas" / "architect"),
                has_persona_md=True,
                templates=[],
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Persona template copying
# ---------------------------------------------------------------------------


class TestPersonaTemplates:

    def test_copies_templates_when_include_templates_true(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()
        (output / "ai" / "outputs" / "developer").mkdir(parents=True)

        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="developer", include_templates=True)]),
        )
        result = copy_assets(spec, idx, lib, output)

        assert (output / "ai" / "outputs" / "developer" / "implementation-plan.md").is_file()
        assert (output / "ai" / "outputs" / "developer" / "pr-description.md").is_file()
        assert "ai/outputs/developer/implementation-plan.md" in result.wrote
        assert "ai/outputs/developer/pr-description.md" in result.wrote

    def test_skips_templates_when_include_templates_false(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="developer", include_templates=False)]
            ),
        )
        result = copy_assets(spec, idx, lib, output)

        assert not (output / "ai" / "outputs" / "developer" / "implementation-plan.md").exists()
        # Templates should not appear in wrote
        template_writes = [w for w in result.wrote if "ai/outputs/developer" in w]
        assert template_writes == []

    def test_warns_when_persona_not_in_index(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="nonexistent", include_templates=True)]
            ),
        )
        result = copy_assets(spec, idx, lib, output)

        assert any("nonexistent" in w and "not found" in w for w in result.warnings)

    def test_warns_when_no_templates_directory(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = LibraryIndex(
            library_root=str(lib),
            personas=[
                PersonaInfo(
                    id="architect",
                    path=str(lib / "personas" / "architect"),
                    has_persona_md=True,
                    templates=["some-template.md"],
                ),
            ],
        )
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="architect", include_templates=True)]
            ),
        )
        result = copy_assets(spec, idx, lib, output)

        assert any("No templates directory" in w for w in result.warnings)

    def test_warns_when_persona_has_empty_templates_list(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        # Create templates dir for architect but leave it empty
        (lib / "personas" / "architect" / "templates").mkdir(parents=True, exist_ok=True)
        idx = LibraryIndex(
            library_root=str(lib),
            personas=[
                PersonaInfo(
                    id="architect",
                    path=str(lib / "personas" / "architect"),
                    has_persona_md=True,
                    templates=[],
                ),
            ],
        )
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="architect", include_templates=True)]
            ),
        )
        result = copy_assets(spec, idx, lib, output)

        assert any("no template files" in w for w in result.warnings)

    def test_copies_templates_for_multiple_personas(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        # Add a tech-qa persona with templates
        tpl_dir = lib / "personas" / "tech-qa" / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "test-plan.md").write_text("# Test Plan\n")

        idx = LibraryIndex(
            library_root=str(lib),
            personas=[
                PersonaInfo(
                    id="developer",
                    path=str(lib / "personas" / "developer"),
                    templates=["implementation-plan.md", "pr-description.md"],
                ),
                PersonaInfo(
                    id="tech-qa",
                    path=str(lib / "personas" / "tech-qa"),
                    templates=["test-plan.md"],
                ),
            ],
        )
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer", include_templates=True),
                PersonaSelection(id="tech-qa", include_templates=True),
            ]),
        )
        result = copy_assets(spec, idx, lib, output)

        assert (output / "ai" / "outputs" / "developer" / "implementation-plan.md").is_file()
        assert (output / "ai" / "outputs" / "tech-qa" / "test-plan.md").is_file()
        assert "ai/outputs/developer/implementation-plan.md" in result.wrote
        assert "ai/outputs/tech-qa/test-plan.md" in result.wrote


# ---------------------------------------------------------------------------
# Command copying
# ---------------------------------------------------------------------------


class TestCommandCopying:

    def test_copies_commands_from_library(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()
        (output / ".claude" / "commands").mkdir(parents=True)

        result = copy_assets(_make_spec(), idx, lib, output)

        assert (output / ".claude" / "commands" / "validate-repo.md").is_file()
        assert (output / ".claude" / "commands" / "seed-tasks.md").is_file()
        assert ".claude/commands/validate-repo.md" in result.wrote
        assert ".claude/commands/seed-tasks.md" in result.wrote

    def test_creates_commands_dir_if_missing(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output)

        assert (output / ".claude" / "commands").is_dir()

    def test_command_content_matches_source(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output)

        src = (lib / "claude" / "commands" / "validate-repo.md").read_text()
        dest = (output / ".claude" / "commands" / "validate-repo.md").read_text()
        assert src == dest


# ---------------------------------------------------------------------------
# Hook copying
# ---------------------------------------------------------------------------


class TestHookCopying:

    def test_copies_hooks_when_packs_enabled(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()
        (output / ".claude" / "hooks").mkdir(parents=True)

        spec = _make_spec(hooks=_all_hooks_config())
        result = copy_assets(spec, idx, lib, output)

        assert (output / ".claude" / "hooks" / "pre-commit-lint.md").is_file()
        assert (output / ".claude" / "hooks" / "security-scan.md").is_file()
        assert ".claude/hooks/pre-commit-lint.md" in result.wrote
        assert ".claude/hooks/security-scan.md" in result.wrote

    def test_creates_hooks_dir_when_packs_enabled(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=_all_hooks_config())
        copy_assets(spec, idx, lib, output)

        assert (output / ".claude" / "hooks").is_dir()

    def test_hook_content_matches_source(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=_all_hooks_config())
        copy_assets(spec, idx, lib, output)

        src = (lib / "claude" / "hooks" / "security-scan.md").read_text()
        dest = (output / ".claude" / "hooks" / "security-scan.md").read_text()
        assert src == dest

    def test_copies_only_selected_hooks(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="pre-commit-lint", enabled=True),
            HookPackSelection(id="security-scan", enabled=False),
        ]))
        result = copy_assets(spec, idx, lib, output)

        assert (output / ".claude" / "hooks" / "pre-commit-lint.md").is_file()
        assert not (output / ".claude" / "hooks" / "security-scan.md").exists()
        assert ".claude/hooks/pre-commit-lint.md" in result.wrote
        assert ".claude/hooks/security-scan.md" not in result.wrote

    def test_no_hooks_copied_when_no_packs_selected(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=HooksConfig(packs=[]))
        result = copy_assets(spec, idx, lib, output)

        assert not (output / ".claude" / "hooks").exists()
        hook_writes = [w for w in result.wrote if ".claude/hooks" in w]
        assert hook_writes == []

    def test_no_hooks_copied_when_all_packs_disabled(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=HooksConfig(packs=[
            HookPackSelection(id="pre-commit-lint", enabled=False),
            HookPackSelection(id="security-scan", enabled=False),
        ]))
        result = copy_assets(spec, idx, lib, output)

        assert not (output / ".claude" / "hooks").exists()
        hook_writes = [w for w in result.wrote if ".claude/hooks" in w]
        assert hook_writes == []

    def test_commands_and_skills_copied_regardless_of_hook_selection(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=HooksConfig(packs=[]))
        result = copy_assets(spec, idx, lib, output)

        assert ".claude/commands/validate-repo.md" in result.wrote
        assert ".claude/commands/seed-tasks.md" in result.wrote
        assert ".claude/skills/review-pr.md" in result.wrote
        assert ".claude/skills/deploy.md" in result.wrote


# ---------------------------------------------------------------------------
# Skills copying
# ---------------------------------------------------------------------------


class TestSkillsCopying:

    def test_copies_skills_from_library(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        assert (output / ".claude" / "skills" / "review-pr.md").is_file()
        assert (output / ".claude" / "skills" / "deploy.md").is_file()
        assert ".claude/skills/review-pr.md" in result.wrote
        assert ".claude/skills/deploy.md" in result.wrote

    def test_creates_skills_dir_if_missing(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output)

        assert (output / ".claude" / "skills").is_dir()

    def test_skill_content_matches_source(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output)

        src = (lib / "claude" / "skills" / "review-pr.md").read_text()
        dest = (output / ".claude" / "skills" / "review-pr.md").read_text()
        assert src == dest


# ---------------------------------------------------------------------------
# Overlay mode (existing files)
# ---------------------------------------------------------------------------


class TestOverlayMode:

    def test_skips_identical_existing_file(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        cmd_dir = output / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        # Write identical content
        (cmd_dir / "validate-repo.md").write_text("# Validate Repo\n")

        result = copy_assets(_make_spec(), idx, lib, output)

        # Should NOT be in wrote (skipped as identical)
        assert ".claude/commands/validate-repo.md" not in result.wrote
        # seed-tasks.md should still be copied
        assert ".claude/commands/seed-tasks.md" in result.wrote

    def test_warns_on_different_existing_file(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        cmd_dir = output / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        # Write different content
        (cmd_dir / "validate-repo.md").write_text("# Custom Validate Repo\n")

        result = copy_assets(_make_spec(), idx, lib, output)

        assert ".claude/commands/validate-repo.md" not in result.wrote
        assert any("different content" in w for w in result.warnings)

    def test_conflict_does_not_overwrite(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        cmd_dir = output / ".claude" / "commands"
        cmd_dir.mkdir(parents=True)
        custom = "# My Custom Content\n"
        (cmd_dir / "validate-repo.md").write_text(custom)

        copy_assets(_make_spec(), idx, lib, output)

        # Original content preserved
        assert (cmd_dir / "validate-repo.md").read_text() == custom

    def test_overlay_copies_only_new_files(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(hooks=_all_hooks_config())

        # First run copies everything
        result1 = copy_assets(spec, idx, lib, output)
        assert len(result1.wrote) > 0

        # Second run copies nothing (all identical)
        result2 = copy_assets(spec, idx, lib, output)
        assert result2.wrote == []
        assert result2.warnings == []


# ---------------------------------------------------------------------------
# StageResult correctness
# ---------------------------------------------------------------------------


class TestStageResult:

    def test_wrote_contains_relative_paths(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        for path in result.wrote:
            assert not path.startswith("/"), f"Path should be relative: {path}"

    def test_wrote_count_matches_expected(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(
                personas=[PersonaSelection(id="developer", include_templates=True)]
            ),
            hooks=_all_hooks_config(),
        )
        result = copy_assets(spec, idx, lib, output)

        # 2 templates + 2 commands + 2 hooks + 2 skills = 8
        assert len(result.wrote) == 8

    def test_no_warnings_on_clean_run(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        assert result.warnings == []

    def test_warnings_accumulate(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="nonexistent1", include_templates=True),
                PersonaSelection(id="nonexistent2", include_templates=True),
            ]),
        )
        result = copy_assets(spec, idx, lib, output)

        assert len([w for w in result.warnings if "not found" in w]) == 2


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------



class TestSymlinkSkipping:

    def test_skips_symlinks_with_warning(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        target_file = tmp_path / "outside.md"
        target_file.write_text("# Outside file\n")
        (lib / "claude" / "commands" / "evil-link.md").symlink_to(target_file)

        result = copy_assets(_make_spec(), idx, lib, output)

        assert not (output / ".claude" / "commands" / "evil-link.md").exists()
        assert any("Skipping symlink" in w and "evil-link.md" in w for w in result.warnings)

    def test_copies_regular_files_alongside_symlinks(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        target_file = tmp_path / "outside.md"
        target_file.write_text("# Outside file\n")
        (lib / "claude" / "commands" / "evil-link.md").symlink_to(target_file)

        result = copy_assets(_make_spec(), idx, lib, output)

        assert (output / ".claude" / "commands" / "validate-repo.md").is_file()
        assert ".claude/commands/validate-repo.md" in result.wrote


class TestEdgeCases:

    def test_accepts_string_paths(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, str(lib), str(output))

        assert len(result.wrote) > 0

    def test_accepts_path_objects(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        assert len(result.wrote) > 0

    def test_empty_persona_list(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(team=TeamConfig(personas=[]), hooks=_all_hooks_config())
        result = copy_assets(spec, idx, lib, output)

        # Still copies commands, skills, and selected hooks
        assert ".claude/commands/validate-repo.md" in result.wrote
        assert ".claude/hooks/pre-commit-lint.md" in result.wrote
        # No template paths
        template_writes = [w for w in result.wrote if "ai/outputs" in w]
        assert template_writes == []

    def test_missing_commands_dir_in_library(self, tmp_path: Path):
        lib = tmp_path / "empty-library"
        lib.mkdir()
        idx = LibraryIndex(library_root=str(lib))
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(team=TeamConfig(personas=[]))
        result = copy_assets(spec, idx, lib, output)

        # Should not error, just copy nothing
        assert result.wrote == []
        assert result.warnings == []

    def test_library_dir_with_subdirectories_only_copies_files(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        # Add a subdirectory in commands (should be ignored)
        (lib / "claude" / "commands" / "subdir").mkdir()
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        # Only files should be in wrote, not directories
        for path in result.wrote:
            assert (output / path).is_file()

    def test_dest_dir_created_automatically(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        # Don't create output dir or subdirs — copy_assets should handle it

        spec = _make_spec(hooks=_all_hooks_config())
        result = copy_assets(spec, idx, lib, output)

        assert (output / ".claude" / "commands").is_dir()
        assert (output / ".claude" / "hooks").is_dir()
        assert len(result.wrote) > 0

    def test_mixed_templates_some_enabled_some_disabled(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        # Add tech-qa with templates
        tpl_dir = lib / "personas" / "tech-qa" / "templates"
        tpl_dir.mkdir(parents=True)
        (tpl_dir / "test-plan.md").write_text("# Test Plan\n")

        idx = LibraryIndex(
            library_root=str(lib),
            personas=[
                PersonaInfo(
                    id="developer",
                    path=str(lib / "personas" / "developer"),
                    templates=["implementation-plan.md", "pr-description.md"],
                ),
                PersonaInfo(
                    id="tech-qa",
                    path=str(lib / "personas" / "tech-qa"),
                    templates=["test-plan.md"],
                ),
            ],
        )
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            team=TeamConfig(personas=[
                PersonaSelection(id="developer", include_templates=True),
                PersonaSelection(id="tech-qa", include_templates=False),
            ]),
        )
        result = copy_assets(spec, idx, lib, output)

        # Developer templates copied
        assert "ai/outputs/developer/implementation-plan.md" in result.wrote
        # Tech-qa templates NOT copied
        assert not any("tech-qa" in w for w in result.wrote if "ai/outputs" in w)
