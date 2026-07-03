""".env discovery + loading for kit-distributed media skills.

The discovery walk is: ``start or Path.cwd()`` → every parent → ``Path.home()``.
First ``.env`` found wins. Existing ``os.environ`` keys are NEVER overwritten —
the process environment always takes precedence over file values, so a CI
secret or shell export is honored even when a stale ``.env`` is checked in.

If ``python-dotenv`` is importable, it is used for parsing (it handles edge
cases like multiline values and shell-style escapes); otherwise an inline
parser is used. The inline parser supports:

- ``KEY=value`` (one per line)
- blank lines and ``#`` comments are ignored
- single- or double-quoted values: ``KEY="value with spaces"``
- inline ``#`` after an UNquoted value is treated as the start of a comment

The function returns a dict of keys it actually set into ``os.environ`` (i.e.
keys that were absent from ``os.environ`` before the call). Callers can use
that return value to log or audit which values came from the file.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["load_env", "find_env_file"]


def find_env_file(start: Path | None = None) -> Path | None:
    """Locate the nearest ``.env`` walking ``start`` → parents → ``$HOME``.

    Returns the first ``.env`` file found, or ``None`` if none exists in the
    walk. ``start`` defaults to ``Path.cwd()``. The walk visits ``start``,
    then ``start.parent``, then ``start.parent.parent``, and so on until the
    filesystem root, then finally ``Path.home()``. Each directory is checked
    for a literal ``.env`` filename.
    """
    cur = (start or Path.cwd()).resolve()

    # Walk cur and all parents.
    visited: set[Path] = set()
    for candidate_dir in [cur, *cur.parents]:
        if candidate_dir in visited:
            continue
        visited.add(candidate_dir)
        env_path = candidate_dir / ".env"
        if env_path.is_file():
            return env_path

    # Fall back to $HOME if not already visited.
    home = Path.home().resolve()
    if home not in visited:
        env_path = home / ".env"
        if env_path.is_file():
            return env_path

    return None


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a ``.env`` file with the inline parser. See module docstring."""
    result: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.lstrip()

        # Quoted value: keep contents verbatim, drop the quotes. We do NOT
        # try to honor inline ``#`` after the closing quote (the comment
        # would have to be syntactically distinguishable from a literal
        # ``#`` inside the quoted value, which python-dotenv handles but
        # the inline parser does not need to).
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        else:
            # Unquoted value: strip an inline ``# comment`` if present, then
            # rstrip any trailing whitespace.
            if " #" in value:
                value = value.split(" #", 1)[0]
            elif "\t#" in value:
                value = value.split("\t#", 1)[0]
            value = value.rstrip()

        result[key] = value
    return result


def load_env(start: Path | None = None) -> dict[str, str]:
    """Load the nearest ``.env`` into ``os.environ`` without overwriting.

    Walks ``start or Path.cwd()`` -> parents -> ``$HOME`` for a ``.env``;
    returns ``{}`` if none is found. Keys already present in ``os.environ``
    are preserved (the process environment wins). Only keys actually set
    into ``os.environ`` are returned.

    If ``python-dotenv`` is installed it is used for parsing; otherwise an
    inline parser handles the common cases (see module docstring). Either
    way, the "no-overwrite" rule is enforced by this function — we do not
    rely on ``dotenv.load_dotenv(override=False)`` semantics, because the
    contract is part of this library's API.
    """
    env_path = find_env_file(start)
    if env_path is None:
        return {}

    try:
        from dotenv import dotenv_values  # type: ignore[import-not-found]
        parsed: dict[str, str | None] = dict(dotenv_values(str(env_path)))
        # python-dotenv may yield ``None`` for keys with no value; treat as ""
        file_values = {k: ("" if v is None else v) for k, v in parsed.items()}
    except ImportError:
        file_values = _parse_env_file(env_path)

    newly_set: dict[str, str] = {}
    for key, value in file_values.items():
        if key in os.environ:
            continue
        os.environ[key] = value
        newly_set[key] = value

    return newly_set
