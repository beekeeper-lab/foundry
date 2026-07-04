"""Scaffold service — creates the directory skeleton for a generated project."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from foundry_app import __version__ as _FOUNDRY_VERSION
from foundry_app.core.models import (
    CompositionSpec,
    LibraryIndex,
    StageResult,
    _persona_dirname,
)
from foundry_app.io.composition_io import save_composition

logger = logging.getLogger(__name__)

_MEDIA_PLAN_FILES = (
    ("IMAGE-PLAN.md.j2", "IMAGE-PLAN.md"),
    ("NARRATION-PLAN.md.j2", "NARRATION-PLAN.md"),
)

# Standard directory structure for a Claude Code project
_CLAUDE_DIRS = [
    ".claude/agents",
    ".claude/commands",
    ".claude/hooks",
    ".claude/skills",
]

_AI_DIRS = [
    "ai/context",
    "ai/outputs",
    "ai/generated/members",
    "ai/generated/expertise",
    "ai/beans",
    "ai/tasks",
    "ai/team",
]

_MEMORY_SCAFFOLD = """\
# MEMORY — Durable Lessons

Curated, small, and load-bearing: one line per lesson, appended by the
bean-closure retro step (see `/close-loop`). When a lesson implicates a
persona, expertise pack, or kit asset, also draft an improvement bean.
Delete entries that stop being true.

## Process

- (none yet)

## Personas

- (none yet)

## Expertise

- (none yet)

## Kit

- (none yet)
"""

_ORCHESTRATION_YAML_BLOCK = """
orchestration:
  orchestrator_role: team-lead
  team_model: available-bench
  required_roles:
    software-development:
      - developer
      - tech-qa
  optional_roles:
    - architect
    - ux-ui-designer
    - integrator-merge-captain
    - ba
"""


def _build_contracts_yaml_block(
    spec: CompositionSpec,
    library_index: LibraryIndex,
) -> str:
    """Render the ``contracts:`` block for the generated composition.yml.

    Emits one entry per persona on the team (``spec.team.personas``),
    sourcing produces/consumes from the LibraryIndex's PersonaInfo. Then
    emits a flat artifact-types reference list — the union of every name
    appearing in any persona's produces/consumes, sorted by name. Each
    artifact-type entry carries ``name``, ``format``, ``template-path``
    only (description and required-fields are intentionally omitted from
    the emit; see ADR-013 Decision 4).

    Returns an empty string when ``spec.team.personas`` is empty so the
    caller can append unconditionally.
    """
    if not spec.team.personas:
        return ""

    personas_block_lines: list[str] = []
    referenced_names: set[str] = set()

    for selection in spec.team.personas:
        info = library_index.persona_by_id(selection.id)
        if info is None:
            continue
        personas_block_lines.append(f"    - id: {info.id}")
        personas_block_lines.append("      produces:")
        if info.produces:
            for name in info.produces:
                personas_block_lines.append(f"        - {name}")
                referenced_names.add(name)
        else:
            personas_block_lines.append("        []")
        personas_block_lines.append("      consumes:")
        if info.consumes:
            for name in info.consumes:
                personas_block_lines.append(f"        - {name}")
                referenced_names.add(name)
        else:
            personas_block_lines.append("        []")

    if not personas_block_lines:
        return ""

    artifact_lines: list[str] = []
    for name in sorted(referenced_names):
        info = library_index.artifact_type_by_name(name)
        if info is None:
            # Persona referenced an unknown name; the indexer would have
            # already dropped it from PersonaInfo, but be defensive here.
            continue
        artifact_lines.append(f"    - name: {info.name}")
        artifact_lines.append(f"      format: {info.format}")
        if info.template_path is None:
            artifact_lines.append("      template-path: null")
        else:
            artifact_lines.append(f"      template-path: {info.template_path}")

    block_lines: list[str] = ["", "contracts:", "  personas:"]
    block_lines.extend(personas_block_lines)
    block_lines.append("  artifact-types:")
    if artifact_lines:
        block_lines.extend(artifact_lines)
    else:
        block_lines.append("    []")
    return "\n".join(block_lines) + "\n"


_MEDIA_SECTION = (
    "## Generating images and audio\n"
    "\n"
    "This project ships with two plan-driven media skills. The plan files at "
    "the project root are the review surface; on-disk MP3s and PNGs are the "
    "output.\n"
    "\n"
    "- `IMAGE-PLAN.md` — image entries with provider/quality frontmatter; the\n"
    "  `generate-image` skill loops the plan, writes one PNG per entry, and\n"
    "  skips entries already present on disk.\n"
    "- `NARRATION-PLAN.md` + inline `> 🎙️ ...` blockquotes in your source\n"
    "  markdown — `generate-audio` walks the source files, generates one MP3\n"
    "  per block, and writes a per-source `manifest.json` storing the\n"
    "  stripped text for content-hash dedup across pages.\n"
    "\n"
    "Both skills discover `.env` from cwd → parents → `$HOME`. Required env "
    "vars (set the ones for the providers you use):\n"
    "\n"
    "- `GEMINI_API_KEY` (default image provider)\n"
    "- `OPENAI_API_KEY` (when `**Generator:**` selects an OpenAI model)\n"
    "- `ELEVENLABS_API_KEY` (all audio runs)\n"
    "\n"
    "See `.claude/shared/skills/generate-image/SKILL.md` and "
    "`.claude/shared/skills/generate-audio/SKILL.md` for usage and cost "
    "discipline notes.\n"
    "\n"
)


def _render_readme(spec: CompositionSpec) -> str:
    """Render the starter README.md content for a generated project."""
    description = spec.project.description or (
        f"AI-team-backed project for {spec.project.name}."
    )
    today = date.today().isoformat()
    media_block = _MEDIA_SECTION if spec.generation.include_media_skills else ""
    return (
        f"# {spec.project.name}\n"
        "\n"
        f"{description}\n"
        "\n"
        "## Getting Started\n"
        "\n"
        "This project was generated by [Foundry]"
        "(https://github.com/beekeeper-lab/foundry). "
        "The Claude Code context is configured in `CLAUDE.md`. "
        "Start by reading that file for project orientation and the team roster.\n"
        "\n"
        "Foundry scaffolds the AI team context only — it does not "
        "generate stack-specific application code. Initialize your "
        "application with the stack-appropriate command — see "
        "[docs/starter-stacks.md](https://github.com/beekeeper-lab/"
        "foundry/blob/main/docs/starter-stacks.md) in the Foundry "
        "repo for common recipes (e.g. `npm create vite@latest`, "
        "`uv init`, `cargo new`).\n"
        "\n"
        "## Structure\n"
        "\n"
        "- `.claude/` — Claude Code configuration (agents, commands, skills, hooks)\n"
        "- `ai/` — AI team workspace (backlog, outputs, context, team composition)\n"
        "\n"
        f"{media_block}"
        "---\n"
        f"Generated by Foundry v{_FOUNDRY_VERSION} on {today}\n"
    )


def _render_project_charter(spec: CompositionSpec) -> str:
    """Render the starter ai/context/project-charter.md content.

    The charter is a TODO-marked one-pager personas read first when opening
    the project. Sections (Purpose, Audience, Success Criteria, Non-Goals,
    Constraints) come from BEAN-252 (ADR-003). Block-quoted prompts under
    each heading guide the human filling in the charter.
    """
    if spec.project.description:
        description_line = f"*{spec.project.description}*"
    else:
        description_line = (
            "*TODO: Add a one-line project description in the composition spec.*"
        )
    today = date.today().isoformat()
    return (
        f"# Project Charter — {spec.project.name}\n"
        "\n"
        "> **Status:** TODO — fill in this charter before the team begins "
        "substantive work.\n"
        "> Personas should read this file first when opening the project.\n"
        "\n"
        f"{description_line}\n"
        "\n"
        "## Purpose\n"
        "\n"
        "> What does this project do, in one paragraph? Lead with the "
        "*outcome* (what changes for the user/business when this exists), "
        "not the implementation. A reader should understand the project's "
        "reason for existing in 30 seconds.\n"
        "\n"
        "`TODO: Replace this paragraph with a one-paragraph statement of "
        "purpose.`\n"
        "\n"
        "## Audience\n"
        "\n"
        "> Who is this for? Name the primary user (role, context, what "
        "they're trying to accomplish) and any secondary stakeholders. If "
        "multiple audiences, distinguish them — different audiences usually "
        "imply different success criteria.\n"
        "\n"
        "`TODO: Describe the primary audience and any secondary "
        "stakeholders.`\n"
        "\n"
        "## Success Criteria\n"
        "\n"
        "> What does \"done\" look like? List 3–5 outcome-shaped criteria "
        "the team can point at to say \"yes, we shipped what we set out to "
        "ship.\" Avoid implementation criteria (e.g., \"uses Postgres\") — "
        "describe the change in the world, not the components used.\n"
        "\n"
        "- [ ] `TODO: Outcome criterion 1`\n"
        "- [ ] `TODO: Outcome criterion 2`\n"
        "- [ ] `TODO: Outcome criterion 3`\n"
        "\n"
        "## Non-Goals\n"
        "\n"
        "> What is this project explicitly *not* doing? Non-goals are as "
        "important as goals — they prevent scope creep and tell the team "
        "where to push back. Include things that a reasonable reader might "
        "assume are in scope but are not.\n"
        "\n"
        "- `TODO: Non-goal 1`\n"
        "- `TODO: Non-goal 2`\n"
        "\n"
        "## Constraints\n"
        "\n"
        "> What boundaries does the project operate within? Include "
        "technical constraints (must run on X, must integrate with Y), "
        "organizational constraints (deadline, budget, team size), and "
        "regulatory/compliance constraints. If the project has no hard "
        "constraints, note that explicitly.\n"
        "\n"
        "- `TODO: Constraint 1`\n"
        "- `TODO: Constraint 2`\n"
        "\n"
        "---\n"
        f"Generated by Foundry v{_FOUNDRY_VERSION} on {today}. "
        "Edit freely — this file is overlay-safe.\n"
    )


def _render_media_plans(
    spec: CompositionSpec,
    library_root: Path,
    root: Path,
    created: list[str],
    warnings: list[str],
) -> None:
    """Stamp IMAGE-PLAN.md and NARRATION-PLAN.md at the project root.

    Renders Jinja2 templates from
    ``<library_root>/templates/media/`` when
    ``spec.generation.include_media_skills`` is True. Overlay-safe: an
    existing plan file at the destination is never overwritten.
    """
    templates_dir = library_root / "templates" / "media"
    if not templates_dir.is_dir():
        warnings.append(
            f"include_media_skills=True but media templates not found at {templates_dir}"
        )
        return

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
    )
    context = {"project_name": spec.project.name}

    for template_name, output_name in _MEDIA_PLAN_FILES:
        dest = root / output_name
        if dest.exists():
            logger.info("Media plan already present, not overwriting: %s", dest)
            continue
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            warnings.append(f"Media plan template missing: {template_name}")
            continue
        dest.write_text(template.render(**context), encoding="utf-8")
        created.append(output_name)
        logger.info("Wrote media plan: %s", dest)


def scaffold_project(
    spec: CompositionSpec,
    output_dir: str | Path,
    library_root: str | Path | None = None,
    library_index: LibraryIndex | None = None,
) -> StageResult:
    """Create the directory skeleton for a generated Claude Code project.

    Creates the standard directory tree based on the composition spec:
    - ``.claude/`` subdirectories (agents, commands, hooks, skills)
    - ``ai/`` subdirectories (context, outputs, beans, tasks)
    - Per-persona output directories under ``ai/outputs/``

    Existing directories are silently skipped (overlay-safe).

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory for the generated project.
        library_root: Path to the ai-team-library root. Required when
            ``spec.generation.include_media_skills`` is True so the media
            plan templates can be located. May be omitted otherwise.
        library_index: Optional indexed view of the library. When provided,
            the generated ``composition.yml`` is augmented with a
            ``contracts:`` block sourced from per-persona ``contracts.yml``
            files and the artifact-type registry. See ADR-013.

    Returns:
        A StageResult listing all directories that were created.
    """
    root = Path(output_dir)
    created: list[str] = []
    warnings: list[str] = []

    # Collect all directories to create
    dirs_to_create: list[Path] = []

    # Project root
    dirs_to_create.append(root)

    # .claude/ directories
    for d in _CLAUDE_DIRS:
        dirs_to_create.append(root / d)

    # ai/ directories
    for d in _AI_DIRS:
        dirs_to_create.append(root / d)

    # Per-persona output directories. Strip any ``extended/`` tier prefix
    # from the id so the on-disk layout stays flat across tiers (ADR-014).
    for persona in spec.team.personas:
        dirs_to_create.append(
            root / "ai" / "outputs" / _persona_dirname(persona.id)
        )

    # Track which directories already exist so we know what we actually created
    existing = {d for d in dirs_to_create if d.exists()}

    # Create all directories
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        if dir_path not in existing:
            rel = str(dir_path.relative_to(root))
            if dir_path == root:
                rel = "."
            created.append(rel)
            logger.info("Created directory: %s", dir_path)

    if not spec.team.personas:
        warnings.append("No personas selected — no per-persona output directories created")

    # Emit the source composition snapshot so the generated project is
    # round-trippable and passes `validate-repo`'s structural checks. Only
    # count as "written" when the on-disk content actually changes, so a
    # second scaffold pass over an unchanged spec is a true no-op.
    composition_path = root / "ai" / "team" / "composition.yml"
    previous_composition = (
        composition_path.read_text(encoding="utf-8")
        if composition_path.exists()
        else None
    )
    save_composition(spec, composition_path)
    # Append the static orchestration policy block so tooling and
    # cold-start agents can read the team model from composition.yml
    # directly. This is policy, not input — it is identical across
    # projects and not driven by the spec. See BEAN-269.
    contracts_block = (
        _build_contracts_yaml_block(spec, library_index)
        if library_index is not None
        else ""
    )
    composition_path.write_text(
        composition_path.read_text(encoding="utf-8")
        + _ORCHESTRATION_YAML_BLOCK
        + contracts_block,
        encoding="utf-8",
    )
    if previous_composition != composition_path.read_text(encoding="utf-8"):
        created.append(str(composition_path.relative_to(root)))
        logger.info("Wrote composition snapshot: %s", composition_path)

    # Emit a starter README.md at the project root. Overlay-safe: do not
    # overwrite an existing README the user has customized.
    readme_path = root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(_render_readme(spec), encoding="utf-8")
        created.append("README.md")
        logger.info("Wrote starter README: %s", readme_path)

    # Emit a starter project charter under ai/context/. Overlay-safe so a
    # filled-in charter is never clobbered. See ADR-003 / BEAN-252.
    charter_path = root / "ai" / "context" / "project-charter.md"
    if not charter_path.exists():
        charter_path.write_text(_render_project_charter(spec), encoding="utf-8")
        created.append(str(charter_path.relative_to(root)))
        logger.info("Wrote starter project charter: %s", charter_path)

    # MEMORY.md — durable lessons the retro step appends to (SPEC-009).
    # Overlay-safe: never clobber accumulated memory.
    memory_path = root / "MEMORY.md"
    if not memory_path.exists():
        memory_path.write_text(_MEMORY_SCAFFOLD, encoding="utf-8")
        created.append("MEMORY.md")
        logger.info("Wrote MEMORY.md scaffold: %s", memory_path)

    # Stamp media plan skeletons (BEAN-284) when the project opts in.
    if spec.generation.include_media_skills:
        if library_root is None:
            warnings.append(
                "include_media_skills=True but library_root not provided; "
                "media plan skeletons skipped"
            )
        else:
            _render_media_plans(
                spec, Path(library_root), root, created, warnings,
            )

    logger.info(
        "Scaffold complete: %d entries created, %d warnings",
        len(created),
        len(warnings),
    )

    return StageResult(wrote=created, warnings=warnings)
