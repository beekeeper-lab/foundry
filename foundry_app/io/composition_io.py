"""YAML/JSON read/write helpers for CompositionSpec and GenerationManifest."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from foundry_app.core.models import CompositionSpec, GenerationManifest


def load_composition(path: str | Path) -> CompositionSpec:
    """Load a CompositionSpec from a YAML file.

    Raises:
        FileNotFoundError: If the path does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
        pydantic.ValidationError: If the data does not match the schema.
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    if data is None:
        data = {}
    return CompositionSpec.model_validate(data)


def save_composition(spec: CompositionSpec, path: str | Path) -> None:
    """Save a CompositionSpec to a YAML file.

    Creates parent directories if they don't exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = spec.model_dump(mode="json", exclude_none=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)


def load_manifest(path: str | Path) -> GenerationManifest:
    """Load a GenerationManifest from a JSON file.

    Raises:
        FileNotFoundError: If the path does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        pydantic.ValidationError: If the data does not match the schema.
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return GenerationManifest.model_validate(data)


def save_manifest(manifest: GenerationManifest, path: str | Path) -> None:
    """Save a GenerationManifest to a JSON file.

    Creates parent directories if they don't exist.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = manifest.model_dump(mode="json")
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
