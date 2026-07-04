# Skill: Generate Audio

## Description

Generates ElevenLabs MP3 narration from inline `> 🎙️` blockquote markers in source markdown. Re-runnable, idempotent against on-disk state, and auditable via per-source manifests. Defaults are tuned for the ElevenLabs Pro plan (500K credits/month at $100), and every run prints a character-count = credits summary so spend stays visible.

The script honors a five-mode skip-on-disk matrix (missing / `--regenerate-changed` / `--force` / `--dry-run` / `--all`) so the same invocation pattern works for incremental authoring, bulk regeneration, and risk-free preview.

## Trigger

Use this skill when the user asks to:

- Generate narration MP3s for a markdown course/document set with inline `> 🎙️` blocks.
- Re-run audio generation to fill in newly added narration blocks.
- Regenerate audio for blocks whose text has been edited.
- Preview what a generation run would do before spending credits.

## How it works

The contract is the **inline source markdown**, not the plan. `NARRATION-PLAN.md` (when present) is parsed for `Voice:` / `Model:` frontmatter for human review; CLI flags always win.

The default scope is `module-*.md` under the project's source directory. `--all` widens to every `*.md` in that directory (crash courses, references, auxiliaries).

For each source file, the script:

1. Walks the file for contiguous blockquoted lines starting with the studio-microphone emoji (`> 🎙️ ...`). Each contiguous run is one narration block.
2. Strips markdown markers via `_media_lib.text.normalize_narration_text` (BEAN-281 contract). The stripped text is what gets sent to ElevenLabs **and** what gets stored in the manifest's `text` field — bit-for-bit.
3. Decides per block: missing → generate, `--regenerate-changed` and stripped text differs from manifest's `text` → generate, `--force` → regenerate everything, otherwise → skip.
4. Calls ElevenLabs via the SDK and writes `audio/<source-stem>/NN_<source-stem>.mp3`.
5. Rewrites the per-source manifest (`audio/<source-stem>/manifest.json`) and removes orphan MP3s whose blocks no longer exist in source.
6. Prints an end-of-run summary: total characters sent across all files = total credits spent.

## Inline source convention

A narration block in source markdown looks like:

```markdown
> 🎙️ Welcome to Module 00. In this module we'll cover the basics
> of context priming and how it shapes every subsequent message.
```

Rules:

- The first line of the block MUST start with `> 🎙️ ` (literal microphone emoji + space).
- Continuation lines are blockquoted with `> ` (no emoji).
- A non-blockquote line (or a blank line, or a line without the `> ` prefix) ends the block.
- Blockquotes that do NOT start with the microphone emoji are ignored — they remain as plain quoted prose in the rendered HTML.

The skill walks every selected source file in lexicographic order; blocks within a file are 1-based and produce filenames `01_<stem>.mp3`, `02_<stem>.mp3`, …

## NARRATION-PLAN.md frontmatter

Optional. When present and passed via `--plan PATH`, the head of the file is parsed for two `**Key:**` lines:

```markdown
# Narration Plan

**Voice:** rachel
**Model:** eleven_multilingual_v2

## Module 00
...
```

Only `Voice:` and `Model:` are recognized. Parsing stops at the first `## ` heading. **CLI flags always override plan frontmatter** — pass `--voice drew` and the plan's `Voice:` line is informational only. The first-line summary the script prints lists the resolved voice and model so the override is visible at run time.

## Voice routing

Default voice is `rachel` (ElevenLabs voice ID `21m00Tcm4TlvDq8ikWAM`). The kit-shipped `STOCK_VOICE_MAP` covers eight stock names that exist in any default ElevenLabs account voice library: `rachel`, `drew`, `paul`, `sarah`, `emily`, `charlie`, `george`, `matilda`.

Unknown values (a name in your own voice library, or a raw voice ID string) **pass through unchanged** to ElevenLabs. The script does not validate; ElevenLabs rejects unknown IDs server-side with a clear error.

`--voice <name-or-id>` is the runtime override. `Voice:` frontmatter in `NARRATION-PLAN.md` is read for human review but does not bind the generator.

**No cloned voice IDs in the kit-shipped voice map.** Cloned voices are per-project preferences and live in user project plans / env / `CLAUDE.md`, not in the kit. The kit ships to every consumer; voice clones stay user-specific.

## Default model

`eleven_multilingual_v2` — the production-tested choice across the Stonewaters portfolio and the canonical reference. `--model <id>` is the override. Plan frontmatter `Model:` is informational.

## Manifest schema

Per-source-file manifest at `audio/<source-stem>/manifest.json`. JSON array of records:

```json
[
  {
    "index": 1,
    "module": "module-00-intro",
    "audio_file": "01_module-00-intro.mp3",
    "text": "Welcome to Module 00. In this module we'll cover the basics of context priming and how it shapes every subsequent message.",
    "size_bytes": 87421
  },
  {
    "index": 2,
    "module": "module-00-intro",
    "audio_file": "02_module-00-intro.mp3",
    "text": "...",
    "size_bytes": 102311
  }
]
```

Field meanings (per ADR-011):

| Field | Meaning |
|---|---|
| `index` | 1-based block number; matches the `NN_` prefix on the MP3 filename. |
| `module` | Source-file stem. |
| `audio_file` | MP3 basename, relative to the manifest's directory. |
| `text` | The **stripped narration** that was sent to ElevenLabs — bit-for-bit. |
| `size_bytes` | MP3 file size in bytes. |

The manifest is authoritative for "what should exist in this directory." When the manifest is rewritten, MP3s whose names no longer appear are removed (orphan cleanup).

### Schema is load-bearing

Adding a field is non-breaking — readers ignore unknown fields. **Removing or renaming any of the five named fields requires a follow-up ADR**, because both this skill's `--regenerate-changed` lookup and every downstream build pipeline's content-hash index depend on the exact field names.

## Content-hash dedup contract

The manifest's `text` field is exactly the output of `_media_lib.text.normalize_narration_text(raw_blockquote)` — exactly what ElevenLabs received. Downstream build pipelines (Foundry-generated builds, Stonewaters' `build_course.py`, future consumers) content-hash `text` via `_media_lib.text.hash_text` and use the resulting sha256 as a portfolio-wide cache key.

A narration block reused in three places hashes to the same digest and renders with one MP3 across all three. Build pipelines MUST import `hash_text` from `_media_lib.text`, not re-implement it — the BEAN-281 contract test (`tests/test_media_lib.py`) defends the regex order.

## Skip-on-disk modes

| Mode | Behavior |
|---|---|
| (default) | Generate every block whose target MP3 is missing. |
| `--regenerate-changed` | Also regenerate blocks whose stripped text differs from the manifest's stored `text`. Whitespace-only edits do NOT trigger regeneration (both sides are post-stripping). |
| `--force` | Regenerate everything for the run. Bypasses both checks. |
| `--dry-run` | Walk + print, **no API calls, no on-disk changes** (manifest stays unchanged, orphans stay on disk). Always run this first against a fresh plan or after a bulk edit. |
| `--all` | Include auxiliary `*.md` files (crash courses, references) instead of the default `module-*.md` glob. |

The five modes are mutually composable: `--dry-run --force` previews a full regeneration; `--dry-run --all --regenerate-changed` shows everything that would change across the whole project including auxiliaries.

### Orphan cleanup

When the manifest is rewritten on a real run, MP3s in `audio/<source-stem>/` whose names no longer appear in the new manifest's expected set are removed. The manifest is the only durable record of "what should exist here" — leaving orphans on disk would cause stale audio to be embedded in rebuilt HTML.

Cleanup runs only on real generation runs, never under `--dry-run`. It runs even when nothing was generated this pass — re-running on a source file with one block deleted will rewrite the manifest and remove the orphaned MP3 even though no new audio was generated.

## Cost discipline

ElevenLabs `eleven_multilingual_v2` is **1 credit per character**. Pro plan = 500K credits/month at $100.

Every run prints a single-line summary at the end:

```
elevenlabs eleven_multilingual_v2: 12 blocks generated, 4321 chars sent = 4321 credits
```

Total characters sent across the run = total credits spent. The credit-per-character constant lives in `generate_audio.py` (`CREDITS_PER_CHAR`); this file is the source of truth. When ElevenLabs changes the rate, update the constant — not this doc, not the ADR.

## Environment

| Variable | Required for | Notes |
|---|---|---|
| `ELEVENLABS_API_KEY` | All generation runs | Not consulted under `--dry-run`. |

The script discovers `.env` files via `_media_lib.env.load_env`, which walks `cwd → parents → $HOME` and loads the first `.env` it finds. **Existing process environment values always win** — a CI secret or shell export is honored even when a stale `.env` is checked in.

## Examples

### Default run — generate missing audio for all modules

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py
```

### Single source file

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    source/module-03-context-priming.md
```

### Dry-run preview before spending credits

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    --dry-run
```

### Regenerate only blocks whose text changed

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    --regenerate-changed
```

### Force regenerate everything (e.g. after a voice change)

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    --voice drew --force
```

### Include crash courses + references

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    --all
```

### Read defaults from a NARRATION-PLAN.md (CLI still wins)

```bash
uv run --with elevenlabs python \
    .claude/shared/skills/generate-audio/generate_audio.py \
    --plan NARRATION-PLAN.md
```

## Error conditions

| Error | Resolution |
|---|---|
| `ELEVENLABS_API_KEY` not set | Add `ELEVENLABS_API_KEY=...` to a `.env` on the cwd → parents → `$HOME` walk, or export in shell. Not required under `--dry-run`. |
| Source file not found | Check the positional argument; default expected layout is `source/module-*.md`. |
| `elevenlabs` package not installed | Run with `uv run --with elevenlabs python <script>` — the dep is intentionally not declared in `pyproject.toml` so the kit stays light. |
| ElevenLabs returns "voice not found" | Either the `--voice` value is a typo, or the voice ID is not in your account. Stock names are `rachel`, `drew`, `paul`, `sarah`, `emily`, `charlie`, `george`, `matilda`. |

## Acknowledgements

The inline `> 🎙️` blockquote scanner, the per-source manifest schema, the orphan-cleanup rule, and the stock-voice map are adapted from `Course_Material/Git_Fundamentals/scripts/generate_narration.py` (the canonical Stonewaters reference, ~274 lines, production-tested across an 18-course portfolio). Markdown stripping is delegated to `_media_lib.text.normalize_narration_text` (BEAN-281), which locks in the regex application order with a contract test so this skill and any downstream build pipeline that hashes narration text stay bit-for-bit compatible.
