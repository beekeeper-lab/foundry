"""Compiler service — assembles CLAUDE.md from library persona and expertise files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from foundry_app.core.models import CompositionSpec, LibraryIndex, StageResult

logger = logging.getLogger(__name__)

# Template variable pattern: {{ var }} or {{ var | filter }}
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(.+?)\s*\}\}")

# Pattern for extracting persona display name from "# Persona: <Name>" header
_PERSONA_HEADER_RE = re.compile(r"^#\s+Persona:\s*(.+)", re.MULTILINE)

# Pattern for "(defer to X)" or "(defer to X; extra text)" parentheticals
_DEFER_TO_RE = re.compile(r"\s*\(defer to ([^;)]+)(?:;[^)]+)?\)")


def _resolve_placeholder(match: re.Match[str], context: dict[str, str]) -> str:
    """Resolve a single {{ ... }} placeholder against the context dict.

    Supports:
    - Simple variables: ``{{ project_name }}``
    - join filter: ``{{ expertise | join(", ") }}``

    Returns the original placeholder text if the variable is not in context.
    """
    expr = match.group(1).strip()

    # Handle join filter:  varname | join("sep")
    join_match = re.match(r"(\w+)\s*\|\s*join\(\s*\"([^\"]*)\"\s*\)", expr)
    if join_match:
        var_name = join_match.group(1)
        separator = join_match.group(2)
        value = context.get(var_name)
        if value is None:
            return match.group(0)  # leave unresolved
        return separator.join(v.strip() for v in value.split(","))

    # Simple variable lookup
    value = context.get(expr)
    if value is None:
        return match.group(0)  # leave unresolved
    return value


def _substitute(text: str, context: dict[str, str]) -> str:
    """Replace all ``{{ ... }}`` placeholders in *text* using *context*."""
    return _PLACEHOLDER_RE.sub(lambda m: _resolve_placeholder(m, context), text)


def _read_file(path: Path) -> str | None:
    """Read a file and return its contents, or None if it doesn't exist."""
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def _build_context(spec: CompositionSpec) -> dict[str, str]:
    """Build the template variable context from the composition spec."""
    expertise_ids = sorted(
        (s.id for s in spec.expertise),
        key=lambda sid: next(
            (s.order for s in spec.expertise if s.id == sid), 0
        ),
    )
    return {
        "project_name": spec.project.name,
        "expertise": ",".join(expertise_ids),
    }


def _build_persona_name_map(index: LibraryIndex) -> dict[str, str]:
    """Build a mapping of persona display names to IDs from the library.

    Reads the ``# Persona: <Name>`` header from each persona.md to extract
    display names.  Returns a dict mapping display name -> persona ID.
    """
    name_map: dict[str, str] = {}
    for persona_info in index.personas:
        persona_md = _read_file(Path(persona_info.path) / "persona.md")
        if persona_md is None:
            continue
        match = _PERSONA_HEADER_RE.search(persona_md)
        if match:
            name_map[match.group(1).strip()] = persona_info.id
    return name_map


def _resolve_persona_name(
    name: str,
    name_to_id: dict[str, str],
) -> str | None:
    """Resolve a display name to a persona ID.

    Handles exact matches and short-form names (e.g., ``"Technical Writer"``
    matching ``"Technical Writer / Doc Owner"``).
    """
    name = name.strip()
    if name in name_to_id:
        return name_to_id[name]
    for canonical, pid in name_to_id.items():
        if canonical.startswith(name + " / "):
            return pid
    return None


def _filter_collaboration_table(
    text: str,
    selected_ids: set[str],
    name_to_id: dict[str, str],
) -> str:
    """Filter Collaboration & Handoffs table to only include selected personas.

    Removes table rows where the collaborator is a known-but-not-selected
    persona.  Rows for unknown entities (e.g., ``"Stakeholders"``) are kept.
    If all data rows are removed, the entire section (heading + table) is
    dropped.
    """
    lines = text.split("\n")
    result: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if re.match(r"^##\s+Collaboration", line):
            # Collect the heading and any blank lines before the table
            section_lines: list[str] = [line]
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                section_lines.append(lines[i])
                i += 1

            # Collect table header row
            if i < len(lines) and lines[i].startswith("|"):
                section_lines.append(lines[i])
                i += 1
            else:
                result.extend(section_lines)
                continue

            # Collect separator row
            if i < len(lines) and lines[i].startswith("|"):
                section_lines.append(lines[i])
                i += 1
            else:
                result.extend(section_lines)
                continue

            # Collect and filter data rows
            data_rows: list[str] = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = lines[i].split("|")
                if len(cells) >= 3:
                    collaborator = cells[1].strip()
                    pid = _resolve_persona_name(collaborator, name_to_id)
                    if pid is None or pid in selected_ids:
                        data_rows.append(lines[i])
                else:
                    data_rows.append(lines[i])
                i += 1

            if data_rows:
                result.extend(section_lines)
                result.extend(data_rows)
            # else: empty table after filtering — drop the entire section
            continue

        result.append(line)
        i += 1

    return "\n".join(result)


def _filter_defer_references(
    text: str,
    selected_ids: set[str],
    name_to_id: dict[str, str],
) -> str:
    """Remove ``(defer to X)`` parentheticals when *X* is not selected."""

    def _replace(match: re.Match[str]) -> str:
        persona_name = match.group(1).strip()
        pid = _resolve_persona_name(persona_name, name_to_id)
        if pid is None or pid in selected_ids:
            return match.group(0)
        return ""

    return _DEFER_TO_RE.sub(_replace, text)


def _filter_persona_references(
    text: str,
    selected_ids: set[str],
    name_to_id: dict[str, str],
) -> str:
    """Remove references to non-selected personas from compiled content.

    1. Filters the Collaboration & Handoffs table.
    2. Strips ``(defer to X)`` parentheticals for non-selected personas.
    """
    text = _filter_collaboration_table(text, selected_ids, name_to_id)
    text = _filter_defer_references(text, selected_ids, name_to_id)
    return text


def _compile_persona_section(
    persona_id: str,
    library_root: Path,
    index: LibraryIndex,
    context: dict[str, str],
    warnings: list[str],
) -> str | None:
    """Compile the section for a single persona.

    Returns the assembled markdown text, or None if the persona directory
    is missing from the library.
    """
    persona_info = index.persona_by_id(persona_id)
    if persona_info is None:
        warnings.append(f"Persona '{persona_id}' not found in library index")
        return None

    persona_dir = Path(persona_info.path)

    parts: list[str] = []
    files_read = 0

    # Read persona.md (primary — defines the role)
    persona_md = _read_file(persona_dir / "persona.md")
    if persona_md is not None:
        parts.append(_substitute(persona_md.strip(), context))
        files_read += 1
    else:
        warnings.append(f"Persona '{persona_id}' missing persona.md")

    # Read outputs.md
    outputs_md = _read_file(persona_dir / "outputs.md")
    if outputs_md is not None:
        parts.append(_substitute(outputs_md.strip(), context))
        files_read += 1

    # Read prompts.md
    prompts_md = _read_file(persona_dir / "prompts.md")
    if prompts_md is not None:
        parts.append(_substitute(prompts_md.strip(), context))
        files_read += 1

    if files_read == 0:
        warnings.append(f"Persona '{persona_id}' has no source files")
        return None

    return "\n\n".join(parts)


def _compile_expertise_section(
    expertise_id: str,
    library_root: Path,
    index: LibraryIndex,
    context: dict[str, str],
    warnings: list[str],
) -> str | None:
    """Compile the section for a single expertise.

    Returns the assembled markdown text, or None if the expertise directory
    is missing from the library.
    """
    expertise_info = index.expertise_by_id(expertise_id)
    if expertise_info is None:
        warnings.append(f"Expertise '{expertise_id}' not found in library index")
        return None

    expertise_dir = Path(expertise_info.path)

    # Read conventions.md (primary file for each expertise)
    conventions = _read_file(expertise_dir / "conventions.md")
    if conventions is not None:
        return _substitute(conventions.strip(), context)

    warnings.append(f"Expertise '{expertise_id}' missing conventions.md")
    return None


def compile_project(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Compile CLAUDE.md from library components based on the composition spec.

    Reads persona source files (persona.md, outputs.md, prompts.md) and expertise
    convention files (conventions.md) from the library, performs template variable
    substitution, and assembles them into a single deterministic CLAUDE.md.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of available library components.
        library_root: Path to the root of the library directory.
        output_dir: Root directory for the generated project.

    Returns:
        A StageResult listing written files and any warnings.
    """
    root = Path(output_dir)
    lib_root = Path(library_root)
    wrote: list[str] = []
    warnings: list[str] = []

    context = _build_context(spec)
    sections: list[str] = []

    # Build persona name map and selected IDs for reference filtering
    name_to_id = _build_persona_name_map(library_index)
    selected_ids = {ps.id for ps in spec.team.personas}

    # --- Project header ---
    header = f"# {spec.project.name}"
    sections.append(header)

    # --- Persona sections (in spec order) ---
    if spec.team.personas:
        sections.append("## Team")
        for persona_sel in spec.team.personas:
            persona_section = _compile_persona_section(
                persona_sel.id, lib_root, library_index, context, warnings,
            )
            if persona_section is not None:
                persona_section = _filter_persona_references(
                    persona_section, selected_ids, name_to_id,
                )
                sections.append(persona_section)

    # --- Expertise sections (sorted by order field, then alphabetically) ---
    if spec.expertise:
        sections.append("## Expertise")
        sorted_expertise = sorted(spec.expertise, key=lambda s: (s.order, s.id))
        for expertise_sel in sorted_expertise:
            expertise_section = _compile_expertise_section(
                expertise_sel.id, lib_root, library_index, context, warnings,
            )
            if expertise_section is not None:
                sections.append(expertise_section)

    # --- Assemble and write ---
    content = "\n\n".join(sections) + "\n"

    claude_md_path = root / "CLAUDE.md"
    claude_md_path.parent.mkdir(parents=True, exist_ok=True)
    claude_md_path.write_text(content, encoding="utf-8")
    wrote.append("CLAUDE.md")
    logger.info("Wrote: %s", claude_md_path)

    # Check for unresolved placeholders in output
    unresolved = _PLACEHOLDER_RE.findall(content)
    if unresolved:
        unique = sorted(set(unresolved))
        warnings.append(
            f"Unresolved placeholders in CLAUDE.md: {', '.join(unique)}"
        )

    logger.info(
        "Compile complete: %d files written, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)
