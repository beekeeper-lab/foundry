# ADR-011: Audio Generation Skill Design (ElevenLabs Narration)

| Field | Value |
|-------|-------|
| **Date** | 2026-04-29 |
| **Status** | Accepted |
| **Bean** | BEAN-283 |
| **Deciders** | Architect |

## Context

The ClaudeKit `.claude/shared/skills/` directory has no audio
generation skill today. The Stonewaters portfolio (18 illustrated,
narrated HTML courses) and any future Foundry-generated portfolio
project needs to turn thousands of short narration paragraphs into
ElevenLabs MP3s — re-runnable, idempotent against on-disk state,
auditable via per-source manifests, and cheap enough to pace
against the ElevenLabs Pro cap (500K credits/month at $100).

The reference design lives in
`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md`
under "Audio-generation skill." The canonical implementation is
`Course_Material/Git_Fundamentals/scripts/generate_narration.py`
(274 lines), which carries production knowledge: the inline
`> 🎙️` blockquote scanner, the markdown-stripping regex order,
the per-source manifest shape, and the orphan-cleanup rule. ADR-009
established ClaudeKit as the canonical home for cross-project
skills; ADR-010 set the precedent for plan-driven, sidecar-driven
media skills routed via plan frontmatter. This ADR continues that
pattern for narration audio.

Three forces shape the contract:

1. **Two surfaces, one source of truth.** Narration text appears in
   two places in the portfolio: inline as `> 🎙️` blockquotes in
   source markdown (the rendered course), and consolidated in
   `NARRATION-PLAN.md` as a reviewer-friendly enumeration. The
   source markdown is what the build pipeline renders; the plan is
   a human review surface. Picking the plan as the source of truth
   would force a manual sync step every time the source markdown
   changes. The inline blocks must be the contract; the plan
   markdown is informational.
2. **Cross-system content-hash dedup.** A narration block that
   appears in three places (e.g. an intro paragraph reused in a
   crash course and a recap page) must render with one MP3 across
   all three. Build pipelines content-hash the *stripped* narration
   text and look up MP3s in a portfolio-wide index. For that lookup
   to hit, the audio generator must store the same stripped text in
   its manifest that the build pipeline hashes — bit-for-bit. BEAN-281
   established `_media_lib.text.normalize_narration_text` and
   `_media_lib.text.hash_text` as the portable contract, with a
   regex-order contract test preventing accidental drift. This skill
   delegates stripping to that module rather than re-implementing it.
3. **Cloned voice IDs are project preference, not kit assets.** The
   Stonewaters Purdue grad courses use a cloned voice ID
   (`s6d7r1gfIA8ArVv5Vocl`, Gregg Reed). ClaudeKit ships to every
   consumer; baking that ID into a kit-shipped voice map would leak
   one user's voice clone into every downstream project. Per user
   direction, cloned voice IDs live in user project plans/env, not
   in committed kit code.

The skill belongs in `.claude/shared/skills/generate-audio/` and is
distributed via the ClaudeKit asset list (`_KIT_DISTRIBUTED_SKILLS`,
BEAN-280) so subtree-mode and library-copy-mode generated projects
both receive it.

## Decision

Six concrete commitments. The Developer task (BEAN-283 task 02)
implements directly against this list.

**1. Inline `> 🎙️` blockquote = the contract; `NARRATION-PLAN.md`
is review surface only.** Source markdown is the source of truth.
The generator scans configured source files for blockquoted lines
beginning with the studio-microphone emoji (🎙️) and treats each
contiguous blockquoted run as one narration block. Default source
glob is `module-*.md` under the project's source directory; `--all`
widens to every `*.md` in that directory (crash courses, references,
auxiliary files).

`NARRATION-PLAN.md`, when present, is parsed for `Voice:` and
`Model:` frontmatter only — informational, not authoritative. CLI
flags override frontmatter. The plan is never the source of which
blocks exist; that's always the source markdown. The plan can carry
per-block character counts so a reviewer can answer "what does the
rest of this course cost" in one line, but the generator does not
read those counts to decide what to generate.

**2. Per-source-file manifest at `audio/<source-stem>/manifest.json`,
schema `{index, module, audio_file, text, size_bytes}`.** One
manifest per source file, written as a JSON array of records. Fields:

- `index` — 1-based block number; matches the `NN_` prefix on the
  MP3 filename (e.g. `01_module-00-intro.mp3` → `index: 1`).
- `module` — the source-file stem (e.g. `module-00-intro`).
- `audio_file` — the MP3 basename, relative to the manifest's
  directory.
- `text` — **the stripped narration text** that was sent to
  ElevenLabs. Not the raw blockquote. Not the source markdown. The
  exact characters that traveled to the API. This is what the build
  pipeline content-hashes for cross-page dedup; bit-for-bit fidelity
  with what was sent is the contract (commitment 5).
- `size_bytes` — the MP3 file size in bytes; used for sanity checks
  and the end-of-run summary.

The manifest is authoritative for "what should exist in this
directory." When the manifest is rewritten, MP3s whose blocks no
longer exist in source are removed (orphan cleanup).

**3. Pre-send stripping uses `_media_lib.text.normalize_narration_text`
from BEAN-281 — no re-implementation.** ElevenLabs literally
pronounces markdown markers ("star star" for `**bold**`), so every
block is normalized before the API call. The generator imports and
calls `normalize_narration_text` from
`.claude/shared/skills/_media_lib/text.py`. The regex application
order (blockquote → mic emoji → HTML tags → bold → italic → code →
link → whitespace collapse) is locked in by the BEAN-281 contract
test; both this skill and any downstream build pipeline that hashes
narration text MUST use that function verbatim. If the regex order
ever changes, both consumers move in lockstep — but the contract
test catches accidental drift either way.

The `text` field stored in the manifest (commitment 2) is exactly
the output of `normalize_narration_text` applied to the captured
blockquote — the same string that was sent to ElevenLabs.

**4. Voice routing — default `rachel`; voice map for stock names;
unknown values pass through as raw IDs; `--voice` overrides; no
cloned voice IDs in committed code.**

- **Default voice:** `rachel`, ElevenLabs voice ID
  `21m00Tcm4TlvDq8ikWAM`.
- **Voice map** (kit-shipped, generic only): `rachel`, `drew`,
  `paul`, `sarah`, `emily`, `charlie`, `george`, `matilda` — names
  that exist in any ElevenLabs account's default voice library and
  the corresponding stock voice IDs. The exact map lives in
  `generate_audio.py`; this ADR fixes the *policy* (stock names
  only), not the exact list, and additions to the stock-name map
  are non-breaking.
- **Passthrough rule:** any `--voice` value not present in the map
  is passed to ElevenLabs as a raw voice ID. This works for two
  cases: (a) a name the user has registered in their own voice
  library, and (b) a raw voice ID string. The script does not
  validate; ElevenLabs validates and returns a clear error if the
  ID is unknown.
- **`--voice <name-or-id>`** is the runtime override. `Voice:`
  frontmatter in `NARRATION-PLAN.md` is informational only.
- **No cloned voice IDs in committed code.** Cloned voices are
  per-project preferences (e.g. the Stonewaters Purdue cloned
  voice). They live in user project plans/env/CLAUDE.md, not in
  the kit's voice map. The generator never auto-discovers cloned
  voices; the user passes them via `--voice <id>` or records them
  in a per-project plan/env file outside the kit.

**5. ElevenLabs default model `eleven_multilingual_v2`; `--model`
overrides; plan frontmatter `Model:` is informational.** The
default tracks the canonical reference implementation and is the
production-tested choice across the Stonewaters portfolio. CLI
`--model` is the runtime override. `Model:` lines in
`NARRATION-PLAN.md` are read for human review but do not bind the
generator — CLI flags win, mirroring the voice-routing rule
(commitment 4) and ADR-010's plan-vs-flag convention.

**6. Skip-on-disk modes — five behaviors, deterministic.**

- **Missing MP3 → generate.** The default. Walk every block in
  every selected source file; if the target MP3 path doesn't
  exist, generate it. This is what makes incremental authoring
  cheap: add one new `> 🎙️` block, re-run, only that one block
  is generated.
- **`--regenerate-changed` → regenerate when stripped text differs
  from manifest.** Compares the current normalized text for each
  block against the manifest's stored `text` field. If they differ,
  regenerate. The comparison hits exactly the right cases because
  both sides are post-stripping (commitment 2 + commitment 3); a
  whitespace-only edit in source markdown collapses to the same
  normalized text and does not trigger regeneration.
- **`--force` → regenerate everything for the run.** Bypasses both
  the missing-file check and the changed-text check. Used when a
  voice or model change requires re-rendering the full set.
- **`--dry-run` → walk the plan, print what would happen, no API
  calls.** Always run dry-run first on a fresh plan or after a
  bulk edit; ElevenLabs spend is irreversible and a 200-block
  course at 600 chars/block is 120K credits (~$24 at the Pro rate
  amortization).
- **`--all` → include auxiliary source files** (crash courses,
  references — every `*.md`) instead of the default `module-*.md`
  glob. Default scope keeps casual re-runs from accidentally
  re-narrating reference material.

These five modes are mutually composable: `--dry-run --force` is a
preview of a full regen; `--dry-run --all --regenerate-changed` is
"what would change across the whole project including auxiliaries."

## Orphan cleanup

When the manifest is rewritten, the generator removes MP3s in
`audio/<source-stem>/` whose `audio_file` names no longer appear in
the new manifest's expected set. The manifest is the only durable
record of "what should exist in this directory" — orphan MP3s are
files whose source `> 🎙️` blocks have been deleted or renumbered,
and leaving them on disk would cause stale audio to be embedded in
rebuilt HTML.

Cleanup runs only on real generation runs, never under `--dry-run`
(dry-run makes no on-disk changes). It runs even when nothing was
generated this pass — re-running on a source file with one block
deleted will rewrite the manifest and remove the orphaned MP3 even
though no new audio was generated.

## Cost discipline

ElevenLabs `eleven_multilingual_v2` is **1 credit per character**.
Pro plan = 500K credits/month at $100. A 30-module intern course
at 8 blocks × 300 chars = ~72K credits ≈ 14% of monthly cap. A
33-module graduate course at 13 blocks × 600 chars = ~257K credits
≈ 50% of monthly cap.

Every run prints a character-count summary at the end:
total characters sent across the run = total credits spent.
Implementation: sum the character counts of every block actually
sent to ElevenLabs in the run (not skipped, not dry-run-previewed)
and print the total before exit. Plan-aware extension: when the
generator was invoked against a project containing
`NARRATION-PLAN.md`, the summary may also print remaining-credit
math from the plan's per-block counts ("this run: X credits;
remaining in plan: Y credits"). The plan-aware extension is
optional polish; the run-total is mandatory.

This is not optional. ElevenLabs spend is the second most
irreversible cost in the agentic-media stack (behind only OpenAI
image batches). The character-count summary is the user's pacing
signal; without it, a 500K-cap user can burn the month's budget on
a single bad invocation. Cost rates change; the credit-per-character
constant lives in `generate_audio.py` and is the load-bearing
version, mirroring ADR-010's cost-table-in-script rule.

## Content-hash dedup contract

The manifest's `text` field MUST be the stripped narration —
exactly the output of
`_media_lib.text.normalize_narration_text(raw_blockquote)` and
exactly what was sent to ElevenLabs. Any downstream build pipeline
that wants to dedupe MP3s across pages — Foundry-generated builds,
the Stonewaters `build_course.py`, or any future consumer —
content-hashes the manifest's `text` via
`_media_lib.text.hash_text` and uses the resulting sha256 as the
cache key.

**Bit-for-bit hash compatibility is required.** The contract is
portable across systems and shipped artifacts; substituting md5,
re-implementing the normalization, or ordering the regexes
differently will desync the cache and force every previously
generated MP3 to be re-narrated. The BEAN-281 contract test
(`tests/test_media_lib.py`) defends the regex order. Downstream
consumers MUST import `hash_text` from `_media_lib.text`, not
re-implement it.

The build pipeline use case is *not* implemented in this skill
(out of scope per the bean — that's a build-time concern; Foundry
itself does not ship a build pipeline). What this ADR locks down
is the *contract* the audio generator honors so that downstream
build pipelines can rely on it.

## Consequences

**Positive:**

- **Cost is predictable per character.** Every block has a known
  cost in credits = its character count. End-of-run summary makes
  spend visible; plan-tracked per-block counts make pacing tractable
  against the monthly cap.
- **Portable dedup.** Same `_media_lib.text.hash_text` across the
  audio generator and any build pipeline means a narration block
  reused in three pages costs one ElevenLabs call. Position-based
  matching is intentionally avoided — it would break the moment
  source files were reordered.
- **Failover when ElevenLabs hits its monthly cap.** When credits
  are exhausted, non-audio courses keep advancing. Plan-first +
  per-source-file manifests + orphan cleanup mean partial work is
  recoverable: when credits return, re-running the generator
  picks up exactly where it left off.
- **No leaked voice clones.** Kit-shipped code carries only generic
  voice names. User project plans carry the cloned IDs. The kit
  ships to every consumer; the user-specific voices stay
  user-specific.
- **Skip-on-disk + content-aware regen are deterministic.** The
  five-mode matrix (missing/regenerate-changed/force/dry-run/all)
  covers every authoring workflow without overlapping behaviors.

**Negative:**

- **Regex order is a cross-system contract.** Changing the regex
  application order in `_media_lib.text.normalize_narration_text`
  changes the hash for every previously stored manifest entry —
  invalidating the audio generator's `--regenerate-changed`
  comparisons and every downstream build pipeline's content-hash
  cache simultaneously. The BEAN-281 contract test guards the order;
  any deliberate change requires coordinated rollouts across the
  generator and every consuming build pipeline. We accept this
  cost — the alternative (per-consumer normalization) would
  guarantee divergent hashes and silent dedup misses.
- **Voice-passthrough trusts the user.** Unknown `--voice` values
  go to ElevenLabs unvalidated. A typo'd voice name produces an
  ElevenLabs error mid-run. We accept this — validating against
  the user's voice library would require an extra API call per run
  and would not cover the cloned-voice case (where the ID is
  meant to look unfamiliar to the kit).
- **Orphan cleanup is silent on dry-run.** A user inspecting a
  dry-run won't see "this MP3 would be removed." The summary lines
  list generation actions; orphan removal is implicit on real runs.
  We accept this for simplicity; the manifest diff is the durable
  record of what changed.
- **Plan frontmatter is informational, not authoritative.** A user
  who carefully writes `Voice:` in `NARRATION-PLAN.md` and then
  forgets `--voice` on the CLI will get the default voice. The
  CLI-wins rule mirrors the rest of the kit (ADR-010) but it does
  surprise occasional users. The first-line summary that the
  generator prints includes the resolved voice and model so the
  surprise is visible in real time.

## Alternatives Considered

1. **Plan markdown as source of truth instead of inline `> 🎙️`
   blocks.** Rejected. The source markdown stays in sync with the
   rendered HTML output by construction — every edit to the
   narration is visible in the same file the build pipeline reads.
   Treating `NARRATION-PLAN.md` as the source forces a manual sync
   step every time the source markdown changes, and that sync step
   is exactly the kind of human chore that goes stale. The plan as
   review surface (rather than source) keeps reviewers' workflows
   intact without making the plan a write-back blocker.
2. **Position-based MP3 reuse instead of content-hash dedup.**
   Rejected. Position-based matching ("block 3 of file X is the
   same MP3 as block 3 of file Y") breaks the moment any source
   file is reordered, split, or merged. Content-hash dedup is
   robust to reordering by construction: the same stripped text
   produces the same sha256 regardless of where it appears.
3. **Inline cloned voice IDs in the kit-shipped voice map.**
   Rejected. The voice map is shipped to every ClaudeKit consumer;
   baking a per-user cloned voice ID into it leaks that user's
   voice clone into every downstream project. Cloned voices are
   per-project preferences and live in user project
   plans/env/CLAUDE.md, never in the kit.
4. **No stripping before send to ElevenLabs.** Rejected.
   ElevenLabs literally pronounces markdown markers ("star star"
   for `**bold**`); this is the day-one bug every shipped TTS
   agent gets wrong. Stripping is mandatory. Re-implementing the
   stripping in this skill (rather than delegating to
   `_media_lib.text.normalize_narration_text`) is also rejected —
   it would diverge from the BEAN-281 contract test and risk
   desyncing the cross-system content hash.
5. **A separate per-block sidecar JSON (one file per MP3) instead
   of a per-source-file manifest array.** Rejected. The audio
   skill's atomic unit is a *source file* — one MP3 per block,
   collated by source. A per-source manifest matches the natural
   grouping (regenerate-changed compares old vs. new for the same
   source file; orphan cleanup operates on the source-file
   directory). Per-block sidecars would scatter that bookkeeping
   across hundreds of files and force the generator to re-walk all
   sidecars to compute the per-source view. The image skill's
   per-PNG sidecar (ADR-010) is the right shape for *that* skill
   because images don't share a natural source-file grouping; for
   audio, the source file is the unit.

## Reversibility

The manifest schema (`{index, module, audio_file, text,
size_bytes}`) is the load-bearing piece. **Adding a field is
non-breaking** — readers ignore unknown fields; old manifests are
forward-compatible. **Removing or renaming any of the five named
fields requires a follow-up ADR**, because both the audio
generator's `--regenerate-changed` lookup and every downstream
build pipeline's content-hash index depend on the exact field
names.

The voice-routing policy (default rachel; stock names only in the
kit map; passthrough for unknown values; no cloned voices) is
similarly load-bearing. Adding a new stock name is non-breaking;
removing rachel as default or admitting cloned voice IDs to the
committed map requires a follow-up ADR.

The `eleven_multilingual_v2` default model and the
1-credit-per-character cost rate live in code, not in this ADR —
they can change without a new ADR as long as the *policy* (default
present, CLI override available, cost printed every run) holds.

