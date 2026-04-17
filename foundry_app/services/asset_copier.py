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
}

# Directory name (under claude/commands/) holding stack-keyed dev-loop command sets.
_DEV_LOOP_DIRNAME = "dev-loop"

# Map: governance command filename (under claude/commands/) → personas that unlock it.
# When NONE of the listed personas is on the team, the command is NOT copied.
_GOVERNANCE_COMMANDS: dict[str, set[str]] = {
    "threat-model.md": {"security-engineer"},
    "risk-liability.md": {"legal-counsel", "compliance-risk"},
}

# Map: governance skill name (skill directory or file under claude/skills/) → personas
# that unlock it.  When NONE of the listed personas is on the team, the skill is NOT copied.
_GOVERNANCE_SKILLS: dict[str, set[str]] = {
    "threat-model": {"security-engineer"},
    "risk-liability": {"legal-counsel", "compliance-risk"},
    "ip-licensing": {"legal-counsel"},
    "contract-review": {"legal-counsel"},
    "regulatory-assessment": {"legal-counsel", "compliance-risk"},
    "legal-drafting": {"legal-counsel"},
}


def copy_assets(
    spec: CompositionSpec,
    library_index: LibraryIndex,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Copy library assets (templates, commands, hooks) into a generated project.

    Copies three categories of assets:
    1. **Persona templates** — per-persona, only when ``include_templates=True``
    2. **Commands** — from ``library/claude/commands/`` to ``.claude/commands/``
    3. **Hooks** — from ``library/claude/hooks/`` to ``.claude/hooks/``

    Overlay-safe: existing identical files are skipped; conflicts produce warnings.

    Args:
        spec: The composition spec describing the project.
        library_index: Index of library contents (from library indexer).
        library_root: Absolute path to the library root directory.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing all files copied and any warnings.
    """
    lib_root = Path(library_root)
    out_root = Path(output_dir)
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
        _copy_skills(team_personas, lib_root, out_root, wrote, warnings)

    # --- Other global assets (settings, process dirs) ---
    for src_subdir, dest_subdir in _GLOBAL_ASSET_DIRS:
        if subtree_mode and dest_subdir.startswith(_CLAUDE_DEST_PREFIX):
            logger.debug("Subtree mode: skipping .claude/ asset dir %s", dest_subdir)
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

        src_dir = lib_root / "personas" / persona.id / "templates"
        dest_dir = out_root / "ai" / "outputs" / persona.id

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
    out_root: Path,
    wrote: list[str],
    warnings: list[str],
) -> None:
    """Copy ``claude/skills/`` to ``.claude/skills/`` with governance gating.

    Skill entries (file or directory) listed in ``_GOVERNANCE_SKILLS`` are
    skipped unless one of their unlocking personas is on the team.  All other
    skills copy unconditionally.
    """
    src_root = lib_root / "claude" / "skills"
    if not src_root.is_dir():
        logger.debug("Skills source directory does not exist: %s", src_root)
        return

    dest_root = out_root / ".claude" / "skills"
    dest_root.mkdir(parents=True, exist_ok=True)

    for src_entry in sorted(src_root.iterdir()):
        if src_entry.is_symlink():
            warnings.append(f"Skipping symlink: {src_entry.name}")
            continue

        # Skill identifier: directory name, or file stem for flat-file skills.
        skill_id = src_entry.name if src_entry.is_dir() else src_entry.stem
        unlockers = _GOVERNANCE_SKILLS.get(skill_id)
        if unlockers is not None and team_personas.isdisjoint(unlockers):
            logger.debug(
                "Governance skill '%s' skipped (no unlocking persona on team)",
                skill_id,
            )
            continue

        if src_entry.is_dir():
            if src_entry.name == "__pycache__":
                continue
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
    """Copy only hook files matching enabled hook packs from the spec.

    Each hook pack ID maps to a file named ``{pack_id}.md`` in the library's
    ``claude/hooks/`` directory.  Only files whose stem matches an enabled pack
    are copied.  If no packs are enabled, no hooks are copied at all.
    """
    enabled_ids = {p.id for p in spec.hooks.packs if p.enabled}

    if not enabled_ids:
        logger.debug("No hook packs enabled — skipping hook copy")
        return

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

        if src_entry.stem not in enabled_ids:
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
