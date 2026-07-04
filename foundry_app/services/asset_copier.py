"""Asset copier service — copies library assets into a generated project."""

from __future__ import annotations

import filecmp
import logging
import shutil
from pathlib import Path

from foundry_app.core.models import CompositionSpec, LibraryIndex, StageResult

logger = logging.getLogger(__name__)

# Library subdirectories copied unconditionally (source_subdir, dest_subdir).
# Note: ``claude/commands`` and ``claude/skills`` are handled by dedicated copiers
# (selection-aware) and are NOT in this list.
_GLOBAL_ASSET_DIRS = [
    ("claude/settings", ".claude"),
    ("process/beans", "ai/beans"),
    ("process/context", "ai/context"),
]

# .claude/ destinations — skipped when subtree mode is active.
_CLAUDE_DEST_PREFIX = ".claude"

# Map: expertise id → dev-loop stack subdirectory under claude/commands/dev-loop/
# The first match (in spec.expertise order) wins.
_DEV_LOOP_STACK_BY_EXPERTISE: dict[str, str] = {
    "python": "python",
    "python-qt-pyside6": "python",
    "node": "node",
    "react": "node",
    "typescript": "node",
    "react-native": "node",
    "frontend-build-tooling": "node",
    # SPEC-021: every language pack gets a dev-loop command set.
    "go": "go",
    "rust": "rust",
    "dotnet": "dotnet",
    "java": "jvm",
    "kotlin": "jvm",
    "dart": "dart",
    "flutter": "flutter",
    "swift": "swift",
    "r": "r",
    "llm-applications": "python",
}

# Directory name (under claude/commands/) holding stack-keyed dev-loop command sets.
_DEV_LOOP_DIRNAME = "dev-loop"

# Map: governance command filename (under claude/commands/) → personas that unlock it.
# When NONE of the listed personas is on the team, the command is NOT copied.
# Persona ids use the canonical ADR-014 reference form (extended personas
# carry the ``extended/`` tier prefix).
_GOVERNANCE_COMMANDS: dict[str, set[str]] = {
    "threat-model.md": {"extended/security-engineer"},
    "risk-liability.md": {"extended/legal-counsel", "extended/compliance-risk"},
}

# Map: governance skill name (skill directory or file under claude/skills/) → personas
# that unlock it.  When NONE of the listed personas is on the team, the skill is NOT copied.
# Persona ids use the canonical ADR-014 reference form.
_GOVERNANCE_SKILLS: dict[str, set[str]] = {
    "threat-model": {"extended/security-engineer"},
    "risk-liability": {"extended/legal-counsel", "extended/compliance-risk"},
    "ip-licensing": {"extended/legal-counsel"},
    "contract-review": {"extended/legal-counsel"},
    "regulatory-assessment": {
        "extended/legal-counsel",
        "extended/compliance-risk",
    },
    "legal-drafting": {"extended/legal-counsel"},
}

# Cross-project skills owned by ClaudeKit (`.claude/shared/skills/<name>/`) rather
# than by ai-team-library.  In library-copy mode, these names resolve from
# ``<claude_kit_root>/skills/<name>/`` instead of from the library's
# ``claude/skills/<name>/``.  Subtree mode does not consult this registry — the
# subtree already includes ``.claude/shared/skills/`` wholesale.
#
# Adding a skill here requires that its source files live at
# ``<claude_kit_root>/skills/<name>/`` and that the skill is NOT also present
# under ``ai-team-library/claude/skills/<name>/``.  See ADR-009 in
# ``ai/context/decisions.md`` for the full ownership criteria.
#
# ``_media_lib`` is the shared helper package for the media skills (env
# discovery, narration normalization + content hashing, cost summaries) — it
# is not user-invokable; the ``_`` prefix mirrors Foundry's ``internal:*``
# convention.  See BEAN-281 for the contract and the regex-order test that
# locks it in.
_KIT_DISTRIBUTED_SKILLS: tuple[str, ...] = (
    "_media_lib",
    "generate-audio",
    "generate-image",
    "generate-screen",
)


def _kit_distributed_skills(kit_root: Path) -> tuple[str, ...]:
    """Resolve the kit-distributed skill list.

    The kit's own ``kit-manifest.json`` (``distributed_skills``) is the
    source of truth (SPEC-027) — a hardcoded tuple here silently drifted
    whenever the kit added or moved a skill. The tuple above remains as a
    fallback for kit checkouts predating the manifest.
    """
    manifest = kit_root / "kit-manifest.json"
    if manifest.is_file():
        try:
            import json

            data = json.loads(manifest.read_text(encoding="utf-8"))
            skills = data.get("distributed_skills")
            if isinstance(skills, list) and all(isinstance(s, str) for s in skills):
                return tuple(skills)
        except (ValueError, OSError):
            logger.warning("Unreadable kit-manifest.json at %s", manifest)
    return _KIT_DISTRIBUTED_SKILLS


def _default_claude_kit_root() -> Path:
    """Return the bundled ClaudeKit submodule path (``<foundry_root>/.claude/shared/``).

    Resolved relative to this module's location: ``foundry_app/services/asset_copier.py``
    sits two parents below the foundry repo root, so ``parents[2]`` is the repo root.
    Callers may override the resolved path by passing ``claude_kit_root`` explicitly
    (useful for tests and for non-checkout-based invocations).
    """
    return Path(__file__).resolve().parents[2] / ".claude" / "shared"


def copy_assets(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
    claude_kit_root: str | Path | None = None,
) -> StageResult:
    """Copy library assets (templates, commands, hooks) into a generated project.

    Copies three categories of assets:
    1. **Persona templates** — per-persona, only when ``include_templates=True``
    2. **Commands** — from ``library/claude/commands/`` to ``.claude/commands/``
    3. **Hooks** — from ``library/claude/hooks/`` to ``.claude/hooks/``

    Skills are sourced from two locations:

    - **Kit-distributed skills** (names in ``_KIT_DISTRIBUTED_SKILLS``) resolve
      from ``<claude_kit_root>/skills/<name>/``.  These are cross-project skills
      owned by ClaudeKit.
    - **All other skills** resolve from ``<library_root>/claude/skills/<name>/``
      (the existing project-template skill location).

    Subtree mode skips ALL skill copying because ``.claude/shared/skills/``
    is already pulled in by ``git subtree add``.

    Overlay-safe: existing identical files are skipped; conflicts produce warnings.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of library contents (from library indexer).
        library_root: Absolute path to the library root directory.
        output_dir: Root directory of the generated project.
        claude_kit_root: Path to the ClaudeKit checkout (typically
            ``<foundry_root>/.claude/shared/``).  Defaults to the foundry repo's
            bundled submodule.  Callers may pass an explicit path for testing
            or for non-checkout-based invocations.  When the resolved path does
            not exist, kit-distributed skills are warned and skipped — generation
            continues so library-copy-mode remains best-effort.

    Returns:
        A StageResult listing all files copied and any warnings.
    """
    lib_root = Path(library_root)
    out_root = Path(output_dir)
    kit_root = Path(claude_kit_root) if claude_kit_root is not None else _default_claude_kit_root()
    wrote: list[str] = []
    warnings: list[str] = []

    subtree_mode = bool(spec.generation.claude_kit_url)
    team_personas = {p.id for p in spec.team.personas}
    dev_loop_stack = _select_dev_loop_stack(spec)

    # --- Persona templates ---
    _copy_persona_templates(spec, library_index, lib_root, out_root, wrote, warnings)

    # --- Commands and skills (selection-aware) ---
    if subtree_mode:
        logger.debug("Subtree mode: skipping .claude/ command + skill copy")
    else:
        _copy_commands(
            team_personas, dev_loop_stack, lib_root, out_root, wrote, warnings,
        )
        _copy_skills(team_personas, lib_root, kit_root, out_root, wrote, warnings)

    # --- Other global assets (settings, process dirs) ---
    for src_subdir, dest_subdir in _GLOBAL_ASSET_DIRS:
        if subtree_mode and dest_subdir.startswith(_CLAUDE_DEST_PREFIX):
            # SPEC-027: settings must land in BOTH modes — the subtree brings
            # the kit's settings.json but never settings.local.json, so
            # subtree projects shipped with no permissions at all. The
            # copier's overlay logic handles files the subtree already has.
            if src_subdir == "claude/settings":
                logger.debug("Subtree mode: still copying %s", src_subdir)
            else:
                logger.debug(
                    "Subtree mode: skipping .claude/ asset dir %s", dest_subdir
                )
                continue
        _copy_directory_files(
            lib_root / src_subdir,
            out_root / dest_subdir,
            out_root,
            wrote,
            warnings,
        )

    # --- Hooks (selective — only enabled packs) ---
    if subtree_mode:
        logger.debug("Subtree mode: skipping hook copy (.claude/hooks/ comes from subtree)")
    else:
        _copy_selected_hooks(spec, lib_root, out_root, wrote, warnings)

    logger.info(
        "Asset copy complete: %d files copied, %d warnings",
        len(wrote),
        len(warnings),
    )

    return StageResult(wrote=wrote, warnings=warnings)


def _copy_persona_templates(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    lib_root: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy persona template files for each persona with include_templates=True."""
    for persona in spec.team.personas:
        if not persona.include_templates:
            logger.debug(
                "Skipping templates for persona '%s' (include_templates=False)",
                persona.id,
            )
            continue

        persona_info = library_index.persona_by_id(persona.id)
        if persona_info is None:
            warnings.append(f"Persona '{persona.id}' not found in library index")
            continue

        # Per ADR-014, persona.id may carry the 'extended/' prefix; the
        # source dir lives at persona_info.path (the canonical on-disk
        # location) and the destination uses the leaf directory name so
        # ai/outputs/ stays flat across tiers.
        src_dir = Path(persona_info.path) / "templates"
        dest_dir = out_root / "ai" / "outputs" / persona_info.dirname

        if not src_dir.is_dir():
            warnings.append(f"No templates directory for persona '{persona.id}'")
            continue

        if not persona_info.templates:
            warnings.append(f"Persona '{persona.id}' has no template files")
            continue

        _copy_directory_files(src_dir, dest_dir, out_root, wrote, warnings)


def _select_dev_loop_stack(spec: CompositionSpec) -> str | None:
    """Pick the dev-loop command stack to copy based on selected expertise.

    Walks ``spec.expertise`` in declared order and returns the subdirectory name
    (e.g. ``"python"``, ``"node"``) of the first expertise mapped in
    ``_DEV_LOOP_STACK_BY_EXPERTISE``.  Returns ``None`` if no selected expertise
    has a dev-loop mapping (in which case no dev-loop commands are copied).
    """
    for ex in spec.expertise:
        stack = _DEV_LOOP_STACK_BY_EXPERTISE.get(ex.id)
        if stack is not None:
            return stack
    return None


def _copy_commands(
    team_personas: set[str],
    dev_loop_stack: str | None,
    lib_root: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy ``claude/commands/`` to ``.claude/commands/`` with selection rules.

    - Top-level files in the governance map are skipped unless one of their
      unlocking personas is on the team.
    - The ``dev-loop/`` subdirectory is handled separately: only the picked
      stack's command set is copied (flattened into ``.claude/commands/``).
    - All other files copy unconditionally.
    """
    src_root = lib_root / "claude" / "commands"
    if not src_root.is_dir():
        logger.debug("Commands source directory does not exist: %s", src_root)
        return

    dest_root = out_root / ".claude" / "commands"
    dest_root.mkdir(parents=True, exist_ok=True)

    for src_entry in sorted(src_root.iterdir()):
        if src_entry.is_symlink():
            warnings.append(f"Skipping symlink: {src_entry.name}")
            continue

        # Dev-loop: pick the chosen stack's set, flattened into commands dir.
        if src_entry.is_dir() and src_entry.name == _DEV_LOOP_DIRNAME:
            if dev_loop_stack is None:
                logger.debug("No dev-loop stack selected — skipping dev-loop commands")
                continue
            stack_dir = src_entry / dev_loop_stack
            if not stack_dir.is_dir():
                warnings.append(
                    f"Dev-loop stack '{dev_loop_stack}' has no directory at {stack_dir}"
                )
                continue
            _copy_directory_files(stack_dir, dest_root, out_root, wrote, warnings)
            continue

        # Other subdirectories: recurse normally.
        if src_entry.is_dir():
            if src_entry.name == "__pycache__":
                continue
            _copy_directory_files(
                src_entry, dest_root / src_entry.name, out_root, wrote, warnings,
            )
            continue

        if not src_entry.is_file():
            continue

        # Governance gate.
        unlockers = _GOVERNANCE_COMMANDS.get(src_entry.name)
        if unlockers is not None and team_personas.isdisjoint(unlockers):
            logger.debug(
                "Governance command '%s' skipped (no unlocking persona on team)",
                src_entry.name,
            )
            continue

        _copy_one_file(src_entry, dest_root / src_entry.name, out_root, wrote, warnings)


def _copy_skills(
    team_personas: set[str],
    lib_root: Path,
    kit_root: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy skills to ``.claude/skills/`` with governance gating.

    Kit-distributed skill names come from the kit's manifest via
    ``_kit_distributed_skills`` (SPEC-027).

    Resolves each skill's source from one of two roots:

    - **Kit-distributed skills** (names in ``_KIT_DISTRIBUTED_SKILLS``) resolve
      from ``<kit_root>/skills/<name>/``.  When the kit path is missing, the
      skill is warned and skipped; generation does not abort.
    - **All other skills** resolve from ``<lib_root>/claude/skills/<name>/``
      (the existing project-template location).

    The set of skills to copy is the union of:

    - every entry under ``<lib_root>/claude/skills/`` (file or directory), and
    - every name in ``_KIT_DISTRIBUTED_SKILLS``.

    A name appearing in both the library and the registry resolves from the kit
    (the registry wins — that is its purpose).

    Skill entries listed in ``_GOVERNANCE_SKILLS`` are skipped unless one of
    their unlocking personas is on the team.  The governance gate applies
    equally to both sources.
    """
    kit_distributed = _kit_distributed_skills(kit_root)
    lib_skills_root = lib_root / "claude" / "skills"
    kit_skills_root = kit_root / "skills"
    dest_root = out_root / ".claude" / "skills"

    # Map each skill name to its source path. Registry entries win over library.
    sources: dict[str, Path] = {}

    if lib_skills_root.is_dir():
        for src_entry in sorted(lib_skills_root.iterdir()):
            if src_entry.is_symlink():
                warnings.append(f"Skipping symlink: {src_entry.name}")
                continue
            if src_entry.is_dir() and src_entry.name == "__pycache__":
                continue
            if not (src_entry.is_dir() or src_entry.is_file()):
                continue
            skill_id = src_entry.name if src_entry.is_dir() else src_entry.stem
            if skill_id in kit_distributed:
                # Registry overrides library: skip the library copy entirely.
                logger.debug(
                    "Skill '%s' is kit-distributed; ignoring library copy at %s",
                    skill_id,
                    src_entry,
                )
                continue
            sources[skill_id] = src_entry
    else:
        logger.debug("Skills source directory does not exist: %s", lib_skills_root)

    # Resolve kit-distributed skills from the kit.
    for skill_id in kit_distributed:
        kit_skill_path = kit_skills_root / skill_id
        if not kit_skill_path.exists():
            warnings.append(
                f"Kit-distributed skill '{skill_id}' missing from kit at "
                f"{kit_skill_path}"
            )
            logger.warning(
                "Kit-distributed skill '%s' missing at %s — skipping",
                skill_id,
                kit_skill_path,
            )
            continue
        sources[skill_id] = kit_skill_path

    if not sources:
        return

    dest_root.mkdir(parents=True, exist_ok=True)

    for skill_id in sorted(sources):
        src_entry = sources[skill_id]

        unlockers = _GOVERNANCE_SKILLS.get(skill_id)
        if unlockers is not None and team_personas.isdisjoint(unlockers):
            logger.debug(
                "Governance skill '%s' skipped (no unlocking persona on team)",
                skill_id,
            )
            continue

        if src_entry.is_dir():
            _copy_directory_files(
                src_entry, dest_root / src_entry.name, out_root, wrote, warnings,
            )
            continue

        if src_entry.is_file():
            _copy_one_file(src_entry, dest_root / src_entry.name, out_root, wrote, warnings)


def _copy_one_file(
    src_file: Path,
    dest_file: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy a single file overlay-safe (skip identical, warn on conflict)."""
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    rel_path = str(dest_file.relative_to(out_root))

    if dest_file.exists():
        if filecmp.cmp(str(src_file), str(dest_file), shallow=False):
            logger.debug("File already exists (identical), skipping: %s", rel_path)
        else:
            warnings.append(f"File already exists with different content: {rel_path}")
            logger.warning("File conflict, skipping: %s", rel_path)
        return

    shutil.copy2(src_file, dest_file)
    wrote.append(rel_path)
    logger.info("Copied asset: %s", rel_path)


def _copy_selected_hooks(
    spec: CompositionSpec,
    lib_root: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy hook files matching enabled hook packs, plus all hook scripts.

    Each hook pack ID maps to a file named ``{pack_id}.md`` in the library's
    ``claude/hooks/`` directory; only docs whose stem matches an enabled pack
    are copied. Executable hook scripts (``*.py``) are ALWAYS copied — the
    settings.json hook wiring references them regardless of pack selection
    (SPEC-004).
    """
    enabled_ids = {p.id for p in spec.hooks.packs if p.enabled}

    src_dir = lib_root / "claude" / "hooks"
    if not src_dir.is_dir():
        logger.debug("Hook source directory does not exist: %s", src_dir)
        return

    dest_dir = out_root / ".claude" / "hooks"
    dest_dir.mkdir(parents=True, exist_ok=True)

    for src_entry in sorted(src_dir.iterdir()):
        if src_entry.is_symlink():
            warnings.append(f"Skipping symlink: {src_entry.name}")
            continue

        if not src_entry.is_file():
            continue

        if src_entry.suffix != ".py" and src_entry.stem not in enabled_ids:
            logger.debug("Hook '%s' not in enabled packs, skipping", src_entry.stem)
            continue

        dest_file = dest_dir / src_entry.name
        rel_path = str(dest_file.relative_to(out_root))

        if dest_file.exists():
            if filecmp.cmp(str(src_entry), str(dest_file), shallow=False):
                logger.debug("File already exists (identical), skipping: %s", rel_path)
            else:
                warnings.append(f"File already exists with different content: {rel_path}")
                logger.warning("File conflict, skipping: %s", rel_path)
            continue

        shutil.copy2(src_entry, dest_file)
        wrote.append(rel_path)
        logger.info("Copied hook: %s", rel_path)


def _copy_directory_files(
    src_dir: Path,
    dest_dir: Path,
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy all files from src_dir to dest_dir recursively, overlay-safe.

    Recurses into subdirectories (e.g. skill folders like ``long-run/SKILL.md``)
    while preserving the directory structure.  Skips ``__pycache__`` directories.
    """
    if not src_dir.is_dir():
        logger.debug("Source directory does not exist, skipping: %s", src_dir)
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    for src_entry in sorted(src_dir.iterdir()):
        if src_entry.is_symlink():
            warnings.append(f"Skipping symlink: {src_entry.name}")
            continue

        # Recurse into subdirectories
        if src_entry.is_dir():
            if src_entry.name == "__pycache__":
                continue
            _copy_directory_files(
                src_entry,
                dest_dir / src_entry.name,
                out_root,
                wrote,
                warnings,
            )
            continue

        if not src_entry.is_file():
            continue

        dest_file = dest_dir / src_entry.name
        rel_path = str(dest_file.relative_to(out_root))

        if dest_file.exists():
            if filecmp.cmp(str(src_entry), str(dest_file), shallow=False):
                logger.debug("File already exists (identical), skipping: %s", rel_path)
            else:
                warnings.append(f"File already exists with different content: {rel_path}")
                logger.warning("File conflict, skipping: %s", rel_path)
            continue

        shutil.copy2(src_entry, dest_file)
        wrote.append(rel_path)
        logger.info("Copied asset: %s", rel_path)
