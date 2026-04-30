"""Tests for media plan skeleton emission in scaffold_project (BEAN-284)."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    ProjectIdentity,
)
from foundry_app.services.scaffold import scaffold_project

_LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "ai-team-library"


def _make_spec(*, include_media_skills: bool, name: str = "Demo Project") -> CompositionSpec:
    return CompositionSpec(
        project=ProjectIdentity(
            name=name,
            slug="demo-project",
            output_root="/tmp",
        ),
        generation=GenerationOptions(include_media_skills=include_media_skills),
    )


class TestIncludeMediaSkillsDefault:
    """The new GenerationOptions field defaults to False."""

    def test_default_is_false(self):
        opts = GenerationOptions()
        assert opts.include_media_skills is False


class TestFlagOff:
    """When the flag is off, no plan files are written."""

    def test_no_image_plan(self, tmp_path: Path):
        scaffold_project(_make_spec(include_media_skills=False), tmp_path, _LIBRARY_ROOT)
        assert not (tmp_path / "IMAGE-PLAN.md").exists()

    def test_no_narration_plan(self, tmp_path: Path):
        scaffold_project(_make_spec(include_media_skills=False), tmp_path, _LIBRARY_ROOT)
        assert not (tmp_path / "NARRATION-PLAN.md").exists()


class TestFlagOn:
    """When the flag is on, both plan files are written at project root."""

    def test_image_plan_written(self, tmp_path: Path):
        result = scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        plan = tmp_path / "IMAGE-PLAN.md"
        assert plan.exists()
        assert "IMAGE-PLAN.md" in result.wrote

    def test_narration_plan_written(self, tmp_path: Path):
        result = scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        plan = tmp_path / "NARRATION-PLAN.md"
        assert plan.exists()
        assert "NARRATION-PLAN.md" in result.wrote

    def test_image_plan_has_documented_keys(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "IMAGE-PLAN.md").read_text(encoding="utf-8")
        for key in (
            "**Style:**",
            "**Generator:**",
            "**Aspect ratio:**",
            "**Background:**",
            "**Text in image:**",
            "**Avoid:**",
        ):
            assert key in text, f"missing key {key!r} in IMAGE-PLAN.md"

    def test_image_plan_default_frontmatter(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "IMAGE-PLAN.md").read_text(encoding="utf-8")
        assert "**Generator:** gemini-3-pro-image-preview" in text
        assert "**Aspect ratio:** 16:9" in text
        assert "**Background:** white" in text
        assert "**Text in image:** minimal" in text

    def test_image_plan_style_not_prefilled(self, tmp_path: Path):
        """Style is project-specific — must remain blank for the user to own."""
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "IMAGE-PLAN.md").read_text(encoding="utf-8")
        # The line should be exactly "**Style:**" with no value after the colon.
        assert "\n**Style:**\n" in text

    def test_narration_plan_has_documented_keys(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "NARRATION-PLAN.md").read_text(encoding="utf-8")
        assert "**Voice:**" in text
        assert "**Model:**" in text

    def test_narration_plan_default_frontmatter(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "NARRATION-PLAN.md").read_text(encoding="utf-8")
        assert "**Voice:** rachel" in text
        assert "**Model:** eleven_multilingual_v2" in text

    def test_narration_plan_explains_microphone_convention(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )
        text = (tmp_path / "NARRATION-PLAN.md").read_text(encoding="utf-8")
        assert "🎙️" in text


class TestProjectNameInterpolation:
    """The plan title interpolates the project name."""

    def test_image_plan_title_has_project_name(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True, name="Spaceship Atlas"),
            tmp_path,
            _LIBRARY_ROOT,
        )
        text = (tmp_path / "IMAGE-PLAN.md").read_text(encoding="utf-8")
        assert text.startswith("# Image Plan — Spaceship Atlas")

    def test_narration_plan_title_has_project_name(self, tmp_path: Path):
        scaffold_project(
            _make_spec(include_media_skills=True, name="Spaceship Atlas"),
            tmp_path,
            _LIBRARY_ROOT,
        )
        text = (tmp_path / "NARRATION-PLAN.md").read_text(encoding="utf-8")
        assert text.startswith("# Narration Plan — Spaceship Atlas")


class TestOverlaySafety:
    """Existing user-edited plan files are never overwritten."""

    def test_existing_image_plan_preserved(self, tmp_path: Path):
        existing = tmp_path / "IMAGE-PLAN.md"
        existing.write_text("# My custom plan\n\nDo not clobber.\n", encoding="utf-8")

        result = scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )

        assert existing.read_text(encoding="utf-8") == "# My custom plan\n\nDo not clobber.\n"
        assert "IMAGE-PLAN.md" not in result.wrote

    def test_existing_narration_plan_preserved(self, tmp_path: Path):
        existing = tmp_path / "NARRATION-PLAN.md"
        existing.write_text("# My custom narration plan\n", encoding="utf-8")

        result = scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, _LIBRARY_ROOT,
        )

        assert existing.read_text(encoding="utf-8") == "# My custom narration plan\n"
        assert "NARRATION-PLAN.md" not in result.wrote


class TestLibraryRootMissing:
    """When include_media_skills=True but library_root is omitted, warn and skip."""

    def test_warns_when_library_root_none(self, tmp_path: Path):
        result = scaffold_project(
            _make_spec(include_media_skills=True), tmp_path, library_root=None,
        )
        assert any("library_root" in w for w in result.warnings)
        assert not (tmp_path / "IMAGE-PLAN.md").exists()
        assert not (tmp_path / "NARRATION-PLAN.md").exists()
