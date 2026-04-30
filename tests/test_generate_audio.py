"""Tests for ``.claude/shared/skills/generate-audio/generate_audio.py``.

The script under test is a kit-distributed skill that ships into generated
projects, so it lives outside ``foundry_app/`` and gets loaded here via
``importlib.util.spec_from_file_location`` (mirroring ``test_generate_image.py``
and ``test_media_lib.py``).

The ``elevenlabs`` SDK is mocked end-to-end so the tests do not require the
package and never hit a real API endpoint during ``uv run pytest``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Loader — bring generate_audio.py in by file path.
# ---------------------------------------------------------------------------

_FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = (
    _FOUNDRY_ROOT / ".claude" / "shared" / "skills" / "generate-audio" / "generate_audio.py"
)


def _load_generate_audio() -> ModuleType:
    mod_name = "generate_audio_under_test"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


ga = _load_generate_audio()


# ---------------------------------------------------------------------------
# Block scanner — finds ``> 🎙️`` blocks; ignores other blockquotes.
# ---------------------------------------------------------------------------


class TestNarrationBlockScanner:
    def test_finds_single_block(self):
        md = "> 🎙️ Welcome to the course.\n"
        blocks = ga.find_narration_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["index"] == 0
        assert "Welcome to the course." in blocks[0]["text"]

    def test_finds_multiple_blocks(self):
        md = (
            "# Module 00\n"
            "> 🎙️ First block.\n"
            "\n"
            "Some prose between.\n"
            "\n"
            "> 🎙️ Second block.\n"
        )
        blocks = ga.find_narration_blocks(md)
        assert len(blocks) == 2
        assert blocks[0]["text"] == "First block."
        assert blocks[1]["text"] == "Second block."
        # Indexes are 0-based in scanner output.
        assert [b["index"] for b in blocks] == [0, 1]

    def test_handles_multiline_block(self):
        md = (
            "> 🎙️ This is line one\n"
            "> and this is line two\n"
            "> and this is line three.\n"
        )
        blocks = ga.find_narration_blocks(md)
        assert len(blocks) == 1
        # Multi-line blocks collapse to single-spaced narration after stripping.
        assert blocks[0]["text"] == "This is line one and this is line two and this is line three."

    def test_ignores_non_microphone_blockquotes(self):
        md = (
            "> Just a plain blockquote.\n"
            "\n"
            "> 🎙️ Real narration block.\n"
            "\n"
            "> Another plain blockquote.\n"
        )
        blocks = ga.find_narration_blocks(md)
        assert len(blocks) == 1
        assert blocks[0]["text"] == "Real narration block."

    def test_returns_empty_for_no_blocks(self):
        md = "# A module\n\nJust prose, no narration.\n"
        assert ga.find_narration_blocks(md) == []

    def test_strips_markdown_via_media_lib(self):
        # Stripping is delegated; we don't re-test the regex order here
        # (BEAN-281's contract test owns that). We only verify that a
        # block carrying markdown markers comes out stripped — i.e. that
        # find_narration_blocks calls into normalize_narration_text.
        md = "> 🎙️ This **bold** and *italic* and `code`.\n"
        blocks = ga.find_narration_blocks(md)
        assert blocks[0]["text"] == "This bold and italic and code."

    def test_delegates_stripping_to_media_lib(self):
        # Spy on the imported function — proves we route through
        # _media_lib instead of a private re-implementation.
        with patch.object(ga, "normalize_narration_text", side_effect=ga.normalize_narration_text) as spy:
            ga.find_narration_blocks("> 🎙️ A block.\n")
            assert spy.called

    def test_position_is_byte_offset_in_source(self):
        md = "intro\n\n> 🎙️ The block.\n"
        blocks = ga.find_narration_blocks(md)
        assert blocks[0]["position"] >= 0
        # Source slice at the position should contain the block start.
        assert "🎙️" in md[blocks[0]["position"]:]


# ---------------------------------------------------------------------------
# NARRATION-PLAN.md frontmatter parser — Voice + Model only; informational.
# ---------------------------------------------------------------------------


class TestPlanFrontmatterParser:
    def test_parses_voice_and_model(self):
        plan = (
            "# Narration Plan\n"
            "**Voice:** rachel\n"
            "**Model:** eleven_multilingual_v2\n"
            "\n"
            "## Module 00\n"
        )
        d = ga.parse_plan_frontmatter(plan)
        assert d == {"voice": "rachel", "model": "eleven_multilingual_v2"}

    def test_only_parses_head_before_first_heading(self):
        plan = (
            "**Voice:** keep_me\n"
            "## Module 00\n"
            "**Voice:** ignore_me\n"
        )
        d = ga.parse_plan_frontmatter(plan)
        assert d["voice"] == "keep_me"

    def test_ignores_unrecognized_keys(self):
        plan = (
            "**Voice:** rachel\n"
            "**Style:** smooth\n"
            "**Branding:** purple\n"
        )
        d = ga.parse_plan_frontmatter(plan)
        assert d == {"voice": "rachel"}

    def test_empty_when_no_frontmatter(self):
        assert ga.parse_plan_frontmatter("# No frontmatter here\n\n## Section\n") == {}


# ---------------------------------------------------------------------------
# Voice resolution — stock map + passthrough; no cloned IDs in code.
# ---------------------------------------------------------------------------


class TestResolveVoice:
    def test_rachel_resolves_to_canonical_id(self):
        assert ga.resolve_voice("rachel") == "21m00Tcm4TlvDq8ikWAM"

    def test_other_stock_names_resolve(self):
        # The ADR pins the policy (stock names only); the exact list lives
        # here in code. Spot-check that a couple resolve consistently.
        assert ga.resolve_voice("drew") == ga.STOCK_VOICE_MAP["drew"]
        assert ga.resolve_voice("sarah") == ga.STOCK_VOICE_MAP["sarah"]

    def test_unknown_name_passes_through(self):
        # Unknown values go to ElevenLabs as raw IDs (could be a name in
        # the user's voice library, a raw ID, or a typo). Not validated.
        assert ga.resolve_voice("MyCustomVoice") == "MyCustomVoice"
        assert ga.resolve_voice("s6d7r1gfIA8ArVv5Vocl") == "s6d7r1gfIA8ArVv5Vocl"

    def test_no_cloned_voice_ids_in_committed_code(self):
        # Defense in depth — the voice map ships in every kit consumer.
        # This test fails CI if anyone accidentally adds a known cloned
        # ID to the stock map.
        forbidden = {
            "s6d7r1gfIA8ArVv5Vocl",  # Stonewaters / Gregg Reed cloned voice
        }
        for vid in ga.STOCK_VOICE_MAP.values():
            assert vid not in forbidden, (
                f"Cloned voice ID {vid!r} leaked into STOCK_VOICE_MAP"
            )

    def test_default_voice_is_rachel(self):
        assert ga.DEFAULT_VOICE == "rachel"


# ---------------------------------------------------------------------------
# Manifest loader.
# ---------------------------------------------------------------------------


class TestLoadExistingManifest:
    def test_returns_empty_when_missing(self, tmp_path: Path):
        assert ga.load_existing_manifest(tmp_path) == {}

    def test_indexes_by_block_number(self, tmp_path: Path):
        manifest = [
            {"index": 1, "module": "m", "audio_file": "01_m.mp3", "text": "a", "size_bytes": 10},
            {"index": 2, "module": "m", "audio_file": "02_m.mp3", "text": "b", "size_bytes": 20},
        ]
        (tmp_path / "manifest.json").write_text(json.dumps(manifest))
        loaded = ga.load_existing_manifest(tmp_path)
        assert set(loaded.keys()) == {1, 2}
        assert loaded[1]["text"] == "a"

    def test_returns_empty_when_corrupt(self, tmp_path: Path):
        (tmp_path / "manifest.json").write_text("not json {{{")
        assert ga.load_existing_manifest(tmp_path) == {}

    def test_returns_empty_when_shape_wrong(self, tmp_path: Path):
        (tmp_path / "manifest.json").write_text(json.dumps([{"foo": "bar"}]))
        assert ga.load_existing_manifest(tmp_path) == {}


# ---------------------------------------------------------------------------
# No cloned voice IDs in committed source — text-level scan as belt-and-braces.
# ---------------------------------------------------------------------------


def test_source_contains_no_cloned_voice_ids():
    """Hard guard: scan the script's own source for forbidden cloned IDs.

    The kit ships to every consumer. A cloned voice ID checked into the
    skill source leaks one user's voice into every downstream project.
    """
    forbidden = {
        "s6d7r1gfIA8ArVv5Vocl",  # Stonewaters / Gregg Reed cloned voice
    }
    src = _SCRIPT_PATH.read_text()
    for vid in forbidden:
        assert vid not in src, (
            f"Cloned voice ID {vid!r} found in committed source {_SCRIPT_PATH}"
        )
