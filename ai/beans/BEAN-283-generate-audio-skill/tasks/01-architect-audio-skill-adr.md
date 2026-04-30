# Task 01: ADR — Audio Generation Skill Design

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends on** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Record an ADR (next consecutive number — likely ADR-011) capturing
the audio generation skill design that BEAN-283's Developer task
will implement. Lock the contract: source-of-truth (inline `> 🎙️`
blocks), manifest schema with stripped text, content-hash dedup
contract via `_media_lib.text.hash_text`, voice routing rules with
no cloned voice IDs in source, ElevenLabs default model, and
cost-per-character reporting.

## Inputs

- `ai/beans/BEAN-283-generate-audio-skill/bean.md`
- `ai/context/decisions.md` — ADR home (next number; ADR-010 is most recent)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` — reference design (Audio-generation skill section)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_narration.py` — canonical implementation
- `.claude/shared/skills/_media_lib/text.py` — the `normalize_narration_text` and `hash_text` functions this skill must use (BEAN-281)

CONTEXT DIET: stay within these inputs.

## Required ADR sections

1. **Context** — narration text lives inline in source markdown (the contract); a sidecar plan markdown is the human review surface. Manifests record the exact stripped text sent to ElevenLabs so re-runs and content-hash dedup match what was sent. Cloned voice IDs are project-specific and stay in user plans, not in kit-shipped code.
2. **Decision** — six concrete commitments:
   1. **Inline `> 🎙️` blockquote = the contract.** Source markdown is the source of truth. `NARRATION-PLAN.md` is the review surface, not the source. Generator scans source files for blockquoted lines starting with the microphone emoji.
   2. **Per-source-file manifest** at `audio/<source-stem>/manifest.json` is an array of `{index, module, audio_file, text, size_bytes}`. `index` is 1-based and matches the `NN_` prefix on the MP3 filename. `text` is the **stripped** narration (markdown markers removed) — what was sent to ElevenLabs and what the build pipeline content-hashes.
   3. **Pre-send stripping** uses `_media_lib.text.normalize_narration_text` from BEAN-281. The same function the build pipeline uses for content-hash dedup. If the regex order changes, both must change in lockstep — but the contract test in BEAN-281 prevents accidental drift.
   4. **Voice routing**: default voice `rachel` (ElevenLabs voice ID `21m00Tcm4TlvDq8ikWAM`). Voice map covers stock names; unknown values pass through as raw IDs. `--voice <name-or-id>` overrides. **No cloned voice IDs in committed code** — they belong in user project plans/env, not the kit.
   5. **ElevenLabs default model**: `eleven_multilingual_v2`. Override via `--model` or plan frontmatter `Model:`.
   6. **Skip-on-disk modes**:
      - Missing MP3 → generate.
      - `--regenerate-changed` → regenerate when current stripped text differs from the manifest's stored `text`.
      - `--force` → regenerate everything for the run.
      - `--dry-run` → walk plan, print plan, no API calls.
      - `--all` → include auxiliary source files (default is `module-*.md`).
3. **Orphan cleanup** — when rewriting a manifest, MP3s whose blocks no longer exist in source are removed. The manifest is the only record of what should exist; it's authoritative.
4. **Cost discipline** — ElevenLabs `eleven_multilingual_v2` is 1 credit per character. Pro plan = 500K credits/mo at $100. Every run prints char-count = credit-count summary. Plan markdown can carry per-block character counts so "what does the rest of this course cost" is one-line answerable.
5. **Content-hash dedup contract** — the manifest's `text` field MUST be the stripped narration. Any downstream pipeline (Foundry-generated build, Stonewaters `build_course.py`, etc.) that wants to dedupe MP3s across pages content-hashes that text via `_media_lib.text.hash_text`. The contract is portable; bit-for-bit hash compatibility is required.
6. **Consequences** — what becomes easier (cost predictability per character; portable dedup; failover if ElevenLabs hits monthly cap, advance non-audio courses); what becomes harder (regex order is a cross-system contract — changes need coordinated rollouts).
7. **Alternatives considered** — at minimum:
   - **Plan markdown as source of truth instead of inline blocks** (rejected: source markdown stays in sync with rendered output; plan-as-source forces a manual sync step).
   - **Position-based MP3 reuse** (rejected: breaks when source files are reordered; content-hash is robust).
   - **Inline cloned voice ID in voice map** (rejected: per-project preference; kit ships only generic names).
   - **No stripping before send** (rejected: ElevenLabs literally pronounces "star star" — every shipped agent gets this wrong on day one).

## Acceptance Criteria

- [ ] ADR exists in `ai/context/decisions.md` with the structure above.
- [ ] ADR is numbered consecutively (likely ADR-011 since ADR-010 is the most recent).
- [ ] All six "Decision" commitments stated unambiguously.
- [ ] Inline-vs-plan source-of-truth distinction is explicit (inline = contract).
- [ ] Manifest schema named: `index, module, audio_file, text, size_bytes`.
- [ ] Voice routing rule is explicit (default rachel; voice map for names; raw IDs passthrough; no cloned voice in committed code).
- [ ] Content-hash dedup contract names the `_media_lib.text.hash_text` function and the cross-system bit-for-bit requirement.
- [ ] Cost rule: 1 credit per char; runs print char count.
- [ ] At least 3 alternatives rejected with one-line reasons.
- [ ] No code changes — design only.

## Definition of Done

- ADR appended to `ai/context/decisions.md`.
- Developer task (02) can read this ADR and implement without further discussion.
- Commit message: `BEAN-283 task 01: ADR for audio generation skill design`.
