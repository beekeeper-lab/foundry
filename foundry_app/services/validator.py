"""Validation rules for Foundry: pre-generation and pre-export checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from foundry_app.core.models import CompositionSpec


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def merge(self, other: ValidationResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def validate_composition(
    composition: CompositionSpec,
    strictness: str = "standard",
) -> ValidationResult:
    """Validate that a composition spec is complete.

    Args:
        composition: The composition spec to validate.
        strictness: Validation mode — "light", "standard", or "strict".
            light: only fatal errors, optional checks suppressed.
            standard: errors for critical issues, warnings for optional.
            strict: all warnings promoted to errors.
    """
    result = ValidationResult()

    if not composition.project.name.strip():
        result.errors.append("Project name is required.")
    if not composition.project.slug.strip():
        result.errors.append("Project slug is required.")

    if not composition.stacks:
        if strictness == "strict":
            result.errors.append("No tech stacks selected.")
        elif strictness == "standard":
            result.warnings.append("No tech stacks selected.")
        # light: silently skip

    if not composition.team.personas:
        result.errors.append("At least one persona must be selected.")

    # Check for duplicate stack IDs
    stack_ids = [s.id for s in composition.stacks]
    if len(stack_ids) != len(set(stack_ids)):
        result.errors.append("Duplicate stack IDs found.")

    # Check for duplicate persona IDs
    persona_ids = [p.id for p in composition.team.personas]
    if len(persona_ids) != len(set(persona_ids)):
        result.errors.append("Duplicate persona IDs found.")

    return result


def validate_library_personas(
    composition: CompositionSpec,
    library_root: Path,
    strictness: str = "standard",
) -> ValidationResult:
    """Validate that all selected personas exist in the library with required files."""
    result = ValidationResult()
    required_files = ["persona.md", "outputs.md", "prompts.md"]

    for persona in composition.team.personas:
        persona_dir = library_root / "personas" / persona.id
        if not persona_dir.is_dir():
            result.errors.append(
                f"Persona directory not found: personas/{persona.id}/"
            )
            continue

        for req_file in required_files:
            if not (persona_dir / req_file).is_file():
                result.errors.append(
                    f"Required file missing: personas/{persona.id}/{req_file}"
                )

        # Check templates directory exists if include_templates is set
        if persona.include_templates:
            templates_dir = persona_dir / "templates"
            if not templates_dir.is_dir():
                msg = f"Templates directory missing: personas/{persona.id}/templates/"
                if strictness == "strict":
                    result.errors.append(msg)
                elif strictness == "standard":
                    result.warnings.append(msg)
            elif not any(templates_dir.glob("*.md")):
                msg = f"No templates found in: personas/{persona.id}/templates/"
                if strictness == "strict":
                    result.errors.append(msg)
                elif strictness == "standard":
                    result.warnings.append(msg)

    return result


def validate_library_stacks(
    composition: CompositionSpec,
    library_root: Path,
    strictness: str = "standard",
) -> ValidationResult:
    """Validate that all selected stacks exist in the library."""
    result = ValidationResult()

    for stack in composition.stacks:
        stack_dir = library_root / "stacks" / stack.id
        if not stack_dir.is_dir():
            result.errors.append(
                f"Stack directory not found: stacks/{stack.id}/"
            )
            continue

        if not any(stack_dir.glob("*.md")):
            msg = f"No markdown files in stack: stacks/{stack.id}/"
            if strictness == "strict":
                result.errors.append(msg)
            elif strictness == "standard":
                result.warnings.append(msg)

    return result


def validate_template_references(
    composition: CompositionSpec,
    library_root: Path,
    strictness: str = "standard",
) -> ValidationResult:
    """Check that template paths referenced in outputs.md actually exist."""
    result = ValidationResult()

    # In light mode, skip template reference checks entirely
    if strictness == "light":
        return result

    for persona in composition.team.personas:
        outputs_file = library_root / "personas" / persona.id / "outputs.md"
        if not outputs_file.is_file():
            continue

        content = outputs_file.read_text()
        # Look for template references like templates/something.md
        import re
        refs = re.findall(r"templates/([a-z0-9_-]+\.md)", content)
        for ref in refs:
            template_path = library_root / "personas" / persona.id / "templates" / ref
            if not template_path.is_file():
                msg = (
                    f"Template referenced in outputs.md but not found: "
                    f"personas/{persona.id}/templates/{ref}"
                )
                if strictness == "strict":
                    result.errors.append(msg)
                else:
                    result.warnings.append(msg)

    return result


def validate_safety_config(composition: CompositionSpec) -> ValidationResult:
    """Validate safety configuration for contradictions and risky settings."""
    result = ValidationResult()
    safety = composition.safety

    # Warn if fully permissive
    if safety.preset == "permissive":
        result.warnings.append(
            "Safety preset is 'permissive' — all operations are allowed. "
            "Consider using 'baseline' for production projects."
        )

    # Error if contradictory: force-push allowed but push denied
    if safety.git.allow_force_push and not safety.git.allow_push:
        result.errors.append(
            "Contradictory git policy: force-push is allowed but push is denied."
        )

    # Warn if destructive ops are all allowed
    if (
        safety.destructive.allow_rm_rf
        and safety.destructive.allow_reset_hard
        and safety.destructive.allow_clean
    ):
        result.warnings.append(
            "All destructive operations are allowed. "
            "Consider restricting rm -rf, reset --hard, or clean."
        )

    return result


def validate_generated_project(project_dir: Path) -> ValidationResult:
    """Validate a generated project has required entry points."""
    result = ValidationResult()

    required = [
        "CLAUDE.md",
        "ai/team/composition.yml",
    ]

    for req in required:
        if not (project_dir / req).is_file():
            result.errors.append(f"Required file missing: {req}")

    agents_dir = project_dir / ".claude" / "agents"
    if not agents_dir.is_dir() or not any(agents_dir.glob("*.md")):
        result.errors.append("No agent definitions found in .claude/agents/")

    members_dir = project_dir / "ai" / "generated" / "members"
    if not members_dir.is_dir() or not any(members_dir.glob("*.md")):
        result.warnings.append(
            "No compiled member prompts in ai/generated/members/ — run compile first."
        )

    # Check for settings.local.json
    settings_file = project_dir / ".claude" / "settings.local.json"
    if not settings_file.is_file():
        result.warnings.append(
            "No .claude/settings.local.json found — safety guardrails not configured."
        )

    # Check for populated skills directory
    skills_dir = project_dir / ".claude" / "skills"
    if not skills_dir.is_dir() or not any(skills_dir.iterdir()):
        result.warnings.append(
            "No skills found in .claude/skills/ — project may lack automation."
        )

    # Check for populated commands directory
    commands_dir = project_dir / ".claude" / "commands"
    if not commands_dir.is_dir() or not any(commands_dir.iterdir()):
        result.warnings.append(
            "No commands found in .claude/commands/ — project may lack shortcuts."
        )

    return result


def run_pre_generation_validation(
    composition: CompositionSpec,
    library_root: Path,
    strictness: str = "standard",
) -> ValidationResult:
    """Run all pre-generation validations.

    Args:
        composition: The composition spec to validate.
        library_root: Path to the ai-team-library root.
        strictness: Validation mode — "light", "standard", or "strict".
    """
    result = ValidationResult()
    result.merge(validate_composition(composition, strictness))
    result.merge(validate_library_personas(composition, library_root, strictness))
    result.merge(validate_library_stacks(composition, library_root, strictness))
    result.merge(validate_template_references(composition, library_root, strictness))
    result.merge(validate_safety_config(composition))
    return result
