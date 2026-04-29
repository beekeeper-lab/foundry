"""Tests for kit-distributed skill resolution in ``asset_copier.copy_assets``.

These tests cover the contract introduced by ADR-009 (BEAN-280):

- Kit-distributed skills (``_KIT_DISTRIBUTED_SKILLS``) resolve from
  ``<claude_kit_root>/skills/<name>/`` in library-copy mode.
- Subtree mode skips skill copying entirely (the subtree already supplies
  ``.claude/shared/skills/``).
- Non-kit skills continue to resolve from ``<library_root>/claude/skills/<name>/``.
- The default ``claude_kit_root`` resolves to the bundled
  ``<foundry_root>/.claude/shared/`` submodule.
"""

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    GenerationOptions,
    HooksConfig,
    LibraryIndex,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.asset_copier import (
    _KIT_DISTRIBUTED_SKILLS,
    _default_claude_kit_root,
    copy_assets,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a minimal CompositionSpec for asset_copier tests."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
        hooks=HooksConfig(packs=[]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _make_library(tmp_path: Path) -> Path:
    """Create a minimal library tree with one non-kit skill (``review-pr.md``)."""
    lib = tmp_path / "library"

    (lib / "personas" / "developer").mkdir(parents=True)
    (lib / "claude" / "commands").mkdir(parents=True)
    (lib / "claude" / "hooks").mkdir(parents=True)

    skill_dir = lib / "claude" / "skills"
    skill_dir.mkdir(parents=True)
    # A non-kit-distributed skill — must continue to resolve from the library.
    (skill_dir / "review-pr.md").write_text("# Review PR\n")

    return lib


def _make_index(lib: Path) -> LibraryIndex:
    return LibraryIndex(
        library_root=str(lib),
        personas=[
            PersonaInfo(
                id="developer",
                path=str(lib / "personas" / "developer"),
                has_persona_md=True,
                templates=[],
            ),
        ],
    )


def _make_kit(tmp_path: Path, *, with_generate_image: bool = True,
              with_generate_screen: bool = True) -> Path:
    """Build a fake ``<claude_kit_root>`` with the kit-distributed skills.

    The shape mirrors ``.claude/shared/skills/<name>/SKILL.md`` so that the
    copier's directory-recursion path is exercised.
    """
    kit = tmp_path / "claude-kit"
    skills_dir = kit / "skills"
    skills_dir.mkdir(parents=True)

    if with_generate_image:
        gi = skills_dir / "generate-image"
        gi.mkdir()
        (gi / "SKILL.md").write_text("# Generate Image\n")

    if with_generate_screen:
        gs = skills_dir / "generate-screen"
        gs.mkdir()
        (gs / "SKILL.md").write_text("# Generate Screen\n")

    return kit


# ---------------------------------------------------------------------------
# Constant
# ---------------------------------------------------------------------------


class TestKitDistributedSkillsConstant:

    def test_kit_distributed_skills_constant_includes_generate_image_and_screen(self):
        # The ADR-009 named registry. Order is not significant; membership is.
        assert "generate-image" in _KIT_DISTRIBUTED_SKILLS
        assert "generate-screen" in _KIT_DISTRIBUTED_SKILLS

    def test_kit_distributed_skills_is_immutable_tuple(self):
        # Tuple, not list — naming and type are part of the contract.
        assert isinstance(_KIT_DISTRIBUTED_SKILLS, tuple)


# ---------------------------------------------------------------------------
# Library-copy mode resolution
# ---------------------------------------------------------------------------


class TestLibraryCopyMode:

    def test_kit_distributed_skill_resolves_from_claude_kit_in_library_copy_mode(
        self, tmp_path: Path,
    ):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        # The skill landed in the output project's .claude/skills/.
        assert (output / ".claude" / "skills" / "generate-image" / "SKILL.md").is_file()
        assert (output / ".claude" / "skills" / "generate-screen" / "SKILL.md").is_file()
        assert ".claude/skills/generate-image/SKILL.md" in result.wrote
        assert ".claude/skills/generate-screen/SKILL.md" in result.wrote

    def test_kit_distributed_skill_content_matches_kit_source(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        src = (kit / "skills" / "generate-image" / "SKILL.md").read_text()
        dest = (output / ".claude" / "skills" / "generate-image" / "SKILL.md").read_text()
        assert src == dest

    def test_non_kit_skill_resolves_from_library(self, tmp_path: Path):
        # Regression-safe: a skill that is NOT in _KIT_DISTRIBUTED_SKILLS still
        # resolves from <library_root>/claude/skills/.
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        assert (output / ".claude" / "skills" / "review-pr.md").is_file()
        assert ".claude/skills/review-pr.md" in result.wrote
        # Library content is preserved verbatim.
        src = (lib / "claude" / "skills" / "review-pr.md").read_text()
        dest = (output / ".claude" / "skills" / "review-pr.md").read_text()
        assert src == dest

    def test_kit_distributed_skill_warns_when_kit_missing_skill(self, tmp_path: Path):
        # Kit checkout is present but the named skill directory is absent.
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path, with_generate_image=False)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        # generate-image is missing — should warn but not abort.
        assert any(
            "generate-image" in w and "missing from kit" in w
            for w in result.warnings
        )
        # generate-screen is still present and copied.
        assert (output / ".claude" / "skills" / "generate-screen" / "SKILL.md").is_file()
        # Non-kit skill is still copied as well.
        assert (output / ".claude" / "skills" / "review-pr.md").is_file()

    def test_registry_overrides_library_when_skill_name_collides(
        self, tmp_path: Path,
    ):
        # If a kit-distributed skill name ALSO exists under the library
        # (legacy or accidental duplication), the registry wins — we resolve
        # from the kit.  ADR-009 §3 mandates "no two homes" but the copier
        # must still behave correctly during a transition.
        lib = _make_library(tmp_path)
        legacy = lib / "claude" / "skills" / "generate-image"
        legacy.mkdir()
        (legacy / "SKILL.md").write_text("# LEGACY library copy\n")
        idx = _make_index(lib)

        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        # Output content matches the kit source, not the library legacy.
        kit_text = (kit / "skills" / "generate-image" / "SKILL.md").read_text()
        out_text = (
            output / ".claude" / "skills" / "generate-image" / "SKILL.md"
        ).read_text()
        assert out_text == kit_text
        assert "LEGACY" not in out_text


# ---------------------------------------------------------------------------
# Subtree mode behavior
# ---------------------------------------------------------------------------


class TestSubtreeMode:

    def test_kit_distributed_skill_skipped_in_subtree_mode(self, tmp_path: Path):
        # In subtree mode, asset_copier skips ALL skills (kit-distributed and
        # otherwise) because `git subtree add` already brings in
        # `.claude/shared/skills/`.
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        spec = _make_spec(
            generation=GenerationOptions(
                claude_kit_url="git@github.com:example/claude-kit.git",
            ),
        )
        result = copy_assets(spec, idx, lib, output, claude_kit_root=kit)

        # No skills were copied — neither registry-resolved nor library-resolved.
        assert not (output / ".claude" / "skills").exists()
        assert not any(".claude/skills/" in w for w in result.wrote)
        # No "missing from kit" warning either — registry isn't consulted.
        assert not any("missing from kit" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Default claude_kit_root resolution
# ---------------------------------------------------------------------------


class TestDefaultClaudeKitRoot:

    def test_default_claude_kit_root_resolves_to_bundled_submodule(self):
        # Auto-derived path is `<foundry_root>/.claude/shared/`.  At test time
        # we run from inside the foundry checkout, so this directory exists
        # and contains the canonical kit-distributed skills.
        default = _default_claude_kit_root()

        assert default.name == "shared"
        assert default.parent.name == ".claude"
        assert default.is_dir(), (
            f"Expected the bundled ClaudeKit submodule at {default} — "
            "is the submodule initialized?"
        )
        # Sanity-check that the canonical skills actually live under the
        # default path.  This is the runtime-shape check that ADR-009 relies on.
        for name in _KIT_DISTRIBUTED_SKILLS:
            assert (default / "skills" / name).is_dir(), (
                f"Kit-distributed skill '{name}' not present under default "
                f"claude_kit_root ({default}). Either the skill was renamed "
                "or the registry drifted from .claude/shared/skills/."
            )

    def test_copy_assets_uses_default_kit_when_param_omitted(self, tmp_path: Path):
        # When claude_kit_root is omitted, copy_assets falls back to the
        # bundled submodule. The test asserts the bundled skills land in
        # the output — i.e. that the default path actually flows through.
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        output = tmp_path / "project"
        output.mkdir()

        result = copy_assets(_make_spec(), idx, lib, output)

        for name in _KIT_DISTRIBUTED_SKILLS:
            kit_skill_marker = output / ".claude" / "skills" / name
            assert kit_skill_marker.exists(), (
                f"Default claude_kit_root failed to deliver '{name}' to the "
                "generated project"
            )
        # No "missing from kit" warnings on a healthy submodule.
        assert not any("missing from kit" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# End-to-end-ish verification
# ---------------------------------------------------------------------------


class TestGeneratedProjectIncludesKitSkills:

    def test_generated_project_has_generate_image_in_library_copy_mode(
        self, tmp_path: Path,
    ):
        # End-to-end-ish: spin up a fake kit, run copy_assets in library-copy
        # mode, and assert generate-image lands in the output's .claude/skills/.
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        # The skill directory is present and contains its SKILL.md.
        gi_dir = output / ".claude" / "skills" / "generate-image"
        assert gi_dir.is_dir()
        assert (gi_dir / "SKILL.md").is_file()
        assert (gi_dir / "SKILL.md").read_text() == "# Generate Image\n"

    def test_generated_project_has_generate_screen_in_library_copy_mode(
        self, tmp_path: Path,
    ):
        lib = _make_library(tmp_path)
        idx = _make_index(lib)
        kit = _make_kit(tmp_path)
        output = tmp_path / "project"
        output.mkdir()

        copy_assets(_make_spec(), idx, lib, output, claude_kit_root=kit)

        gs_dir = output / ".claude" / "skills" / "generate-screen"
        assert gs_dir.is_dir()
        assert (gs_dir / "SKILL.md").is_file()
