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


# ---------------------------------------------------------------------------
# Manifest writer + orphan cleanup.
# ---------------------------------------------------------------------------


class TestWriteManifest:
    def test_writes_array_of_records(self, tmp_path: Path):
        entries = [
            {"index": 1, "module": "m", "audio_file": "01_m.mp3", "text": "a", "size_bytes": 10},
        ]
        ga.write_manifest(tmp_path, entries)
        loaded = json.loads((tmp_path / "manifest.json").read_text())
        assert loaded == entries

    def test_creates_directory_if_missing(self, tmp_path: Path):
        target = tmp_path / "deep" / "nested"
        ga.write_manifest(target, [])
        assert (target / "manifest.json").exists()


class TestCleanupOrphans:
    def test_removes_orphans(self, tmp_path: Path):
        (tmp_path / "01_m.mp3").write_bytes(b"a")
        (tmp_path / "02_m.mp3").write_bytes(b"b")
        (tmp_path / "99_old.mp3").write_bytes(b"old")
        removed = ga.cleanup_orphans(tmp_path, {"01_m.mp3", "02_m.mp3"})
        assert removed == ["99_old.mp3"]
        assert not (tmp_path / "99_old.mp3").exists()
        assert (tmp_path / "01_m.mp3").exists()

    def test_no_orphans_returns_empty(self, tmp_path: Path):
        (tmp_path / "01_m.mp3").write_bytes(b"a")
        assert ga.cleanup_orphans(tmp_path, {"01_m.mp3"}) == []

    def test_missing_dir_no_op(self, tmp_path: Path):
        assert ga.cleanup_orphans(tmp_path / "does-not-exist", {"x.mp3"}) == []

    def test_ignores_non_mp3_files(self, tmp_path: Path):
        (tmp_path / "01_m.mp3").write_bytes(b"a")
        (tmp_path / "manifest.json").write_text("[]")
        (tmp_path / "README.md").write_text("# notes")
        removed = ga.cleanup_orphans(tmp_path, {"01_m.mp3"})
        assert removed == []
        assert (tmp_path / "manifest.json").exists()
        assert (tmp_path / "README.md").exists()


# ---------------------------------------------------------------------------
# ElevenLabs client integration — fully mocked.
# ---------------------------------------------------------------------------


class TestGenerateAudioForBlock:
    def _mock_client(self, audio_bytes: bytes = b"\x00\x01\x02\x03") -> MagicMock:
        client = MagicMock()
        # text_to_speech.convert returns an iterable of byte chunks.
        client.text_to_speech.convert.return_value = iter([audio_bytes])
        return client

    def test_writes_mp3_and_returns_size(self, tmp_path: Path):
        client = self._mock_client(b"x" * 1024)
        out = tmp_path / "audio" / "m" / "01_m.mp3"
        size = ga.generate_audio_for_block(
            client, "hello", out, voice_id="VID", model_id="MOD",
        )
        assert size == 1024
        assert out.exists()
        assert out.read_bytes() == b"x" * 1024

    def test_passes_voice_and_model_to_convert(self, tmp_path: Path):
        client = self._mock_client()
        out = tmp_path / "01_m.mp3"
        ga.generate_audio_for_block(
            client, "hello", out, voice_id="V123", model_id="MOD42",
        )
        client.text_to_speech.convert.assert_called_once()
        kwargs = client.text_to_speech.convert.call_args.kwargs
        assert kwargs["text"] == "hello"
        assert kwargs["voice_id"] == "V123"
        assert kwargs["model_id"] == "MOD42"
        assert kwargs["output_format"] == "mp3_44100_128"

    def test_default_model_is_eleven_multilingual_v2(self, tmp_path: Path):
        client = self._mock_client()
        out = tmp_path / "01_m.mp3"
        ga.generate_audio_for_block(client, "x", out, voice_id="V")
        kwargs = client.text_to_speech.convert.call_args.kwargs
        assert kwargs["model_id"] == ga.DEFAULT_MODEL == "eleven_multilingual_v2"

    def test_creates_parent_dirs(self, tmp_path: Path):
        client = self._mock_client()
        out = tmp_path / "deep" / "tree" / "x.mp3"
        ga.generate_audio_for_block(client, "x", out, voice_id="V")
        assert out.exists()


class TestGetElevenlabsClient:
    def test_constructs_client_with_api_key(self, monkeypatch):
        captured = {}

        class FakeEL:
            def __init__(self, api_key: str) -> None:
                captured["api_key"] = api_key

        monkeypatch.setattr(ga, "_import_elevenlabs", lambda: FakeEL)
        client = ga.get_elevenlabs_client("test-key")
        assert isinstance(client, FakeEL)
        assert captured["api_key"] == "test-key"


# ---------------------------------------------------------------------------
# Skip-on-disk decision matrix.
# ---------------------------------------------------------------------------


class TestDecideAction:
    def test_missing_file_means_generate_new(self, tmp_path: Path):
        needs, reason = ga.decide_action(
            "hi", tmp_path / "missing.mp3", None,
            force=False, regenerate_changed=False,
        )
        assert needs is True
        assert reason == "new"

    def test_existing_file_no_flags_means_skip(self, tmp_path: Path):
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, reason = ga.decide_action(
            "hi", p, {"text": "hi"},
            force=False, regenerate_changed=False,
        )
        assert needs is False
        assert reason == "exists"

    def test_force_means_generate_even_when_exists(self, tmp_path: Path):
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, reason = ga.decide_action(
            "hi", p, {"text": "hi"},
            force=True, regenerate_changed=False,
        )
        assert needs is True
        assert reason == "forced"

    def test_regenerate_changed_when_text_differs(self, tmp_path: Path):
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, reason = ga.decide_action(
            "new text", p, {"text": "old text"},
            force=False, regenerate_changed=True,
        )
        assert needs is True
        assert reason == "text changed"

    def test_regenerate_changed_when_text_same_means_skip(self, tmp_path: Path):
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, _reason = ga.decide_action(
            "same", p, {"text": "same"},
            force=False, regenerate_changed=True,
        )
        assert needs is False

    def test_regenerate_changed_with_no_existing_entry_skips(self, tmp_path: Path):
        # The "missing in manifest but file exists on disk" case — without
        # existing-text to compare we can't decide change; default is skip.
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, _reason = ga.decide_action(
            "anything", p, None,
            force=False, regenerate_changed=True,
        )
        assert needs is False

    def test_force_wins_over_regenerate_changed(self, tmp_path: Path):
        p = tmp_path / "x.mp3"
        p.write_bytes(b"a")
        needs, reason = ga.decide_action(
            "same", p, {"text": "same"},
            force=True, regenerate_changed=True,
        )
        assert needs is True
        assert reason == "forced"


# ---------------------------------------------------------------------------
# process_source — end-to-end with mocked client.
# ---------------------------------------------------------------------------


def _mock_client(audio_bytes: bytes = b"x" * 100) -> MagicMock:
    client = MagicMock()
    # Each call returns a fresh iterator of bytes.
    client.text_to_speech.convert.side_effect = lambda **_: iter([audio_bytes])
    return client


class TestProcessSource:
    def _write_source(self, tmp_path: Path, body: str) -> Path:
        src = tmp_path / "source"
        src.mkdir()
        f = src / "module-00-intro.md"
        f.write_text(body)
        return f

    def test_default_generates_missing(self, tmp_path: Path):
        f = self._write_source(
            tmp_path,
            "# M\n> 🎙️ First.\n\n> 🎙️ Second.\n",
        )
        client = _mock_client(b"x" * 1024)
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        assert result["generated"] == 2
        assert result["skipped"] == 0
        assert result["chars_sent"] == len("First.") + len("Second.")
        # Two API calls.
        assert client.text_to_speech.convert.call_count == 2

    def test_skips_existing_by_default(self, tmp_path: Path):
        f = self._write_source(
            tmp_path,
            "> 🎙️ Same text.\n",
        )
        # Pre-create the MP3 + manifest with matching text.
        audio_dir = tmp_path / "audio" / "module-00-intro"
        audio_dir.mkdir(parents=True)
        (audio_dir / "01_module-00-intro.mp3").write_bytes(b"old")
        (audio_dir / "manifest.json").write_text(json.dumps([
            {"index": 1, "module": "module-00-intro",
             "audio_file": "01_module-00-intro.mp3",
             "text": "Same text.", "size_bytes": 3}
        ]))
        client = _mock_client()
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        assert result["generated"] == 0
        assert result["skipped"] == 1
        assert client.text_to_speech.convert.call_count == 0

    def test_force_regenerates_existing(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ Hi.\n")
        audio_dir = tmp_path / "audio" / "module-00-intro"
        audio_dir.mkdir(parents=True)
        (audio_dir / "01_module-00-intro.mp3").write_bytes(b"old")
        client = _mock_client(b"NEW")
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V", force=True,
            print_fn=lambda *_a, **_k: None,
        )
        assert result["generated"] == 1
        assert (audio_dir / "01_module-00-intro.mp3").read_bytes() == b"NEW"

    def test_regenerate_changed_when_text_drifted(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ NEW text.\n")
        audio_dir = tmp_path / "audio" / "module-00-intro"
        audio_dir.mkdir(parents=True)
        (audio_dir / "01_module-00-intro.mp3").write_bytes(b"old")
        (audio_dir / "manifest.json").write_text(json.dumps([
            {"index": 1, "module": "module-00-intro",
             "audio_file": "01_module-00-intro.mp3",
             "text": "OLD text.", "size_bytes": 3}
        ]))
        client = _mock_client(b"NEW2")
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V", regenerate_changed=True,
            print_fn=lambda *_a, **_k: None,
        )
        assert result["generated"] == 1
        # Manifest now reflects the new text.
        manifest = json.loads((audio_dir / "manifest.json").read_text())
        assert manifest[0]["text"] == "NEW text."

    def test_dry_run_no_api_no_filesystem_writes(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ Block one.\n")
        client = _mock_client()
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V", dry_run=True,
            print_fn=lambda *_a, **_k: None,
        )
        assert result["generated"] == 0
        assert result["would_generate"] == 1
        assert result["chars_sent"] == 0
        assert client.text_to_speech.convert.call_count == 0
        # No manifest written under dry-run.
        assert not (tmp_path / "audio" / "module-00-intro" / "manifest.json").exists()

    def test_dry_run_skips_orphan_cleanup(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ Block one.\n")
        audio_dir = tmp_path / "audio" / "module-00-intro"
        audio_dir.mkdir(parents=True)
        (audio_dir / "99_orphan.mp3").write_bytes(b"orphan")
        client = _mock_client()
        ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V", dry_run=True,
            print_fn=lambda *_a, **_k: None,
        )
        # Orphan MUST still exist after dry-run.
        assert (audio_dir / "99_orphan.mp3").exists()

    def test_orphan_cleanup_on_real_run(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ Only block.\n")
        audio_dir = tmp_path / "audio" / "module-00-intro"
        audio_dir.mkdir(parents=True)
        (audio_dir / "99_orphan.mp3").write_bytes(b"orphan")
        client = _mock_client()
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        assert result["orphans_removed"] == ["99_orphan.mp3"]
        assert not (audio_dir / "99_orphan.mp3").exists()

    def test_writes_manifest_with_stripped_text(self, tmp_path: Path):
        f = self._write_source(
            tmp_path,
            "> 🎙️ Has **bold** and *italic*.\n",
        )
        client = _mock_client()
        ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        manifest = json.loads(
            (tmp_path / "audio" / "module-00-intro" / "manifest.json").read_text()
        )
        assert manifest[0]["text"] == "Has bold and italic."
        # Stripped text is also what was sent to ElevenLabs.
        kwargs = client.text_to_speech.convert.call_args.kwargs
        assert kwargs["text"] == "Has bold and italic."

    def test_manifest_record_shape(self, tmp_path: Path):
        f = self._write_source(tmp_path, "> 🎙️ Block.\n")
        client = _mock_client(b"x" * 7)
        ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        manifest = json.loads(
            (tmp_path / "audio" / "module-00-intro" / "manifest.json").read_text()
        )
        assert manifest[0] == {
            "index": 1,
            "module": "module-00-intro",
            "audio_file": "01_module-00-intro.mp3",
            "text": "Block.",
            "size_bytes": 7,
        }

    def test_no_blocks_returns_empty_manifest(self, tmp_path: Path):
        f = self._write_source(tmp_path, "# Just prose, no narration.\n")
        client = _mock_client()
        result = ga.process_source(
            f, tmp_path / "audio",
            client=client, voice_id="V",
            print_fn=lambda *_a, **_k: None,
        )
        assert result["manifest"] == []
        assert result["generated"] == 0
        assert client.text_to_speech.convert.call_count == 0


# ---------------------------------------------------------------------------
# Source file selection.
# ---------------------------------------------------------------------------


class TestSelectSourceFiles:
    def test_default_glob_matches_module_only(self, tmp_path: Path):
        src = tmp_path / "source"
        src.mkdir()
        for name in ("module-00.md", "module-01.md", "crash-course.md", "README.md"):
            (src / name).write_text("x")
        files = ga.select_source_files(src)
        assert sorted(f.name for f in files) == ["module-00.md", "module-01.md"]

    def test_all_includes_auxiliary_files(self, tmp_path: Path):
        src = tmp_path / "source"
        src.mkdir()
        for name in ("module-00.md", "crash-course.md", "appendix.md"):
            (src / name).write_text("x")
        files = ga.select_source_files(src, include_all=True)
        assert sorted(f.name for f in files) == [
            "appendix.md", "crash-course.md", "module-00.md",
        ]

    def test_explicit_file_returned_directly(self, tmp_path: Path):
        src = tmp_path / "source"
        src.mkdir()
        f = src / "anywhere.md"
        f.write_text("x")
        assert ga.select_source_files(src, explicit=f) == [f]

    def test_explicit_directory_globs(self, tmp_path: Path):
        d = tmp_path / "elsewhere"
        d.mkdir()
        for name in ("a.md", "b.md", "c.txt"):
            (d / name).write_text("x")
        files = ga.select_source_files(tmp_path / "source-unused", explicit=d)
        assert sorted(f.name for f in files) == ["a.md", "b.md"]

    def test_explicit_missing_returns_empty(self, tmp_path: Path):
        src = tmp_path / "source"
        src.mkdir()
        files = ga.select_source_files(src, explicit=tmp_path / "no-exist")
        assert files == []


# ---------------------------------------------------------------------------
# Cost reporting — char-count = credits.
# ---------------------------------------------------------------------------


class TestCostSummary:
    def test_credits_equal_chars_for_v2(self):
        out = ga.format_cost_summary(1234, blocks_generated=5)
        assert "1234 chars sent" in out
        assert "1234 credits" in out
        assert "5 blocks generated" in out

    def test_zero_chars_zero_credits(self):
        out = ga.format_cost_summary(0)
        assert "0 chars sent" in out
        assert "0 credits" in out

    def test_default_model_in_summary(self):
        out = ga.format_cost_summary(100)
        assert "elevenlabs" in out
        assert ga.DEFAULT_MODEL in out

    def test_credit_rate_constant_is_one(self):
        # ADR-011 cost discipline: eleven_multilingual_v2 = 1 credit/char.
        # If ElevenLabs ever changes this, the cost table in code is the
        # source of truth — but we want a CI signal when it changes.
        assert ga.CREDITS_PER_CHAR == 1.0


# ---------------------------------------------------------------------------
# Voice + model resolution — CLI wins over plan; plan fallback; default.
# ---------------------------------------------------------------------------


class TestResolveVoiceAndModel:
    def test_cli_overrides_plan(self):
        plan = "**Voice:** rachel\n**Model:** plan_model\n"
        v, m = ga._resolve_voice_and_model("drew", "cli_model", plan)
        assert v == "drew"
        assert m == "cli_model"

    def test_plan_fills_when_cli_missing(self):
        plan = "**Voice:** sarah\n**Model:** plan_model\n"
        v, m = ga._resolve_voice_and_model(None, None, plan)
        assert v == "sarah"
        assert m == "plan_model"

    def test_defaults_when_neither_present(self):
        v, m = ga._resolve_voice_and_model(None, None, None)
        assert v == ga.DEFAULT_VOICE == "rachel"
        assert m == ga.DEFAULT_MODEL == "eleven_multilingual_v2"

    def test_partial_cli_partial_plan(self):
        plan = "**Voice:** sarah\n"  # plan has voice; we override model on CLI.
        v, m = ga._resolve_voice_and_model(None, "cli_model", plan)
        assert v == "sarah"
        assert m == "cli_model"


# ---------------------------------------------------------------------------
# main() CLI — dry-run path (no API), char-count summary in output.
# ---------------------------------------------------------------------------


class TestMainCLI:
    def _setup_project(self, tmp_path: Path) -> tuple[Path, Path]:
        src = tmp_path / "source"
        src.mkdir()
        (src / "module-00.md").write_text("> 🎙️ Hello world.\n")
        (src / "module-01.md").write_text("> 🎙️ Another block.\n")
        audio = tmp_path / "audio"
        return src, audio

    def test_dry_run_makes_no_api_calls(self, tmp_path: Path, capsys, monkeypatch):
        src, audio = self._setup_project(tmp_path)
        # Guard: even if an API key is present, dry-run must not build a client.
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake")
        monkeypatch.setattr(
            ga, "get_elevenlabs_client",
            lambda _key: pytest.fail("should not build client under --dry-run"),
        )
        rc = ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(audio),
            "--dry-run",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "DRY RUN" in out
        assert "would be generated" in out

    def test_missing_api_key_fails_outside_dry_run(self, tmp_path: Path, monkeypatch, capsys):
        src, audio = self._setup_project(tmp_path)
        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        # Stub load_env to avoid pulling in a real .env from cwd.
        monkeypatch.setattr(ga, "load_env", lambda *a, **k: {})
        rc = ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(audio),
        ])
        assert rc == 2
        err = capsys.readouterr().err
        assert "ELEVENLABS_API_KEY" in err

    def test_full_run_prints_char_count_summary(
        self, tmp_path: Path, monkeypatch, capsys,
    ):
        src, audio = self._setup_project(tmp_path)
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake")
        monkeypatch.setattr(ga, "load_env", lambda *a, **k: {})
        client = _mock_client(b"x" * 100)
        monkeypatch.setattr(ga, "get_elevenlabs_client", lambda _key: client)

        rc = ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(audio),
        ])
        assert rc == 0
        out = capsys.readouterr().out
        # 2 blocks, "Hello world." (12) + "Another block." (14) = 26 chars.
        assert "26 chars sent" in out
        assert "26 credits" in out
        # Two API calls.
        assert client.text_to_speech.convert.call_count == 2
        # Manifests written.
        assert (audio / "module-00" / "manifest.json").exists()
        assert (audio / "module-01" / "manifest.json").exists()

    def test_voice_flag_overrides_plan_voice(self, tmp_path: Path, monkeypatch):
        src, audio = self._setup_project(tmp_path)
        plan = tmp_path / "NARRATION-PLAN.md"
        plan.write_text("**Voice:** rachel\n")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake")
        monkeypatch.setattr(ga, "load_env", lambda *a, **k: {})
        client = _mock_client()
        monkeypatch.setattr(ga, "get_elevenlabs_client", lambda _key: client)

        ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(audio),
            "--plan", str(plan),
            "--voice", "drew",
        ])
        # All convert calls should have used drew's stock ID, not rachel's.
        for call in client.text_to_speech.convert.call_args_list:
            assert call.kwargs["voice_id"] == ga.STOCK_VOICE_MAP["drew"]
            assert call.kwargs["voice_id"] != ga.STOCK_VOICE_MAP["rachel"]

    def test_all_flag_includes_auxiliary(self, tmp_path: Path, monkeypatch, capsys):
        src = tmp_path / "source"
        src.mkdir()
        (src / "module-00.md").write_text("> 🎙️ A.\n")
        (src / "crash-course.md").write_text("> 🎙️ B.\n")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake")
        monkeypatch.setattr(ga, "load_env", lambda *a, **k: {})
        client = _mock_client()
        monkeypatch.setattr(ga, "get_elevenlabs_client", lambda _key: client)

        ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(tmp_path / "audio"),
            "--all",
        ])
        # Both files were processed; 2 API calls.
        assert client.text_to_speech.convert.call_count == 2

    def test_default_excludes_auxiliary(self, tmp_path: Path, monkeypatch):
        src = tmp_path / "source"
        src.mkdir()
        (src / "module-00.md").write_text("> 🎙️ A.\n")
        (src / "crash-course.md").write_text("> 🎙️ B.\n")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "fake")
        monkeypatch.setattr(ga, "load_env", lambda *a, **k: {})
        client = _mock_client()
        monkeypatch.setattr(ga, "get_elevenlabs_client", lambda _key: client)

        ga.main([
            "--source-dir", str(src),
            "--audio-dir", str(tmp_path / "audio"),
        ])
        # Only module-00 (1 call).
        assert client.text_to_speech.convert.call_count == 1
