# Skill Specification: `generate-image` (v1)

## Overview

A shared Claude Code skill for generating images via Google's Gemini image generation models (Nano Banana family). Designed as a low-level utility that can be:

- Invoked directly by a user via `/generate-image`
- Called by other skills (e.g., a future `generate-screen` or `generate-ui` skill)
- Shared across projects via the claude-kit submodule

This skill generates **single image assets** (or small sets of variations). It is not responsible for generating application screens, pages, or code.

---

## Architecture

```
Claude Code slash command
  -> SKILL.md (instructions to Claude)
    -> Python script (API call, file I/O)
      -> Gemini API (image generation)
        -> image file + metadata JSON sidecar
```

- **Entry point**: `/generate-image` slash command
- **Skill file**: SKILL.md instructs Claude how to invoke the script
- **Backend**: Single Python script, executed via `uv run --with google-genai --with pillow`
- **API**: Google Gemini (`google-genai` SDK)
- **API key**: `GEMINI_API_KEY` from environment or `.env` file

---

## File Layout

### Skill files (in claude-kit submodule)

```
.claude/shared/
  skills/
    generate-image/
      SKILL.md
      generate_image.py
  commands/
    generate-image.md
```

Minimal footprint: one skill definition, one script, one command. No extra templates, examples, or README files. SKILL.md contains all documentation.

### Output files (in consuming project)

```
images/
  <context>/
    <asset-name>-01.png
    <asset-name>-01.json
    <asset-name>-02.png
    <asset-name>-02.json
```

- `<context>` is a user-provided subdirectory (project name, feature, etc.)
- Default context: `misc`
- Metadata JSON sidecar saved beside each image

---

## Models

### Friendly names and mapping

| Friendly Name | Model ID | Use Case |
|---|---|---|
| `nanobanana2` | `gemini-3.1-flash-image-preview` | Fast, cheap. Drafts, iterations, simple graphics. |
| `nanobanana-pro` | `gemini-3-pro-image-preview` | High fidelity. Infographics, final assets, complex prompts, text rendering. |

The mapping is a dict at the top of the script — easy to update when model IDs change.

### Model selection (`--model`)

| Value | Behavior |
|---|---|
| `auto` | Routed by `quality_mode` (see below). Default. |
| `nanobanana2` | Use NB2 explicitly. |
| `nanobanana-pro` | Use Pro explicitly. |

### Fallback cascade

If the selected model fails due to access/quota issues:
- `nanobanana-pro` -> fall back to `nanobanana2`, warn the user
- `nanobanana2` -> error (nothing to fall back to)

Explicit model selection is always honored first. Fallback only triggers on API errors, not by default.

---

## Quality Mode (`--quality-mode`)

Controls intent. Affects auto-routing and is recorded in metadata.

| Value | Auto-routes to | Intent |
|---|---|---|
| `draft` | `nanobanana2` | Quick iteration, concept exploration |
| `variations` | `nanobanana2` | Multiple takes on a concept |
| `edit` | `nanobanana2` | Refine an existing image with references |
| `final` | `nanobanana-pro` | Polished, production-ready output |

Default: `draft`

When `--model` is set explicitly, it overrides auto-routing regardless of quality mode.

---

## CLI Interface

The script is invoked via CLI args only (no JSON request file in v1).

```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py \
  --prompt "A premium AI dashboard hero image" \
  --model auto \
  --quality-mode draft \
  --aspect-ratio 16:9 \
  --output-dir images/foundry \
  --asset-name dashboard-hero
```

### Arguments

| Arg | Required | Default | Description |
|---|---|---|---|
| `--prompt` | Yes* | — | Text description of the image |
| `--model` | No | `auto` | `auto`, `nanobanana2`, `nanobanana-pro` |
| `--quality-mode` | No | `draft` | `draft`, `final`, `edit`, `variations` |
| `--goal` | No | — | What the image is for (hero image, icon, infographic, etc.) |
| `--style` | No | — | Artistic/design direction |
| `--aspect-ratio` | No | — | e.g., `16:9`, `1:1`, `9:16` |
| `--background` | No | — | `transparent`, `white`, `dark`, or freeform |
| `--text-in-image` | No | — | `none`, `minimal`, `allowed`, `exact` |
| `--color-palette` | No | — | Comma-separated hex values (e.g., `#1F3A5F,#2D6A4F`) |
| `--negative` | No | — | Repeatable. Things to avoid. |
| `--reference-image` | No | — | Repeatable. Path to reference image file. |
| `--output-dir` | No | `images/misc` | Output directory |
| `--asset-name` | No | `image` | Base filename for outputs |
| `--count` | No | `1` | Number of images to generate (each is a separate API call) |

*`--prompt` is required unless `--reference-image` is provided, in which case a minimal prompt is still recommended.

---

## Prompt Assembly

The script builds a composite prompt from structured inputs. Assembly order:

1. Goal (if provided): `Create a [goal].`
2. Prompt: `[prompt]`
3. Style (if provided): `Style: [style].`
4. Color palette (if provided): `Use colors inspired by: [palette].`
5. Aspect ratio (if provided): `Aspect ratio: [aspect_ratio].`
6. Background (if provided): `Background: [background].`
7. Text in image (if provided): `Text in image: [text_in_image].`
8. Negative constraints (if any): `Avoid: [negatives].`

Only included fields appear in the assembled prompt. The assembly is simple string concatenation — no templating engine, no prompt engineering tricks. Readable, debuggable, deterministic.

---

## Reference Images

When `--reference-image` paths are provided:

1. Verify each path exists; fail with a clear error if any are missing
2. Load and include in the Gemini API request as inline image parts
3. Record which images were used in output metadata

Reference images are sent alongside the text prompt. The user's intent for how references should influence the result comes through the prompt text (e.g., "use this style", "same composition but different content").

---

## Output

### Image files

- Format: PNG
- Naming: `<asset-name>-01.png`, `<asset-name>-02.png`, etc.
- Directory created automatically if it doesn't exist

### Metadata sidecar (per image)

`<asset-name>-01.json`:

```json
{
  "timestamp": "2026-03-07T14:30:00Z",
  "model_requested": "auto",
  "model_resolved": "gemini-3.1-flash-image-preview",
  "quality_mode": "draft",
  "prompt": "original user prompt",
  "assembled_prompt": "full prompt sent to model",
  "goal": "hero image",
  "style": "clean premium SaaS",
  "aspect_ratio": "16:9",
  "background": "dark",
  "reference_images": [],
  "output_file": "dashboard-hero-01.png",
  "output_index": 1,
  "fallback_used": false
}
```

Only populated fields are included (no null-padding).

### Script stdout

The script prints JSON to stdout for Claude (or a parent skill) to consume:

```json
{
  "success": true,
  "model_resolved": "gemini-3.1-flash-image-preview",
  "fallback_used": false,
  "images": [
    {
      "image_path": "images/foundry/dashboard-hero-01.png",
      "metadata_path": "images/foundry/dashboard-hero-01.json"
    }
  ]
}
```

On failure:

```json
{
  "success": false,
  "error": "GEMINI_API_KEY is not set. Create a .env file or export the variable."
}
```

---

## Environment & Dependencies

### API key

The script loads `GEMINI_API_KEY` from:
1. Environment variable (checked first)
2. `.env` file in the project root (fallback)

Manual `.env` parsing (read lines, split on `=`, skip comments). No `python-dotenv` dependency needed for this.

### Execution

```bash
uv run --with google-genai --with pillow \
  .claude/shared/skills/generate-image/generate_image.py [args]
```

`uv run --with` handles dependencies ephemerally — no install step, no pollution of the project's venv, works in any project that has `uv`.

---

## Error Handling

Clear, actionable errors for:

| Condition | Error message |
|---|---|
| No API key | `GEMINI_API_KEY is not set. Create a .env file or export the variable.` |
| Missing prompt (no refs either) | `--prompt is required when no --reference-image is provided.` |
| Invalid model name | `Unknown model 'foo'. Valid options: auto, nanobanana2, nanobanana-pro` |
| Reference image not found | `Reference image not found: path/to/file.png` |
| API error (model access) | `Gemini API error for model gemini-3-pro-image-preview: [error]. Falling back to nanobanana2.` |
| API error (no fallback) | `Gemini API error: [error detail]` |
| Count < 1 | `--count must be at least 1` |

---

## Scope Boundaries

### In scope (v1)

- Text-to-image generation
- Reference image support
- Model selection and auto-routing with fallback
- Quality mode
- Metadata sidecar output
- Structured CLI arguments
- `.env` loading
- Shareable via claude-kit submodule

### Out of scope (v1)

- JSON request file input
- Database storage
- Cloud uploads
- Async/queue processing
- Image catalog
- Multi-vendor backends
- Full screen/page generation
- Request schema validation files
- Example request files

---

## Acceptance Criteria

1. `/generate-image` slash command triggers the skill
2. Prompt-only image generation works with NB2
3. Explicit Pro selection works
4. `auto` routing uses NB2 for draft, Pro for final
5. Fallback from Pro to NB2 works when Pro is unavailable
6. Reference images are included in the API request
7. Image file + metadata JSON sidecar are saved
8. Output paths are predictable and configurable
9. Errors are clear and actionable
10. Script stdout is valid JSON consumable by other skills
11. Works in any project with `uv` — no project-specific dependencies
