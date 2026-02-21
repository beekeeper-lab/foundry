"""Pydantic data models for Foundry composition specs, safety configs, and manifests."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Strictness(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    STRICT = "strict"


class HookMode(str, Enum):
    ENFORCING = "enforcing"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"


class Posture(str, Enum):
    BASELINE = "baseline"
    HARDENED = "hardened"
    REGULATED = "regulated"


class SeedMode(str, Enum):
    DETAILED = "detailed"
    KICKOFF = "kickoff"


class FileActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SKIP = "skip"


# ---------------------------------------------------------------------------
# Project identity
# ---------------------------------------------------------------------------

def _validate_safe_id(v: str, field_name: str) -> str:
    """Reject IDs containing path traversal sequences or path separators."""
    if ".." in v or "/" in v or "\\" in v:
        raise ValueError(
            f"{field_name} must not contain '..', '/', or '\\', got: {v!r}"
        )
    return v


def _validate_safe_path(v: str, field_name: str) -> str:
    """Reject paths with '..' components (but allow relative and absolute)."""
    from pathlib import PurePosixPath

    parts = PurePosixPath(v).parts
    if ".." in parts:
        raise ValueError(
            f"{field_name} must not contain '..' path components, got: {v!r}"
        )
    return v


class ProjectIdentity(BaseModel):
    """Top-level project metadata."""

    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Human-readable project name",
    )
    slug: str = Field(
        ..., min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$",
        description="URL/filesystem-safe identifier",
    )
    output_root: str = Field(
        default="./generated-projects", max_length=500,
        description="Parent directory for generated output",
    )
    output_folder: str | None = Field(
        default=None, max_length=200,
        description="Specific subfolder name; defaults to slug if omitted",
    )

    @field_validator("output_root")
    @classmethod
    def validate_output_root(cls, v: str) -> str:
        return _validate_safe_path(v, "output_root")

    @field_validator("output_folder")
    @classmethod
    def validate_output_folder(cls, v: str | None) -> str | None:
        if v is not None:
            _validate_safe_id(v, "output_folder")
        return v

    @property
    def resolved_output_folder(self) -> str:
        return self.output_folder or self.slug


# ---------------------------------------------------------------------------
# Expertise selection
# ---------------------------------------------------------------------------

class ExpertiseSelection(BaseModel):
    """A single expertise pack chosen for the project."""

    id: str = Field(
        ..., min_length=1, max_length=100,
        description="Expertise identifier (e.g. 'python')",
    )
    order: int = Field(default=0, description="Sort order when compiling prompts")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return _validate_safe_id(v, "expertise id")


class ExpertiseOverrides(BaseModel):
    """Optional per-expertise overrides — reserved for future extensibility.

    TODO: Currently unused. Remove if not needed by v2.0.
    """

    expertise_id: str
    overrides: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Architecture & cloud
# ---------------------------------------------------------------------------

class ArchitecturePattern(str, Enum):
    MONOLITH = "monolith"
    MODULAR_MONOLITH = "modular-monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event-driven"


class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    SELF_HOSTED = "self-hosted"


class ArchitectureConfig(BaseModel):
    """Architecture patterns and cloud providers selected for the project."""

    patterns: list[ArchitecturePattern] = Field(
        default_factory=list,
        description="Selected architecture patterns",
    )
    cloud_providers: list[CloudProvider] = Field(
        default_factory=list,
        description="Selected cloud deployment targets",
    )


# ---------------------------------------------------------------------------
# Persona / team
# ---------------------------------------------------------------------------

class PersonaSelection(BaseModel):
    """A single persona chosen for the project team."""

    id: str = Field(
        ..., min_length=1, max_length=100,
        description="Persona identifier (e.g. 'developer')",
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return _validate_safe_id(v, "persona id")
    include_agent: bool = Field(default=True, description="Generate .claude/agents/ file")
    include_templates: bool = Field(default=True, description="Copy persona templates")
    strictness: Strictness = Field(
        default=Strictness.STANDARD,
        description="Validation strictness for this persona",
    )


class TeamConfig(BaseModel):
    """Team composition — which personas are included."""

    personas: list[PersonaSelection] = Field(
        default_factory=list,
        description="Ordered list of personas on the team",
    )


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

class HookPackSelection(BaseModel):
    """A single hook pack chosen for the project."""

    id: str = Field(..., min_length=1, max_length=100, description="Hook pack identifier")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return _validate_safe_id(v, "hook pack id")
    category: str = Field(default="", description="Hook category (git, az, code-quality)")
    enabled: bool = Field(default=True)
    mode: HookMode = Field(default=HookMode.ENFORCING)


class HooksConfig(BaseModel):
    """Hook configuration for the project."""

    posture: Posture = Field(default=Posture.BASELINE, description="Safety posture preset")
    packs: list[HookPackSelection] = Field(
        default_factory=list,
        description="Selected hook packs",
    )


# ---------------------------------------------------------------------------
# Safety policies
# ---------------------------------------------------------------------------

class GitPolicy(BaseModel):
    """Git operation safety policy."""

    allow_push: bool = Field(default=True)
    allow_force_push: bool = Field(default=False)
    allow_branch_delete: bool = Field(default=False)
    protected_branches: list[str] = Field(default_factory=lambda: ["main", "master"])


class ShellPolicy(BaseModel):
    """Shell command safety policy."""

    allow_shell: bool = Field(default=True)
    blocked_commands: list[str] = Field(default_factory=list)
    blocked_patterns: list[str] = Field(default_factory=list)


class FileSystemPolicy(BaseModel):
    """Filesystem access safety policy."""

    allow_write: bool = Field(default=True)
    allow_delete: bool = Field(default=False)
    protected_paths: list[str] = Field(default_factory=list)
    allowed_extensions: list[str] = Field(default_factory=list)


class NetworkPolicy(BaseModel):
    """Network access safety policy."""

    allow_network: bool = Field(default=True)
    allowed_domains: list[str] = Field(default_factory=list)
    blocked_domains: list[str] = Field(default_factory=list)


class SecretPolicy(BaseModel):
    """Secret/credential safety policy."""

    scan_for_secrets: bool = Field(default=True)
    block_on_secret: bool = Field(default=True)
    secret_patterns: list[str] = Field(default_factory=list)

    @field_validator("secret_patterns")
    @classmethod
    def validate_secret_patterns(cls, v: list[str]) -> list[str]:
        import re

        for i, pattern in enumerate(v):
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValueError(
                    f"secret_patterns[{i}] is not a valid regex: {exc}"
                ) from exc
        return v


class DestructiveOpsPolicy(BaseModel):
    """Policy for destructive operations."""

    allow_destructive: bool = Field(default=False)
    require_confirmation: bool = Field(default=True)
    blocked_operations: list[str] = Field(default_factory=list)


class SafetyConfig(BaseModel):
    """Aggregate safety configuration composed of sub-policies."""

    git: GitPolicy = Field(default_factory=GitPolicy)
    shell: ShellPolicy = Field(default_factory=ShellPolicy)
    filesystem: FileSystemPolicy = Field(default_factory=FileSystemPolicy)
    network: NetworkPolicy = Field(default_factory=NetworkPolicy)
    secrets: SecretPolicy = Field(default_factory=SecretPolicy)
    destructive_ops: DestructiveOpsPolicy = Field(default_factory=DestructiveOpsPolicy)

    @staticmethod
    def permissive_safety() -> SafetyConfig:
        """Factory: minimal restrictions for trusted environments."""
        return SafetyConfig(
            git=GitPolicy(
                allow_push=True, allow_force_push=True,
                allow_branch_delete=True, protected_branches=[],
            ),
            shell=ShellPolicy(allow_shell=True),
            filesystem=FileSystemPolicy(
                allow_write=True, allow_delete=True,
            ),
            network=NetworkPolicy(allow_network=True),
            secrets=SecretPolicy(
                scan_for_secrets=False, block_on_secret=False,
            ),
            destructive_ops=DestructiveOpsPolicy(
                allow_destructive=True, require_confirmation=False,
            ),
        )

    @staticmethod
    def baseline_safety() -> SafetyConfig:
        """Factory: sensible defaults for general development."""
        return SafetyConfig()

    @staticmethod
    def hardened_safety() -> SafetyConfig:
        """Factory: strict controls for sensitive projects."""
        return SafetyConfig(
            git=GitPolicy(
                allow_push=True, allow_force_push=False,
                allow_branch_delete=False,
                protected_branches=["main", "master", "release/*"],
            ),
            shell=ShellPolicy(
                allow_shell=True,
                blocked_commands=["rm -rf /", "mkfs", "dd"],
                blocked_patterns=[r"curl.*\|.*sh", r"wget.*\|.*bash"],
            ),
            filesystem=FileSystemPolicy(
                allow_write=True, allow_delete=False,
                protected_paths=["/etc", "/usr", "/var"],
            ),
            network=NetworkPolicy(allow_network=True),
            secrets=SecretPolicy(
                scan_for_secrets=True, block_on_secret=True,
                secret_patterns=[
                    r"(?i)api[_-]?key", r"(?i)secret[_-]?key",
                    r"(?i)password\s*=", r"(?i)token\s*=",
                ],
            ),
            destructive_ops=DestructiveOpsPolicy(
                allow_destructive=False, require_confirmation=True,
                blocked_operations=["drop database", "truncate table"],
            ),
        )


# ---------------------------------------------------------------------------
# Generation options
# ---------------------------------------------------------------------------

class GenerationOptions(BaseModel):
    """Controls what the pipeline produces."""

    seed_tasks: bool = Field(default=True, description="Generate seeded task list")
    seed_mode: SeedMode = Field(
        default=SeedMode.DETAILED,
        description="Seed task detail level",
    )
    write_manifest: bool = Field(default=True, description="Write manifest.json")
    write_diff_report: bool = Field(default=False, description="Write diff-report.md")


# ---------------------------------------------------------------------------
# CompositionSpec — the top-level spec
# ---------------------------------------------------------------------------

class CompositionSpec(BaseModel):
    """Top-level composition specification — the input to the generation pipeline."""

    project: ProjectIdentity
    expertise: list[ExpertiseSelection] = Field(default_factory=list)
    team: TeamConfig = Field(default_factory=TeamConfig)
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    generation: GenerationOptions = Field(default_factory=GenerationOptions)
    safety: SafetyConfig | None = Field(
        default=None,
        description="Inline safety config; if omitted, derived from hooks posture",
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationMessage(BaseModel):
    """A single validation finding."""

    severity: Severity
    code: str = Field(..., description="Machine-readable code, e.g. 'missing-persona'")
    message: str = Field(..., description="Human-readable description")


class ValidationResult(BaseModel):
    """Aggregated validation output from pre-generation checks."""

    messages: list[ValidationMessage] = Field(default_factory=list)

    @property
    def errors(self) -> list[ValidationMessage]:
        return [m for m in self.messages if m.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[ValidationMessage]:
        return [m for m in self.messages if m.severity == Severity.WARNING]

    @property
    def infos(self) -> list[ValidationMessage]:
        return [m for m in self.messages if m.severity == Severity.INFO]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


# ---------------------------------------------------------------------------
# Pipeline results
# ---------------------------------------------------------------------------

class StageResult(BaseModel):
    """Result of a single pipeline stage."""

    wrote: list[str] = Field(default_factory=list, description="Files written by this stage")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")


class GenerationManifest(BaseModel):
    """Complete record of a generation run."""

    run_id: str = Field(..., description="Unique run identifier (timestamp-based)")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    library_version: str = Field(default="", description="Git short-hash of library")
    composition_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized CompositionSpec for traceability",
    )
    stages: dict[str, StageResult] = Field(
        default_factory=dict,
        description="Per-stage results keyed by stage name",
    )

    @property
    def total_files_written(self) -> int:
        return sum(len(s.wrote) for s in self.stages.values())

    @property
    def all_warnings(self) -> list[str]:
        warnings: list[str] = []
        for stage in self.stages.values():
            warnings.extend(stage.warnings)
        return warnings


# ---------------------------------------------------------------------------
# Overlay mode
# ---------------------------------------------------------------------------

class FileAction(BaseModel):
    """Describes a single file action for overlay/re-generation."""

    path: str = Field(..., description="Relative path within the project")
    action: FileActionType
    reason: str = Field(default="", description="Why this action was chosen")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        p = PurePosixPath(v)
        if p.is_absolute():
            raise ValueError(f"FileAction path must be relative, got: {v}")
        if ".." in p.parts:
            raise ValueError(f"FileAction path must not contain '..', got: {v}")
        return v


class OverlayPlan(BaseModel):
    """Plan for overlaying changes on an existing project."""

    actions: list[FileAction] = Field(default_factory=list)
    dry_run: bool = Field(default=False)

    @property
    def creates(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == FileActionType.CREATE]

    @property
    def updates(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == FileActionType.UPDATE]

    @property
    def deletes(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == FileActionType.DELETE]

    @property
    def skips(self) -> list[FileAction]:
        return [a for a in self.actions if a.action == FileActionType.SKIP]


# ---------------------------------------------------------------------------
# Library index
# ---------------------------------------------------------------------------

class PersonaInfo(BaseModel):
    """Metadata about a discovered persona in the library."""

    id: str = Field(..., min_length=1)
    path: str = Field(..., description="Path to persona directory")
    has_persona_md: bool = False
    has_outputs_md: bool = False
    has_prompts_md: bool = False
    templates: list[str] = Field(default_factory=list, description="Template filenames")


class ExpertiseInfo(BaseModel):
    """Metadata about a discovered expertise in the library."""

    id: str
    path: str = Field(..., description="Path to expertise directory")
    files: list[str] = Field(default_factory=list, description="Convention doc filenames")


class HookPackInfo(BaseModel):
    """Metadata about a discovered hook pack in the library."""

    id: str
    path: str = Field(..., description="Path to hook pack directory")
    files: list[str] = Field(default_factory=list, description="Hook policy filenames")
    category: str = Field(default="", description="Hook category (git, az, code-quality)")


class LibraryIndex(BaseModel):
    """Index of all building blocks discovered in a library directory."""

    library_root: str = Field(..., description="Absolute path to library root")
    personas: list[PersonaInfo] = Field(default_factory=list)
    expertise: list[ExpertiseInfo] = Field(default_factory=list)
    hook_packs: list[HookPackInfo] = Field(default_factory=list)

    def persona_by_id(self, persona_id: str) -> PersonaInfo | None:
        return next((p for p in self.personas if p.id == persona_id), None)

    def expertise_by_id(self, expertise_id: str) -> ExpertiseInfo | None:
        return next((s for s in self.expertise if s.id == expertise_id), None)

    def hook_pack_by_id(self, pack_id: str) -> HookPackInfo | None:
        return next((h for h in self.hook_packs if h.id == pack_id), None)
