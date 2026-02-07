"""Safety service: convert SafetyConfig into settings.local.json and policy docs."""

from __future__ import annotations

import json
from pathlib import Path

from foundry_app.core.models import (
    DestructiveOpsPolicy,
    FileSystemPolicy,
    GitPolicy,
    NetworkPolicy,
    SafetyConfig,
    SecretPolicy,
    ShellPolicy,
    StageResult,
)


def safety_to_settings_json(safety: SafetyConfig) -> dict:
    """Convert a SafetyConfig into a Claude Code settings.local.json dict.

    Returns a dict with a ``permissions`` block containing ``allow``,
    ``deny``, and ``defaultMode`` keys.
    """
    allow: list[str] = []
    deny: list[str] = []

    # --- Git policy ---
    if safety.git.allow_push:
        allow.append("Bash(git push *)")
    else:
        deny.append("Bash(git push *)")

    if not safety.git.allow_force_push:
        deny.append("Bash(git push --force *)")
        deny.append("Bash(git push -f *)")

    if not safety.git.allow_branch_delete:
        deny.append("Bash(git branch -D *)")
        deny.append("Bash(git branch -d *)")

    # --- Shell policy ---
    if not safety.shell.allow_sudo:
        deny.append("Bash(sudo *)")

    if not safety.shell.allow_install:
        deny.append("Bash(pip install *)")
        deny.append("Bash(npm install -g *)")
        deny.append("Bash(apt install *)")

    for pattern in safety.shell.deny_patterns:
        deny.append(f"Bash({pattern})")

    # --- Filesystem policy ---
    allow.append("Read(**)")
    allow.append("Edit(src/**)")
    allow.append("Edit(tests/**)")
    allow.append("Edit(ai/**)")

    if not safety.filesystem.allow_outside_project:
        deny.append("Read(/etc/**)")
        deny.append("Edit(/etc/**)")

    for pattern in safety.filesystem.deny_patterns:
        deny.append(f"Edit({pattern})")

    # --- Network policy ---
    if not safety.network.allow_network:
        deny.append("Bash(curl *)")
        deny.append("Bash(wget *)")

    # --- Secrets policy ---
    if safety.secrets.block_env_files:
        deny.append("Read(.env)")
        deny.append("Read(.env.*)")
        deny.append("Edit(.env)")
        deny.append("Edit(.env.*)")

    if safety.secrets.block_credentials:
        deny.append("Read(**/credentials*)")
        deny.append("Read(**/secrets*)")
        deny.append("Edit(**/credentials*)")
        deny.append("Edit(**/secrets*)")

    # --- Destructive ops policy ---
    if not safety.destructive.allow_rm_rf:
        deny.append("Bash(rm -rf *)")
        deny.append("Bash(rm -r *)")

    if not safety.destructive.allow_reset_hard:
        deny.append("Bash(git reset --hard *)")

    if not safety.destructive.allow_clean:
        deny.append("Bash(git clean -f *)")
        deny.append("Bash(git clean -fd *)")

    # Determine default mode based on preset
    if safety.preset == "permissive":
        default_mode = "auto"
    elif safety.preset == "hardened":
        default_mode = "askEveryTime"
    else:
        default_mode = "acceptEdits"

    return {
        "permissions": {
            "allow": allow,
            "deny": deny,
            "defaultMode": default_mode,
        }
    }


def safety_to_policy_docs(
    safety: SafetyConfig, project_name: str
) -> dict[str, str]:
    """Generate markdown policy documents from a SafetyConfig.

    Returns a dict mapping filename to markdown content.
    """
    docs: dict[str, str] = {}

    # --- Main safety policy ---
    docs["safety-policy.md"] = _build_safety_policy(safety, project_name)
    docs["git-policy.md"] = _build_git_policy(safety.git)
    docs["shell-policy.md"] = _build_shell_policy(safety.shell, safety.destructive)

    return docs


def write_safety_files(
    safety: SafetyConfig,
    project_name: str,
    project_dir: Path,
) -> StageResult:
    """Write settings.local.json and policy docs into the project directory."""
    result = StageResult()

    # Write settings.local.json
    settings_dict = safety_to_settings_json(safety)
    settings_path = project_dir / ".claude" / "settings.local.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings_dict, indent=2) + "\n")
    result.wrote.append(str(settings_path.relative_to(project_dir)))

    # Write policy docs
    policy_docs = safety_to_policy_docs(safety, project_name)
    context_dir = project_dir / "ai" / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in policy_docs.items():
        path = context_dir / filename
        path.write_text(content)
        result.wrote.append(str(path.relative_to(project_dir)))

    return result


# --- Presets ---


def permissive_safety() -> SafetyConfig:
    """Fully open safety config — minimal restrictions."""
    return SafetyConfig(
        preset="permissive",
        git=GitPolicy(allow_push=True, allow_force_push=True, allow_branch_delete=True),
        shell=ShellPolicy(allow_sudo=True, allow_install=True),
        filesystem=FileSystemPolicy(allow_outside_project=True),
        network=NetworkPolicy(allow_network=True, allow_external_apis=True),
        secrets=SecretPolicy(block_env_files=False, block_credentials=False),
        destructive=DestructiveOpsPolicy(
            allow_rm_rf=True, allow_reset_hard=True, allow_clean=True,
        ),
    )


def baseline_safety() -> SafetyConfig:
    """Sensible defaults — blocks dangerous ops, allows normal development."""
    return SafetyConfig(
        preset="baseline",
        git=GitPolicy(
            allow_push=True, allow_force_push=False,
            allow_branch_delete=False,
        ),
        shell=ShellPolicy(allow_sudo=False, allow_install=True),
        filesystem=FileSystemPolicy(allow_outside_project=False),
        network=NetworkPolicy(allow_network=True, allow_external_apis=True),
        secrets=SecretPolicy(block_env_files=True, block_credentials=True),
        destructive=DestructiveOpsPolicy(
            allow_rm_rf=False, allow_reset_hard=False, allow_clean=False,
        ),
    )


def hardened_safety() -> SafetyConfig:
    """Strict safety config — maximum guardrails."""
    return SafetyConfig(
        preset="hardened",
        git=GitPolicy(
            allow_push=False, allow_force_push=False,
            allow_branch_delete=False,
        ),
        shell=ShellPolicy(allow_sudo=False, allow_install=False),
        filesystem=FileSystemPolicy(allow_outside_project=False),
        network=NetworkPolicy(
            allow_network=False, allow_external_apis=False,
        ),
        secrets=SecretPolicy(block_env_files=True, block_credentials=True),
        destructive=DestructiveOpsPolicy(
            allow_rm_rf=False, allow_reset_hard=False, allow_clean=False,
        ),
    )


# --- Internal helpers ---


def _build_safety_policy(safety: SafetyConfig, project_name: str) -> str:
    """Build the main safety-policy.md document."""
    lines = [
        f"# Safety Policy: {project_name}",
        "",
        f"> Preset: **{safety.preset}**",
        "",
        "This document describes the safety guardrails configured for this project.",
        "These rules are enforced via `.claude/settings.local.json` and should be",
        "followed by all agents working in this project.",
        "",
        "## Summary",
        "",
    ]

    if safety.preset == "permissive":
        lines.append(
            "This project uses a **permissive** safety posture. "
            "Most operations are allowed."
        )
    elif safety.preset == "hardened":
        lines.append(
            "This project uses a **hardened** safety posture. "
            "Operations are restricted by default."
        )
    else:
        lines.append(
            "This project uses a **baseline** safety posture. "
            "Dangerous operations are blocked."
        )

    lines.extend([
        "",
        "## Policies",
        "",
        f"- **Git:** push={'yes' if safety.git.allow_push else 'no'}, "
        f"force-push={'yes' if safety.git.allow_force_push else 'no'}, "
        f"branch-delete={'yes' if safety.git.allow_branch_delete else 'no'}",
        f"- **Shell:** sudo={'yes' if safety.shell.allow_sudo else 'no'}, "
        f"install={'yes' if safety.shell.allow_install else 'no'}",
        "- **Filesystem:** outside-project="
        f"{'yes' if safety.filesystem.allow_outside_project else 'no'}",
        f"- **Network:** network={'yes' if safety.network.allow_network else 'no'}, "
        f"external-apis={'yes' if safety.network.allow_external_apis else 'no'}",
        f"- **Secrets:** block-env={'yes' if safety.secrets.block_env_files else 'no'}, "
        f"block-credentials={'yes' if safety.secrets.block_credentials else 'no'}",
        f"- **Destructive:** rm-rf={'yes' if safety.destructive.allow_rm_rf else 'no'}, "
        f"reset-hard={'yes' if safety.destructive.allow_reset_hard else 'no'}, "
        f"clean={'yes' if safety.destructive.allow_clean else 'no'}",
        "",
        "See `git-policy.md` and `shell-policy.md` for detailed rules.",
        "",
    ])
    return "\n".join(lines)


def _build_git_policy(git: GitPolicy) -> str:
    """Build the git-policy.md document."""
    lines = [
        "# Git Policy",
        "",
        "## Rules",
        "",
    ]
    if git.allow_push:
        lines.append("- `git push` is **allowed** to remote branches.")
    else:
        lines.append("- `git push` is **denied**. Use PRs or request manual push.")

    if git.allow_force_push:
        lines.append("- `git push --force` is **allowed** (use with caution).")
    else:
        lines.append("- `git push --force` is **denied**. Never force-push.")

    if git.allow_branch_delete:
        lines.append("- `git branch -D` is **allowed** for cleanup.")
    else:
        lines.append("- `git branch -D` is **denied**. Branches are preserved.")

    lines.append("")
    return "\n".join(lines)


def _build_shell_policy(shell: ShellPolicy, destructive: DestructiveOpsPolicy) -> str:
    """Build the shell-policy.md document."""
    lines = [
        "# Shell Policy",
        "",
        "## Rules",
        "",
    ]
    if shell.allow_sudo:
        lines.append("- `sudo` is **allowed**.")
    else:
        lines.append("- `sudo` is **denied**. No elevated privileges.")

    if shell.allow_install:
        lines.append("- Package installation (`pip install`, `npm install`) is **allowed**.")
    else:
        lines.append("- Package installation is **denied**. Use pre-approved dependencies only.")

    if not destructive.allow_rm_rf:
        lines.append("- `rm -rf` is **denied**. Use targeted file removal only.")

    if not destructive.allow_reset_hard:
        lines.append("- `git reset --hard` is **denied**. Preserve working tree state.")

    if shell.deny_patterns:
        lines.append("")
        lines.append("## Additional Denied Patterns")
        lines.append("")
        for pattern in shell.deny_patterns:
            lines.append(f"- `{pattern}`")

    lines.append("")
    return "\n".join(lines)
