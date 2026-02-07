"""Tests for foundry_app.services.library_indexer: scan, cache, and load library index."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import LibraryIndex
from foundry_app.services.library_indexer import (
    build_library_index,
    load_index_cache,
    write_index_cache,
)

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


# -- Discovery ----------------------------------------------------------------


def test_build_library_index_discovers_personas():
    """build_library_index should find all persona directories in the library."""
    index = build_library_index(LIBRARY_ROOT)

    persona_ids = [p.id for p in index.personas]
    assert len(persona_ids) > 0, "Expected at least one persona"
    assert "team-lead" in persona_ids
    assert "developer" in persona_ids


def test_build_library_index_discovers_stacks():
    """build_library_index should find all stack directories in the library."""
    index = build_library_index(LIBRARY_ROOT)

    stack_ids = [s.id for s in index.stacks]
    assert len(stack_ids) > 0, "Expected at least one stack"
    assert "python" in stack_ids


def test_persona_entry_has_files():
    """PersonaIndexEntry for team-lead should list persona.md and templates."""
    index = build_library_index(LIBRARY_ROOT)

    team_lead = next(p for p in index.personas if p.id == "team-lead")
    assert "persona.md" in team_lead.files
    assert len(team_lead.templates) > 0, "team-lead should have templates"
    assert "task-spec.md" in team_lead.templates


# -- Cache roundtrip -----------------------------------------------------------


def test_write_and_load_cache_roundtrip(tmp_path: Path):
    """write_index_cache then load_index_cache should return an equivalent index."""
    original = build_library_index(LIBRARY_ROOT)

    cache_file = write_index_cache(original, tmp_path)
    assert cache_file.is_file()

    loaded = load_index_cache(tmp_path)
    assert loaded is not None
    assert loaded.root == original.root
    assert len(loaded.personas) == len(original.personas)
    assert len(loaded.stacks) == len(original.stacks)
    # Spot-check a persona entry survived the roundtrip
    orig_ids = sorted(p.id for p in original.personas)
    loaded_ids = sorted(p.id for p in loaded.personas)
    assert orig_ids == loaded_ids


def test_load_cache_missing_returns_none(tmp_path: Path):
    """load_index_cache should return None when no cache file exists."""
    result = load_index_cache(tmp_path)
    assert result is None


# -- Edge cases ----------------------------------------------------------------


def test_build_index_empty_library(tmp_path: Path):
    """build_library_index on a directory with an empty personas/ dir returns empty lists."""
    (tmp_path / "personas").mkdir()
    (tmp_path / "stacks").mkdir()

    index = build_library_index(tmp_path)

    assert isinstance(index, LibraryIndex)
    assert len(index.personas) == 0
    assert len(index.stacks) == 0
