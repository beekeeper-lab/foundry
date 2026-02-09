"""Tests for foundry_app.core.models — Pydantic data contracts."""

import pytest
from pydantic import ValidationError

from foundry_app.core.models import (
    CompositionSpec,
    DestructiveOpsPolicy,
    FileAction,
    FileActionType,
    FileSystemPolicy,
    GenerationManifest,
    GenerationOptions,
    GitPolicy,
    HookMode,
    HookPackInfo,
    HookPackSelection,
    HooksConfig,
    LibraryIndex,
    NetworkPolicy,
    OverlayPlan,
    PersonaInfo,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    SafetyConfig,
    SecretPolicy,
    SeedMode,
    ShellPolicy,
    StackInfo,
    StackSelection,
    StageResult,
    Strictness,
    TeamConfig,
)

# ---------------------------------------------------------------------------
# ProjectIdentity
# ---------------------------------------------------------------------------

class TestProjectIdentity:
    def test_minimal(self):
        p = ProjectIdentity(name="Test", slug="test")
        assert p.name == "Test"
        assert p.slug == "test"
        assert p.output_root == "./generated-projects"
        assert p.output_folder is None

    def test_resolved_output_folder_uses_slug(self):
        p = ProjectIdentity(name="Test", slug="my-proj")
        assert p.resolved_output_folder == "my-proj"

    def test_resolved_output_folder_uses_explicit(self):
        p = ProjectIdentity(name="Test", slug="my-proj", output_folder="custom")
        assert p.resolved_output_folder == "custom"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            ProjectIdentity(name="", slug="test")

    def test_empty_slug_rejected(self):
        with pytest.raises(ValidationError):
            ProjectIdentity(name="Test", slug="")

    def test_invalid_slug_pattern(self):
        with pytest.raises(ValidationError):
            ProjectIdentity(name="Test", slug="Invalid Slug!")

    def test_slug_allows_hyphens_and_numbers(self):
        p = ProjectIdentity(name="Test", slug="my-proj-123")
        assert p.slug == "my-proj-123"

    def test_slug_must_start_with_alphanumeric(self):
        with pytest.raises(ValidationError):
            ProjectIdentity(name="Test", slug="-bad-start")


# ---------------------------------------------------------------------------
# StackSelection
# ---------------------------------------------------------------------------

class TestStackSelection:
    def test_minimal(self):
        s = StackSelection(id="python")
        assert s.id == "python"
        assert s.order == 0

    def test_with_order(self):
        s = StackSelection(id="react", order=20)
        assert s.order == 20

    def test_empty_id_rejected(self):
        with pytest.raises(ValidationError):
            StackSelection(id="")


# ---------------------------------------------------------------------------
# PersonaSelection
# ---------------------------------------------------------------------------

class TestPersonaSelection:
    def test_defaults(self):
        p = PersonaSelection(id="developer")
        assert p.include_agent is True
        assert p.include_templates is True
        assert p.strictness == Strictness.STANDARD

    def test_custom_strictness(self):
        p = PersonaSelection(id="security-engineer", strictness="strict")
        assert p.strictness == Strictness.STRICT

    def test_empty_id_rejected(self):
        with pytest.raises(ValidationError):
            PersonaSelection(id="")


# ---------------------------------------------------------------------------
# TeamConfig
# ---------------------------------------------------------------------------

class TestTeamConfig:
    def test_empty(self):
        t = TeamConfig()
        assert t.personas == []

    def test_with_personas(self):
        t = TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
            PersonaSelection(id="developer"),
        ])
        assert len(t.personas) == 2
        assert t.personas[0].id == "team-lead"


# ---------------------------------------------------------------------------
# HookPackSelection / HooksConfig
# ---------------------------------------------------------------------------

class TestHooksConfig:
    def test_defaults(self):
        h = HooksConfig()
        assert h.posture == Posture.BASELINE
        assert h.packs == []

    def test_with_packs(self):
        h = HooksConfig(
            posture="hardened",
            packs=[
                HookPackSelection(id="pre-commit-lint", enabled=True, mode="enforcing"),
                HookPackSelection(id="security-scan", enabled=False),
            ],
        )
        assert h.posture == Posture.HARDENED
        assert len(h.packs) == 2
        assert h.packs[1].enabled is False

    def test_hook_pack_defaults(self):
        hp = HookPackSelection(id="test-pack")
        assert hp.enabled is True
        assert hp.mode == HookMode.ENFORCING


# ---------------------------------------------------------------------------
# Safety sub-policies
# ---------------------------------------------------------------------------

class TestGitPolicy:
    def test_defaults(self):
        g = GitPolicy()
        assert g.allow_push is True
        assert g.allow_force_push is False
        assert g.allow_branch_delete is False
        assert g.protected_branches == ["main", "master"]


class TestShellPolicy:
    def test_defaults(self):
        s = ShellPolicy()
        assert s.allow_shell is True
        assert s.blocked_commands == []


class TestFileSystemPolicy:
    def test_defaults(self):
        f = FileSystemPolicy()
        assert f.allow_write is True
        assert f.allow_delete is False


class TestNetworkPolicy:
    def test_defaults(self):
        n = NetworkPolicy()
        assert n.allow_network is True


class TestSecretPolicy:
    def test_defaults(self):
        s = SecretPolicy()
        assert s.scan_for_secrets is True
        assert s.block_on_secret is True


class TestDestructiveOpsPolicy:
    def test_defaults(self):
        d = DestructiveOpsPolicy()
        assert d.allow_destructive is False
        assert d.require_confirmation is True


# ---------------------------------------------------------------------------
# SafetyConfig factories
# ---------------------------------------------------------------------------

class TestSafetyConfig:
    def test_baseline(self):
        sc = SafetyConfig.baseline_safety()
        assert sc.git.allow_force_push is False
        assert sc.filesystem.allow_delete is False
        assert sc.secrets.scan_for_secrets is True
        assert sc.destructive_ops.allow_destructive is False

    def test_permissive(self):
        sc = SafetyConfig.permissive_safety()
        assert sc.git.allow_force_push is True
        assert sc.git.allow_branch_delete is True
        assert sc.git.protected_branches == []
        assert sc.filesystem.allow_delete is True
        assert sc.secrets.scan_for_secrets is False
        assert sc.destructive_ops.allow_destructive is True
        assert sc.destructive_ops.require_confirmation is False

    def test_hardened(self):
        sc = SafetyConfig.hardened_safety()
        assert sc.git.allow_force_push is False
        assert sc.git.allow_branch_delete is False
        assert "release/*" in sc.git.protected_branches
        assert len(sc.shell.blocked_commands) > 0
        assert sc.filesystem.allow_delete is False
        assert sc.secrets.block_on_secret is True
        assert len(sc.secrets.secret_patterns) > 0
        assert sc.destructive_ops.allow_destructive is False

    def test_default_equals_baseline(self):
        default = SafetyConfig()
        baseline = SafetyConfig.baseline_safety()
        assert default.model_dump() == baseline.model_dump()


# ---------------------------------------------------------------------------
# GenerationOptions
# ---------------------------------------------------------------------------

class TestGenerationOptions:
    def test_defaults(self):
        g = GenerationOptions()
        assert g.seed_tasks is True
        assert g.seed_mode == SeedMode.DETAILED
        assert g.write_manifest is True
        assert g.write_diff_report is False

    def test_kickoff_mode(self):
        g = GenerationOptions(seed_mode="kickoff")
        assert g.seed_mode == SeedMode.KICKOFF


# ---------------------------------------------------------------------------
# CompositionSpec
# ---------------------------------------------------------------------------

class TestCompositionSpec:
    def test_minimal(self):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Test", slug="test"),
        )
        assert spec.project.name == "Test"
        assert spec.stacks == []
        assert spec.team.personas == []

    def test_full(self):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Full", slug="full"),
            stacks=[StackSelection(id="python", order=10)],
            team=TeamConfig(personas=[
                PersonaSelection(id="developer"),
            ]),
            hooks=HooksConfig(posture="hardened", packs=[
                HookPackSelection(id="pre-commit-lint"),
            ]),
            generation=GenerationOptions(seed_tasks=True, write_diff_report=True),
        )
        assert len(spec.stacks) == 1
        assert len(spec.team.personas) == 1
        assert spec.hooks.posture == Posture.HARDENED
        assert spec.generation.write_diff_report is True

    def test_with_safety(self):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Safe", slug="safe"),
            safety=SafetyConfig.hardened_safety(),
        )
        assert spec.safety is not None
        assert spec.safety.git.allow_force_push is False

    def test_safety_defaults_to_none(self):
        spec = CompositionSpec(
            project=ProjectIdentity(name="No Safety", slug="no-safety"),
        )
        assert spec.safety is None

    def test_serialization_roundtrip(self):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Round Trip", slug="round-trip"),
            stacks=[
                StackSelection(id="python", order=10),
                StackSelection(id="react", order=20),
            ],
            team=TeamConfig(personas=[
                PersonaSelection(id="team-lead", strictness="strict"),
                PersonaSelection(id="developer"),
            ]),
            hooks=HooksConfig(posture="hardened", packs=[
                HookPackSelection(id="security-scan", mode="enforcing"),
            ]),
            generation=GenerationOptions(
                seed_tasks=True, write_manifest=True, write_diff_report=True,
            ),
        )
        data = spec.model_dump(mode="json")
        restored = CompositionSpec.model_validate(data)
        assert restored.model_dump(mode="json") == data


# ---------------------------------------------------------------------------
# StageResult
# ---------------------------------------------------------------------------

class TestStageResult:
    def test_empty(self):
        sr = StageResult()
        assert sr.wrote == []
        assert sr.warnings == []

    def test_with_data(self):
        sr = StageResult(
            wrote=["CLAUDE.md", ".claude/agents/dev.md"],
            warnings=["Missing optional field"],
        )
        assert len(sr.wrote) == 2
        assert len(sr.warnings) == 1


# ---------------------------------------------------------------------------
# GenerationManifest
# ---------------------------------------------------------------------------

class TestGenerationManifest:
    def test_minimal(self):
        m = GenerationManifest(run_id="2026-02-07T10-00-00Z")
        assert m.run_id == "2026-02-07T10-00-00Z"
        assert m.stages == {}

    def test_total_files_written(self):
        m = GenerationManifest(
            run_id="test",
            stages={
                "scaffold": StageResult(wrote=["a.md", "b.md"]),
                "compile": StageResult(wrote=["c.md"]),
            },
        )
        assert m.total_files_written == 3

    def test_all_warnings(self):
        m = GenerationManifest(
            run_id="test",
            stages={
                "scaffold": StageResult(warnings=["w1"]),
                "compile": StageResult(warnings=["w2", "w3"]),
            },
        )
        assert m.all_warnings == ["w1", "w2", "w3"]

    def test_json_roundtrip(self):
        m = GenerationManifest(
            run_id="2026-02-07T10-00-00Z",
            library_version="abc1234",
            composition_snapshot={"project": {"name": "Test", "slug": "test"}},
            stages={
                "scaffold": StageResult(wrote=["CLAUDE.md"], warnings=[]),
                "compile": StageResult(wrote=["dev.md"], warnings=["missing stack"]),
            },
        )
        data = m.model_dump(mode="json")
        restored = GenerationManifest.model_validate(data)
        assert restored.run_id == m.run_id
        assert restored.total_files_written == 2
        assert len(restored.all_warnings) == 1


# ---------------------------------------------------------------------------
# FileAction / OverlayPlan
# ---------------------------------------------------------------------------

class TestFileAction:
    def test_create(self):
        fa = FileAction(path="CLAUDE.md", action="create", reason="New project")
        assert fa.action == FileActionType.CREATE

    def test_all_action_types(self):
        for action_type in FileActionType:
            fa = FileAction(path="test.md", action=action_type.value)
            assert fa.action == action_type

    def test_rejects_path_traversal(self):
        with pytest.raises(ValidationError, match="must not contain"):
            FileAction(path="../../../etc/passwd", action=FileActionType.CREATE)

    def test_rejects_embedded_dotdot(self):
        with pytest.raises(ValidationError, match="must not contain"):
            FileAction(path="foo/../../bar", action=FileActionType.CREATE)

    def test_rejects_absolute_path(self):
        with pytest.raises(ValidationError, match="must be relative"):
            FileAction(path="/etc/passwd", action=FileActionType.CREATE)

    def test_accepts_valid_relative_path(self):
        fa = FileAction(path="sub/dir/file.md", action=FileActionType.CREATE)
        assert fa.path == "sub/dir/file.md"

    def test_accepts_dotfile(self):
        fa = FileAction(path=".claude/settings.json", action=FileActionType.CREATE)
        assert fa.path == ".claude/settings.json"


class TestOverlayPlan:
    def test_empty(self):
        op = OverlayPlan()
        assert op.actions == []
        assert op.dry_run is False

    def test_filtered_properties(self):
        op = OverlayPlan(actions=[
            FileAction(path="new.md", action="create"),
            FileAction(path="old.md", action="update"),
            FileAction(path="removed.md", action="delete"),
            FileAction(path="unchanged.md", action="skip"),
            FileAction(path="another_new.md", action="create"),
        ])
        assert len(op.creates) == 2
        assert len(op.updates) == 1
        assert len(op.deletes) == 1
        assert len(op.skips) == 1


# ---------------------------------------------------------------------------
# LibraryIndex
# ---------------------------------------------------------------------------

class TestLibraryIndex:
    def _make_index(self):
        return LibraryIndex(
            library_root="/tmp/lib",
            personas=[
                PersonaInfo(id="developer", path="/tmp/lib/personas/developer",
                            has_persona_md=True, templates=["design-doc.md"]),
                PersonaInfo(id="tech-qa", path="/tmp/lib/personas/tech-qa",
                            has_persona_md=True, has_outputs_md=True),
            ],
            stacks=[
                StackInfo(id="python", path="/tmp/lib/stacks/python",
                          files=["conventions.md"]),
            ],
            hook_packs=[
                HookPackInfo(id="pre-commit-lint", path="/tmp/lib/hooks/pre-commit-lint",
                             files=["policy.md"]),
            ],
        )

    def test_persona_by_id_found(self):
        idx = self._make_index()
        p = idx.persona_by_id("developer")
        assert p is not None
        assert p.has_persona_md is True

    def test_persona_by_id_not_found(self):
        idx = self._make_index()
        assert idx.persona_by_id("nonexistent") is None

    def test_stack_by_id_found(self):
        idx = self._make_index()
        s = idx.stack_by_id("python")
        assert s is not None
        assert "conventions.md" in s.files

    def test_stack_by_id_not_found(self):
        idx = self._make_index()
        assert idx.stack_by_id("rust") is None

    def test_hook_pack_by_id_found(self):
        idx = self._make_index()
        h = idx.hook_pack_by_id("pre-commit-lint")
        assert h is not None

    def test_hook_pack_by_id_not_found(self):
        idx = self._make_index()
        assert idx.hook_pack_by_id("nope") is None


# ---------------------------------------------------------------------------
# Enum values
# ---------------------------------------------------------------------------

class TestEnums:
    def test_strictness_values(self):
        assert Strictness.LIGHT.value == "light"
        assert Strictness.STANDARD.value == "standard"
        assert Strictness.STRICT.value == "strict"

    def test_hook_mode_values(self):
        assert HookMode.ENFORCING.value == "enforcing"
        assert HookMode.PERMISSIVE.value == "permissive"
        assert HookMode.DISABLED.value == "disabled"

    def test_posture_values(self):
        assert Posture.BASELINE.value == "baseline"
        assert Posture.HARDENED.value == "hardened"
        assert Posture.REGULATED.value == "regulated"

    def test_seed_mode_values(self):
        assert SeedMode.DETAILED.value == "detailed"
        assert SeedMode.KICKOFF.value == "kickoff"

    def test_file_action_type_values(self):
        assert FileActionType.CREATE.value == "create"
        assert FileActionType.UPDATE.value == "update"
        assert FileActionType.DELETE.value == "delete"
        assert FileActionType.SKIP.value == "skip"
