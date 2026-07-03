#!/usr/bin/env python3
"""Generate narration audio from inline ``> 🎙️`` markdown blocks via ElevenLabs.

Source of truth is the source markdown — every contiguous run of
blockquoted lines starting with the studio-microphone emoji is one
narration block. ``NARRATION-PLAN.md`` (when present) is parsed for
``Voice:`` and ``Model:`` frontmatter only — informational, not
authoritative. CLI flags override frontmatter.

Per-source-file manifests live at ``audio/<source-stem>/manifest.json``
and carry ``{index, module, audio_file, text, size_bytes}`` records.
The ``text`` field is the **stripped narration** that was sent to
ElevenLabs — bit-for-bit identical to what the API received — so
downstream build pipelines can content-hash it via
``_media_lib.text.hash_text`` for cross-page MP3 dedup.

Skip-on-disk modes (mutually composable):

    (default)               Generate every block whose MP3 is missing.
    --regenerate-changed    Also regenerate blocks whose stripped text
                            differs from the manifest's stored ``text``.
    --force                 Regenerate everything for the run.
    --dry-run               Walk + print, no API calls, no on-disk
                            changes (orphan cleanup is also skipped).
    --all                   Include auxiliary source files (every
                            ``*.md``) instead of the default
                            ``module-*.md`` glob.

Usage examples
--------------

    # Generate audio for all modules (skips existing files):
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py

    # Single source file:
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        source/module-03.md

    # Regenerate when stripped text changed:
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        --regenerate-changed

    # Different voice (a stock name, or a raw ElevenLabs ID):
    uv run --with elevenlabs python \\
        .claude/shared/skills/generate-audio/generate_audio.py \\
        --voice drew

Environment
-----------

``ELEVENLABS_API_KEY`` is required. The script discovers ``.env`` files
via ``_media_lib.env.load_env`` (cwd → parents → ``$HOME``); existing
process-environment values always win over file values.

Acknowledgements
----------------

The inline ``> 🎙️`` blockquote scanner, the per-source manifest
schema, the orphan-cleanup rule, and the stock-voice map are adapted
from ``Course_Material/Git_Fundamentals/scripts/generate_narration.py``
(the canonical Stonewaters reference, ~274 lines, production-tested
across an 18-course portfolio). This skill delegates markdown
stripping to ``_media_lib.text.normalize_narration_text`` (BEAN-281)
so the regex order stays in lockstep with downstream build pipelines.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# _media_lib import — works whether the script is run from the kit checkout
# or from a generated project's symlink farm.
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_SKILLS_ROOT = _THIS_DIR.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

try:
    from _media_lib.env import load_env  # type: ignore[import-not-found]
    from _media_lib.text import normalize_narration_text  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only when symlinks broken
    def load_env(start: Path | None = None) -> dict[str, str]:  # type: ignore[misc]
        return {}

    def normalize_narration_text(text: str) -> str:  # type: ignore[misc]
        return text


# ---------------------------------------------------------------------------
# Constants — voice map (stock names ONLY), model defaults, cost rate.
# No cloned voice IDs in committed code (ADR-011 commitment 4).
# ---------------------------------------------------------------------------

DEFAULT_VOICE = "rachel"
DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"

# Stock ElevenLabs voices that exist in any default account voice library.
# Unknown values pass through as raw IDs — the script does not validate.
STOCK_VOICE_MAP: dict[str, str] = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "drew": "29vD33N1CtxCmqQRPOHJ",
    "paul": "5Q0t7uMcjvnagumLfvZi",
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "emily": "LcfcDJNUP1GQjkzn1xUU",
    "charlie": "IKne3meq5aSn9XLyUdCD",
    "george": "JBFqnCBsd6RMkjVDRZzb",
    "matilda": "XrExE9yKIg1WjnnlVkGX",
}

# ElevenLabs `eleven_multilingual_v2` cost rate. **Source of truth lives
# here** — when ElevenLabs changes the rate, update this constant, not
# any docs that link to it. (Mirrors the cost-table-in-script rule in
# ADR-010 / generate-image.)
CREDITS_PER_CHAR: float = 1.0


# ---------------------------------------------------------------------------
# Inline ``> 🎙️`` blockquote scanner.
# ---------------------------------------------------------------------------

# A narration block is a contiguous run of blockquote lines starting with
# the microphone emoji. Continuation lines start with ``> `` (no emoji).
_BLOCK_RE = re.compile(
    r"(?:^|\n)(?:> 🎙️ .+(?:\n> .+)*)",
    re.MULTILINE,
)


def find_narration_blocks(markdown_text: str) -> list[dict[str, Any]]:
    """Extract narration blocks marked with 🎙️ from markdown.

    Each block is a contiguous run of blockquoted lines starting with
    the studio-microphone emoji. Continuation lines (``> ...`` without
    the emoji) are folded into the same block. Blockquotes that do
    NOT start with the emoji are ignored.

    Returns a list of ``{"index": int, "raw": str, "text": str,
    "position": int}`` dicts in document order. ``index`` is 0-based
    in this scanner; the manifest writer adds 1 to produce the 1-based
    block number used in MP3 filenames. ``text`` is the stripped
    narration via :func:`_media_lib.text.normalize_narration_text`.
    """
    blocks: list[dict[str, Any]] = []
    for i, match in enumerate(_BLOCK_RE.finditer(markdown_text)):
        raw = match.group().strip()
        text = normalize_narration_text(raw)
        blocks.append(
            {
                "index": i,
                "raw": raw,
                "text": text,
                "position": match.start(),
            }
        )
    return blocks


# ---------------------------------------------------------------------------
# NARRATION-PLAN.md frontmatter parser — informational only.
# ---------------------------------------------------------------------------

# Match ``**Key:** value`` lines in the head before the first ``##`` heading.
_FRONTMATTER_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z _-]*?):\*\*\s*(.*)$")


def parse_plan_frontmatter(plan_text: str) -> dict[str, str]:
    """Parse ``Voice:`` and ``Model:`` from ``NARRATION-PLAN.md`` head.

    Only ``**Voice:**`` and ``**Model:**`` (case-insensitive on the key)
    are recognized; other keys are ignored. Parsing stops at the first
    ``## `` heading. Returns lowercase-keyed dict (``"voice"``,
    ``"model"``) — empty dict when the plan has no recognized
    frontmatter.

    Per ADR-011: this is informational. CLI flags ALWAYS win.
    """
    result: dict[str, str] = {}
    for raw_line in plan_text.splitlines():
        if raw_line.startswith("## "):
            break
        m = _FRONTMATTER_RE.match(raw_line.strip())
        if not m:
            continue
        key = m.group(1).strip().lower().replace(" ", "_").replace("-", "_")
        value = m.group(2).strip()
        if key in ("voice", "model"):
            result[key] = value
    return result


def resolve_voice(voice_name_or_id: str) -> str:
    """Resolve a voice name to an ElevenLabs voice ID.

    Stock names in :data:`STOCK_VOICE_MAP` resolve to their canonical
    voice IDs. Unknown values pass through unchanged — they may be raw
    voice IDs, names registered in the user's own ElevenLabs voice
    library, or typos. ElevenLabs validates server-side and returns a
    clear error if the ID is unknown.
    """
    return STOCK_VOICE_MAP.get(voice_name_or_id, voice_name_or_id)


# ---------------------------------------------------------------------------
# Manifest helpers.
# ---------------------------------------------------------------------------


def load_existing_manifest(module_audio_dir: Path) -> dict[int, dict[str, Any]]:
    """Load existing manifest and index by 1-based block number.

    Returns an empty dict when the manifest does not exist, fails to
    parse, or lacks the expected shape — callers treat all three as
    "no prior state" and proceed.
    """
    manifest_path = module_audio_dir / "manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        entries = json.loads(manifest_path.read_text())
        return {e["index"]: e for e in entries}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def write_manifest(module_audio_dir: Path, entries: list[dict[str, Any]]) -> None:
    """Write the per-source manifest to ``<module_audio_dir>/manifest.json``.

    Entries are written as a JSON array with two-space indentation. The
    directory is created if missing. Callers are responsible for the
    record shape (``index, module, audio_file, text, size_bytes``); this
    helper does not validate.
    """
    module_audio_dir.mkdir(parents=True, exist_ok=True)
    (module_audio_dir / "manifest.json").write_text(
        json.dumps(entries, indent=2) + "\n"
    )


def cleanup_orphans(module_audio_dir: Path, expected_audio_files: set[str]) -> list[str]:
    """Remove MP3s whose blocks no longer exist in the current manifest.

    Returns the list of removed filenames (basenames). The directory is
    walked for ``*.mp3`` files; any name not in ``expected_audio_files``
    is removed. The function is a no-op when the directory does not
    exist. Callers MUST NOT invoke this under ``--dry-run`` — orphan
    cleanup is only correct on real generation runs.
    """
    if not module_audio_dir.is_dir():
        return []
    removed: list[str] = []
    for mp3 in sorted(module_audio_dir.glob("*.mp3")):
        if mp3.name not in expected_audio_files:
            mp3.unlink()
            removed.append(mp3.name)
    return removed


# ---------------------------------------------------------------------------
# ElevenLabs client wrapper.
# ---------------------------------------------------------------------------


def _import_elevenlabs() -> Any:
    """Lazy import of the ``elevenlabs`` SDK with a friendly error.

    The dep is not declared in ``pyproject.toml`` because the canonical
    invocation is ``uv run --with elevenlabs python <script>``; this
    function fires only when actually generating audio. Tests mock the
    SDK before ``generate_audio_for_block`` is called, so this import
    never runs under ``uv run pytest``.
    """
    try:
        from elevenlabs import ElevenLabs  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised at runtime only
        raise SystemExit(
            "ERROR: elevenlabs package not installed. "
            "Run: uv run --with elevenlabs python <script>"
        ) from exc
    return ElevenLabs


def get_elevenlabs_client(api_key: str) -> Any:
    """Construct an ``ElevenLabs(api_key=...)`` client.

    Split out so tests can mock the constructor without monkey-patching
    the lazy import path.
    """
    ElevenLabs = _import_elevenlabs()
    return ElevenLabs(api_key=api_key)


def generate_audio_for_block(
    client: Any,
    text: str,
    output_path: Path,
    voice_id: str,
    model_id: str = DEFAULT_MODEL,
) -> int:
    """Generate one MP3 via ElevenLabs and write it to ``output_path``.

    The ``client`` is an already-constructed ElevenLabs SDK instance
    (see :func:`get_elevenlabs_client`); the function does not consult
    ``os.environ`` directly. It calls
    ``client.text_to_speech.convert(...)`` with the documented defaults
    (``output_format=mp3_44100_128``), concatenates the streamed bytes,
    and writes the file. Returns the file size in bytes.
    """
    audio_gen = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format=DEFAULT_OUTPUT_FORMAT,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audio_bytes = b"".join(audio_gen)
    output_path.write_bytes(audio_bytes)
    return len(audio_bytes)


# ---------------------------------------------------------------------------
# Per-source orchestration — applies the five-mode skip-on-disk matrix.
# ---------------------------------------------------------------------------


def decide_action(
    block_text: str,
    audio_path: Path,
    existing_entry: dict[str, Any] | None,
    *,
    force: bool,
    regenerate_changed: bool,
) -> tuple[bool, str]:
    """Return ``(needs_generation, reason)`` for a single block.

    Decision matrix per ADR-011 commitment 6:

    - ``force=True``                                    -> generate (``"forced"``)
    - audio file does not exist                         -> generate (``"new"``)
    - ``regenerate_changed`` AND manifest's ``text`` differs from current
                                                         -> generate (``"text changed"``)
    - otherwise                                          -> skip (``"exists"``)

    Comparison uses ``.strip()`` on both sides so trailing whitespace in
    a manifest written by an earlier version of the script does not
    falsely flag a block as changed.
    """
    if force:
        return True, "forced"
    if not audio_path.exists():
        return True, "new"
    if regenerate_changed and existing_entry is not None:
        old_text = existing_entry.get("text", "")
        if old_text.strip() != block_text.strip():
            return True, "text changed"
    return False, "exists"


def process_source(
    source_path: Path,
    audio_root: Path,
    *,
    client: Any | None,
    voice_id: str,
    model_id: str = DEFAULT_MODEL,
    force: bool = False,
    regenerate_changed: bool = False,
    dry_run: bool = False,
    print_fn: Any = print,
) -> dict[str, Any]:
    """Process one markdown source file end-to-end.

    Walks the file, applies the skip-on-disk matrix, generates MP3s
    where needed (unless ``dry_run``), writes the per-source manifest,
    and runs orphan cleanup (only on real runs). Returns a stats dict
    with per-source counters used by the caller's end-of-run summary.

    Returned keys:

    - ``module``: source-file stem.
    - ``manifest``: list of manifest records, each
      ``{index, module, audio_file, text, size_bytes}``.
    - ``generated``: count of blocks for which an API call was made
      (always 0 under ``dry_run``).
    - ``skipped``: count of blocks whose MP3 already existed and was
      not regenerated.
    - ``would_generate``: count of blocks the dry-run preview marked
      for generation (always 0 outside ``dry_run``).
    - ``chars_sent``: total characters sent to ElevenLabs this run for
      this source (always 0 under ``dry_run``); equals total credits
      spent for this source per ADR-011 cost discipline.
    - ``orphans_removed``: list of orphan MP3 basenames removed.
    """
    module_name = source_path.stem
    text = source_path.read_text()
    blocks = find_narration_blocks(text)

    module_audio_dir = audio_root / module_name
    existing = load_existing_manifest(module_audio_dir)

    manifest: list[dict[str, Any]] = []
    generated = 0
    skipped = 0
    would_generate = 0
    chars_sent = 0

    if not blocks:
        print_fn(f"  {module_name}: no narration blocks found, skipping")
        return {
            "module": module_name,
            "manifest": manifest,
            "generated": generated,
            "skipped": skipped,
            "would_generate": would_generate,
            "chars_sent": chars_sent,
            "orphans_removed": [],
        }

    for block in blocks:
        idx = block["index"] + 1  # 1-based block number
        audio_filename = f"{idx:02d}_{module_name}.mp3"
        audio_path = module_audio_dir / audio_filename
        block_text = block["text"]

        existing_entry = existing.get(idx)
        needs, reason = decide_action(
            block_text,
            audio_path,
            existing_entry,
            force=force,
            regenerate_changed=regenerate_changed,
        )

        entry: dict[str, Any] = {
            "index": idx,
            "module": module_name,
            "audio_file": audio_filename,
            "text": block_text,
        }

        if dry_run:
            if needs:
                print_fn(f"  [{module_name}] Block {idx}: WOULD GENERATE ({reason})")
                preview = block_text[:80]
                print_fn(f"    {preview}{'...' if len(block_text) > 80 else ''}")
                would_generate += 1
            else:
                print_fn(f"  [{module_name}] Block {idx}: exists, skip")
            entry["size_bytes"] = (
                audio_path.stat().st_size if audio_path.exists() else 0
            )
        elif needs:
            if client is None:  # pragma: no cover - defensive only
                raise RuntimeError(
                    "process_source called with dry_run=False and client=None"
                )
            print_fn(f"  [{module_name}] Block {idx}: generating ({reason})...")
            size = generate_audio_for_block(
                client,
                block_text,
                audio_path,
                voice_id=voice_id,
                model_id=model_id,
            )
            entry["size_bytes"] = size
            generated += 1
            chars_sent += len(block_text)
            print_fn(f"    -> {audio_filename} ({size:,} bytes)")
        else:
            entry["size_bytes"] = (
                audio_path.stat().st_size if audio_path.exists() else 0
            )
            skipped += 1

        manifest.append(entry)

    # Orphan cleanup on real runs only.
    expected = {e["audio_file"] for e in manifest}
    orphans_removed: list[str] = []
    if not dry_run:
        orphans_removed = cleanup_orphans(module_audio_dir, expected)
        for name in orphans_removed:
            print_fn(f"  [{module_name}] Removing orphan: {name}")
        write_manifest(module_audio_dir, manifest)

    summary = f"{module_name}: {len(blocks)} blocks"
    if generated:
        summary += f", {generated} generated"
    if would_generate:
        summary += f", {would_generate} would generate"
    if skipped:
        summary += f", {skipped} skipped"
    if orphans_removed:
        summary += f", {len(orphans_removed)} orphan(s) removed"
    print_fn(f"  {summary}")

    return {
        "module": module_name,
        "manifest": manifest,
        "generated": generated,
        "skipped": skipped,
        "would_generate": would_generate,
        "chars_sent": chars_sent,
        "orphans_removed": orphans_removed,
    }


def select_source_files(
    source_dir: Path,
    *,
    explicit: Path | None = None,
    include_all: bool = False,
) -> list[Path]:
    """Return the source files to process.

    Selection rules:

    - ``explicit`` is a path provided on the CLI. If it points to a file,
      return ``[that file]``. If it points to a directory, glob ``*.md``
      under it.
    - Otherwise, when ``include_all`` is True, glob every ``*.md`` under
      ``source_dir`` (auxiliary files: crash courses, references).
    - Otherwise, glob ``module-*.md`` (the default scope: just modules).

    Returned list is sorted for deterministic ordering.
    """
    if explicit is not None:
        if explicit.is_file():
            return [explicit]
        if explicit.is_dir():
            return sorted(explicit.glob("*.md"))
        return []
    if include_all:
        return sorted(source_dir.glob("*.md"))
    return sorted(source_dir.glob("module-*.md"))


# ---------------------------------------------------------------------------
# Cost reporting.
# ---------------------------------------------------------------------------


def format_cost_summary(
    total_chars: int,
    *,
    provider: str = "elevenlabs",
    model: str = DEFAULT_MODEL,
    blocks_generated: int = 0,
) -> str:
    """Return the end-of-run cost summary line.

    For ``eleven_multilingual_v2`` the rate is 1 credit per character
    (see :data:`CREDITS_PER_CHAR`); total characters sent ARE total
    credits spent. Format::

        elevenlabs eleven_multilingual_v2: 12 blocks generated, 4321 chars sent = 4321 credits

    The single-line shape mirrors :func:`_media_lib.cost.format_cost_summary`
    so logs across the audio + image generators look uniform.
    """
    credits = int(round(total_chars * CREDITS_PER_CHAR))
    return (
        f"{provider} {model}: {blocks_generated} blocks generated, "
        f"{total_chars} chars sent = {credits} credits"
    )


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate narration audio from inline > 🎙️ markdown blocks "
            "via ElevenLabs TTS."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "source",
        nargs="?",
        help=(
            "Single source file or directory. If omitted, the default "
            "source directory is used (./source by default)."
        ),
    )
    parser.add_argument(
        "--source-dir",
        default=None,
        help="Source directory to walk (default: ./source if it exists, else cwd).",
    )
    parser.add_argument(
        "--audio-dir",
        default=None,
        help="Audio output directory (default: ./audio).",
    )
    parser.add_argument(
        "--plan",
        default=None,
        help=(
            "Optional path to NARRATION-PLAN.md for informational "
            "Voice/Model defaults. CLI flags override the plan."
        ),
    )
    parser.add_argument(
        "--voice",
        default=None,
        help=(
            f"ElevenLabs voice name or ID (default: {DEFAULT_VOICE}). "
            "Stock names resolve via the in-script voice map; unknown "
            "values pass through as raw IDs."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"ElevenLabs model ID (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without making API calls.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate ALL audio for the run, even if files exist.",
    )
    parser.add_argument(
        "--regenerate-changed",
        action="store_true",
        help=(
            "Regenerate audio only for blocks whose stripped text "
            "differs from the manifest."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Include auxiliary source files (every *.md) instead of "
            "the default module-*.md glob."
        ),
    )
    return parser


def _resolve_voice_and_model(
    cli_voice: str | None,
    cli_model: str | None,
    plan_text: str | None,
) -> tuple[str, str]:
    """Resolve effective voice + model from CLI + plan + defaults.

    Per ADR-011, CLI flags ALWAYS win. The plan is read for
    ``Voice:``/``Model:`` defaults but never overrides the CLI.
    """
    plan_fm: dict[str, str] = {}
    if plan_text is not None:
        plan_fm = parse_plan_frontmatter(plan_text)
    voice = cli_voice or plan_fm.get("voice") or DEFAULT_VOICE
    model = cli_model or plan_fm.get("model") or DEFAULT_MODEL
    return voice, model


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Returns the process exit code."""
    parser = _build_argparser()
    args = parser.parse_args(argv)

    # .env discovery (only useful when generating audio for real).
    load_env()

    # Resolve source / audio directories.
    cwd = Path.cwd()
    source_dir = (
        Path(args.source_dir) if args.source_dir
        else (cwd / "source" if (cwd / "source").is_dir() else cwd)
    )
    audio_dir = Path(args.audio_dir) if args.audio_dir else cwd / "audio"

    explicit = Path(args.source) if args.source else None
    if explicit is not None and not explicit.exists():
        # Allow short forms relative to source_dir (matches the reference).
        alt = source_dir / args.source
        if alt.exists():
            explicit = alt

    files = select_source_files(
        source_dir, explicit=explicit, include_all=args.all,
    )

    # Plan parsing — informational only.
    plan_text = None
    if args.plan:
        plan_path = Path(args.plan)
        if plan_path.is_file():
            plan_text = plan_path.read_text()
        else:
            print(f"WARNING: plan file not found: {plan_path}", file=sys.stderr)

    voice_name, model_id = _resolve_voice_and_model(args.voice, args.model, plan_text)
    voice_id = resolve_voice(voice_name)

    if not files:
        print("No source files found.")
        return 0

    print(f"Processing {len(files)} file(s)...")
    print(f"Audio output: {audio_dir}")
    print(f"Voice: {voice_name} (id: {voice_id})")
    print(f"Model: {model_id}")
    if args.force:
        print("FORCE MODE - all audio will be regenerated")
    if args.regenerate_changed:
        print("REGENERATE CHANGED - only blocks with edited text will be regenerated")
    if args.dry_run:
        print("DRY RUN - no audio will be generated")
    print()

    # Build the client only when we will actually generate.
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            print(
                "ERROR: ELEVENLABS_API_KEY not set (process env or .env file)",
                file=sys.stderr,
            )
            return 2
        client = get_elevenlabs_client(api_key)

    total_blocks = 0
    total_generated = 0
    total_would_generate = 0
    total_skipped = 0
    total_chars = 0

    for f in files:
        result = process_source(
            f, audio_dir,
            client=client,
            voice_id=voice_id,
            model_id=model_id,
            force=args.force,
            regenerate_changed=args.regenerate_changed,
            dry_run=args.dry_run,
        )
        total_blocks += len(result["manifest"])
        total_generated += result["generated"]
        total_would_generate += result["would_generate"]
        total_skipped += result["skipped"]
        total_chars += result["chars_sent"]

    print()
    print(f"Total: {total_blocks} narration blocks across {len(files)} files")
    if args.dry_run:
        print(
            f"Dry-run preview: {total_would_generate} block(s) would be generated, "
            f"{total_skipped} skipped"
        )
        print("(Run without --dry-run to spend credits and generate.)")
    else:
        print(
            format_cost_summary(
                total_chars,
                model=model_id,
                blocks_generated=total_generated,
            )
        )
    return 0


if __name__ == "__main__":  # pragma: no cover - module entrypoint
    raise SystemExit(main())
