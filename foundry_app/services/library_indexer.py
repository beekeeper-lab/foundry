"""Service to scan and index a library directory."""

from __future__ import annotations

import json
from pathlib import Path

from foundry_app.core.models import LibraryIndex


def build_library_index(library_root: Path) -> LibraryIndex:
    """Scan the library root and return a LibraryIndex."""
    return LibraryIndex.from_library_path(library_root)


def write_index_cache(index: LibraryIndex, cache_dir: Path) -> Path:
    """Write the library index to a JSON cache file."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "library_index.json"
    cache_file.write_text(index.model_dump_json(indent=2))
    return cache_file


def load_index_cache(cache_dir: Path) -> LibraryIndex | None:
    """Load a cached library index if it exists."""
    cache_file = cache_dir / "library_index.json"
    if not cache_file.exists():
        return None
    data = json.loads(cache_file.read_text())
    return LibraryIndex.model_validate(data)
