"""Data contracts for Foundry: composition spec, generation manifest, library index."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

# --- Composition Spec (project-local: ai/team/composition.yml) ---


class ProjectIdentity(BaseModel):
    name: str
    slug: str
    subtitle: str = ""
    output_root: str = "./generated-projects"
    output_folder: str = ""
    created_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class StackSelection(BaseModel):
    id: str
    order: int = 10


class StackOverrides(BaseModel):
    notes_md: str = ""


class PersonaSelection(BaseModel):
    id: str
    include_agent: bool = True
    include_templates: bool = True
    strictness: str = "standard"  # light | standard | strict


class TeamConfig(BaseModel):
    personas: list[PersonaSelection] = Field(default_factory=list)


class HookPackSelection(BaseModel):
    id: str
    enabled: bool = True
    mode: str = "enforcing"  # enforcing | advisory


class HooksConfig(BaseModel):
    posture: str = "baseline"  # baseline | hardened | regulated
    packs: list[HookPackSelection] = Field(default_factory=list)


class GenerationOptions(BaseModel):
    seed_tasks: bool = True
    seed_mode: str = "detailed"  # detailed | kickoff | beans
    write_manifest: bool = True
    write_diff_report: bool = False
    inject_project_context: bool = True


class GitPolicy(BaseModel):
    allow_push: bool = True
    allow_force_push: bool = False
    allow_branch_delete: bool = False

class ShellPolicy(BaseModel):
    allow_sudo: bool = False
    allow_install: bool = True
    deny_patterns: list[str] = Field(default_factory=list)

class FileSystemPolicy(BaseModel):
    allow_outside_project: bool = False
    deny_patterns: list[str] = Field(default_factory=list)
    editable_dirs: list[str] = Field(
        default_factory=lambda: ["src/**", "tests/**", "ai/**"]
    )

class NetworkPolicy(BaseModel):
    allow_network: bool = True
    allow_external_apis: bool = True

class SecretPolicy(BaseModel):
    block_env_files: bool = True
    block_credentials: bool = True

class DestructiveOpsPolicy(BaseModel):
    allow_rm_rf: bool = False
    allow_reset_hard: bool = False
    allow_clean: bool = False

class SafetyConfig(BaseModel):
    preset: str = "baseline"  # permissive | baseline | hardened | custom
    git: GitPolicy = Field(default_factory=GitPolicy)
    shell: ShellPolicy = Field(default_factory=ShellPolicy)
    filesystem: FileSystemPolicy = Field(default_factory=FileSystemPolicy)
    network: NetworkPolicy = Field(default_factory=NetworkPolicy)
    secrets: SecretPolicy = Field(default_factory=SecretPolicy)
    destructive: DestructiveOpsPolicy = Field(default_factory=DestructiveOpsPolicy)


class CompositionSpec(BaseModel):
    """The authoritative project spec produced by the wizard and edited in the
    Composition Editor. Serialized as composition.yml."""

    project: ProjectIdentity
    stacks: list[StackSelection] = Field(default_factory=list)
    stack_overrides: StackOverrides = Field(default_factory=StackOverrides)
    team: TeamConfig = Field(default_factory=TeamConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    generation: GenerationOptions = Field(default_factory=GenerationOptions)


# --- Generation Manifest (produced each run: ai/generated/manifest.json) ---


class StageResult(BaseModel):
    wrote: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GenerationManifest(BaseModel):
    """Machine- and human-readable record of file operations from a generation run."""

    run_id: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H-%M-%SZ"
        )
    )
    library_version: str = ""  # git commit hash if available
    composition_snapshot: CompositionSpec | None = None
    stages: dict[str, StageResult] = Field(default_factory=dict)
    overlay_summary: OverlaySummary | None = None


# --- Overlay Models (used by overlay.py for overlay mode) ---


class FileAction(BaseModel):
    """Classification of a single file in the overlay plan."""

    rel_path: str
    action: str  # "create" | "unchanged" | "conflict" | "force_overwrite"
    reason: str = ""
    sidecar_path: str = ""


class OverlayPlan(BaseModel):
    """Complete plan for an overlay operation."""

    target_dir: str
    actions: list[FileAction] = Field(default_factory=list)
    orphans: list[str] = Field(default_factory=list)

    @property
    def creates(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "create"]

    @property
    def unchanged(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "unchanged"]

    @property
    def conflicts(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "conflict"]

    @property
    def force_overwrites(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == "force_overwrite"]

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


class OverlaySummary(BaseModel):
    """Summary of overlay operation recorded in the manifest."""

    mode: str = "overlay"  # "overlay" | "dry_run"
    target_dir: str = ""
    files_created: int = 0
    files_unchanged: int = 0
    files_conflicted: int = 0
    files_force_overwritten: int = 0
    orphaned_files: list[str] = Field(default_factory=list)
    sidecars_written: list[str] = Field(default_factory=list)


# --- Library Index (computed on load: .foundry/cache/library_index.json) ---


class PersonaIndexEntry(BaseModel):
    id: str
    path: str
    files: list[str] = Field(default_factory=list)
    templates: list[str] = Field(default_factory=list)


class StackIndexEntry(BaseModel):
    id: str
    path: str
    files: list[str] = Field(default_factory=list)


class HookIndexEntry(BaseModel):
    id: str
    default_enabled: bool = True
    mode: str = "enforcing"


class SkillIndexEntry(BaseModel):
    id: str
    path: str
    files: list[str] = Field(default_factory=list)


class CommandIndexEntry(BaseModel):
    id: str
    path: str


class LibraryIndex(BaseModel):
    """Computed index created on app load from the library root."""

    root: str
    personas: list[PersonaIndexEntry] = Field(default_factory=list)
    stacks: list[StackIndexEntry] = Field(default_factory=list)
    hooks: list[HookIndexEntry] = Field(default_factory=list)
    skills: list[SkillIndexEntry] = Field(default_factory=list)
    commands: list[CommandIndexEntry] = Field(default_factory=list)

    @classmethod
    def from_library_path(cls, library_root: Path) -> LibraryIndex:
        """Scan a library directory and build the index."""
        root = library_root.resolve()
        personas: list[PersonaIndexEntry] = []
        stacks: list[StackIndexEntry] = []
        hooks: list[HookIndexEntry] = []
        skills: list[SkillIndexEntry] = []
        commands: list[CommandIndexEntry] = []

        # Scan personas
        personas_dir = root / "personas"
        if personas_dir.is_dir():
            for persona_dir in sorted(personas_dir.iterdir()):
                if not persona_dir.is_dir():
                    continue
                files = [
                    f.name
                    for f in persona_dir.iterdir()
                    if f.is_file() and f.suffix == ".md"
                ]
                templates_dir = persona_dir / "templates"
                templates = []
                if templates_dir.is_dir():
                    templates = [
                        f.name
                        for f in sorted(templates_dir.iterdir())
                        if f.is_file() and f.suffix == ".md"
                    ]
                personas.append(
                    PersonaIndexEntry(
                        id=persona_dir.name,
                        path=str(persona_dir.relative_to(root)),
                        files=sorted(files),
                        templates=templates,
                    )
                )

        # Scan stacks
        stacks_dir = root / "stacks"
        if stacks_dir.is_dir():
            for stack_dir in sorted(stacks_dir.iterdir()):
                if not stack_dir.is_dir():
                    continue
                files = [
                    f.name
                    for f in sorted(stack_dir.iterdir())
                    if f.is_file() and f.suffix == ".md"
                ]
                stacks.append(
                    StackIndexEntry(
                        id=stack_dir.name,
                        path=str(stack_dir.relative_to(root)),
                        files=files,
                    )
                )

        # Scan hooks
        hooks_dir = root / "claude" / "hooks"
        if hooks_dir.is_dir():
            for hook_file in sorted(hooks_dir.iterdir()):
                if hook_file.is_file() and hook_file.suffix == ".md":
                    hooks.append(
                        HookIndexEntry(
                            id=hook_file.stem,
                        )
                    )

        # Scan skills
        skills_dir = root / "claude" / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(skills_dir.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_files = [
                    f.name
                    for f in sorted(skill_dir.iterdir())
                    if f.is_file()
                ]
                skills.append(
                    SkillIndexEntry(
                        id=skill_dir.name,
                        path=str(skill_dir.relative_to(root)),
                        files=skill_files,
                    )
                )

        # Scan commands
        commands_dir = root / "claude" / "commands"
        if commands_dir.is_dir():
            for cmd_file in sorted(commands_dir.iterdir()):
                if cmd_file.is_file() and cmd_file.suffix == ".md":
                    commands.append(
                        CommandIndexEntry(
                            id=cmd_file.stem,
                            path=str(cmd_file.relative_to(root)),
                        )
                    )

        return cls(
            root=str(root),
            personas=personas,
            stacks=stacks,
            hooks=hooks,
            skills=skills,
            commands=commands,
        )
