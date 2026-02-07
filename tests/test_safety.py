"""Tests for foundry_app.services.safety: SafetyConfig conversion and presets."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    DestructiveOpsPolicy,
    FileSystemPolicy,
    GitPolicy,
    NetworkPolicy,
    SafetyConfig,
    SecretPolicy,
    ShellPolicy,
)
from foundry_app.services.safety import (
    baseline_safety,
    hardened_safety,
    permissive_safety,
    safety_to_policy_docs,
    safety_to_settings_json,
    write_safety_files,
)

# -- safety_to_settings_json --------------------------------------------------


def test_baseline_settings_json_denies_force_push():
    """Baseline preset should deny git push --force."""
    config = baseline_safety()
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(git push --force *)" in deny
    assert "Bash(git push -f *)" in deny


def test_baseline_settings_json_allows_push():
    """Baseline preset should allow git push."""
    config = baseline_safety()
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Bash(git push *)" in allow


def test_baseline_settings_json_denies_sudo():
    """Baseline preset should deny sudo."""
    config = baseline_safety()
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(sudo *)" in deny


def test_baseline_settings_json_denies_rm_rf():
    """Baseline preset should deny rm -rf."""
    config = baseline_safety()
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(rm -rf *)" in deny


def test_permissive_settings_json_has_no_key_denials():
    """Permissive preset should not deny common ops."""
    config = permissive_safety()
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(sudo *)" not in deny
    assert "Bash(rm -rf *)" not in deny
    assert "Bash(git push --force *)" not in deny


def test_permissive_default_mode_is_auto():
    """Permissive preset should use 'auto' default mode."""
    config = permissive_safety()
    result = safety_to_settings_json(config)
    assert result["permissions"]["defaultMode"] == "auto"


def test_hardened_default_mode_is_ask_every_time():
    """Hardened preset should use 'askEveryTime' default mode."""
    config = hardened_safety()
    result = safety_to_settings_json(config)
    assert result["permissions"]["defaultMode"] == "askEveryTime"


def test_baseline_default_mode_is_accept_edits():
    """Baseline preset should use 'acceptEdits' default mode."""
    config = baseline_safety()
    result = safety_to_settings_json(config)
    assert result["permissions"]["defaultMode"] == "acceptEdits"


def test_hardened_denies_push():
    """Hardened preset should deny git push entirely."""
    config = hardened_safety()
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(git push *)" in deny


def test_custom_shell_deny_patterns():
    """Custom deny_patterns in ShellPolicy should appear in deny list."""
    config = SafetyConfig(
        shell=ShellPolicy(deny_patterns=["docker rm *", "kill -9 *"])
    )
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(docker rm *)" in deny
    assert "Bash(kill -9 *)" in deny


def test_secrets_block_env_files():
    """When block_env_files is True, .env patterns should be denied."""
    config = SafetyConfig(secrets=SecretPolicy(block_env_files=True))
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Read(.env)" in deny
    assert "Edit(.env)" in deny


def test_secrets_unblocked_env_files():
    """When block_env_files is False, .env patterns should not be denied."""
    config = SafetyConfig(secrets=SecretPolicy(block_env_files=False))
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Read(.env)" not in deny


def test_network_denied():
    """When allow_network is False, curl and wget should be denied."""
    config = SafetyConfig(network=NetworkPolicy(allow_network=False))
    result = safety_to_settings_json(config)

    deny = result["permissions"]["deny"]
    assert "Bash(curl *)" in deny
    assert "Bash(wget *)" in deny


# -- safety_to_policy_docs -----------------------------------------------------


def test_policy_docs_returns_three_files():
    """safety_to_policy_docs should return safety-policy, git-policy, shell-policy."""
    config = baseline_safety()
    docs = safety_to_policy_docs(config, "Test Project")

    assert "safety-policy.md" in docs
    assert "git-policy.md" in docs
    assert "shell-policy.md" in docs


def test_safety_policy_contains_project_name():
    """safety-policy.md should contain the project name."""
    config = baseline_safety()
    docs = safety_to_policy_docs(config, "My Project")

    assert "My Project" in docs["safety-policy.md"]


def test_safety_policy_contains_preset():
    """safety-policy.md should mention the preset name."""
    config = hardened_safety()
    docs = safety_to_policy_docs(config, "Test")

    assert "hardened" in docs["safety-policy.md"]


def test_git_policy_reflects_config():
    """git-policy.md should reflect allow/deny for push operations."""
    config = SafetyConfig(git=GitPolicy(allow_push=False))
    docs = safety_to_policy_docs(config, "Test")

    assert "denied" in docs["git-policy.md"].lower()


def test_shell_policy_reflects_destructive_ops():
    """shell-policy.md should mention denied destructive ops."""
    config = SafetyConfig(
        destructive=DestructiveOpsPolicy(allow_rm_rf=False)
    )
    docs = safety_to_policy_docs(config, "Test")

    assert "rm -rf" in docs["shell-policy.md"]


# -- Presets -------------------------------------------------------------------


def test_permissive_preset_is_fully_open():
    """permissive_safety() should allow everything."""
    config = permissive_safety()
    assert config.preset == "permissive"
    assert config.git.allow_push is True
    assert config.git.allow_force_push is True
    assert config.shell.allow_sudo is True
    assert config.destructive.allow_rm_rf is True
    assert config.secrets.block_env_files is False


def test_baseline_preset_blocks_dangerous():
    """baseline_safety() should block force-push, sudo, rm-rf."""
    config = baseline_safety()
    assert config.preset == "baseline"
    assert config.git.allow_push is True
    assert config.git.allow_force_push is False
    assert config.shell.allow_sudo is False
    assert config.destructive.allow_rm_rf is False
    assert config.secrets.block_env_files is True


def test_hardened_preset_blocks_everything():
    """hardened_safety() should block push, install, network."""
    config = hardened_safety()
    assert config.preset == "hardened"
    assert config.git.allow_push is False
    assert config.shell.allow_install is False
    assert config.network.allow_network is False


# -- write_safety_files --------------------------------------------------------


def test_write_safety_files_creates_settings_json(tmp_path: Path):
    """write_safety_files should create .claude/settings.local.json."""
    config = baseline_safety()
    result = write_safety_files(config, "Test", tmp_path)

    settings_path = tmp_path / ".claude" / "settings.local.json"
    assert settings_path.is_file()
    assert ".claude/settings.local.json" in result.wrote


def test_write_safety_files_creates_policy_docs(tmp_path: Path):
    """write_safety_files should create policy docs in ai/context/."""
    config = baseline_safety()
    result = write_safety_files(config, "Test", tmp_path)

    assert (tmp_path / "ai" / "context" / "safety-policy.md").is_file()
    assert (tmp_path / "ai" / "context" / "git-policy.md").is_file()
    assert (tmp_path / "ai" / "context" / "shell-policy.md").is_file()
    assert "ai/context/safety-policy.md" in result.wrote


def test_write_safety_files_settings_json_is_valid_json(tmp_path: Path):
    """The written settings.local.json should be valid JSON."""
    import json

    config = baseline_safety()
    write_safety_files(config, "Test", tmp_path)

    settings_path = tmp_path / ".claude" / "settings.local.json"
    data = json.loads(settings_path.read_text())
    assert "permissions" in data
    assert "deny" in data["permissions"]
    assert "allow" in data["permissions"]


# -- editable_dirs -------------------------------------------------------------


def test_default_editable_dirs_produces_standard_rules():
    """Default editable_dirs should produce Edit(src/**), Edit(tests/**), Edit(ai/**)."""
    config = SafetyConfig()
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Edit(src/**)" in allow
    assert "Edit(tests/**)" in allow
    assert "Edit(ai/**)" in allow


def test_custom_editable_dirs_single():
    """A single custom editable dir should produce one Edit() rule."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["foundry_app/**"])
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Edit(foundry_app/**)" in allow
    assert "Edit(src/**)" not in allow
    assert "Edit(tests/**)" not in allow


def test_custom_editable_dirs_multiple():
    """Multiple custom dirs should each produce an Edit() rule."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(
            editable_dirs=["app/**", "lib/**", "scripts/**"]
        )
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Edit(app/**)" in allow
    assert "Edit(lib/**)" in allow
    assert "Edit(scripts/**)" in allow
    assert len([r for r in allow if r.startswith("Edit(")]) == 3


def test_empty_editable_dirs_no_edit_rules():
    """Empty editable_dirs list should produce no Edit() rules."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=[])
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    edit_rules = [r for r in allow if r.startswith("Edit(")]
    assert edit_rules == []
    # Read(**) should still be present
    assert "Read(**)" in allow


def test_editable_dirs_strips_whitespace():
    """Entries with whitespace should be stripped."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["  src/**  ", " tests/** "])
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Edit(src/**)" in allow
    assert "Edit(tests/**)" in allow


def test_editable_dirs_skips_empty_entries():
    """Empty strings in the list should be skipped."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["src/**", "", "  ", "tests/**"])
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    edit_rules = [r for r in allow if r.startswith("Edit(")]
    assert len(edit_rules) == 2
    assert "Edit(src/**)" in allow
    assert "Edit(tests/**)" in allow


def test_preset_functions_get_default_editable_dirs():
    """Preset functions should produce default editable_dirs."""
    for preset_fn in (baseline_safety, hardened_safety, permissive_safety):
        config = preset_fn()
        assert config.filesystem.editable_dirs == ["src/**", "tests/**", "ai/**"]


def test_filesystem_policy_default_editable_dirs():
    """FileSystemPolicy default should be ['src/**', 'tests/**', 'ai/**']."""
    policy = FileSystemPolicy()
    assert policy.editable_dirs == ["src/**", "tests/**", "ai/**"]


def test_editable_dirs_yaml_round_trip():
    """editable_dirs should survive YAML serialization round-trip."""
    import yaml

    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["foundry_app/**", "tests/**"])
    )
    yaml_str = yaml.dump(config.model_dump(), default_flow_style=False)
    loaded = yaml.safe_load(yaml_str)
    restored = SafetyConfig(**loaded)
    assert restored.filesystem.editable_dirs == ["foundry_app/**", "tests/**"]


def test_old_config_without_editable_dirs_gets_default():
    """A SafetyConfig dict missing editable_dirs should get the default."""
    old_data = {
        "preset": "baseline",
        "filesystem": {"allow_outside_project": False, "deny_patterns": []},
    }
    config = SafetyConfig(**old_data)
    assert config.filesystem.editable_dirs == ["src/**", "tests/**", "ai/**"]


def test_editable_dirs_without_glob_accepted():
    """A bare directory name without glob pattern is accepted as-is."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["src"])
    )
    result = safety_to_settings_json(config)

    allow = result["permissions"]["allow"]
    assert "Edit(src)" in allow


def test_editable_dirs_read_rule_always_present():
    """Read(**) is always present regardless of editable_dirs."""
    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=[])
    )
    result = safety_to_settings_json(config)
    assert "Read(**)" in result["permissions"]["allow"]


def test_write_safety_files_custom_dirs_in_json(tmp_path: Path):
    """Custom editable_dirs should appear in the written settings.local.json."""
    import json

    config = SafetyConfig(
        filesystem=FileSystemPolicy(editable_dirs=["foundry_app/**", "tests/**"])
    )
    write_safety_files(config, "Foundry", tmp_path)

    settings_path = tmp_path / ".claude" / "settings.local.json"
    data = json.loads(settings_path.read_text())
    allow = data["permissions"]["allow"]
    assert "Edit(foundry_app/**)" in allow
    assert "Edit(tests/**)" in allow
    assert "Edit(src/**)" not in allow
