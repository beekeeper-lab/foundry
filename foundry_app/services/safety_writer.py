"""Safety writer service — generates .claude/settings.json for a generated project."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    Posture,
    SafetyConfig,
    StageResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Posture → SafetyConfig mapping
# ---------------------------------------------------------------------------

_POSTURE_FACTORIES: dict[Posture, callable] = {
    Posture.BASELINE: SafetyConfig.baseline_safety,
    Posture.HARDENED: SafetyConfig.hardened_safety,
    Posture.REGULATED: SafetyConfig.hardened_safety,  # regulated uses hardened as base
}


def _build_safety_config(spec: CompositionSpec) -> SafetyConfig:
    """Build a SafetyConfig from the composition spec.

    Priority:
    1. Explicit ``spec.safety`` overrides (if provided)
    2. Posture-based factory (from ``spec.hooks.posture``)
    """
    if spec.safety is not None:
        return spec.safety

    factory = _POSTURE_FACTORIES.get(spec.hooks.posture, SafetyConfig.baseline_safety)
    return factory()


def write_safety(spec: CompositionSpec, output_dir: str | Path) -> StageResult:
    """Generate ``.claude/settings.json`` in the output directory.

    Assembles a safety configuration from the spec's posture preset and
    optional inline overrides, then writes it as JSON.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    settings_dir = root / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)

    safety = _build_safety_config(spec)

    # Build the settings structure
    settings = {
        "safety": safety.model_dump(mode="json"),
    }

    settings_path = settings_dir / "settings.json"
    settings_path.write_text(
        json.dumps(settings, indent=2) + "\n",
        encoding="utf-8",
    )

    rel_path = str(settings_path.relative_to(root))
    wrote.append(rel_path)

    logger.info(
        "Safety config written: posture=%s, path=%s",
        spec.hooks.posture.value,
        rel_path,
    )

    return StageResult(wrote=wrote, warnings=warnings)
