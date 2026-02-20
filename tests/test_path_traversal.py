"""Security tests — path traversal hardening (BEAN-112)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    HookPackSelection,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.generator import generate_project


# ---------------------------------------------------------------------------
# ProjectIdentity.output_root
# ---------------------------------------------------------------------------

class TestOutputRootTraversal:
    """output_root must not contain '..' path components."""

    def test_rejects_dotdot_relative(self):
        with pytest.raises(ValidationError, match="output_root"):
            ProjectIdentity(name="x", slug="x", output_root="../../../tmp")

    def test_rejects_dotdot_embedded(self):
        with pytest.raises(ValidationError, match="output_root"):
            ProjectIdentity(name="x", slug="x", output_root="foo/../bar")

    def test_accepts_relative_path(self):
        p = ProjectIdentity(name="x", slug="x", output_root="./generated-projects")
        assert p.output_root == "./generated-projects"

    def test_accepts_absolute_path(self):
        p = ProjectIdentity(name="x", slug="x", output_root="/home/user/projects")
        assert p.output_root == "/home/user/projects"

    def test_accepts_nested_relative(self):
        p = ProjectIdentity(name="x", slug="x", output_root="some/deep/path")
        assert p.output_root == "some/deep/path"


# ---------------------------------------------------------------------------
# ProjectIdentity.output_folder
# ---------------------------------------------------------------------------

class TestOutputFolderTraversal:
    """output_folder must not contain traversal sequences or separators."""

    def test_rejects_dotdot(self):
        with pytest.raises(ValidationError, match="output_folder"):
            ProjectIdentity(name="x", slug="x", output_folder="../../evil")

    def test_rejects_slash(self):
        with pytest.raises(ValidationError, match="output_folder"):
            ProjectIdentity(name="x", slug="x", output_folder="foo/bar")

    def test_rejects_backslash(self):
        with pytest.raises(ValidationError, match="output_folder"):
            ProjectIdentity(name="x", slug="x", output_folder="foo\\bar")

    def test_accepts_simple_name(self):
        p = ProjectIdentity(name="x", slug="x", output_folder="my-project")
        assert p.output_folder == "my-project"

    def test_accepts_none(self):
        p = ProjectIdentity(name="x", slug="x", output_folder=None)
        assert p.output_folder is None


# ---------------------------------------------------------------------------
# PersonaSelection.id
# ---------------------------------------------------------------------------

class TestPersonaIdTraversal:
    """Persona IDs must not contain traversal sequences."""

    def test_rejects_dotdot(self):
        with pytest.raises(ValidationError, match="persona id"):
            PersonaSelection(id="../../evil")

    def test_rejects_slash(self):
        with pytest.raises(ValidationError, match="persona id"):
            PersonaSelection(id="foo/bar")

    def test_rejects_backslash(self):
        with pytest.raises(ValidationError, match="persona id"):
            PersonaSelection(id="foo\\bar")

    def test_accepts_normal_id(self):
        p = PersonaSelection(id="developer")
        assert p.id == "developer"

    def test_accepts_hyphenated_id(self):
        p = PersonaSelection(id="tech-qa")
        assert p.id == "tech-qa"


# ---------------------------------------------------------------------------
# StackSelection.id
# ---------------------------------------------------------------------------

class TestStackIdTraversal:
    """Stack IDs must not contain traversal sequences."""

    def test_rejects_dotdot(self):
        with pytest.raises(ValidationError, match="stack id"):
            StackSelection(id="../../evil")

    def test_rejects_slash(self):
        with pytest.raises(ValidationError, match="stack id"):
            StackSelection(id="foo/bar")

    def test_accepts_normal_id(self):
        s = StackSelection(id="python")
        assert s.id == "python"


# ---------------------------------------------------------------------------
# HookPackSelection.id
# ---------------------------------------------------------------------------

class TestHookPackIdTraversal:
    """Hook pack IDs must not contain traversal sequences."""

    def test_rejects_dotdot(self):
        with pytest.raises(ValidationError, match="hook pack id"):
            HookPackSelection(id="../../evil")

    def test_rejects_slash(self):
        with pytest.raises(ValidationError, match="hook pack id"):
            HookPackSelection(id="foo/bar")

    def test_accepts_normal_id(self):
        h = HookPackSelection(id="pre-commit-lint")
        assert h.id == "pre-commit-lint"


# ---------------------------------------------------------------------------
# Generator containment check
# ---------------------------------------------------------------------------

class TestGeneratorContainment:
    """generate_project() must reject output dirs that escape containment."""

    def test_rejects_traversal_in_composition_output_root(self, tmp_path):
        """A composition with a traversal output_root should be rejected at model level."""
        with pytest.raises(ValidationError, match="output_root"):
            CompositionSpec(
                project=ProjectIdentity(
                    name="evil",
                    slug="evil",
                    output_root="../../../tmp",
                ),
            )

    def test_rejects_traversal_in_persona_id(self):
        """A composition with a traversal persona ID should be rejected at model level."""
        with pytest.raises(ValidationError, match="persona id"):
            CompositionSpec(
                project=ProjectIdentity(name="test", slug="test"),
                team={"personas": [{"id": "../../admin"}]},
            )

    def test_runtime_containment_rejects_traversal_bypassing_model(self, tmp_path):
        """Runtime ValueError fires even when Pydantic model validation is bypassed.

        Uses model_construct() to skip validators, proving the generator's
        runtime containment check is an independent defense-in-depth layer.
        """
        safe_root = tmp_path / "safe"
        safe_root.mkdir()

        # Bypass Pydantic validators — model_construct() skips field validation,
        # allowing a traversal path that would normally be rejected.
        project = ProjectIdentity.model_construct(
            name="evil",
            slug="evil",
            output_root=str(safe_root),
            output_folder="../../escape",
        )
        spec = CompositionSpec.model_construct(
            project=project,
            stacks=[],
            team=TeamConfig(),
            generation=GenerationOptions(),
        )

        with pytest.raises(ValueError, match="Refusing to generate"):
            generate_project(spec, library_root=tmp_path / "lib")

    def test_safe_composition_accepted(self):
        """A valid composition should be accepted."""
        spec = CompositionSpec(
            project=ProjectIdentity(
                name="My Project",
                slug="my-project",
                output_root="./generated",
            ),
            stacks=[StackSelection(id="python")],
        )
        assert spec.project.slug == "my-project"
