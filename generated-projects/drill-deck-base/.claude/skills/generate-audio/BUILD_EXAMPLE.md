# Build pipeline example: cross-page MP3 dedup via content hash

This is a **worked sketch**, not a runnable script. It shows how a downstream
build pipeline reuses one MP3 across every page that quotes the same narration
block. Foundry-generated projects don't ship a fixed build target, so this
lives here as a reference rather than as kit code.

## The contract (recap)

`generate-audio` writes per-source manifests at
`audio/<source-stem>/manifest.json`. Each record's `text` field is the
**stripped narration** that was sent to ElevenLabs — bit-for-bit identical
to the output of `_media_lib.text.normalize_narration_text(raw_blockquote)`.

```json
{
  "index": 1,
  "module": "module-00-intro",
  "audio_file": "01_module-00-intro.mp3",
  "text": "Welcome to Module 00. In this module we'll cover the basics ...",
  "size_bytes": 87421
}
```

Because the stripped text is reproducible, two different source files that
quote the same narration block hash to the same digest — and a build pipeline
can serve one MP3 to both pages.

## The library function

`_media_lib.text.hash_text(text: str) -> str` returns a stable sha256 hex
digest. Both this skill and any consumer **must import** it rather than
re-implementing — the BEAN-281 contract test
(`tests/test_media_lib.py::test_hash_text_is_stable`) defends the regex
order and digest format.

```python
from _media_lib.text import hash_text

digest = hash_text("Welcome to Module 00.")  # 64-char hex sha256
```

## A build-pipeline sketch

Walk every per-source manifest, build a `digest → first-MP3-path` index,
emit `<audio>` HTML pointing at the canonical copy.

```python
import json
from pathlib import Path

from _media_lib.text import hash_text


def build_audio_index(audio_root: Path) -> dict[str, Path]:
    """Return {sha256: canonical_mp3_path} across every source manifest."""
    index: dict[str, Path] = {}
    for manifest_path in sorted(audio_root.glob("*/manifest.json")):
        records = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in records:
            digest = hash_text(record["text"])
            mp3 = manifest_path.parent / record["audio_file"]
            # First-wins: deterministic when sources are walked in lex order.
            index.setdefault(digest, mp3)
    return index


def render_audio_tag(stripped_text: str, index: dict[str, Path]) -> str:
    """Return an <audio> tag pointing at the canonical MP3 for this text."""
    digest = hash_text(stripped_text)
    mp3 = index.get(digest)
    if mp3 is None:
        # Block was never generated — generate-audio hasn't run yet, or
        # the block was added to source after the last run.
        return f'<!-- audio missing for digest {digest[:8]} -->'
    return f'<audio src="{mp3.as_posix()}" controls></audio>'
```

## Why this matters

A 200-block course that reuses the "What we covered" recap across every
module page would otherwise multiply the cost: 5 reuses × 200 blocks ×
~600 chars = 600K credits. Content-hash dedup makes that 200 blocks of
canonical audio + 1000 reused playbacks at the HTML layer — same listener
experience, fixed cost.

## Don't re-implement the hash

The whole contract collapses if the digest function drifts between
producer and consumer. **Always import `hash_text` from `_media_lib.text`**;
the contract test in `tests/test_media_lib.py` is the gate.
