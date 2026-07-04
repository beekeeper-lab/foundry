"""Compiler service — assembles CLAUDE.md from library persona and expertise files."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import NamedTuple

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseInfo,
    LibraryIndex,
    PersonaSelection,
    StageResult,
    _persona_dirname,
)

logger = logging.getLogger(__name__)

# Template variable pattern: {{ var }} or {{ var | filter }}
_PLACEHOLDER_RE = re.compile(r"\{\{\s*(.+?)\s*\}\}")

# Pattern for extracting persona display name from "# Persona: <Name>" header
_PERSONA_HEADER_RE = re.compile(r"^#\s+Persona:\s*(.+)", re.MULTILINE)

# Pattern for "(defer to X)" or "(defer to X; extra text)" parentheticals
_DEFER_TO_RE = re.compile(r"\s*\(defer to ([^;)]+)(?:;[^)]+)?\)")

# Acronyms that should be uppercased when rendering display names derived
# from kebab-case identifiers (e.g. ``tech-qa`` -> ``Tech QA``). Extend when
# a new acronym-bearing persona or expertise id is introduced.
_ACRONYMS: frozenset[str] = frozenset({
    "qa", "ui", "ux", "api", "sre", "ml", "ai", "ba",
    "sql", "dba", "aws", "gcp", "ci", "cd",
})


def _display_name_from_id(identifier: str) -> str:
    """Convert a kebab-case id into a human-readable display name.

    Acronyms listed in ``_ACRONYMS`` are uppercased; other segments are
    title-cased. Consecutive acronym segments collapse with ``/`` so that
    ``ux-ui-designer`` renders as ``UX/UI Designer`` rather than
    ``Ux Ui Designer``.
    """
    parts = identifier.split("-")
    words: list[str] = []
    run: list[str] = []

    def _flush() -> None:
        if run:
            words.append("/".join(run))
            run.clear()

    for part in parts:
        if part.lower() in _ACRONYMS:
            run.append(part.upper())
        else:
            _flush()
            words.append(part.capitalize())
    _flush()
    return " ".join(words)


def _canonicalize_persona_header(name: str) -> str:
    """Trim a ``# Persona: <Name>`` header down to its short display form.

    Rules applied in order:

    1. Remove trailing parenthetical annotations (``Business Analyst (BA)``
       -> ``Business Analyst``).
    2. Split on `` / ``. Merge consecutive segments whose adjoining tokens
       are short (<= 3 char) all-upper acronyms using ``/`` — this turns
       ``UX / UI Designer`` into ``UX/UI Designer``. Otherwise keep only
       the first segment (``Tech-QA / Test Engineer`` -> ``Tech-QA``).
    """
    name = re.sub(r"\s*\([^)]+\)\s*", "", name).strip()
    if " / " not in name:
        return name

    segments = [s.strip() for s in name.split(" / ") if s.strip()]
    merged = [segments[0]]
    for seg in segments[1:]:
        prev_tokens = merged[-1].split()
        cur_tokens = seg.split()
        if not prev_tokens or not cur_tokens:
            break
        prev_last = prev_tokens[-1]
        cur_first = cur_tokens[0]
        if (
            prev_last.isupper() and len(prev_last) <= 3
            and cur_first.isupper() and len(cur_first) <= 3
        ):
            merged[-1] = f"{merged[-1]}/{cur_first}"
            rest = cur_tokens[1:]
            if rest:
                merged.append(" ".join(rest))
        else:
            break
    return " ".join(merged)


def _persona_display_name(persona_id: str, index: LibraryIndex) -> str:
    """Return the display name for a persona.

    Prefers the persona's own ``# Persona: <Name>`` header (canonicalized),
    falling back to ``_display_name_from_id`` when the header is missing.
    The fallback strips any ADR-014 ``extended/`` tier prefix so the rendered
    name is purely role-based, not tier-based.
    """
    persona_info = index.persona_by_id(persona_id)
    if persona_info is not None:
        persona_md = _read_file(Path(persona_info.path) / "persona.md")
        if persona_md is not None:
            match = _PERSONA_HEADER_RE.search(persona_md)
            if match:
                return _canonicalize_persona_header(match.group(1).strip())
    return _display_name_from_id(_persona_dirname(persona_id))


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


def _expertise_applies_to(
    persona_id: str,
    expertise_info: ExpertiseInfo,
) -> bool:
    """Return True if *expertise_info* should be inlined into *persona_id*'s prompt.

    The rule (ADR-012): an empty ``applies_to`` list means "applies to every
    persona" (preserves pre-BEAN-259 behavior); otherwise the persona must be
    listed explicitly. The library indexer has already filtered out unknown
    persona IDs from ``applies_to`` (with a warning), so a non-empty list here
    is guaranteed to contain only real persona IDs.
    """
    if not expertise_info.applies_to:
        return True
    return persona_id in expertise_info.applies_to


def _get_emitted_expertise_ids(
    spec: CompositionSpec,
    library_index: LibraryIndex,
) -> list[str]:
    """Return the ordered list of expertise IDs whose source file will be
    emitted (i.e. ``conventions.md`` exists on disk).

    This is the same predicate ``_compile_expertise_section`` uses to decide
    whether to write ``ai/generated/expertise/<id>.md``. Surfaces it as a
    helper so other stages (agent headers, persona-scoped substitutions)
    can stay in sync without re-implementing the check.
    """
    emitted: list[str] = []
    for sel in sorted(spec.expertise, key=lambda s: (s.order, s.id)):
        info = library_index.expertise_by_id(sel.id)
        if info is None:
            continue
        if _expertise_entry_file(Path(info.path)) is not None:
            emitted.append(sel.id)
    return emitted


def _strip_frontmatter(text: str) -> str:
    """Drop a leading YAML frontmatter block (SPEC-019 pack metadata).

    Frontmatter is indexer metadata, not prompt content — compiled
    expertise files must not carry it.
    """
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end < 0:
        return text
    return text[end + 5:].lstrip("\n")


def _expertise_entry_file(expertise_dir: Path) -> Path | None:
    """Resolve the entry file for an expertise pack.

    ``conventions.md`` is the canonical entry file. Packs without one
    (all compliance/cloud/business packs as of 2026-07) fall back to their
    first ``.md`` file alphabetically — matching the indexer's primary-file
    rule — so no pack silently compiles to nothing (SPEC-003).
    """
    conventions = expertise_dir / "conventions.md"
    if conventions.is_file():
        return conventions
    candidates = sorted(expertise_dir.glob("*.md"))
    return candidates[0] if candidates else None


def _build_context(
    spec: CompositionSpec,
    emitted_expertise_ids: list[str] | None = None,
) -> dict[str, str]:
    """Build the shared template variable context from the composition spec.

    Use this for non-persona-scoped substitutions (e.g., expertise files).
    For persona-scoped substitutions, use ``_build_persona_context`` so that
    ``{{ strictness }}`` resolves to the per-persona strictness value.

    When ``emitted_expertise_ids`` is provided, ``{{ expertise }}`` resolves
    to only those IDs. Callers with access to a LibraryIndex should compute
    this via ``_get_emitted_expertise_ids`` so missing-source expertise is
    dropped from compiled prompts. When None, all spec expertise IDs are
    used (legacy behavior for callers without library access).
    """
    if emitted_expertise_ids is None:
        expertise_ids: list[str] = sorted(
            (s.id for s in spec.expertise),
            key=lambda sid: next(
                (s.order for s in spec.expertise if s.id == sid), 0
            ),
        )
    else:
        expertise_ids = list(emitted_expertise_ids)
    return {
        "project_name": spec.project.name,
        "expertise": ",".join(expertise_ids),
    }


def _build_persona_context(
    spec: CompositionSpec,
    persona_sel: PersonaSelection,
    emitted_expertise_ids: list[str] | None = None,
) -> dict[str, str]:
    """Build a context dict for substituting placeholders in a single persona's
    source files. Includes every shared key plus the persona's own ``strictness``.
    """
    ctx = _build_context(spec, emitted_expertise_ids)
    ctx["strictness"] = persona_sel.strictness.value
    return ctx


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
    spec: CompositionSpec | None = None,
) -> str | None:
    """Compile the section for a single persona.

    ``context`` must include ``strictness`` — callers build it via
    ``_build_persona_context`` so ``{{ strictness }}`` resolves to this
    persona's own strictness value.

    Per ADR-012, when persona sections embed expertise content (today they do
    not), only expertise where ``_expertise_applies_to(persona_id, info)`` is
    True contributes. This is a forward-compat guard: if and when this
    function starts inlining expertise, it must filter through that helper.

    Returns the assembled markdown text, or None if the persona directory
    is missing from the library.
    """
    persona_info = index.persona_by_id(persona_id)
    if persona_info is None:
        # Lazy-import to avoid a circular dependency between compiler and
        # library_indexer at module load time.
        from foundry_app.services.library_indexer import (
            format_unknown_persona_error,
        )
        warnings.append(format_unknown_persona_error(persona_id, index))
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

    # SPEC-012: member prompts carry their persona-relevant expertise —
    # the high-signal Defaults excerpt inline (token-budgeted by
    # _extract_expertise_highlights) plus a pointer to the full compiled
    # conventions file. The ADR-012 `_expertise_applies_to` filter gates
    # which expertise reaches which persona.
    if spec is not None:
        # Function-level import: agent_writer imports compiler at module
        # load, so this direction must stay lazy to avoid a cycle.
        from foundry_app.services.agent_writer import (
            _extract_expertise_highlights,
        )

        expertise_blocks: list[str] = []
        for sel in sorted(spec.expertise, key=lambda s: (s.order, s.id)):
            info = index.expertise_by_id(sel.id)
            if info is None or not _expertise_applies_to(persona_id, info):
                continue
            entry = _expertise_entry_file(Path(info.path))
            if entry is None:
                continue
            highlights = _extract_expertise_highlights(
                _substitute(entry.read_text(encoding="utf-8"), context)
            )
            block = [f"### {_display_name_from_id(sel.id)}"]
            if highlights:
                block.append(highlights)
            block.append(
                f"Full conventions: `ai/generated/expertise/{sel.id}.md`"
            )
            expertise_blocks.append("\n\n".join(block))
        if expertise_blocks:
            parts.append(
                "## Expertise Conventions\n\n" + "\n\n".join(expertise_blocks)
            )

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

    # conventions.md is the canonical entry file; packs without one compile
    # from ALL their .md files (sorted) so authored content is never silently
    # dropped (SPEC-003). Packs with conventions.md keep entry-only emission
    # to preserve the established token profile.
    conventions = _read_file(expertise_dir / "conventions.md")
    if conventions is not None:
        return _substitute(_strip_frontmatter(conventions).strip(), context)

    sibling_files = sorted(expertise_dir.glob("*.md"))
    if sibling_files:
        parts = [
            _strip_frontmatter(_read_file(path) or "") for path in sibling_files
        ]
        combined = "\n\n---\n\n".join(p.strip() for p in parts if p.strip())
        if combined:
            warnings.append(
                f"Expertise '{expertise_id}' has no conventions.md; "
                f"compiled from {len(sibling_files)} pack file(s) instead"
            )
            return _substitute(combined, context)

    warnings.append(f"Expertise '{expertise_id}' has no compilable .md files")
    return None


def _extract_first_sentence(text: str) -> str:
    """Extract the first meaningful sentence from markdown text."""
    for line in text.strip().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            # Take first sentence
            parts = re.split(r"(?<=[.!?])\s+", stripped, maxsplit=1)
            return parts[0] if parts else stripped[:120]
    return ""


def _build_lean_claude_md(
    spec: CompositionSpec,
    persona_descriptions: list[tuple[str, str, str]],
    expertise_ids: list[str],
) -> str:
    """Build a lean CLAUDE.md with project summary, tech stack, and pointers.

    Args:
        spec: The composition spec.
        persona_descriptions: List of ``(persona_id, display_name, one-line
            description)`` tuples. ``display_name`` is resolved upstream via
            ``_persona_display_name`` so acronyms and slashed names render
            correctly in the Team table.
        expertise_ids: Sorted list of expertise IDs included in the project.

    Returns:
        The assembled lean CLAUDE.md content.
    """
    sections: list[str] = []

    # --- Project header ---
    header = f"# {spec.project.name}"
    if spec.project.description:
        header += f"\n\n{spec.project.description}"
    sections.append(header)

    # --- Scope (BEAN-251 + BEAN-253) ---
    # Paired policy: the AI team works under ai/ (matching the narrow
    # Edit(ai/**) permission in settings.local.json); the human owns the
    # application source. Foundry does not scaffold stack-specific app
    # code — users initialize their app with a stack-appropriate command
    # (see docs/starter-stacks.md in the Foundry repo). See ADR-006.
    scope_lines = [
        "## Scope",
        "",
        "This project was generated by "
        "[Foundry](https://github.com/beekeeper-lab/foundry). "
        "The AI team produces plans, designs, reviews, and docs under "
        "`ai/`; the human initializes and implements the application "
        "source code. The `Edit(ai/**)` permission in "
        "`.claude/settings.local.json` matches this intent — agents "
        "write under `ai/`, humans write the app.",
        "",
        "Foundry does not scaffold stack-specific application code. "
        "Initialize your application with the stack-appropriate command "
        "— see `docs/starter-stacks.md` in the Foundry repo for common "
        "recipes.",
    ]
    sections.append("\n".join(scope_lines))

    # --- Tech Stack ---
    if expertise_ids:
        tech_lines = ["## Tech Stack", ""]
        tech_lines.append("| Technology | Source |")
        tech_lines.append("|------------|--------|")
        for eid in expertise_ids:
            display = _display_name_from_id(eid)
            tech_lines.append(
                f"| {display} | `ai/generated/expertise/{eid}.md` |"
            )
        sections.append("\n".join(tech_lines))

    # --- Directory Structure ---
    dir_lines = [
        "## Directory Structure",
        "",
        "```",
        ".claude/            # Claude Code config (agents, commands, hooks, skills)",
        "ai/",
        "  context/          # Project context and decisions",
        "  outputs/          # Persona working directories",
        "  generated/        # Generated prompts (members + expertise)",
        "  beans/            # Work tracking (bean workflow)",
        "  tasks/            # Seeded task lists",
        "```",
    ]
    sections.append("\n".join(dir_lines))

    # --- Team ---
    if persona_descriptions:
        team_lines = ["## Team", ""]
        team_lines.append("| Persona | Role | Agent | Full Prompt |")
        team_lines.append("|---------|------|-------|-------------|")
        for pid, display, desc in persona_descriptions:
            # Links must use the flattened leaf dirname (ADR-014): agents and
            # members are written flat regardless of extended/ tier.
            leaf = _persona_dirname(pid)
            team_lines.append(
                f"| {display} | {desc} "
                f"| `.claude/agents/{leaf}.md` "
                f"| `ai/generated/members/{leaf}.md` |"
            )
        sections.append("\n".join(team_lines))

    # --- Team Orchestration Model ---
    # Render only personas actually on the team (SPEC-018): name-dropping
    # absent specialists sent readers hunting for roles that don't exist.
    team_leaves = {_persona_dirname(pid) for pid, _, _ in persona_descriptions}
    bench = sorted(
        _display_name_from_id(leaf)
        for leaf in team_leaves - {"team-lead", "developer", "tech-qa"}
    )
    merge_owner = (
        "the **Integrator Merge Captain**"
        if "integrator-merge-captain" in team_leaves
        else "the **Team Lead** (no Merge Captain on this team)"
    )
    orchestration_lines = [
        "## Team Orchestration Model",
        "",
        "- **Team Lead is the orchestrator.** The Team Lead selects beans, "
        "decomposes work into tasks, assigns roles, and sequences execution.",
        "- The listed personas are an **available bench of specialists**, "
        "not the default active participants for every bean or task.",
        "- For **software development work**, the Team Lead must always "
        "assign:",
        "  - **Developer**",
        "  - **Tech-QA**",
    ]
    if bench:
        orchestration_lines.append(
            "- Other specialists on this team — "
            + ", ".join(f"**{name}**" for name in bench)
            + " — are assigned only when the bean or task requires them.",
        )
    orchestration_lines.append(
        f"- Merges to `main` (`/merge-bean`) are owned by {merge_owner}; "
        "see the library task taxonomy's 'Fallback When Absent' table for "
        "other role fallbacks.",
    )
    sections.append("\n".join(orchestration_lines))

    # --- Workflow (BEAN-268) ---
    workflow_lines = [
        "## Workflow",
        "",
        "Work is tracked using the **bean workflow**: each unit of work "
        "(feature, fix, chore) is a bean stored under "
        "`ai/beans/BEAN-NNN-<slug>/`. The backlog index is "
        "`ai/beans/_index.md`. See `ai/context/bean-workflow.md` for the "
        "full lifecycle.",
        "",
        "Day-1 slash commands:",
        "",
        "- `/long-run` — autonomous backlog processing "
        "(`.claude/commands/long-run.md`)",
        "- `/show-backlog` — display the current bean backlog "
        "(`.claude/commands/show-backlog.md`)",
        "- `/pick-bean` — pick the next approved bean and start work on "
        "it (`.claude/commands/pick-bean.md`)",
        "- `/new-bean` — create a new bean from a problem description "
        "(`.claude/commands/new-bean.md`)",
        "- `/spawn-task` — dispatch a single task to its assigned "
        "persona (`.claude/commands/spawn-task.md`)",
        "- `/review-beans` — review beans pending approval "
        "(`.claude/commands/review-beans.md`)",
        "",
        "Full command set: `.claude/commands/`.",
    ]
    sections.append("\n".join(workflow_lines))

    # --- Pointers ---
    pointer_lines = [
        "## Documentation",
        "",
        "Full persona prompts and expertise conventions are in `ai/generated/`:",
        "",
    ]
    if persona_descriptions:
        pointer_lines.append(
            "- **Persona prompts:** `ai/generated/members/<persona>.md`"
        )
    if expertise_ids:
        pointer_lines.append(
            "- **Expertise conventions:** `ai/generated/expertise/<expertise>.md`"
        )
    pointer_lines.append("- **Agent files:** `.claude/agents/<persona>.md`")
    pointer_lines.append("- **Project context:** `ai/context/`")
    sections.append("\n".join(pointer_lines))

    return "\n\n".join(sections) + "\n"


class AgnosticCompileResult(NamedTuple):
    """Result of the harness-agnostic half of the compile stage.

    Carries the ``StageResult`` for the emitted files plus the derived
    metadata (persona descriptions, emitted expertise IDs) that harness-
    specific emitters need to render their entry-point document.
    """

    result: StageResult
    persona_descriptions: list[tuple[str, str, str]]
    emitted_expertise_ids: list[str]


def compile_agnostic_outputs(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> AgnosticCompileResult:
    """Compile the harness-agnostic outputs of the compile stage.

    Writes the full persona prompts to ``ai/generated/members/`` and the
    expertise conventions to ``ai/generated/expertise/``, then checks the
    generated tree for unresolved placeholders. These files are consumed by
    any harness (IMP-08) — nothing Claude-specific is emitted here.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of available library components.
        library_root: Path to the root of the library directory.
        output_dir: Root directory for the generated project.

    Returns:
        An AgnosticCompileResult with the StageResult plus the persona
        descriptions and emitted expertise IDs needed by harness-specific
        emitters (e.g. ``compile_claude_outputs``).
    """
    root = Path(output_dir)
    lib_root = Path(library_root)
    wrote: list[str] = []
    warnings: list[str] = []

    # Determine which expertise will actually be emitted so persona templates
    # don't substitute {{ expertise | join(...) }} with missing-source IDs.
    emitted_expertise_ids = _get_emitted_expertise_ids(spec, library_index)
    context = _build_context(spec, emitted_expertise_ids)

    # Build persona name map and selected IDs for reference filtering
    name_to_id = _build_persona_name_map(library_index)
    selected_ids = {ps.id for ps in spec.team.personas}

    # --- Compile and write full persona files to ai/generated/members/ ---
    persona_descriptions: list[tuple[str, str, str]] = []
    if spec.team.personas:
        members_dir = root / "ai" / "generated" / "members"
        members_dir.mkdir(parents=True, exist_ok=True)

        for persona_sel in spec.team.personas:
            persona_ctx = _build_persona_context(
                spec, persona_sel, emitted_expertise_ids,
            )
            persona_section = _compile_persona_section(
                persona_sel.id, lib_root, library_index, persona_ctx, warnings,
                spec=spec,
            )
            if persona_section is not None:
                persona_section = _filter_persona_references(
                    persona_section, selected_ids, name_to_id,
                )
                # Write full content to separate file. Strip any ``extended/``
                # tier prefix from the id (ADR-014) so the on-disk filename
                # stays a flat leaf name.
                member_path = (
                    members_dir / f"{_persona_dirname(persona_sel.id)}.md"
                )
                member_path.write_text(persona_section + "\n", encoding="utf-8")
                rel = str(member_path.relative_to(root))
                wrote.append(rel)
                logger.info("Wrote: %s", member_path)

                # Extract one-line description for CLAUDE.md team table
                desc = _extract_first_sentence(persona_section)
                display = _persona_display_name(persona_sel.id, library_index)
                persona_descriptions.append((persona_sel.id, display, desc))

    # --- Compile and write full expertise files to ai/generated/expertise/ ---
    # ``emitted_expertise_ids`` (computed above) already identifies the
    # expertise whose source files will be written; iterate in that order so
    # the warning-emitting path in ``_compile_expertise_section`` still runs
    # for any missing-source expertise listed in the spec.
    sorted_expertise = sorted(spec.expertise, key=lambda s: (s.order, s.id))
    if sorted_expertise:
        expertise_dir = root / "ai" / "generated" / "expertise"
        expertise_dir.mkdir(parents=True, exist_ok=True)

        for expertise_sel in sorted_expertise:
            expertise_section = _compile_expertise_section(
                expertise_sel.id, lib_root, library_index, context, warnings,
            )
            if expertise_section is not None:
                exp_path = expertise_dir / f"{expertise_sel.id}.md"
                exp_path.write_text(expertise_section + "\n", encoding="utf-8")
                rel = str(exp_path.relative_to(root))
                wrote.append(rel)
                logger.info("Wrote: %s", exp_path)

    # Check for unresolved placeholders in member/expertise files
    generated_dir = root / "ai" / "generated"
    for fpath in generated_dir.rglob("*.md") if generated_dir.exists() else []:
        file_content = fpath.read_text(encoding="utf-8")
        unresolved = _PLACEHOLDER_RE.findall(file_content)
        if unresolved:
            unique = sorted(set(unresolved))
            rel = str(fpath.relative_to(root))
            warnings.append(
                f"Unresolved placeholders in {rel}: {', '.join(unique)}"
            )

    return AgnosticCompileResult(
        result=StageResult(wrote=wrote, warnings=warnings),
        persona_descriptions=persona_descriptions,
        emitted_expertise_ids=emitted_expertise_ids,
    )


def compile_claude_outputs(
    spec: CompositionSpec,
    output_dir: str | Path,
    persona_descriptions: list[tuple[str, str, str]],
    emitted_expertise_ids: list[str],
) -> StageResult:
    """Compile the Claude-specific outputs of the compile stage.

    Writes the lean CLAUDE.md entry-point document. This is the harness-
    specific half of the compile stage (IMP-08): a future HarnessTarget
    adapter replaces this function without touching
    ``compile_agnostic_outputs``.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory for the generated project.
        persona_descriptions: ``(persona_id, display_name, description)``
            tuples produced by ``compile_agnostic_outputs``.
        emitted_expertise_ids: Expertise IDs whose source was actually
            written, so the generated CLAUDE.md never carries broken links.

    Returns:
        A StageResult listing written files and any warnings.
    """
    root = Path(output_dir)

    content = _build_lean_claude_md(spec, persona_descriptions, emitted_expertise_ids)

    claude_md_path = root / "CLAUDE.md"
    claude_md_path.parent.mkdir(parents=True, exist_ok=True)
    claude_md_path.write_text(content, encoding="utf-8")
    logger.info("Wrote: %s", claude_md_path)

    return StageResult(wrote=["CLAUDE.md"], warnings=[])


def compile_project(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Compile CLAUDE.md and persona/expertise files from library components.

    Orchestrates the two halves of the compile stage: the harness-agnostic
    emission (``compile_agnostic_outputs`` — members + expertise under
    ai/generated/) and the Claude-specific emission
    (``compile_claude_outputs`` — the lean CLAUDE.md). The split keeps the
    agnostic half reusable when a future HarnessTarget adapter (IMP-08)
    supplies a different harness-specific emitter.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of available library components.
        library_root: Path to the root of the library directory.
        output_dir: Root directory for the generated project.

    Returns:
        A StageResult listing written files and any warnings.
    """
    agnostic = compile_agnostic_outputs(
        spec, library_index, library_root, output_dir,
    )
    claude = compile_claude_outputs(
        spec,
        output_dir,
        agnostic.persona_descriptions,
        agnostic.emitted_expertise_ids,
    )

    wrote = list(agnostic.result.wrote) + list(claude.wrote)
    warnings = list(agnostic.result.warnings) + list(claude.warnings)

    logger.info(
        "Compile complete: %d files written, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)
