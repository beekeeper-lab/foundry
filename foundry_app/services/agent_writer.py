"""Agent writer service — generates .claude/agents/<persona>.md files."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from foundry_app.core.models import (
    CompositionSpec,
    LibraryIndex,
    StageResult,
    _persona_dirname,
)
from foundry_app.services.compiler import (
    _PLACEHOLDER_RE,
    _build_context,
    _build_persona_context,
    _expertise_applies_to,
    _expertise_entry_file,
    _get_emitted_expertise_ids,
    _substitute,
)

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Max number of operating principles / key rules to extract per persona
_MAX_KEY_RULES = 5

# ---------------------------------------------------------------------------
# Model tiers and tool presets (SPEC-011). The library's per-persona
# defaults.yml files use SEMANTIC names; the concrete mapping lives only
# here so model churn is a one-line change, never a library-wide edit.
# Known tool names dated 2026-07; the harness set evolves, so unknown
# names WARN rather than fail (see validator).
# ---------------------------------------------------------------------------

MODEL_TIERS: dict[str, str] = {
    "strongest": "opus",
    "standard": "sonnet",
    "fast": "haiku",
}
_CONCRETE_MODELS = frozenset({"opus", "sonnet", "haiku", "inherit"})

# None means "emit no tools key" (all tools available).
TOOL_PRESETS: dict[str, list[str] | None] = {
    "full": None,
    # Reviewers: read + search + run checks, but no edits to source.
    "read-review": ["Read", "Grep", "Glob", "Bash"],
    # Doc-centric roles: author documents, never run shell commands.
    "docs-only": ["Read", "Grep", "Glob", "Write", "Edit"],
}

KNOWN_TOOLS = frozenset({
    "Read", "Write", "Edit", "NotebookEdit", "Bash", "Grep", "Glob",
    "WebFetch", "WebSearch", "Agent", "TodoWrite", "AskUserQuestion",
})


def _load_persona_defaults(persona_dir: Path) -> dict[str, str]:
    """Read the persona's defaults.yml ({model: <tier>, tools: <preset>})."""
    path = persona_dir / "defaults.yml"
    if not path.is_file():
        return {}
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:  # malformed defaults must never break generation
        logger.warning("Unparseable defaults.yml at %s", path)
        return {}


def resolve_model(value: str | None) -> str | None:
    """Resolve a tier or concrete alias to the frontmatter model value."""
    if value is None:
        return None
    if value in MODEL_TIERS:
        return MODEL_TIERS[value]
    return value  # concrete alias (validated elsewhere)


def resolve_tools(value: str | list[str] | None) -> list[str] | None:
    """Resolve a preset name or explicit list to a tool list (None = all)."""
    if value is None:
        return None
    if isinstance(value, str):
        return TOOL_PRESETS.get(value)
    return list(value)

# Max lines of expertise conventions to include as highlights
_MAX_EXPERTISE_HIGHLIGHT_LINES = 15


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


def _extract_expertise_highlights(conventions_text: str) -> str:
    """Extract the key highlights from an expertise conventions.md file.

    Captures the Defaults section, soft-capped at _MAX_EXPERTISE_HIGHLIGHT_LINES.
    Truncation is fence-aware: if the cap is reached while inside a fenced code
    block (``` ... ```), extraction continues until the fence closes so the
    emitted excerpt never has an unbalanced fence. A hard cap bounds runaway
    on malformed sources; if the source still ends with an open fence, the
    dangling opener (and lines after it) are dropped.
    """
    lines = conventions_text.strip().splitlines()
    highlights: list[str] = []
    in_defaults = False
    fence_open = False
    hard_cap = _MAX_EXPERTISE_HIGHLIGHT_LINES * 4

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            continue
        if stripped.startswith("---"):
            continue
        if not stripped:
            if highlights:
                highlights.append("")
            continue

        if stripped == "## Defaults":
            in_defaults = True
            continue
        if in_defaults:
            if stripped.startswith("## "):
                in_defaults = False
            else:
                highlights.append(stripped)
                if stripped.startswith("```"):
                    fence_open = not fence_open

        if len(highlights) >= hard_cap:
            break
        if len(highlights) >= _MAX_EXPERTISE_HIGHLIGHT_LINES and not fence_open:
            break

    # Safety net: if we still ended inside an open fence (malformed source or
    # hard cap tripped mid-block), drop everything from the last opener
    # onward so the output has balanced fences.
    if fence_open:
        for i in range(len(highlights) - 1, -1, -1):
            if highlights[i].startswith("```"):
                highlights = highlights[:i]
                break

    return "\n".join(highlights).strip()


def write_agents(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Generate .claude/agents/<persona>.md files for each selected persona.

    Each agent file combines persona identity with expertise context into a
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

    # Gather expertise info. Only list expertise whose source file will
    # actually be emitted — a missing-source expertise produces a warning
    # elsewhere but must not appear as a "zombie" entry in agent headers.
    # Keep (id, info) pairs so each persona's header can list only the
    # expertise that actually applies to it (SPEC-012 over-claim fix).
    emitted_expertise_ids = _get_emitted_expertise_ids(spec, library_index)
    emitted_expertise_infos = [
        (eid, library_index.expertise_by_id(eid))
        for eid in emitted_expertise_ids
    ]

    # Shared context — used to render non-persona-scoped fragments such as
    # expertise conventions. Persona-scoped fragments get their own context
    # built inside the per-persona loop so {{ strictness }} resolves correctly.
    shared_context = _build_context(spec, emitted_expertise_ids)

    # Pre-compute the unfiltered expertise highlights so we don't re-read
    # every expertise file once per persona. Each entry retains its source
    # ExpertiseInfo so the per-persona loop can apply the ADR-012 filter.
    # Each item: {"name", "highlights", "info"}. Missing-source expertise
    # is dropped here once (with a warning) rather than per-persona.
    all_expertise_sections: list[dict[str, object]] = []
    seen_missing: set[str] = set()
    for expertise_sel in spec.expertise:
        expertise_info = library_index.expertise_by_id(expertise_sel.id)
        if expertise_info is None:
            if expertise_sel.id not in seen_missing:
                warnings.append(
                    f"Expertise '{expertise_sel.id}' not found in library index"
                )
                seen_missing.add(expertise_sel.id)
            continue

        entry_path = _expertise_entry_file(Path(expertise_info.path))
        if entry_path is not None:
            conventions_text = _substitute(
                entry_path.read_text(encoding="utf-8"), shared_context,
            )
            highlights = _extract_expertise_highlights(conventions_text)
            if highlights:
                all_expertise_sections.append({
                    "name": expertise_sel.id.replace("-", " ").title(),
                    "highlights": highlights,
                    "info": expertise_info,
                })

    # Generate agent file for each persona
    agents_dir = out_root / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    for persona_sel in spec.team.personas:
        if not persona_sel.include_agent:
            continue
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

        # Substitute placeholders in the source before extracting fragments.
        # The template's outer render does not recursively resolve Jinja
        # expressions that appear inside variable values, so extracted strings
        # like {{ project_name }} would otherwise leak through verbatim.
        persona_ctx = _build_persona_context(
            spec, persona_sel, emitted_expertise_ids,
        )
        persona_text = _substitute(
            persona_path.read_text(encoding="utf-8"), persona_ctx,
        )

        # Build role name: expertise + persona (e.g., "Python Developer").
        # Use the emitted list so the role name never derives from a
        # missing-source expertise.
        primary_expertise = (
            emitted_expertise_ids[0].replace("-", " ").title()
            if emitted_expertise_ids
            else ""
        )
        # Strip any ``extended/`` tier prefix (ADR-014) before producing the
        # human-readable role name; the tier is metadata, not part of the role.
        persona_title = _persona_dirname(persona_sel.id).replace("-", " ").title()
        role_name = (
            f"{primary_expertise} {persona_title}".strip()
            if primary_expertise
            else persona_title
        )

        # ADR-012 LOAD-BEARING change: filter expertise per persona. Each
        # expertise's ## Applies To list governs whether its highlights get
        # inlined into THIS persona's agent file. Empty applies_to means
        # "all personas" (preserves pre-BEAN-259 behavior for unannotated
        # expertise files).
        expertise_sections: list[dict[str, str]] = [
            {"name": entry["name"], "highlights": entry["highlights"]}
            for entry in all_expertise_sections
            if _expertise_applies_to(persona_sel.id, entry["info"])
        ]

        leaf = _persona_dirname(persona_sel.id)
        role_description = _extract_role_description(persona_text)
        # Frontmatter description drives Claude Code's delegation routing;
        # it must be single-line and safe inside double quotes.
        agent_description = (
            f"{role_name}. {role_description}" if role_description else role_name
        )
        agent_description = " ".join(agent_description.split()).replace('"', "'")

        # Model/tools: composition override wins, else library defaults.yml,
        # else omit the key entirely (inherit session model / all tools).
        defaults = _load_persona_defaults(Path(persona_info.path))
        agent_model = resolve_model(
            persona_sel.model
            if persona_sel.model is not None
            else defaults.get("model")
        )
        agent_tools = resolve_tools(
            persona_sel.tools
            if persona_sel.tools is not None
            else defaults.get("tools")
        )
        if agent_model == "inherit":
            agent_model = None

        # Header lists only expertise applicable to THIS persona — the
        # inlined sections below are ADR-012-filtered, so a full-project
        # list would over-claim (SPEC-012).
        applicable_ids = [
            eid for eid, info in emitted_expertise_infos
            if info is not None and _expertise_applies_to(persona_sel.id, info)
        ]
        expertise_names = (
            ", ".join(applicable_ids) if applicable_ids else "General"
        )

        context = {
            "agent_name": leaf,
            "agent_description": agent_description,
            "agent_model": agent_model,
            "agent_tools": agent_tools,
            "role_name": role_name,
            "role_description": role_description,
            "expertise_names": expertise_names,
            "mission": _extract_mission(persona_text),
            "key_rules": _extract_key_rules(persona_text),
            "expertise_sections": expertise_sections,
        }

        content = template.render(**context)
        # Use the leaf directory name so .claude/agents/ stays a flat
        # directory regardless of tier (ADR-014).
        agent_file = agents_dir / f"{leaf}.md"
        agent_file.write_text(content, encoding="utf-8")

        rel_path = str(agent_file.relative_to(out_root))
        wrote.append(rel_path)
        logger.info("Wrote agent file: %s", rel_path)

    # Placeholder-leakage guard: scan every written agent file and surface
    # any remaining {{ ... }} expressions as warnings so the leak isn't silent.
    for rel in wrote:
        fpath = out_root / rel
        unresolved = _PLACEHOLDER_RE.findall(fpath.read_text(encoding="utf-8"))
        if unresolved:
            unique = sorted(set(unresolved))
            warnings.append(
                f"Unresolved placeholders in {rel}: {', '.join(unique)}"
            )

    logger.info(
        "Agent writer complete: %d files written, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)
