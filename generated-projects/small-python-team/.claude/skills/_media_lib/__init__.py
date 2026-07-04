"""Shared helpers for the kit-distributed media skills.

This package is consumed by ``generate-image`` and (forthcoming)
``generate-audio`` skills, plus any downstream build pipeline that wants to
reproduce the same content-hash dedup behavior.

Public surface (the contract):

- :func:`load_env` — walk cwd -> parents -> ``$HOME`` for a ``.env`` and
  load missing keys into ``os.environ`` without overwriting existing ones.
- :func:`find_env_file` — same walk, but returns the path without loading.
- :func:`normalize_narration_text` — strip markdown / HTML / blockquote /
  emoji and collapse whitespace, in a fixed order. **Load-bearing for
  hash stability** — see ``text.py`` docstring.
- :func:`hash_text` — sha256 hex digest of normalized text.
- :data:`NORMALIZATION_ORDER` — the canonical regex application order;
  re-exported so contract tests can import it directly.
- :func:`lookup_cost`, :func:`format_cost_summary`, :func:`summarize_run` —
  shared cost-summary helpers (provider-agnostic).

The ``_`` prefix in the directory name signals "internal helpers — not a
user-invokable slash command" (mirroring Foundry's ``internal:*`` convention).
"""

from .cost import format_cost_summary, lookup_cost, summarize_run
from .env import find_env_file, load_env
from .text import NORMALIZATION_ORDER, hash_text, normalize_narration_text

__all__ = [
    "NORMALIZATION_ORDER",
    "find_env_file",
    "format_cost_summary",
    "hash_text",
    "load_env",
    "lookup_cost",
    "normalize_narration_text",
    "summarize_run",
]
