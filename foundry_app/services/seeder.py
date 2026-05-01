"""Seeder service — emits the starter BEAN-001-bootstrap bean for a generated project."""

from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    SeedMode,
    StageResult,
    _persona_dirname,
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
        "Create initial ADR for expertise decisions",
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

_STARTER_BEAN_ID = "BEAN-001"
_STARTER_BEAN_SLUG = "bootstrap"
_STARTER_BEAN_DIR = f"{_STARTER_BEAN_ID}-{_STARTER_BEAN_SLUG}"
_STARTER_BEAN_TITLE = "Bootstrap Project Team"
_CHARTER_REL_PATH = "ai/context/project-charter.md"

_INDEX_HEADER = """# Bean Backlog

## Status Key

| Status | Meaning |
|--------|---------|
| Unapproved | Created, awaiting human review and approval |
| Approved | Reviewed and approved, ready for execution |
| In Progress | Tasks created and execution underway |
| Done | All acceptance criteria met |
| Deferred | Intentionally postponed |

## Backlog

| Bean ID | Title | Category | Priority | Status | Owner |
|---------|-------|----------|----------|--------|-------|
"""


def _get_task_templates(seed_mode: SeedMode) -> dict[str, list[str]]:
    """Return the task template set for the given seed mode."""
    if seed_mode == SeedMode.KICKOFF:
        return _KICKOFF_TASKS
    return _DETAILED_TASKS


def _slugify(text: str, max_words: int = 6) -> str:
    """Lowercase kebab-case slug of the first `max_words` words of `text`."""
    words = re.findall(r"[A-Za-z0-9]+", text.lower())[:max_words]
    return "-".join(words) or "task"


def _render_bean_md(spec: CompositionSpec, charter_present: bool) -> str:
    """Render the starter bean's bean.md."""
    if charter_present:
        problem = (
            f"The freshly generated project for **{spec.project.name}** "
            "needs the team to complete its day-1 setup before substantive "
            "work begins. Seeded tasks for each selected persona are "
            "collected under this bean so the work enters the bean "
            "workflow instead of bypassing it.\n\n"
            f"Start by reading `{_CHARTER_REL_PATH}` — the project charter "
            "authored for this project (BEAN-252) captures the purpose, "
            "audience, success criteria, non-goals, and constraints each "
            "persona should align their kickoff tasks against."
        )
    else:
        problem = (
            f"The freshly generated project for **{spec.project.name}** "
            "needs the team to complete its day-1 setup before substantive "
            "work begins. Seeded tasks for each selected persona are "
            "collected under this bean so the work enters the bean "
            "workflow instead of bypassing it.\n\n"
            "No project charter was scaffolded — each persona should agree "
            "on purpose, audience, and success criteria before proceeding."
        )

    today = date.today().isoformat()
    return (
        f"# {_STARTER_BEAN_ID}: {_STARTER_BEAN_TITLE}\n"
        "\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        f"| **Bean ID** | {_STARTER_BEAN_ID} |\n"
        "| **Status** | Approved |\n"
        "| **Priority** | Medium |\n"
        f"| **Created** | {today} |\n"
        "| **Started** | — |\n"
        "| **Completed** | — |\n"
        "| **Duration** | — |\n"
        "| **Owner** | (unassigned) |\n"
        "| **Category** | App |\n"
        "\n"
        "## Problem Statement\n"
        "\n"
        f"{problem}\n"
        "\n"
        "## Goal\n"
        "\n"
        "Each selected persona completes their kickoff tasks so the team "
        "has a shared understanding of scope, tooling, and acceptance "
        "standards before the first feature bean is picked.\n"
        "\n"
        "## Acceptance Criteria\n"
        "\n"
        "- [ ] Every task under `tasks/` is marked Done.\n"
        "- [ ] The Team Lead has created the next bean(s) from project "
        "requirements.\n"
        "\n"
        "## Tasks\n"
        "\n"
        "> Populated by the Seeder. Personas claim tasks in the normal "
        "workflow.\n"
        "\n"
        "## Notes\n"
        "\n"
        "Auto-generated by the Foundry Seeder. Edit freely — this file is "
        "overlay-safe.\n"
    )


def _render_task_md(
    task_num: int, persona_id: str, description: str
) -> str:
    """Render an individual task file under tasks/NN-<owner>-<slug>.md.

    ``persona_id`` is the canonical reference form (per ADR-014, extended
    personas are ``extended/<name>``). The Owner row keeps that form so the
    document round-trips with composition.yml; the on-disk ``ai/outputs/``
    pointer uses the leaf directory name to match the actual filesystem
    layout the scaffolder creates.
    """
    output_dir_name = _persona_dirname(persona_id)
    return (
        f"# Task {task_num:02d} — {persona_id}: {description}\n"
        "\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        f"| **Owner** | {persona_id} |\n"
        "| **Depends On** | — |\n"
        "| **Status** | Pending |\n"
        "| **Started** | — |\n"
        "| **Completed** | — |\n"
        "| **Duration** | — |\n"
        "\n"
        "## Goal\n"
        "\n"
        f"{description}\n"
        "\n"
        "## Acceptance Criteria\n"
        "\n"
        "- [ ] Goal above is complete.\n"
        "- [ ] Output is recorded under "
        f"`ai/outputs/{output_dir_name}/` when applicable.\n"
    )


def _index_row() -> str:
    """Return the Markdown table row listing the starter bean in _index.md."""
    return (
        f"| {_STARTER_BEAN_ID} | {_STARTER_BEAN_TITLE} | App | "
        "Medium | Approved | (unassigned) |\n"
    )


def _upsert_index(index_path: Path) -> bool:
    """Append the starter bean row to _index.md, or create the file.

    Returns True if the file was created or modified, False if the row was
    already present (idempotent re-runs produce no change).
    """
    row = _index_row()
    if not index_path.exists():
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(_INDEX_HEADER + row, encoding="utf-8")
        return True

    existing = index_path.read_text(encoding="utf-8")
    if _STARTER_BEAN_ID in existing:
        return False
    updated = existing.rstrip() + "\n" + row
    index_path.write_text(updated, encoding="utf-8")
    return True


def seed_tasks(spec: CompositionSpec, output_dir: str | Path) -> StageResult:
    """Emit the starter BEAN-001-bootstrap bean for a freshly generated project.

    Writes:
    - ``ai/beans/BEAN-001-bootstrap/bean.md`` with ``Status: Approved``.
    - ``ai/beans/BEAN-001-bootstrap/tasks/NN-<owner>-<slug>.md`` — one file per
      seeded task (same set previously written to ``ai/tasks/_index.md``).
    - ``ai/beans/_index.md`` — appends a BEAN-001 row if not already present.

    The bean's Problem Statement references ``ai/context/project-charter.md``
    when that file is present in the generated tree (emitted by BEAN-252),
    otherwise falls back to a generic bootstrap placeholder.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    bean_dir = root / "ai" / "beans" / _STARTER_BEAN_DIR
    tasks_dir = bean_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    charter_present = (root / _CHARTER_REL_PATH).exists()

    bean_md_path = bean_dir / "bean.md"
    bean_md_path.write_text(
        _render_bean_md(spec, charter_present), encoding="utf-8"
    )
    wrote.append(str(bean_md_path.relative_to(root)))

    templates = _get_task_templates(spec.generation.seed_mode)
    persona_ids = [p.id for p in spec.team.personas]

    if not persona_ids:
        warnings.append("No personas selected — seed task file will be empty")

    task_num = 1
    for persona_id in persona_ids:
        # Seed templates are keyed by the bare directory name; strip the
        # ADR-014 ``extended/`` prefix before lookup. Use the leaf for the
        # task filename too, so files don't sprout a phantom ``extended/``
        # subdirectory under ``tasks/``.
        leaf = _persona_dirname(persona_id)
        tasks = templates.get(leaf, [])
        if not tasks:
            warnings.append(
                f"No seed task templates for persona '{persona_id}'"
            )
            continue

        for task_desc in tasks:
            slug = _slugify(task_desc)
            filename = f"{task_num:02d}-{leaf}-{slug}.md"
            task_path = tasks_dir / filename
            task_path.write_text(
                _render_task_md(task_num, persona_id, task_desc),
                encoding="utf-8",
            )
            wrote.append(str(task_path.relative_to(root)))
            task_num += 1

    index_path = root / "ai" / "beans" / "_index.md"
    if _upsert_index(index_path):
        wrote.append(str(index_path.relative_to(root)))

    logger.info(
        "Seed tasks complete: %d tasks emitted under %s (mode=%s)",
        task_num - 1,
        _STARTER_BEAN_DIR,
        spec.generation.seed_mode.value,
    )

    return StageResult(wrote=wrote, warnings=warnings)
