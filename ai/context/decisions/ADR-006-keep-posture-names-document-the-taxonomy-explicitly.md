# ADR-006: Keep Posture Names, Document the Taxonomy Explicitly

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-250 |
| **Deciders** | Architect |

## Context

External review flagged the hook posture taxonomy (`baseline` / `hardened` / `regulated`) as "conceptually muddy": the reviewer observed compositions at `baseline` that appeared to enable multiple git, cloud, compliance, QA, lint, and secret controls, prompting the question "if this is baseline, what does hardened mean?"

The reviewer proposed two resolutions:
1. **Slim** `baseline` so the word matches the posture.
2. **Rename** the levels so the taxonomy is honest about what each level turns on.

Inspecting the code, the current per-posture **base pack set** in `safety_writer._POSTURE_BASE` is already narrow:

| Posture | Base packs (stack-independent) | Base count |
|---------|--------------------------------|------------|
| `baseline` | `git-commit-branch` | 1 |
| `hardened` | `git-commit-branch`, `git-push-feature`, `security-scan` | 3 |
| `regulated` | `git-commit-branch`, `git-push-feature`, `security-scan`, `compliance-gate`, `post-task-qa` | 5 |

Stack-aware layering (BEAN-255) adds at most one lint pack (expertise-driven) and one cloud pack per cloud provider, and cloud packs are only added at `hardened`/`regulated`. So a `baseline` project with Python + AWS gets exactly **two** packs: `git-commit-branch` + `pre-commit-lint`. Not "muddy" in the code — muddy in the **documentation and example compositions**, where the reader cannot infer this without reading `safety_writer.py`.

The reviewer's premise (that `baseline` includes Azure, compliance, QA, secret controls) does not match the base-pack set. It matches what a user sees if they look at the full library of available packs and assume all of them are enabled at `baseline`, or if they look at an example YAML where an explicit `packs:` list overrides stack-aware defaults.

## Decision

**Keep the existing names (`baseline` / `hardened` / `regulated`) and make the taxonomy visible through documentation + a lock-in test.**

Specifically:
1. Add `ai/context/hook-posture.md` that states — for each posture — the **intent**, the **base pack list**, the **default enforcement mode**, and how stack-aware layering adds to it.
2. Expose `posture_base_packs(posture) -> list[str]` as a public helper in `safety_writer.py` so the mapping is importable (for tests, UI surfaces, and future tooling) and no longer buried in a module-private dict.
3. Add a Tech-QA test that asserts `posture_base_packs(Posture.BASELINE|HARDENED|REGULATED)` matches the documented list — so the doc and code cannot drift.

## Rationale — why keep the names

- **The code is not broken; the narration is.** The existing mapping already forms a reasonable ordering (1 → 3 → 5 base packs). Slimming `baseline` further would mean zero base packs, which removes the one guardrail (`git-commit-branch`) every generated project benefits from.
- **Rename has a large blast radius** — every example YAML, every loaded composition, every settings default, every docs reference, every screenshot in flight would change. The bean even calls this out as "visible in every composition YAML."
- **The reviewer's concern is answered by making the taxonomy legible**, not by changing identifiers. A reader who opens `hook-posture.md` can predict the pack count within a reasonable range for each level — which is exactly the bean's stated goal.
- **`regulated` has a distinct meaning** (compliance + post-task-qa) that `hardened` does not capture. Collapsing to a two-level rename would lose that signal.

## Alternatives Rejected

1. **Rename `baseline` → `minimal`, `hardened` → `standard`, `regulated` → `strict` (reviewer's option B).** Rejected: forces migration of every composition YAML, settings key, UI label, and test. The existing names already suggest an ordering once documented. The rename trades a documentation problem for a migration problem.
2. **Slim `baseline` to zero base packs.** Rejected: `git-commit-branch` is the one guardrail we want on by default — it blocks edits on `main` / `master` / `test` / `prod`. Removing it means every new project starts with no safety net.
3. **Collapse to two levels (`standard` / `strict`).** Rejected: `regulated` encodes a compliance-adjacent intent (compliance-gate + post-task-qa) that doesn't fit the `hardened` bucket. Users picking `regulated` are making a different statement than users picking `hardened`.

## Consequences

- `ai/context/hook-posture.md` becomes the canonical reference for the taxonomy. `safety_writer.py` module docstring and `hook-selection.md` link to it.
- A failing lock-in test flags any future silent change to `_POSTURE_BASE` — taxonomy changes must update the doc too.
- No migration aliases are needed — enum values are unchanged.
- If a future bean wants to restructure levels, this ADR is superseded and the rename migration happens then.

