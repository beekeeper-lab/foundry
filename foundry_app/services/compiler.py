"""Compiler service — assembles CLAUDE.md from library persona and stack files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from foundry_app.core.models import CompositionSpec, LibraryIndex, StageResult

logger = logging.getLogger(__name__)

# Template variable pattern: {{ var }} or {{ var | filter }}
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(.+?)\s*\}\}")


def _resolve_placeholder(match: re.Match[str], context: dict[str, str]) -> str:
    """Resolve a single {{ ... }} placeholder against the context dict.

    Supports:
    - Simple variables: ``{{ project_name }}``
    - join filter: ``{{ stacks | join(", ") }}``

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
    stack_ids = sorted(
        (s.id for s in spec.stacks),
        key=lambda sid: next(
            (s.order for s in spec.stacks if s.id == sid), 0
        ),
    )
    return {
        "project_name": spec.project.name,
        "stacks": ",".join(stack_ids),
    }


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


def _compile_stack_section(
    stack_id: str,
    library_root: Path,
    index: LibraryIndex,
    context: dict[str, str],
    warnings: list[str],
) -> str | None:
    """Compile the section for a single stack.

    Returns the assembled markdown text, or None if the stack directory
    is missing from the library.
    """
    stack_info = index.stack_by_id(stack_id)
    if stack_info is None:
        warnings.append(f"Stack '{stack_id}' not found in library index")
        return None

    stack_dir = Path(stack_info.path)

    # Read conventions.md (primary file for each stack)
    conventions = _read_file(stack_dir / "conventions.md")
    if conventions is not None:
        return _substitute(conventions.strip(), context)

    warnings.append(f"Stack '{stack_id}' missing conventions.md")
    return None


def compile_project(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Compile CLAUDE.md from library components based on the composition spec.

    Reads persona source files (persona.md, outputs.md, prompts.md) and stack
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
                sections.append(persona_section)

    # --- Stack sections (sorted by order field, then alphabetically) ---
    if spec.stacks:
        sections.append("## Technology Stacks")
        sorted_stacks = sorted(spec.stacks, key=lambda s: (s.order, s.id))
        for stack_sel in sorted_stacks:
            stack_section = _compile_stack_section(
                stack_sel.id, lib_root, library_index, context, warnings,
            )
            if stack_section is not None:
                sections.append(stack_section)

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
