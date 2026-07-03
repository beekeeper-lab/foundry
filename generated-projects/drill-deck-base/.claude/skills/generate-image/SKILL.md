# Skill: Generate Image

## Description

Generates image assets from text descriptions, with two modes:

- **Plan-driven** (`--plan IMAGE-PLAN.md`): batch-generate dozens or hundreds of images from a reviewed markdown plan. Skip-on-disk is the loop body — re-running adds only the missing images. End-of-run prints provider, count, and estimated cost.
- **Single-shot** (`--prompt "..."`): generate one image (or `--count N`) from CLI flags only. Used by `generate-screen` and ad-hoc callers.

Routes between Google Gemini (Nanobanana family) and OpenAI (gpt-image family) per the plan's frontmatter, with a unified `--quality low|medium|high` knob across both providers. Records an auditable JSON sidecar next to every PNG.

## Trigger

Use this skill when the user asks to:

- Generate an image, icon, hero image, splash screen, or any visual asset.
- Generate every image planned for a project from an `IMAGE-PLAN.md`.
- Re-run image generation to fill in newly added entries.
- Create concept art, illustrations, or infographics.

Also used programmatically by `generate-screen` (which invokes the single-shot path).

## Choosing a mode

| You have... | Use... |
|---|---|
| A reviewed `IMAGE-PLAN.md` with N image entries | `--plan path/to/IMAGE-PLAN.md` |
| One ad-hoc prompt for a single asset | `--prompt "..."` |

The two modes share provider-dispatch and rate-limiter code. They differ only in input shape (a plan vs. a single prompt) and looping (many vs. one).

---

## Plan-driven mode

### IMAGE-PLAN.md format

The plan starts with frontmatter expressed as bold-key markdown, followed by sections for each module, each containing numbered image entries.

```markdown
# Image Plan — Example Project

**Style:** Friendly cartoon, Head First textbook style — clean lines, warm colors with purple accents.
**Branding:** purple/violet accents
**Aspect ratio:** 16:9
**Background:** white
**Text in image:** minimal
**Avoid:** photorealistic, dark, scary, cluttered
**Philosophy:** consistency across modules
**Generator:** gemini-3-pro-image-preview
**Quality:** high
**Size:** 1536x1024

## Module 00: Basics

### Image 1: m00-hero
- **File**: `images/module-00/m00-hero.png`
- **Page**: title card / hero
- **Description**: A friendly cartoon developer waving at the reader.

### Image 2: m00-pipeline
- **File**: `images/module-00/m00-pipeline.png`
- **Description**: ignored when a structured Prompt block is present
- **Prompt**:
    Goal: editorial illustration for a programming book
    Scene: data flowing through pipes from left to right
    Style: Head First book illustration style, clean lines
    Aspect ratio: 16:9
    Background: white
    Text in image: minimal
    Avoid: photorealism, dark, scary
```

### Recognized frontmatter keys

| Key | Purpose |
|---|---|
| `Style:` | Stylistic direction; appended to every prompt as a default |
| `Branding:` | Optional brand palette / logo notes |
| `Aspect ratio:` | Default aspect ratio (e.g. `16:9`) |
| `Background:` | Default background (e.g. `white`) |
| `Text in image:` | Default text policy (e.g. `minimal`) |
| `Avoid:` | Comma-separated negative constraints |
| `Philosophy:` | Optional broader stylistic note |
| `Generator:` | **Provider router** — see "Provider routing" below |
| `Quality:` | Unified `low` / `medium` / `high` (overrides CLI default) |
| `Size:` | OpenAI only — e.g. `1024x1024`, `1536x1024`, `1024x1536` |

### Per-image entry shape

Required:

- `### Image N: <slug>` — heading; `<slug>` is the filename stem.
- `- **File**: <path>` — relative to the plan's directory.
- `- **Description**: <prose>` — natural-language scene description.

Optional:

- `- **Page**: <where it appears>` — purely human-readable; the script ignores it.
- `- **Prompt**:` followed by an indented block with `Goal:`, `Scene:`, `Style:`, `Aspect ratio:`, `Background:`, `Text in image:`, `Avoid:` keys. **When present, the structured prompt overrides Description+frontmatter assembly.**

### Plan-driven flags

| Flag | Effect |
|---|---|
| `--plan PATH` | Required. Path to `IMAGE-PLAN.md`. |
| `--filter SUBSTR` | Restrict to entries whose `**File**` path contains the substring. |
| `--force` | Regenerate plan entries that already exist on disk. |
| `--dry-run` | Walk the plan and print what would be generated; **no API calls**. |
| `--quality low\|medium\|high` | Default `high`. Plan frontmatter `Quality:` overrides this. |
| `--generator VALUE` | Override frontmatter `Generator:` line for this run. |

Always `--dry-run` a fresh plan before spending money.

### Skip-on-disk

The loop is:

```
for entry in plan:
    if entry.file_path exists on disk and not --force:
        skip
    else:
        call provider API
        write PNG and sidecar JSON
```

Add Image 220 to the plan, re-run the script, it generates exactly that one image. Add a whole new module's worth of entries, re-run, it generates only the new ones. The plan + on-disk state is the contract.

---

## Single-shot mode

Used by `generate-screen` and any ad-hoc consumer. No frontmatter; provider/quality come from CLI flags.

```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py \
  --prompt "A friendly cartoon robot waving" \
  --style "Head First book illustration style" \
  --quality high \
  --aspect-ratio 16:9 \
  --output-dir images/hero \
  --asset-name hero
```

Optional flags (preserved from the previous skill):

- `--goal "hero image"` — what the image is for.
- `--style "clean premium SaaS"` — artistic direction.
- `--aspect-ratio 16:9` — for Gemini, passed via `image_config.aspect_ratio`.
- `--background dark` — `transparent`, `white`, `dark`, or freeform.
- `--text-in-image none|minimal|allowed|exact`.
- `--color-palette "#1F3A5F,#2D6A4F"`.
- `--negative "no clutter" --negative "no cartoon"` — repeatable.
- `--reference-image path/to/ref.png` — repeatable.
- `--output-dir images/foo` — default `images/misc`.
- `--asset-name hero` — default `image`.
- `--count 4` — number of images.

Single-shot prints a JSON document to stdout summarizing the generation; the cost line goes to stderr so it does not contaminate JSON consumers.

---

## Provider routing (both modes)

Tolerant containment dispatch:

- **Default** (`Generator:` line omitted entirely) → Gemini `gemini-3-pro-image-preview` (Nanobanana Pro).
- **Any value containing `openai` OR `gpt-image`** (case-insensitive) → OpenAI.
  - The OpenAI model is extracted with the regex `gpt-image-[\d.]+`.
  - When the value contains only the bare word `openai`, the script uses the OpenAI default (`gpt-image-2`).

All of these route to OpenAI and resolve to the model in the value:

```
openai-gpt-image-1.5
openai-gpt-image-2
gpt-image-1.5
gpt-image-2
OpenAI gpt-image-2
```

Anything else routes to Gemini.

### OpenAI default + fallback

The OpenAI default model is `gpt-image-2`. When the API returns the org-verification error (the dashboard requires verifying the org before `gpt-image-2` is callable), the script:

1. Prints a one-line warning to stderr (mentioning the verification requirement and the fallback that just happened).
2. Retries the same request against `gpt-image-1.5`.
3. Records `fallback_used: true` in the sidecar.

On the OpenAI `billing hard limit` error the script **fails fast** — no retry, no backoff. The hard limit is hard; the script's job is to surface the decision quickly so the user can raise the dashboard cap or wait for the next billing period.

### One-provider-per-project rule

Pick one provider for the life of a project and stick with it. Visible style drift between Gemini and OpenAI within a single project is the most visible quality bug in any portfolio-style output. The `Generator:` frontmatter line is the lock. When you change it, you are committing to regenerating every image (`--force`).

---

## Quality flag

`--quality low|medium|high` (default `high`). Plan frontmatter `Quality:` overrides the CLI default.

| `--quality` | OpenAI gpt-image-2 / 1.5 | Gemini |
|---|---|---|
| `low` | `low` | `nanobanana2` (`gemini-3.1-flash-image-preview`) |
| `medium` | `medium` | `nanobanana2` |
| `high` | `high` | `nanobanana-pro` (`gemini-3-pro-image-preview`) |

OpenAI's quality token passes through unchanged. Gemini's two model slots — the cheaper `nanobanana2` and the higher-fidelity `nanobanana-pro` — collapse `low` and `medium` onto `nanobanana2` and `high` onto `nanobanana-pro`.

---

## Sidecar JSON

After every successful generation, the script writes a JSON sidecar next to the PNG with the same stem (`<slug>.png` ↔ `<slug>.json`). Required fields:

```json
{
  "timestamp": "2026-04-29T20:14:33.123456+00:00",
  "provider": "gemini",
  "model": "gemini-3-pro-image-preview",
  "assembled_prompt": "Scene: ...\nStyle: ...\n...",
  "output_file": "m00-hero.png",
  "generation_time_ms": 23121,
  "fallback_used": false,
  "aspect_ratio": "16:9",
  "background": "white",
  "text_in_image": "minimal",
  "negative_constraints": ["photorealistic", "dark"],
  "usage": {
    "prompt_tokens": 141,
    "candidates_tokens": 1348,
    "total_tokens": 1715
  }
}
```

OpenAI generations also include:

```json
{
  "quality": "high",
  "size":    "1536x1024"
}
```

OpenAI's image API does not return token usage, so `usage` is omitted on OpenAI sidecars.

The `assembled_prompt` field is the prompt **as actually sent** — that is what reproduces the image. The plan's prose `Description` lives upstream and may have been edited since.

---

## Rate limiter & retry behavior

- **Gemini**: hard-paced at ~18 req/min via `MIN_INTERVAL_SECONDS = 60.0/18`. On 429, reads `retryDelay` from the error body and sleeps that long; up to `MAX_RETRIES_ON_429 = 3` retries per request. The constant is not configurable — it is a property of the Gemini per-minute quota.
- **OpenAI**: respects the 429 retry-after window when present and retries within the same per-request retry budget. On `billing hard limit`, fails fast without retrying.

---

## Cost summary

End-of-run output (plan-driven mode prints to stdout; single-shot mode prints to stderr) contains:

- Generated, skipped, and error counts.
- Provider and model (and quality/size on OpenAI).
- Total tokens (Gemini only) and estimated cost in USD.

Cost rates live in `_COST_TABLE` at the top of `generate_image.py`. **The cost table in the script is the source of truth.** When provider prices change, update `_COST_TABLE` directly — not this doc, not the ADR.

---

## Environment

| Variable | Required for | Notes |
|---|---|---|
| `GEMINI_API_KEY` | Gemini routing (the default) | |
| `OPENAI_API_KEY` | OpenAI routing | Only consulted when the resolved provider is OpenAI. |

The script discovers `.env` files via `_media_lib.env.load_env`, which walks `cwd → parents → $HOME` and loads the first `.env` it finds. **Existing process environment values always win** — a CI secret or shell export is honored even when a stale `.env` is checked in.

---

## Examples

### Plan-driven dry run

```bash
uv run --with google-genai --with openai \
  .claude/shared/skills/generate-image/generate_image.py \
  --plan IMAGE-PLAN.md --dry-run
```

### Plan-driven, regenerate just module 04

```bash
uv run --with google-genai --with openai \
  .claude/shared/skills/generate-image/generate_image.py \
  --plan IMAGE-PLAN.md --filter module-04 --force
```

### Single-shot (used by generate-screen)

```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py \
  --prompt "Hero illustration of a friendly cartoon developer" \
  --style "Head First book style" \
  --quality high \
  --aspect-ratio 16:9 \
  --output-dir images/hero \
  --asset-name hero
```

---

## Error conditions

| Error | Resolution |
|---|---|
| `GEMINI_API_KEY` not set (Gemini routing) | Add `GEMINI_API_KEY=...` to a `.env` on the cwd→parents→$HOME walk, or export in shell |
| `OPENAI_API_KEY` not set (OpenAI routing) | Add `OPENAI_API_KEY=...` similarly |
| Plan file not found | Check `--plan` path; default expected name is `IMAGE-PLAN.md` |
| Plan entry missing `**File**` | Entry is silently dropped; check the plan markdown |
| OpenAI org verification required | Automatic fallback to `gpt-image-1.5` with one-line warning; verify org at platform.openai.com to use `gpt-image-2` |
| OpenAI billing hard limit | Script fails fast; raise the dashboard cap or wait for next billing period |
| 429 (Gemini or OpenAI) | Automatic retry honoring `retryDelay`; 3 attempts per request |

## Acknowledgements

Plan parser, frontmatter regex set, dispatch logic, and the `MIN_INTERVAL_SECONDS = 60.0/18` rate-limiter constant are adapted from `Course_Material/Git_Fundamentals/scripts/generate_images.py` (the Stonewaters reference, ~495 lines, production-tested across an 18-course portfolio). The script in this skill credits that source in its module docstring.
