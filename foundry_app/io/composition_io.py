"""IO helpers for reading and writing composition specs and manifests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from foundry_app.core.models import CompositionSpec, GenerationManifest


class CompositionIOError(Exception):
    """Raised when a composition or manifest cannot be loaded or saved."""


def load_composition(path: Path) -> CompositionSpec:
    """Load a CompositionSpec from a YAML file.

    Raises:
        CompositionIOError: If the file is missing, unreadable, contains
            malformed YAML, or fails Pydantic validation.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CompositionIOError(f"Composition file not found: {path}") from None
    except PermissionError:
        raise CompositionIOError(f"Permission denied reading: {path}") from None
    except OSError as exc:
        raise CompositionIOError(f"Cannot read {path}: {exc}") from exc

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise CompositionIOError(f"Malformed YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise CompositionIOError(
            f"Expected a YAML mapping in {path}, got {type(data).__name__}."
        )

    try:
        return CompositionSpec.model_validate(data)
    except ValidationError as exc:
        raise CompositionIOError(
            f"Invalid composition data in {path}: {exc}"
        ) from exc


def save_composition(composition: CompositionSpec, path: Path) -> None:
    """Save a CompositionSpec to a YAML file.

    Raises:
        CompositionIOError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = composition.model_dump()
        path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    except PermissionError:
        raise CompositionIOError(f"Permission denied writing: {path}") from None
    except OSError as exc:
        raise CompositionIOError(f"Cannot write {path}: {exc}") from exc


def load_manifest(path: Path) -> GenerationManifest:
    """Load a GenerationManifest from a JSON file.

    Raises:
        CompositionIOError: If the file is missing, unreadable, contains
            malformed JSON, or fails Pydantic validation.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CompositionIOError(f"Manifest file not found: {path}") from None
    except PermissionError:
        raise CompositionIOError(f"Permission denied reading: {path}") from None
    except OSError as exc:
        raise CompositionIOError(f"Cannot read {path}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CompositionIOError(f"Malformed JSON in {path}: {exc}") from exc

    try:
        return GenerationManifest.model_validate(data)
    except ValidationError as exc:
        raise CompositionIOError(
            f"Invalid manifest data in {path}: {exc}"
        ) from exc


def save_manifest(manifest: GenerationManifest, path: Path) -> None:
    """Save a GenerationManifest to a JSON file.

    Raises:
        CompositionIOError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    except PermissionError:
        raise CompositionIOError(f"Permission denied writing: {path}") from None
    except OSError as exc:
        raise CompositionIOError(f"Cannot write {path}: {exc}") from exc
