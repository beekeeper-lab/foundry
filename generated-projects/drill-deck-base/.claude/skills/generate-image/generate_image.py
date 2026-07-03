#!/usr/bin/env python3
"""Generate images via Gemini or OpenAI from a plan or a single prompt.

Two modes of operation, sharing one provider-dispatch and rate-limiter
code path:

    --plan path/to/IMAGE-PLAN.md  [--filter sub] [--force] [--dry-run]
        Plan-driven batch mode. Walks an ``IMAGE-PLAN.md`` file (bold-key
        frontmatter + ``### Image N: <slug>`` entries), generates only
        the missing images, writes a JSON sidecar next to each PNG, and
        prints an end-of-run summary with provider, count, and an
        estimated cost computed from the in-script cost table.

    --prompt "..."  [--quality high] [--output-dir ...] [--asset-name ...]
        Single-shot mode preserved for ``generate-screen`` and ad-hoc
        callers. Generates exactly one image (or ``--count N``) from
        flags only — no plan, no frontmatter.

Provider routing is locked per project in plan frontmatter:

    **Generator:** gemini-3-pro-image-preview        (default)
    **Generator:** openai-gpt-image-2                (newer, requires org verification)
    **Generator:** openai-gpt-image-1.5              (no verification needed)

Containment dispatch — any value containing ``openai`` or ``gpt-image``
(case-insensitive) routes to OpenAI; the model name is extracted with
``gpt-image-[\\d.]+``. Anything else routes to Gemini.

Quality (unified flag, default ``high``):

    | --quality | OpenAI gpt-image-2 / 1.5 | Gemini             |
    | low       | low                       | nanobanana2        |
    | medium    | medium                    | nanobanana2        |
    | high      | high                      | nanobanana-pro     |

Acknowledgements
----------------

The plan parser, frontmatter regex set, dispatch logic, and Gemini
rate-limiter constant in this script are adapted from
``Course_Material/Git_Fundamentals/scripts/generate_images.py`` (the
canonical Stonewaters implementation, ~495 lines, production-tested
across an 18-course portfolio). That script is the load-bearing
reference for ``MIN_INTERVAL_SECONDS = 60.0/18``, the 429
retry-with-``retryDelay`` pattern, and the bold-key frontmatter shape.

Cost-table source-of-truth lives in this file (``_COST_TABLE`` below).
When provider prices change, update the constants here, not in the
ADR or docs that link to it.

Usage examples
--------------

    # Plan-driven
    uv run --with google-genai --with openai \\
        .claude/shared/skills/generate-image/generate_image.py \\
        --plan IMAGE-PLAN.md --dry-run
    uv run --with google-genai --with openai \\
        .claude/shared/skills/generate-image/generate_image.py \\
        --plan IMAGE-PLAN.md --filter module-04

    # Single-shot (used by generate-screen)
    uv run --with google-genai --with pillow \\
        .claude/shared/skills/generate-image/generate_image.py \\
        --prompt "Hero illustration of a friendly robot" \\
        --quality high --aspect-ratio 16:9 \\
        --output-dir images/hero --asset-name hero

Environment
-----------

``GEMINI_API_KEY`` is required for Gemini routing.
``OPENAI_API_KEY`` is required for OpenAI routing.
Either may live in the process environment or in the nearest ``.env``
on the cwd → parents → ``$HOME`` walk (see ``_media_lib.env.load_env``).
The process environment always wins.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
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
except ImportError:  # pragma: no cover - exercised only when symlinks broken
    def load_env(start: Path | None = None) -> dict[str, str]:  # type: ignore[misc]
        return {}


# ---------------------------------------------------------------------------
# Constants — provider names, model defaults, rate limits, quality mapping.
# ---------------------------------------------------------------------------

# Default Gemini model (Nanobanana Pro). This is the high-quality slot.
GEMINI_PRO_MODEL = "gemini-3-pro-image-preview"
# Faster, cheaper Gemini slot used for low/medium quality.
GEMINI_FLASH_MODEL = "gemini-3.1-flash-image-preview"

# OpenAI defaults — gpt-image-2 is preferred but requires org verification;
# falls back to 1.5 automatically (see ``_OPENAI_FALLBACK_MODEL``).
DEFAULT_OPENAI_MODEL = "gpt-image-2"
_OPENAI_FALLBACK_MODEL = "gpt-image-1.5"

# Rate limiter — Gemini's per-minute ceiling is 20; target ~18/min for
# headroom. Carried verbatim from the Stonewaters reference; do NOT make
# this configurable — it is a property of the Gemini quota, not a tunable.
MIN_INTERVAL_SECONDS = 60.0 / 18
MAX_RETRIES_ON_429 = 3

# Friendly-name → real Gemini model id used in plan-driven mode.
GEMINI_FRIENDLY_TO_MODEL = {
    "nanobanana-pro": GEMINI_PRO_MODEL,
    "nanobanana2": GEMINI_FLASH_MODEL,
}

# Unified --quality flag → provider arg mapping. Per ADR-010 commitment 4.
# OpenAI passes the quality token verbatim. Gemini uses the friendly model name
# (resolved to a real model id via GEMINI_FRIENDLY_TO_MODEL).
_QUALITY_TO_OPENAI = {"low": "low", "medium": "medium", "high": "high"}
_QUALITY_TO_GEMINI = {
    "low": "nanobanana2",
    "medium": "nanobanana2",
    "high": "nanobanana-pro",
}

VALID_QUALITIES = ("low", "medium", "high")
DEFAULT_QUALITY = "high"
DEFAULT_OPENAI_SIZE = "1536x1024"


# ---------------------------------------------------------------------------
# Cost table (USD per image). Source-of-truth lives here per ADR-010.
# Numbers cross-checked against AGENTIC-MEDIA-SKILLS.md "Cost rates" section
# in the Stonewaters Course_Material reference. When provider prices change,
# update these constants, not the ADR or skill docs.
# ---------------------------------------------------------------------------

_COST_TABLE: dict[tuple[str, str, str], float] = {
    # gpt-image-1.5
    ("gpt-image-1.5", "low", "1024x1024"): 0.011,
    ("gpt-image-1.5", "medium", "1024x1024"): 0.042,
    ("gpt-image-1.5", "high", "1024x1024"): 0.167,
    ("gpt-image-1.5", "low", "1536x1024"): 0.011,
    ("gpt-image-1.5", "medium", "1536x1024"): 0.042,
    ("gpt-image-1.5", "high", "1536x1024"): 0.133,
    ("gpt-image-1.5", "low", "1024x1536"): 0.011,
    ("gpt-image-1.5", "medium", "1024x1536"): 0.042,
    ("gpt-image-1.5", "high", "1024x1536"): 0.133,
    # gpt-image-2
    ("gpt-image-2", "low", "1024x1024"): 0.006,
    ("gpt-image-2", "medium", "1024x1024"): 0.053,
    ("gpt-image-2", "high", "1024x1024"): 0.211,
    ("gpt-image-2", "low", "1536x1024"): 0.005,
    ("gpt-image-2", "medium", "1536x1024"): 0.041,
    ("gpt-image-2", "high", "1536x1024"): 0.165,
    ("gpt-image-2", "low", "1024x1536"): 0.005,
    ("gpt-image-2", "medium", "1024x1536"): 0.041,
    ("gpt-image-2", "high", "1024x1536"): 0.165,
}

# Gemini doesn't price per-image; it prices per-token. Use the rate from
# AGENTIC-MEDIA-SKILLS.md ($0.00007/token, computed empirically from batch
# experience). End-of-run summary multiplies total tokens by this rate.
_GEMINI_USD_PER_TOKEN = 0.00007


# ---------------------------------------------------------------------------
# Frontmatter + plan parsing — adapted from
# Course_Material/Git_Fundamentals/scripts/generate_images.py.
# ---------------------------------------------------------------------------


_FRONTMATTER_KEYS = {
    "style": r"^\*\*Style:\*\*\s*(.+)$",
    "branding": r"^\*\*Branding:\*\*\s*(.+)$",
    "aspect_ratio": r"^\*\*Aspect ratio:\*\*\s*(.+)$",
    "background": r"^\*\*Background:\*\*\s*(.+)$",
    "text_in_image": r"^\*\*Text in image:\*\*\s*(.+)$",
    "avoid": r"^\*\*Avoid:\*\*\s*(.+)$",
    "philosophy": r"^\*\*Philosophy:\*\*\s*(.+)$",
    "generator": r"^\*\*Generator:\*\*\s*(.+)$",
    "quality": r"^\*\*Quality:\*\*\s*(.+)$",
    "size": r"^\*\*Size:\*\*\s*(.+)$",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    """Extract plan-level defaults from top-of-file ``**Key:**`` lines.

    Only looks at the head of the file (everything before the first ``## ``
    heading), matching the Stonewaters reference parser.
    """
    defaults: dict[str, str] = {}
    head = text.split("\n## ", 1)[0]
    for key, pattern in _FRONTMATTER_KEYS.items():
        m = re.search(pattern, head, re.MULTILINE)
        if m:
            defaults[key] = m.group(1).strip()
    return defaults


def parse_image_plan(plan_path: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Parse an ``IMAGE-PLAN.md`` file into ``(entries, defaults)``.

    Each entry has: ``short_name``, ``module_title``, ``file``, ``page``,
    ``description``, ``prompt_parts`` (possibly empty), and ``defaults``
    (a back-reference to the plan-level frontmatter).
    """
    text = plan_path.read_text()
    defaults = parse_frontmatter(text)

    entries: list[dict[str, Any]] = []
    current_module = ""
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]

        if re.match(r"^##\s+(?:Module|Week)\s+.+", line):
            current_module = line.lstrip("#").strip()

        img_match = re.match(r"^###\s+Image\s+\d+:\s*(.+)", line)
        if img_match:
            entry: dict[str, Any] = {
                "short_name": img_match.group(1).strip(),
                "module_title": current_module,
                "file": "",
                "page": "",
                "description": "",
                "prompt_parts": {},
                "defaults": defaults,
            }

            j = i + 1
            in_prompt = False
            prompt_lines: list[str] = []
            while j < len(lines):
                ll = lines[j]
                if re.match(r"^###\s+Image\s+\d+:", ll) or re.match(r"^##\s+", ll):
                    break

                if in_prompt:
                    if (
                        re.match(r"^- \*\*", ll)
                        or re.match(r"^###\s+", ll)
                        or re.match(r"^##\s+", ll)
                        or ll.strip() == "---"
                    ):
                        in_prompt = False
                    else:
                        prompt_lines.append(ll.strip())
                        j += 1
                        continue

                file_match = re.match(r"- \*\*File\*\*:\s*`?(.+?)`?$", ll)
                if file_match:
                    entry["file"] = file_match.group(1).strip("`")

                page_match = re.match(r"- \*\*Page\*\*:\s*(.+)", ll)
                if page_match:
                    entry["page"] = page_match.group(1).strip()

                desc_match = re.match(r"- \*\*Description\*\*:\s*(.+)", ll)
                if desc_match:
                    entry["description"] = desc_match.group(1).strip()

                if ll.strip() == "- **Prompt**:":
                    in_prompt = True

                j += 1

            prompt_text = "\n".join(prompt_lines)
            for key in [
                "Goal",
                "Scene",
                "Style",
                "Aspect ratio",
                "Background",
                "Text in image",
                "Avoid",
            ]:
                m = re.search(
                    rf"{key}:\s*(.+?)(?:\n\s*"
                    r"(?:Goal|Scene|Style|Aspect ratio|Background|Text in image|Avoid):|$)",
                    prompt_text,
                    re.DOTALL,
                )
                if m:
                    entry["prompt_parts"][key.lower().replace(" ", "_")] = m.group(1).strip()

            if entry["file"]:
                entries.append(entry)

        i += 1

    return entries, defaults


def assemble_prompt_from_entry(entry: dict[str, Any]) -> str:
    """Build a prompt from a plan entry — structured Prompt block wins,
    otherwise concatenate Description with frontmatter defaults.
    """
    parts = entry["prompt_parts"]
    defaults = entry["defaults"]

    if parts:
        sections: list[str] = []
        labels = {
            "goal": "Goal",
            "scene": "Scene",
            "style": "Style",
            "aspect_ratio": "Aspect ratio",
            "background": "Background",
            "text_in_image": "Text in image",
            "avoid": "Avoid",
        }
        for key, label in labels.items():
            if key in parts:
                sections.append(f"{label}: {parts[key]}")
        return "\n".join(sections)

    if not entry["description"]:
        return ""

    sections = [f"Scene: {entry['description']}"]
    if "style" in defaults:
        sections.append(f"Style: {defaults['style']}")
    if "branding" in defaults:
        sections.append(f"Branding: {defaults['branding']}")
    if "aspect_ratio" in defaults:
        sections.append(f"Aspect ratio: {defaults['aspect_ratio']}")
    if "background" in defaults:
        sections.append(f"Background: {defaults['background']}")
    if "text_in_image" in defaults:
        sections.append(f"Text in image: {defaults['text_in_image']}")
    if "avoid" in defaults:
        sections.append(f"Avoid: {defaults['avoid']}")
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Provider dispatch — see ADR-010 commitment 2.
# ---------------------------------------------------------------------------


def resolve_provider(
    defaults: dict[str, str],
    *,
    cli_quality: str | None = None,
    cli_override: str | None = None,
) -> dict[str, Any]:
    """Return a resolved provider config dict.

    Returns one of::

        {"provider": "gemini",  "model": "<id>", "quality": "<low|medium|high>",
         "friendly": "<nanobanana-pro|nanobanana2>"}
        {"provider": "openai",  "model": "<gpt-image-X>", "quality": "...",
         "size": "..."}

    ``cli_override`` is treated like a frontmatter ``Generator:`` value;
    when present it overrides any frontmatter line. ``cli_quality``
    defaults the quality when frontmatter ``Quality:`` is absent.
    """
    raw = (cli_override or defaults.get("generator") or "").lower().strip()

    # Resolve unified quality. Plan frontmatter wins over CLI default.
    fm_quality = (defaults.get("quality") or "").lower().strip()
    quality = fm_quality if fm_quality in VALID_QUALITIES else (cli_quality or DEFAULT_QUALITY)
    if quality not in VALID_QUALITIES:
        quality = DEFAULT_QUALITY

    # Tolerant containment dispatch: openai OR gpt-image → OpenAI.
    if "openai" in raw or "gpt-image" in raw:
        m = re.search(r"gpt-image-[\d.]+", raw)
        model = m.group(0) if m else DEFAULT_OPENAI_MODEL
        size = (defaults.get("size") or DEFAULT_OPENAI_SIZE).strip()
        return {
            "provider": "openai",
            "model": model,
            "quality": _QUALITY_TO_OPENAI[quality],
            "size": size,
        }

    # Default → Gemini.
    friendly = _QUALITY_TO_GEMINI[quality]
    return {
        "provider": "gemini",
        "model": GEMINI_FRIENDLY_TO_MODEL[friendly],
        "friendly": friendly,
        "quality": quality,
    }


# ---------------------------------------------------------------------------
# Helpers — retry-delay extraction, OpenAI error classification.
# ---------------------------------------------------------------------------


def _extract_retry_delay(err_str: str) -> int:
    """Pull ``retryDelay`` seconds out of a 429 error message; +2 for jitter.

    Matches both ``retryDelay: '30s'`` (Gemini error body) and bare
    integers; falls back to 30 when nothing is found.
    """
    m = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", err_str)
    if m:
        return int(m.group(1)) + 2
    # OpenAI 429 may include a bare ``Please retry after N seconds`` form.
    m = re.search(r"retry[- ]after[:\s]+(\d+)", err_str, re.IGNORECASE)
    if m:
        return int(m.group(1)) + 2
    return 30


def _is_openai_org_verification_error(err: Exception) -> bool:
    """True when the OpenAI error indicates the org needs to be verified
    before ``gpt-image-2`` is callable. Containment check on common phrases.
    """
    msg = str(err).lower()
    needles = (
        "must be verified",
        "organization must be verified",
        "verify your organization",
        "org verification",
        "organization verification",
    )
    return any(n in msg for n in needles)


def _is_openai_billing_hard_limit(err: Exception) -> bool:
    """True when the error is the OpenAI ``billing hard limit`` — never retry."""
    msg = str(err).lower()
    return "billing hard limit" in msg or "billing_hard_limit" in msg


# ---------------------------------------------------------------------------
# Provider implementations.
# ---------------------------------------------------------------------------


def _generate_gemini(prompt: str, output_path: Path, api_key: str,
                     config: dict[str, Any],
                     reference_paths: list[Path] | None = None,
                     aspect_ratio: str | None = None) -> dict[str, Any]:
    """Call Gemini, write PNG, return metadata dict (without timestamp).

    Retries up to ``MAX_RETRIES_ON_429`` times on 429 errors, honoring
    ``retryDelay`` from the error body when present.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    contents: list[Any] = []
    for ref in reference_paths or []:
        mime = "image/png" if ref.suffix.lower() == ".png" else "image/jpeg"
        contents.append(types.Part.from_bytes(data=ref.read_bytes(), mime_type=mime))
    contents.append(prompt)

    config_kwargs: dict[str, Any] = {"response_modalities": ["IMAGE", "TEXT"]}
    if aspect_ratio:
        config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)
    gen_config = types.GenerateContentConfig(**config_kwargs)

    start = time.time()
    response = None
    for attempt in range(MAX_RETRIES_ON_429 + 1):
        try:
            response = client.models.generate_content(
                model=config["model"],
                contents=contents,
                config=gen_config,
            )
            break
        except Exception as e:
            err = str(e)
            if "429" in err and attempt < MAX_RETRIES_ON_429:
                wait_s = _extract_retry_delay(err)
                print(f" (429, retry in {wait_s}s)", end="", flush=True)
                time.sleep(wait_s)
                continue
            raise

    elapsed_ms = int((time.time() - start) * 1000)

    if response is None or not getattr(response, "candidates", None):
        raise ValueError("No image in response")

    image_data = None
    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) and part.inline_data.mime_type.startswith("image/"):
            image_data = part.inline_data.data
            break
    if image_data is None:
        raise ValueError("No image data found in response parts")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(image_data, str):
        image_data = base64.b64decode(image_data)
    output_path.write_bytes(image_data)

    usage: dict[str, int] = {}
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        um = response.usage_metadata
        usage = {
            "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
            "candidates_tokens": getattr(um, "candidates_token_count", 0) or 0,
            "total_tokens": getattr(um, "total_token_count", 0) or 0,
        }

    return {
        "provider": "gemini",
        "model": config["model"],
        "output_file": output_path.name,
        "generation_time_ms": elapsed_ms,
        "usage": usage,
        "fallback_used": False,
    }


def _openai_call(client: Any, model: str, prompt: str, size: str, quality: str) -> Any:
    """Single OpenAI Images API call. Extracted for easy mocking."""
    return client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )


def _generate_openai(prompt: str, output_path: Path, api_key: str,
                     config: dict[str, Any]) -> dict[str, Any]:
    """Call OpenAI, write PNG, return metadata dict (without timestamp).

    Behavior:
    - Retries up to ``MAX_RETRIES_ON_429`` times on 429 errors.
    - On the org-verification error for ``gpt-image-2``, prints a one-line
      warning to stderr, retries the request against ``gpt-image-1.5``,
      and records ``fallback_used: true`` in the returned dict.
    - On the ``billing hard limit`` error, fails fast (no retry).
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = config["model"]
    size = config.get("size", DEFAULT_OPENAI_SIZE)
    quality = config.get("quality", DEFAULT_QUALITY)
    fallback_used = False

    start = time.time()
    resp = None
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES_ON_429 + 1):
        try:
            resp = _openai_call(client, model, prompt, size, quality)
            break
        except Exception as e:
            last_err = e
            err_str = str(e)
            # Hard limit → fail fast, do not retry.
            if _is_openai_billing_hard_limit(e):
                raise
            # gpt-image-2 verification error → fall back exactly once.
            if model == DEFAULT_OPENAI_MODEL and _is_openai_org_verification_error(e):
                print(
                    f"WARNING: {DEFAULT_OPENAI_MODEL} requires OpenAI org "
                    f"verification; falling back to {_OPENAI_FALLBACK_MODEL} for "
                    "this run. Verify your org at platform.openai.com to use "
                    f"{DEFAULT_OPENAI_MODEL}.",
                    file=sys.stderr,
                )
                model = _OPENAI_FALLBACK_MODEL
                fallback_used = True
                continue  # retry with fallback within same attempt budget
            # 429 → backoff and retry within budget.
            is_429 = "429" in err_str or "rate limit" in err_str.lower()
            if is_429 and attempt < MAX_RETRIES_ON_429:
                wait_s = _extract_retry_delay(err_str)
                print(f" (429, retry in {wait_s}s)", end="", flush=True)
                time.sleep(wait_s)
                continue
            raise

    if resp is None:
        raise RuntimeError(f"OpenAI request returned no response: {last_err}")

    elapsed_ms = int((time.time() - start) * 1000)
    img_b64 = resp.data[0].b64_json
    img_bytes = base64.b64decode(img_b64)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(img_bytes)

    return {
        "provider": "openai",
        "model": model,
        "quality": quality,
        "size": size,
        "output_file": output_path.name,
        "generation_time_ms": elapsed_ms,
        "fallback_used": fallback_used,
    }


def generate_image(prompt: str, output_path: Path, api_key: str,
                   config: dict[str, Any],
                   *,
                   reference_paths: list[Path] | None = None,
                   aspect_ratio: str | None = None) -> dict[str, Any]:
    """Top-level provider dispatch."""
    if config["provider"] == "openai":
        return _generate_openai(prompt, output_path, api_key, config)
    return _generate_gemini(
        prompt,
        output_path,
        api_key,
        config,
        reference_paths=reference_paths,
        aspect_ratio=aspect_ratio,
    )


# ---------------------------------------------------------------------------
# Sidecar JSON.
# ---------------------------------------------------------------------------


def build_sidecar(
    *,
    meta: dict[str, Any],
    assembled_prompt: str,
    defaults: dict[str, str] | None = None,
    aspect_ratio: str | None = None,
    background: str | None = None,
    text_in_image: str | None = None,
    negative_constraints: list[str] | None = None,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose the sidecar dict for a successful generation.

    Required fields (per ADR-010 commitment 6):
      - timestamp (ISO 8601 UTC)
      - provider, model
      - quality, size (OpenAI only — included from ``meta`` when present)
      - assembled_prompt (the prompt as actually sent)
      - output_file (basename)
      - generation_time_ms
      - usage (Gemini only — included from ``meta`` when present)
      - fallback_used
      - negative_constraints
      - aspect_ratio
      - background
      - text_in_image
    """
    defaults = defaults or {}

    sidecar: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": meta["provider"],
        "model": meta["model"],
        "assembled_prompt": assembled_prompt,
        "output_file": meta["output_file"],
        "generation_time_ms": meta["generation_time_ms"],
        "fallback_used": meta.get("fallback_used", False),
    }

    # OpenAI-specific fields when the provider call returned them.
    for key in ("quality", "size"):
        if key in meta:
            sidecar[key] = meta[key]

    # Gemini-specific token usage when present.
    if "usage" in meta:
        sidecar["usage"] = meta["usage"]

    # Plan / single-shot trim — pull the sidecar's user-facing fields out of
    # explicit args first, falling back to the plan defaults map.
    sidecar["aspect_ratio"] = aspect_ratio or defaults.get("aspect_ratio") or ""
    sidecar["background"] = background or defaults.get("background") or ""
    sidecar["text_in_image"] = text_in_image or defaults.get("text_in_image") or ""

    if negative_constraints is None:
        avoid = defaults.get("avoid", "")
        if avoid:
            negative_constraints = [s.strip() for s in avoid.split(",") if s.strip()]
        else:
            negative_constraints = []
    sidecar["negative_constraints"] = negative_constraints

    if extras:
        sidecar.update(extras)

    return sidecar


def write_sidecar(path: Path, sidecar: dict[str, Any]) -> None:
    path.write_text(json.dumps(sidecar, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Cost estimation + end-of-run summary.
# ---------------------------------------------------------------------------


def estimate_cost(provider: str, model: str, quality: str, size: str,
                  total_tokens: int = 0) -> float:
    """Estimate per-image USD cost. Gemini → tokens × per-token rate; OpenAI →
    look up (model, quality, size) in ``_COST_TABLE``.
    """
    if provider == "gemini":
        return total_tokens * _GEMINI_USD_PER_TOKEN
    return _COST_TABLE.get((model, quality, size), 0.0)


def format_run_summary(*, provider: str, model: str, generated: int,
                       skipped: int, errors: int,
                       total_cost_usd: float, total_tokens: int = 0,
                       quality: str | None = None,
                       size: str | None = None) -> str:
    """One-block summary string, multi-line. Contains provider, count, cost."""
    lines = [
        "=" * 60,
        f"Generated: {generated}, Skipped: {skipped}, Errors: {errors}",
    ]
    if generated > 0:
        details = f"Provider: {provider} · model: {model}"
        if provider == "openai":
            details += f" · quality: {quality} · size: {size}"
        lines.append(details)
        if provider == "gemini" and total_tokens:
            lines.append(f"Total tokens: {total_tokens:,}")
        lines.append(f"Estimated cost: ${total_cost_usd:.2f}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# API key lookup — driven by load_env, then env var, then explicit failure.
# ---------------------------------------------------------------------------


def load_api_key(provider: str) -> str:
    """Resolve the per-provider API key from os.environ.

    Caller is expected to have already invoked ``load_env(...)`` once at
    program startup; this just reads ``os.environ``. If the key is missing,
    raise a clear error.
    """
    env_key = "OPENAI_API_KEY" if provider == "openai" else "GEMINI_API_KEY"
    val = os.environ.get(env_key)
    if not val:
        raise SystemExit(
            f"ERROR: {env_key} not found in environment or any .env file "
            "(walked cwd → parents → $HOME)."
        )
    return val.strip()


# ---------------------------------------------------------------------------
# Plan-driven main loop.
# ---------------------------------------------------------------------------


def _resolve_plan_output_path(plan_path: Path, file_field: str) -> Path:
    """Resolve a plan entry's ``**File**`` value against the plan's directory.

    Plan files use paths relative to the plan's containing directory
    (the course root). Absolute paths are honored as-is.
    """
    raw = file_field.strip()
    p = Path(raw)
    if p.is_absolute():
        return p
    return plan_path.parent / p


def run_plan(args: argparse.Namespace) -> int:
    """Plan-driven generation loop. Returns process exit code."""
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"ERROR: plan file not found: {plan_path}", file=sys.stderr)
        return 2

    entries, defaults = parse_image_plan(plan_path)

    if args.filter:
        entries = [e for e in entries if args.filter in e["file"]]

    config = resolve_provider(
        defaults,
        cli_quality=args.quality,
        cli_override=args.generator,
    )

    # Header
    if config["provider"] == "openai":
        print(
            f"Image Generator — {len(entries)} planned · "
            f"provider: openai · model: {config['model']} · "
            f"quality: {config['quality']} · size: {config['size']}"
        )
    else:
        print(
            f"Image Generator — {len(entries)} planned · "
            f"provider: gemini · model: {config['model']} "
            f"({config.get('friendly', '')})"
        )
    print("=" * 60)

    # Lazily load API key only when we actually need to call the API.
    api_key: str | None = None
    last_call_time = 0.0
    generated = 0
    skipped = 0
    errors = 0
    total_tokens = 0
    total_cost = 0.0

    for idx, entry in enumerate(entries):
        file_path = _resolve_plan_output_path(plan_path, entry["file"])
        short = f"[{idx + 1}/{len(entries)}] {entry['short_name']}"

        if file_path.exists() and not args.force:
            print(f"  {short} — exists, skipping")
            skipped += 1
            continue

        prompt = assemble_prompt_from_entry(entry)
        if not prompt:
            print(f"  {short} — no prompt (no Description and no Prompt block), skipping")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  {short} — WOULD GENERATE → {entry['file']}")
            continue

        # Rate-limit Gemini (~18 req/min). OpenAI's 429 retry is in-call.
        if config["provider"] == "gemini":
            elapsed = time.time() - last_call_time
            if last_call_time and elapsed < MIN_INTERVAL_SECONDS:
                time.sleep(MIN_INTERVAL_SECONDS - elapsed)

        if api_key is None:
            api_key = load_api_key(config["provider"])

        print(f"  {short} — generating...", end="", flush=True)
        last_call_time = time.time()

        try:
            meta = generate_image(prompt, file_path, api_key, config)
            sidecar = build_sidecar(
                meta=meta,
                assembled_prompt=prompt,
                defaults=defaults,
            )
            write_sidecar(file_path.with_suffix(".json"), sidecar)

            tokens = meta.get("usage", {}).get("total_tokens", 0)
            total_tokens += tokens
            total_cost += estimate_cost(
                provider=meta["provider"],
                model=meta["model"],
                quality=meta.get("quality", config.get("quality", DEFAULT_QUALITY)),
                size=meta.get("size", config.get("size", DEFAULT_OPENAI_SIZE)),
                total_tokens=tokens,
            )
            generated += 1

            size_kb = file_path.stat().st_size / 1024 if file_path.exists() else 0
            print(f" OK {size_kb:.0f} KB, {meta['generation_time_ms'] / 1000:.1f}s")
        except SystemExit:
            raise
        except Exception as e:
            errors += 1
            print(f" ERROR: {e}")

    if args.dry_run:
        # Walk the plan but no API calls; no cost summary line, just counts.
        print("=" * 60)
        print(f"Dry run — would generate {len(entries) - skipped}, skip {skipped}")
        return 0

    print(
        format_run_summary(
            provider=config["provider"],
            model=config["model"],
            generated=generated,
            skipped=skipped,
            errors=errors,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            quality=config.get("quality"),
            size=config.get("size"),
        )
    )
    return 0 if errors == 0 else 1


# ---------------------------------------------------------------------------
# Single-shot mode (preserved for generate-screen).
# ---------------------------------------------------------------------------


def assemble_prompt_from_args(args: argparse.Namespace) -> str:
    """Build a single-shot prompt from individual flags."""
    parts: list[str] = []
    if args.goal:
        parts.append(f"Create a {args.goal}.")
    if args.prompt:
        parts.append(args.prompt)
    if args.style:
        parts.append(f"Style: {args.style}.")
    if args.color_palette:
        parts.append(f"Use colors inspired by: {args.color_palette}.")
    if args.aspect_ratio:
        parts.append(f"Aspect ratio: {args.aspect_ratio}.")
    if args.background:
        parts.append(f"Background: {args.background}.")
    if args.text_in_image:
        parts.append(f"Text in image: {args.text_in_image}.")
    if args.negative:
        parts.append(f"Avoid: {', '.join(args.negative)}.")
    return " ".join(parts)


def run_single_shot(args: argparse.Namespace) -> int:
    """Single-shot generation. Returns process exit code."""
    if not args.prompt and not args.reference_image:
        print(
            "ERROR: --prompt is required when no --reference-image is provided.",
            file=sys.stderr,
        )
        return 2

    reference_paths: list[Path] = []
    for ref in args.reference_image or []:
        p = Path(ref)
        if not p.exists():
            print(f"ERROR: reference image not found: {ref}", file=sys.stderr)
            return 2
        reference_paths.append(p)

    # Provider config — single-shot uses CLI flags only (no frontmatter).
    config = resolve_provider(
        {},
        cli_quality=args.quality,
        cli_override=args.generator,
    )
    api_key = load_api_key(config["provider"])

    assembled = assemble_prompt_from_args(args)
    if not assembled.strip():
        assembled = "Generate an image based on the provided reference images."

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, str]] = []
    total_tokens = 0
    total_cost = 0.0
    errors = 0

    for i in range(args.count):
        idx = f"{i + 1:02d}"
        image_file = output_dir / f"{args.asset_name}-{idx}.png"
        meta_file = output_dir / f"{args.asset_name}-{idx}.json"

        try:
            meta = generate_image(
                assembled,
                image_file,
                api_key,
                config,
                reference_paths=reference_paths,
                aspect_ratio=args.aspect_ratio,
            )
        except Exception as e:
            errors += 1
            print(f"ERROR generating image {idx}: {e}", file=sys.stderr)
            continue

        sidecar = build_sidecar(
            meta=meta,
            assembled_prompt=assembled,
            aspect_ratio=args.aspect_ratio,
            background=args.background,
            text_in_image=args.text_in_image,
            negative_constraints=list(args.negative) if args.negative else None,
            extras={"prompt": args.prompt} if args.prompt else None,
        )
        write_sidecar(meta_file, sidecar)

        tokens = meta.get("usage", {}).get("total_tokens", 0) or 0
        total_tokens += tokens
        total_cost += estimate_cost(
            provider=meta["provider"],
            model=meta["model"],
            quality=meta.get("quality", config.get("quality", DEFAULT_QUALITY)),
            size=meta.get("size", config.get("size", DEFAULT_OPENAI_SIZE)),
            total_tokens=tokens,
        )

        results.append({
            "image_path": str(image_file),
            "metadata_path": str(meta_file),
        })

    output = {
        "success": errors == 0,
        "provider": config["provider"],
        "model": config["model"],
        "fallback_used": any(
            json.loads(Path(r["metadata_path"]).read_text()).get("fallback_used", False)
            for r in results
        ),
        "images": results,
    }
    print(json.dumps(output, indent=2))

    # Always print the cost summary line on stderr too, so generate-screen
    # can ignore it but interactive callers see it.
    if results:
        print(
            format_run_summary(
                provider=config["provider"],
                model=config["model"],
                generated=len(results),
                skipped=0,
                errors=errors,
                total_cost_usd=total_cost,
                total_tokens=total_tokens,
                quality=config.get("quality"),
                size=config.get("size"),
            ),
            file=sys.stderr,
        )

    return 0 if errors == 0 else 1


# ---------------------------------------------------------------------------
# CLI plumbing.
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate images via Gemini or OpenAI (plan-driven or single-shot)",
    )
    # Mode selection — exactly one of --plan or --prompt (single-shot)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", type=str, default=None,
                      help="Path to IMAGE-PLAN.md (plan-driven mode)")
    mode.add_argument("--prompt", type=str, default=None,
                      help="Single-shot prompt (single-shot mode)")

    # Plan-driven flags
    parser.add_argument("--filter", type=str, default=None,
                        help="Substring filter on plan entries' **File** path")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate plan entries that already exist on disk")
    parser.add_argument("--dry-run", action="store_true",
                        help="Walk the plan and print what would be generated; no API calls")

    # Provider override — applies to both modes
    parser.add_argument("--generator", type=str, default=None,
                        help="Override Generator: frontmatter (e.g. openai-gpt-image-2)")

    # Unified quality flag — applies to both modes
    parser.add_argument("--quality", type=str, default=DEFAULT_QUALITY,
                        choices=list(VALID_QUALITIES),
                        help="Unified quality: low|medium|high (default: high)")

    # Single-shot flags (preserved for generate-screen + ad-hoc)
    parser.add_argument("--goal", type=str, default=None,
                        help="What the image is for (hero image, icon, etc.)")
    parser.add_argument("--style", type=str, default=None,
                        help="Artistic/design direction")
    parser.add_argument("--aspect-ratio", type=str, default=None,
                        help="Aspect ratio (e.g. 16:9, 1:1)")
    parser.add_argument("--background", type=str, default=None,
                        help="Background style (transparent, white, dark, ...)")
    parser.add_argument("--text-in-image", type=str, default=None,
                        choices=["none", "minimal", "allowed", "exact"],
                        help="Text rendering rules")
    parser.add_argument("--color-palette", type=str, default=None,
                        help="Comma-separated hex values")
    parser.add_argument("--negative", action="append", default=None,
                        help="Things to avoid (repeatable)")
    parser.add_argument("--reference-image", action="append", default=None,
                        help="Path to reference image (repeatable)")
    parser.add_argument("--output-dir", type=str, default="images/misc",
                        help="Output directory (default: images/misc)")
    parser.add_argument("--asset-name", type=str, default="image",
                        help="Base filename (default: image)")
    parser.add_argument("--count", type=int, default=1,
                        help="Number of images to generate (default: 1)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load .env on the cwd → parents → $HOME walk. Existing process env wins.
    load_env()

    if args.plan:
        return run_plan(args)
    if args.prompt or args.reference_image:
        return run_single_shot(args)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
