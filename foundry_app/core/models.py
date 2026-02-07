"""Data contracts for Foundry: composition spec, generation manifest, library index."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

# --- Composition Spec (project-local: ai/team/composition.yml) ---


class ProjectIdentity(BaseModel):
    name: str
    slug: str
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
    write_manifest: bool = True
    write_diff_report: bool = False


class CompositionSpec(BaseModel):
    """The authoritative project spec produced by the wizard and edited in the
    Composition Editor. Serialized as composition.yml."""

    project: ProjectIdentity
    stacks: list[StackSelection] = Field(default_factory=list)
    stack_overrides: StackOverrides = Field(default_factory=StackOverrides)
    team: TeamConfig = Field(default_factory=TeamConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
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


class LibraryIndex(BaseModel):
    """Computed index created on app load from the library root."""

    root: str
    personas: list[PersonaIndexEntry] = Field(default_factory=list)
    stacks: list[StackIndexEntry] = Field(default_factory=list)
    hooks: list[HookIndexEntry] = Field(default_factory=list)

    @classmethod
    def from_library_path(cls, library_root: Path) -> LibraryIndex:
        """Scan a library directory and build the index."""
        root = library_root.resolve()
        personas: list[PersonaIndexEntry] = []
        stacks: list[StackIndexEntry] = []
        hooks: list[HookIndexEntry] = []

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

        return cls(
            root=str(root),
            personas=personas,
            stacks=stacks,
            hooks=hooks,
        )
