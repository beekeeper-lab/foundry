"""Asset copier: copy skills, commands, and hook docs from the library into a generated project."""

from __future__ import annotations

import shutil
from pathlib import Path

from foundry_app.core.models import HooksConfig, StageResult

# Skills that every project gets regardless of persona selection
_CORE_SKILLS = [
    "compile-team",
    "seed-tasks",
    "new-work",
    "handoff",
    "close-loop",
    "validate-config",
    "validate-repo",
]

# Commands that every project gets regardless of persona selection
_CORE_COMMANDS = [
    "compile-team",
    "seed-tasks",
    "new-work",
    "handoff",
    "status-report",
    "validate-config",
    "validate-repo",
]

# Persona-specific additional skills
_PERSONA_SKILLS: dict[str, list[str]] = {
    "architect": ["new-adr", "new-dev-decision", "scaffold-project"],
    "developer": ["new-dev-decision", "review-pr"],
    "ba": ["notes-to-stories"],
    "tech-qa": ["build-traceability"],
    "security-engineer": ["threat-model"],
    "technical-writer": ["update-docs"],
    "devops-release": ["release-notes"],
}

# Persona-specific additional commands
_PERSONA_COMMANDS: dict[str, list[str]] = {
    "architect": ["new-adr", "new-dev-decision", "scaffold-project"],
    "developer": ["new-dev-decision", "review-pr"],
    "ba": ["notes-to-stories"],
    "tech-qa": ["build-traceability"],
    "security-engineer": ["threat-model"],
    "technical-writer": ["update-docs"],
    "devops-release": ["release-notes"],
}


def copy_skills(
    library_root: Path,
    project_dir: Path,
    persona_ids: list[str],
) -> StageResult:
    """Copy skill directories from the library into the project's .claude/skills/.

    Copies core skills plus persona-relevant skills. Skills that don't exist
    in the library are silently skipped.
    """
    result = StageResult()
    skills_src = library_root / "claude" / "skills"
    skills_dst = project_dir / ".claude" / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)

    # Build the full set of skill IDs to copy
    skill_ids = set(_CORE_SKILLS)
    for pid in persona_ids:
        skill_ids.update(_PERSONA_SKILLS.get(pid, []))

    for skill_id in sorted(skill_ids):
        src_dir = skills_src / skill_id
        if not src_dir.is_dir():
            continue
        dst_dir = skills_dst / skill_id
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        # Record all copied files
        for f in sorted(dst_dir.rglob("*")):
            if f.is_file():
                result.wrote.append(str(f.relative_to(project_dir)))

    return result


def copy_commands(
    library_root: Path,
    project_dir: Path,
    persona_ids: list[str],
) -> StageResult:
    """Copy command files from the library into the project's .claude/commands/.

    Copies core commands plus persona-relevant commands. Commands that don't
    exist in the library are silently skipped.
    """
    result = StageResult()
    commands_src = library_root / "claude" / "commands"
    commands_dst = project_dir / ".claude" / "commands"
    commands_dst.mkdir(parents=True, exist_ok=True)

    # Build the full set of command IDs to copy
    command_ids = set(_CORE_COMMANDS)
    for pid in persona_ids:
        command_ids.update(_PERSONA_COMMANDS.get(pid, []))

    for cmd_id in sorted(command_ids):
        src_file = commands_src / f"{cmd_id}.md"
        if not src_file.is_file():
            continue
        dst_file = commands_dst / f"{cmd_id}.md"
        shutil.copy2(src_file, dst_file)
        result.wrote.append(str(dst_file.relative_to(project_dir)))

    return result


def write_hooks_config(
    library_root: Path,
    project_dir: Path,
    hooks_config: HooksConfig,
) -> StageResult:
    """Copy enabled hook pack documentation into the project's .claude/hooks/.

    Copies the markdown doc for each enabled hook pack from the library.
    """
    result = StageResult()
    hooks_src = library_root / "claude" / "hooks"
    hooks_dst = project_dir / ".claude" / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)

    for pack in hooks_config.packs:
        if not pack.enabled:
            continue
        src_file = hooks_src / f"{pack.id}.md"
        if not src_file.is_file():
            result.warnings.append(f"Hook pack not found in library: {pack.id}")
            continue
        dst_file = hooks_dst / f"{pack.id}.md"
        shutil.copy2(src_file, dst_file)
        result.wrote.append(str(dst_file.relative_to(project_dir)))

    # Always copy the hook-policy.md if it exists
    policy_src = hooks_src / "hook-policy.md"
    if policy_src.is_file():
        policy_dst = hooks_dst / "hook-policy.md"
        if not policy_dst.exists():
            shutil.copy2(policy_src, policy_dst)
            result.wrote.append(str(policy_dst.relative_to(project_dir)))

    return result
