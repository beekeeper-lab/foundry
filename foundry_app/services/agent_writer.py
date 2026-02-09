"""Agent writer service — generates .claude/agents/<persona>.md files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from foundry_app.core.models import CompositionSpec, LibraryIndex, StageResult

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Max number of operating principles / key rules to extract per persona
_MAX_KEY_RULES = 5

# Max lines of stack conventions to include as highlights
_MAX_STACK_HIGHLIGHT_LINES = 15


def _extract_mission(persona_text: str) -> str:
    """Extract the Mission section from persona.md content."""
    match = re.search(
        r"^## Mission\s*\n(.*?)(?=\n## |\Z)",
        persona_text,
        re.MULTILINE | re.DOTALL,
    )
    if match:
        return match.group(1).strip()
    # Fallback: use first paragraph
    lines = persona_text.strip().splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def _extract_role_description(persona_text: str) -> str:
    """Extract a one-line role description from the Mission section."""
    mission = _extract_mission(persona_text)
    if not mission:
        return ""
    # Take first sentence
    first_sentence = re.split(r"(?<=[.!?])\s+", mission, maxsplit=1)
    return first_sentence[0] if first_sentence else mission[:120]


def _extract_key_rules(persona_text: str) -> list[str]:
    """Extract key rules from Operating Principles section."""
    match = re.search(
        r"^## Operating Principles\s*\n(.*?)(?=\n## |\Z)",
        persona_text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []

    rules: list[str] = []
    for line in match.group(1).strip().splitlines():
        line = line.strip()
        if line.startswith("- **"):
            # Extract the bold principle name and its description
            bold_match = re.match(r"- \*\*(.+?)\*\*\.?\s*(.*)", line)
            if bold_match:
                rules.append(f"{bold_match.group(1)}: {bold_match.group(2)}")
            else:
                rules.append(line.lstrip("- "))
        elif line.startswith("- "):
            rules.append(line.lstrip("- "))

        if len(rules) >= _MAX_KEY_RULES:
            break

    return rules


def _extract_stack_highlights(conventions_text: str) -> str:
    """Extract the key highlights from a stack conventions.md file."""
    lines = conventions_text.strip().splitlines()
    highlights: list[str] = []
    in_defaults = False

    for line in lines:
        stripped = line.strip()
        # Skip the title and intro text
        if stripped.startswith("# "):
            continue
        if stripped.startswith("---"):
            continue
        if not stripped:
            if highlights:
                highlights.append("")
            continue

        # Capture the Defaults table
        if stripped == "## Defaults":
            in_defaults = True
            continue
        if in_defaults:
            if stripped.startswith("## "):
                in_defaults = False
            else:
                highlights.append(stripped)

        if len(highlights) >= _MAX_STACK_HIGHLIGHT_LINES:
            break

    return "\n".join(highlights).strip()


def write_agents(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Generate .claude/agents/<persona>.md files for each selected persona.

    Each agent file combines persona identity with stack context into a
    named team member role. The file is self-contained enough to be useful
    on its own, while referencing the full compiled member prompt for depth.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of library contents.
        library_root: Path to the library root directory.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing written files and any warnings.
    """
    out_root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )
    template = env.get_template("agent.md.j2")

    # Gather stack info
    stack_ids = [s.id for s in spec.stacks]
    stack_names = ", ".join(stack_ids) if stack_ids else "General"

    # Gather stack sections (shared across all personas)
    stack_sections: list[dict[str, str]] = []
    for stack_sel in spec.stacks:
        stack_info = library_index.stack_by_id(stack_sel.id)
        if stack_info is None:
            warnings.append(f"Stack '{stack_sel.id}' not found in library index")
            continue

        conventions_path = Path(stack_info.path) / "conventions.md"
        if conventions_path.is_file():
            conventions_text = conventions_path.read_text(encoding="utf-8")
            highlights = _extract_stack_highlights(conventions_text)
            if highlights:
                stack_sections.append({
                    "name": stack_sel.id.replace("-", " ").title(),
                    "highlights": highlights,
                })

    # Generate agent file for each persona
    agents_dir = out_root / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    for persona_sel in spec.team.personas:
        persona_info = library_index.persona_by_id(persona_sel.id)
        if persona_info is None:
            warnings.append(f"Persona '{persona_sel.id}' not found in library index")
            continue

        persona_path = Path(persona_info.path) / "persona.md"
        if not persona_path.is_file():
            warnings.append(
                f"Persona '{persona_sel.id}' missing persona.md at {persona_path}"
            )
            continue

        persona_text = persona_path.read_text(encoding="utf-8")

        # Build role name: stack + persona (e.g., "Python Developer")
        primary_stack = stack_ids[0].replace("-", " ").title() if stack_ids else ""
        persona_title = persona_sel.id.replace("-", " ").title()
        role_name = f"{primary_stack} {persona_title}".strip() if primary_stack else persona_title

        context = {
            "role_name": role_name,
            "role_description": _extract_role_description(persona_text),
            "stack_names": stack_names,
            "persona_id": persona_sel.id,
            "mission": _extract_mission(persona_text),
            "key_rules": _extract_key_rules(persona_text),
            "stack_sections": stack_sections,
        }

        content = template.render(**context)
        agent_file = agents_dir / f"{persona_sel.id}.md"
        agent_file.write_text(content, encoding="utf-8")

        rel_path = str(agent_file.relative_to(out_root))
        wrote.append(rel_path)
        logger.info("Wrote agent file: %s", rel_path)

    logger.info(
        "Agent writer complete: %d files written, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)
