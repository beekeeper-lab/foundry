"""Seeder service — generates starter task files in a generated project."""

from __future__ import annotations

import logging
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    SeedMode,
    StageResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Seed templates per persona role
# ---------------------------------------------------------------------------

_DETAILED_TASKS: dict[str, list[str]] = {
    "team-lead": [
        "Review project composition and verify all generated outputs",
        "Create initial bean backlog from project requirements",
        "Assign team roles and establish communication patterns",
    ],
    "ba": [
        "Gather and document initial project requirements",
        "Define user stories and acceptance criteria for first milestone",
        "Create domain glossary and business rules document",
    ],
    "architect": [
        "Review generated architecture and validate patterns",
        "Document system boundaries and integration points",
        "Create initial ADR for technology stack decisions",
    ],
    "developer": [
        "Set up local development environment and verify build",
        "Implement core module skeleton based on architecture",
        "Write initial unit tests for core data models",
    ],
    "tech-qa": [
        "Create test plan template for the project",
        "Set up CI test pipeline configuration",
        "Define quality gates and coverage thresholds",
    ],
    "code-quality-reviewer": [
        "Define code review standards and style guidelines",
        "Create pull request review checklist template",
        "Establish ship/no-ship criteria and quality bar",
    ],
    "devops-release": [
        "Set up CI/CD pipeline configuration and build scripts",
        "Define deployment environments and promotion strategy",
        "Create release runbook and rollback procedures",
    ],
    "security-engineer": [
        "Conduct initial threat model for the application",
        "Review architecture for security risks and attack surfaces",
        "Define security requirements and hardening checklist",
    ],
    "compliance-risk": [
        "Identify applicable regulatory requirements and controls",
        "Create compliance evidence tracking matrix",
        "Document data classification and handling procedures",
    ],
    "researcher-librarian": [
        "Survey technology options and create decision matrix",
        "Build initial knowledge base with project references",
        "Produce research memo on key architectural trade-offs",
    ],
    "technical-writer": [
        "Create project README and getting-started guide",
        "Define documentation structure and style conventions",
        "Draft initial API documentation outline",
    ],
    "ux-ui-designer": [
        "Map user workflows and create information architecture",
        "Produce wireframes for primary screens and interactions",
        "Define UX acceptance criteria for first milestone",
    ],
    "integrator-merge-captain": [
        "Define branch strategy and merge workflow",
        "Set up integration validation checks",
        "Create release notes template and changelog format",
    ],
}

_KICKOFF_TASKS: dict[str, list[str]] = {
    "team-lead": [
        "Review composition and create initial backlog",
    ],
    "ba": [
        "Document initial requirements",
    ],
    "architect": [
        "Validate architecture decisions",
    ],
    "developer": [
        "Set up development environment and build",
    ],
    "tech-qa": [
        "Create test plan and quality gates",
    ],
    "code-quality-reviewer": [
        "Define code review standards and PR checklist",
    ],
    "devops-release": [
        "Set up CI/CD pipeline and deployment strategy",
    ],
    "security-engineer": [
        "Conduct initial threat model and security review",
    ],
    "compliance-risk": [
        "Identify regulatory requirements and controls",
    ],
    "researcher-librarian": [
        "Survey technology options and build knowledge base",
    ],
    "technical-writer": [
        "Create project README and documentation structure",
    ],
    "ux-ui-designer": [
        "Map user workflows and produce initial wireframes",
    ],
    "integrator-merge-captain": [
        "Define branch strategy and merge workflow",
    ],
}


def _get_task_templates(seed_mode: SeedMode) -> dict[str, list[str]]:
    """Return the task template set for the given seed mode."""
    if seed_mode == SeedMode.KICKOFF:
        return _KICKOFF_TASKS
    return _DETAILED_TASKS


def seed_tasks(spec: CompositionSpec, output_dir: str | Path) -> StageResult:
    """Generate a starter task index file based on the composition spec.

    Creates ``ai/tasks/_index.md`` with initial tasks for each selected
    persona.  The level of detail depends on ``spec.generation.seed_mode``.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    tasks_dir = root / "ai" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    templates = _get_task_templates(spec.generation.seed_mode)
    persona_ids = [p.id for p in spec.team.personas]

    if not persona_ids:
        warnings.append("No personas selected — seed task file will be empty")

    lines: list[str] = [
        "# Task Index",
        "",
        "Auto-generated starter tasks based on project composition.",
        "",
        "| # | Task | Owner | Status |",
        "|---|------|-------|--------|",
    ]

    task_num = 1
    for persona_id in persona_ids:
        tasks = templates.get(persona_id, [])
        if not tasks:
            warnings.append(
                f"No seed task templates for persona '{persona_id}'"
            )
            continue

        for task_desc in tasks:
            lines.append(f"| {task_num} | {task_desc} | {persona_id} | Pending |")
            task_num += 1

    lines.append("")  # trailing newline

    index_path = tasks_dir / "_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    rel_path = str(index_path.relative_to(root))
    wrote.append(rel_path)

    logger.info(
        "Seed tasks complete: %d tasks generated for %d personas (mode=%s)",
        task_num - 1,
        len(persona_ids),
        spec.generation.seed_mode.value,
    )

    return StageResult(wrote=wrote, warnings=warnings)
