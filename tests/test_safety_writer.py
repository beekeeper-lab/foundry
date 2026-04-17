"""Tests for foundry_app.services.safety_writer — native Claude Code hooks generation."""

import json
from pathlib import Path

from foundry_app.core.models import (
    ArchitectureConfig,
    CloudProvider,
    CompositionSpec,
    ExpertiseSelection,
    HookMode,
    HookPackSelection,
    HooksConfig,
    PersonaSelection,
    Posture,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.safety_writer import posture_base_packs, write_safety

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        expertise=[ExpertiseSelection(id="python")],
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

    def test_settings_has_hooks_key(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        data = _read_settings(tmp_path)
        assert "hooks" in data

    def test_hooks_has_pre_and_post(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        data = _read_settings(tmp_path)
        assert "PreToolUse" in data["hooks"]
        assert "PostToolUse" in data["hooks"]

    def test_output_dir_accepts_string(self, tmp_path: Path):
        result = write_safety(_make_spec(), str(tmp_path))
        assert len(result.wrote) == 1


# ---------------------------------------------------------------------------
# Hook entry format
# ---------------------------------------------------------------------------


class TestHookEntryFormat:

    def test_pre_tool_use_entry_has_matcher(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        entry = data["hooks"]["PreToolUse"][0]
        assert "matcher" in entry

    def test_pre_tool_use_entry_has_hooks_array(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        entry = data["hooks"]["PreToolUse"][0]
        assert isinstance(entry["hooks"], list)

    def test_hook_has_type_and_command(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        hook = data["hooks"]["PreToolUse"][0]["hooks"][0]
        assert hook["type"] == "command"
        assert "command" in hook
        assert len(hook["command"]) > 0


# ---------------------------------------------------------------------------
# Specific hook packs
# ---------------------------------------------------------------------------


class TestGitCommitBranch:

    def test_generates_pre_tool_use(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 1
        assert len(data["hooks"]["PostToolUse"]) == 0

    def test_matcher_targets_edit_write(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        matcher = data["hooks"]["PreToolUse"][0]["matcher"]
        assert "Edit" in matcher
        assert "Write" in matcher

    def test_command_checks_branch(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert "main" in command
        assert "master" in command
        assert "exit 1" in command


class TestPreCommitLint:

    def test_generates_post_tool_use(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="pre-commit-lint")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 0
        assert len(data["hooks"]["PostToolUse"]) == 1

    def test_command_runs_linter(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="pre-commit-lint")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        command = data["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        assert "ruff" in command


class TestSecurityScan:

    def test_generates_post_tool_use(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="security-scan")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PostToolUse"]) == 1

    def test_command_scans_for_secrets(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="security-scan")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        command = data["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        assert "secret" in command.lower() or "PRIVATE KEY" in command


class TestAzReadOnly:

    def test_generates_pre_tool_use_on_bash(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="az-read-only")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 1
        assert data["hooks"]["PreToolUse"][0]["matcher"] == "Bash"

    def test_command_blocks_mutations(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="az-read-only")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert "create" in command
        assert "delete" in command
        assert "exit 1" in command


# ---------------------------------------------------------------------------
# Posture defaults
# ---------------------------------------------------------------------------


class TestBaselinePosture:

    def test_baseline_has_branch_guard(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) >= 1
        matchers = [e["matcher"] for e in data["hooks"]["PreToolUse"]]
        assert any("Edit" in m for m in matchers)

    def test_baseline_has_lint_hook(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PostToolUse"]) >= 1
        commands = [
            h["command"]
            for e in data["hooks"]["PostToolUse"]
            for h in e["hooks"]
        ]
        assert any("ruff" in c for c in commands)


class TestHardenedPosture:

    def test_hardened_has_more_hooks_than_baseline(self, tmp_path: Path):
        baseline_spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        hardened_spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))

        write_safety(baseline_spec, tmp_path / "baseline")
        write_safety(hardened_spec, tmp_path / "hardened")

        baseline_data = _read_settings(tmp_path / "baseline")
        hardened_data = _read_settings(tmp_path / "hardened")

        baseline_count = (
            len(baseline_data["hooks"]["PreToolUse"])
            + len(baseline_data["hooks"]["PostToolUse"])
        )
        hardened_count = (
            len(hardened_data["hooks"]["PreToolUse"])
            + len(hardened_data["hooks"]["PostToolUse"])
        )
        assert hardened_count > baseline_count

    def test_hardened_includes_security_scan(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        all_commands = [
            h["command"]
            for key in ("PreToolUse", "PostToolUse")
            for e in data["hooks"][key]
            for h in e["hooks"]
        ]
        assert any("secret" in c.lower() or "PRIVATE KEY" in c for c in all_commands)


class TestRegulatedPosture:

    def test_regulated_has_most_hooks(self, tmp_path: Path):
        hardened_spec = _make_spec(hooks=HooksConfig(posture=Posture.HARDENED))
        regulated_spec = _make_spec(hooks=HooksConfig(posture=Posture.REGULATED))

        write_safety(hardened_spec, tmp_path / "hardened")
        write_safety(regulated_spec, tmp_path / "regulated")

        hardened_data = _read_settings(tmp_path / "hardened")
        regulated_data = _read_settings(tmp_path / "regulated")

        hardened_count = (
            len(hardened_data["hooks"]["PreToolUse"])
            + len(hardened_data["hooks"]["PostToolUse"])
        )
        regulated_count = (
            len(regulated_data["hooks"]["PreToolUse"])
            + len(regulated_data["hooks"]["PostToolUse"])
        )
        assert regulated_count > hardened_count

    def test_regulated_includes_compliance(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.REGULATED))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        all_commands = [
            h["command"]
            for key in ("PreToolUse", "PostToolUse")
            for e in data["hooks"][key]
            for h in e["hooks"]
        ]
        assert any("compliance" in c.lower() for c in all_commands)


# ---------------------------------------------------------------------------
# Pack selection behavior
# ---------------------------------------------------------------------------


class TestPackSelection:

    def test_explicit_packs_override_posture(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            posture=Posture.REGULATED,
            packs=[HookPackSelection(id="git-commit-branch")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        # Only one pack selected, so only its hooks appear
        assert len(data["hooks"]["PreToolUse"]) == 1
        assert len(data["hooks"]["PostToolUse"]) == 0

    def test_disabled_pack_produces_no_hooks(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[
                HookPackSelection(id="git-commit-branch", mode=HookMode.DISABLED),
            ],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 0
        assert len(data["hooks"]["PostToolUse"]) == 0

    def test_disabled_pack_not_enabled_produces_no_hooks(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[
                HookPackSelection(id="git-commit-branch", enabled=False),
            ],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 0
        assert len(data["hooks"]["PostToolUse"]) == 0

    def test_multiple_packs_combine(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[
                HookPackSelection(id="git-commit-branch"),
                HookPackSelection(id="pre-commit-lint"),
            ],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 1  # branch guard
        assert len(data["hooks"]["PostToolUse"]) == 1  # lint

    def test_no_packs_empty_posture_produces_baseline_defaults(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(posture=Posture.BASELINE))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        # Baseline defaults: git-commit-branch + pre-commit-lint
        assert len(data["hooks"]["PreToolUse"]) >= 1
        assert len(data["hooks"]["PostToolUse"]) >= 1

    def test_workflow_packs_produce_no_hooks(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[
                HookPackSelection(id="git-generate-pr"),
                HookPackSelection(id="git-merge-to-test"),
                HookPackSelection(id="git-merge-to-prod"),
            ],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 0
        assert len(data["hooks"]["PostToolUse"]) == 0


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
        assert "hooks" in data

    def test_json_is_pretty_printed(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        raw = (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
        assert "\n" in raw
        assert "  " in raw

    def test_json_ends_with_newline(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        raw = (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
        assert raw.endswith("\n")

    def test_no_safety_key_in_output(self, tmp_path: Path):
        write_safety(_make_spec(), tmp_path)
        data = _read_settings(tmp_path)
        assert "safety" not in data

    def test_unknown_pack_id_skipped(self, tmp_path: Path):
        spec = _make_spec(hooks=HooksConfig(
            packs=[HookPackSelection(id="nonexistent-pack")],
        ))
        write_safety(spec, tmp_path)
        data = _read_settings(tmp_path)
        assert len(data["hooks"]["PreToolUse"]) == 0
        assert len(data["hooks"]["PostToolUse"]) == 0


# ---------------------------------------------------------------------------
# Stack-aware selection — BEAN-255
# ---------------------------------------------------------------------------


def _all_commands(data: dict) -> list[str]:
    return [
        h["command"]
        for key in ("PreToolUse", "PostToolUse")
        for e in data["hooks"][key]
        for h in e["hooks"]
    ]


class TestStackAwareLintSelection:
    """Lint pack tracks the declared expertise, not a static default."""

    def test_python_stack_gets_ruff_not_eslint(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python")],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("ruff" in c for c in commands)
        assert not any("eslint" in c.lower() for c in commands)
        assert not any("prettier" in c.lower() for c in commands)
        assert not any("tsc" in c.lower() for c in commands)

    def test_react_typescript_stack_gets_eslint_prettier_tsc(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="react"),
                ExpertiseSelection(id="typescript"),
            ],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("eslint" in c.lower() for c in commands)
        assert any("prettier" in c.lower() for c in commands)
        assert any("tsc" in c.lower() for c in commands)
        assert not any("ruff" in c for c in commands)

    def test_node_only_stack_gets_js_lint(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="node")],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("eslint" in c.lower() for c in commands)
        assert not any("ruff" in c for c in commands)

    def test_mixed_python_and_typescript_gets_both_lints(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="python"),
                ExpertiseSelection(id="typescript"),
            ],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("ruff" in c for c in commands)
        assert any("eslint" in c.lower() for c in commands)

    def test_duplicate_js_expertises_add_pack_once(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="react"),
                ExpertiseSelection(id="typescript"),
                ExpertiseSelection(id="node"),
            ],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        # eslint should appear in one pack's command only
        eslint_hits = sum(1 for c in commands if "eslint" in c.lower())
        assert eslint_hits == 1

    def test_unmapped_expertise_adds_no_lint(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="clean-code")],
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert not any("ruff" in c for c in commands)
        assert not any("eslint" in c.lower() for c in commands)


class TestStackAwareCloudSelection:
    """Cloud hooks only appear for declared providers, and only above baseline."""

    def test_no_cloud_no_cloud_hooks_at_baseline(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[]),
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert not any("az " in c or "'az" in c for c in commands)
        assert not any("aws " in c or "'aws" in c for c in commands)

    def test_no_cloud_no_cloud_hooks_at_hardened(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[]),
            hooks=HooksConfig(posture=Posture.HARDENED),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert not any("az\\s" in c for c in commands)
        assert not any("aws\\s" in c for c in commands)

    def test_aws_hardened_gets_aws_hook_not_azure(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[CloudProvider.AWS]),
            hooks=HooksConfig(posture=Posture.HARDENED),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("aws\\s" in c for c in commands)
        assert not any("az\\s" in c for c in commands)

    def test_azure_hardened_gets_azure_hook_not_aws(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[CloudProvider.AZURE]),
            hooks=HooksConfig(posture=Posture.HARDENED),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("az\\s" in c for c in commands)
        assert not any("aws\\s" in c for c in commands)

    def test_aws_baseline_gets_no_cloud_hook(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[CloudProvider.AWS]),
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert not any("aws\\s" in c for c in commands)

    def test_both_clouds_regulated_gets_both_hooks(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(
                cloud_providers=[CloudProvider.AWS, CloudProvider.AZURE],
            ),
            hooks=HooksConfig(posture=Posture.REGULATED),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("aws\\s" in c for c in commands)
        assert any("az\\s" in c for c in commands)


class TestStackMismatchWarnings:
    """Explicit pack selections that don't match the stack produce warnings."""

    def test_ruff_on_typescript_project_warns(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id="react"),
                ExpertiseSelection(id="typescript"),
            ],
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = write_safety(spec, tmp_path)
        assert any("pre-commit-lint" in w and "python" in w for w in result.warnings)
        # Pack still written (backward compatibility)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("ruff" in c for c in commands)

    def test_eslint_on_python_project_warns(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python")],
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint-js")]),
        )
        result = write_safety(spec, tmp_path)
        assert any("pre-commit-lint-js" in w and "js" in w for w in result.warnings)

    def test_azure_hook_without_azure_provider_warns(self, tmp_path: Path):
        spec = _make_spec(
            architecture=ArchitectureConfig(cloud_providers=[CloudProvider.AWS]),
            hooks=HooksConfig(packs=[HookPackSelection(id="az-limited-ops")]),
        )
        result = write_safety(spec, tmp_path)
        assert any("az-limited-ops" in w and "azure" in w for w in result.warnings)

    def test_matched_explicit_pack_produces_no_warning(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="python")],
            hooks=HooksConfig(packs=[HookPackSelection(id="pre-commit-lint")]),
        )
        result = write_safety(spec, tmp_path)
        assert result.warnings == []

    def test_stack_aware_defaults_never_warn(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id="react")],
            hooks=HooksConfig(posture=Posture.HARDENED),
            architecture=ArchitectureConfig(cloud_providers=[CloudProvider.AWS]),
        )
        result = write_safety(spec, tmp_path)
        assert result.warnings == []


class TestStackAwareEndToEnd:
    """Full-composition scenarios from the bean's acceptance criteria."""

    def test_small_python_team_yields_ruff_no_azure(self, tmp_path: Path):
        """Regenerating examples/small-python-team.yml shape."""
        spec = CompositionSpec(
            project=ProjectIdentity(name="Small Python Team", slug="small-python-team"),
            expertise=[
                ExpertiseSelection(id="python", order=10),
                ExpertiseSelection(id="clean-code", order=20),
            ],
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("ruff" in c for c in commands)
        assert not any("eslint" in c.lower() for c in commands)
        assert not any("az\\s" in c for c in commands)
        assert not any("aws\\s" in c for c in commands)

    def test_react_ts_composition_yields_js_lint_no_ruff(self, tmp_path: Path):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Web App", slug="web-app"),
            expertise=[
                ExpertiseSelection(id="react", order=10),
                ExpertiseSelection(id="typescript", order=20),
                ExpertiseSelection(id="node", order=30),
            ],
            team=TeamConfig(personas=[PersonaSelection(id="developer")]),
            hooks=HooksConfig(posture=Posture.BASELINE),
        )
        write_safety(spec, tmp_path)
        commands = _all_commands(_read_settings(tmp_path))
        assert any("eslint" in c.lower() for c in commands)
        assert any("prettier" in c.lower() for c in commands)
        assert any("tsc" in c.lower() for c in commands)
        assert not any("ruff" in c for c in commands)


# ---------------------------------------------------------------------------
# Posture taxonomy lock-in — mirrors ai/context/hook-posture.md
# ---------------------------------------------------------------------------


class TestPostureTaxonomy:
    """Lock-in test for the posture → base pack mapping.

    If this test fails, the posture base packs changed. Update
    `ai/context/hook-posture.md` (and the summary table in
    `ai/context/hook-selection.md`) together with the mapping change, then
    update this test. See ADR-006 in ai/context/decisions.md.
    """

    def test_baseline_base_packs(self):
        assert posture_base_packs(Posture.BASELINE) == ["git-commit-branch"]

    def test_hardened_base_packs(self):
        assert posture_base_packs(Posture.HARDENED) == [
            "git-commit-branch",
            "git-push-feature",
            "security-scan",
        ]

    def test_regulated_base_packs(self):
        assert posture_base_packs(Posture.REGULATED) == [
            "git-commit-branch",
            "git-push-feature",
            "security-scan",
            "compliance-gate",
            "post-task-qa",
        ]

    def test_baseline_count_is_less_than_hardened(self):
        """The taxonomy ordering: baseline ⊂ hardened ⊂ regulated by pack count."""
        assert len(posture_base_packs(Posture.BASELINE)) < len(
            posture_base_packs(Posture.HARDENED)
        )
        assert len(posture_base_packs(Posture.HARDENED)) < len(
            posture_base_packs(Posture.REGULATED)
        )

    def test_hardened_is_superset_of_baseline(self):
        """Every baseline pack appears in hardened and regulated."""
        baseline = set(posture_base_packs(Posture.BASELINE))
        assert baseline.issubset(set(posture_base_packs(Posture.HARDENED)))
        assert baseline.issubset(set(posture_base_packs(Posture.REGULATED)))

    def test_regulated_is_superset_of_hardened(self):
        hardened = set(posture_base_packs(Posture.HARDENED))
        assert hardened.issubset(set(posture_base_packs(Posture.REGULATED)))

    def test_returned_list_is_fresh_copy(self):
        """Mutating the returned list must not affect the internal mapping."""
        first = posture_base_packs(Posture.BASELINE)
        first.append("rogue-pack")
        second = posture_base_packs(Posture.BASELINE)
        assert second == ["git-commit-branch"]
