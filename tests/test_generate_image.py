"""Tests for ``.claude/shared/skills/generate-image/generate_image.py``.

The script under test is a kit-distributed skill that ships into generated
projects, so it lives outside ``foundry_app/`` and gets loaded here via
``importlib.util.spec_from_file_location`` (mirroring ``test_media_lib.py``).

External SDKs (``google.genai`` and ``openai``) are mocked at the module
level so the tests do not require either package — and so we never hit a
real API endpoint during ``uv run pytest``.
"""

from __future__ import annotations

import base64
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Loader — bring generate_image.py in by file path so it's importable in the
# tests without needing to add the skills directory to PYTHONPATH globally.
# ---------------------------------------------------------------------------

_FOUNDRY_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = (
    _FOUNDRY_ROOT / ".claude" / "shared" / "skills" / "generate-image" / "generate_image.py"
)


def _load_generate_image() -> ModuleType:
    mod_name = "generate_image_under_test"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


gi = _load_generate_image()


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------


class TestFrontmatterParser:

    def test_recognizes_every_documented_key(self):
        text = (
            "# Image Plan\n"
            "**Style:** Friendly cartoon, Head First textbook style\n"
            "**Branding:** purple/violet accents\n"
            "**Aspect ratio:** 16:9\n"
            "**Background:** white\n"
            "**Text in image:** minimal\n"
            "**Avoid:** photorealistic, dark, scary\n"
            "**Philosophy:** consistent across modules\n"
            "**Generator:** gemini-3-pro-image-preview\n"
            "**Quality:** high\n"
            "**Size:** 1536x1024\n"
            "\n"
            "## Module 00\n"
        )
        d = gi.parse_frontmatter(text)
        assert d["style"].startswith("Friendly cartoon")
        assert d["branding"] == "purple/violet accents"
        assert d["aspect_ratio"] == "16:9"
        assert d["background"] == "white"
        assert d["text_in_image"] == "minimal"
        assert d["avoid"] == "photorealistic, dark, scary"
        assert d["philosophy"] == "consistent across modules"
        assert d["generator"] == "gemini-3-pro-image-preview"
        assert d["quality"] == "high"
        assert d["size"] == "1536x1024"

    def test_only_parses_head_before_first_heading(self):
        text = (
            "**Style:** keep me\n"
            "## Module 00\n"
            "**Style:** ignore me\n"
        )
        d = gi.parse_frontmatter(text)
        assert d["style"] == "keep me"

    def test_missing_keys_are_absent(self):
        d = gi.parse_frontmatter("**Style:** simple\n")
        assert "generator" not in d
        assert "quality" not in d


# ---------------------------------------------------------------------------
# Plan parser
# ---------------------------------------------------------------------------


def _write_plan(tmp_path: Path, body: str) -> Path:
    plan = tmp_path / "IMAGE-PLAN.md"
    plan.write_text(body)
    return plan


class TestPlanParser:

    def test_image_entry_with_description_only(self, tmp_path):
        plan = _write_plan(tmp_path, (
            "# Plan\n"
            "**Style:** simple\n"
            "**Background:** white\n"
            "\n"
            "## Module 00: Basics\n"
            "\n"
            "### Image 1: m00-hero\n"
            "- **File**: `images/module-00/m00-hero.png`\n"
            "- **Page**: title card\n"
            "- **Description**: A robot waving hello.\n"
        ))
        entries, defaults = gi.parse_image_plan(plan)
        assert len(entries) == 1
        e = entries[0]
        assert e["file"] == "images/module-00/m00-hero.png"
        assert e["page"] == "title card"
        assert e["description"] == "A robot waving hello."
        assert e["short_name"] == "m00-hero"
        assert e["module_title"].startswith("Module 00")
        assert e["prompt_parts"] == {}
        assert defaults["style"] == "simple"

    def test_image_entry_with_structured_prompt_block(self, tmp_path):
        plan = _write_plan(tmp_path, (
            "**Style:** ignored when Prompt block present\n"
            "## Module 01: Test\n"
            "### Image 1: m01-pipe\n"
            "- **File**: `images/m01-pipe.png`\n"
            "- **Description**: ignored\n"
            "- **Prompt**:\n"
            "    Goal: editorial illustration\n"
            "    Scene: data flowing through pipes\n"
            "    Style: Head First book style\n"
            "    Aspect ratio: 16:9\n"
            "    Background: white\n"
            "    Text in image: minimal\n"
            "    Avoid: photorealism\n"
        ))
        entries, _ = gi.parse_image_plan(plan)
        assert len(entries) == 1
        parts = entries[0]["prompt_parts"]
        assert parts["goal"] == "editorial illustration"
        assert parts["scene"] == "data flowing through pipes"
        assert parts["style"] == "Head First book style"
        assert parts["aspect_ratio"] == "16:9"
        assert parts["background"] == "white"
        assert parts["text_in_image"] == "minimal"
        assert parts["avoid"] == "photorealism"

    def test_entry_without_file_is_dropped(self, tmp_path):
        plan = _write_plan(tmp_path, (
            "## Module 01\n"
            "### Image 1: missing-file\n"
            "- **Description**: no file field, should be dropped\n"
            "### Image 2: ok\n"
            "- **File**: images/ok.png\n"
            "- **Description**: present\n"
        ))
        entries, _ = gi.parse_image_plan(plan)
        assert len(entries) == 1
        assert entries[0]["short_name"] == "ok"

    def test_assemble_prompt_uses_structured_block_when_present(self):
        entry = {
            "description": "ignored",
            "defaults": {"style": "default-style"},
            "prompt_parts": {"goal": "g", "scene": "s", "style": "from-prompt"},
        }
        out = gi.assemble_prompt_from_entry(entry)
        assert "Goal: g" in out
        assert "Scene: s" in out
        assert "Style: from-prompt" in out
        assert "default-style" not in out

    def test_assemble_prompt_falls_back_to_description_plus_defaults(self):
        entry = {
            "description": "A friendly robot.",
            "defaults": {
                "style": "Head First style",
                "aspect_ratio": "16:9",
                "background": "white",
                "avoid": "photorealism",
            },
            "prompt_parts": {},
        }
        out = gi.assemble_prompt_from_entry(entry)
        assert out.startswith("Scene: A friendly robot.")
        assert "Style: Head First style" in out
        assert "Aspect ratio: 16:9" in out
        assert "Background: white" in out
        assert "Avoid: photorealism" in out

    def test_assemble_prompt_empty_when_no_description_and_no_block(self):
        entry = {"description": "", "defaults": {}, "prompt_parts": {}}
        assert gi.assemble_prompt_from_entry(entry) == ""


# ---------------------------------------------------------------------------
# Provider dispatch — tolerant containment + regex.
# ---------------------------------------------------------------------------


class TestProviderDispatch:

    def test_default_routes_to_gemini_with_pro_model(self):
        cfg = gi.resolve_provider({})
        assert cfg["provider"] == "gemini"
        assert cfg["model"] == gi.GEMINI_PRO_MODEL
        assert cfg["friendly"] == "nanobanana-pro"
        assert cfg["quality"] == "high"

    @pytest.mark.parametrize("value", [
        "openai-gpt-image-1.5",
        "openai-gpt-image-2",
        "gpt-image-1.5",
        "gpt-image-2",
        "OpenAI gpt-image-2",
        "GPT-IMAGE-2",
        "openai",  # bare 'openai' → default OpenAI model
    ])
    def test_openai_dispatch_is_tolerant(self, value):
        cfg = gi.resolve_provider({"generator": value})
        assert cfg["provider"] == "openai"

    def test_openai_model_extracted_via_regex(self):
        cfg = gi.resolve_provider({"generator": "openai-gpt-image-1.5"})
        assert cfg["model"] == "gpt-image-1.5"
        cfg = gi.resolve_provider({"generator": "openai-gpt-image-2"})
        assert cfg["model"] == "gpt-image-2"

    def test_openai_default_model_when_no_match(self):
        cfg = gi.resolve_provider({"generator": "openai"})
        assert cfg["model"] == gi.DEFAULT_OPENAI_MODEL

    @pytest.mark.parametrize("value", [
        "gemini-3-pro-image-preview",
        "nanobanana-pro",
        "Imagen 4",
        "",
    ])
    def test_non_openai_dispatch_routes_to_gemini(self, value):
        cfg = gi.resolve_provider({"generator": value})
        assert cfg["provider"] == "gemini"

    def test_cli_override_beats_frontmatter(self):
        cfg = gi.resolve_provider(
            {"generator": "gemini-3-pro-image-preview"},
            cli_override="openai-gpt-image-2",
        )
        assert cfg["provider"] == "openai"
        assert cfg["model"] == "gpt-image-2"

    def test_frontmatter_quality_overrides_cli_default(self):
        cfg = gi.resolve_provider({"quality": "low"}, cli_quality="high")
        # Default routes to Gemini; low → nanobanana2.
        assert cfg["friendly"] == "nanobanana2"
        assert cfg["quality"] == "low"

    def test_openai_size_default(self):
        cfg = gi.resolve_provider({"generator": "openai-gpt-image-2"})
        assert cfg["size"] == gi.DEFAULT_OPENAI_SIZE

    def test_openai_size_from_frontmatter(self):
        cfg = gi.resolve_provider({
            "generator": "openai-gpt-image-2",
            "size": "1024x1536",
        })
        assert cfg["size"] == "1024x1536"


# ---------------------------------------------------------------------------
# Quality flag → provider arg mapping (every cell of the table).
# ---------------------------------------------------------------------------


class TestQualityMapping:

    @pytest.mark.parametrize("quality,expected", [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high"),
    ])
    def test_openai_quality_passthrough(self, quality, expected):
        cfg = gi.resolve_provider({"generator": "openai-gpt-image-2"}, cli_quality=quality)
        assert cfg["quality"] == expected

    @pytest.mark.parametrize("quality,expected_friendly,expected_model", [
        ("low", "nanobanana2", gi.GEMINI_FLASH_MODEL),
        ("medium", "nanobanana2", gi.GEMINI_FLASH_MODEL),
        ("high", "nanobanana-pro", gi.GEMINI_PRO_MODEL),
    ])
    def test_gemini_quality_to_friendly_model(self, quality, expected_friendly, expected_model):
        cfg = gi.resolve_provider({}, cli_quality=quality)
        assert cfg["friendly"] == expected_friendly
        assert cfg["model"] == expected_model


# ---------------------------------------------------------------------------
# OpenAI org-verification fallback path (mocked).
# ---------------------------------------------------------------------------


class _FakeOpenAIResp:
    """Minimal OpenAI Images API response shape — single image as base64."""

    def __init__(self, png_bytes: bytes):
        self.data = [SimpleNamespace(b64_json=base64.b64encode(png_bytes).decode())]


def _stub_openai_module(call_handler):
    """Build a fake ``openai`` module suitable for ``sys.modules`` injection.

    ``call_handler`` is a function ``(model, prompt, size, quality) -> _FakeOpenAIResp``
    that may raise to simulate API errors.
    """
    fake_openai = ModuleType("openai")

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.images = SimpleNamespace(generate=self._generate)

        def _generate(self, *, model, prompt, size, quality, n):
            return call_handler(model, prompt, size, quality)

    fake_openai.OpenAI = FakeClient  # type: ignore[attr-defined]
    return fake_openai


class TestOpenAIFallback:

    def test_org_verification_error_falls_back_to_1_5(self, tmp_path, monkeypatch):
        calls: list[str] = []

        def handler(model, prompt, size, quality):
            calls.append(model)
            if model == "gpt-image-2":
                raise RuntimeError(
                    "Your organization must be verified to use the model "
                    "`gpt-image-2`. Please go to platform.openai.com to verify."
                )
            return _FakeOpenAIResp(b"\x89PNG\r\n\x1a\nFAKE")

        monkeypatch.setitem(sys.modules, "openai", _stub_openai_module(handler))
        out = tmp_path / "out.png"
        config = {
            "provider": "openai",
            "model": "gpt-image-2",
            "quality": "high",
            "size": "1536x1024",
        }
        meta = gi._generate_openai("a prompt", out, "fake-key", config)

        assert calls == ["gpt-image-2", "gpt-image-1.5"]
        assert meta["fallback_used"] is True
        assert meta["model"] == "gpt-image-1.5"
        assert out.exists()

    def test_no_fallback_when_starting_with_1_5(self, tmp_path, monkeypatch):
        calls: list[str] = []

        def handler(model, prompt, size, quality):
            calls.append(model)
            return _FakeOpenAIResp(b"\x89PNG\r\n\x1a\nFAKE")

        monkeypatch.setitem(sys.modules, "openai", _stub_openai_module(handler))
        out = tmp_path / "out.png"
        config = {
            "provider": "openai",
            "model": "gpt-image-1.5",
            "quality": "low",
            "size": "1024x1024",
        }
        meta = gi._generate_openai("p", out, "fake-key", config)

        assert calls == ["gpt-image-1.5"]
        assert meta["fallback_used"] is False

    def test_billing_hard_limit_fails_fast(self, tmp_path, monkeypatch):
        calls: list[str] = []

        def handler(model, prompt, size, quality):
            calls.append(model)
            raise RuntimeError("Billing hard limit has been reached.")

        monkeypatch.setitem(sys.modules, "openai", _stub_openai_module(handler))
        with pytest.raises(RuntimeError, match="Billing hard limit"):
            gi._generate_openai("p", tmp_path / "out.png", "k", {
                "provider": "openai", "model": "gpt-image-2",
                "quality": "high", "size": "1536x1024",
            })
        # Exactly one call — no retries on billing-hard-limit.
        assert calls == ["gpt-image-2"]


# ---------------------------------------------------------------------------
# Skip-on-disk + --filter + --force + --dry-run
# ---------------------------------------------------------------------------


def _make_args(**overrides):
    """Build an argparse-style namespace with sensible defaults."""
    base = dict(
        plan=None,
        prompt=None,
        filter=None,
        force=False,
        dry_run=False,
        generator=None,
        quality=gi.DEFAULT_QUALITY,
        goal=None,
        style=None,
        aspect_ratio=None,
        background=None,
        text_in_image=None,
        color_palette=None,
        negative=None,
        reference_image=None,
        output_dir="images/misc",
        asset_name="image",
        count=1,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _basic_plan(tmp_path: Path, n: int = 2, generator: str = "") -> Path:
    body = ["# Plan", "**Style:** simple"]
    if generator:
        body.append(f"**Generator:** {generator}")
    body.append("")
    body.append("## Module 01")
    for i in range(1, n + 1):
        body.extend([
            f"### Image {i}: img-{i:02d}",
            f"- **File**: images/img-{i:02d}.png",
            f"- **Description**: image number {i}",
        ])
    return _write_plan(tmp_path, "\n".join(body) + "\n")


class TestPlanLoop:

    def test_skip_on_disk(self, tmp_path, monkeypatch):
        plan = _basic_plan(tmp_path, n=2)
        # Pre-create one of the two PNGs.
        existing = tmp_path / "images" / "img-01.png"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"already-there")

        # Mock the API call so any non-skipped entries don't need network.
        called = MagicMock(return_value={
            "provider": "gemini",
            "model": gi.GEMINI_PRO_MODEL,
            "output_file": "img-02.png",
            "generation_time_ms": 5,
            "usage": {"total_tokens": 100},
            "fallback_used": False,
        })
        monkeypatch.setattr(gi, "generate_image", called)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        # Have to make the side effect actually create the file.
        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"fake-png")
            return {
                "provider": "gemini",
                "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name,
                "generation_time_ms": 5,
                "usage": {"total_tokens": 100},
                "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)

        rc = gi.run_plan(_make_args(plan=str(plan)))
        assert rc == 0
        # The pre-existing one should NOT have been overwritten.
        assert existing.read_bytes() == b"already-there"
        # The new one should exist.
        assert (tmp_path / "images" / "img-02.png").exists()
        # And its sidecar.
        assert (tmp_path / "images" / "img-02.json").exists()

    def test_force_regenerates_existing(self, tmp_path, monkeypatch):
        plan = _basic_plan(tmp_path, n=1)
        existing = tmp_path / "images" / "img-01.png"
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b"old-content")

        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"new-content")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 5,
                "usage": {"total_tokens": 50}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        rc = gi.run_plan(_make_args(plan=str(plan), force=True))
        assert rc == 0
        assert existing.read_bytes() == b"new-content"

    def test_filter_substring(self, tmp_path, monkeypatch):
        # 3 entries — only filter for the middle one.
        plan = _basic_plan(tmp_path, n=3)
        seen: list[str] = []

        def fake(prompt, output_path, api_key, config, **kwargs):
            seen.append(output_path.name)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"x")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 1,
                "usage": {"total_tokens": 1}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        rc = gi.run_plan(_make_args(plan=str(plan), filter="img-02"))
        assert rc == 0
        assert seen == ["img-02.png"]

    def test_dry_run_makes_no_api_calls(self, tmp_path, monkeypatch, capsys):
        plan = _basic_plan(tmp_path, n=2)
        called = MagicMock()
        monkeypatch.setattr(gi, "generate_image", called)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        rc = gi.run_plan(_make_args(plan=str(plan), dry_run=True))
        assert rc == 0
        called.assert_not_called()
        out = capsys.readouterr().out
        assert "WOULD GENERATE" in out


# ---------------------------------------------------------------------------
# Sidecar JSON shape — every required field for both providers.
# ---------------------------------------------------------------------------


class TestSidecarShape:

    def test_gemini_sidecar_required_fields(self):
        meta = {
            "provider": "gemini",
            "model": gi.GEMINI_PRO_MODEL,
            "output_file": "img-01.png",
            "generation_time_ms": 1234,
            "usage": {"prompt_tokens": 10, "candidates_tokens": 20, "total_tokens": 30},
            "fallback_used": False,
        }
        sidecar = gi.build_sidecar(
            meta=meta,
            assembled_prompt="Scene: a robot",
            defaults={
                "aspect_ratio": "16:9",
                "background": "white",
                "text_in_image": "minimal",
                "avoid": "photorealism, dark",
            },
        )
        for key in (
            "timestamp", "provider", "model", "assembled_prompt", "output_file",
            "generation_time_ms", "usage", "fallback_used",
            "aspect_ratio", "background", "text_in_image", "negative_constraints",
        ):
            assert key in sidecar, f"missing required field {key!r}"
        assert sidecar["negative_constraints"] == ["photorealism", "dark"]
        assert sidecar["aspect_ratio"] == "16:9"
        assert sidecar["fallback_used"] is False

    def test_openai_sidecar_includes_quality_and_size(self):
        meta = {
            "provider": "openai",
            "model": "gpt-image-2",
            "quality": "high",
            "size": "1536x1024",
            "output_file": "img-01.png",
            "generation_time_ms": 8000,
            "fallback_used": True,
        }
        sidecar = gi.build_sidecar(
            meta=meta,
            assembled_prompt="x",
            aspect_ratio="16:9",
            background="white",
            text_in_image="minimal",
            negative_constraints=["clutter"],
        )
        assert sidecar["quality"] == "high"
        assert sidecar["size"] == "1536x1024"
        assert sidecar["fallback_used"] is True
        assert sidecar["negative_constraints"] == ["clutter"]

    def test_no_negative_constraints_yields_empty_list(self):
        meta = {
            "provider": "gemini",
            "model": gi.GEMINI_PRO_MODEL,
            "output_file": "x.png",
            "generation_time_ms": 1,
            "fallback_used": False,
        }
        sidecar = gi.build_sidecar(meta=meta, assembled_prompt="p", defaults={})
        assert sidecar["negative_constraints"] == []


# ---------------------------------------------------------------------------
# Cost summary / end-of-run output.
# ---------------------------------------------------------------------------


class TestCostSummary:

    def test_openai_cost_lookup(self):
        # Verbatim from _COST_TABLE.
        assert gi.estimate_cost(
            provider="openai", model="gpt-image-2", quality="high",
            size="1536x1024", total_tokens=0,
        ) == pytest.approx(0.165)

    def test_gemini_cost_from_tokens(self):
        # 10000 tokens × $0.00007 = $0.70
        assert gi.estimate_cost(
            provider="gemini", model=gi.GEMINI_PRO_MODEL, quality="high",
            size="", total_tokens=10000,
        ) == pytest.approx(0.7)

    def test_openai_unknown_combo_returns_zero(self):
        assert gi.estimate_cost(
            provider="openai", model="gpt-image-1.5", quality="ultra",
            size="9999x9999", total_tokens=0,
        ) == 0.0

    def test_format_run_summary_openai_includes_provider_and_cost(self):
        s = gi.format_run_summary(
            provider="openai", model="gpt-image-2",
            generated=3, skipped=1, errors=0,
            total_cost_usd=0.50, quality="high", size="1536x1024",
        )
        assert "Generated: 3" in s
        assert "openai" in s
        assert "gpt-image-2" in s
        assert "$0.50" in s

    def test_format_run_summary_gemini_includes_tokens(self):
        s = gi.format_run_summary(
            provider="gemini", model=gi.GEMINI_PRO_MODEL,
            generated=2, skipped=0, errors=0,
            total_cost_usd=0.14, total_tokens=2000,
        )
        assert "Total tokens: 2,000" in s
        assert "$0.14" in s
        assert "gemini" in s


# ---------------------------------------------------------------------------
# Rate limiter — Gemini ~18 req/min via MIN_INTERVAL_SECONDS.
# ---------------------------------------------------------------------------


class TestRateLimiter:

    def test_min_interval_constant_is_60_over_18(self):
        # The constant carries provenance from the Stonewaters reference.
        # Don't change it — it is a property of the Gemini quota.
        assert gi.MIN_INTERVAL_SECONDS == 60.0 / 18

    def test_plan_loop_sleeps_between_gemini_calls(self, tmp_path, monkeypatch):
        plan = _basic_plan(tmp_path, n=2)
        sleep_calls: list[float] = []

        # Patch sleep to record durations and not actually sleep.
        monkeypatch.setattr(gi.time, "sleep", lambda s: sleep_calls.append(s))
        # Patch time so the second iteration sees a tiny "elapsed".
        # Sequence: header writes, loop enters; first call records last_call_time
        # and uses time.time(); second iteration computes elapsed = now - last_call_time.
        clock = [1000.0]

        def fake_time():
            t = clock[0]
            clock[0] += 0.001  # tiny advance per call
            return t

        monkeypatch.setattr(gi.time, "time", fake_time)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"x")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 1,
                "usage": {"total_tokens": 1}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)

        rc = gi.run_plan(_make_args(plan=str(plan)))
        assert rc == 0
        # At least one sleep should have been recorded (between iterations).
        # The duration should be close to MIN_INTERVAL_SECONDS.
        nontrivial = [s for s in sleep_calls if s > 1.0]
        assert nontrivial, f"expected pacing sleep, got {sleep_calls!r}"
        assert max(nontrivial) <= gi.MIN_INTERVAL_SECONDS + 0.01

    def test_extract_retry_delay_from_gemini_429_body(self):
        msg = (
            "google.api_core.exceptions.ResourceExhausted: 429 "
            "RESOURCE_EXHAUSTED retryDelay: '5s'"
        )
        assert gi._extract_retry_delay(msg) == 7  # 5 + 2 jitter

    def test_extract_retry_delay_falls_back(self):
        assert gi._extract_retry_delay("nothing parseable here") == 30

    def test_extract_retry_delay_from_openai_retry_after(self):
        msg = "429 too many requests. Please retry after 12 seconds."
        assert gi._extract_retry_delay(msg) == 14


# ---------------------------------------------------------------------------
# OpenAI 429 retry path (Gemini retry path covered by Stonewaters reference).
# ---------------------------------------------------------------------------


class TestOpenAI429Retry:

    def test_429_retried_within_budget(self, tmp_path, monkeypatch):
        attempts: list[int] = []

        def handler(model, prompt, size, quality):
            attempts.append(1)
            if len(attempts) < 2:
                raise RuntimeError("429: rate limit exceeded retryDelay: '1s'")
            return _FakeOpenAIResp(b"\x89PNGOK")

        monkeypatch.setitem(sys.modules, "openai", _stub_openai_module(handler))
        # Patch sleep so retries don't actually pause.
        monkeypatch.setattr(gi.time, "sleep", lambda s: None)

        meta = gi._generate_openai("p", tmp_path / "out.png", "k", {
            "provider": "openai", "model": "gpt-image-1.5",
            "quality": "low", "size": "1024x1024",
        })
        assert len(attempts) == 2
        assert meta["fallback_used"] is False


# ---------------------------------------------------------------------------
# Full end-of-run print contains provider + count + cost.
# ---------------------------------------------------------------------------


class TestEndOfRunSummaryPrinted:

    def test_summary_prints_in_plan_loop(self, tmp_path, monkeypatch, capsys):
        plan = _basic_plan(tmp_path, n=1)

        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"x")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 1,
                "usage": {"total_tokens": 1234}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        gi.run_plan(_make_args(plan=str(plan)))
        out = capsys.readouterr().out
        assert "Generated: 1" in out
        assert "gemini" in out
        assert "Estimated cost:" in out


# ---------------------------------------------------------------------------
# .env discovery via _media_lib.env.load_env (smoke test — the loader is
# exercised in test_media_lib.py; we just check generate_image actually
# imports it and uses it without crashing).
# ---------------------------------------------------------------------------


class TestEnvDiscovery:

    def test_load_env_is_imported_from_media_lib(self):
        assert callable(gi.load_env)
        # The bound function should be the one from _media_lib (not the
        # local fallback), assuming the package is importable from the
        # script's sys.path manipulation.
        assert gi.load_env.__module__.endswith("env") or gi.load_env.__module__.endswith(
            "_media_lib.env"
        )

    def test_main_loads_env_then_dispatches(self, tmp_path, monkeypatch):
        plan = _basic_plan(tmp_path, n=1)
        # Empty .env in the plan dir; load_env should run without error.
        (tmp_path / ".env").write_text("# nothing\n")

        called = MagicMock(return_value=0)
        monkeypatch.setattr(gi, "run_plan", called)

        rc = gi.main(["--plan", str(plan)])
        assert rc == 0
        called.assert_called_once()


# ---------------------------------------------------------------------------
# Single-shot mode preservation — generate-screen surface.
# ---------------------------------------------------------------------------


class TestSingleShotMode:

    def test_single_shot_produces_image_and_sidecar(self, tmp_path, monkeypatch):
        os.chdir(tmp_path)

        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"PNG")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 5,
                "usage": {"total_tokens": 42}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        args = _make_args(
            prompt="A friendly robot",
            style="Head First style",
            aspect_ratio="16:9",
            output_dir=str(tmp_path / "images" / "hero"),
            asset_name="hero",
            count=1,
        )
        rc = gi.run_single_shot(args)
        assert rc == 0
        png = tmp_path / "images" / "hero" / "hero-01.png"
        meta_path = tmp_path / "images" / "hero" / "hero-01.json"
        assert png.exists()
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text())
        assert meta["provider"] == "gemini"
        assert "Head First style" in meta["assembled_prompt"]
        assert meta["aspect_ratio"] == "16:9"

    def test_single_shot_count_generates_multiple(self, tmp_path, monkeypatch):
        def fake(prompt, output_path, api_key, config, **kwargs):
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(b"x")
            return {
                "provider": "gemini", "model": gi.GEMINI_PRO_MODEL,
                "output_file": output_path.name, "generation_time_ms": 1,
                "usage": {}, "fallback_used": False,
            }
        monkeypatch.setattr(gi, "generate_image", fake)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        args = _make_args(
            prompt="x",
            output_dir=str(tmp_path / "out"),
            asset_name="img",
            count=3,
        )
        gi.run_single_shot(args)
        assert (tmp_path / "out" / "img-01.png").exists()
        assert (tmp_path / "out" / "img-02.png").exists()
        assert (tmp_path / "out" / "img-03.png").exists()

    def test_single_shot_requires_prompt_or_reference(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        args = _make_args(prompt=None, reference_image=None)
        rc = gi.run_single_shot(args)
        assert rc == 2


# ---------------------------------------------------------------------------
# CLI entry — argument parsing surface.
# ---------------------------------------------------------------------------


class TestCLI:

    def test_parser_accepts_plan_flag(self):
        p = gi.build_parser()
        args = p.parse_args(["--plan", "x.md"])
        assert args.plan == "x.md"

    def test_parser_accepts_single_shot_flags(self):
        p = gi.build_parser()
        args = p.parse_args([
            "--prompt", "robot", "--style", "head first",
            "--aspect-ratio", "16:9", "--quality", "high",
            "--output-dir", "out", "--asset-name", "hero",
        ])
        assert args.prompt == "robot"
        assert args.style == "head first"
        assert args.aspect_ratio == "16:9"
        assert args.quality == "high"
        assert args.output_dir == "out"
        assert args.asset_name == "hero"

    def test_parser_default_quality_is_high(self):
        p = gi.build_parser()
        args = p.parse_args(["--prompt", "x"])
        assert args.quality == "high"

    def test_parser_rejects_invalid_quality(self):
        p = gi.build_parser()
        with pytest.raises(SystemExit):
            p.parse_args(["--prompt", "x", "--quality", "ultra"])

    def test_main_with_no_args_prints_help(self, capsys):
        rc = gi.main([])
        assert rc == 2
