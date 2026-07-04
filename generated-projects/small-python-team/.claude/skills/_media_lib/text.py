"""Narration text normalization + content hashing.

This module is the **portable contract** between every consumer that wants to
deduplicate generated media (audio MP3s today, potentially images or other
artifacts later) by content. The hash of any narration string MUST be stable
across:

- the kit-distributed media skills (audio + image generators), and
- any downstream build pipeline that wants to reproduce or verify the same
  artifacts.

If the regex order or normalization steps in :func:`normalize_narration_text`
drift, hashes diverge and every previously generated artifact is treated as
stale. **Port these functions verbatim into any downstream consumer; do not
re-implement the normalization.**

The canonical source for the regex order is
``Course_Material/Git_Fundamentals/scripts/generate_narration.py`` from the
Stonewaters consulting course material — see ``find_narration_blocks`` for the
original implementation. The order here is locked in by the regex-order
contract test in ``tests/test_media_lib.py``.
"""

from __future__ import annotations

import hashlib
import re

# Compiled patterns — module-level so the regex order is visible at a glance
# and cheap to apply. The ORDER OF APPLICATION is the load-bearing contract;
# do not reorder without updating every downstream consumer.
_BLOCKQUOTE_RE = re.compile(r"^> ?", re.MULTILINE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"\*(.+?)\*")
_CODE_RE = re.compile(r"`(.+?)`")
_LINK_RE = re.compile(r"\[(.+?)\]\(.+?\)")
_WHITESPACE_RUN_RE = re.compile(r"\s+")

_MIC_EMOJI = "\U0001f399️"  # 🎙️ — studio microphone + variation selector

# Canonical regex application order. Exposed as a module constant so the
# contract test can assert it directly — if a contributor reorders the steps
# inside ``normalize_narration_text``, this tuple must be updated in lockstep,
# and the contract test catches the drift either way.
NORMALIZATION_ORDER: tuple[str, ...] = (
    "blockquote",   # 1. strip leading ``> `` blockquote markers (line by line)
    "mic_emoji",    # 2. strip 🎙️ emoji (with optional trailing space)
    "html_tag",     # 3. strip HTML tags
    "bold",         # 4. **bold** -> bold
    "italic",       # 5. *italic* -> italic
    "code",         # 6. `code`   -> code
    "link",         # 7. [label](url) -> label
    "whitespace",   # 8. collapse runs of whitespace to single spaces, then strip
)


def normalize_narration_text(text: str) -> str:
    """Normalize narration markdown for content hashing and TTS.

    The regexes are applied in this **exact order** (the load-bearing
    contract — see module docstring):

    1. Strip leading ``> `` blockquote markers (line by line).
    2. Strip the 🎙️ emoji (and any trailing space after it).
    3. Strip HTML tags (``<[^>]+>``).
    4. ``**bold**`` -> ``bold``
    5. ``*italic*`` -> ``italic``
    6. ``` `code` ``` -> ``code``
    7. ``[label](url)`` -> ``label``
    8. Collapse runs of whitespace (including newlines) to single spaces,
       then strip leading/trailing whitespace.

    Steps 1, 4, 5, 6, 7 are ported verbatim from the Stonewaters reference
    (``Course_Material/Git_Fundamentals/scripts/generate_narration.py``).
    Steps 2, 3, 8 are extensions for downstream consumers (HTML stripping
    and whitespace collapse make hashes robust across whitespace-only edits
    in the source markdown).

    Downstream consumers MUST use this function verbatim — re-implementing
    it in a build pipeline will produce divergent hashes.
    """
    # 1. Blockquote markers (line by line, preserves line structure).
    text = _BLOCKQUOTE_RE.sub("", text)

    # 2. Microphone emoji — strip "🎙️ " (with trailing space) first so the
    #    space is consumed cleanly, then any bare "🎙️" left over.
    text = text.replace(f"{_MIC_EMOJI} ", "").replace(_MIC_EMOJI, "")

    # 3. HTML tags.
    text = _HTML_TAG_RE.sub("", text)

    # 4. Bold (must come before italic — ``**foo**`` would otherwise match
    #    italic twice and lose nothing because of the non-greedy match).
    text = _BOLD_RE.sub(r"\1", text)

    # 5. Italic.
    text = _ITALIC_RE.sub(r"\1", text)

    # 6. Inline code.
    text = _CODE_RE.sub(r"\1", text)

    # 7. Links — keep label, drop URL.
    text = _LINK_RE.sub(r"\1", text)

    # 8. Whitespace collapse + strip.
    text = _WHITESPACE_RUN_RE.sub(" ", text).strip()

    return text


def hash_text(text: str) -> str:
    """Return ``sha256(normalize_narration_text(text)).hexdigest()``.

    This is the canonical content-hash for narration dedup. Two inputs that
    normalize to the same string MUST produce the same hash, by construction.
    Consumers (audio generator, build pipeline, dedup index) treat this
    digest as the cache key for generated artifacts.

    Downstream consumers MUST use this function verbatim — substituting
    e.g. md5 or skipping normalization will desync the cache.
    """
    return hashlib.sha256(normalize_narration_text(text).encode("utf-8")).hexdigest()
